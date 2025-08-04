# 🎯 狙擊手智能分層系統 - API 端點

from fastapi import APIRouter, Query, HTTPException, BackgroundTasks, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import or_
import os

from app.services.sniper_smart_layer import sniper_smart_layer, SniperSmartLayerSystem
from app.services.sniper_emergency_trigger import sniper_emergency_trigger
from app.services.sniper_signal_history_service import sniper_signal_tracker
from app.utils.timezone_utils import get_taiwan_now, ensure_taiwan_timezone
from app.core.database import get_db
from app.models.sniper_signal_history import SniperSignalDetails
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ==================== 精準策略時間過濾器 ====================

async def _apply_precision_time_filter(signals: List[Dict]) -> List[Dict]:
    """
    🚀 精準策略時間過濾 - 多層時間優先篩選
    
    優先級：
    1. ⚡ 10秒內：實時分析信號 (最高優先級)
    2. 🔥 1分鐘內：新鮮分析信號 (高優先級)  
    3. ⏰ 5分鐘內：近期分析信號 (中優先級)
    4. 🕐 15分鐘內：可用分析信號 (低優先級)
    5. ⚠️ 超過15分鐘：帶過期警告 (最低優先級)
    """
    try:
        from app.utils.timezone_utils import get_taiwan_now
        
        now = get_taiwan_now().replace(tzinfo=None)  # 移除時區信息避免比較錯誤
        
        tier_1 = []  # ≤10秒
        tier_2 = []  # ≤1分鐘
        tier_3 = []  # ≤5分鐘
        tier_4 = []  # ≤15分鐘
        tier_5 = []  # >15分鐘
        
        for signal in signals:
            try:
                # 解析信號生成時間
                created_at = signal.get('created_at')
                if isinstance(created_at, str):
                    # 簡化時間解析，避免時區錯誤
                    if 'T' in created_at:
                        created_at = created_at.split('T')[0] + ' ' + created_at.split('T')[1].split('+')[0].split('Z')[0]
                    created_at = datetime.strptime(created_at[:19], '%Y-%m-%d %H:%M:%S')
                elif isinstance(created_at, datetime):
                    created_at = created_at.replace(tzinfo=None)
                else:
                    # 如果時間解析失敗，給默認時間差
                    signal['time_diff_seconds'] = 600  # 10分鐘
                    signal['precision_tier'] = 'unknown'
                    tier_4.append(signal)
                    continue
                    
                time_diff = (now - created_at).total_seconds()
                
                # 添加時間差標記
                signal['time_diff_seconds'] = time_diff
                signal['local_created_at'] = created_at.strftime('%Y-%m-%d %H:%M:%S')
                signal['precision_tier'] = None
                
                if time_diff <= 10:
                    signal['precision_tier'] = 'realtime'
                    tier_1.append(signal)
                elif time_diff <= 60:
                    signal['precision_tier'] = 'fresh'
                    tier_2.append(signal)
                elif time_diff <= 300:
                    signal['precision_tier'] = 'recent'
                    tier_3.append(signal)
                elif time_diff <= 900:
                    signal['precision_tier'] = 'available'
                    tier_4.append(signal)
                else:
                    signal['precision_tier'] = 'expired'
                    signal['expiry_warning'] = True
                    tier_5.append(signal)
            except Exception as e:
                logger.warning(f"⚠️ 信號時間解析失敗: {e}")
                signal['time_diff_seconds'] = 600
                signal['precision_tier'] = 'unknown'
                tier_4.append(signal)
        
        # 記錄分層結果
        logger.info(f"🚀 精準策略時間分層: "
                   f"實時({len(tier_1)}) | 新鮮({len(tier_2)}) | 近期({len(tier_3)}) | "
                   f"可用({len(tier_4)}) | 過期({len(tier_5)})")
        
        # 優先返回高層級信號，但更寬鬆的策略
        combined_signals = []
        
        if tier_1:
            logger.info(f"⚡ 包含實時信號: {len(tier_1)} 個 (≤10秒)")
            combined_signals.extend(tier_1)
        if tier_2:
            logger.info(f"🔥 包含新鮮信號: {len(tier_2)} 個 (≤1分鐘)")
            combined_signals.extend(tier_2)
        if tier_3:
            logger.info(f"⏰ 包含近期信號: {len(tier_3)} 個 (≤5分鐘)")
            combined_signals.extend(tier_3)
        if tier_4:
            logger.info(f"🕐 包含可用信號: {len(tier_4)} 個 (≤15分鐘)")
            combined_signals.extend(tier_4)
        
        # 如果高質量信號不夠，也包含過期信號但標記警告
        if len(combined_signals) < 5 and tier_5:
            logger.info(f"⚠️ 補充過期信號: {len(tier_5)} 個 (>15分鐘)")
            combined_signals.extend(tier_5[:10])  # 最多添加10個過期信號
        
        return combined_signals if combined_signals else signals  # 如果沒有任何信號，返回原始列表
    except Exception as e:
        logger.error(f"❌ 精準時間過濾失敗: {e}")
        return signals  # 返回原始信號列表

