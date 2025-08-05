# 🎯 Trading-X 系統

> **重要：本系統使用 100% 真實數據，不包含任何模擬或回退機制**

## 📁 系統架構

```
X/
├── 🎯 strategies/          # 交易策略模組
│   ├── phase1/            # Phase1 基礎策略
│   │   ├── phase1b_volatility_adaptation.py      # 波動性適應引擎
│   │   └── phase1c_signal_standardization.py     # 信號標準化引擎
│   └── phase3/            # Phase3 高級策略
│       └── phase3_market_analyzer.py              # 市場深度分析器
├── 🔧 core/               # 核心系統組件
│   ├── binance_data_connector.py                  # 真實幣安數據連接器
│   ├── real_data_signal_quality_engine.py         # 信號品質控制引擎
│   └── signal_scoring_engine.py                   # 信號評分引擎
├── 📊 indicators/         # 技術指標模組
│   └── pandas_ta_indicators.py                    # 技術指標計算引擎
├── 📡 monitoring/         # 監控系統
│   ├── real_time_market_monitor.py                # 即時市場監控
│   ├── real_time_unified_monitoring_manager.py    # 統一監控管理
│   └── monitoring_api.py                          # 監控 API 接口
├── 🛠️ utils/             # 工具與測試
│   ├── test_real_binance_data.py                  # 真實數據測試
│   └── quick_system_verification.py               # 系統驗證工具
├── 🌐 frontend/          # 前端界面
├── ⚙️ config.py          # 系統配置
├── 🚀 launcher.py        # 系統啟動器  
└── 📋 main.py            # 傳統啟動方式
```

## 🚀 快速啟動

### 方法一：使用新啟動器（推薦）
```bash
# 完整系統啟動
python launcher.py --mode full

# 僅啟動監控系統
python launcher.py --mode monitoring

# 僅啟動API服務
python launcher.py --mode api

# 系統測試
python launcher.py --mode test
```

### 方法二：傳統啟動
```bash
# 啟動完整系統
python main.py
```

### 4. 啟動監控
```bash
curl -X POST http://localhost:8001/api/v1/x-monitoring/start
```

## API端點說明

### 系統控制
- `POST /api/v1/x-monitoring/start` - 啟動監控
- `POST /api/v1/x-monitoring/stop` - 停止監控
- `GET /api/v1/x-monitoring/status` - 系統狀態

### 數據查詢
- `GET /api/v1/x-monitoring/dashboard` - 監控儀表板
- `GET /api/v1/x-monitoring/signals/recent` - 近期信號
- `GET /api/v1/x-monitoring/signals/statistics` - 統計數據

### 配置管理
- `POST /api/v1/x-monitoring/config` - 更新配置
- `POST /api/v1/x-monitoring/signals/manual-trigger` - 手動觸發

## 監控配置

### 預設監控標的
- BTCUSDT
- ETHUSDT  
- BNBUSDT

### 處理間隔
- 預設: 30秒
- 最小: 10秒

### 通知設定
- **CRITICAL**: 5分鐘冷卻，每小時最多6次
- **HIGH**: 10分鐘冷卻，每小時最多4次
- **MEDIUM**: 30分鐘冷卻，每小時最多2次

## 信號優先級

### 五級分類系統
1. **CRITICAL** - 高質量確認信號，立即執行
2. **HIGH** - 強信號，謹慎執行
3. **MEDIUM** - 中等信號，監控準備
4. **LOW** - 弱信號，低優先級觀察
5. **REJECTED** - 被拒絕信號

### 決策因子
- 信號強度 (25%)
- 市場環境評分 (25%)
- 風險評估評分 (25%)
- 時機優化評分 (15%)
- 組合適配評分 (10%)

## 數據完整性檢查

### 四級狀態
- **COMPLETE** - 數據完整 (≥90%)
- **PARTIAL** - 數據部分缺失 (70-89%)
- **INCOMPLETE** - 數據不完整 (50-69%)
- **INVALID** - 數據無效 (<50%)

### 品質要求
- 最低數據完整性要求: 80%
- 信號記憶體大小: 100個
- 去重時間窗口: 5分鐘

## 檔案結構

```
X/
├── __init__.py                              # 包初始化
├── main.py                                  # 主程式入口
├── real_data_signal_quality_engine.py      # 信號質量控制引擎
├── real_time_unified_monitoring_manager.py # 統一監控管理器
├── monitoring_api.py                        # API端點
└── README.md                               # 說明文檔
```

## 系統特色

### 🎯 真實數據驅動
- 直接使用現有Phase系統的真實數據
- 無測試數據，無模擬數據
- 數據完整性實時驗證

### 🔧 兩階段架構
- Stage 1: 信號候選者池篩選
- Stage 2: EPL執行決策層判斷
- 多維度評估確保信號品質

### 📧 智能通知系統
- 基於優先級的冷卻時間
- 每小時通知數量限制
- Gmail整合自動發送

### 📊 完整監控
- 即時系統狀態監控
- 信號歷史記錄管理
- 統計數據自動追蹤

## 日誌記錄

系統自動記錄到 `x_monitoring.log` 檔案，包含：
- 系統啟動/關閉事件
- 信號處理記錄
- 錯誤診斷信息
- 性能統計數據

## 注意事項

1. **埠號使用**: 系統使用 8001 埠，避免與主系統 (8000) 衝突
2. **資源使用**: 30秒間隔監控，資源使用適中
3. **數據依賴**: 需要主系統的 Phase 服務正常運行
4. **Gmail設定**: 需要正確配置Gmail通知服務

## 故障排除

### 常見問題
1. **無法導入app模組**: 確保在Trading-X根目錄執行
2. **數據獲取失敗**: 檢查Phase系統服務狀態
3. **通知發送失敗**: 驗證Gmail服務配置
4. **埠號衝突**: 修改main.py中的埠號設定

### 檢查指令
```bash
# 系統狀態
curl http://localhost:8001/api/v1/x-monitoring/health

# 監控狀態  
curl http://localhost:8001/api/v1/x-monitoring/status

# 手動觸發測試
curl -X POST "http://localhost:8001/api/v1/x-monitoring/signals/manual-trigger?symbol=BTCUSDT&force=true"
```

---

**版本**: 1.0.0  
**最後更新**: 2025-01-15  
**維護**: Trading X 開發團隊
