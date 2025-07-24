from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc
from typing import List, Optional

from app.core.database import get_db
from app.models.models import Strategy
from app.schemas.strategy import StrategyResponse, StrategyCreate, StrategyUpdate

router = APIRouter()

@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """獲取策略列表"""
    try:
        query = db.query(Strategy)
        if active_only:
            query = query.filter(Strategy.is_active == True)
        
        query = query.order_by(desc(Strategy.created_at))
        result = await db.execute(query)
        strategies = result.scalars().all()
        
        return [StrategyResponse.from_orm(strategy) for strategy in strategies]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取策略列表失敗: {str(e)}")

@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db)
):
    """獲取特定策略"""
    try:
        query = db.query(Strategy).filter(Strategy.id == strategy_id)
        result = await db.execute(query)
        strategy = result.scalar_one_or_none()
        
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")
        
        return StrategyResponse.from_orm(strategy)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取策略失敗: {str(e)}")

@router.post("/", response_model=StrategyResponse)
async def create_strategy(
    strategy: StrategyCreate,
    db: AsyncSession = Depends(get_db)
):
    """創建新策略"""
    try:
        new_strategy = Strategy(
            name=strategy.name,
            description=strategy.description,
            config=strategy.config,
            created_by=strategy.created_by
        )
        
        db.add(new_strategy)
        await db.commit()
        await db.refresh(new_strategy)
        
        return StrategyResponse.from_orm(new_strategy)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"創建策略失敗: {str(e)}")

@router.get("/presets/advanced")
async def get_advanced_strategies():
    """獲取進階策略配置預設"""
    strategies = {
        "multi_timeframe_trend": {
            "name": "多重時間框架趨勢策略",
            "description": "結合多個時間框架的趨勢分析，確保高勝率",
            "config": {
                "primary_timeframe": "1h",
                "confirmation_timeframes": ["4h", "1d"],
                "indicators": {
                    "ema_fast": 20,
                    "ema_slow": 50,
                    "macd": {"fast": 12, "slow": 26, "signal": 9},
                    "rsi": {"period": 14, "overbought": 70, "oversold": 30},
                    "atr_multiplier": 2.0
                },
                "entry_conditions": {
                    "trend_alignment": True,
                    "momentum_confirmation": True,
                    "volume_confirmation": True
                },
                "risk_management": {
                    "stop_loss_atr_multiplier": 2.0,
                    "take_profit_ratio": 3.0,
                    "max_risk_per_trade": 2.0
                }
            }
        },
        "mean_reversion_bb": {
            "name": "布林通道均值回歸策略",
            "description": "在超買超賣區域進行反向交易",
            "config": {
                "timeframe": "1h",
                "indicators": {
                    "bb_period": 20,
                    "bb_std": 2.0,
                    "rsi_period": 14,
                    "stoch_k": 14,
                    "stoch_d": 3
                },
                "entry_conditions": {
                    "bb_oversold": True,
                    "rsi_oversold": 30,
                    "stoch_oversold": 20
                },
                "exit_conditions": {
                    "bb_middle": True,
                    "rsi_neutral": 50
                }
            }
        },
        "breakout_momentum": {
            "name": "突破動量策略",
            "description": "捕捉重要支撐阻力位的突破",
            "config": {
                "timeframe": "1h",
                "indicators": {
                    "bb_period": 20,
                    "volume_sma": 20,
                    "atr_period": 14,
                    "pivot_points": True
                },
                "entry_conditions": {
                    "bb_squeeze": True,
                    "volume_spike": 1.5,
                    "momentum_confirm": True
                },
                "risk_management": {
                    "stop_loss_percentage": 2.0,
                    "trailing_stop": True,
                    "position_size": "kelly"
                }
            }
        },
        "ai_enhanced_signals": {
            "name": "AI增強信號策略",
            "description": "結合機器學習模型的信號增強",
            "config": {
                "base_strategy": "multi_timeframe_trend",
                "ai_models": {
                    "price_prediction": True,
                    "sentiment_analysis": True,
                    "pattern_recognition": True
                },
                "confidence_threshold": 0.75,
                "signal_filtering": {
                    "market_regime": True,
                    "volatility_filter": True,
                    "correlation_filter": True
                }
            }
        }
    }
    
    return {
        "strategies": strategies,
        "total_count": len(strategies),
        "categories": ["trend_following", "mean_reversion", "breakout", "ai_enhanced"]
    }
