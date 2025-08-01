#!/usr/bin/env python3

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

def test_gmail_direct():
    """直接測試 Gmail SMTP 連接"""
    
    # 從環境變數讀取配置
    sender_email = "henry1010921@gmail.com"
    sender_password = "jedo jvvv hbqh ujrd"  # 應用程式密碼
    recipient_email = "henry1010921@gmail.com"
    
    print(f"📧 測試 Gmail 發送...")
    print(f"發送者: {sender_email}")
    print(f"接收者: {recipient_email}")
    print(f"密碼長度: {len(sender_password)} 字符")
    
    try:
        # 創建郵件內容
        message = MIMEMultipart("alternative")
        message["Subject"] = "🎯 Trading-X Gmail 直接測試"
        message["From"] = sender_email
        message["To"] = recipient_email
        
        # 郵件內容
        text = f"""
🎯 Trading-X Gmail 直接測試

這是一封測試郵件，用於驗證 Gmail 通知功能。

測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
發送者: {sender_email}
接收者: {recipient_email}

如果您收到這封郵件，表示 Gmail 通知功能正常工作！

---
Trading-X 進階交易策略系統
        """
        
        part = MIMEText(text, "plain")
        message.attach(part)
        
        # 建立 SMTP 連接
        print("🔌 連接 Gmail SMTP 服務器...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            print("🔐 啟動 TLS 加密...")
            server.starttls(context=context)
            
            print("🔑 登入 Gmail 帳戶...")
            server.login(sender_email, sender_password)
            
            print("📤 發送郵件...")
            server.sendmail(sender_email, recipient_email, message.as_string())
            
        print("✅ 郵件發送成功！")
        print(f"📧 請檢查 {recipient_email} 的收件箱")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Gmail 認證失敗: {e}")
        print("💡 請檢查:")
        print("   • Gmail 應用程式密碼是否正確")
        print("   • 是否啟用了兩步驟驗證")
        return False
        
    except Exception as e:
        print(f"❌ 發送失敗: {e}")
        print(f"錯誤類型: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_gmail_direct()
    exit(0 if success else 1)
