#!/usr/bin/env python3
"""
測試動態時間計算集成
強制觸發新信號並檢查動態時間計算是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.services.realtime_signal_engine import RealtimeSignalEngine
from app.models.signal_types import TradingSignalAlert
from app.models.sniper_signal_history import SniperSignalDetails
from sqlalchemy import select
import logging

# 設置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

async def test_dynamic_time_calculation():
    """測試動態時間計算功能"""
    
    # 創建測試信號
    test_signals = [
        TradingSignalAlert(
            symbol="TESTUSDT", 
            signal_type="BUY",
            entry_price=50000.0,
            stop_loss=49000.0,
            take_profit=52000.0,
            confidence=0.95,  # 高信心度 - 應該得到更長時間
            timeframe="1h",
            urgency="high",
            risk_reward_ratio=2.04
        ),
        TradingSignalAlert(
            symbol="TEST2USDT", 
            signal_type="BUY",
            entry_price=100.0,
            stop_loss=95.0,
            take_profit=110.0,
            confidence=0.60,  # 中等信心度 - 應該得到中等時間
            timeframe="15m",
            urgency="medium",
            risk_reward_ratio=2.0
        ),
        TradingSignalAlert(
            symbol="TEST3USDT", 
            signal_type="BUY",
            entry_price=10.0,
            stop_loss=9.5,
            take_profit=11.0,
            confidence=0.30,  # 低信心度 - 應該得到較短時間
            timeframe="1m",
            urgency="low",
            risk_reward_ratio=1.0
        )
    ]
    
    engine = RealtimeSignalEngine()
    
    print("🧪 開始測試動態時間計算...")
    
    signal_ids = []
    for i, signal in enumerate(test_signals, 1):
        print(f"\n📊 測試信號 {i}: {signal.symbol}")
        print(f"   信心度: {signal.confidence}")
        print(f"   時間框架: {signal.timeframe}")
        print(f"   緊急度: {signal.urgency}")
        
        # 儲存信號並取得ID
        signal_id = await engine._save_signal_to_database(signal)
        if signal_id:
            signal_ids.append(signal_id)
            print(f"✅ 信號已儲存: {signal_id}")
        else:
            print(f"❌ 信號儲存失敗")
    
    # 檢查儲存的結果
    print(f"\n🔍 檢查儲存的信號時間計算結果:")
    print("=" * 80)
    
    async for session in get_async_session():
        for signal_id in signal_ids:
            result = await session.execute(
                select(SniperSignalDetails).where(
                    SniperSignalDetails.signal_id == signal_id
                )
            )
            signal_record = result.scalar_one_or_none()
            
            if signal_record:
                time_diff = signal_record.expires_at - signal_record.created_at
                actual_hours = time_diff.total_seconds() / 3600
                
                print(f"🎯 {signal_record.symbol}:")
                print(f"   設定時長: {signal_record.expiry_hours}小時")
                print(f"   實際時長: {actual_hours:.1f}小時") 
                print(f"   創建時間: {signal_record.created_at}")
                print(f"   過期時間: {signal_record.expires_at}")
                print(f"   品質: {signal_record.signal_quality}")
                print(f"   時間框架: {signal_record.timeframe}")
                
                if actual_hours != 24.0:
                    print(f"   ✅ 動態時間計算成功！")
                else:
                    print(f"   ⚠️  仍使用固定24小時")
                print()
        
        break  # 只需要一個session

if __name__ == "__main__":
    asyncio.run(test_dynamic_time_calculation())
