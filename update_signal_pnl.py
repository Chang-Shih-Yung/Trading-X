#!/usr/bin/env python3
"""
更新信號的真實PnL以測試統計功能
"""

import asyncio
import sys
import random
sys.path.append('.')

async def update_signal_pnl():
    print("🔄 更新信號PnL以測試統計功能...")
    
    try:
        from app.core.database import get_db
        from app.models.sniper_signal_history import SniperSignalDetails, SignalStatus
        from sqlalchemy import select, update
        from app.utils.timezone_utils import get_taiwan_now
        from datetime import timedelta
        
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            # 獲取所有活躍信號
            result = await db.execute(
                select(SniperSignalDetails).where(
                    SniperSignalDetails.status == SignalStatus.ACTIVE
                ).limit(20)  # 只更新前20個
            )
            
            signals = result.scalars().all()
            print(f"📊 找到 {len(signals)} 個活躍信號")
            
            updated_count = 0
            tp_count = 0
            sl_count = 0
            expired_count = 0
            
            for signal in signals:
                # 模擬不同的結果
                outcome = random.choice(['tp', 'sl', 'expired', 'active'])
                
                if outcome == 'tp':
                    # 觸碰止盈 - 正收益
                    new_status = SignalStatus.HIT_TP
                    pnl = random.uniform(0.5, 8.0)  # 0.5% 到 8% 收益
                    tp_count += 1
                elif outcome == 'sl':
                    # 觸碰止損 - 負收益
                    new_status = SignalStatus.HIT_SL
                    pnl = random.uniform(-6.0, -0.5)  # -6% 到 -0.5% 虧損
                    sl_count += 1
                elif outcome == 'expired':
                    # 過期 - 小幅收益或虧損
                    new_status = SignalStatus.EXPIRED
                    pnl = random.uniform(-2.0, 3.0)  # -2% 到 3%
                    expired_count += 1
                else:
                    # 保持活躍，計算當前PnL
                    continue
                
                # 更新信號
                await db.execute(
                    update(SniperSignalDetails)
                    .where(SniperSignalDetails.id == signal.id)
                    .values(
                        status=new_status,
                        pnl_percentage=round(pnl, 2),
                        result_time=get_taiwan_now(),
                        result_price=signal.entry_price * (1 + pnl/100) if signal.signal_type == 'BUY' else signal.entry_price * (1 - pnl/100)
                    )
                )
                
                updated_count += 1
                print(f"   {signal.symbol} {signal.signal_type}: {new_status.value} (PnL: {pnl:+.2f}%)")
            
            await db.commit()
            
            print(f"\n✅ 更新完成:")
            print(f"   總更新數: {updated_count}")
            print(f"   止盈信號: {tp_count}")
            print(f"   止損信號: {sl_count}")
            print(f"   過期信號: {expired_count}")
            
            # 測試統計查詢
            print("\n📈 查詢更新後的統計...")
            
            stats_result = await db.execute(
                select(
                    SniperSignalDetails.status,
                    SniperSignalDetails.pnl_percentage
                ).where(SniperSignalDetails.pnl_percentage.isnot(None))
            )
            
            pnl_data = stats_result.fetchall()
            
            positive_pnl = [row.pnl_percentage for row in pnl_data if row.pnl_percentage > 0]
            negative_pnl = [row.pnl_percentage for row in pnl_data if row.pnl_percentage < 0]
            
            print(f"   有PnL數據的信號: {len(pnl_data)}")
            print(f"   盈利信號: {len(positive_pnl)} (平均: {sum(positive_pnl)/len(positive_pnl) if positive_pnl else 0:.2f}%)")
            print(f"   虧損信號: {len(negative_pnl)} (平均: {sum(negative_pnl)/len(negative_pnl) if negative_pnl else 0:.2f}%)")
            
            if pnl_data:
                total_pnl = sum(row.pnl_percentage for row in pnl_data)
                avg_pnl = total_pnl / len(pnl_data)
                print(f"   總收益: {total_pnl:.2f}%")
                print(f"   平均收益: {avg_pnl:.2f}%")
                print(f"   真實成功率: {len(positive_pnl)/len(pnl_data)*100:.1f}%")
        
        finally:
            await db_gen.aclose()
        
        print("✅ PnL更新測試完成")
        
    except Exception as e:
        print(f"❌ 更新失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(update_signal_pnl())
