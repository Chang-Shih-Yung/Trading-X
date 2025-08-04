#!/usr/bin/env python3
"""
🧹 清理重複信號腳本
保留每個symbol最新的信號，刪除舊的重複信號
"""

import asyncio
import sqlite3
from datetime import datetime
from typing import List, Dict
import json

async def cleanup_duplicate_signals():
    """清理重複信號，每個symbol只保留最新的"""
    
    print("🧹 開始清理重複信號...")
    print("=" * 50)
    
    # 連接數據庫
    conn = sqlite3.connect('tradingx.db')
    cursor = conn.cursor()
    
    try:
        # 1. 獲取每個symbol的信號統計
        cursor.execute('''
            SELECT symbol, COUNT(*) as count
            FROM sniper_signal_details 
            WHERE status = 'ACTIVE'
            GROUP BY symbol
            ORDER BY count DESC
        ''')
        
        symbol_counts = cursor.fetchall()
        
        print("📊 每個交易對的活躍信號數量:")
        total_signals = 0
        for symbol, count in symbol_counts:
            print(f"  {symbol}: {count} 個信號")
            total_signals += count
        
        print(f"\n總計: {total_signals} 個活躍信號")
        print()
        
        # 2. 找出每個symbol最新的信號ID（要保留的）
        keep_signals = []
        for symbol, _ in symbol_counts:
            cursor.execute('''
                SELECT id, signal_id, created_at
                FROM sniper_signal_details 
                WHERE symbol = ? AND status = 'ACTIVE'
                ORDER BY created_at DESC, id DESC
                LIMIT 1
            ''', (symbol,))
            
            latest = cursor.fetchone()
            if latest:
                keep_signals.append(latest[0])
                print(f"✅ 保留 {symbol} 最新信號: {latest[1]} (ID: {latest[0]})")
        
        print(f"\n📌 將保留 {len(keep_signals)} 個最新信號")
        
        # 3. 計算要刪除的信號數量
        cursor.execute('''
            SELECT COUNT(*) 
            FROM sniper_signal_details 
            WHERE status = 'ACTIVE'
        ''')
        total_active = cursor.fetchone()[0]
        
        to_delete_count = total_active - len(keep_signals)
        
        if to_delete_count > 0:
            print(f"🗑️  將刪除 {to_delete_count} 個重複的舊信號")
            print()
            
            # 4. 詢問確認
            confirm = input(f"❓ 確定要刪除 {to_delete_count} 個重複信號嗎? (y/N): ")
            
            if confirm.lower() in ['y', 'yes']:
                # 5. 執行刪除（刪除不在keep_signals列表中的活躍信號）
                placeholders = ','.join(['?' for _ in keep_signals])
                
                if keep_signals:
                    cursor.execute(f'''
                        DELETE FROM sniper_signal_details 
                        WHERE status = 'ACTIVE' AND id NOT IN ({placeholders})
                    ''', keep_signals)
                else:
                    cursor.execute('''
                        DELETE FROM sniper_signal_details 
                        WHERE status = 'ACTIVE'
                    ''')
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                print(f"✅ 成功刪除 {deleted_count} 個重複信號")
                
                # 6. 驗證結果
                cursor.execute('''
                    SELECT symbol, COUNT(*) as count
                    FROM sniper_signal_details 
                    WHERE status = 'ACTIVE'
                    GROUP BY symbol
                ''')
                
                final_counts = cursor.fetchall()
                print(f"\n📊 清理後每個交易對的活躍信號數量:")
                for symbol, count in final_counts:
                    print(f"  {symbol}: {count} 個信號")
                
                total_remaining = sum(count for _, count in final_counts)
                print(f"\n總計: {total_remaining} 個活躍信號")
                
            else:
                print("❌ 取消刪除操作")
        else:
            print("✅ 沒有發現重複信號，無需清理")
    
    except Exception as e:
        print(f"❌ 清理過程中發生錯誤: {e}")
        conn.rollback()
    
    finally:
        conn.close()
        print("🏁 清理操作完成")

if __name__ == "__main__":
    asyncio.run(cleanup_duplicate_signals())
