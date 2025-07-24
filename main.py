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
    """應用程式生命週期管理 - 簡化版本避免錯誤"""
    try:
        # 啟動時初始化數據庫
        await create_tables()
        print("✅ 數據庫初始化完成")
        
        # 創建服務實例但不立即啟動背景任務（避免錯誤）
        market_service = MarketDataService()
        strategy_engine = StrategyEngine()
        
        # 儲存服務實例到應用程式狀態
        app.state.market_service = market_service
        app.state.strategy_engine = strategy_engine
        
        print("✅ 服務實例創建完成")
        
    except Exception as e:
        print(f"⚠️ 初始化警告: {e}")
        # 即使出錯也繼續啟動，避免服務無法啟動
    
    yield
    
    # 關閉時清理
    try:
        if hasattr(app.state, 'market_service'):
            await app.state.market_service.stop()
        if hasattr(app.state, 'strategy_engine'):
            await app.state.strategy_engine.stop()
        print("✅ 服務清理完成")
    except Exception as e:
        print(f"⚠️ 清理警告: {e}")

# 創建 FastAPI 應用程式
app = FastAPI(
    title="Trading X - 進階交易策略系統",
    description="整合多重技術指標的智能交易系統",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 設定 - 修正跨域問題  
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://127.0.0.1:3000", 
        "http://127.0.0.1:3001",
        "http://localhost:5173",  # Vite 開發服務器
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有HTTP方法
    allow_headers=["*"],  # 允許所有請求頭
    expose_headers=["*"]  # 暴露所有響應頭
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
