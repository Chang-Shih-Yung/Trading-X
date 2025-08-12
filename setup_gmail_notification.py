#!/usr/bin/env python3
"""
Gmail 通知配置和測試工具
用於設置和測試交易信號的Gmail通知功能
"""

import asyncio
import os
import sys
import getpass
sys.path.append('/Users/henrychang/Desktop/Trading-X')

from app.services.gmail_notification import GmailNotificationService
from X.app.services.realtime_signal_engine import RealtimeSignalEngine, TradingSignalAlert
from datetime import datetime

def setup_environment_variables():
    """設置環境變數"""
    print("🔧 Gmail通知配置設置")
    print("=" * 50)
    
    # 獲取Gmail配置
    sender_email = input("請輸入您的Gmail帳號: ").strip()
    if not sender_email:
        print("❌ Gmail帳號不能為空")
        return False
    
    print("\n📱 Gmail應用程式密碼設置說明:")
    print("1. 登入 Google 帳戶")
    print("2. 前往 https://myaccount.google.com/security")
    print("3. 啟用兩步驟驗證")
    print("4. 選擇「應用程式密碼」")
    print("5. 生成新的應用程式密碼")
    print()
    
    app_password = getpass.getpass("請輸入Gmail應用程式密碼 (隱藏輸入): ").strip()
    if not app_password:
        print("❌ 應用程式密碼不能為空")
        return False
    
    recipient_email = input(f"接收通知的郵箱 (預設: {sender_email}): ").strip()
    if not recipient_email:
        recipient_email = sender_email
    
    # 設置環境變數
    os.environ['GMAIL_SENDER'] = sender_email
    os.environ['GMAIL_APP_PASSWORD'] = app_password
    os.environ['GMAIL_RECIPIENT'] = recipient_email
    
    print(f"\n✅ 環境變數設置完成:")
    print(f"   發送者: {sender_email}")
    print(f"   接收者: {recipient_email}")
    
    # 創建 .env 文件（可選）
    create_env = input("\n是否創建 .env 文件保存設置? (y/N): ").strip().lower()
    if create_env == 'y':
        try:
            with open('/Users/henrychang/Desktop/Trading-X/.env', 'w') as f:
                f.write(f"GMAIL_SENDER={sender_email}\n")
                f.write(f"GMAIL_APP_PASSWORD={app_password}\n")
                f.write(f"GMAIL_RECIPIENT={recipient_email}\n")
            print("✅ .env 文件已創建")
        except Exception as e:
            print(f"⚠️ 創建 .env 文件失敗: {e}")
    
    return True

async def test_gmail_notification():
    """測試Gmail通知功能"""
    print("\n🧪 測試Gmail通知功能")
    print("=" * 30)
    
    try:
        # 檢查環境變數
        sender_email = os.getenv('GMAIL_SENDER')
        app_password = os.getenv('GMAIL_APP_PASSWORD')
        recipient_email = os.getenv('GMAIL_RECIPIENT', sender_email)
        
        if not sender_email or not app_password:
            print("❌ 環境變數未設置，請先運行配置")
            return False
        
        # 創建Gmail服務
        gmail_service = GmailNotificationService(
            sender_email=sender_email,
            sender_password=app_password,
            recipient_email=recipient_email
        )
        
        print("📧 Gmail服務初始化完成")
        
        # 測試基本連接
        print("🔍 測試Gmail連接...")
        test_result = await gmail_service.test_notification()
        
        if test_result:
            print("✅ Gmail連接測試成功！")
        else:
            print("❌ Gmail連接測試失敗")
            return False
        
        # 測試交易信號通知
        print("\n🎯 測試交易信號通知...")
        
        # 創建測試信號
        test_signal = TradingSignalAlert(
            symbol="BTCUSDT",
            signal_type="STRONG_BUY",
            confidence=0.85,
            entry_price=118500.0,
            stop_loss=115000.0,
            take_profit=125000.0,
            risk_reward_ratio=1.86,
            indicators_used=["RSI", "MACD", "BollingerBands"],
            reasoning="RSI超賣反彈 + MACD金叉 + 突破布林帶上軌",
            timeframe="15m",
            timestamp=datetime.now(),
            urgency="high"
        )
        
        # 發送測試信號
        signal_result = await gmail_service.send_signal_notification(test_signal)
        
        if signal_result:
            print("✅ 交易信號通知測試成功！")
            print("📧 請檢查您的郵箱是否收到測試信號")
        else:
            print("❌ 交易信號通知測試失敗")
            return False
        
        # 顯示統計信息
        stats = gmail_service.get_notification_stats()
        print(f"\n📊 通知統計:")
        print(f"   總通知數: {stats.get('total_notifications', 0)}")
        print(f"   通知狀態: {'啟用' if stats.get('enabled', False) else '禁用'}")
        print(f"   最低信心度: {stats.get('min_confidence_threshold', 0)}")
        print(f"   冷卻時間: {stats.get('cooldown_minutes', 0)}分鐘")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試Gmail通知時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_integration_with_signal_engine():
    """測試與信號引擎的整合"""
    print("\n🔗 測試與實時信號引擎的整合")
    print("=" * 40)
    
    try:
        # 檢查環境變數
        sender_email = os.getenv('GMAIL_SENDER')
        app_password = os.getenv('GMAIL_APP_PASSWORD')
        recipient_email = os.getenv('GMAIL_RECIPIENT', sender_email)
        
        if not sender_email or not app_password:
            print("❌ 環境變數未設置")
            return False
        
        # 創建信號引擎
        signal_engine = RealtimeSignalEngine()
        
        # 設置Gmail通知
        signal_engine.setup_gmail_notification(
            sender_email=sender_email,
            sender_password=app_password,
            recipient_email=recipient_email
        )
        
        print("✅ 信號引擎Gmail通知設置完成")
        
        # 測試通知
        test_result = await signal_engine.test_gmail_notification()
        
        if test_result:
            print("✅ 信號引擎Gmail通知測試成功！")
            print("🎉 系統已準備好發送實時交易信號通知")
        else:
            print("❌ 信號引擎Gmail通知測試失敗")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 測試整合時發生錯誤: {e}")
        return False

async def main():
    """主函數"""
    print("📧 Trading-X Gmail通知配置工具")
    print("=" * 50)
    
    while True:
        print("\n請選擇操作:")
        print("1. 設置Gmail環境變數")
        print("2. 測試Gmail通知功能")
        print("3. 測試與信號引擎整合")
        print("4. 顯示當前配置")
        print("5. 退出")
        
        choice = input("\n請輸入選項 (1-5): ").strip()
        
        if choice == '1':
            setup_environment_variables()
            
        elif choice == '2':
            await test_gmail_notification()
            
        elif choice == '3':
            await test_integration_with_signal_engine()
            
        elif choice == '4':
            print(f"\n📋 當前配置:")
            print(f"   GMAIL_SENDER: {os.getenv('GMAIL_SENDER', '未設置')}")
            print(f"   GMAIL_APP_PASSWORD: {'已設置' if os.getenv('GMAIL_APP_PASSWORD') else '未設置'}")
            print(f"   GMAIL_RECIPIENT: {os.getenv('GMAIL_RECIPIENT', '未設置')}")
            
        elif choice == '5':
            print("👋 感謝使用 Trading-X Gmail通知配置工具")
            break
            
        else:
            print("❌ 無效選項，請重新選擇")

if __name__ == "__main__":
    asyncio.run(main())
