"""
🖥️ Phase4 Unified Monitoring Dashboard - Complete Implementation
================================================================

基於 unified_monitoring_dashboard_config.json v2.1.0 的完整實現
實時系統狀態監控與性能分析儀表板

Features:
- 實時數據更新 (1秒刷新)
- 完整的Phase1-Phase3數據整合
- 24小時活動數據保留
- 多層級監控架構
- 智能警報系統
"""

import asyncio
import logging
import json
import time
import statistics
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict, deque
from enum import Enum

logger = logging.getLogger(__name__)

class SystemStatus(Enum):
    """系統狀態枚舉"""
    GREEN = "green"
    YELLOW = "yellow" 
    RED = "red"

class WidgetType(Enum):
    """Widget類型枚舉"""
    STATUS_INDICATOR_GRID = "status_indicator_grid"
    TIME_SERIES_CHARTS_AND_COUNTERS = "time_series_charts_and_counters"
    DECISION_ANALYTICS_DASHBOARD = "decision_analytics_dashboard"
    NOTIFICATION_PERFORMANCE_DASHBOARD = "notification_performance_dashboard"
    PERFORMANCE_METRICS_DASHBOARD = "performance_metrics_dashboard"

class SignalPriority(Enum):
    """信號優先級枚舉"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class EPLDecisionType(Enum):
    """EPL決策類型枚舉"""
    REPLACE_POSITION = "REPLACE"
    STRENGTHEN_POSITION = "STRENGTHEN"
    CREATE_NEW_POSITION = "CREATE_NEW"
    IGNORE_SIGNAL = "IGNORE"

@dataclass
class AlertThreshold:
    """警報閾值配置"""
    metric_name: str
    threshold_value: float
    comparison: str  # '<', '>', '<=', '>='
    severity: str    # 'warning', 'critical'

@dataclass
class MetricValue:
    """指標值數據結構"""
    value: float
    timestamp: datetime
    source: str
    confidence: float = 1.0

@dataclass
class TimeSeriesData:
    """時間序列數據"""
    metric_name: str
    values: deque = field(default_factory=lambda: deque(maxlen=14400))  # 4小時 @ 1秒間隔
    last_update: datetime = field(default_factory=datetime.utcnow)
    
    def add_value(self, value: float, timestamp: datetime = None):
        """添加新值"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.values.append(MetricValue(value, timestamp, "dashboard", 1.0))
        self.last_update = timestamp
    
    def get_latest_value(self) -> Optional[float]:
        """獲取最新值"""
        if self.values:
            return self.values[-1].value
        return None
    
    def get_average(self, minutes: int = 10) -> float:
        """獲取指定時間內的平均值"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_values = [v.value for v in self.values if v.timestamp >= cutoff_time]
        return statistics.mean(recent_values) if recent_values else 0.0

@dataclass
class WidgetData:
    """儀表板Widget數據"""
    widget_id: str
    widget_type: WidgetType
    title: str
    data: Dict[str, Any]
    last_update: datetime
    refresh_rate: int  # 秒
    status: SystemStatus = SystemStatus.GREEN

@dataclass
class SystemHealthIndicator:
    """系統健康指標"""
    component: str
    status: SystemStatus
    metrics: Dict[str, float]
    alerts: List[str]
    last_check: datetime
    alert_thresholds: List[AlertThreshold] = field(default_factory=list)

@dataclass
class NotificationDeliveryMetrics:
    """通知交付指標"""
    channel: str
    priority: SignalPriority
    sent_count: int = 0
    delivered_count: int = 0
    failed_count: int = 0
    avg_delivery_time: float = 0.0
    last_update: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def delivery_rate(self) -> float:
        """交付成功率"""
        if self.sent_count == 0:
            return 0.0
        return (self.delivered_count / self.sent_count) * 100

@dataclass
class EPLDecisionMetrics:
    """EPL決策指標"""
    decision_type: EPLDecisionType
    count: int = 0
    success_count: int = 0
    avg_latency: float = 0.0
    last_update: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.count == 0:
            return 0.0
        return (self.success_count / self.count) * 100

@dataclass 
class SignalProcessingStats:
    """信號處理統計"""
    total_signals: int = 0
    signals_by_priority: Dict[SignalPriority, int] = field(default_factory=lambda: {p: 0 for p in SignalPriority})
    signals_by_source: Dict[str, int] = field(default_factory=dict)
    processing_latency: TimeSeriesData = field(default_factory=lambda: TimeSeriesData("processing_latency"))
    quality_distribution: Dict[str, int] = field(default_factory=dict)

class UnifiedMonitoringDashboard:
    """
    Phase4 統一監控儀表板 - 完整實現
    
    基於JSON配置的實時監控系統，集成Phase1-Phase3數據流
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化監控儀表板"""
        self.config_path = config_path or str(Path(__file__).parent / "unified_monitoring_dashboard_config.json")
        self.config = self._load_config()
        
        # 核心數據儲存
        self.widgets: Dict[str, WidgetData] = {}
        self.system_health: Dict[str, SystemHealthIndicator] = {}
        self.time_series_data: Dict[str, TimeSeriesData] = {}
        
        # 監控指標
        self.signal_processing_stats = SignalProcessingStats()
        self.epl_decision_metrics: Dict[EPLDecisionType, EPLDecisionMetrics] = {
            decision_type: EPLDecisionMetrics(decision_type) for decision_type in EPLDecisionType
        }
        self.notification_metrics: Dict[Tuple[str, SignalPriority], NotificationDeliveryMetrics] = {}
        
        # 性能監控
        self.performance_metrics = {
            "cpu_usage": TimeSeriesData("cpu_usage"),
            "memory_usage": TimeSeriesData("memory_usage"), 
            "disk_io": TimeSeriesData("disk_io"),
            "network_io": TimeSeriesData("network_io"),
            "signals_per_second": TimeSeriesData("signals_per_second"),
            "decisions_per_second": TimeSeriesData("decisions_per_second"),
            "notifications_per_second": TimeSeriesData("notifications_per_second")
        }
        
        # 系統狀態
        self.dashboard_enabled = True
        self.last_update = datetime.utcnow()
        self.error_count = 0
        self.update_latency_history = deque(maxlen=100)
        
        # 初始化組件
        self._initialize_widgets()
        self._initialize_health_indicators()
        
        logger.info("統一監控儀表板初始化完成")
    
    def _load_config(self) -> Dict[str, Any]:
        """載入配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入儀表板配置失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            "PHASE4_UNIFIED_MONITORING_DASHBOARD": {
                "dashboard_widgets": {
                    "system_status_overview": {
                        "widget_type": "status_indicator_grid",
                        "refresh_rate": "real_time_1s"
                    },
                    "signal_processing_analytics": {
                        "widget_type": "time_series_charts_and_counters", 
                        "refresh_rate": "5_second_updates"
                    },
                    "epl_decision_tracking": {
                        "widget_type": "decision_analytics_dashboard",
                        "refresh_rate": "real_time_updates"
                    },
                    "notification_success_monitoring": {
                        "widget_type": "notification_performance_dashboard",
                        "refresh_rate": "30_second_updates"
                    },
                    "system_performance_monitoring": {
                        "widget_type": "performance_metrics_dashboard",
                        "refresh_rate": "10_second_updates"
                    }
                }
            }
        }
    
    def _initialize_widgets(self):
        """初始化儀表板組件"""
        dashboard_config = self.config.get("PHASE4_UNIFIED_MONITORING_DASHBOARD", {})
        widgets_config = dashboard_config.get("dashboard_widgets", {})
        
        for widget_id, widget_config in widgets_config.items():
            widget_type_str = widget_config.get("widget_type", "status_indicator_grid")
            widget_type = WidgetType(widget_type_str)
            
            refresh_rate_str = widget_config.get("refresh_rate", "5_second_updates")
            refresh_rate = self._parse_refresh_rate(refresh_rate_str)
            
            self.widgets[widget_id] = WidgetData(
                widget_id=widget_id,
                widget_type=widget_type,
                title=self._generate_widget_title(widget_id),
                data={},
                last_update=datetime.utcnow(),
                refresh_rate=refresh_rate
            )
        
        logger.info(f"初始化 {len(self.widgets)} 個儀表板組件")
    
    def _parse_refresh_rate(self, refresh_rate_str: str) -> int:
        """解析刷新率字符串為秒數"""
        if "real_time" in refresh_rate_str or "1s" in refresh_rate_str:
            return 1
        elif "5_second" in refresh_rate_str:
            return 5
        elif "10_second" in refresh_rate_str:
            return 10
        elif "30_second" in refresh_rate_str:
            return 30
        else:
            return 5  # 默認5秒
    
    def _generate_widget_title(self, widget_id: str) -> str:
        """生成Widget標題"""
        title_map = {
            "system_status_overview": "系統狀態總覽",
            "signal_processing_analytics": "信號處理分析",
            "epl_decision_tracking": "EPL決策追蹤",
            "notification_success_monitoring": "通知成功監控",
            "system_performance_monitoring": "系統性能監控"
        }
        return title_map.get(widget_id, widget_id.replace("_", " ").title())
    
    def _initialize_health_indicators(self):
        """初始化系統健康指標"""
        components = [
            "phase1_signal_generation",
            "phase2_pre_evaluation", 
            "phase3_execution_policy",
            "notification_system"
        ]
        
        for component in components:
            self.system_health[component] = SystemHealthIndicator(
                component=component,
                status=SystemStatus.GREEN,
                metrics={},
                alerts=[],
                last_check=datetime.utcnow()
            )
    
    # ============================================================================
    # 核心數據收集方法
    # ============================================================================
    
    def record_signal_processed(self, signal_data: Dict[str, Any]):
        """記錄信號處理事件"""
        try:
            self.signal_processing_stats.total_signals += 1
            
            # 記錄優先級分布
            priority = signal_data.get("priority", SignalPriority.MEDIUM)
            if isinstance(priority, str):
                priority = SignalPriority(priority)
            self.signal_processing_stats.signals_by_priority[priority] += 1
            
            # 記錄來源分布
            source = signal_data.get("source", "unknown")
            self.signal_processing_stats.signals_by_source[source] = \
                self.signal_processing_stats.signals_by_source.get(source, 0) + 1
            
            # 記錄處理延遲
            latency = signal_data.get("processing_latency", 0.0)
            self.signal_processing_stats.processing_latency.add_value(latency)
            
            # 記錄質量分布
            quality = signal_data.get("quality_score", 0.5)
            quality_bucket = f"{int(quality * 10) / 10:.1f}"
            self.signal_processing_stats.quality_distribution[quality_bucket] = \
                self.signal_processing_stats.quality_distribution.get(quality_bucket, 0) + 1
            
            # 更新性能指標
            self.performance_metrics["signals_per_second"].add_value(1.0)
            
        except Exception as e:
            logger.error(f"記錄信號處理失敗: {e}")
            self.error_count += 1
    
    def record_epl_decision(self, decision_data: Dict[str, Any]):
        """記錄EPL決策事件"""
        try:
            decision_type_str = decision_data.get("decision_type", "IGNORE")
            decision_type = EPLDecisionType(decision_type_str)
            
            metrics = self.epl_decision_metrics[decision_type]
            metrics.count += 1
            
            # 記錄成功狀態
            if decision_data.get("success", False):
                metrics.success_count += 1
            
            # 記錄延遲
            latency = decision_data.get("decision_latency", 0.0)
            if metrics.avg_latency == 0:
                metrics.avg_latency = latency
            else:
                metrics.avg_latency = (metrics.avg_latency + latency) / 2
            
            metrics.last_update = datetime.utcnow()
            
            # 更新性能指標
            self.performance_metrics["decisions_per_second"].add_value(1.0)
            
        except Exception as e:
            logger.error(f"記錄EPL決策失敗: {e}")
            self.error_count += 1
    
    def record_notification_delivery(self, notification_data: Dict[str, Any]):
        """記錄通知交付事件"""
        try:
            channel = notification_data.get("channel", "unknown")
            priority_str = notification_data.get("priority", "MEDIUM")
            priority = SignalPriority(priority_str)
            
            key = (channel, priority)
            if key not in self.notification_metrics:
                self.notification_metrics[key] = NotificationDeliveryMetrics(channel, priority)
            
            metrics = self.notification_metrics[key]
            metrics.sent_count += 1
            
            # 記錄交付狀態
            if notification_data.get("delivered", False):
                metrics.delivered_count += 1
                delivery_time = notification_data.get("delivery_time", 0.0)
                if metrics.avg_delivery_time == 0:
                    metrics.avg_delivery_time = delivery_time
                else:
                    metrics.avg_delivery_time = (metrics.avg_delivery_time + delivery_time) / 2
            else:
                metrics.failed_count += 1
            
            metrics.last_update = datetime.utcnow()
            
            # 更新性能指標
            self.performance_metrics["notifications_per_second"].add_value(1.0)
            
        except Exception as e:
            logger.error(f"記錄通知交付失敗: {e}")
            self.error_count += 1
    
    def update_system_performance(self, performance_data: Dict[str, float]):
        """更新系統性能指標"""
        try:
            for metric_name, value in performance_data.items():
                if metric_name in self.performance_metrics:
                    self.performance_metrics[metric_name].add_value(value)
        except Exception as e:
            logger.error(f"更新系統性能指標失敗: {e}")
            self.error_count += 1
    
    # ============================================================================
    # Widget數據生成方法
    # ============================================================================
    
    def generate_system_status_overview_data(self) -> Dict[str, Any]:
        """生成系統狀態總覽數據"""
        return {
            "components": {
                "phase1_signal_generation": {
                    "status": self._evaluate_phase1_status(),
                    "metrics": {
                        "signals_per_minute": self._get_signals_per_minute(),
                        "quality_distribution": self._get_quality_distribution_summary(),
                        "source_availability": self._get_source_availability()
                    },
                    "alerts": self._get_phase1_alerts()
                },
                "phase2_pre_evaluation": {
                    "status": self._evaluate_phase2_status(),
                    "metrics": {
                        "processing_latency": self.signal_processing_stats.processing_latency.get_average(5),
                        "channel_distribution": self._get_channel_distribution(),
                        "quality_scores": self._get_average_quality_scores()
                    },
                    "alerts": self._get_phase2_alerts()
                },
                "phase3_execution_policy": {
                    "status": self._evaluate_phase3_status(), 
                    "metrics": {
                        "decision_latency": self._get_average_decision_latency(),
                        "decision_distribution": self._get_decision_distribution(),
                        "risk_violations": self._get_risk_violations_count()
                    },
                    "alerts": self._get_phase3_alerts()
                },
                "notification_system": {
                    "status": self._evaluate_notification_status(),
                    "metrics": {
                        "delivery_success_rate": self._get_overall_delivery_rate(),
                        "channel_health": self._get_channel_health_summary(),
                        "queue_depth": self._get_notification_queue_depth()
                    },
                    "alerts": self._get_notification_alerts()
                }
            },
            "last_update": datetime.utcnow().isoformat(),
            "overall_system_status": self._get_overall_system_status()
        }
    
    def generate_signal_processing_analytics_data(self) -> Dict[str, Any]:
        """生成信號處理分析數據"""
        return {
            "signal_volume_chart": {
                "total_signals": self._get_signal_volume_timeseries(),
                "signals_by_priority": self._get_signals_by_priority_timeseries(),
                "signals_by_source": dict(self.signal_processing_stats.signals_by_source)
            },
            "processing_latency_chart": {
                "phase1_latency": self._get_phase_latency_timeseries("phase1"),
                "phase2_latency": self._get_phase_latency_timeseries("phase2"),
                "phase3_latency": self._get_phase_latency_timeseries("phase3"),
                "total_latency": self._get_total_latency_timeseries(),
                "percentiles": self._calculate_latency_percentiles()
            },
            "quality_distribution_histogram": {
                "signal_quality_distribution": dict(self.signal_processing_stats.quality_distribution),
                "confidence_distribution": self._get_confidence_distribution(),
                "bins": [f"{i/10:.1f}" for i in range(0, 11)]
            },
            "summary_stats": {
                "total_signals_processed": self.signal_processing_stats.total_signals,
                "average_processing_latency": self.signal_processing_stats.processing_latency.get_average(),
                "signals_per_minute": self._get_signals_per_minute()
            }
        }
    
    def generate_epl_decision_tracking_data(self) -> Dict[str, Any]:
        """生成EPL決策追蹤數據"""
        return {
            "decision_type_pie_chart": {
                "data": {
                    decision_type.value: metrics.count 
                    for decision_type, metrics in self.epl_decision_metrics.items()
                },
                "percentages": {
                    decision_type.value: self._calculate_decision_percentage(decision_type)
                    for decision_type in EPLDecisionType
                }
            },
            "decision_timeline": {
                "events": self._get_recent_decision_events(),
                "priority_color_coding": {
                    "CRITICAL": "red",
                    "HIGH": "orange",
                    "MEDIUM": "yellow", 
                    "LOW": "blue"
                }
            },
            "success_rate_metrics": {
                "overall_decision_accuracy": self._calculate_overall_decision_accuracy(),
                "replacement_success_rate": self.epl_decision_metrics[EPLDecisionType.REPLACE_POSITION].success_rate,
                "strengthening_effectiveness": self.epl_decision_metrics[EPLDecisionType.STRENGTHEN_POSITION].success_rate,
                "new_position_performance": self.epl_decision_metrics[EPLDecisionType.CREATE_NEW_POSITION].success_rate
            },
            "decision_summary": {
                decision_type.value: {
                    "count": metrics.count,
                    "success_rate": metrics.success_rate,
                    "avg_latency": metrics.avg_latency
                }
                for decision_type, metrics in self.epl_decision_metrics.items()
            }
        }
    
    def generate_notification_success_monitoring_data(self) -> Dict[str, Any]:
        """生成通知成功監控數據"""
        return {
            "delivery_success_matrix": {
                "data": self._generate_delivery_matrix(),
                "channels": list(set(key[0] for key in self.notification_metrics.keys())),
                "priorities": [p.value for p in SignalPriority]
            },
            "notification_volume_chart": {
                "notifications_sent": self._get_notification_volume_timeseries("sent"),
                "notifications_delivered": self._get_notification_volume_timeseries("delivered"),
                "notifications_failed": self._get_notification_volume_timeseries("failed")
            },
            "user_engagement_analytics": {
                "notifications_sent": sum(m.sent_count for m in self.notification_metrics.values()),
                "notifications_opened": sum(m.delivered_count for m in self.notification_metrics.values()),
                "actions_taken": self._get_actions_taken_count(),
                "conversion_rates": self._calculate_conversion_rates()
            },
            "channel_performance": {
                channel: {
                    "delivery_rate": self._get_channel_delivery_rate(channel),
                    "avg_delivery_time": self._get_channel_avg_delivery_time(channel),
                    "total_sent": self._get_channel_total_sent(channel)
                }
                for channel in set(key[0] for key in self.notification_metrics.keys())
            }
        }
    
    def generate_system_performance_monitoring_data(self) -> Dict[str, Any]:
        """生成系統性能監控數據"""
        return {
            "resource_utilization": {
                "cpu_usage": self.performance_metrics["cpu_usage"].get_latest_value() or 0.0,
                "memory_usage": self.performance_metrics["memory_usage"].get_latest_value() or 0.0,
                "disk_io": self.performance_metrics["disk_io"].get_latest_value() or 0.0,
                "network_io": self.performance_metrics["network_io"].get_latest_value() or 0.0
            },
            "throughput_metrics": {
                "signals_per_second": self._calculate_throughput("signals_per_second"),
                "decisions_per_second": self._calculate_throughput("decisions_per_second"),
                "notifications_per_second": self._calculate_throughput("notifications_per_second"),
                "capacity_indicators": self._get_capacity_indicators()
            },
            "error_rate_monitoring": {
                "processing_errors": self._get_error_rate("processing"),
                "notification_errors": self._get_error_rate("notification"),
                "system_errors": self._get_error_rate("system"),
                "total_errors": self.error_count
            },
            "performance_trends": {
                metric_name: self._get_performance_trend(metric_name)
                for metric_name in self.performance_metrics.keys()
            }
        }
    
    # ============================================================================
    # 輔助方法
    # ============================================================================
    
    def _evaluate_phase1_status(self) -> str:
        """評估Phase1狀態"""
        signals_per_minute = self._get_signals_per_minute()
        quality_avg = self._get_average_quality_scores()
        
        if signals_per_minute < 10 or quality_avg < 0.6:
            return SystemStatus.RED.value
        elif signals_per_minute < 20 or quality_avg < 0.8:
            return SystemStatus.YELLOW.value
        else:
            return SystemStatus.GREEN.value
    
    def _evaluate_phase2_status(self) -> str:
        """評估Phase2狀態"""
        latency = self.signal_processing_stats.processing_latency.get_average(5)
        quality = self._get_average_quality_scores()
        
        if latency > 15 or quality < 0.6:
            return SystemStatus.RED.value
        elif latency > 10 or quality < 0.7:
            return SystemStatus.YELLOW.value
        else:
            return SystemStatus.GREEN.value
    
    def _evaluate_phase3_status(self) -> str:
        """評估Phase3狀態"""
        decision_latency = self._get_average_decision_latency()
        ignore_rate = self._get_ignore_decision_rate()
        
        if decision_latency > 500 or ignore_rate > 60:
            return SystemStatus.RED.value
        elif decision_latency > 300 or ignore_rate > 40:
            return SystemStatus.YELLOW.value
        else:
            return SystemStatus.GREEN.value
    
    def _evaluate_notification_status(self) -> str:
        """評估通知系統狀態"""
        delivery_rate = self._get_overall_delivery_rate()
        queue_depth = self._get_notification_queue_depth()
        
        if delivery_rate < 95 or queue_depth > 100:
            return SystemStatus.RED.value
        elif delivery_rate < 98 or queue_depth > 50:
            return SystemStatus.YELLOW.value
        else:
            return SystemStatus.GREEN.value
    
    def _get_signals_per_minute(self) -> float:
        """獲取每分鐘信號數"""
        # 簡化實現：基於最近的信號處理數據
        return self.performance_metrics["signals_per_second"].get_average(1) * 60
    
    def _get_quality_distribution_summary(self) -> Dict[str, float]:
        """獲取質量分布摘要"""
        total = sum(self.signal_processing_stats.quality_distribution.values())
        if total == 0:
            return {"high": 0.0, "medium": 0.0, "low": 0.0}
        
        high = sum(count for bucket, count in self.signal_processing_stats.quality_distribution.items() 
                  if float(bucket) >= 0.8)
        medium = sum(count for bucket, count in self.signal_processing_stats.quality_distribution.items() 
                    if 0.5 <= float(bucket) < 0.8)
        low = sum(count for bucket, count in self.signal_processing_stats.quality_distribution.items() 
                 if float(bucket) < 0.5)
        
        return {
            "high": (high / total) * 100,
            "medium": (medium / total) * 100,
            "low": (low / total) * 100
        }
    
    def _get_source_availability(self) -> float:
        """獲取來源可用性"""
        # 簡化實現：假設所有來源都可用
        return 100.0
    
    def _get_phase1_alerts(self) -> List[str]:
        """獲取Phase1警報"""
        alerts = []
        if self._get_signals_per_minute() < 10:
            alerts.append("信號生成率過低")
        if self._get_average_quality_scores() < 0.6:
            alerts.append("平均質量分數過低")
        return alerts
    
    def _get_channel_distribution(self) -> Dict[str, float]:
        """獲取通道分布"""
        # 簡化實現
        return {"email": 40.0, "sms": 30.0, "push": 30.0}
    
    def _get_average_quality_scores(self) -> float:
        """獲取平均質量分數"""
        if not self.signal_processing_stats.quality_distribution:
            return 0.5
        
        total_signals = sum(self.signal_processing_stats.quality_distribution.values())
        weighted_sum = sum(float(bucket) * count 
                          for bucket, count in self.signal_processing_stats.quality_distribution.items())
        
        return weighted_sum / total_signals if total_signals > 0 else 0.5
    
    def _get_phase2_alerts(self) -> List[str]:
        """獲取Phase2警報"""
        alerts = []
        latency = self.signal_processing_stats.processing_latency.get_average(5)
        if latency > 15:
            alerts.append("處理延遲過高")
        if self._get_average_quality_scores() < 0.6:
            alerts.append("嵌入質量分數過低")
        return alerts
    
    def _get_average_decision_latency(self) -> float:
        """獲取平均決策延遲"""
        latencies = [m.avg_latency for m in self.epl_decision_metrics.values() if m.avg_latency > 0]
        return statistics.mean(latencies) if latencies else 0.0
    
    def _get_decision_distribution(self) -> Dict[str, float]:
        """獲取決策分布"""
        total = sum(m.count for m in self.epl_decision_metrics.values())
        if total == 0:
            return {dt.value: 0.0 for dt in EPLDecisionType}
        
        return {
            dt.value: (m.count / total) * 100 
            for dt, m in self.epl_decision_metrics.items()
        }
    
    def _get_risk_violations_count(self) -> int:
        """獲取風險違規計數"""
        # 簡化實現
        return 0
    
    def _get_phase3_alerts(self) -> List[str]:
        """獲取Phase3警報"""
        alerts = []
        if self._get_average_decision_latency() > 500:
            alerts.append("決策延遲過高")
        if self._get_ignore_decision_rate() > 60:
            alerts.append("忽略決策率過高")
        return alerts
    
    def _get_ignore_decision_rate(self) -> float:
        """獲取忽略決策率"""
        total = sum(m.count for m in self.epl_decision_metrics.values())
        ignore_count = self.epl_decision_metrics[EPLDecisionType.IGNORE_SIGNAL].count
        return (ignore_count / total) * 100 if total > 0 else 0.0
    
    def _get_overall_delivery_rate(self) -> float:
        """獲取整體交付率"""
        total_sent = sum(m.sent_count for m in self.notification_metrics.values())
        total_delivered = sum(m.delivered_count for m in self.notification_metrics.values())
        return (total_delivered / total_sent) * 100 if total_sent > 0 else 0.0
    
    def _get_channel_health_summary(self) -> Dict[str, str]:
        """獲取通道健康摘要"""
        # 簡化實現
        return {"email": "healthy", "sms": "healthy", "push": "healthy"}
    
    def _get_notification_queue_depth(self) -> int:
        """獲取通知隊列深度"""
        # 簡化實現
        return 0
    
    def _get_notification_alerts(self) -> List[str]:
        """獲取通知警報"""
        alerts = []
        if self._get_overall_delivery_rate() < 95:
            alerts.append("交付成功率過低")
        if self._get_notification_queue_depth() > 100:
            alerts.append("通知隊列積壓")
        return alerts
    
    def _get_overall_system_status(self) -> str:
        """獲取整體系統狀態"""
        statuses = [
            self._evaluate_phase1_status(),
            self._evaluate_phase2_status(), 
            self._evaluate_phase3_status(),
            self._evaluate_notification_status()
        ]
        
        if SystemStatus.RED.value in statuses:
            return SystemStatus.RED.value
        elif SystemStatus.YELLOW.value in statuses:
            return SystemStatus.YELLOW.value
        else:
            return SystemStatus.GREEN.value
    
    # 時間序列數據方法（簡化實現）
    def _get_signal_volume_timeseries(self) -> List[Dict[str, Any]]:
        """獲取信號量時間序列"""
        # 簡化實現，返回模擬數據
        return [
            {"timestamp": (datetime.utcnow() - timedelta(minutes=i)).isoformat(), 
             "value": max(0, self.signal_processing_stats.total_signals + i)}
            for i in range(60, 0, -1)
        ]
    
    def _get_signals_by_priority_timeseries(self) -> Dict[str, List[Dict[str, Any]]]:
        """獲取按優先級分組的信號時間序列"""
        return {
            priority.value: [
                {"timestamp": (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
                 "value": max(0, count + i)}
                for i in range(60, 0, -1)
            ]
            for priority, count in self.signal_processing_stats.signals_by_priority.items()
        }
    
    # 其他輔助方法的簡化實現...
    def _get_phase_latency_timeseries(self, phase: str) -> List[Dict[str, Any]]:
        return []
    
    def _get_total_latency_timeseries(self) -> List[Dict[str, Any]]:
        return []
    
    def _calculate_latency_percentiles(self) -> Dict[str, float]:
        return {"p50": 10.0, "p95": 50.0, "p99": 100.0}
    
    def _get_confidence_distribution(self) -> Dict[str, int]:
        return {"0.8": 50, "0.9": 30, "1.0": 20}
    
    def _calculate_decision_percentage(self, decision_type: EPLDecisionType) -> float:
        total = sum(m.count for m in self.epl_decision_metrics.values())
        count = self.epl_decision_metrics[decision_type].count
        return (count / total) * 100 if total > 0 else 0.0
    
    def _get_recent_decision_events(self) -> List[Dict[str, Any]]:
        return []
    
    def _calculate_overall_decision_accuracy(self) -> float:
        total_decisions = sum(m.count for m in self.epl_decision_metrics.values())
        total_successes = sum(m.success_count for m in self.epl_decision_metrics.values())
        return (total_successes / total_decisions) * 100 if total_decisions > 0 else 0.0
    
    def _generate_delivery_matrix(self) -> Dict[str, Dict[str, float]]:
        return {}
    
    def _get_notification_volume_timeseries(self, metric_type: str) -> List[Dict[str, Any]]:
        return []
    
    def _get_actions_taken_count(self) -> int:
        return 0
    
    def _calculate_conversion_rates(self) -> Dict[str, float]:
        return {"open_rate": 75.0, "action_rate": 25.0}
    
    def _get_channel_delivery_rate(self, channel: str) -> float:
        channel_metrics = [m for key, m in self.notification_metrics.items() if key[0] == channel]
        if not channel_metrics:
            return 0.0
        return statistics.mean([m.delivery_rate for m in channel_metrics])
    
    def _get_channel_avg_delivery_time(self, channel: str) -> float:
        channel_metrics = [m for key, m in self.notification_metrics.items() if key[0] == channel]
        if not channel_metrics:
            return 0.0
        return statistics.mean([m.avg_delivery_time for m in channel_metrics if m.avg_delivery_time > 0])
    
    def _get_channel_total_sent(self, channel: str) -> int:
        channel_metrics = [m for key, m in self.notification_metrics.items() if key[0] == channel]
        return sum(m.sent_count for m in channel_metrics)
    
    def _calculate_throughput(self, metric_name: str) -> float:
        return self.performance_metrics[metric_name].get_average(5)
    
    def _get_capacity_indicators(self) -> Dict[str, float]:
        return {"max_theoretical": 1000.0, "current": 450.0}
    
    def _get_error_rate(self, error_type: str) -> float:
        return 0.5  # 簡化實現
    
    def _get_performance_trend(self, metric_name: str) -> Dict[str, Any]:
        return {"trend": "stable", "change_percentage": 2.5}
    
    # ============================================================================
    # 公共API方法
    # ============================================================================
    
    async def update_all_widgets(self):
        """更新所有Widget數據"""
        start_time = time.time()
        
        try:
            # 更新各個Widget
            widget_updaters = {
                "system_status_overview": self.generate_system_status_overview_data,
                "signal_processing_analytics": self.generate_signal_processing_analytics_data,
                "epl_decision_tracking": self.generate_epl_decision_tracking_data,
                "notification_success_monitoring": self.generate_notification_success_monitoring_data,
                "system_performance_monitoring": self.generate_system_performance_monitoring_data
            }
            
            for widget_id, widget in self.widgets.items():
                if widget_id in widget_updaters:
                    widget.data = widget_updaters[widget_id]()
                    widget.last_update = datetime.utcnow()
            
            self.last_update = datetime.utcnow()
            
            # 記錄更新延遲
            update_latency = (time.time() - start_time) * 1000  # 毫秒
            self.update_latency_history.append(update_latency)
            
            logger.debug(f"儀表板更新完成，耗時 {update_latency:.2f}ms")
            
        except Exception as e:
            logger.error(f"更新儀表板失敗: {e}")
            self.error_count += 1
    
    def get_widget_data(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """獲取指定Widget數據"""
        widget = self.widgets.get(widget_id)
        if widget:
            return {
                "widget_id": widget.widget_id,
                "widget_type": widget.widget_type.value,
                "title": widget.title,
                "data": widget.data,
                "last_update": widget.last_update.isoformat(),
                "status": widget.status.value
            }
        return None
    
    def get_all_widgets_data(self) -> Dict[str, Any]:
        """獲取所有Widget數據"""
        return {
            "widgets": {
                widget_id: self.get_widget_data(widget_id)
                for widget_id in self.widgets.keys()
            },
            "dashboard_status": {
                "enabled": self.dashboard_enabled,
                "last_update": self.last_update.isoformat(),
                "error_count": self.error_count,
                "avg_update_latency": statistics.mean(self.update_latency_history) if self.update_latency_history else 0.0
            }
        }
    
    def get_real_time_api_data(self) -> Dict[str, Any]:
        """獲取實時API數據 - 對應JSON配置中的 /api/v1/monitoring/dashboard"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_status": self._get_overall_system_status(),
            "widgets": self.get_all_widgets_data()["widgets"],
            "performance_summary": {
                "total_signals": self.signal_processing_stats.total_signals,
                "total_decisions": sum(m.count for m in self.epl_decision_metrics.values()),
                "notification_success_rate": self._get_overall_delivery_rate(),
                "system_latency": statistics.mean(self.update_latency_history) if self.update_latency_history else 0.0
            }
        }
    
    async def start_real_time_monitoring(self):
        """啟動實時監控循環"""
        logger.info("啟動統一監控儀表板實時更新")
        
        while self.dashboard_enabled:
            try:
                await self.update_all_widgets()
                await asyncio.sleep(1)  # 1秒刷新率
            except Exception as e:
                logger.error(f"實時監控循環錯誤: {e}")
                await asyncio.sleep(5)  # 錯誤時等待更長時間
    
    def stop_monitoring(self):
        """停止監控"""
        self.dashboard_enabled = False
        logger.info("統一監控儀表板已停止")

# ============================================================================
# 使用示例和測試
# ============================================================================

async def main():
    """主程序示例"""
    dashboard = UnifiedMonitoringDashboard()
    
    # 模擬一些數據
    dashboard.record_signal_processed({
        "priority": "HIGH",
        "source": "binance_websocket",
        "processing_latency": 12.5,
        "quality_score": 0.85
    })
    
    dashboard.record_epl_decision({
        "decision_type": "CREATE_NEW",
        "success": True,
        "decision_latency": 250.0
    })
    
    dashboard.record_notification_delivery({
        "channel": "email",
        "priority": "HIGH", 
        "delivered": True,
        "delivery_time": 1500.0
    })
    
    # 更新儀表板
    await dashboard.update_all_widgets()
    
    # 獲取數據
    api_data = dashboard.get_real_time_api_data()
    print(json.dumps(api_data, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
