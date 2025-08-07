"""
🎯 Phase4 EPL Decision History Tracking
======================================

EPL決策歷史追蹤實現 - 基於配置驅動的決策過程記錄與分析
與 epl_decision_history_tracking_config.json 配置文件對應
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class EPLDecisionType(Enum):
    """EPL決策類型"""
    REPLACE_POSITION = "REPLACE_POSITION"
    STRENGTHEN_POSITION = "STRENGTHEN_POSITION"
    CREATE_NEW_POSITION = "CREATE_NEW_POSITION"
    IGNORE_SIGNAL = "IGNORE_SIGNAL"

class SignalPriority(Enum):
    """信號優先級"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class EPLDecisionRecord:
    """EPL決策記錄"""
    decision_id: str
    timestamp: datetime
    symbol: str
    signal_priority: SignalPriority
    decision_type: EPLDecisionType
    confidence_score: float
    risk_assessment: Dict[str, float]
    position_context: Dict[str, Any]
    execution_details: Dict[str, Any]
    outcome_tracking: Optional[Dict[str, Any]] = None

@dataclass
class DecisionOutcome:
    """決策結果追蹤"""
    decision_id: str
    execution_success: bool
    performance_metrics: Dict[str, float]
    actual_vs_expected: Dict[str, float]
    lessons_learned: List[str]
    timestamp: datetime

