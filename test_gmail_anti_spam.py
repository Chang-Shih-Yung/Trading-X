#!/usr/bin/env python3
"""
測試Gmail通知防重複機制
"""

import asyncio
import os
import sys
from datetime import datetime

# 添加app目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.gmail_notification import GmailNotificationService
from app.services.realtime_signal_engine import TradingSignalAlert

async def test_anti_spam():
    """測試防重複機制"""
    print("🧪 開始測試Gmail通知防重複機制...")
    
    # 初始化Gmail服務
    gmail_service = GmailNotificationService(
        sender_email=os.getenv('GMAIL_SENDER', 'henry1010921@gmail.com'),
        sender_password=os.getenv('GMAIL_APP_PASSWORD', ''),
        recipient_email=os.getenv('GMAIL_RECIPIENT', 'henry1010921@gmail.com')
    )
    
    # 創建測試信號
    test_signal = TradingSignalAlert(
        symbol="BTCUSDT",
        signal_type="BUY",
        confidence=0.85,
        entry_price=50000.0,
        stop_loss=48000.0,
        take_profit=55000.0,
        risk_reward_ratio=2.5,
        indicators_used=["RSI", "MACD", "SMA"],
        reasoning="RSI超賣反彈，MACD金叉，價格突破阻力位",
        timeframe="1h",
        timestamp=datetime.now(),
        urgency="high"
    )
    
    print(f"📊 測試信號: {test_signal.symbol} {test_signal.signal_type} (信心度: {test_signal.confidence:.3f})")
    
    # 測試1: 第一次發送（應該成功）
    print("\n🔸 測試1: 第一次發送...")
    result1 = await gmail_service.send_signal_notification(test_signal)
    print(f"結果: {'✅ 成功' if result1 else '❌ 失敗'}")
    
    # 測試2: 立即重複發送（應該被阻止）
    print("\n🔸 測試2: 立即重複發送...")
    result2 = await gmail_service.send_signal_notification(test_signal)
    print(f"結果: {'❌ 被阻止（正確）' if not result2 else '⚠️ 未被阻止（錯誤）'}")
    
    # 測試3: 修改信心度後發送（應該被阻止，因為其他信息相同）
    print("\n🔸 測試3: 修改信心度後發送...")
    test_signal.confidence = 0.87
    result3 = await gmail_service.send_signal_notification(test_signal)
    print(f"結果: {'❌ 被阻止（正確）' if not result3 else '⚠️ 未被阻止（錯誤）'}")
    
    # 測試4: 不同交易對（應該成功）
    print("\n🔸 測試4: 不同交易對...")
    test_signal.symbol = "ETHUSDT"
    result4 = await gmail_service.send_signal_notification(test_signal)
    print(f"結果: {'✅ 成功' if result4 else '❌ 失敗'}")
    
    # 顯示統計信息
    print("\n📈 通知統計:")
    stats = gmail_service.get_notification_stats()
    print(f"- 總通知數: {stats.get('total_notifications', 0)}")
    print(f"- 信號類型: {stats.get('signal_types', {})}")
    print(f"- 消息簽名緩存大小: {len(gmail_service.message_signatures)}")
    
    print("\n🎯 測試完成！")
    print("預期結果: 測試1和4成功，測試2和3被阻止")

if __name__ == "__main__":
    # 載入環境變數
    from dotenv import load_dotenv
    load_dotenv()
    
    # 檢查Gmail配置
    if not os.getenv('GMAIL_APP_PASSWORD'):
        print("❌ 請先配置Gmail App Password")
        print("運行: python setup_gmail_notification.py")
        exit(1)
    
    # 運行測試
    asyncio.run(test_anti_spam())
