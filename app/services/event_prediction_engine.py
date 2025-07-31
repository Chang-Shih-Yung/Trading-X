"""
事件預測引擎 - Trading X Phase 3 Week 1
基於歷史數據和市場模式的事件預測系統
"""

import logging
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
from collections import deque
import pickle
import os

logger = logging.getLogger(__name__)

class PredictionConfidence(Enum):
    """預測信心等級"""
    VERY_LOW = "very_low"      # 0.0-0.3
    LOW = "low"                # 0.3-0.5
    MEDIUM = "medium"          # 0.5-0.7
    HIGH = "high"              # 0.7-0.85
    VERY_HIGH = "very_high"    # 0.85-1.0

class EventCategory(Enum):
    """事件類別"""
    MACRO_ECONOMIC = "macro_economic"      # 宏觀經濟事件
    TECHNICAL_BREAKOUT = "technical_breakout"  # 技術突破事件
    VOLUME_ANOMALY = "volume_anomaly"      # 成交量異常
    VOLATILITY_SPIKE = "volatility_spike"  # 波動率激增
    CORRELATION_BREAK = "correlation_break" # 相關性破裂
    LIQUIDITY_CRISIS = "liquidity_crisis"  # 流動性危機

@dataclass
class MarketPattern:
    """市場模式數據"""
    pattern_id: str
    category: EventCategory
    pattern_features: Dict[str, float]  # 特徵向量
    historical_occurrences: int        # 歷史發生次數
    success_rate: float                # 成功預測率
    avg_lead_time_hours: float         # 平均提前時間（小時）
    confidence_threshold: float        # 信心閾值
    last_occurrence: Optional[datetime] = None

@dataclass
class EventPrediction:
    """事件預測結果"""
    prediction_id: str
    event_category: EventCategory
    predicted_event_time: datetime
    confidence: float
    confidence_level: PredictionConfidence
    affected_symbols: List[str]
    expected_impact_magnitude: float   # 預期影響幅度 (0.0-1.0)
    prediction_horizon_hours: int     # 預測時間範圍
    contributing_patterns: List[str]   # 貢獻的模式ID
    risk_factors: Dict[str, float]    # 風險因子
    prediction_timestamp: datetime
    is_early_warning: bool            # 是否為早期預警

@dataclass
class PredictionValidation:
    """預測驗證結果"""
    prediction_id: str
    actual_event_occurred: bool
    actual_event_time: Optional[datetime]
    actual_impact_magnitude: Optional[float]
    prediction_accuracy: float        # 預測準確度
    time_accuracy: float              # 時間準確度
    impact_accuracy: float            # 影響準確度
    validation_timestamp: datetime

