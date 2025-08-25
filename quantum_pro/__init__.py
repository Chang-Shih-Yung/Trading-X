"""
Trading X 量子決策系統 (Quantum Pro)

一個基於精密隱馬可夫模型和貝葉斯決策理論的高頻交易決策引擎。
整合區塊鏈即時數據流，實現多制度市場識別和量子化決策執行。

主要模組:
- regime_hmm_quantum: 時變隱馬可夫模型核心引擎
- quantum_decision_optimizer: 量子決策優化器
- quantum_config_manager: 配置管理系統
- quantum_launcher: 生產級啟動器

版本: 1.0.0
作者: Trading X Team
日期: 2025-08-25
"""

__version__ = "1.0.0"
__author__ = "Trading X Team"

from .quantum_config_manager import (
    HypothesisTemplate,
    QuantumConfigManager,
    RegimeDefinition,
    SymbolConfig,
    get_config_manager,
)
from .quantum_decision_optimizer import (
    MarketObservation,
    ProductionQuantumProcessor,
    QuantumDecisionConfig,
    QuantumDecisionEngine,
    TradingHypothesis,
)

# 導入主要類別
from .regime_hmm_quantum import EmissionParams, TimeVaryingHMM

__all__ = [
    # 核心HMM引擎
    'TimeVaryingHMM',
    'EmissionParams',
    
    # 量子決策系統
    'QuantumDecisionConfig',
    'QuantumDecisionEngine',
    'ProductionQuantumProcessor',
    'MarketObservation', 
    'TradingHypothesis',
    
    # 配置管理
    'QuantumConfigManager',
    'SymbolConfig',
    'RegimeDefinition', 
    'HypothesisTemplate',
    'get_config_manager'
]

# 系統資訊
SYSTEM_INFO = {
    "name": "Trading X Quantum Pro",
    "version": __version__,
    "description": "精密量子決策交易系統",
    "supported_exchanges": ["Binance", "OKX"],
    "supported_symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT", "SOLUSDT"],
    "regime_count": 6,
    "decision_algorithms": ["SPRT", "Kelly", "Bayesian_Belief_Update"],
    "mathematical_models": ["Time_Varying_HMM", "Student_t_Distribution", "Logistic_Transition"]
}

def get_system_info():
    """獲取系統資訊"""
    return SYSTEM_INFO.copy()

def quick_start():
    """快速啟動指南"""
    instructions = """
    Trading X Quantum Pro 快速啟動:
    
    1. 確保配置文件存在:
       quantum_pro/config/quantum_config.json
    
    2. 啟動量子決策系統:
       python -m quantum_pro.quantum_launcher
    
    3. 或者在代碼中使用:
       from quantum_pro import ProductionQuantumProcessor
       processor = ProductionQuantumProcessor(config)
       await processor.start_processing()
    
    詳細文檔請參考: quantum_pro/README.md
    """
    print(instructions)
    return instructions
