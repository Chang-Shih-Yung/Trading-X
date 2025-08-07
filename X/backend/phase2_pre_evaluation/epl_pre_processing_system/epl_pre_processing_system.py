"""
🧠 Phase 2: 信號前處理層 (Pre-Evaluation Layer)
=============================================

EPL 前處理系統 - 三步驟信號品質控制
1. 去重分析引擎
2. 信號關聯分析器  
3. 品質控制門檻
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import sys
from pathlib import Path

# 添加路徑
current_dir = Path(__file__).parent
sys.path.extend([
    str(current_dir.parent / "shared_core"),
    str(current_dir.parent / "phase1_signal_generation"),
])

from unified_signal_candidate_pool import SignalCandidate, SignalSource

logger = logging.getLogger(__name__)

class DeduplicationResult(Enum):
    """去重分析結果"""
    UNIQUE = "⭐ 獨特"             # 快速通道 - 獨特信號
    IGNORE = "❌ 忽略"           # 完全重複，忽略
    DELAY_OBSERVE = "⚠️ 延遲觀察"  # 可能重複，延遲觀察
    PASS = "✅ 通過"            # 無重複，通過

class CorrelationAnalysisResult(Enum):
    """關聯分析結果"""
    STRENGTHEN_CANDIDATE = "➕ 強化候選"  # 強化現有持倉
    REPLACE_CANDIDATE = "🔁 替換候選"    # 替換現有持倉
    INDEPENDENT_NEW = "✅ 獨立新單"      # 獨立新交易

class QualityControlResult(Enum):
    """品質控制結果"""
    EXCELLENT = "🌟 優秀"              # 快速通道 - 優秀品質
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
    pass_to_epl: bool                    # 是否通過進入EPL
    processing_notes: List[str]          # 處理備註
    similarity_score: Optional[float]    # 相似度分數
    risk_assessment: Dict[str, Any]      # 風險評估詳情
    timestamp: datetime

class DeduplicationEngine:
    """Step 1: 去重分析引擎"""
    
    def __init__(self):
        self.processed_signals: List[SignalCandidate] = []
        self.similarity_threshold = 0.85  # 85%相似度閾值
        self.time_overlap_minutes = 15    # 15分鐘時間重疊
        self.confidence_diff_threshold = 0.03  # 3%信心度差異
    
    async def analyze_duplication(self, candidate: SignalCandidate) -> Tuple[DeduplicationResult, float, List[str]]:
        """分析信號重複性"""
        notes = []
        max_similarity = 0.0
        
        try:
            # 篩選相關的歷史信號 (同標的 + 時間窗口內)
            relevant_signals = self._get_relevant_historical_signals(candidate)
            
            if not relevant_signals:
                notes.append("無歷史信號比對")
                return DeduplicationResult.PASS, 0.0, notes
            
            # 逐一比較相似度
            for historical_signal in relevant_signals:
                similarity = self._calculate_signal_similarity(candidate, historical_signal)
                max_similarity = max(max_similarity, similarity)
                
                # 時間重疊檢測
                time_overlap = self._check_time_overlap(candidate, historical_signal)
                
                # 指標來源比對
                indicator_similarity = self._compare_indicator_sources(candidate, historical_signal)
                
                # 信心度差異分析
                confidence_diff = abs(candidate.confidence - historical_signal.confidence)
                
                notes.append(f"與{historical_signal.id}相似度: {similarity:.2f}")
                
                # 判斷重複性
                if (time_overlap and 
                    indicator_similarity > self.similarity_threshold and 
                    confidence_diff < self.confidence_diff_threshold):
                    
                    if similarity > 0.95:  # 高度相似
                        notes.append("高度重複信號，建議忽略")
                        return DeduplicationResult.IGNORE, similarity, notes
                    elif similarity > 0.80:  # 中度相似
                        notes.append("中度重複信號，延遲觀察")
                        return DeduplicationResult.DELAY_OBSERVE, similarity, notes
            
            notes.append(f"最高相似度: {max_similarity:.2f}")
            return DeduplicationResult.PASS, max_similarity, notes
            
        except Exception as e:
            logger.error(f"去重分析失敗: {e}")
            notes.append(f"分析錯誤: {e}")
            return DeduplicationResult.PASS, 0.0, notes  # 錯誤時預設通過
    
    def _get_relevant_historical_signals(self, candidate: SignalCandidate) -> List[SignalCandidate]:
        """獲取相關歷史信號"""
        cutoff_time = candidate.timestamp - timedelta(minutes=self.time_overlap_minutes)
        
        return [
            signal for signal in self.processed_signals
            if (signal.symbol == candidate.symbol and 
                signal.timestamp > cutoff_time and
                signal.timestamp < candidate.timestamp)
        ]
    
    def _calculate_signal_similarity(self, candidate1: SignalCandidate, candidate2: SignalCandidate) -> float:
        """計算信號相似度"""
        similarity_factors = []
        
        # 1. 強度相似度
        strength_similarity = 1 - abs(candidate1.signal_strength - candidate2.signal_strength) / 100
        similarity_factors.append(strength_similarity * 0.3)
        
        # 2. 方向相似度
        direction_similarity = 1.0 if candidate1.direction == candidate2.direction else 0.0
        similarity_factors.append(direction_similarity * 0.2)
        
        # 3. 來源相似度
        source_similarity = 1.0 if candidate1.source == candidate2.source else 0.5
        similarity_factors.append(source_similarity * 0.2)
        
        # 4. 技術指標相似度
        tech_similarity = self._calculate_technical_similarity(
            candidate1.technical_snapshot, candidate2.technical_snapshot
        )
        similarity_factors.append(tech_similarity * 0.3)
        
        return sum(similarity_factors)
    
    def _calculate_technical_similarity(self, tech1, tech2) -> float:
        """計算技術指標相似度"""
        try:
            similarities = []
            
            # RSI相似度
            rsi_sim = 1 - abs(tech1.rsi - tech2.rsi) / 100
            similarities.append(rsi_sim)
            
            # MACD相似度
            macd_sim = 1 - min(1.0, abs(tech1.macd_signal - tech2.macd_signal) / 2)
            similarities.append(macd_sim)
            
            # 布林帶位置相似度
            bb_sim = 1 - abs(tech1.bollinger_position - tech2.bollinger_position)
            similarities.append(bb_sim)
            
            return np.mean(similarities)
            
        except Exception:
            return 0.5  # 預設中等相似度
    
    def _check_time_overlap(self, candidate1: SignalCandidate, candidate2: SignalCandidate) -> bool:
        """檢查時間重疊"""
        time_diff = abs((candidate1.timestamp - candidate2.timestamp).total_seconds() / 60)
        return time_diff < self.time_overlap_minutes
    
    def _compare_indicator_sources(self, candidate1: SignalCandidate, candidate2: SignalCandidate) -> float:
        """比較指標來源相似度"""
        # 簡化實現 - 比較來源類型
        if candidate1.source == candidate2.source:
            return 1.0
        elif candidate1.source in [SignalSource.PHASE1ABC_DYNAMIC] and candidate2.source in [SignalSource.PHASE1ABC_DYNAMIC]:
            return 0.8
        else:
            return 0.3
    
    def add_processed_signal(self, signal: SignalCandidate):
        """添加已處理信號到歷史記錄"""
        self.processed_signals.append(signal)
        
        # 保持歷史記錄在合理範圍內 (最近1小時)
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.processed_signals = [s for s in self.processed_signals if s.timestamp > cutoff_time]

class CorrelationAnalyzer:
    """Step 2: 信號關聯分析器"""
    
    def __init__(self):
        self.current_positions: Dict[str, SignalCandidate] = {}  # 當前持倉信號
        self.symbol_correlations: Dict[str, List[str]] = {}      # 標的相關性映射
    
    async def analyze_correlation(self, candidate: SignalCandidate) -> Tuple[CorrelationAnalysisResult, List[str]]:
        """分析信號關聯性"""
        notes = []
        
        try:
            # 標的相關性檢測
            correlated_symbols = self._get_correlated_symbols(candidate.symbol)
            notes.append(f"相關標的: {correlated_symbols}")
            
            # 檢查當前持倉
            current_position = self.current_positions.get(candidate.symbol)
            
            if current_position:
                # 方向衝突分析
                direction_conflict = self._analyze_direction_conflict(candidate, current_position)
                
                # 持倉關聯評估
                position_strength_diff = candidate.signal_strength - current_position.signal_strength
                confidence_diff = candidate.confidence - current_position.confidence
                
                notes.append(f"當前持倉強度差: {position_strength_diff:.1f}")
                notes.append(f"信心度差異: {confidence_diff:.3f}")
                
                # 決策邏輯
                if direction_conflict and confidence_diff > 0.15:  # 方向相反且信心度大幅提升
                    notes.append("建議替換：方向相反且信心度大幅提升")
                    return CorrelationAnalysisResult.REPLACE_CANDIDATE, notes
                
                elif not direction_conflict and confidence_diff > 0.08:  # 方向相同且信心度提升
                    notes.append("建議強化：方向相同且信心度提升")
                    return CorrelationAnalysisResult.STRENGTHEN_CANDIDATE, notes
                
                else:
                    notes.append("持倉關聯度低，視為獨立機會")
                    return CorrelationAnalysisResult.INDEPENDENT_NEW, notes
            
            # 檢查相關標的持倉
            for corr_symbol in correlated_symbols:
                if corr_symbol in self.current_positions:
                    corr_position = self.current_positions[corr_symbol]
                    correlation_impact = self._assess_correlation_impact(candidate, corr_position)
                    notes.append(f"與{corr_symbol}持倉相關性: {correlation_impact}")
            
            notes.append("無直接持倉衝突，視為獨立新機會")
            return CorrelationAnalysisResult.INDEPENDENT_NEW, notes
            
        except Exception as e:
            logger.error(f"關聯分析失敗: {e}")
            notes.append(f"分析錯誤: {e}")
            return CorrelationAnalysisResult.INDEPENDENT_NEW, notes
    
    def _get_correlated_symbols(self, symbol: str) -> List[str]:
        """獲取相關標的"""
        # 預定義的加密貨幣相關性
        correlation_groups = {
            "BTCUSDT": ["ETHUSDT", "ADAUSDT"],
            "ETHUSDT": ["BTCUSDT", "DOTUSDT", "LINKUSDT"],
            "ADAUSDT": ["DOTUSDT", "ATOMUSDT"],
            "SOLUSDT": ["AVAXUSDT", "NEARUSDT"]
        }
        
        return correlation_groups.get(symbol, [])
    
    def _analyze_direction_conflict(self, candidate: SignalCandidate, current_position: SignalCandidate) -> bool:
        """分析方向衝突"""
        return candidate.direction != current_position.direction
    
    def _assess_correlation_impact(self, candidate: SignalCandidate, correlated_position: SignalCandidate) -> str:
        """評估相關性影響"""
        if candidate.direction == correlated_position.direction:
            return "正相關 - 可能加強組合風險"
        else:
            return "負相關 - 可能提供對沖效果"
    
    def update_position(self, symbol: str, signal: SignalCandidate):
        """更新持倉信號"""
        self.current_positions[symbol] = signal
    
    def remove_position(self, symbol: str):
        """移除持倉"""
        if symbol in self.current_positions:
            del self.current_positions[symbol]

class QualityControlGate:
    """Step 3: 品質控制門檻"""
    
    def __init__(self):
        self.strength_threshold = 70.0      # 信號強度閾值
        self.liquidity_threshold = 0.6      # 流動性閾值
        self.risk_score_threshold = 0.3     # 風險評分閾值
    
    async def evaluate_quality(self, candidate: SignalCandidate) -> Tuple[QualityControlResult, Dict[str, Any], List[str]]:
        """評估信號品質"""
        notes = []
        risk_assessment = {}
        
        try:
            # 1. 信號強度篩選
            if candidate.signal_strength < self.strength_threshold:
                notes.append(f"信號強度 {candidate.signal_strength:.1f} < 閾值 {self.strength_threshold}")
                return QualityControlResult.FAIL_STRENGTH, {}, notes
            
            # 2. 市場流動性驗證
            liquidity_score = candidate.market_environment.liquidity_score
            if liquidity_score < self.liquidity_threshold:
                notes.append(f"流動性 {liquidity_score:.2f} < 閾值 {self.liquidity_threshold}")
                return QualityControlResult.FAIL_LIQUIDITY, {}, notes
            
            # 3. 風險評估
            risk_assessment = await self._comprehensive_risk_assessment(candidate)
            
            if risk_assessment["overall_risk_score"] > self.risk_score_threshold:
                notes.append(f"風險評分過高: {risk_assessment['overall_risk_score']:.3f}")
                return QualityControlResult.FAIL_RISK, risk_assessment, notes
            
            # 通過所有檢查
            notes.append("✅ 通過所有品質控制檢查")
            notes.append(f"強度: {candidate.signal_strength:.1f}, 流動性: {liquidity_score:.2f}, 風險: {risk_assessment['overall_risk_score']:.3f}")
            
            return QualityControlResult.PASS, risk_assessment, notes
            
        except Exception as e:
            logger.error(f"品質評估失敗: {e}")
            notes.append(f"評估錯誤: {e}")
            return QualityControlResult.PASS, {}, notes  # 錯誤時預設通過
    
    async def _comprehensive_risk_assessment(self, candidate: SignalCandidate) -> Dict[str, Any]:
        """綜合風險評估"""
        risk_factors = {}
        
        # 1. 波動性風險
        volatility = candidate.market_environment.volatility
        volatility_risk = min(1.0, volatility * 20)  # 正規化到0-1
        risk_factors["volatility_risk"] = volatility_risk
        
        # 2. 流動性風險
        liquidity_risk = 1.0 - candidate.market_environment.liquidity_score
        risk_factors["liquidity_risk"] = liquidity_risk
        
        # 3. 技術指標風險 (極端值風險)
        tech_risk = 0.0
        if candidate.technical_snapshot.rsi > 80 or candidate.technical_snapshot.rsi < 20:
            tech_risk += 0.3
        if abs(candidate.technical_snapshot.williams_r) > 80:
            tech_risk += 0.2
        risk_factors["technical_risk"] = min(1.0, tech_risk)
        
        # 4. 市場環境風險
        momentum = abs(candidate.market_environment.momentum)
        momentum_risk = min(1.0, momentum * 2)
        risk_factors["momentum_risk"] = momentum_risk
        
        # 5. 數據完整性風險
        data_risk = 1.0 - candidate.data_completeness
        risk_factors["data_completeness_risk"] = data_risk
        
        # 綜合風險評分 (加權平均)
        weights = {
            "volatility_risk": 0.3,
            "liquidity_risk": 0.25,
            "technical_risk": 0.2,
            "momentum_risk": 0.15,
            "data_completeness_risk": 0.1
        }
        
        overall_risk = sum(risk_factors[factor] * weights[factor] for factor in risk_factors)
        
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

class PreEvaluationLayer:
    """EPL 前處理系統主控制器"""
    
    def __init__(self):
        self.deduplication_engine = DeduplicationEngine()
        self.correlation_analyzer = CorrelationAnalyzer()
        self.quality_control_gate = QualityControlGate()
        
        self.processing_stats = {
            "total_processed": 0,
            "passed_to_epl": 0,
            "rejection_reasons": {
                "duplication": 0,
                "quality_strength": 0,
                "quality_liquidity": 0,
                "quality_risk": 0
            }
        }
    
    async def process_signal_candidate(self, candidate: SignalCandidate) -> PreEvaluationResult:
        """處理信號候選者 - 三步驟流程 (Phase1數據優化版)"""
        all_notes = []
        
        try:
            logger.info(f"🧠 EPL前處理開始: {candidate.id}")
            
            # 🚀 智能快速通道判斷
            if self._is_high_quality_from_phase1(candidate):
                logger.info(f"⚡ 高品質信號快速通道: {candidate.id}")
                return self._express_lane_processing(candidate)
            
            # Step 1: 精簡去重分析 (利用Phase1 dynamic_params)
            dedup_result, similarity, dedup_notes = await self.deduplication_engine.analyze_duplication(candidate)
            all_notes.extend([f"[去重] {note}" for note in dedup_notes])
            
            # 如果重複性太高，直接拒絕
            if dedup_result == DeduplicationResult.IGNORE:
                self.processing_stats["rejection_reasons"]["duplication"] += 1
                result = PreEvaluationResult(
                    candidate=candidate,
                    deduplication_result=dedup_result,
                    correlation_result=CorrelationAnalysisResult.INDEPENDENT_NEW,  # 預設值
                    quality_result=QualityControlResult.PASS,  # 預設值
                    pass_to_epl=False,
                    processing_notes=all_notes,
                    similarity_score=similarity,
                    risk_assessment={},
                    timestamp=datetime.now()
                )
                self._update_processing_stats(result)
                return result
            
            # Step 2: 信號關聯分析 (利用Phase1 market_environment)
            correlation_result, corr_notes = await self.correlation_analyzer.analyze_correlation(candidate)
            all_notes.extend([f"[關聯] {note}" for note in corr_notes])
            
            # Step 3: 簡化品質控制 (信任Phase1品質指標)
            quality_result, risk_assessment, quality_notes = await self.quality_control_gate.evaluate_quality(candidate)
            all_notes.extend([f"[品質] {note}" for note in quality_notes])
            
            # 判斷是否通過進入EPL
            pass_to_epl = (
                dedup_result != DeduplicationResult.IGNORE and
                quality_result == QualityControlResult.PASS
            )
            
            # 記錄拒絕原因
            if not pass_to_epl:
                if quality_result == QualityControlResult.FAIL_STRENGTH:
                    self.processing_stats["rejection_reasons"]["quality_strength"] += 1
                elif quality_result == QualityControlResult.FAIL_LIQUIDITY:
                    self.processing_stats["rejection_reasons"]["quality_liquidity"] += 1
                elif quality_result == QualityControlResult.FAIL_RISK:
                    self.processing_stats["rejection_reasons"]["quality_risk"] += 1
            
            # 如果通過，添加到已處理信號記錄
            if pass_to_epl:
                self.deduplication_engine.add_processed_signal(candidate)
                self.processing_stats["passed_to_epl"] += 1
            
            result = PreEvaluationResult(
                candidate=candidate,
                deduplication_result=dedup_result,
                correlation_result=correlation_result,
                quality_result=quality_result,
                pass_to_epl=pass_to_epl,
                processing_notes=all_notes,
                similarity_score=similarity,
                risk_assessment=risk_assessment,
                timestamp=datetime.now()
            )
            
            self._update_processing_stats(result)
            
            status = "✅ 通過EPL" if pass_to_epl else "❌ 未通過EPL"
            logger.info(f"🧠 EPL前處理完成: {candidate.id} - {status}")
            
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
                risk_assessment={},
                timestamp=datetime.now()
            )
    
    def _update_processing_stats(self, result: PreEvaluationResult):
        """更新處理統計"""
        self.processing_stats["total_processed"] += 1
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """獲取處理統計"""
        stats = self.processing_stats.copy()
        if stats["total_processed"] > 0:
            stats["pass_rate"] = stats["passed_to_epl"] / stats["total_processed"] * 100
        else:
            stats["pass_rate"] = 0.0
        return stats
    
    def update_position_status(self, symbol: str, signal: Optional[SignalCandidate] = None):
        """更新持倉狀態"""
        if signal:
            self.correlation_analyzer.update_position(symbol, signal)
        else:
            self.correlation_analyzer.remove_position(symbol)
    
    def _is_high_quality_from_phase1(self, candidate: SignalCandidate) -> bool:
        """基於Phase1數據判斷是否為高品質信號 (快速通道條件)"""
        try:
            # Phase1品質指標檢查
            data_quality = candidate.data_completeness >= 0.9
            signal_clarity = candidate.signal_clarity >= 0.8
            confidence_high = candidate.confidence >= 0.75
            
            # 技術指標完整性檢查
            tech_snapshot = candidate.technical_snapshot
            has_strong_indicators = (
                tech_snapshot and
                hasattr(tech_snapshot, 'rsi') and
                hasattr(tech_snapshot, 'macd_signal') and
                hasattr(tech_snapshot, 'bb_position')
            )
            
            # 市場環境穩定性
            market_env = candidate.market_environment
            stable_market = (
                market_env and
                hasattr(market_env, 'volatility') and
                market_env.volatility < 0.08  # 低波動
            )
            
            # 信號強度閾值
            strong_signal = candidate.signal_strength >= 75
            
            # 綜合判斷
            return (data_quality and signal_clarity and confidence_high and 
                   has_strong_indicators and stable_market and strong_signal)
                   
        except Exception as e:
            logger.warning(f"⚠️ 快速通道檢查失敗: {e}")
            return False
    
    def _express_lane_processing(self, candidate: SignalCandidate) -> PreEvaluationResult:
        """快速通道處理 - 直接通過高品質信號"""
        logger.info(f"🚀 快速通道處理: {candidate.id}")
        
        # 快速風險評估
        risk_assessment = {
            "overall_risk": "LOW",
            "risk_score": 0.15,
            "phase1_quality_verified": True,
            "express_lane": True,
            "confidence_boost": 0.05  # 給予額外信心加成
        }
        
        result = PreEvaluationResult(
            candidate=candidate,
            deduplication_result=DeduplicationResult.UNIQUE,  # 信任高品質信號
            correlation_result=CorrelationAnalysisResult.INDEPENDENT_NEW,
            quality_result=QualityControlResult.EXCELLENT,
            pass_to_epl=True,
            processing_notes=[
                "[快速通道] Phase1品質驗證通過",
                "[快速通道] 數據完整性優秀",
                "[快速通道] 信號清晰度高",
                "[快速通道] 直接推進EPL決策層"
            ],
            similarity_score=0.0,  # 假設獨特
            risk_assessment=risk_assessment,
            timestamp=datetime.now()
        )
        
        # 更新統計
        self.processing_stats["total_processed"] += 1
        self.processing_stats["passed_to_epl"] += 1
        self.processing_stats["express_lane_count"] = self.processing_stats.get("express_lane_count", 0) + 1
        
        # 添加到已處理信號記錄
        self.deduplication_engine.add_processed_signal(candidate)
        
        return result

# 全局前處理層實例
pre_evaluation_layer = PreEvaluationLayer()
