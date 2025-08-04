"""
🎯 狙擊手信號過期處理服務
基於智能時間分層的動態過期時間計算，確保歷史數據來自真實的過期信號
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, update
from sqlalchemy.orm import sessionmaker

from app.core.database import AsyncSessionLocal, get_db
from app.utils.time_utils import get_taiwan_now_naive
from app.services.intelligent_timeframe_classifier import IntelligentTimeframeClassifier

# 在 scalping_precision.py 中定義的函數
def get_taiwan_now():
    """獲取台灣時間"""
    import pytz
    from datetime import datetime
    taiwan_tz = pytz.timezone('Asia/Taipei')
    return datetime.now(taiwan_tz)

logger = logging.getLogger(__name__)

class SignalExpirationService:
    """🎯 狙擊手信號過期處理服務"""
    
    def __init__(self):
        self.timeframe_classifier = IntelligentTimeframeClassifier()
        
    async def check_and_process_expired_signals(self) -> Dict[str, Any]:
        """
        檢查並處理基於動態時間計算的過期信號
        將過期的真實信號轉移到歷史數據中
        """
        try:
            async with AsyncSessionLocal() as session:
                # 1. 獲取所有活躍的狙擊手信號
                active_signals = await self._get_active_signals(session)
                logger.info(f"🎯 檢查 {len(active_signals)} 個活躍狙擊手信號")
                
                expired_count = 0
                processed_signals = []
                
                for signal in active_signals:
                    # 2. 檢查信號是否已過期（基於動態時間計算）
                    is_expired, remaining_minutes = await self._check_signal_expiration(signal)
                    
                    if is_expired:
                        # 3. 處理過期信號：更新狀態為 EXPIRED
                        success = await self._mark_signal_as_expired(session, signal)
                        if success:
                            expired_count += 1
                            processed_signals.append({
                                'signal_id': signal['signal_id'],
                                'symbol': signal['symbol'],
                                'signal_type': signal['signal_type'],
                                'created_at': signal['created_at'],
                                'expired_at': get_taiwan_now(),
                                'recommended_duration_minutes': signal.get('recommended_duration_minutes', 0)
                            })
                            logger.info(f"✅ 狙擊手信號已過期: {signal['symbol']} (持續{signal.get('recommended_duration_minutes', 0)}分鐘)")
                    else:
                        logger.debug(f"🎯 狙擊手信號仍活躍: {signal['symbol']} (剩餘{remaining_minutes:.1f}分鐘)")
                
                await session.commit()
                
                result = {
                    'success': True,
                    'total_checked': len(active_signals),
                    'expired_count': expired_count,
                    'processed_signals': processed_signals,
                    'message': f'成功處理 {expired_count} 個過期的真實狙擊手信號'
                }
                
                logger.info(f"🎯 過期處理完成: 檢查{len(active_signals)}個，過期{expired_count}個")
                return result
                
        except Exception as e:
            logger.error(f"❌ 狙擊手信號過期處理失敗: {e}")
            return {
                'success': False,
                'error': str(e),
                'expired_count': 0
            }
    
    async def _get_active_signals(self, session: AsyncSession) -> List[Dict[str, Any]]:
        """獲取所有活躍的狙擊手信號"""
        try:
            # 查詢 trading_signals 表中的活躍信號（包含智能時間分層數據）
            query = text("""
                SELECT 
                    id,
                    symbol,
                    signal_type,
                    entry_price,
                    stop_loss,
                    take_profit,
                    confidence,
                    signal_strength,
                    created_at,
                    expires_at,
                    strategy_name,
                    reasoning,
                    timeframe,
                    precision_score,
                    is_precision_selected,
                    status
                FROM trading_signals 
                WHERE (status IS NULL OR status = 'active') 
                AND is_precision_selected = 1
                AND precision_score >= 4.0
                ORDER BY created_at DESC
            """)
            
            result = await session.execute(query)
            rows = result.fetchall()
            
            signals = []
            for row in rows:
                signal_dict = dict(row._mapping)
                signal_dict['signal_id'] = signal_dict['id']
                signals.append(signal_dict)
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ 獲取活躍信號失敗: {e}")
            return []
    
    async def _check_signal_expiration(self, signal: Dict[str, Any]) -> tuple[bool, float]:
        """
        檢查信號是否已過期（基於智能時間分層的動態計算）
        """
        try:
            created_at = signal['created_at']
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            # 檢查是否有預設的 expires_at
            expires_at = signal.get('expires_at')
            if expires_at:
                if isinstance(expires_at, str):
                    expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                
                now = get_taiwan_now().replace(tzinfo=created_at.tzinfo) if created_at.tzinfo else get_taiwan_now_naive()
                remaining_seconds = (expires_at - now).total_seconds()
                remaining_minutes = remaining_seconds / 60
                
                is_expired = remaining_seconds <= 0
                logger.debug(f"🎯 {signal['symbol']} 預設過期檢查: 剩餘{remaining_minutes:.1f}分鐘 ({'已過期' if is_expired else '仍活躍'})")
                return is_expired, remaining_minutes
            
            # 如果沒有預設過期時間，使用智能時間分層重新計算
            return await self._calculate_dynamic_expiration(signal)
            
        except Exception as e:
            logger.error(f"❌ 檢查信號過期失敗: {e}")
            return False, 0.0
    
    async def _calculate_dynamic_expiration(self, signal: Dict[str, Any]) -> tuple[bool, float]:
        """使用智能時間分層重新計算動態過期時間"""
        try:
            # 從信號中提取技術指標數據
            symbol = signal['symbol']
            confidence = signal.get('confidence', 0.0)
            timeframe = signal.get('timeframe', '5m')
            precision_score = signal.get('precision_score', 5.0)
            
            # 構建模擬的技術指標數據（在實際環境中這些數據來自實時計算）
            mock_indicators = {
                'rsi_14': 65.0,
                'macd_signal': 1,
                'ema_cross': True,
                'bollinger_squeeze': False,
                'volume_sma_ratio': 1.2
            }
            
            # 使用智能時間分層分類器計算建議持續時間
            classification_result = await asyncio.to_thread(
                self.timeframe_classifier.classify_and_calculate_duration,
                symbol=symbol,
                technical_indicators=mock_indicators,
                signal_strength=confidence,
                market_conditions={'trend': 'bullish', 'volatility': 'medium'},
                precision_score=precision_score
            )
            
            recommended_duration_minutes = classification_result.get('recommended_duration_minutes', 60)
            
            # 計算是否過期
            created_at = signal['created_at']
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            now = get_taiwan_now().replace(tzinfo=created_at.tzinfo) if created_at.tzinfo else get_taiwan_now_naive()
            elapsed_minutes = (now - created_at).total_seconds() / 60
            remaining_minutes = recommended_duration_minutes - elapsed_minutes
            
            is_expired = remaining_minutes <= 0
            
            logger.info(f"🎯 {symbol} 動態過期計算: 建議{recommended_duration_minutes}分鐘，經過{elapsed_minutes:.1f}分鐘，剩餘{remaining_minutes:.1f}分鐘")
            
            return is_expired, remaining_minutes
            
        except Exception as e:
            logger.error(f"❌ 動態過期計算失敗: {e}")
            # 使用默認過期邏輯：1小時
            created_at = signal['created_at']
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            now = get_taiwan_now().replace(tzinfo=created_at.tzinfo) if created_at.tzinfo else get_taiwan_now_naive()
            elapsed_minutes = (now - created_at).total_seconds() / 60
            remaining_minutes = 60 - elapsed_minutes  # 默認1小時
            
            return remaining_minutes <= 0, remaining_minutes
    
    async def _mark_signal_as_expired(self, session: AsyncSession, signal: Dict[str, Any]) -> bool:
        """將信號標記為已過期狀態"""
        try:
            signal_id = signal['signal_id']
            now = get_taiwan_now_naive()
            
            # 更新信號狀態為 expired
            update_query = text("""
                UPDATE trading_signals 
                SET 
                    status = 'expired',
                    archived_at = :archived_at,
                    reasoning = COALESCE(reasoning, '') || ' | 🎯 狙擊手信號已過期 - 基於智能時間分層動態計算'
                WHERE id = :signal_id
            """)
            
            await session.execute(update_query, {
                'signal_id': signal_id,
                'archived_at': now.isoformat()
            })
            
            logger.info(f"✅ 狙擊手信號已標記為過期: {signal['symbol']} (ID: {signal_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 標記信號過期失敗: {e}")
            return False
    
    async def get_expired_signals_for_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """獲取過期的狙擊手信號用於歷史數據展示"""
        try:
            async with AsyncSessionLocal() as session:
                query = text("""
                    SELECT 
                        id,
                        symbol,
                        signal_type,
                        entry_price,
                        stop_loss,
                        take_profit,
                        confidence,
                        signal_strength,
                        created_at,
                        archived_at,
                        strategy_name,
                        reasoning,
                        timeframe,
                        precision_score,
                        risk_reward_ratio,
                        status
                    FROM trading_signals 
                    WHERE status = 'expired'
                    AND is_precision_selected = 1
                    AND precision_score >= 4.0
                    ORDER BY archived_at DESC
                    LIMIT :limit
                """)
                
                result = await session.execute(query, {'limit': limit})
                rows = result.fetchall()
                
                expired_signals = []
                for row in rows:
                    signal_dict = dict(row._mapping)
                    signal_dict['archive_reason'] = 'expired_by_dynamic_calculation'
                    signal_dict['is_sniper_signal'] = True
                    signal_dict['data_source'] = 'real_market_signals'
                    expired_signals.append(signal_dict)
                
                logger.info(f"🎯 獲取 {len(expired_signals)} 個過期狙擊手歷史信號")
                return expired_signals
                
        except Exception as e:
            logger.error(f"❌ 獲取過期狙擊手信號失敗: {e}")
            return []
    
    async def cleanup_old_expired_signals(self, days_old: int = 7) -> int:
        """清理過舊的過期信號（保留最近7天的歷史數據）"""
        try:
            async with AsyncSessionLocal() as session:
                cutoff_date = get_taiwan_now_naive() - timedelta(days=days_old)
                
                # 刪除超過指定天數的過期信號
                delete_query = text("""
                    DELETE FROM trading_signals 
                    WHERE status = 'expired'
                    AND archived_at < :cutoff_date
                """)
                
                result = await session.execute(delete_query, {
                    'cutoff_date': cutoff_date.isoformat()
                })
                
                deleted_count = result.rowcount
                await session.commit()
                
                logger.info(f"🧹 清理 {deleted_count} 個 {days_old} 天前的過期信號")
                return deleted_count
                
        except Exception as e:
            logger.error(f"❌ 清理過期信號失敗: {e}")
            return 0

# 創建全域實例
signal_expiration_service = SignalExpirationService()
