"""
動態重分配算法 - Trading X Phase 3
實時監控並重新分配權重以優化交易性能
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import asyncio
import math
from collections import defaultdict, deque
import numpy as np

logger = logging.getLogger(__name__)

class ReallocationTrigger(Enum):
    """重分配觸發條件"""
    PERFORMANCE_DEGRADATION = "performance_degradation"    # 性能下降
    SIGNAL_QUALITY_CHANGE = "signal_quality_change"       # 信號品質變化
    MARKET_REGIME_SHIFT = "market_regime_shift"           # 市場制度轉換
    VOLATILITY_SPIKE = "volatility_spike"                 # 波動率突增
    CORRELATION_BREAKDOWN = "correlation_breakdown"        # 相關性破裂
    RISK_THRESHOLD_BREACH = "risk_threshold_breach"       # 風險閾值突破
    MANUAL_OVERRIDE = "manual_override"                   # 手動覆蓋

class OptimizationMethod(Enum):
    """優化方法"""
    GRADIENT_ASCENT = "gradient_ascent"           # 梯度上升
    GENETIC_ALGORITHM = "genetic_algorithm"       # 遺傳算法
    PARTICLE_SWARM = "particle_swarm"            # 粒子群優化
    BAYESIAN_OPTIMIZATION = "bayesian_optimization" # 貝葉斯優化
    ADAPTIVE_MOMENTUM = "adaptive_momentum"       # 自適應動量

@dataclass
class PerformanceMetrics:
    """性能指標"""
    symbol: str
    timeframe: str
    
    # 收益相關
    total_return: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    
    # 風險相關
    volatility: float = 0.0
    var_95: float = 0.0        # 95% VaR
    beta: float = 1.0
    
    # 交易相關
    total_trades: int = 0
    avg_trade_duration: float = 0.0
    profit_factor: float = 1.0
    
    # 信號品質
    signal_accuracy: float = 0.0
    false_positive_rate: float = 0.0
    signal_timeliness: float = 0.0
    
    # 時間戳
    measurement_time: datetime = field(default_factory=datetime.now)
    measurement_period_hours: int = 24

@dataclass
class WeightOptimizationResult:
    """權重優化結果"""
    original_weights: Dict[str, float]
    optimized_weights: Dict[str, float]
    expected_improvement: float
    confidence_score: float
    optimization_method: OptimizationMethod
    iterations: int
    convergence_achieved: bool
    
    # 詳細分析
    performance_projection: PerformanceMetrics
    risk_assessment: Dict[str, float]
    sensitivity_analysis: Dict[str, float]
    
    optimization_time: datetime = field(default_factory=datetime.now)
    explanation: str = ""

@dataclass
class ReallocationEvent:
    """重分配事件記錄"""
    event_id: str
    trigger: ReallocationTrigger
    symbol: str
    timeframe: str
    
    before_weights: Dict[str, float]
    after_weights: Dict[str, float]
    expected_impact: float
    actual_impact: Optional[float] = None
    
    trigger_data: Dict[str, Any] = field(default_factory=dict)
    event_time: datetime = field(default_factory=datetime.now)
    validation_time: Optional[datetime] = None

class DynamicReallocationEngine:
    """動態重分配引擎"""
    
    def __init__(self):
        # 性能追蹤
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.weight_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
        self.reallocation_history: deque = deque(maxlen=200)
        
        # 優化參數
        self.optimization_params = {
            "learning_rate": 0.01,
            "momentum": 0.9,
            "decay_rate": 0.95,
            "convergence_threshold": 0.001,
            "max_iterations": 100,
            "improvement_threshold": 0.02,  # 2% 最小改善要求
            "risk_penalty": 0.1
        }
        
        # 觸發閾值
        self.trigger_thresholds = {
            "performance_degradation": -0.05,      # 5% 性能下降
            "signal_quality_change": -0.10,        # 10% 品質下降
            "volatility_spike": 2.0,                # 2倍波動率增加
            "correlation_breakdown": -0.3,          # 相關性降至-0.3以下
            "risk_threshold_breach": 0.15           # 15% VaR 突破
        }
        
        # 統計數據
        self.stats = {
            "total_reallocations": 0,
            "successful_reallocations": 0,
            "total_improvement": 0.0,
            "avg_improvement": 0.0,
            "last_reallocation": None
        }
        
        # 運行狀態
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        logger.info("⚙️ 動態重分配引擎初始化完成")
    
    async def start_monitoring(self):
        """啟動動態監控"""
        if self.is_monitoring:
            logger.warning("⚠️ 動態監控已經在運行中")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("🚀 動態重分配監控已啟動")
    
    async def stop_monitoring(self):
        """停止動態監控"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("⏹️ 動態重分配監控已停止")
    
    async def _monitoring_loop(self):
        """監控循環"""
        while self.is_monitoring:
            try:
                # 檢查所有活躍的交易對和時間框架
                await self._check_reallocation_triggers()
                
                # 等待下次檢查 (每5分鐘)
                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 監控循環錯誤: {e}")
                await asyncio.sleep(60)
    
    async def _check_reallocation_triggers(self):
        """檢查重分配觸發條件"""
        # 模擬檢查多個交易對
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        timeframes = ["short", "medium", "long"]
        
        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    # 獲取最新性能指標
                    current_metrics = await self._get_performance_metrics(symbol, timeframe)
                    if not current_metrics:
                        continue
                    
                    # 檢查觸發條件
                    trigger = await self._evaluate_triggers(symbol, timeframe, current_metrics)
                    
                    if trigger:
                        logger.info(f"🎯 檢測到重分配觸發: {symbol} {timeframe} - {trigger.value}")
                        
                        # 執行重分配
                        await self.execute_reallocation(symbol, timeframe, trigger)
                        
                except Exception as e:
                    logger.error(f"❌ 檢查 {symbol} {timeframe} 觸發條件失敗: {e}")
    
    async def _get_performance_metrics(self, symbol: str, timeframe: str) -> Optional[PerformanceMetrics]:
        """獲取性能指標 (模擬實現)"""
        # 在實際實現中，這裡會從數據庫或交易引擎獲取真實的性能數據
        import random
        
        metrics = PerformanceMetrics(
            symbol=symbol,
            timeframe=timeframe,
            total_return=random.uniform(-0.1, 0.15),
            sharpe_ratio=random.uniform(0.5, 2.5),
            max_drawdown=random.uniform(-0.20, -0.05),
            win_rate=random.uniform(0.45, 0.75),
            volatility=random.uniform(0.15, 0.45),
            var_95=random.uniform(-0.08, -0.02),
            total_trades=random.randint(10, 100),
            signal_accuracy=random.uniform(0.6, 0.9),
            false_positive_rate=random.uniform(0.05, 0.25)
        )
        
        # 存儲歷史數據
        key = f"{symbol}_{timeframe}"
        self.performance_history[key].append(metrics)
        
        return metrics
    
    async def _evaluate_triggers(self, 
                               symbol: str, 
                               timeframe: str, 
                               current_metrics: PerformanceMetrics) -> Optional[ReallocationTrigger]:
        """評估是否觸發重分配"""
        key = f"{symbol}_{timeframe}"
        history = self.performance_history[key]
        
        if len(history) < 2:
            return None
        
        # 獲取歷史基準 - 修復 deque 切片問題
        history_list = list(history)[:-1]  # 轉換為列表再進行切片
        historical_avg = self._calculate_historical_average(history_list)
        
        # 檢查性能下降
        if current_metrics.total_return < historical_avg.total_return + self.trigger_thresholds["performance_degradation"]:
            return ReallocationTrigger.PERFORMANCE_DEGRADATION
        
        # 檢查信號品質變化
        if current_metrics.signal_accuracy < historical_avg.signal_accuracy + self.trigger_thresholds["signal_quality_change"]:
            return ReallocationTrigger.SIGNAL_QUALITY_CHANGE
        
        # 檢查波動率突增
        if current_metrics.volatility > historical_avg.volatility * self.trigger_thresholds["volatility_spike"]:
            return ReallocationTrigger.VOLATILITY_SPIKE
        
        # 檢查風險閾值突破
        if abs(current_metrics.var_95) > abs(historical_avg.var_95) + self.trigger_thresholds["risk_threshold_breach"]:
            return ReallocationTrigger.RISK_THRESHOLD_BREACH
        
        return None
    
    def _calculate_historical_average(self, metrics_list: List[PerformanceMetrics]) -> PerformanceMetrics:
        """計算歷史平均值"""
        if not metrics_list:
            return PerformanceMetrics("", "")
        
        avg_metrics = PerformanceMetrics(
            symbol=metrics_list[0].symbol,
            timeframe=metrics_list[0].timeframe
        )
        
        # 計算各項指標的平均值
        n = len(metrics_list)
        avg_metrics.total_return = sum(m.total_return for m in metrics_list) / n
        avg_metrics.sharpe_ratio = sum(m.sharpe_ratio for m in metrics_list) / n
        avg_metrics.max_drawdown = sum(m.max_drawdown for m in metrics_list) / n
        avg_metrics.win_rate = sum(m.win_rate for m in metrics_list) / n
        avg_metrics.volatility = sum(m.volatility for m in metrics_list) / n
        avg_metrics.var_95 = sum(m.var_95 for m in metrics_list) / n
        avg_metrics.signal_accuracy = sum(m.signal_accuracy for m in metrics_list) / n
        avg_metrics.false_positive_rate = sum(m.false_positive_rate for m in metrics_list) / n
        
        return avg_metrics
    
    async def execute_reallocation(self, 
                                 symbol: str, 
                                 timeframe: str, 
                                 trigger: ReallocationTrigger,
                                 current_weights: Dict[str, float] = None) -> Optional[WeightOptimizationResult]:
        """執行權重重分配"""
        try:
            # 獲取當前權重 (如果未提供)
            if current_weights is None:
                current_weights = await self._get_current_weights(symbol, timeframe)
            
            # 獲取性能數據
            performance_data = await self._get_performance_metrics(symbol, timeframe)
            if not performance_data:
                logger.error(f"❌ 無法獲取 {symbol} {timeframe} 的性能數據")
                return None
            
            # 選擇優化方法
            optimization_method = self._select_optimization_method(trigger, performance_data)
            
            # 執行權重優化
            optimization_result = await self._optimize_weights(
                symbol, timeframe, current_weights, performance_data, optimization_method
            )
            
            if not optimization_result:
                logger.warning(f"⚠️ {symbol} {timeframe} 權重優化失敗")
                return None
            
            # 驗證優化結果
            if optimization_result.expected_improvement < self.optimization_params["improvement_threshold"]:
                logger.info(f"📊 {symbol} {timeframe} 優化改善不足，跳過重分配")
                return optimization_result
            
            # 記錄重分配事件
            event_id = f"{symbol}_{timeframe}_{int(datetime.now().timestamp())}"
            reallocation_event = ReallocationEvent(
                event_id=event_id,
                trigger=trigger,
                symbol=symbol,
                timeframe=timeframe,
                before_weights=current_weights,
                after_weights=optimization_result.optimized_weights,
                expected_impact=optimization_result.expected_improvement,
                trigger_data={
                    "performance_metrics": performance_data.__dict__,
                    "optimization_method": optimization_method.value
                }
            )
            
            self.reallocation_history.append(reallocation_event)
            
            # 更新統計數據
            self.stats["total_reallocations"] += 1
            self.stats["last_reallocation"] = datetime.now()
            
            logger.info(f"✅ 完成權重重分配: {symbol} {timeframe} (預期改善: {optimization_result.expected_improvement:.2%})")
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"❌ 執行重分配失敗: {symbol} {timeframe} - {e}")
            return None
    
    async def _get_current_weights(self, symbol: str, timeframe: str) -> Dict[str, float]:
        """獲取當前權重 (模擬實現)"""
        # 在實際實現中，這裡會從權重引擎獲取當前權重
        return {
            "precision_filter_weight": 0.25,
            "market_condition_weight": 0.20,
            "technical_analysis_weight": 0.20,
            "regime_analysis_weight": 0.15,
            "fear_greed_weight": 0.10,
            "trend_alignment_weight": 0.05,
            "market_depth_weight": 0.03,
            "funding_rate_weight": 0.01,
            "smart_money_weight": 0.01
        }
    
    def _select_optimization_method(self, 
                                  trigger: ReallocationTrigger, 
                                  performance_data: PerformanceMetrics) -> OptimizationMethod:
        """選擇優化方法"""
        # 根據觸發條件和性能特徵選擇最適合的優化方法
        
        if trigger == ReallocationTrigger.PERFORMANCE_DEGRADATION:
            # 性能下降時使用梯度上升快速調整
            return OptimizationMethod.GRADIENT_ASCENT
        
        elif trigger == ReallocationTrigger.VOLATILITY_SPIKE:
            # 波動率突增時使用自適應動量
            return OptimizationMethod.ADAPTIVE_MOMENTUM
        
        elif trigger == ReallocationTrigger.MARKET_REGIME_SHIFT:
            # 市場制度轉換時使用遺傳算法探索新空間
            return OptimizationMethod.GENETIC_ALGORITHM
        
        elif trigger == ReallocationTrigger.SIGNAL_QUALITY_CHANGE:
            # 信號品質變化時使用粒子群優化
            return OptimizationMethod.PARTICLE_SWARM
        
        else:
            # 預設使用貝葉斯優化
            return OptimizationMethod.BAYESIAN_OPTIMIZATION
    
    async def _optimize_weights(self, 
                              symbol: str,
                              timeframe: str,
                              current_weights: Dict[str, float],
                              performance_data: PerformanceMetrics,
                              method: OptimizationMethod) -> Optional[WeightOptimizationResult]:
        """權重優化核心算法"""
        
        # 將權重轉換為向量
        weight_names = list(current_weights.keys())
        current_vector = np.array([current_weights[name] for name in weight_names])
        
        # 根據方法執行優化
        if method == OptimizationMethod.GRADIENT_ASCENT:
            optimized_vector, iterations, converged = await self._gradient_ascent_optimization(
                current_vector, performance_data
            )
        
        elif method == OptimizationMethod.ADAPTIVE_MOMENTUM:
            optimized_vector, iterations, converged = await self._adaptive_momentum_optimization(
                current_vector, performance_data
            )
        
        else:
            # 簡化實現：使用梯度上升作為預設
            optimized_vector, iterations, converged = await self._gradient_ascent_optimization(
                current_vector, performance_data
            )
        
        # 確保權重和為1
        optimized_vector = optimized_vector / np.sum(optimized_vector)
        
        # 轉換回字典格式
        optimized_weights = {
            name: max(0.001, float(weight))  # 確保最小權重
            for name, weight in zip(weight_names, optimized_vector)
        }
        
        # 計算預期改善
        current_score = self._calculate_objective_function(current_vector, performance_data)
        optimized_score = self._calculate_objective_function(optimized_vector, performance_data)
        expected_improvement = (optimized_score - current_score) / abs(current_score) if current_score != 0 else 0
        
        # 計算信心度
        confidence_score = min(1.0, max(0.0, 0.5 + expected_improvement))
        
        return WeightOptimizationResult(
            original_weights=current_weights,
            optimized_weights=optimized_weights,
            expected_improvement=expected_improvement,
            confidence_score=confidence_score,
            optimization_method=method,
            iterations=iterations,
            convergence_achieved=converged,
            performance_projection=performance_data,  # 簡化實現
            risk_assessment={"overall_risk": performance_data.volatility},
            sensitivity_analysis={name: abs(optimized_weights[name] - current_weights[name]) 
                                for name in weight_names},
            explanation=f"使用 {method.value} 方法優化，經過 {iterations} 次迭代"
        )
    
    async def _gradient_ascent_optimization(self, 
                                          current_weights: np.ndarray,
                                          performance_data: PerformanceMetrics) -> Tuple[np.ndarray, int, bool]:
        """梯度上升優化"""
        weights = current_weights.copy()
        learning_rate = self.optimization_params["learning_rate"]
        max_iterations = self.optimization_params["max_iterations"]
        convergence_threshold = self.optimization_params["convergence_threshold"]
        
        for iteration in range(max_iterations):
            # 計算梯度 (數值梯度)
            gradient = np.zeros_like(weights)
            epsilon = 1e-6
            
            current_score = self._calculate_objective_function(weights, performance_data)
            
            for i in range(len(weights)):
                weights_plus = weights.copy()
                weights_plus[i] += epsilon
                weights_plus = weights_plus / np.sum(weights_plus)  # 重新標準化
                
                score_plus = self._calculate_objective_function(weights_plus, performance_data)
                gradient[i] = (score_plus - current_score) / epsilon
            
            # 更新權重
            old_weights = weights.copy()
            weights += learning_rate * gradient
            
            # 確保權重為正且和為1
            weights = np.maximum(weights, 0.001)
            weights = weights / np.sum(weights)
            
            # 檢查收斂
            if np.linalg.norm(weights - old_weights) < convergence_threshold:
                return weights, iteration + 1, True
        
        return weights, max_iterations, False
    
    async def _adaptive_momentum_optimization(self, 
                                            current_weights: np.ndarray,
                                            performance_data: PerformanceMetrics) -> Tuple[np.ndarray, int, bool]:
        """自適應動量優化"""
        weights = current_weights.copy()
        velocity = np.zeros_like(weights)
        
        learning_rate = self.optimization_params["learning_rate"]
        momentum = self.optimization_params["momentum"]
        max_iterations = self.optimization_params["max_iterations"]
        convergence_threshold = self.optimization_params["convergence_threshold"]
        
        for iteration in range(max_iterations):
            # 計算梯度
            gradient = np.zeros_like(weights)
            epsilon = 1e-6
            current_score = self._calculate_objective_function(weights, performance_data)
            
            for i in range(len(weights)):
                weights_plus = weights.copy()
                weights_plus[i] += epsilon
                weights_plus = weights_plus / np.sum(weights_plus)
                
                score_plus = self._calculate_objective_function(weights_plus, performance_data)
                gradient[i] = (score_plus - current_score) / epsilon
            
            # 更新速度和權重
            velocity = momentum * velocity + learning_rate * gradient
            old_weights = weights.copy()
            weights += velocity
            
            # 確保權重為正且和為1
            weights = np.maximum(weights, 0.001)
            weights = weights / np.sum(weights)
            
            # 檢查收斂
            if np.linalg.norm(weights - old_weights) < convergence_threshold:
                return weights, iteration + 1, True
        
        return weights, max_iterations, False
    
    def _calculate_objective_function(self, 
                                    weights: np.ndarray, 
                                    performance_data: PerformanceMetrics) -> float:
        """計算目標函數 (風險調整收益)"""
        # 簡化的目標函數：夏普比率 + 勝率 - 風險懲罰
        risk_penalty = self.optimization_params["risk_penalty"]
        
        # 基礎分數：夏普比率和勝率的加權組合
        base_score = (
            performance_data.sharpe_ratio * 0.4 +
            performance_data.win_rate * 0.3 +
            performance_data.signal_accuracy * 0.2 +
            (1.0 - performance_data.false_positive_rate) * 0.1
        )
        
        # 風險懲罰：基於波動率和最大回撤
        risk_score = (
            performance_data.volatility * 0.6 +
            abs(performance_data.max_drawdown) * 0.4
        )
        
        # 權重分散度獎勵 (避免過度集中)
        entropy = -np.sum(weights * np.log(weights + 1e-10))
        diversity_bonus = entropy / np.log(len(weights)) * 0.1
        
        final_score = base_score - risk_penalty * risk_score + diversity_bonus
        
        return final_score
    
    def get_reallocation_history(self, hours_back: int = 168) -> List[ReallocationEvent]:
        """獲取重分配歷史"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        return [
            event for event in self.reallocation_history
            if event.event_time >= cutoff_time
        ]
    
    def validate_reallocation_performance(self, 
                                        event_id: str, 
                                        actual_performance: PerformanceMetrics) -> bool:
        """驗證重分配性能"""
        # 找到對應的重分配事件
        target_event = None
        for event in self.reallocation_history:
            if event.event_id == event_id:
                target_event = event
                break
        
        if not target_event:
            logger.error(f"❌ 找不到重分配事件: {event_id}")
            return False
        
        # 計算實際改善
        # 這裡需要與重分配前的性能進行比較
        # 簡化實現：假設我們有基準性能
        baseline_return = 0.0  # 應該從歷史數據獲取
        actual_improvement = actual_performance.total_return - baseline_return
        
        target_event.actual_impact = actual_improvement
        target_event.validation_time = datetime.now()
        
        # 更新統計數據
        if actual_improvement > 0:
            self.stats["successful_reallocations"] += 1
            self.stats["total_improvement"] += actual_improvement
            self.stats["avg_improvement"] = self.stats["total_improvement"] / self.stats["successful_reallocations"]
        
        success = actual_improvement >= target_event.expected_impact * 0.5  # 至少達到50%預期
        
        if success:
            logger.info(f"✅ 重分配驗證成功: {event_id} (實際改善: {actual_improvement:.2%})")
        else:
            logger.warning(f"⚠️ 重分配效果不如預期: {event_id} (實際: {actual_improvement:.2%}, 預期: {target_event.expected_impact:.2%})")
        
        return success
    
    def export_engine_status(self) -> Dict:
        """導出引擎狀態"""
        return {
            "is_monitoring": self.is_monitoring,
            "stats": self.stats,
            "optimization_params": self.optimization_params,
            "trigger_thresholds": self.trigger_thresholds,
            "recent_reallocations": [
                {
                    "event_id": event.event_id,
                    "trigger": event.trigger.value,
                    "symbol": event.symbol,
                    "timeframe": event.timeframe,
                    "expected_impact": event.expected_impact,
                    "actual_impact": event.actual_impact,
                    "event_time": event.event_time.isoformat()
                }
                for event in list(self.reallocation_history)[-10:]
            ],
            "performance_tracking": {
                key: len(history) for key, history in self.performance_history.items()
            },
            "export_time": datetime.now().isoformat()
        }

# 全局實例
dynamic_reallocation_engine = DynamicReallocationEngine()
