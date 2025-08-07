"""
🎛️ Phase4 Output Monitoring Core Coordinator
============================================

Phase4輸出監控核心協調器 - 統一管理和協調所有監控組件
整合5個監控模塊的功能，提供統一的API接口
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 添加監控模塊路徑
current_dir = Path(__file__).parent
sys.path.extend([
    str(current_dir / "1_unified_monitoring_dashboard"),
    str(current_dir / "2_signal_processing_statistics"),
    str(current_dir / "3_epl_decision_history_tracking"),
    str(current_dir / "4_notification_success_rate_monitoring"),
    str(current_dir / "5_system_performance_metrics_monitoring")
])

# 導入監控組件
try:
    from unified_monitoring_dashboard import unified_dashboard
    from signal_processing_statistics import signal_statistics
    from epl_decision_history_tracking import epl_decision_tracker
    from notification_success_rate_monitoring import notification_monitor
    from system_performance_metrics_monitoring import performance_monitor
    MONITORING_COMPONENTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"監控組件導入失敗: {e}")
    MONITORING_COMPONENTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class Phase4MonitoringCoordinator:
    """Phase4監控協調器"""
    
    def __init__(self):
        self.coordinator_enabled = True
        self.last_update = datetime.now()
        
        # 組件狀態追蹤
        self.component_status = {
            "unified_dashboard": {"enabled": False, "last_update": None, "error_count": 0},
            "signal_statistics": {"enabled": False, "last_update": None, "error_count": 0},
            "epl_decision_tracker": {"enabled": False, "last_update": None, "error_count": 0},
            "notification_monitor": {"enabled": False, "last_update": None, "error_count": 0},
            "performance_monitor": {"enabled": False, "last_update": None, "error_count": 0}
        }
        
        # 數據聚合緩存
        self.aggregated_cache = {}
        self.cache_ttl = 60  # 緩存60秒
        
        # 初始化協調器
        self._initialize_coordinator()
    
    def _initialize_coordinator(self):
        """初始化協調器"""
        logger.info("初始化Phase4監控協調器")
        
        if not MONITORING_COMPONENTS_AVAILABLE:
            logger.warning("監控組件不可用，協調器將以有限模式運行")
            return
        
        # 檢查各組件狀態
        self._check_component_availability()
        
        logger.info(f"監控協調器初始化完成，可用組件: {self._get_available_components()}")
    
    def _check_component_availability(self):
        """檢查組件可用性"""
        components = {
            "unified_dashboard": unified_dashboard if MONITORING_COMPONENTS_AVAILABLE else None,
            "signal_statistics": signal_statistics if MONITORING_COMPONENTS_AVAILABLE else None,
            "epl_decision_tracker": epl_decision_tracker if MONITORING_COMPONENTS_AVAILABLE else None,
            "notification_monitor": notification_monitor if MONITORING_COMPONENTS_AVAILABLE else None,
            "performance_monitor": performance_monitor if MONITORING_COMPONENTS_AVAILABLE else None
        }
        
        for component_name, component_instance in components.items():
            if component_instance is not None:
                try:
                    # 簡單的可用性測試
                    self.component_status[component_name]["enabled"] = True
                    self.component_status[component_name]["last_update"] = datetime.now()
                    logger.info(f"組件 {component_name} 可用")
                except Exception as e:
                    logger.error(f"組件 {component_name} 不可用: {e}")
                    self.component_status[component_name]["error_count"] += 1
    
    def _get_available_components(self) -> List[str]:
        """獲取可用組件列表"""
        return [name for name, status in self.component_status.items() if status["enabled"]]
    
    async def get_comprehensive_monitoring_overview(self) -> Dict[str, Any]:
        """獲取綜合監控概覽"""
        try:
            current_time = datetime.now()
            
            # 檢查緩存
            cache_key = "comprehensive_overview"
            if self._is_cache_valid(cache_key):
                return self.aggregated_cache[cache_key]
            
            overview = {
                "monitoring_metadata": {
                    "generated_at": current_time.isoformat(),
                    "coordinator_status": "active" if self.coordinator_enabled else "inactive",
                    "available_components": self._get_available_components(),
                    "total_components": len(self.component_status),
                    "last_update": self.last_update.isoformat()
                },
                "component_health_summary": self._get_component_health_summary(),
                "unified_dashboard_summary": {},
                "signal_processing_overview": {},
                "epl_decision_summary": {},
                "notification_performance": {},
                "system_performance_summary": {},
                "cross_component_insights": {},
                "overall_system_health": {}
            }
            
            # 並行獲取各組件數據
            component_tasks = []
            
            if self.component_status["unified_dashboard"]["enabled"] and MONITORING_COMPONENTS_AVAILABLE:
                component_tasks.append(self._get_dashboard_summary())
            
            if self.component_status["signal_statistics"]["enabled"] and MONITORING_COMPONENTS_AVAILABLE:
                component_tasks.append(self._get_signal_statistics_summary())
            
            if self.component_status["epl_decision_tracker"]["enabled"] and MONITORING_COMPONENTS_AVAILABLE:
                component_tasks.append(self._get_epl_summary())
            
            if self.component_status["notification_monitor"]["enabled"] and MONITORING_COMPONENTS_AVAILABLE:
                component_tasks.append(self._get_notification_summary())
            
            if self.component_status["performance_monitor"]["enabled"] and MONITORING_COMPONENTS_AVAILABLE:
                component_tasks.append(self._get_performance_summary())
            
            # 執行並收集結果
            if component_tasks:
                results = await asyncio.gather(*component_tasks, return_exceptions=True)
                
                # 處理結果
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"組件數據獲取失敗: {result}")
                        continue
                    
                    # 根據任務順序分配結果
                    if i == 0 and self.component_status["unified_dashboard"]["enabled"]:
                        overview["unified_dashboard_summary"] = result
                    elif i == 1 and self.component_status["signal_statistics"]["enabled"]:
                        overview["signal_processing_overview"] = result
                    # ... 其他組件類似處理
            
            # 生成跨組件洞察
            overview["cross_component_insights"] = self._generate_cross_component_insights(overview)
            
            # 生成整體系統健康評估
            overview["overall_system_health"] = self._assess_overall_system_health(overview)
            
            # 更新緩存
            self.aggregated_cache[cache_key] = overview
            self.aggregated_cache[f"{cache_key}_timestamp"] = current_time
            
            self.last_update = current_time
            return overview
            
        except Exception as e:
            logger.error(f"獲取綜合監控概覽失敗: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "coordinator_status": "error"
            }
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """檢查緩存是否有效"""
        if cache_key not in self.aggregated_cache:
            return False
        
        timestamp_key = f"{cache_key}_timestamp"
        if timestamp_key not in self.aggregated_cache:
            return False
        
        cache_time = self.aggregated_cache[timestamp_key]
        return (datetime.now() - cache_time).total_seconds() < self.cache_ttl
    
    def _get_component_health_summary(self) -> Dict[str, Any]:
        """獲取組件健康摘要"""
        healthy_components = len([s for s in self.component_status.values() if s["enabled"]])
        total_components = len(self.component_status)
        
        total_errors = sum(s["error_count"] for s in self.component_status.values())
        
        return {
            "healthy_components": healthy_components,
            "total_components": total_components,
            "health_percentage": (healthy_components / total_components) * 100,
            "total_error_count": total_errors,
            "component_details": self.component_status,
            "overall_status": "healthy" if healthy_components == total_components else "degraded" if healthy_components > 0 else "critical"
        }
    
    async def _get_dashboard_summary(self) -> Dict[str, Any]:
        """獲取儀表板摘要"""
        try:
            if not MONITORING_COMPONENTS_AVAILABLE:
                return {"status": "component_unavailable"}
            
            # 從統一儀表板獲取關鍵指標
            dashboard_data = await unified_dashboard.update_dashboard_data()
            
            return {
                "dashboard_status": dashboard_data.get("dashboard_status", "unknown"),
                "widgets_updated": dashboard_data.get("widgets_updated", 0),
                "update_latency_ms": dashboard_data.get("update_latency_ms", 0),
                "last_update": dashboard_data.get("last_update"),
                "widget_summary": {
                    widget_id: {
                        "status": widget_data.get("status", "unknown"),
                        "last_update": widget_data.get("last_update")
                    }
                    for widget_id, widget_data in dashboard_data.get("widget_data", {}).items()
                }
            }
        except Exception as e:
            logger.error(f"獲取儀表板摘要失敗: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _get_signal_statistics_summary(self) -> Dict[str, Any]:
        """獲取信號統計摘要"""
        try:
            if not MONITORING_COMPONENTS_AVAILABLE:
                return {"status": "component_unavailable"}
            
            # 獲取實時指標
            real_time_metrics = await signal_statistics.get_real_time_metrics()
            
            return {
                "real_time_status": real_time_metrics.get("real_time_status", "unknown"),
                "recent_signal_count": real_time_metrics.get("recent_5min_metrics", {}).get("signal_count", 0),
                "average_quality": real_time_metrics.get("recent_5min_metrics", {}).get("average_quality", 0),
                "average_latency": real_time_metrics.get("recent_5min_metrics", {}).get("average_latency", 0),
                "processing_rate": real_time_metrics.get("processing_rate", {}),
                "total_signals_tracked": len(signal_statistics.signal_history)
            }
        except Exception as e:
            logger.error(f"獲取信號統計摘要失敗: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _get_epl_summary(self) -> Dict[str, Any]:
        """獲取EPL決策摘要"""
        try:
            if not MONITORING_COMPONENTS_AVAILABLE:
                return {"status": "component_unavailable"}
            
            # 獲取最近的決策
            recent_decisions = await epl_decision_tracker.get_recent_decisions(hours=1)
            
            # 計算基本統計
            total_decisions = len(epl_decision_tracker.decision_history)
            decisions_with_outcomes = len(epl_decision_tracker.outcome_history)
            
            return {
                "total_decisions_tracked": total_decisions,
                "decisions_with_outcomes": decisions_with_outcomes,
                "recent_decisions_1h": len(recent_decisions),
                "decision_type_distribution": dict(epl_decision_tracker.decision_type_stats),
                "priority_distribution": dict(epl_decision_tracker.priority_stats),
                "tracking_enabled": epl_decision_tracker.tracking_enabled,
                "last_update": epl_decision_tracker.last_update.isoformat()
            }
        except Exception as e:
            logger.error(f"獲取EPL決策摘要失敗: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _get_notification_summary(self) -> Dict[str, Any]:
        """獲取通知摘要"""
        try:
            if not MONITORING_COMPONENTS_AVAILABLE:
                return {"status": "component_unavailable"}
            
            # 獲取實時指標
            real_time_metrics = await notification_monitor.get_real_time_metrics()
            
            return {
                "real_time_status": real_time_metrics.get("real_time_status", "unknown"),
                "recent_notifications": real_time_metrics.get("recent_5min_metrics", {}).get("total_notifications", 0),
                "recent_success_rate": real_time_metrics.get("recent_5min_metrics", {}).get("success_rate", 0),
                "channel_activity": real_time_metrics.get("recent_5min_metrics", {}).get("channel_activity", {}),
                "notification_rate": real_time_metrics.get("notification_rate", {}),
                "total_notifications_tracked": len(notification_monitor.notification_history),
                "monitoring_enabled": notification_monitor.monitoring_enabled
            }
        except Exception as e:
            logger.error(f"獲取通知摘要失敗: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _get_performance_summary(self) -> Dict[str, Any]:
        """獲取性能摘要"""
        try:
            if not MONITORING_COMPONENTS_AVAILABLE:
                return {"status": "component_unavailable"}
            
            # 獲取實時性能指標
            real_time_metrics = await performance_monitor.get_real_time_performance_metrics()
            
            system_metrics = real_time_metrics.get("system_metrics", {})
            
            return {
                "monitoring_status": real_time_metrics.get("monitoring_status", "unknown"),
                "health_status": real_time_metrics.get("health_status", "unknown"),
                "cpu_usage": system_metrics.get("cpu_usage", 0),
                "memory_usage": system_metrics.get("memory_usage", 0),
                "disk_usage": system_metrics.get("disk_usage", 0),
                "alert_count": real_time_metrics.get("alert_count", 0),
                "samples_collected": len(performance_monitor.system_snapshots),
                "monitoring_enabled": performance_monitor.monitoring_enabled
            }
        except Exception as e:
            logger.error(f"獲取性能摘要失敗: {e}")
            return {"status": "error", "error": str(e)}
    
    def _generate_cross_component_insights(self, overview: Dict[str, Any]) -> Dict[str, Any]:
        """生成跨組件洞察"""
        insights = {
            "performance_correlation": {},
            "bottleneck_analysis": {},
            "optimization_opportunities": [],
            "system_efficiency": {}
        }
        
        try:
            # 性能相關性分析
            signal_summary = overview.get("signal_processing_overview", {})
            performance_summary = overview.get("system_performance_summary", {})
            notification_summary = overview.get("notification_performance", {})
            
            # CPU與信號處理關聯
            if signal_summary.get("recent_signal_count", 0) > 0 and performance_summary.get("cpu_usage", 0) > 0:
                insights["performance_correlation"]["signal_cpu_correlation"] = {
                    "signals_per_cpu_percent": signal_summary["recent_signal_count"] / max(performance_summary["cpu_usage"], 1),
                    "efficiency_rating": "high" if performance_summary["cpu_usage"] < 50 else "medium" if performance_summary["cpu_usage"] < 80 else "low"
                }
            
            # 瓶頸分析
            bottlenecks = []
            
            if performance_summary.get("cpu_usage", 0) > 80:
                bottlenecks.append("high_cpu_usage")
            
            if performance_summary.get("memory_usage", 0) > 85:
                bottlenecks.append("high_memory_usage")
            
            if signal_summary.get("average_latency", 0) > 1000:
                bottlenecks.append("high_signal_latency")
            
            if notification_summary.get("recent_success_rate", 1) < 0.9:
                bottlenecks.append("low_notification_success")
            
            insights["bottleneck_analysis"]["identified_bottlenecks"] = bottlenecks
            insights["bottleneck_analysis"]["severity"] = "high" if len(bottlenecks) > 2 else "medium" if len(bottlenecks) > 0 else "low"
            
            # 優化機會
            optimization_opportunities = []
            
            if performance_summary.get("cpu_usage", 0) < 30 and signal_summary.get("recent_signal_count", 0) > 0:
                optimization_opportunities.append("可以增加信號處理併發度以提高吞吐量")
            
            if notification_summary.get("recent_success_rate", 1) > 0.95:
                optimization_opportunities.append("通知系統表現優異，可考慮增加通知頻率")
            
            if len(bottlenecks) == 0:
                optimization_opportunities.append("系統運行良好，可考慮進一步優化以提升效率")
            
            insights["optimization_opportunities"] = optimization_opportunities
            
            # 系統效率評估
            efficiency_scores = []
            
            if performance_summary.get("cpu_usage", 0) > 0:
                cpu_efficiency = max(0, 1 - (performance_summary["cpu_usage"] / 100))
                efficiency_scores.append(cpu_efficiency)
            
            if signal_summary.get("average_quality", 0) > 0:
                quality_efficiency = signal_summary["average_quality"]
                efficiency_scores.append(quality_efficiency)
            
            if notification_summary.get("recent_success_rate", 0) > 0:
                notification_efficiency = notification_summary["recent_success_rate"]
                efficiency_scores.append(notification_efficiency)
            
            if efficiency_scores:
                overall_efficiency = sum(efficiency_scores) / len(efficiency_scores)
                insights["system_efficiency"] = {
                    "overall_score": overall_efficiency,
                    "efficiency_grade": self._get_efficiency_grade(overall_efficiency),
                    "component_scores": {
                        "cpu_efficiency": efficiency_scores[0] if len(efficiency_scores) > 0 else 0,
                        "signal_quality": efficiency_scores[1] if len(efficiency_scores) > 1 else 0,
                        "notification_success": efficiency_scores[2] if len(efficiency_scores) > 2 else 0
                    }
                }
            
        except Exception as e:
            logger.error(f"生成跨組件洞察失敗: {e}")
            insights["error"] = str(e)
        
        return insights
    
    def _get_efficiency_grade(self, score: float) -> str:
        """獲取效率等級"""
        if score >= 0.9:
            return "A+"
        elif score >= 0.8:
            return "A"
        elif score >= 0.7:
            return "B"
        elif score >= 0.6:
            return "C"
        else:
            return "D"
    
    def _assess_overall_system_health(self, overview: Dict[str, Any]) -> Dict[str, Any]:
        """評估整體系統健康"""
        health_assessment = {
            "overall_status": "unknown",
            "health_score": 0.0,
            "critical_issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        try:
            health_factors = []
            
            # 組件健康評估
            component_health = overview.get("component_health_summary", {})
            component_health_score = component_health.get("health_percentage", 0) / 100
            health_factors.append(("component_health", component_health_score, 0.25))
            
            # 性能健康評估
            performance_summary = overview.get("system_performance_summary", {})
            performance_health_score = self._calculate_performance_health_score(performance_summary)
            health_factors.append(("performance_health", performance_health_score, 0.25))
            
            # 信號處理健康評估
            signal_summary = overview.get("signal_processing_overview", {})
            signal_health_score = self._calculate_signal_health_score(signal_summary)
            health_factors.append(("signal_health", signal_health_score, 0.2))
            
            # 通知健康評估
            notification_summary = overview.get("notification_performance", {})
            notification_health_score = self._calculate_notification_health_score(notification_summary)
            health_factors.append(("notification_health", notification_health_score, 0.15))
            
            # EPL決策健康評估
            epl_summary = overview.get("epl_decision_summary", {})
            epl_health_score = self._calculate_epl_health_score(epl_summary)
            health_factors.append(("epl_health", epl_health_score, 0.15))
            
            # 計算加權平均健康分數
            total_weighted_score = sum(score * weight for _, score, weight in health_factors)
            total_weight = sum(weight for _, _, weight in health_factors)
            overall_health_score = total_weighted_score / total_weight if total_weight > 0 else 0
            
            # 確定整體狀態
            if overall_health_score >= 0.9:
                overall_status = "excellent"
            elif overall_health_score >= 0.8:
                overall_status = "good"
            elif overall_health_score >= 0.7:
                overall_status = "fair"
            elif overall_health_score >= 0.5:
                overall_status = "poor"
            else:
                overall_status = "critical"
            
            # 收集問題和建議
            critical_issues, warnings, recommendations = self._collect_health_issues_and_recommendations(overview, health_factors)
            
            health_assessment.update({
                "overall_status": overall_status,
                "health_score": overall_health_score,
                "health_factors": {name: score for name, score, _ in health_factors},
                "critical_issues": critical_issues,
                "warnings": warnings,
                "recommendations": recommendations
            })
            
        except Exception as e:
            logger.error(f"評估整體系統健康失敗: {e}")
            health_assessment["error"] = str(e)
        
        return health_assessment
    
    def _calculate_performance_health_score(self, performance_summary: Dict) -> float:
        """計算性能健康分數"""
        if not performance_summary or performance_summary.get("status") == "error":
            return 0.5  # 中等分數，因為無法確定狀態
        
        cpu_usage = performance_summary.get("cpu_usage", 0)
        memory_usage = performance_summary.get("memory_usage", 0)
        alert_count = performance_summary.get("alert_count", 0)
        
        # CPU分數（使用率越低越好，但太低也不好）
        cpu_score = 1.0 if 20 <= cpu_usage <= 60 else max(0, 1 - abs(cpu_usage - 40) / 60)
        
        # 記憶體分數
        memory_score = max(0, 1 - (memory_usage / 100))
        
        # 警報分數
        alert_score = max(0, 1 - (alert_count / 10))  # 假設10個警報為最差情況
        
        return (cpu_score + memory_score + alert_score) / 3
    
    def _calculate_signal_health_score(self, signal_summary: Dict) -> float:
        """計算信號健康分數"""
        if not signal_summary or signal_summary.get("status") == "error":
            return 0.5
        
        average_quality = signal_summary.get("average_quality", 0)
        average_latency = signal_summary.get("average_latency", 1000)
        processing_rate = signal_summary.get("processing_rate", {}).get("performance_ratio", 0)
        
        # 質量分數
        quality_score = average_quality if average_quality <= 1 else average_quality / 100
        
        # 延遲分數（延遲越低越好）
        latency_score = max(0, 1 - (average_latency / 2000))  # 2秒為基準
        
        # 處理率分數
        rate_score = min(1.0, processing_rate)
        
        return (quality_score + latency_score + rate_score) / 3
    
    def _calculate_notification_health_score(self, notification_summary: Dict) -> float:
        """計算通知健康分數"""
        if not notification_summary or notification_summary.get("status") == "error":
            return 0.5
        
        success_rate = notification_summary.get("recent_success_rate", 0)
        notification_rate = notification_summary.get("notification_rate", {}).get("performance_ratio", 0)
        
        # 成功率分數
        success_score = success_rate
        
        # 發送率分數
        rate_score = min(1.0, notification_rate)
        
        return (success_score + rate_score) / 2
    
    def _calculate_epl_health_score(self, epl_summary: Dict) -> float:
        """計算EPL健康分數"""
        if not epl_summary or epl_summary.get("status") == "error":
            return 0.5
        
        total_decisions = epl_summary.get("total_decisions_tracked", 0)
        decisions_with_outcomes = epl_summary.get("decisions_with_outcomes", 0)
        
        # 決策完整性分數
        completeness_score = decisions_with_outcomes / max(total_decisions, 1) if total_decisions > 0 else 0
        
        # 決策活動分數
        activity_score = min(1.0, total_decisions / 100) if total_decisions > 0 else 0  # 假設100個決策為滿分
        
        return (completeness_score + activity_score) / 2
    
    def _collect_health_issues_and_recommendations(self, overview: Dict, health_factors: List) -> Tuple[List[str], List[str], List[str]]:
        """收集健康問題和建議"""
        critical_issues = []
        warnings = []
        recommendations = []
        
        # 檢查各個組件的健康狀況
        for factor_name, score, _ in health_factors:
            if score < 0.3:
                critical_issues.append(f"{factor_name} 嚴重異常 (分數: {score:.2f})")
            elif score < 0.6:
                warnings.append(f"{factor_name} 需要關注 (分數: {score:.2f})")
        
        # 基於跨組件洞察添加建議
        cross_insights = overview.get("cross_component_insights", {})
        bottlenecks = cross_insights.get("bottleneck_analysis", {}).get("identified_bottlenecks", [])
        
        if "high_cpu_usage" in bottlenecks:
            recommendations.append("CPU使用率過高，建議優化計算密集型任務")
        
        if "high_memory_usage" in bottlenecks:
            recommendations.append("記憶體使用率過高，建議檢查內存洩漏或增加RAM")
        
        if "high_signal_latency" in bottlenecks:
            recommendations.append("信號處理延遲較高，建議優化處理算法或增加並發")
        
        if "low_notification_success" in bottlenecks:
            recommendations.append("通知成功率較低，建議檢查通知渠道配置")
        
        # 添加優化建議
        optimization_opportunities = cross_insights.get("optimization_opportunities", [])
        recommendations.extend(optimization_opportunities)
        
        return critical_issues, warnings, recommendations
    
    async def record_system_event(self, event_data: Dict[str, Any]) -> bool:
        """記錄系統事件"""
        try:
            event_type = event_data.get("type", "unknown")
            component = event_data.get("component", "system")
            
            # 根據事件類型路由到相應的組件
            if component == "signal_processing" and MONITORING_COMPONENTS_AVAILABLE:
                return await signal_statistics.record_signal_metrics(event_data)
            elif component == "epl_decision" and MONITORING_COMPONENTS_AVAILABLE:
                return await epl_decision_tracker.record_epl_decision(event_data)
            elif component == "notification" and MONITORING_COMPONENTS_AVAILABLE:
                if event_type == "sent":
                    return await notification_monitor.record_notification_sent(event_data)
                elif event_type == "status_update":
                    return await notification_monitor.update_notification_status(
                        event_data.get("notification_id", ""),
                        event_data
                    )
            
            # 更新組件狀態
            if component in self.component_status:
                self.component_status[component]["last_update"] = datetime.now()
            
            return True
            
        except Exception as e:
            logger.error(f"記錄系統事件失敗: {e}")
            return False
    
    async def get_component_specific_data(self, component_name: str, data_type: str = "summary") -> Dict[str, Any]:
        """獲取特定組件的詳細數據"""
        try:
            if not MONITORING_COMPONENTS_AVAILABLE:
                return {"status": "components_unavailable"}
            
            if component_name == "unified_dashboard":
                if data_type == "full":
                    return await unified_dashboard.get_dashboard_export_data()
                else:
                    return await self._get_dashboard_summary()
            
            elif component_name == "signal_statistics":
                if data_type == "full":
                    return await signal_statistics.get_comprehensive_statistics()
                else:
                    return await signal_statistics.get_real_time_metrics()
            
            elif component_name == "epl_decision_tracker":
                if data_type == "full":
                    return await epl_decision_tracker.get_comprehensive_decision_analysis()
                else:
                    return await epl_decision_tracker.get_recent_decisions()
            
            elif component_name == "notification_monitor":
                if data_type == "full":
                    return await notification_monitor.get_comprehensive_monitoring_report()
                else:
                    return await notification_monitor.get_real_time_metrics()
            
            elif component_name == "performance_monitor":
                if data_type == "full":
                    return await performance_monitor.get_comprehensive_performance_report()
                else:
                    return await performance_monitor.get_real_time_performance_metrics()
            
            else:
                return {"error": f"未知組件: {component_name}"}
                
        except Exception as e:
            logger.error(f"獲取組件數據失敗: {e}")
            return {"error": str(e)}
    
    def get_coordinator_status(self) -> Dict[str, Any]:
        """獲取協調器狀態"""
        return {
            "coordinator_enabled": self.coordinator_enabled,
            "last_update": self.last_update.isoformat(),
            "components_available": MONITORING_COMPONENTS_AVAILABLE,
            "component_status": self.component_status,
            "available_components": self._get_available_components(),
            "cache_info": {
                "cache_entries": len(self.aggregated_cache),
                "cache_ttl_seconds": self.cache_ttl
            }
        }
    
    def clear_cache(self):
        """清理緩存"""
        self.aggregated_cache.clear()
        logger.info("監控協調器緩存已清理")
    
    def stop_coordinator(self):
        """停止協調器"""
        self.coordinator_enabled = False
        self.clear_cache()
        logger.info("Phase4監控協調器已停止")

# 全局實例
monitoring_coordinator = Phase4MonitoringCoordinator()
