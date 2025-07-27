from fastapi import APIRouter
from app.api.v1.endpoints import signals, market_data, backtest, strategies, news, scalping, market_analysis, smart_timing

api_router = APIRouter()

api_router.include_router(signals.router, prefix="/signals", tags=["signals"])
api_router.include_router(market_data.router, prefix="/market", tags=["market"])
api_router.include_router(backtest.router, prefix="/backtest", tags=["backtest"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(scalping.router, prefix="/scalping", tags=["短線交易"])
api_router.include_router(market_analysis.router, prefix="/market-analysis", tags=["高級市場分析"])
api_router.include_router(smart_timing.router, prefix="/config", tags=["智能時間配置"])
