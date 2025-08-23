"""
產品級鏈上價格連接器 + 智能混合系統
Production-Grade Onchain Price Connector + Smart Hybrid System
"""

# 原有的純鏈上連接器
from .production_connector import (
    ProductionOnChainPriceConnector,
    get_production_connector,
    cleanup_production_connector,
    get_crypto_price,
    get_all_crypto_prices
)

# 新的智能混合連接器
from .smart_hybrid_connector import (
    SmartHybridPriceConnector,
    get_smart_hybrid_connector,
    cleanup_smart_hybrid_connector,
    get_crypto_price_smart,
    get_all_crypto_prices_smart
)

from .config import ProductionConfig
from .fallback_config import FallbackConfig
from .pool_discovery import PoolDiscoveryEngine
from .price_fetcher import RealTimePriceFetcher
from .enhanced_price_fetcher import EnhancedPriceFetcher

__all__ = [
    # 原有純鏈上連接器
    'ProductionOnChainPriceConnector',
    'get_production_connector', 
    'cleanup_production_connector',
    'get_crypto_price',
    'get_all_crypto_prices',
    
    # 新的智能混合連接器 (推薦使用)
    'SmartHybridPriceConnector',
    'get_smart_hybrid_connector',
    'cleanup_smart_hybrid_connector', 
    'get_crypto_price_smart',
    'get_all_crypto_prices_smart',
    
    # 配置和組件
    'ProductionConfig',
    'FallbackConfig',
    'PoolDiscoveryEngine',
    'RealTimePriceFetcher',
    'EnhancedPriceFetcher'
]

__version__ = "2.0.0"
__author__ = "Trading-X Production Team"
__description__ = "產品級BSC鏈上價格抓取系統 + 智能混合回退機制 - 支援PancakeSwap V2/V3自動主池發現 + WebSocket幣安API智能回退"
