#!/usr/bin/env python3
"""
🧹 清理測試信號腳本
保留真實信號，刪除測試信號

測試信號特徵：
1. signal_id 包含 "test_" 
2. reasoning 包含 "測試"
3. sniper_metrics 包含 "test": True
"""

import asyncio
import sqlite3
from datetime import datetime
from typing import List, Dict
import json

async def cleanup_test_signals():
    """清理測試信號"""
    
    print("🧹 開始清理測試信號...")
    print("=" * 50)
    
    # 連接數據庫
    conn = sqlite3.connect('tradingx.db')
    cursor = conn.cursor()
    
    try:
        # 1. 查詢所有信號，識別測試信號
        cursor.execute('''
            SELECT id, signal_id, symbol, created_at, reasoning, metadata_json, status
            FROM sniper_signal_details 
            ORDER BY created_at DESC
        ''')
        
        all_signals = cursor.fetchall()
        test_signals = []
        real_signals = []
        
        print(f"📊 總信號數量: {len(all_signals)}")
        
        for signal in all_signals:
            signal_id, symbol, created_at, reasoning, metadata_json, status = signal[1], signal[2], signal[3], signal[4], signal[5], signal[6]
            
            # 判斷是否為測試信號
            is_test = False
            
            # 條件1: signal_id 包含 "test_"
            if "test_" in signal_id.lower():
                is_test = True
                
            # 條件2: reasoning 包含 "測試"
            if reasoning and "測試" in reasoning:
                is_test = True
                
            # 條件3: metadata_json 包含 test: true
            if metadata_json:
                try:
                    metadata = json.loads(metadata_json)
                    if metadata.get("test") is True:
                        is_test = True
                except:
                    pass
            
            if is_test:
                test_signals.append(signal)
            else:
                real_signals.append(signal)
        
        print(f"🧪 測試信號數量: {len(test_signals)}")
        print(f"✅ 真實信號數量: {len(real_signals)}")
        print()
        
        # 2. 顯示要刪除的測試信號
        if test_signals:
            print("🗑️  將要刪除的測試信號:")
            for i, signal in enumerate(test_signals[:10]):  # 只顯示前10個
                print(f"  {i+1}. ID: {signal[1]}, Symbol: {signal[2]}, Created: {signal[3]}")
            
            if len(test_signals) > 10:
                print(f"  ... 還有 {len(test_signals) - 10} 個測試信號")
            print()
            
            # 3. 詢問確認
            confirm = input(f"❓ 確定要刪除 {len(test_signals)} 個測試信號嗎? (y/N): ")
            
            if confirm.lower() in ['y', 'yes']:
                # 4. 執行刪除
                test_ids = [signal[0] for signal in test_signals]
                placeholders = ','.join(['?' for _ in test_ids])
                
                cursor.execute(f'''
                    DELETE FROM sniper_signal_details 
                    WHERE id IN ({placeholders})
                ''', test_ids)
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                print(f"✅ 成功刪除 {deleted_count} 個測試信號")
                
                # 5. 驗證剩餘信號
                cursor.execute('SELECT COUNT(*) FROM sniper_signal_details')
                remaining_count = cursor.fetchone()[0]
                print(f"📊 剩餘信號數量: {remaining_count}")
                
            else:
                print("❌ 取消刪除操作")
        else:
            print("✅ 沒有找到測試信號，無需清理")
    
    except Exception as e:
        print(f"❌ 清理過程中發生錯誤: {e}")
        conn.rollback()
    
    finally:
        conn.close()
        print("🏁 清理操作完成")

if __name__ == "__main__":
    asyncio.run(cleanup_test_signals())
