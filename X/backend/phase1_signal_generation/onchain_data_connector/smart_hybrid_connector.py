"""
🎯 智能混合價格連接器 - 主模塊
Smart Hybrid Price Connector
鏈上數據為主 + WebSocket 幣安API 智能回退
"""

import asyncio
from typing import Dict, Optional, List
import logging
from datetime import datetime, timedelta

# 🔧 使用本地配置，不從根目錄導入
from .config import ProductionConfig
from .fallback_config import FallbackConfig
from .pool_discovery import PoolDiscoveryEngine
from .enhanced_price_fetcher import EnhancedPriceFetcher

logger = logging.getLogger(__name__)

class SmartHybridPriceConnector:
    """智能混合價格連接器"""
    
    def __init__(self, binance_fallback_connector=None, binance_fallback=None):
        self.config = ProductionConfig()
        self.fallback_config = FallbackConfig()
        self.pool_discovery = PoolDiscoveryEngine()
        self.enhanced_fetcher: Optional[EnhancedPriceFetcher] = None
        # 支援兩種參數名稱以保持兼容性
        self.binance_fallback = binance_fallback_connector or binance_fallback
        self.main_pools: Dict[str, Dict] = {}
        self.is_initialized = False
        self.is_streaming = False
        
        # 回退狀態追蹤
        self.fallback_status: Dict[str, bool] = {}
        self.fallback_start_times: Dict[str, datetime] = {}
        self.recovery_attempts: Dict[str, int] = {}
        
        logger.info("🚀 智能混合價格連接器已創建")
    
    async def initialize(self):
        """初始化智能混合連接器"""
        logger.info("⚡ 初始化智能混合價格連接器...")
        
        # 1. 初始化主池發現引擎
        await self.pool_discovery.initialize()
        
        # 2. 發現所有主池
        logger.info("🔍 開始發現七大幣種主池...")
        self.main_pools = await self.pool_discovery.discover_main_pools()
        
        if not self.main_pools:
            logger.error("❌ 無法發現任何主池，將完全依賴幣安API回退")
            # 即使沒有主池，也要初始化，完全依賴回退機制
        else:
            logger.info(f"✅ 成功發現 {len(self.main_pools)} 個主池:")
            for symbol, pool_info in self.main_pools.items():
                logger.info(f"   💰 {symbol}: {pool_info['address']} ({pool_info['version']})")
        
        # 3. 初始化增強版價格抓取器
        if self.main_pools:
            self.enhanced_fetcher = EnhancedPriceFetcher(self.main_pools)
            await self.enhanced_fetcher.initialize()
        
        # 4. 初始化回退狀態
        for symbol in self.config.SUPPORTED_SYMBOLS:
            symbol_pair = f"{symbol}USDT"
            self.fallback_status[symbol_pair] = False
            self.recovery_attempts[symbol_pair] = 0
        
        self.is_initialized = True
        logger.info("🎉 智能混合價格連接器初始化完成")
    
    async def start_price_streaming(self):
        """開始智能價格流"""
        if not self.is_initialized:
            await self.initialize()
        
        logger.info("🚀 啟動智能混合價格流...")
        self.is_streaming = True
        
        # 啟動主要價格流
        if self.enhanced_fetcher:
            asyncio.create_task(self.enhanced_fetcher.start_price_streaming())
        
        # 啟動智能回退監控
        asyncio.create_task(self._smart_fallback_monitor())
        
        # 啟動恢復檢測
        asyncio.create_task(self._recovery_monitor())
        
        # 等待首次價格數據
        await asyncio.sleep(1)
        logger.info("✅ 智能混合價格流已啟動")
    
    async def _smart_fallback_monitor(self):
        """智能回退監控"""
        while self.is_streaming:
            try:
                await asyncio.sleep(5)  # 每5秒檢查一次
                
                for symbol in self.config.SUPPORTED_SYMBOLS:
                    symbol_pair = f"{symbol}USDT"
                    
                    # 檢查是否需要啟用回退
                    if not self.fallback_status[symbol_pair]:
                        if await self._should_enable_fallback(symbol_pair):
                            await self._enable_fallback(symbol_pair)
                    
                    # 檢查是否可以恢復
                    elif self.fallback_status[symbol_pair]:
                        if await self._should_try_recovery(symbol_pair):
                            await self._try_recovery(symbol_pair)
                
            except Exception as e:
                logger.error(f"❌ 智能回退監控異常: {e}")
                await asyncio.sleep(5)
    
    async def _should_enable_fallback(self, symbol: str) -> bool:
        """判斷是否應該啟用回退機制"""
        if not self.enhanced_fetcher:
            return True  # 沒有鏈上抓取器，直接回退
        
        # 檢查鏈上數據狀態
        fallback_status = self.enhanced_fetcher.get_fallback_status()
        
        # 如果這個幣種在回退列表中，啟用回退
        if symbol in fallback_status.get('symbols_on_fallback', []):
            return True
        
        # 檢查價格數據新鮮度
        price_data = await self.enhanced_fetcher.get_price_data(symbol)
        if not price_data:
            return True
        
        if 'timestamp' in price_data:
            age = (datetime.now() - price_data['timestamp']).total_seconds()
            if age > self.fallback_config.PRICE_STALENESS_THRESHOLD:
                return True
        
        return False
    
    async def _enable_fallback(self, symbol: str):
        """啟用回退機制"""
        logger.warning(f"🔄 {symbol} 啟用幣安API回退機制")
        self.fallback_status[symbol] = True
        self.fallback_start_times[symbol] = datetime.now()
        self.recovery_attempts[symbol] = 0
    
    async def _should_try_recovery(self, symbol: str) -> bool:
        """判斷是否應該嘗試恢復"""
        # 檢查回退時間是否足夠長
        start_time = self.fallback_start_times.get(symbol)
        if start_time:
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed < self.fallback_config.FALLBACK_RETRY_INTERVAL:
                return False
        
        return True
    
    async def _try_recovery(self, symbol: str):
        """嘗試恢復到鏈上數據"""
        if not self.enhanced_fetcher:
            return
        
        self.recovery_attempts[symbol] += 1
        logger.info(f"🔄 {symbol} 嘗試恢復到鏈上數據 (第{self.recovery_attempts[symbol]}次)")
        
        # 測試鏈上數據可用性
        price_data = await self.enhanced_fetcher.get_price_data(symbol)
        
        if price_data and 'price' in price_data:
            # 檢查數據新鮮度
            if 'timestamp' in price_data:
                age = (datetime.now() - price_data['timestamp']).total_seconds()
                if age <= self.fallback_config.PRICE_STALENESS_THRESHOLD:
                    # 恢復成功
                    logger.info(f"✅ {symbol} 成功恢復到鏈上數據")
                    self.fallback_status[symbol] = False
                    if symbol in self.fallback_start_times:
                        del self.fallback_start_times[symbol]
                    self.recovery_attempts[symbol] = 0
                    return
        
        # 恢復失敗，重置回退開始時間
        self.fallback_start_times[symbol] = datetime.now()
    
    async def _recovery_monitor(self):
        """恢復監控"""
        while self.is_streaming:
            try:
                await asyncio.sleep(30)  # 每30秒檢查一次
                
                # 定期重新掃描主池
                if self.pool_discovery.should_rediscover():
                    logger.info("⏰ 定期重新掃描主池...")
                    new_pools = await self.pool_discovery.discover_main_pools()
                    if new_pools:
                        self.main_pools = new_pools
                        if self.enhanced_fetcher:
                            # 這裡需要重新初始化抓取器，暫時跳過
                            pass
                
            except Exception as e:
                logger.error(f"❌ 恢復監控異常: {e}")
                await asyncio.sleep(30)
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """
        智能獲取價格 - Phase1 Schema 兼容
        優先級：鏈上數據 > 幣安API回退
        """
        if not self.is_streaming:
            logger.warning(f"⚠️ 價格流未啟動，無法獲取 {symbol} 價格")
            return None
        
        # 支援 BTC -> BTCUSDT 轉換
        if symbol in self.config.SUPPORTED_SYMBOLS:
            symbol = f"{symbol}USDT"
        
        # 檢查是否使用回退機制
        use_fallback = self.fallback_status.get(symbol, False)
        
        if not use_fallback and self.enhanced_fetcher:
            # 嘗試從鏈上獲取
            price = await self.enhanced_fetcher.get_live_price(symbol)
            if price is not None:
                return price
            
            # 鏈上失敗，臨時啟用回退
            logger.warning(f"⚠️ {symbol} 鏈上數據臨時失敗，使用回退機制")
            use_fallback = True
        
        # 使用幣安API回退
        if use_fallback and self.binance_fallback:
            try:
                # 調用現有的幣安API獲取價格
                clean_symbol = symbol.replace('USDT', '')
                price = await self._get_binance_fallback_price(clean_symbol)
                if price is not None:
                    logger.debug(f"🔄 {symbol} 使用幣安API回退: ${price:.4f}")
                    return price
            except Exception as e:
                logger.error(f"❌ {symbol} 幣安API回退失敗: {e}")
        
        logger.warning(f"⚠️ 無法獲取 {symbol} 價格（鏈上和回退都失敗）")
        return None
    
    async def _get_binance_fallback_price(self, symbol: str) -> Optional[float]:
        """從幣安API回退獲取價格"""
        if not self.binance_fallback:
            return None
        
        try:
            # 這裡需要調用你現有的 WebSocket 幣安API 邏輯
            # 假設現有的連接器有 get_price 方法
            if hasattr(self.binance_fallback, 'get_price'):
                return await self.binance_fallback.get_price(symbol)
            elif hasattr(self.binance_fallback, 'get_latest_price'):
                return await self.binance_fallback.get_latest_price(symbol)
            else:
                logger.warning("⚠️ 幣安回退連接器沒有找到價格獲取方法")
                return None
        except Exception as e:
            logger.error(f"❌ 幣安API回退調用失敗: {e}")
            return None
    
    async def get_price_data(self, symbol: str) -> Optional[Dict]:
        """獲取完整價格數據"""
        # 支援 BTC -> BTCUSDT 轉換
        if symbol in self.config.SUPPORTED_SYMBOLS:
            symbol = f"{symbol}USDT"
        
        use_fallback = self.fallback_status.get(symbol, False)
        
        if not use_fallback and self.enhanced_fetcher:
            data = await self.enhanced_fetcher.get_price_data(symbol)
            if data:
                return data
        
        # 回退模式只返回基本價格數據
        price = await self._get_binance_fallback_price(symbol.replace('USDT', ''))
        if price is not None:
            return {
                'price': price,
                'timestamp': datetime.now(),
                'source': 'binance_api_fallback',
                'is_fallback': True
            }
        
        return None
    
    async def get_all_prices(self) -> Dict[str, float]:
        """獲取所有支援幣種的即時價格"""
        prices = {}
        
        for symbol in self.config.SUPPORTED_SYMBOLS:
            price = await self.get_price(symbol)
            if price is not None:
                prices[f"{symbol}USDT"] = price
        
        return prices
    
    async def get_supported_symbols(self) -> List[str]:
        """獲取支援的交易對"""
        return self.config.get_symbol_pairs()
    
    async def get_system_status(self) -> Dict[str, any]:
        """獲取系統狀態"""
        status = {
            'initialized': self.is_initialized,
            'streaming': self.is_streaming,
            'main_pools_count': len(self.main_pools),
            'supported_symbols': len(self.config.SUPPORTED_SYMBOLS),
            'timestamp': datetime.now().isoformat(),
            'fallback_status': self.fallback_status.copy(),
            'symbols_on_fallback': [k for k, v in self.fallback_status.items() if v],
            'has_binance_fallback': self.binance_fallback is not None
        }
        
        if self.enhanced_fetcher:
            onchain_status = self.enhanced_fetcher.get_fallback_status()
            status['onchain_failures'] = onchain_status.get('total_failures', 0)
            status['onchain_health'] = len(onchain_status.get('symbols_on_fallback', []))
        
        return status
    
    async def refresh_pools(self):
        """手動刷新主池"""
        logger.info("🔄 手動刷新主池...")
        
        if not self.pool_discovery:
            logger.error("❌ 主池發現引擎未初始化")
            return
        
        # 停止當前價格流
        if self.enhanced_fetcher:
            self.enhanced_fetcher.stop_streaming()
        
        # 重新發現主池
        new_pools = await self.pool_discovery.discover_main_pools()
        
        if new_pools:
            self.main_pools = new_pools
            
            # 重新初始化增強版抓取器
            self.enhanced_fetcher = EnhancedPriceFetcher(self.main_pools)
            await self.enhanced_fetcher.initialize()
            
            # 重新啟動價格流
            if self.is_streaming:
                asyncio.create_task(self.enhanced_fetcher.start_price_streaming())
            
            logger.info(f"✅ 主池刷新完成，更新 {len(new_pools)} 個主池")
        else:
            logger.error("❌ 主池刷新失敗")
    
    async def stop(self):
        """停止智能混合連接器"""
        logger.info("🛑 停止智能混合價格連接器...")
        
        self.is_streaming = False
        
        if self.enhanced_fetcher:
            await self.enhanced_fetcher.close()
            self.enhanced_fetcher = None
        
        if self.pool_discovery:
            await self.pool_discovery.close()
        
        self.is_initialized = False
        logger.info("✅ 智能混合價格連接器已停止")
    
    async def __aenter__(self):
        """異步上下文管理器 - 進入"""
        await self.initialize()
        await self.start_price_streaming()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器 - 退出"""
        await self.stop()

# 全局實例
_global_hybrid_connector: Optional[SmartHybridPriceConnector] = None

async def get_smart_hybrid_connector(binance_fallback=None) -> SmartHybridPriceConnector:
    """獲取全局智能混合連接器實例"""
    global _global_hybrid_connector
    
    if _global_hybrid_connector is None:
        _global_hybrid_connector = SmartHybridPriceConnector(binance_fallback)
        await _global_hybrid_connector.initialize()
        await _global_hybrid_connector.start_price_streaming()
    
    return _global_hybrid_connector

async def cleanup_smart_hybrid_connector():
    """清理全局智能混合連接器"""
    global _global_hybrid_connector
    
    if _global_hybrid_connector:
        await _global_hybrid_connector.stop()
        _global_hybrid_connector = None

# Phase1 Schema 兼容性函數（智能混合版本）
async def get_crypto_price_smart(symbol: str, binance_fallback=None) -> Optional[float]:
    """
    Phase1 Schema 兼容函數 - 智能混合版本
    獲取加密貨幣價格（鏈上優先，幣安API回退）
    """
    connector = await get_smart_hybrid_connector(binance_fallback)
    return await connector.get_price(symbol)

async def get_all_crypto_prices_smart(binance_fallback=None) -> Dict[str, float]:
    """
    Phase1 Schema 兼容函數 - 智能混合版本
    獲取所有支援的加密貨幣價格（鏈上優先，幣安API回退）
    """
    connector = await get_smart_hybrid_connector(binance_fallback)
    return await connector.get_all_prices()
