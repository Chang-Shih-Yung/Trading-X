# Trading-X 自動化系統測試套件

這個目錄包含了 Trading-X 自動化交易系統的完整測試套件，用於驗證系統的各項功能和性能。

## 🎯 測試目標

驗證完整的自動化流程：
```
WebSocket 即時數據收集 → pandas-ta 技術分析 → 交易信號生成 → WebSocket 信號廣播
```

## 📁 新版測試結構

```
TEST/
├── realtime_signals/           # 即時信號引擎測試
│   ├── test_realtime_signal_engine.py     # 引擎基礎功能測試
│   ├── test_pandas_ta_integration.py      # pandas-ta 整合測試
│   └── test_automation_flow.py            # 端到端自動化流程測試
├── performance/                # 性能測試
│   └── test_performance_load.py           # 性能與負載測試
├── data_management/            # 數據管理測試
│   └── test_data_cleanup.py               # 數據清理與管理測試
└── run_comprehensive_tests.py             # 綜合測試運行器
```

## 🚀 快速開始

### 運行所有測試
```bash
cd TEST
python run_comprehensive_tests.py
```

### 運行特定測試類別

#### 即時信號引擎測試
```bash
# 引擎基礎功能
python realtime_signals/test_realtime_signal_engine.py

# pandas-ta 整合
python realtime_signals/test_pandas_ta_integration.py

# 端到端自動化流程
python realtime_signals/test_automation_flow.py
```

#### 性能測試
```bash
# 注意：性能測試需要安裝 psutil
pip install psutil aiohttp

python performance/test_performance_load.py
```

#### 數據管理測試
```bash
python data_management/test_data_cleanup.py
```

## 🧪 測試詳情

### 1. 即時信號引擎測試 (`realtime_signals/`)

#### `test_realtime_signal_engine.py`
- **目的**: 測試信號引擎的基礎功能
- **測試項目**:
  - 引擎生命週期（啟動、停止、狀態檢查）
  - WebSocket 信號接收
  - 配置更新功能
  - 信號歷史查詢

#### `test_pandas_ta_integration.py`
- **目的**: 測試 pandas-ta 技術指標整合
- **測試項目**:
  - 技術指標計算（RSI, MACD, Bollinger Bands 等）
  - 信號生成邏輯驗證
  - 多時間框架分析
  - 指標計算性能

#### `test_automation_flow.py`
- **目的**: 測試完整自動化流程
- **測試項目**:
  - 端到端數據流驗證
  - WebSocket 數據收集 → 分析 → 信號廣播
  - 流程時間性能
  - 自動化觸發機制

### 2. 性能測試 (`performance/`)

#### `test_performance_load.py`
- **目的**: 測試系統性能與負載能力
- **測試項目**:
  - 並發請求處理能力
  - WebSocket 連接負載測試
  - 記憶體洩漏檢測
  - 持續負載穩定性

### 3. 數據管理測試 (`data_management/`)

#### `test_data_cleanup.py`
- **目的**: 測試數據存儲與清理機制
- **測試項目**:
  - 數據存儲和檢索功能
  - 7天自動清理週期
  - 數據庫完整性檢查
  - 存儲效率測試

## 📊 測試報告

運行 `run_comprehensive_tests.py` 會生成：

1. **控制台報告**: 即時顯示測試進度和結果
2. **JSON 報告**: `comprehensive_test_report.json` 包含詳細數據

### 報告內容
- 測試執行統計
- 各類別成功率
- 系統健康評估
- 核心功能狀態
- 改善建議

## 🏥 系統健康評估標準

| 成功率 | 狀態 | 說明 |
|--------|------|------|
| ≥90% | 優秀 | 系統運行完美 |
| ≥75% | 良好 | 基本正常，少量問題 |
| ≥50% | 需改善 | 部分功能異常 |
| <50% | 嚴重問題 | 需要立即處理 |

## 🔧 測試環境要求

### 基本要求
- Python 3.9+
- 後端服務運行在 `localhost:8000`
- SQLite 數據庫 (`tradingx.db`)

### 可選依賴
```bash
# 性能測試需要
pip install psutil aiohttp

# WebSocket 測試需要
pip install websockets

# HTTP 請求測試需要
pip install requests
```

## 🚨 故障排除

### 常見問題

