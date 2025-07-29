# Trading X 測試腳本集合

這個資料夾包含了 Trading X 系統的所有測試腳本，按功能分類整理。

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
