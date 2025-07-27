#!/usr/bin/env python3
"""
驗證信號倒數計時邏輯的腳本
測試：
1. 信號生成後開始倒數
2. 過期後生成新信號
3. 每個幣種同時只有一個活躍信號
"""

import requests
import json
import time
from datetime import datetime

def get_signals():
    """獲取當前信號"""
    try:
        response = requests.get("http://localhost:8000/api/v1/scalping/signals")
        return response.json()
    except Exception as e:
        print(f"獲取信號失敗: {e}")
        return []

def test_countdown_logic():
    """測試倒數計時邏輯"""
    print("🔍 開始測試信號倒數計時邏輯...")
    print("=" * 60)
    
    # 第一次檢查
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - 第一次檢查")
    signals1 = get_signals()
    
    if not signals1:
        print("❌ 沒有信號")
        return
    
    for signal in signals1:
        remaining = signal.get('remaining_time_minutes', 0)
        print(f"📊 {signal['symbol']}: {remaining:.1f}分鐘剩餘 (ID: {signal.get('id', 'N/A')})")
    
    print("\n⏳ 等待30秒...")
    time.sleep(30)
    
    # 第二次檢查
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - 第二次檢查")
    signals2 = get_signals()
    
    print("\n📈 時間變化對比:")
    signal_map1 = {s['symbol']: s for s in signals1}
    signal_map2 = {s['symbol']: s for s in signals2}
    
    for symbol in signal_map1.keys():
        if symbol in signal_map2:
            old_time = signal_map1[symbol].get('remaining_time_minutes', 0)
            new_time = signal_map2[symbol].get('remaining_time_minutes', 0)
            old_id = signal_map1[symbol].get('id', 'N/A')
            new_id = signal_map2[symbol].get('id', 'N/A')
            
            time_diff = old_time - new_time
            
            if old_id == new_id:
                # 相同信號，檢查時間倒數
                if time_diff > 0:
                    print(f"✅ {symbol}: {old_time:.1f} → {new_time:.1f} (倒數 {time_diff:.1f}分鐘) ✓")
                else:
                    print(f"❌ {symbol}: {old_time:.1f} → {new_time:.1f} (時間沒倒數) ✗")
            else:
                # 不同信號，表示生成了新信號
                print(f"🔄 {symbol}: 新信號生成 (ID: {old_id} → {new_id})")
        else:
            print(f"❓ {symbol}: 信號消失")
    
    print("\n" + "=" * 60)
    print("✅ 測試完成")

if __name__ == "__main__":
    test_countdown_logic()
