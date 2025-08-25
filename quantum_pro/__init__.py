"""
Trading X 量子決策系統 - 生產級優化版本

基於 ChatGPT 建議的向量化計算優化，專為加密貨幣交易設計的量子決策引擎。

主要特色:
- 向量化前向-後向算法 (10-50x 性能提升)
- 轉移矩陣智能快取
- 生產級數值穩定性
- 七大幣種即時監控: BTC/ETH/BNB/SOL/XRP/DOGE/ADA
- 無模擬數據，純真實API整合

版本: 2.0.0 (ChatGPT 優化版)
作者: Trading X Quantum Team
"""

__version__ = "2.0.0"
__author__ = "Trading X Quantum Team"

# 生產級啟動器
from .production_launcher import ProductionQuantumLauncher
from .quantum_decision_optimizer import (
    CryptoMarketObservation,
    ProductionQuantumConfig,
    ProductionQuantumEngine,
    ProductionTradingHypothesis,
)
from .quantum_production_extension import (
    AlertManager,
    PerformanceMonitor,
    TradingXQuantumProcessor,
)

# 核心組件導入
from .regime_hmm_quantum import (
    ProductionQuantumRegimeHMM,
    QuantumObservation,
    RegimeState,
)

# 系統配置
QUANTUM_PRO_CONFIG = {
    "version": __version__,
    "name": "Trading X Quantum Pro",
    "description": "生產級量子決策交易系統",
    "supported_symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT"],
    "optimization_features": [
        "向量化前向-後向算法",
        "轉移矩陣快取",
        "逐行多項式邏輯優化",
        "加權Student-t參數估計",
        "系統重採樣粒子濾波"
    ],
    "data_sources": [
        "Binance WebSocket",
        "Trading X Market Data Service",
        "Real-time Order Book",
        "Funding Rate API"
    ]
}

def get_system_info():
    """獲取系統資訊"""
    return {
        "name": QUANTUM_PRO_CONFIG["name"],
        "version": __version__,
        "supported_symbols": QUANTUM_PRO_CONFIG["supported_symbols"],
        "optimization_level": "Production Grade with ChatGPT Vectorization"
    }

def create_production_config(**kwargs):
    """創建生產級配置"""
    return ProductionQuantumConfig(**kwargs)

def create_quantum_processor(config: ProductionQuantumConfig):
    """創建量子處理器"""
    return TradingXQuantumProcessor(config)

# 公開API
__all__ = [
    # 核心類別
    'ProductionQuantumRegimeHMM',
    'ProductionQuantumEngine', 
    'ProductionQuantumConfig',
    'TradingXQuantumProcessor',
    'ProductionQuantumLauncher',
    
    # 數據模型
    'CryptoMarketObservation',
    'ProductionTradingHypothesis',
    'RegimeState',
    'QuantumObservation',
    
    # 輔助工具
    'PerformanceMonitor',
    'AlertManager',
    
    # 工廠函數
    'create_production_config',
    'create_quantum_processor',
    'get_system_info',
    
    # 配置
    'QUANTUM_PRO_CONFIG'
]