# ==================== Pydantic 模型 ====================

class SmartLayerQuery(BaseModel):
    """智能分層查詢參數"""
    symbols: Optional[List[str]] = None
    include_analysis: bool = True
    quality_threshold: float = 6.0
    max_signals_per_symbol: int = 1

class LastStrategyQuery(BaseModel):
    """上一單策略查詢參數"""
    include_recommendation: bool = True
    include_risk_assessment: bool = True

class DynamicRiskParamsResponse(BaseModel):
    """動態風險參數響應模型"""
    symbol: str
    market_volatility_score: float
    volume_score: float
    liquidity_score: float
    emotion_multiplier: float
    market_regime: str
    regime_confidence: float
    bull_weight: float
    bear_weight: float
    dynamic_stop_loss: float
    dynamic_take_profit: float
    confidence_threshold: float
    rsi_threshold: List[int]
    ma_periods: List[int]
    position_multiplier: float
    last_update: str

# ==================== API 端點 ====================

@router.delete("/clear-test-signals", response_model=dict)
async def clear_test_signals(
    db: AsyncSession = Depends(get_db)
):
    """🧹 清理所有測試信號（包含 test_ 或 smart_ 前綴的信號）"""
    try:
        from sqlalchemy import select, delete
        
        # 查詢包含測試前綴的信號
        test_prefixes = ['test_', 'smart_', 'demo_']
        conditions = []
        for prefix in test_prefixes:
            conditions.append(SniperSignalDetails.signal_id.like(f'{prefix}%'))
        
        # 先查詢數量
        count_stmt = select(SniperSignalDetails).filter(or_(*conditions))
        result = await db.execute(count_stmt)
        signals_to_delete = result.scalars().all()
        delete_count = len(signals_to_delete)
        
        # 刪除測試信號
        delete_stmt = delete(SniperSignalDetails).where(or_(*conditions))
        await db.execute(delete_stmt)
        await db.commit()
        
        logger.info(f"🧹 清理測試信號完成: 刪除 {delete_count} 個信號")
        
        return {
            "status": "success",
            "deleted_count": delete_count,
            "message": f"🧹 成功清理 {delete_count} 個測試信號",
            "cleared_prefixes": test_prefixes,
            "timestamp": get_taiwan_now().isoformat()
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ 刪除測試信號失敗: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"清理測試信號失敗: {str(e)}"
        )

