#!/usr/bin/env python3
"""
簡化的Email狀態檢查 - Trading X
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def check_email_status():
    """檢查Email狀態"""
    try:
        from app.core.database import get_db
        from app.models.sniper_signal_history import SniperSignalDetails, EmailStatus
        from sqlalchemy import select, func, and_
        
        print("🔍 檢查Email狀態...")
        
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            # 查詢總信號數
            total_result = await db.execute(
                select(func.count(SniperSignalDetails.id))
            )
            total_signals = total_result.scalar() or 0
            print(f"📧 總信號數: {total_signals}")
            
            # 查詢超過重試限制的信號
            excessive_result = await db.execute(
                select(
                    SniperSignalDetails.symbol,
                    SniperSignalDetails.signal_id,
                    SniperSignalDetails.email_retry_count,
                    SniperSignalDetails.email_status,
                    SniperSignalDetails.error_message
                ).where(
                    SniperSignalDetails.email_retry_count >= 5
                ).limit(10)
            )
            
            excessive_signals = excessive_result.fetchall()
            
            if excessive_signals:
                print(f"\n⚠️  發現 {len(excessive_signals)} 個超過重試限制的信號:")
                for signal in excessive_signals:
                    print(f"   📧 {signal[0]} {signal[1]}: 重試 {signal[2]} 次, 狀態: {signal[3]}")
                    if signal[4]:
                        print(f"      錯誤: {signal[4][:100]}...")
            else:
                print("✅ 沒有發現超過重試限制的信號")
                
        finally:
            await db_gen.aclose()
            
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_email_status())
