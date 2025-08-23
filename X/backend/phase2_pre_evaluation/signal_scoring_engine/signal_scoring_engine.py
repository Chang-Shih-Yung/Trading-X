"""
🎯 Trading X - Enhanced Signal Scoring Engine (Integrated Version) v2.1.0
完全符合 signal_scoring_engine.json 規範的增強信號評分引擎
模組類型：embedded_scoring_engine
整合模式：embedded_in_epl_step3_quality_control
"""

from typing import Dict, Any, List
import math
import statistics

# 為了向後兼容，提供 SignalScoringEngine 別名
class SignalScoringEngine:
    """向後兼容的信號評分引擎"""
    
    def __init__(self):
        self.enhanced_engine = EnhancedSignalScoringEngine()
    
    def calculate_score(self, signal_data: Dict[str, Any]) -> float:
        """計算信號評分"""
        try:
            result = self.enhanced_engine.calculate_enhanced_score(signal_data)
            return result.get('final_score', 0.0)
        except Exception as e:
            return 0.0
    
    def evaluate_signal_quality(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """評估信號品質"""
        return self.enhanced_engine.calculate_enhanced_score(signal_data)

class EnhancedSignalScoringEngine:
    """
    增強信號評分引擎 v2.1.0
    包含微異常檢測和源共識驗證的整合版本
    """
    
    def __init__(self):
        # 評分算法權重 (JSON 規範要求)
        self.scoring_weights = {
            "strength_scoring": 0.3,
            "confidence_scoring": 0.25, 
            "quality_scoring": 0.2,
            "risk_scoring": 0.15,
            "timing_scoring": 0.1
        }
        
        # 源共識驗證閾值
        self.consensus_thresholds = {
            "source_overlap_threshold": 0.72,
            "model_diversity_threshold": 0.8,
            "action_bias_threshold": 0.85
        }
        
        # 微異常檢測參數
        self.anomaly_detection_params = {
            "volatility_jump_threshold": 0.3,
            "confidence_drop_threshold": 0.1,
            "window_size_minutes": 15
        }
        
        # 歷史數據用於基線計算
        self.historical_confidence_data = []
        self.signal_volatility_history = []
        
        # 🎯 分層系統整合
        self.tier_aware_scoring = True
        self.tier_boost_factors = {
            'CRITICAL': 1.2,    # 🚨 CRITICAL 層級信號加成 20%
            'HIGH': 1.1,        # 🎯 HIGH 層級信號加成 10%
            'MEDIUM': 1.0,      # 📊 MEDIUM 層級信號保持原值
            'LOW': 0.9          # 📈 LOW 層級信號降低 10%
        }
    
    def score_signal(self, signal_data: Dict[str, Any]) -> Dict[str, float]:
        """
        信號評分主方法 - 3ms embedded processing + 分層意識增強
        
        處理層:
        - Layer 0: Data Extraction (1ms)  
        - Layer 1: Score Calculation (2ms)
        - Layer 2: Tier Enhancement (0.5ms) 🎯 新增
        """
        try:
            # Layer 0: Data Extraction (1ms)
            extracted_metrics = self._layer_0_data_extraction(signal_data)
            
            # Layer 1: Score Calculation (2ms)
            base_score_dict = self._layer_1_score_calculation(extracted_metrics, signal_data)
            
            # Layer 2: Tier Enhancement (0.5ms) 🎯 分層增強
            if self.tier_aware_scoring:
                enhanced_score_dict = self._layer_2_tier_enhancement(base_score_dict, signal_data)
                return enhanced_score_dict
            else:
                return base_score_dict
            
        except Exception:
            # 預設回傳值
            return {
                "strength_score": 0.5,
                "confidence_score": 0.7,
                "quality_score": 0.6,
                "risk_score": 0.5,
                "timing_score": 0.8
            }
    
    def _layer_0_data_extraction(self, signal_data: Dict[str, Any]) -> Dict[str, float]:
        """Layer 0: 數據提取和微異常檢測 (1ms)"""
        # 提取基本數據
        base_value = signal_data.get('value', 0.5)
        confidence = signal_data.get('confidence', 0.7)
        signal_strength = signal_data.get('signal_strength', abs(base_value))
        
        # 微異常檢測
        volatility_jump_penalty = self._detect_volatility_jump(signal_strength)
        confidence_drop_rate_monitoring = self._monitor_confidence_drop_rate(confidence)
        
        return {
            "base_value": base_value,
            "confidence": confidence,
            "signal_strength": signal_strength,
            "volatility_jump_penalty": volatility_jump_penalty,
            "confidence_drop_rate_monitoring": confidence_drop_rate_monitoring
        }
    
    def _layer_1_score_calculation(self, extracted_metrics: Dict[str, float], signal_data: Dict[str, Any]) -> Dict[str, float]:
        """Layer 1: 完整評分計算 (2ms)"""
        base_value = extracted_metrics["base_value"]
        confidence = extracted_metrics["confidence"]
        signal_strength = extracted_metrics["signal_strength"]
        volatility_penalty = extracted_metrics["volatility_jump_penalty"]
        confidence_drop_penalty = extracted_metrics["confidence_drop_rate_monitoring"]
        
        # 增強評分算法
        strength_score = self._calculate_strength_scoring(signal_strength, volatility_penalty)
        confidence_score = self._calculate_confidence_scoring(confidence, confidence_drop_penalty)
        quality_score = self._calculate_quality_scoring(strength_score, confidence_score)
        risk_score = self._calculate_risk_scoring(signal_strength)
        timing_score = self._calculate_timing_scoring(signal_data)
        
        # 源共識驗證 (如果有多個信號源)
        if 'sources' in signal_data:
            consensus_adjustment = self._perform_source_consensus_validation(signal_data['sources'])
            strength_score *= consensus_adjustment
            confidence_score *= consensus_adjustment
        
        return {
            "strength_score": min(1.0, max(0.0, strength_score)),
            "confidence_score": min(1.0, max(0.0, confidence_score)),
            "quality_score": min(1.0, max(0.0, quality_score)),
            "risk_score": min(1.0, max(0.0, risk_score)),
            "timing_score": min(1.0, max(0.0, timing_score))
        }
    
    def _calculate_strength_scoring(self, signal_strength: float, volatility_penalty: float) -> float:
        """強度評分：linear_scoring_based_on_signal_strength + volatility_jump_penalty"""
        base_strength = min(1.0, abs(signal_strength))
        adjusted_strength = base_strength * (1.0 - volatility_penalty)
        return adjusted_strength
    
    def _calculate_confidence_scoring(self, confidence: float, confidence_drop_penalty: float) -> float:
        """信心評分：direct_confidence_mapping_with_drop_rate_detection"""
        adjusted_confidence = confidence * (1.0 - confidence_drop_penalty)
        return min(1.0, max(0.0, adjusted_confidence))
    
    def _calculate_quality_scoring(self, strength_score: float, confidence_score: float) -> float:
        """質量評分：average_of_strength_and_confidence"""
        return (strength_score + confidence_score) / 2
    
    def _calculate_risk_scoring(self, signal_strength: float) -> float:
        """風險評分：inverse_risk_assessment"""
        return 1.0 - min(1.0, abs(signal_strength) * 1.2)
    
    def _calculate_timing_scoring(self, signal_data: Dict[str, Any]) -> float:
        """時機評分：adaptive_time_scoring_based_on_market_stress"""
        market_stress = signal_data.get('market_stress', 0.5)
        
        # 動態時機評估 (range: 0.6-1.0)
        base_timing = 0.8
        market_stress_adjustment = self._evaluate_market_stress_adjustment(market_stress)
        
        timing_score = base_timing + market_stress_adjustment
        return min(1.0, max(0.6, timing_score))
    
    def _detect_volatility_jump(self, signal_strength: float) -> float:
        """信號波動監控：rolling_standard_deviation_analysis"""
        self.signal_volatility_history.append(signal_strength)
        
        # 保持 15 分鐘窗口
        if len(self.signal_volatility_history) > 15:
            self.signal_volatility_history.pop(0)
        
        if len(self.signal_volatility_history) >= 3:
            std_dev = statistics.stdev(self.signal_volatility_history)
            if std_dev > self.anomaly_detection_params["volatility_jump_threshold"]:
                return 0.2  # 20% 懲罰
        
        return 0.0
    
    def _monitor_confidence_drop_rate(self, confidence: float) -> float:
        """信心下降檢測：rate_of_change_analysis"""
        self.historical_confidence_data.append(confidence)
        
        if len(self.historical_confidence_data) > 10:
            self.historical_confidence_data.pop(0)
        
        if len(self.historical_confidence_data) >= 2:
            historical_average = statistics.mean(self.historical_confidence_data[:-1])
            drop_rate = (historical_average - confidence) / historical_average if historical_average > 0 else 0
            
            if drop_rate > self.anomaly_detection_params["confidence_drop_threshold"]:
                return drop_rate * 0.5  # 按下降率比例懲罰
        
        return 0.0
    
    def _evaluate_market_stress_adjustment(self, market_stress: float) -> float:
        """市場壓力調整：dynamic_timing_evaluation"""
        if market_stress > 0.8:
            return -0.1  # 高壓力環境降低時機分數
        elif market_stress < 0.3:
            return 0.1   # 低壓力環境提升時機分數
        return 0.0
    
    def _perform_source_consensus_validation(self, sources: List[Dict[str, Any]]) -> float:
        """源共識驗證"""
        if len(sources) < 2:
            return 1.0
        
        # 計算源重疊評分：jaccard_similarity_coefficient
        source_overlap_score = self._calculate_jaccard_similarity_coefficient(sources)
        
        # 計算模型多樣性評分：entropy_based_diversity_measure
        model_diversity_score = self._calculate_entropy_based_diversity_measure(sources)
        
        # 計算行動偏差評分：directional_consensus_measure
        action_bias_score = self._calculate_directional_consensus_measure(sources)
        
        # 加權平均法衝突解決
        consensus_factor = (
            source_overlap_score * 0.4 + 
            model_diversity_score * 0.3 + 
            action_bias_score * 0.3
        )
        
        return min(1.0, max(0.5, consensus_factor))
    
    def _calculate_jaccard_similarity_coefficient(self, sources: List[Dict[str, Any]]) -> float:
        """Jaccard 相似係數計算"""
        if len(sources) < 2:
            return 1.0
        
        # 簡化實現：計算信號強度的相似性
        strengths = [s.get('signal_strength', 0.5) for s in sources]
        avg_strength = statistics.mean(strengths)
        similarity = 1.0 - statistics.stdev(strengths) if len(strengths) > 1 else 1.0
        
        return min(1.0, max(0.0, similarity))
    
    def _calculate_entropy_based_diversity_measure(self, sources: List[Dict[str, Any]]) -> float:
        """基於熵的多樣性測量"""
        if len(sources) < 2:
            return 1.0
        
        # 計算模型類型多樣性
        model_types = [s.get('model_type', 'default') for s in sources]
        unique_types = len(set(model_types))
        diversity_score = unique_types / len(model_types)
        
        return diversity_score
    
    def _calculate_directional_consensus_measure(self, sources: List[Dict[str, Any]]) -> float:
        """方向性共識測量"""
        if len(sources) < 2:
            return 1.0
        
        # 計算信號方向一致性
        directions = []
        for source in sources:
            signal_value = source.get('value', 0)
            if signal_value > 0:
                directions.append(1)
            elif signal_value < 0:
                directions.append(-1)
            else:
                directions.append(0)
        
        # 計算一致性比例
        if directions:
            most_common_direction = max(set(directions), key=directions.count)
            consensus_ratio = directions.count(most_common_direction) / len(directions)
            return consensus_ratio
        
        return 1.0
    
    def _layer_2_tier_enhancement(self, base_scores: Dict[str, float], signal_data: Dict[str, Any]) -> Dict[str, float]:
        """Layer 2: 分層增強評分 - 基於 Phase1A 分層信息的評分增強"""
        try:
            # 提取分層信息
            tier_metadata = signal_data.get('metadata', {}).get('tier_metadata', {})
            tier_config = signal_data.get('metadata', {}).get('tier_config', {})
            signal_tier = tier_metadata.get('tier', 'MEDIUM')
            
            # 如果沒有分層信息，返回原始評分
            if not tier_metadata:
                return base_scores
            
            # 獲取分層加成係數
            tier_str = signal_tier.value if hasattr(signal_tier, 'value') else str(signal_tier)
            tier_boost = self.tier_boost_factors.get(tier_str, 1.0)
            
            # 創建增強評分副本
            enhanced_scores = base_scores.copy()
            
            # 1. 基於 Lean 信心度增強信心評分
            lean_confidence = tier_metadata.get('lean_confidence', 0.0)
            if lean_confidence > 0:
                lean_boost = min(0.3, lean_confidence * 0.5)  # 最大30%加成
                enhanced_scores['confidence_score'] = min(1.0, 
                    enhanced_scores['confidence_score'] + lean_boost
                )
            
            # 2. 基於分層等級增強強度評分
            enhanced_scores['strength_score'] = min(1.0, 
                enhanced_scores['strength_score'] * tier_boost
            )
            
            # 3. 基於倉位乘數調整質量評分
            position_multiplier = tier_config.get('position_multiplier', 1.0)
            if position_multiplier > 0.5:  # 大倉位信號提高質量要求
                enhanced_scores['quality_score'] = min(1.0,
                    enhanced_scores['quality_score'] * 1.1
                )
            elif position_multiplier < 0.3:  # 小倉位信號降低質量要求
                enhanced_scores['quality_score'] = max(0.3,
                    enhanced_scores['quality_score'] * 0.9
                )
            
            # 4. 基於執行優先級調整時間評分
            execution_priority = tier_config.get('execution_priority', 3)
            if execution_priority <= 2:  # 高優先級信號
                enhanced_scores['timing_score'] = min(1.0,
                    enhanced_scores['timing_score'] * 1.15
                )
            
            # 5. 基於期望收益調整風險評分
            expected_return = tier_metadata.get('expected_return', 0.0)
            if expected_return > 0.01:  # 高期望收益
                enhanced_scores['risk_score'] = min(1.0,
                    enhanced_scores['risk_score'] * 1.1
                )
            elif expected_return < 0:  # 負期望收益
                enhanced_scores['risk_score'] = max(0.3,
                    enhanced_scores['risk_score'] * 0.8
                )
            
            # 6. 添加分層評分元數據
            enhanced_scores['tier_enhancement_applied'] = True
            enhanced_scores['tier_boost_factor'] = tier_boost
            enhanced_scores['lean_confidence_boost'] = lean_confidence
            enhanced_scores['tier_level'] = tier_str
            
            return enhanced_scores
            
        except Exception as e:
            # 分層增強失敗，返回原始評分
            base_scores['tier_enhancement_error'] = str(e)
            return base_scores
    
    def get_tier_adjusted_final_score(self, scores: Dict[str, float]) -> float:
        """計算分層調整後的最終評分"""
        try:
            # 基礎加權評分
            base_final_score = (
                scores.get('strength_score', 0.5) * self.scoring_weights['strength_scoring'] +
                scores.get('confidence_score', 0.7) * self.scoring_weights['confidence_scoring'] +
                scores.get('quality_score', 0.6) * self.scoring_weights['quality_scoring'] +
                scores.get('risk_score', 0.5) * self.scoring_weights['risk_scoring'] +
                scores.get('timing_score', 0.8) * self.scoring_weights['timing_scoring']
            )
            
            # 分層加成
            tier_boost = scores.get('tier_boost_factor', 1.0)
            final_score = min(1.0, base_final_score * tier_boost)
            
            return final_score
            
        except Exception:
            return 0.7  # 默認評分
        most_common_direction = max(set(directions), key=directions.count)
        consensus_count = directions.count(most_common_direction)
        consensus_ratio = consensus_count / len(directions)
        
        return consensus_ratio

# 全域實例 (embedded_in_epl_step3_quality_control)
signal_scoring_engine = EnhancedSignalScoringEngine()

class TierAwareScoring:
    """分層感知評分系統 - Phase2 與 Phase1A 分層系統整合"""
    
    def __init__(self):
        self.base_scoring_engine = signal_scoring_engine
        
        # 分層權重調整策略
        self.tier_weight_adjustments = {
            'CRITICAL': {
                'strength_weight_boost': 0.1,      # 強度權重提升
                'confidence_weight_boost': 0.15,   # 信心度權重大幅提升
                'quality_requirement_strict': True, # 嚴格質量要求
                'risk_tolerance_low': 0.8          # 低風險容忍度
            },
            'HIGH': {
                'strength_weight_boost': 0.05,
                'confidence_weight_boost': 0.1,
                'quality_requirement_strict': True,
                'risk_tolerance_low': 0.9
            },
            'MEDIUM': {
                'strength_weight_boost': 0.0,
                'confidence_weight_boost': 0.0,
                'quality_requirement_strict': False,
                'risk_tolerance_low': 1.0
            },
            'LOW': {
                'strength_weight_boost': -0.05,    # 探索性信號，降低強度要求
                'confidence_weight_boost': -0.1,
                'quality_requirement_strict': False,
                'risk_tolerance_low': 1.2          # 允許更高風險
            }
        }
    
    def calculate_tier_score(self, signal_data: Dict[str, Any], lean_params: Dict[str, Any]) -> Dict[str, float]:
        """計算分層感知評分 - 結合 Lean 信心度和技術指標"""
        
        # 提取 Lean 參數
        lean_confidence = lean_params.get('confidence_level', 0.5)
        lean_direction = lean_params.get('consensus_direction', 'NEUTRAL')
        lean_expected_return = lean_params.get('expected_return', 0.0)
        signal_tier = lean_params.get('signal_tier', 'MEDIUM')
        
        # 基礎技術評分
        base_scores = self.base_scoring_engine.score_signal(signal_data)
        
        # 分層權重調整
        tier_adjustments = self.tier_weight_adjustments.get(signal_tier, self.tier_weight_adjustments['MEDIUM'])
        
        # 調整後的評分權重
        adjusted_weights = self.base_scoring_engine.scoring_weights.copy()
        adjusted_weights['strength_scoring'] += tier_adjustments['strength_weight_boost']
        adjusted_weights['confidence_scoring'] += tier_adjustments['confidence_weight_boost']
        
        # 正規化權重
        total_weight = sum(adjusted_weights.values())
        for key in adjusted_weights:
            adjusted_weights[key] /= total_weight
        
        # Lean 信心度融合到信心度評分
        lean_boost = lean_confidence * 0.3  # Lean 貢獻最多 30%
        enhanced_confidence_score = min(1.0, base_scores.get('confidence_score', 0.7) + lean_boost)
        
        # 期望收益融合到強度評分
        return_boost = abs(lean_expected_return) * 5.0  # 期望收益轉換為強度加成
        enhanced_strength_score = min(1.0, base_scores.get('strength_score', 0.5) + return_boost)
        
        # 分層質量要求
        quality_score = base_scores.get('quality_score', 0.6)
        if tier_adjustments['quality_requirement_strict'] and quality_score < 0.7:
            quality_score *= 0.8  # 嚴格模式下，低質量信號懲罰
        
        # 風險容忍度調整
        risk_score = base_scores.get('risk_score', 0.5)
        risk_adjustment = tier_adjustments['risk_tolerance_low']
        adjusted_risk_score = min(1.0, risk_score * risk_adjustment)
        
        # 計算最終分層評分
        tier_aware_scores = {
            'base_strength_score': base_scores.get('strength_score', 0.5),
            'enhanced_strength_score': enhanced_strength_score,
            'base_confidence_score': base_scores.get('confidence_score', 0.7),
            'enhanced_confidence_score': enhanced_confidence_score,
            'quality_score': quality_score,
            'adjusted_risk_score': adjusted_risk_score,
            'timing_score': base_scores.get('timing_score', 0.8),
            'lean_confidence_boost': lean_boost,
            'lean_return_boost': return_boost,
            'signal_tier': signal_tier,
            'tier_weight_adjustments': tier_adjustments
        }
        
        # 最終加權評分
        final_tier_score = (
            enhanced_strength_score * adjusted_weights['strength_scoring'] +
            enhanced_confidence_score * adjusted_weights['confidence_scoring'] +
            quality_score * adjusted_weights['quality_scoring'] +
            adjusted_risk_score * adjusted_weights['risk_scoring'] +
            tier_aware_scores['timing_score'] * adjusted_weights['timing_scoring']
        )
        
        tier_aware_scores['final_tier_score'] = final_tier_score
        tier_aware_scores['score_improvement'] = final_tier_score - base_scores.get('final_score', 0.7)
        
        return tier_aware_scores
    
    def compare_tier_performance(self, signals_with_tiers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """比較不同分層的性能表現"""
        tier_performance = {
            'CRITICAL': {'count': 0, 'avg_score': 0.0, 'scores': []},
            'HIGH': {'count': 0, 'avg_score': 0.0, 'scores': []},
            'MEDIUM': {'count': 0, 'avg_score': 0.0, 'scores': []},
            'LOW': {'count': 0, 'avg_score': 0.0, 'scores': []}
        }
        
        for signal in signals_with_tiers:
            tier = signal.get('signal_tier', 'MEDIUM')
            score = signal.get('final_tier_score', 0.0)
            
            if tier in tier_performance:
                tier_performance[tier]['count'] += 1
                tier_performance[tier]['scores'].append(score)
        
        # 計算統計數據
        for tier in tier_performance:
            scores = tier_performance[tier]['scores']
            if scores:
                tier_performance[tier]['avg_score'] = sum(scores) / len(scores)
                tier_performance[tier]['min_score'] = min(scores)
                tier_performance[tier]['max_score'] = max(scores)
                tier_performance[tier]['score_std'] = (sum((x - tier_performance[tier]['avg_score'])**2 for x in scores) / len(scores))**0.5
        
        return tier_performance
    
    def get_tier_recommendation(self, tier_score_result: Dict[str, float]) -> Dict[str, Any]:
        """基於分層評分結果提供建議"""
        final_score = tier_score_result.get('final_tier_score', 0.0)
        signal_tier = tier_score_result.get('signal_tier', 'MEDIUM')
        score_improvement = tier_score_result.get('score_improvement', 0.0)
        
        recommendation = {
            'execution_recommendation': 'HOLD',
            'confidence_level': 'MEDIUM',
            'suggested_position_size': 0.5,
            'reasoning': []
        }
        
        # 基於分層和評分的執行建議
        if signal_tier == 'CRITICAL' and final_score > 0.8:
            recommendation['execution_recommendation'] = 'STRONG_BUY'
            recommendation['confidence_level'] = 'HIGH'
            recommendation['suggested_position_size'] = 0.8
            recommendation['reasoning'].append('CRITICAL層級信號，高評分，強烈建議執行')
            
        elif signal_tier == 'HIGH' and final_score > 0.75:
            recommendation['execution_recommendation'] = 'BUY'
            recommendation['confidence_level'] = 'HIGH'
            recommendation['suggested_position_size'] = 0.6
            recommendation['reasoning'].append('HIGH層級信號，良好評分，建議執行')
            
        elif signal_tier == 'MEDIUM' and final_score > 0.7:
            recommendation['execution_recommendation'] = 'BUY'
            recommendation['confidence_level'] = 'MEDIUM'
            recommendation['suggested_position_size'] = 0.4
            recommendation['reasoning'].append('MEDIUM層級信號，達標評分，可以執行')
            
        elif signal_tier == 'LOW' and final_score > 0.6:
            recommendation['execution_recommendation'] = 'SMALL_BUY'
            recommendation['confidence_level'] = 'LOW'
            recommendation['suggested_position_size'] = 0.2
            recommendation['reasoning'].append('LOW層級信號，探索性執行')
            
        else:
            recommendation['reasoning'].append(f'{signal_tier}層級信號評分不足({final_score:.2f})，建議持有')
        
        # 改進建議
        if score_improvement > 0.1:
            recommendation['reasoning'].append(f'分層優化帶來{score_improvement:.2f}分改進')
        elif score_improvement < -0.05:
            recommendation['reasoning'].append(f'分層調整降低{abs(score_improvement):.2f}分，需檢查參數')
        
        return recommendation

# 全域分層感知評分實例
tier_aware_scoring_engine = TierAwareScoring()
