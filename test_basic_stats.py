#!/usr/bin/env python3
"""
簡化測試增強統計功能
"""

import asyncio
import sys
sys.path.append('.')

async def test_basic_stats():
    print("🧪 簡化統計測試...")
    
    try:
        # 直接測試數據庫連接和統計功能
        from app.core.database import get_db
        from sqlalchemy import select, func
        from app.models.sniper_signal_history import SniperSignalDetails, SignalStatus
        
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            # 查詢總信號數
            total_result = await db.execute(
                select(func.count(SniperSignalDetails.id))
            )
            total_signals = total_result.scalar() or 0
            
            print(f"📊 數據庫統計:")
            print(f"   總信號數: {total_signals}")
            
            if total_signals > 0:
                # 查詢狀態分佈
                status_result = await db.execute(
                    select(
                        SniperSignalDetails.status,
                        func.count(SniperSignalDetails.id).label('count'),
                        func.avg(SniperSignalDetails.pnl_percentage).label('avg_pnl')
                    ).group_by(SniperSignalDetails.status)
                )
                
                print("   狀態分佈:")
                total_pnl = 0.0
                profitable_count = 0
                
                for row in status_result.fetchall():
                    status = row.status
                    count = row.count
                    avg_pnl = row.avg_pnl or 0.0
                    
                    print(f"     {status}: {count} 個信號, 平均PnL: {avg_pnl:.2f}%")
                    
                    if avg_pnl > 0:
                        profitable_count += count
                        total_pnl += avg_pnl * count
                
                # 計算統計指標
                real_success_rate = (profitable_count / total_signals * 100) if total_signals > 0 else 0.0
                avg_total_pnl = total_pnl / total_signals if total_signals > 0 else 0.0
                
                print(f"   真實成功率: {real_success_rate:.1f}%")
                print(f"   平均總收益: {avg_total_pnl:.2f}%")
                print(f"   盈利信號數: {profitable_count}")
                
        finally:
            await db_gen.aclose()
        
        print("✅ 基礎統計測試完成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_basic_stats())
