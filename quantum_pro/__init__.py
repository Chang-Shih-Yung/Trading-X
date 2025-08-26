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
from .quantum_ultimate_launcher import QuantumUltimateLauncher

# 已棄用啟動器 (保留向後兼容)
try:
    from .production_launcher import ProductionQuantumLauncher
except ImportError:
    ProductionQuantumLauncher = None

# 已棄用 quantum_decision_optimizer (功能已整合到其他模組)
# from .quantum_decision_optimizer import (
#     CryptoMarketObservation,
#     ProductionQuantumConfig,
#     ProductionQuantumEngine,
#     ProductionTradingHypothesis,
# )

# 已棄用組件 (保留向後兼容)
try:
    from .quantum_production_extension import (
        AlertManager,
        PerformanceMonitor,
        TradingXQuantumProcessor,
    )
except ImportError:
    TradingXQuantumProcessor = None
    PerformanceMonitor = None
    AlertManager = None

# BTC 量子終極模型整合
from .btc_quantum_ultimate_model import (
    QUANTUM_CONFIG,
    BTCQuantumUltimateModel,
    create_btc_quantum_model,
    evaluate_quantum_circuit,
    feature_to_hJ_advanced,
)

# 量子終極啟動器組件
from .quantum_ultimate_launcher import QUANTUM_SYMBOLS, QuantumUltimateLauncher

# 核心組件導入
from .regime_hmm_quantum import (
    OnlineEMAdaptor,
    QuantumSignalSelector,
    RegimeShiftDetector,
    TimeVaryingHMM,
    TradingX信號,
    TradingX信號輸出器,
    即時市場觀測,
    即時幣安數據收集器,
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
    "recommended_launcher": "QuantumUltimateLauncher"
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
    創建量子處理器 (推薦使用量子終極啟動器)
    
    ⚠️ DEPRECATED: 建議使用 QuantumUltimateLauncher
    """
    if TradingXQuantumProcessor:
        return TradingXQuantumProcessor(config)
    else:
        return None

# 公開API
__all__ = [
    # 核心類別
    'TimeVaryingHMM',
    'ProductionQuantumEngine', 
    'ProductionQuantumConfig',
    'QuantumUltimateLauncher',
    
    # BTC 量子終極模型
    'BTCQuantumUltimateModel',
    'create_btc_quantum_model',
    'evaluate_quantum_circuit',
    'feature_to_hJ_advanced',
    'QUANTUM_CONFIG',
    
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
    
    # 工廠函數
    'create_production_config',
    'get_system_info',
    
    # 配置
    'QUANTUM_PRO_CONFIG'
]

# 條件性添加可選組件
if TradingXQuantumProcessor:
    __all__.extend(['TradingXQuantumProcessor', 'create_quantum_processor'])
if PerformanceMonitor:
    __all__.extend(['PerformanceMonitor', 'AlertManager'])
if ProductionQuantumLauncher:
    __all__.append('ProductionQuantumLauncher')
