"""
🎯 智能分層系統 - 時間區分短中長線動態調整因子
基於開單時間、市場狀況、波動率等多重因子進行智能分類
"""

import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class TimeframeCategory(Enum):
    """時間框架分類 - 統一標準"""
    ULTRA_SHORT = "ultra_short"  # 超短線: 1-90分鐘 (對應 SHORT_TERM)
    SHORT = "short"              # 短線: 1.5-8小時
    MEDIUM = "medium"            # 中線: 8-48小時
    LONG = "long"                # 長線: 24-120小時

@dataclass
class TimeframeAdjustmentFactor:
    """時間框架調整因子"""
    volatility_factor: float      # 波動率因子 0.5-2.0
    liquidity_factor: float       # 流動性因子 0.8-1.5
    trend_strength_factor: float  # 趋势强度因子 0.6-1.8
    market_session_factor: float  # 市場時段因子 0.7-1.3
    risk_factor: float            # 風險因子 0.4-2.5
    confidence_multiplier: float  # 信心度倍數 0.8-1.5

@dataclass
class IntelligentTimeframeResult:
    """智能時間框架分析結果"""
    category: TimeframeCategory
    recommended_duration_minutes: int
    adjustment_factors: TimeframeAdjustmentFactor  
    confidence_score: float        # 分類信心度 0.0-1.0
    reasoning: str                # 分類推理
    risk_level: str               # 風險等級
    optimal_entry_window: int     # 最佳進場窗口(分鐘)

