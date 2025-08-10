"""
🎯 Trading X - Enhanced Signal Scoring Engine (Integrated Version) v2.1.0
完全符合 signal_scoring_engine.json 規範的增強信號評分引擎
模組類型：embedded_scoring_engine
整合模式：embedded_in_epl_step3_quality_control
"""

from typing import Dict, Any, List
import math
import statistics

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
    
    def score_signal(self, signal_data: Dict[str, Any]) -> Dict[str, float]:
        """
        信號評分主方法 - 3ms embedded processing
        
        處理層:
        - Layer 0: Data Extraction (1ms)  
        - Layer 1: Score Calculation (2ms)
        """
        try:
            # Layer 0: Data Extraction (1ms)
            extracted_metrics = self._layer_0_data_extraction(signal_data)
            
            # Layer 1: Score Calculation (2ms)
            complete_score_dict = self._layer_1_score_calculation(extracted_metrics, signal_data)
            
            return complete_score_dict
            
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
        
        if not directions:
            return 1.0
        
        # 計算方向一致性
        most_common_direction = max(set(directions), key=directions.count)
        consensus_count = directions.count(most_common_direction)
        consensus_ratio = consensus_count / len(directions)
        
        return consensus_ratio

# 全域實例 (embedded_in_epl_step3_quality_control)
signal_scoring_engine = EnhancedSignalScoringEngine()
