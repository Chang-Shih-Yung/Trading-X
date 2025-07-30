# 即時市場數據API整合指南

## 📋 概述

本系統已成功整合幣安（Binance）即時市場數據API，提供 WebSocket 和 RESTful API 兩種數據獲取方式，支援即時價格、深度、K線數據的獲取和推送。

## 🚀 核心功能

### 1. 交易所API整合
- ✅ **幣安（Binance）**: 使用 CCXT 和原生 WebSocket API
- ✅ **OKX**: 使用 CCXT API（備用）
- 🔄 **可擴展**: 支援添加更多交易所

### 2. 數據更新機制
- ✅ **WebSocket 即時串流**: 毫秒級數據更新
- ✅ **RESTful API 輪詢**: 備用數據獲取方式
- ✅ **自動容錯切換**: WebSocket 失敗時自動切換到輪詢模式

### 3. 支援的數據類型
- 📊 **即時價格**: 24小時價格變化、成交量
- 📈 **K線數據**: 多時間間隔（1m, 5m, 15m, 1h, 4h, 1d）
- 📋 **深度數據**: 買賣盤前10檔報價
- 🎯 **市場總覽**: 漲跌排行、市場統計

## 🔧 技術架構

### WebSocket 客戶端
```python
app/services/binance_websocket.py
├── BinanceWebSocketClient    # WebSocket 連接管理
├── BinanceDataCollector     # 數據收集器
├── TickerData              # 價格數據結構
├── KlineData               # K線數據結構
└── DepthData               # 深度數據結構
```

### 市場數據服務
```python
app/services/market_data.py
├── MarketDataService        # 增強版市場數據服務
├── _setup_websocket_callbacks  # WebSocket 回調設置
├── get_realtime_price      # 即時價格獲取
├── get_realtime_depth      # 即時深度獲取
└── get_market_summary      # 市場總覽
```

### API 端點
```python
app/api/v1/endpoints/realtime_market.py
├── /realtime/prices        # 即時價格API
├── /realtime/depth/{symbol} # 深度數據API
├── /realtime/klines/{symbol} # K線數據API
├── /realtime/summary       # 市場總覽API
├── /realtime/all          # 所有數據API
├── /realtime/ws           # WebSocket端點
└── /realtime/status       # 服務狀態API
```

## 📡 API 使用說明

### 1. 啟動即時數據服務

```bash
POST /api/v1/market/realtime/start
```

**請求體**:
```json
{
  "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
  "intervals": ["1m", "5m", "1h"]
}
```