class IntelligentTimeframeClassifier:
    """智能時間框架分類器 - 整合Phase策略動態參數"""
    
    def __init__(self):
        # 導入Phase策略引擎以獲取動態參數
        try:
            from app.services.signal_scoring_engine import signal_scoring_engine
            from app.services.phase1b_volatility_adaptation import enhanced_signal_scoring_engine
            self.phase_engine = signal_scoring_engine
            self.phase1b_engine = enhanced_signal_scoring_engine
            self.use_dynamic_params = True
        except ImportError:
            self.use_dynamic_params = False
            
        self.classification_config = {
            "ultra_short": {
                "base_duration_range": (1, 15),      # 1-15分鐘
                "volatility_threshold": 0.025,       # 高波動要求
                "liquidity_threshold": 1.5,          # 高流動性要求
                "risk_tolerance": 0.02,              # 2%最大風險
                "confidence_threshold": self._get_dynamic_confidence_threshold("ultra_short")
            },
            "short": {
                "base_duration_range": (15, 120),    # 15分鐘-2小時
                "volatility_threshold": 0.015,       # 中等波動
                "liquidity_threshold": 1.2,          
                "risk_tolerance": 0.03,              # 3%風險
                "confidence_threshold": self._get_dynamic_confidence_threshold("short")
            },
            "medium": {
                "base_duration_range": (120, 1440),  # 2-24小時
                "volatility_threshold": 0.008,       # 較低波動
                "liquidity_threshold": 1.0,
                "risk_tolerance": 0.05,              # 5%風險
                "confidence_threshold": self._get_dynamic_confidence_threshold("medium")
            },
            "long": {
                "base_duration_range": (1440, 10080), # 1-7天
                "volatility_threshold": 0.005,        # 低波動
                "liquidity_threshold": 0.8,
                "risk_tolerance": 0.08,               # 8%風險
                "confidence_threshold": self._get_dynamic_confidence_threshold("long")
            }
        }
        
        # 市場時段調整表
        self.session_adjustments = {
            "asia_morning": 1.1,      # 8-12點
            "asia_afternoon": 1.0,    # 12-15點
            "europe_opening": 0.8,    # 15-17點
            "europe_session": 0.9,    # 17-21點
            "us_opening": 0.7,        # 21-23點
            "us_session": 0.8,        # 23-2點
            "overnight": 1.3          # 2-8點
        }
        
        logger.info("🎯 智能時間框架分類器初始化完成")
    
    def _get_dynamic_confidence_threshold(self, timeframe_type: str) -> float:
        """從Phase策略引擎獲取動態信心度閾值"""
        if not self.use_dynamic_params:
            # 回退到靜態值
            fallback_thresholds = {
                "ultra_short": 0.85,
                "short": 0.75, 
                "medium": 0.65,
                "long": 0.55
            }
            return fallback_thresholds.get(timeframe_type, 0.75)
        
        try:
            # 使用Phase策略動態計算的基礎信心度
            base_threshold = getattr(self.phase_engine.templates, 'confidence_threshold', None)
            if base_threshold is None:
                # 從當前活躍的週期模板獲取
                active_template = self.phase_engine.templates.get_current_active_template()
                base_threshold = getattr(active_template, 'confidence_threshold', 0.75)
            
            # 根據時間框架類型調整
            timeframe_adjustments = {
                "ultra_short": 0.10,  # 超短線需要更高信心度
                "short": 0.0,         # 短線使用基準值
                "medium": -0.10,      # 中線稍微降低要求
                "long": -0.20         # 長線進一步降低要求
            }
            
            adjustment = timeframe_adjustments.get(timeframe_type, 0.0)
            final_threshold = max(0.3, min(0.9, base_threshold + adjustment))
            
            logger.debug(f"🎯 {timeframe_type} 動態信心度閾值: {base_threshold:.3f} + {adjustment:.3f} = {final_threshold:.3f}")
            return final_threshold
            
        except Exception as e:
            logger.warning(f"⚠️ 動態閾值獲取失敗: {e}，使用靜態值")
            fallback_thresholds = {
                "ultra_short": 0.85,
                "short": 0.75,
                "medium": 0.65, 
                "long": 0.55
            }
            return fallback_thresholds.get(timeframe_type, 0.75)
    
    def _get_phase_confidence_default(self) -> float:
        """獲取Phase策略默認信心度值"""
        if not self.use_dynamic_params:
            return 0.7  # 靜態回退值
        
        try:
            # 使用當前活躍的模板信心度
            active_template = self.phase_engine.templates.get_current_active_template()
            base_confidence = getattr(active_template, 'confidence_threshold', 0.75)
            return base_confidence
        except Exception as e:
            logger.debug(f"⚠️ 獲取Phase默認信心度失敗: {e}")
            return 0.7
    
    async def classify_timeframe(
        self,
        signal_data: Dict[str, Any],
        market_data: Dict[str, Any],
        current_time: Optional[datetime] = None
    ) -> IntelligentTimeframeResult:
        """
        智能分類時間框架
        
        Args:
            signal_data: 信號數據 (包含信心度、信號強度等)
            market_data: 市場數據 (包含波動率、流動性等)
            current_time: 當前時間
            
        Returns:
            IntelligentTimeframeResult: 分類結果
        """
        try:
            if current_time is None:
                current_time = datetime.now()
            
            # 1. 計算調整因子
            adjustment_factors = self._calculate_adjustment_factors(signal_data, market_data, current_time)
            
            # 2. 評估各時間框架適合度
            category_scores = {}
            for category_name, config in self.classification_config.items():
                score = await self._evaluate_category_fitness(
                    signal_data, market_data, adjustment_factors, 
                    category_name, config
                )
                category_scores[category_name] = score
            
            # 3. 選擇最佳分類
            best_category_name = max(category_scores, key=category_scores.get)
            best_score = category_scores[best_category_name]
            
            # 4. 計算推薦持續時間
            recommended_duration = self._calculate_recommended_duration(
                best_category_name, adjustment_factors, signal_data
            )
            
            # 5. 生成分析推理
            reasoning = self._generate_classification_reasoning(
                best_category_name, category_scores, adjustment_factors
            )
            
            # 6. 評估風險等級
            risk_level = self._assess_risk_level(adjustment_factors, best_category_name)
            
            # 7. 計算最佳進場窗口
            optimal_entry_window = self._calculate_optimal_entry_window(
                recommended_duration, adjustment_factors
            )
            
            result = IntelligentTimeframeResult(
                category=TimeframeCategory(best_category_name),
                recommended_duration_minutes=recommended_duration,
                adjustment_factors=adjustment_factors,
                confidence_score=best_score,
                reasoning=reasoning,
                risk_level=risk_level,
                optimal_entry_window=optimal_entry_window
            )
            
            logger.info(f"🎯 時間框架分類完成: {best_category_name} ({recommended_duration}分鐘, 信心度: {best_score:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 智能時間框架分類失敗: {e}")
            # 返回默認分類
            return self._get_default_classification()
    
    def _calculate_adjustment_factors(
        self, 
        signal_data: Dict[str, Any], 
        market_data: Dict[str, Any],
        current_time: datetime
    ) -> TimeframeAdjustmentFactor:
        """計算調整因子"""
        
        # 1. 波動率因子 (0.5-2.0)
        volatility = market_data.get('volatility', 0.02)
        if volatility > 0.04:
            volatility_factor = 0.5  # 高波動 -> 縮短時間
        elif volatility > 0.02:
            volatility_factor = 0.8
        elif volatility > 0.01:
            volatility_factor = 1.0
        elif volatility > 0.005:
            volatility_factor = 1.4
        else:
            volatility_factor = 2.0  # 低波動 -> 延長時間
        
        # 2. 流動性因子 (0.8-1.5)
        volume_ratio = market_data.get('volume_ratio', 1.0)
        if volume_ratio > 2.0:
            liquidity_factor = 0.8   # 高流動性 -> 快速執行
        elif volume_ratio > 1.5:
            liquidity_factor = 0.9
        elif volume_ratio > 0.8:
            liquidity_factor = 1.0
        else:
            liquidity_factor = 1.5   # 低流動性 -> 延長等待
        
        # 3. 趨勢強度因子 (0.6-1.8)
        trend_strength = signal_data.get('trend_strength', 0.5)
        if trend_strength > 0.8:
            trend_strength_factor = 0.6  # 強趨勢 -> 快速跟隨
        elif trend_strength > 0.6:
            trend_strength_factor = 0.8
        elif trend_strength > 0.4:
            trend_strength_factor = 1.0
        elif trend_strength > 0.2:
            trend_strength_factor = 1.4
        else:
            trend_strength_factor = 1.8  # 弱趨勢 -> 延長觀察
        
        # 4. 市場時段因子
        market_session_factor = self._get_market_session_factor(current_time)
        
        # 5. 風險因子 (0.4-2.5) - 使用Phase策略動態閾值
        signal_confidence = signal_data.get('confidence', self._get_phase_confidence_default())
        signal_strength = signal_data.get('signal_strength', self._get_phase_confidence_default())
        combined_reliability = (signal_confidence + signal_strength) / 2
        
        if combined_reliability > 0.9:
            risk_factor = 0.4    # 高可靠性 -> 快速行動
        elif combined_reliability > 0.8:
            risk_factor = 0.7
        elif combined_reliability > 0.7:
            risk_factor = 1.0
        elif combined_reliability > 0.6:
            risk_factor = 1.5
        else:
            risk_factor = 2.5    # 低可靠性 -> 謹慎等待
        
        # 6. 信心度倍數 (0.8-1.5)
        if signal_confidence > 0.9:
            confidence_multiplier = 1.5
        elif signal_confidence > 0.8:
            confidence_multiplier = 1.2
        elif signal_confidence > 0.7:
            confidence_multiplier = 1.0
        else:
            confidence_multiplier = 0.8
        
        return TimeframeAdjustmentFactor(
            volatility_factor=volatility_factor,
            liquidity_factor=liquidity_factor,
            trend_strength_factor=trend_strength_factor,
            market_session_factor=market_session_factor,
            risk_factor=risk_factor,
            confidence_multiplier=confidence_multiplier
        )
    
    def _get_market_session_factor(self, current_time: datetime) -> float:
        """獲取市場時段調整因子"""
        hour = current_time.hour
        
        if 8 <= hour < 12:
            return self.session_adjustments["asia_morning"]
        elif 12 <= hour < 15:
            return self.session_adjustments["asia_afternoon"]
        elif 15 <= hour < 17:
            return self.session_adjustments["europe_opening"]
        elif 17 <= hour < 21:
            return self.session_adjustments["europe_session"]
        elif 21 <= hour < 23:
            return self.session_adjustments["us_opening"]
        elif 23 <= hour or hour < 2:
            return self.session_adjustments["us_session"]
        else:
            return self.session_adjustments["overnight"]
    
    async def _evaluate_category_fitness(
        self,
        signal_data: Dict[str, Any],
        market_data: Dict[str, Any],
        adjustment_factors: TimeframeAdjustmentFactor,
        category_name: str,
        config: Dict[str, Any]
    ) -> float:
        """評估分類適合度"""
        
        score = 0.0
        max_score = 1.0
        
        # 1. 波動率適合度 (權重: 25%)
        volatility = market_data.get('volatility', 0.02)
        volatility_threshold = config['volatility_threshold']
        
        if category_name in ['ultra_short', 'short']:
            # 短線需要足夠波動率
            volatility_score = min(volatility / volatility_threshold, 2.0) * 0.5
        else:
            # 中長線避免過高波動
            if volatility <= volatility_threshold:
                volatility_score = 1.0
            else:
                volatility_score = max(0.0, 1.0 - (volatility - volatility_threshold) / volatility_threshold)
        
        score += volatility_score * 0.25
        
        # 2. 流動性適合度 (權重: 20%)
        volume_ratio = market_data.get('volume_ratio', 1.0)
        liquidity_threshold = config['liquidity_threshold']
        
        if volume_ratio >= liquidity_threshold:
            liquidity_score = 1.0
        else:
            liquidity_score = volume_ratio / liquidity_threshold
        
        score += liquidity_score * 0.20
        
        # 3. 信心度適合度 (權重: 25%)
        signal_confidence = signal_data.get('confidence', 0.7)
        confidence_threshold = config['confidence_threshold']
        
        if signal_confidence >= confidence_threshold:
            confidence_score = 1.0 + (signal_confidence - confidence_threshold) * 0.5
        else:
            confidence_score = signal_confidence / confidence_threshold * 0.8
        
        score += min(confidence_score, 1.0) * 0.25
        
        # 4. 風險適合度 (權重: 15%)
        expected_risk = signal_data.get('expected_risk', 0.03)
        risk_tolerance = config['risk_tolerance']
        
        if expected_risk <= risk_tolerance:
            risk_score = 1.0
        else:
            risk_score = max(0.0, 1.0 - (expected_risk - risk_tolerance) / risk_tolerance)
        
        score += risk_score * 0.15
        
        # 5. 市場時段適合度 (權重: 15%)
        session_factor = adjustment_factors.market_session_factor
        
        if category_name in ['ultra_short', 'short']:
            # 短線在活躍時段更適合
            session_score = max(0.0, 2.0 - session_factor)  # 因子越小(越活躍)得分越高
        else:
            # 中長線時段影響較小
            session_score = 0.8
        
        score += session_score * 0.15
        
        return min(score, max_score)
    
    def _calculate_recommended_duration(
        self,
        category_name: str,
        adjustment_factors: TimeframeAdjustmentFactor,
        signal_data: Dict[str, Any]
    ) -> int:
        """計算推薦持續時間 - 基於 Phase 1B/1C + Phase 1+2+3 多維分析"""
        
        # 🎯 基礎時間（小時）
        base_times_hours = {
            'ultra_short': 0.25,   # 15分鐘
            'short': 3,            # 短線: 3小時基礎
            'medium': 18,          # 中線: 18小時基礎
            'long': 48             # 長線: 48小時基礎
        }
        
        base_hours = base_times_hours[category_name]
        
        # 🎯 Phase 1B 多維分析加成
        indicator_count = signal_data.get('indicator_count', 5)  # 預設5個指標
        phase1b_multiplier = 1.0 + (indicator_count - 3) * 0.1
        phase1b_multiplier = max(0.8, min(1.5, phase1b_multiplier))  # 限制80%-150%
        
        # 🎯 Phase 1C 精準度調整
        precision = signal_data.get('confidence', 0.8)
        phase1c_multiplier = 0.7 + (precision * 0.6)
        
        # 🎯 Phase 1+2+3 技術強度加成
        technical_strength = signal_data.get('signal_strength', 0.7)
        market_confidence = signal_data.get('market_confidence', 0.8)
        risk_reward_ratio = signal_data.get('risk_reward_ratio', 2.0)
        
        technical_multiplier = 0.8 + (technical_strength * 0.4)  # 0.8-1.2倍
        confidence_multiplier = 0.9 + (market_confidence * 0.3)  # 0.9-1.2倍
        convergence_multiplier = min(1.3, 1.0 + (risk_reward_ratio - 2.0) * 0.1)  # 最高1.3倍
        
        phase123_multiplier = (technical_multiplier + confidence_multiplier + convergence_multiplier) / 3
        
        # 🎯 品質評分時間加成
        quality_score = signal_data.get('quality_score', 5.0)
        if quality_score >= 8.0:
            quality_multiplier = 1.4    # 高品質+40%
        elif quality_score >= 6.5:
            quality_multiplier = 1.2    # 中高品質+20%
        elif quality_score >= 5.0:
            quality_multiplier = 1.0    # 標準時間
        else:
            quality_multiplier = 0.8    # 低品質-20%
        
        # 🎯 市場條件調整
        market_conditions = signal_data.get('market_strength', 0.7)  # 市場強度
        if market_conditions >= 0.8:
            market_multiplier = 1.2     # 好市場+20%
        elif market_conditions >= 0.6:
            market_multiplier = 1.0     # 正常市場
        else:
            market_multiplier = 0.8     # 差市場-20%
        
        # 🎯 綜合計算
        # Step 1: Phase1ABC 處理
        phase1abc_time = base_hours * phase1b_multiplier * phase1c_multiplier
        
        # Step 2: Phase123 增強
        phase123_time = phase1abc_time * phase123_multiplier
        
        # Step 3: 品質和市場調整
        final_hours = phase123_time * quality_multiplier * market_multiplier
        
        # 🎯 時間範圍限制（小時）
        limits_hours = {
            'ultra_short': (0.025, 0.25),  # 1.5分鐘-15分鐘
            'short': (1.5, 8.0),           # 短線: 1.5-8小時
            'medium': (8.0, 48.0),         # 中線: 8-48小時
            'long': (24.0, 120.0)          # 長線: 24-120小時
        }
        
        min_hours, max_hours = limits_hours[category_name]
        constrained_hours = max(min_hours, min(max_hours, final_hours))
        
        # 轉換為分鐘
        final_minutes = int(constrained_hours * 60)
        
        logger.info(f"🎯 {category_name} 時間計算: {base_hours}h → Phase1ABC:{phase1abc_time:.2f}h → Phase123:{phase123_time:.2f}h → 最終:{final_minutes}分鐘")
        
        return final_minutes
    
    def _generate_classification_reasoning(
        self,
        selected_category: str,
        category_scores: Dict[str, float],
        adjustment_factors: TimeframeAdjustmentFactor
    ) -> str:
        """生成分類推理"""
        
        category_names = {
            'ultra_short': '超短線',
            'short': '短線',
            'medium': '中線', 
            'long': '長線'
        }
        
        selected_name = category_names[selected_category]
        selected_score = category_scores[selected_category]
        
        # 找出關鍵影響因子
        factors = {
            '波動率': adjustment_factors.volatility_factor,
            '流動性': adjustment_factors.liquidity_factor, 
            '趨勢強度': adjustment_factors.trend_strength_factor,
            '市場時段': adjustment_factors.market_session_factor,
            '風險評估': adjustment_factors.risk_factor,
            '信心度': adjustment_factors.confidence_multiplier
        }
        
        # 找出最主要的影響因子
        extreme_factors = []
        for name, value in factors.items():
            if value <= 0.7:
                extreme_factors.append(f"{name}促進快速執行({value:.2f})")
            elif value >= 1.3:
                extreme_factors.append(f"{name}建議延長等待({value:.2f})")
        
        reasoning = f"🎯 智能分析建議採用{selected_name}策略 (適合度: {selected_score:.3f})\n\n"
        
        if extreme_factors:
            reasoning += "📊 主要影響因子:\n" + "\n".join(f"• {factor}" for factor in extreme_factors[:3])
        else:
            reasoning += "📊 各項指標均衡，適合標準執行策略"
        
        # 添加與其他分類的比較
        other_scores = {k: v for k, v in category_scores.items() if k != selected_category}
        if other_scores:
            second_best = max(other_scores, key=other_scores.get)
            second_score = other_scores[second_best]
            if selected_score - second_score < 0.1:
                reasoning += f"\n\n⚠️ 與{category_names[second_best]}策略評分接近({second_score:.3f})，建議密切監控"
        
        return reasoning
    
    def _assess_risk_level(self, adjustment_factors: TimeframeAdjustmentFactor, category: str) -> str:
        """評估風險等級"""
        
        risk_score = (
            adjustment_factors.volatility_factor * 0.3 +
            adjustment_factors.risk_factor * 0.4 +
            (2.0 - adjustment_factors.confidence_multiplier) * 0.3
        )
        
        if risk_score <= 0.8:
            return "LOW"
        elif risk_score <= 1.2:
            return "MEDIUM"
        elif risk_score <= 1.8:
            return "HIGH"
        else:
            return "EXTREME"
    
    def _calculate_optimal_entry_window(
        self, 
        duration_minutes: int, 
        adjustment_factors: TimeframeAdjustmentFactor
    ) -> int:
        """計算最佳進場窗口"""
        
        # 基礎進場窗口為持續時間的10-20%
        base_window = duration_minutes * 0.15
        
        # 根據流動性和信心度調整
        window_adjustment = (
            adjustment_factors.liquidity_factor * 0.5 +
            adjustment_factors.confidence_multiplier * 0.5
        )
        
        optimal_window = base_window * window_adjustment
        
        # 限制最小1分鐘，最大為持續時間的30%
        return int(max(1, min(duration_minutes * 0.3, optimal_window)))
    
    def _get_default_classification(self) -> IntelligentTimeframeResult:
        """獲取默認分類(發生錯誤時使用)"""
        
        default_factors = TimeframeAdjustmentFactor(
            volatility_factor=1.0,
            liquidity_factor=1.0,
            trend_strength_factor=1.0,
            market_session_factor=1.0,
            risk_factor=1.0,
            confidence_multiplier=1.0
        )
        
        return IntelligentTimeframeResult(
            category=TimeframeCategory.SHORT,
            recommended_duration_minutes=60,
            adjustment_factors=default_factors,
            confidence_score=0.5,
            reasoning="🔄 系統錯誤，使用默認短線策略",
            risk_level="MEDIUM",
            optimal_entry_window=10
        )

