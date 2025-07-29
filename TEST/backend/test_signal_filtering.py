#!/usr/bin/env python3
"""
測試後端信號篩選機制
驗證：
1. 同時創建兩筆同幣種的精準信號（信心度不同）
2. 檢查後端是否只保留信心度最高的信號
3. 驗證篩選機制是否正常工作
4. 清理所有測試數據
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

def create_dual_precision_signals():
    """創建兩筆同幣種但信心度不同的精準信號"""
    try:
        print("🎯 創建兩筆同幣種精準測試信號...")
        
        # 連接資料庫
        conn = sqlite3.connect('tradingx.db')
        cursor = conn.cursor()
        
        now = get_taiwan_now()
        expires_at = now + timedelta(seconds=25)  # 25秒後過期
        
        # 第一筆信號 - 高信心度
        signal1 = {
            'symbol': 'BTCUSDT',
            'timeframe': '1m',
            'signal_type': 'BUY',
            'signal_strength': 95.5,  # 高強度
            'confidence': 92.8,       # 高信心度
            'precision_score': 0.950, # 高精準度評分
            'entry_price': 65432.10,
            'stop_loss': 65200.00,
            'take_profit': 65800.00,
            'primary_timeframe': '1m',
            'strategy_name': '高信心度測試信號_25秒',
            'status': 'active',
            'is_scalping': 1,
            'is_precision_selected': 1,
            'market_condition_score': 0.95,
            'indicator_consistency': 0.92,
            'timing_score': 0.96,
            'risk_adjustment': 0.93,
            'created_at': now.isoformat(),
            'expires_at': expires_at.isoformat(),
            'reasoning': '高信心度測試信號 - 篩選機制驗證 (評分: 0.950)',
            'urgency_level': 'high',
            'risk_reward_ratio': 1.73
        }
        
        # 第二筆信號 - 較低信心度
        signal2 = {
            'symbol': 'BTCUSDT',  # 相同幣種
            'timeframe': '1m',
            'signal_type': 'BUY',
            'signal_strength': 88.2,  # 較低強度
            'confidence': 85.6,       # 較低信心度
            'precision_score': 0.905, # 較低精準度評分（但仍>0.9）
            'entry_price': 65425.50,
            'stop_loss': 65190.00,
            'take_profit': 65790.00,
            'primary_timeframe': '1m',
            'strategy_name': '低信心度測試信號_25秒',
            'status': 'active',
            'is_scalping': 1,
            'is_precision_selected': 1,
            'market_condition_score': 0.89,
            'indicator_consistency': 0.87,
            'timing_score': 0.91,
            'risk_adjustment': 0.88,
            'created_at': now.isoformat(),
            'expires_at': expires_at.isoformat(),
            'reasoning': '低信心度測試信號 - 篩選機制驗證 (評分: 0.905)',
            'urgency_level': 'high',
            'risk_reward_ratio': 1.55
        }
        
        # 插入第一筆信號
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
            signal1['symbol'], signal1['timeframe'], signal1['signal_type'],
            signal1['signal_strength'], signal1['confidence'], signal1['precision_score'],
            signal1['entry_price'], signal1['stop_loss'], signal1['take_profit'],
            signal1['primary_timeframe'], signal1['strategy_name'], signal1['status'], 
            signal1['is_scalping'], signal1['is_precision_selected'], 
            signal1['market_condition_score'], signal1['indicator_consistency'], 
            signal1['timing_score'], signal1['risk_adjustment'], signal1['created_at'], 
            signal1['expires_at'], signal1['reasoning'], signal1['urgency_level'], 
            signal1['risk_reward_ratio']
        ))
        
        signal1_id = cursor.lastrowid
        
        # 插入第二筆信號
        cursor.execute(insert_query, (
            signal2['symbol'], signal2['timeframe'], signal2['signal_type'],
            signal2['signal_strength'], signal2['confidence'], signal2['precision_score'],
            signal2['entry_price'], signal2['stop_loss'], signal2['take_profit'],
            signal2['primary_timeframe'], signal2['strategy_name'], signal2['status'], 
            signal2['is_scalping'], signal2['is_precision_selected'], 
            signal2['market_condition_score'], signal2['indicator_consistency'], 
            signal2['timing_score'], signal2['risk_adjustment'], signal2['created_at'], 
            signal2['expires_at'], signal2['reasoning'], signal2['urgency_level'], 
            signal2['risk_reward_ratio']
        ))
        
        signal2_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        print(f"✅ 兩筆測試信號創建成功")
        print(f"📊 信號對比:")
        print(f"   第一筆 (ID: {signal1_id}):")
        print(f"   - 信心度: {signal1['confidence']}%")
        print(f"   - 精準度: {signal1['precision_score']}")
        print(f"   - 策略名: {signal1['strategy_name']}")
        print(f"   第二筆 (ID: {signal2_id}):")
        print(f"   - 信心度: {signal2['confidence']}%")
        print(f"   - 精準度: {signal2['precision_score']}")
        print(f"   - 策略名: {signal2['strategy_name']}")
        print(f"   🎯 預期保留: 第一筆（信心度更高）")
        
        return [signal1_id, signal2_id], [signal1, signal2]
        
    except Exception as e:
        print(f"❌ 創建測試信號失敗: {e}")
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
                return []
        else:
            print(f"❌ API響應錯誤: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 獲取信號失敗: {e}")
        return []

def get_dashboard_signals():
    """獲取儀表板精準信號"""
    try:
        response = requests.get("http://localhost:8000/api/v1/scalping/dashboard-precision-signals")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'signals' in data:
                return data['signals']
            elif isinstance(data, list):
                return data
            else:
                return []
        else:
            print(f"❌ 儀表板API響應錯誤: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 獲取儀表板信號失敗: {e}")
        return []

def get_expired_signals():
    """獲取過期信號（歷史數據）"""
    try:
        response = requests.get("http://localhost:8000/api/v1/scalping/expired")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'signals' in data:
                return data['signals']
            elif isinstance(data, list):
                return data
            else:
                return []
        else:
            print(f"❌ 歷史信號API響應錯誤: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 獲取歷史信號失敗: {e}")
        return []

def find_btcusdt_signals(signals):
    """查找BTCUSDT的測試信號"""
    btc_signals = []
    for signal in signals:
        if isinstance(signal, dict):
            symbol = signal.get('symbol', '')
            strategy_name = signal.get('strategy_name', '')
            if symbol == 'BTCUSDT' and ('測試信號_25秒' in strategy_name):
                btc_signals.append(signal)
    return btc_signals

def cleanup_test_signals():
    """清理所有測試信號"""
    try:
        print("\n🧹 清理所有測試信號...")
        conn = sqlite3.connect('tradingx.db')
        cursor = conn.cursor()
        
        # 刪除所有測試信號
        cursor.execute("""
            DELETE FROM trading_signals 
            WHERE strategy_name LIKE '%測試信號_25秒%'
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            print(f"✅ 已清理 {deleted_count} 個測試信號")
        else:
            print("⚠️ 未找到要清理的測試信號")
            
        return deleted_count
            
    except Exception as e:
        print(f"❌ 清理測試信號失敗: {e}")
        return 0

