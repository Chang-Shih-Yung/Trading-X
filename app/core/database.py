from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
from app.core.config import settings

# 創建非同步資料庫引擎
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# 創建會話工廠
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 創建基礎模型類
Base = declarative_base()

# 元數據
metadata = MetaData()

async def create_tables():
    """創建所有資料表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """獲取資料庫會話"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

class DatabaseManager:
    """資料庫管理器"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal
    
    async def create_session(self) -> AsyncSession:
        """創建新的資料庫會話"""
        return self.session_factory()
    
    async def close(self):
        """關閉資料庫連接"""
        await self.engine.dispose()

# 全域資料庫管理器實例
db_manager = DatabaseManager()
