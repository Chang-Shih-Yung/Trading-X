#!/usr/bin/env python3
"""
驗證信號完整生命週期的腳本
測試流程：
1. 創建符合精準門檻的15秒測試信號
2. 驗證信號倒數計時邏輯
3. 等待信號過期
4. 檢查歷史數據頁面顯示
5. 清理測試數據
"""

import requests
import json
import time
import sqlite3
from datetime import datetime, timedelta
import pytz

# 台灣時區
TAIWAN_TZ = pytz.timezone('Asia/Taipei')

def get_taiwan_now():
    """獲取台灣當前時間"""
    return datetime.now(TAIWAN_TZ).replace(tzinfo=None)

def create_precision_test_signal():
    """創建符合精準門檻的15秒測試信號"""
    try:
        print("🎯 創建精準測試信號...")
        
        # 連接資料庫直接插入測試信號
        conn = sqlite3.connect('tradingx.db')
        cursor = conn.cursor()
        
        # 生成測試信號數據 - 確保符合精準門檻
        now = get_taiwan_now()
        expires_at = now + timedelta(seconds=15)  # 15秒後過期
        
        test_signal = {
            'symbol': 'BTCUSDT',
            'timeframe': '1m',
            'signal_type': 'BUY',
            'signal_strength': 92.5,  # 高強度
            'confidence': 88.8,       # 高信心度
            'precision_score': 0.925, # 高精準度評分 > 0.9
            'entry_price': 65432.10,
            'stop_loss': 65200.00,
            'take_profit': 65800.00,
            'primary_timeframe': '1m',
            'strategy_name': '精準測試信號_15秒',
            'status': 'active',
            'is_scalping': 1,
            'is_precision_selected': 1,  # 標記為精準選中
            'market_condition_score': 0.92,  # 市場條件評分
            'indicator_consistency': 0.89,   # 指標一致性
            'timing_score': 0.94,           # 時機評分
            'risk_adjustment': 0.91,        # 風險調整
            'created_at': now.isoformat(),
            'expires_at': expires_at.isoformat(),
            'reasoning': '測試精準信號_驗證完整生命週期 (評分: 0.925)',
            'urgency_level': 'high',
            'risk_reward_ratio': 1.73
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
        
        print(f"✅ 精準測試信號創建成功 (ID: {signal_id})")
        print(f"📊 信號詳情:")
        print(f"   - 交易對: {test_signal['symbol']}")
        print(f"   - 精準度評分: {test_signal['precision_score']} (>0.9 門檻)")
        print(f"   - 信心度: {test_signal['confidence']}%")
        print(f"   - 信號強度: {test_signal['signal_strength']}")
        print(f"   - 過期時間: {expires_at.strftime('%H:%M:%S')} (15秒後)")
        
        return signal_id, test_signal
        
    except Exception as e:
        print(f"❌ 創建精準測試信號失敗: {e}")
        return None, None

def get_signals():
    """獲取當前活躍信號"""
    try:
        response = requests.get("http://localhost:8000/api/v1/scalping/signals")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'signals' in data:
                return data['signals']
            elif isinstance(data, list):
                return data
            else:
                print(f"⚠️ 意外的響應格式: {type(data)}")
                return []
        else:
            print(f"❌ API響應錯誤: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 獲取信號失敗: {e}")
        return []

def get_expired_signals():
    """獲取過期信號"""
    try:
        response = requests.get("http://localhost:8000/api/v1/scalping/expired")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ 獲取過期信號失敗: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 獲取過期信號失敗: {e}")
        return []

def find_test_signal_in_active(signals, test_signal_name="精準測試信號_15秒"):
    """在活躍信號中查找測試信號"""
    for signal in signals:
        if isinstance(signal, dict):
            strategy_name = signal.get('strategy_name', '')
            if test_signal_name in strategy_name:
                return signal
    return None

def find_test_signal_in_expired(expired_signals, test_signal_name="精準測試信號_15秒"):
    """在過期信號中查找測試信號"""
    for signal in expired_signals:
        if isinstance(signal, dict):
            strategy_name = signal.get('strategy_name', '')
            if test_signal_name in strategy_name:
                return signal
    return None

def cleanup_test_signal():
    """清理測試信號"""
    try:
        print("\n🧹 清理測試信號...")
        conn = sqlite3.connect('tradingx.db')
        cursor = conn.cursor()
        
        # 刪除測試信號
        cursor.execute("""
            DELETE FROM trading_signals 
            WHERE strategy_name LIKE '%精準測試信號_15秒%'
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            print(f"✅ 已清理 {deleted_count} 個測試信號")
        else:
            print("⚠️ 未找到要清理的測試信號")
            
        return deleted_count > 0
            
    except Exception as e:
        print(f"❌ 清理測試信號失敗: {e}")
        return False

def test_signal_lifecycle():
    """測試信號完整生命週期"""
    print("� 開始測試信號完整生命週期...")
    print("=" * 60)
    
    # 步驟1: 創建精準測試信號
    signal_id, test_signal = create_precision_test_signal()
    if not signal_id:
        print("❌ 無法創建測試信號，測試終止")
        return False
    
    print("\n⏳ 等待3秒讓系統處理...")
    time.sleep(3)
    
    # 步驟2: 驗證信號出現在活躍列表中
    print(f"\n📊 {datetime.now().strftime('%H:%M:%S')} - 檢查活躍信號")
    active_signals = get_signals()
    test_active_signal = find_test_signal_in_active(active_signals)
    
    if test_active_signal:
        remaining = test_active_signal.get('remaining_time_minutes', 0)
        remaining_seconds = test_active_signal.get('validity_info', {}).get('remaining_seconds', 0)
        print(f"✅ 測試信號出現在活躍列表中")
        print(f"   - 剩餘時間: {remaining:.2f}分鐘 ({remaining_seconds}秒)")
        print(f"   - 精準度評分: {test_active_signal.get('precision_score', 0)}")
        print(f"   - 是否精準驗證: {test_active_signal.get('is_precision_verified', False)}")
    else:
        print("❌ 測試信號未出現在活躍列表中")
        cleanup_test_signal()
        return False
    
    # 步驟3: 等待一段時間再檢查（驗證倒數）
    print(f"\n⏳ 等待8秒驗證倒數...")
    time.sleep(8)
    
    print(f"\n📊 {datetime.now().strftime('%H:%M:%S')} - 再次檢查活躍信號")
    active_signals2 = get_signals()
    test_active_signal2 = find_test_signal_in_active(active_signals2)
    
    if test_active_signal2:
        remaining2 = test_active_signal2.get('remaining_time_minutes', 0)
        remaining_seconds2 = test_active_signal2.get('validity_info', {}).get('remaining_seconds', 0)
        
        time_diff = remaining - remaining2
        seconds_diff = remaining_seconds - remaining_seconds2
        
        print(f"📈 時間倒數驗證:")
        print(f"   - 第一次: {remaining:.2f}分鐘 ({remaining_seconds}秒)")
        print(f"   - 第二次: {remaining2:.2f}分鐘 ({remaining_seconds2}秒)")
        print(f"   - 差異: {time_diff:.2f}分鐘 ({seconds_diff}秒)")
        
        if seconds_diff > 6:  # 考慮到8秒間隔
            print("✅ 時間倒數正常")
        else:
            print("⚠️ 時間倒數可能有問題")
    else:
        print("⚠️ 第二次檢查時信號已消失（可能已過期）")
    
    # 步驟4: 等待信號過期
    print(f"\n⏳ 等待信號過期... (剩餘約{max(0, 15-8-3)}秒)")
    time.sleep(max(0, 15-8-3+2))  # 多等2秒確保過期
    
    # 步驟5: 檢查信號是否從活躍列表消失
    print(f"\n📊 {datetime.now().strftime('%H:%M:%S')} - 檢查信號是否過期")
    active_signals3 = get_signals()
    test_active_signal3 = find_test_signal_in_active(active_signals3)
    
    if test_active_signal3:
        print("❌ 信號仍在活躍列表中（未正確過期）")
        remaining3 = test_active_signal3.get('remaining_time_minutes', 0)
        print(f"   - 當前剩餘時間: {remaining3:.2f}分鐘")
    else:
        print("✅ 信號已從活躍列表中移除")
    
    # 步驟6: 檢查信號是否出現在歷史數據中
    print(f"\n📜 檢查歷史數據頁面...")
    expired_signals = get_expired_signals()
    test_expired_signal = find_test_signal_in_expired(expired_signals)
    
    if test_expired_signal:
        print("✅ 測試信號成功出現在歷史數據頁面")
        print(f"   - 狀態: {test_expired_signal.get('status', 'unknown')}")
        print(f"   - 歸檔時間: {test_expired_signal.get('archived_at', 'N/A')}")
        print(f"   - 策略名稱: {test_expired_signal.get('strategy_name', 'N/A')}")
    else:
        print("❌ 測試信號未出現在歷史數據頁面")
        print("⚠️ 可能需要手動觸發過期處理")
        
        # 嘗試手動觸發過期處理
        try:
            print("🔄 嘗試手動觸發過期處理...")
            response = requests.post("http://localhost:8000/api/v1/scalping/process-expired")
            if response.status_code == 200:
                print("✅ 手動觸發成功，重新檢查...")
                time.sleep(2)
                expired_signals = get_expired_signals()
                test_expired_signal = find_test_signal_in_expired(expired_signals)
                if test_expired_signal:
                    print("✅ 現在測試信號出現在歷史數據頁面")
                else:
                    print("❌ 仍未找到測試信號")
        except Exception as e:
            print(f"❌ 手動觸發失敗: {e}")
    
    return test_expired_signal is not None

def main():
    """主函數"""
    print("🧪 精準信號完整生命週期測試")
    print("=" * 60)
    print("📋 測試流程:")
    print("   1. 創建符合精準門檻的15秒測試信號")
    print("   2. 驗證信號出現在活躍列表中")
    print("   3. 驗證時間倒數功能")
    print("   4. 等待信號自動過期")
    print("   5. 驗證信號出現在歷史數據頁面")
    print("   6. 清理測試數據")
    print("=" * 60)
    
    # 運行生命週期測試
    success = test_signal_lifecycle()
    
    if success:
        print(f"\n🎉 測試成功完成！")
    else:
        print(f"\n⚠️ 測試部分失敗，請檢查相關功能")
    
    # 詢問是否清理
    print("\n" + "=" * 60)
    user_input = input("🤔 是否要清理測試信號? (y/N): ").strip().lower()
    
    if user_input in ['y', 'yes']:
        if cleanup_test_signal():
            print("✅ 測試完成並已清理")
        else:
            print("⚠️ 清理過程中出現問題")
    else:
        print("ℹ️ 測試信號保留，可手動清理")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
