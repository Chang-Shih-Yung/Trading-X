#!/usr/bin/env python3
"""
🎯 數據庫初始化腳本
初始化狙擊手策略系統所需的數據庫表結構
"""

import asyncio
import logging
from datetime import datetime

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_database():
    """初始化數據庫表結構"""
    try:
        logger.info("🚀 開始初始化數據庫...")
        
        # 導入數據庫相關模塊
        from app.core.database import engine, get_db
        from app.models.sniper_signal_history import Base
        
        # 創建所有表
        async with engine.begin() as conn:
            # 刪除現有表（如果存在）
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("🗑️ 清理現有表結構...")
            
            # 創建新表
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ 創建新表結構完成")
        
        logger.info("🎯 數據庫初始化完成！")
        
        # 插入一些測試數據
        await insert_test_data()
        
    except Exception as e:
        logger.error(f"❌ 數據庫初始化失敗: {e}")
        raise

async def insert_test_data():
    """插入測試數據"""
    try:
        logger.info("📊 開始插入測試數據...")
        
        from app.core.database import AsyncSessionLocal
        from app.models.sniper_signal_history import (
            SniperSignalDetails, 
            SignalStatus, 
            TradingTimeframe,
            SignalQuality,
            EmailStatus
        )
        from app.utils.timezone_utils import get_taiwan_now
        import uuid
        
        async with AsyncSessionLocal() as session:
            # 創建一些測試信號
            test_signals = []
            symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']
            
            for i, symbol in enumerate(symbols):
                # 分配不同的時間框架
                timeframes = [TradingTimeframe.SHORT_TERM, TradingTimeframe.MEDIUM_TERM, TradingTimeframe.LONG_TERM]
                quality_levels = [SignalQuality.HIGH, SignalQuality.MEDIUM, SignalQuality.LOW]
                email_statuses = [EmailStatus.SENT, EmailStatus.PENDING, EmailStatus.FAILED]
                
                signal = SniperSignalDetails(
                    signal_id=str(uuid.uuid4()),
                    symbol=symbol,
                    signal_type='BUY',
                    entry_price=50000.0 + i * 1000,  # 模擬價格
                    stop_loss_price=49000.0 + i * 1000,
                    take_profit_price=52000.0 + i * 1000,
                    signal_strength=0.85 + i * 0.02,
                    confluence_count=3 + i,
                    signal_quality=quality_levels[i % len(quality_levels)],
                    timeframe=timeframes[i % len(timeframes)],
                    expiry_hours=24,
                    risk_reward_ratio=2.0,
                    market_volatility=0.15,
                    atr_value=500.0,
                    market_regime='BULL',
                    created_at=get_taiwan_now(),
                    expires_at=get_taiwan_now(),
                    status=SignalStatus.HIT_TP if i % 2 == 0 else SignalStatus.ACTIVE,
                    result_price=51000.0 + i * 1000 if i % 2 == 0 else None,
                    result_time=get_taiwan_now() if i % 2 == 0 else None,
                    pnl_percentage=2.0 + i * 0.5 if i % 2 == 0 else None,
                    email_status=email_statuses[i % len(email_statuses)],
                    email_sent_at=get_taiwan_now() if i % 2 == 0 else None,
                    email_retry_count=i % 4,  # 0-3 重試次數
                    layer_one_time=0.5,
                    layer_two_time=1.2,
                    pass_rate=85.0 + i * 2,
                    reasoning=f"測試信號 {i+1}: {symbol} 技術指標匯聚，上漲信號強烈"
                )
                test_signals.append(signal)
            
            # 批量插入
            session.add_all(test_signals)
            await session.commit()
            
            logger.info(f"✅ 成功插入 {len(test_signals)} 個測試信號")
            
    except Exception as e:
        logger.error(f"❌ 插入測試數據失敗: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database())
