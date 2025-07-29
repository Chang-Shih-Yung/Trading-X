#!/usr/bin/env python3
"""
清除測試信號
用於清理測試過程中生成的智能信號
"""

import sqlite3
from datetime import datetime
import pytz

# 台灣時區
TAIWAN_TZ = pytz.timezone('Asia/Taipei')

def get_taiwan_now():
    """獲取台灣當前時間"""
    return datetime.now(TAIWAN_TZ).replace(tzinfo=None)

def clear_test_signals():
    """清除測試信號"""
    
    conn = sqlite3.connect('tradingx.db')
    cursor = conn.cursor()
    
    # 查詢測試信號
    cursor.execute("""
        SELECT id, symbol, strategy_name, timeframe, created_at 
        FROM trading_signals 
        WHERE strategy_name LIKE '%牛市%' 
        AND is_scalping = 1 
        ORDER BY id DESC
    """)
    
    test_signals = cursor.fetchall()
    
    if not test_signals:
        print("❌ 沒有找到測試信號")
        conn.close()
        return
    
    print(f"🔍 找到 {len(test_signals)} 個測試信號:")
    for signal in test_signals:
        signal_id, symbol, strategy_name, timeframe, created_at = signal
        print(f"   ID: {signal_id} | {symbol} | {strategy_name} | {timeframe} | {created_at}")
    
    # 確認刪除
    print(f"\n⚠️  即將刪除 {len(test_signals)} 個測試信號")
    
    # 刪除測試信號
    cursor.execute("""
        DELETE FROM trading_signals 
        WHERE strategy_name LIKE '%牛市%' 
        AND is_scalping = 1
    """)
    
    deleted_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"🗑️  成功刪除 {deleted_count} 個測試信號")
    print("✅ 測試信號清理完成")

if __name__ == "__main__":
    clear_test_signals()
