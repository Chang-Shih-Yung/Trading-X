#!/usr/bin/env python3
"""
檢查信號時間和重複發送問題
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from sqlalchemy import text

async def check_signal_timing():
    async for db in get_db():
        try:
            # 檢查最新信號的詳細時間信息
            result = await db.execute(
                text('''
                    SELECT signal_id, symbol, signal_type, entry_price, 
                           expiry_hours, created_at, expires_at,
                           email_status, email_sent_at
                    FROM sniper_signal_details 
                    ORDER BY created_at DESC 
                    LIMIT 10
                ''')
            )
            signals = result.fetchall()
            
            print('⏰ 最新信號時間分析:')
            print('=' * 100)
            
            for signal in signals:
                from datetime import datetime
                created = datetime.fromisoformat(str(signal.created_at))
                expires = datetime.fromisoformat(str(signal.expires_at))
                duration_hours = (expires - created).total_seconds() / 3600
                
                print(f'🎯 {signal.symbol} ({signal.signal_id[:30]}...)')
                print(f'   創建時間: {signal.created_at}')
                print(f'   過期時間: {signal.expires_at}')
                print(f'   設定時長: {signal.expiry_hours}小時')
                print(f'   實際時長: {duration_hours:.1f}小時')
                print(f'   Email狀態: {signal.email_status}')
                
                if signal.expiry_hours == 24:
                    print(f'   ⚠️  仍使用固定24小時')
                else:
                    print(f'   ✅ 使用動態時間: {signal.expiry_hours}小時')
                    
                print()
                
            # 檢查重複信號
            print('\n🔍 檢查重複信號:')
            print('=' * 100)
            
            result = await db.execute(
                text('''
                    SELECT symbol, signal_type, entry_price, COUNT(*) as count,
                           MIN(created_at) as first_created,
                           MAX(created_at) as last_created
                    FROM sniper_signal_details 
                    WHERE created_at >= datetime('now', '-1 hour')
                    GROUP BY symbol, signal_type, ROUND(entry_price, 6)
                    HAVING COUNT(*) > 1
                    ORDER BY count DESC
                ''')
            )
            duplicates = result.fetchall()
            
            if duplicates:
                print(f'發現 {len(duplicates)} 組重複信號:')
                for dup in duplicates:
                    print(f'🔄 {dup.symbol} {dup.signal_type}: {dup.count}個重複')
                    print(f'   價格: ${dup.entry_price:.6f}')
                    print(f'   時間範圍: {dup.first_created} → {dup.last_created}')
                    print()
            else:
                print('✅ 沒有發現重複信號')
                
        except Exception as e:
            print(f"❌ 查詢失敗: {e}")
        break

if __name__ == "__main__":
    asyncio.run(check_signal_timing())
