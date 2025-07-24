from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, create_tables
from app.services.market_data import MarketDataService
from app.services.strategy_engine import StrategyEngine

@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時初始化
    await create_tables()
    
    # 啟動市場數據服務
    market_service = MarketDataService()
    strategy_engine = StrategyEngine()
    
    # 儲存服務實例到應用程式狀態
    app.state.market_service = market_service
    app.state.strategy_engine = strategy_engine
    
    # 啟動背景任務
    market_task = asyncio.create_task(market_service.start_real_time_data())
    strategy_task = asyncio.create_task(strategy_engine.start_signal_generation())
    
    # 儲存任務以便後續取消
    app.state.background_tasks = [market_task, strategy_task]
    
    yield
    
    # 關閉時清理
    await market_service.stop()
    await strategy_engine.stop()
    
    # 取消背景任務
    for task in app.state.background_tasks:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

# 創建 FastAPI 應用程式
app = FastAPI(
    title="Trading X - 進階交易策略系統",
    description="整合多重技術指標的智能交易系統",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含 API 路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """根路徑健康檢查"""
    return {
        "message": "Trading X 系統正在運行",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """系統健康檢查"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
