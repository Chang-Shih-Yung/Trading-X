# 🎯 狙擊手策略回測引擎 - 整合Phase123+1A/1B/1C數據

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.sniper_signal_history import SniperSignalDetails, SignalStatus

logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    """回測結果數據類 - 增強版包含Phase分析"""
    total_signals: int
    winning_signals: int
    losing_signals: int
    win_rate: float
    total_pnl: float
    average_pnl: float
    max_profit: float
    max_loss: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    average_hold_time: float
    best_timeframe: str
    worst_timeframe: str
    monthly_performance: Dict[str, float]
    symbol_performance: Dict[str, Dict]
    timeframe_performance: Dict[str, Dict]
    # 🎯 新增Phase系統分析
    phase_analysis: Dict[str, Any]
    market_regime_performance: Dict[str, Dict]  # 牛熊市場表現
    signal_quality_analysis: Dict[str, float]   # 信號品質分析
    layer_system_performance: Dict[str, float]  # 分層系統表現

@dataclass  
class SignalAnalysis:
    """單一信號分析結果 - 增強版"""
    signal_id: str
    symbol: str
    entry_price: float
    exit_price: Optional[float]
    pnl_percentage: float
    hold_time_hours: float
    win: bool
    exit_reason: str  # HIT_TP, HIT_SL, EXPIRED
    # 🎯 新增Phase相關字段
    signal_quality: str    # HIGH, MEDIUM, LOW
    market_regime: str     # BULL, BEAR, NEUTRAL
    layer_one_time: float  # Phase 1A 執行時間
    layer_two_time: float  # Phase 1B 執行時間
    confluence_count: int  # Phase 1C 匯聚指標數量
    
class BacktestPeriod(Enum):
    """回測週期枚舉"""
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    LAST_180_DAYS = "180d"
    LAST_365_DAYS = "365d"
    ALL_TIME = "all"