def test_signal_filtering_mechanism():
    """測試信號篩選機制"""
    print("🧪 測試後端信號篩選機制")
    print("=" * 80)
    print("📋 測試目標:")
    print("   1. 創建兩筆同幣種但信心度不同的精準信號")
    print("   2. 檢查API是否只返回信心度最高的信號")
    print("   3. 驗證儀表板篩選機制正確性")
    print("   4. 檢查歷史數據頁面是否也只有一筆過期信號")
    print("=" * 80)
    
    # 步驟1: 創建兩筆測試信號
    signal_ids, signals_data = create_dual_precision_signals()
    if not signal_ids:
        print("❌ 無法創建測試信號，測試終止")
        return False
    
    print("\n⏳ 等待3秒讓系統處理...")
    time.sleep(3)
    
    # 步驟2: 檢查普通API返回的信號
    print(f"\n📊 {datetime.now().strftime('%H:%M:%S')} - 檢查普通API返回的信號")
    active_signals = get_signals()
    btc_signals = find_btcusdt_signals(active_signals)
    
    print(f"🔍 普通API找到 {len(btc_signals)} 個BTCUSDT測試信號")
    
    # 顯示找到的信號詳情
    for i, signal in enumerate(btc_signals, 1):
        confidence = signal.get('confidence', 0)
        strategy_name = signal.get('strategy_name', '')
        print(f"   信號{i}: {strategy_name} - 信心度{confidence}%")
    
    # 步驟3: 檢查儀表板API返回的信號（這是重點）
    print(f"\n📱 {datetime.now().strftime('%H:%M:%S')} - 檢查儀表板精準信號API")
    dashboard_signals = get_dashboard_signals()
    dashboard_btc_signals = find_btcusdt_signals(dashboard_signals)
    
    print(f"🎯 儀表板API找到 {len(dashboard_btc_signals)} 個BTCUSDT測試信號")
    
    filtering_success = False
    
    if len(dashboard_btc_signals) == 0:
        print("❌ 儀表板沒有找到任何BTCUSDT測試信號")
        
    elif len(dashboard_btc_signals) == 1:
        # 理想情況：只有一個信號
        signal = dashboard_btc_signals[0]
        confidence = signal.get('confidence', 0)
        precision_score = signal.get('precision_score', 0)
        strategy_name = signal.get('strategy_name', '')
        
        print(f"✅ 儀表板篩選機制正常工作 - 只返回1個信號:")
        print(f"   - 策略名稱: {strategy_name}")
        print(f"   - 信心度: {confidence}%")
        print(f"   - 精準度: {precision_score}")
        
        # 驗證是否保留了信心度更高的信號
        if confidence >= 92:  # 第一筆信號的信心度
            print(f"✅ 正確保留了高信心度信號")
            filtering_success = True
        else:
            print(f"❌ 保留了錯誤的信號（應該保留信心度更高的）")
            filtering_success = False
    
    elif len(dashboard_btc_signals) == 2:
        # 兩個信號都存在，篩選機制未工作
        print(f"⚠️ 儀表板發現2個BTCUSDT測試信號，篩選機制未工作:")
        
        for i, signal in enumerate(dashboard_btc_signals, 1):
            confidence = signal.get('confidence', 0)
            precision_score = signal.get('precision_score', 0)
            strategy_name = signal.get('strategy_name', '')
            print(f"   信號{i}: {strategy_name} - 信心度{confidence}% - 精準度{precision_score}")
        
        print(f"❌ 儀表板篩選機制未正常工作（應該只保留1個信號）")
        filtering_success = False
    
    else:
        print(f"❓ 意外情況：儀表板找到 {len(dashboard_btc_signals)} 個信號")
        filtering_success = False
    
    # 步驟4: 等待信號過期
    print(f"\n⏳ 等待25秒讓信號過期...")
    time.sleep(26)  # 多等1秒確保過期
    
    # 步驟5: 檢查歷史數據頁面
    print(f"\n📚 {datetime.now().strftime('%H:%M:%S')} - 檢查歷史數據頁面")
    expired_signals = get_expired_signals()
    expired_btc_signals = find_btcusdt_signals(expired_signals)
    
    print(f"� 歷史數據找到 {len(expired_btc_signals)} 個BTCUSDT測試信號")
    
    if len(expired_btc_signals) == 1:
        signal = expired_btc_signals[0]
        confidence = signal.get('confidence', 0)
        strategy_name = signal.get('strategy_name', '')
        print(f"✅ 歷史數據正確 - 只有1個過期信號:")
        print(f"   - 策略名稱: {strategy_name}")
        print(f"   - 信心度: {confidence}%")
        
        if confidence >= 92:
            print(f"✅ 歷史數據保留了正確的高信心度信號")
        else:
            print(f"⚠️ 歷史數據保留了低信心度信號")
            
    elif len(expired_btc_signals) == 2:
        print(f"⚠️ 歷史數據中有2個過期信號，篩選可能未生效")
        for i, signal in enumerate(expired_btc_signals, 1):
            confidence = signal.get('confidence', 0)
            strategy_name = signal.get('strategy_name', '')
            print(f"   過期信號{i}: {strategy_name} - 信心度{confidence}%")
    else:
        print(f"❓ 歷史數據中有 {len(expired_btc_signals)} 個過期信號")
    
    return filtering_success

