#!/usr/bin/env python3
"""
🧪 信號生成與郵件系統測試
驗證完整流程：實時信號→資料庫→自動郵件
"""

import asyncio
import requests
from datetime import datetime, timedelta
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.sniper_signal_history import *
from app.utils.timezone_utils import get_taiwan_now
import time

async def create_test_signal():
    """創建測試信號驗證自動郵件系統"""
    async with AsyncSessionLocal() as session:
        test_signal = SniperSignalDetails(
            signal_id=f'MANUAL_TEST_{int(time.time())}',
            symbol='BTCUSDT',
            signal_type='BUY',
            entry_price=65000.0,
            stop_loss_price=64500.0,
            take_profit_price=66000.0,
            signal_strength=0.88,
            confluence_count=5,
            signal_quality=SignalQuality.HIGH,
            timeframe=TradingTimeframe.MEDIUM_TERM,
            expiry_hours=24,
            risk_reward_ratio=2.0,
            market_volatility=0.15,
            atr_value=200.0,
            market_regime='BULL',
            created_at=get_taiwan_now(),
            expires_at=get_taiwan_now() + timedelta(hours=24),
            status=SignalStatus.ACTIVE,
            email_status=EmailStatus.PENDING,  # 🎯 測試自動郵件
            email_retry_count=0,
            layer_one_time=0.3,
            layer_two_time=0.8,
            pass_rate=95.0,
            reasoning='🧪 手動測試: 驗證實時信號→資料庫→前端→自動郵件的完整流程'
        )
        
        session.add(test_signal)
        await session.commit()
        print(f'🧪 測試信號已創建: {test_signal.signal_id}')
        print(f'   - 符號: {test_signal.symbol}')
        print(f'   - 郵件狀態: {test_signal.email_status}')
        print(f'   - 創建時間: {test_signal.created_at}')
        return test_signal.signal_id

def test_api_signal_generation():
    """測試前端智能分層系統API"""
    try:
        response = requests.get(
            'http://localhost:8000/api/v1/sniper/smart-layer-signals',
            params={
                'include_analysis': True,
                'quality_threshold': 4,
                'max_signals_per_symbol': 1,
                'strategy_mode': 'comprehensive'
            }
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API響應成功: {len(data.get('signals', []))} 個信號")
            for signal in data.get('signals', [])[:3]:  # 只顯示前3個
                print(f"   - {signal.get('symbol')}: {signal.get('signal_type')} (強度: {signal.get('signal_strength', 0):.2f})")
        else:
            print(f"❌ API響應失敗: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ API測試失敗: {e}")

async def check_database_signals():
    """檢查資料庫中的信號"""
    async with AsyncSessionLocal() as session:
        # 檢查最近的信號
        query = select(SniperSignalDetails).order_by(
            SniperSignalDetails.created_at.desc()
        ).limit(5)
        
        result = await session.execute(query)
        signals = result.scalars().all()
        
        print(f"\n📊 資料庫最新5個信號:")
        for signal in signals:
            created_time = signal.created_at.strftime('%H:%M:%S')
            print(f"   {signal.symbol}: {signal.email_status} | {signal.signal_type} | {created_time}")

async def main():
    print("🚀 開始測試信號生成系統...")
    
    print("\n1. 測試前端API信號生成")
    test_api_signal_generation()
    
    print("\n2. 檢查資料庫現有信號")
    await check_database_signals()
    
    print("\n3. 手動創建測試信號")
    signal_id = await create_test_signal()
    
    print("\n4. 等待30秒後再檢查...")
    await asyncio.sleep(30)
    await check_database_signals()
    
    print("\n✅ 測試完成！請檢查郵件是否收到。")

if __name__ == "__main__":
    asyncio.run(main())
