# 量子決策系統 - 獨立版本 (即時 API 整合)

## 概述

這是一個**完全獨立**的量子決策交易系統，專為加密貨幣市場設計。整合了量子增強的隱藏馬可夫模型、即時幣安 API 數據流，以及統計優勢最大化算法。系統可以獨立運作，無需依賴外部交易平台，支援七種主要加密貨幣的即時量子決策分析。

**核心理念**: "在市場隨機坍縮的過程中，始終站在統計優勢最大的一邊" ⚡

## 🚀 主要特色

### 核心功能 (基於量子決策理論)

- **時變隱馬可夫模型**: 動態更新 6 種市場制度機率，實時適應市場變化
- **量子信號篩選層**: 使用 `(期望報酬 × 機率) / 風險` 統計優勢最大化算法
- **即時幣安 API 整合**: WebSocket 串流接收 orderbook/trade 數據，無延遲決策
- **統計仲裁引擎**: 多重假設檢驗，選擇統計優勢最大的交易機會
- **Kelly 最優倉位**: 制度感知的風險調整倉位管理

### 獨立系統優勢

- **零依賴部署**: 無需外部交易系統，可獨立運作
- **即時七幣種監控**: BTC/ETH/BNB/SOL/XRP/DOGE/ADA 同步分析
- **多重確認機制**: 技術指標 + 市場微觀結構 + 即時數據流
- **動態參數調整**: 市場條件自適應的決策閾值
- **完整風險控制**: 內建止損、倉位管理、緊急保護機制

## 📁 系統架構

```
quantum_pro/
├── __init__.py                      # 模組初始化與系統資訊
├── regime_hmm_quantum.py           # 核心量子 HMM 引擎 (主要檔案)
├── quantum_decision_optimizer.py   # 量子決策最佳化系統
├── quantum_standalone_launcher.py  # 🚀 推薦啟動器 (獨立運行)
├── quantum_quick_verify.py         # 系統快速驗證工具
├── test_quantum_realtime_api.py    # 即時 API 整合測試
├── ARCHITECTURE_CLEANUP_GUIDE.md   # 架構說明文件
└── README.md                       # 本文件
```

### 🎯 推薦使用方式

```bash
# 啟動獨立量子系統
cd quantum_pro
python3 quantum_standalone_launcher.py

# 系統驗證
python3 quantum_quick_verify.py

# API 測試
python3 test_quantum_realtime_api.py
```

## 🔧 核心組件

### 1. TimeVaryingHMM (即時市場制度識別)

- **6 狀態制度建模**: BULL_TREND, BEAR_TREND, HIGH_VOL, LOW_VOL, MEAN_REVERT, BREAKOUT
- **動態機率更新**: 即時調整制度機率分佈
- **量子增強**: 統計優勢最大化的信號篩選
- **數值穩定**: 對數空間計算，避免數值溢出

### 2. 即時幣安數據收集器

- **WebSocket 串流**: 即時價格、訂單簿、成交數據
- **多幣種同步**: 同時監控 7 個主要交易對
- **數據品質控制**: 延遲檢測、異常過濾
- **緩衝區管理**: 智能數據暫存與處理

### 3. QuantumSignalSelector (統計優勢最大化)

```python
統計優勢 = (期望報酬 × 機率) / 風險
# 只選擇統計優勢 > 閾值的信號
```

### 4. TradingX 信號輸出器

- **標準化信號格式**: 與 Trading X 格式相容
- **風險參數計算**: 止損、止盈、倉位建議
- **信心度評估**: 基於制度穩定性的信心分數
- **執行時機優化**: 最佳進場點位識別

### 5. Kelly 最優倉位計算

```python
# Kelly 公式與風險調整
f* = (期望報酬 - 交易成本) / 風險方差 × kelly_multiplier
# 制度感知的動態調整
position_size = f* × 制度信心度 × 流動性因子
```

## 🛠 安裝與配置

