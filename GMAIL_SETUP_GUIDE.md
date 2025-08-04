# Gmail 通知設置指南

## 🔧 環境變數配置

在 `.env` 文件中設置以下三個環境變數：

```env
# Gmail 通知配置
GMAIL_USER=your-gmail@gmail.com           # 你的Gmail帳戶
GMAIL_PASSWORD=your-app-password          # 16字符應用程式密碼
GMAIL_RECIPIENT=recipient@gmail.com       # 接收通知的郵箱（可以是同一個）
```

## 📋 設置步驟

### 1. 啟用兩步驟驗證
1. 登入 [Google 帳戶](https://myaccount.google.com/)
2. 點擊「安全性」
3. 找到「登入 Google」區塊
4. 啟用「兩步驟驗證」

### 2. 生成應用程式密碼
1. 在「安全性」頁面中
2. 點擊「應用程式密碼」
3. 選擇「其他 (自訂名稱)」
4. 輸入「Trading-X」或其他名稱
5. 點擊「產生」
6. **重要**: 複製16字符的應用程式密碼（格式類似：abcd efgh ijkl mnop）

### 3. 更新 .env 配置
```env
GMAIL_USER=henry1010921@gmail.com
GMAIL_PASSWORD=abcd efgh ijkl mnop
GMAIL_RECIPIENT=henry1010921@gmail.com
```

**⚠️ 注意**：
- 使用應用程式密碼，不是帳戶密碼
- 應用程式密碼包含空格是正常的
- 可以發送給自己或其他郵箱

## 🧪 測试Gmail功能

運行測試腳本：
```bash
python test_gmail_simple.py
```

如果看到以下訊息表示成功：
```
✅ Gmail 測試郵件已成功發送！
📬 請檢查 your-email@gmail.com 的收件箱
```

## 🚨 常見問題

### 認證失敗
```
❌ Gmail 認證失敗: (535, '5.7.8 Username and Password not accepted')
```

**解決方法**：
1. 確認已啟用兩步驟驗證
2. 使用應用程式密碼，不是帳戶密碼
3. 檢查應用程式密碼是否正確複製（包含空格）

### SMTP 連接失敗
```
❌ SMTP 錯誤: [Errno 61] Connection refused
```

**解決方法**：
1. 檢查網絡連接
2. 確認防火牆設置
3. 嘗試使用其他網絡

## 📧 狙擊手通知設置

當 Gmail 配置成功後，狙擊手策略會在以下情況發送通知：

- 🎯 高品質信號生成時
- 📊 信號執行結果更新時
- ⚠️ 系統異常或錯誤時

通知設置在 `.env` 中：
```env
SNIPER_EMAIL_ENABLED=true          # 啟用郵件通知
SNIPER_MIN_CONFIDENCE=0.8          # 最低信心度閾值
SNIPER_NOTIFICATION_COOLDOWN=300   # 通知冷卻時間（秒）
```

## ✅ 完整配置示例

```env
# Gmail 通知配置
GMAIL_USER=your-email@gmail.com
GMAIL_PASSWORD=abcd efgh ijkl mnop
GMAIL_RECIPIENT=your-email@gmail.com

# 狙擊手計劃通知設定
SNIPER_EMAIL_ENABLED=true
SNIPER_MIN_CONFIDENCE=0.8
SNIPER_NOTIFICATION_COOLDOWN=300
```

配置完成後，狙擊手策略將自動發送郵件通知到指定郵箱！🚀
