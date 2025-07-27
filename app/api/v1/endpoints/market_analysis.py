"""
高級市場分析API端點
提供牛熊市判斷、動態止盈止損、短線歷史管理等功能
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pydantic import BaseModel

from app.core.database import get_db
from app.utils.time_utils import get_taiwan_now_naive
from app.services.market_analysis import (
    MarketAnalysisService, 
    MarketCondition, 
    DynamicStopLoss, 
    BreakoutSignal,
    SignalDirection,
    MarketTrend,
    MarketPhase
)
from app.services.short_term_history import (
    ShortTermHistoryService,
    HistoryStatistics,
    ShortTermSignalHistory,
    TradeResult
)
from app.services.market_data import MarketDataService

router = APIRouter()

# Pydantic 模型
class MarketAnalysisRequest(BaseModel):
    symbol: str
    timeframe: str = "1h"
    fear_greed_index: Optional[float] = None
    funding_rate: Optional[float] = None

class MarketAnalysisResponse(BaseModel):
    symbol: str
    market_condition: Dict[str, Any]
    analysis_timestamp: datetime
    bull_score: float
    bear_score: float
    trend: str
    phase: Optional[str]
    confidence: float
    key_factors: List[str]

class DynamicStopLossRequest(BaseModel):
    symbol: str
    entry_price: float
    signal_direction: str  # "LONG" or "SHORT"
    timeframe: str = "1h"

class DynamicStopLossResponse(BaseModel):
    symbol: str
    entry_price: float
    stop_loss_price: float
    take_profit_price: float
    stop_loss_pct: float
    take_profit_pct: float
    risk_reward_ratio: float
    reasoning: str
    market_condition_adjusted: bool
    atr_adjusted: bool

class BreakoutAnalysisResponse(BaseModel):
    symbol: str
    is_breakout: bool
    breakout_type: str
    strength: float
    volume_ratio: float
    price_momentum: float
    indicators_confirmation: Dict[str, bool]
    analysis_timestamp: datetime

class HistoryRequest(BaseModel):
    days: int = 30
    symbol: Optional[str] = None
    limit: int = 100
    offset: int = 0
    trade_result: Optional[str] = None

class RecalculateRequest(BaseModel):
    new_breakeven_threshold: float = 0.5

# 初始化服務
market_analyzer = MarketAnalysisService()
history_service = ShortTermHistoryService()
market_data_service = MarketDataService()

@router.post("/analyze-market", response_model=MarketAnalysisResponse)
async def analyze_market_condition(
    request: MarketAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    分析市場狀況（牛熊市判斷）
    """
    try:
        # 獲取價格數據
        price_data = await market_data_service.get_kline_data(
            symbol=request.symbol,
            interval=request.timeframe,
            limit=200
        )
        
        if price_data is None or price_data.empty:
            raise HTTPException(status_code=404, detail=f"無法獲取 {request.symbol} 的價格數據")
        
        # 進行市場分析
        market_condition = market_analyzer.analyze_market_condition(
            price_data=price_data,
            fear_greed_index=request.fear_greed_index,
            funding_rate=request.funding_rate
        )
        
        return MarketAnalysisResponse(
            symbol=request.symbol,
            market_condition={
                "trend": market_condition.trend.value,
                "phase": market_condition.phase.value if market_condition.phase else None,
                "bull_score": market_condition.bull_score,
                "bear_score": market_condition.bear_score,
                "confidence": market_condition.confidence,
                "key_factors": market_condition.key_factors
            },
            analysis_timestamp=market_condition.analysis_timestamp,
            bull_score=market_condition.bull_score,
            bear_score=market_condition.bear_score,
            trend=market_condition.trend.value,
            phase=market_condition.phase.value if market_condition.phase else None,
            confidence=market_condition.confidence,
            key_factors=market_condition.key_factors
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"市場分析失敗: {str(e)}")

