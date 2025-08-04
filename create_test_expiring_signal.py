"""
創建一個測試狙擊手信號，用於驗證過期處理系統
⚠️  警告：這會創建測試資料，僅供開發測試使用！
"""

import sqlite3
import asyncio
from datetime import datetime, timedelta
from app.utils.time_utils import get_taiwan_now_naive

async def create_test_expiring_signal():
    """創建一個即將過期的測試狙擊手信號"""
    
    # 警告與確認
    print("⚠️  警告：這將創建測試資料！")
    print("📋 注意：根據系統要求，不應該有假資料或測試資料")
    print("🔄 這個腳本僅供開發測試和驗證過期處理系統使用")
    confirm = input("❓ 確定要創建測試信號嗎？(yes/no): ")
    
    if confirm.lower() not in ['yes', 'y']:
        print("❌ 操作已取消 - 沒有創建測試資料")
        return None
    
    try:
        # 連接資料庫
        conn = sqlite3.connect('tradingx.db')
        cursor = conn.cursor()
        
        # 生成測試信號數據（6秒後過期）
        now = get_taiwan_now_naive()
        expires_at = now + timedelta(minutes=1)  # 1分鐘後過期
        
        test_signal = {
            'symbol': 'TESTUSDT',
            'timeframe': '5m',
            'signal_type': 'BUY',
            'signal_strength': 75.0,
            'confidence': 0.75,
            'precision_score': 6.5,  # 高於4.0的精準信號閾值
            'entry_price': 50000.0,
            'current_price': 50000.0,
            'stop_loss': 49500.0,
            'take_profit': 50800.0,
            'risk_reward_ratio': 1.6,
            'primary_timeframe': '5m',
            'strategy_name': '🎯 測試狙擊手過期信號 - 2分鐘後過期',
            'is_scalping': 1,
            'is_precision_selected': 1,  # 標記為精準信號
            'market_condition_score': 0.8,
            'indicator_consistency': 0.85,
            'timing_score': 0.9,
            'risk_adjustment': 0.15,
            'created_at': now.isoformat(),
            'expires_at': expires_at.isoformat(),
            'reasoning': '🎯 這是一個測試狙擊手信號，專門用於驗證基於智能時間分層動態計算的過期處理系統。信號將在2分鐘後過期。',
            'urgency_level': 'high',
            'status': None,  # 活躍狀態
            'is_active': 1
        }
        
        # 插入測試信號 (讓數據庫自動生成ID)
        insert_sql = """
        INSERT INTO trading_signals (
            symbol, timeframe, signal_type, signal_strength, confidence, 
            precision_score, entry_price, current_price, stop_loss, take_profit, risk_reward_ratio,
            primary_timeframe, strategy_name, is_scalping, is_precision_selected, 
            market_condition_score, indicator_consistency, timing_score, risk_adjustment, 
            created_at, expires_at, reasoning, urgency_level, status, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(insert_sql, (
            test_signal['symbol'], test_signal['timeframe'], 
            test_signal['signal_type'], test_signal['signal_strength'], test_signal['confidence'],
            test_signal['precision_score'], test_signal['entry_price'], test_signal['current_price'],
            test_signal['stop_loss'], test_signal['take_profit'], test_signal['risk_reward_ratio'], 
            test_signal['primary_timeframe'], test_signal['strategy_name'], test_signal['is_scalping'], 
            test_signal['is_precision_selected'], test_signal['market_condition_score'], 
            test_signal['indicator_consistency'], test_signal['timing_score'], test_signal['risk_adjustment'], 
            test_signal['created_at'], test_signal['expires_at'], test_signal['reasoning'], 
            test_signal['urgency_level'], test_signal['status'], test_signal['is_active']
        ))
        
        signal_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        print(f"✅ 測試狙擊手過期信號已創建")
        print(f"📊 信號詳情:")
        print(f"   - ID: {signal_id}")
        print(f"   - 交易對: {test_signal['symbol']}")
        print(f"   - 信號類型: {test_signal['signal_type']}")
        print(f"   - 信心度: {test_signal['confidence']:.1%}")
        print(f"   - 精準度評分: {test_signal['precision_score']}")
        print(f"   - 創建時間: {test_signal['created_at']}")
        print(f"   - 過期時間: {test_signal['expires_at']}")
        print(f"   - 有效期限: 2分鐘")
        print(f"⏰ 將在 {expires_at.strftime('%H:%M:%S')} 過期")
        
        return signal_id
        
    except Exception as e:
        print(f"❌ 創建測試狙擊手過期信號失敗: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(create_test_expiring_signal())