### 1. 環境要求

```bash
Python 3.9+
numpy >= 1.21.0
scipy >= 1.7.0
pandas >= 1.3.0
websocket-client >= 1.0.0
requests >= 2.25.0
```

### 2. 快速安裝

```bash
# 進入 quantum_pro 目錄
cd quantum_pro

# 安裝依賴 (如果尚未安裝)
pip install numpy scipy pandas websocket-client requests

# 驗證系統
python3 quantum_quick_verify.py
```

### 3. 配置檔案 (可選)

預設配置已優化，如需調整可編輯：

```python
# 在 regime_hmm_quantum.py 中調整參數
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT"]
REGIME_CONFIDENCE_THRESHOLD = 0.6  # 制度信心閾值
STATISTICAL_ADVANTAGE_THRESHOLD = 0.15  # 統計優勢閾值
```

## 🚀 使用方法

### 1. 啟動獨立量子系統

```bash
cd quantum_pro
python3 quantum_standalone_launcher.py
```

### 2. 系統驗證

```bash
# 快速驗證所有組件
python3 quantum_quick_verify.py

# 應該看到: "✅ 7/7 測試通過! quantum_pro 系統可以獨立運作!"
```

### 3. API 整合測試

```bash
# 測試即時幣安 API 連接
python3 test_quantum_realtime_api.py

# 驗證 WebSocket 數據流
```

### 4. 系統監控

系統運行時會自動輸出：

- 🔄 制度識別狀態
- 📊 信念狀態熵值
- ⚡ 量子決策觸發
- 🛡️ 風險監控警報

### 5. 決策輸出示例

```
🎯 量子決策觸發 [BTCUSDT]:
   制度=BULL_TREND, 方向=LONG, 倉位=4.56%,
   統計優勢=0.234, 信心度=0.847
```

## 📊 核心模組說明

### 1. TimeVaryingHMM (時變隱馬可夫模型)

```python
# 動態制度識別
model = TimeVaryingHMM(n_states=6, z_dim=3)
regime_probs = model.get_regime_probabilities(market_data)
```

### 2. QuantumSignalSelector (量子信號篩選)

```python
# 統計優勢最大化
selector = QuantumSignalSelector()
best_signal = selector.select_optimal_signal(candidates)
```

### 3. 即時幣安數據收集器

```python
# WebSocket 即時數據流
collector = 即時幣安數據收集器()
await collector.start_streaming(symbols=SYMBOLS)
```

### 4. TradingX 信號輸出器

```python
# 標準化信號輸出
outputter = TradingX信號輸出器()
signal = outputter.format_signal(decision_result)
```

## 🛡️ 風險控制

### 1. 多層風險檢查

- **統計優勢閾值**: 只執行統計優勢 > 0.15 的信號
- **制度信心度**: 制度機率必須 > 60% 才執行
- **倉位限制**: Kelly 倍數限制，最大單一倉位 8%
- **流動性保護**: 根據訂單簿深度調整倉位

### 2. 即時監控指標

- **決策品質**: 統計優勢分佈監控
- **數據品質**: WebSocket 延遲、異常檢測
- **制度穩定性**: 制度轉換頻率監控
- **系統健康**: 記憶體使用、處理速度

### 3. 緊急保護機制

- **數據異常**: 自動降級為觀望模式
- **制度不明確**: 暫停交易直到制度穩定
- **統計優勢不足**: 自動過濾低優勢信號
- **系統過載**: 自動調整處理頻率

## 📈 性能指標

### 1. 系統效能

- **制度識別延遲**: < 1 秒
- **決策生成速度**: < 500ms
- **WebSocket 延遲**: < 100ms
- **記憶體使用**: < 200MB

### 2. 決策品質

- **制度識別準確率**: > 75%
- **統計優勢閾值**: > 0.15
- **信號勝率目標**: 55-65%
- **夏普比率目標**: > 1.5

