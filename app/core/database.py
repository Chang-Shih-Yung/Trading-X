from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
from app.core.config import settings
import os
from pathlib import Path

# 三個獨立資料庫配置
DB_BASE_PATH = Path("/Users/itts/Desktop/Trading X/data/databases")
DB_BASE_PATH.mkdir(parents=True, exist_ok=True)

# 市場數據庫引擎
market_engine = create_async_engine(
    f"sqlite+aiosqlite:///{DB_BASE_PATH}/market_data.db",
    echo=settings.DEBUG,
    future=True
)

# 學習記錄資料庫引擎
learning_engine = create_async_engine(
    f"sqlite+aiosqlite:///{DB_BASE_PATH}/learning_records.db",
    echo=settings.DEBUG,
    future=True
)

# 極端事件資料庫引擎
extreme_events_engine = create_async_engine(
    f"sqlite+aiosqlite:///{DB_BASE_PATH}/extreme_events.db",
    echo=settings.DEBUG,
    future=True
)

# 為了向後兼容，保留原始引擎（指向市場數據庫）
engine = market_engine

# 創建各資料庫的會話工廠
MarketSessionLocal = async_sessionmaker(
    market_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

LearningSessionLocal = async_sessionmaker(
    learning_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

ExtremeEventsSessionLocal = async_sessionmaker(
    extreme_events_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 為了向後兼容，保留原始會話工廠
AsyncSessionLocal = MarketSessionLocal

# 創建基礎模型類
Base = declarative_base()
LearningBase = declarative_base()
ExtremeEventsBase = declarative_base()

# 元數據
metadata = MetaData()
learning_metadata = MetaData()
extreme_events_metadata = MetaData()

async def create_tables():
    """創建所有資料表到對應的資料庫"""
    print("正在創建三個獨立資料庫...")
    
    # 創建市場數據庫表
    try:
        print("創建市場數據庫...")
        async with market_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ 市場數據庫創建完成")
    except Exception as e:
        print(f"市場數據庫創建錯誤: {e}")
    
    # 創建學習記錄資料庫表
    try:
        print("創建學習記錄資料庫...")
        from app.models.learning_models import LearningRecord, BacktestResult, ParameterEvolution, StrategyPerformance, LearningStatistics
        async with learning_engine.begin() as conn:
            await conn.run_sync(LearningBase.metadata.create_all)
        print("✅ 學習記錄資料庫創建完成")
    except Exception as e:
        print(f"學習記錄資料庫創建錯誤: {e}")
    
    # 創建極端事件資料庫表
    try:
        print("創建極端事件資料庫...")
        from app.models.extreme_events_models import CrashDetection, SystemProtection, LiquidityEvent, CorrelationBreakdown, VolumeAnomaly, EmergencyShutdown
        async with extreme_events_engine.begin() as conn:
            await conn.run_sync(ExtremeEventsBase.metadata.create_all)
        print("✅ 極端事件資料庫創建完成")
    except Exception as e:
        print(f"極端事件資料庫創建錯誤: {e}")

async def get_db():
    """獲取市場數據庫會話（向後兼容）"""
    async with MarketSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_market_db():
    """獲取市場數據庫會話"""
    async with MarketSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_learning_db():
    """獲取學習記錄資料庫會話"""
    async with LearningSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_extreme_events_db():
    """獲取極端事件資料庫會話"""
    async with ExtremeEventsSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

class DatabaseManager:
    """增強型資料庫管理器"""
    
    def __init__(self):
        self.market_engine = market_engine
        self.learning_engine = learning_engine
        self.extreme_events_engine = extreme_events_engine
        self.market_session_factory = MarketSessionLocal
        self.learning_session_factory = LearningSessionLocal
        self.extreme_events_session_factory = ExtremeEventsSessionLocal
        
        # 向後兼容
        self.engine = market_engine
        self.session_factory = MarketSessionLocal
    
    async def create_market_session(self) -> AsyncSession:
        """創建市場數據庫會話"""
        return self.market_session_factory()
    
    async def create_learning_session(self) -> AsyncSession:
        """創建學習記錄資料庫會話"""
        return self.learning_session_factory()
    
    async def create_extreme_events_session(self) -> AsyncSession:
        """創建極端事件資料庫會話"""
        return self.extreme_events_session_factory()
    
    async def create_session(self) -> AsyncSession:
        """創建新的資料庫會話（向後兼容，默認市場數據庫）"""
        return self.market_session_factory()
    
    async def close(self):
        """關閉所有資料庫連接"""
        await self.market_engine.dispose()
        await self.learning_engine.dispose()
        await self.extreme_events_engine.dispose()
    
    async def get_database_stats(self) -> dict:
        """獲取所有資料庫統計信息"""
        stats = {
            "market_data_db": f"{DB_BASE_PATH}/market_data.db",
            "learning_records_db": f"{DB_BASE_PATH}/learning_records.db", 
            "extreme_events_db": f"{DB_BASE_PATH}/extreme_events.db",
            "database_sizes": {}
        }
        
        # 計算檔案大小
        for db_name, db_path in [
            ("market_data", f"{DB_BASE_PATH}/market_data.db"),
            ("learning_records", f"{DB_BASE_PATH}/learning_records.db"),
            ("extreme_events", f"{DB_BASE_PATH}/extreme_events.db")
        ]:
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                size_mb = size_bytes / (1024 * 1024)
                stats["database_sizes"][db_name] = f"{size_mb:.2f} MB"
            else:
                stats["database_sizes"][db_name] = "0 MB (not created)"
        
        return stats

# 全域資料庫管理器實例
db_manager = DatabaseManager()
