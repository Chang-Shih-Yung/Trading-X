"""
📬 Phase4 Notification Success Rate Monitoring - OPTIMIZED
=======================================================

通知成功率監控實現 - 基於配置驅動的多通道通知效果追蹤
與 notification_success_rate_monitoring_config.json 配置文件精確對應

實現完整的多通道通知架構監控、延遲管理分析、用戶參與度分析、
跨階段數據追蹤、系統性能優化和報告預警系統
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict, deque
from enum import Enum
import statistics
import uuid

logger = logging.getLogger(__name__)

class NotificationChannel(Enum):
    """通知通道類型 - 對應JSON配置的multi_channel_tracking"""
    GMAIL = "gmail"
    WEBSOCKET = "websocket" 
    FRONTEND = "frontend"
    SMS = "sms"

class NotificationPriority(Enum):
    """通知優先級 - 對應JSON配置的priority_level_performance"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class NotificationStatus(Enum):
    """通知狀態 - 對應JSON配置的delivery_tracking"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"

class DelayBatchType(Enum):
    """延遲批次類型 - 對應JSON配置的priority_based_delay_tracking"""
    IMMEDIATE = "immediate"  # 0ms 延遲
    FIVE_MINUTE_BATCH = "five_minute_batch"  # 300秒批次
    THIRTY_MINUTE_BATCH = "thirty_minute_batch"  # 1800秒批次
    DAILY_SUMMARY = "daily_summary"  # 日終摘要

class EngagementActionType(Enum):
    """參與度行為類型 - 對應JSON配置的notification_action_tracking"""
    SIGNAL_TO_EXECUTION = "signal_to_execution"
    EPL_DECISION_RESPONSE = "epl_decision_response"
    REAL_TIME_ACTION = "real_time_action"
    PORTFOLIO_ADJUSTMENT = "portfolio_adjustment"

@dataclass
class NotificationRecord:
    """通知記錄 - 對應JSON配置的raw_notification_data"""
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
    # 新增字段 - 對應JSON配置
    master_transaction_id: Optional[str] = None  # unified_tracking_system
    phase1_signal_id: Optional[str] = None  # phase1_signal_to_notification_mapping
    phase2_decision_id: Optional[str] = None  # phase2_decision_to_notification_mapping
    phase3_execution_id: Optional[str] = None  # phase3_execution_to_notification_mapping
    batch_type: Optional[DelayBatchType] = None  # priority_based_delay_tracking
    
@dataclass
class GmailNotificationMetrics:
    """Gmail通知指標 - 對應JSON配置的gmail_notification_monitoring"""
    authentication_success_rate: float = 0.0
    message_composition_success: float = 0.0
    smtp_delivery_success: float = 0.0
    delivery_confirmation_rate: float = 0.0
    message_preparation_time: float = 0.0
    authentication_latency: float = 0.0
    smtp_transmission_time: float = 0.0
    end_to_end_delivery_time: float = 0.0
    oauth2_failures: int = 0
    template_rendering_failures: int = 0
    smtp_transmission_failures: int = 0
    rate_limiting_impacts: int = 0

@dataclass
class WebsocketBroadcastMetrics:
    """WebSocket廣播指標 - 對應JSON配置的websocket_broadcast_monitoring"""
    active_connections: int = 0
    connection_stability: float = 0.0
    reconnection_success_rate: float = 0.0
    message_delivery_confirmation: float = 0.0
    message_broadcast_latency: float = 0.0
    client_reception_rate: float = 0.0
    message_persistence_24h: float = 0.0
    concurrent_client_handling: float = 0.0
    intelligent_filtering_accuracy: float = 0.0
    bandwidth_optimization: float = 0.0

@dataclass
class FrontendIntegrationMetrics:
    """前端整合指標 - 對應JSON配置的frontend_integration_monitoring"""
    real_time_update_success: float = 0.0
    update_latency: float = 0.0
    data_synchronization: float = 0.0
    visual_rendering_success: float = 0.0
    popup_alert_delivery: float = 0.0
    priority_highlighting: float = 0.0
    sound_notification_delivery: float = 0.0
    user_interaction_tracking: float = 0.0
    notification_responsiveness: float = 0.0
    alert_fatigue_measurement: float = 0.0

@dataclass
class SmsEmergencyMetrics:
    """SMS緊急通知指標 - 對應JSON配置的sms_emergency_monitoring"""
    sms_gateway_success: float = 0.0
    message_truncation_accuracy: float = 0.0
    priority_queue_performance: float = 0.0
    delivery_confirmation: float = 0.0
    hourly_rate_limit_adherence: float = 0.0
    critical_only_filtering_accuracy: float = 0.0
    cost_per_successful_delivery: float = 0.0
    message_relevance_scoring: float = 0.0
    user_response_rate: float = 0.0
    opt_out_rate_tracking: float = 0.0

@dataclass
class UserEngagementMetrics:
    """用戶參與度指標 - 對應JSON配置的user_engagement_analytics"""
    signal_to_execution_conversion: float = 0.0
    execution_timing_analysis: float = 0.0
    execution_success_correlation: float = 0.0
    epl_decision_responses: float = 0.0
    decision_implementation_rate: float = 0.0
    immediate_actions: int = 0
    delayed_actions: int = 0
    multi_step_actions: int = 0
    notification_relevance_scoring: float = 0.0
    timing_satisfaction_scoring: float = 0.0
    overall_system_satisfaction: float = 0.0

@dataclass
class CrossPhaseTrackingData:
    """跨階段追蹤數據 - 對應JSON配置的cross_phase_data_tracking"""
    master_transaction_id: str
    phase1_signal_correlation: Dict[str, Any] = field(default_factory=dict)
    phase2_decision_correlation: Dict[str, Any] = field(default_factory=dict)
    phase3_execution_correlation: Dict[str, Any] = field(default_factory=dict)
    unified_performance_metrics: Dict[str, float] = field(default_factory=dict)
    data_consistency_status: str = "pending"
    end_to_end_latency: float = 0.0

@dataclass
class ChannelMetrics:
    """通道指標 - 更新以對應JSON配置"""
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
    # 新增專門指標
    gmail_metrics: Optional[GmailNotificationMetrics] = None
    websocket_metrics: Optional[WebsocketBroadcastMetrics] = None
    frontend_metrics: Optional[FrontendIntegrationMetrics] = None
    sms_metrics: Optional[SmsEmergencyMetrics] = None

class NotificationSuccessRateMonitor:
    """
    通知成功率監控系統 
    完整實現JSON配置的PHASE4_NOTIFICATION_SUCCESS_RATE_MONITORING
    """
    
    def __init__(self):
        # 載入配置文件
        self.config = self._load_config()
        
        # 通知記錄存儲 - 對應data_storage_and_retrieval
        self.notification_history: deque = deque(maxlen=100000)
        self.channel_metrics: Dict[str, ChannelMetrics] = {}
        self.cross_phase_tracking: Dict[str, CrossPhaseTrackingData] = {}
        
        # 實時統計 - 對應real_time_data_access
        self.hourly_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.daily_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # 延遲管理分析 - 對應delay_management_analytics
        self.delay_batch_queues: Dict[DelayBatchType, List[NotificationRecord]] = {
            DelayBatchType.IMMEDIATE: [],
            DelayBatchType.FIVE_MINUTE_BATCH: [],
            DelayBatchType.THIRTY_MINUTE_BATCH: [],
            DelayBatchType.DAILY_SUMMARY: []
        }
        
        # 用戶參與度追蹤 - 對應user_engagement_analytics
        self.engagement_tracking: Dict[str, UserEngagementMetrics] = {}
        self.notification_action_history: List[Dict[str, Any]] = []
        
        # 通知架構監控 - 對應notification_architecture_monitoring
        self.architecture_monitoring = {
            "gmail_monitoring": GmailNotificationMetrics(),
            "websocket_monitoring": WebsocketBroadcastMetrics(),
            "frontend_monitoring": FrontendIntegrationMetrics(),
            "sms_monitoring": SmsEmergencyMetrics()
        }
        
        # 系統性能監控 - 對應system_performance_optimization
        self.system_performance = {
            "server_uptime": 0.0,
            "processing_capacity": 0,
            "queue_depth": 0,
            "resource_utilization": {},
            "network_latency": 0.0,
            "bandwidth_utilization": 0.0
        }
        
        # 報告和預警 - 對應reporting_and_alerting
        self.alert_system = {
            "performance_alerts": [],
            "quality_alerts": [],
            "last_alert_check": datetime.now()
        }
        
        # 性能監控
        self.monitoring_enabled = True
        self.last_update = datetime.now()
        
        # 警報設置 - 對應alert_thresholds
        self.alert_thresholds = {
            "success_rate_warning": 0.9,
            "success_rate_critical": 0.8,
            "delivery_latency_warning": 5000,  # 5秒
            "delivery_latency_critical": 10000,  # 10秒
            "engagement_rate_warning": 0.3,
            "queue_depth_warning": 1000,
            "queue_depth_critical": 5000
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
                "notification_architecture_monitoring": {
                    "multi_channel_tracking": {
                        "gmail_notification_monitoring": {"delivery_tracking": True},
                        "websocket_broadcast_monitoring": {"connection_tracking": True},
                        "frontend_integration_monitoring": {"dashboard_update_tracking": True},
                        "sms_emergency_monitoring": {"sms_delivery_tracking": True}
                    }
                },
                "delay_management_analytics": {
                    "priority_based_delay_tracking": {
                        "critical_immediate_delivery": {"zero_delay_achievement": True},
                        "high_priority_batch_delivery": {"five_minute_batch_compliance": True},
                        "medium_priority_batch_delivery": {"thirty_minute_batch_compliance": True},
                        "low_priority_daily_summary": {"end_of_day_delivery": True}
                    }
                },
                "user_engagement_analytics": {
                    "notification_action_tracking": {"trade_execution_actions": True},
                    "engagement_correlation_analysis": {"notification_to_action_correlation": True},
                    "notification_effectiveness_measurement": {"click_through_rates": True}
                },
                "cross_phase_data_tracking": {
                    "phase_integration_mapping": {"phase1_signal_to_notification_mapping": True},
                    "unified_tracking_system": {"master_transaction_id_system": True}
                },
                "system_performance_optimization": {
                    "delivery_infrastructure_monitoring": {"server_performance": True},
                    "scalability_analytics": {"load_testing_results": True}
                }
            }
        }
    
    def _initialize_monitoring(self):
        """初始化監控系統 - 對應JSON配置的system_metadata"""
        logger.info("初始化通知成功率監控系統")
        
        # 初始化通道指標 - 對應multi_channel_tracking
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
                engagement_rate=0.0,
                # 初始化專門通道指標
                gmail_metrics=GmailNotificationMetrics() if channel == NotificationChannel.GMAIL else None,
                websocket_metrics=WebsocketBroadcastMetrics() if channel == NotificationChannel.WEBSOCKET else None,
                frontend_metrics=FrontendIntegrationMetrics() if channel == NotificationChannel.FRONTEND else None,
                sms_metrics=SmsEmergencyMetrics() if channel == NotificationChannel.SMS else None
            )
        
        # 清理過舊的數據
        self._cleanup_old_records()
        
        # 初始化延遲管理 - 對應delay_management_analytics
        self._initialize_delay_management()
        
        # 初始化跨階段追蹤 - 對應cross_phase_data_tracking
        self._initialize_cross_phase_tracking()
        
        # 初始化系統性能監控 - 對應system_performance_optimization
        self._initialize_system_performance_monitoring()
        
        logger.info("通知成功率監控系統初始化完成")
    
    def _initialize_delay_management(self):
        """初始化延遲管理 - 對應JSON配置的delay_management_analytics"""
        logger.info("初始化延遲管理系統")
        
        # 設置批次延遲配置
        self.delay_config = {
            DelayBatchType.IMMEDIATE: {"target_delay": 0, "tolerance": 100},  # 0ms ± 100ms
            DelayBatchType.FIVE_MINUTE_BATCH: {"target_delay": 300000, "tolerance": 30000},  # 5分鐘 ± 30秒
            DelayBatchType.THIRTY_MINUTE_BATCH: {"target_delay": 1800000, "tolerance": 180000},  # 30分鐘 ± 3分鐘
            DelayBatchType.DAILY_SUMMARY: {"target_delay": 86400000, "tolerance": 3600000}  # 24小時 ± 1小時
        }
        
    def _initialize_cross_phase_tracking(self):
        """初始化跨階段追蹤 - 對應JSON配置的cross_phase_data_tracking"""
        logger.info("初始化跨階段數據追蹤")
        
        # Phase整合配置
        self.phase_integration_config = {
            "phase1_signal_mapping": True,
            "phase2_decision_mapping": True,
            "phase3_execution_mapping": True,
            "unified_tracking_enabled": True,
            "data_consistency_monitoring": True
        }
        
    def _initialize_system_performance_monitoring(self):
        """初始化系統性能監控 - 對應JSON配置的system_performance_optimization"""
        logger.info("初始化系統性能監控")
        
        # 設置性能監控配置
        self.performance_config = {
            "server_monitoring": True,
            "network_monitoring": True,
            "scalability_analytics": True,
            "capacity_planning": True
        }
        
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
        """記錄發送的通知 - 對應JSON配置的raw_notification_data"""
        try:
            # 生成通知ID和主事務ID
            notification_id = f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{notification_data.get('channel', 'unknown')}_{uuid.uuid4().hex[:8]}"
            master_transaction_id = notification_data.get('master_transaction_id', f"tx_{uuid.uuid4().hex}")
            
            # 創建通知記錄
            record = NotificationRecord(
                notification_id=notification_id,
                timestamp=datetime.fromisoformat(notification_data.get('timestamp', datetime.now().isoformat())),
                channel=NotificationChannel(notification_data.get('channel', 'websocket')),
                priority=NotificationPriority(notification_data.get('priority', 'MEDIUM')),
                recipient_id=notification_data.get('recipient_id', 'unknown'),
                content_type=notification_data.get('content_type', 'signal'),
                status=NotificationStatus.SENT,
                retry_count=0,
                # 新增跨階段追蹤字段
                master_transaction_id=master_transaction_id,
                phase1_signal_id=notification_data.get('phase1_signal_id'),
                phase2_decision_id=notification_data.get('phase2_decision_id'),
                phase3_execution_id=notification_data.get('phase3_execution_id'),
                batch_type=DelayBatchType(notification_data.get('batch_type', 'immediate'))
            )
            
            # 添加到歷史記錄
            self.notification_history.append(record)
            
            # 更新實時統計
            self._update_real_time_stats(record, "sent")
            
            # 更新通道指標
            self._update_channel_metrics(record.channel.value, "sent")
            
            # 更新架構監控指標
            await self._update_architecture_monitoring(record, "sent")
            
            # 更新跨階段追蹤
            await self._update_cross_phase_tracking(record)
            
            # 更新延遲管理
            self._update_delay_management(record)
            
            self.last_update = datetime.now()
            
            logger.info(f"記錄通知發送: {notification_id}, 通道: {record.channel.value}, 事務ID: {master_transaction_id}")
            return notification_id
            
        except Exception as e:
            logger.error(f"記錄通知發送失敗: {e}")
            return ""

    async def update_notification_status(self, notification_id: str, status_data: Dict[str, Any]) -> bool:
        """更新通知狀態 - 對應JSON配置的delivery_tracking"""
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
            
            # 更新架構監控
            await self._update_architecture_monitoring(record, new_status.value)
            
            # 更新用戶參與度追蹤
            if new_status in [NotificationStatus.OPENED, NotificationStatus.CLICKED]:
                await self._update_user_engagement_tracking(record, new_status.value)
            
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

    async def _update_architecture_monitoring(self, record: NotificationRecord, event_type: str):
        """更新架構監控指標 - 對應JSON配置的notification_architecture_monitoring"""
        try:
            if record.channel == NotificationChannel.GMAIL:
                await self._update_gmail_monitoring(record, event_type)
            elif record.channel == NotificationChannel.WEBSOCKET:
                await self._update_websocket_monitoring(record, event_type)
            elif record.channel == NotificationChannel.FRONTEND:
                await self._update_frontend_monitoring(record, event_type)
            elif record.channel == NotificationChannel.SMS:
                await self._update_sms_monitoring(record, event_type)
                
        except Exception as e:
            logger.error(f"更新架構監控失敗: {e}")

    async def _update_gmail_monitoring(self, record: NotificationRecord, event_type: str):
        """更新Gmail監控指標 - 對應JSON配置的gmail_notification_monitoring"""
        gmail_metrics = self.architecture_monitoring["gmail_monitoring"]
        
        if event_type == "sent":
            gmail_metrics.message_composition_success += 1
        elif event_type == "delivered":
            gmail_metrics.smtp_delivery_success += 1
            gmail_metrics.delivery_confirmation_rate += 1
            if record.delivery_latency:
                gmail_metrics.end_to_end_delivery_time = record.delivery_latency
        elif event_type == "failed":
            if record.error_message:
                if "oauth" in record.error_message.lower():
                    gmail_metrics.oauth2_failures += 1
                elif "template" in record.error_message.lower():
                    gmail_metrics.template_rendering_failures += 1
                elif "smtp" in record.error_message.lower():
                    gmail_metrics.smtp_transmission_failures += 1
                elif "rate" in record.error_message.lower():
                    gmail_metrics.rate_limiting_impacts += 1

    async def _update_websocket_monitoring(self, record: NotificationRecord, event_type: str):
        """更新WebSocket監控指標 - 對應JSON配置的websocket_broadcast_monitoring"""
        ws_metrics = self.architecture_monitoring["websocket_monitoring"]
        
        if event_type == "sent":
            ws_metrics.active_connections += 1
        elif event_type == "delivered":
            ws_metrics.message_delivery_confirmation += 1
            ws_metrics.client_reception_rate += 1
            if record.delivery_latency:
                ws_metrics.message_broadcast_latency = record.delivery_latency
        elif event_type == "failed":
            ws_metrics.active_connections = max(0, ws_metrics.active_connections - 1)

    async def _update_frontend_monitoring(self, record: NotificationRecord, event_type: str):
        """更新前端監控指標 - 對應JSON配置的frontend_integration_monitoring"""
        frontend_metrics = self.architecture_monitoring["frontend_monitoring"]
        
        if event_type == "sent":
            frontend_metrics.real_time_update_success += 1
        elif event_type == "delivered":
            frontend_metrics.data_synchronization += 1
            frontend_metrics.visual_rendering_success += 1
            if record.delivery_latency:
                frontend_metrics.update_latency = record.delivery_latency
        elif event_type == "opened":
            frontend_metrics.popup_alert_delivery += 1
        elif event_type == "clicked":
            frontend_metrics.user_interaction_tracking += 1

    async def _update_sms_monitoring(self, record: NotificationRecord, event_type: str):
        """更新SMS監控指標 - 對應JSON配置的sms_emergency_monitoring"""
        sms_metrics = self.architecture_monitoring["sms_monitoring"]
        
        if event_type == "sent":
            if record.priority == NotificationPriority.CRITICAL:
                sms_metrics.critical_only_filtering_accuracy += 1
        elif event_type == "delivered":
            sms_metrics.sms_gateway_success += 1
            sms_metrics.delivery_confirmation += 1
            if record.engagement_data and 'message_length' in record.engagement_data:
                if record.engagement_data['message_length'] <= 160:
                    sms_metrics.message_truncation_accuracy += 1

    async def _update_cross_phase_tracking(self, record: NotificationRecord):
        """更新跨階段追蹤 - 對應JSON配置的cross_phase_data_tracking"""
        try:
            if not record.master_transaction_id:
                return
                
            # 創建或更新跨階段追蹤記錄
            if record.master_transaction_id not in self.cross_phase_tracking:
                self.cross_phase_tracking[record.master_transaction_id] = CrossPhaseTrackingData(
                    master_transaction_id=record.master_transaction_id
                )
            
            tracking = self.cross_phase_tracking[record.master_transaction_id]
            
            # 更新Phase1信號相關性
            if record.phase1_signal_id:
                tracking.phase1_signal_correlation.update({
                    "signal_id": record.phase1_signal_id,
                    "signal_to_notification_time": record.delivery_latency,
                    "notification_channel": record.channel.value,
                    "priority_mapping": record.priority.value
                })
            
            # 更新Phase2決策相關性
            if record.phase2_decision_id:
                tracking.phase2_decision_correlation.update({
                    "decision_id": record.phase2_decision_id,
                    "decision_to_notification_time": record.delivery_latency,
                    "decision_confidence_impact": record.priority.value,
                    "notification_customization": record.content_type
                })
            
            # 更新Phase3執行相關性
            if record.phase3_execution_id:
                tracking.phase3_execution_correlation.update({
                    "execution_id": record.phase3_execution_id,
                    "execution_to_notification_time": record.delivery_latency,
                    "execution_status_updates": record.status.value,
                    "performance_impact": record.engagement_data or {}
                })
            
            # 更新統一性能指標
            tracking.unified_performance_metrics.update({
                "notification_delivery_success": 1.0 if record.status == NotificationStatus.DELIVERED else 0.0,
                "cross_phase_latency": record.delivery_latency or 0.0,
                "data_consistency": 1.0 if all([
                    tracking.phase1_signal_correlation,
                    tracking.phase2_decision_correlation, 
                    tracking.phase3_execution_correlation
                ]) else 0.5
            })
            
            tracking.data_consistency_status = "complete" if len(tracking.unified_performance_metrics) >= 3 else "partial"
            
        except Exception as e:
            logger.error(f"更新跨階段追蹤失敗: {e}")

    def _update_delay_management(self, record: NotificationRecord):
        """更新延遲管理 - 對應JSON配置的delay_management_analytics"""
        try:
            if not record.batch_type:
                return
                
            # 添加到對應的批次佇列
            self.delay_batch_queues[record.batch_type].append(record)
            
            # 檢查批次是否需要處理
            self._process_delay_batches()
            
        except Exception as e:
            logger.error(f"更新延遲管理失敗: {e}")

    def _process_delay_batches(self):
        """處理延遲批次 - 對應JSON配置的priority_based_delay_tracking"""
        current_time = datetime.now()
        
        for batch_type, queue in self.delay_batch_queues.items():
            if not queue:
                continue
                
            config = self.delay_config[batch_type]
            target_delay_ms = config["target_delay"]
            
            # 檢查是否達到批次處理時間
            oldest_record = min(queue, key=lambda r: r.timestamp)
            elapsed_ms = (current_time - oldest_record.timestamp).total_seconds() * 1000
            
            if elapsed_ms >= target_delay_ms:
                # 處理批次
                self._execute_batch_delivery(batch_type, queue.copy())
                # 清空佇列
                queue.clear()

    def _execute_batch_delivery(self, batch_type: DelayBatchType, records: List[NotificationRecord]):
        """執行批次投遞 - 對應JSON配置的intelligent_batching"""
        logger.info(f"執行 {batch_type.value} 批次投遞，包含 {len(records)} 條通知")
        
        # 根據批次類型進行不同處理
        if batch_type == DelayBatchType.IMMEDIATE:
            pass  # 立即投遞，無需特殊處理
        elif batch_type == DelayBatchType.FIVE_MINUTE_BATCH:
            self._aggregate_batch_content(records, "5_minute")
        elif batch_type == DelayBatchType.THIRTY_MINUTE_BATCH:
            self._aggregate_batch_content(records, "30_minute")
        elif batch_type == DelayBatchType.DAILY_SUMMARY:
            self._generate_daily_summary(records)

    def _aggregate_batch_content(self, records: List[NotificationRecord], batch_window: str):
        """聚合批次內容 - 對應JSON配置的content_aggregation"""
        content_groups = defaultdict(list)
        for record in records:
            content_groups[record.content_type].append(record)
        
        for content_type, group_records in content_groups.items():
            logger.info(f"聚合 {content_type} 類型通知，{batch_window} 批次，共 {len(group_records)} 條")

    def _generate_daily_summary(self, records: List[NotificationRecord]):
        """生成日終摘要 - 對應JSON配置的end_of_day_delivery"""
        logger.info(f"生成日終摘要，包含 {len(records)} 條通知")
        
        summary_stats = defaultdict(int)
        for record in records:
            summary_stats[record.content_type] += 1
        
        logger.info(f"日終摘要統計: {dict(summary_stats)}")

    async def _update_user_engagement_tracking(self, record: NotificationRecord, action_type: str):
        """更新用戶參與度追蹤 - 對應JSON配置的user_engagement_analytics"""
        try:
            user_id = record.recipient_id
            
            # 創建或獲取用戶參與度指標
            if user_id not in self.engagement_tracking:
                self.engagement_tracking[user_id] = UserEngagementMetrics()
            
            engagement = self.engagement_tracking[user_id]
            
            # 記錄參與度行為
            action_record = {
                "timestamp": datetime.now().isoformat(),
                "notification_id": record.notification_id,
                "action_type": action_type,
                "channel": record.channel.value,
                "priority": record.priority.value,
                "content_type": record.content_type,
                "response_time": record.delivery_latency or 0.0
            }
            
            self.notification_action_history.append(action_record)
            
            # 更新參與度指標
            if action_type == "opened":
                if record.delivery_latency:
                    engagement.timing_satisfaction_scoring = min(1.0, 5000 / record.delivery_latency)
                    
            elif action_type == "clicked":
                if record.content_type == "signal":
                    engagement.signal_to_execution_conversion += 1
                elif record.content_type == "epl_decision":
                    engagement.epl_decision_responses += 1
                    
                # 判斷行為類型
                if record.delivery_latency and record.delivery_latency < 60000:  # 1分鐘內
                    engagement.immediate_actions += 1
                else:
                    engagement.delayed_actions += 1
                    
            # 更新整體滿意度
            self._calculate_user_satisfaction(engagement, record)
            
        except Exception as e:
            logger.error(f"更新用戶參與度追蹤失敗: {e}")

    def _calculate_user_satisfaction(self, engagement: UserEngagementMetrics, record: NotificationRecord):
        """計算用戶滿意度 - 對應JSON配置的user_satisfaction_metrics"""
        time_satisfaction = 1.0 if record.delivery_latency and record.delivery_latency < 5000 else 0.5
        relevance_satisfaction = 0.8  # 假設預設相關性
        channel_satisfaction = 0.9 if record.channel == NotificationChannel.WEBSOCKET else 0.7
        
        engagement.overall_system_satisfaction = (
            time_satisfaction + relevance_satisfaction + channel_satisfaction
        ) / 3

    async def get_comprehensive_monitoring_report(self) -> Dict[str, Any]:
        """獲取綜合監控報告 - 對應JSON配置的reporting_and_alerting"""
        try:
            current_time = datetime.now()
            
            if not self.notification_history:
                return self._get_empty_report()
            
            # 基本統計
            total_notifications = len(self.notification_history)
            
            # 通道性能分析 - 對應notification_architecture_monitoring
            channel_analysis = self._analyze_channel_performance()
            
            # 延遲管理分析 - 對應delay_management_analytics
            delay_analysis = self._analyze_delay_management()
            
            # 用戶參與度分析 - 對應user_engagement_analytics
            engagement_analysis = self._analyze_user_engagement()
            
            # 跨階段數據分析 - 對應cross_phase_data_tracking
            cross_phase_analysis = self._analyze_cross_phase_data()
            
            # 系統性能分析 - 對應system_performance_optimization
            system_performance_analysis = self._analyze_system_performance()
            
            # 警報狀態 - 對應automated_alerting
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
                "notification_architecture_monitoring": channel_analysis,
                "delay_management_analytics": delay_analysis,
                "user_engagement_analytics": engagement_analysis,
                "cross_phase_data_tracking": cross_phase_analysis,
                "system_performance_optimization": system_performance_analysis,
                "reporting_and_alerting": alert_status,
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
            "message": "尚無通知數據可供分析"
        }

    def _analyze_channel_performance(self) -> Dict[str, Any]:
        """分析通道性能 - 對應JSON配置的notification_architecture_monitoring"""
        channel_stats = {}
        
        for channel_name, metrics in self.channel_metrics.items():
            channel_stats[channel_name] = {
                "total_sent": metrics.total_sent,
                "successful_deliveries": metrics.successful_deliveries,
                "failed_deliveries": metrics.failed_deliveries,
                "success_rate": metrics.success_rate,
                "engagement_rate": metrics.engagement_rate,
                "average_delivery_time": metrics.average_delivery_time
            }
            
            # 添加專門通道指標
            if metrics.gmail_metrics:
                channel_stats[channel_name]["gmail_specific"] = asdict(metrics.gmail_metrics)
            elif metrics.websocket_metrics:
                channel_stats[channel_name]["websocket_specific"] = asdict(metrics.websocket_metrics)
            elif metrics.frontend_metrics:
                channel_stats[channel_name]["frontend_specific"] = asdict(metrics.frontend_metrics)
            elif metrics.sms_metrics:
                channel_stats[channel_name]["sms_specific"] = asdict(metrics.sms_metrics)
        
        return {
            "multi_channel_tracking": channel_stats,
            "cross_channel_analytics": {
                "best_performing_channel": max(channel_stats.items(), key=lambda x: x[1]["success_rate"])[0] if channel_stats else "none",
                "overall_success_rate": sum(m.success_rate for m in self.channel_metrics.values()) / len(self.channel_metrics) if self.channel_metrics else 0
            }
        }

    def _analyze_delay_management(self) -> Dict[str, Any]:
        """分析延遲管理 - 對應JSON配置的delay_management_analytics"""
        delay_stats = {}
        
        for batch_type, queue in self.delay_batch_queues.items():
            delay_stats[batch_type.value] = {
                "queue_depth": len(queue),
                "target_delay": self.delay_config[batch_type]["target_delay"],
                "compliance_rate": self._calculate_delay_compliance(batch_type, queue)
            }
        
        return {
            "priority_based_delay_tracking": delay_stats,
            "delay_optimization": {
                "overall_delay_performance": sum(stats["compliance_rate"] for stats in delay_stats.values()) / len(delay_stats) if delay_stats else 0,
                "intelligent_batching_effectiveness": self._calculate_batching_effectiveness()
            }
        }

    def _analyze_user_engagement(self) -> Dict[str, Any]:
        """分析用戶參與度 - 對應JSON配置的user_engagement_analytics"""
        if not self.engagement_tracking:
            return {"notification_action_tracking": {}, "engagement_correlation_analysis": {}}
        
        total_users = len(self.engagement_tracking)
        avg_satisfaction = sum(e.overall_system_satisfaction for e in self.engagement_tracking.values()) / total_users
        
        return {
            "notification_action_tracking": {
                "total_tracked_users": total_users,
                "average_signal_conversion": sum(e.signal_to_execution_conversion for e in self.engagement_tracking.values()) / total_users,
                "average_decision_responses": sum(e.epl_decision_responses for e in self.engagement_tracking.values()) / total_users,
                "immediate_vs_delayed_actions": {
                    "immediate": sum(e.immediate_actions for e in self.engagement_tracking.values()),
                    "delayed": sum(e.delayed_actions for e in self.engagement_tracking.values())
                }
            },
            "engagement_correlation_analysis": {
                "overall_user_satisfaction": avg_satisfaction,
                "engagement_trends": self._analyze_engagement_trends()
            },
            "notification_effectiveness_measurement": {
                "average_timing_satisfaction": sum(e.timing_satisfaction_scoring for e in self.engagement_tracking.values()) / total_users
            }
        }

    def _analyze_cross_phase_data(self) -> Dict[str, Any]:
        """分析跨階段數據 - 對應JSON配置的cross_phase_data_tracking"""
        if not self.cross_phase_tracking:
            return {"phase_integration_mapping": {}, "unified_tracking_system": {}}
        
        total_transactions = len(self.cross_phase_tracking)
        complete_transactions = len([t for t in self.cross_phase_tracking.values() if t.data_consistency_status == "complete"])
        
        return {
            "phase_integration_mapping": {
                "total_tracked_transactions": total_transactions,
                "complete_integration_rate": complete_transactions / total_transactions if total_transactions > 0 else 0,
                "phase1_coverage": len([t for t in self.cross_phase_tracking.values() if t.phase1_signal_correlation]),
                "phase2_coverage": len([t for t in self.cross_phase_tracking.values() if t.phase2_decision_correlation]),
                "phase3_coverage": len([t for t in self.cross_phase_tracking.values() if t.phase3_execution_correlation])
            },
            "unified_tracking_system": {
                "master_transaction_tracking": True,
                "data_consistency_rate": complete_transactions / total_transactions if total_transactions > 0 else 0,
                "average_end_to_end_latency": sum(t.end_to_end_latency for t in self.cross_phase_tracking.values()) / total_transactions if total_transactions > 0 else 0
            }
        }

    def _analyze_system_performance(self) -> Dict[str, Any]:
        """分析系統性能 - 對應JSON配置的system_performance_optimization"""
        return {
            "delivery_infrastructure_monitoring": {
                "server_performance": self.system_performance,
                "queue_management_efficiency": sum(len(queue) for queue in self.delay_batch_queues.values()),
                "processing_throughput": len(self.notification_history) / max(1, (datetime.now() - min(r.timestamp for r in self.notification_history)).total_seconds() / 3600) if self.notification_history else 0
            },
            "scalability_analytics": {
                "current_load_metrics": {
                    "active_notifications": len(self.notification_history),
                    "tracked_users": len(self.engagement_tracking),
                    "cross_phase_transactions": len(self.cross_phase_tracking)
                },
                "performance_optimization_suggestions": self._generate_performance_suggestions()
            }
        }

    def _check_alert_conditions(self) -> Dict[str, Any]:
        """檢查警報條件 - 對應JSON配置的automated_alerting"""
        alerts = []
        current_time = datetime.now()
        
        # 檢查性能退化警報
        overall_success_rate = self._calculate_overall_success_rate()
        
        if overall_success_rate < self.alert_thresholds["success_rate_critical"]:
            alerts.append({
                "type": "performance_degradation_alert",
                "severity": "critical",
                "message": f"整體成功率過低: {overall_success_rate:.1%}",
                "threshold": self.alert_thresholds["success_rate_critical"],
                "current_value": overall_success_rate
            })
        elif overall_success_rate < self.alert_thresholds["success_rate_warning"]:
            alerts.append({
                "type": "performance_degradation_alert", 
                "severity": "warning",
                "message": f"整體成功率低於警告線: {overall_success_rate:.1%}",
                "threshold": self.alert_thresholds["success_rate_warning"],
                "current_value": overall_success_rate
            })
        
        # 檢查佇列深度警報
        total_queue_depth = sum(len(queue) for queue in self.delay_batch_queues.values())
        if total_queue_depth > self.alert_thresholds["queue_depth_critical"]:
            alerts.append({
                "type": "queue_backup_alert",
                "severity": "critical",
                "message": f"通知佇列積壓嚴重: {total_queue_depth} 條",
                "current_value": total_queue_depth
            })
        
        return {
            "real_time_dashboards": {
                "delivery_status_dashboard": {"alert_count": len(alerts)},
                "performance_metrics_dashboard": {"system_status": "critical" if any(a["severity"] == "critical" for a in alerts) else "warning" if alerts else "healthy"}
            },
            "automated_alerting": {
                "performance_degradation_alerts": [a for a in alerts if a["type"] == "performance_degradation_alert"],
                "quality_degradation_alerts": [],
                "total_alerts": len(alerts),
                "last_check": current_time.isoformat()
            }
        }

    def _calculate_overall_success_rate(self) -> float:
        """計算整體成功率"""
        if not self.channel_metrics:
            return 0.0
        
        total_sent = sum(m.total_sent for m in self.channel_metrics.values())
        total_successful = sum(m.successful_deliveries for m in self.channel_metrics.values())
        
        return total_successful / total_sent if total_sent > 0 else 0.0

    def _calculate_delay_compliance(self, batch_type: DelayBatchType, queue: List[NotificationRecord]) -> float:
        """計算延遲合規率"""
        if not queue:
            return 1.0
        
        config = self.delay_config[batch_type]
        target_delay = config["target_delay"]
        tolerance = config["tolerance"]
        
        compliant_count = 0
        for record in queue:
            actual_delay = (datetime.now() - record.timestamp).total_seconds() * 1000
            if abs(actual_delay - target_delay) <= tolerance:
                compliant_count += 1
        
        return compliant_count / len(queue)

    def _calculate_batching_effectiveness(self) -> float:
        """計算批次處理效率"""
        total_processed = sum(len(queue) for queue in self.delay_batch_queues.values())
        if total_processed == 0:
            return 1.0
        
        # 簡化計算：基於佇列深度的倒數
        effectiveness = 1.0 / (1.0 + total_processed * 0.01)
        return effectiveness

    def _analyze_engagement_trends(self) -> Dict[str, Any]:
        """分析參與度趨勢"""
        if not self.notification_action_history:
            return {}
        
        recent_actions = [
            action for action in self.notification_action_history
            if (datetime.now() - datetime.fromisoformat(action["timestamp"])).days <= 7
        ]
        
        return {
            "recent_activity": len(recent_actions),
            "action_types": {
                action_type: len([a for a in recent_actions if a["action_type"] == action_type])
                for action_type in ["opened", "clicked"]
            }
        }

    def _generate_performance_suggestions(self) -> List[str]:
        """生成性能建議"""
        suggestions = []
        
        # 基於佇列深度
        total_queue_depth = sum(len(queue) for queue in self.delay_batch_queues.values())
        if total_queue_depth > 100:
            suggestions.append("考慮增加處理容量以減少佇列積壓")
        
        # 基於成功率
        overall_success_rate = self._calculate_overall_success_rate()
        if overall_success_rate < 0.9:
            suggestions.append("檢查通道配置和網路連接以提高成功率")
        
        return suggestions if suggestions else ["系統運行良好，暫無優化建議"]

    def _generate_optimization_recommendations(self) -> List[str]:
        """生成優化建議 - 對應JSON配置的完整建議系統"""
        recommendations = []
        
        # 基於通道性能
        if self.channel_metrics:
            best_channel = max(self.channel_metrics.items(), key=lambda x: x[1].success_rate)
            worst_channel = min(self.channel_metrics.items(), key=lambda x: x[1].success_rate)
            
            if best_channel[1].success_rate > 0.95:
                recommendations.append(f"通道 {best_channel[0]} 表現優異 ({best_channel[1].success_rate:.1%})，建議優先使用")
            
            if worst_channel[1].success_rate < 0.8:
                recommendations.append(f"通道 {worst_channel[0]} 成功率較低 ({worst_channel[1].success_rate:.1%})，建議檢查配置")
        
        # 基於用戶參與度
        if self.engagement_tracking:
            avg_satisfaction = sum(e.overall_system_satisfaction for e in self.engagement_tracking.values()) / len(self.engagement_tracking)
            if avg_satisfaction < 0.7:
                recommendations.append(f"用戶滿意度較低 ({avg_satisfaction:.1%})，建議優化通知內容和時機")
        
        # 基於系統性能
        total_queue_depth = sum(len(queue) for queue in self.delay_batch_queues.values())
        if total_queue_depth > self.alert_thresholds["queue_depth_warning"]:
            recommendations.append("通知佇列積壓，建議增加處理容量或優化批次策略")
        
        # 基於跨階段整合
        if self.cross_phase_tracking:
            complete_rate = len([t for t in self.cross_phase_tracking.values() if t.data_consistency_status == "complete"]) / len(self.cross_phase_tracking)
            if complete_rate < 0.8:
                recommendations.append(f"跨階段數據整合率較低 ({complete_rate:.1%})，建議加強Phase間的數據同步")
        
        return recommendations if recommendations else ["系統運行狀況良好，暫無優化建議"]

    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """獲取實時指標 - 對應JSON配置的real_time_data_access"""
        current_time = datetime.now()
        recent_cutoff = current_time - timedelta(minutes=5)
        
        recent_notifications = [
            record for record in self.notification_history
            if record.timestamp > recent_cutoff
        ]
        
        if not recent_notifications:
            return {
                "live_notification_monitoring": "no_recent_activity",
                "timestamp": current_time.isoformat()
            }
        
        successful_recent = len([
            r for r in recent_notifications
            if r.status in [NotificationStatus.DELIVERED, NotificationStatus.OPENED, NotificationStatus.CLICKED]
        ])
        
        channel_activity = defaultdict(int)
        for record in recent_notifications:
            channel_activity[record.channel.value] += 1
        
        return {
            "live_notification_monitoring": "active",
            "instant_user_engagement_tracking": {
                "recent_engagement_events": len([r for r in recent_notifications if r.status in [NotificationStatus.OPENED, NotificationStatus.CLICKED]]),
                "engagement_rate": len([r for r in recent_notifications if r.status in [NotificationStatus.OPENED, NotificationStatus.CLICKED]]) / len(recent_notifications) if recent_notifications else 0
            },
            "cross_phase_real_time_correlation": {
                "active_transactions": len([t for t in self.cross_phase_tracking.values() if t.data_consistency_status == "partial"]),
                "completed_transactions": len([t for t in self.cross_phase_tracking.values() if t.data_consistency_status == "complete"])
            },
            "performance_alert_triggers": {
                "current_queue_depth": sum(len(queue) for queue in self.delay_batch_queues.values()),
                "recent_success_rate": successful_recent / len(recent_notifications) if recent_notifications else 0,
                "alert_status": "healthy" if successful_recent / len(recent_notifications) > 0.9 else "warning"
            },
            "timestamp": current_time.isoformat(),
            "recent_5min_metrics": {
                "total_notifications": len(recent_notifications),
                "successful_notifications": successful_recent,
                "success_rate": successful_recent / len(recent_notifications),
                "channel_activity": dict(channel_activity)
            }
        }

# 全局實例
notification_monitor = NotificationSuccessRateMonitor()
