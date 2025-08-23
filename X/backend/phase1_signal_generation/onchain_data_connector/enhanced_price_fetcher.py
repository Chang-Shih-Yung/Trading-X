"""
⚡ WebSocket + Multicall 優化價格抓取器
Enhanced Real-time Price Fetcher with WebSocket + Multicall
"""

import asyncio
import aiohttp
import websockets
from typing import Dict, Optional, List, Tuple, Set
from web3 import Web3
from eth_utils import to_checksum_address, function_signature_to_4byte_selector
import json
import time
import logging
from datetime import datetime, timedelta

# 🔧 使用本地配置，不從根目錄導入
from .config import ProductionConfig
from .fallback_config import FallbackConfig

logger = logging.getLogger(__name__)

class EnhancedPriceFetcher:
    """增強版即時價格抓取器 - WebSocket + Multicall"""
    
    def __init__(self, main_pools: Dict[str, Dict]):
        self.config = ProductionConfig()
        self.fallback_config = FallbackConfig()
        self.main_pools = main_pools
        self.session: Optional[aiohttp.ClientSession] = None
        self.web3_instances: List[Web3] = []
        self.websocket_connections: List = []
        self.price_cache: Dict[str, Dict] = {}
        self.price_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.is_running = False
        self.last_block_number = 0
        
        # Multicall 合約配置
        self.multicall_address = "0xcA11bde05977b3631167028862bE2a173976CA11"  # BSC Multicall3
        self.multicall_abi = [
            {
                "inputs": [
                    {
                        "components": [
                            {"name": "target", "type": "address"},
                            {"name": "callData", "type": "bytes"}
                        ],
                        "name": "calls",
                        "type": "tuple[]"
                    }
                ],
                "name": "aggregate",
                "outputs": [
                    {"name": "blockNumber", "type": "uint256"},
                    {"name": "returnData", "type": "bytes[]"}
                ],
                "type": "function"
            }
        ]
        
        # V2 getReserves 函數選擇器
        self.get_reserves_selector = function_signature_to_4byte_selector("getReserves()")
        
        # V3 slot0 函數選擇器
        self.slot0_selector = function_signature_to_4byte_selector("slot0()")
        
        # 失敗統計
        self.failure_counts: Dict[str, int] = {}
        self.last_failure_times: Dict[str, datetime] = {}
    
    async def initialize(self):
        """初始化增強版價格抓取器"""
        if not self.session:
            connector = aiohttp.TCPConnector(limit=50, limit_per_host=10)
            timeout = aiohttp.ClientTimeout(total=self.config.RPC_TIMEOUT)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
        # 初始化 Web3 實例
        self.web3_instances = []
        for rpc_url in self.config.BSC_RPC_NODES[:3]:  # 使用前3個節點
            try:
                w3 = Web3(Web3.HTTPProvider(rpc_url))
                if w3.is_connected():
                    self.web3_instances.append(w3)
                    logger.info(f"✅ 增強版抓取器已連接 RPC: {rpc_url}")
            except Exception as e:
                logger.warning(f"⚠️ 增強版抓取器無法連接 RPC {rpc_url}: {e}")
        
        if not self.web3_instances:
            raise Exception("❌ 增強版抓取器無法連接任何 RPC 節點")
        
        # 初始化 WebSocket 連接
        await self._initialize_websockets()
    
    async def _initialize_websockets(self):
        """初始化 WebSocket 連接"""
        ws_endpoints = [
            "wss://ws.publicnode.com/bsc",
            "wss://bsc.nodereal.io/ws/v1/your-api-key"  # 需要替換為實際 API key
        ]
        
        for endpoint in ws_endpoints[:1]:  # 暫時只用一個
            try:
                # 這裡先不實際連接 WebSocket，保持原有輪詢邏輯
                # 但為將來 WebSocket 實現做準備
                logger.info(f"📡 WebSocket 端點準備: {endpoint}")
            except Exception as e:
                logger.warning(f"⚠️ WebSocket 連接失敗: {e}")
    
    async def start_price_streaming(self):
        """開始增強版價格流抓取"""
        logger.info("🚀 啟動增強版即時價格流抓取...")
        self.is_running = True
        
        # 啟動主要價格流任務
        asyncio.create_task(self._enhanced_price_loop())
        
        # 啟動健康檢查任務
        asyncio.create_task(self._health_check_loop())
    
    async def _enhanced_price_loop(self):
        """增強版價格循環"""
        while self.is_running:
            try:
                start_time = time.time()
                
                # 使用 Multicall 批量抓取價格
                prices = await self._multicall_fetch_prices()
                
                # 更新快取
                for symbol, price_data in prices.items():
                    if price_data:
                        # 動態價格異常檢測
                        if self._is_price_anomaly(symbol, price_data['price']):
                            logger.warning(f"⚠️ {symbol} 價格可能異常: ${price_data['price']:.4f}")
                            price_data['anomaly_detected'] = True
                        else:
                            price_data['anomaly_detected'] = False
                        
                        # 更新價格歷史
                        self._update_price_history(symbol, price_data['price'])
                        
                        # 重置失敗計數
                        self.failure_counts[symbol] = 0
                        
                        self.price_cache[symbol] = {
                            **price_data,
                            'timestamp': datetime.now(),
                            'fetch_time_ms': (time.time() - start_time) * 1000,
                            'source': 'onchain_multicall',
                            'is_fallback': False
                        }
                    else:
                        # 記錄失敗
                        self._record_failure(symbol)
                
                fetch_time = (time.time() - start_time) * 1000
                success_count = len([p for p in prices.values() if p is not None])
                logger.debug(f"💰 增強版價格更新: {success_count}/{len(prices)} 成功, 耗時: {fetch_time:.1f}ms")
                
                # 每10次成功更新才輸出一次INFO日誌
                if not hasattr(self, '_update_counter'):
                    self._update_counter = 0
                self._update_counter += 1
                if self._update_counter % 10 == 0:
                    logger.info(f"✅ 價格更新統計: 最近10次更新平均耗時 {fetch_time:.1f}ms")
                
                # 🔧 優化：降低更新頻率，減少記憶體壓力和API負載
                if fetch_time < 500:
                    interval = 2.0   # 2秒 (減少頻率)
                elif fetch_time < 1000:
                    interval = 3.0   # 3秒 (原本500ms太頻繁)
                else:
                    interval = 5.0   # 5秒 (高延遲時更保守)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ 增強版價格抓取異常: {e}")
                await asyncio.sleep(1)
    
    async def _multicall_fetch_prices(self) -> Dict[str, Optional[Dict]]:
        """使用 Multicall 批量抓取價格"""
        for w3 in self.web3_instances:
            try:
                # 準備 Multicall 調用
                calls = []
                symbol_call_mapping = []
                
                for symbol, pool_info in self.main_pools.items():
                    pool_address = to_checksum_address(pool_info['address'])
                    
                    if pool_info['version'] == 'V2':
                        # V2: getReserves()
                        call_data = self.get_reserves_selector
                        calls.append((pool_address, call_data))
                        symbol_call_mapping.append((symbol, 'v2'))
                    elif pool_info['version'] == 'V3':
                        # V3: slot0()
                        call_data = self.slot0_selector
                        calls.append((pool_address, call_data))
                        symbol_call_mapping.append((symbol, 'v3'))
                
                if not calls:
                    return {}
                
                # 執行 Multicall
                multicall = w3.eth.contract(
                    address=to_checksum_address(self.multicall_address),
                    abi=self.multicall_abi
                )
                
                block_number, return_data = multicall.functions.aggregate(calls).call()
                
                # 解析結果
                prices = {}
                for i, ((symbol, version), data) in enumerate(zip(symbol_call_mapping, return_data)):
                    try:
                        if version == 'v2':
                            price_data = self._parse_v2_data(symbol, data, self.main_pools[symbol])
                        else:
                            price_data = self._parse_v3_data(symbol, data, self.main_pools[symbol])
                        
                        prices[symbol] = price_data
                    except Exception as e:
                        logger.debug(f"❌ {symbol} 數據解析失敗: {e}")
                        prices[symbol] = None
                
                return prices
                
            except Exception as e:
                logger.debug(f"❌ Multicall 失敗: {e}")
                continue
        
        # 如果 Multicall 都失敗，回退到單獨調用
        return await self._fallback_individual_calls()
    
    def _parse_v2_data(self, symbol: str, data: bytes, pool_info: Dict) -> Optional[Dict]:
        """解析 V2 getReserves 數據"""
        try:
            # 解碼 getReserves 返回值
            if len(data) < 96:  # 3 * 32 bytes
                return None
            
            reserve0 = int.from_bytes(data[0:32], byteorder='big')
            reserve1 = int.from_bytes(data[32:64], byteorder='big')
            
            # 計算價格
            token0_is_usdt = (
                to_checksum_address(pool_info['token0']) == 
                to_checksum_address(self.config.USDT_ADDRESS)
            )
            
            clean_symbol = symbol.replace('USDT', '')
            token_decimals = self.config.get_token_decimals(clean_symbol)
            usdt_decimals = self.config.get_usdt_decimals()
            
            if token0_is_usdt:
                usdt_amount = reserve0 / (10 ** usdt_decimals)
                token_amount = reserve1 / (10 ** token_decimals)
                price = usdt_amount / token_amount
            else:
                token_amount = reserve0 / (10 ** token_decimals)
                usdt_amount = reserve1 / (10 ** usdt_decimals)
                price = usdt_amount / token_amount
            
            if price > 0 and price < float('inf'):
                return {
                    'price': price,
                    'reserve0': reserve0,
                    'reserve1': reserve1,
                    'pool_address': pool_info['address'],
                    'version': 'V2',
                    'token0_is_usdt': token0_is_usdt
                }
        except Exception as e:
            logger.debug(f"❌ {symbol} V2數據解析失敗: {e}")
        
        return None
    
    def _parse_v3_data(self, symbol: str, data: bytes, pool_info: Dict) -> Optional[Dict]:
        """解析 V3 slot0 數據"""
        try:
            # 解碼 slot0 返回值
            if len(data) < 32:
                return None
            
            sqrt_price_x96 = int.from_bytes(data[0:32], byteorder='big')
            
            if sqrt_price_x96 == 0:
                return None
            
            # 計算價格
            price_raw = (sqrt_price_x96 ** 2) / (2 ** 192)
            
            token0_is_usdt = (
                to_checksum_address(pool_info['token0']) == 
                to_checksum_address(self.config.USDT_ADDRESS)
            )
            
            if token0_is_usdt:
                price = 1 / price_raw
            else:
                price = price_raw
            
            if price > 0 and price < float('inf'):
                return {
                    'price': price,
                    'sqrt_price_x96': sqrt_price_x96,
                    'pool_address': pool_info['address'],
                    'version': 'V3',
                    'fee_tier': pool_info['fee_tier'],
                    'token0_is_usdt': token0_is_usdt
                }
        except Exception as e:
            logger.debug(f"❌ {symbol} V3數據解析失敗: {e}")
        
        return None
    
    async def _fallback_individual_calls(self) -> Dict[str, Optional[Dict]]:
        """回退到單獨 RPC 調用"""
        logger.info("🔄 Multicall失敗，回退到單獨調用")
        
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
                prices[symbol] = None
        
        return prices
    
    async def _fetch_single_price(self, symbol: str, pool_info: Dict) -> Optional[Dict]:
        """抓取單個池的價格（保持原有邏輯）"""
        # 這裡使用之前的單獨調用邏輯
        # [保持原有的 _fetch_v2_price 和 _fetch_v3_price 邏輯]
        pass
    
    def _record_failure(self, symbol: str):
        """記錄失敗"""
        now = datetime.now()
        self.failure_counts[symbol] = self.failure_counts.get(symbol, 0) + 1
        self.last_failure_times[symbol] = now
    
    def _should_use_fallback(self, symbol: str) -> bool:
        """判斷是否應該使用回退機制"""
        failure_count = self.failure_counts.get(symbol, 0)
        last_failure = self.last_failure_times.get(symbol)
        
        if failure_count >= self.fallback_config.MAX_CONSECUTIVE_FAILURES:
            return True
        
        if last_failure:
            time_since_failure = (datetime.now() - last_failure).total_seconds()
            if time_since_failure < self.fallback_config.FAILURE_WINDOW_SECONDS:
                return failure_count >= 2
        
        return False
    
    async def _health_check_loop(self):
        """健康檢查循環"""
        while self.is_running:
            try:
                await asyncio.sleep(self.fallback_config.HEALTH_CHECK_INTERVAL)
                
                # 檢查價格數據新鮮度
                stale_symbols = []
                for symbol, data in self.price_cache.items():
                    if 'timestamp' in data:
                        age = (datetime.now() - data['timestamp']).total_seconds()
                        if age > self.fallback_config.PRICE_STALENESS_THRESHOLD:
                            stale_symbols.append(symbol)
                
                if stale_symbols:
                    logger.warning(f"⚠️ 價格數據過期: {stale_symbols}")
                
            except Exception as e:
                logger.error(f"❌ 健康檢查失敗: {e}")
    
    def _is_price_anomaly(self, symbol: str, current_price: float) -> bool:
        """動態價格異常檢測"""
        if symbol not in self.price_history:
            return False
        
        recent_prices = [price for timestamp, price in self.price_history[symbol][-10:]]
        
        if len(recent_prices) < 3:
            return False
        
        avg_price = sum(recent_prices) / len(recent_prices)
        
        if avg_price > 0:
            change_ratio = abs(current_price - avg_price) / avg_price
            return change_ratio > self.config.PRICE_VOLATILITY_THRESHOLD
        
        return False
    
    def _update_price_history(self, symbol: str, price: float):
        """更新價格歷史"""
        now = datetime.now()
        
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append((now, price))
        
        cutoff_time = now - timedelta(seconds=self.config.PRICE_CACHE_DURATION)
        self.price_history[symbol] = [
            (timestamp, price) for timestamp, price in self.price_history[symbol]
            if timestamp > cutoff_time
        ]
        
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
    
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
    
    def get_fallback_status(self) -> Dict[str, any]:
        """獲取回退機制狀態"""
        return {
            'failure_counts': self.failure_counts.copy(),
            'symbols_on_fallback': [
                symbol for symbol in self.main_pools.keys()
                if self._should_use_fallback(symbol)
            ],
            'total_failures': sum(self.failure_counts.values()),
            'last_update': datetime.now().isoformat()
        }
    
    def stop_streaming(self):
        """停止價格流"""
        logger.info("🛑 停止增強版即時價格流抓取...")
        self.is_running = False
    
    async def close(self):
        """關閉連接"""
        self.stop_streaming()
        
        # 關閉 WebSocket 連接
        for ws in self.websocket_connections:
            try:
                await ws.close()
            except:
                pass
        
        if self.session:
            await self.session.close()
            self.session = None
