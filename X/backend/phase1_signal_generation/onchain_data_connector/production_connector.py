"""
🎯 產品級鏈上價格連接器 - 主模塊
Production-Grade Onchain Price Connector
整合主池發現 + 即時價格抓取，符合 Phase1 Schema
"""

import asyncio
from typing import Dict, Optional, List
import logging
from datetime import datetime

# 🔧 使用本地配置，不從根目錄導入
from .config import ProductionConfig
from .pool_discovery import PoolDiscoveryEngine
from .price_fetcher import RealTimePriceFetcher

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionOnChainPriceConnector:
    """產品級鏈上價格連接器"""
    
    def __init__(self):
        self.config = ProductionConfig()
        self.pool_discovery = PoolDiscoveryEngine()
        self.price_fetcher: Optional[RealTimePriceFetcher] = None
        self.main_pools: Dict[str, Dict] = {}
        self.is_initialized = False
        self.is_streaming = False
        
        logger.info("🚀 產品級鏈上價格連接器已創建")
    
    async def initialize(self):
        """初始化連接器"""
        logger.info("⚡ 初始化產品級鏈上價格連接器...")
        
        # 1. 初始化主池發現引擎
        await self.pool_discovery.initialize()
        
        # 2. 發現所有主池
        logger.info("🔍 開始發現七大幣種主池...")
        self.main_pools = await self.pool_discovery.discover_main_pools()
        
        if not self.main_pools:
            raise Exception("❌ 無法發現任何主池")
        
        logger.info(f"✅ 成功發現 {len(self.main_pools)} 個主池:")
        for symbol, pool_info in self.main_pools.items():
            logger.info(f"   💰 {symbol}: {pool_info['address']} ({pool_info['version']})")
        
        # 3. 初始化價格抓取器
        self.price_fetcher = RealTimePriceFetcher(self.main_pools)
        await self.price_fetcher.initialize()
        
        self.is_initialized = True
        logger.info("🎉 產品級鏈上價格連接器初始化完成")
    
    async def start_price_streaming(self):
        """開始價格流"""
        if not self.is_initialized:
            await self.initialize()
        
        if not self.price_fetcher:
            raise Exception("❌ 價格抓取器未初始化")
        
        logger.info("🚀 啟動產品級價格流...")
        self.is_streaming = True
        
        # 啟動價格流（背景任務）
        asyncio.create_task(self.price_fetcher.start_price_streaming())
        
        # 等待首次價格數據
        await asyncio.sleep(1)
        logger.info("✅ 產品級價格流已啟動")
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """
        獲取即時價格 (Phase1 Schema 兼容)
        Args:
            symbol: 交易對符號，如 'BTCUSDT'
        Returns:
            價格 (float) 或 None
        """
        if not self.is_streaming or not self.price_fetcher:
            logger.warning(f"⚠️ 價格流未啟動，無法獲取 {symbol} 價格")
            return None
        
        # 符合 Phase1 Schema: 支援 BTC -> BTCUSDT 轉換
        if symbol in self.config.SUPPORTED_SYMBOLS:
            symbol = f"{symbol}USDT"
        
        price = await self.price_fetcher.get_live_price(symbol)
        
        if price is None:
            logger.warning(f"⚠️ 無法獲取 {symbol} 價格")
        
        return price
    
    async def get_price_data(self, symbol: str) -> Optional[Dict]:
        """
        獲取完整價格數據
        Returns:
            包含價格、池信息、時間戳等的完整數據
        """
        if not self.is_streaming or not self.price_fetcher:
            return None
        
        # 符合 Phase1 Schema: 支援 BTC -> BTCUSDT 轉換
        if symbol in self.config.SUPPORTED_SYMBOLS:
            symbol = f"{symbol}USDT"
        
        return await self.price_fetcher.get_price_data(symbol)
    
    async def get_all_prices(self) -> Dict[str, float]:
        """
        獲取所有支援幣種的即時價格
        Returns:
            {symbol: price} 格式的字典
        """
        if not self.is_streaming or not self.price_fetcher:
            return {}
        
        return await self.price_fetcher.get_all_prices()
    
    async def get_supported_symbols(self) -> List[str]:
        """獲取支援的交易對"""
        return self.config.get_symbol_pairs()
    
    async def refresh_pools(self):
        """手動刷新主池"""
        logger.info("🔄 手動刷新主池...")
        
        if not self.pool_discovery:
            logger.error("❌ 主池發現引擎未初始化")
            return
        
        # 停止當前價格流
        if self.price_fetcher:
            self.price_fetcher.stop_streaming()
        
        # 重新發現主池
        new_pools = await self.pool_discovery.discover_main_pools()
        
        if new_pools:
            self.main_pools = new_pools
            
            # 重新初始化價格抓取器
            self.price_fetcher = RealTimePriceFetcher(self.main_pools)
            await self.price_fetcher.initialize()
            
            # 重新啟動價格流
            if self.is_streaming:
                asyncio.create_task(self.price_fetcher.start_price_streaming())
            
            logger.info(f"✅ 主池刷新完成，更新 {len(new_pools)} 個主池")
        else:
            logger.error("❌ 主池刷新失敗")
    
    async def get_pool_info(self) -> Dict[str, Dict]:
        """獲取當前主池信息"""
        return self.main_pools.copy()
    
    async def health_check(self) -> Dict[str, any]:
        """健康檢查"""
        health = {
            'initialized': self.is_initialized,
            'streaming': self.is_streaming,
            'main_pools_count': len(self.main_pools),
            'supported_symbols': len(self.config.SUPPORTED_SYMBOLS),
            'timestamp': datetime.now().isoformat()
        }
        
        if self.price_fetcher:
            prices = await self.price_fetcher.get_all_prices()
            health['active_prices'] = len(prices)
            health['latest_prices'] = list(prices.keys())
        
        return health
    
    async def stop(self):
        """停止連接器"""
        logger.info("🛑 停止產品級鏈上價格連接器...")
        
        self.is_streaming = False
        
        if self.price_fetcher:
            await self.price_fetcher.close()
            self.price_fetcher = None
        
        if self.pool_discovery:
            await self.pool_discovery.close()
        
        self.is_initialized = False
        logger.info("✅ 產品級鏈上價格連接器已停止")
    
    async def __aenter__(self):
        """異步上下文管理器 - 進入"""
        await self.initialize()
        await self.start_price_streaming()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器 - 退出"""
        await self.stop()

# 全局實例（可選）
_global_connector: Optional[ProductionOnChainPriceConnector] = None

async def get_production_connector() -> ProductionOnChainPriceConnector:
    """獲取全局產品級連接器實例"""
    global _global_connector
    
    if _global_connector is None:
        _global_connector = ProductionOnChainPriceConnector()
        await _global_connector.initialize()
        await _global_connector.start_price_streaming()
    
    return _global_connector

async def cleanup_production_connector():
    """清理全局連接器"""
    global _global_connector
    
    if _global_connector:
        await _global_connector.stop()
        _global_connector = None

# Phase1 Schema 兼容性函數
async def get_crypto_price(symbol: str) -> Optional[float]:
    """
    Phase1 Schema 兼容函數
    獲取加密貨幣價格
    """
    connector = await get_production_connector()
    return await connector.get_price(symbol)

async def get_all_crypto_prices() -> Dict[str, float]:
    """
    Phase1 Schema 兼容函數
    獲取所有支援的加密貨幣價格
    """
    connector = await get_production_connector()
    return await connector.get_all_prices()
