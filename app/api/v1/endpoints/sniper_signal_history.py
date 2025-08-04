# 🎯 狙擊手信號歷史管理 - API 端點

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.services.sniper_signal_history_service import (
    sniper_signal_tracker,
    sniper_signal_analyzer
)
from app.models.sniper_signal_history import (
    SniperSignalDetails,
    SniperSignalSummary,
    SignalStatus,
    SignalQuality,
    TradingTimeframe
)
from app.utils.timezone_utils import get_taiwan_now, ensure_taiwan_timezone
from app.core.database import db_manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ==================== Pydantic 模型 ====================

class SignalHistoryQuery(BaseModel):
    """信號歷史查詢參數"""
    symbol: Optional[str] = None
    timeframe: Optional[TradingTimeframe] = None
    status: Optional[SignalStatus] = None
    quality: Optional[SignalQuality] = None
    days: int = 7
    limit: int = 100

class PerformanceMetricsQuery(BaseModel):
    """性能指標查詢參數"""
    symbol: Optional[str] = None
    timeframe: Optional[TradingTimeframe] = None
    days: int = 30

# ==================== API 端點 ====================

@router.get("/history/signals")
async def get_signal_history(
    symbol: Optional[str] = Query(None, description="交易對篩選"),
    timeframe: Optional[str] = Query(None, description="時間框架篩選"),
    status: Optional[str] = Query(None, description="狀態篩選"),
    quality: Optional[str] = Query(None, description="品質篩選"),
    days: int = Query(7, description="查詢天數"),
    limit: int = Query(100, description="返回數量限制"),
    offset: int = Query(0, description="分頁偏移")
):
    """
    📜 獲取狙擊手信號歷史記錄
    
    支持多維度篩選和分頁查詢
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        session = await db_manager.create_session()
        try:
            from sqlalchemy import select, and_
            
            # 🎯 與回測系統一致：只顯示包含完整Phase數據的信號
            query = select(SniperSignalDetails).where(
                and_(
                    SniperSignalDetails.created_at >= start_date,
                    # 確保有完整的Phase數據（與回測系統篩選條件一致）
                    SniperSignalDetails.signal_quality.isnot(None),
                    SniperSignalDetails.market_regime.isnot(None),
                    SniperSignalDetails.layer_one_time.isnot(None),
                    SniperSignalDetails.layer_two_time.isnot(None)
                )
            )
            
            # 應用篩選條件
            if symbol:
                query = query.where(SniperSignalDetails.symbol == symbol.upper())
            if timeframe:
                try:
                    tf_enum = TradingTimeframe(timeframe.upper())
                    query = query.where(SniperSignalDetails.timeframe == tf_enum)
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid timeframe: {timeframe}")
            if status:
                try:
                    status_enum = SignalStatus(status.upper())
                    query = query.where(SniperSignalDetails.status == status_enum)
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
            if quality:
                try:
                    quality_enum = SignalQuality(quality.upper())
                    query = query.filter(SniperSignalDetails.signal_quality == quality_enum)
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid quality: {quality}")
            
            # 排序和分頁
            query = query.order_by(SniperSignalDetails.created_at.desc())
            
            result = await session.execute(query.offset(offset).limit(limit))
            signals = result.scalars().all()
            
            # 獲取總數（與查詢條件一致）
            count_query = select(SniperSignalDetails).where(
                and_(
                    SniperSignalDetails.created_at >= start_date,
                    # 🎯 與回測系統一致：只計算完整Phase數據的信號
                    SniperSignalDetails.signal_quality.isnot(None),
                    SniperSignalDetails.market_regime.isnot(None),
                    SniperSignalDetails.layer_one_time.isnot(None),
                    SniperSignalDetails.layer_two_time.isnot(None)
                )
            )
            if symbol:
                count_query = count_query.where(SniperSignalDetails.symbol == symbol.upper())
            if timeframe:
                tf_enum = TradingTimeframe(timeframe.upper())
                count_query = count_query.where(SniperSignalDetails.timeframe == tf_enum)
            if status:
                status_enum = SignalStatus(status.upper())
                count_query = count_query.where(SniperSignalDetails.status == status_enum)
            
            from sqlalchemy import func
            count_result = await session.execute(select(func.count()).select_from(count_query.subquery()))
            total_count = count_result.scalar()
            
            # 轉換為API響應格式
            signal_list = []
            for signal in signals:
                signal_dict = {
                    'signal_id': signal.signal_id,
                    'symbol': signal.symbol,
                    'signal_type': signal.signal_type,
                    'entry_price': signal.entry_price,
                    'stop_loss_price': signal.stop_loss_price,
                    'take_profit_price': signal.take_profit_price,
                    'signal_strength': signal.signal_strength,
                    'confluence_count': signal.confluence_count,
                    'signal_quality': signal.signal_quality.value,
                    'timeframe': signal.timeframe.value,
                    'risk_reward_ratio': signal.risk_reward_ratio,
                    'status': signal.status.value,
                    'created_at': ensure_taiwan_timezone(signal.created_at).isoformat(),
                    'expires_at': ensure_taiwan_timezone(signal.expires_at).isoformat(),
                    'pnl_percentage': signal.pnl_percentage,
                    'result_price': signal.result_price,
                    'result_time': ensure_taiwan_timezone(signal.result_time).isoformat() if signal.result_time else None,
                    'reasoning': signal.reasoning
                }
                signal_list.append(signal_dict)
            
            return {
                'success': True,
                'data': {
                    'signals': signal_list,
                    'pagination': {
                        'total_count': total_count,
                        'current_page': (offset // limit) + 1,
                        'page_size': limit,
                        'total_pages': (total_count + limit - 1) // limit
                    },
                    'filters_applied': {
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'status': status,
                        'quality': quality,
                        'days': days
                    }
                }
            }
        finally:
            await session.close()
            
    except Exception as e:
        logger.error(f"❌ 信號歷史查詢失敗: {e}")
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")

@router.get("/history/active-signals")
async def get_active_signals():
    """
    🔥 獲取所有當前活躍的信號 - 前端優化格式
    
    用於監控當前正在進行的交易信號，返回前端需要的完整數據格式
    """
    try:
        # 直接從資料庫獲取活躍信號，不經過monitor_active_signals處理
        from app.models.sniper_signal_history import SniperSignalDetails, SignalStatus
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import select, and_
        from app.utils.timezone_utils import get_taiwan_now
        
        async with AsyncSessionLocal() as session:
            # 查詢所有活躍信號
            query = select(SniperSignalDetails).where(
                and_(
                    SniperSignalDetails.status == SignalStatus.ACTIVE,
                    SniperSignalDetails.expires_at > get_taiwan_now()
                )
            ).order_by(SniperSignalDetails.created_at.desc()).limit(20)
            
            result = await session.execute(query)
            db_signals = result.scalars().all()
            
            # 轉換為前端需要的格式
            active_signals = []
            for signal in db_signals:
                signal_data = {
                    'signal_id': signal.signal_id,
                    'symbol': signal.symbol,
                    'signal_type': signal.signal_type,
                    'entry_price': float(signal.entry_price),
                    'stop_loss_price': float(signal.stop_loss_price), 
                    'take_profit_price': float(signal.take_profit_price),
                    'confidence': float(signal.signal_strength),  # 🎯 前端需要的confidence字段
                    'signal_strength': float(signal.signal_strength),
                    'risk_reward_ratio': float(signal.risk_reward_ratio),
                    'timeframe': signal.timeframe.value if hasattr(signal.timeframe, 'value') else str(signal.timeframe),
                    'signal_quality': signal.signal_quality.value if hasattr(signal.signal_quality, 'value') else str(signal.signal_quality),
                    'market_regime': signal.market_regime,
                    'created_at': signal.created_at.isoformat(),
                    'expires_at': signal.expires_at.isoformat(),
                    'reasoning': signal.reasoning,
                    'email_status': signal.email_status.value if hasattr(signal.email_status, 'value') else str(signal.email_status),
                    'pass_rate': float(signal.pass_rate or 0),
                    'confluence_count': signal.confluence_count,
                    'layer_one_time': float(signal.layer_one_time or 0),
                    'layer_two_time': float(signal.layer_two_time or 0),
                    'action': 'active'  # 標記為活躍信號
                }
                active_signals.append(signal_data)
        
        logger.info(f"📊 直接從資料庫獲取 {len(active_signals)} 個活躍信號")
        
        return {
            'success': True,
            'data': {
                'active_signals': active_signals,
                'total_active': len(active_signals),
                'last_check': get_taiwan_now().isoformat(),
                'data_source': 'database_direct'  # 標記數據來源
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 活躍信號查詢失敗: {e}")
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")

@router.get("/history/statistics")
async def get_overall_statistics():
    """
    📊 獲取整體統計數據
    
    提供系統整體的信號統計概覽
    """
    try:
        async with db_manager.create_session() as session:
            # 總信號數
            total_signals = await session.query(SniperSignalDetails).count()
            
            # 各狀態統計
            status_stats = {}
            for status in SignalStatus:
                count = await session.query(SniperSignalDetails).filter(
                    SniperSignalDetails.status == status
                ).count()
                status_stats[status.value] = count
            
            # 各品質統計
            quality_stats = {}
            for quality in SignalQuality:
                count = await session.query(SniperSignalDetails).filter(
                    SniperSignalDetails.signal_quality == quality
                ).count()
                quality_stats[quality.value] = count
            
            # 活躍交易對統計
            active_symbols = await session.query(SniperSignalDetails.symbol).distinct().all()
            symbol_list = [symbol[0] for symbol in active_symbols]
            
            # 最近7天統計
            week_ago = datetime.now() - timedelta(days=7)
            recent_signals = await session.query(SniperSignalDetails).filter(
                SniperSignalDetails.created_at >= week_ago
            ).count()
            
            return {
                'success': True,
                'data': {
                    'overview': {
                        'total_signals_all_time': total_signals,
                        'recent_7_days': recent_signals,
                        'active_symbols': len(symbol_list),
                        'symbols_list': symbol_list
                    },
                    'status_distribution': status_stats,
                    'quality_distribution': quality_stats,
                    'generated_at': datetime.now().isoformat()
                }
            }
            
    except Exception as e:
        logger.error(f"❌ 整體統計查詢失敗: {e}")
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")

# 將路由添加到主應用
def include_history_routes(app):
    """將信號歷史管理路由添加到主應用"""
    app.include_router(router, prefix="/api/v1/sniper", tags=["Sniper Signal History"])
