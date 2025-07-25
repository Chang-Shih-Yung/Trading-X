# 高級交易系統後端 API 文檔

## 概述

本系統將原本前端的市場情緒判斷、短線信號歷史管理等複雜邏輯遷移到後端，提供了完整的牛熊市分析、動態止盈止損計算、突破信號檢測等功能。

## 核心服務架構

### 1. 市場分析服務 (`MarketAnalysisService`)

#### 功能特點

- **牛熊市判斷**: 基於 MA200、ADX、價格結構、恐懼貪婪指數、資金費率、減半週期等多因素評分
- **動態止盈止損**: 根據 ATR 波動率、市場階段、信號方向動態調整
- **突破信號檢測**: 綜合分析成交量、價格、MACD、RSI、布林帶等指標

#### 牛熊市評分系統

```python
# 牛市分數計算邏輯
bull_score = 0

# MA200 趨勢 (權重: 3)
if price > ma200 and ma200_slope > 0: bull_score += 3

# ADX 指標 (權重: 2)
if adx > 25 and di_plus > di_minus: bull_score += 2

# 價格結構 (權重: 2)
bull_score += structure_score * 2

# 恐懼貪婪指數 (權重: 1)
if fear_greed_index > 55: bull_score += 1

# 資金費率 (權重: 1)
if funding_rate >= 0.01: bull_score += 1

# 減半週期 (權重: 2)
if is_within_halving_window(): bull_score += 2

# 結果判斷
if bull_score >= 6: trend = "bull"
elif bear_score >= 6: trend = "bear"
else: trend = "neutral"
```

#### 動態止盈止損邏輯

```python
# 多單止盈止損計算
if signal_direction == LONG:
    base_stop_pct = 0.012  # 基礎止損 1.2%

    # 牛市調整
    if market_condition == BULL:
        if phase == MAIN_BULL:
            risk_reward_ratio = 4.0  # 主升段放大盈虧比
        elif phase == HIGH_VOLATILITY:
            risk_reward_ratio = 2.5  # 高位震盪縮小
            base_stop_pct = 0.008    # 縮緊止損
        else:
            risk_reward_ratio = 3.0  # 初升段保守

    # ATR 調整
    if atr_pct > 0.03:
        base_stop_pct *= 1.2  # 高波動增加止損空間
    elif atr_pct < 0.01:
        base_stop_pct *= 0.8  # 低波動縮小止損空間

# 空單邏輯類似，但風險回報比更保守
```

### 2. 短線歷史管理服務 (`ShortTermHistoryService`)

#### 功能特點

- **自動過期處理**: 定期檢查並歸檔過期信號
- **智能數據管理**: 保留最近 80%記錄 + 成功 20%記錄，總數限制 5000 筆
- **歷史結果重算**: 支持更新平手標準（如 0.5%）並重新計算所有歷史記錄
- **多維度統計**: 按交易對、策略、日期分析表現

#### 交易結果判斷邏輯

```python
def calculate_final_result(signal):
    if signal_type in ['LONG', 'SCALPING_LONG']:
        profit_loss_pct = ((current_price - entry_price) / entry_price) * 100
    else:  # SHORT
        profit_loss_pct = ((entry_price - current_price) / entry_price) * 100

    # 新的0.5%平手標準
    if abs(profit_loss_pct) <= 0.5:
        return TradeResult.BREAKEVEN
    elif profit_loss_pct > 0.5:
        return TradeResult.WIN
    else:
        return TradeResult.LOSS
```

### 3. 增強短線信號服務 (`EnhancedScalpingService`)

#### 功能特點

- **多因素信號生成**: 整合市場分析、技術指標、突破檢測
- **智能方向判斷**: 根據牛熊市環境調整多空偏好
- **動態參數調整**: 根據市場階段和波動率調整信號參數
- **多時間框架分析**: 支持 1m、3m、5m、15m、30m 等時間框架

#### 信號生成流程

```python
async def generate_enhanced_signals():
    for symbol in target_symbols:
        for timeframe in timeframes:
            # 1. 獲取價格數據
            price_data = await get_kline_data(symbol, timeframe)

            # 2. 市場狀況分析
            market_condition = analyze_market_condition(price_data)

            # 3. 突破信號檢測
            breakout_signal = detect_breakout_signals(price_data)

            # 4. 技術指標分析
            technical_analysis = analyze_technical_indicators(price_data)

            # 5. 生成信號
            signals = create_signals_from_analysis(...)

    # 6. 排序和篩選
    return rank_and_filter_signals(all_signals)
```

