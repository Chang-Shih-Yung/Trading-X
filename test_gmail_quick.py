#!/usr/bin/env python3
"""
快速測試Gmail通知功能
"""

import asyncio
import sys
import os
sys.path.append('/Users/henrychang/Desktop/Trading-X')

from app.services.gmail_notification import GmailNotificationService
from app.services.realtime_signal_engine import TradingSignalAlert
from datetime import datetime

async def quick_test():
    """快速測試Gmail通知"""
    print("🧪 快速Gmail通知測試")
    print("=" * 30)
    
    try:
        # 從.env文件讀取配置
        with open('/Users/henrychang/Desktop/Trading-X/.env', 'r') as f:
            env_content = f.read()
        
        # 解析環境變數
        gmail_sender = None
        gmail_password = None
        gmail_recipient = None
        
        for line in env_content.split('\n'):
            if line.startswith('GMAIL_SENDER='):
                gmail_sender = line.split('=', 1)[1]
            elif line.startswith('GMAIL_APP_PASSWORD='):
                gmail_password = line.split('=', 1)[1]
            elif line.startswith('GMAIL_RECIPIENT='):
                gmail_recipient = line.split('=', 1)[1]
        
        if not gmail_sender or not gmail_password:
            print("❌ Gmail配置未找到")
            return
        
        print(f"📧 使用配置: {gmail_sender} → {gmail_recipient or gmail_sender}")
        
        # 創建Gmail服務
        gmail_service = GmailNotificationService(
            sender_email=gmail_sender,
            sender_password=gmail_password,
            recipient_email=gmail_recipient or gmail_sender
        )
        
        # 測試基本連接
        print("🔍 測試Gmail連接...")
        test_result = await gmail_service.test_notification()
        
        if test_result:
            print("✅ Gmail基本連接測試成功！")
        else:
            print("❌ Gmail基本連接測試失敗")
            return
        
        # 測試交易信號通知
        print("\n🎯 測試交易信號通知...")
        
        # 創建測試信號 - 使用60%信心度來測試新設定
        test_signal = TradingSignalAlert(
            symbol="BTCUSDT",
            signal_type="BUY", 
            confidence=0.65,  # 65%信心度，高於新閾值60%
            entry_price=118500.0,
            stop_loss=115000.0,
            take_profit=125000.0,
            risk_reward_ratio=1.86,
            indicators_used=["RSI", "MACD", "BollingerBands", "智能共振濾波器"],
            reasoning="🎯 技術指標確認: RSI回升(32→42) + MACD趨勢轉強 + 布林帶中軌支撐 + 智能共振濾波器確認",
            timeframe="15m",
            timestamp=datetime.now(),
            urgency="medium"
        )
        
        # 發送測試信號
        signal_result = await gmail_service.send_signal_notification(test_signal)
        
        if signal_result:
            print("✅ 交易信號通知測試成功！")
            print("📧 請檢查您的郵箱 henry1010921@gmail.com")
            print("📱 如果沒看到郵件，請檢查垃圾郵件資料夾")
        else:
            print("❌ 交易信號通知測試失敗")
            return
        
        # 顯示統計信息
        stats = gmail_service.get_notification_stats()
        print(f"\n📊 通知統計:")
        print(f"   總通知數: {stats.get('total_notifications', 0)}")
        print(f"   通知狀態: {'✅ 啟用' if stats.get('enabled', False) else '❌ 禁用'}")
        print(f"   最低信心度: {stats.get('min_confidence_threshold', 0):.0%}")
        print(f"   冷卻時間: {stats.get('cooldown_minutes', 0)}分鐘")
        
        print(f"\n🎉 Gmail通知功能測試完成！")
        print(f"💡 當系統檢測到信心度≥60%的交易信號時，會自動發送通知")
        print(f"⏰ 同一交易對5分鐘內只發送一次，避免垃圾郵件")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(quick_test())
