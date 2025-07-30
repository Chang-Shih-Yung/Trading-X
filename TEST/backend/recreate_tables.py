#!/usr/bin/env python3
"""
重新創建數據庫表以匹配最新的模型定義
"""

import asyncio
from app.core.database import engine, Base
from app.models.models import TradingSignal, MarketData, TechnicalIndicator, Strategy

async def recreate_tables():
    """重新創建所有數據庫表"""
    try:
        async with engine.begin() as conn:
            # 刪除現有表
            await conn.run_sync(Base.metadata.drop_all)
            print('✅ 已刪除現有表')
            
            # 重新創建表
            await conn.run_sync(Base.metadata.create_all)
            print('✅ 已重新創建表')
            
        print('🎉 數據庫表結構更新完成！')
        
    except Exception as e:
        print(f'❌ 更新數據庫表結構失敗: {e}')
        raise

if __name__ == "__main__":
    asyncio.run(recreate_tables())