# 全局實例
intelligent_timeframe_classifier = IntelligentTimeframeClassifier()

# 🎯 Phase 2+3 增強擴展方法
class IntelligentTimeframeClassifierEnhanced:
    """Phase 2+3 增強的智能時間框架分類器"""
    
    def __init__(self):
        self.base_classifier = intelligent_timeframe_classifier
        
    async def get_enhanced_timeframe_classification(self, 
                                                 symbol: str, 
                                                 df: pd.DataFrame) -> Dict[str, Any]:
        """
        🎯 Phase 2+3 增強時間框架分類
        整合市場體制分析和深度數據
        """
        try:
            # 基礎分類
            base_result = await self.base_classifier.classify_intelligent_timeframe(df)
            base_classification = base_result.to_dict()
            
            # 🚀 Phase 2 市場體制增強
            phase2_analysis = await self._get_phase2_market_analysis(symbol)
            
            # 🚀 Phase 3 市場深度增強
            phase3_analysis = await self._get_phase3_market_depth(symbol)
            
            # 🧠 智能融合算法
            enhanced_timeframe = self._fuse_phase_analyses(
                base_classification,
                phase2_analysis, 
                phase3_analysis
            )
            
            return {
                **base_classification,
                "enhanced_timeframe": enhanced_timeframe,
                "phase2_factors": phase2_analysis,
                "phase3_factors": phase3_analysis,
                "fusion_confidence": enhanced_timeframe.get("confidence", 0.8),
                "recommended_duration_enhanced": enhanced_timeframe.get("duration_minutes", 60)
            }
            
        except Exception as e:
            logger.error(f"增強時間框架分類失敗: {e}")
            base_result = await self.base_classifier.classify_intelligent_timeframe(df)
            return base_result.to_dict()
    
    async def _get_phase2_market_analysis(self, symbol: str) -> Dict[str, Any]:
        """獲取 Phase 2 市場體制分析"""
        try:
            # 這裡會調用 Phase 2 分析 API
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = f"http://localhost:8000/api/v1/scalping/phase2-market-regime"
                params = {"symbols": symbol}
                
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("market_analysis", {})
                        
        except Exception as e:
            logger.warning(f"Phase 2 分析獲取失敗: {e}")
            
        return {
            "market_regime": "neutral",
            "bull_bear_score": 0.5,
            "fear_greed_index": 50,
            "timeframe_impact": "medium"
        }
    
    async def _get_phase3_market_depth(self, symbol: str) -> Dict[str, Any]:
        """獲取 Phase 3 市場深度分析"""
        try:
            # 這裡會調用 Phase 3 分析 API
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = f"http://localhost:8000/api/v1/scalping/phase3-market-depth"
                
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        analyses = data.get("phase3_analyses", [])
                        
                        # 找到對應symbol的分析
                        for analysis in analyses:
                            if analysis.get("symbol") == symbol:
                                return analysis.get("phase3_assessment", {})
                                
        except Exception as e:
            logger.warning(f"Phase 3 分析獲取失敗: {e}")
            
        return {
            "market_pressure_score": 0.5,
            "order_book_imbalance": 0.0,
            "funding_rate_sentiment": "neutral",
            "depth_impact": "medium"
        }
    
    def _fuse_phase_analyses(self, 
                           base: Dict[str, Any],
                           phase2: Dict[str, Any], 
                           phase3: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 Phase 2+3 分析融合算法
        """
        try:
            base_duration = base.get("recommended_duration_minutes", 60)
            base_confidence = base.get("confidence_score", 0.8)
            
            # Phase 2 市場體制調整
            market_regime = phase2.get("market_regime", "neutral")
            bull_bear_score = phase2.get("bull_bear_score", 0.5)
            fear_greed = phase2.get("fear_greed_index", 50)
            
            # Phase 3 市場深度調整
            pressure_score = phase3.get("market_pressure_score", 0.5)
            funding_sentiment = phase3.get("funding_rate_sentiment", "neutral")
            
            # 🎯 智能時間框架調整算法
            duration_multiplier = 1.0
            confidence_adjustment = 0.0
            
            # 市場體制影響
            if market_regime == "trending":
                duration_multiplier *= 1.3  # 趨勢市場延長時間
                confidence_adjustment += 0.1
            elif market_regime == "consolidating":
                duration_multiplier *= 0.8  # 盤整市場縮短時間
                confidence_adjustment -= 0.05
                
            # 牛熊情緒影響
            if bull_bear_score > 0.7:  # 強烈看漲
                duration_multiplier *= 1.2
                confidence_adjustment += 0.05
            elif bull_bear_score < 0.3:  # 強烈看跌
                duration_multiplier *= 1.15
                confidence_adjustment += 0.05
                
            # 恐懼貪婪指數影響
            if fear_greed > 80 or fear_greed < 20:  # 極端情緒
                duration_multiplier *= 0.9  # 縮短時間，快進快出
                confidence_adjustment += 0.1  # 但信心度提高
                
            # 市場壓力影響
            if pressure_score > 0.7:  # 高壓力環境
                duration_multiplier *= 0.85
                confidence_adjustment += 0.05
            elif pressure_score < 0.3:  # 低壓力環境
                duration_multiplier *= 1.1
                
            # 資金費率情緒影響
            if funding_sentiment == "extreme_bullish":
                duration_multiplier *= 0.9  # 避免過度樂觀
            elif funding_sentiment == "extreme_bearish":
                duration_multiplier *= 0.9  # 避免過度悲觀
                
            # 計算最終值
            enhanced_duration = int(base_duration * duration_multiplier)
            enhanced_confidence = min(1.0, max(0.0, base_confidence + confidence_adjustment))
            
            # 🎯 智能分層決策
            if enhanced_duration <= 30:
                timeframe_category = "ultra_short"
                category_zh = "超短線"
            elif enhanced_duration <= 90:
                timeframe_category = "short"
                category_zh = "短線"
            elif enhanced_duration <= 240:
                timeframe_category = "medium"
                category_zh = "中線"
            else:
                timeframe_category = "long"
                category_zh = "長線"
                
            reasoning_parts = []
            if market_regime != "neutral":
                reasoning_parts.append(f"市場{market_regime}")
            if abs(bull_bear_score - 0.5) > 0.2:
                sentiment = "看漲" if bull_bear_score > 0.5 else "看跌"
                reasoning_parts.append(f"{sentiment}情緒")
            if fear_greed > 80:
                reasoning_parts.append("極度貪婪")
            elif fear_greed < 20:
                reasoning_parts.append("極度恐懼")
            if abs(pressure_score - 0.5) > 0.2:
                pressure = "高壓" if pressure_score > 0.5 else "低壓"
                reasoning_parts.append(f"{pressure}環境")
                
            reasoning = f"Phase2+3分析: {', '.join(reasoning_parts) if reasoning_parts else '均衡市場'}"
            
            return {
                "timeframe_category": timeframe_category,
                "timeframe_category_zh": category_zh,
                "duration_minutes": enhanced_duration,
                "confidence": enhanced_confidence,
                "reasoning": reasoning,
                "phase2_influence": {
                    "market_regime": market_regime,
                    "bull_bear_score": bull_bear_score,
                    "fear_greed_index": fear_greed
                },
                "phase3_influence": {
                    "pressure_score": pressure_score,
                    "funding_sentiment": funding_sentiment
                },
                "fusion_factors": {
                    "duration_multiplier": duration_multiplier,
                    "confidence_adjustment": confidence_adjustment
                }
            }
            
        except Exception as e:
            logger.error(f"Phase融合算法失敗: {e}")
            return {
                "timeframe_category": base.get("category", "short"),
                "timeframe_category_zh": "短線",
                "duration_minutes": base.get("recommended_duration_minutes", 60),
                "confidence": base.get("confidence_score", 0.8),
                "reasoning": "使用基礎分類（融合失敗）"
            }

# 創建增強分類器實例
enhanced_timeframe_classifier = IntelligentTimeframeClassifierEnhanced()
