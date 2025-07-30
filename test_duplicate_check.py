#!/usr/bin/env python3
"""
測試Gmail防重複發送的簡單驗證
"""

import asyncio
import os
import sys
from datetime import datetime

# 添加app目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.gmail_notification import GmailNotificationService
from app.services.realtime_signal_engine import TradingSignalAlert

async def simple_duplicate_test():
    """簡單的重複發送測試"""
    print("🔍 檢查Gmail重複發送問題...")
    
    # 從.env載入配置
    gmail_sender = os.getenv('GMAIL_SENDER')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD') 
    gmail_recipient = os.getenv('GMAIL_RECIPIENT')
    
    if not gmail_sender or not gmail_password:
        print("❌ Gmail配置不完整")
        return
    
    # 創建Gmail服務
    gmail_service = GmailNotificationService(
        sender_email=gmail_sender,
        sender_password=gmail_password,
        recipient_email=gmail_recipient or gmail_sender
    )
    
    # 創建完全相同的測試信號
    signal = TradingSignalAlert(
        symbol="TESTUSDT",
        signal_type="BUY",
        confidence=0.75,
        entry_price=100.0,
        stop_loss=95.0,
        take_profit=110.0,
        risk_reward_ratio=2.0,
        indicators_used=["RSI"],
        reasoning="測試重複發送",
        timeframe="1h",
        timestamp=datetime.now(),
        urgency="medium"
    )
    
    print("📊 發送第一次通知...")
    result1 = await gmail_service.send_signal_notification(signal)
    print(f"   結果1: {'✅ 發送成功' if result1 else '❌ 發送失敗'}")
    
    print("📊 立即發送相同信號...")
    result2 = await gmail_service.send_signal_notification(signal)
    print(f"   結果2: {'❌ 被阻止（正確）' if not result2 else '⚠️ 重複發送（問題）'}")
    
    print("📊 稍微修改信號再發送...")
    signal.confidence = 0.76  # 稍微改變信心度
    result3 = await gmail_service.send_signal_notification(signal)
    print(f"   結果3: {'❌ 被阻止（正確）' if not result3 else '⚠️ 重複發送（問題）'}")
    
    # 統計信息
    stats = gmail_service.get_notification_stats()
    print(f"\n📈 發送統計: {stats.get('total_notifications', 0)} 筆")
    print(f"🔒 簽名緩存: {len(gmail_service.message_signatures)} 個")
    
    if stats.get('total_notifications', 0) == 1:
        print("✅ 防重複機制正常工作！")
    else:
        print("⚠️ 可能有重複發送問題")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(simple_duplicate_test())