## API 端點總覽

### 市場分析 API (`/api/v1/market-analysis/`)

| 端點                          | 方法 | 功能             | 說明                     |
| ----------------------------- | ---- | ---------------- | ------------------------ |
| `/analyze-market`             | POST | 市場狀況分析     | 牛熊市判斷、市場階段識別 |
| `/calculate-stop-loss`        | POST | 動態止盈止損計算 | 基於市場條件和 ATR 調整  |
| `/breakout-analysis/{symbol}` | GET  | 突破信號分析     | 多指標突破檢測           |
| `/batch-market-analysis`      | POST | 批量市場分析     | 多交易對並行分析         |
| `/market-sentiment/{symbol}`  | GET  | 市場情緒分析     | 綜合情緒評分和建議       |

### 短線歷史 API (`/api/v1/market-analysis/history/`)

| 端點                       | 方法 | 功能         | 說明                   |
| -------------------------- | ---- | ------------ | ---------------------- |
| `/statistics`              | GET  | 歷史統計數據 | 勝率、盈虧、持有時間等 |
| `/records`                 | GET  | 歷史記錄查詢 | 支持分頁、篩選         |
| `/recalculate`             | POST | 重新計算結果 | 應用新的平手標準       |
| `/process-expired-signals` | POST | 處理過期信號 | 自動歸檔過期信號       |

### 增強短線 API (`/api/v1/scalping/`)

| 端點                    | 方法 | 功能         | 說明                   |
| ----------------------- | ---- | ------------ | ---------------------- |
| `/signals`              | GET  | 增強短線信號 | 整合牛熊市分析的信號   |
| `/prices`               | GET  | 即時價格     | 包含 24 小時統計       |
| `/market-sentiment`     | GET  | 市場整體情緒 | 基於信號分析的情緒指標 |
| `/strategy-performance` | GET  | 策略表現統計 | 多維度表現分析         |

## 使用示例

### 1. 獲取市場分析

```javascript
// 分析BTC市場狀況
const response = await axios.post('/api/v1/market-analysis/analyze-market', {
  symbol: 'BTCUSDT',
  timeframe: '1h',
  fear_greed_index: 75,
  funding_rate: 0.015
})

// 響應示例
{
  "symbol": "BTCUSDT",
  "trend": "bull",
  "phase": "main_bull",
  "bull_score": 8.5,
  "bear_score": 2.3,
  "confidence": 0.87,
  "key_factors": [
    "價格突破MA200且向上",
    "ADX強勢上漲(32.1, +DI > -DI)",
    "價格結構呈現上升趨勢"
  ]
}
```

### 2. 計算動態止盈止損

```javascript
// 計算多單的止盈止損
const response = await axios.post('/api/v1/market-analysis/calculate-stop-loss', {
  symbol: 'ETHUSDT',
  entry_price: 3000,
  signal_direction: 'LONG',
  timeframe: '15m'
})

// 響應示例
{
  "stop_loss_price": 2964,
  "take_profit_price": 3144,
  "stop_loss_pct": -1.2,
  "take_profit_pct": 4.8,
  "risk_reward_ratio": 4.0,
  "reasoning": "bull市場，LONG信號，風險回報比4:1，ATR調整",
  "atr_adjusted": true,
  "market_condition_adjusted": true
}
```

### 3. 獲取增強短線信號

```javascript
// 獲取牛市條件下的保守短線信號
const response = await axios.get('/api/v1/scalping/signals', {
  params: {
    market_condition: 'bull',
    risk_level: 'conservative',
    min_confidence: 0.8
  }
})

// 響應示例
{
  "signals": [
    {
      "id": "BTCUSDT_15m_LONG_1703123456",
      "symbol": "BTCUSDT",
      "signal_type": "LONG",
      "confidence": 0.89,
      "urgency_level": "high",
      "entry_price": 43250,
      "stop_loss": 42731,
      "take_profit": 45327,
      "risk_reward_ratio": 4.0,
      "market_condition": {
        "trend": "bull",
        "phase": "main_bull",
        "confidence": 0.85
      },
      "breakout_analysis": {
        "is_breakout": true,
        "breakout_type": "volume_price_breakout",
        "strength": 0.78
      },
      "reasoning": "牛市環境(牛市分數8.2) | 當前處於主升段 | 檢測到volume_price_breakout突破(強度0.78) | 建議做多",
      "strategy_name": "牛市主升-15m",
      "atr_adjusted": true,
      "market_condition_adjusted": true
    }
  ],
  "total_signals": 8,
  "market_analysis": {
    "overall_trend": "bullish",
    "avg_confidence": 0.823,
    "breakout_signals": 5,
    "bull_bear_ratio": 3.5
  }
}
```

