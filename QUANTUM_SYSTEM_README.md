# Trading X 量子決策系統

## 概述

Trading X 量子決策系統是一個基於精密隱馬可夫模型（HMM）和貝葉斯決策理論的高頻交易決策引擎。系統整合了區塊鏈即時數據流，實現多制度市場識別和量子化決策執行。

## 核心特性

### 1. 精密 HMM 制度識別
- **時變轉移矩陣**: `A_t[i,j] = softmax(b_{ij} + w_{ij}^T z_t)`
- **Student-t 厚尾分布**: 處理加密貨幣市場極值事件
- **多維觀測模型**: 收益率、波動率、斜率、訂單簿不平衡

### 2. 量子決策架構
- **SPRT 坍縮控制**: 順序機率比檢定，α=0.03, β=0.15
- **信念更新**: 對數機率比方法，遺忘因子 γ=0.98
- **Kelly 資金管理**: 動態倉位調整，最大倉位 8%

### 3. 區塊鏈數據整合
- **七種主要幣對**: BTC, ETH, BNB, ADA, DOT, LINK, SOL
- **即時數據流**: WebSocket 價格、深度、K線數據
- **技術指標計算**: RSI、波動率、價格斜率、資金費率

## 系統架構

```
├── regime_hmm_quantum.py          # 核心 HMM 量子引擎
├── quantum_decision_optimizer.py  # 量子決策優化器
├── quantum_config_manager.py      # 配置管理器
├── quantum_launcher.py            # 生產啟動器
└── config/
    └── quantum_config.json        # 系統配置文件
```

## 數學基礎

### 1. 制度轉移概率
```
P(H_t = j | H_{t-1} = i, z_t) = softmax_j(b_{ij} + w_{ij}^T z_t)
```

### 2. 信念更新公式
```
log(P_t(k)/P_t(k̄)) = γ * log(P_{t-1}(k)/P_{t-1}(k̄)) + log(L_k/L_k̄)
```

### 3. SPRT 決策閾值
```
A = log((1-β)/α) ≈ 2.94
B = log(β/(1-α)) ≈ -1.39
```

### 4. Kelly 倉位計算
```
f* = (ER - transaction_cost) / σ² * kelly_multiplier
```

## 安裝與配置

### 1. 環境要求
```bash
Python 3.9+
numpy >= 1.21.0
scipy >= 1.7.0
pandas >= 1.3.0
```

### 2. 安裝依賴
```bash
pip install -r requirements.txt
```

### 3. 配置文件
編輯 `config/quantum_config.json`:

```json
{
  "quantum_decision_config": {
    "sprt_parameters": {
      "alpha": 0.03,        // Type-I 錯誤率
      "beta": 0.15          // Type-II 錯誤率
    },
    "kelly_management": {
      "kelly_multiplier": 0.2,      // Kelly 倍數
      "max_position_cap": 0.08      // 最大倉位比例
    }
  }
}
```

## 使用方法

### 1. 啟動量子決策系統
```bash
python quantum_launcher.py
```

### 2. 監控系統狀態
系統會自動輸出：
- 制度識別狀態
- 信念狀態熵值
- 決策觸發信息
- 風險監控警報

### 3. 決策輸出示例
```
量子決策觸發 [BTCUSDT]: 假設=BULL_BREAKOUT_BTCUSDT, 方向=1, 倉位=0.0456, 信心度=0.847, 期望收益=0.0023
```

## 核心模組說明

### 1. TimeVaryingHMM
```python
# 時變隱馬可夫模型
model = TimeVaryingHMM(n_states=6, z_dim=3)
log_alpha, log_c = model.forward_log(x_seq, z_seq)
```

### 2. QuantumDecisionEngine
```python
# 量子決策引擎
engine = QuantumDecisionEngine(config)
decision = await engine.process_observation(obs, hypotheses)
```

### 3. ProductionQuantumProcessor
```python
# 生產級處理器
processor = ProductionQuantumProcessor(config)
await processor.start_processing()
```

## 風險控制

### 1. 多層風險檢查
- **倉位限制**: 單一幣對最大 8% 倉位
- **回撤控制**: 最大 3% 回撤限制
- **制度確認**: 制度信心度最低 60%

### 2. 實時監控
- **決策品質**: 成功率監控，最低 55%
- **數據質量**: 延遲監控，最大 5 秒
- **系統健康**: 緩衝區大小、熵值檢查

### 3. 緊急機制
- **自動停損**: 5% 緊急停損
- **制度失效**: 不明確制度自動觀望
- **數據異常**: 自動降級保護模式

## 性能指標

### 1. 決策效率
- **平均決策時間**: < 2 分鐘
- **制度識別準確率**: > 75%
- **信念收斂速度**: < 120 秒

### 2. 交易表現
- **預期勝率**: 55-65%
- **盈虧比**: 1:1.2
- **最大回撤**: < 3%

## 故障排除

### 1. 常見問題

**Q: 制度識別不穩定**
A: 檢查數據質量，調整 `regime_confidence_threshold`

**Q: 決策頻率過高**
A: 提高 `min_er_threshold` 或調整 SPRT 參數

**Q: 倉位過小**
A: 檢查 `kelly_multiplier` 和波動率估計

### 2. 日誌分析
```bash
# 查看決策日誌
tail -f logs/quantum_decision_$(date +%Y%m%d).log

# 查看錯誤日誌
grep "ERROR" logs/quantum_decision_*.log
```

## 開發與擴展

### 1. 添加新的假設類型
在 `quantum_config.json` 中添加新的 `hypothesis_templates`

### 2. 自定義技術指標
擴展 `TechnicalIndicatorCalculator` 類

### 3. 新交易對支持
在 `active_symbols` 中添加新的交易對配置

## 法律聲明

本系統僅供研究和教育目的。實際交易存在風險，請謹慎使用。開發者不對任何交易損失負責。

## 版本歷史

- **v1.0.0**: 初始版本，支援七種主要加密貨幣
- 基於精密 HMM 的制度識別
- SPRT + Kelly 組合決策框架
- 生產級風險控制機制

---

© 2025 Trading X 量子決策系統. 保留所有權利.
