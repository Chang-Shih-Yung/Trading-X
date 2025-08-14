"""
🎯 Trading X - 自動回測驗證器
48小時信號驗證與動態閾值調整系統
符合 auto_backtest_config.json v1.0.0 規範
Phase5 獨立運行，與Phase1-4 協作
"""

import asyncio
import logging
import json
import time
import statistics
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
from enum import Enum
import warnings
import sys
from pathlib import Path
import aiohttp
import pandas as pd
import numpy as np

# 添加Phase1A模組路徑
sys.path.append(str(Path(__file__).parent.parent.parent / "phase1_signal_generation" / "phase1a_basic_signal_generation"))

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

# ==================== 數據結構定義 ====================

class ValidationStatus(Enum):
    """驗證狀態枚舉"""
    PENDING = "pending"
    TRACKING = "tracking"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"

class SignalPerformanceClass(Enum):
    """信號性能分類"""
    EXCELLENT = "excellent"      # 勝率≥80%, 盈虧比≥2.0
    GOOD = "good"               # 勝率70-80%, 盈虧比1.5-2.0
    MARGINAL = "marginal"       # 勝率60-70%, 盈虧比1.2-1.5
    POOR = "poor"               # 勝率<60%, 盈虧比<1.2

class MarketConditionType(Enum):
    """市場條件類型"""
    TREND_BULLISH = "trend_bullish"
    TREND_BEARISH = "trend_bearish"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"

@dataclass
class BacktestSignal:
    """回測信號數據結構"""
    signal_id: str
    symbol: str
    signal_type: str
    priority: str
    confidence: float
    win_rate_prediction: float
    entry_price: float
    entry_time: datetime
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None
    holding_duration: Optional[timedelta] = None
    status: ValidationStatus = ValidationStatus.PENDING
    market_conditions: List[str] = field(default_factory=list)
    technical_analysis: Dict[str, Any] = field(default_factory=dict)
    risk_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceMetrics:
    """性能指標"""
    win_rate: float
    profit_loss_ratio: float
    sharpe_ratio: float
    maximum_drawdown: float
    total_trades: int
    successful_trades: int
    total_return: float
    average_profit: float
    average_loss: float
    average_holding_time: timedelta
    sample_size: int
    confidence_interval: Tuple[float, float]

@dataclass
class DynamicThresholds:
    """動態閾值"""
    win_rate_threshold: float
    profit_loss_threshold: float
    confidence_threshold: float
    last_updated: datetime
    adjustment_reason: str
    market_condition_factor: float
    volatility_factor: float

@dataclass
class ValidationWindow:
    """驗證窗口"""
    start_time: datetime
    end_time: datetime
    window_hours: int
    signals_tracked: List[str]
    performance_metrics: Optional[PerformanceMetrics]
    market_conditions: List[MarketConditionType]
    validation_status: str

# ==================== 自動回測驗證器核心類 ====================

