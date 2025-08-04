#!/usr/bin/env python3
"""
🎯 簡化測試：直接插入信號到資料庫
"""

import asyncio
import logging
from datetime import datetime, timedelta
import uuid

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def insert_test_signal():
    """直接插入測試信號到資料庫"""
    try:
        logger.info("🚀 開始插入測試信號...")
        
        # 導入所需模塊
        from app.core.database import AsyncSessionLocal
        from app.models.sniper_signal_history import (
            SniperSignalDetails, 
            EmailStatus, 
            SignalStatus, 
            SignalQuality, 
            TradingTimeframe
        )
        from app.utils.timezone_utils import get_taiwan_now
        
        async with AsyncSessionLocal() as session:
            # 創建測試信號
            test_signal = SniperSignalDetails(
                signal_id=f"TEST_{int(datetime.now().timestamp())}",
                symbol="BTCUSDT",
                signal_type="BUY",
                entry_price=50500.0,
                stop_loss_price=49500.0,
                take_profit_price=52000.0,
                signal_strength=0.85,
                confluence_count=3,
                signal_quality=SignalQuality.HIGH,
                timeframe=TradingTimeframe.MEDIUM_TERM,
                expiry_hours=24,
                risk_reward_ratio=2.0,
                market_volatility=0.15,
                atr_value=100.0,
                market_regime="BULL",
                created_at=get_taiwan_now(),
                expires_at=get_taiwan_now() + timedelta(hours=24),
                status=SignalStatus.ACTIVE,
                email_status=EmailStatus.PENDING,  # 🎯 設置為待發送
                email_retry_count=0,
                layer_one_time=0.5,
                layer_two_time=1.2,
                pass_rate=85.0,
                reasoning="測試信號：技術指標匯聚，強烈看漲信號，測試郵件自動發送功能"
            )
            
            session.add(test_signal)
            await session.commit()
            
            logger.info(f"✅ 測試信號已插入資料庫！信號ID: {test_signal.signal_id}")
            logger.info("📧 郵件將在90秒內自動發送")
        
    except Exception as e:
        logger.error(f"❌ 插入測試信號失敗: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(insert_test_signal())