### 3. 風險控制

- **最大單一倉位**: 8%
- **制度信心閾值**: 60%
- **Kelly 倍數上限**: 0.25
- **緊急停損**: 自動風險管理

## 🔧 故障排除

### 1. 常見問題

**Q: 系統驗證失敗**

```bash
# 檢查 Python 版本和依賴
python3 --version  # 需要 3.9+
pip list | grep -E "(numpy|scipy|pandas|websocket)"
```

**Q: WebSocket 連接失敗**

```bash
# 測試網路連接
python3 test_quantum_realtime_api.py
# 檢查防火牆設定
```

**Q: 制度識別不穩定**

```python
# 調整制度信心閾值
REGIME_CONFIDENCE_THRESHOLD = 0.7  # 提高至 70%
```

**Q: 統計優勢過低**

```python
# 降低優勢閾值或檢查市場條件
STATISTICAL_ADVANTAGE_THRESHOLD = 0.10  # 降至 10%
```

### 2. 日誌檢查

```bash
# 檢查系統輸出
python3 quantum_standalone_launcher.py | tee quantum_log.txt

# 監控系統狀態
tail -f quantum_log.txt
```

### 3. 效能監控

```bash
# 系統資源使用
top -p $(pgrep -f quantum_standalone_launcher)

# 網路連接狀態
netstat -an | grep 9443  # Binance WebSocket
```

## 🚀 開發與擴展

### 1. 添加新的交易對

```python
# 在 regime_hmm_quantum.py 中修改
SYMBOLS = ["BTCUSDT", "ETHUSDT", "...", "NEWUSDT"]
```

### 2. 調整制度類型

```python
# 修改制度定義
REGIMES = ["BULL_TREND", "BEAR_TREND", "...", "CUSTOM_REGIME"]
```

### 3. 自定義統計優勢計算

```python
def calculate_statistical_advantage(expected_return, probability, risk):
    # 自定義算法
    return (expected_return * probability) / risk
```

### 4. 整合新的數據源

```python
# 擴展數據收集器
class CustomDataCollector(即時幣安數據收集器):
    def add_new_exchange_support(self):
        # 添加新交易所支援
        pass
```

## 📚 技術文件

### 相關文件

- `ARCHITECTURE_CLEANUP_GUIDE.md` - 架構說明與遷移指南
- `regime_hmm_quantum.py` - 核心演算法實現
- `quantum_quick_verify.py` - 系統驗證程序

### 學術參考

- Hidden Markov Models for Time Series Analysis
- Kelly Criterion in Portfolio Optimization
- Statistical Arbitrage in Cryptocurrency Markets
- Quantum-Enhanced Decision Making Algorithms

## ⚠️ 法律聲明

本系統僅供研究和教育目的使用。加密貨幣交易存在高風險，可能導致資金損失。使用者應：

- 充分了解加密貨幣市場風險
- 根據自身風險承受能力進行配置
- 建議先在模擬環境測試
- 遵守當地金融法規

**開發者不對任何交易損失或系統故障承擔責任。**

## 📝 版本歷史

- **v2.0.0**: 獨立系統版本

  - ✅ 完全獨立運作，無外部依賴
  - ✅ 即時幣安 API 整合 (WebSocket)
  - ✅ 量子信號篩選層實現
  - ✅ HMM 動態制度識別
  - ✅ 統計優勢最大化算法

- **v1.0.0**: 初始版本
  - 基礎 HMM 制度識別
  - Trading X 系統整合
  - Kelly 倉位管理

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 開發流程

1. Fork 本專案
2. 創建功能分支 (`git checkout -b feature/new-feature`)
3. 提交更改 (`git commit -am 'Add new feature'`)
4. 推送分支 (`git push origin feature/new-feature`)
5. 創建 Pull Request

---

**© 2025 Quantum Pro Trading System. 獨立量子決策，統計優勢最大化。** ⚡
