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
    timestamp: datetime
    success: bool  # 執行成功
    pnl: Optional[float] = None  # 損益
    risk_realized: Optional[float] = None  # 實際風險
    execution_quality: Optional[float] = None  # 執行品質
    performance_metrics: Optional[Dict[str, float]] = None  # 性能指標
    actual_vs_expected: Optional[Dict[str, float]] = None  # 實際vs預期
    lessons_learned: Optional[List[str]] = None  # 經驗教訓

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
                "system_metadata": {
                    "version": "2.1.0",
                    "description": "EPL Decision History Tracking - Default Configuration"
                },
                "decision_tracking": {
                    "track_all_decisions": True,
                    "retention_period_days": 30,
                    "outcome_follow_up_hours": 24
                },
                "decision_tracking_architecture": {
                    "decision_lifecycle_monitoring": {
                        "decision_creation": {"enabled": True},
                        "decision_execution_tracking": {"enabled": True},
                        "outcome_measurement": {"enabled": True}
                    },
                    "decision_type_analytics": {
                        "replacement_decision_tracking": {"enabled": True},
                        "strengthening_decision_tracking": {"enabled": True},
                        "new_position_decision_tracking": {"enabled": True},
                        "ignore_decision_tracking": {"enabled": True}
                    }
                },
                "learning_and_optimization": {
                    "pattern_recognition": {"enabled": True},
                    "adaptive_learning": {"enabled": True},
                    "feedback_integration": {"enabled": True}
                },
                "reporting_and_analytics": {
                    "real_time_dashboards": {"enabled": True},
                    "historical_analysis": {"enabled": True}
                },
                "data_storage_and_retrieval": {
                    "decision_data_storage": {
                        "raw_decision_data": {"retention_period": "5_years"},
                        "aggregated_analytics": {"retention_period": "10_years"}
                    }
                }
            }
        }
    
    def _initialize_tracking(self):
        """初始化追蹤系統"""
        logger.info("初始化EPL決策歷史追蹤系統")
        
        # 設置追蹤參數
        config = self.config.get("PHASE4_EPL_DECISION_HISTORY_TRACKING", {})
        tracking_config = config.get("decision_tracking", {})
        
        self.track_all_decisions = tracking_config.get("track_all_decisions", True)
        self.retention_days = tracking_config.get("retention_period_days", 30)
        self.outcome_follow_up_hours = tracking_config.get("outcome_follow_up_hours", 24)
        
        # 清理過舊的記錄
        self._cleanup_old_records()
        
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
                timestamp=datetime.now(),
                success=outcome_data.get('success', outcome_data.get('execution_success', False)),
                pnl=outcome_data.get('pnl'),
                risk_realized=outcome_data.get('risk_realized'),
                execution_quality=outcome_data.get('execution_quality'),
                performance_metrics=outcome_data.get('performance_metrics', {}),
                actual_vs_expected=outcome_data.get('actual_vs_expected', {}),
                lessons_learned=outcome_data.get('lessons_learned', [])
            )
            
            self.outcome_history[decision_id] = outcome
            
            # 更新成功率統計
            decision_record = self._find_decision_by_id(decision_id)
            if decision_record:
                decision_type = decision_record.decision_type.value
                self.success_rates[decision_type].append(outcome.success)
                
                # 限制成功率歷史記錄長度
                if len(self.success_rates[decision_type]) > 1000:
                    self.success_rates[decision_type].pop(0)
            
            logger.info(f"記錄決策結果: {decision_id}, 成功: {outcome.success}")
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
                    "success": outcome.success,
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
                self.outcome_history[record.decision_id].success
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
    
    async def update_decision_outcome(self, decision_id: str, outcome_data: Dict[str, Any]) -> bool:
        """更新決策結果 (別名方法)"""
        return await self.record_decision_outcome(decision_id, outcome_data)
    
    async def get_decisions_by_type(self, decision_type: str) -> List[Dict[str, Any]]:
        """按類型獲取決策"""
        try:
            decisions = [
                record for record in self.decision_history
                if record.decision_type.value == decision_type
            ]
            
            return [
                {
                    "decision_id": record.decision_id,
                    "timestamp": record.timestamp.isoformat(),
                    "symbol": record.symbol,
                    "priority": record.signal_priority.value,
                    "confidence_score": record.confidence_score,
                    "risk_assessment": record.risk_assessment,
                    "has_outcome": record.decision_id in self.outcome_history
                }
                for record in sorted(decisions, key=lambda x: x.timestamp, reverse=True)
            ]
            
        except Exception as e:
            logger.error(f"按類型獲取決策失敗: {e}")
            return []
    
    async def get_comprehensive_analytics(self) -> Dict[str, Any]:
        """獲取綜合分析 (別名方法)"""
        return await self.get_comprehensive_decision_analysis()
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """獲取性能指標"""
        try:
            if not self.decision_history:
                return {"message": "暫無決策數據"}
            
            # 基本統計
            total_decisions = len(self.decision_history)
            decisions_with_outcomes = len(self.outcome_history)
            
            # 計算成功率
            successful_outcomes = sum(
                1 for outcome in self.outcome_history.values()
                if outcome.success
            )
            
            success_rate = successful_outcomes / decisions_with_outcomes if decisions_with_outcomes > 0 else 0
            
            # 計算平均 PnL
            pnl_values = [
                outcome.pnl for outcome in self.outcome_history.values()
                if outcome.pnl is not None
            ]
            
            avg_pnl = statistics.mean(pnl_values) if pnl_values else 0
            
            # 風險指標
            risk_realizations = [
                outcome.risk_realized for outcome in self.outcome_history.values()
                if outcome.risk_realized is not None
            ]
            
            avg_risk_realized = statistics.mean(risk_realizations) if risk_realizations else 0
            
            return {
                "total_decisions": total_decisions,
                "decisions_with_outcomes": decisions_with_outcomes,
                "success_rate": success_rate,
                "average_pnl": avg_pnl,
                "average_risk_realized": avg_risk_realized,
                "completion_rate": decisions_with_outcomes / total_decisions if total_decisions > 0 else 0,
                "performance_summary": {
                    "profitable_decisions": successful_outcomes,
                    "unprofitable_decisions": decisions_with_outcomes - successful_outcomes,
                    "pending_decisions": total_decisions - decisions_with_outcomes
                }
            }
            
        except Exception as e:
            logger.error(f"獲取性能指標失敗: {e}")
            return {"error": str(e)}
    
    async def analyze_decision_patterns(self) -> Dict[str, Any]:
        """分析決策模式"""
        try:
            if not self.decision_history:
                return {"message": "暫無決策數據進行模式分析"}
            
            # 成功模式分析
            successful_decisions = [
                record for record in self.decision_history
                if record.decision_id in self.outcome_history and 
                self.outcome_history[record.decision_id].success
            ]
            
            # 失敗模式分析  
            failed_decisions = [
                record for record in self.decision_history
                if record.decision_id in self.outcome_history and 
                not self.outcome_history[record.decision_id].success
            ]
            
            return {
                "successful_patterns": {
                    "count": len(successful_decisions),
                    "avg_confidence": statistics.mean([d.confidence_score for d in successful_decisions]) if successful_decisions else 0,
                    "priority_distribution": self._analyze_priority_distribution(successful_decisions),
                    "decision_type_distribution": self._analyze_decision_type_distribution(successful_decisions)
                },
                "failure_patterns": {
                    "count": len(failed_decisions),
                    "avg_confidence": statistics.mean([d.confidence_score for d in failed_decisions]) if failed_decisions else 0,
                    "priority_distribution": self._analyze_priority_distribution(failed_decisions),
                    "decision_type_distribution": self._analyze_decision_type_distribution(failed_decisions)
                },
                "insights": self._generate_pattern_insights(successful_decisions, failed_decisions)
            }
            
        except Exception as e:
            logger.error(f"決策模式分析失敗: {e}")
            return {"error": str(e)}
    
    async def get_decision_timeline(self) -> List[Dict[str, Any]]:
        """獲取決策時間線"""
        try:
            timeline = []
            
            for record in sorted(self.decision_history, key=lambda x: x.timestamp):
                timeline_entry = {
                    "timestamp": record.timestamp.isoformat(),
                    "decision_id": record.decision_id,
                    "symbol": record.symbol,
                    "decision_type": record.decision_type.value,
                    "priority": record.signal_priority.value,
                    "confidence_score": record.confidence_score
                }
                
                # 添加結果信息（如果有）
                if record.decision_id in self.outcome_history:
                    outcome = self.outcome_history[record.decision_id]
                    timeline_entry["outcome"] = {
                        "success": outcome.success,
                        "pnl": outcome.pnl,
                        "outcome_timestamp": outcome.timestamp.isoformat()
                    }
                
                timeline.append(timeline_entry)
            
            return timeline
            
        except Exception as e:
            logger.error(f"獲取決策時間線失敗: {e}")
            return []
    
    async def get_risk_analytics(self) -> Dict[str, Any]:
        """獲取風險分析"""
        try:
            if not self.outcome_history:
                return {"message": "暫無結果數據進行風險分析"}
            
            # 風險實現分析
            risk_data = []
            return_data = []
            
            for outcome in self.outcome_history.values():
                if outcome.risk_realized is not None:
                    risk_data.append(outcome.risk_realized)
                if outcome.pnl is not None:
                    return_data.append(outcome.pnl)
            
            risk_analysis = {
                "risk_vs_return": {
                    "avg_risk_realized": statistics.mean(risk_data) if risk_data else 0,
                    "avg_return": statistics.mean(return_data) if return_data else 0,
                    "risk_return_ratio": abs(statistics.mean(return_data) / statistics.mean(risk_data)) if risk_data and statistics.mean(risk_data) != 0 else 0
                },
                "risk_realization": {
                    "total_outcomes": len(self.outcome_history),
                    "high_risk_outcomes": len([r for r in risk_data if r > 0.02]),
                    "low_risk_outcomes": len([r for r in risk_data if r <= 0.01]),
                    "risk_distribution": {
                        "low_risk": len([r for r in risk_data if r <= 0.01]),
                        "medium_risk": len([r for r in risk_data if 0.01 < r <= 0.02]),
                        "high_risk": len([r for r in risk_data if r > 0.02])
                    }
                }
            }
            
            return risk_analysis
            
        except Exception as e:
            logger.error(f"風險分析失敗: {e}")
            return {"error": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        try:
            return {
                "system_health": "healthy" if self.tracking_enabled else "disabled",
                "total_decisions": len(self.decision_history),
                "total_outcomes": len(self.outcome_history),
                "last_update": self.last_update.isoformat(),
                "memory_usage": f"{len(self.decision_history)} decisions in memory",
                "configuration": {
                    "retention_days": getattr(self, 'retention_days', 30),
                    "track_all_decisions": getattr(self, 'track_all_decisions', True),
                    "outcome_follow_up_hours": getattr(self, 'outcome_follow_up_hours', 24)
                },
                "recent_activity": {
                    "decisions_last_hour": len([
                        d for d in self.decision_history
                        if d.timestamp > datetime.now() - timedelta(hours=1)
                    ]),
                    "outcomes_last_hour": len([
                        o for o in self.outcome_history.values()
                        if o.timestamp > datetime.now() - timedelta(hours=1)
                    ])
                }
            }
            
        except Exception as e:
            logger.error(f"獲取系統狀態失敗: {e}")
            return {"error": str(e)}
    
    def _analyze_priority_distribution(self, decisions: List[EPLDecisionRecord]) -> Dict[str, int]:
        """分析優先級分佈"""
        distribution = defaultdict(int)
        for decision in decisions:
            distribution[decision.signal_priority.value] += 1
        return dict(distribution)
    
    def _analyze_decision_type_distribution(self, decisions: List[EPLDecisionRecord]) -> Dict[str, int]:
        """分析決策類型分佈"""
        distribution = defaultdict(int)
        for decision in decisions:
            distribution[decision.decision_type.value] += 1
        return dict(distribution)
    
    def _generate_pattern_insights(self, successful_decisions: List, failed_decisions: List) -> List[str]:
        """生成模式洞察"""
        insights = []
        
        if successful_decisions and failed_decisions:
            # 成功決策的平均信心分數
            success_confidence = statistics.mean([d.confidence_score for d in successful_decisions])
            failure_confidence = statistics.mean([d.confidence_score for d in failed_decisions])
            
            if success_confidence > failure_confidence + 0.1:
                insights.append(f"成功決策的平均信心分數 ({success_confidence:.2f}) 明顯高於失敗決策 ({failure_confidence:.2f})")
            
            # 優先級分析
            success_critical = len([d for d in successful_decisions if d.signal_priority == SignalPriority.CRITICAL])
            failure_critical = len([d for d in failed_decisions if d.signal_priority == SignalPriority.CRITICAL])
            
            if success_critical > 0 and failure_critical > 0:
                success_critical_rate = success_critical / len(successful_decisions)
                failure_critical_rate = failure_critical / len(failed_decisions)
                
                if success_critical_rate > failure_critical_rate + 0.2:
                    insights.append("CRITICAL 優先級決策在成功案例中占比更高")
        
        return insights if insights else ["需要更多數據來識別明確模式"]

# 全局實例
epl_decision_tracker = EPLDecisionHistoryTracker()

@dataclass
class MarketSnapshot:
    """市場快照數據"""
    timestamp: datetime
    symbol: str
    price: float
    volume: float
    volatility: float
    market_conditions: Dict[str, Any]
    technical_indicators: Dict[str, float]
    sentiment_score: Optional[float] = None

@dataclass  
class PortfolioState:
    """投資組合狀態"""
    timestamp: datetime
    total_value: float
    available_cash: float
    positions: Dict[str, Dict[str, Any]]
    risk_metrics: Dict[str, float]
    correlation_matrix: Optional[Dict[str, Dict[str, float]]] = None
    exposure_limits: Optional[Dict[str, float]] = None

@dataclass
class ExecutionMetrics:
    """執行指標"""
    decision_id: str
    execution_timestamp: datetime
    planned_price: float
    actual_price: float
    slippage: float
    execution_latency: float
    market_impact: float
    execution_quality_score: float
    fees_and_costs: Dict[str, float]

    async def track_execution_lifecycle(self, decision_id: str, execution_data: Dict[str, Any]) -> bool:
        """追蹤執行生命週期"""
        try:
            # 創建執行指標
            execution_metrics = ExecutionMetrics(
                decision_id=decision_id,
                execution_timestamp=datetime.fromisoformat(execution_data.get('timestamp', datetime.now().isoformat())),
                planned_price=execution_data.get('planned_price', 0.0),
                actual_price=execution_data.get('actual_price', 0.0),
                slippage=execution_data.get('slippage', 0.0),
                execution_latency=execution_data.get('latency', 0.0),
                market_impact=execution_data.get('market_impact', 0.0),
                execution_quality_score=execution_data.get('quality_score', 0.0),
                fees_and_costs=execution_data.get('costs', {})
            )
            
            # 更新決策記錄
            decision_record = self._find_decision_by_id(decision_id)
            if decision_record:
                decision_record.execution_details['execution_metrics'] = asdict(execution_metrics)
                logger.info(f"更新執行生命週期: {decision_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"追蹤執行生命週期失敗: {e}")
            return False
    
    async def capture_market_context(self, symbol: str) -> MarketSnapshot:
        """擷取市場上下文"""
        try:
            # 模擬市場數據擷取 (實際應該從市場數據源獲取)
            market_snapshot = MarketSnapshot(
                timestamp=datetime.now(),
                symbol=symbol,
                price=0.0,  # 應該從實際數據源獲取
                volume=0.0,
                volatility=0.0,
                market_conditions={"trend": "neutral", "session": "active"},
                technical_indicators={"rsi": 50.0, "macd": 0.0},
                sentiment_score=0.5
            )
            
            logger.info(f"擷取市場上下文: {symbol}")
            return market_snapshot
            
        except Exception as e:
            logger.error(f"擷取市場上下文失敗: {e}")
            # 返回默認快照
            return MarketSnapshot(
                timestamp=datetime.now(),
                symbol=symbol,
                price=0.0, volume=0.0, volatility=0.0,
                market_conditions={}, technical_indicators={}
            )
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """驗證數據完整性"""
        try:
            integrity_report = {
                "validation_timestamp": datetime.now().isoformat(),
                "total_decisions": len(self.decision_history),
                "total_outcomes": len(self.outcome_history),
                "integrity_checks": {}
            }
            
            # 檢查決策記錄完整性
            missing_outcomes = 0
            invalid_records = 0
            
            for record in self.decision_history:
                # 檢查必要欄位
                if not all([record.decision_id, record.symbol, record.timestamp]):
                    invalid_records += 1
                
                # 檢查是否有對應的結果
                if record.decision_id not in self.outcome_history:
                    missing_outcomes += 1
            
            integrity_report["integrity_checks"] = {
                "invalid_records": invalid_records,
                "missing_outcomes": missing_outcomes,
                "data_consistency": "good" if invalid_records == 0 else "issues_found",
                "outcome_coverage": (len(self.outcome_history) / max(len(self.decision_history), 1)) * 100
            }
            
            logger.info("數據完整性驗證完成")
            return integrity_report
            
        except Exception as e:
            logger.error(f"數據完整性驗證失敗: {e}")
            return {"error": str(e)}

    async def analyze_replacement_patterns(self) -> Dict[str, Any]:
        """分析替換決策模式"""
        try:
            replacement_decisions = [
                record for record in self.decision_history
                if record.decision_type == EPLDecisionType.REPLACE_POSITION
            ]
            
            if not replacement_decisions:
                return {"message": "暫無替換決策數據"}
            
            # 分析替換頻率
            total_decisions = len(self.decision_history)
            replacement_rate = len(replacement_decisions) / total_decisions
            
            # 分析替換成功率
            successful_replacements = 0
            for record in replacement_decisions:
                if record.decision_id in self.outcome_history:
                    outcome = self.outcome_history[record.decision_id]
                    if outcome.success:
                        successful_replacements += 1
            
            replacement_success_rate = successful_replacements / len(replacement_decisions) if replacement_decisions else 0
            
            # 分析信心分數分佈
            confidence_scores = [r.confidence_score for r in replacement_decisions]
            avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0
            
            return {
                "replacement_frequency": {
                    "total_replacements": len(replacement_decisions),
                    "replacement_rate": replacement_rate,
                    "average_confidence": avg_confidence
                },
                "replacement_effectiveness": {
                    "success_rate": replacement_success_rate,
                    "successful_count": successful_replacements,
                    "failed_count": len(replacement_decisions) - successful_replacements
                },
                "insights": self._generate_replacement_insights(replacement_decisions)
            }
            
        except Exception as e:
            logger.error(f"分析替換模式失敗: {e}")
            return {"error": str(e)}
    
    async def analyze_strengthening_patterns(self) -> Dict[str, Any]:
        """分析強化決策模式"""
        try:
            strengthening_decisions = [
                record for record in self.decision_history
                if record.decision_type == EPLDecisionType.STRENGTHEN_POSITION
            ]
            
            if not strengthening_decisions:
                return {"message": "暫無強化決策數據"}
            
            # 基本統計
            total_decisions = len(self.decision_history)
            strengthening_rate = len(strengthening_decisions) / total_decisions
            
            # 成功率分析
            successful_strengthenings = sum(
                1 for record in strengthening_decisions
                if record.decision_id in self.outcome_history and 
                self.outcome_history[record.decision_id].success
            )
            
            success_rate = successful_strengthenings / len(strengthening_decisions) if strengthening_decisions else 0
            
            return {
                "strengthening_frequency": {
                    "total_strengthenings": len(strengthening_decisions),
                    "strengthening_rate": strengthening_rate,
                    "average_confidence": statistics.mean([r.confidence_score for r in strengthening_decisions])
                },
                "strengthening_effectiveness": {
                    "success_rate": success_rate,
                    "successful_count": successful_strengthenings
                }
            }
            
        except Exception as e:
            logger.error(f"分析強化模式失敗: {e}")
            return {"error": str(e)}
    
    async def analyze_new_position_patterns(self) -> Dict[str, Any]:
        """分析新倉位決策模式"""
        try:
            new_position_decisions = [
                record for record in self.decision_history
                if record.decision_type == EPLDecisionType.CREATE_NEW_POSITION
            ]
            
            if not new_position_decisions:
                return {"message": "暫無新倉位決策數據"}
            
            # 基本統計
            creation_rate = len(new_position_decisions) / len(self.decision_history)
            
            # 成功率分析
            successful_creations = sum(
                1 for record in new_position_decisions
                if record.decision_id in self.outcome_history and
                self.outcome_history[record.decision_id].success
            )
            
            success_rate = successful_creations / len(new_position_decisions) if new_position_decisions else 0
            
            return {
                "creation_frequency": {
                    "total_new_positions": len(new_position_decisions),
                    "creation_rate": creation_rate,
                    "average_confidence": statistics.mean([r.confidence_score for r in new_position_decisions])
                },
                "creation_effectiveness": {
                    "success_rate": success_rate,
                    "successful_count": successful_creations
                }
            }
            
        except Exception as e:
            logger.error(f"分析新倉位模式失敗: {e}")
            return {"error": str(e)}
    
    async def analyze_ignore_patterns(self) -> Dict[str, Any]:
        """分析忽略決策模式"""
        try:
            ignore_decisions = [
                record for record in self.decision_history
                if record.decision_type == EPLDecisionType.IGNORE_SIGNAL
            ]
            
            if not ignore_decisions:
                return {"message": "暫無忽略決策數據"}
            
            # 忽略率分析
            ignore_rate = len(ignore_decisions) / len(self.decision_history)
            
            # 忽略原因分析
            ignore_reasons = defaultdict(int)
            for record in ignore_decisions:
                reason = record.position_context.get('reason', 'unknown')
                ignore_reasons[reason] += 1
            
            return {
                "ignore_frequency": {
                    "total_ignores": len(ignore_decisions),
                    "ignore_rate": ignore_rate,
                    "average_confidence": statistics.mean([r.confidence_score for r in ignore_decisions])
                },
                "ignore_reasons": dict(ignore_reasons),
                "filtering_effectiveness": self._calculate_filtering_effectiveness(ignore_decisions)
            }
            
        except Exception as e:
            logger.error(f"分析忽略模式失敗: {e}")
            return {"error": str(e)}
    
    async def generate_learning_insights(self) -> Dict[str, Any]:
        """生成學習洞察"""
        try:
            if not self.decision_history:
                return {"message": "暫無決策數據生成學習洞察"}
            
            # 模式識別
            successful_patterns = await self._identify_successful_patterns()
            failure_patterns = await self._identify_failure_patterns()
            
            # 適應性學習建議
            adaptive_recommendations = self._generate_adaptive_recommendations()
            
            # 回饋整合分析
            feedback_integration = self._analyze_feedback_integration()
            
            return {
                "pattern_recognition": {
                    "successful_patterns": successful_patterns,
                    "failure_patterns": failure_patterns
                },
                "adaptive_learning": {
                    "recommendations": adaptive_recommendations,
                    "threshold_adjustments": self._suggest_threshold_adjustments()
                },
                "feedback_integration": feedback_integration,
                "learning_summary": self._summarize_learning_insights()
            }
            
        except Exception as e:
            logger.error(f"生成學習洞察失敗: {e}")
            return {"error": str(e)}

    async def integrate_phase1_signals(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """整合 Phase1 信號數據"""
        try:
            # 提取 Phase1 信號候選資料
            signal_candidate = signal_data.get('signal_candidate', {})
            
            integrated_data = {
                "original_signal_candidate": signal_candidate,
                "signal_quality_metrics": {
                    "technical_strength": signal_candidate.get('technical_strength', 0.5),
                    "market_timing": signal_candidate.get('market_timing', 0.5),
                    "source_reliability": signal_candidate.get('source_reliability', 0.5)
                },
                "market_context": await self.capture_market_context(signal_candidate.get('symbol', 'UNKNOWN'))
            }
            
            logger.info("Phase1 信號數據整合完成")
            return integrated_data
            
        except Exception as e:
            logger.error(f"整合 Phase1 信號失敗: {e}")
            return {}
    
    async def integrate_phase2_evaluation(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """整合 Phase2 預評估結果"""
        try:
            # 提取 Phase2 預評估結果
            pre_evaluation = evaluation_data.get('pre_evaluation_result', {})
            
            integrated_data = {
                "pre_evaluation_result": pre_evaluation,
                "embedded_scoring": pre_evaluation.get('embedded_scoring', {}),
                "correlation_analysis": pre_evaluation.get('correlation_analysis', {}),
                "portfolio_state": self._extract_portfolio_state(evaluation_data)
            }
            
            logger.info("Phase2 預評估數據整合完成")
            return integrated_data
            
        except Exception as e:
            logger.error(f"整合 Phase2 評估失敗: {e}")
            return {}
    
    async def integrate_phase3_execution(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """整合 Phase3 執行數據"""
        try:
            # 提取執行相關數據
            execution_result = execution_data.get('execution_result', {})
            
            integrated_data = {
                "execution_initiation": {
                    "execution_timestamp": execution_result.get('timestamp'),
                    "execution_latency": execution_result.get('latency'),
                    "market_conditions_at_execution": execution_result.get('market_conditions'),
                    "slippage_measurement": execution_result.get('slippage')
                },
                "execution_monitoring": {
                    "position_establishment": execution_result.get('position_changes'),
                    "risk_parameter_application": execution_result.get('risk_parameters'),
                    "portfolio_impact": execution_result.get('portfolio_impact'),
                    "correlation_effects": execution_result.get('correlation_impact')
                }
            }
            
            logger.info("Phase3 執行數據整合完成")
            return integrated_data
            
        except Exception as e:
            logger.error(f"整合 Phase3 執行失敗: {e}")
            return {}
    
    async def export_phase4_analytics(self) -> Dict[str, Any]:
        """匯出 Phase4 分析結果"""
        try:
            # 匯出所有分析結果供其他系統使用
            analytics_export = {
                "export_timestamp": datetime.now().isoformat(),
                "decision_analytics": await self.get_comprehensive_decision_analysis(),
                "performance_metrics": await self.get_performance_metrics(),
                "pattern_insights": {
                    "replacement_patterns": await self.analyze_replacement_patterns(),
                    "strengthening_patterns": await self.analyze_strengthening_patterns(),
                    "new_position_patterns": await self.analyze_new_position_patterns(),
                    "ignore_patterns": await self.analyze_ignore_patterns()
                },
                "learning_insights": await self.generate_learning_insights(),
                "system_status": await self.get_system_status()
            }
            
            logger.info("Phase4 分析結果匯出完成")
            return analytics_export
            
        except Exception as e:
            logger.error(f"匯出 Phase4 分析失敗: {e}")
            return {"error": str(e)}

    def _generate_replacement_insights(self, replacement_decisions: List) -> List[str]:
        """生成替換洞察"""
        insights = []
        
        if len(replacement_decisions) > 10:
            avg_confidence = statistics.mean([r.confidence_score for r in replacement_decisions])
            if avg_confidence > 0.8:
                insights.append("替換決策普遍具有高信心分數")
            elif avg_confidence < 0.6:
                insights.append("替換決策信心分數偏低，建議檢討標準")
        
        return insights if insights else ["需要更多數據生成洞察"]
    
    def _extract_portfolio_state(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取投資組合狀態"""
        return {
            "current_positions": evaluation_data.get('portfolio', {}).get('positions', {}),
            "risk_metrics": evaluation_data.get('portfolio', {}).get('risk_metrics', {}),
            "available_cash": evaluation_data.get('portfolio', {}).get('cash', 0.0),
            "total_value": evaluation_data.get('portfolio', {}).get('total_value', 0.0)
        }
    
    def _calculate_filtering_effectiveness(self, ignore_decisions: List) -> Dict[str, Any]:
        """計算過濾效果"""
        if not ignore_decisions:
            return {"effectiveness": "no_data"}
        
        # 計算低品質信號過濾率
        low_quality_ignores = len([d for d in ignore_decisions if d.confidence_score < 0.5])
        filtering_rate = low_quality_ignores / len(ignore_decisions)
        
        return {
            "low_quality_filtering_rate": filtering_rate,
            "total_filtered": len(ignore_decisions),
            "effectiveness_score": min(filtering_rate * 2, 1.0)  # 歸一化到0-1
        }
    
    async def _identify_successful_patterns(self) -> Dict[str, Any]:
        """識別成功模式"""
        successful_decisions = [
            record for record in self.decision_history
            if record.decision_id in self.outcome_history and
            self.outcome_history[record.decision_id].success
        ]
        
        if not successful_decisions:
            return {"patterns": "insufficient_data"}
        
        # 分析成功決策的共同特徵
        avg_confidence = statistics.mean([d.confidence_score for d in successful_decisions])
        priority_distribution = defaultdict(int)
        
        for decision in successful_decisions:
            priority_distribution[decision.signal_priority.value] += 1
        
        return {
            "average_confidence": avg_confidence,
            "priority_distribution": dict(priority_distribution),
            "pattern_count": len(successful_decisions)
        }
    
    async def _identify_failure_patterns(self) -> Dict[str, Any]:
        """識別失敗模式"""
        failed_decisions = [
            record for record in self.decision_history
            if record.decision_id in self.outcome_history and
            not self.outcome_history[record.decision_id].success
        ]
        
        if not failed_decisions:
            return {"patterns": "insufficient_data"}
        
        # 分析失敗決策的共同特徵
        avg_confidence = statistics.mean([d.confidence_score for d in failed_decisions])
        priority_distribution = defaultdict(int)
        
        for decision in failed_decisions:
            priority_distribution[decision.signal_priority.value] += 1
        
        return {
            "average_confidence": avg_confidence,
            "priority_distribution": dict(priority_distribution),
            "pattern_count": len(failed_decisions)
        }
    
    def _generate_adaptive_recommendations(self) -> List[str]:
        """生成適應性建議"""
        recommendations = []
        
        if self.success_rates:
            overall_success_rate = sum(
                sum(successes) / len(successes) for successes in self.success_rates.values() if successes
            ) / len(self.success_rates)
            
            if overall_success_rate < 0.7:
                recommendations.append("整體成功率偏低，建議調整決策閾值")
            elif overall_success_rate > 0.9:
                recommendations.append("成功率極高，可考慮降低決策門檻以增加機會")
        
        return recommendations if recommendations else ["系統表現穩定，繼續監控"]
    
    def _suggest_threshold_adjustments(self) -> Dict[str, float]:
        """建議閾值調整"""
        adjustments = {}
        
        # 基於成功率建議置信度閾值調整
        if self.success_rates:
            for decision_type, successes in self.success_rates.items():
                if successes:
                    success_rate = sum(successes) / len(successes)
                    if success_rate < 0.6:
                        adjustments[f"{decision_type}_confidence_threshold"] = 0.1  # 提高閾值
                    elif success_rate > 0.9:
                        adjustments[f"{decision_type}_confidence_threshold"] = -0.05  # 降低閾值
        
        return adjustments
    
    def _analyze_feedback_integration(self) -> Dict[str, Any]:
        """分析回饋整合"""
        return {
            "total_outcomes_tracked": len(self.outcome_history),
            "feedback_coverage": len(self.outcome_history) / max(len(self.decision_history), 1),
            "learning_effectiveness": "good" if len(self.outcome_history) > 0 else "limited",
            "improvement_areas": ["增加結果追蹤覆蓋率", "加強即時回饋機制"]
        }
    
    def _summarize_learning_insights(self) -> str:
        """總結學習洞察"""
        if not self.decision_history:
            return "暫無足夠數據生成學習總結"
        
        total_decisions = len(self.decision_history)
        total_outcomes = len(self.outcome_history)
        
        return f"已追蹤 {total_decisions} 個決策，其中 {total_outcomes} 個有結果回饋。系統正在持續學習和優化決策模式。"
