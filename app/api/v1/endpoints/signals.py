from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, and_, select, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.models import TradingSignal
from app.services.strategy_engine import StrategyEngine
from app.schemas.signals import SignalResponse, SignalCreate, SignalFilter, AnalyzeRequest

router = APIRouter()

@router.get("/", response_model=List[SignalResponse])
async def get_signals(
    symbol: Optional[str] = Query(None, description="交易對篩選"),
    timeframe: Optional[str] = Query(None, description="時間框架篩選"),
    signal_type: Optional[str] = Query(None, description="信號類型篩選"),
    min_confidence: Optional[float] = Query(0.7, description="最低置信度"),
    limit: int = Query(50, description="返回數量限制"),
    db: AsyncSession = Depends(get_db)
):
    """獲取交易信號列表"""
    try:
        stmt = select(TradingSignal).filter(
            TradingSignal.status == "ACTIVE",
            TradingSignal.confidence >= min_confidence
        )
        
        if symbol:
            stmt = stmt.filter(TradingSignal.symbol == symbol)
        if timeframe:
            stmt = stmt.filter(TradingSignal.timeframe == timeframe)
        if signal_type:
            stmt = stmt.filter(TradingSignal.signal_type == signal_type)
        
        stmt = stmt.order_by(desc(TradingSignal.created_at)).limit(limit)
        
        result = await db.execute(stmt)
        signals = result.scalars().all()
        
        return [SignalResponse.from_orm(signal) for signal in signals]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取信號失敗: {str(e)}")

@router.get("/latest", response_model=List[SignalResponse])
async def get_latest_signals(
    hours: int = Query(24, description="過去幾小時的信號"),
    db: AsyncSession = Depends(get_db)
):
    """獲取最新信號"""
    try:
        since_time = datetime.utcnow() - timedelta(hours=hours)
        
        stmt = select(TradingSignal).filter(
            and_(
                TradingSignal.created_at >= since_time,
                TradingSignal.status == "ACTIVE",
                TradingSignal.confidence >= 0.7
            )
        ).order_by(desc(TradingSignal.signal_strength)).limit(20)
        
        result = await db.execute(stmt)
        signals = result.scalars().all()
        
        return [SignalResponse.from_orm(signal) for signal in signals]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取最新信號失敗: {str(e)}")

@router.get("/top", response_model=List[SignalResponse])
async def get_top_signals(
    limit: int = Query(10, description="返回數量"),
    db: AsyncSession = Depends(get_db)
):
    """獲取置信度最高的信號"""
    try:
        stmt = select(TradingSignal).filter(
            TradingSignal.status == "ACTIVE"
        ).order_by(
            desc(TradingSignal.confidence),
            desc(TradingSignal.risk_reward_ratio)
        ).limit(limit)
        
        result = await db.execute(stmt)
        signals = result.scalars().all()
        
        return [SignalResponse.from_orm(signal) for signal in signals]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取頂級信號失敗: {str(e)}")

@router.get("/{signal_id}", response_model=SignalResponse)
async def get_signal(
    signal_id: int,
    db: AsyncSession = Depends(get_db)
):
    """獲取特定信號詳情"""
    try:
        stmt = select(TradingSignal).filter(TradingSignal.id == signal_id)
        result = await db.execute(stmt)
        signal = result.scalar_one_or_none()
        
        if not signal:
            raise HTTPException(status_code=404, detail="信號不存在")
        
        return SignalResponse.from_orm(signal)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取信號失敗: {str(e)}")

@router.post("/analyze")
async def analyze_symbol(
    request: AnalyzeRequest
):
    """手動分析特定交易對"""
    try:
        strategy_engine = StrategyEngine()
        signal = await strategy_engine.analyze_symbol(request.symbol, request.timeframe)
        
        if signal:
            return {
                "success": True,
                "message": f"分析完成: {request.symbol} {request.timeframe}",
                "signal": {
                    "signal_type": signal.signal_type.value,
                    "confidence": signal.confidence,
                    "signal_strength": signal.signal_strength,
                    "entry_price": signal.entry_price,
                    "stop_loss": signal.stop_loss,
                    "take_profit": signal.take_profit,
                    "risk_reward_ratio": signal.risk_reward_ratio,
                    "reasoning": signal.reasoning
                }
            }
        else:
            return {
                "success": True,
                "message": f"未發現{request.symbol} {request.timeframe}的交易機會",
                "signal": None
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失敗: {str(e)}")

@router.get("/performance/summary")
async def get_signal_performance(
    days: int = Query(30, description="統計天數"),
    db: AsyncSession = Depends(get_db)
):
    """獲取信號表現統計"""
    try:
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # 統計信號數量
        total_stmt = select(TradingSignal).filter(
            TradingSignal.created_at >= since_date
        )
        total_result = await db.execute(total_stmt)
        total_signals = len(total_result.scalars().all())
        
        # 按信號類型統計
        long_stmt = select(TradingSignal).filter(
            and_(
                TradingSignal.created_at >= since_date,
                TradingSignal.signal_type == "LONG"
            )
        )
        long_result = await db.execute(long_stmt)
        long_signals = len(long_result.scalars().all())
        
        short_stmt = select(TradingSignal).filter(
            and_(
                TradingSignal.created_at >= since_date,
                TradingSignal.signal_type == "SHORT"
            )
        )
        short_result = await db.execute(short_stmt)
        short_signals = len(short_result.scalars().all())
        
        # 平均置信度和風險回報比
        all_signals_stmt = select(TradingSignal).filter(
            TradingSignal.created_at >= since_date
        )
        all_signals_result = await db.execute(all_signals_stmt)
        all_signals = all_signals_result.scalars().all()
        
        avg_confidence = sum(s.confidence for s in all_signals) / len(all_signals) if all_signals else 0
        avg_rr_ratio = sum(s.risk_reward_ratio for s in all_signals) / len(all_signals) if all_signals else 0
        
        return {
            "period_days": days,
            "total_signals": total_signals,
            "long_signals": long_signals,
            "short_signals": short_signals,
            "average_confidence": round(avg_confidence, 3),
            "average_risk_reward_ratio": round(avg_rr_ratio, 2),
            "signals_per_day": round(total_signals / days, 1)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取表現統計失敗: {str(e)}")
