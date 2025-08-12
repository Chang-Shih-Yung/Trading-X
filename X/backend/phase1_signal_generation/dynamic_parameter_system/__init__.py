"""
Dynamic Parameter System for Phase1 Signal Generation
Phase1 動態參數系統 - 市場自適應參數調整

這個模組提供了一個完整的動態參數系統，可以根據市場制度、交易時段和其他市場條件
自動調整Phase1-5的信號生成參數。

主要組件:
- DynamicParameterEngine: 主要引擎類
- MarketRegimeDetector: 市場制度檢測器  
- TradingSessionDetector: 交易時段檢測器
- DynamicParameterAdapter: 參數適配器

使用方式:
```python
from dynamic_parameter_system import create_dynamic_parameter_engine

# 創建引擎
engine = await create_dynamic_parameter_engine()

# 獲取Phase1動態參數
result = await engine.get_dynamic_parameters("phase1")

# 獲取單個參數值
confidence_threshold = await engine.get_parameter_value("phase1", "confidence_threshold")
```
"""

from .dynamic_parameter_engine import (
    MarketData,
    AdaptedParameter,
    MarketDataSource,
    RealTimeMarketDataSource,
    MarketRegimeDetector,
    TradingSessionDetector,
    DynamicParameterAdapter,
    DynamicParameterEngine,
    MarketRegime,
    TradingSession
)

__version__ = "1.0.0"
__author__ = "Trading X Team"
__description__ = "Dynamic Parameter System for Market Adaptive Trading"

__all__ = [
    "MarketData",
    "AdaptedParameter", 
    "MarketDataSource",
    "RealTimeMarketDataSource",
    "MarketRegimeDetector",
    "TradingSessionDetector", 
    "DynamicParameterAdapter",
    "DynamicParameterEngine",
    "MarketRegime",
    "TradingSession"
]