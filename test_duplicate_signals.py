#!/usr/bin/env python3
"""
測試同幣種多個相同最佳信號的處理邏輯
"""

import asyncio
import sys
sys.path.append('/Users/itts/Desktop/Trading X')

from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, desc
from app.core.database import get_db
from app.models.sniper_signal_history import SniperSignalDetails, EmailStatus

async def test_duplicate_best_signals():
    """測試同幣種多個相同最佳信號的查詢邏輯"""
    print("🧪 測試同幣種多個相同最佳信號處理邏輯")
    print("=" * 60)
    
    try:
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            # 1. 查看現有信號分佈
            print("1️⃣ 檢查現有信號分佈...")
            result = await db.execute(
                select(
                    SniperSignalDetails.symbol,
                    SniperSignalDetails.signal_strength,
                    func.count(SniperSignalDetails.id).label('count'),
                    func.max(SniperSignalDetails.created_at).label('latest_time')
                )
                .where(
                    and_(
                        SniperSignalDetails.email_status.in_([EmailStatus.PENDING, EmailStatus.FAILED]),
                        SniperSignalDetails.email_sent_at.is_(None),
                        SniperSignalDetails.created_at >= datetime.now() - timedelta(hours=24)
                    )
                )
                .group_by(SniperSignalDetails.symbol, SniperSignalDetails.signal_strength)
                .order_by(desc(SniperSignalDetails.signal_strength))
            )
            
            signals_distribution = result.all()
            if signals_distribution:
                print(f"   📊 找到 {len(signals_distribution)} 個信號組合:")
                for row in signals_distribution[:10]:  # 只顯示前10個
                    print(f"      {row.symbol}: 信心度 {row.signal_strength:.3f}, 數量 {row.count}, 最新時間 {row.latest_time}")
            else:
                print("   📭 沒有找到待發送的信號")
                return
            
            # 2. 測試最佳信號查詢邏輯
            print("\n2️⃣ 測試最佳信號查詢邏輯...")
            
            # 查詢每個幣種的最高信心度
            subquery = (
                select(
                    SniperSignalDetails.symbol,
                    func.max(SniperSignalDetails.signal_strength).label('max_strength')
                )
                .where(
                    and_(
                        SniperSignalDetails.email_status.in_([EmailStatus.PENDING, EmailStatus.FAILED]),
                        SniperSignalDetails.email_sent_at.is_(None),
                        SniperSignalDetails.email_retry_count < 5,
                        SniperSignalDetails.created_at >= datetime.now() - timedelta(hours=24)
                    )
                )
                .group_by(SniperSignalDetails.symbol)
                .subquery()
            )
            
            # 獲取最優秀的信號詳情
            result = await db.execute(
                select(SniperSignalDetails)
                .join(
                    subquery,
                    and_(
                        SniperSignalDetails.symbol == subquery.c.symbol,
                        SniperSignalDetails.signal_strength == subquery.c.max_strength
                    )
                )
                .where(
                    and_(
                        SniperSignalDetails.email_status.in_([EmailStatus.PENDING, EmailStatus.FAILED]),
                        SniperSignalDetails.email_sent_at.is_(None)
                    )
                )
                .order_by(
                    desc(SniperSignalDetails.signal_strength),
                    desc(SniperSignalDetails.created_at)
                )
            )
            
            best_signals = result.scalars().all()
            print(f"   📈 SQL 查詢返回 {len(best_signals)} 個最佳信號")
            
            # 3. 測試去重邏輯
            print("\n3️⃣ 測試去重邏輯...")
            
            # 檢查是否有重複的幣種
            symbol_counts = {}
            for signal in best_signals:
                if signal.symbol in symbol_counts:
                    symbol_counts[signal.symbol] += 1
                else:
                    symbol_counts[signal.symbol] = 1
            
            duplicates = {symbol: count for symbol, count in symbol_counts.items() if count > 1}
            if duplicates:
                print(f"   ⚠️  發現重複幣種: {duplicates}")
                for symbol, count in duplicates.items():
                    print(f"      {symbol}: {count} 個相同最佳信號")
            else:
                print("   ✅ 沒有發現重複幣種")
            
            # 應用去重邏輯
            unique_signals = {}
            for signal in best_signals:
                if signal.symbol not in unique_signals:
                    unique_signals[signal.symbol] = signal
                else:
                    # 如果已存在該幣種，比較創建時間，選擇更新的
                    existing = unique_signals[signal.symbol]
                    if signal.created_at > existing.created_at:
                        print(f"      🔄 {signal.symbol}: 替換為更新的信號 ({signal.created_at} > {existing.created_at})")
                        unique_signals[signal.symbol] = signal
            
            final_signals = list(unique_signals.values())
            print(f"   📧 去重後剩餘 {len(final_signals)} 個信號")
            
            # 4. 顯示最終要發送的信號
            print("\n4️⃣ 最終要發送的信號:")
            if final_signals:
                for signal in final_signals[:5]:  # 只顯示前5個
                    print(f"      • {signal.symbol}: 信心度 {signal.signal_strength:.3f}, ID {signal.signal_id}, 時間 {signal.created_at}")
            else:
                print("      📭 沒有信號要發送")
            
        finally:
            await db.close()
            
    except Exception as e:
        print(f"❌ 測試過程中出現錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_duplicate_best_signals())