1. **連接失敗**
   ```
   確保後端服務運行: uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **模組導入錯誤**
   ```bash
   pip install -r requirements.txt
   ```

3. **數據庫錯誤**
   ```
   檢查 tradingx.db 文件存在且可讀寫
   ```

4. **WebSocket 連接超時**
   ```
   檢查防火牆設置和網路連接
   ```

### 調試模式
在測試腳本開頭設置：
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📈 持續集成

建議將測試整合到 CI/CD 流程：

```yaml
# .github/workflows/test.yml 示例
name: Comprehensive Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Start backend
        run: uvicorn main:app --host 0.0.0.0 --port 8000 &
      - name: Run tests
        run: python TEST/run_comprehensive_tests.py
```

## 🎯 核心驗證目標

這個測試套件確保以下核心功能正常工作：

✅ **WebSocket 即時數據收集**: 驗證能夠即時接收市場數據
✅ **pandas-ta 技術分析**: 驗證技術指標計算準確性
✅ **智能信號生成**: 驗證交易信號邏輯正確性
✅ **自動化流程**: 驗證端到端自動化無縫運行
✅ **數據管理**: 驗證數據存儲和清理機制
✅ **系統性能**: 驗證高負載下的穩定性

通過這個全面的測試套件，確保 Trading-X 自動化交易系統能夠可靠、高效地運行。

---

## 📂 歷史測試檔案

以下為舊有的測試檔案，保留供參考：

## 📁 資料夾結構

### 🔧 backend/ - 後端測試腳本
- `test_precision_signal.py` - 精準信號時間顯示和過期機制測試
- `test_real_price.py` - 實時價格數據獲取測試
- `test_timeframe_integration.py` - 時間框架整合測試
- `verify_signals.py` - 信號驗證腳本
- `test_trading_system.py` - 交易系統整體測試

### 🎨 frontend/ - 前端測試腳本
- `test_frontend_display.js` - 前端顯示功能測試
- `test_time_format.js` - 時間格式測試

### ⚙️ config/ - 配置測試腳本
- `test_config.py` - 配置文件測試

## 🚀 使用方法

### 後端測試
```bash
# 切換到項目根目錄
cd /Users/henrychang/Desktop/Trading-X

# 運行精準信號測試
python TEST/backend/test_precision_signal.py

# 運行實時價格測試
python TEST/backend/test_real_price.py

# 運行時間框架整合測試
python TEST/backend/test_timeframe_integration.py

# 運行信號驗證
python TEST/backend/verify_signals.py

# 運行完整交易系統測試
pytest TEST/backend/test_trading_system.py -v
```

### 前端測試
```bash
# 運行前端測試需要在瀏覽器中執行
# 或使用 Node.js 環境：
node TEST/frontend/test_frontend_display.js
node TEST/frontend/test_time_format.js
```

### 配置測試
```bash
# 測試配置文件
python TEST/config/test_config.py
```

## 📋 測試功能說明

### 精準信號測試 (`test_precision_signal.py`)
- ✅ 創建20秒過期的測試信號
- ✅ 驗證時間顯示正確性
- ✅ 測試自動過期機制
- ✅ 檢查歷史數據記錄
- ✅ 清理測試數據

### 實時價格測試 (`test_real_price.py`)
- 測試價格數據獲取
- 驗證數據格式
- 檢查更新頻率

### 時間框架整合測試 (`test_timeframe_integration.py`)
- 測試多時間框架分析
- 驗證時間框架轉換
- 檢查信號一致性

### 信號驗證 (`verify_signals.py`)
- ✅ 創建符合精準門檻的15秒測試信號
- ✅ 驗證信號出現在活躍列表中
- ✅ 測試時間倒數功能
- ✅ 驗證信號自動過期機制
- ✅ 檢查歷史數據頁面顯示
- ✅ 自動清理測試數據

## 🎯 測試最佳實踐

1. **運行前確保後端服務啟動**：
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **測試順序建議**：
   - 先運行配置測試
   - 再運行後端API測試
   - 最後運行前端測試

3. **清理測試數據**：
   - 大部分測試腳本會自動清理
   - 如需手動清理，請參考各腳本的清理函數

## 🛠️ 維護說明

- 新增測試腳本請放入對應的子資料夾
- 更新此 README 文件說明新腳本的用途
- 保持測試腳本的獨立性，避免相互依賴
- 定期檢查測試腳本是否仍然有效

## 📊 測試報告

測試結果會輸出到控制台，包含：
- ✅ 成功項目
- ❌ 失敗項目  
- ⚠️ 警告信息
- 📊 統計數據

---

**最後更新**: 2025-07-29
**維護者**: Trading X 開發團隊
