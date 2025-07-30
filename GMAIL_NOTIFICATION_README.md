# Gmail 通知功能使用說明

## 功能概述

Trading-X 系統現在支援當 pandas-ta 分析出交易信號時，自動透過 Gmail 發送通知到您的信箱。

## 🔧 設置步驟

### 1. 準備Gmail帳號

1. **確保您有Gmail帳號**
2. **啟用兩步驟驗證**
   - 前往 [Google帳戶安全設定](https://myaccount.google.com/security)
   - 啟用「兩步驟驗證」

3. **生成應用程式密碼**
   - 在安全設定中選擇「應用程式密碼」
   - 選擇「郵件」和您的設備
   - 生成16位應用程式密碼（記下來，只會顯示一次）

### 2. 配置系統

#### 方法一：使用配置工具（推薦）

```bash
python setup_gmail_notification.py
```

按照提示輸入：
- Gmail帳號
- 應用程式密碼
- 接收通知的郵箱（可以是同一個）

#### 方法二：手動設置環境變數

```bash
export GMAIL_SENDER="your_email@gmail.com"
export GMAIL_APP_PASSWORD="your_16_digit_app_password"
export GMAIL_RECIPIENT="your_email@gmail.com"
```

或創建 `.env` 文件：
```
GMAIL_SENDER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_digit_app_password
GMAIL_RECIPIENT=your_email@gmail.com
```

### 3. 啟動系統

設置完成後，重新啟動後端：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📧 通知設定

### 預設設定

- **最低信心度**: 70% (只有信心度 ≥ 70% 的信號才會發送通知)
- **冷卻時間**: 15分鐘 (同一交易對15分鐘內只發送一次)
- **信號類型**: 所有類型 (BUY, STRONG_BUY, SELL, STRONG_SELL)
- **緊急程度**: high, critical 等高緊急度信號優先

### 郵件內容

每封通知郵件包含：

1. **信號基本資訊**
   - 交易對 (例如: BTCUSDT)
   - 信號類型 (BUY/SELL/STRONG_BUY/STRONG_SELL)
   - 信心度百分比
   - 緊急程度

2. **價格資訊**
   - 建議進場價格
   - 止損價格
   - 止盈價格
   - 風險回報比

3. **技術分析**
   - 使用的技術指標
   - 分析原因
   - 時間框架

4. **格式**
   - 美觀的HTML格式
   - 純文字備份
   - 手機友好的排版

## 🧪 測試功能

### 測試Gmail連接

```bash
python setup_gmail_notification.py
# 選擇選項 2: 測試Gmail通知功能
```

### 測試信號通知

系統會自動發送測試信號，包含：
- 模擬的BTCUSDT STRONG_BUY信號
- 85%信心度
- 完整的價格和分析資訊

## 🎯 實際使用

### 信號觸發條件

系統會在以下情況自動發送Gmail通知：

1. **WebSocket接收到價格更新**
2. **pandas-ta分析檢測到交易信號**
3. **信號信心度 ≥ 70%**
4. **該交易對冷卻時間已過**
5. **信號緊急程度為 high 或 critical**

### 監控的交易對

預設監控：
- BTCUSDT (比特幣)
- ETHUSDT (以太坊)  
- BNBUSDT (幣安幣)
- ADAUSDT (艾達幣)
- XRPUSDT (瑞波幣)
- SOLUSDT (Solana)

### 時間框架

- 1分鐘 (1m) - 極短線
- 5分鐘 (5m) - 短線
- 15分鐘 (15m) - 中短線
- 1小時 (1h) - 中線

## 📊 監控和統計

### 檢查通知狀態

在後端日誌中查看：
```
📧 Gmail通知已設置: your_email@gmail.com → your_email@gmail.com
✅ Gmail通知測試成功
📧 準備發送Gmail通知: BTCUSDT STRONG_BUY
✅ Gmail通知發送成功: BTCUSDT STRONG_BUY
```

### 通知統計

系統會記錄：
- 總通知數量
- 按信號類型分類統計
- 最近發送的通知
- 發送成功/失敗率

## ⚠️ 注意事項

### 安全性

1. **保護應用程式密碼**: 不要在代碼中硬編碼
2. **使用環境變數**: 或 .env 文件存儲敏感信息
3. **定期更換密碼**: 建議定期更新應用程式密碼

### 郵件限制

1. **Gmail發送限制**: 每日500封（個人帳戶）
2. **避免垃圾郵件**: 系統有冷卻機制
3. **網路連接**: 需要穩定的網路連接

### 故障排除

常見問題：

1. **"Authentication failed"**
   - 檢查Gmail帳號和應用程式密碼
   - 確認已啟用兩步驟驗證

2. **"Connection timed out"**
   - 檢查網路連接
   - 確認防火牆設定

3. **沒有收到郵件**
   - 檢查垃圾郵件資料夾
   - 確認信號信心度是否達到閾值

## 🚀 進階配置

### 自定義設定

可以透過代碼調整：

```python
# 修改信心度閾值
gmail_service.update_settings(min_confidence=0.8)

# 修改冷卻時間
gmail_service.update_settings(cooldown_minutes=30)

# 啟用/禁用通知
gmail_service.enable_notifications()
gmail_service.disable_notifications()
```

### 與智能共振濾波器整合

系統已整合：
- `intelligent_consensus_config.json` 配置
- 多指標共振確認
- 市場狀態適應性調整

## 📞 支持

如有問題，請檢查：
1. 後端日誌輸出
2. Gmail設定是否正確
3. 網路連接狀態
4. 系統錯誤訊息

系統會詳細記錄所有Gmail相關的操作和錯誤，方便排查問題。
