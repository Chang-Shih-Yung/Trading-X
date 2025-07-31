"""
週期切換機制 - Trading X Phase 3
智能切換不同時間框架以適應市場條件變化
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import asyncio
from collections import deque
import math

logger = logging.getLogger(__name__)

class SwitchTrigger(Enum):
    """切換觸發條件"""
    VOLATILITY_REGIME_CHANGE = "volatility_regime_change"    # 波動制度變化
    TREND_STRENGTH_SHIFT = "trend_strength_shift"           # 趨勢強度轉變
    MARKET_EFFICIENCY_CHANGE = "market_efficiency_change"    # 市場效率變化
    LIQUIDITY_CONDITION_SHIFT = "liquidity_condition_shift" # 流動性條件變化
    PERFORMANCE_THRESHOLD = "performance_threshold"         # 性能閾值觸發
    TIME_BASED_ROTATION = "time_based_rotation"             # 基於時間的輪換
    CORRELATION_BREAKDOWN = "correlation_breakdown"         # 相關性失效
    MANUAL_OVERRIDE = "manual_override"                     # 手動覆蓋

class SwitchDirection(Enum):
    """切換方向"""
    SHORT_TO_MEDIUM = "short_to_medium"      # 短線→中線
    SHORT_TO_LONG = "short_to_long"          # 短線→長線
    MEDIUM_TO_SHORT = "medium_to_short"      # 中線→短線
    MEDIUM_TO_LONG = "medium_to_long"        # 中線→長線
    LONG_TO_MEDIUM = "long_to_medium"        # 長線→中線
    LONG_TO_SHORT = "long_to_short"          # 長線→短線

class MarketRegime(Enum):
    """市場制度"""
    TRENDING_BULL = "trending_bull"          # 趨勢性牛市
    TRENDING_BEAR = "trending_bear"          # 趨勢性熊市
    RANGING_STABLE = "ranging_stable"        # 區間震盪(穩定)
    RANGING_VOLATILE = "ranging_volatile"    # 區間震盪(高波動)
    BREAKDOWN = "breakdown"                  # 結構性破裂
    RECOVERY = "recovery"                    # 恢復階段

@dataclass
class MarketConditionSnapshot:
    """市場條件快照"""
    symbol: str
    timestamp: datetime
    
    # 波動性指標
    realized_volatility: float        # 已實現波動率
    implied_volatility: float         # 隱含波動率
    volatility_regime: str            # 波動制度
    
    # 趨勢指標
    trend_strength: float            # 趨勢強度 (0-1)
    trend_direction: int             # 趨勢方向 (-1, 0, 1)
    trend_persistence: float         # 趨勢持續性
    
    # 市場效率指標
    price_efficiency: float          # 價格效率
    information_ratio: float         # 信息比率
    market_impact_cost: float        # 市場衝擊成本
    
    # 流動性指標
    bid_ask_spread: float           # 買賣價差
    order_book_depth: float         # 訂單簿深度
    turnover_rate: float            # 換手率
    
    # 制度識別
    current_regime: MarketRegime
    regime_confidence: float        # 制度識別信心度
    regime_duration: int           # 當前制度持續時間(小時)

@dataclass
class TimeframeSwitchEvent:
    """時間框架切換事件"""
    event_id: str
    symbol: str
    
    # 切換詳情
    from_timeframe: str
    to_timeframe: str
    switch_direction: SwitchDirection
    trigger: SwitchTrigger
    
    # 市場條件
    market_condition: MarketConditionSnapshot
    trigger_value: float           # 觸發閾值
    confidence_score: float        # 切換信心度
    
    # 預期效果
    expected_performance_improvement: float
    expected_risk_reduction: float
    expected_duration_hours: int
    
    # 執行狀態
    switch_time: datetime = field(default_factory=datetime.now)
    execution_successful: bool = True
    actual_performance: Optional[float] = None
    actual_duration: Optional[int] = None
    
    # 元數據
    explanation: str = ""
    validation_time: Optional[datetime] = None

@dataclass
class TimeframePerformanceProfile:
    """時間框架性能檔案"""
    timeframe: str
    symbol: str
    
    # 適應性指標
    volatility_adaptation: float     # 波動適應度
    trend_following_ability: float   # 趨勢跟蹤能力
    ranging_market_performance: float # 震盪市場表現
    
    # 風險特徵
    max_drawdown_tendency: float     # 最大回撤傾向
    volatility_exposure: float       # 波動暴露度
    tail_risk_protection: float      # 尾部風險保護
    
    # 市場制度適應性
    regime_adaptability: Dict[MarketRegime, float] = field(default_factory=dict)
    
    # 歷史表現
    avg_return_by_regime: Dict[MarketRegime, float] = field(default_factory=dict)
    success_rate_by_regime: Dict[MarketRegime, float] = field(default_factory=dict)
    
    last_updated: datetime = field(default_factory=datetime.now)

class TimeframeSwitchEngine:
    """時間框架切換引擎"""
    
    def __init__(self):
        # 切換歷史
        self.switch_history: deque = deque(maxlen=500)
        self.market_condition_history: Dict[str, deque] = {}
        
        # 性能檔案
        self.timeframe_profiles: Dict[str, TimeframePerformanceProfile] = {}
        
        # 當前狀態
        self.current_timeframes: Dict[str, str] = {}  # symbol -> timeframe
        self.active_switches: Dict[str, TimeframeSwitchEvent] = {}
        
        # 切換閾值配置
        self.switch_thresholds = {
            "volatility_increase": 1.5,        # 波動率增加1.5倍觸發
            "volatility_decrease": 0.6,        # 波動率降至0.6倍觸發
            "trend_strength_high": 0.8,        # 高趨勢強度閾值
            "trend_strength_low": 0.3,         # 低趨勢強度閾值
            "efficiency_degradation": -0.2,    # 效率下降20%
            "performance_threshold": -0.1,     # 性能下降10%
            "regime_confidence": 0.7,          # 制度識別信心閾值
            "min_switch_interval_hours": 4     # 最小切換間隔
        }
        
        # 統計數據
        self.stats = {
            "total_switches": 0,
            "successful_switches": 0,
            "avg_improvement": 0.0,
            "switch_accuracy": 0.0,
            "active_timeframes": {}
        }
        
        # 運行狀態
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # 初始化時間框架性能檔案
        self._initialize_timeframe_profiles()
        
        logger.info("🔄 時間框架切換引擎初始化完成")
    
    def _initialize_timeframe_profiles(self):
        """初始化時間框架性能檔案"""
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "SOLUSDT"]
        timeframes = ["short", "medium", "long"]
        
        for symbol in symbols:
            for timeframe in timeframes:
                profile_key = f"{symbol}_{timeframe}"
                
                # 根據時間框架特性設定初始檔案
                if timeframe == "short":
                    profile = TimeframePerformanceProfile(
                        timeframe=timeframe,
                        symbol=symbol,
                        volatility_adaptation=0.9,        # 短線高波動適應
                        trend_following_ability=0.6,      # 中等趨勢跟蹤
                        ranging_market_performance=0.8,   # 震盪市場表現佳
                        max_drawdown_tendency=0.7,        # 較高回撤傾向
                        volatility_exposure=0.9,          # 高波動暴露
                        tail_risk_protection=0.5          # 中等尾部風險保護
                    )
                
                elif timeframe == "medium":
                    profile = TimeframePerformanceProfile(
                        timeframe=timeframe,
                        symbol=symbol,
                        volatility_adaptation=0.7,
                        trend_following_ability=0.8,      # 較強趨勢跟蹤
                        ranging_market_performance=0.6,
                        max_drawdown_tendency=0.5,
                        volatility_exposure=0.6,
                        tail_risk_protection=0.7
                    )
                
                else:  # long
                    profile = TimeframePerformanceProfile(
                        timeframe=timeframe,
                        symbol=symbol,
                        volatility_adaptation=0.4,        # 低波動適應
                        trend_following_ability=0.9,      # 最強趨勢跟蹤
                        ranging_market_performance=0.4,   # 震盪市場表現較差
                        max_drawdown_tendency=0.3,        # 低回撤傾向
                        volatility_exposure=0.3,          # 低波動暴露
                        tail_risk_protection=0.9          # 高尾部風險保護
                    )
                
                # 初始化制度適應性
                profile.regime_adaptability = {
                    MarketRegime.TRENDING_BULL: 0.8 if timeframe == "long" else 0.6,
                    MarketRegime.TRENDING_BEAR: 0.7 if timeframe == "long" else 0.5,
                    MarketRegime.RANGING_STABLE: 0.9 if timeframe == "short" else 0.4,
                    MarketRegime.RANGING_VOLATILE: 0.8 if timeframe == "short" else 0.3,
                    MarketRegime.BREAKDOWN: 0.6 if timeframe == "short" else 0.8,
                    MarketRegime.RECOVERY: 0.7
                }
                
                self.timeframe_profiles[profile_key] = profile
                
            # 設定預設時間框架
            self.current_timeframes[symbol] = "medium"  # 預設中線
        
        logger.info(f"📊 初始化 {len(self.timeframe_profiles)} 個時間框架性能檔案")
    
    async def start_monitoring(self):
        """啟動切換監控"""
        if self.is_monitoring:
            logger.warning("⚠️ 時間框架切換監控已在運行")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("🚀 時間框架切換監控已啟動")
    
    async def stop_monitoring(self):
        """停止切換監控"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("⏹️ 時間框架切換監控已停止")
    
    async def _monitoring_loop(self):
        """監控循環"""
        while self.is_monitoring:
            try:
                # 檢查所有交易對的切換條件
                await self._check_switch_conditions()
                
                # 清理過期的切換事件
                self._cleanup_expired_switches()
                
                # 等待下次檢查 (每10分鐘)
                await asyncio.sleep(600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 切換監控循環錯誤: {e}")
                await asyncio.sleep(120)
    
    async def _check_switch_conditions(self):
        """檢查切換條件"""
        for symbol in self.current_timeframes.keys():
            try:
                # 獲取市場條件快照
                market_condition = await self._get_market_condition_snapshot(symbol)
                if not market_condition:
                    continue
                
                # 存儲歷史數據
                if symbol not in self.market_condition_history:
                    self.market_condition_history[symbol] = deque(maxlen=100)
                self.market_condition_history[symbol].append(market_condition)
                
                # 評估是否需要切換
                switch_recommendation = await self._evaluate_switch_need(symbol, market_condition)
                
                if switch_recommendation:
                    logger.info(f"🎯 檢測到切換建議: {symbol} {switch_recommendation['trigger'].value}")
                    
                    # 執行時間框架切換
                    await self.execute_timeframe_switch(
                        symbol=symbol,
                        target_timeframe=switch_recommendation['target_timeframe'],
                        trigger=switch_recommendation['trigger'],
                        market_condition=market_condition,
                        confidence_score=switch_recommendation['confidence']
                    )
                
            except Exception as e:
                logger.error(f"❌ 檢查 {symbol} 切換條件失敗: {e}")
    
    async def _get_market_condition_snapshot(self, symbol: str) -> Optional[MarketConditionSnapshot]:
        """獲取市場條件快照 (模擬實現)"""
        import random
        
        # 模擬市場數據
        realized_vol = random.uniform(0.2, 0.8)
        trend_strength = random.uniform(0.1, 0.9)
        
        # 簡單的制度識別邏輯
        if trend_strength > 0.7 and realized_vol < 0.4:
            regime = MarketRegime.TRENDING_BULL if random.random() > 0.5 else MarketRegime.TRENDING_BEAR
        elif trend_strength < 0.3 and realized_vol < 0.4:
            regime = MarketRegime.RANGING_STABLE
        elif trend_strength < 0.3 and realized_vol > 0.6:
            regime = MarketRegime.RANGING_VOLATILE
        elif realized_vol > 0.7:
            regime = MarketRegime.BREAKDOWN
        else:
            regime = MarketRegime.RECOVERY
        
        return MarketConditionSnapshot(
            symbol=symbol,
            timestamp=datetime.now(),
            realized_volatility=realized_vol,
            implied_volatility=realized_vol * random.uniform(0.8, 1.2),
            volatility_regime="high" if realized_vol > 0.5 else "low",
            trend_strength=trend_strength,
            trend_direction=1 if random.random() > 0.5 else -1,
            trend_persistence=random.uniform(0.3, 0.9),
            price_efficiency=random.uniform(0.4, 0.9),
            information_ratio=random.uniform(0.1, 2.0),
            market_impact_cost=random.uniform(0.001, 0.01),
            bid_ask_spread=random.uniform(0.0001, 0.001),
            order_book_depth=random.uniform(0.5, 2.0),
            turnover_rate=random.uniform(0.1, 3.0),
            current_regime=regime,
            regime_confidence=random.uniform(0.6, 0.95),
            regime_duration=random.randint(1, 48)
        )
    
    async def _evaluate_switch_need(self, 
                                  symbol: str, 
                                  current_condition: MarketConditionSnapshot) -> Optional[Dict]:
        """評估是否需要切換時間框架"""
        current_timeframe = self.current_timeframes[symbol]
        current_profile = self.timeframe_profiles[f"{symbol}_{current_timeframe}"]
        
        # 檢查最小切換間隔
        last_switch_time = self._get_last_switch_time(symbol)
        if last_switch_time:
            hours_since_switch = (datetime.now() - last_switch_time).total_seconds() / 3600
            if hours_since_switch < self.switch_thresholds["min_switch_interval_hours"]:
                return None
        
        recommendations = []
        
        # 1. 波動制度變化檢查
        volatility_trigger = self._check_volatility_regime_change(symbol, current_condition)
        if volatility_trigger:
            recommendations.append(volatility_trigger)
        
        # 2. 趨勢強度變化檢查
        trend_trigger = self._check_trend_strength_shift(symbol, current_condition)
        if trend_trigger:
            recommendations.append(trend_trigger)
        
        # 3. 市場制度適應性檢查
        regime_trigger = self._check_regime_adaptability(symbol, current_condition, current_profile)
        if regime_trigger:
            recommendations.append(regime_trigger)
        
        # 4. 市場效率變化檢查
        efficiency_trigger = self._check_market_efficiency_change(symbol, current_condition)
        if efficiency_trigger:
            recommendations.append(efficiency_trigger)
        
        # 選擇最佳推薦
        if recommendations:
            # 按信心度排序，選擇最高的
            best_recommendation = max(recommendations, key=lambda r: r['confidence'])
            if best_recommendation['confidence'] >= 0.7:
                return best_recommendation
        
        return None
    
    def _check_volatility_regime_change(self, 
                                      symbol: str, 
                                      current_condition: MarketConditionSnapshot) -> Optional[Dict]:
        """檢查波動制度變化"""
        current_timeframe = self.current_timeframes[symbol]
        history = self.market_condition_history.get(symbol, deque())
        
        if len(history) < 5:
            return None
        
        # 計算歷史平均波動率
        recent_volatility = [h.realized_volatility for h in list(history)[-5:]]
        avg_volatility = sum(recent_volatility) / len(recent_volatility)
        
        volatility_ratio = current_condition.realized_volatility / avg_volatility
        
        # 波動率大幅增加 -> 考慮切換到短線
        if (volatility_ratio > self.switch_thresholds["volatility_increase"] and 
            current_timeframe != "short"):
            
            confidence = min(0.9, 0.5 + (volatility_ratio - 1.5) * 0.4)
            return {
                "trigger": SwitchTrigger.VOLATILITY_REGIME_CHANGE,
                "target_timeframe": "short",
                "confidence": confidence,
                "explanation": f"波動率增加 {volatility_ratio:.1f}x，建議切換至短線"
            }
        
        # 波動率大幅降低 -> 考慮切換到長線
        elif (volatility_ratio < self.switch_thresholds["volatility_decrease"] and
              current_timeframe != "long" and
              current_condition.trend_strength > 0.6):
            
            confidence = min(0.9, 0.5 + (1.0 - volatility_ratio) * 0.8)
            return {
                "trigger": SwitchTrigger.VOLATILITY_REGIME_CHANGE,
                "target_timeframe": "long",
                "confidence": confidence,
                "explanation": f"波動率降低至 {volatility_ratio:.1f}x，建議切換至長線"
            }
        
        return None
    
    def _check_trend_strength_shift(self, 
                                  symbol: str, 
                                  current_condition: MarketConditionSnapshot) -> Optional[Dict]:
        """檢查趨勢強度變化"""
        current_timeframe = self.current_timeframes[symbol]
        
        # 強趨勢 -> 長線
        if (current_condition.trend_strength > self.switch_thresholds["trend_strength_high"] and
            current_condition.trend_persistence > 0.7 and
            current_timeframe != "long"):
            
            confidence = min(0.9, 0.6 + current_condition.trend_strength * 0.3)
            return {
                "trigger": SwitchTrigger.TREND_STRENGTH_SHIFT,
                "target_timeframe": "long",
                "confidence": confidence,
                "explanation": f"檢測到強趨勢 ({current_condition.trend_strength:.2f})，建議長線策略"
            }
        
        # 弱趨勢 -> 短線
        elif (current_condition.trend_strength < self.switch_thresholds["trend_strength_low"] and
              current_timeframe != "short"):
            
            confidence = min(0.8, 0.6 + (0.5 - current_condition.trend_strength))
            return {
                "trigger": SwitchTrigger.TREND_STRENGTH_SHIFT,
                "target_timeframe": "short",
                "confidence": confidence,
                "explanation": f"趨勢強度弱 ({current_condition.trend_strength:.2f})，建議短線策略"
            }
        
        return None
    
    def _check_regime_adaptability(self, 
                                 symbol: str, 
                                 current_condition: MarketConditionSnapshot,
                                 current_profile: TimeframePerformanceProfile) -> Optional[Dict]:
        """檢查市場制度適應性"""
        current_regime = current_condition.current_regime
        current_timeframe = self.current_timeframes[symbol]
        
        # 獲取當前時間框架對當前制度的適應性
        current_adaptability = current_profile.regime_adaptability.get(current_regime, 0.5)
        
        # 檢查其他時間框架的適應性
        best_timeframe = current_timeframe
        best_adaptability = current_adaptability
        
        for timeframe in ["short", "medium", "long"]:
            if timeframe == current_timeframe:
                continue
            
            profile_key = f"{symbol}_{timeframe}"
            if profile_key in self.timeframe_profiles:
                adaptability = self.timeframe_profiles[profile_key].regime_adaptability.get(current_regime, 0.5)
                if adaptability > best_adaptability + 0.15:  # 至少15%的優勢
                    best_timeframe = timeframe
                    best_adaptability = adaptability
        
        if (best_timeframe != current_timeframe and 
            current_condition.regime_confidence > self.switch_thresholds["regime_confidence"]):
            
            confidence = min(0.9, current_condition.regime_confidence * (best_adaptability - current_adaptability))
            return {
                "trigger": SwitchTrigger.MARKET_EFFICIENCY_CHANGE,
                "target_timeframe": best_timeframe,
                "confidence": confidence,
                "explanation": f"當前制度 {current_regime.value} 更適合 {best_timeframe} 策略"
            }
        
        return None
    
    def _check_market_efficiency_change(self, 
                                      symbol: str, 
                                      current_condition: MarketConditionSnapshot) -> Optional[Dict]:
        """檢查市場效率變化"""
        current_timeframe = self.current_timeframes[symbol]
        
        # 市場效率降低 -> 短線機會增加
        if (current_condition.price_efficiency < 0.5 and 
            current_condition.market_impact_cost < 0.005 and
            current_timeframe != "short"):
            
            confidence = 0.6 + (0.5 - current_condition.price_efficiency)
            return {
                "trigger": SwitchTrigger.MARKET_EFFICIENCY_CHANGE,
                "target_timeframe": "short",
                "confidence": confidence,
                "explanation": f"市場效率降低 ({current_condition.price_efficiency:.2f})，短線機會增加"
            }
        
        return None
    
    def _get_last_switch_time(self, symbol: str) -> Optional[datetime]:
        """獲取最後切換時間"""
        for event in reversed(self.switch_history):
            if event.symbol == symbol:
                return event.switch_time
        return None
    
    async def execute_timeframe_switch(self,
                                     symbol: str,
                                     target_timeframe: str,
                                     trigger: SwitchTrigger,
                                     market_condition: MarketConditionSnapshot,
                                     confidence_score: float,
                                     manual_override: bool = False) -> Optional[TimeframeSwitchEvent]:
        """執行時間框架切換"""
        try:
            current_timeframe = self.current_timeframes[symbol]
            
            if current_timeframe == target_timeframe:
                logger.warning(f"⚠️ {symbol} 已經在 {target_timeframe} 時間框架")
                return None
            
            # 確定切換方向
            switch_direction = self._determine_switch_direction(current_timeframe, target_timeframe)
            
            # 預測切換效果
            expected_improvement = self._predict_switch_performance(
                symbol, current_timeframe, target_timeframe, market_condition
            )
            
            # 創建切換事件
            event_id = f"{symbol}_{current_timeframe}_{target_timeframe}_{int(datetime.now().timestamp())}"
            
            switch_event = TimeframeSwitchEvent(
                event_id=event_id,
                symbol=symbol,
                from_timeframe=current_timeframe,
                to_timeframe=target_timeframe,
                switch_direction=switch_direction,
                trigger=trigger,
                market_condition=market_condition,
                trigger_value=confidence_score,
                confidence_score=confidence_score,
                expected_performance_improvement=expected_improvement,
                expected_risk_reduction=0.1 if target_timeframe == "long" else -0.1,
                expected_duration_hours=self._estimate_switch_duration(trigger, market_condition),
                explanation=f"由 {trigger.value} 觸發，從 {current_timeframe} 切換至 {target_timeframe}"
            )
            
            # 執行切換
            if not manual_override and confidence_score < 0.7:
                logger.info(f"📊 {symbol} 切換信心度不足 ({confidence_score:.2f})，暫緩執行")
                return switch_event
            
            # 更新當前時間框架
            self.current_timeframes[symbol] = target_timeframe
            
            # 記錄切換事件
            self.switch_history.append(switch_event)
            self.active_switches[symbol] = switch_event
            
            # 更新統計數據
            self.stats["total_switches"] += 1
            self.stats["active_timeframes"][symbol] = target_timeframe
            
            logger.info(f"✅ 執行時間框架切換: {symbol} {current_timeframe} → {target_timeframe} (信心度: {confidence_score:.2f})")
            
            return switch_event
            
        except Exception as e:
            logger.error(f"❌ 執行 {symbol} 時間框架切換失敗: {e}")
            return None
    
    def _determine_switch_direction(self, from_timeframe: str, to_timeframe: str) -> SwitchDirection:
        """確定切換方向"""
        direction_map = {
            ("short", "medium"): SwitchDirection.SHORT_TO_MEDIUM,
            ("short", "long"): SwitchDirection.SHORT_TO_LONG,
            ("medium", "short"): SwitchDirection.MEDIUM_TO_SHORT,
            ("medium", "long"): SwitchDirection.MEDIUM_TO_LONG,
            ("long", "medium"): SwitchDirection.LONG_TO_MEDIUM,
            ("long", "short"): SwitchDirection.LONG_TO_SHORT
        }
        return direction_map.get((from_timeframe, to_timeframe), SwitchDirection.MEDIUM_TO_SHORT)
    
    def _predict_switch_performance(self, 
                                  symbol: str,
                                  from_timeframe: str,
                                  to_timeframe: str,
                                  market_condition: MarketConditionSnapshot) -> float:
        """預測切換性能改善"""
        # 獲取性能檔案
        from_profile = self.timeframe_profiles[f"{symbol}_{from_timeframe}"]
        to_profile = self.timeframe_profiles[f"{symbol}_{to_timeframe}"]
        
        # 基於當前市場制度的適應性差異
        current_regime = market_condition.current_regime
        from_adaptability = from_profile.regime_adaptability.get(current_regime, 0.5)
        to_adaptability = to_profile.regime_adaptability.get(current_regime, 0.5)
        
        # 基於市場條件的匹配度
        volatility_match = self._calculate_volatility_match(to_profile, market_condition)
        trend_match = self._calculate_trend_match(to_profile, market_condition)
        
        # 綜合預測改善
        adaptability_improvement = to_adaptability - from_adaptability
        condition_match = (volatility_match + trend_match) / 2
        
        # 加權計算預期改善
        expected_improvement = (
            adaptability_improvement * 0.4 +
            condition_match * 0.3 +
            market_condition.regime_confidence * 0.2 +
            (1.0 - market_condition.realized_volatility) * 0.1  # 低波動加分
        )
        
        return max(-0.3, min(0.5, expected_improvement))  # 限制在合理範圍
    
    def _calculate_volatility_match(self, 
                                  profile: TimeframePerformanceProfile,
                                  market_condition: MarketConditionSnapshot) -> float:
        """計算波動率匹配度"""
        # 根據檔案的波動適應性和當前波動率計算匹配度
        optimal_volatility = 1.0 - profile.volatility_adaptation  # 適應性越高，最佳波動率越高
        volatility_diff = abs(market_condition.realized_volatility - optimal_volatility)
        return max(0.0, 1.0 - volatility_diff * 2)
    
    def _calculate_trend_match(self, 
                             profile: TimeframePerformanceProfile,
                             market_condition: MarketConditionSnapshot) -> float:
        """計算趨勢匹配度"""
        # 趨勢跟蹤能力與當前趨勢強度的匹配
        trend_diff = abs(profile.trend_following_ability - market_condition.trend_strength)
        return max(0.0, 1.0 - trend_diff)
    
    def _estimate_switch_duration(self, 
                                trigger: SwitchTrigger,
                                market_condition: MarketConditionSnapshot) -> int:
        """估計切換持續時間"""
        base_duration = {
            SwitchTrigger.VOLATILITY_REGIME_CHANGE: 12,
            SwitchTrigger.TREND_STRENGTH_SHIFT: 24,
            SwitchTrigger.MARKET_EFFICIENCY_CHANGE: 8,
            SwitchTrigger.LIQUIDITY_CONDITION_SHIFT: 6,
            SwitchTrigger.PERFORMANCE_THRESHOLD: 48,
            SwitchTrigger.TIME_BASED_ROTATION: 72,
            SwitchTrigger.CORRELATION_BREAKDOWN: 24
        }.get(trigger, 24)
        
        # 根據制度信心度調整
        confidence_factor = 0.5 + market_condition.regime_confidence * 0.5
        estimated_duration = int(base_duration * confidence_factor)
        
        return max(4, min(168, estimated_duration))  # 限制在4小時到7天
    
    def _cleanup_expired_switches(self):
        """清理過期的切換事件"""
        current_time = datetime.now()
        expired_symbols = []
        
        for symbol, switch_event in self.active_switches.items():
            expected_end = switch_event.switch_time + timedelta(hours=switch_event.expected_duration_hours)
            if current_time > expected_end:
                expired_symbols.append(symbol)
        
        for symbol in expired_symbols:
            del self.active_switches[symbol]
            logger.info(f"🗑️ 清理過期切換事件: {symbol}")
    
    def get_current_timeframes(self) -> Dict[str, str]:
        """獲取當前所有時間框架"""
        return self.current_timeframes.copy()
    
    def get_switch_history(self, symbol: str = None, hours_back: int = 168) -> List[TimeframeSwitchEvent]:
        """獲取切換歷史"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        history = [
            event for event in self.switch_history
            if event.switch_time >= cutoff_time
        ]
        
        if symbol:
            history = [event for event in history if event.symbol == symbol]
        
        return sorted(history, key=lambda e: e.switch_time, reverse=True)
    
    def validate_switch_performance(self, 
                                  event_id: str,
                                  actual_performance_improvement: float) -> bool:
        """驗證切換性能"""
        # 查找切換事件
        target_event = None
        for event in self.switch_history:
            if event.event_id == event_id:
                target_event = event
                break
        
        if not target_event:
            logger.error(f"❌ 找不到切換事件: {event_id}")
            return False
        
        # 記錄實際性能
        target_event.actual_performance = actual_performance_improvement
        target_event.validation_time = datetime.now()
        
        # 計算實際持續時間
        if target_event.validation_time:
            actual_duration = (target_event.validation_time - target_event.switch_time).total_seconds() / 3600
            target_event.actual_duration = int(actual_duration)
        
        # 判斷成功標準
        success_threshold = target_event.expected_performance_improvement * 0.5  # 至少達到50%預期
        is_successful = actual_performance_improvement >= success_threshold
        
        if is_successful:
            self.stats["successful_switches"] += 1
            self.stats["switch_accuracy"] = self.stats["successful_switches"] / self.stats["total_switches"]
            
            # 更新性能檔案
            self._update_performance_profile(target_event, actual_performance_improvement)
        
        logger.info(f"{'✅' if is_successful else '⚠️'} 切換驗證: {event_id} "
                   f"(實際: {actual_performance_improvement:.2%}, 預期: {target_event.expected_performance_improvement:.2%})")
        
        return is_successful
    
    def _update_performance_profile(self, 
                                  switch_event: TimeframeSwitchEvent,
                                  actual_improvement: float):
        """更新性能檔案"""
        profile_key = f"{switch_event.symbol}_{switch_event.to_timeframe}"
        if profile_key in self.timeframe_profiles:
            profile = self.timeframe_profiles[profile_key]
            regime = switch_event.market_condition.current_regime
            
            # 更新制度表現記錄
            if regime not in profile.avg_return_by_regime:
                profile.avg_return_by_regime[regime] = actual_improvement
                profile.success_rate_by_regime[regime] = 1.0 if actual_improvement > 0 else 0.0
            else:
                # 使用指數移動平均更新
                alpha = 0.3
                profile.avg_return_by_regime[regime] = (
                    alpha * actual_improvement + 
                    (1 - alpha) * profile.avg_return_by_regime[regime]
                )
                
                old_success_rate = profile.success_rate_by_regime[regime]
                new_success = 1.0 if actual_improvement > 0 else 0.0
                profile.success_rate_by_regime[regime] = (
                    alpha * new_success + (1 - alpha) * old_success_rate
                )
            
            profile.last_updated = datetime.now()
            logger.info(f"📊 更新 {profile_key} 制度 {regime.value} 性能檔案")
    
    def export_switch_analysis(self) -> Dict:
        """導出切換分析摘要"""
        return {
            "engine_status": {
                "is_monitoring": self.is_monitoring,
                "stats": self.stats,
                "switch_thresholds": self.switch_thresholds
            },
            "current_timeframes": self.current_timeframes,
            "active_switches": {
                symbol: {
                    "from_timeframe": event.from_timeframe,
                    "to_timeframe": event.to_timeframe,
                    "trigger": event.trigger.value,
                    "confidence_score": event.confidence_score,
                    "switch_time": event.switch_time.isoformat(),
                    "expected_improvement": event.expected_performance_improvement
                }
                for symbol, event in self.active_switches.items()
            },
            "recent_switches": [
                {
                    "event_id": event.event_id,
                    "symbol": event.symbol,
                    "switch_direction": event.switch_direction.value,
                    "trigger": event.trigger.value,
                    "confidence_score": event.confidence_score,
                    "expected_improvement": event.expected_performance_improvement,
                    "actual_improvement": event.actual_performance,
                    "switch_time": event.switch_time.isoformat()
                }
                for event in list(self.switch_history)[-10:]
            ],
            "timeframe_performance_summary": {
                key: {
                    "volatility_adaptation": profile.volatility_adaptation,
                    "trend_following_ability": profile.trend_following_ability,
                    "ranging_market_performance": profile.ranging_market_performance,
                    "regime_adaptability": {k.value: v for k, v in profile.regime_adaptability.items()},
                    "last_updated": profile.last_updated.isoformat()
                }
                for key, profile in list(self.timeframe_profiles.items())[:10]  # 前10個檔案
            },
            "export_time": datetime.now().isoformat()
        }

# 全局實例
timeframe_switch_engine = TimeframeSwitchEngine()
