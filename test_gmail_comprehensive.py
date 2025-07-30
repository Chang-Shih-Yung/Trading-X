#!/usr/bin/env python3
"""
Gmail通知系統綜合測試
測試消息簽名系統、智能冷卻機制、重試保護和內存管理
"""

import asyncio
import os
import sys
from datetime import datetime
import time

# 添加app目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.gmail_notification import GmailNotificationService
from app.services.realtime_signal_engine import TradingSignalAlert

class GmailNotificationTester:
    def __init__(self):
        self.gmail_service = None
        self.test_results = []
        
    async def setup_service(self):
        """設置Gmail服務"""
        print("🔧 設置Gmail通知服務...")
        
        gmail_sender = os.getenv('GMAIL_SENDER')
        gmail_password = os.getenv('GMAIL_APP_PASSWORD') 
        gmail_recipient = os.getenv('GMAIL_RECIPIENT')
        
        if not gmail_sender or not gmail_password:
            print("❌ Gmail配置不完整")
            return False
            
        self.gmail_service = GmailNotificationService(
            sender_email=gmail_sender,
            sender_password=gmail_password,
            recipient_email=gmail_recipient or gmail_sender
        )
        
        print(f"✅ Gmail服務已設置: {gmail_sender} → {gmail_recipient or gmail_sender}")
        return True
    
    def create_test_signal(self, symbol="TESTUSDT", signal_type="BUY", confidence=0.75, entry_price=100.0, variation=0):
        """創建測試信號"""
        return TradingSignalAlert(
            symbol=symbol,
            signal_type=signal_type,
            confidence=confidence + (variation * 0.01),  # 微調信心度
            entry_price=entry_price + variation,
            stop_loss=entry_price * 0.95,
            take_profit=entry_price * 1.1,
            risk_reward_ratio=2.0,
            indicators_used=["RSI", "MACD"],
            reasoning="測試信號",
            timeframe="1h",
            timestamp=datetime.now(),
            urgency="medium"
        )
    
    async def test_message_signature_system(self):
        """測試消息簽名系統"""
        print("\n🔸 測試1: 消息簽名系統")
        print("=" * 50)
        
        # 創建相同的信號
        signal1 = self.create_test_signal()
        signal2 = self.create_test_signal()  # 完全相同
        signal3 = self.create_test_signal(confidence=0.76)  # 稍微不同的信心度
        
        print("📊 發送第一個信號...")
        result1 = await self.gmail_service.send_signal_notification(signal1)
        
        print("📊 發送相同信號...")
        result2 = await self.gmail_service.send_signal_notification(signal2)
        
        print("📊 發送微調信號...")
        result3 = await self.gmail_service.send_signal_notification(signal3)
        
        # 驗證結果
        success = result1 and not result2 and not result3
        self.test_results.append({
            'test': '消息簽名系統',
            'success': success,
            'details': f"首次:{result1}, 重複:{result2}, 微調:{result3}"
        })
        
        print(f"結果: {'✅ 通過' if success else '❌ 失敗'}")
        print(f"- 首次發送: {'✅ 成功' if result1 else '❌ 失敗'}")
        print(f"- 重複發送: {'✅ 被阻止' if not result2 else '❌ 未被阻止'}")
        print(f"- 微調發送: {'✅ 被阻止' if not result3 else '❌ 未被阻止'}")
        
        return success
    
    async def test_intelligent_cooldown(self):
        """測試智能冷卻機制"""
        print("\n🔸 測試2: 智能冷卻機制")
        print("=" * 50)
        
        # 測試不同交易對
        signal_btc1 = self.create_test_signal("BTCUSDT", "BUY", 0.80, 50000.0)
        signal_btc2 = self.create_test_signal("BTCUSDT", "SELL", 0.82, 50100.0)  # 不同信號類型
        signal_eth = self.create_test_signal("ETHUSDT", "BUY", 0.80, 3000.0)
        
        print("📊 發送BTC買入信號...")
        result1 = await self.gmail_service.send_signal_notification(signal_btc1)
        
        print("📊 立即發送BTC賣出信號（相同交易對）...")
        result2 = await self.gmail_service.send_signal_notification(signal_btc2)
        
        print("📊 發送ETH買入信號（不同交易對）...")
        result3 = await self.gmail_service.send_signal_notification(signal_eth)
        
        # 驗證結果
        success = result1 and not result2 and result3
        self.test_results.append({
            'test': '智能冷卻機制',
            'success': success,
            'details': f"BTC買入:{result1}, BTC賣出:{result2}, ETH買入:{result3}"
        })
        
        print(f"結果: {'✅ 通過' if success else '❌ 失敗'}")
        print(f"- BTC買入信號: {'✅ 成功' if result1 else '❌ 失敗'}")
        print(f"- BTC賣出信號: {'✅ 被冷卻' if not result2 else '❌ 未被冷卻'}")
        print(f"- ETH買入信號: {'✅ 成功' if result3 else '❌ 失敗'}")
        
        return success
    
    async def test_retry_protection(self):
        """測試發送失敗重試保護"""
        print("\n🔸 測試3: 發送失敗重試保護")
        print("=" * 50)
        
        # 臨時破壞Gmail配置來模擬失敗
        original_password = self.gmail_service.sender_password
        self.gmail_service.sender_password = "invalid_password"
        
        signal = self.create_test_signal("RETRYTEST", "BUY", 0.85, 1000.0)
        
        print("📊 使用錯誤密碼發送信號（應該失敗）...")
        result1 = await self.gmail_service.send_signal_notification(signal)
        
        # 恢復正確密碼
        self.gmail_service.sender_password = original_password
        
        print("📊 恢復正確密碼後重新發送...")
        result2 = await self.gmail_service.send_signal_notification(signal)
        
        # 驗證結果
        success = not result1 and result2
        self.test_results.append({
            'test': '發送失敗重試保護',
            'success': success,
            'details': f"失敗發送:{result1}, 重試發送:{result2}"
        })
        
        print(f"結果: {'✅ 通過' if success else '❌ 失敗'}")
        print(f"- 失敗發送: {'✅ 正確失敗' if not result1 else '❌ 意外成功'}")
        print(f"- 重試發送: {'✅ 成功' if result2 else '❌ 失敗'}")
        
        return success
    
    async def test_memory_management(self):
        """測試內存管理"""
        print("\n🔸 測試4: 內存管理")
        print("=" * 50)
        
        # 記錄初始簽名數量
        initial_signatures = len(self.gmail_service.message_signatures)
        print(f"初始簽名數量: {initial_signatures}")
        
        # 發送多個不同信號來測試緩存管理
        successful_sends = 0
        for i in range(10):
            signal = self.create_test_signal(f"CACHE{i:02d}", "BUY", 0.70 + i*0.01, 100 + i*10)
            result = await self.gmail_service.send_signal_notification(signal)
            if result:
                successful_sends += 1
                print(f"  信號 {i+1}/10: ✅ 發送成功")
            else:
                print(f"  信號 {i+1}/10: ❌ 發送失敗")
            
            # 添加小延遲避免過快
            await asyncio.sleep(0.1)
        
        final_signatures = len(self.gmail_service.message_signatures)
        print(f"最終簽名數量: {final_signatures}")
        print(f"成功發送: {successful_sends}/10")
        
        # 檢查簽名緩存是否正常工作
        cache_working = final_signatures == (initial_signatures + successful_sends)
        
        # 測試緩存大小限制（需要大量信號才能觸發）
        max_signatures = self.gmail_service.max_signatures
        print(f"簽名緩存限制: {max_signatures}")
        
        success = cache_working and final_signatures <= max_signatures
        self.test_results.append({
            'test': '內存管理',
            'success': success,
            'details': f"初始:{initial_signatures}, 最終:{final_signatures}, 成功:{successful_sends}"
        })
        
        print(f"結果: {'✅ 通過' if success else '❌ 失敗'}")
        print(f"- 緩存追蹤: {'✅ 正確' if cache_working else '❌ 錯誤'}")
        print(f"- 大小限制: {'✅ 正常' if final_signatures <= max_signatures else '❌ 超限'}")
        
        return success
    
    async def test_confidence_threshold(self):
        """測試信心度閾值"""
        print("\n🔸 測試5: 信心度閾值")
        print("=" * 50)
        
        # 測試低信心度信號
        low_confidence = self.create_test_signal("LOWCONF", "BUY", 0.50, 1000.0)  # 50% < 60%閾值
        high_confidence = self.create_test_signal("HIGHCONF", "BUY", 0.75, 1000.0)  # 75% > 60%閾值
        
        print("📊 發送低信心度信號（50%）...")
        result1 = await self.gmail_service.send_signal_notification(low_confidence)
        
        print("📊 發送高信心度信號（75%）...")
        result2 = await self.gmail_service.send_signal_notification(high_confidence)
        
        success = not result1 and result2
        self.test_results.append({
            'test': '信心度閾值',
            'success': success,
            'details': f"低信心度:{result1}, 高信心度:{result2}"
        })
        
        print(f"結果: {'✅ 通過' if success else '❌ 失敗'}")
        print(f"- 低信心度(50%): {'✅ 被阻止' if not result1 else '❌ 未被阻止'}")
        print(f"- 高信心度(75%): {'✅ 成功' if result2 else '❌ 失敗'}")
        
        return success
    
    def print_final_stats(self):
        """打印最終統計"""
        print("\n" + "=" * 60)
        print("📊 Gmail通知系統測試報告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        
        print(f"總測試數: {total_tests}")
        print(f"通過測試: {passed_tests}")
        print(f"失敗測試: {total_tests - passed_tests}")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        print("\n詳細結果:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅ 通過" if result['success'] else "❌ 失敗"
            print(f"{i}. {result['test']}: {status}")
            print(f"   詳情: {result['details']}")
        
        # 顯示Gmail服務統計
        if self.gmail_service:
            stats = self.gmail_service.get_notification_stats()
            print(f"\n📈 Gmail服務統計:")
            print(f"- 總通知數: {stats.get('total_notifications', 0)}")
            print(f"- 信號類型分布: {stats.get('signal_types', {})}")
            print(f"- 簽名緩存大小: {len(self.gmail_service.message_signatures)}")
            print(f"- 冷卻記錄數: {len(self.gmail_service.last_notifications)}")
        
        overall_success = passed_tests == total_tests
        print(f"\n🎯 整體測試結果: {'✅ 全部通過' if overall_success else '❌ 部分失敗'}")
        
        return overall_success

async def main():
    """主測試函數"""
    print("🧪 Gmail通知系統綜合測試開始")
    print("測試項目: 消息簽名、智能冷卻、重試保護、內存管理、信心度閾值")
    print("=" * 60)
    
    tester = GmailNotificationTester()
    
    # 設置服務
    if not await tester.setup_service():
        print("❌ 無法設置Gmail服務，測試終止")
        return
    
    # 執行所有測試
    try:
        await tester.test_message_signature_system()
        await asyncio.sleep(1)  # 測試間隔
        
        await tester.test_intelligent_cooldown()
        await asyncio.sleep(1)
        
        await tester.test_retry_protection()
        await asyncio.sleep(1)
        
        await tester.test_memory_management()
        await asyncio.sleep(1)
        
        await tester.test_confidence_threshold()
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
    
    # 顯示最終報告
    tester.print_final_stats()

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
    asyncio.run(main())