class EPLDecisionHistoryTracker:
    """EPL決策歷史追蹤系統"""
    
    def __init__(self):
        # 載入配置文件
        self.config = self._load_config()
        
        # 決策歷史存儲
        self.decision_history: deque = deque(maxlen=50000)  # 保留最近50000個決策
        self.outcome_history: Dict[str, DecisionOutcome] = {}
        
        # 統計數據
        self.decision_type_stats: Dict[str, int] = defaultdict(int)
        self.priority_stats: Dict[str, int] = defaultdict(int)
        self.success_rates: Dict[str, List[bool]] = defaultdict(list)
        
        # 性能追蹤
        self.tracking_enabled = True
        self.last_update = datetime.now()
        
        # 初始化追蹤系統
        self._initialize_tracking()
        
    def _load_config(self) -> Dict[str, Any]:
        """載入配置文件"""
        try:
            config_path = Path(__file__).parent / "epl_decision_history_tracking_config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入EPL追蹤配置失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            "PHASE4_EPL_DECISION_HISTORY_TRACKING": {
                "decision_tracking": {
                    "track_all_decisions": True,
                    "retention_period_days": 30,
                    "outcome_follow_up_hours": 24
                },
                "performance_analysis": {
                    "success_rate_calculation": True,
                    "confidence_correlation_analysis": True,
                    "decision_pattern_recognition": True
                }
            }
        }
    
    def _initialize_tracking(self):
        """初始化追蹤系統"""
        logger.info("初始化EPL決策歷史追蹤系統")
        
        # 清理過舊的記錄
        self._cleanup_old_records()
        
        # 設置追蹤參數
        config = self.config.get("PHASE4_EPL_DECISION_HISTORY_TRACKING", {})
        tracking_config = config.get("decision_tracking", {})
        
        self.track_all_decisions = tracking_config.get("track_all_decisions", True)
        self.retention_days = tracking_config.get("retention_period_days", 30)
        self.outcome_follow_up_hours = tracking_config.get("outcome_follow_up_hours", 24)
        
    def _cleanup_old_records(self):
        """清理過舊的記錄"""
        cutoff_time = datetime.now() - timedelta(days=self.retention_days)
        
        # 清理決策歷史
        self.decision_history = deque(
            [record for record in self.decision_history 
             if record.timestamp > cutoff_time],
            maxlen=50000
        )
        
        # 清理結果歷史
        old_decision_ids = [
            decision_id for decision_id, outcome in self.outcome_history.items()
            if outcome.timestamp < cutoff_time
        ]
        for decision_id in old_decision_ids:
            del self.outcome_history[decision_id]
    
    async def record_epl_decision(self, decision_data: Dict[str, Any]) -> str:
        """記錄EPL決策"""
        try:
            # 生成決策ID
            decision_id = f"epl_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{decision_data.get('symbol', 'UNK')}"
            
            # 創建決策記錄
            decision_record = EPLDecisionRecord(
                decision_id=decision_id,
                timestamp=datetime.fromisoformat(decision_data.get('timestamp', datetime.now().isoformat())),
                symbol=decision_data.get('symbol', 'UNKNOWN'),
                signal_priority=SignalPriority(decision_data.get('priority', 'MEDIUM')),
                decision_type=EPLDecisionType(decision_data.get('decision_type', 'IGNORE_SIGNAL')),
                confidence_score=float(decision_data.get('confidence_score', 0.5)),
                risk_assessment=decision_data.get('risk_assessment', {}),
                position_context=decision_data.get('position_context', {}),
                execution_details=decision_data.get('execution_details', {})
            )
            
            # 添加到歷史記錄
            self.decision_history.append(decision_record)
            
            # 更新統計
            self._update_decision_statistics(decision_record)
            
            self.last_update = datetime.now()
            
            logger.info(f"記錄EPL決策: {decision_id}, 類型: {decision_record.decision_type.value}")
            return decision_id
            
        except Exception as e:
            logger.error(f"記錄EPL決策失敗: {e}")
            return ""
    
    def _update_decision_statistics(self, record: EPLDecisionRecord):
        """更新決策統計"""
        self.decision_type_stats[record.decision_type.value] += 1
        self.priority_stats[record.signal_priority.value] += 1
    
    async def record_decision_outcome(self, decision_id: str, outcome_data: Dict[str, Any]) -> bool:
        """記錄決策結果"""
        try:
            outcome = DecisionOutcome(
                decision_id=decision_id,
                execution_success=outcome_data.get('execution_success', False),
                performance_metrics=outcome_data.get('performance_metrics', {}),
                actual_vs_expected=outcome_data.get('actual_vs_expected', {}),
                lessons_learned=outcome_data.get('lessons_learned', []),
                timestamp=datetime.now()
            )
            
            self.outcome_history[decision_id] = outcome
            
            # 更新成功率統計
            decision_record = self._find_decision_by_id(decision_id)
            if decision_record:
                decision_type = decision_record.decision_type.value
                self.success_rates[decision_type].append(outcome.execution_success)
                
                # 限制成功率歷史記錄長度
                if len(self.success_rates[decision_type]) > 1000:
                    self.success_rates[decision_type].pop(0)
            
            logger.info(f"記錄決策結果: {decision_id}, 成功: {outcome.execution_success}")
            return True
            
        except Exception as e:
            logger.error(f"記錄決策結果失敗: {e}")
            return False
    
    def _find_decision_by_id(self, decision_id: str) -> Optional[EPLDecisionRecord]:
        """根據ID查找決策記錄"""
        for record in self.decision_history:
            if record.decision_id == decision_id:
                return record
        return None
    
    async def get_comprehensive_decision_analysis(self) -> Dict[str, Any]:
        """獲取綜合決策分析"""
        try:
            current_time = datetime.now()
            
            if not self.decision_history:
                return self._get_empty_analysis()
            
            # 基本統計
            total_decisions = len(self.decision_history)
            decisions_with_outcomes = len(self.outcome_history)
            
            # 決策類型分析
            decision_type_analysis = self._analyze_decision_types()
            
            # 優先級分析
            priority_analysis = self._analyze_priority_patterns()
            
            # 成功率分析
            success_rate_analysis = self._analyze_success_rates()
            
            # 置信度相關性分析
            confidence_analysis = self._analyze_confidence_correlation()
            
            # 時間模式分析
            temporal_analysis = self._analyze_temporal_patterns()
            
            # 性能指標
            performance_metrics = self._calculate_performance_metrics()
            
            # 風險評估分析
            risk_analysis = self._analyze_risk_patterns()
            
            return {
                "analysis_metadata": {
                    "generated_at": current_time.isoformat(),
                    "total_decisions_tracked": total_decisions,
                    "decisions_with_outcomes": decisions_with_outcomes,
                    "tracking_period": {
                        "start": min(r.timestamp for r in self.decision_history).isoformat(),
                        "end": max(r.timestamp for r in self.decision_history).isoformat()
                    },
                    "last_update": self.last_update.isoformat()
                },
                "decision_type_distribution": decision_type_analysis,
                "priority_level_insights": priority_analysis,
                "success_rate_analysis": success_rate_analysis,
                "confidence_correlation_analysis": confidence_analysis,
                "temporal_decision_patterns": temporal_analysis,
                "performance_benchmarks": performance_metrics,
                "risk_assessment_insights": risk_analysis,
                "decision_quality_trends": self._analyze_decision_quality_trends(),
                "recommendations": self._generate_recommendations()
            }
            
        except Exception as e:
            logger.error(f"生成綜合決策分析失敗: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def _get_empty_analysis(self) -> Dict[str, Any]:
        """獲取空分析數據"""
        return {
            "analysis_metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_decisions_tracked": 0,
                "status": "no_data"
            },
            "message": "沒有足夠的決策數據進行分析"
        }
    
    def _analyze_decision_types(self) -> Dict[str, Any]:
        """分析決策類型"""
        type_distribution = dict(self.decision_type_stats)
        total = sum(type_distribution.values())
        
        if total == 0:
            return {"distribution": {}, "trends": []}
        
        # 計算百分比
        type_percentages = {
            decision_type: (count / total) * 100
            for decision_type, count in type_distribution.items()
        }
        
        # 分析趨勢（最近24小時 vs 之前）
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_decisions = [r for r in self.decision_history if r.timestamp > cutoff_time]
        older_decisions = [r for r in self.decision_history if r.timestamp <= cutoff_time]
        
        recent_type_stats = defaultdict(int)
        older_type_stats = defaultdict(int)
        
        for record in recent_decisions:
            recent_type_stats[record.decision_type.value] += 1
        
        for record in older_decisions:
            older_type_stats[record.decision_type.value] += 1
        
        # 計算趨勢變化
        trend_changes = {}
        for decision_type in type_distribution.keys():
            recent_ratio = recent_type_stats[decision_type] / max(len(recent_decisions), 1)
            older_ratio = older_type_stats[decision_type] / max(len(older_decisions), 1)
            
            trend_changes[decision_type] = {
                "recent_ratio": recent_ratio,
                "previous_ratio": older_ratio,
                "change_percentage": ((recent_ratio - older_ratio) / max(older_ratio, 0.01)) * 100
            }
        
        return {
            "distribution": type_distribution,
            "percentages": type_percentages,
            "trend_analysis": trend_changes,
            "dominant_decision_type": max(type_distribution.items(), key=lambda x: x[1])[0] if type_distribution else None
        }
    
    def _analyze_priority_patterns(self) -> Dict[str, Any]:
        """分析優先級模式"""
        priority_distribution = dict(self.priority_stats)
        
        # 按優先級分析決策類型
        priority_decision_matrix = defaultdict(lambda: defaultdict(int))
        
        for record in self.decision_history:
            priority_decision_matrix[record.signal_priority.value][record.decision_type.value] += 1
        
        # 計算各優先級的處理效率
        priority_efficiency = {}
        for priority, decisions in priority_decision_matrix.items():
            total = sum(decisions.values())
            efficiency_score = 0
            
            if total > 0:
                # 高效決策權重: CREATE_NEW_POSITION=1.0, STRENGTHEN=0.8, REPLACE=0.6, IGNORE=0.2
                weights = {
                    "CREATE_NEW_POSITION": 1.0,
                    "STRENGTHEN_POSITION": 0.8,
                    "REPLACE_POSITION": 0.6,
                    "IGNORE_SIGNAL": 0.2
                }
                
                weighted_sum = sum(decisions[dt] * weights.get(dt, 0.5) for dt in decisions)
                efficiency_score = weighted_sum / total
            
            priority_efficiency[priority] = efficiency_score
        
        return {
            "distribution": priority_distribution,
            "decision_matrix": dict(priority_decision_matrix),
            "processing_efficiency": priority_efficiency,
            "priority_ranking": sorted(priority_efficiency.items(), key=lambda x: x[1], reverse=True)
        }
    
    def _analyze_success_rates(self) -> Dict[str, Any]:
        """分析成功率"""
        success_rate_summary = {}
        
        for decision_type, successes in self.success_rates.items():
            if successes:
                success_rate = sum(successes) / len(successes)
                recent_successes = successes[-10:] if len(successes) >= 10 else successes
                recent_success_rate = sum(recent_successes) / len(recent_successes)
                
                success_rate_summary[decision_type] = {
                    "overall_success_rate": success_rate,
                    "recent_success_rate": recent_success_rate,
                    "total_attempts": len(successes),
                    "trend": "improving" if recent_success_rate > success_rate else "declining" if recent_success_rate < success_rate else "stable"
                }
        
        # 計算整體成功率
        all_successes = []
        for successes in self.success_rates.values():
            all_successes.extend(successes)
        
        overall_success_rate = sum(all_successes) / len(all_successes) if all_successes else 0
        
        return {
            "by_decision_type": success_rate_summary,
            "overall_success_rate": overall_success_rate,
            "total_tracked_outcomes": len(all_successes),
            "best_performing_decision": max(success_rate_summary.items(), key=lambda x: x[1]["overall_success_rate"])[0] if success_rate_summary else None
        }
    
    def _analyze_confidence_correlation(self) -> Dict[str, Any]:
        """分析置信度相關性"""
        decisions_with_outcomes = []
        
        for record in self.decision_history:
            if record.decision_id in self.outcome_history:
                outcome = self.outcome_history[record.decision_id]
                decisions_with_outcomes.append({
                    "confidence": record.confidence_score,
                    "success": outcome.execution_success,
                    "decision_type": record.decision_type.value
                })
        
        if not decisions_with_outcomes:
            return {"correlation_analysis": "insufficient_data"}
        
        # 按置信度區間分析成功率
        confidence_bins = {
            "low_confidence": [d for d in decisions_with_outcomes if d["confidence"] < 0.5],
            "medium_confidence": [d for d in decisions_with_outcomes if 0.5 <= d["confidence"] < 0.8],
            "high_confidence": [d for d in decisions_with_outcomes if d["confidence"] >= 0.8]
        }
        
        bin_analysis = {}
        for bin_name, decisions in confidence_bins.items():
            if decisions:
                success_rate = sum(d["success"] for d in decisions) / len(decisions)
                avg_confidence = statistics.mean(d["confidence"] for d in decisions)
                
                bin_analysis[bin_name] = {
                    "count": len(decisions),
                    "success_rate": success_rate,
                    "average_confidence": avg_confidence
                }
        
        # 計算相關性係數（簡化版）
        confidences = [d["confidence"] for d in decisions_with_outcomes]
        successes = [1 if d["success"] else 0 for d in decisions_with_outcomes]
        
        correlation_coefficient = 0
        if len(confidences) > 1:
            try:
                mean_conf = statistics.mean(confidences)
                mean_succ = statistics.mean(successes)
                
                numerator = sum((c - mean_conf) * (s - mean_succ) for c, s in zip(confidences, successes))
                denominator = (sum((c - mean_conf) ** 2 for c in confidences) * sum((s - mean_succ) ** 2 for s in successes)) ** 0.5
                
                if denominator > 0:
                    correlation_coefficient = numerator / denominator
            except:
                pass
        
        return {
            "confidence_bin_analysis": bin_analysis,
            "correlation_coefficient": correlation_coefficient,
            "correlation_strength": self._interpret_correlation(correlation_coefficient),
            "total_analyzed": len(decisions_with_outcomes)
        }
    
    def _interpret_correlation(self, coefficient: float) -> str:
        """解釋相關性係數"""
        abs_coeff = abs(coefficient)
        if abs_coeff >= 0.8:
            return "very_strong"
        elif abs_coeff >= 0.6:
            return "strong"
        elif abs_coeff >= 0.4:
            return "moderate"
        elif abs_coeff >= 0.2:
            return "weak"
        else:
            return "very_weak"
    
    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
        """分析時間模式"""
        # 按小時分析決策模式
        hourly_patterns = defaultdict(lambda: defaultdict(int))
        
        for record in self.decision_history:
            hour = record.timestamp.hour
            hourly_patterns[hour][record.decision_type.value] += 1
        
        # 找出最活躍的時段
        hourly_activity = {hour: sum(decisions.values()) for hour, decisions in hourly_patterns.items()}
        peak_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # 按工作日分析
        weekday_patterns = defaultdict(lambda: defaultdict(int))
        
        for record in self.decision_history:
            weekday = record.timestamp.weekday()  # 0=Monday
            weekday_patterns[weekday][record.decision_type.value] += 1
        
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_analysis = {}
        
        for day_num, decisions in weekday_patterns.items():
            day_name = weekday_names[day_num]
            total_decisions = sum(decisions.values())
            
            weekday_analysis[day_name] = {
                "total_decisions": total_decisions,
                "decision_distribution": dict(decisions),
                "activity_score": total_decisions / max(sum(hourly_activity.values()), 1)
            }
        
        return {
            "hourly_patterns": dict(hourly_patterns),
            "peak_activity_hours": [f"{hour:02d}:00" for hour, _ in peak_hours],
            "weekday_analysis": weekday_analysis,
            "busiest_day": max(weekday_analysis.items(), key=lambda x: x[1]["total_decisions"])[0] if weekday_analysis else None
        }
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """計算性能指標"""
        if not self.decision_history:
            return {}
        
        # 決策延遲分析
        decision_latencies = []
        for record in self.decision_history:
            # 模擬決策延遲（實際應該從執行詳情中獲取）
            latency = record.execution_details.get('decision_latency', 0)
            if latency > 0:
                decision_latencies.append(latency)
        
        # 置信度分析
        confidence_scores = [record.confidence_score for record in self.decision_history]
        
        # 風險評估分析
        risk_scores = []
        for record in self.decision_history:
            overall_risk = record.risk_assessment.get('overall_risk', 0.5)
            risk_scores.append(overall_risk)
        
        return {
            "decision_latency_metrics": {
                "average_latency": statistics.mean(decision_latencies) if decision_latencies else 0,
                "median_latency": statistics.median(decision_latencies) if decision_latencies else 0,
                "max_latency": max(decision_latencies) if decision_latencies else 0
            },
            "confidence_metrics": {
                "average_confidence": statistics.mean(confidence_scores),
                "confidence_distribution": self._create_confidence_distribution(confidence_scores),
                "low_confidence_rate": len([c for c in confidence_scores if c < 0.5]) / len(confidence_scores)
            },
            "risk_metrics": {
                "average_risk_score": statistics.mean(risk_scores),
                "high_risk_decisions": len([r for r in risk_scores if r > 0.7]) / len(risk_scores),
                "risk_distribution": self._create_risk_distribution(risk_scores)
            },
            "throughput_metrics": {
                "decisions_per_hour": len(self.decision_history) / max((datetime.now() - min(r.timestamp for r in self.decision_history)).total_seconds() / 3600, 1),
                "total_decisions": len(self.decision_history),
                "decisions_with_outcomes": len(self.outcome_history)
            }
        }
    
    def _create_confidence_distribution(self, scores: List[float]) -> Dict[str, int]:
        """創建置信度分佈"""
        distribution = {"0.0-0.2": 0, "0.2-0.4": 0, "0.4-0.6": 0, "0.6-0.8": 0, "0.8-1.0": 0}
        
        for score in scores:
            if score < 0.2:
                distribution["0.0-0.2"] += 1
            elif score < 0.4:
                distribution["0.2-0.4"] += 1
            elif score < 0.6:
                distribution["0.4-0.6"] += 1
            elif score < 0.8:
                distribution["0.6-0.8"] += 1
            else:
                distribution["0.8-1.0"] += 1
        
        return distribution
    
    def _create_risk_distribution(self, scores: List[float]) -> Dict[str, int]:
        """創建風險分佈"""
        distribution = {"Low": 0, "Medium": 0, "High": 0}
        
        for score in scores:
            if score < 0.3:
                distribution["Low"] += 1
            elif score < 0.7:
                distribution["Medium"] += 1
            else:
                distribution["High"] += 1
        
        return distribution
    
    def _analyze_risk_patterns(self) -> Dict[str, Any]:
        """分析風險模式"""
        risk_by_decision_type = defaultdict(list)
        risk_by_priority = defaultdict(list)
        
        for record in self.decision_history:
            overall_risk = record.risk_assessment.get('overall_risk', 0.5)
            risk_by_decision_type[record.decision_type.value].append(overall_risk)
            risk_by_priority[record.signal_priority.value].append(overall_risk)
        
        # 計算各決策類型的平均風險
        risk_by_type_summary = {}
        for decision_type, risks in risk_by_decision_type.items():
            if risks:
                risk_by_type_summary[decision_type] = {
                    "average_risk": statistics.mean(risks),
                    "max_risk": max(risks),
                    "risk_variance": statistics.variance(risks) if len(risks) > 1 else 0
                }
        
        # 計算各優先級的平均風險
        risk_by_priority_summary = {}
        for priority, risks in risk_by_priority.items():
            if risks:
                risk_by_priority_summary[priority] = {
                    "average_risk": statistics.mean(risks),
                    "max_risk": max(risks),
                    "risk_variance": statistics.variance(risks) if len(risks) > 1 else 0
                }
        
        return {
            "risk_by_decision_type": risk_by_type_summary,
            "risk_by_priority": risk_by_priority_summary,
            "riskiest_decision_type": max(risk_by_type_summary.items(), key=lambda x: x[1]["average_risk"])[0] if risk_by_type_summary else None,
            "safest_decision_type": min(risk_by_type_summary.items(), key=lambda x: x[1]["average_risk"])[0] if risk_by_type_summary else None
        }
    
    def _analyze_decision_quality_trends(self) -> Dict[str, Any]:
        """分析決策質量趨勢"""
        # 按時間順序分析決策質量
        sorted_decisions = sorted(self.decision_history, key=lambda x: x.timestamp)
        
        if len(sorted_decisions) < 10:
            return {"trend_analysis": "insufficient_data"}
        
        # 將決策分成時間段
        total_decisions = len(sorted_decisions)
        segment_size = max(total_decisions // 5, 10)  # 分成5段，每段至少10個決策
        
        segments = []
        for i in range(0, total_decisions, segment_size):
            segment = sorted_decisions[i:i + segment_size]
            if len(segment) >= 5:  # 確保每段有足夠的數據
                segments.append(segment)
        
        trend_data = []
        for i, segment in enumerate(segments):
            avg_confidence = statistics.mean(record.confidence_score for record in segment)
            avg_risk = statistics.mean(record.risk_assessment.get('overall_risk', 0.5) for record in segment)
            
            # 計算該段的成功率
            segment_outcomes = [
                self.outcome_history[record.decision_id].execution_success
                for record in segment
                if record.decision_id in self.outcome_history
            ]
            
            success_rate = statistics.mean(segment_outcomes) if segment_outcomes else None
            
            trend_data.append({
                "segment": i + 1,
                "time_range": {
                    "start": segment[0].timestamp.isoformat(),
                    "end": segment[-1].timestamp.isoformat()
                },
                "average_confidence": avg_confidence,
                "average_risk": avg_risk,
                "success_rate": success_rate,
                "decision_count": len(segment)
            })
        
        return {
            "trend_segments": trend_data,
            "quality_improvement": self._calculate_quality_improvement(trend_data),
            "trend_summary": self._summarize_trends(trend_data)
        }
    
    def _calculate_quality_improvement(self, trend_data: List[Dict]) -> Dict[str, Any]:
        """計算質量改善"""
        if len(trend_data) < 2:
            return {"improvement_analysis": "insufficient_data"}
        
        first_segment = trend_data[0]
        last_segment = trend_data[-1]
        
        confidence_change = last_segment["average_confidence"] - first_segment["average_confidence"]
        risk_change = last_segment["average_risk"] - first_segment["average_risk"]
        
        success_rate_change = None
        if first_segment["success_rate"] is not None and last_segment["success_rate"] is not None:
            success_rate_change = last_segment["success_rate"] - first_segment["success_rate"]
        
        return {
            "confidence_improvement": confidence_change,
            "risk_reduction": -risk_change,  # 負值表示風險降低
            "success_rate_improvement": success_rate_change,
            "overall_quality_trend": "improving" if confidence_change > 0 and risk_change < 0 else "declining" if confidence_change < 0 and risk_change > 0 else "mixed"
        }
    
    def _summarize_trends(self, trend_data: List[Dict]) -> str:
        """總結趨勢"""
        if len(trend_data) < 2:
            return "數據不足以分析趨勢"
        
        # 分析置信度趨勢
        confidence_values = [segment["average_confidence"] for segment in trend_data]
        confidence_trend = "上升" if confidence_values[-1] > confidence_values[0] else "下降"
        
        # 分析風險趨勢
        risk_values = [segment["average_risk"] for segment in trend_data]
        risk_trend = "上升" if risk_values[-1] > risk_values[0] else "下降"
        
        return f"決策置信度呈現{confidence_trend}趨勢，風險水平{risk_trend}。"
    
    def _generate_recommendations(self) -> List[str]:
        """生成建議"""
        recommendations = []
        
        # 基於成功率分析生成建議
        if self.success_rates:
            best_performing = max(self.success_rates.items(), key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0)
            worst_performing = min(self.success_rates.items(), key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 1)
            
            best_rate = sum(best_performing[1]) / len(best_performing[1]) if best_performing[1] else 0
            worst_rate = sum(worst_performing[1]) / len(worst_performing[1]) if worst_performing[1] else 0
            
            if best_rate > 0.8:
                recommendations.append(f"決策類型 {best_performing[0]} 表現優異（成功率 {best_rate:.1%}），建議增加此類決策的使用頻率")
            
            if worst_rate < 0.6:
                recommendations.append(f"決策類型 {worst_performing[0]} 表現不佳（成功率 {worst_rate:.1%}），建議檢討決策標準")
        
        # 基於置信度分析生成建議
        if self.decision_history:
            avg_confidence = statistics.mean(record.confidence_score for record in self.decision_history)
            
            if avg_confidence < 0.6:
                recommendations.append("整體決策置信度偏低，建議優化信號質量篩選標準")
            elif avg_confidence > 0.8:
                recommendations.append("決策置信度表現良好，可考慮提高決策頻率")
        
        # 基於風險分析生成建議
        high_risk_decisions = len([
            record for record in self.decision_history
            if record.risk_assessment.get('overall_risk', 0.5) > 0.7
        ])
        
        if high_risk_decisions / len(self.decision_history) > 0.3:
            recommendations.append("高風險決策比例偏高，建議加強風險控制機制")
        
        return recommendations if recommendations else ["系統運行正常，暫無特殊建議"]
    
    async def get_recent_decisions(self, hours: int = 24) -> List[Dict[str, Any]]:
        """獲取最近的決策記錄"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_decisions = [
            record for record in self.decision_history
            if record.timestamp > cutoff_time
        ]
        
        return [
            {
                "decision_id": record.decision_id,
                "timestamp": record.timestamp.isoformat(),
                "symbol": record.symbol,
                "priority": record.signal_priority.value,
                "decision_type": record.decision_type.value,
                "confidence_score": record.confidence_score,
                "risk_assessment": record.risk_assessment,
                "has_outcome": record.decision_id in self.outcome_history
            }
            for record in sorted(recent_decisions, key=lambda x: x.timestamp, reverse=True)
        ]
    
    def get_decision_by_id(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """根據ID獲取決策詳情"""
        record = self._find_decision_by_id(decision_id)
        if not record:
            return None
        
        result = {
            "decision_record": asdict(record),
            "outcome": None
        }
        
        if decision_id in self.outcome_history:
            result["outcome"] = asdict(self.outcome_history[decision_id])
        
        return result

# 全局實例
epl_decision_tracker = EPLDecisionHistoryTracker()
