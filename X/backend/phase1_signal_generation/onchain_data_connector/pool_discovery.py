"""
🏭 主池發現引擎 - 產品級實現
Production-Grade Pool Discovery Engine
自動發現PancakeSwap V2/V3最高流動性主池
"""

import asyncio
import aiohttp
from typing import Dict, Optional, Tuple, List
from web3 import Web3
from eth_utils import to_checksum_address
import logging
from datetime import datetime, timedelta

# 🔧 統一配置：使用 config.py 的完整 ProductionConfig，確保所有調用一致
from .config import ProductionConfig

logger = logging.getLogger(__name__)

class PoolDiscoveryEngine:
    """主池發現引擎"""
    
    def __init__(self):
        self.config = ProductionConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.web3_instances: List[Web3] = []
        self.pool_cache: Dict[str, Dict] = {}
        self.last_discovery_time: Optional[datetime] = None
        
        # ABI 定義
        self.v2_factory_abi = [
            {
                "constant": True,
                "inputs": [
                    {"name": "tokenA", "type": "address"},
                    {"name": "tokenB", "type": "address"}
                ],
                "name": "getPair",
                "outputs": [{"name": "pair", "type": "address"}],
                "type": "function"
            }
        ]
        
        self.v3_factory_abi = [
            {
                "constant": True,
                "inputs": [
                    {"name": "tokenA", "type": "address"},
                    {"name": "tokenB", "type": "address"},
                    {"name": "fee", "type": "uint24"}
                ],
                "name": "getPool",
                "outputs": [{"name": "pool", "type": "address"}],
                "type": "function"
            }
        ]
        
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
            },
            {
                "constant": True,
                "inputs": [],
                "name": "liquidity",
                "outputs": [{"name": "", "type": "uint128"}],
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
    
    async def initialize(self):
        """初始化連接池"""
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
                    logger.info(f"✅ 已連接 RPC 節點: {rpc_url}")
            except Exception as e:
                logger.warning(f"⚠️ 無法連接 RPC 節點 {rpc_url}: {e}")
        
        if not self.web3_instances:
            raise Exception("❌ 無法連接任何 RPC 節點")
    
    async def discover_main_pools(self) -> Dict[str, Dict]:
        """發現所有七大幣種的主池"""
        logger.info("🔍 開始主池發現流程...")
        
        main_pools = {}
        
        for symbol in self.config.SUPPORTED_SYMBOLS:
            try:
                pool_info = await self._discover_symbol_main_pool(symbol)
                if pool_info:
                    main_pools[f"{symbol}USDT"] = pool_info
                    logger.info(f"✅ {symbol}USDT 主池發現: {pool_info['address']} ({pool_info['version']})")
                else:
                    logger.error(f"❌ {symbol}USDT 主池發現失敗")
            except Exception as e:
                logger.error(f"❌ {symbol}USDT 主池發現異常: {e}")
        
        self.pool_cache = main_pools
        self.last_discovery_time = datetime.now()
        
        logger.info(f"🎉 主池發現完成，共發現 {len(main_pools)} 個主池")
        return main_pools
    
    async def _discover_symbol_main_pool(self, symbol: str) -> Optional[Dict]:
        """發現單個幣種的主池"""
        token_address = self.config.get_token_address(symbol)
        if not token_address:
            logger.error(f"❌ 找不到 {symbol} 的代幣地址")
            return None
        
        usdt_address = self.config.USDT_ADDRESS
        
        # 嘗試 V3 池（優先，因為通常流動性更高）
        v3_pool = await self._find_best_v3_pool(token_address, usdt_address)
        
        # 嘗試 V2 池
        v2_pool = await self._find_v2_pool(token_address, usdt_address)
        
        # 比較流動性，選擇最佳池
        pools = []
        if v3_pool:
            pools.append(v3_pool)
        if v2_pool:
            pools.append(v2_pool)
        
        if not pools:
            return None
        
        # 選擇流動性最高的池
        best_pool = max(pools, key=lambda p: p['liquidity_usdt'])
        
        # 使用動態流動性判斷
        if not self.config.is_liquidity_acceptable(best_pool['liquidity_usdt'], symbol):
            logger.warning(f"⚠️ {symbol} 最佳池流動性較低: {best_pool['liquidity_usdt']:.2f} USDT，但仍可使用")
        
        # 計算流動性評分
        liquidity_score = self.config.get_liquidity_score(best_pool['liquidity_usdt'])
        best_pool['liquidity_score'] = liquidity_score
        
        logger.info(f"💧 {symbol} 流動性評分: {liquidity_score:.3f}")
        
        return best_pool
    
    async def _find_best_v3_pool(self, token_address: str, usdt_address: str) -> Optional[Dict]:
        """尋找最佳 V3 池"""
        best_pool = None
        max_liquidity = 0
        
        for fee_tier in self.config.V3_FEE_TIERS:
            try:
                pool_address = await self._get_v3_pool_address(token_address, usdt_address, fee_tier)
                if pool_address and pool_address != "0x0000000000000000000000000000000000000000":
                    liquidity_info = await self._get_v3_pool_liquidity(pool_address, token_address, usdt_address)
                    if liquidity_info and liquidity_info['liquidity_usdt'] > max_liquidity:
                        max_liquidity = liquidity_info['liquidity_usdt']
                        best_pool = {
                            'address': pool_address,
                            'version': 'V3',
                            'fee_tier': fee_tier,
                            'token0': liquidity_info['token0'],
                            'token1': liquidity_info['token1'],
                            'liquidity_usdt': liquidity_info['liquidity_usdt'],
                            'sqrt_price_x96': liquidity_info.get('sqrt_price_x96', 0)
                        }
            except Exception as e:
                logger.debug(f"V3 池 fee_tier {fee_tier} 檢查失敗: {e}")
        
        return best_pool
    
    async def _find_v2_pool(self, token_address: str, usdt_address: str) -> Optional[Dict]:
        """尋找 V2 池"""
        try:
            pool_address = await self._get_v2_pool_address(token_address, usdt_address)
            if pool_address and pool_address != "0x0000000000000000000000000000000000000000":
                liquidity_info = await self._get_v2_pool_liquidity(pool_address, token_address, usdt_address)
                if liquidity_info:
                    return {
                        'address': pool_address,
                        'version': 'V2',
                        'token0': liquidity_info['token0'],
                        'token1': liquidity_info['token1'],
                        'liquidity_usdt': liquidity_info['liquidity_usdt'],
                        'reserve0': liquidity_info['reserve0'],
                        'reserve1': liquidity_info['reserve1']
                    }
        except Exception as e:
            logger.debug(f"V2 池檢查失敗: {e}")
        
        return None
    
    async def _get_v3_pool_address(self, token_a: str, token_b: str, fee: int) -> Optional[str]:
        """從 V3 Factory 獲取池地址"""
        for w3 in self.web3_instances:
            try:
                factory = w3.eth.contract(
                    address=to_checksum_address(self.config.PANCAKE_V3_FACTORY),
                    abi=self.v3_factory_abi
                )
                
                pool_address = factory.functions.getPool(
                    to_checksum_address(token_a),
                    to_checksum_address(token_b),
                    fee
                ).call()
                
                return pool_address
            except Exception as e:
                continue
        
        return None
    
    async def _get_v2_pool_address(self, token_a: str, token_b: str) -> Optional[str]:
        """從 V2 Factory 獲取池地址"""
        for w3 in self.web3_instances:
            try:
                factory = w3.eth.contract(
                    address=to_checksum_address(self.config.PANCAKE_V2_FACTORY),
                    abi=self.v2_factory_abi
                )
                
                pair_address = factory.functions.getPair(
                    to_checksum_address(token_a),
                    to_checksum_address(token_b)
                ).call()
                
                return pair_address
            except Exception as e:
                continue
        
        return None
    
    async def _get_v3_pool_liquidity(self, pool_address: str, token_a: str, token_b: str) -> Optional[Dict]:
        """獲取 V3 池流動性信息"""
        for w3 in self.web3_instances:
            try:
                pool = w3.eth.contract(
                    address=to_checksum_address(pool_address),
                    abi=self.v3_pool_abi
                )
                
                # 獲取池信息
                token0 = pool.functions.token0().call()
                token1 = pool.functions.token1().call()
                liquidity = pool.functions.liquidity().call()
                slot0 = pool.functions.slot0().call()
                sqrt_price_x96 = slot0[0]
                
                # V3 池流動性計算需要考慮價格範圍和代幣餘額
                # 這裡使用簡化方法：直接查詢池中代幣餘額
                try:
                    # 獲取池中代幣餘額
                    usdt_contract = w3.eth.contract(
                        address=to_checksum_address(self.config.USDT_ADDRESS),
                        abi=[{
                            "constant": True,
                            "inputs": [{"name": "_owner", "type": "address"}],
                            "name": "balanceOf",
                            "outputs": [{"name": "balance", "type": "uint256"}],
                            "type": "function"
                        }]
                    )
                    
                    usdt_balance = usdt_contract.functions.balanceOf(pool_address).call()
                    liquidity_usdt = (usdt_balance / (10 ** 6)) * 2  # USDT 餘額 * 2 作為總流動性估算
                    
                except Exception:
                    # 回退到原始方法
                    if sqrt_price_x96 > 0:
                        # 估算流動性（使用更保守的計算）
                        liquidity_usdt = liquidity / (10 ** 12)  # 更保守的估算
                    
                    return {
                        'token0': token0,
                        'token1': token1,
                        'liquidity_usdt': liquidity_usdt,
                        'sqrt_price_x96': sqrt_price_x96
                    }
            except Exception as e:
                continue
        
        return None
    
    async def _get_v2_pool_liquidity(self, pool_address: str, token_a: str, token_b: str) -> Optional[Dict]:
        """獲取 V2 池流動性信息"""
        for w3 in self.web3_instances:
            try:
                pair = w3.eth.contract(
                    address=to_checksum_address(pool_address),
                    abi=self.v2_pair_abi
                )
                
                # 獲取池信息
                token0 = pair.functions.token0().call()
                token1 = pair.functions.token1().call()
                reserves = pair.functions.getReserves().call()
                reserve0, reserve1 = reserves[0], reserves[1]
                
                # 計算 USDT 流動性（USDT 是 6 位小數）
                if to_checksum_address(token0) == to_checksum_address(self.config.USDT_ADDRESS):
                    liquidity_usdt = reserve0 / (10 ** 6) * 2  # USDT 是 6 位小數
                elif to_checksum_address(token1) == to_checksum_address(self.config.USDT_ADDRESS):
                    liquidity_usdt = reserve1 / (10 ** 6) * 2  # USDT 是 6 位小數
                else:
                    # 如果都不是 USDT，估算流動性（需要更複雜的邏輯）
                    liquidity_usdt = max(reserve0, reserve1) / (10 ** 6)  # 假設是 USDT 等價
                
                return {
                    'token0': token0,
                    'token1': token1,
                    'liquidity_usdt': liquidity_usdt,
                    'reserve0': reserve0,
                    'reserve1': reserve1
                }
            except Exception as e:
                continue
        
        return None
    
    def should_rediscover(self) -> bool:
        """檢查是否需要重新發現主池"""
        if not self.last_discovery_time:
            return True
        
        elapsed = datetime.now() - self.last_discovery_time
        return elapsed.total_seconds() >= self.config.POOL_DISCOVERY_INTERVAL
    
    async def get_main_pools(self) -> Dict[str, Dict]:
        """獲取主池（帶自動重新發現）"""
        if self.should_rediscover():
            logger.info("⏰ 觸發主池重新發現...")
            return await self.discover_main_pools()
        else:
            return self.pool_cache
    
    async def close(self):
        """關閉連接"""
        if self.session:
            await self.session.close()
            self.session = None
