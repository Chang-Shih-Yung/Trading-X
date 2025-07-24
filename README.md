# 🚀 Trading X - 進階交易策略系統

![Trading X](https://via.placeholder.com/800x200/1f2937/ffffff?text=Trading+X+-+Advanced+Trading+Strategy+System)

## 📖 專案簡介

Trading X 是一個功能完整的加密貨幣交易策略系統，提供實時市場數據分析、技術指標計算、交易信號生成、新聞分析和回測功能。

### ✨ 主要特色

- 🔥 **實時市場數據** - 整合多個交易所 API，提供即時價格和交易數據
- 📊 **技術分析** - 內建多種技術指標（MA、RSI、MACD、布林帶等）
- 🎯 **智能信號** - 自動生成買賣信號和風險評估
- 📰 **新聞分析** - 多源新聞聚合，包含市場情緒分析
- 🔄 **回測系統** - 歷史數據回測，驗證策略效果
- 📱 **響應式界面** - 現代化 Web 界面，支援桌機和手機
- 🚀 **高性能** - 異步處理，支援高併發請求

## 🛠️ 技術架構

### 後端技術棧

- **框架**: FastAPI (Python 3.9+)
- **數據庫**: SQLAlchemy 2.0 + SQLite
- **API**: RESTful API with automatic OpenAPI documentation
- **異步**: 完全異步處理，支援高併發
- **市場數據**: CCXT 整合多家交易所
- **新聞來源**: CoinTelegraph RSS, CryptoPanic API, 區塊鏈新聞聚合

### 前端技術棧

- **框架**: Vue.js 3 + TypeScript
- **構建工具**: Vite
- **樣式**: Tailwind CSS
- **HTTP 客戶端**: Axios
- **路由**: Vue Router 4
- **狀態管理**: Composition API

## 🚀 快速開始

### Windows 用戶

1. 下載專案到本地
2. 雙擊 `start_all.ps1` 一鍵啟動
3. 瀏覽器訪問 http://localhost:3000

詳細指南：[Windows 安裝指南](WINDOWS_SETUP_GUIDE.md) | [快速開始](QUICK_START.md)

### macOS/Linux 用戶

```bash
# 克隆專案
git clone https://github.com/Chang-Shih-Yung/Trading-X.git
cd Trading-X

# 安裝後端依賴並啟動
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 安裝前端依賴並啟動（新終端）
cd frontend
npm install
npm run dev
```

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
