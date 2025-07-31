"""
基礎權重引擎 - Trading X Phase 3
動態權重計算和分配系統，整合三週期模板與實時市場數據
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging

from .timeframe_weight_templates import (
    TimeframeWeightTemplates, 
    TradingTimeframe, 
    TimeframeWeightTemplate,
    SignalBlockWeights
)

logger = logging.getLogger(__name__)

@dataclass
class MarketConditions:
    """市場條件數據結構"""
    symbol: str
    current_price: float
    volatility_score: float      # 0.0-1.0
    trend_strength: float        # 0.0-1.0
    volume_strength: float       # 0.0-1.0
    liquidity_score: float       # 0.0-1.0
    sentiment_score: float       # 0.0-1.0
    fear_greed_index: int        # 0-100
    market_regime: str          # BULL_TREND, BEAR_TREND, VOLATILE, SIDEWAYS
    regime_confidence: float     # 0.0-1.0
    timestamp: datetime

@dataclass
class SignalBlockData:
    """信號區塊數據"""
    block_name: str
    availability: bool           # 信號是否可用
    quality_score: float        # 信號品質評分 0.0-1.0
    confidence: float           # 信號信心度 0.0-1.0
    latency_ms: float          # 信號延遲（毫秒）
    last_update: datetime      # 最後更新時間
    error_count: int           # 錯誤次數
    success_rate: float        # 成功率 0.0-1.0

@dataclass 
class WeightCalculationResult:
    """權重計算結果"""
    symbol: str
    timeframe: TradingTimeframe
    calculated_weights: SignalBlockWeights
    market_conditions: MarketConditions
    signal_availabilities: Dict[str, SignalBlockData]
    total_confidence: float
    recommendation_score: float  # 整體推薦評分
    risk_level: str             # LOW, MEDIUM, HIGH
    calculation_timestamp: datetime
    weight_adjustments: Dict[str, float]  # 記錄調整幅度

class DynamicWeightEngine:
    """動態權重引擎"""
    
    def __init__(self):
        self.template_manager = TimeframeWeightTemplates()
        self.signal_availability_cache = {}
        self.market_conditions_cache = {}
        self.calculation_history = []
        
        # 引擎配置
        self.config = {
            "cache_expiry_minutes": 5,
            "min_confidence_threshold": 0.3,
            "max_weight_adjustment": 0.5,      # 最大權重調整幅度
            "availability_penalty_factor": 0.7, # 信號不可用時的懲罰因子
            "quality_boost_factor": 1.2,       # 高品質信號的提升因子
            "regime_adaptation_strength": 0.3   # 市場機制適應強度
        }
        
        logger.info("✅ 動態權重引擎初始化完成")
    
    async def calculate_dynamic_weights(self, 
                                      symbol: str,
                                      timeframe: TradingTimeframe,
                                      market_conditions: MarketConditions,
                                      signal_availabilities: Dict[str, SignalBlockData]) -> WeightCalculationResult:
        """
        計算動態權重分配
        
        Args:
            symbol: 交易對
            timeframe: 交易時間框架 
            market_conditions: 市場條件數據
            signal_availabilities: 各信號區塊可用性數據
        """
        try:
            logger.info(f"🎯 開始計算 {symbol} {timeframe.value} 動態權重...")
            
            # 1. 獲取基礎模板
            base_template = self.template_manager.get_adaptive_template(
                timeframe=timeframe,
                market_volatility=market_conditions.volatility_score,
                trend_strength=market_conditions.trend_strength,
                volume_strength=market_conditions.volume_strength
            )
            
            if not base_template:
                raise ValueError(f"無法獲取 {timeframe} 的基礎權重模板")
            
            # 2. 複製基礎權重
            dynamic_weights = SignalBlockWeights(
                precision_filter_weight=base_template.signal_weights.precision_filter_weight,
                market_condition_weight=base_template.signal_weights.market_condition_weight,
                technical_analysis_weight=base_template.signal_weights.technical_analysis_weight,
                regime_analysis_weight=base_template.signal_weights.regime_analysis_weight,
                fear_greed_weight=base_template.signal_weights.fear_greed_weight,
                trend_alignment_weight=base_template.signal_weights.trend_alignment_weight,
                market_depth_weight=base_template.signal_weights.market_depth_weight,
                funding_rate_weight=base_template.signal_weights.funding_rate_weight,
                smart_money_weight=base_template.signal_weights.smart_money_weight
            )
            
            # 3. 根據信號可用性調整權重
            weight_adjustments = {}
            weight_adjustments.update(await self._adjust_weights_by_availability(
                dynamic_weights, signal_availabilities
            ))
            
            # 4. 根據市場條件調整權重
            market_adjustments = await self._adjust_weights_by_market_conditions(
                dynamic_weights, market_conditions, timeframe
            )
            weight_adjustments.update(market_adjustments)
            
            # 5. 根據信號品質調整權重
            quality_adjustments = await self._adjust_weights_by_quality(
                dynamic_weights, signal_availabilities
            )
            weight_adjustments.update(quality_adjustments)
            
            # 6. 權重標準化
            await self._normalize_weights(dynamic_weights)
            
            # 7. 計算整體評估指標
            total_confidence = self._calculate_total_confidence(
                dynamic_weights, signal_availabilities
            )
            
            recommendation_score = self._calculate_recommendation_score(
                dynamic_weights, market_conditions, signal_availabilities
            )
            
            risk_level = self._determine_risk_level(
                market_conditions, total_confidence, recommendation_score
            )
            
            # 8. 構建結果
            result = WeightCalculationResult(
                symbol=symbol,
                timeframe=timeframe,
                calculated_weights=dynamic_weights,
                market_conditions=market_conditions,
                signal_availabilities=signal_availabilities,
                total_confidence=total_confidence,
                recommendation_score=recommendation_score,
                risk_level=risk_level,
                calculation_timestamp=datetime.now(),
                weight_adjustments=weight_adjustments
            )
            
            # 9. 保存計算歷史
            self.calculation_history.append(result)
            self._cleanup_old_history()
            
            logger.info(f"✅ {symbol} {timeframe.value} 動態權重計算完成 "
                       f"(總信心度: {total_confidence:.3f}, 推薦評分: {recommendation_score:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 動態權重計算失敗: {e}")
            raise e
    
    async def _adjust_weights_by_availability(self, 
                                            weights: SignalBlockWeights,
                                            availabilities: Dict[str, SignalBlockData]) -> Dict[str, float]:
        """根據信號可用性調整權重"""
        adjustments = {}
        
        # 信號區塊映射
        signal_mapping = {
            "precision_filter": "precision_filter_weight",
            "market_condition": "market_condition_weight", 
            "technical_analysis": "technical_analysis_weight",
            "regime_analysis": "regime_analysis_weight",
            "fear_greed": "fear_greed_weight",
            "trend_alignment": "trend_alignment_weight",
            "market_depth": "market_depth_weight",
            "funding_rate": "funding_rate_weight",
            "smart_money": "smart_money_weight"
        }
        
        for signal_name, weight_attr in signal_mapping.items():
            if signal_name in availabilities:
                signal_data = availabilities[signal_name]
                current_weight = getattr(weights, weight_attr)
                
                if not signal_data.availability:
                    # 信號不可用，降低權重
                    penalty = current_weight * (1 - self.config["availability_penalty_factor"])
                    new_weight = current_weight - penalty
                    setattr(weights, weight_attr, max(0.0, new_weight))
                    adjustments[f"{signal_name}_availability"] = -penalty
                    
                    logger.warning(f"⚠️ {signal_name} 信號不可用，權重降低 {penalty:.3f}")
        
        return adjustments
    
    async def _adjust_weights_by_market_conditions(self,
                                                 weights: SignalBlockWeights,
                                                 conditions: MarketConditions,
                                                 timeframe: TradingTimeframe) -> Dict[str, float]:
        """根據市場條件調整權重"""
        adjustments = {}
        adjustment_strength = self.config["regime_adaptation_strength"]
        
        # 🎯 市場機制適應性調整
        if conditions.market_regime == "BULL_TREND":
            # 牛市：增加趨勢和機制分析權重
            trend_boost = weights.trend_alignment_weight * adjustment_strength
            regime_boost = weights.regime_analysis_weight * adjustment_strength
            
            weights.trend_alignment_weight += trend_boost
            weights.regime_analysis_weight += regime_boost
            
            adjustments["bull_trend_alignment"] = trend_boost
            adjustments["bull_regime_boost"] = regime_boost
            
        elif conditions.market_regime == "BEAR_TREND":
            # 熊市：增加精準篩選和風險管理權重
            precision_boost = weights.precision_filter_weight * adjustment_strength
            fear_greed_boost = weights.fear_greed_weight * adjustment_strength
            
            weights.precision_filter_weight += precision_boost
            weights.fear_greed_weight += fear_greed_boost
            
            adjustments["bear_precision_boost"] = precision_boost
            adjustments["bear_fear_greed_boost"] = fear_greed_boost
            
        elif conditions.market_regime == "VOLATILE":
            # 高波動：增加市場條件和精準篩選權重
            condition_boost = weights.market_condition_weight * adjustment_strength
            precision_boost = weights.precision_filter_weight * adjustment_strength * 0.5
            
            weights.market_condition_weight += condition_boost
            weights.precision_filter_weight += precision_boost
            
            adjustments["volatile_condition_boost"] = condition_boost
            adjustments["volatile_precision_boost"] = precision_boost
        
        # 🎯 Fear & Greed 指數調整
        if conditions.fear_greed_index <= 20:  # 極度恐懼
            fear_boost = weights.fear_greed_weight * 0.5
            weights.fear_greed_weight += fear_boost
            adjustments["extreme_fear_boost"] = fear_boost
            
        elif conditions.fear_greed_index >= 80:  # 極度貪婪
            fear_boost = weights.fear_greed_weight * 0.3
            weights.fear_greed_weight += fear_boost
            adjustments["extreme_greed_boost"] = fear_boost
        
        # 🎯 波動率調整
        if conditions.volatility_score > 0.8:
            # 高波動時增加精準篩選權重
            volatility_boost = weights.precision_filter_weight * 0.2
            weights.precision_filter_weight += volatility_boost
            adjustments["high_volatility_boost"] = volatility_boost
        
        return adjustments
    
    async def _adjust_weights_by_quality(self,
                                       weights: SignalBlockWeights,
                                       availabilities: Dict[str, SignalBlockData]) -> Dict[str, float]:
        """根據信號品質調整權重"""
        adjustments = {}
        quality_factor = self.config["quality_boost_factor"]
        
        signal_mapping = {
            "precision_filter": "precision_filter_weight",
            "market_condition": "market_condition_weight", 
            "technical_analysis": "technical_analysis_weight",
            "regime_analysis": "regime_analysis_weight",
            "fear_greed": "fear_greed_weight",
            "trend_alignment": "trend_alignment_weight"
        }
        
        for signal_name, weight_attr in signal_mapping.items():
            if signal_name in availabilities:
                signal_data = availabilities[signal_name]
                current_weight = getattr(weights, weight_attr)
                
                # 高品質信號提升權重
                if signal_data.quality_score > 0.8 and signal_data.success_rate > 0.7:
                    quality_boost = current_weight * (quality_factor - 1.0) * signal_data.quality_score
                    new_weight = current_weight + quality_boost
                    setattr(weights, weight_attr, min(1.0, new_weight))
                    adjustments[f"{signal_name}_quality"] = quality_boost
                    
                    logger.info(f"🌟 {signal_name} 高品質信號，權重提升 {quality_boost:.3f}")
        
        return adjustments
    
    async def _normalize_weights(self, weights: SignalBlockWeights):
        """標準化權重，確保總和為1.0"""
        total = weights.get_total_weight()
        
        if total <= 0:
            logger.error("❌ 權重總和為0，無法標準化")
            return
        
        if abs(total - 1.0) < 0.01:
            return  # 已經接近1.0，無需調整
        
        # 標準化所有權重
        normalization_factor = 1.0 / total
        
        weights.precision_filter_weight *= normalization_factor
        weights.market_condition_weight *= normalization_factor
        weights.technical_analysis_weight *= normalization_factor
        weights.regime_analysis_weight *= normalization_factor
        weights.fear_greed_weight *= normalization_factor
        weights.trend_alignment_weight *= normalization_factor
        weights.market_depth_weight *= normalization_factor
        weights.funding_rate_weight *= normalization_factor
        weights.smart_money_weight *= normalization_factor
        
        logger.info(f"⚖️ 權重標準化: {total:.3f} → 1.000")
    
    def _calculate_total_confidence(self,
                                  weights: SignalBlockWeights,
                                  availabilities: Dict[str, SignalBlockData]) -> float:
        """計算加權總信心度"""
        total_confidence = 0.0
        total_weight = 0.0
        
        signal_mapping = {
            "precision_filter": weights.precision_filter_weight,
            "market_condition": weights.market_condition_weight,
            "technical_analysis": weights.technical_analysis_weight,
            "regime_analysis": weights.regime_analysis_weight,
            "fear_greed": weights.fear_greed_weight,
            "trend_alignment": weights.trend_alignment_weight,
            "market_depth": weights.market_depth_weight,
            "funding_rate": weights.funding_rate_weight,
            "smart_money": weights.smart_money_weight
        }
        
        for signal_name, weight in signal_mapping.items():
            if signal_name in availabilities and availabilities[signal_name].availability:
                signal_confidence = availabilities[signal_name].confidence
                weighted_confidence = signal_confidence * weight
                total_confidence += weighted_confidence
                total_weight += weight
        
        return total_confidence / total_weight if total_weight > 0 else 0.0
    
    def _calculate_recommendation_score(self,
                                      weights: SignalBlockWeights,
                                      conditions: MarketConditions,
                                      availabilities: Dict[str, SignalBlockData]) -> float:
        """計算整體推薦評分"""
        # 基礎評分來自加權信心度
        base_score = self._calculate_total_confidence(weights, availabilities)
        
        # 市場條件修正
        market_modifier = 1.0
        
        # 機制信心度修正
        if conditions.regime_confidence > 0.7:
            market_modifier += 0.1
        elif conditions.regime_confidence < 0.3:
            market_modifier -= 0.2
        
        # 波動率修正
        if conditions.volatility_score > 0.8:
            market_modifier -= 0.1  # 高波動降低推薦
        elif conditions.volatility_score < 0.3:
            market_modifier += 0.05  # 低波動稍微提升
        
        # 成交量強度修正
        if conditions.volume_strength > 0.7:
            market_modifier += 0.05
        elif conditions.volume_strength < 0.3:
            market_modifier -= 0.1
        
        # 流動性修正
        if conditions.liquidity_score < 0.5:
            market_modifier -= 0.15
        
        final_score = base_score * market_modifier
        return max(0.0, min(1.0, final_score))
    
    def _determine_risk_level(self,
                            conditions: MarketConditions,
                            confidence: float,
                            recommendation: float) -> str:
        """確定風險等級"""
        risk_score = 0.0
        
        # 市場條件風險
        if conditions.volatility_score > 0.7:
            risk_score += 0.3
        if conditions.regime_confidence < 0.5:
            risk_score += 0.2
        if conditions.liquidity_score < 0.5:
            risk_score += 0.2
        
        # 信號風險
        if confidence < 0.5:
            risk_score += 0.2
        if recommendation < 0.6:
            risk_score += 0.1
        
        if risk_score >= 0.6:
            return "HIGH"
        elif risk_score >= 0.3:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _cleanup_old_history(self):
        """清理舊的計算歷史"""
        if len(self.calculation_history) > 1000:
            self.calculation_history = self.calculation_history[-500:]
    
    async def get_weight_calculation_history(self, 
                                           symbol: Optional[str] = None,
                                           timeframe: Optional[TradingTimeframe] = None,
                                           limit: int = 100) -> List[WeightCalculationResult]:
        """獲取權重計算歷史"""
        filtered_history = self.calculation_history
        
        if symbol:
            filtered_history = [r for r in filtered_history if r.symbol == symbol]
        
        if timeframe:
            filtered_history = [r for r in filtered_history if r.timeframe == timeframe]
        
        return filtered_history[-limit:]
    
    def export_engine_status(self) -> Dict:
        """導出引擎狀態"""
        return {
            "engine_name": "Dynamic Weight Engine",
            "total_calculations": len(self.calculation_history),
            "cache_entries": len(self.signal_availability_cache),
            "config": self.config,
            "recent_calculations": [
                {
                    "symbol": calc.symbol,
                    "timeframe": calc.timeframe.value,
                    "confidence": round(calc.total_confidence, 3),
                    "recommendation": round(calc.recommendation_score, 3),
                    "risk_level": calc.risk_level,
                    "timestamp": calc.calculation_timestamp.isoformat()
                }
                for calc in self.calculation_history[-10:]
            ]
        }

# 全局引擎實例
dynamic_weight_engine = DynamicWeightEngine()
