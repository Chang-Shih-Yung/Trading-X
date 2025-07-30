"""
即時信號引擎 API 端點
提供啟動、停止、配置和監控信號引擎的介面
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import asyncio
import logging

from app.services.realtime_signal_engine import realtime_signal_engine, TradingSignalAlert
from app.api.v1.endpoints.realtime_market import manager
from app.utils.time_utils import get_taiwan_now_naive

router = APIRouter()
logger = logging.getLogger(__name__)

# 請求模型
class SignalEngineConfig(BaseModel):
    """信號引擎配置"""
    monitored_symbols: Optional[List[str]] = None
    monitored_timeframes: Optional[List[str]] = None
    confidence_threshold: Optional[float] = None
    signal_cooldown: Optional[int] = None
    min_history_points: Optional[int] = None

class SignalAlert(BaseModel):
    """信號警報模型"""
    symbol: str
    signal_type: str
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    indicators_used: List[str]
    reasoning: str
    timeframe: str
    urgency: str
    timestamp: str

# 信號廣播回調函數
async def websocket_signal_callback(signal: TradingSignalAlert):
    """WebSocket 信號廣播回調"""
    try:
        await manager.broadcast_trading_signal(signal)
    except Exception as e:
        logger.error(f"WebSocket 信號廣播失敗: {e}")

# 註冊回調函數
realtime_signal_engine.add_signal_callback(websocket_signal_callback)

@router.post("/start")
async def start_signal_engine(background_tasks: BackgroundTasks):
    """啟動即時信號引擎"""
    try:
        if realtime_signal_engine.running:
            return {
                "success": False,
                "message": "信號引擎已在運行中",
                "status": "already_running"
            }
        
        # 初始化引擎
        from main import app
        market_service = app.state.market_service
        await realtime_signal_engine.initialize(market_service)
        
        # 在背景啟動
        background_tasks.add_task(realtime_signal_engine.start)
        
        return {
            "success": True,
            "message": "即時信號引擎啟動成功",
            "status": "started",
            "config": {
                "monitored_symbols": realtime_signal_engine.monitored_symbols,
                "monitored_timeframes": realtime_signal_engine.monitored_timeframes,
                "confidence_threshold": realtime_signal_engine.confidence_threshold,
                "min_history_points": realtime_signal_engine.min_history_points
            },
            "timestamp": get_taiwan_now_naive().isoformat()
        }
        
    except Exception as e:
        logger.error(f"啟動信號引擎失敗: {e}")
        raise HTTPException(status_code=500, detail=f"啟動失敗: {str(e)}")

@router.post("/stop")
async def stop_signal_engine():
    """停止即時信號引擎"""
    try:
        if not realtime_signal_engine.running:
            return {
                "success": False,
                "message": "信號引擎未在運行",
                "status": "not_running"
            }
        
        await realtime_signal_engine.stop()
        
        return {
            "success": True,
            "message": "即時信號引擎已停止",
            "status": "stopped",
            "timestamp": get_taiwan_now_naive().isoformat()
        }
        
    except Exception as e:
        logger.error(f"停止信號引擎失敗: {e}")
        raise HTTPException(status_code=500, detail=f"停止失敗: {str(e)}")

@router.get("/status")
async def get_signal_engine_status():
    """獲取信號引擎狀態"""
    try:
        stats = realtime_signal_engine.get_statistics()
        
        return {
            "success": True,
            "data": {
                "running": stats['running'],
                "monitored_symbols": stats['monitored_symbols'],
                "monitored_timeframes": stats['monitored_timeframes'],
                "total_signals": stats['total_signals_generated'],
                "signals_24h": stats['signals_last_24h'],
                "average_confidence": round(stats['average_confidence'], 3),
                "websocket_connections": len(manager.active_connections),
                "last_signals": stats['last_signals']
            },
            "timestamp": get_taiwan_now_naive().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取引擎狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取狀態失敗: {str(e)}")

@router.post("/config")
async def update_signal_engine_config(config: SignalEngineConfig):
    """更新信號引擎配置"""
    try:
        updated_fields = []
        
        if config.monitored_symbols is not None:
            realtime_signal_engine.monitored_symbols = config.monitored_symbols
            updated_fields.append("monitored_symbols")
        
        if config.monitored_timeframes is not None:
            realtime_signal_engine.monitored_timeframes = config.monitored_timeframes
            updated_fields.append("monitored_timeframes")
        
        if config.confidence_threshold is not None:
            if 0.0 <= config.confidence_threshold <= 1.0:
                realtime_signal_engine.confidence_threshold = config.confidence_threshold
                updated_fields.append("confidence_threshold")
            else:
                raise ValueError("信心度閾值必須在 0.0 - 1.0 之間")
        
        if config.signal_cooldown is not None:
            if config.signal_cooldown >= 0:
                realtime_signal_engine.signal_cooldown = config.signal_cooldown
                updated_fields.append("signal_cooldown")
            else:
                raise ValueError("信號冷卻時間必須 >= 0")
        
        if config.min_history_points is not None:
            if config.min_history_points >= 50:
                realtime_signal_engine.min_history_points = config.min_history_points
                updated_fields.append("min_history_points")
            else:
                raise ValueError("最少歷史數據點必須 >= 50")
        
        return {
            "success": True,
            "message": f"配置更新成功: {', '.join(updated_fields)}",
            "updated_fields": updated_fields,
            "current_config": {
                "monitored_symbols": realtime_signal_engine.monitored_symbols,
                "monitored_timeframes": realtime_signal_engine.monitored_timeframes,
                "confidence_threshold": realtime_signal_engine.confidence_threshold,
                "signal_cooldown": realtime_signal_engine.signal_cooldown,
                "min_history_points": realtime_signal_engine.min_history_points
            },
            "timestamp": get_taiwan_now_naive().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新配置失敗: {e}")
        raise HTTPException(status_code=500, detail=f"更新配置失敗: {str(e)}")

@router.get("/signals/recent")
async def get_recent_signals(hours: int = 24):
    """獲取最近的信號"""
    try:
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_signals = [
            SignalAlert(
                symbol=signal.symbol,
                signal_type=signal.signal_type,
                confidence=signal.confidence,
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                risk_reward_ratio=signal.risk_reward_ratio,
                indicators_used=signal.indicators_used,
                reasoning=signal.reasoning,
                timeframe=signal.timeframe,
                urgency=signal.urgency,
                timestamp=signal.timestamp.isoformat()
            )
            for signal in realtime_signal_engine.signal_history
            if signal.timestamp > cutoff_time
        ]
        
        return {
            "success": True,
            "data": {
                "signals": recent_signals,
                "count": len(recent_signals),
                "time_range_hours": hours
            },
            "timestamp": get_taiwan_now_naive().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取最近信號失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取信號失敗: {str(e)}")

@router.post("/signals/test")
async def generate_test_signal():
    """生成測試信號（用於測試 WebSocket 廣播）"""
    try:
        from datetime import datetime
        
        test_signal = TradingSignalAlert(
            symbol="BTCUSDT",
            signal_type="BUY",
            confidence=0.85,
            entry_price=95000.0,
            stop_loss=92000.0,
            take_profit=98000.0,
            risk_reward_ratio=1.0,
            indicators_used=["RSI", "MACD", "K線形態"],
            reasoning="測試信號 - RSI超賣反彈 + MACD金叉",
            timeframe="1h",
            timestamp=datetime.now(),
            urgency="high"
        )
        
        # 觸發廣播
        await websocket_signal_callback(test_signal)
        
        return {
            "success": True,
            "message": "測試信號已生成並廣播",
            "signal": SignalAlert(
                symbol=test_signal.symbol,
                signal_type=test_signal.signal_type,
                confidence=test_signal.confidence,
                entry_price=test_signal.entry_price,
                stop_loss=test_signal.stop_loss,
                take_profit=test_signal.take_profit,
                risk_reward_ratio=test_signal.risk_reward_ratio,
                indicators_used=test_signal.indicators_used,
                reasoning=test_signal.reasoning,
                timeframe=test_signal.timeframe,
                urgency=test_signal.urgency,
                timestamp=test_signal.timestamp.isoformat()
            ),
            "timestamp": get_taiwan_now_naive().isoformat()
        }
        
    except Exception as e:
        logger.error(f"生成測試信號失敗: {e}")
        raise HTTPException(status_code=500, detail=f"生成測試信號失敗: {str(e)}")

@router.get("/health")
async def health_check():
    """健康檢查"""
    try:
        stats = realtime_signal_engine.get_statistics()
        
        health_status = {
            "service": "realtime_signal_engine",
            "status": "healthy" if stats['running'] else "stopped",
            "uptime_indicators": {
                "engine_running": stats['running'],
                "signals_generated": stats['total_signals_generated'] > 0,
                "websocket_connections": len(manager.active_connections) >= 0,
                "monitored_symbols": len(stats['monitored_symbols']) > 0
            },
            "metrics": {
                "signals_24h": stats['signals_last_24h'],
                "average_confidence": stats['average_confidence'],
                "active_connections": len(manager.active_connections),
                "monitored_pairs": len(stats['monitored_symbols'])
            }
        }
        
        return {
            "success": True,
            "data": health_status,
            "timestamp": get_taiwan_now_naive().isoformat()
        }
        
    except Exception as e:
        logger.error(f"健康檢查失敗: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": get_taiwan_now_naive().isoformat()
        }
