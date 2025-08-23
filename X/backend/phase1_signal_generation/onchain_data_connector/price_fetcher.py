"""
⚡ 即時價格抓取引擎 - 產品級實現
Production-Grade Real-time Price Fetcher
支援 WebSocket + Multicall 批量抓取 + 動態價格異常檢測
"""

import asyncio
import aiohttp
from typing import Dict, Optional, List, Tuple
from web3 import Web3
from eth_utils import to_checksum_address
import json
import time
import logging
from datetime import datetime, timedelta

# 🔧 使用本地配置，不從根目錄導入
from .config import ProductionConfig

logger = logging.getLogger(__name__)

class RealTimePriceFetcher:
    """即時價格抓取引擎"""
    
    def __init__(self, main_pools: Dict[str, Dict]):
        self.config = ProductionConfig()
        self.main_pools = main_pools
        self.session: Optional[aiohttp.ClientSession] = None
        self.web3_instances: List[Web3] = []
        self.price_cache: Dict[str, Dict] = {}
        self.price_history: Dict[str, List[Tuple[datetime, float]]] = {}  # 價格歷史用於異常檢測
        self.is_running = False
        
        # V2 Pair ABI
        self.v2_pair_abi = [
            {
                "constant": True,
                "inputs": [],
                "name": "getReserves",
                "outputs": [
                    {"name": "_reserve0", "type": "uint112"},
                    {"name": "_reserve1", "type": "uint112"},
                    {"name": "_blockTimestampLast", "type": "uint32"}
                ],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "token0",
                "outputs": [{"name": "", "type": "address"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "token1",
                "outputs": [{"name": "", "type": "address"}],
                "type": "function"
            }
        ]
        
        # V3 Pool ABI
        self.v3_pool_abi = [
            {
                "constant": True,
                "inputs": [],
                "name": "slot0",
                "outputs": [
                    {"name": "sqrtPriceX96", "type": "uint160"},
                    {"name": "tick", "type": "int24"},
                    {"name": "observationIndex", "type": "uint16"},
                    {"name": "observationCardinality", "type": "uint16"},
                    {"name": "observationCardinalityNext", "type": "uint16"},
                    {"name": "feeProtocol", "type": "uint8"},
                    {"name": "unlocked", "type": "bool"}
                ],
                "type": "function"
            }
        ]
    
    async def initialize(self):
        """初始化價格抓取器"""
        if not self.session:
            connector = aiohttp.TCPConnector(limit=50, limit_per_host=10)
            timeout = aiohttp.ClientTimeout(total=self.config.RPC_TIMEOUT)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
        # 初始化 Web3 實例
        self.web3_instances = []
        for rpc_url in self.config.BSC_RPC_NODES:
            try:
                w3 = Web3(Web3.HTTPProvider(rpc_url))
                if w3.is_connected():
                    self.web3_instances.append(w3)
                    logger.info(f"✅ 價格抓取器已連接 RPC: {rpc_url}")
            except Exception as e:
                logger.warning(f"⚠️ 價格抓取器無法連接 RPC {rpc_url}: {e}")
        
        if not self.web3_instances:
            raise Exception("❌ 價格抓取器無法連接任何 RPC 節點")
    
    async def start_price_streaming(self):
        """開始價格流抓取"""
        logger.info("🚀 啟動即時價格流抓取...")
        self.is_running = True
        
        while self.is_running:
            try:
                start_time = time.time()
                
                # 批量抓取所有池的價格
                prices = await self._fetch_all_prices()
                
                # 更新快取
                for symbol, price_data in prices.items():
                    # 動態價格異常檢測
                    if self._is_price_anomaly(symbol, price_data['price']):
                        logger.warning(f"⚠️ {symbol} 價格可能異常: ${price_data['price']:.4f}")
                        # 仍然更新，但標記為可能異常
                        price_data['anomaly_detected'] = True
                    else:
                        price_data['anomaly_detected'] = False
                    
                    # 更新價格歷史
                    self._update_price_history(symbol, price_data['price'])
                    
                    self.price_cache[symbol] = {
                        **price_data,
                        'timestamp': datetime.now(),
                        'fetch_time_ms': (time.time() - start_time) * 1000
                    }
                
                fetch_time = (time.time() - start_time) * 1000
                logger.info(f"💰 價格更新完成: {len(prices)} 個交易對, 耗時: {fetch_time:.1f}ms")
                
                # 等待下次更新
                await asyncio.sleep(self.config.PRICE_UPDATE_INTERVAL / 1000)
                
            except Exception as e:
                logger.error(f"❌ 價格抓取異常: {e}")
                await asyncio.sleep(1)  # 出錯時暫停1秒
    
    async def _fetch_all_prices(self) -> Dict[str, Dict]:
        """批量抓取所有價格"""
        tasks = []
        
        for symbol, pool_info in self.main_pools.items():
            task = self._fetch_single_price(symbol, pool_info)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for i, result in enumerate(results):
            symbol = list(self.main_pools.keys())[i]
            if not isinstance(result, Exception) and result:
                prices[symbol] = result
            else:
                logger.warning(f"⚠️ {symbol} 價格抓取失敗: {result}")
        
        return prices
    
    async def _fetch_single_price(self, symbol: str, pool_info: Dict) -> Optional[Dict]:
        """抓取單個池的價格"""
        try:
            if pool_info['version'] == 'V2':
                return await self._fetch_v2_price(symbol, pool_info)
            elif pool_info['version'] == 'V3':
                return await self._fetch_v3_price(symbol, pool_info)
        except Exception as e:
            logger.debug(f"❌ {symbol} 價格抓取失敗: {e}")
            return None
    
    async def _fetch_v2_price(self, symbol: str, pool_info: Dict) -> Optional[Dict]:
        """抓取 V2 池價格"""
        for w3 in self.web3_instances:
            try:
                pair = w3.eth.contract(
                    address=to_checksum_address(pool_info['address']),
                    abi=self.v2_pair_abi
                )
                
                reserves = pair.functions.getReserves().call()
                reserve0, reserve1 = reserves[0], reserves[1]
                
                # 確定 USDT 是 token0 還是 token1
                token0_is_usdt = (
                    to_checksum_address(pool_info['token0']) == 
                    to_checksum_address(self.config.USDT_ADDRESS)
                )
                
                # 獲取代幣符號（移除USDT後綴）
                clean_symbol = symbol.replace('USDT', '')
                
                # 獲取代幣和USDT的小數位數
                token_decimals = self.config.get_token_decimals(clean_symbol)
                usdt_decimals = self.config.get_usdt_decimals()
                
                if token0_is_usdt:
                    # USDT 是 token0，代幣是 token1
                    usdt_amount = reserve0 / (10 ** usdt_decimals)
                    token_amount = reserve1 / (10 ** token_decimals)
                    price = usdt_amount / token_amount
                else:
                    # 代幣是 token0，USDT 是 token1
                    token_amount = reserve0 / (10 ** token_decimals)
                    usdt_amount = reserve1 / (10 ** usdt_decimals)
                    price = usdt_amount / token_amount
                
                # 動態價格檢查（只檢查是否為正數和非零）
                if price > 0 and price < float('inf'):
                    return {
                        'price': price,
                        'reserve0': reserve0,
                        'reserve1': reserve1,
                        'pool_address': pool_info['address'],
                        'version': 'V2',
                        'token0_is_usdt': token0_is_usdt,
                        'token_decimals': token_decimals,
                        'usdt_decimals': usdt_decimals
                    }
                else:
                    logger.warning(f"⚠️ {symbol} V2 價格無效: {price}")
                    return None
                    
            except Exception as e:
                continue
        
        return None
    
    async def _fetch_v3_price(self, symbol: str, pool_info: Dict) -> Optional[Dict]:
        """抓取 V3 池價格"""
        for w3 in self.web3_instances:
            try:
                pool = w3.eth.contract(
                    address=to_checksum_address(pool_info['address']),
                    abi=self.v3_pool_abi
                )
                
                slot0 = pool.functions.slot0().call()
                sqrt_price_x96 = slot0[0]
                
                if sqrt_price_x96 == 0:
                    continue
                
                # 計算價格
                price_raw = (sqrt_price_x96 ** 2) / (2 ** 192)
                
                # 確定 USDT 是 token0 還是 token1
                token0_is_usdt = (
                    to_checksum_address(pool_info['token0']) == 
                    to_checksum_address(self.config.USDT_ADDRESS)
                )
                
                if token0_is_usdt:
                    # USDT 是 token0，需要倒數
                    price = 1 / price_raw
                else:
                    # 代幣是 token0
                    price = price_raw
                
                # 動態價格檢查（只檢查是否為正數和非零）
                if price > 0 and price < float('inf'):
                    return {
                        'price': price,
                        'sqrt_price_x96': sqrt_price_x96,
                        'pool_address': pool_info['address'],
                        'version': 'V3',
                        'fee_tier': pool_info['fee_tier'],
                        'token0_is_usdt': token0_is_usdt
                    }
                else:
                    logger.warning(f"⚠️ {symbol} V3 價格無效: {price}")
                    return None
                    
            except Exception as e:
                continue
        
        return None
    
    def _is_price_anomaly(self, symbol: str, current_price: float) -> bool:
        """動態價格異常檢測"""
        if symbol not in self.price_history:
            return False  # 沒有歷史數據，無法判斷
        
        recent_prices = [price for timestamp, price in self.price_history[symbol][-10:]]  # 最近10個價格
        
        if len(recent_prices) < 3:
            return False  # 數據不足
        
        # 計算平均價格
        avg_price = sum(recent_prices) / len(recent_prices)
        
        # 計算變動幅度
        if avg_price > 0:
            change_ratio = abs(current_price - avg_price) / avg_price
            return change_ratio > self.config.PRICE_VOLATILITY_THRESHOLD
        
        return False
    
    def _update_price_history(self, symbol: str, price: float):
        """更新價格歷史"""
        now = datetime.now()
        
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        # 添加新價格
        self.price_history[symbol].append((now, price))
        
        # 清理過期數據（保留最近5分鐘）
        cutoff_time = now - timedelta(seconds=self.config.PRICE_CACHE_DURATION)
        self.price_history[symbol] = [
            (timestamp, price) for timestamp, price in self.price_history[symbol]
            if timestamp > cutoff_time
        ]
        
        # 限制最大數量（最多保留100條記錄）
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
    
    def _is_price_reasonable(self, symbol: str, price: float) -> bool:
        """基本價格合理性檢查（移除靜態範圍）"""
        # 只檢查是否為正數和非無限大
        return price > 0 and price < float('inf') and not (price != price)  # 檢查 NaN
    
    async def get_live_price(self, symbol: str) -> Optional[float]:
        """獲取即時價格"""
        price_data = self.price_cache.get(symbol)
        if price_data:
            return price_data['price']
        return None
    
    async def get_price_data(self, symbol: str) -> Optional[Dict]:
        """獲取完整價格數據"""
        return self.price_cache.get(symbol)
    
    async def get_all_prices(self) -> Dict[str, float]:
        """獲取所有即時價格"""
        return {
            symbol: data['price'] 
            for symbol, data in self.price_cache.items()
            if 'price' in data
        }
    
    def stop_streaming(self):
        """停止價格流"""
        logger.info("🛑 停止即時價格流抓取...")
        self.is_running = False
    
    async def close(self):
        """關閉連接"""
        self.stop_streaming()
        if self.session:
            await self.session.close()
            self.session = None