**響應**:
```json
{
  "success": true,
  "message": "即時數據服務啟動成功",
  "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
  "intervals": ["1m", "5m", "1h"],
  "websocket_enabled": true,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. 獲取即時價格

```bash
GET /api/v1/market/realtime/prices?symbols=BTCUSDT,ETHUSDT
```

**響應**:
```json
{
  "success": true,
  "data": {
    "BTCUSDT": {
      "symbol": "BTCUSDT",
      "price": 45000.50,
      "change": 1200.30,
      "change_percent": 2.74,
      "high_24h": 46000.00,
      "low_24h": 43500.00,
      "volume_24h": 25000.50,
      "timestamp": "2024-01-01T12:00:00Z"
    }
  },
  "count": 1,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 3. 獲取深度數據

```bash
GET /api/v1/market/realtime/depth/BTCUSDT
```

**響應**:
```json
{
  "success": true,
  "data": {
    "symbol": "BTCUSDT",
    "bids": [[45000.50, 1.25], [45000.00, 2.50]],
    "asks": [[45001.00, 1.10], [45001.50, 3.20]],
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 4. 獲取K線數據

```bash
GET /api/v1/market/realtime/klines/BTCUSDT?interval=1m
```

**響應**:
```json
{
  "success": true,
  "data": {
    "symbol": "BTCUSDT",
    "interval": "1m",
    "open": 45000.00,
    "high": 45100.00,
    "low": 44950.00,
    "close": 45050.00,
    "volume": 125.50,
    "trade_count": 450,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 5. 獲取市場總覽

```bash
GET /api/v1/market/realtime/summary
```

**響應**:
```json
{
  "success": true,
  "data": {
    "total_symbols": 6,
    "active_symbols": 6,
    "avg_change_percent": 1.25,
    "top_gainers": [...],
    "top_losers": [...],
    "total_volume": 150000.75,
    "websocket_status": "enabled",
    "last_update": "2024-01-01T12:00:00Z"
  }
}
```

## 🔌 WebSocket 使用說明

### 連接端點
```
ws://localhost:8000/api/v1/market/realtime/ws
```

### 訂閱數據
發送訂閱消息：
```json
{
  "action": "subscribe",
  "symbols": ["BTCUSDT", "ETHUSDT"],
  "data_types": ["prices", "depths", "klines"]
}
```

### 接收數據
系統會推送以下類型的消息：
```json
{
  "type": "price_update",
  "data": {
    "symbol": "BTCUSDT",
    "price": 45000.50,
    "change_percent": 2.74,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 取消訂閱
```json
{
  "action": "unsubscribe"
}
```

### 心跳檢測
```json
{
  "action": "ping"
}
```

響應：
```json
{
  "type": "pong",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🧪 測試方法

### 1. 運行後端服務
```bash
cd /Users/henrychang/Desktop/Trading-X
uvicorn main:app --reload
```

### 2. 執行API測試
```bash
cd TEST
python test_realtime_integration.py
```

### 3. 使用API文檔測試
訪問: http://localhost:8000/docs

在 Swagger UI 中測試各個端點

### 4. WebSocket 測試
使用瀏覽器控制台或 WebSocket 客戶端：
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/market/realtime/ws');

ws.onopen = function() {
    ws.send(JSON.stringify({
        action: 'subscribe',
        symbols: ['BTCUSDT', 'ETHUSDT']
    }));
};

ws.onmessage = function(event) {
    console.log('收到數據:', JSON.parse(event.data));
};
```

## 📊 性能特性

### 延遲特性
- **WebSocket 模式**: < 100ms 延遲
- **RESTful API**: < 500ms 響應時間
- **數據庫儲存**: 異步批量插入

### 吞吐量
- **並發連接**: 支援多個 WebSocket 連接
- **請求處理**: > 100 RPS
- **數據更新頻率**: 每秒多次更新

### 容錯機制
- **自動重連**: WebSocket 斷線自動重連
- **備用模式**: WebSocket 失敗時切換到輪詢
- **錯誤恢復**: 服務異常時自動重試

## 🛠️ 配置選項

### 監控的交易對
預設監控的主要交易對：
```python
symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'DOGEUSDT']
```

### 時間間隔
支援的K線時間間隔：
```python
intervals = ['1m', '5m', '15m', '1h', '4h', '1d']
```

### WebSocket 更新頻率
- **價格數據**: 實時推送
- **K線數據**: 每根K線關閉時推送
- **深度數據**: 100ms 間隔推送

## 🔄 系統整合

### 與現有系統的整合
1. **信號生成**: 即時數據自動提供給 pandas-ta 優化系統
2. **策略引擎**: 可接收即時價格進行策略計算
3. **資料庫儲存**: 自動將K線數據儲存到 SQLite 資料庫

### 前端整合
前端可通過以下方式獲取即時數據：
1. **RESTful API**: 定期輪詢獲取數據
2. **WebSocket**: 建立持續連接接收推送
3. **混合模式**: 初始載入用API，後續更新用WebSocket

## 🚨 注意事項

### 1. 網路連接
- 需要穩定的網路連接到幣安服務器
- 建議使用有線網路以獲得最佳性能

### 2. API 限制
- 幣安公共API有請求頻率限制
- WebSocket 連接數有限制
- 建議合理控制請求頻率

### 3. 數據準確性
- 數據來源為幣安公共API
- 價格可能與實際交易略有延遲
- 用於分析參考，實際交易需謹慎

### 4. 系統資源
- WebSocket 連接會占用系統資源
- 大量數據儲存需要足夠磁碟空間
- 建議監控系統性能

## 📈 未來擴展

### 1. 更多交易所
- 準備整合 OKX、火幣等其他交易所
- 統一數據格式和API介面

### 2. 更多數據類型
- 交易歷史數據
- 資金費率數據
- 期貨合約數據

### 3. 智能分析
- 實時技術指標計算
- 異常價格變動檢測
- 套利機會識別

---

## 🆘 問題排查

### 常見問題

**Q: WebSocket 連接失敗？**
A: 檢查網路連接，確保可以訪問 stream.binance.com

**Q: 數據更新緩慢？**
A: 檢查系統資源使用情況，可能需要優化配置

**Q: API 響應錯誤？**
A: 查看日誌文件，檢查是否有API限制或網路問題

### 日誌查看
系統日誌會顯示詳細的運行狀態：
```bash
# 查看服務啟動日誌
tail -f logs/market_data.log

# 查看WebSocket連接日誌  
tail -f logs/websocket.log
```

---

**更新時間**: 2024年1月
**版本**: v1.0.0
**維護者**: Trading X 開發團隊
