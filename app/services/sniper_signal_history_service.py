# 🎯 狙擊手信號歷史管理 - 核心服務

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session

from app.models.sniper_signal_history import (
    SniperSignalDetails, 
    SniperSignalSummary,
    SignalStatus,
    SignalQuality, 
    TradingTimeframe
)
from app.core.database import db_manager
from sniper_unified_data_layer import TradingTimeframe as SniperTimeframe, DynamicRiskParameters
import logging

logger = logging.getLogger(__name__)

class SniperSignalTracker:
    """
    🎯 狙擊手信號追蹤器
    
    負責：
    1. 接收新的狙擊手信號並儲存
    2. 監控活躍信號狀態變化
    3. 更新信號結果 (止盈/止損/過期)
    4. 維護信號生命週期管理
    """
    
    def __init__(self):
        self.active_signals_cache = {}  # 內存快取活躍信號
        
    async def record_new_signal(
        self,
        symbol: str,
        signal_type: str,
        entry_price: float,
        stop_loss_price: float,
        take_profit_price: float,
        signal_strength: float,
        confluence_count: int,
        timeframe: TradingTimeframe,
        risk_params: DynamicRiskParameters,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        📝 記錄新的狙擊手信號
        
        Returns: signal_id (唯一標識符)
        """
        try:
            # 生成唯一信號ID
            signal_id = f"sniper_{symbol}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # 計算信號品質等級
            if signal_strength >= 0.7:
                quality = SignalQuality.HIGH
            elif signal_strength >= 0.4:
                quality = SignalQuality.MEDIUM
            else:
                quality = SignalQuality.LOW
            
            # 計算過期時間
            expiry_hours = risk_params.expiry_hours
            expires_at = datetime.now() + timedelta(hours=expiry_hours)
            
            # 計算風險回報比
            if signal_type.upper() == "BUY":
                risk = entry_price - stop_loss_price
                reward = take_profit_price - entry_price
            else:  # SELL
                risk = stop_loss_price - entry_price
                reward = entry_price - take_profit_price
            
            risk_reward_ratio = reward / risk if risk > 0 else 0.0
            
            # 準備額外元數據
            metadata_json = json.dumps(metadata or {})
            
            # 創建詳細記錄
            signal_detail = SniperSignalDetails(
                signal_id=signal_id,
                symbol=symbol,
                signal_type=signal_type.upper(),
                entry_price=entry_price,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                signal_strength=signal_strength,
                confluence_count=confluence_count,
                signal_quality=quality,
                timeframe=timeframe,
                expiry_hours=expiry_hours,
                risk_reward_ratio=risk_reward_ratio,
                market_volatility=risk_params.market_volatility,
                atr_value=risk_params.atr_value,
                market_regime=getattr(risk_params, 'market_regime', None),
                expires_at=expires_at,
                status=SignalStatus.ACTIVE,
                layer_one_time=getattr(risk_params, 'layer_one_time', None),
                layer_two_time=getattr(risk_params, 'layer_two_time', None),
                pass_rate=getattr(risk_params, 'pass_rate', None),
                metadata_json=metadata_json,
                reasoning=metadata.get('reasoning', '') if metadata else ''
            )
            
            # 儲存到資料庫
            session = await db_manager.create_session()
            try:
                session.add(signal_detail)
                await session.commit()
            finally:
                await session.close()
                
            # 更新內存快取
            self.active_signals_cache[signal_id] = {
                'symbol': symbol,
                'signal_type': signal_type,
                'entry_price': entry_price,
                'stop_loss_price': stop_loss_price,
                'take_profit_price': take_profit_price,
                'expires_at': expires_at,
                'status': SignalStatus.ACTIVE
            }
            
            logger.info(f"✅ 狙擊手信號已記錄: {signal_id} ({symbol} {signal_type})")
            return signal_id
            
        except Exception as e:
            logger.error(f"❌ 狙擊手信號記錄失敗: {e}")
            raise

    async def update_signal_result(
        self,
        signal_id: str,
        new_status: SignalStatus,
        result_price: float,
        result_time: Optional[datetime] = None
    ) -> bool:
        """
        🎯 更新信號結果狀態
        
        當價格觸及止損/止盈或信號過期時調用
        """
        try:
            if result_time is None:
                result_time = datetime.now()
                
            session = await db_manager.create_session()
            try:
                # 查詢信號詳情
                from sqlalchemy import select
                stmt = select(SniperSignalDetails).where(SniperSignalDetails.signal_id == signal_id)
                result = await session.execute(stmt)
                signal = result.scalar_one_or_none()
                
                if not signal:
                    logger.warning(f"⚠️ 信號不存在: {signal_id}")
                    return False
                
                # 計算盈虧百分比
                pnl_percentage = 0.0
                if new_status in [SignalStatus.HIT_TP, SignalStatus.HIT_SL]:
                    if signal.signal_type == "BUY":
                        pnl_percentage = ((result_price - signal.entry_price) / signal.entry_price) * 100
                    else:  # SELL
                        pnl_percentage = ((signal.entry_price - result_price) / signal.entry_price) * 100
                
                # 更新信號狀態
                signal.status = new_status
                signal.result_price = result_price
                signal.result_time = result_time
                signal.pnl_percentage = pnl_percentage
                
                await session.commit()
                
                # 更新內存快取
                if signal_id in self.active_signals_cache:
                    self.active_signals_cache[signal_id]['status'] = new_status
                    if new_status != SignalStatus.ACTIVE:
                        del self.active_signals_cache[signal_id]
                
                logger.info(f"✅ 信號狀態已更新: {signal_id} -> {new_status.value} (PnL: {pnl_percentage:.2f}%)")
                return True
            finally:
                await session.close()
                
        except Exception as e:
            logger.error(f"❌ 信號狀態更新失敗: {signal_id}, {e}")
            return False

    async def monitor_active_signals(self) -> List[Dict]:
        """
        🔍 監控所有活躍信號
        
        檢查是否有信號需要狀態更新（價格觸及止損/止盈或過期）
        返回需要更新的信號列表
        """
        try:
            current_time = datetime.now()
            signals_to_update = []
            
            session = await db_manager.create_session()
            try:
                # 查詢所有活躍信號
                from sqlalchemy import select
                stmt = select(SniperSignalDetails).where(SniperSignalDetails.status == SignalStatus.ACTIVE)
                result = await session.execute(stmt)
                active_signals = result.scalars().all()
                
                for signal in active_signals:
                    # 檢查是否過期
                    if current_time >= signal.expires_at:
                        signals_to_update.append({
                            'signal_id': signal.signal_id,
                            'action': 'expire',
                            'new_status': SignalStatus.EXPIRED,
                            'symbol': signal.symbol
                        })
                        continue
                    
                    # 檢查價格觸及止損/止盈（需要從市場數據服務獲取當前價格）
                    # 這裡需要與市場數據服務整合
                    signals_to_update.append({
                        'signal_id': signal.signal_id,
                        'action': 'price_check',
                        'symbol': signal.symbol,
                        'entry_price': signal.entry_price,
                        'stop_loss_price': signal.stop_loss_price,
                        'take_profit_price': signal.take_profit_price,
                        'signal_type': signal.signal_type
                    })
                
                return signals_to_update
            finally:
                await session.close()
            
        except Exception as e:
            logger.error(f"❌ 活躍信號監控失敗: {e}")
            return []

    async def cleanup_expired_details(self, days_to_keep: int = 7) -> int:
        """
        🧹 清理過期的詳細記錄
        
        刪除超過指定天數的詳細記錄（但保留摘要統計）
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            session = await db_manager.create_session()
            try:
                from sqlalchemy import select, delete
                stmt = delete(SniperSignalDetails).where(SniperSignalDetails.created_at < cutoff_date)
                result = await session.execute(stmt)
                deleted_count = result.rowcount
                
                await session.commit()
                
                logger.info(f"✅ 清理完成: 刪除了 {deleted_count} 條過期的詳細記錄")
                return deleted_count
            finally:
                await session.close()
            
        except Exception as e:
            logger.error(f"❌ 清理過期記錄失敗: {e}")
            return 0

class SniperSignalAnalyzer:
    """
    📊 狙擊手信號分析器
    
    負責：
    1. 生成每日統計摘要
    2. 計算性能指標
    3. 趨勢分析
    4. 勝率統計
    """
    
    async def generate_daily_summary(self, target_date: datetime) -> bool:
        """
        📈 生成指定日期的每日統計摘要
        """
        try:
            start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            session = await db_manager.create_session()
            try:
                # 查詢當日所有信號
                from sqlalchemy import select
                stmt = select(SniperSignalDetails).where(
                    and_(
                        SniperSignalDetails.created_at >= start_date,
                        SniperSignalDetails.created_at < end_date
                    )
                )
                result = await session.execute(stmt)
                daily_signals = result.scalars().all()
                
                # 按交易對和時間框架分組統計
                summary_data = {}
                
                for signal in daily_signals:
                    key = (signal.symbol, signal.timeframe)
                    
                    if key not in summary_data:
                        summary_data[key] = {
                            'symbol': signal.symbol,
                            'timeframe': signal.timeframe,
                            'total_signals': 0,
                            'high_quality_signals': 0,
                            'medium_quality_signals': 0,
                            'low_quality_signals': 0,
                            'hit_tp_count': 0,
                            'hit_sl_count': 0,
                            'expired_count': 0,
                            'cancelled_count': 0,
                            'pnl_list': [],
                            'signal_strength_list': [],
                            'confluence_list': [],
                            'risk_reward_list': [],
                            'volatility_list': [],
                            'atr_list': [],
                            'layer_one_time_list': [],
                            'layer_two_time_list': [],
                            'pass_rate_list': []
                        }
                    
                    data = summary_data[key]
                    data['total_signals'] += 1
                    
                    # 品質統計
                    if signal.signal_quality == SignalQuality.HIGH:
                        data['high_quality_signals'] += 1
                    elif signal.signal_quality == SignalQuality.MEDIUM:
                        data['medium_quality_signals'] += 1
                    else:
                        data['low_quality_signals'] += 1
                    
                    # 結果統計
                    if signal.status == SignalStatus.HIT_TP:
                        data['hit_tp_count'] += 1
                    elif signal.status == SignalStatus.HIT_SL:
                        data['hit_sl_count'] += 1
                    elif signal.status == SignalStatus.EXPIRED:
                        data['expired_count'] += 1
                    elif signal.status == SignalStatus.CANCELLED:
                        data['cancelled_count'] += 1
                    
                    # 收集數值用於平均計算
                    if signal.pnl_percentage is not None:
                        data['pnl_list'].append(signal.pnl_percentage)
                    data['signal_strength_list'].append(signal.signal_strength)
                    data['confluence_list'].append(signal.confluence_count)
                    data['risk_reward_list'].append(signal.risk_reward_ratio)
                    data['volatility_list'].append(signal.market_volatility)
                    data['atr_list'].append(signal.atr_value)
                    
                    if signal.layer_one_time:
                        data['layer_one_time_list'].append(signal.layer_one_time)
                    if signal.layer_two_time:
                        data['layer_two_time_list'].append(signal.layer_two_time)
                    if signal.pass_rate:
                        data['pass_rate_list'].append(signal.pass_rate)
                
                # 創建或更新摘要記錄
                for (symbol, timeframe), data in summary_data.items():
                    # 計算統計指標
                    total_results = data['hit_tp_count'] + data['hit_sl_count']
                    win_rate = data['hit_tp_count'] / total_results if total_results > 0 else 0.0
                    
                    # 檢查是否已存在摘要記錄
                    from sqlalchemy import select
                    stmt = select(SniperSignalSummary).where(
                        and_(
                            SniperSignalSummary.symbol == symbol,
                            SniperSignalSummary.date == start_date,
                            SniperSignalSummary.timeframe == timeframe
                        )
                    )
                    result = await session.execute(stmt)
                    existing_summary = result.scalar_one_or_none()
                    
                    if existing_summary:
                        # 更新現有記錄
                        summary = existing_summary
                    else:
                        # 創建新記錄
                        summary = SniperSignalSummary(
                            symbol=symbol,
                            date=start_date,
                            timeframe=timeframe
                        )
                        session.add(summary)
                    
                    # 更新統計數據
                    summary.total_signals = data['total_signals']
                    summary.high_quality_signals = data['high_quality_signals']
                    summary.medium_quality_signals = data['medium_quality_signals']
                    summary.low_quality_signals = data['low_quality_signals']
                    summary.hit_tp_count = data['hit_tp_count']
                    summary.hit_sl_count = data['hit_sl_count']
                    summary.expired_count = data['expired_count']
                    summary.cancelled_count = data['cancelled_count']
                    summary.win_rate = win_rate
                    
                    # 計算平均值
                    summary.avg_pnl_percentage = sum(data['pnl_list']) / len(data['pnl_list']) if data['pnl_list'] else 0.0
                    summary.avg_signal_strength = sum(data['signal_strength_list']) / len(data['signal_strength_list'])
                    summary.avg_confluence_count = sum(data['confluence_list']) / len(data['confluence_list'])
                    summary.avg_risk_reward_ratio = sum(data['risk_reward_list']) / len(data['risk_reward_list'])
                    summary.avg_market_volatility = sum(data['volatility_list']) / len(data['volatility_list'])
                    summary.avg_atr_value = sum(data['atr_list']) / len(data['atr_list'])
                    
                    if data['layer_one_time_list']:
                        summary.avg_layer_one_time = sum(data['layer_one_time_list']) / len(data['layer_one_time_list'])
                    if data['layer_two_time_list']:
                        summary.avg_layer_two_time = sum(data['layer_two_time_list']) / len(data['layer_two_time_list'])
                    if data['pass_rate_list']:
                        summary.avg_pass_rate = sum(data['pass_rate_list']) / len(data['pass_rate_list'])
                
                await session.commit()
                
                logger.info(f"✅ 每日摘要生成完成: {target_date.date()} ({len(summary_data)} 個統計項目)")
                return True
            finally:
                await session.close()
            
        except Exception as e:
            logger.error(f"❌ 每日摘要生成失敗: {target_date.date()}, {e}")
            return False

    async def get_performance_metrics(
        self, 
        symbol: Optional[str] = None,
        timeframe: Optional[TradingTimeframe] = None,
        days: int = 30
    ) -> Dict:
        """
        📊 獲取性能指標統計
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            session = await db_manager.create_session()
            try:
                from sqlalchemy import select
                stmt = select(SniperSignalSummary).where(SniperSignalSummary.date >= start_date)
                
                if symbol:
                    stmt = stmt.where(SniperSignalSummary.symbol == symbol)
                if timeframe:
                    stmt = stmt.where(SniperSignalSummary.timeframe == timeframe)
                
                result = await session.execute(stmt)
                summaries = result.scalars().all()
                
                if not summaries:
                    return {'error': 'No data available for the specified period'}
                
                # 計算聚合統計
                total_signals = sum(s.total_signals for s in summaries)
                total_tp = sum(s.hit_tp_count for s in summaries)
                total_sl = sum(s.hit_sl_count for s in summaries)
                total_results = total_tp + total_sl
                
                overall_win_rate = total_tp / total_results if total_results > 0 else 0.0
                avg_pnl = sum(s.avg_pnl_percentage * s.total_signals for s in summaries) / total_signals if total_signals > 0 else 0.0
                
                return {
                    'period_days': days,
                    'total_signals': total_signals,
                    'total_profitable': total_tp,
                    'total_losing': total_sl,
                    'overall_win_rate': round(overall_win_rate * 100, 2),
                    'average_pnl_percentage': round(avg_pnl, 2),
                    'high_quality_percentage': round(sum(s.high_quality_signals for s in summaries) / total_signals * 100, 2) if total_signals > 0 else 0,
                    'average_signal_strength': round(sum(s.avg_signal_strength * s.total_signals for s in summaries) / total_signals, 3) if total_signals > 0 else 0,
                    'average_confluence': round(sum(s.avg_confluence_count * s.total_signals for s in summaries) / total_signals, 1) if total_signals > 0 else 0,
                    'symbols_analyzed': len(set(s.symbol for s in summaries)),
                    'timeframes_used': len(set(s.timeframe for s in summaries))
                }
            finally:
                await session.close()
                
        except Exception as e:
            logger.error(f"❌ 性能指標獲取失敗: {e}")
            return {'error': str(e)}

# 全局實例
sniper_signal_tracker = SniperSignalTracker()
sniper_signal_analyzer = SniperSignalAnalyzer()