### 4. 獲取歷史統計

```javascript
// 獲取過去30天的表現統計
const response = await axios.get('/api/v1/market-analysis/history/statistics?days=30')

// 響應示例
{
  "statistics": {
    "total_signals": 247,
    "win_count": 156,
    "loss_count": 67,
    "breakeven_count": 24,
    "win_rate": 63.16,
    "avg_profit_pct": 2.34,
    "avg_loss_pct": -1.12,
    "avg_hold_time_minutes": 127.5,
    "best_performer": {
      "symbol": "ETHUSDT",
      "profit_pct": 8.45,
      "strategy": "牛市主升-5m",
      "date": "2024-01-15 14:23"
    }
  },
  "performance_analysis": {
    "symbol_performance": {
      "BTCUSDT": {
        "total_trades": 89,
        "win_rate": 67.4,
        "avg_profit_loss": 1.87
      }
    },
    "strategy_performance": {
      "牛市主升-15m": {
        "total_trades": 45,
        "win_rate": 71.1,
        "avg_profit_loss": 2.12
      }
    }
  }
}
```

## 前端整合

### 新增增強儀表板組件

新的 `EnhancedDashboard.vue` 組件提供：

1. **市場情緒總覽**: 即時顯示整體市場情緒、信號分布、牛熊分數
2. **增強短線信號**: 展示整合牛熊市分析的高品質信號
3. **歷史表現統計**: 多維度統計分析和最佳/最差表現展示
4. **快速操作**: 一鍵處理過期信號、重算歷史結果等

### 路由配置

```typescript
// 新增路由
{
  path: '/enhanced',
  name: 'EnhancedDashboard',
  component: () => import('@/views/EnhancedDashboard.vue')
}
```

訪問 `http://localhost:5173/enhanced` 即可使用增強儀表板。

## 配置說明

### 環境變數

```env
# 數據庫配置
DATABASE_URL=sqlite:///./tradingx.db

# API配置
API_HOST=0.0.0.0
API_PORT=8000

# 市場分析配置
MIN_CONFIDENCE=0.75
MAX_SIGNALS_PER_SYMBOL=3
HISTORY_RECORD_LIMIT=5000

# 快取配置
CACHE_EXPIRE_MINUTES=3
```

### 依賴安裝

```bash
# 後端依賴
pip install pandas numpy pandas-ta sqlalchemy asyncio pydantic fastapi

# 前端依賴
npm install axios vue-router@4
```

## 部署建議

### 1. 後端部署

```bash
# 安裝依賴
pip install -r requirements.txt

# 初始化資料庫
python -c "from app.core.database import create_tables; import asyncio; asyncio.run(create_tables())"

# 啟動服務
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 前端部署

```bash
# 安裝依賴
npm install

# 開發模式
npm run dev

# 生產構建
npm run build
```

### 3. Docker 部署

```bash
# 使用現有的Docker配置
docker-compose up -d
```

## 監控和維護

### 1. 日誌監控

- 市場分析服務日誌: 關注牛熊市判斷準確性
- 信號生成日誌: 監控信號品質和數量
- 歷史處理日誌: 確保過期信號及時處理

### 2. 性能指標

- API 響應時間: 市場分析 < 2s，信號生成 < 5s
- 數據庫查詢: 歷史統計 < 1s
- 記憶體使用: 監控技術指標計算的記憶體消耗

### 3. 數據清理

- 自動清理超過 5000 筆的歷史記錄
- 定期備份重要統計數據
- 監控資料庫大小和查詢性能

## 總結

通過將複雜的市場分析邏輯遷移到後端，系統實現了：

1. **更準確的分析**: 後端可以處理更複雜的計算和多因子模型
2. **更好的性能**: 避免前端重複計算，提升用戶體驗
3. **更強的擴展性**: 後端服務可以獨立擴展和優化
4. **更完整的歷史管理**: 智能數據管理和統計分析
5. **更靈活的配置**: 支持不同風險等級和市場條件的策略調整

新的架構為交易系統提供了更專業、更可靠的分析能力，能夠更好地支持實際交易決策。
