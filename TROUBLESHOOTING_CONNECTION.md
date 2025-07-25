# 連接超時問題診斷和修復指南

## 問題描述

前端應用出現 `ERR_CONNECTION_TIMED_OUT` 錯誤，無法連接到後端 API (localhost:8000)。

## 已修復的問題

### 1. 後端導入錯誤修復

- ✅ 修復了 `models.py` 中 `Signal` 和 `TradingSignal` 模型的導入問題
- ✅ 添加了向後兼容的別名 `Signal = TradingSignal`
- ✅ 修復了 signals.py 中缺少 logger 的問題

### 2. 前端 API 配置優化

- ✅ 創建了統一的 API 配置文件 (`utils/api.ts`)
- ✅ 增加了超時時間到 15 秒
- ✅ 添加了自動重試機制 (3 次重試)
- ✅ 添加了健康檢查和服務等待機制
- ✅ 更新了主要 API 調用使用新的配置

### 3. 服務狀態改進

- ✅ 改進了服務狀態檢查機制
- ✅ 添加了服務等待功能
- ✅ 改進了錯誤處理和用戶反饋

## 服務運行狀態

### 後端服務 (端口 8000)

- ✅ 服務正常運行
- ✅ 健康檢查通過: `curl http://localhost:8000/health`
- ✅ API 端點響應正常

### 前端服務 (端口 3000)

- ✅ 前端開發服務器正常運行
- ✅ 可訪問 http://localhost:3000

## 問題可能的原因

### 1. 網絡配置問題

- 防火牆阻止 localhost 連接
- DNS 解析問題
- 網絡適配器配置

### 2. 瀏覽器安全策略

- CORS 設置
- 安全模式限制
- 瀏覽器緩存問題

### 3. 系統資源問題

- 端口占用
- 記憶體不足
- CPU 負載過高

## 診斷步驟

### 1. 檢查服務運行狀態

```bash
# 檢查後端服務
curl http://localhost:8000/health

# 檢查前端服務
curl http://localhost:3000

# 檢查端口占用
lsof -i :8000
lsof -i :3000
```

### 2. 檢查網絡連通性

```bash
# ping localhost
ping localhost

# 檢查 localhost 解析
nslookup localhost

# 測試端口連接
telnet localhost 8000
```

### 3. 瀏覽器診斷

- 打開開發者工具 (F12)
- 檢查 Network 標籤
- 清除瀏覽器緩存
- 嘗試隱私模式

## 修復建議

### 1. 立即解決方案

- ✅ 重啟後端和前端服務
- ✅ 使用新的 API 配置和重試機制
- ✅ 檢查服務健康狀態

### 2. 網絡修復

```bash
# 清除 DNS 緩存 (macOS)
sudo dscacheutil -flushcache

# 重置網絡設置
sudo ifconfig lo0 down
sudo ifconfig lo0 up
```

### 3. 瀏覽器修復

- 清除瀏覽器緩存和 Cookie
- 禁用瀏覽器擴展
- 嘗試其他瀏覽器

### 4. 系統修復

```bash
# 檢查系統資源
top
df -h

# 重啟網絡服務 (如果需要)
sudo launchctl unload /Library/LaunchDaemons/com.apple.mDNSResponder.plist
sudo launchctl load /Library/LaunchDaemons/com.apple.mDNSResponder.plist
```

## 新功能特性

### API 重試機制

- 自動重試失敗的請求 (最多 3 次)
- 智能延遲重試 (指數退避)
- 網絡錯誤自動恢復

### 健康檢查

- 服務啟動等待機制
- 實時服務狀態監控
- 自動故障恢復

### 用戶體驗改進

- 更友好的錯誤提示
- 離線模式支持
- 加載狀態優化

## 監控和日誌

### 後端日誌監控

後端服務會輸出詳細的請求日誌，包括：

- 請求響應時間
- API 調用統計
- 錯誤詳情

### 前端錯誤監控

前端會記錄：

- API 請求時間
- 重試次數
- 網絡狀態

## 聯絡支援

如果問題持續存在，請提供：

1. 瀏覽器開發者工具的 Network 截圖
2. 後端服務日誌
3. 系統信息 (OS 版本、瀏覽器版本)
4. 嘗試過的修復步驟

---

更新時間: 2025-07-25
版本: 1.0.0