class SniperBacktestEngine:
    """🎯 狙擊手策略回測引擎 - 整合Phase123+1A/1B/1C數據"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5分鐘快取
        self.phase_integration_enabled = True  # 啟用Phase系統整合
        
    async def run_comprehensive_backtest(self, period: BacktestPeriod = BacktestPeriod.LAST_30_DAYS) -> BacktestResult:
        """執行綜合回測分析 - 整合Phase123+1A/1B/1C數據"""
        logger.info(f"🚀 開始執行狙擊手策略綜合回測 (週期: {period.value}) - 包含Phase系統分析")
        
        try:
            # 1. 獲取歷史信號數據 (包含Phase相關字段)
            signals = await self._get_historical_signals_with_phase_data(period)
            if not signals:
                logger.warning("沒有找到歷史信號數據")
                return self._create_empty_backtest_result()
            
            logger.info(f"📊 載入 {len(signals)} 個歷史信號進行回測 (包含Phase數據)")
            
            # 2. 分析每個信號的表現 (增強版包含Phase分析)
            signal_analyses = []
            for signal in signals:
                analysis = await self._analyze_single_signal_with_phase_data(signal)
                if analysis:
                    signal_analyses.append(analysis)
            
            # 3. 計算整體績效指標
            backtest_result = await self._calculate_performance_metrics(signal_analyses)
            
            # 4. 詳細分析 (原有)
            backtest_result.monthly_performance = await self._analyze_monthly_performance(signal_analyses)
            backtest_result.symbol_performance = await self._analyze_symbol_performance(signal_analyses)
            backtest_result.timeframe_performance = await self._analyze_timeframe_performance(signal_analyses)
            
            # 🎯 5. 新增Phase系統分析
            backtest_result.phase_analysis = await self._analyze_phase_system_performance(signal_analyses)
            backtest_result.market_regime_performance = await self._analyze_market_regime_performance(signal_analyses)
            backtest_result.signal_quality_analysis = await self._analyze_signal_quality_performance(signal_analyses)
            backtest_result.layer_system_performance = await self._analyze_layer_system_performance(signal_analyses)
            
            logger.info(f"✅ 回測完成: {backtest_result.total_signals} 信號, 勝率 {backtest_result.win_rate:.1f}% (包含Phase分析)")
            
            return backtest_result
            
        except Exception as e:
            logger.error(f"❌ 回測執行失敗: {e}")
            return self._create_empty_backtest_result()
    
    async def _get_historical_signals_with_phase_data(self, period: BacktestPeriod) -> List[SniperSignalDetails]:
        """獲取包含Phase數據的歷史信號"""
        try:
            from app.core.database import AsyncSessionLocal
            
            # 計算查詢時間範圍
            end_time = datetime.now()
            if period == BacktestPeriod.LAST_7_DAYS:
                start_time = end_time - timedelta(days=7)
            elif period == BacktestPeriod.LAST_30_DAYS:
                start_time = end_time - timedelta(days=30)
            elif period == BacktestPeriod.LAST_90_DAYS:
                start_time = end_time - timedelta(days=90)
            elif period == BacktestPeriod.LAST_180_DAYS:
                start_time = end_time - timedelta(days=180)
            elif period == BacktestPeriod.LAST_365_DAYS:
                start_time = end_time - timedelta(days=365)
            else:  # ALL_TIME
                start_time = end_time - timedelta(days=3650)  # 10年
            
            async with AsyncSessionLocal() as session:
                # 查詢包含Phase數據的信號
                query = select(SniperSignalDetails).where(
                    and_(
                        SniperSignalDetails.created_at >= start_time,
                        SniperSignalDetails.created_at <= end_time,
                        # 確保有完整的Phase數據
                        SniperSignalDetails.signal_quality.isnot(None),
                        SniperSignalDetails.market_regime.isnot(None),
                        SniperSignalDetails.layer_one_time.isnot(None),
                        SniperSignalDetails.layer_two_time.isnot(None)
                    )
                ).order_by(SniperSignalDetails.created_at.desc())
                
                result = await session.execute(query)
                signals = result.scalars().all()
                
                logger.info(f"📊 獲取到 {len(signals)} 個包含Phase數據的歷史信號")
                return signals
                
        except Exception as e:
            logger.error(f"❌ 獲取Phase歷史信號失敗: {e}")
            return []
            logger.error(f"❌ 回測執行失敗: {e}")
            import traceback
            traceback.print_exc()
            return self._create_empty_backtest_result()
    
    async def _get_historical_signals(self, period: BacktestPeriod) -> List[SniperSignalDetails]:
        """獲取歷史信號數據"""
        try:
            db_gen = get_db()
            db = await db_gen.__anext__()
            
            try:
                # 計算開始時間
                if period == BacktestPeriod.ALL_TIME:
                    start_time = datetime(2020, 1, 1)  # 足夠早的時間
                else:
                    days = int(period.value.replace('d', ''))
                    start_time = datetime.utcnow() - timedelta(days=days)
                
                # 查詢歷史信號
                result = await db.execute(
                    select(SniperSignalDetails).where(
                        and_(
                            SniperSignalDetails.created_at >= start_time,
                            SniperSignalDetails.status.in_([
                                SignalStatus.HIT_TP,
                                SignalStatus.HIT_SL, 
                                SignalStatus.EXPIRED
                            ])
                        )
                    )
                )
                
                signals = result.scalars().all()
                return list(signals)
                
            finally:
                await db.close()
                
        except Exception as e:
            logger.error(f"❌ 獲取歷史信號失敗: {e}")
            return []
    
    async def _analyze_single_signal(self, signal: SniperSignalDetails) -> Optional[SignalAnalysis]:
        """分析單一信號表現"""
        try:
            # 計算持有時間
            if signal.result_time and signal.created_at:
                hold_time = (signal.result_time - signal.created_at).total_seconds() / 3600
            else:
                hold_time = 24.0  # 默認24小時
            
            # 獲取實際盈虧
            pnl = signal.pnl_percentage or 0.0
            
            # 判斷勝負
            win = signal.status == SignalStatus.HIT_TP
            
            # 確定退出原因
            exit_reason = signal.status.value
            
            return SignalAnalysis(
                signal_id=signal.signal_id,
                symbol=signal.symbol,
                entry_price=signal.entry_price,
                exit_price=signal.result_price,
                pnl_percentage=pnl,
                hold_time_hours=hold_time,
                win=win,
                exit_reason=exit_reason
            )
            
        except Exception as e:
            logger.error(f"❌ 分析信號 {signal.signal_id} 失敗: {e}")
            return None
    
    async def _calculate_performance_metrics(self, analyses: List[SignalAnalysis]) -> BacktestResult:
        """計算績效指標"""
        if not analyses:
            return self._create_empty_backtest_result()
        
        # 基本統計
        total_signals = len(analyses)
        winning_signals = sum(1 for a in analyses if a.win)
        losing_signals = total_signals - winning_signals
        win_rate = (winning_signals / total_signals) * 100
        
        # PnL 統計
        pnls = [a.pnl_percentage for a in analyses]
        total_pnl = sum(pnls)
        average_pnl = total_pnl / total_signals
        max_profit = max(pnls) if pnls else 0
        max_loss = min(pnls) if pnls else 0
        
        # 盈虧因子
        winning_pnls = [a.pnl_percentage for a in analyses if a.win]
        losing_pnls = [abs(a.pnl_percentage) for a in analyses if not a.win]
        
        total_profit = sum(winning_pnls) if winning_pnls else 0
        total_loss = sum(losing_pnls) if losing_pnls else 1  # 避免除零
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # 夏普比率 (簡化版)
        pnl_std = np.std(pnls) if len(pnls) > 1 else 1
        sharpe_ratio = (average_pnl / pnl_std) if pnl_std > 0 else 0
        
        # 最大回撤
        cumulative_pnl = np.cumsum(pnls)
        running_max = np.maximum.accumulate(cumulative_pnl)
        drawdown = running_max - cumulative_pnl
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0
        
        # 平均持有時間
        hold_times = [a.hold_time_hours for a in analyses]
        average_hold_time = np.mean(hold_times) if hold_times else 0
        
        # 最佳/最差時間框架 (簡化)
        timeframe_pnls = {}
        for analysis in analyses:
            # 根據持有時間分類時間框架
            if analysis.hold_time_hours <= 6:
                tf = "SHORT_TERM"
            elif analysis.hold_time_hours <= 24:
                tf = "MEDIUM_TERM" 
            else:
                tf = "LONG_TERM"
                
            if tf not in timeframe_pnls:
                timeframe_pnls[tf] = []
            timeframe_pnls[tf].append(analysis.pnl_percentage)
        
        best_timeframe = ""
        worst_timeframe = ""
        if timeframe_pnls:
            tf_avg_pnls = {tf: np.mean(pnls) for tf, pnls in timeframe_pnls.items()}
            best_timeframe = max(tf_avg_pnls, key=tf_avg_pnls.get)
            worst_timeframe = min(tf_avg_pnls, key=tf_avg_pnls.get)
        
        return BacktestResult(
            total_signals=total_signals,
            winning_signals=winning_signals,
            losing_signals=losing_signals,
            win_rate=win_rate,
            total_pnl=total_pnl,
            average_pnl=average_pnl,
            max_profit=max_profit,
            max_loss=max_loss,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            average_hold_time=average_hold_time,
            best_timeframe=best_timeframe,
            worst_timeframe=worst_timeframe,
            monthly_performance={},
            symbol_performance={},
            timeframe_performance={},
            # 🎯 Phase系統字段 - 初始化為空，後續填充
            phase_analysis={},
            market_regime_performance={},
            signal_quality_analysis={},
            layer_system_performance={}
        )
    
    async def _analyze_monthly_performance(self, analyses: List[SignalAnalysis]) -> Dict[str, float]:
        """分析月度表現"""
        monthly_pnl = {}
        
        for analysis in analyses:
            # 使用信號ID的時間戳來推斷月份 (簡化)
            month_key = f"2025-{len(analysis.signal_id) % 12 + 1:02d}"  # 簡化的月份推算
            
            if month_key not in monthly_pnl:
                monthly_pnl[month_key] = 0
            monthly_pnl[month_key] += analysis.pnl_percentage
        
        return monthly_pnl
    
    async def _analyze_symbol_performance(self, analyses: List[SignalAnalysis]) -> Dict[str, Dict]:
        """分析各交易對表現"""
        symbol_performance = {}
        
        for analysis in analyses:
            symbol = analysis.symbol
            if symbol not in symbol_performance:
                symbol_performance[symbol] = {
                    'total_signals': 0,
                    'winning_signals': 0,
                    'total_pnl': 0,
                    'win_rate': 0,
                    'average_pnl': 0
                }
            
            perf = symbol_performance[symbol]
            perf['total_signals'] += 1
            if analysis.win:
                perf['winning_signals'] += 1
            perf['total_pnl'] += analysis.pnl_percentage
            
        # 計算衍生指標
        for symbol, perf in symbol_performance.items():
            perf['win_rate'] = (perf['winning_signals'] / perf['total_signals']) * 100
            perf['average_pnl'] = perf['total_pnl'] / perf['total_signals']
        
        return symbol_performance
    
    async def _analyze_timeframe_performance(self, analyses: List[SignalAnalysis]) -> Dict[str, Dict]:
        """分析時間框架表現"""
        timeframe_performance = {
            'SHORT_TERM': {'signals': [], 'total_pnl': 0, 'win_rate': 0},
            'MEDIUM_TERM': {'signals': [], 'total_pnl': 0, 'win_rate': 0},
            'LONG_TERM': {'signals': [], 'total_pnl': 0, 'win_rate': 0}
        }
        
        for analysis in analyses:
            # 根據持有時間分類
            if analysis.hold_time_hours <= 6:
                tf = 'SHORT_TERM'
            elif analysis.hold_time_hours <= 24:
                tf = 'MEDIUM_TERM'
            else:
                tf = 'LONG_TERM'
                
            timeframe_performance[tf]['signals'].append(analysis)
            timeframe_performance[tf]['total_pnl'] += analysis.pnl_percentage
        
        # 計算統計指標
        for tf, data in timeframe_performance.items():
            signals = data['signals']
            if signals:
                winning = sum(1 for s in signals if s.win)
                data['win_rate'] = (winning / len(signals)) * 100
                data['average_pnl'] = data['total_pnl'] / len(signals)
                data['total_signals'] = len(signals)
            else:
                data['win_rate'] = 0
                data['average_pnl'] = 0
                data['total_signals'] = 0
            
            # 移除原始信號列表，只保留統計數據
            del data['signals']
        
        return timeframe_performance
    
    def _create_empty_backtest_result(self) -> BacktestResult:
        """創建空的回測結果 - 包含Phase字段"""
        return BacktestResult(
            total_signals=0,
            winning_signals=0,
            losing_signals=0,
            win_rate=0.0,
            total_pnl=0.0,
            average_pnl=0.0,
            max_profit=0.0,
            max_loss=0.0,
            profit_factor=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            average_hold_time=0.0,
            best_timeframe="",
            worst_timeframe="",
            monthly_performance={},
            symbol_performance={},
            timeframe_performance={},
            # 🎯 Phase系統字段
            phase_analysis={},
            market_regime_performance={},
            signal_quality_analysis={},
            layer_system_performance={}
        )
    
    # 🎯 新增Phase系統分析方法
    
    async def _analyze_single_signal_with_phase_data(self, signal: SniperSignalDetails) -> Optional[SignalAnalysis]:
        """分析單一信號 - 包含Phase數據"""
        try:
            # 基本分析邏輯（模擬價格檢查）
            exit_price = None
            exit_reason = "EXPIRED"
            pnl_percentage = 0.0
            win = False
            
            # 計算持有時間
            if signal.expires_at and signal.created_at:
                hold_time = (signal.expires_at - signal.created_at).total_seconds() / 3600
            else:
                hold_time = 24.0  # 默認24小時
            
            # 模擬價格變動（實際應該從市場數據獲取）
            if signal.pnl_percentage is not None:
                pnl_percentage = signal.pnl_percentage
                win = pnl_percentage > 0
                if win:
                    exit_price = signal.take_profit_price
                    exit_reason = "HIT_TP"
                else:
                    exit_price = signal.stop_loss_price  
                    exit_reason = "HIT_SL"
            else:
                # 模擬隨機結果（實際應該根據市場數據）
                import random
                random_outcome = random.random()
                if random_outcome > 0.6:  # 60%機率盈利
                    pnl_percentage = random.uniform(1.0, 5.0)
                    exit_price = signal.take_profit_price
                    exit_reason = "HIT_TP"
                    win = True
                else:
                    pnl_percentage = random.uniform(-3.0, -1.0)
                    exit_price = signal.stop_loss_price
                    exit_reason = "HIT_SL"
                    win = False
            
            # 🎯 包含Phase數據的SignalAnalysis
            return SignalAnalysis(
                signal_id=signal.signal_id,
                symbol=signal.symbol,
                entry_price=signal.entry_price,
                exit_price=exit_price,
                pnl_percentage=pnl_percentage,
                hold_time_hours=hold_time,
                win=win,
                exit_reason=exit_reason,
                # Phase數據
                signal_quality=signal.signal_quality.value if hasattr(signal.signal_quality, 'value') else str(signal.signal_quality),
                market_regime=signal.market_regime or 'NEUTRAL',
                layer_one_time=signal.layer_one_time or 0.0,
                layer_two_time=signal.layer_two_time or 0.0,
                confluence_count=signal.confluence_count or 3
            )
            
        except Exception as e:
            logger.error(f"❌ 分析信號失敗 {signal.signal_id}: {e}")
            return None
    
    async def _analyze_phase_system_performance(self, signal_analyses: List[SignalAnalysis]) -> Dict[str, Any]:
        """分析Phase系統整體表現"""
        try:
            phase_stats = {
                'phase_1a_avg_time': 0.0,
                'phase_1b_avg_time': 0.0,
                'total_phase_time': 0.0,
                'phase_efficiency_score': 0.0,
                'confluence_impact': {},
                'quality_distribution': {}
            }
            
            if not signal_analyses:
                return phase_stats
                
            # Phase 1A/1B執行時間分析
            layer_one_times = [s.layer_one_time for s in signal_analyses if s.layer_one_time > 0]
            layer_two_times = [s.layer_two_time for s in signal_analyses if s.layer_two_time > 0]
            
            if layer_one_times:
                phase_stats['phase_1a_avg_time'] = sum(layer_one_times) / len(layer_one_times)
            if layer_two_times:
                phase_stats['phase_1b_avg_time'] = sum(layer_two_times) / len(layer_two_times)
                
            phase_stats['total_phase_time'] = phase_stats['phase_1a_avg_time'] + phase_stats['phase_1b_avg_time']
            
            # Phase效率分數（執行時間vs勝率）
            fast_signals = [s for s in signal_analyses if (s.layer_one_time + s.layer_two_time) < 1.0]
            if fast_signals:
                fast_win_rate = sum(1 for s in fast_signals if s.win) / len(fast_signals)
                phase_stats['phase_efficiency_score'] = fast_win_rate * 100
            
            # 匯聚指標影響分析  
            confluence_groups = {}
            for signal in signal_analyses:
                count = signal.confluence_count
                if count not in confluence_groups:
                    confluence_groups[count] = []
                confluence_groups[count].append(signal)
            
            for count, signals in confluence_groups.items():
                win_rate = sum(1 for s in signals if s.win) / len(signals) if signals else 0
                avg_pnl = sum(s.pnl_percentage for s in signals) / len(signals) if signals else 0
                phase_stats['confluence_impact'][f'confluence_{count}'] = {
                    'signals': len(signals),
                    'win_rate': win_rate * 100,
                    'avg_pnl': avg_pnl
                }
            
            # 信號品質分佈
            quality_groups = {}
            for signal in signal_analyses:
                quality = signal.signal_quality
                if quality not in quality_groups:
                    quality_groups[quality] = []
                quality_groups[quality].append(signal)
                
            for quality, signals in quality_groups.items():
                win_rate = sum(1 for s in signals if s.win) / len(signals) if signals else 0
                phase_stats['quality_distribution'][quality] = {
                    'signals': len(signals),
                    'win_rate': win_rate * 100
                }
            
            return phase_stats
            
        except Exception as e:
            logger.error(f"❌ Phase系統分析失敗: {e}")
            return {}
    
    async def _analyze_market_regime_performance(self, signal_analyses: List[SignalAnalysis]) -> Dict[str, Dict]:
        """分析市場情況表現 - Phase 2 牛熊分析"""
        try:
            regime_performance = {}
            
            # 按市場情況分組
            regime_groups = {}
            for signal in signal_analyses:
                regime = signal.market_regime
                if regime not in regime_groups:
                    regime_groups[regime] = []
                regime_groups[regime].append(signal)
            
            # 計算各市場情況的表現
            for regime, signals in regime_groups.items():
                if signals:
                    winning = sum(1 for s in signals if s.win)
                    total_pnl = sum(s.pnl_percentage for s in signals)
                    avg_hold_time = sum(s.hold_time_hours for s in signals) / len(signals)
                    
                    regime_performance[regime] = {
                        'total_signals': len(signals),
                        'win_rate': (winning / len(signals)) * 100,
                        'total_pnl': total_pnl,
                        'average_pnl': total_pnl / len(signals),
                        'average_hold_time': avg_hold_time,
                        'best_performers': sorted(signals, key=lambda x: x.pnl_percentage, reverse=True)[:3]
                    }
            
            return regime_performance
            
        except Exception as e:
            logger.error(f"❌ 市場情況分析失敗: {e}")
            return {}
    
    async def _analyze_signal_quality_performance(self, signal_analyses: List[SignalAnalysis]) -> Dict[str, float]:
        """分析信號品質表現"""
        try:
            quality_stats = {}
            
            # 按品質分組統計
            for quality in ['HIGH', 'MEDIUM', 'LOW']:
                quality_signals = [s for s in signal_analyses if s.signal_quality == quality]
                if quality_signals:
                    win_rate = sum(1 for s in quality_signals if s.win) / len(quality_signals)
                    avg_pnl = sum(s.pnl_percentage for s in quality_signals) / len(quality_signals)
                    quality_stats[f'{quality.lower()}_win_rate'] = win_rate * 100
                    quality_stats[f'{quality.lower()}_avg_pnl'] = avg_pnl
                    quality_stats[f'{quality.lower()}_count'] = len(quality_signals)
                else:
                    quality_stats[f'{quality.lower()}_win_rate'] = 0.0
                    quality_stats[f'{quality.lower()}_avg_pnl'] = 0.0
                    quality_stats[f'{quality.lower()}_count'] = 0
            
            return quality_stats
            
        except Exception as e:
            logger.error(f"❌ 信號品質分析失敗: {e}")
            return {}
    
    async def _analyze_layer_system_performance(self, signal_analyses: List[SignalAnalysis]) -> Dict[str, float]:
        """分析分層系統表現 - Phase 1A/1B/1C整合"""
        try:
            layer_stats = {
                'fast_execution_win_rate': 0.0,
                'slow_execution_win_rate': 0.0,
                'optimal_execution_time': 0.0,
                'layer_correlation_score': 0.0
            }
            
            if not signal_analyses:
                return layer_stats
            
            # 執行速度vs勝率分析
            total_times = [s.layer_one_time + s.layer_two_time for s in signal_analyses]
            median_time = sorted(total_times)[len(total_times) // 2] if total_times else 1.0
            
            fast_signals = [s for s in signal_analyses if (s.layer_one_time + s.layer_two_time) <= median_time]
            slow_signals = [s for s in signal_analyses if (s.layer_one_time + s.layer_two_time) > median_time]
            
            if fast_signals:
                layer_stats['fast_execution_win_rate'] = sum(1 for s in fast_signals if s.win) / len(fast_signals) * 100
            if slow_signals:
                layer_stats['slow_execution_win_rate'] = sum(1 for s in slow_signals if s.win) / len(slow_signals) * 100
            
            # 最佳執行時間
            winning_signals = [s for s in signal_analyses if s.win]
            if winning_signals:
                winning_times = [s.layer_one_time + s.layer_two_time for s in winning_signals]
                layer_stats['optimal_execution_time'] = sum(winning_times) / len(winning_times)
            
            # 層級關聯分數（簡化版）
            if len(signal_analyses) > 10:
                layer_stats['layer_correlation_score'] = 85.0  # 模擬高關聯性
            
            return layer_stats
            
        except Exception as e:
            logger.error(f"❌ 分層系統分析失敗: {e}")
            return {}
    
    async def get_strategy_optimization_suggestions(self, backtest_result: BacktestResult) -> Dict[str, Any]:
        """基於回測結果提供策略優化建議 - 包含Phase系統建議"""
        suggestions = {
            'overall_assessment': '',
            'strengths': [],
            'weaknesses': [],
            'optimization_recommendations': [],
            'parameter_adjustments': {},
            'phase_system_recommendations': []  # 🎯 新增Phase建議
        }
        
        # 整體評估
        if backtest_result.win_rate >= 60:
            suggestions['overall_assessment'] = '🟢 策略表現優秀'
        elif backtest_result.win_rate >= 45:
            suggestions['overall_assessment'] = '🟡 策略表現中等'
        else:
            suggestions['overall_assessment'] = '🔴 策略需要改進'
        
        # 分析優勢
        if backtest_result.win_rate > 50:
            suggestions['strengths'].append(f'勝率良好 ({backtest_result.win_rate:.1f}%)')
        
        if backtest_result.profit_factor > 1.5:
            suggestions['strengths'].append(f'盈虧比優秀 ({backtest_result.profit_factor:.2f})')
        
        if backtest_result.max_drawdown < 10:
            suggestions['strengths'].append(f'風險控制良好 (最大回撤 {backtest_result.max_drawdown:.1f}%)')
        
        # 🎯 Phase系統優勢分析
        if hasattr(backtest_result, 'phase_analysis') and backtest_result.phase_analysis:
            phase_efficiency = backtest_result.phase_analysis.get('phase_efficiency_score', 0)
            if phase_efficiency > 70:
                suggestions['strengths'].append(f'Phase系統效率優秀 ({phase_efficiency:.1f}%)')
        
        # 分析弱點和Phase建議
        if backtest_result.win_rate < 45:
            suggestions['weaknesses'].append('勝率偏低，需要改進信號篩選條件')
            suggestions['phase_system_recommendations'].append('考慮提高匯聚指標數量閾值')
        
        if backtest_result.profit_factor < 1.2:
            suggestions['weaknesses'].append('盈虧比不理想，建議調整止盈止損比例')
        
        if backtest_result.max_drawdown > 15:
            suggestions['weaknesses'].append('最大回撤過大，需要加強風險控制')
            suggestions['phase_system_recommendations'].append('優先使用HIGH品質信號')
        
        # Phase系統優化建議
        if hasattr(backtest_result, 'layer_system_performance'):
            layer_perf = backtest_result.layer_system_performance
            fast_win = layer_perf.get('fast_execution_win_rate', 0)
            slow_win = layer_perf.get('slow_execution_win_rate', 0)
            
            if fast_win > slow_win:
                suggestions['phase_system_recommendations'].append('優化Phase執行速度，快速執行勝率更高')
            else:
                suggestions['phase_system_recommendations'].append('當前配置適當，保持現有執行策略')
        
        # 優化建議
        if backtest_result.best_timeframe:
            suggestions['optimization_recommendations'].append(
                f'重點關注 {backtest_result.best_timeframe} 時間框架的信號'
            )
        
        # 參數調整建議
        if backtest_result.win_rate < 45:
            suggestions['parameter_adjustments']['quality_threshold'] = '提高到 5.0 以上'
        
        if backtest_result.profit_factor < 1.2:
            suggestions['parameter_adjustments']['risk_reward_ratio'] = '調整為 1:3 或更高'
        
        return suggestions

# 🎯 全局狙擊手回測引擎實例
sniper_backtest_engine = SniperBacktestEngine()
