# Trading X Quantum Pro

## 📁 資料夾結構

```
quantum_pro/
├── __init__.py                                    # Python 包初始化
├── README.md                                      # 系統文檔
├── examples.py                                    # 使用示例
├── regime_hmm_quantum.py                          # 核心 HMM 量子引擎
├── quantum_decision_optimizer.py                  # 量子決策優化器
├── quantum_config_manager.py                      # 配置管理系統
├── quantum_launcher.py                            # 生產級啟動器
├── QUANTUM_DECISION_INTEGRATION_GUIDE.md          # 詳細整合指南
└── config/
    └── quantum_config.json                        # 系統配置文件
```

## 🚀 快速啟動

### 方法 1: 使用啟動腳本
```bash
python start_quantum_pro.py
```

### 方法 2: 直接模組啟動
```bash
python -m quantum_pro.quantum_launcher
```

### 方法 3: 在代碼中使用
```python
from quantum_pro import ProductionQuantumProcessor, get_config_manager

# 載入配置
config_manager = get_config_manager()
config = config_manager.get_quantum_decision_config()

# 啟動處理器
processor = ProductionQuantumProcessor(config)
await processor.start_processing()
```

## 📖 使用示例

運行示例代碼了解系統功能：
```bash
python quantum_pro/examples.py
```

## ⚙️ 系統配置

編輯 `quantum_pro/config/quantum_config.json` 來調整系統參數：

- **SPRT 參數**: `alpha=0.03`, `beta=0.15`
- **Kelly 管理**: `kelly_multiplier=0.2`, `max_position_cap=0.08`
- **風險控制**: `max_drawdown=0.03`, `volatility_lookback=30`

## 🔧 核心模組

### 1. TimeVaryingHMM
時變隱馬可夫模型，支援六種市場制度識別

### 2. QuantumDecisionEngine  
量子決策引擎，實現 SPRT + Kelly + 貝葉斯信念更新

### 3. ProductionQuantumProcessor
生產級處理器，整合 Trading X 區塊鏈數據流

### 4. QuantumConfigManager
配置管理系統，支援動態參數調整

## 📊 監控的加密貨幣

- BTCUSDT (權重: 30%)
- ETHUSDT (權重: 25%) 
- BNBUSDT (權重: 15%)
- ADAUSDT (權重: 10%)
- DOTUSDT (權重: 8%)
- LINKUSDT (權重: 7%)
- SOLUSDT (權重: 5%)

## 🎯 主要特性

- ✅ 精密 HMM 制度識別
- ✅ SPRT 坍縮控制決策
- ✅ Kelly 資金管理
- ✅ Student-t 厚尾分布處理
- ✅ 即時區塊鏈數據整合
- ✅ 多層風險控制機制
- ✅ 生產級錯誤處理

## 📈 性能指標

- **決策準確率**: > 55%
- **制度識別準確率**: > 75%
- **平均決策時間**: < 2 分鐘
- **最大回撤**: < 3%

詳細文檔請參考 `QUANTUM_DECISION_INTEGRATION_GUIDE.md`
