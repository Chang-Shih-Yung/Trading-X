from fastapi import APIRouter
from app.api.v1.endpoints import signals, market_data, backtest, strategies, news, market_analysis, smart_timing, log_management, realtime_signals, notifications
from app.api.v1.endpoints.scalping_precision import router as scalping_router
from app.api.v1.endpoints.scalping_precision import router as scalping_precision_router  # 添加精準路由
from app.api.v1.endpoints.realtime_market import router as realtime_router
from app.api.v1.endpoints.enhanced_analysis import router as enhanced_analysis_router
from app.api.v1.event_coordination import router as event_coordination_router

api_router = APIRouter()

# API路由註冊
api_router.include_router(signals.router, prefix="/signals", tags=["signals"])
api_router.include_router(market_data.router, prefix="/market", tags=["market"])
api_router.include_router(realtime_router, prefix="/realtime", tags=["即時市場數據"])  # 修正路由前綴
api_router.include_router(realtime_signals.router, prefix="/realtime-signals", tags=["即時信號引擎"])  # 新增即時信號引擎
api_router.include_router(enhanced_analysis_router, prefix="/enhanced", tags=["增強技術分析"])
api_router.include_router(backtest.router, prefix="/backtest", tags=["backtest"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(scalping_router, prefix="/scalping", tags=["短線交易-精準篩選"])
api_router.include_router(scalping_precision_router, prefix="/scalping-precision", tags=["Phase 1A+1B+1C 完整系統"])  # 新增Phase 1C路由
api_router.include_router(market_analysis.router, prefix="/market-analysis", tags=["高級市場分析"])
api_router.include_router(smart_timing.router, prefix="/config", tags=["智能時間配置"])
api_router.include_router(log_management.router, prefix="/admin", tags=["系統管理-日誌"])  # 新增日誌管理
api_router.include_router(event_coordination_router, prefix="/event", tags=["事件協調引擎"])  # Phase 3 Week 3
api_router.include_router(notifications.router, prefix="/notifications", tags=["🎯 狙擊手通知系統"])  # 狙擊手 Email 通知
