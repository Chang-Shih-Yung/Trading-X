"""
📬 Phase4 Notification Success Rate Monitoring
==============================================

通知成功率監控實現 - 基於配置驅動的多通道通知效果追蹤
與 notification_success_rate_monitoring_config.json 配置文件對應
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

class NotificationChannel(Enum):
    """通知通道類型"""
    GMAIL = "gmail"
    WEBSOCKET = "websocket"
    FRONTEND = "frontend"
    SMS = "sms"
    TELEGRAM = "telegram"
    DISCORD = "discord"

class NotificationPriority(Enum):
    """通知優先級"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class NotificationStatus(Enum):
    """通知狀態"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"

@dataclass
class NotificationRecord:
    """通知記錄"""
    notification_id: str
    timestamp: datetime
    channel: NotificationChannel
    priority: NotificationPriority
    recipient_id: str
    content_type: str
    status: NotificationStatus
    delivery_latency: Optional[float] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    engagement_data: Optional[Dict[str, Any]] = None

@dataclass
class ChannelMetrics:
    """通道指標"""
    channel: NotificationChannel
    total_sent: int
    successful_deliveries: int
    failed_deliveries: int
    bounced_deliveries: int
    opened_notifications: int
    clicked_notifications: int
    average_delivery_time: float
    success_rate: float
    engagement_rate: float

class NotificationSuccessRateMonitor:
    """通知成功率監控系統"""
    
    def __init__(self):
        # 載入配置文件
        self.config = self._load_config()
        
        # 通知記錄存儲
        self.notification_history: deque = deque(maxlen=100000)  # 保留最近100000條通知
        self.channel_metrics: Dict[str, ChannelMetrics] = {}
        
        # 實時統計
        self.hourly_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.daily_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # 性能監控
        self.monitoring_enabled = True
        self.last_update = datetime.now()
        
        # 警報設置
        self.alert_thresholds = {
            "success_rate_warning": 0.9,
            "success_rate_critical": 0.8,
            "delivery_latency_warning": 5000,  # 5秒
            "delivery_latency_critical": 10000  # 10秒
        }
        
        # 初始化監控系統
        self._initialize_monitoring()
        
    def _load_config(self) -> Dict[str, Any]:
        """載入配置文件"""
        try:
            config_path = Path(__file__).parent / "notification_success_rate_monitoring_config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入通知監控配置失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            "PHASE4_NOTIFICATION_SUCCESS_RATE_MONITORING": {
                "channel_monitoring": {
                    "gmail_delivery_tracking": {"enable_open_tracking": True, "enable_click_tracking": True},
                    "websocket_connection_monitoring": {"connection_timeout": 30},
                    "frontend_notification_analytics": {"user_interaction_tracking": True},
                    "sms_delivery_confirmation": {"enable_delivery_receipts": True}
                },
                "success_rate_analysis": {
                    "calculation_windows": ["1_hour", "24_hours", "7_days"],
                    "alert_thresholds": {"warning": 0.9, "critical": 0.8}
                }
            }
        }
    
    def _initialize_monitoring(self):
        """初始化監控系統"""
        logger.info("初始化通知成功率監控系統")
        
        # 初始化通道指標
        for channel in NotificationChannel:
            self.channel_metrics[channel.value] = ChannelMetrics(
                channel=channel,
                total_sent=0,
                successful_deliveries=0,
                failed_deliveries=0,
                bounced_deliveries=0,
                opened_notifications=0,
                clicked_notifications=0,
                average_delivery_time=0.0,
                success_rate=0.0,
                engagement_rate=0.0
            )
        
        # 清理過舊的數據
        self._cleanup_old_records()
        
    def _cleanup_old_records(self):
        """清理過舊的記錄"""
        cutoff_time = datetime.now() - timedelta(days=30)  # 保留30天數據
        
        # 清理通知歷史
        self.notification_history = deque(
            [record for record in self.notification_history 
             if record.timestamp > cutoff_time],
            maxlen=100000
        )
        
    async def record_notification_sent(self, notification_data: Dict[str, Any]) -> str:
        """記錄發送的通知"""
        try:
            # 生成通知ID
            notification_id = f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{notification_data.get('channel', 'unknown')}"
            
            # 創建通知記錄
            record = NotificationRecord(
                notification_id=notification_id,
                timestamp=datetime.fromisoformat(notification_data.get('timestamp', datetime.now().isoformat())),
                channel=NotificationChannel(notification_data.get('channel', 'websocket')),
                priority=NotificationPriority(notification_data.get('priority', 'MEDIUM')),
                recipient_id=notification_data.get('recipient_id', 'unknown'),
                content_type=notification_data.get('content_type', 'signal'),
                status=NotificationStatus.SENT,
                retry_count=0
            )
            
            # 添加到歷史記錄
            self.notification_history.append(record)
            
            # 更新實時統計
            self._update_real_time_stats(record, "sent")
            
            # 更新通道指標
            self._update_channel_metrics(record.channel.value, "sent")
            
            self.last_update = datetime.now()
            
            logger.info(f"記錄通知發送: {notification_id}, 通道: {record.channel.value}")
            return notification_id
            
        except Exception as e:
            logger.error(f"記錄通知發送失敗: {e}")
            return ""
    
    async def update_notification_status(self, notification_id: str, status_data: Dict[str, Any]) -> bool:
        """更新通知狀態"""
        try:
            # 查找通知記錄
            record = self._find_notification_by_id(notification_id)
            if not record:
                logger.warning(f"未找到通知記錄: {notification_id}")
                return False
            
            # 更新狀態
            new_status = NotificationStatus(status_data.get('status', 'failed'))
            old_status = record.status
            record.status = new_status
            
            # 更新其他字段
            if 'delivery_latency' in status_data:
                record.delivery_latency = float(status_data['delivery_latency'])
            
            if 'retry_count' in status_data:
                record.retry_count = int(status_data['retry_count'])
            
            if 'error_message' in status_data:
                record.error_message = status_data['error_message']
            
            if 'engagement_data' in status_data:
                record.engagement_data = status_data['engagement_data']
            
            # 更新統計
            self._update_real_time_stats(record, new_status.value)
            self._update_channel_metrics(record.channel.value, new_status.value)
            
            logger.info(f"更新通知狀態: {notification_id}, {old_status.value} -> {new_status.value}")
            return True
            
        except Exception as e:
            logger.error(f"更新通知狀態失敗: {e}")
            return False
    
    def _find_notification_by_id(self, notification_id: str) -> Optional[NotificationRecord]:
        """根據ID查找通知記錄"""
        for record in self.notification_history:
            if record.notification_id == notification_id:
                return record
        return None
    
    def _update_real_time_stats(self, record: NotificationRecord, event_type: str):
        """更新實時統計"""
        current_hour = record.timestamp.replace(minute=0, second=0, microsecond=0)
        current_day = record.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 小時統計
        hour_key = current_hour.isoformat()
        self.hourly_stats[hour_key][f"{record.channel.value}_{event_type}"] += 1
        
        # 日統計
        day_key = current_day.isoformat()
        self.daily_stats[day_key][f"{record.channel.value}_{event_type}"] += 1
        
        # 限制記錄數量
        if len(self.hourly_stats) > 72:  # 保留72小時
            oldest_hour = min(self.hourly_stats.keys())
            del self.hourly_stats[oldest_hour]
            
        if len(self.daily_stats) > 60:  # 保留60天
            oldest_day = min(self.daily_stats.keys())
            del self.daily_stats[oldest_day]
    
    def _update_channel_metrics(self, channel: str, event_type: str):
        """更新通道指標"""
        if channel not in self.channel_metrics:
            return
        
        metrics = self.channel_metrics[channel]
        
        if event_type == "sent":
            metrics.total_sent += 1
        elif event_type == "delivered":
            metrics.successful_deliveries += 1
        elif event_type == "failed":
            metrics.failed_deliveries += 1
        elif event_type == "bounced":
            metrics.bounced_deliveries += 1
        elif event_type == "opened":
            metrics.opened_notifications += 1
        elif event_type == "clicked":
            metrics.clicked_notifications += 1
        
        # 重新計算成功率
        if metrics.total_sent > 0:
            metrics.success_rate = (metrics.successful_deliveries + metrics.opened_notifications) / metrics.total_sent
            metrics.engagement_rate = metrics.clicked_notifications / metrics.total_sent
    
    async def get_comprehensive_monitoring_report(self) -> Dict[str, Any]:
        """獲取綜合監控報告"""
        try:
            current_time = datetime.now()
            
            if not self.notification_history:
                return self._get_empty_report()
            
            # 基本統計
            total_notifications = len(self.notification_history)
            
            # 通道性能分析
            channel_analysis = self._analyze_channel_performance()
            
            # 成功率分析
            success_rate_analysis = self._analyze_success_rates()
            
            # 延遲分析
            latency_analysis = self._analyze_delivery_latency()
            
            # 參與度分析
            engagement_analysis = self._analyze_engagement_metrics()
            
            # 故障分析
            failure_analysis = self._analyze_failure_patterns()
            
            # 時間趨勢分析
            temporal_analysis = self._analyze_temporal_trends()
            
            # 警報狀態
            alert_status = self._check_alert_conditions()
            
            return {
                "monitoring_metadata": {
                    "generated_at": current_time.isoformat(),
                    "total_notifications_tracked": total_notifications,
                    "monitoring_period": {
                        "start": min(r.timestamp for r in self.notification_history).isoformat(),
                        "end": max(r.timestamp for r in self.notification_history).isoformat()
                    },
                    "last_update": self.last_update.isoformat()
                },
                "channel_performance_analysis": channel_analysis,
                "success_rate_breakdown": success_rate_analysis,
                "delivery_latency_insights": latency_analysis,
                "engagement_metrics_analysis": engagement_analysis,
                "failure_pattern_analysis": failure_analysis,
                "temporal_trend_analysis": temporal_analysis,
                "alert_status": alert_status,
                "optimization_recommendations": self._generate_optimization_recommendations()
            }
            
        except Exception as e:
            logger.error(f"生成綜合監控報告失敗: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def _get_empty_report(self) -> Dict[str, Any]:
        """獲取空報告"""
        return {
            "monitoring_metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_notifications_tracked": 0,
                "status": "no_data"
            },
            "message": "沒有足夠的通知數據生成報告"
        }
    
    def _analyze_channel_performance(self) -> Dict[str, Any]:
        """分析通道性能"""
        channel_stats = defaultdict(lambda: {
            "sent": 0, "delivered": 0, "failed": 0, "opened": 0, "clicked": 0,
            "delivery_times": [], "retry_counts": []
        })
        
        # 收集各通道統計
        for record in self.notification_history:
            channel = record.channel.value
            channel_stats[channel]["sent"] += 1
            
            if record.status == NotificationStatus.DELIVERED:
                channel_stats[channel]["delivered"] += 1
            elif record.status == NotificationStatus.FAILED:
                channel_stats[channel]["failed"] += 1
            elif record.status == NotificationStatus.OPENED:
                channel_stats[channel]["opened"] += 1
            elif record.status == NotificationStatus.CLICKED:
                channel_stats[channel]["clicked"] += 1
            
            if record.delivery_latency:
                channel_stats[channel]["delivery_times"].append(record.delivery_latency)
            
            channel_stats[channel]["retry_counts"].append(record.retry_count)
        
        # 計算各通道指標
        performance_summary = {}
        for channel, stats in channel_stats.items():
            total_sent = stats["sent"]
            if total_sent == 0:
                continue
            
            successful_deliveries = stats["delivered"] + stats["opened"] + stats["clicked"]
            
            performance_summary[channel] = {
                "total_notifications": total_sent,
                "success_rate": successful_deliveries / total_sent,
                "failure_rate": stats["failed"] / total_sent,
                "engagement_rate": stats["clicked"] / total_sent,
                "average_delivery_time": statistics.mean(stats["delivery_times"]) if stats["delivery_times"] else 0,
                "average_retry_count": statistics.mean(stats["retry_counts"]),
                "reliability_score": self._calculate_reliability_score(channel, stats)
            }
        
        # 排名分析
        if performance_summary:
            best_channel = max(performance_summary.items(), key=lambda x: x[1]["success_rate"])
            worst_channel = min(performance_summary.items(), key=lambda x: x[1]["success_rate"])
            
            return {
                "by_channel": performance_summary,
                "rankings": {
                    "best_performing": {"channel": best_channel[0], "success_rate": best_channel[1]["success_rate"]},
                    "worst_performing": {"channel": worst_channel[0], "success_rate": worst_channel[1]["success_rate"]},
                    "fastest_delivery": min(performance_summary.items(), key=lambda x: x[1]["average_delivery_time"])[0],
                    "highest_engagement": max(performance_summary.items(), key=lambda x: x[1]["engagement_rate"])[0]
                }
            }
        
        return {"by_channel": {}, "rankings": {}}
    
    def _calculate_reliability_score(self, channel: str, stats: Dict) -> float:
        """計算可靠性分數"""
        total_sent = stats["sent"]
        if total_sent == 0:
            return 0.0
        
        # 成功率權重：60%
        success_rate = (stats["delivered"] + stats["opened"] + stats["clicked"]) / total_sent
        success_weight = 0.6
        
        # 延遲權重：20%
        avg_latency = statistics.mean(stats["delivery_times"]) if stats["delivery_times"] else 1000
        latency_score = max(0, 1 - (avg_latency / 10000))  # 10秒為基準
        latency_weight = 0.2
        
        # 重試率權重：20%
        avg_retries = statistics.mean(stats["retry_counts"])
        retry_score = max(0, 1 - (avg_retries / 3))  # 3次重試為基準
        retry_weight = 0.2
        
        return (success_rate * success_weight + 
                latency_score * latency_weight + 
                retry_score * retry_weight)
    
    def _analyze_success_rates(self) -> Dict[str, Any]:
        """分析成功率"""
        # 按時間窗口分析成功率
        time_windows = {
            "1_hour": timedelta(hours=1),
            "24_hours": timedelta(hours=24),
            "7_days": timedelta(days=7)
        }
        
        success_rate_analysis = {}
        current_time = datetime.now()
        
        for window_name, window_duration in time_windows.items():
            cutoff_time = current_time - window_duration
            window_notifications = [
                record for record in self.notification_history
                if record.timestamp > cutoff_time
            ]
            
            if not window_notifications:
                success_rate_analysis[window_name] = {"success_rate": 0, "total_notifications": 0}
                continue
            
            successful = len([
                record for record in window_notifications
                if record.status in [NotificationStatus.DELIVERED, NotificationStatus.OPENED, NotificationStatus.CLICKED]
            ])
            
            total = len(window_notifications)
            success_rate = successful / total if total > 0 else 0
            
            success_rate_analysis[window_name] = {
                "success_rate": success_rate,
                "total_notifications": total,
                "successful_notifications": successful,
                "failed_notifications": total - successful
            }
        
        # 按優先級分析成功率
        priority_success_rates = defaultdict(lambda: {"successful": 0, "total": 0})
        
        for record in self.notification_history:
            priority = record.priority.value
            priority_success_rates[priority]["total"] += 1
            
            if record.status in [NotificationStatus.DELIVERED, NotificationStatus.OPENED, NotificationStatus.CLICKED]:
                priority_success_rates[priority]["successful"] += 1
        
        priority_analysis = {}
        for priority, stats in priority_success_rates.items():
            if stats["total"] > 0:
                priority_analysis[priority] = {
                    "success_rate": stats["successful"] / stats["total"],
                    "total_notifications": stats["total"]
                }
        
        return {
            "by_time_window": success_rate_analysis,
            "by_priority": priority_analysis,
            "overall_success_rate": self._calculate_overall_success_rate(),
            "success_rate_trend": self._calculate_success_rate_trend()
        }
    
    def _calculate_overall_success_rate(self) -> float:
        """計算整體成功率"""
        if not self.notification_history:
            return 0.0
        
        successful = len([
            record for record in self.notification_history
            if record.status in [NotificationStatus.DELIVERED, NotificationStatus.OPENED, NotificationStatus.CLICKED]
        ])
        
        return successful / len(self.notification_history)
    
    def _calculate_success_rate_trend(self) -> str:
        """計算成功率趨勢"""
        if len(self.notification_history) < 100:
            return "insufficient_data"
        
        # 比較最近的成功率與之前的成功率
        total_notifications = len(self.notification_history)
        split_point = total_notifications // 2
        
        recent_notifications = list(self.notification_history)[split_point:]
        older_notifications = list(self.notification_history)[:split_point]
        
        recent_success_rate = len([
            r for r in recent_notifications
            if r.status in [NotificationStatus.DELIVERED, NotificationStatus.OPENED, NotificationStatus.CLICKED]
        ]) / len(recent_notifications)
        
        older_success_rate = len([
            r for r in older_notifications
            if r.status in [NotificationStatus.DELIVERED, NotificationStatus.OPENED, NotificationStatus.CLICKED]
        ]) / len(older_notifications)
        
        if recent_success_rate > older_success_rate + 0.05:
            return "improving"
        elif recent_success_rate < older_success_rate - 0.05:
            return "declining"
        else:
            return "stable"
    
    def _analyze_delivery_latency(self) -> Dict[str, Any]:
        """分析投遞延遲"""
        delivery_times = [
            record.delivery_latency for record in self.notification_history
            if record.delivery_latency is not None
        ]
        
        if not delivery_times:
            return {"latency_analysis": "no_delivery_time_data"}
        
        # 基本統計
        latency_stats = {
            "average_latency": statistics.mean(delivery_times),
            "median_latency": statistics.median(delivery_times),
            "min_latency": min(delivery_times),
            "max_latency": max(delivery_times),
            "std_dev": statistics.stdev(delivery_times) if len(delivery_times) > 1 else 0
        }
        
        # 百分位數
        sorted_times = sorted(delivery_times)
        latency_stats.update({
            "p90_latency": sorted_times[int(0.9 * len(sorted_times))],
            "p95_latency": sorted_times[int(0.95 * len(sorted_times))],
            "p99_latency": sorted_times[int(0.99 * len(sorted_times))]
        })
        
        # 按通道分析延遲
        channel_latency = defaultdict(list)
        for record in self.notification_history:
            if record.delivery_latency:
                channel_latency[record.channel.value].append(record.delivery_latency)
        
        channel_latency_analysis = {}
        for channel, latencies in channel_latency.items():
            if latencies:
                channel_latency_analysis[channel] = {
                    "average_latency": statistics.mean(latencies),
                    "median_latency": statistics.median(latencies),
                    "max_latency": max(latencies)
                }
        
        return {
            "overall_latency_statistics": latency_stats,
            "by_channel": channel_latency_analysis,
            "latency_distribution": self._create_latency_distribution(delivery_times),
            "slow_delivery_alerts": [
                channel for channel, stats in channel_latency_analysis.items()
                if stats["average_latency"] > self.alert_thresholds["delivery_latency_warning"]
            ]
        }
    
    def _create_latency_distribution(self, delivery_times: List[float]) -> Dict[str, int]:
        """創建延遲分佈"""
        distribution = {
            "0-1s": 0, "1-2s": 0, "2-5s": 0, "5-10s": 0, "10s+": 0
        }
        
        for latency in delivery_times:
            if latency < 1000:
                distribution["0-1s"] += 1
            elif latency < 2000:
                distribution["1-2s"] += 1
            elif latency < 5000:
                distribution["2-5s"] += 1
            elif latency < 10000:
                distribution["5-10s"] += 1
            else:
                distribution["10s+"] += 1
        
        return distribution
    
    def _analyze_engagement_metrics(self) -> Dict[str, Any]:
        """分析參與度指標"""
        engagement_stats = {
            "total_notifications": len(self.notification_history),
            "opened_notifications": 0,
            "clicked_notifications": 0,
            "bounced_notifications": 0
        }
        
        channel_engagement = defaultdict(lambda: {"sent": 0, "opened": 0, "clicked": 0})
        
        for record in self.notification_history:
            channel = record.channel.value
            channel_engagement[channel]["sent"] += 1
            
            if record.status == NotificationStatus.OPENED:
                engagement_stats["opened_notifications"] += 1
                channel_engagement[channel]["opened"] += 1
            elif record.status == NotificationStatus.CLICKED:
                engagement_stats["clicked_notifications"] += 1
                channel_engagement[channel]["clicked"] += 1
            elif record.status == NotificationStatus.BOUNCED:
                engagement_stats["bounced_notifications"] += 1
        
        # 計算整體參與度
        total = engagement_stats["total_notifications"]
        if total > 0:
            engagement_stats.update({
                "open_rate": engagement_stats["opened_notifications"] / total,
                "click_through_rate": engagement_stats["clicked_notifications"] / total,
                "bounce_rate": engagement_stats["bounced_notifications"] / total
            })
        
        # 按通道計算參與度
        channel_engagement_analysis = {}
        for channel, stats in channel_engagement.items():
            if stats["sent"] > 0:
                channel_engagement_analysis[channel] = {
                    "open_rate": stats["opened"] / stats["sent"],
                    "click_through_rate": stats["clicked"] / stats["sent"],
                    "total_sent": stats["sent"]
                }
        
        return {
            "overall_engagement": engagement_stats,
            "by_channel": channel_engagement_analysis,
            "highest_engagement_channel": max(
                channel_engagement_analysis.items(), 
                key=lambda x: x[1]["click_through_rate"]
            )[0] if channel_engagement_analysis else None
        }
    
    def _analyze_failure_patterns(self) -> Dict[str, Any]:
        """分析故障模式"""
        failure_analysis = {
            "total_failures": 0,
            "failure_by_channel": defaultdict(int),
            "failure_by_priority": defaultdict(int),
            "common_error_messages": defaultdict(int),
            "retry_analysis": defaultdict(list)
        }
        
        for record in self.notification_history:
            if record.status == NotificationStatus.FAILED:
                failure_analysis["total_failures"] += 1
                failure_analysis["failure_by_channel"][record.channel.value] += 1
                failure_analysis["failure_by_priority"][record.priority.value] += 1
                
                if record.error_message:
                    failure_analysis["common_error_messages"][record.error_message] += 1
                
                failure_analysis["retry_analysis"][record.channel.value].append(record.retry_count)
        
        # 計算重試統計
        retry_statistics = {}
        for channel, retry_counts in failure_analysis["retry_analysis"].items():
            if retry_counts:
                retry_statistics[channel] = {
                    "average_retries": statistics.mean(retry_counts),
                    "max_retries": max(retry_counts),
                    "total_failed_notifications": len(retry_counts)
                }
        
        # 識別問題通道
        problem_channels = []
        total_notifications = len(self.notification_history)
        
        for channel, failure_count in failure_analysis["failure_by_channel"].items():
            channel_total = len([r for r in self.notification_history if r.channel.value == channel])
            failure_rate = failure_count / channel_total if channel_total > 0 else 0
            
            if failure_rate > 0.1:  # 失敗率超過10%
                problem_channels.append({
                    "channel": channel,
                    "failure_rate": failure_rate,
                    "total_failures": failure_count
                })
        
        return {
            "failure_summary": dict(failure_analysis["failure_by_channel"]),
            "failure_by_priority": dict(failure_analysis["failure_by_priority"]),
            "common_errors": dict(failure_analysis["common_error_messages"]),
            "retry_statistics": retry_statistics,
            "problem_channels": problem_channels,
            "overall_failure_rate": failure_analysis["total_failures"] / total_notifications if total_notifications > 0 else 0
        }
    
    def _analyze_temporal_trends(self) -> Dict[str, Any]:
        """分析時間趨勢"""
        # 按小時分析活動模式
        hourly_activity = defaultdict(int)
        hourly_success = defaultdict(int)
        
        for record in self.notification_history:
            hour = record.timestamp.hour
            hourly_activity[hour] += 1
            
            if record.status in [NotificationStatus.DELIVERED, NotificationStatus.OPENED, NotificationStatus.CLICKED]:
                hourly_success[hour] += 1
        
        # 計算各小時的成功率
        hourly_success_rates = {}
        for hour, total in hourly_activity.items():
            success_count = hourly_success.get(hour, 0)
            hourly_success_rates[hour] = success_count / total if total > 0 else 0
        
        # 找出最佳和最差時段
        if hourly_success_rates:
            best_hour = max(hourly_success_rates.items(), key=lambda x: x[1])
            worst_hour = min(hourly_success_rates.items(), key=lambda x: x[1])
        else:
            best_hour = worst_hour = None
        
        # 按天分析趨勢
        daily_trends = defaultdict(lambda: {"sent": 0, "successful": 0})
        
        for record in self.notification_history:
            day_key = record.timestamp.date().isoformat()
            daily_trends[day_key]["sent"] += 1
            
            if record.status in [NotificationStatus.DELIVERED, NotificationStatus.OPENED, NotificationStatus.CLICKED]:
                daily_trends[day_key]["successful"] += 1
        
        # 計算最近7天的趨勢
        recent_days = sorted(daily_trends.keys())[-7:]
        recent_success_rates = []
        
        for day in recent_days:
            day_data = daily_trends[day]
            success_rate = day_data["successful"] / day_data["sent"] if day_data["sent"] > 0 else 0
            recent_success_rates.append(success_rate)
        
        # 計算趨勢方向
        trend_direction = "stable"
        if len(recent_success_rates) >= 3:
            early_avg = statistics.mean(recent_success_rates[:len(recent_success_rates)//2])
            late_avg = statistics.mean(recent_success_rates[len(recent_success_rates)//2:])
            
            if late_avg > early_avg + 0.05:
                trend_direction = "improving"
            elif late_avg < early_avg - 0.05:
                trend_direction = "declining"
        
        return {
            "hourly_patterns": {
                "activity_by_hour": dict(hourly_activity),
                "success_rate_by_hour": hourly_success_rates,
                "best_performance_hour": f"{best_hour[0]:02d}:00" if best_hour else None,
                "worst_performance_hour": f"{worst_hour[0]:02d}:00" if worst_hour else None
            },
            "daily_trends": {
                "recent_7_days": [
                    {
                        "date": day,
                        "sent": daily_trends[day]["sent"],
                        "successful": daily_trends[day]["successful"],
                        "success_rate": daily_trends[day]["successful"] / daily_trends[day]["sent"] if daily_trends[day]["sent"] > 0 else 0
                    }
                    for day in recent_days
                ],
                "trend_direction": trend_direction
            }
        }
    
    def _check_alert_conditions(self) -> Dict[str, Any]:
        """檢查警報條件"""
        alerts = []
        current_time = datetime.now()
        
        # 檢查整體成功率
        overall_success_rate = self._calculate_overall_success_rate()
        
        if overall_success_rate < self.alert_thresholds["success_rate_critical"]:
            alerts.append({
                "type": "critical",
                "message": f"整體成功率過低: {overall_success_rate:.1%}",
                "threshold": self.alert_thresholds["success_rate_critical"],
                "current_value": overall_success_rate
            })
        elif overall_success_rate < self.alert_thresholds["success_rate_warning"]:
            alerts.append({
                "type": "warning",
                "message": f"整體成功率低於警告線: {overall_success_rate:.1%}",
                "threshold": self.alert_thresholds["success_rate_warning"],
                "current_value": overall_success_rate
            })
        
        # 檢查各通道成功率
        channel_stats = self._analyze_channel_performance()
        for channel, stats in channel_stats.get("by_channel", {}).items():
            success_rate = stats["success_rate"]
            
            if success_rate < self.alert_thresholds["success_rate_critical"]:
                alerts.append({
                    "type": "critical",
                    "message": f"通道 {channel} 成功率過低: {success_rate:.1%}",
                    "channel": channel,
                    "current_value": success_rate
                })
        
        # 檢查延遲
        recent_notifications = [
            r for r in self.notification_history
            if r.timestamp > current_time - timedelta(hours=1) and r.delivery_latency
        ]
        
        if recent_notifications:
            avg_latency = statistics.mean(r.delivery_latency for r in recent_notifications)
            
            if avg_latency > self.alert_thresholds["delivery_latency_critical"]:
                alerts.append({
                    "type": "critical",
                    "message": f"平均投遞延遲過高: {avg_latency:.0f}ms",
                    "threshold": self.alert_thresholds["delivery_latency_critical"],
                    "current_value": avg_latency
                })
        
        return {
            "alert_count": len(alerts),
            "critical_alerts": len([a for a in alerts if a["type"] == "critical"]),
            "warning_alerts": len([a for a in alerts if a["type"] == "warning"]),
            "alerts": alerts,
            "system_status": "critical" if any(a["type"] == "critical" for a in alerts) else "warning" if alerts else "healthy"
        }
    
    def _generate_optimization_recommendations(self) -> List[str]:
        """生成優化建議"""
        recommendations = []
        
        # 基於成功率分析
        channel_performance = self._analyze_channel_performance()
        if channel_performance.get("by_channel"):
            best_channel = max(channel_performance["by_channel"].items(), key=lambda x: x[1]["success_rate"])
            worst_channel = min(channel_performance["by_channel"].items(), key=lambda x: x[1]["success_rate"])
            
            if best_channel[1]["success_rate"] > 0.95:
                recommendations.append(f"通道 {best_channel[0]} 表現優異，建議優先使用此通道")
            
            if worst_channel[1]["success_rate"] < 0.8:
                recommendations.append(f"通道 {worst_channel[0]} 成功率較低，建議檢查配置或考慮替代方案")
        
        # 基於延遲分析
        latency_analysis = self._analyze_delivery_latency()
        if "slow_delivery_alerts" in latency_analysis and latency_analysis["slow_delivery_alerts"]:
            recommendations.append(f"以下通道延遲較高，建議優化: {', '.join(latency_analysis['slow_delivery_alerts'])}")
        
        # 基於參與度分析
        engagement_analysis = self._analyze_engagement_metrics()
        overall_engagement = engagement_analysis.get("overall_engagement", {})
        
        if overall_engagement.get("click_through_rate", 0) < 0.1:
            recommendations.append("點擊率較低，建議優化通知內容和呼叫行動")
        
        if overall_engagement.get("open_rate", 0) < 0.3:
            recommendations.append("開啟率較低，建議優化通知標題和發送時機")
        
        # 基於故障分析
        failure_analysis = self._analyze_failure_patterns()
        if failure_analysis.get("overall_failure_rate", 0) > 0.1:
            recommendations.append("整體失敗率較高，建議檢查系統穩定性和重試機制")
        
        return recommendations if recommendations else ["系統運行良好，暫無優化建議"]
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """獲取實時指標"""
        current_time = datetime.now()
        recent_cutoff = current_time - timedelta(minutes=5)
        
        recent_notifications = [
            record for record in self.notification_history
            if record.timestamp > recent_cutoff
        ]
        
        if not recent_notifications:
            return {
                "real_time_status": "no_recent_activity",
                "timestamp": current_time.isoformat()
            }
        
        # 實時統計
        successful_recent = len([
            r for r in recent_notifications
            if r.status in [NotificationStatus.DELIVERED, NotificationStatus.OPENED, NotificationStatus.CLICKED]
        ])
        
        channel_activity = defaultdict(int)
        for record in recent_notifications:
            channel_activity[record.channel.value] += 1
        
        return {
            "real_time_status": "active",
            "timestamp": current_time.isoformat(),
            "recent_5min_metrics": {
                "total_notifications": len(recent_notifications),
                "successful_notifications": successful_recent,
                "success_rate": successful_recent / len(recent_notifications),
                "channel_activity": dict(channel_activity)
            },
            "notification_rate": {
                "notifications_per_minute": len(recent_notifications),
                "target_rate": 10,  # 目標每5分鐘50個通知
                "performance_ratio": len(recent_notifications) / 10
            }
        }

# 全局實例
notification_monitor = NotificationSuccessRateMonitor()