class EventPredictionEngine:
    """事件預測引擎"""
    
    def __init__(self):
        self.patterns_database = {}  # 模式數據庫
        self.prediction_history = deque(maxlen=1000)  # 預測歷史
        self.validation_history = deque(maxlen=500)   # 驗證歷史
        self.market_data_cache = {}  # 市場數據快取
        
        # 預測引擎配置
        self.config = {
            "min_confidence_threshold": 0.3,
            "early_warning_threshold": 0.7,
            "max_prediction_horizon_hours": 168,  # 7天
            "pattern_learning_rate": 0.1,
            "feature_importance_weights": {
                "price_momentum": 0.25,
                "volume_profile": 0.20,
                "volatility_regime": 0.20,
                "market_sentiment": 0.15,
                "correlation_matrix": 0.10,
                "liquidity_conditions": 0.10
            },
            "validation_lookback_hours": 72
        }
        
        # 統計數據
        self.stats = {
            "total_predictions": 0,
            "successful_predictions": 0,
            "early_warnings_issued": 0,
            "patterns_learned": 0,
            "avg_prediction_accuracy": 0.0,
            "prediction_by_category": {},
            "model_last_trained": None
        }
        
        # 初始化基礎模式
        self._initialize_base_patterns()
        logger.info("✅ 事件預測引擎初始化完成")
    
    def _initialize_base_patterns(self):
        """初始化基礎預測模式"""
        base_patterns = [
            # 宏觀經濟事件模式
            MarketPattern(
                pattern_id="macro_fed_meeting",
                category=EventCategory.MACRO_ECONOMIC,
                pattern_features={
                    "fed_meeting_proximity": 1.0,
                    "rate_change_probability": 0.8,
                    "market_volatility_pre": 0.6,
                    "volume_increase_pre": 0.7
                },
                historical_occurrences=24,
                success_rate=0.78,
                avg_lead_time_hours=48,
                confidence_threshold=0.65
            ),
            
            # 技術突破模式
            MarketPattern(
                pattern_id="technical_resistance_break",
                category=EventCategory.TECHNICAL_BREAKOUT,
                pattern_features={
                    "resistance_test_count": 0.8,
                    "volume_confirmation": 0.7,
                    "momentum_buildup": 0.6,
                    "breakout_strength": 0.9
                },
                historical_occurrences=156,
                success_rate=0.72,
                avg_lead_time_hours=12,
                confidence_threshold=0.60
            ),
            
            # 成交量異常模式
            MarketPattern(
                pattern_id="volume_spike_precursor",
                category=EventCategory.VOLUME_ANOMALY,
                pattern_features={
                    "volume_ratio_anomaly": 0.9,
                    "price_volume_divergence": 0.7,
                    "market_microstructure": 0.6,
                    "order_flow_imbalance": 0.8
                },
                historical_occurrences=89,
                success_rate=0.68,
                avg_lead_time_hours=6,
                confidence_threshold=0.55
            ),
            
            # 波動率激增模式
            MarketPattern(
                pattern_id="volatility_regime_change",
                category=EventCategory.VOLATILITY_SPIKE,
                pattern_features={
                    "vix_term_structure": 0.8,
                    "realized_vol_trend": 0.7,
                    "options_flow_sentiment": 0.6,
                    "fear_greed_momentum": 0.5
                },
                historical_occurrences=67,
                success_rate=0.75,
                avg_lead_time_hours=24,
                confidence_threshold=0.70
            ),
            
            # 流動性危機模式
            MarketPattern(
                pattern_id="liquidity_stress_buildup",
                category=EventCategory.LIQUIDITY_CRISIS,
                pattern_features={
                    "bid_ask_widening": 0.9,
                    "depth_deterioration": 0.8,
                    "cross_asset_correlation": 0.7,
                    "funding_stress_indicators": 0.6
                },
                historical_occurrences=23,
                success_rate=0.82,
                avg_lead_time_hours=36,
                confidence_threshold=0.75
            )
        ]
        
        for pattern in base_patterns:
            self.patterns_database[pattern.pattern_id] = pattern
            
        logger.info(f"🎯 初始化 {len(base_patterns)} 個基礎預測模式")
    
    async def analyze_market_conditions(self, symbol: str) -> Dict[str, float]:
        """分析當前市場條件"""
        try:
            # 獲取市場數據 (模擬實現)
            current_time = datetime.now()
            
            # 模擬市場特徵提取
            market_features = {
                "price_momentum": np.random.uniform(0.2, 0.9),
                "volume_profile": np.random.uniform(0.3, 0.8),
                "volatility_regime": np.random.uniform(0.1, 0.7),
                "market_sentiment": np.random.uniform(0.2, 0.6),
                "correlation_matrix": np.random.uniform(0.4, 0.8),
                "liquidity_conditions": np.random.uniform(0.3, 0.7),
                "technical_indicators": np.random.uniform(0.2, 0.8),
                "macro_factor_exposure": np.random.uniform(0.1, 0.5)
            }
            
            # 快取市場數據
            self.market_data_cache[symbol] = {
                "features": market_features,
                "timestamp": current_time
            }
            
            return market_features
            
        except Exception as e:
            logger.error(f"❌ 市場條件分析失敗 {symbol}: {e}")
            return {}
    
    async def generate_predictions(self, symbols: List[str] = None) -> List[EventPrediction]:
        """生成事件預測"""
        try:
            if not symbols:
                symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
            
            predictions = []
            
            for symbol in symbols:
                # 分析市場條件
                market_features = await self.analyze_market_conditions(symbol)
                if not market_features:
                    continue
                
                # 對每個模式進行匹配和預測
                for pattern_id, pattern in self.patterns_database.items():
                    prediction = await self._evaluate_pattern_match(
                        symbol, pattern, market_features
                    )
                    
                    if prediction and prediction.confidence >= self.config["min_confidence_threshold"]:
                        predictions.append(prediction)
                        
                        # 統計更新
                        self.stats["total_predictions"] += 1
                        category = prediction.event_category.value
                        self.stats["prediction_by_category"][category] = (
                            self.stats["prediction_by_category"].get(category, 0) + 1
                        )
                        
                        # 早期預警檢查
                        if prediction.confidence >= self.config["early_warning_threshold"]:
                            prediction.is_early_warning = True
                            self.stats["early_warnings_issued"] += 1
            
            # 保存預測歷史
            for prediction in predictions:
                self.prediction_history.append(prediction)
            
            logger.info(f"🔮 生成 {len(predictions)} 個事件預測")
            return predictions
            
        except Exception as e:
            logger.error(f"❌ 事件預測生成失敗: {e}")
            return []
    
    async def _evaluate_pattern_match(self, symbol: str, pattern: MarketPattern, 
                                    market_features: Dict[str, float]) -> Optional[EventPrediction]:
        """評估模式匹配度並生成預測"""
        try:
            # 計算特徵相似度
            similarity_score = 0.0
            feature_count = 0
            
            for pattern_feature, pattern_value in pattern.pattern_features.items():
                if pattern_feature in market_features:
                    market_value = market_features[pattern_feature]
                    # 計算特徵相似度 (使用餘弦相似度的簡化版本)
                    similarity = 1.0 - abs(pattern_value - market_value)
                    similarity_score += similarity
                    feature_count += 1
            
            if feature_count == 0:
                return None
            
            # 平均相似度
            avg_similarity = similarity_score / feature_count
            
            # 調整信心度 (結合模式成功率和相似度)
            confidence = (avg_similarity * 0.6 + pattern.success_rate * 0.4)
            
            # 檢查是否超過模式閾值
            if confidence < pattern.confidence_threshold:
                return None
            
            # 確定信心等級
            confidence_level = self._determine_confidence_level(confidence)
            
            # 預測事件時間
            predicted_time = datetime.now() + timedelta(hours=pattern.avg_lead_time_hours)
            
            # 計算預期影響幅度
            impact_magnitude = min(1.0, confidence * pattern.success_rate * 1.2)
            
            # 生成風險因子
            risk_factors = {
                "pattern_age": min(1.0, (datetime.now() - (pattern.last_occurrence or datetime.now())).days / 30),
                "market_regime_change": market_features.get("volatility_regime", 0.5),
                "liquidity_risk": 1.0 - market_features.get("liquidity_conditions", 0.5),
                "correlation_risk": market_features.get("correlation_matrix", 0.5)
            }
            
            # 創建預測
            prediction = EventPrediction(
                prediction_id=f"{pattern.pattern_id}_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                event_category=pattern.category,
                predicted_event_time=predicted_time,
                confidence=confidence,
                confidence_level=confidence_level,
                affected_symbols=[symbol],
                expected_impact_magnitude=impact_magnitude,
                prediction_horizon_hours=int(pattern.avg_lead_time_hours * 1.5),
                contributing_patterns=[pattern.pattern_id],
                risk_factors=risk_factors,
                prediction_timestamp=datetime.now(),
                is_early_warning=False
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"❌ 模式匹配評估失敗: {e}")
            return None
    
    def _determine_confidence_level(self, confidence: float) -> PredictionConfidence:
        """確定信心等級"""
        if confidence >= 0.85:
            return PredictionConfidence.VERY_HIGH
        elif confidence >= 0.7:
            return PredictionConfidence.HIGH
        elif confidence >= 0.5:
            return PredictionConfidence.MEDIUM
        elif confidence >= 0.3:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW
    
    async def validate_predictions(self, lookback_hours: int = 72) -> List[PredictionValidation]:
        """驗證歷史預測準確性"""
        try:
            validations = []
            cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
            
            # 找出需要驗證的預測
            predictions_to_validate = [
                p for p in self.prediction_history 
                if p.prediction_timestamp >= cutoff_time and 
                   p.predicted_event_time <= datetime.now()
            ]
            
            for prediction in predictions_to_validate:
                validation = await self._validate_single_prediction(prediction)
                if validation:
                    validations.append(validation)
                    self.validation_history.append(validation)
            
            # 更新統計數據
            if validations:
                successful_predictions = sum(1 for v in validations if v.actual_event_occurred)
                self.stats["successful_predictions"] += successful_predictions
                
                # 計算平均準確率
                avg_accuracy = np.mean([v.prediction_accuracy for v in validations])
                self.stats["avg_prediction_accuracy"] = (
                    self.stats["avg_prediction_accuracy"] * 0.8 + avg_accuracy * 0.2
                )
            
            logger.info(f"📊 驗證 {len(validations)} 個歷史預測")
            return validations
            
        except Exception as e:
            logger.error(f"❌ 預測驗證失敗: {e}")
            return []
    
    async def _validate_single_prediction(self, prediction: EventPrediction) -> Optional[PredictionValidation]:
        """驗證單個預測"""
        try:
            # 模擬事件驗證邏輯
            # 在實際實現中，這裡會查詢真實的市場事件數據
            
            # 基於預測信心度模擬實際發生概率
            actual_occurred = np.random.random() < (prediction.confidence * 0.8)
            
            if actual_occurred:
                # 模擬實際事件時間 (在預測時間附近)
                time_variance_hours = np.random.normal(0, prediction.prediction_horizon_hours * 0.2)
                actual_event_time = prediction.predicted_event_time + timedelta(hours=time_variance_hours)
                
                # 模擬實際影響幅度
                impact_variance = np.random.normal(1.0, 0.3)
                actual_impact = prediction.expected_impact_magnitude * impact_variance
                actual_impact = max(0.0, min(1.0, actual_impact))
                
                # 計算準確度
                time_diff_hours = abs((actual_event_time - prediction.predicted_event_time).total_seconds() / 3600)
                time_accuracy = max(0.0, 1.0 - (time_diff_hours / prediction.prediction_horizon_hours))
                
                impact_diff = abs(actual_impact - prediction.expected_impact_magnitude)
                impact_accuracy = max(0.0, 1.0 - impact_diff)
                
                prediction_accuracy = (time_accuracy * 0.5 + impact_accuracy * 0.5)
                
            else:
                actual_event_time = None
                actual_impact = None
                time_accuracy = 0.0
                impact_accuracy = 0.0
                prediction_accuracy = 0.0
            
            validation = PredictionValidation(
                prediction_id=prediction.prediction_id,
                actual_event_occurred=actual_occurred,
                actual_event_time=actual_event_time,
                actual_impact_magnitude=actual_impact,
                prediction_accuracy=prediction_accuracy,
                time_accuracy=time_accuracy,
                impact_accuracy=impact_accuracy,
                validation_timestamp=datetime.now()
            )
            
            return validation
            
        except Exception as e:
            logger.error(f"❌ 單個預測驗證失敗: {e}")
            return None
    
    async def learn_from_validations(self):
        """從驗證結果中學習並更新模式"""
        try:
            if len(self.validation_history) < 10:
                return
            
            # 分析模式表現
            pattern_performance = {}
            
            for validation in self.validation_history:
                # 找到對應的預測
                prediction = next(
                    (p for p in self.prediction_history if p.prediction_id == validation.prediction_id),
                    None
                )
                
                if prediction:
                    for pattern_id in prediction.contributing_patterns:
                        if pattern_id not in pattern_performance:
                            pattern_performance[pattern_id] = []
                        pattern_performance[pattern_id].append(validation.prediction_accuracy)
            
            # 更新模式成功率
            updated_patterns = 0
            for pattern_id, accuracies in pattern_performance.items():
                if pattern_id in self.patterns_database:
                    pattern = self.patterns_database[pattern_id]
                    avg_accuracy = np.mean(accuracies)
                    
                    # 使用學習率更新成功率
                    learning_rate = self.config["pattern_learning_rate"]
                    pattern.success_rate = (
                        pattern.success_rate * (1 - learning_rate) + 
                        avg_accuracy * learning_rate
                    )
                    
                    updated_patterns += 1
            
            self.stats["patterns_learned"] += updated_patterns
            self.stats["model_last_trained"] = datetime.now()
            
            logger.info(f"🧠 從驗證結果學習，更新 {updated_patterns} 個模式")
            
        except Exception as e:
            logger.error(f"❌ 模式學習失敗: {e}")
    
    def get_prediction_summary(self) -> Dict[str, Any]:
        """獲取預測系統摘要"""
        try:
            recent_predictions = [
                p for p in self.prediction_history 
                if (datetime.now() - p.prediction_timestamp).hours <= 24
            ]
            
            early_warnings = [p for p in recent_predictions if p.is_early_warning]
            
            # 按類別統計
            category_stats = {}
            for prediction in recent_predictions:
                category = prediction.event_category.value
                if category not in category_stats:
                    category_stats[category] = {"count": 0, "avg_confidence": 0.0}
                category_stats[category]["count"] += 1
                category_stats[category]["avg_confidence"] += prediction.confidence
            
            # 計算平均信心度
            for category in category_stats:
                if category_stats[category]["count"] > 0:
                    category_stats[category]["avg_confidence"] /= category_stats[category]["count"]
            
            return {
                "engine_status": "active",
                "total_patterns": len(self.patterns_database),
                "recent_predictions_24h": len(recent_predictions),
                "early_warnings_active": len(early_warnings),
                "prediction_categories": category_stats,
                "engine_stats": self.stats,
                "last_analysis_time": datetime.now().isoformat(),
                "prediction_accuracy": self.stats["avg_prediction_accuracy"],
                "system_health": "good" if self.stats["avg_prediction_accuracy"] > 0.6 else "needs_attention"
            }
            
        except Exception as e:
            logger.error(f"❌ 預測摘要生成失敗: {e}")
            return {"engine_status": "error", "error": str(e)}

# 全局實例
event_prediction_engine = EventPredictionEngine()
