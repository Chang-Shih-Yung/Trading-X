"""
短線信號歷史管理服務
負責短線信號的生成、驗證、歸檔和統計分析
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict

from ..utils.time_utils import get_taiwan_now_naive, taiwan_now_minus
from enum import Enum
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func, text
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.models import TradingSignal as SignalModel
from app.services.market_analysis import MarketAnalysisService, MarketCondition, DynamicStopLoss, SignalDirection

logger = logging.getLogger(__name__)

class TradeResult(Enum):
    """交易結果枚舉"""
    WIN = "win"
    LOSS = "loss"
    BREAKEVEN = "breakeven"
    PENDING = "pending"
    EXPIRED = "expired"

@dataclass
class ShortTermSignalHistory:
    """短線信號歷史記錄"""
    id: int
    symbol: str
    signal_type: str
    entry_price: float
    current_price: Optional[float]
    stop_loss: float
    take_profit: float
    confidence: float
    created_at: datetime
    expires_at: datetime
    archived_at: Optional[datetime]
    trade_result: TradeResult
    profit_loss_pct: Optional[float]
    max_profit_pct: Optional[float]
    max_loss_pct: Optional[float]
    time_to_result: Optional[int]  # 秒
    market_condition: Optional[Dict[str, Any]]
    reasoning: str
    strategy_name: str

@dataclass
class HistoryStatistics:
    """歷史統計數據"""
    total_signals: int
    win_count: int
    loss_count: int
    breakeven_count: int
    expired_count: int
    win_rate: float
    avg_profit_pct: float
    avg_loss_pct: float
    avg_hold_time_minutes: float
    best_performer: Optional[Dict[str, Any]]
    worst_performer: Optional[Dict[str, Any]]
    symbol_performance: Dict[str, Dict[str, Any]]
    strategy_performance: Dict[str, Dict[str, Any]]
    daily_performance: Dict[str, Dict[str, Any]]

class ShortTermHistoryService:
    """短線信號歷史管理服務"""
    
    def __init__(self):
        self.market_analyzer = MarketAnalysisService()
        self.max_history_records = 5000  # 最大歷史記錄數
        self.recent_records_ratio = 0.8  # 保留80%最近記錄
        self.successful_records_ratio = 0.2  # 保留20%成功記錄
        
    async def process_expired_signals(self, db: AsyncSession) -> int:
        """
        處理過期的短線信號，移動到歷史記錄
        
        Returns:
            int: 處理的過期信號數量
        """
        try:
            current_time = get_taiwan_now_naive()
            
            # 使用原生SQL查詢，因為資料庫表結構與模型不完全一致
            # 查找狀態為expired且為短線時間框架的信號
            raw_query = text("""
                SELECT id, symbol, signal_type, signal_strength, confidence,
                       entry_price, stop_loss, take_profit, risk_reward_ratio,
                       timeframe, reasoning, created_at, expires_at, status, indicators_used
                FROM trading_signals 
                WHERE status = 'expired'
                AND timeframe IN ('1m', '3m', '5m', '15m', '30m')
                AND (reasoning LIKE '%短線%' OR reasoning LIKE '%scalping%' OR reasoning LIKE '%框架短線策略%')
            """)
            
            result = await db.execute(raw_query)
            expired_signals = result.fetchall()
            
            processed_count = 0
            
            for signal_row in expired_signals:
                try:
                    # 將查詢結果轉換為字典格式以便處理
                    signal_dict = {
                        'id': signal_row[0],
                        'symbol': signal_row[1],
                        'signal_type': signal_row[2],
                        'signal_strength': signal_row[3],
                        'confidence': signal_row[4],
                        'entry_price': signal_row[5],
                        'stop_loss': signal_row[6],
                        'take_profit': signal_row[7],
                        'risk_reward_ratio': signal_row[8],
                        'timeframe': signal_row[9],
                        'reasoning': signal_row[10],
                        'created_at': signal_row[11],
                        'expires_at': signal_row[12],
                        'status': signal_row[13],
                        'indicators_used': signal_row[14]
                    }
                    
                    # 計算最終結果
                    trade_result, profit_loss_pct = await self._calculate_final_result_from_dict(signal_dict)
                    
                    # 創建歷史記錄
                    await self._create_history_record(db, signal_dict, trade_result, profit_loss_pct)
                    
                    # 更新信號狀態為已歸檔（可選，或者保持expired狀態）
                    update_query = text("""
                        UPDATE trading_signals 
                        SET status = 'archived'
                        WHERE id = :signal_id
                    """)
                    await db.execute(update_query, {'signal_id': signal_dict['id']})
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"處理過期信號 {signal_dict.get('id', 'unknown')} 失敗: {e}")
                    continue
            
            await db.commit()
            
            # 清理過多的歷史記錄
            if processed_count > 0:
                await self._cleanup_old_history(db)
            
            logger.info(f"成功處理 {processed_count} 個過期短線信號")
            return processed_count
            
        except Exception as e:
            logger.error(f"處理過期信號失敗: {e}")
            await db.rollback()
            return 0
    
    async def get_history_statistics(self, 
                                   db: AsyncSession,
                                   days: int = 30,
                                   symbol: Optional[str] = None) -> HistoryStatistics:
        """
        獲取歷史統計數據
        
        Args:
            db: 數據庫會話
            days: 統計天數
            symbol: 特定交易對（可選）
            
        Returns:
            HistoryStatistics: 統計結果
        """
        try:
            start_date = taiwan_now_minus(days=days)
            
            # 構建查詢條件
            conditions = [
                SignalModel.archived_at >= start_date,
                SignalModel.trade_result.isnot(None)
            ]
            
            if symbol:
                conditions.append(SignalModel.symbol == symbol)
            
            # 查詢歷史記錄
            stmt = select(SignalModel).where(and_(*conditions))
            result = await db.execute(stmt)
            history_records = result.scalars().all()
            
            if not history_records:
                return self._empty_statistics()
            
            # 計算基本統計
            total_signals = len(history_records)
            win_count = sum(1 for r in history_records if r.trade_result == TradeResult.WIN.value)
            loss_count = sum(1 for r in history_records if r.trade_result == TradeResult.LOSS.value)
            breakeven_count = sum(1 for r in history_records if r.trade_result == TradeResult.BREAKEVEN.value)
            expired_count = sum(1 for r in history_records if r.trade_result == TradeResult.EXPIRED.value)
            
            win_rate = (win_count / total_signals) * 100 if total_signals > 0 else 0
            
            # 計算平均盈虧
            profitable_records = [r for r in history_records if r.profit_loss_pct and r.profit_loss_pct > 0]
            losing_records = [r for r in history_records if r.profit_loss_pct and r.profit_loss_pct < 0]
            
            avg_profit_pct = sum(r.profit_loss_pct for r in profitable_records) / len(profitable_records) if profitable_records else 0
            avg_loss_pct = sum(r.profit_loss_pct for r in losing_records) / len(losing_records) if losing_records else 0
            
            # 計算平均持有時間
            hold_times = []
            for record in history_records:
                if record.created_at and record.archived_at:
                    hold_time = (record.archived_at - record.created_at).total_seconds() / 60
                    hold_times.append(hold_time)
            
            avg_hold_time = sum(hold_times) / len(hold_times) if hold_times else 0
            
            # 找出最佳和最差表現
            best_performer = None
            worst_performer = None
            
            if profitable_records:
                best = max(profitable_records, key=lambda x: x.profit_loss_pct)
                best_performer = {
                    'symbol': best.symbol,
                    'profit_pct': best.profit_loss_pct,
                    'strategy': best.strategy_name,
                    'date': best.created_at.strftime('%Y-%m-%d %H:%M')
                }
            
            if losing_records:
                worst = min(losing_records, key=lambda x: x.profit_loss_pct)
                worst_performer = {
                    'symbol': worst.symbol,
                    'loss_pct': worst.profit_loss_pct,
                    'strategy': worst.strategy_name,
                    'date': worst.created_at.strftime('%Y-%m-%d %H:%M')
                }
            
            # 分析交易對表現
            symbol_performance = await self._analyze_symbol_performance(history_records)
            
            # 分析策略表現
            strategy_performance = await self._analyze_strategy_performance(history_records)
            
            # 分析每日表現
            daily_performance = await self._analyze_daily_performance(history_records)
            
            return HistoryStatistics(
                total_signals=total_signals,
                win_count=win_count,
                loss_count=loss_count,
                breakeven_count=breakeven_count,
                expired_count=expired_count,
                win_rate=win_rate,
                avg_profit_pct=avg_profit_pct,
                avg_loss_pct=avg_loss_pct,
                avg_hold_time_minutes=avg_hold_time,
                best_performer=best_performer,
                worst_performer=worst_performer,
                symbol_performance=symbol_performance,
                strategy_performance=strategy_performance,
                daily_performance=daily_performance
            )
            
        except Exception as e:
            logger.error(f"獲取歷史統計失敗: {e}")
            return self._empty_statistics()
    
    async def recalculate_historical_results(self, 
                                           db: AsyncSession,
                                           new_breakeven_threshold: float = 0.5) -> Dict[str, Any]:
        """
        重新計算歷史記錄的交易結果（應用新的平手標準）
        
        Args:
            db: 數據庫會話
            new_breakeven_threshold: 新的平手閾值（百分比）
            
        Returns:
            Dict: 重算結果統計
        """
        try:
            # 查詢所有已歸檔的記錄
            stmt = select(SignalModel).where(
                and_(
                    SignalModel.archived_at.isnot(None),
                    SignalModel.profit_loss_pct.isnot(None)
                )
            )
            
            result = await db.execute(stmt)
            historical_records = result.scalars().all()
            
            changes = {
                'total_processed': 0,
                'win_to_breakeven': 0,
                'loss_to_breakeven': 0,
                'breakeven_to_win': 0,
                'breakeven_to_loss': 0,
                'no_change': 0
            }
            
            for record in historical_records:
                old_result = record.trade_result
                
                # 應用新的判斷邏輯
                if abs(record.profit_loss_pct) <= new_breakeven_threshold:
                    new_result = TradeResult.BREAKEVEN.value
                elif record.profit_loss_pct > new_breakeven_threshold:
                    new_result = TradeResult.WIN.value
                else:
                    new_result = TradeResult.LOSS.value
                
                # 記錄變化
                if old_result != new_result:
                    if old_result == TradeResult.WIN.value and new_result == TradeResult.BREAKEVEN.value:
                        changes['win_to_breakeven'] += 1
                    elif old_result == TradeResult.LOSS.value and new_result == TradeResult.BREAKEVEN.value:
                        changes['loss_to_breakeven'] += 1
                    elif old_result == TradeResult.BREAKEVEN.value and new_result == TradeResult.WIN.value:
                        changes['breakeven_to_win'] += 1
                    elif old_result == TradeResult.BREAKEVEN.value and new_result == TradeResult.LOSS.value:
                        changes['breakeven_to_loss'] += 1
                    
                    # 更新記錄
                    record.trade_result = new_result
                else:
                    changes['no_change'] += 1
                
                changes['total_processed'] += 1
            
            await db.commit()
            
            logger.info(f"重算歷史結果完成: {changes}")
            return changes
            
        except Exception as e:
            logger.error(f"重算歷史結果失敗: {e}")
            await db.rollback()
            return {'error': str(e)}
    
    async def get_short_term_history(self, 
                                   db: AsyncSession,
                                   limit: int = 100,
                                   offset: int = 0,
                                   symbol: Optional[str] = None,
                                   trade_result: Optional[str] = None) -> List[Dict]:
        """
        獲取短線信號歷史記錄
        
        Args:
            db: 數據庫會話
            limit: 限制數量
            offset: 偏移量
            symbol: 篩選交易對
            trade_result: 篩選交易結果
            
        Returns:
            List[Dict]: 歷史記錄列表
        """
        try:
            # 使用原生SQL查詢已歸檔的短線信號
            where_conditions = ["status IN ('expired', 'archived')"]
            where_conditions.append("timeframe IN ('1m', '3m', '5m', '15m', '30m')")
            where_conditions.append("(reasoning LIKE '%短線%' OR reasoning LIKE '%scalping%' OR reasoning LIKE '%框架短線策略%')")
            
            if symbol:
                where_conditions.append(f"symbol = '{symbol}'")
                
            if trade_result:
                where_conditions.append(f"status = '{trade_result}'")
            
            query = f"""
                SELECT id, symbol, signal_type, signal_strength, confidence,
                       entry_price, stop_loss, take_profit, risk_reward_ratio,
                       timeframe, reasoning, created_at, expires_at, status, indicators_used
                FROM trading_signals 
                WHERE {' AND '.join(where_conditions)}
                ORDER BY created_at DESC
                LIMIT {limit} OFFSET {offset}
            """
            
            result = await db.execute(text(query))
            rows = result.fetchall()
            
            # 轉換為字典格式
            history_records = []
            for row in rows:
                record = {
                    "id": row[0],
                    "symbol": row[1],
                    "signal_type": row[2],
                    "signal_strength": row[3],
                    "confidence": row[4],
                    "entry_price": row[5],
                    "stop_loss": row[6],
                    "take_profit": row[7],
                    "risk_reward_ratio": row[8],
                    "timeframe": row[9],
                    "reasoning": row[10],
                    "created_at": row[11],
                    "expires_at": row[12],
                    "status": row[13],
                    "indicators_used": row[14],
                    # 添加計算的歷史字段
                    "archived_at": row[12],  # 使用expires_at作為archived_at
                    "trade_result": "EXPIRED",  # 標記為已過期
                    "profit_loss_pct": None,
                    "current_price": None,
                    "max_profit_pct": None,
                    "max_loss_pct": None,
                    "time_to_result": None,
                    "market_condition": "Unknown",
                    "strategy_name": "短線策略"
                }
                history_records.append(record)
            
            return history_records
            
        except Exception as e:
            logger.error(f"獲取短線歷史記錄失敗: {e}")
            return []

    async def _calculate_final_result(self, signal: SignalModel) -> Tuple[TradeResult, Optional[float]]:
        """計算信號的最終交易結果"""
        try:
            if not signal.current_price or not signal.entry_price:
                return TradeResult.EXPIRED, None
            
            # 計算盈虧百分比
            if signal.signal_type in ['LONG', 'SCALPING_LONG']:
                profit_loss_pct = ((signal.current_price - signal.entry_price) / signal.entry_price) * 100
            else:  # SHORT or SCALPING_SHORT
                profit_loss_pct = ((signal.entry_price - signal.current_price) / signal.entry_price) * 100
            
            # 判斷結果（使用0.5%作為平手標準）
            if abs(profit_loss_pct) <= 0.5:
                return TradeResult.BREAKEVEN, profit_loss_pct
            elif profit_loss_pct > 0.5:
                return TradeResult.WIN, profit_loss_pct
            else:
                return TradeResult.LOSS, profit_loss_pct
                
        except Exception as e:
            logger.error(f"計算最終結果失敗: {e}")
            return TradeResult.EXPIRED, None

    async def _calculate_final_result_from_dict(self, signal_dict: dict) -> Tuple[TradeResult, Optional[float]]:
        """從字典格式計算信號的最終交易結果"""
        try:
            # 對於過期信號，使用模擬的市場價格或直接標記為過期
            # 這裡可以通過市場數據服務獲取實際價格
            # 暫時標記為已過期
            return TradeResult.EXPIRED, None
                
        except Exception as e:
            logger.error(f"計算最終結果失敗: {e}")
            return TradeResult.EXPIRED, None

    async def _create_history_record(self, db: AsyncSession, signal_dict: dict, trade_result: TradeResult, profit_loss_pct: Optional[float]):
        """創建歷史記錄（將在歷史表中實現）"""
        try:
            # 目前只是記錄到日誌，未來可以創建專門的歷史表
            logger.info(f"歷史記錄創建 - ID: {signal_dict['id']}, 結果: {trade_result.value}, 盈虧: {profit_loss_pct}%")
            
        except Exception as e:
            logger.error(f"創建歷史記錄失敗: {e}")
    
    async def _update_history_statistics(self, db: AsyncSession, signal: SignalModel):
        """更新歷史統計數據"""
        # 這裡可以實現更複雜的統計更新邏輯
        # 例如更新每日、每週、每月的統計數據
        pass
    
    async def _cleanup_old_history(self, db: AsyncSession):
        """清理過多的歷史記錄"""
        try:
            # 統計當前歷史記錄數量
            count_stmt = select(func.count(SignalModel.id)).where(SignalModel.archived_at.isnot(None))
            result = await db.execute(count_stmt)
            total_count = result.scalar()
            
            if total_count <= self.max_history_records:
                return
            
            # 需要刪除的記錄數
            records_to_delete = total_count - self.max_history_records
            
            # 保留最近的記錄和成功的記錄
            recent_limit = int(self.max_history_records * self.recent_records_ratio)
            successful_limit = int(self.max_history_records * self.successful_records_ratio)
            
            # 獲取要保留的記錄ID
            # 1. 最近的記錄
            recent_stmt = (select(SignalModel.id)
                          .where(SignalModel.archived_at.isnot(None))
                          .order_by(SignalModel.archived_at.desc())
                          .limit(recent_limit))
            recent_result = await db.execute(recent_stmt)
            recent_ids = [row[0] for row in recent_result.fetchall()]
            
            # 2. 成功的記錄
            successful_stmt = (select(SignalModel.id)
                             .where(and_(
                                 SignalModel.archived_at.isnot(None),
                                 SignalModel.trade_result == TradeResult.WIN.value
                             ))
                             .order_by(SignalModel.profit_loss_pct.desc())
                             .limit(successful_limit))
            successful_result = await db.execute(successful_stmt)
            successful_ids = [row[0] for row in successful_result.fetchall()]
            
            # 合併要保留的ID
            keep_ids = set(recent_ids + successful_ids)
            
            # 刪除其他記錄
            delete_stmt = delete(SignalModel).where(
                and_(
                    SignalModel.archived_at.isnot(None),
                    ~SignalModel.id.in_(keep_ids)
                )
            )
            
            result = await db.execute(delete_stmt)
            deleted_count = result.rowcount
            
            await db.commit()
            logger.info(f"清理了 {deleted_count} 條舊的歷史記錄")
            
        except Exception as e:
            logger.error(f"清理歷史記錄失敗: {e}")
            await db.rollback()
    
    def _empty_statistics(self) -> HistoryStatistics:
        """返回空的統計數據"""
        return HistoryStatistics(
            total_signals=0,
            win_count=0,
            loss_count=0,
            breakeven_count=0,
            expired_count=0,
            win_rate=0.0,
            avg_profit_pct=0.0,
            avg_loss_pct=0.0,
            avg_hold_time_minutes=0.0,
            best_performer=None,
            worst_performer=None,
            symbol_performance={},
            strategy_performance={},
            daily_performance={}
        )
    
    async def _analyze_symbol_performance(self, records: List[SignalModel]) -> Dict[str, Dict[str, Any]]:
        """分析交易對表現"""
        symbol_stats = {}
        
        for record in records:
            symbol = record.symbol
            if symbol not in symbol_stats:
                symbol_stats[symbol] = {
                    'total_trades': 0,
                    'wins': 0,
                    'losses': 0,
                    'breakevens': 0,
                    'total_profit_loss': 0.0,
                    'best_trade': None,
                    'worst_trade': None
                }
            
            stats = symbol_stats[symbol]
            stats['total_trades'] += 1
            
            if record.trade_result == TradeResult.WIN.value:
                stats['wins'] += 1
            elif record.trade_result == TradeResult.LOSS.value:
                stats['losses'] += 1
            elif record.trade_result == TradeResult.BREAKEVEN.value:
                stats['breakevens'] += 1
            
            if record.profit_loss_pct:
                stats['total_profit_loss'] += record.profit_loss_pct
                
                if stats['best_trade'] is None or record.profit_loss_pct > stats['best_trade']:
                    stats['best_trade'] = record.profit_loss_pct
                    
                if stats['worst_trade'] is None or record.profit_loss_pct < stats['worst_trade']:
                    stats['worst_trade'] = record.profit_loss_pct
        
        # 計算最終統計
        for symbol, stats in symbol_stats.items():
            if stats['total_trades'] > 0:
                stats['win_rate'] = (stats['wins'] / stats['total_trades']) * 100
                stats['avg_profit_loss'] = stats['total_profit_loss'] / stats['total_trades']
            else:
                stats['win_rate'] = 0
                stats['avg_profit_loss'] = 0
        
        return symbol_stats
    
    async def _analyze_strategy_performance(self, records: List[SignalModel]) -> Dict[str, Dict[str, Any]]:
        """分析策略表現"""
        strategy_stats = {}
        
        for record in records:
            strategy = record.strategy_name or "Unknown"
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    'total_trades': 0,
                    'wins': 0,
                    'losses': 0,
                    'breakevens': 0,
                    'total_profit_loss': 0.0,
                    'avg_confidence': 0.0
                }
            
            stats = strategy_stats[strategy]
            stats['total_trades'] += 1
            stats['avg_confidence'] += record.confidence
            
            if record.trade_result == TradeResult.WIN.value:
                stats['wins'] += 1
            elif record.trade_result == TradeResult.LOSS.value:
                stats['losses'] += 1
            elif record.trade_result == TradeResult.BREAKEVEN.value:
                stats['breakevens'] += 1
            
            if record.profit_loss_pct:
                stats['total_profit_loss'] += record.profit_loss_pct
        
        # 計算最終統計
        for strategy, stats in strategy_stats.items():
            if stats['total_trades'] > 0:
                stats['win_rate'] = (stats['wins'] / stats['total_trades']) * 100
                stats['avg_profit_loss'] = stats['total_profit_loss'] / stats['total_trades']
                stats['avg_confidence'] = stats['avg_confidence'] / stats['total_trades']
            else:
                stats['win_rate'] = 0
                stats['avg_profit_loss'] = 0
                stats['avg_confidence'] = 0
        
        return strategy_stats
    
    async def _analyze_daily_performance(self, records: List[SignalModel]) -> Dict[str, Dict[str, Any]]:
        """分析每日表現"""
        daily_stats = {}
        
        for record in records:
            if not record.archived_at:
                continue
                
            date_key = record.archived_at.strftime('%Y-%m-%d')
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    'total_trades': 0,
                    'wins': 0,
                    'losses': 0,
                    'breakevens': 0,
                    'total_profit_loss': 0.0
                }
            
            stats = daily_stats[date_key]
            stats['total_trades'] += 1
            
            if record.trade_result == TradeResult.WIN.value:
                stats['wins'] += 1
            elif record.trade_result == TradeResult.LOSS.value:
                stats['losses'] += 1
            elif record.trade_result == TradeResult.BREAKEVEN.value:
                stats['breakevens'] += 1
            
            if record.profit_loss_pct:
                stats['total_profit_loss'] += record.profit_loss_pct
        
        # 計算最終統計
        for date, stats in daily_stats.items():
            if stats['total_trades'] > 0:
                stats['win_rate'] = (stats['wins'] / stats['total_trades']) * 100
                stats['avg_profit_loss'] = stats['total_profit_loss'] / stats['total_trades']
            else:
                stats['win_rate'] = 0
                stats['avg_profit_loss'] = 0
        
        return daily_stats