class AutoBacktestValidator:
    """自動回測驗證器"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        
        # 運行狀態
        self.is_running = False
        self.validation_window_hours = self.config['backtest_validator']['validation_window_hours']
        
        # 數據存儲
        self.active_signals = {}  # signal_id -> BacktestSignal
        self.completed_validations = deque(maxlen=1000)
        self.performance_history = deque(maxlen=100)
        self.threshold_history = deque(maxlen=50)
        
        # 動態閾值
        self.current_thresholds = self._initialize_thresholds()
        
        # 統計數據
        self.stats = {
            'total_signals_tracked': 0,
            'completed_validations': 0,
            'excellent_signals': 0,
            'good_signals': 0,
            'marginal_signals': 0,
            'poor_signals': 0,
            'threshold_adjustments': 0,
            'emergency_stops': 0
        }
        
        # 訂閱者
        self.validation_subscribers = []
        self.threshold_update_subscribers = []
        
        # 任務
        self.validator_tasks = []
        
        # 初始化Phase1A信號生成器
        self.phase1a_generator = None
        self._init_phase1a_generator()
        
        logger.info("自動回測驗證器初始化完成")
    
    def _init_phase1a_generator(self):
        """初始化Phase1A信號生成器"""
        try:
            from phase1a_basic_signal_generation import Phase1ABasicSignalGeneration
            self.phase1a_generator = Phase1ABasicSignalGeneration()
            
            # 為回測模式設置運行狀態，不需要實際的WebSocket連接
            self.phase1a_generator.is_running = True
            logger.info("✅ Phase1A信號生成器初始化成功（回測模式）")
        except ImportError as e:
            logger.error(f"❌ Phase1A模組導入失敗: {e}")
            self.phase1a_generator = None
        except Exception as e:
            logger.error(f"❌ Phase1A信號生成器初始化失敗: {e}")
            self.phase1a_generator = None
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """載入配置"""
        if config_path is None:
            # 動態取得當前檔案路徑
            current_dir = Path(__file__).parent
            config_path = str(current_dir / "auto_backtest_config.json")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"配置載入失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """預設配置"""
        return {
            "backtest_validator": {
                "validation_window_hours": 48,
                "update_frequency_minutes": 30,
                "parallel_validation": True
            },
            "validation_methodology": {
                "performance_metrics": {
                    "win_rate": {"target_threshold": 0.70},
                    "profit_loss_ratio": {"target_threshold": 1.5},
                    "sharpe_ratio": {"target_threshold": 1.0},
                    "maximum_drawdown": {"target_threshold": 0.15}
                }
            },
            "dynamic_threshold_system": {
                "adjustment_frequency_hours": 6,
                "threshold_bounds": {
                    "win_rate_min": 0.60,
                    "win_rate_max": 0.85,
                    "profit_loss_min": 1.2,
                    "profit_loss_max": 2.5
                }
            },
            "signal_categorization": {
                "excellent_signals": {
                    "win_rate_threshold": 0.80,
                    "profit_loss_threshold": 2.0
                },
                "good_signals": {
                    "win_rate_range": [0.70, 0.80],
                    "profit_loss_range": [1.5, 2.0]
                },
                "marginal_signals": {
                    "win_rate_range": [0.60, 0.70],
                    "profit_loss_range": [1.2, 1.5]
                }
            }
        }
    
    def _initialize_thresholds(self) -> DynamicThresholds:
        """初始化動態閾值"""
        performance_config = self.config['validation_methodology']['performance_metrics']
        
        return DynamicThresholds(
            win_rate_threshold=performance_config['win_rate']['target_threshold'],
            profit_loss_threshold=performance_config['profit_loss_ratio']['target_threshold'],
            confidence_threshold=0.80,
            last_updated=datetime.now(),
            adjustment_reason="initialization",
            market_condition_factor=1.0,
            volatility_factor=1.0
        )
    
    async def start_validator(self):
        """啟動自動回測驗證器"""
        if self.is_running:
            logger.warning("自動回測驗證器已在運行")
            return
        
        try:
            logger.info("啟動自動回測驗證器...")
            
            # 啟動核心任務
            self.validator_tasks = [
                asyncio.create_task(self._validation_loop()),
                asyncio.create_task(self._threshold_adjustment_loop()),
                asyncio.create_task(self._performance_analysis_loop()),
                asyncio.create_task(self._cleanup_loop()),
                asyncio.create_task(self._monitoring_loop())
            ]
            
            self.is_running = True
            logger.info("✅ 自動回測驗證器啟動成功")
            
        except Exception as e:
            logger.error(f"自動回測驗證器啟動失敗: {e}")
            await self.stop_validator()
    
    async def stop_validator(self):
        """停止自動回測驗證器"""
        logger.info("停止自動回測驗證器...")
        
        self.is_running = False
        
        # 取消所有任務
        for task in self.validator_tasks:
            if not task.done():
                task.cancel()
        
        self.validator_tasks.clear()
        logger.info("✅ 自動回測驗證器已停止")
    
    async def track_signal(self, signal_data: Dict[str, Any]) -> str:
        """開始追蹤信號"""
        try:
            signal_id = signal_data.get('signal_id', f"signal_{int(datetime.now().timestamp())}")
            
            # 創建回測信號
            backtest_signal = BacktestSignal(
                signal_id=signal_id,
                symbol=signal_data.get('symbol', 'UNKNOWN'),
                signal_type=signal_data.get('signal_type', 'UNKNOWN'),
                priority=signal_data.get('priority', 'MEDIUM'),
                confidence=signal_data.get('confidence', 0.5),
                win_rate_prediction=signal_data.get('win_rate_prediction', 0.5),
                entry_price=signal_data.get('current_price', 0.0),
                entry_time=datetime.now(),
                market_conditions=signal_data.get('market_conditions', []),
                technical_analysis=signal_data.get('technical_analysis', {}),
                risk_metrics=signal_data.get('risk_metrics', {}),
                metadata=signal_data.get('trigger_metadata', {})
            )
            
            # 設置狀態為追蹤中
            backtest_signal.status = ValidationStatus.TRACKING
            
            # 存儲信號
            self.active_signals[signal_id] = backtest_signal
            
            # 更新統計
            self.stats['total_signals_tracked'] += 1
            
            logger.info(f"📊 開始追蹤信號: {signal_id} | {backtest_signal.symbol} | 預測勝率: {backtest_signal.win_rate_prediction:.2%}")
            
            return signal_id
            
        except Exception as e:
            logger.error(f"信號追蹤失敗: {e}")
            return ""
    
    async def update_signal_price(self, symbol: str, current_price: float):
        """更新信號價格 (用於計算浮動盈虧)"""
        try:
            for signal_id, signal in self.active_signals.items():
                if signal.symbol == symbol and signal.status == ValidationStatus.TRACKING:
                    # 計算當前盈虧
                    price_change = (current_price - signal.entry_price) / signal.entry_price
                    signal.profit_loss_pct = price_change
                    signal.profit_loss = price_change * 10000  # 假設$10000投資額
                    
                    # 檢查是否達到驗證完成條件
                    await self._check_validation_completion(signal_id, current_price)
                    
        except Exception as e:
            logger.error(f"信號價格更新失敗: {e}")
    
    async def _check_validation_completion(self, signal_id: str, current_price: float):
        """檢查驗證完成條件"""
        try:
            signal = self.active_signals.get(signal_id)
            if not signal or signal.status != ValidationStatus.TRACKING:
                return
            
            now = datetime.now()
            time_elapsed = now - signal.entry_time
            
            # 檢查時間窗口
            if time_elapsed.total_seconds() >= self.validation_window_hours * 3600:
                await self._complete_validation(signal_id, current_price, "time_window_completed")
                return
            
            # 檢查止盈止損條件 (簡化版)
            if signal.profit_loss_pct is not None:
                # 止盈: +5%
                if signal.profit_loss_pct >= 0.05:
                    await self._complete_validation(signal_id, current_price, "take_profit")
                    return
                
                # 止損: -3%
                if signal.profit_loss_pct <= -0.03:
                    await self._complete_validation(signal_id, current_price, "stop_loss")
                    return
                    
        except Exception as e:
            logger.error(f"驗證完成檢查失敗: {e}")
    
    async def _complete_validation(self, signal_id: str, exit_price: float, exit_reason: str):
        """完成驗證"""
        try:
            signal = self.active_signals.get(signal_id)
            if not signal:
                return
            
            # 更新信號狀態
            signal.exit_price = exit_price
            signal.exit_time = datetime.now()
            signal.holding_duration = signal.exit_time - signal.entry_time
            signal.status = ValidationStatus.COMPLETED
            signal.metadata['exit_reason'] = exit_reason
            
            # 計算最終盈虧
            signal.profit_loss_pct = (exit_price - signal.entry_price) / signal.entry_price
            signal.profit_loss = signal.profit_loss_pct * 10000
            
            # 移動到完成列表
            self.completed_validations.append(signal)
            del self.active_signals[signal_id]
            
            # 更新統計
            self.stats['completed_validations'] += 1
            
            # 分類信號性能
            performance_class = self._classify_signal_performance(signal)
            self._update_performance_stats(performance_class)
            
            # 通知訂閱者
            await self._notify_validation_completion(signal, performance_class)
            
            logger.info(f"✅ 驗證完成: {signal_id} | {signal.symbol} | 盈虧: {signal.profit_loss_pct:.2%} | 類別: {performance_class.value}")
            
        except Exception as e:
            logger.error(f"驗證完成處理失敗: {e}")
    
    def _classify_signal_performance(self, signal: BacktestSignal) -> SignalPerformanceClass:
        """分類信號性能"""
        # 簡化的性能分類 (基於單個信號)
        profit_loss_pct = signal.profit_loss_pct or 0
        
        # 根據實際表現與預測比較
        if profit_loss_pct >= 0.03:  # 實際盈利≥3%
            if signal.win_rate_prediction >= 0.75:
                return SignalPerformanceClass.EXCELLENT
            else:
                return SignalPerformanceClass.GOOD
        elif profit_loss_pct >= 0.01:  # 實際盈利1-3%
            if signal.win_rate_prediction >= 0.60:
                return SignalPerformanceClass.GOOD
            else:
                return SignalPerformanceClass.MARGINAL
        elif profit_loss_pct >= -0.01:  # 小虧損或微盈利
            return SignalPerformanceClass.MARGINAL
        else:  # 虧損≥1%
            return SignalPerformanceClass.POOR
    
    def _update_performance_stats(self, performance_class: SignalPerformanceClass):
        """更新性能統計"""
        if performance_class == SignalPerformanceClass.EXCELLENT:
            self.stats['excellent_signals'] += 1
        elif performance_class == SignalPerformanceClass.GOOD:
            self.stats['good_signals'] += 1
        elif performance_class == SignalPerformanceClass.MARGINAL:
            self.stats['marginal_signals'] += 1
        elif performance_class == SignalPerformanceClass.POOR:
            self.stats['poor_signals'] += 1
    
    async def _notify_validation_completion(self, signal: BacktestSignal, performance_class: SignalPerformanceClass):
        """通知驗證完成"""
        validation_result = {
            'signal_id': signal.signal_id,
            'symbol': signal.symbol,
            'performance_class': performance_class.value,
            'profit_loss_pct': signal.profit_loss_pct,
            'holding_duration_hours': signal.holding_duration.total_seconds() / 3600 if signal.holding_duration else 0,
            'predicted_win_rate': signal.win_rate_prediction,
            'actual_outcome': 'win' if signal.profit_loss_pct > 0 else 'loss',
            'exit_reason': signal.metadata.get('exit_reason', 'unknown')
        }
        
        for subscriber in self.validation_subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(validation_result)
                else:
                    subscriber(validation_result)
            except Exception as e:
                logger.error(f"驗證完成通知失敗: {e}")
    
    async def _validation_loop(self):
        """驗證主循環"""
        while self.is_running:
            try:
                # 檢查過期信號
                await self._check_expired_signals()
                
                # 清理完成的驗證
                await self._cleanup_completed_validations()
                
                await asyncio.sleep(300)  # 每5分鐘檢查一次
                
            except Exception as e:
                logger.error(f"驗證循環錯誤: {e}")
                await asyncio.sleep(60)
    
    async def _check_expired_signals(self):
        """檢查過期信號"""
        now = datetime.now()
        expired_signals = []
        
        for signal_id, signal in self.active_signals.items():
            time_elapsed = now - signal.entry_time
            if time_elapsed.total_seconds() > (self.validation_window_hours + 1) * 3600:  # 超時1小時
                expired_signals.append(signal_id)
        
        for signal_id in expired_signals:
            signal = self.active_signals[signal_id]
            signal.status = ValidationStatus.EXPIRED
            signal.exit_time = now
            
            # 估算最終價格 (實際應該獲取真實價格)
            estimated_exit_price = signal.entry_price * 1.001  # 假設小幅上漲
            await self._complete_validation(signal_id, estimated_exit_price, "expired")
    
    async def _threshold_adjustment_loop(self):
        """閾值調整循環"""
        while self.is_running:
            try:
                await self._adjust_dynamic_thresholds()
                
                adjustment_hours = self.config['dynamic_threshold_system']['adjustment_frequency_hours']
                await asyncio.sleep(adjustment_hours * 3600)
                
            except Exception as e:
                logger.error(f"閾值調整循環錯誤: {e}")
                await asyncio.sleep(3600)
    
    async def _adjust_dynamic_thresholds(self):
        """調整動態閾值"""
        try:
            if len(self.completed_validations) < 20:  # 樣本量不足
                return
            
            # 計算最近的性能指標
            recent_signals = list(self.completed_validations)[-50:]  # 最近50個信號
            performance_metrics = self._calculate_performance_metrics(recent_signals)
            
            if not performance_metrics:
                return
            
            # 獲取閾值邊界
            bounds = self.config['dynamic_threshold_system']['threshold_bounds']
            
            # 計算調整因子
            adjustment_factors = self._calculate_adjustment_factors(performance_metrics)
            
            # 調整勝率閾值
            new_win_rate_threshold = self.current_thresholds.win_rate_threshold * adjustment_factors['win_rate']
            new_win_rate_threshold = max(bounds['win_rate_min'], min(bounds['win_rate_max'], new_win_rate_threshold))
            
            # 調整盈虧比閾值
            new_pl_threshold = self.current_thresholds.profit_loss_threshold * adjustment_factors['profit_loss']
            new_pl_threshold = max(bounds['profit_loss_min'], min(bounds['profit_loss_max'], new_pl_threshold))
            
            # 檢查是否需要調整
            win_rate_change = abs(new_win_rate_threshold - self.current_thresholds.win_rate_threshold)
            pl_change = abs(new_pl_threshold - self.current_thresholds.profit_loss_threshold)
            
            if win_rate_change > 0.02 or pl_change > 0.1:  # 顯著變化才調整
                old_thresholds = asdict(self.current_thresholds)
                
                self.current_thresholds.win_rate_threshold = new_win_rate_threshold
                self.current_thresholds.profit_loss_threshold = new_pl_threshold
                self.current_thresholds.last_updated = datetime.now()
                self.current_thresholds.adjustment_reason = f"performance_based_adjustment"
                
                # 記錄閾值歷史
                self.threshold_history.append({
                    'timestamp': datetime.now(),
                    'old_thresholds': old_thresholds,
                    'new_thresholds': asdict(self.current_thresholds),
                    'performance_metrics': asdict(performance_metrics)
                })
                
                self.stats['threshold_adjustments'] += 1
                
                # 通知閾值更新
                await self._notify_threshold_update()
                
                logger.info(f"🔧 動態閾值調整: 勝率 {old_thresholds['win_rate_threshold']:.3f} → {new_win_rate_threshold:.3f}, 盈虧比 {old_thresholds['profit_loss_threshold']:.2f} → {new_pl_threshold:.2f}")
            
        except Exception as e:
            logger.error(f"動態閾值調整失敗: {e}")
    
    def _calculate_performance_metrics(self, signals: List[BacktestSignal]) -> Optional[PerformanceMetrics]:
        """計算性能指標"""
        try:
            if not signals:
                return None
            
            # 基本統計
            total_trades = len(signals)
            successful_trades = len([s for s in signals if s.profit_loss_pct and s.profit_loss_pct > 0])
            win_rate = successful_trades / total_trades if total_trades > 0 else 0
            
            # 盈虧統計
            profits = [s.profit_loss_pct for s in signals if s.profit_loss_pct and s.profit_loss_pct > 0]
            losses = [abs(s.profit_loss_pct) for s in signals if s.profit_loss_pct and s.profit_loss_pct < 0]
            
            average_profit = statistics.mean(profits) if profits else 0
            average_loss = statistics.mean(losses) if losses else 0
            profit_loss_ratio = average_profit / average_loss if average_loss > 0 else float('inf')
            
            # 總回報
            total_return = sum([s.profit_loss_pct for s in signals if s.profit_loss_pct]) if signals else 0
            
            # 持有時間
            holding_times = [s.holding_duration for s in signals if s.holding_duration]
            average_holding_time = statistics.mean([ht.total_seconds() for ht in holding_times]) if holding_times else 0
            average_holding_time = timedelta(seconds=average_holding_time)
            
            # 簡化的Sharpe比率和最大回撤計算
            returns = [s.profit_loss_pct for s in signals if s.profit_loss_pct is not None]
            if len(returns) > 1:
                sharpe_ratio = statistics.mean(returns) / statistics.stdev(returns) if statistics.stdev(returns) > 0 else 0
                
                # 計算最大回撤
                cumulative_returns = []
                cumulative = 0
                for ret in returns:
                    cumulative += ret
                    cumulative_returns.append(cumulative)
                
                peak = cumulative_returns[0]
                max_drawdown = 0
                for value in cumulative_returns:
                    if value > peak:
                        peak = value
                    drawdown = (peak - value) / peak if peak != 0 else 0
                    max_drawdown = max(max_drawdown, drawdown)
            else:
                sharpe_ratio = 0
                max_drawdown = 0
            
            # 信心區間 (簡化版)
            confidence_interval = (
                max(0, win_rate - 0.1),
                min(1, win_rate + 0.1)
            )
            
            return PerformanceMetrics(
                win_rate=win_rate,
                profit_loss_ratio=profit_loss_ratio,
                sharpe_ratio=sharpe_ratio,
                maximum_drawdown=max_drawdown,
                total_trades=total_trades,
                successful_trades=successful_trades,
                total_return=total_return,
                average_profit=average_profit,
                average_loss=average_loss,
                average_holding_time=average_holding_time,
                sample_size=total_trades,
                confidence_interval=confidence_interval
            )
            
        except Exception as e:
            logger.error(f"性能指標計算失敗: {e}")
            return None
    
    def _calculate_adjustment_factors(self, performance_metrics: PerformanceMetrics) -> Dict[str, float]:
        """計算調整因子"""
        # 基於實際性能調整閾值
        target_win_rate = 0.70
        target_pl_ratio = 1.5
        
        # 勝率調整因子
        win_rate_ratio = performance_metrics.win_rate / target_win_rate
        if win_rate_ratio > 1.1:  # 表現優於目標
            win_rate_factor = 1.02  # 小幅提高閾值
        elif win_rate_ratio < 0.9:  # 表現低於目標
            win_rate_factor = 0.98  # 小幅降低閾值
        else:
            win_rate_factor = 1.0
        
        # 盈虧比調整因子
        pl_ratio = performance_metrics.profit_loss_ratio / target_pl_ratio
        if pl_ratio > 1.2:
            pl_factor = 1.03
        elif pl_ratio < 0.8:
            pl_factor = 0.97
        else:
            pl_factor = 1.0
        
        return {
            'win_rate': win_rate_factor,
            'profit_loss': pl_factor
        }
    
    async def _notify_threshold_update(self):
        """通知閾值更新"""
        threshold_update = {
            'timestamp': datetime.now().isoformat(),
            'new_thresholds': asdict(self.current_thresholds),
            'adjustment_reason': self.current_thresholds.adjustment_reason
        }
        
        for subscriber in self.threshold_update_subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(threshold_update)
                else:
                    subscriber(threshold_update)
            except Exception as e:
                logger.error(f"閾值更新通知失敗: {e}")
    
    async def _performance_analysis_loop(self):
        """性能分析循環"""
        while self.is_running:
            try:
                # 生成性能報告
                await self._generate_performance_report()
                
                await asyncio.sleep(1800)  # 每30分鐘分析一次
                
            except Exception as e:
                logger.error(f"性能分析循環錯誤: {e}")
                await asyncio.sleep(1800)
    
    async def _generate_performance_report(self):
        """生成性能報告"""
        try:
            if len(self.completed_validations) < 10:
                return
            
            recent_signals = list(self.completed_validations)[-30:]  # 最近30個信號
            performance_metrics = self._calculate_performance_metrics(recent_signals)
            
            if performance_metrics:
                self.performance_history.append({
                    'timestamp': datetime.now(),
                    'metrics': asdict(performance_metrics),
                    'sample_size': len(recent_signals)
                })
                
                # 檢查是否需要緊急停止
                await self._check_emergency_conditions(performance_metrics)
                
        except Exception as e:
            logger.error(f"性能報告生成失敗: {e}")
    
    async def _check_emergency_conditions(self, performance_metrics: PerformanceMetrics):
        """檢查緊急條件"""
        try:
            # 連續虧損檢查
            recent_signals = list(self.completed_validations)[-10:]
            consecutive_losses = 0
            
            for signal in reversed(recent_signals):
                if signal.profit_loss_pct and signal.profit_loss_pct < 0:
                    consecutive_losses += 1
                else:
                    break
            
            # 緊急停止條件
            emergency_conditions = [
                consecutive_losses >= 8,  # 連續8次虧損
                performance_metrics.win_rate < 0.3,  # 勝率低於30%
                performance_metrics.maximum_drawdown > 0.2  # 最大回撤超過20%
            ]
            
            if any(emergency_conditions):
                self.stats['emergency_stops'] += 1
                logger.warning(f"🚨 緊急條件觸發: 連續虧損{consecutive_losses}, 勝率{performance_metrics.win_rate:.2%}, 最大回撤{performance_metrics.maximum_drawdown:.2%}")
                
                # 這裡可以實現實際的緊急停止邏輯
                # await self._trigger_emergency_stop()
                
        except Exception as e:
            logger.error(f"緊急條件檢查失敗: {e}")
    
    async def _cleanup_loop(self):
        """清理循環"""
        while self.is_running:
            try:
                await self._cleanup_old_data()
                
                await asyncio.sleep(3600)  # 每小時清理一次
                
            except Exception as e:
                logger.error(f"清理循環錯誤: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_data(self):
        """清理舊數據"""
        try:
            # 清理超過保留期的數據
            cutoff_time = datetime.now() - timedelta(days=7)
            
            # 清理完成的驗證 (保留最近1000個)
            if len(self.completed_validations) > 1000:
                self.completed_validations = deque(
                    [v for v in self.completed_validations if v.exit_time and v.exit_time > cutoff_time],
                    maxlen=1000
                )
            
            # 清理性能歷史 (保留最近100個)
            if len(self.performance_history) > 100:
                self.performance_history = deque(self.performance_history, maxlen=100)
            
            # 清理閾值歷史 (保留最近50個)
            if len(self.threshold_history) > 50:
                self.threshold_history = deque(self.threshold_history, maxlen=50)
                
        except Exception as e:
            logger.error(f"數據清理失敗: {e}")
    
    async def _cleanup_completed_validations(self):
        """清理已完成的驗證"""
        # 這個方法在 _validation_loop 中調用，目前邏輯已在 _cleanup_old_data 中處理
        pass
    
    async def _monitoring_loop(self):
        """監控循環"""
        while self.is_running:
            try:
                # 記錄統計信息
                active_count = len(self.active_signals)
                completed_count = len(self.completed_validations)
                
                if active_count > 0 or completed_count > 0:
                    logger.info(f"📊 回測驗證器狀態: 追蹤中 {active_count}, 已完成 {completed_count}, 統計: {self.stats}")
                
                await asyncio.sleep(600)  # 每10分鐘報告一次
                
            except Exception as e:
                logger.error(f"監控循環錯誤: {e}")
                await asyncio.sleep(600)
    
    def subscribe_to_validations(self, callback: Callable):
        """訂閱驗證結果"""
        if callback not in self.validation_subscribers:
            self.validation_subscribers.append(callback)
            logger.info(f"新增驗證結果訂閱者: {callback.__name__}")
    
    def subscribe_to_threshold_updates(self, callback: Callable):
        """訂閱閾值更新"""
        if callback not in self.threshold_update_subscribers:
            self.threshold_update_subscribers.append(callback)
            logger.info(f"新增閾值更新訂閱者: {callback.__name__}")
    
    async def get_validator_status(self) -> Dict[str, Any]:
        """獲取驗證器狀態"""
        try:
            recent_performance = None
            if self.performance_history:
                recent_performance = self.performance_history[-1]['metrics']
            
            return {
                'is_running': self.is_running,
                'active_signals_count': len(self.active_signals),
                'completed_validations_count': len(self.completed_validations),
                'current_thresholds': asdict(self.current_thresholds),
                'recent_performance': recent_performance,
                'statistics': self.stats.copy(),
                'validation_window_hours': self.validation_window_hours,
                'configuration': {
                    'validation_window': self.validation_window_hours,
                    'update_frequency': self.config['backtest_validator']['update_frequency_minutes'],
                    'threshold_bounds': self.config['dynamic_threshold_system']['threshold_bounds']
                }
            }
            
        except Exception as e:
            logger.error(f"狀態獲取失敗: {e}")
            return {'error': str(e)}
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """獲取性能摘要"""
        try:
            if not self.completed_validations:
                return {'message': '暫無完成的驗證數據'}
            
            all_signals = list(self.completed_validations)
            performance_metrics = self._calculate_performance_metrics(all_signals)
            
            if not performance_metrics:
                return {'message': '性能指標計算失敗'}
            
            # 分類統計
            excellent_count = self.stats['excellent_signals']
            good_count = self.stats['good_signals']
            marginal_count = self.stats['marginal_signals']
            poor_count = self.stats['poor_signals']
            total_classified = excellent_count + good_count + marginal_count + poor_count
            
            return {
                'overall_performance': asdict(performance_metrics),
                'signal_classification': {
                    'excellent': {'count': excellent_count, 'percentage': excellent_count/total_classified*100 if total_classified > 0 else 0},
                    'good': {'count': good_count, 'percentage': good_count/total_classified*100 if total_classified > 0 else 0},
                    'marginal': {'count': marginal_count, 'percentage': marginal_count/total_classified*100 if total_classified > 0 else 0},
                    'poor': {'count': poor_count, 'percentage': poor_count/total_classified*100 if total_classified > 0 else 0}
                },
                'threshold_adjustments': self.stats['threshold_adjustments'],
                'emergency_stops': self.stats['emergency_stops'],
                'data_points': len(all_signals)
            }
            
        except Exception as e:
            logger.error(f"性能摘要獲取失敗: {e}")
            return {'error': str(e)}

    async def _fetch_historical_klines(self, symbol: str, interval: str = '5m', limit: int = 1000) -> pd.DataFrame:
        """
        獲取歷史K線數據用於Phase1A回測
        
        Args:
            symbol: 交易對符號 (如 'BTCUSDT')
            interval: K線間隔 ('1m', '5m', '15m', '1h', '4h', '1d')
            limit: 獲取數量限制
            
        Returns:
            pd.DataFrame: 包含OHLCV數據的DataFrame
        """
        try:
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 轉換為DataFrame
                        df = pd.DataFrame(data, columns=[
                            'open_time', 'open', 'high', 'low', 'close', 'volume',
                            'close_time', 'quote_asset_volume', 'number_of_trades',
                            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                        ])
                        
                        # 數據類型轉換
                        df['open'] = pd.to_numeric(df['open'])
                        df['high'] = pd.to_numeric(df['high'])
                        df['low'] = pd.to_numeric(df['low'])
                        df['close'] = pd.to_numeric(df['close'])
                        df['volume'] = pd.to_numeric(df['volume'])
                        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
                        
                        return df[['open_time', 'open', 'high', 'low', 'close', 'volume']]
                    else:
                        logger.error(f"獲取{symbol}歷史數據失敗: HTTP {response.status}")
                        return pd.DataFrame()
                        
        except Exception as e:
            logger.error(f"獲取歷史K線數據失敗: {e}")
            return pd.DataFrame()

    async def _run_phase1a_backtest(self, symbol: str, timeframe: str = '5m', days: int = 7) -> Dict[str, Any]:
        """
        運行Phase1A回測驗證
        
        Args:
            symbol: 交易對符號
            timeframe: 時間框架
            days: 回測天數
            
        Returns:
            Dict: 回測結果包含勝率、盈虧比等指標
        """
        try:
            # 獲取歷史數據
            historical_data = await self._fetch_historical_klines(
                symbol=symbol,
                interval=timeframe,
                limit=days * 288  # 5分鐘K線，一天288根
            )
            
            if historical_data.empty:
                return {'error': f'無法獲取{symbol}歷史數據'}
            
            # 使用Phase1A生成器生成信號
            signals = []
            for i in range(len(historical_data) - 50):  # 保留50個數據點作為緩衝
                current_data = historical_data.iloc[:i+50]  # 使用前i+50個數據點
                
                # 確保為Phase1A生成器預填充足夠的歷史數據
                if i == 0:  # 只在第一次時預填充
                    # 為Phase1A生成器預填充歷史價格數據
                    self.phase1a_generator.price_buffer[symbol] = deque(maxlen=1000)
                    for j in range(min(50, len(current_data))):
                        price_data = {
                            'timestamp': int(current_data.iloc[j]['open_time'].timestamp() * 1000),
                            'price': float(current_data.iloc[j]['close']),
                            'volume': float(current_data.iloc[j]['volume'])
                        }
                        self.phase1a_generator.price_buffer[symbol].append(price_data)
                
                try:
                    # 模擬Phase1A信號生成
                    market_data = {
                        'symbol': symbol,
                        'timestamp': int(current_data.iloc[-1]['open_time'].timestamp() * 1000),
                        'price': float(current_data.iloc[-1]['close']),
                        'high': float(current_data.iloc[-1]['high']),
                        'low': float(current_data.iloc[-1]['low']),
                        'open': float(current_data.iloc[-1]['open']),
                        'volume': float(current_data.iloc[-1]['volume']),
                        'change_percent': 0.0,
                        'bid': float(current_data.iloc[-1]['close']),
                        'ask': float(current_data.iloc[-1]['close'])
                    }
                    
                    generated_signals = await self.phase1a_generator.generate_signals(symbol, market_data)
                    
                    if generated_signals and len(generated_signals) > 0:
                        # 取第一個信號作為代表
                        signal = generated_signals[0]
                        signal_data = {
                            'timestamp': current_data.iloc[-1]['open_time'],
                            'symbol': symbol,
                            'signal_type': signal.direction,
                            'entry_price': float(current_data.iloc[-1]['close']),
                            'confidence': signal.confidence,
                            'target_price': None,  # BasicSignal 沒有此屬性，設為 None
                            'stop_loss': None      # BasicSignal 沒有此屬性，設為 None
                        }
                        signals.append(signal_data)
                        
                except Exception as e:
                    logger.warning(f"Phase1A信號生成失敗 at index {i}: {e}")
                    continue
            
            # 計算回測性能
            if not signals:
                return {'error': 'Phase1A未生成任何信號'}
            
            # 驗證信號性能
            validated_signals = []
            for signal in signals:
                # 找到信號後續價格數據進行驗證
                signal_time = signal['timestamp']
                future_data = historical_data[historical_data['open_time'] > signal_time].head(20)
                
                if len(future_data) > 0:
                    validation_result = self._validate_signal_performance(signal, future_data)
                    validated_signals.append(validation_result)
            
            # 計算統計指標
            if validated_signals:
                win_rate = sum(1 for s in validated_signals if s.get('profitable', False)) / len(validated_signals)
                total_pnl = sum(s.get('pnl_ratio', 0) for s in validated_signals)
                avg_pnl = total_pnl / len(validated_signals) if validated_signals else 0
                
                return {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'backtest_days': days,
                    'total_signals': len(validated_signals),
                    'win_rate': win_rate,
                    'avg_pnl_ratio': avg_pnl,
                    'total_pnl_ratio': total_pnl,
                    'signals': validated_signals[:10]  # 返回前10個信號作為樣本
                }
            else:
                return {'error': '無有效信號可驗證'}
                
        except Exception as e:
            logger.error(f"Phase1A回測失敗: {e}")
            return {'error': str(e)}

    def _validate_signal_performance(self, signal: Dict, future_data: pd.DataFrame) -> Dict[str, Any]:
        """
        驗證單個信號的性能表現
        
        Args:
            signal: 信號數據
            future_data: 信號後的價格數據
            
        Returns:
            Dict: 包含盈虧信息的驗證結果
        """
        try:
            entry_price = signal['entry_price']
            signal_type = signal.get('signal_type', 'buy')
            target_price = signal.get('target_price')
            stop_loss = signal.get('stop_loss')
            
            # 計算信號結果
            max_profit = 0
            max_loss = 0
            final_pnl = 0
            hit_target = False
            hit_stop = False
            
            for _, row in future_data.iterrows():
                high_price = row['high']
                low_price = row['low']
                close_price = row['close']
                
                if signal_type.lower() == 'buy':
                    # 買入信號邏輯
                    profit = (high_price - entry_price) / entry_price
                    loss = (low_price - entry_price) / entry_price
                    
                    max_profit = max(max_profit, profit)
                    max_loss = min(max_loss, loss)
                    
                    # 檢查止盈止損
                    if target_price and high_price >= target_price:
                        final_pnl = (target_price - entry_price) / entry_price
                        hit_target = True
                        break
                    elif stop_loss and low_price <= stop_loss:
                        final_pnl = (stop_loss - entry_price) / entry_price
                        hit_stop = True
                        break
                        
                    # 使用收盤價作為最終結果
                    final_pnl = (close_price - entry_price) / entry_price
                    
                else:  # sell signal
                    # 賣出信號邏輯
                    profit = (entry_price - low_price) / entry_price
                    loss = (high_price - entry_price) / entry_price
                    
                    max_profit = max(max_profit, profit)
                    max_loss = min(max_loss, loss)
                    
                    # 檢查止盈止損
                    if target_price and low_price <= target_price:
                        final_pnl = (entry_price - target_price) / entry_price
                        hit_target = True
                        break
                    elif stop_loss and high_price >= stop_loss:
                        final_pnl = (entry_price - stop_loss) / entry_price
                        hit_stop = True
                        break
                        
                    # 使用收盤價作為最終結果
                    final_pnl = (entry_price - close_price) / entry_price
            
            return {
                **signal,
                'profitable': final_pnl > 0,
                'pnl_ratio': final_pnl,
                'max_profit': max_profit,
                'max_loss': max_loss,
                'hit_target': hit_target,
                'hit_stop': hit_stop
            }
            
        except Exception as e:
            logger.error(f"信號性能驗證失敗: {e}")
            return {**signal, 'error': str(e)}

    async def run_phase1a_validation_cycle(self) -> Dict[str, Any]:
        """
        運行Phase1A驗證週期，針對多個主要加密貨幣
        
        Returns:
            Dict: 包含所有幣種回測結果的綜合報告
        """
        try:
            # 主要加密貨幣列表
            major_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT']
            
            results = {}
            overall_stats = {
                'total_signals': 0,
                'total_wins': 0,
                'total_pnl': 0,
                'symbol_count': 0
            }
            
            for symbol in major_symbols:
                logger.info(f"開始Phase1A回測驗證: {symbol}")
                
                # 運行單幣種回測
                backtest_result = await self._run_phase1a_backtest(
                    symbol=symbol,
                    timeframe='5m',
                    days=7  # 7天回測週期
                )
                
                if 'error' not in backtest_result:
                    results[symbol] = backtest_result
                    
                    # 累積統計
                    overall_stats['total_signals'] += backtest_result.get('total_signals', 0)
                    overall_stats['total_wins'] += int(backtest_result.get('win_rate', 0) * backtest_result.get('total_signals', 0))
                    overall_stats['total_pnl'] += backtest_result.get('total_pnl_ratio', 0)
                    overall_stats['symbol_count'] += 1
                    
                    logger.info(f"{symbol} Phase1A回測完成: 勝率={backtest_result.get('win_rate', 0):.2%}")
                else:
                    logger.error(f"{symbol} Phase1A回測失敗: {backtest_result.get('error')}")
                    results[symbol] = backtest_result
                
                # 短暫延遲避免API限制
                await asyncio.sleep(1)
            
            # 計算總體指標
            overall_win_rate = (overall_stats['total_wins'] / overall_stats['total_signals']) if overall_stats['total_signals'] > 0 else 0
            avg_pnl_ratio = overall_stats['total_pnl'] / overall_stats['symbol_count'] if overall_stats['symbol_count'] > 0 else 0
            
            validation_summary = {
                'validation_timestamp': datetime.now().isoformat(),
                'overall_performance': {
                    'overall_win_rate': overall_win_rate,
                    'total_signals': overall_stats['total_signals'],
                    'successful_symbols': overall_stats['symbol_count'],
                    'avg_pnl_ratio': avg_pnl_ratio,
                    'target_achieved': overall_win_rate >= 0.70  # 70%目標勝率
                },
                'symbol_results': results,
                'phase1a_integration_status': 'active'
            }
            
            # 記錄驗證結果
            logger.info(f"Phase1A驗證週期完成 - 總體勝率: {overall_win_rate:.2%}, 目標達成: {'是' if overall_win_rate >= 0.70 else '否'}")
            
            return validation_summary
            
        except Exception as e:
            logger.error(f"Phase1A驗證週期失敗: {e}")
            return {'error': str(e), 'validation_timestamp': datetime.now().isoformat()}

# ==================== 全局實例和便捷函數 ====================

# 全局自動回測驗證器實例
auto_backtest_validator = AutoBacktestValidator()

async def start_auto_backtest_validator():
    """啟動自動回測驗證器"""
    await auto_backtest_validator.start_validator()

async def stop_auto_backtest_validator():
    """停止自動回測驗證器"""
    await auto_backtest_validator.stop_validator()

async def track_signal_for_validation(signal_data: Dict[str, Any]) -> str:
    """追蹤信號進行驗證"""
    return await auto_backtest_validator.track_signal(signal_data)

async def update_signal_validation_price(symbol: str, current_price: float):
    """更新信號驗證價格"""
    await auto_backtest_validator.update_signal_price(symbol, current_price)

def subscribe_to_validation_results(callback: Callable):
    """訂閱驗證結果"""
    auto_backtest_validator.subscribe_to_validations(callback)

def subscribe_to_threshold_updates(callback: Callable):
    """訂閱閾值更新"""
    auto_backtest_validator.subscribe_to_threshold_updates(callback)

async def get_backtest_validator_status() -> Dict[str, Any]:
    """獲取回測驗證器狀態"""
    return await auto_backtest_validator.get_validator_status()

async def get_backtest_performance_summary() -> Dict[str, Any]:
    """獲取回測性能摘要"""
    return await auto_backtest_validator.get_performance_summary()

async def run_phase1a_validation() -> Dict[str, Any]:
    """運行Phase1A驗證週期"""
    return await auto_backtest_validator.run_phase1a_validation_cycle()
