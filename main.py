from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import os
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, create_tables
from app.services.market_data import MarketDataService
from app.services.strategy_engine import StrategyEngine
from app.services.realtime_signal_engine import RealtimeSignalEngine
from app.utils.log_manager import start_log_management, stop_log_management
from app.utils.realtime_log_filter import setup_realtime_logging, disable_noisy_loggers

@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理 - 整合即時數據服務"""
    try:
        # 設置實時交易策略日誌過濾器
        setup_realtime_logging()
        disable_noisy_loggers()
        
        # 啟動時初始化數據庫
        await create_tables()
        print("✅ 數據庫初始化完成")
        
        # 創建服務實例
        market_service = MarketDataService()
        strategy_engine = StrategyEngine()
        realtime_signal_engine = RealtimeSignalEngine()
        
        # 儲存服務實例到應用程式狀態
        app.state.market_service = market_service
        app.state.strategy_engine = strategy_engine
        app.state.realtime_signal_engine = realtime_signal_engine
        
        print("✅ 服務實例創建完成")
        
        # 啟動即時數據服務（在背景執行）
        try:
            # 主要交易對
            symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT', 'DOGEUSDT']
            intervals = ['1m', '5m', '15m', '1h']
            
            # 在背景啟動即時數據收集
            asyncio.create_task(market_service.start_real_time_data(symbols, intervals))
            print(f"✅ 即時數據服務已啟動 - WebSocket模式: {market_service.websocket_enabled}")
            print(f"   監控代號: {symbols}")
            print(f"   時間間隔: {intervals}")
            
            # 🚀 啟動實時信號引擎 - 真正的 pandas-ta 分析
            realtime_signal_engine.monitored_symbols = symbols
            
            # 初始化實時信號引擎並傳入 market_service
            await realtime_signal_engine.initialize(market_service)
            
            # 啟動實時信號引擎
            asyncio.create_task(realtime_signal_engine.start())
            print("🎯 實時信號引擎已啟動 - WebSocket → pandas-ta → 信號生成流程運行中")
            
            # 🔧 設置Gmail通知（可選）
            try:
                # 優先使用 settings 中的配置
                gmail_sender = settings.GMAIL_SENDER
                gmail_password = settings.GMAIL_APP_PASSWORD
                gmail_recipient = settings.GMAIL_RECIPIENT or gmail_sender
                
                # 只有當設定不為空時才啟用Gmail通知
                if gmail_sender and gmail_password:
                    realtime_signal_engine.setup_gmail_notification(
                        sender_email=gmail_sender,
                        sender_password=gmail_password,
                        recipient_email=gmail_recipient
                    )
                    print(f"📧 Gmail通知已設置: {gmail_sender} → {gmail_recipient}")
                    
                    # 只在需要時才進行測試（通過環境變數控制）
                    test_on_startup = os.getenv('GMAIL_TEST_ON_STARTUP', 'false').lower() == 'true'
                    if test_on_startup:
                        test_result = await realtime_signal_engine.test_gmail_notification()
                        if test_result:
                            print("✅ Gmail通知測試成功")
                        else:
                            print("⚠️ Gmail通知測試失敗")
                    else:
                        print("📧 Gmail通知已準備就緒（跳過啟動測試）")
                        print("   提示: 設置 GMAIL_TEST_ON_STARTUP=true 來啟用啟動時測試")
                else:
                    print("ℹ️ Gmail設定未配置，跳過Gmail通知功能")
                    print("   提示: 在 .env 文件中設置 GMAIL_SENDER, GMAIL_APP_PASSWORD, GMAIL_RECIPIENT 來啟用Gmail通知")
                    
            except Exception as e:
                print(f"⚠️ Gmail通知設置失敗: {e}")
                print("   Gmail通知功能已禁用，其他功能正常運行")
            
        except Exception as e:
            print(f"⚠️ 即時數據服務啟動警告: {e}")
            # 即使即時數據失敗也繼續運行基本服務
        
        # 啟動WebSocket廣播任務
        try:
            from app.api.v1.endpoints.realtime_market import start_broadcast_task
            start_broadcast_task()
            print("✅ WebSocket廣播任務已啟動")
        except Exception as e:
            print(f"⚠️ WebSocket廣播任務啟動警告: {e}")
        
        # 啟動日誌管理系統
        try:
            await start_log_management()
            print("✅ 日誌管理系統已啟動 - 每小時自動清理")
        except Exception as e:
            print(f"⚠️ 日誌管理系統啟動警告: {e}")
        
    except Exception as e:
        print(f"⚠️ 初始化警告: {e}")
        # 即使出錯也繼續啟動，避免服務無法啟動
    
    yield
    
    # 關閉時清理
    try:
        # 停止日誌管理
        await stop_log_management()
        print("✅ 日誌管理系統已停止")
        
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
