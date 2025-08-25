#!/usr/bin/env python3
"""
Trading X 四資料庫分離系統
- market_data.db: 市場數據 (K線、指標、價格警報)
- learning_records.db: 學習記錄 (Phase2參數、Phase5回測)
- extreme_events.db: 極端事件 (閃崩、系統保護、流動性事件)
- signals.db: 信號歷史 (Phase2信號存儲、學習進度追蹤)
"""

import asyncio
import sqlite3
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SeparatedDatabaseManager:
    """四資料庫分離管理器"""
    
    def __init__(self, base_dir: str = None):
        # 修正為動態路徑
        if base_dir is None:
            self.base_dir = Path(__file__).parent.parent.parent
        else:
            self.base_dir = Path(base_dir)
        self.db_dir = self.base_dir / "databases"
        self.db_dir.mkdir(exist_ok=True)
        
        # 三個資料庫路徑
        self.databases = {
            "market_data": self.db_dir / "market_data.db",
            "learning_records": self.db_dir / "learning_records.db", 
            "extreme_events": self.db_dir / "extreme_events.db",
            "signals": self.db_dir / "signals.db"
        }
        
        # 建立引擎
        self.engines = {}
        self.session_factories = {}
        self.bases = {}
        
        for db_name, db_path in self.databases.items():
            # SQLite 異步連接字串
            db_url = f"sqlite+aiosqlite:///{db_path}"
            
            # 創建引擎
            self.engines[db_name] = create_async_engine(
                db_url,
                echo=False,
                future=True,
                pool_pre_ping=True
            )
            
            # 創建會話工廠
            self.session_factories[db_name] = async_sessionmaker(
                self.engines[db_name],
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # 創建基礎類
            self.bases[db_name] = declarative_base()
    
    def get_engine(self, db_name: str):
        """獲取指定資料庫引擎"""
        return self.engines.get(db_name)
    
    def get_session_factory(self, db_name: str):
        """獲取指定資料庫會話工廠"""
        return self.session_factories.get(db_name)
    
    def get_base(self, db_name: str):
        """獲取指定資料庫基礎類"""
        return self.bases.get(db_name)
    
    async def create_session(self, db_name: str) -> AsyncSession:
        """創建指定資料庫會話"""
        factory = self.session_factories.get(db_name)
        if not factory:
            raise ValueError(f"Database {db_name} not found")
        return factory()
    
    async def create_all_tables(self):
        """創建所有資料庫的表格"""
        
        # 導入所有模型
        try:
            from app.models.market_models import MarketData, TechnicalIndicator, PriceAlert
            from app.models.learning_models import Phase2Learning, Phase5Backtest, ParameterEvolution
            from app.models.extreme_models import CrashDetection, SystemProtection, LiquidityEvent, CorrelationBreakdown
        except ImportError:
            # 備用導入路徑
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from app.models.market_models import MarketData, TechnicalIndicator, PriceAlert
            from app.models.learning_models import Phase2Learning, Phase5Backtest, ParameterEvolution
            from app.models.extreme_models import CrashDetection, SystemProtection, LiquidityEvent, CorrelationBreakdown
        
        # 為每個資料庫創建對應的表格
        for db_name, engine in self.engines.items():
            try:
                async with engine.begin() as conn:
                    if db_name == "market_data":
                        await conn.run_sync(self.bases["market_data"].metadata.create_all)
                    elif db_name == "learning_records":
                        await conn.run_sync(self.bases["learning_records"].metadata.create_all)
                    elif db_name == "extreme_events":
                        await conn.run_sync(self.bases["extreme_events"].metadata.create_all)
                
                logger.info(f"Successfully created tables for {db_name}")
            except Exception as e:
                logger.error(f"Failed to create tables for {db_name}: {e}")
    
    async def get_db_session(self, db_name: str):
        """獲取資料庫會話 (依賴注入用)"""
        session = await self.create_session(db_name)
        try:
            yield session
        finally:
            await session.close()
    
    async def close_all(self):
        """關閉所有資料庫連接"""
        for db_name, engine in self.engines.items():
            try:
                await engine.dispose()
                logger.info(f"Closed database connection: {db_name}")
            except Exception as e:
                logger.error(f"Error closing {db_name}: {e}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """獲取資料庫資訊"""
        info = {
            "database_count": len(self.databases),
            "databases": {},
            "total_size_mb": 0
        }
        
        for db_name, db_path in self.databases.items():
            size_mb = 0
            if db_path.exists():
                size_mb = db_path.stat().st_size / (1024 * 1024)
                info["total_size_mb"] += size_mb
            
            info["databases"][db_name] = {
                "path": str(db_path),
                "exists": db_path.exists(),
                "size_mb": round(size_mb, 2)
            }
        
        info["total_size_mb"] = round(info["total_size_mb"], 2)
        return info

# 全域資料庫管理器
db_manager = SeparatedDatabaseManager()

# 便利函數
async def get_market_db():
    """獲取市場數據資料庫會話"""
    async for session in db_manager.get_db_session("market_data"):
        yield session

async def get_learning_db():
    """獲取學習記錄資料庫會話"""
    async for session in db_manager.get_db_session("learning_records"):
        yield session

async def get_extreme_db():
    """獲取極端事件資料庫會話"""
    async for session in db_manager.get_db_session("extreme_events"):
        yield session

async def get_signals_db():
    """獲取信號歷史資料庫會話"""
    async for session in db_manager.get_db_session("signals"):
        yield session

async def test_database_separation():
    """測試四資料庫分離系統"""
    print("🔍 測試四資料庫分離系統...")
    
    try:
        # 創建所有表格
        await db_manager.create_all_tables()
        
        # 獲取資料庫資訊
        info = db_manager.get_database_info()
        
        print(f"✅ 資料庫創建成功！")
        print(f"📊 資料庫數量: {info['database_count']}")
        print(f"💾 總大小: {info['total_size_mb']} MB")
        
        for db_name, db_info in info["databases"].items():
            status = "✅ 存在" if db_info["exists"] else "❌ 不存在"
            print(f"   {db_name}: {status} ({db_info['size_mb']} MB)")
        
        # 測試會話創建
        print(f"\n🔗 測試資料庫連接...")
        for db_name in ["market_data", "learning_records", "extreme_events", "signals"]:
            session = await db_manager.create_session(db_name)
            await session.close()
            print(f"   {db_name}: ✅ 連接成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False
    finally:
        await db_manager.close_all()

if __name__ == "__main__":
    asyncio.run(test_database_separation())
