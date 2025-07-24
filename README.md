# 進階交易策略系統 Trading X

## 專案概述

這是一個完整的進階交易策略系統，整合即時行情數據、多重技術指標分析、AI 策略輔助和自動化交易信號。

## 系統架構

### 🔍 [1] 資料來源與行情引擎

- ✅ 即時 K 線數據串接（Binance/OKX API）
- ✅ 歷史行情數據處理（OHLCV）
- ✅ 時間軸快取系統
- ✅ 多時間框架支援

### 📈 [2] 技術指標計算模組

- **核心指標**：
  - 支撐/壓力點（Pivot Points）
  - 布林通道（Bollinger Bands）
  - ATR（Average True Range）
  - MACD / RSI
  - EMA/SMA 移動平均
  - 成交量指標
  - 斐波那契回調
  - 一目均衡表

### 🧠 [3] 盈虧比策略引擎

- 多重條件判斷邏輯
- 動態止損/止盈計算
- 風險管理模組
- 信號強度評分系統

### 🤖 [4] AI 策略輔助

- 機器學習預測模型
- 模式識別
- 情緒分析整合
- 策略優化建議

### 📊 [5] 回測與分析

- 歷史數據回測
- 績效分析報告
- 風險指標計算
- 策略比較工具

### 💡 [6] 通知與部署

- 即時信號推播
- Web 介面監控
- API 服務
- 雲端部署支援

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 配置環境變數

```bash
cp .env.example .env
# 編輯 .env 檔案，添加API金鑰
```

### 3. 初始化資料庫

```bash
python -m alembic upgrade head
```

### 4. 啟動服務

```bash
# 啟動後端API
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 啟動Celery任務
celery -A app.celery worker --loglevel=info

# 啟動前端 (在frontend目錄)
npm run dev
```

## 技術堆疊

- **後端**: Python, FastAPI, SQLAlchemy, PostgreSQL
- **前端**: Vue.js 3, TypeScript, ECharts, Tailwind CSS
- **數據處理**: Pandas, NumPy, TA-Lib
- **機器學習**: TensorFlow, Scikit-learn
- **時間序列**: InfluxDB, TimescaleDB
- **快取**: Redis
- **任務排程**: Celery
- **部署**: Docker, Kubernetes

## 主要功能

### 1. 多重技術指標整合

- 趨勢指標：EMA、SMA、MACD、一目均衡表
- 動量指標：RSI、Stochastic、Williams %R
- 波動性指標：布林通道、ATR、Keltner 通道
- 成交量指標：OBV、VWAP、成交量震盪器
- 支撐壓力：Pivot Points、斐波那契、趨勢線

### 2. 智能信號生成

- 多時間框架確認
- 信號強度評分（0-100）
- 風險回報比計算
- 市場情緒分析

### 3. 風險管理

- 動態止損設定
- 倉位大小計算
- 最大回撤控制
- 相關性分析

### 4. AI 輔助決策

- 價格預測模型
- 模式識別系統
- 市場異常檢測
- 策略參數優化

## API 端點

- `GET /api/signals` - 獲取交易信號
- `GET /api/indicators` - 獲取技術指標
- `GET /api/backtest` - 執行回測
- `POST /api/strategy` - 創建自定義策略
- `GET /api/performance` - 獲取績效報告

## 部署指南

### Docker 部署

```bash
docker-compose up -d
```

### Kubernetes 部署

```bash
kubectl apply -f k8s/
```

## 貢獻指南

1. Fork 專案
2. 創建功能分支
3. 提交變更
4. 發起 Pull Request

## 授權

MIT License

## 聯絡資訊

如有問題或建議，請聯絡開發團隊。
