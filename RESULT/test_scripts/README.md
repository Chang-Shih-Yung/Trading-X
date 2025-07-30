# 測試腳本說明文檔

## 📝 腳本總覽

本目錄包含自動化測試腳本，用於驗證Trading X系統的各項功能和性能。

---

## 🧪 test_realtime_fixed.py

### 腳本用途
**主要功能**: 即時市場數據整合系統的完整自動化測試  
**測試目標**: 驗證API端點、WebSocket連接、數據正確性和系統穩定性  
**適用階段**: 第一階段 - 即時市場數據整合

### 技術特點
- **異步設計**: 使用asyncio和aiohttp進行異步測試
- **WebSocket支援**: 完整的WebSocket連接和消息測試
- **自動清理**: 測試完成後自動清理資源
- **詳細日誌**: 每個測試步驟都有詳細記錄
- **JSON輸出**: 結構化的測試結果輸出

### 測試範圍

#### 1. 服務狀態測試 (3項)
```python
await tester.test_service_status()
```
- 檢查服務運行狀態
- 驗證WebSocket啟用狀態  
- 統計活躍連接數

#### 2. API響應格式測試 (3項)
```python
await tester.test_api_response_format()
```
- 驗證必要響應字段 (`success`, `data`, `timestamp`)
- 檢查數據結構完整性
- 確認HTTP狀態碼正確性

#### 3. 價格數據內容測試 (2項)
```python
await tester.test_price_data_content()
```
- 驗證價格數據格式和內容
- 檢查數值範圍合理性
- 確認時間戳準確性

#### 4. WebSocket連接測試 (7項)
```python
await tester.test_websocket_connection()
```
- WebSocket連接建立和確認
- 訂閱/取消訂閱功能
- 即時數據推送接收
- 心跳機制驗證

### 使用方法

#### 環境準備
```bash
# 確保系統已啟動
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 安裝依賴（如果需要）
pip install aiohttp websockets
```

#### 執行測試
```bash
cd /Users/henrychang/Desktop/Trading-X
python test_realtime_fixed.py
```

#### 查看結果
```bash
# 檢查控制台輸出
cat test_realtime_fixed_results.json | jq

# 查看測試總結
python -c "
import json
with open('test_realtime_fixed_results.json', 'r') as f:
    results = json.load(f)
print(f'總測試: {len(results[\"api_tests\"]) + len(results[\"websocket_tests\"])}')
print(f'錯誤數: {len(results[\"errors\"])}')
"
```

### 測試配置

#### 基礎設定
```python
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/realtime/ws"
```

#### 測試參數
- **連接超時**: 5-30秒（根據測試項目調整）
- **重試機制**: 自動重試失敗的連接
- **數據驗證**: 多層次數據格式驗證
- **錯誤處理**: 捕獲並記錄所有異常

### 輸出格式

#### 控制台輸出
```
開始改進版即時市場數據測試...
測試目標: http://localhost:8000

=== 服務狀態測試 ===
✅ 服務狀態_服務運行狀態: 服務運行狀態: True
✅ 服務狀態_WebSocket啟用狀態: WebSocket啟用狀態: True
...

============================================================
測試總結報告
============================================================
總測試數: 15
成功: 15 | 失敗: 0
成功率: 100.0%
✅ 所有測試都通過了！
```

#### JSON結果文件
```json
{
  "api_tests": {
    "服務狀態_服務運行狀態": {
      "success": true,
      "message": "服務運行狀態: True",
      "timestamp": "2025-07-30T11:30:40.285422",
      "data": {"service_running": true}
    }
  },
  "websocket_tests": {...},
  "start_time": "2025-07-30T11:30:40.274672",
  "errors": []
}
```

### 錯誤處理

#### 常見錯誤類型
1. **連接錯誤**: 服務未啟動或端口被佔用
2. **超時錯誤**: 響應時間過長
3. **格式錯誤**: API響應格式不符合預期
4. **數據錯誤**: 價格數據異常或缺失

#### 排錯指南
```bash
# 檢查服務狀態
curl http://localhost:8000/health

# 檢查端口佔用
lsof -i :8000

# 查看服務日誌
tail -f server.log

# 重啟服務
pkill -f uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 擴展指南

#### 添加新測試
```python
async def test_new_feature(self):
    """測試新功能"""
    try:
        # 測試邏輯
        result = await some_api_call()
        
        # 驗證結果
        assert result.get("success") == True
        
        self.log_result("新功能測試", True, "測試通過", result)
    except Exception as e:
        self.log_result("新功能測試", False, f"測試失敗: {e}")
```

#### 自定義配置
```python
class CustomTester(RealtimeDataTester):
    def __init__(self, custom_config):
        super().__init__()
        self.config = custom_config
```

### 最佳實踐

#### 測試設計
1. **獨立性**: 每個測試獨立運行，不依賴其他測試
2. **冪等性**: 多次執行結果一致
3. **完整性**: 覆蓋正常和異常情況
4. **可讀性**: 清晰的測試名稱和日誌

#### 維護建議
1. **定期更新**: 隨功能變化更新測試
2. **性能監控**: 關注測試執行時間
3. **結果分析**: 定期分析測試結果趨勢
4. **自動化**: 集成到CI/CD流程

---

## 🔄 持續集成

### 自動化執行
```yaml
# GitHub Actions 範例
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Tests
        run: python test_realtime_fixed.py
```

### 測試報告
- 自動生成測試報告
- 結果通知和告警
- 歷史趨勢分析
- 性能指標追蹤

---

*最後更新: 2025年7月30日*  
*腳本版本: v1.0 - 即時數據整合測試*
