# 🎯 狙擊手計劃 Gmail 配置完整指南

## 📧 Gmail 配置步驟

### 步驟 1: 啟用 Gmail 兩步驟驗證

1. 前往 [Google 帳戶設定](https://myaccount.google.com/)
2. 點擊左側的「安全性」
3. 在「登入 Google」區塊中，點擊「兩步驟驗證」
4. 按照指示完成兩步驟驗證設定

### 步驟 2: 生成應用程式密碼

1. 在「安全性」頁面中，找到「應用程式密碼」
2. 點擊「應用程式密碼」
3. 選擇「其他 (自訂名稱)」
4. 輸入「Trading X 狙擊手計劃」
5. 點擊「產生」
6. **複製生成的 16 字符密碼** (例如: `abcd efgh ijkl mnop`)

### 步驟 3: 配置 .env 文件

編輯 `/Users/itts/Desktop/Trading X/.env` 文件：

```env
GMAIL_USER=your-email@gmail.com
GMAIL_PASSWORD=abcd efgh ijkl mnop
GMAIL_RECIPIENT=recipient@gmail.com
GMAIL_SMTP_SERVER=smtp.gmail.com
GMAIL_SMTP_PORT=587
SNIPER_EMAIL_ENABLED=true
SNIPER_MIN_CONFIDENCE=0.8
SNIPER_NOTIFICATION_COOLDOWN=300
```

**重要提醒**:

- `GMAIL_USER`: 您的 Gmail 地址
- `GMAIL_PASSWORD`: 剛才生成的 16 字符應用程式密碼 (不是您的 Gmail 密碼!)
- `GMAIL_RECIPIENT`: 接收狙擊手信號通知的郵箱

### 步驟 4: 測試 Gmail 配置

```bash
cd "/Users/itts/Desktop/Trading X"
python3 test_gmail_sniper.py
```

## 📨 Email 通知內容

狙擊手計劃會發送以下內容的 Email：

```
主題: 🎯 狙擊手計劃信號 - BTCUSDT BUY

內容:
🎯 狙擊手計劃 - 高精準度交易信號

📊 交易標的: BTCUSDT
📈 信號類型: BUY
💰 進場價格: $67,890.1234
🛑 止損價格: $65,000.0000
🎯 止盈價格: $72,000.0000
⭐ 信心度: 95%
⏰ 時間框架: 1h

🎯 狙擊手分析:
[詳細的技術分析內容]

🔍 技術指標:
🎯 狙擊手雙層架構, ⚡ 動態過濾引擎, 📊 市場狀態: BULLISH

⚡ 狙擊手指標:
• 市場狀態: BULLISH
• Layer 1 時間: 12.0ms
• Layer 2 時間: 23.0ms
• 信號通過率: 94.3%

📅 生成時間: 2024-12-19 14:30:00
```

## 🔧 故障排除

### 常見問題

1. **"Authentication failed"**

   - 確認使用的是應用程式密碼，不是 Gmail 密碼
   - 檢查兩步驟驗證是否已啟用

2. **"SMTP connection failed"**

   - 檢查網路連接
   - 確認 SMTP 設定正確 (smtp.gmail.com:587)

3. **"Permission denied"**
   - 確認 Gmail 帳戶允許「較不安全的應用程式」存取
   - 或使用應用程式密碼

### 測試步驟

```bash
# 1. 檢查配置
cat /Users/itts/Desktop/Trading\ X/.env

# 2. 測試後端服務
curl http://localhost:8000/api/v1/notifications/email/status

# 3. 運行完整測試
python3 test_gmail_sniper.py

# 4. 檢查系統整合
python3 test_sniper_plan_complete.py
```

## 🎯 生產環境使用

配置完成後，狙擊手界面中的「📧 發送通知」按鈕將自動發送 Email：

1. 訪問: http://localhost:3002/sniper-strategy
2. 等待狙擊手信號生成
3. 點擊信號卡片中的「📧 發送通知」按鈕
4. 系統會自動發送詳細的交易信號到指定郵箱

## 📊 通知頻率控制

- `SNIPER_MIN_CONFIDENCE`: 最低信心度閾值 (預設 0.8)
- `SNIPER_NOTIFICATION_COOLDOWN`: 通知間隔時間 (預設 300 秒)
- 只有高信心度的狙擊手信號才會觸發自動通知

配置完成後，您的狙擊手計劃將具備完整的 Email 自動通知功能！