@router.post("/update-signal-status", response_model=dict)
async def update_signal_status(
    signal_id: str,
    new_status: str,
    pnl_percentage: Optional[float] = None,
    result_price: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    """🔧 手動更新信號狀態（用於測試統計算法）"""
    try:
        from sqlalchemy import select, update
        from app.models.sniper_signal_history import SniperSignalDetails, SignalStatus
        
        # 查找信號
        stmt = select(SniperSignalDetails).where(SniperSignalDetails.signal_id == signal_id)
        result = await db.execute(stmt)
        signal = result.scalar_one_or_none()
        
        if not signal:
            raise HTTPException(status_code=404, detail=f"信號 {signal_id} 不存在")
        
        # 狀態映射
        status_map = {
            "expired": SignalStatus.EXPIRED,
            "hit_tp": SignalStatus.HIT_TP,
            "hit_sl": SignalStatus.HIT_SL,
            "cancelled": SignalStatus.CANCELLED
        }
        
        if new_status not in status_map:
            raise HTTPException(status_code=400, detail=f"無效狀態: {new_status}")
        
        # 更新信號
        update_data = {
            "status": status_map[new_status],
            "result_time": get_taiwan_now()
        }
        
        if pnl_percentage is not None:
            update_data["pnl_percentage"] = pnl_percentage
        
        if result_price is not None:
            update_data["result_price"] = result_price
        
        stmt = update(SniperSignalDetails).where(
            SniperSignalDetails.signal_id == signal_id
        ).values(**update_data)
        
        await db.execute(stmt)
        await db.commit()
        
        logger.info(f"🔧 信號狀態更新: {signal_id} → {new_status}")
        
        return {
            "status": "success",
            "message": f"信號 {signal_id} 狀態已更新為 {new_status}",
            "updates": update_data,
            "timestamp": get_taiwan_now().isoformat()
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ 更新信號狀態失敗: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"更新信號狀態失敗: {str(e)}"
        )

async def _generate_enhanced_statistics(signals: List[Dict]) -> Dict:
    """生成增強統計信息"""
    try:
        from app.core.database import get_db
        from app.models.sniper_signal_history import SniperSignalDetails, SignalStatus
        from sqlalchemy import select, func
        
        # 獲取數據庫統計
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            # 基本統計
            total_result = await db.execute(
                select(func.count(SniperSignalDetails.id))
            )
            total_db_signals = total_result.scalar() or 0
            
            # 狀態統計
            status_result = await db.execute(
                select(
                    SniperSignalDetails.status,
                    func.count(SniperSignalDetails.id),
                    func.avg(SniperSignalDetails.pnl_percentage)
                ).group_by(SniperSignalDetails.status)
            )
            
            status_stats = {}
            for row in status_result.fetchall():
                status_stats[row[0].value] = {
                    'count': row[1],
                    'avg_pnl': round(row[2] or 0, 2)
                }
            
            # 計算真實統計指標
            active_count = status_stats.get('ACTIVE', {}).get('count', 0)
            tp_count = status_stats.get('HIT_TP', {}).get('count', 0)
            sl_count = status_stats.get('HIT_SL', {}).get('count', 0)
            expired_count = status_stats.get('EXPIRED', {}).get('count', 0)
            
            completed_signals = tp_count + sl_count + expired_count
            traditional_win_rate = (tp_count / completed_signals * 100) if completed_signals > 0 else 0.0
            
            # 基於PnL的真實成功率
            profitable_result = await db.execute(
                select(func.count(SniperSignalDetails.id))
                .where(SniperSignalDetails.pnl_percentage > 0)
            )
            profitable_count = profitable_result.scalar() or 0
            real_success_rate = (profitable_count / total_db_signals * 100) if total_db_signals > 0 else 0.0
            
            return {
                'database_stats': {
                    'total_signals': total_db_signals,
                    'active_signals': active_count,
                    'traditional_win_rate': round(traditional_win_rate, 1),
                    'real_success_rate': round(real_success_rate, 1),
                    'status_breakdown': status_stats
                },
                'api_stats': {
                    'returned_signals': len(signals),
                    'symbols_covered': len(set(s['symbol'] for s in signals)),
                    'avg_quality_score': round(sum(s.get('quality_score', 0) for s in signals) / len(signals), 2) if signals else 0,
                    'quality_range': {
                        'min': min(s.get('quality_score', 0) for s in signals) if signals else 0,
                        'max': max(s.get('quality_score', 0) for s in signals) if signals else 0
                    }
                },
                'filtering_efficiency': {
                    'db_to_api_ratio': round((len(signals) / total_db_signals * 100), 1) if total_db_signals > 0 else 0,
                    'active_to_api_ratio': round((len(signals) / active_count * 100), 1) if active_count > 0 else 0
                }
            }
            
        finally:
            await db_gen.aclose()
            
    except Exception as e:
        logger.error(f"❌ 生成增強統計失敗: {e}")
        return {
            'database_stats': {'error': str(e)},
            'api_stats': {'returned_signals': len(signals)},
            'filtering_efficiency': {'error': 'calculation_failed'}
        }
