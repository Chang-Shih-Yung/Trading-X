#!/usr/bin/env python3
"""
測試真實價格計算功能
"""

import asyncio
import sqlite3
from datetime import datetime, timedelta
import requests
import time

def create_test_signal():
    """創建一個即將過期的測試信號"""
    try:
        conn = sqlite3.connect('tradingx.db')
        cursor = conn.cursor()
        
        # 創建一個1分鐘後過期的測試信號
        now = datetime.now()
        expires_at = now + timedelta(minutes=1)
        
        # 插入測試信號
        cursor.execute("""
            INSERT INTO trading_signals (
                symbol, timeframe, signal_type, signal_strength, confidence,
                entry_price, stop_loss, take_profit,
                primary_timeframe, strategy_name, urgency_level, reasoning,
                is_active, is_scalping, created_at, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'BTCUSDT', '5m', 'LONG', 0.85, 0.85,
            95000.0, 94000.0, 96000.0,  # 假設的價格
            '5m', '真實價格測試策略', 'high', '測試真實價格計算功能',
            True, True, now.isoformat(), expires_at.isoformat()
        ))
        
        signal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ 創建測試信號 ID: {signal_id}")
        print(f"   進場價格: $95,000")
        print(f"   過期時間: {expires_at.strftime('%H:%M:%S')}")
        return signal_id
        
    except Exception as e:
        print(f"❌ 創建測試信號失敗: {e}")
        return None

def check_signal_status(signal_id):
    """檢查信號狀態"""
    try:
        conn = sqlite3.connect('tradingx.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, symbol, entry_price, current_price, 
                   profit_loss_pct, trade_result, status, created_at, expires_at
            FROM trading_signals 
            WHERE id = ?
        """, (signal_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            print(f"\n📊 信號狀態報告 (ID: {signal_id}):")
            print(f"   幣種: {result[1]}")
            print(f"   進場價格: ${result[2]:,.2f}")
            print(f"   當前價格: ${result[3]:,.2f}" if result[3] else "   當前價格: 未設置")
            print(f"   盈虧百分比: {result[4]:.2f}%" if result[4] else "   盈虧百分比: 未計算")
            print(f"   交易結果: {result[5]}" if result[5] else "   交易結果: 未確定")
            print(f"   狀態: {result[6]}" if result[6] else "   狀態: 活躍")
            print(f"   過期時間: {result[8]}")
            return result
        else:
            print(f"❌ 找不到信號 ID: {signal_id}")
            return None
            
    except Exception as e:
        print(f"❌ 檢查信號狀態失敗: {e}")
        return None

def test_api_call():
    """測試API調用以觸發過期信號處理"""
    try:
        response = requests.get('http://localhost:8000/api/v1/scalping/signals')
        if response.status_code == 200:
            print("✅ API 調用成功，觸發過期信號處理")
        else:
            print(f"⚠️ API 調用返回狀態碼: {response.status_code}")
    except Exception as e:
        print(f"❌ API 調用失敗: {e}")

def main():
    """主測試流程"""
    print("🧪 開始測試真實價格計算功能")
    print("=" * 50)
    
    # 1. 創建測試信號
    signal_id = create_test_signal()
    if not signal_id:
        return
    
    # 2. 檢查初始狀態
    print("\n1️⃣ 檢查初始狀態:")
    check_signal_status(signal_id)
    
    # 3. 等待信號過期
    print(f"\n2️⃣ 等待信號過期（約65秒）...")
    for i in range(65):
        time.sleep(1)
        remaining = 65 - i
        print(f"\r   ⏳ 倒數計時: {remaining} 秒", end="", flush=True)
    
    print("\n\n3️⃣ 觸發過期信號處理:")
    test_api_call()
    
    # 4. 等待處理完成
    print("\n   等待處理完成...")
    time.sleep(3)
    
    # 5. 檢查最終狀態
    print("\n4️⃣ 檢查最終狀態:")
    final_result = check_signal_status(signal_id)
    
    if final_result and final_result[6] == 'expired':
        print("\n🎉 測試成功！信號已過期並處理完成")
        if final_result[3]:  # current_price
            print(f"✅ 成功獲取真實價格: ${final_result[3]:,.2f}")
        if final_result[4] is not None:  # profit_loss_pct
            print(f"✅ 成功計算盈虧: {final_result[4]:.2f}%")
        if final_result[5]:  # trade_result
            print(f"✅ 成功判斷結果: {final_result[5]}")
    else:
        print("\n❌ 測試失敗：信號未正確處理")

if __name__ == "__main__":
    main()
