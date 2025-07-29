#!/usr/bin/env python3
"""
測試精準信號的時間顯示和過期機制
"""

import sqlite3
import asyncio
from datetime import datetime, timedelta
import pytz
import requests
import time
import json

# 台灣時區
TAIWAN_TZ = pytz.timezone('Asia/Taipei')

def get_taiwan_now():
    """獲取台灣當前時間"""
    return datetime.now(TAIWAN_TZ).replace(tzinfo=None)

def create_test_signal():
    """創建一個測試精準信號，有效期限20秒"""
    try:
        # 連接資料庫
        conn = sqlite3.connect('tradingx.db')
        cursor = conn.cursor()
        
        # 生成測試信號數據
        now = get_taiwan_now()
        expires_at = now + timedelta(seconds=20)  # 20秒後過期
        
        test_signal = {
            'symbol': 'BTCUSDT',
            'timeframe': '1m',
            'signal_type': 'BUY',
            'signal_strength': 85.5,  # 必填欄位
            'confidence': 85.5,
            'precision_score': 0.892,
            'entry_price': 65432.10,
            'stop_loss': 65200.00,
            'take_profit': 65800.00,
            'primary_timeframe': '1m',  # 必填欄位
            'strategy_name': '測試精準策略',
            'status': 'active',
            'is_scalping': 1,
            'is_precision_selected': 1,
            'market_condition_score': 0.88,
            'indicator_consistency': 0.91,
            'timing_score': 0.87,
            'risk_adjustment': 0.95,
            'created_at': now.isoformat(),
            'expires_at': expires_at.isoformat(),
            'reasoning': '測試精準篩選 - 20秒過期測試 (評分: 0.892)',
            'urgency_level': 'high',
            'risk_reward_ratio': 1.59
        }
        
        # 插入測試信號
        insert_query = """
            INSERT INTO trading_signals (
                symbol, timeframe, signal_type, signal_strength, confidence, precision_score,
                entry_price, stop_loss, take_profit, primary_timeframe, strategy_name,
                status, is_scalping, is_precision_selected,
                market_condition_score, indicator_consistency, timing_score, risk_adjustment,
                created_at, expires_at, reasoning, urgency_level, risk_reward_ratio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(insert_query, (
            test_signal['symbol'], test_signal['timeframe'], test_signal['signal_type'],
            test_signal['signal_strength'], test_signal['confidence'], test_signal['precision_score'],
            test_signal['entry_price'], test_signal['stop_loss'], test_signal['take_profit'],
            test_signal['primary_timeframe'], test_signal['strategy_name'], test_signal['status'], 
            test_signal['is_scalping'], test_signal['is_precision_selected'], 
            test_signal['market_condition_score'], test_signal['indicator_consistency'], 
            test_signal['timing_score'], test_signal['risk_adjustment'], test_signal['created_at'], 
            test_signal['expires_at'], test_signal['reasoning'], test_signal['urgency_level'], 
            test_signal['risk_reward_ratio']
        ))
        
        signal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ 測試信號已創建 (ID: {signal_id})")
        print(f"📊 信號詳情:")
        print(f"   - 交易對: {test_signal['symbol']}")
        print(f"   - 信號類型: {test_signal['signal_type']}")
        print(f"   - 精準度評分: {test_signal['precision_score']}")
        print(f"   - 創建時間: {test_signal['created_at']}")
        print(f"   - 過期時間: {test_signal['expires_at']}")
        print(f"   - 有效期限: 20秒")
        print(f"⏰ 將在 {expires_at.strftime('%H:%M:%S')} 過期")
        
        return signal_id, test_signal
        
    except Exception as e:
        print(f"❌ 創建測試信號失敗: {e}")
        return None, None

def test_api_response():
    """測試API響應中的時間顯示"""
    try:
        print("\n🔍 測試API響應...")
        response = requests.get('http://localhost:8000/api/v1/scalping/signals')
        
        if response.status_code == 200:
            data = response.json()
            signals = data.get('signals', [])
            
            # 查找BTCUSDT測試信號
            test_signal = None
            for signal in signals:
                if signal['symbol'] == 'BTCUSDT' and '測試精準策略' in signal.get('strategy_name', ''):
                    test_signal = signal
                    break
            
            if test_signal:
                print(f"✅ 找到測試信號:")
                print(f"   - 剩餘時間: {test_signal.get('remaining_time_minutes', 0):.2f} 分鐘")
                print(f"   - 剩餘秒數: {test_signal.get('validity_info', {}).get('remaining_seconds', 0)} 秒")
                print(f"   - 狀態: {test_signal.get('validity_info', {}).get('status', 'unknown')}")
                print(f"   - 顯示文字: {test_signal.get('validity_info', {}).get('text', 'N/A')}")
                print(f"   - 是否可執行: {test_signal.get('validity_info', {}).get('can_execute', False)}")
                
                return test_signal
            else:
                print("⚠️ 未找到測試信號")
                return None
        else:
            print(f"❌ API請求失敗: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 測試API響應失敗: {e}")
        return None

def wait_for_expiry_and_check():
    """等待信號過期並檢查歷史數據"""
    print("\n⏳ 等待信號過期...")
    
    # 等待25秒確保信號過期
    for i in range(25, 0, -1):
        print(f"⏰ 倒數 {i} 秒...")
        time.sleep(1)
    
    print("\n🔍 檢查信號是否已過期...")
    
    # 檢查當前活躍信號
    try:
        response = requests.get('http://localhost:8000/api/v1/scalping/signals')
        if response.status_code == 200:
            data = response.json()
            signals = data.get('signals', [])
            
            # 查找是否還有測試信號
            test_signal_found = False
            for signal in signals:
                if signal['symbol'] == 'BTCUSDT' and '測試精準策略' in signal.get('strategy_name', ''):
                    test_signal_found = True
                    break
            
            if not test_signal_found:
                print("✅ 測試信號已從活躍信號中移除")
            else:
                print("⚠️ 測試信號仍在活躍信號中")
        
    except Exception as e:
        print(f"❌ 檢查活躍信號失敗: {e}")
    
    # 檢查過期信號
    try:
        response = requests.get('http://localhost:8000/api/v1/scalping/expired')
        if response.status_code == 200:
            expired_signals = response.json()
            
            # 查找測試信號是否在過期列表中
            test_signal_in_expired = False
            for signal in expired_signals:
                if signal['symbol'] == 'BTCUSDT' and '測試精準策略' in signal.get('strategy_name', ''):
                    test_signal_in_expired = True
                    print("✅ 測試信號已出現在過期信號列表中")
                    print(f"   - 狀態: {signal.get('status', 'unknown')}")
                    print(f"   - 歸檔時間: {signal.get('archived_at', 'N/A')}")
                    break
            
            if not test_signal_in_expired:
                print("⚠️ 測試信號未在過期信號列表中找到")
                
        else:
            print(f"❌ 獲取過期信號失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 檢查過期信號失敗: {e}")

def cleanup_test_signal():
    """清理測試信號"""
    try:
        print("\n🧹 清理測試信號...")
        conn = sqlite3.connect('tradingx.db')
        cursor = conn.cursor()
        
        # 刪除測試信號
        cursor.execute("""
            DELETE FROM trading_signals 
            WHERE symbol = 'BTCUSDT' 
            AND strategy_name = '測試精準策略'
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            print(f"✅ 已清理 {deleted_count} 個測試信號")
        else:
            print("⚠️ 未找到要清理的測試信號")
            
    except Exception as e:
        print(f"❌ 清理測試信號失敗: {e}")

def main():
    """主測試流程"""
    print("🚀 開始精準信號時間顯示測試")
    print("=" * 50)
    
    # 1. 創建測試信號
    signal_id, test_signal = create_test_signal()
    if not signal_id:
        print("❌ 測試終止：無法創建測試信號")
        return
    
    # 2. 等待3秒讓後端處理
    print("\n⏳ 等待3秒讓後端處理...")
    time.sleep(3)
    
    # 3. 測試API響應
    api_signal = test_api_response()
    
    # 4. 等待信號過期並檢查
    wait_for_expiry_and_check()
    
    # 5. 詢問是否清理測試信號
    print("\n" + "=" * 50)
    user_input = input("🤔 是否要清理測試信號? (y/N): ").strip().lower()
    
    if user_input in ['y', 'yes']:
        cleanup_test_signal()
        print("✅ 測試完成並已清理")
    else:
        print("✅ 測試完成，測試信號保留")

if __name__ == "__main__":
    main()