def main():
    """主函數"""
    print("🚀 後端信號篩選機制測試")
    print("=" * 60)
    
    try:
        # 運行篩選測試
        success = test_signal_filtering_mechanism()
        
        if success:
            print(f"\n🎉 測試結果: 篩選機制工作正常！")
            print("✅ 後端成功保留了信心度最高的信號")
        else:
            print(f"\n⚠️ 測試結果: 篩選機制可能需要檢查")
            print("❌ 後端未能正確篩選信號")
        
        # 給用戶時間檢查前端
        print("\n" + "=" * 60)
        print("🔍 現在您可以手動檢查前端頁面：")
        print("   1. 儀表板頁面 - 查看是否只顯示1個高信心度信號")
        print("   2. 歷史數據頁面 - 查看是否只有1個過期信號")
        print("⏰ 等待60秒後自動清理測試數據...")
        
        # 倒數計時
        for i in range(60, 0, -10):
            print(f"   ⏳ {i}秒後自動清理...")
            time.sleep(10)
        
        # 詢問是否清理
        print("\n" + "=" * 60)
        print("� 自動清理所有測試信號...")
        deleted_count = cleanup_test_signals()
        if deleted_count > 0:
            print("✅ 測試完成並已清理所有測試數據")
        else:
            print("⚠️ 清理過程中出現問題")
        
    except KeyboardInterrupt:
        print(f"\n\n🛑 測試被用戶中止")
        cleanup_test_signals()
    except Exception as e:
        print(f"\n\n❌ 測試過程中出現錯誤: {e}")
        cleanup_test_signals()
    
    print("=" * 60)

if __name__ == "__main__":
    main()
