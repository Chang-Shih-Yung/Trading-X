"""
Trading X 量子決策系統 - 獨立版本

這是一個完全獨立的量子交易決策系統，專注於加密貨幣市場的技術分析和自動化交易信號生成。

主要特色:
- 🔬 量子增強的隱藏馬可夫模型 (HMM)
- 📡 即時幣安 API 數據整合 (WebSocket)
- ⚡ 統計優勢最大化算法
- 🎯 Trading X 標準信號輸出
- 🚀 完全獨立運作，無外部依賴

支援交易對: BTC/ETH/BNB/SOL/XRP/DOGE/ADA

快速開始:
    from quantum_pro import QuantumStandaloneLauncher
    launcher = QuantumStandaloneLauncher()
    await launcher.run()

版本: 2.0.0 (獨立版)
作者: Trading X Quantum Team
"""

__version__ = "2.0.0"
__author__ = "Trading X Quantum Team"

# 主要啟動器 (推薦)
from .quantum_standalone_launcher import QuantumStandaloneLauncher

# 已棄用啟動器 (保留向後兼容)
from .production_launcher import ProductionQuantumLauncher
from .quantum_decision_optimizer import (
    CryptoMarketObservation,
    ProductionQuantumConfig,
    ProductionQuantumEngine,
    ProductionTradingHypothesis,
)
# 已棄用組件 (保留向後兼容)
from .quantum_production_extension import (
    TradingXQuantumProcessor,
    PerformanceMonitor,
    AlertManager,
)

# 核心組件導入
from .regime_hmm_quantum import (
    TimeVaryingHMM,
    即時幣安數據收集器,
    TradingX信號輸出器,
    即時市場觀測,
    TradingX信號,
    QuantumSignalSelector,
    OnlineEMAdaptor,
    RegimeShiftDetector
)

# 系統配置
QUANTUM_PRO_CONFIG = {
    "version": __version__,
    "name": "Trading X Quantum Pro",
    "description": "獨立量子決策交易系統",
    "supported_symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT"],
    "key_features": [
        "量子增強隱藏馬可夫模型",
        "即時幣安 API 整合", 
        "統計優勢最大化算法",
        "Trading X 標準信號輸出",
        "完全獨立運作"
    ],
    "data_sources": [
        "Binance WebSocket (即時價格流)",
        "Binance REST API (資金費率/OI)",
        "即時訂單簿分析",
        "交易流統計"
    ],
    "recommended_launcher": "QuantumStandaloneLauncher"
}

def get_system_info():
    """獲取系統資訊"""
    return {
        "name": QUANTUM_PRO_CONFIG["name"],
        "version": __version__,
        "supported_symbols": QUANTUM_PRO_CONFIG["supported_symbols"],
        "optimization_level": "Production Grade with Quantum Enhancement",
        "recommended_launcher": QUANTUM_PRO_CONFIG["recommended_launcher"],
        "status": "Independent Operation Ready"
    }

def create_production_config(**kwargs):
    """創建生產級配置"""
    return ProductionQuantumConfig(**kwargs)

def create_quantum_processor(config=None):
    """
    創建量子處理器 (推薦使用獨立啟動器)
    
    ⚠️ DEPRECATED: 建議使用 QuantumStandaloneLauncher
    """
    return TradingXQuantumProcessor(config)

# 公開API
__all__ = [
    # 核心類別
    'TimeVaryingHMM',
    'ProductionQuantumEngine', 
    'ProductionQuantumConfig',
    'TradingXQuantumProcessor',
    'ProductionQuantumLauncher',
    'QuantumStandaloneLauncher',
    
    # 即時API整合
    '即時幣安數據收集器',
    'TradingX信號輸出器',
    '即時市場觀測',
    'TradingX信號',
    
    # 量子組件
    'QuantumSignalSelector',
    'OnlineEMAdaptor', 
    'RegimeShiftDetector',
    
    # 數據模型
    'CryptoMarketObservation',
    'ProductionTradingHypothesis',
    
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
