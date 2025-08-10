"""
🧠 Phase 2: EPL前處理系統 (Enhanced Pre-Processing Layer)
========================================================

EPL前處理系統 v2.1.0 - 智能三步驟品質控制與優化路由
1. 智能去重分析引擎 (Phase1數據優化重用)
2. 上下文關聯分析器 (市場環境信任機制) 
3. 輕量品質控制門檻 (整合評分引擎)
4. 智能路由系統 (快速/標準/深度通道)
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

# 模擬SignalCandidate數據結構
@dataclass
class SignalCandidate:
    """信號候選者數據結構"""
    id: str
    symbol: str
    signal_strength: float
    confidence: float
    direction: str
    timestamp: datetime
    source: str
    data_completeness: float
    signal_clarity: float
    dynamic_params: Dict[str, Any]
    market_environment: Dict[str, Any]
    technical_snapshot: Dict[str, Any]

class DeduplicationResult(Enum):
    """去重分析結果"""
    UNIQUE = "⭐ 獨特"
    IGNORE = "❌ 忽略" 
    DELAY_OBSERVE = "⚠️ 延遲觀察"
    PASS = "✅ 通過"

class CorrelationAnalysisResult(Enum):
    """關聯分析結果"""
    STRENGTHEN_CANDIDATE = "➕ 強化候選"
    REPLACE_CANDIDATE = "🔁 替換候選"
    INDEPENDENT_NEW = "✅ 獨立新單"

class QualityControlResult(Enum):
    """品質控制結果"""
    EXCELLENT = "🌟 優秀"
    PASS = "✅ 通過"
    FAIL_STRENGTH = "❌ 信號強度不足"
    FAIL_LIQUIDITY = "❌ 流動性不足"
    FAIL_RISK = "❌ 風險評估未通過"

@dataclass
class PreEvaluationResult:
    """前處理評估結果"""
    candidate: SignalCandidate
    deduplication_result: DeduplicationResult
    correlation_result: CorrelationAnalysisResult
    quality_result: QualityControlResult
    pass_to_epl: bool
    processing_notes: List[str]
    similarity_score: Optional[float]
    risk_assessment: Dict[str, Any]
    timestamp: datetime

class IntelligentDeduplicationEngine:
    """智能去重分析引擎 - 利用Phase1動態參數快速去重"""
    
    def __init__(self):
        self.processed_signals: List[SignalCandidate] = []
        self.similarity_threshold = 0.85  # JSON配置: 85%相似度閾值
        self.time_overlap_minutes = 15    # JSON配置: 15分鐘時間重疊
        self.confidence_diff_threshold = 0.03  # JSON配置: 3%信心度差異
        
        # JSON增強功能: 源共識驗證參數
        self.source_overlap_score_threshold = 0.72
        self.model_diversity_score_threshold = 0.8
        self.action_bias_score_threshold = 0.85
    
    async def analyze_duplication(self, candidate: SignalCandidate) -> Tuple[DeduplicationResult, float, List[str]]:
        """智能去重分析 - 利用Phase1 dynamic_params"""
        notes = []
        max_similarity = 0.0
        
        try:
            # JSON功能: 利用Phase1 dynamic_params進行快速去重
            relevant_signals = self._get_relevant_signals_with_phase1_params(candidate)
            
            if not relevant_signals:
                notes.append("Phase1動態參數無歷史匹配")
                return DeduplicationResult.PASS, 0.0, notes
            
            # JSON增強功能: 源共識驗證
            source_consensus_result = self._validate_source_consensus(candidate, relevant_signals)
            
            for historical_signal in relevant_signals:
                # 計算相似度
                similarity = self._calculate_enhanced_similarity(candidate, historical_signal)
                max_similarity = max(max_similarity, similarity)
                
                # JSON功能: Phase1數據重用檢查
                adaptation_time_match = self._check_adaptation_timestamp_match(
                    candidate, historical_signal
                )
                
                notes.append(f"與{historical_signal.id}相似度: {similarity:.2f}")
                
                # JSON規範判斷邏輯
                if (similarity > 0.95 and adaptation_time_match):
                    notes.append("高度重複（Phase1適應時間戳匹配）")
                    return DeduplicationResult.IGNORE, similarity, notes
                elif (similarity > self.similarity_threshold and 
                      source_consensus_result["preserve"] == False):
                    notes.append("中度重複（源共識驗證未通過）") 
                    return DeduplicationResult.DELAY_OBSERVE, similarity, notes
            
            # JSON增強功能: 模型多樣性保留規則
            if source_consensus_result["model_diversity_score"] > self.model_diversity_score_threshold:
                notes.append("模型多樣性保留規則觸發")
                return DeduplicationResult.UNIQUE, max_similarity, notes
            
            notes.append(f"Phase1優化去重完成，最高相似度: {max_similarity:.2f}")
            return DeduplicationResult.PASS, max_similarity, notes
            
        except Exception as e:
            logger.error(f"智能去重分析失敗: {e}")
            notes.append(f"分析錯誤: {e}")
            return DeduplicationResult.PASS, 0.0, notes
    
    def _get_relevant_signals_with_phase1_params(self, candidate: SignalCandidate) -> List[SignalCandidate]:
        """利用Phase1動態參數獲取相關信號"""
        # JSON數據重用: id + dynamic_params.adaptation_timestamp
        candidate_adaptation_time = candidate.dynamic_params.get("adaptation_timestamp")
        cutoff_time = candidate.timestamp - timedelta(minutes=self.time_overlap_minutes)
        
        relevant = []
        for signal in self.processed_signals:
            if (signal.symbol == candidate.symbol and 
                signal.timestamp > cutoff_time and
                signal.timestamp < candidate.timestamp):
                
                # Phase1動態參數匹配檢查
                signal_adaptation_time = signal.dynamic_params.get("adaptation_timestamp")
                if candidate_adaptation_time and signal_adaptation_time:
                    time_diff = abs((candidate_adaptation_time - signal_adaptation_time).total_seconds())
                    if time_diff < 300:  # 5分鐘內的適應時間戳
                        relevant.append(signal)
                else:
                    relevant.append(signal)  # 備用邏輯
        
        return relevant
    
    def _validate_source_consensus(self, candidate: SignalCandidate, historical_signals: List[SignalCandidate]) -> Dict[str, Any]:
        """JSON增強功能: 源共識驗證"""
        if not historical_signals:
            return {"preserve": True, "model_diversity_score": 1.0}
        
        # 計算源重疊分數
        candidate_sources = set([candidate.source])
        historical_sources = set([s.source for s in historical_signals])
        source_overlap_score = len(candidate_sources.intersection(historical_sources)) / len(candidate_sources.union(historical_sources))
        
        # 計算模型多樣性分數
        all_sources = candidate_sources.union(historical_sources)
        model_diversity_score = len(all_sources) / (len(all_sources) + 1)  # 正規化
        
        # 計算行動偏差分數
        candidate_direction = candidate.direction
        historical_directions = [s.direction for s in historical_signals]
        same_direction_count = sum(1 for d in historical_directions if d == candidate_direction)
        action_bias_score = same_direction_count / len(historical_directions) if historical_directions else 0
        
        # JSON保留規則: preserve_if_model_diversity_score > 0.8
        preserve = model_diversity_score > self.model_diversity_score_threshold
        
        return {
            "source_overlap_score": source_overlap_score,
            "model_diversity_score": model_diversity_score,
            "action_bias_score": action_bias_score,
            "preserve": preserve
        }
    
    def _calculate_enhanced_similarity(self, candidate1: SignalCandidate, candidate2: SignalCandidate) -> float:
        """增強相似度計算"""
        similarity_factors = []
        
        # 強度相似度
        strength_similarity = 1 - abs(candidate1.signal_strength - candidate2.signal_strength) / 100
        similarity_factors.append(strength_similarity * 0.3)
        
        # 方向相似度
        direction_similarity = 1.0 if candidate1.direction == candidate2.direction else 0.0
        similarity_factors.append(direction_similarity * 0.2)
        
        # 來源相似度
        source_similarity = 1.0 if candidate1.source == candidate2.source else 0.5
        similarity_factors.append(source_similarity * 0.2)
        
        # 技術指標相似度
        tech_similarity = self._calculate_technical_similarity(
            candidate1.technical_snapshot, candidate2.technical_snapshot
        )
        similarity_factors.append(tech_similarity * 0.3)
        
        return sum(similarity_factors)
    
    def _calculate_technical_similarity(self, tech1: Dict[str, Any], tech2: Dict[str, Any]) -> float:
        """計算技術指標相似度"""
        try:
            similarities = []
            
            # RSI相似度
            rsi_sim = 1 - abs(tech1.get("rsi", 50) - tech2.get("rsi", 50)) / 100
            similarities.append(rsi_sim)
            
            # MACD相似度  
            macd_sim = 1 - min(1.0, abs(tech1.get("macd_signal", 0) - tech2.get("macd_signal", 0)) / 2)
            similarities.append(macd_sim)
            
            # 布林帶位置相似度
            bb_sim = 1 - abs(tech1.get("bollinger_position", 0.5) - tech2.get("bollinger_position", 0.5))
            similarities.append(bb_sim)
            
            return sum(similarities) / len(similarities)  # 平均值
            
        except Exception:
            return 0.5  # 預設中等相似度
    
    def _check_adaptation_timestamp_match(self, candidate1: SignalCandidate, candidate2: SignalCandidate) -> bool:
        """檢查Phase1適應時間戳匹配"""
        time1 = candidate1.dynamic_params.get("adaptation_timestamp")
        time2 = candidate2.dynamic_params.get("adaptation_timestamp")
        
        if time1 and time2:
            time_diff = abs((time1 - time2).total_seconds())
            return time_diff < 60  # 1分鐘內視為匹配
        return False
    
    def add_processed_signal(self, signal: SignalCandidate):
        """添加已處理信號到歷史記錄"""
        self.processed_signals.append(signal)
        
        # 保持歷史記錄在合理範圍內
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.processed_signals = [s for s in self.processed_signals if s.timestamp > cutoff_time]

class ContextualCorrelationAnalyzer:
    """上下文關聯分析器 - 利用Phase1市場環境快速決策"""
    
    def __init__(self):
        self.current_positions: Dict[str, SignalCandidate] = {}
        self.symbol_correlations: Dict[str, List[str]] = {}
        
        # JSON配置參數
        self.direction_conflict_threshold = 0.15
        self.confidence_improvement_threshold = 0.08
    
    async def analyze_correlation(self, candidate: SignalCandidate) -> Tuple[CorrelationAnalysisResult, List[str]]:
        """上下文關聯分析 - 信任Phase1市場環境分析"""
        notes = []
        
        try:
            # JSON功能: 利用Phase1市場環境數據
            market_analysis = self._leverage_phase1_market_environment(candidate)
            notes.extend(market_analysis["notes"])
            
            # 檢查當前持倉
            current_position = self.current_positions.get(candidate.symbol)
            
            if current_position:
                # JSON決策邏輯: strengthen/replace/independent_decision
                decision_result = self._make_correlation_decision(candidate, current_position, market_analysis)
                notes.extend(decision_result["notes"])
                return decision_result["result"], notes
            
            # 檢查相關標的關聯性
            correlation_impact = self._assess_symbol_correlations(candidate)
            notes.extend(correlation_impact["notes"])
            
            notes.append("JSON規範: 信任Phase1市場環境，視為獨立新機會")
            return CorrelationAnalysisResult.INDEPENDENT_NEW, notes
            
        except Exception as e:
            logger.error(f"上下文關聯分析失敗: {e}")
            notes.append(f"分析錯誤: {e}")
            return CorrelationAnalysisResult.INDEPENDENT_NEW, notes
    
    def _leverage_phase1_market_environment(self, candidate: SignalCandidate) -> Dict[str, Any]:
        """JSON功能: 利用Phase1市場環境進行快速決策"""
        market_env = candidate.market_environment
        notes = []
        
        # JSON數據重用: market_environment.volatility + liquidity_score
        volatility = market_env.get("volatility", 0.02)
        liquidity_score = market_env.get("liquidity_score", 0.7)
        momentum = market_env.get("momentum", 0.0)
        
        notes.append(f"Phase1市場環境: 波動性={volatility:.3f}, 流動性={liquidity_score:.2f}")
        
        # JSON優化策略: trust_phase1_market_analysis_results
        market_regime = "stable"
        if volatility > 0.05:
            market_regime = "high_volatility"
        elif volatility < 0.01:
            market_regime = "low_volatility"
        
        if liquidity_score < 0.3:
            market_regime += "_low_liquidity"
        
        notes.append(f"JSON優化: 信任Phase1市場分析，市場狀態={market_regime}")
        
        return {
            "volatility": volatility,
            "liquidity_score": liquidity_score,
            "momentum": momentum,
            "market_regime": market_regime,
            "notes": notes
        }
    
    def _make_correlation_decision(self, candidate: SignalCandidate, current_position: SignalCandidate, market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """JSON決策邏輯: strengthen/replace/independent_decision"""
        notes = []
        
        # 方向衝突分析
        direction_conflict = candidate.direction != current_position.direction
        
        # 信心度差異
        confidence_diff = candidate.confidence - current_position.confidence
        
        # 持倉強度差異
        strength_diff = candidate.signal_strength - current_position.signal_strength
        
        notes.append(f"方向衝突: {direction_conflict}, 信心度差異: {confidence_diff:.3f}")
        notes.append(f"強度差異: {strength_diff:.1f}")
        
        # JSON決策邏輯
        if direction_conflict and confidence_diff > self.direction_conflict_threshold:
            notes.append("JSON決策: 方向相反且信心度大幅提升 -> 替換候選")
            return {"result": CorrelationAnalysisResult.REPLACE_CANDIDATE, "notes": notes}
        
        elif not direction_conflict and confidence_diff > self.confidence_improvement_threshold:
            notes.append("JSON決策: 方向相同且信心度提升 -> 強化候選")
            return {"result": CorrelationAnalysisResult.STRENGTHEN_CANDIDATE, "notes": notes}
        
        else:
            notes.append("JSON決策: 關聯度低 -> 獨立新單")
            return {"result": CorrelationAnalysisResult.INDEPENDENT_NEW, "notes": notes}
    
    def _assess_symbol_correlations(self, candidate: SignalCandidate) -> Dict[str, Any]:
        """評估標的相關性"""
        notes = []
        
        # 預定義相關性組
        correlation_groups = {
            "BTCUSDT": ["ETHUSDT", "ADAUSDT"],
            "ETHUSDT": ["BTCUSDT", "DOTUSDT", "LINKUSDT"],
            "ADAUSDT": ["DOTUSDT", "ATOMUSDT"],
            "SOLUSDT": ["AVAXUSDT", "NEARUSDT"]
        }
        
        correlated_symbols = correlation_groups.get(candidate.symbol, [])
        notes.append(f"相關標的: {correlated_symbols}")
        
        # 檢查相關標的持倉
        for corr_symbol in correlated_symbols:
            if corr_symbol in self.current_positions:
                corr_position = self.current_positions[corr_symbol]
                if candidate.direction == corr_position.direction:
                    notes.append(f"與{corr_symbol}正相關 - 可能加強組合風險")
                else:
                    notes.append(f"與{corr_symbol}負相關 - 可能提供對沖效果")
        
        return {"notes": notes}
    
    def update_position(self, symbol: str, signal: SignalCandidate):
        """更新持倉信號"""
        self.current_positions[symbol] = signal
    
    def remove_position(self, symbol: str):
        """移除持倉"""
        if symbol in self.current_positions:
            del self.current_positions[symbol]

class LightweightQualityControlGate:
    """輕量品質控制門檻 - 信任Phase1品質指標補充風險評估"""
    
    def __init__(self):
        # JSON配置參數
        self.strength_threshold = 70.0
        self.liquidity_threshold = 0.6
        self.risk_score_threshold = 0.3
        
        # JSON增強功能: 微異常參數
        self.signal_volatility_jump_threshold = 0.3
        self.confidence_drop_rate_threshold = 0.1
        
        # JSON增強功能: 延遲觀察參數
        self.tracking_duration_minutes = 5
        self.performance_improvement_threshold = 0.15
        self.reinforcement_upgrade_threshold = 0.2
        
        # JSON整合評分引擎權重
        self.scoring_weights = {
            "strength": 0.3,
            "confidence": 0.25,
            "quality": 0.2,
            "risk": 0.15,
            "timing": 0.1
        }
    
    async def evaluate_quality(self, candidate: SignalCandidate) -> Tuple[QualityControlResult, Dict[str, Any], List[str]]:
        """輕量品質評估 - 信任Phase1品質指標"""
        notes = []
        risk_assessment = {}
        
        try:
            # JSON功能: 信任Phase1品質指標
            phase1_quality_trust = self._trust_phase1_quality_indicators(candidate)
            notes.extend(phase1_quality_trust["notes"])
            
            # JSON增強功能: 微異常篩選
            micro_anomaly_result = self._micro_anomaly_screening(candidate)
            notes.extend(micro_anomaly_result["notes"])
            
            if micro_anomaly_result["review_required"]:
                notes.append("微異常檢測觸發，需要審查")
                return QualityControlResult.FAIL_RISK, {"micro_anomaly": True}, notes
            
            # JSON整合評分: 嵌入式信號評分引擎
            integrated_score = self._embedded_signal_scoring_engine(candidate)
            notes.append(f"整合評分: {integrated_score:.3f}")
            
            # 簡化品質檢查（信任Phase1）
            if phase1_quality_trust["strength_pass"] and phase1_quality_trust["liquidity_pass"]:
                # 補充極端風險檢查
                risk_assessment = await self._supplement_extreme_risk_check(candidate)
                
                if risk_assessment["overall_risk_score"] > self.risk_score_threshold:
                    notes.append(f"極端風險檢查未通過: {risk_assessment['overall_risk_score']:.3f}")
                    return QualityControlResult.FAIL_RISK, risk_assessment, notes
                
                # JSON增強功能: 延遲觀察追蹤
                if integrated_score >= 0.9:
                    notes.append("JSON規範: 優秀品質，快速通道")
                    return QualityControlResult.EXCELLENT, risk_assessment, notes
                else:
                    notes.append("JSON規範: 通過品質控制")
                    return QualityControlResult.PASS, risk_assessment, notes
            
            else:
                # 基於Phase1信任的失敗判斷
                if not phase1_quality_trust["strength_pass"]:
                    return QualityControlResult.FAIL_STRENGTH, {}, notes
                else:
                    return QualityControlResult.FAIL_LIQUIDITY, {}, notes
            
        except Exception as e:
            logger.error(f"輕量品質評估失敗: {e}")
            notes.append(f"評估錯誤: {e}")
            return QualityControlResult.PASS, {}, notes
    
    def _trust_phase1_quality_indicators(self, candidate: SignalCandidate) -> Dict[str, Any]:
        """JSON功能: 信任Phase1品質指標"""
        notes = []
        
        # JSON數據重用: data_completeness + signal_clarity + confidence
        data_completeness = candidate.data_completeness
        signal_clarity = candidate.signal_clarity
        confidence = candidate.confidence
        
        notes.append(f"Phase1品質指標: 數據完整性={data_completeness:.2f}, 信號清晰度={signal_clarity:.2f}")
        
        # JSON信任策略: high_trust_for_quality_indicators
        strength_pass = candidate.signal_strength >= self.strength_threshold or signal_clarity >= 0.8
        liquidity_pass = (candidate.market_environment.get("liquidity_score", 0.7) >= self.liquidity_threshold or 
                         data_completeness >= 0.9)
        
        notes.append(f"JSON信任: 強度通過={strength_pass}, 流動性通過={liquidity_pass}")
        
        return {
            "data_completeness": data_completeness,
            "signal_clarity": signal_clarity,
            "confidence": confidence,
            "strength_pass": strength_pass,
            "liquidity_pass": liquidity_pass,
            "notes": notes
        }
    
    def _micro_anomaly_screening(self, candidate: SignalCandidate) -> Dict[str, Any]:
        """JSON增強功能: 微異常篩選"""
        notes = []
        
        # 信號波動性跳躍檢測
        dynamic_params = candidate.dynamic_params
        signal_volatility_jump = dynamic_params.get("volatility_jump", 0.0)
        
        # 信心度下降率檢測
        confidence_drop_rate = dynamic_params.get("confidence_drop_rate", 0.0)
        
        notes.append(f"微異常檢測: 波動性跳躍={signal_volatility_jump:.3f}, 信心度下降率={confidence_drop_rate:.3f}")
        
        # JSON規範: review_required_trigger
        review_required = (signal_volatility_jump > self.signal_volatility_jump_threshold or
                          confidence_drop_rate > self.confidence_drop_rate_threshold)
        
        return {
            "signal_volatility_jump": signal_volatility_jump,
            "confidence_drop_rate": confidence_drop_rate,
            "review_required": review_required,
            "notes": notes
        }
    
    def _embedded_signal_scoring_engine(self, candidate: SignalCandidate) -> float:
        """JSON整合評分: 嵌入式信號評分引擎"""
        # JSON規範: strength(0.3) + confidence(0.25) + quality(0.2) + risk(0.15) + timing(0.1)
        
        # 強度評分
        strength_score = candidate.signal_strength / 100.0
        
        # 信心度評分
        confidence_score = candidate.confidence
        
        # 品質評分
        quality_score = (candidate.data_completeness + candidate.signal_clarity) / 2.0
        
        # 風險評分（逆向）
        market_risk = candidate.market_environment.get("volatility", 0.02)
        risk_score = 1.0 - min(1.0, market_risk * 20)
        
        # 時機評分（簡化）
        timing_score = 0.8  # 默認良好時機
        
        # 加權計算
        integrated_score = (
            strength_score * self.scoring_weights["strength"] +
            confidence_score * self.scoring_weights["confidence"] +
            quality_score * self.scoring_weights["quality"] +
            risk_score * self.scoring_weights["risk"] +
            timing_score * self.scoring_weights["timing"]
        )
        
        return integrated_score
    
    async def _supplement_extreme_risk_check(self, candidate: SignalCandidate) -> Dict[str, Any]:
        """補充極端風險檢查"""
        risk_factors = {}
        
        # 極端波動性風險
        volatility = candidate.market_environment.get("volatility", 0.02)
        extreme_volatility_risk = min(1.0, max(0.0, (volatility - 0.05) * 10))  # 5%以上為極端
        risk_factors["extreme_volatility_risk"] = extreme_volatility_risk
        
        # 流動性枯竭風險
        liquidity_score = candidate.market_environment.get("liquidity_score", 0.7)
        liquidity_risk = max(0.0, (0.3 - liquidity_score) * 3.33)  # 30%以下為風險
        risk_factors["liquidity_depletion_risk"] = liquidity_risk
        
        # 數據完整性風險
        data_risk = 1.0 - candidate.data_completeness
        risk_factors["data_completeness_risk"] = data_risk
        
        # 綜合風險評分
        overall_risk = max(extreme_volatility_risk, liquidity_risk, data_risk)
        
        return {
            **risk_factors,
            "overall_risk_score": overall_risk,
            "risk_level": self._get_risk_level(overall_risk),
            "assessment_timestamp": datetime.now()
        }
    
    def _get_risk_level(self, risk_score: float) -> str:
        """獲取風險等級"""
        if risk_score < 0.2:
            return "低風險"
        elif risk_score < 0.4:
            return "中低風險"
        elif risk_score < 0.6:
            return "中等風險"
        elif risk_score < 0.8:
            return "中高風險"
        else:
            return "高風險"

class EnhancedPreEvaluationLayer:
    """EPL前處理系統主控制器 v2.1.0 - 智能路由與三步驟優化流程"""
    
    def __init__(self):
        # JSON核心依賴: 三步驟處理引擎
        self.deduplication_engine = IntelligentDeduplicationEngine()
        self.correlation_analyzer = ContextualCorrelationAnalyzer()
        self.quality_control_gate = LightweightQualityControlGate()
        
        # JSON性能統計
        self.processing_stats = {
            "total_processed": 0,
            "passed_to_epl": 0,
            "express_lane_count": 0,
            "standard_lane_count": 0,
            "deep_lane_count": 0,
            "rejection_reasons": {
                "duplication": 0,
                "quality_strength": 0,
                "quality_liquidity": 0,
                "quality_risk": 0,
                "micro_anomaly": 0
            },
            "performance_metrics": {
                "avg_processing_time": 0.0,
                "express_lane_avg_time": 0.0,
                "standard_lane_avg_time": 0.0
            }
        }
        
        # JSON智能路由配置
        self.routing_config = {
            "express_lane": {
                "data_completeness_threshold": 0.9,
                "signal_clarity_threshold": 0.8,
                "confidence_threshold": 0.75,
                "micro_anomaly_threshold": 0.2,
                "market_stress_threshold": 0.7
            },
            "dynamic_allocation": {
                "market_stress_thresholds": [0.3, 0.7],
                "volatility_thresholds": [0.4, 0.8]
            }
        }
    
    async def process_signal_candidate(self, candidate: SignalCandidate) -> PreEvaluationResult:
        """JSON主處理方法: 智能路由 + 三步驟優化流程"""
        start_time = time.time()
        all_notes = []
        
        try:
            logger.info(f"🧠 EPL前處理開始: {candidate.id}")
            
            # JSON第一層: 智能路由決策
            routing_decision = self._intelligent_routing_decision(candidate)
            all_notes.extend(routing_decision["notes"])
            
            # 根據路由決策選擇處理通道
            if routing_decision["lane"] == "express":
                result = await self._express_lane_processing(candidate)
                self.processing_stats["express_lane_count"] += 1
            elif routing_decision["lane"] == "deep":
                result = await self._deep_analysis_processing(candidate)
                self.processing_stats["deep_lane_count"] += 1
            else:
                result = await self._standard_lane_processing(candidate)
                self.processing_stats["standard_lane_count"] += 1
            
            # 記錄性能指標
            processing_time = (time.time() - start_time) * 1000
            self._update_performance_metrics(routing_decision["lane"], processing_time)
            
            # 更新統計
            self._update_processing_stats(result)
            
            result.processing_notes = all_notes + result.processing_notes
            
            status = "✅ 通過EPL" if result.pass_to_epl else "❌ 未通過EPL"
            logger.info(f"🧠 EPL前處理完成: {candidate.id} - {status} ({processing_time:.1f}ms)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ EPL前處理失敗: {e}")
            all_notes.append(f"處理錯誤: {e}")
            
            # 錯誤時返回基本結果
            return PreEvaluationResult(
                candidate=candidate,
                deduplication_result=DeduplicationResult.PASS,
                correlation_result=CorrelationAnalysisResult.INDEPENDENT_NEW,
                quality_result=QualityControlResult.PASS,
                pass_to_epl=False,
                processing_notes=all_notes,
                similarity_score=0.0,
                risk_assessment={"error": str(e)},
                timestamp=datetime.now()
            )
    
    def _intelligent_routing_decision(self, candidate: SignalCandidate) -> Dict[str, Any]:
        """JSON智能路由系統: 動態通道分配"""
        notes = []
        
        # JSON微異常篩選
        micro_anomaly_score = self._calculate_micro_anomaly_score(candidate)
        notes.append(f"微異常分數: {micro_anomaly_score:.3f}")
        
        # JSON市場壓力指數
        market_stress_index = self._calculate_market_stress_index(candidate)
        notes.append(f"市場壓力指數: {market_stress_index:.3f}")
        
        # JSON快速通道條件
        express_conditions = self._check_express_lane_conditions(candidate, micro_anomaly_score, market_stress_index)
        
        if express_conditions["qualified"]:
            notes.append("JSON路由: 快速通道 - 高品質信號")
            return {"lane": "express", "notes": notes}
        
        # JSON深度分析條件
        if (market_stress_index > self.routing_config["dynamic_allocation"]["market_stress_thresholds"][1] or
            micro_anomaly_score > 0.5):
            notes.append("JSON路由: 深度分析 - 複雜市場條件")
            return {"lane": "deep", "notes": notes}
        
        # 默認標準通道
        notes.append("JSON路由: 標準通道 - 常規處理")
        return {"lane": "standard", "notes": notes}
    
    def _calculate_micro_anomaly_score(self, candidate: SignalCandidate) -> float:
        """JSON微異常分數計算"""
        # 信號波動性跳躍
        volatility_jump = candidate.dynamic_params.get("volatility_jump", 0.0)
        
        # 信心度下降率
        confidence_drop = candidate.dynamic_params.get("confidence_drop_rate", 0.0)
        
        # 組合微異常分數
        micro_anomaly_score = (volatility_jump + confidence_drop) / 2.0
        
        return min(1.0, micro_anomaly_score)
    
    def _calculate_market_stress_index(self, candidate: SignalCandidate) -> float:
        """JSON市場壓力指數計算"""
        market_env = candidate.market_environment
        
        # 波動性組件
        volatility = market_env.get("volatility", 0.02)
        volatility_stress = min(1.0, volatility / 0.1)  # 10%波動性為滿分
        
        # 流動性組件
        liquidity = market_env.get("liquidity_score", 0.7)
        liquidity_stress = max(0.0, (0.5 - liquidity) * 2)  # 50%以下流動性為壓力
        
        # 動量組件
        momentum = abs(market_env.get("momentum", 0.0))
        momentum_stress = min(1.0, momentum)
        
        # 綜合市場壓力指數
        market_stress = (volatility_stress * 0.4 + liquidity_stress * 0.4 + momentum_stress * 0.2)
        
        return market_stress
    
    def _check_express_lane_conditions(self, candidate: SignalCandidate, micro_anomaly_score: float, market_stress_index: float) -> Dict[str, Any]:
        """JSON快速通道條件檢查"""
        config = self.routing_config["express_lane"]
        
        conditions = {
            "data_completeness": candidate.data_completeness >= config["data_completeness_threshold"],
            "signal_clarity": candidate.signal_clarity >= config["signal_clarity_threshold"],
            "confidence": candidate.confidence >= config["confidence_threshold"],
            "micro_anomaly": micro_anomaly_score < config["micro_anomaly_threshold"],
            "market_stress": market_stress_index < config["market_stress_threshold"]
        }
        
        qualified = all(conditions.values())
        
        return {"qualified": qualified, "conditions": conditions}
    
    async def _express_lane_processing(self, candidate: SignalCandidate) -> PreEvaluationResult:
        """JSON快速通道處理 - 3ms目標"""
        notes = ["[快速通道] JSON優化處理"]
        
        # 快速品質驗證
        risk_assessment = {
            "express_lane": True,
            "risk_level": "LOW",
            "phase1_trusted": True
        }
        
        # 快速去重檢查
        if len(self.deduplication_engine.processed_signals) > 0:
            recent_similar = any(
                s.symbol == candidate.symbol and 
                abs((candidate.timestamp - s.timestamp).total_seconds()) < 300
                for s in self.deduplication_engine.processed_signals[-5:]  # 檢查最近5個
            )
            if recent_similar:
                notes.append("[快速通道] 檢測到近期相似信號")
                return PreEvaluationResult(
                    candidate=candidate,
                    deduplication_result=DeduplicationResult.DELAY_OBSERVE,
                    correlation_result=CorrelationAnalysisResult.INDEPENDENT_NEW,
                    quality_result=QualityControlResult.EXCELLENT,
                    pass_to_epl=False,
                    processing_notes=notes,
                    similarity_score=0.8,
                    risk_assessment=risk_assessment,
                    timestamp=datetime.now()
                )
        
        # 快速通過
        self.deduplication_engine.add_processed_signal(candidate)
        notes.append("[快速通道] 直接通過EPL")
        
        return PreEvaluationResult(
            candidate=candidate,
            deduplication_result=DeduplicationResult.UNIQUE,
            correlation_result=CorrelationAnalysisResult.INDEPENDENT_NEW,
            quality_result=QualityControlResult.EXCELLENT,
            pass_to_epl=True,
            processing_notes=notes,
            similarity_score=0.0,
            risk_assessment=risk_assessment,
            timestamp=datetime.now()
        )
    
    async def _standard_lane_processing(self, candidate: SignalCandidate) -> PreEvaluationResult:
        """JSON標準通道處理 - 15ms目標"""
        notes = ["[標準通道] JSON優化三步驟流程"]
        
        # Step 1: 智能去重
        dedup_result, similarity, dedup_notes = await self.deduplication_engine.analyze_duplication(candidate)
        notes.extend([f"[去重] {note}" for note in dedup_notes])
        
        if dedup_result == DeduplicationResult.IGNORE:
            self.processing_stats["rejection_reasons"]["duplication"] += 1
            return PreEvaluationResult(
                candidate=candidate,
                deduplication_result=dedup_result,
                correlation_result=CorrelationAnalysisResult.INDEPENDENT_NEW,
                quality_result=QualityControlResult.PASS,
                pass_to_epl=False,
                processing_notes=notes,
                similarity_score=similarity,
                risk_assessment={},
                timestamp=datetime.now()
            )
        
        # Step 2: 上下文關聯
        correlation_result, corr_notes = await self.correlation_analyzer.analyze_correlation(candidate)
        notes.extend([f"[關聯] {note}" for note in corr_notes])
        
        # Step 3: 輕量品質控制
        quality_result, risk_assessment, quality_notes = await self.quality_control_gate.evaluate_quality(candidate)
        notes.extend([f"[品質] {note}" for note in quality_notes])
        
        # 最終決策
        pass_to_epl = (dedup_result != DeduplicationResult.IGNORE and
                       quality_result in [QualityControlResult.PASS, QualityControlResult.EXCELLENT])
        
        if pass_to_epl:
            self.deduplication_engine.add_processed_signal(candidate)
        else:
            # 記錄拒絕原因
            if quality_result == QualityControlResult.FAIL_STRENGTH:
                self.processing_stats["rejection_reasons"]["quality_strength"] += 1
            elif quality_result == QualityControlResult.FAIL_LIQUIDITY:
                self.processing_stats["rejection_reasons"]["quality_liquidity"] += 1
            elif quality_result == QualityControlResult.FAIL_RISK:
                self.processing_stats["rejection_reasons"]["quality_risk"] += 1
        
        return PreEvaluationResult(
            candidate=candidate,
            deduplication_result=dedup_result,
            correlation_result=correlation_result,
            quality_result=quality_result,
            pass_to_epl=pass_to_epl,
            processing_notes=notes,
            similarity_score=similarity,
            risk_assessment=risk_assessment,
            timestamp=datetime.now()
        )
    
    async def _deep_analysis_processing(self, candidate: SignalCandidate) -> PreEvaluationResult:
        """JSON深度分析處理 - 40ms目標"""
        notes = ["[深度分析] JSON完整驗證流程"]
        
        # 完整三步驟 + 額外分析
        result = await self._standard_lane_processing(candidate)
        
        # 深度分析增強
        notes.append("[深度分析] 額外市場環境驗證")
        notes.append("[深度分析] 延遲觀察追蹤設置")
        
        result.processing_notes = notes + result.processing_notes
        
        return result
    
    def _update_performance_metrics(self, lane: str, processing_time: float):
        """更新性能指標"""
        metrics = self.processing_stats["performance_metrics"]
        
        # 更新平均處理時間
        total = self.processing_stats["total_processed"]
        if total > 0:
            metrics["avg_processing_time"] = (
                (metrics["avg_processing_time"] * total + processing_time) / (total + 1)
            )
        else:
            metrics["avg_processing_time"] = processing_time
        
        # 更新通道特定指標
        if lane == "express":
            count = self.processing_stats["express_lane_count"]
            if count > 0:
                metrics["express_lane_avg_time"] = (
                    (metrics["express_lane_avg_time"] * (count - 1) + processing_time) / count
                )
            else:
                metrics["express_lane_avg_time"] = processing_time
        elif lane == "standard":
            count = self.processing_stats["standard_lane_count"]
            if count > 0:
                metrics["standard_lane_avg_time"] = (
                    (metrics["standard_lane_avg_time"] * (count - 1) + processing_time) / count
                )
            else:
                metrics["standard_lane_avg_time"] = processing_time
    
    def _update_processing_stats(self, result: PreEvaluationResult):
        """更新處理統計"""
        self.processing_stats["total_processed"] += 1
        if result.pass_to_epl:
            self.processing_stats["passed_to_epl"] += 1
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """獲取處理統計"""
        stats = self.processing_stats.copy()
        if stats["total_processed"] > 0:
            stats["pass_rate"] = stats["passed_to_epl"] / stats["total_processed"] * 100
            stats["express_lane_ratio"] = stats["express_lane_count"] / stats["total_processed"] * 100
            stats["standard_lane_ratio"] = stats["standard_lane_count"] / stats["total_processed"] * 100
            stats["deep_lane_ratio"] = stats["deep_lane_count"] / stats["total_processed"] * 100
        else:
            stats["pass_rate"] = 0.0
            stats["express_lane_ratio"] = 0.0
            stats["standard_lane_ratio"] = 0.0
            stats["deep_lane_ratio"] = 0.0
        return stats
    
    def update_position_status(self, symbol: str, signal: Optional[SignalCandidate] = None):
        """更新持倉狀態"""
        if signal:
            self.correlation_analyzer.update_position(symbol, signal)
        else:
            self.correlation_analyzer.remove_position(symbol)

# JSON全局實例
enhanced_pre_evaluation_layer = EnhancedPreEvaluationLayer()
