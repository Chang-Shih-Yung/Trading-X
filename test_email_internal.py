#!/usr/bin/env python3
"""
直接測試 Email 系統內部狀態
"""

import asyncio
import sys
import os

# 添加項目根目錄到 Python path
sys.path.append('/Users/itts/Desktop/Trading X')

async def test_email_manager_internal():
    """直接測試 Email 管理器內部狀態"""
    try:
        from app.services.sniper_email_manager import SniperEmailManager
        from datetime import datetime
        
        print("🔧 直接測試 Email 管理器內部狀態")
        print("=" * 50)
        
        # 創建 Email 管理器實例
        manager = SniperEmailManager()
        
        print(f"1️⃣ Gmail 服務狀態: {'✅ 已配置' if manager.gmail_service else '❌ 未配置'}")
        print(f"2️⃣ 掃描任務狀態: {'🔄 運行中' if manager.scanning_task and not manager.scanning_task.done() else '⏹️ 已停止'}")
        print(f"3️⃣ 今日已發送記錄數: {len(manager._sent_signals_today)}")
        print(f"4️⃣ 運行狀態: {'🟢 運行中' if manager.is_running else '🔴 已停止'}")
        
        # 測試清理功能
        print("\n🧹 測試清理功能:")
        
        # 添加一些測試記錄
        today = datetime.now().strftime('%Y%m%d')
        yesterday = '20241204'  # 假設的昨日日期
        
        manager._sent_signals_today.add(f'BTCUSDT_{yesterday}')
        manager._sent_signals_today.add(f'ETHUSDT_{yesterday}')
        manager._sent_signals_today.add(f'ADAUSDT_{today}')
        manager._sent_signals_today.add(f'DOTUSDT_{today}')
        
        print(f"   清理前記錄數: {len(manager._sent_signals_today)}")
        manager._cleanup_sent_signals_record()
        print(f"   清理後記錄數: {len(manager._sent_signals_today)}")
        print(f"   保留的記錄: {list(manager._sent_signals_today)}")
        
        # 如果掃描任務正在運行，顯示一些統計
        if manager.scanning_task and not manager.scanning_task.done():
            print("\n📊 掃描任務狀態: 正在運行")
            print("   - 30秒掃描間隔")
            print("   - 每個代幣每天只發送最佳信號")
            print("   - 自動清理過期記錄")
        else:
            print("\n⚠️  掃描任務未運行")
            print("   建議重啟服務以啟動Email自動掃描")
        
        print("\n✅ 內部測試完成")
        
    except Exception as e:
        print(f"❌ 測試過程中出現錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_email_manager_internal())