@router.post("/calculate-stop-loss", response_model=DynamicStopLossResponse)
async def calculate_dynamic_stop_loss(
    request: DynamicStopLossRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    計算動態止盈止損
    """
    try:
        # 獲取價格數據
        price_data = await market_data_service.get_kline_data(
            symbol=request.symbol,
            interval=request.timeframe,
            limit=200
        )
        
        if price_data is None or price_data.empty:
            raise HTTPException(status_code=404, detail=f"無法獲取 {request.symbol} 的價格數據")
        
        # 分析市場狀況
        market_condition = market_analyzer.analyze_market_condition(price_data)
        
        # 計算動態止盈止損
        signal_direction = SignalDirection.LONG if request.signal_direction.upper() == "LONG" else SignalDirection.SHORT
        
        stop_loss = market_analyzer.calculate_dynamic_stop_loss(
            entry_price=request.entry_price,
            signal_direction=signal_direction,
            price_data=price_data,
            market_condition=market_condition,
            timeframe=request.timeframe
        )
        
        return DynamicStopLossResponse(
            symbol=request.symbol,
            entry_price=request.entry_price,
            stop_loss_price=stop_loss.stop_loss_price,
            take_profit_price=stop_loss.take_profit_price,
            stop_loss_pct=stop_loss.stop_loss_pct,
            take_profit_pct=stop_loss.take_profit_pct,
            risk_reward_ratio=stop_loss.risk_reward_ratio,
            reasoning=stop_loss.reasoning,
            market_condition_adjusted=stop_loss.market_condition_adjusted,
            atr_adjusted=stop_loss.atr_adjusted
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"動態止盈止損計算失敗: {str(e)}")

@router.get("/breakout-analysis/{symbol}", response_model=BreakoutAnalysisResponse)
async def analyze_breakout_signals(
    symbol: str,
    timeframe: str = Query("1h", description="時間框架"),
    db: AsyncSession = Depends(get_db)
):
    """
    分析突破信號
    """
    try:
        # 獲取價格數據
        price_data = await market_data_service.get_kline_data(
            symbol=symbol,
            interval=timeframe,
            limit=100
        )
        
        if price_data is None or price_data.empty:
            raise HTTPException(status_code=404, detail=f"無法獲取 {symbol} 的價格數據")
        
        # 檢測突破信號
        breakout_signal = market_analyzer.detect_breakout_signals(price_data)
        
        return BreakoutAnalysisResponse(
            symbol=symbol,
            is_breakout=breakout_signal.is_breakout,
            breakout_type=breakout_signal.breakout_type,
            strength=breakout_signal.strength,
            volume_ratio=breakout_signal.volume_ratio,
            price_momentum=breakout_signal.price_momentum,
            indicators_confirmation=breakout_signal.indicators_confirmation,
            analysis_timestamp=get_taiwan_now_naive()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"突破信號分析失敗: {str(e)}")

@router.post("/batch-market-analysis")
async def batch_market_analysis(
    symbols: List[str],
    timeframe: str = "1h",
    fear_greed_index: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    批量市場分析
    """
    try:
        results = []
        
        for symbol in symbols:
            try:
                # 獲取價格數據
                price_data = await market_data_service.get_kline_data(
                    symbol=symbol,
                    interval=timeframe,
                    limit=200
                )
                
                if price_data is None or price_data.empty:
                    continue
                
                # 進行市場分析
                market_condition = market_analyzer.analyze_market_condition(
                    price_data=price_data,
                    fear_greed_index=fear_greed_index
                )
                
                # 檢測突破信號
                breakout_signal = market_analyzer.detect_breakout_signals(price_data)
                
                result = {
                    "symbol": symbol,
                    "market_condition": {
                        "trend": market_condition.trend.value,
                        "phase": market_condition.phase.value if market_condition.phase else None,
                        "bull_score": market_condition.bull_score,
                        "bear_score": market_condition.bear_score,
                        "confidence": market_condition.confidence,
                        "key_factors": market_condition.key_factors[:3]  # 只返回前3個關鍵因素
                    },
                    "breakout_analysis": {
                        "is_breakout": breakout_signal.is_breakout,
                        "breakout_type": breakout_signal.breakout_type,
                        "strength": breakout_signal.strength,
                        "volume_ratio": breakout_signal.volume_ratio
                    },
                    "analysis_timestamp": get_taiwan_now_naive()
                }
                
                results.append(result)
                
            except Exception as e:
                # 跳過失敗的交易對，繼續處理其他的
                continue
        
        return {
            "total_analyzed": len(results),
            "analysis_results": results,
            "global_market_sentiment": _calculate_global_sentiment(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量市場分析失敗: {str(e)}")

@router.post("/process-expired-signals")
async def process_expired_signals(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    處理過期的短線信號
    """
    try:
        expired_count = await history_service.process_expired_signals(db)
        
        return {
            "success": True,
            "processed_count": expired_count,
            "message": f"成功處理 {expired_count} 個過期短線信號"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理過期信號失敗: {str(e)}")

@router.get("/history/statistics")
async def get_history_statistics(
    days: int = Query(30, description="統計天數"),
    symbol: Optional[str] = Query(None, description="特定交易對"),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取短線信號歷史統計
    """
    try:
        statistics = await history_service.get_history_statistics(
            db=db,
            days=days,
            symbol=symbol
        )
        
        return {
            "statistics": {
                "total_signals": statistics.total_signals,
                "win_count": statistics.win_count,
                "loss_count": statistics.loss_count,
                "breakeven_count": statistics.breakeven_count,
                "expired_count": statistics.expired_count,
                "win_rate": round(statistics.win_rate, 2),
                "avg_profit_pct": round(statistics.avg_profit_pct, 2),
                "avg_loss_pct": round(statistics.avg_loss_pct, 2),
                "avg_hold_time_minutes": round(statistics.avg_hold_time_minutes, 1),
                "best_performer": statistics.best_performer,
                "worst_performer": statistics.worst_performer
            },
            "performance_analysis": {
                "symbol_performance": statistics.symbol_performance,
                "strategy_performance": statistics.strategy_performance,
                "daily_performance": statistics.daily_performance
            },
            "query_params": {
                "days": days,
                "symbol": symbol,
                "analysis_timestamp": get_taiwan_now_naive()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取歷史統計失敗: {str(e)}")

@router.get("/history/records")
async def get_history_records(
    limit: int = Query(100, description="限制數量"),
    offset: int = Query(0, description="偏移量"),
    symbol: Optional[str] = Query(None, description="篩選交易對"),
    trade_result: Optional[str] = Query(None, description="篩選交易結果"),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取短線信號歷史記錄
    """
    try:
        history_records = await history_service.get_short_term_history(
            db=db,
            limit=limit,
            offset=offset,
            symbol=symbol,
            trade_result=trade_result
        )
        
        # 轉換為字典格式以便序列化
        records_data = []
        for record in history_records:
            # history_records 已經是字典格式
            if isinstance(record, dict):
                record_dict = record
            else:
                # 如果還是對象格式，轉換為字典
                record_dict = {
                    "id": record.id,
                    "symbol": record.symbol,
                    "signal_type": record.signal_type,
                    "entry_price": record.entry_price,
                    "current_price": getattr(record, 'current_price', None),
                    "stop_loss": record.stop_loss,
                    "take_profit": record.take_profit,
                    "confidence": record.confidence,
                    "created_at": record.created_at,
                    "expires_at": record.expires_at,
                    "archived_at": getattr(record, 'archived_at', record.expires_at),
                    "trade_result": getattr(record, 'trade_result', 'EXPIRED'),
                    "profit_loss_pct": getattr(record, 'profit_loss_pct', None),
                    "max_profit_pct": getattr(record, 'max_profit_pct', None),
                    "max_loss_pct": getattr(record, 'max_loss_pct', None),
                    "time_to_result": getattr(record, 'time_to_result', None),
                    "market_condition": getattr(record, 'market_condition', 'Unknown'),
                    "reasoning": record.reasoning,
                    "strategy_name": getattr(record, 'strategy_name', '短線策略')
                }
            records_data.append(record_dict)
        
        return {
            "records": records_data,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total_returned": len(records_data)
            },
            "filters": {
                "symbol": symbol,
                "trade_result": trade_result
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取歷史記錄失敗: {str(e)}")

@router.post("/history/recalculate")
async def recalculate_historical_results(
    request: RecalculateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    重新計算歷史記錄的交易結果
    """
    try:
        changes = await history_service.recalculate_historical_results(
            db=db,
            new_breakeven_threshold=request.new_breakeven_threshold
        )
        
        return {
            "success": True,
            "new_breakeven_threshold": request.new_breakeven_threshold,
            "changes": changes,
            "message": f"成功重算 {changes.get('total_processed', 0)} 筆歷史記錄"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重算歷史結果失敗: {str(e)}")

@router.get("/market-sentiment/{symbol}")
async def get_market_sentiment(
    symbol: str,
    db: AsyncSession = Depends(get_db)
):
    """
    獲取特定交易對的綜合市場情緒
    """
    try:
        # 獲取價格數據
        price_data = await market_data_service.get_kline_data(
            symbol=symbol,
            interval="1h",
            limit=200
        )
        
        if price_data is None or price_data.empty:
            raise HTTPException(status_code=404, detail=f"無法獲取 {symbol} 的價格數據")
        
        # 進行綜合分析
        market_condition = market_analyzer.analyze_market_condition(price_data)
        breakout_signal = market_analyzer.detect_breakout_signals(price_data)
        
        # 計算綜合情緒分數
        sentiment_score = _calculate_sentiment_score(market_condition, breakout_signal)
        
        return {
            "symbol": symbol,
            "sentiment_score": sentiment_score,
            "sentiment_label": _get_sentiment_label(sentiment_score),
            "market_condition": {
                "trend": market_condition.trend.value,
                "phase": market_condition.phase.value if market_condition.phase else None,
                "bull_score": market_condition.bull_score,
                "bear_score": market_condition.bear_score,
                "confidence": market_condition.confidence
            },
            "breakout_signals": {
                "is_breakout": breakout_signal.is_breakout,
                "strength": breakout_signal.strength,
                "type": breakout_signal.breakout_type
            },
            "recommendations": _generate_recommendations(market_condition, breakout_signal),
            "analysis_timestamp": get_taiwan_now_naive()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"市場情緒分析失敗: {str(e)}")

# 輔助函數
def _calculate_global_sentiment(results: List[Dict]) -> Dict[str, Any]:
    """計算全域市場情緒"""
    if not results:
        return {"sentiment": "neutral", "confidence": 0}
    
    bull_scores = [r["market_condition"]["bull_score"] for r in results]
    bear_scores = [r["market_condition"]["bear_score"] for r in results]
    breakout_count = sum(1 for r in results if r["breakout_analysis"]["is_breakout"])
    
    avg_bull_score = sum(bull_scores) / len(bull_scores)
    avg_bear_score = sum(bear_scores) / len(bear_scores)
    breakout_ratio = breakout_count / len(results)
    
    if avg_bull_score > avg_bear_score + 2:
        sentiment = "bullish"
    elif avg_bear_score > avg_bull_score + 2:
        sentiment = "bearish"
    else:
        sentiment = "neutral"
    
    confidence = min(abs(avg_bull_score - avg_bear_score) / 10, 0.95)
    
    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "avg_bull_score": avg_bull_score,
        "avg_bear_score": avg_bear_score,
        "breakout_ratio": breakout_ratio,
        "analyzed_symbols": len(results)
    }

def _calculate_sentiment_score(market_condition: MarketCondition, breakout_signal: BreakoutSignal) -> float:
    """計算情緒分數 (-1 到 1)"""
    # 基於牛熊分數的基礎分數
    base_score = (market_condition.bull_score - market_condition.bear_score) / 10
    
    # 突破信號調整
    if breakout_signal.is_breakout:
        if breakout_signal.strength > 0.7:
            base_score += 0.2
        elif breakout_signal.strength > 0.4:
            base_score += 0.1
    
    # 信心度加權
    weighted_score = base_score * market_condition.confidence
    
    return max(-1, min(1, weighted_score))

def _get_sentiment_label(score: float) -> str:
    """獲取情緒標籤"""
    if score > 0.6:
        return "極度樂觀"
    elif score > 0.3:
        return "樂觀"
    elif score > 0.1:
        return "偏樂觀"
    elif score > -0.1:
        return "中性"
    elif score > -0.3:
        return "偏悲觀"
    elif score > -0.6:
        return "悲觀"
    else:
        return "極度悲觀"

def _generate_recommendations(market_condition: MarketCondition, breakout_signal: BreakoutSignal) -> List[str]:
    """生成投資建議"""
    recommendations = []
    
    if market_condition.trend == MarketTrend.BULL:
        if market_condition.phase == MarketPhase.MAIN_BULL:
            recommendations.append("主升段，建議順勢做多，可適度放大倉位")
        elif market_condition.phase == MarketPhase.HIGH_VOLATILITY:
            recommendations.append("高位震盪，建議短線操作，快進快出")
        elif market_condition.phase == MarketPhase.LATE_BULL:
            recommendations.append("牛市末期，風險較高，建議減倉或觀望")
        else:
            recommendations.append("牛市初期，可逐步建倉")
    elif market_condition.trend == MarketTrend.BEAR:
        recommendations.append("熊市環境，建議以做空為主或空倉觀望")
    else:
        recommendations.append("震盪市場，建議區間操作或等待明確趨勢")
    
    if breakout_signal.is_breakout and breakout_signal.strength > 0.6:
        recommendations.append(f"檢測到{breakout_signal.breakout_type}突破，可考慮順勢操作")
    
    if market_condition.confidence < 0.5:
        recommendations.append("市場信號不明確，建議謹慎操作，控制倉位")
    
    return recommendations
