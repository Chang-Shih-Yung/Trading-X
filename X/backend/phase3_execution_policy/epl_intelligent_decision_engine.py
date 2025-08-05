"""
⚙️ Phase 3: 執行決策層 (Execution Policy Layer)
============================================

EPL 智能決策引擎 - 四情境決策系統
A. 替單決策 B. 加倉決策 C. 新單建立 D. 信號忽略
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import sys
from pathlib import Path

# 添加路徑
current_dir = Path(__file__).parent
sys.path.extend([
    str(current_dir.parent / "shared_core"),
    str(current_dir.parent / "phase1_signal_generation"),
    str(current_dir.parent / "phase2_pre_evaluation")
])

from unified_signal_candidate_pool import SignalCandidate
from epl_pre_processing_system import PreEvaluationResult, CorrelationAnalysisResult

logger = logging.getLogger(__name__)

class EPLDecision(Enum):
    """EPL 決策類型"""
    REPLACE_POSITION = "🔁 替單決策"      # 平倉原單 → 開新單
    STRENGTHEN_POSITION = "➕ 加倉決策"   # 提升現單倉位/調整止盈止損
    CREATE_NEW_POSITION = "✅ 新單建立"   # 建立新獨立交易信號
    IGNORE_SIGNAL = "❌ 信號忽略"        # 丟棄並記錄原因

class SignalPriority(Enum):
    """信號優先級"""
    CRITICAL = "🚨 CRITICAL級"     # 緊急信號
    HIGH = "🎯 HIGH級"            # 高品質信號
    MEDIUM = "📊 MEDIUM級"        # 標準信號
    LOW = "📈 LOW級"              # 觀察信號

@dataclass
class PositionInfo:
    """持倉信息"""
    symbol: str
    direction: str                    # BUY/SELL
    size: float                      # 倉位大小
    entry_price: float               # 進入價格
    current_signal: SignalCandidate  # 當前信號
    stop_loss: Optional[float]       # 止損價格
    take_profit: Optional[float]     # 止盈價格
    unrealized_pnl: float           # 未實現盈虧
    entry_timestamp: datetime       # 開倉時間

@dataclass
class EPLDecisionResult:
    """EPL 決策結果"""
    decision: EPLDecision
    priority: SignalPriority
    candidate: SignalCandidate
    reasoning: List[str]                    # 決策理由
    execution_params: Dict[str, Any]        # 執行參數
    risk_management: Dict[str, Any]         # 風險管理設定
    performance_tracking: Dict[str, Any]    # 績效追蹤信息
    notification_config: Dict[str, Any]     # 通知配置
    timestamp: datetime

class ReplacementDecisionEngine:
    """情境 A: 替單決策引擎"""
    
    def __init__(self):
        self.confidence_threshold = 0.15  # 信心度提升閾值 +15%
        self.direction_conflict_required = True  # 必須方向相反
    
    async def evaluate_replacement(self, candidate: SignalCandidate, 
                                 current_position: PositionInfo) -> Tuple[bool, List[str], Dict[str, Any]]:
        """評估是否應該替換現有持倉"""
        reasons = []
        execution_params = {}
        
        try:
            # 檢查方向衝突
            direction_conflict = candidate.direction != current_position.direction
            if not direction_conflict and self.direction_conflict_required:
                reasons.append("❌ 方向相同，不符合替單條件")
                return False, reasons, {}
            
            # 計算信心度提升
            confidence_improvement = candidate.confidence - current_position.current_signal.confidence
            
            if confidence_improvement < self.confidence_threshold:
                reasons.append(f"❌ 信心度提升不足: {confidence_improvement:.3f} < {self.confidence_threshold}")
                return False, reasons, {}
            
            # 檢查信號強度對比
            strength_improvement = candidate.signal_strength - current_position.current_signal.signal_strength
            
            # 評估市場時機
            market_timing_score = await self._evaluate_market_timing(candidate, current_position)
            
            # 計算替換可行性分數
            replacement_score = (
                confidence_improvement * 0.4 +
                (strength_improvement / 100) * 0.3 +
                market_timing_score * 0.3
            )
            
            if replacement_score > 0.6:  # 替換閾值
                reasons.append(f"✅ 建議替換 - 綜合評分: {replacement_score:.3f}")
                reasons.append(f"  信心度提升: +{confidence_improvement:.3f}")
                reasons.append(f"  強度提升: +{strength_improvement:.1f}")
                reasons.append(f"  市場時機: {market_timing_score:.2f}")
                
                # 設定執行參數
                execution_params = {
                    "close_current_position": True,
                    "close_price_type": "market",  # 市價平倉
                    "new_position_size": self._calculate_optimal_size(candidate, current_position),
                    "entry_price_type": "market",
                    "replacement_reason": "信心度大幅提升且方向相反",
                    "urgency_level": "high" if confidence_improvement > 0.25 else "medium"
                }
                
                return True, reasons, execution_params
            else:
                reasons.append(f"❌ 替換評分不足: {replacement_score:.3f} < 0.6")
                return False, reasons, {}
                
        except Exception as e:
            logger.error(f"替單評估失敗: {e}")
            reasons.append(f"評估錯誤: {e}")
            return False, reasons, {}
    
    async def _evaluate_market_timing(self, candidate: SignalCandidate, position: PositionInfo) -> float:
        """評估市場時機"""
        timing_factors = []
        
        # 波動性時機 (高波動性有利於替換)
        volatility = candidate.market_environment.volatility
        volatility_timing = min(1.0, volatility * 20)  # 正規化
        timing_factors.append(volatility_timing * 0.4)
        
        # 流動性時機
        liquidity_timing = candidate.market_environment.liquidity_score
        timing_factors.append(liquidity_timing * 0.3)
        
        # 技術指標時機 (RSI極端值有利)
        rsi = candidate.technical_snapshot.rsi
        if rsi > 70 or rsi < 30:  # RSI極端值
            rsi_timing = 1.0
        else:
            rsi_timing = 0.5
        timing_factors.append(rsi_timing * 0.3)
        
        return sum(timing_factors)
    
    def _calculate_optimal_size(self, candidate: SignalCandidate, current_position: PositionInfo) -> float:
        """計算最佳新倉位大小"""
        # 基於信心度調整倉位大小
        confidence_multiplier = min(2.0, candidate.confidence * 2)
        base_size = current_position.size
        
        # 考慮波動性調整
        volatility = candidate.market_environment.volatility
        volatility_adjustment = max(0.5, 1.0 - volatility * 10)
        
        optimal_size = base_size * confidence_multiplier * volatility_adjustment
        return round(optimal_size, 4)

class StrengtheningDecisionEngine:
    """情境 B: 加倉決策引擎"""
    
    def __init__(self):
        self.confidence_threshold = 0.08  # 信心度提升閾值 +8%
        self.same_direction_required = True  # 必須方向相同
        self.max_position_multiplier = 2.0  # 最大倉位倍數
    
    async def evaluate_strengthening(self, candidate: SignalCandidate, 
                                   current_position: PositionInfo) -> Tuple[bool, List[str], Dict[str, Any]]:
        """評估是否應該加強現有持倉"""
        reasons = []
        execution_params = {}
        
        try:
            # 檢查方向一致性
            same_direction = candidate.direction == current_position.direction
            if not same_direction:
                reasons.append("❌ 方向不同，不符合加倉條件")
                return False, reasons, {}
            
            # 計算信心度提升
            confidence_improvement = candidate.confidence - current_position.current_signal.confidence
            
            if confidence_improvement < self.confidence_threshold:
                reasons.append(f"❌ 信心度提升不足: {confidence_improvement:.3f} < {self.confidence_threshold}")
                return False, reasons, {}
            
            # 檢查當前持倉表現
            position_performance = await self._evaluate_position_performance(current_position)
            
            # 風險評估 - 確保加倉不會過度放大風險
            risk_assessment = await self._assess_strengthening_risk(candidate, current_position)
            
            # 計算加倉可行性分數
            strengthening_score = (
                confidence_improvement * 0.4 +
                position_performance * 0.3 +
                (1.0 - risk_assessment["overall_risk"]) * 0.3
            )
            
            if strengthening_score > 0.5:  # 加倉閾值
                reasons.append(f"✅ 建議加倉 - 綜合評分: {strengthening_score:.3f}")
                reasons.append(f"  信心度提升: +{confidence_improvement:.3f}")
                reasons.append(f"  持倉表現: {position_performance:.2f}")
                reasons.append(f"  風險評估: {risk_assessment['risk_level']}")
                
                # 設定執行參數
                additional_size = self._calculate_additional_size(candidate, current_position, confidence_improvement)
                new_stop_loss, new_take_profit = self._calculate_new_levels(candidate, current_position)
                
                execution_params = {
                    "action_type": "strengthen",
                    "additional_size": additional_size,
                    "entry_price_type": "market",
                    "adjust_stop_loss": new_stop_loss,
                    "adjust_take_profit": new_take_profit,
                    "strengthening_reason": "方向相同且信心度提升",
                    "risk_management": risk_assessment
                }
                
                return True, reasons, execution_params
            else:
                reasons.append(f"❌ 加倉評分不足: {strengthening_score:.3f} < 0.5")
                return False, reasons, {}
                
        except Exception as e:
            logger.error(f"加倉評估失敗: {e}")
            reasons.append(f"評估錯誤: {e}")
            return False, reasons, {}
    
    async def _evaluate_position_performance(self, position: PositionInfo) -> float:
        """評估當前持倉表現"""
        # 簡化實現 - 基於未實現盈虧和持有時間
        if position.unrealized_pnl > 0:
            performance_score = min(1.0, position.unrealized_pnl / 100)  # 正規化盈利
        else:
            performance_score = max(0.0, 1.0 + position.unrealized_pnl / 100)  # 虧損懲罰
        
        # 持有時間調整 (新持倉更適合加倉)
        holding_hours = (datetime.now() - position.entry_timestamp).total_seconds() / 3600
        time_factor = max(0.5, 1.0 - holding_hours / 24)  # 24小時後衰減
        
        return performance_score * time_factor
    
    async def _assess_strengthening_risk(self, candidate: SignalCandidate, position: PositionInfo) -> Dict[str, Any]:
        """評估加倉風險"""
        risk_factors = {}
        
        # 1. 倉位集中度風險
        concentration_risk = min(1.0, position.size / 1000)  # 假設基礎單位
        risk_factors["concentration_risk"] = concentration_risk
        
        # 2. 市場波動風險
        volatility_risk = min(1.0, candidate.market_environment.volatility * 20)
        risk_factors["volatility_risk"] = volatility_risk
        
        # 3. 技術指標極端風險
        rsi = candidate.technical_snapshot.rsi
        if rsi > 80 or rsi < 20:
            extreme_risk = 0.8
        elif rsi > 70 or rsi < 30:
            extreme_risk = 0.5
        else:
            extreme_risk = 0.2
        risk_factors["extreme_risk"] = extreme_risk
        
        # 綜合風險評分
        overall_risk = (
            concentration_risk * 0.4 +
            volatility_risk * 0.3 +
            extreme_risk * 0.3
        )
        
        return {
            **risk_factors,
            "overall_risk": overall_risk,
            "risk_level": "高" if overall_risk > 0.7 else "中" if overall_risk > 0.4 else "低"
        }
    
    def _calculate_additional_size(self, candidate: SignalCandidate, position: PositionInfo, confidence_improvement: float) -> float:
        """計算追加倉位大小"""
        # 基於信心度提升比例計算
        base_additional = position.size * confidence_improvement * 2  # 基礎追加
        
        # 限制最大倉位
        max_total_size = position.size * self.max_position_multiplier
        max_additional = max_total_size - position.size
        
        return min(base_additional, max_additional)
    
    def _calculate_new_levels(self, candidate: SignalCandidate, position: PositionInfo) -> Tuple[float, float]:
        """計算新的止損和止盈水平"""
        # 基於新信號的技術指標調整止損止盈
        current_price = position.entry_price  # 簡化，實際應獲取當前價格
        atr = candidate.technical_snapshot.atr
        
        if position.direction == "BUY":
            new_stop_loss = current_price - (atr * 2)
            new_take_profit = current_price + (atr * 4)
        else:
            new_stop_loss = current_price + (atr * 2)
            new_take_profit = current_price - (atr * 4)
        
        return new_stop_loss, new_take_profit

class NewPositionDecisionEngine:
    """情境 C: 新單建立引擎"""
    
    def __init__(self):
        self.quality_threshold = 80.0  # 品質分數閾值
        self.max_concurrent_positions = 5  # 最大同時持倉數
    
    async def evaluate_new_position(self, candidate: SignalCandidate, 
                                  current_positions: Dict[str, PositionInfo]) -> Tuple[bool, List[str], Dict[str, Any]]:
        """評估是否應該建立新持倉"""
        reasons = []
        execution_params = {}
        
        try:
            # 檢查是否已有該標的持倉
            if candidate.symbol in current_positions:
                reasons.append("❌ 該標的已有持倉")
                return False, reasons, {}
            
            # 檢查持倉數量限制
            if len(current_positions) >= self.max_concurrent_positions:
                reasons.append(f"❌ 持倉數量已達上限: {len(current_positions)}/{self.max_concurrent_positions}")
                return False, reasons, {}
            
            # 檢查信號品質
            if candidate.signal_strength < self.quality_threshold:
                reasons.append(f"❌ 信號品質不足: {candidate.signal_strength:.1f} < {self.quality_threshold}")
                return False, reasons, {}
            
            # 評估市場環境適合性
            market_suitability = await self._evaluate_market_suitability(candidate)
            
            # 檢查與現有持倉的相關性風險
            correlation_risk = await self._assess_portfolio_correlation_risk(candidate, current_positions)
            
            # 計算新單可行性分數
            new_position_score = (
                (candidate.signal_strength / 100) * 0.4 +
                candidate.confidence * 0.3 +
                market_suitability * 0.2 +
                (1.0 - correlation_risk) * 0.1
            )
            
            if new_position_score > 0.7:  # 新單閾值
                reasons.append(f"✅ 建議新建持倉 - 綜合評分: {new_position_score:.3f}")
                reasons.append(f"  信號強度: {candidate.signal_strength:.1f}")
                reasons.append(f"  信心度: {candidate.confidence:.3f}")
                reasons.append(f"  市場適合度: {market_suitability:.2f}")
                reasons.append(f"  組合相關性風險: {correlation_risk:.2f}")
                
                # 設定執行參數
                position_size = self._calculate_optimal_position_size(candidate, current_positions)
                stop_loss, take_profit = self._calculate_initial_levels(candidate)
                
                execution_params = {
                    "action_type": "new_position",
                    "position_size": position_size,
                    "entry_price_type": "market",
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "creation_reason": "無持倉且品質>80分",
                    "risk_management": {
                        "max_risk_per_trade": position_size * 0.02,  # 2%風險
                        "position_weight": position_size / sum(pos.size for pos in current_positions.values()) if current_positions else 1.0
                    }
                }
                
                return True, reasons, execution_params
            else:
                reasons.append(f"❌ 新單評分不足: {new_position_score:.3f} < 0.7")
                return False, reasons, {}
                
        except Exception as e:
            logger.error(f"新單評估失敗: {e}")
            reasons.append(f"評估錯誤: {e}")
            return False, reasons, {}
    
    async def _evaluate_market_suitability(self, candidate: SignalCandidate) -> float:
        """評估市場環境適合性"""
        suitability_factors = []
        
        # 1. 流動性適合性
        liquidity_score = candidate.market_environment.liquidity_score
        suitability_factors.append(liquidity_score * 0.4)
        
        # 2. 波動性適合性 (適中波動性最佳)
        volatility = candidate.market_environment.volatility
        if 0.01 <= volatility <= 0.03:  # 適中波動性
            volatility_score = 1.0
        elif 0.005 <= volatility <= 0.05:  # 可接受範圍
            volatility_score = 0.7
        else:  # 極端波動性
            volatility_score = 0.3
        suitability_factors.append(volatility_score * 0.3)
        
        # 3. 技術指標環境
        rsi = candidate.technical_snapshot.rsi
        if 30 <= rsi <= 70:  # 正常範圍
            rsi_score = 1.0
        elif 20 <= rsi <= 80:  # 可接受範圍
            rsi_score = 0.7
        else:  # 極端值
            rsi_score = 0.4
        suitability_factors.append(rsi_score * 0.3)
        
        return sum(suitability_factors)
    
    async def _assess_portfolio_correlation_risk(self, candidate: SignalCandidate, 
                                               current_positions: Dict[str, PositionInfo]) -> float:
        """評估組合相關性風險"""
        if not current_positions:
            return 0.0  # 無現有持倉，無相關性風險
        
        correlation_scores = []
        
        # 預定義相關性矩陣 (簡化)
        correlation_matrix = {
            ("BTCUSDT", "ETHUSDT"): 0.8,
            ("BTCUSDT", "ADAUSDT"): 0.6,
            ("ETHUSDT", "DOTUSDT"): 0.7,
            # ... 更多相關性定義
        }
        
        for symbol, position in current_positions.items():
            # 查找相關性
            corr_key1 = (candidate.symbol, symbol)
            corr_key2 = (symbol, candidate.symbol)
            
            correlation = correlation_matrix.get(corr_key1, correlation_matrix.get(corr_key2, 0.2))
            
            # 如果方向相同，相關性增加風險
            if candidate.direction == position.direction:
                risk_contribution = correlation * position.size / 1000  # 簡化風險計算
            else:
                risk_contribution = correlation * 0.5  # 反向持倉降低風險
            
            correlation_scores.append(risk_contribution)
        
        return min(1.0, sum(correlation_scores))
    
    def _calculate_optimal_position_size(self, candidate: SignalCandidate, 
                                       current_positions: Dict[str, PositionInfo]) -> float:
        """計算最佳持倉大小"""
        # 基礎倉位大小 (基於信心度)
        base_size = candidate.confidence * 1000  # 簡化計算
        
        # 基於波動性調整
        volatility = candidate.market_environment.volatility
        volatility_adjustment = max(0.5, 1.0 - volatility * 20)
        
        # 基於現有組合調整
        if current_positions:
            avg_position_size = sum(pos.size for pos in current_positions.values()) / len(current_positions)
            size_adjustment = min(2.0, avg_position_size / 500)  # 與平均倉位的比例
        else:
            size_adjustment = 1.0
        
        optimal_size = base_size * volatility_adjustment * size_adjustment
        return round(optimal_size, 4)
    
    def _calculate_initial_levels(self, candidate: SignalCandidate) -> Tuple[float, float]:
        """計算初始止損和止盈水平"""
        # 使用ATR設定止損止盈
        atr = candidate.technical_snapshot.atr
        # 假設當前價格 (實際應從市場數據獲取)
        current_price = 50000  # 簡化假設
        
        if candidate.direction == "BUY":
            stop_loss = current_price - (atr * 2)      # 2 ATR止損
            take_profit = current_price + (atr * 4)    # 4 ATR止盈 (2:1盈虧比)
        else:  # SELL
            stop_loss = current_price + (atr * 2)
            take_profit = current_price - (atr * 4)
        
        return stop_loss, take_profit

class IgnoreDecisionEngine:
    """情境 D: 信號忽略引擎"""
    
    def __init__(self):
        self.ignore_reasons = {
            "quality_insufficient": "品質分數不達標",
            "high_duplication": "重複性過高",
            "risk_excessive": "風險評估過高",
            "market_unsuitable": "市場環境不適合",
            "portfolio_limit": "組合限制"
        }
    
    async def evaluate_ignore(self, candidate: SignalCandidate, 
                            pre_eval_result: PreEvaluationResult) -> Tuple[bool, List[str], Dict[str, Any]]:
        """評估是否應該忽略信號"""
        reasons = []
        ignore_analysis = {}
        
        try:
            should_ignore = False
            
            # 檢查前處理結果
            if not pre_eval_result.pass_to_epl:
                should_ignore = True
                if pre_eval_result.quality_result.value.startswith("❌"):
                    reasons.append(f"品質控制未通過: {pre_eval_result.quality_result.value}")
                    ignore_analysis["primary_reason"] = "quality_insufficient"
                
                if pre_eval_result.deduplication_result.value == "❌ 忽略":
                    reasons.append("去重分析建議忽略")
                    ignore_analysis["primary_reason"] = "high_duplication"
            
            # 額外的忽略條件檢查
            
            # 1. 信號強度過低
            if candidate.signal_strength < 50:
                should_ignore = True
                reasons.append(f"信號強度過低: {candidate.signal_strength:.1f}")
                ignore_analysis["primary_reason"] = "quality_insufficient"
            
            # 2. 數據完整性不足
            if candidate.data_completeness < 0.7:
                should_ignore = True
                reasons.append(f"數據完整性不足: {candidate.data_completeness:.2f}")
                ignore_analysis["primary_reason"] = "quality_insufficient"
            
            # 3. 市場環境極端
            volatility = candidate.market_environment.volatility
            if volatility > 0.1:  # 極高波動
                should_ignore = True
                reasons.append(f"市場波動性過高: {volatility:.3f}")
                ignore_analysis["primary_reason"] = "market_unsuitable"
            
            # 4. 技術指標極端且不確定
            rsi = candidate.technical_snapshot.rsi
            if (rsi > 90 or rsi < 10) and candidate.confidence < 0.8:
                should_ignore = True
                reasons.append(f"技術指標極端且信心度不足: RSI={rsi:.1f}, 信心度={candidate.confidence:.2f}")
                ignore_analysis["primary_reason"] = "market_unsuitable"
            
            if should_ignore:
                ignore_analysis.update({
                    "ignore_timestamp": datetime.now(),
                    "signal_id": candidate.id,
                    "symbol": candidate.symbol,
                    "original_strength": candidate.signal_strength,
                    "original_confidence": candidate.confidence,
                    "model_feedback": {
                        "signal_quality_score": candidate.signal_strength,
                        "market_condition_score": 1.0 - volatility * 10,
                        "data_reliability_score": candidate.data_completeness,
                        "improvement_suggestions": self._generate_improvement_suggestions(candidate)
                    }
                })
                
                reasons.append("✅ 確認忽略信號並記錄反饋數據")
            else:
                reasons.append("❌ 未發現忽略條件，不應忽略")
            
            return should_ignore, reasons, ignore_analysis
            
        except Exception as e:
            logger.error(f"忽略評估失敗: {e}")
            reasons.append(f"評估錯誤: {e}")
            return True, reasons, {"error": str(e)}  # 錯誤時預設忽略
    
    def _generate_improvement_suggestions(self, candidate: SignalCandidate) -> List[str]:
        """生成模型改進建議"""
        suggestions = []
        
        if candidate.signal_strength < 70:
            suggestions.append("提高信號強度計算精度")
        
        if candidate.confidence < 0.7:
            suggestions.append("改進信心度評估算法")
        
        if candidate.data_completeness < 0.8:
            suggestions.append("加強數據源完整性檢查")
        
        volatility = candidate.market_environment.volatility
        if volatility > 0.05:
            suggestions.append("增加極端波動性過濾機制")
        
        return suggestions

class PriorityClassificationEngine:
    """信號優先級分類引擎"""
    
    def __init__(self):
        self.priority_thresholds = {
            SignalPriority.CRITICAL: {"strength": 90, "confidence": 0.9, "urgency_factors": 3},
            SignalPriority.HIGH: {"strength": 80, "confidence": 0.8, "urgency_factors": 2},
            SignalPriority.MEDIUM: {"strength": 70, "confidence": 0.7, "urgency_factors": 1},
            SignalPriority.LOW: {"strength": 60, "confidence": 0.6, "urgency_factors": 0}
        }
    
    def classify_priority(self, candidate: SignalCandidate, decision: EPLDecision) -> Tuple[SignalPriority, List[str]]:
        """分類信號優先級"""
        reasons = []
        urgency_factors = []
        
        # 計算緊急因素
        
        # 1. 替單決策自動提升優先級
        if decision == EPLDecision.REPLACE_POSITION:
            urgency_factors.append("替單決策")
        
        # 2. 極端技術指標
        rsi = candidate.technical_snapshot.rsi
        if rsi > 85 or rsi < 15:
            urgency_factors.append("RSI極端值")
        
        # 3. 高波動性環境
        volatility = candidate.market_environment.volatility
        if volatility > 0.05:
            urgency_factors.append("高波動性")
        
        # 4. 狙擊手雙層架構信號
        if candidate.source.value == "狙擊手雙層架構":
            urgency_factors.append("狙擊手信號")
        
        # 5. 資金費率極端值
        if candidate.market_environment.funding_rate:
            funding_rate = abs(candidate.market_environment.funding_rate)
            if funding_rate > 0.01:  # 1%以上
                urgency_factors.append("極端資金費率")
        
        urgency_count = len(urgency_factors)
        
        # 根據閾值分類
        for priority, thresholds in self.priority_thresholds.items():
            if (candidate.signal_strength >= thresholds["strength"] and
                candidate.confidence >= thresholds["confidence"] and
                urgency_count >= thresholds["urgency_factors"]):
                
                reasons.append(f"符合{priority.value}條件:")
                reasons.append(f"  強度: {candidate.signal_strength:.1f} >= {thresholds['strength']}")
                reasons.append(f"  信心度: {candidate.confidence:.2f} >= {thresholds['confidence']}")
                reasons.append(f"  緊急因素: {urgency_count} >= {thresholds['urgency_factors']}")
                if urgency_factors:
                    reasons.append(f"  緊急因素詳情: {', '.join(urgency_factors)}")
                
                return priority, reasons
        
        # 預設為LOW級
        reasons.append("未達到更高優先級條件，歸類為LOW級")
        return SignalPriority.LOW, reasons

class ExecutionPolicyLayer:
    """EPL 智能決策引擎主控制器"""
    
    def __init__(self):
        self.replacement_engine = ReplacementDecisionEngine()
        self.strengthening_engine = StrengtheningDecisionEngine()
        self.new_position_engine = NewPositionDecisionEngine()
        self.ignore_engine = IgnoreDecisionEngine()
        self.priority_classifier = PriorityClassificationEngine()
        
        # 模擬持倉管理 (實際應整合交易系統)
        self.current_positions: Dict[str, PositionInfo] = {}
        
        # 決策統計
        self.decision_stats = {
            "total_processed": 0,
            "decisions": {decision: 0 for decision in EPLDecision},
            "priorities": {priority: 0 for priority in SignalPriority}
        }
    
    async def make_execution_decision(self, candidate: SignalCandidate, 
                                    pre_eval_result: PreEvaluationResult) -> EPLDecisionResult:
        """執行決策主邏輯"""
        all_reasoning = []
        
        try:
            logger.info(f"⚙️ EPL決策開始: {candidate.id}")
            
            # 預檢查 - 是否應該直接忽略
            should_ignore, ignore_reasons, ignore_analysis = await self.ignore_engine.evaluate_ignore(candidate, pre_eval_result)
            
            if should_ignore:
                # 直接忽略
                priority, priority_reasons = self.priority_classifier.classify_priority(candidate, EPLDecision.IGNORE_SIGNAL)
                
                all_reasoning.extend([f"[忽略評估] {reason}" for reason in ignore_reasons])
                all_reasoning.extend([f"[優先級] {reason}" for reason in priority_reasons])
                
                result = EPLDecisionResult(
                    decision=EPLDecision.IGNORE_SIGNAL,
                    priority=priority,
                    candidate=candidate,
                    reasoning=all_reasoning,
                    execution_params={},
                    risk_management={},
                    performance_tracking=ignore_analysis,
                    notification_config=self._get_notification_config(EPLDecision.IGNORE_SIGNAL, priority),
                    timestamp=datetime.now()
                )
                
                self._update_decision_stats(result)
                logger.info(f"⚙️ EPL決策完成: {candidate.id} - {EPLDecision.IGNORE_SIGNAL.value}")
                return result
            
            # 檢查當前持倉狀況
            current_position = self.current_positions.get(candidate.symbol)
            
            decision = None
            execution_params = {}
            risk_management = {}
            
            if current_position:
                # 有持倉的情況 - 評估替換或加強
                
                # 根據關聯分析結果決定策略
                if pre_eval_result.correlation_result == CorrelationAnalysisResult.REPLACE_CANDIDATE:
                    # 評估替換
                    should_replace, replace_reasons, replace_params = await self.replacement_engine.evaluate_replacement(
                        candidate, current_position
                    )
                    
                    all_reasoning.extend([f"[替換評估] {reason}" for reason in replace_reasons])
                    
                    if should_replace:
                        decision = EPLDecision.REPLACE_POSITION
                        execution_params = replace_params
                        risk_management = await self._calculate_replacement_risk(candidate, current_position)
                    
                elif pre_eval_result.correlation_result == CorrelationAnalysisResult.STRENGTHEN_CANDIDATE:
                    # 評估加強
                    should_strengthen, strengthen_reasons, strengthen_params = await self.strengthening_engine.evaluate_strengthening(
                        candidate, current_position
                    )
                    
                    all_reasoning.extend([f"[加強評估] {reason}" for reason in strengthen_reasons])
                    
                    if should_strengthen:
                        decision = EPLDecision.STRENGTHEN_POSITION
                        execution_params = strengthen_params
                        risk_management = await self._calculate_strengthening_risk(candidate, current_position)
                
                # 如果以上都不適用，視為獨立新單處理
                if not decision:
                    all_reasoning.append("[決策] 持倉評估不通過，視為獨立機會")
                    # 繼續到新單評估邏輯
            
            if not decision:
                # 無持倉或持倉評估不通過 - 評估新單
                should_create, new_reasons, new_params = await self.new_position_engine.evaluate_new_position(
                    candidate, self.current_positions
                )
                
                all_reasoning.extend([f"[新單評估] {reason}" for reason in new_reasons])
                
                if should_create:
                    decision = EPLDecision.CREATE_NEW_POSITION
                    execution_params = new_params
                    risk_management = await self._calculate_new_position_risk(candidate)
                else:
                    # 所有評估都不通過，忽略信號
                    decision = EPLDecision.IGNORE_SIGNAL
                    execution_params = {}
                    risk_management = {}
                    all_reasoning.append("[決策] 所有評估均不通過，忽略信號")
            
            # 分類優先級
            priority, priority_reasons = self.priority_classifier.classify_priority(candidate, decision)
            all_reasoning.extend([f"[優先級] {reason}" for reason in priority_reasons])
            
            # 建立績效追蹤信息
            performance_tracking = self._create_performance_tracking(candidate, decision, execution_params)
            
            # 建立決策結果
            result = EPLDecisionResult(
                decision=decision,
                priority=priority,
                candidate=candidate,
                reasoning=all_reasoning,
                execution_params=execution_params,
                risk_management=risk_management,
                performance_tracking=performance_tracking,
                notification_config=self._get_notification_config(decision, priority),
                timestamp=datetime.now()
            )
            
            # 更新持倉狀態 (模擬)
            await self._update_position_status(result)
            
            # 更新統計
            self._update_decision_stats(result)
            
            logger.info(f"⚙️ EPL決策完成: {candidate.id} - {decision.value} ({priority.value})")
            return result
            
        except Exception as e:
            logger.error(f"❌ EPL決策失敗: {e}")
            all_reasoning.append(f"決策錯誤: {e}")
            
            # 錯誤時返回忽略決策
            return EPLDecisionResult(
                decision=EPLDecision.IGNORE_SIGNAL,
                priority=SignalPriority.LOW,
                candidate=candidate,
                reasoning=all_reasoning,
                execution_params={},
                risk_management={},
                performance_tracking={"error": str(e)},
                notification_config={},
                timestamp=datetime.now()
            )
    
    async def _calculate_replacement_risk(self, candidate: SignalCandidate, position: PositionInfo) -> Dict[str, Any]:
        """計算替換風險"""
        return {
            "risk_type": "position_replacement",
            "current_position_risk": abs(position.unrealized_pnl),
            "new_signal_risk": candidate.market_environment.volatility * 1000,
            "transition_risk": "market_impact_minimal",
            "max_drawdown_estimate": 0.05  # 5%
        }
    
    async def _calculate_strengthening_risk(self, candidate: SignalCandidate, position: PositionInfo) -> Dict[str, Any]:
        """計算加強風險"""
        return {
            "risk_type": "position_strengthening",
            "concentration_risk": position.size / 1000,  # 簡化
            "additional_risk": candidate.market_environment.volatility * 500,
            "portfolio_impact": "moderate_increase",
            "max_additional_exposure": position.size * 0.5
        }
    
    async def _calculate_new_position_risk(self, candidate: SignalCandidate) -> Dict[str, Any]:
        """計算新單風險"""
        return {
            "risk_type": "new_position",
            "initial_risk": candidate.market_environment.volatility * 1000,
            "liquidity_risk": 1.0 - candidate.market_environment.liquidity_score,
            "market_impact": "minimal",
            "max_loss_estimate": 0.03  # 3%
        }
    
    def _create_performance_tracking(self, candidate: SignalCandidate, decision: EPLDecision, 
                                   execution_params: Dict[str, Any]) -> Dict[str, Any]:
        """建立績效追蹤信息"""
        return {
            "tracking_id": f"{candidate.id}_{decision.name}",
            "signal_metadata": {
                "source": candidate.source.value,
                "strength": candidate.signal_strength,
                "confidence": candidate.confidence,
                "market_conditions": asdict(candidate.market_environment)
            },
            "decision_metadata": {
                "decision_type": decision.value,
                "execution_params": execution_params,
                "decision_timestamp": datetime.now()
            },
            "tracking_metrics": {
                "entry_conditions": asdict(candidate.technical_snapshot),
                "expected_performance": self._estimate_performance(candidate, decision),
                "risk_metrics": candidate.market_environment.volatility
            }
        }
    
    def _estimate_performance(self, candidate: SignalCandidate, decision: EPLDecision) -> Dict[str, float]:
        """估算預期表現"""
        base_return = candidate.signal_strength / 100 * 0.05  # 簡化估算
        
        if decision == EPLDecision.REPLACE_POSITION:
            expected_return = base_return * 1.2  # 替換通常有更高期望
        elif decision == EPLDecision.STRENGTHEN_POSITION:
            expected_return = base_return * 1.1  # 加強有適度提升
        else:
            expected_return = base_return
        
        return {
            "expected_return": expected_return,
            "expected_volatility": candidate.market_environment.volatility,
            "confidence_interval": candidate.confidence
        }
    
    def _get_notification_config(self, decision: EPLDecision, priority: SignalPriority) -> Dict[str, Any]:
        """獲取通知配置"""
        config = {
            "email_enabled": False,
            "websocket_enabled": True,
            "frontend_display": True,
            "urgency_level": "low"
        }
        
        if priority == SignalPriority.CRITICAL:
            config.update({
                "email_enabled": True,
                "email_delay": 0,  # 即時
                "websocket_enabled": True,
                "frontend_alert": True,
                "urgency_level": "critical"
            })
        elif priority == SignalPriority.HIGH:
            config.update({
                "email_enabled": True,
                "email_delay": 300,  # 5分鐘延遲
                "websocket_enabled": True,
                "frontend_highlight": True,
                "urgency_level": "high"
            })
        elif priority == SignalPriority.MEDIUM:
            config.update({
                "email_enabled": False,
                "websocket_enabled": True,
                "frontend_display": True,
                "urgency_level": "medium"
            })
        
        # 忽略信號不發送通知
        if decision == EPLDecision.IGNORE_SIGNAL:
            config.update({
                "email_enabled": False,
                "websocket_enabled": False,
                "frontend_display": False,
                "urgency_level": "none"
            })
        
        return config
    
    async def _update_position_status(self, result: EPLDecisionResult):
        """更新持倉狀態 (模擬)"""
        symbol = result.candidate.symbol
        
        if result.decision == EPLDecision.REPLACE_POSITION:
            # 替換持倉
            if symbol in self.current_positions:
                del self.current_positions[symbol]
            
            # 創建新持倉
            new_position = PositionInfo(
                symbol=symbol,
                direction=result.candidate.direction,
                size=result.execution_params.get("new_position_size", 1000),
                entry_price=50000,  # 簡化假設
                current_signal=result.candidate,
                stop_loss=None,
                take_profit=None,
                unrealized_pnl=0.0,
                entry_timestamp=datetime.now()
            )
            self.current_positions[symbol] = new_position
            
        elif result.decision == EPLDecision.STRENGTHEN_POSITION:
            # 加強持倉
            if symbol in self.current_positions:
                position = self.current_positions[symbol]
                additional_size = result.execution_params.get("additional_size", 0)
                position.size += additional_size
                position.current_signal = result.candidate  # 更新信號
                
        elif result.decision == EPLDecision.CREATE_NEW_POSITION:
            # 創建新持倉
            new_position = PositionInfo(
                symbol=symbol,
                direction=result.candidate.direction,
                size=result.execution_params.get("position_size", 1000),
                entry_price=50000,  # 簡化假設
                current_signal=result.candidate,
                stop_loss=result.execution_params.get("stop_loss"),
                take_profit=result.execution_params.get("take_profit"),
                unrealized_pnl=0.0,
                entry_timestamp=datetime.now()
            )
            self.current_positions[symbol] = new_position
    
    def _update_decision_stats(self, result: EPLDecisionResult):
        """更新決策統計"""
        self.decision_stats["total_processed"] += 1
        self.decision_stats["decisions"][result.decision] += 1
        self.decision_stats["priorities"][result.priority] += 1
    
    def get_decision_stats(self) -> Dict[str, Any]:
        """獲取決策統計"""
        stats = self.decision_stats.copy()
        if stats["total_processed"] > 0:
            # 計算比例
            stats["decision_rates"] = {
                decision.name: count / stats["total_processed"] * 100
                for decision, count in stats["decisions"].items()
            }
            stats["priority_rates"] = {
                priority.name: count / stats["total_processed"] * 100
                for priority, count in stats["priorities"].items()
            }
        return stats
    
    def get_current_positions(self) -> Dict[str, Dict[str, Any]]:
        """獲取當前持倉概況"""
        return {
            symbol: {
                "direction": pos.direction,
                "size": pos.size,
                "entry_price": pos.entry_price,
                "unrealized_pnl": pos.unrealized_pnl,
                "signal_source": pos.current_signal.source.value,
                "signal_strength": pos.current_signal.signal_strength,
                "entry_time": pos.entry_timestamp.isoformat()
            }
            for symbol, pos in self.current_positions.items()
        }

# 全局執行決策層實例
execution_policy_layer = ExecutionPolicyLayer()
