#!/usr/bin/env python3
"""
簡單的 Gmail 測試腳本
使用 .env 中的三個配置：GMAIL_USER, GMAIL_PASSWORD, GMAIL_RECIPIENT
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv

def test_gmail():
    """測試 Gmail 發送功能"""
    
    # 載入環境變數
    load_dotenv()
    
    # 從 .env 讀取配置
    gmail_user = os.getenv('GMAIL_USER')
    gmail_password = os.getenv('GMAIL_PASSWORD')
    gmail_recipient = os.getenv('GMAIL_RECIPIENT')
    
    print("🧪 Testing Gmail Configuration")
    print("=" * 40)
    print(f"📧 GMAIL_USER: {gmail_user}")
    print(f"🔑 GMAIL_PASSWORD: {'*' * len(gmail_password) if gmail_password else 'Not Set'}")
    print(f"📬 GMAIL_RECIPIENT: {gmail_recipient}")
    print()
    
    # 檢查配置
    if not gmail_user or gmail_user == 'your-email@gmail.com':
        print("❌ 請在 .env 文件中設置正確的 GMAIL_USER")
        return False
        
    if not gmail_password or gmail_password == 'your-16-character-app-password':
        print("❌ 請在 .env 文件中設置正確的 GMAIL_PASSWORD（應用程式密碼）")
        return False
        
    if not gmail_recipient or gmail_recipient == 'recipient@gmail.com':
        print("❌ 請在 .env 文件中設置正確的 GMAIL_RECIPIENT")
        return False
    
    try:
        # 創建郵件
        message = MIMEMultipart("alternative")
        message["Subject"] = "🎯 Trading-X Gmail 測試 - " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message["From"] = gmail_user
        message["To"] = gmail_recipient
        
        # 郵件內容
        text_content = f"""
🎯 Trading-X Gmail 連接測試成功！

測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (台灣時間)
發送者: {gmail_user}
接收者: {gmail_recipient}

✅ Gmail SMTP 連接正常
✅ 應用程式密碼驗證通過
✅ 郵件發送功能可用

這表示狙擊手策略的 Email 通知功能已準備就緒！

---
Trading-X 進階交易策略系統
狙擊手雙層架構 + Phase 1ABC + Phase 2+3 完整整合
        """
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px;">
            <div style="background: white; border-radius: 10px; padding: 30px; max-width: 600px; margin: 0 auto;">
                <h1 style="color: #333; text-align: center;">🎯 Trading-X Gmail 測試</h1>
                
                <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #28a745; margin-top: 0;">✅ 連接測試成功！</h3>
                    <p><strong>測試時間:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (台灣時間)</p>
                    <p><strong>發送者:</strong> {gmail_user}</p>
                    <p><strong>接收者:</strong> {gmail_recipient}</p>
                </div>
                
                <div style="background: #e8f5e8; border-radius: 8px; padding: 15px; margin: 20px 0;">
                    <h4 style="color: #155724; margin-top: 0;">測試結果:</h4>
                    <ul style="color: #155724;">
                        <li>✅ Gmail SMTP 連接正常</li>
                        <li>✅ 應用程式密碼驗證通過</li>
                        <li>✅ 郵件發送功能可用</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p style="color: #666; font-size: 14px;">
                        Trading-X 進階交易策略系統<br>
                        狙擊手雙層架構 + Phase 1ABC + Phase 2+3 完整整合
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 添加文字和HTML內容
        text_part = MIMEText(text_content, "plain", "utf-8")
        html_part = MIMEText(html_content, "html", "utf-8")
        
        message.attach(text_part)
        message.attach(html_part)
        
        # 建立 SMTP 連接
        print("🔌 連接 Gmail SMTP 服務器...")
        
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            print("📡 啟動 TLS 加密...")
            server.starttls(context=context)
            
            print("🔐 登入 Gmail 帳戶...")
            server.login(gmail_user, gmail_password)
            
            print("📨 發送測試郵件...")
            server.sendmail(gmail_user, gmail_recipient, message.as_string())
            
            print("✅ Gmail 測試郵件已成功發送！")
            print(f"📬 請檢查 {gmail_recipient} 的收件箱")
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Gmail 認證失敗: {e}")
        print("💡 請確認：")
        print("   1. Gmail 帳戶已啟用兩步驟驗證")
        print("   2. 使用的是應用程式密碼（16字符），不是帳戶密碼")
        print("   3. 應用程式密碼格式正確（可能需要移除空格）")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP 錯誤: {e}")
        return False
        
    except Exception as e:
        print(f"❌ 發送失敗: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Trading-X Gmail 功能測試")
    print("=" * 50)
    
    success = test_gmail()
    
    if success:
        print("\n🎉 Gmail 通知功能測試通過！")
        print("狙擊手策略的 Email 通知已準備就緒。")
    else:
        print("\n❌ Gmail 測試失敗，請檢查配置。")
