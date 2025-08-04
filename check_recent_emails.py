#!/usr/bin/env python3
"""
檢查最近發送的Email信號
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from sqlalchemy import text

async def check_recent_emails():
    async for db in get_db():
        try:
            result = await db.execute(
                text('''
                    SELECT signal_id, symbol, signal_type, entry_price, 
                           stop_loss_price, take_profit_price,
                           email_status, email_sent_at, reasoning
                    FROM sniper_signal_details 
                    WHERE email_status = 'SENT' 
                    ORDER BY email_sent_at DESC 
                    LIMIT 5
                ''')
            )
            signals = result.fetchall()
            
            print('📧 最近發送的Email信號:')
            print('=' * 80)
            for signal in signals:
                print(f'🎯 {signal.symbol} {signal.signal_type}')
                print(f'   信號ID: {signal.signal_id}')
                print(f'   進場價: ${signal.entry_price:.6f}')
                print(f'   止損價: ${signal.stop_loss_price:.6f}')
                print(f'   止盈價: ${signal.take_profit_price:.6f}')
                print(f'   發送時間: {signal.email_sent_at}')
                print(f'   Email狀態: {signal.email_status}')
                print(f'   分析摘要: {signal.reasoning}')
                print('-' * 80)
                
        except Exception as e:
            print(f"❌ 查詢失敗: {e}")
        break

if __name__ == "__main__":
    asyncio.run(check_recent_emails())
