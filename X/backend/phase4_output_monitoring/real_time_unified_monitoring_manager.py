"""
🎯 Trading X - Phase4 Real-Time Unified Monitoring Manager
統一監控管理器 - 符合 JSON Schema 規範的企業級監控系統
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
from pathlib import Path
from collections import defaultdict, deque

# 導入通知系統
try:
    from .notification_service.notification_manager import (
        NotificationManager, 
        NotificationChannel,
        NotificationPriority
    )
    NOTIFICATION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ 通知系統不可用: {e}")
    NOTIFICATION_AVAILABLE = False
    
    # 定義備用類避免 NameError
    class NotificationPriority(Enum):
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"
    
    class NotificationChannel(Enum):
        EMAIL = "email"
        DISCORD = "discord"

logger = logging.getLogger(__name__)

class MonitoringStatus(Enum):
    """監控狀態枚舉"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    DEGRADED = "degraded"

class AlertLevel(Enum):
    """告警級別"""
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class SystemMetrics:
    """系統指標"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    active_connections: int
    signal_processing_rate: float
    error_rate: float
    response_time_ms: float

@dataclass
class PhaseStatus:
    """Phase 狀態"""
    phase_name: str
    status: MonitoringStatus
    last_update: datetime
    metrics: Dict[str, Any]
    error_count: int = 0
    uptime_seconds: float = 0.0

@dataclass
class AlertRecord:
    """告警記錄"""
    id: str
    timestamp: datetime
    level: AlertLevel
    phase: str
    message: str
    resolved: bool = False
    resolution_time: Optional[datetime] = None

class RealTimeUnifiedMonitoringManager:
    """實時統一監控管理器"""
    
    def __init__(self):
        """初始化監控管理器"""
        self.monitoring_enabled = False
        self.start_time = datetime.now()
        
        # 系統狀態
        self.phase_statuses: Dict[str, PhaseStatus] = {}
        self.system_metrics: deque = deque(maxlen=1000)  # 保留最近1000條記錄
        self.alert_records: deque = deque(maxlen=500)    # 保留最近500條告警
        
        # 監控配置
        self.monitoring_interval = 5.0  # 5秒監控間隔
        self.alert_thresholds = {
            "cpu_usage_warning": 70.0,
            "cpu_usage_critical": 90.0,
            "memory_usage_warning": 80.0,
            "memory_usage_critical": 95.0,
            "error_rate_warning": 0.05,
            "error_rate_critical": 0.15,
            "response_time_warning": 1000.0,  # 1秒
            "response_time_critical": 3000.0  # 3秒
        }
        
        # 通知系統
        self.notification_manager = None
        if NOTIFICATION_AVAILABLE:
            try:
                self.notification_manager = NotificationManager()
                logger.info("✅ 通知系統初始化成功")
            except Exception as e:
                logger.warning(f"⚠️ 通知系統初始化失敗: {e}")
        
        # 回調函數
        self.status_callbacks: List[Callable] = []
        self.alert_callbacks: List[Callable] = []
        
        # 監控任務
        self.monitoring_task = None
        
        logger.info("✅ 統一監控管理器初始化完成")
    
    async def start_monitoring(self):
        """啟動監控系統"""
        if self.monitoring_enabled:
            logger.warning("監控系統已經在運行中")
            return
        
        self.monitoring_enabled = True
        self.start_time = datetime.now()
        
        # 初始化 Phase 狀態
        self._initialize_phase_statuses()
        
        # 啟動監控任務
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("🚀 統一監控系統已啟動")
        
        # 發送啟動通知
        await self._send_notification(
            "監控系統啟動",
            "Trading X 統一監控系統已成功啟動",
            NotificationPriority.INFO
        )
    
    async def stop_monitoring(self):
        """停止監控系統"""
        if not self.monitoring_enabled:
            return
        
        self.monitoring_enabled = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🔄 統一監控系統已停止")
    
    def _initialize_phase_statuses(self):
        """初始化 Phase 狀態"""
        phases = ["Phase1", "Phase2", "Phase3", "Phase4", "Phase5"]
        
        for phase in phases:
            self.phase_statuses[phase] = PhaseStatus(
                phase_name=phase,
                status=MonitoringStatus.INACTIVE,
                last_update=datetime.now(),
                metrics={},
                error_count=0,
                uptime_seconds=0.0
            )
    
    async def _monitoring_loop(self):
        """監控主循環"""
        logger.info("📊 監控主循環已啟動")
        
        while self.monitoring_enabled:
            try:
                # 收集系統指標
                metrics = await self._collect_system_metrics()
                self.system_metrics.append(metrics)
                
                # 檢查告警條件
                await self._check_alert_conditions(metrics)
                
                # 更新 Phase 狀態
                await self._update_phase_statuses()
                
                # 觸發狀態回調
                await self._trigger_status_callbacks()
                
                # 等待下一次監控
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 監控循環錯誤: {e}")
                await asyncio.sleep(1.0)
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """收集系統指標"""
        current_time = datetime.now()
        
        # 基礎指標（真實系統中應該從實際系統獲取）
        try:
            import psutil
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent
        except ImportError:
            # 使用模擬數據作為後備
            cpu_usage = 25.0 + (time.time() % 10) * 2  # 模擬 25-45% CPU
            memory_usage = 60.0 + (time.time() % 5) * 3  # 模擬 60-75% 內存
        
        # 計算業務指標
        active_connections = len(self.phase_statuses)
        signal_processing_rate = self._calculate_signal_processing_rate()
        error_rate = self._calculate_error_rate()
        response_time_ms = self._calculate_average_response_time()
        
        return SystemMetrics(
            timestamp=current_time,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            active_connections=active_connections,
            signal_processing_rate=signal_processing_rate,
            error_rate=error_rate,
            response_time_ms=response_time_ms
        )
    
    def _calculate_signal_processing_rate(self) -> float:
        """計算信號處理速率"""
        # 從最近的指標計算處理速率
        if len(self.system_metrics) < 2:
            return 0.0
        
        recent_metrics = list(self.system_metrics)[-10:]  # 最近10個指標
        return len(recent_metrics) / max(1, len(recent_metrics) * self.monitoring_interval)
    
    def _calculate_error_rate(self) -> float:
        """計算錯誤率"""
        total_errors = sum(status.error_count for status in self.phase_statuses.values())
        total_operations = max(1, len(self.system_metrics))
        return total_errors / total_operations
    
    def _calculate_average_response_time(self) -> float:
        """計算平均響應時間"""
        if not self.system_metrics:
            return 0.0
        
        recent_metrics = list(self.system_metrics)[-5:]  # 最近5個指標
        return sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics)
    
    async def _check_alert_conditions(self, metrics: SystemMetrics):
        """檢查告警條件"""
        alerts = []
        
        # CPU 使用率告警
        if metrics.cpu_usage > self.alert_thresholds["cpu_usage_critical"]:
            alerts.append(("CPU使用率過高", f"CPU使用率: {metrics.cpu_usage:.1f}%", AlertLevel.CRITICAL))
        elif metrics.cpu_usage > self.alert_thresholds["cpu_usage_warning"]:
            alerts.append(("CPU使用率告警", f"CPU使用率: {metrics.cpu_usage:.1f}%", AlertLevel.WARNING))
        
        # 內存使用率告警
        if metrics.memory_usage > self.alert_thresholds["memory_usage_critical"]:
            alerts.append(("內存使用率過高", f"內存使用率: {metrics.memory_usage:.1f}%", AlertLevel.CRITICAL))
        elif metrics.memory_usage > self.alert_thresholds["memory_usage_warning"]:
            alerts.append(("內存使用率告警", f"內存使用率: {metrics.memory_usage:.1f}%", AlertLevel.WARNING))
        
        # 錯誤率告警
        if metrics.error_rate > self.alert_thresholds["error_rate_critical"]:
            alerts.append(("系統錯誤率過高", f"錯誤率: {metrics.error_rate:.3f}", AlertLevel.CRITICAL))
        elif metrics.error_rate > self.alert_thresholds["error_rate_warning"]:
            alerts.append(("系統錯誤率告警", f"錯誤率: {metrics.error_rate:.3f}", AlertLevel.WARNING))
        
        # 響應時間告警
        if metrics.response_time_ms > self.alert_thresholds["response_time_critical"]:
            alerts.append(("系統響應過慢", f"響應時間: {metrics.response_time_ms:.1f}ms", AlertLevel.CRITICAL))
        elif metrics.response_time_ms > self.alert_thresholds["response_time_warning"]:
            alerts.append(("系統響應告警", f"響應時間: {metrics.response_time_ms:.1f}ms", AlertLevel.WARNING))
        
        # 處理告警
        for title, message, level in alerts:
            await self._create_alert(title, message, level, "System")
    
    async def _create_alert(self, title: str, message: str, level: AlertLevel, phase: str):
        """創建告警"""
        alert_id = f"{phase}_{int(time.time())}"
        
        alert = AlertRecord(
            id=alert_id,
            timestamp=datetime.now(),
            level=level,
            phase=phase,
            message=f"{title}: {message}",
            resolved=False
        )
        
        self.alert_records.append(alert)
        
        # 發送通知
        priority = NotificationPriority.CRITICAL if level == AlertLevel.CRITICAL else NotificationPriority.HIGH
        await self._send_notification(title, message, priority)
        
        # 觸發告警回調
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"告警回調錯誤: {e}")
        
        logger.warning(f"🚨 {level.value.upper()} 告警: {alert.message}")
    
    async def _update_phase_statuses(self):
        """更新 Phase 狀態"""
        current_time = datetime.now()
        
        for phase_name in self.phase_statuses:
            status = self.phase_statuses[phase_name]
            
            # 更新運行時間
            if status.status == MonitoringStatus.ACTIVE:
                time_diff = (current_time - status.last_update).total_seconds()
                status.uptime_seconds += time_diff
            
            status.last_update = current_time
    
    async def _trigger_status_callbacks(self):
        """觸發狀態回調"""
        for callback in self.status_callbacks:
            try:
                await callback(self.get_monitoring_summary())
            except Exception as e:
                logger.error(f"狀態回調錯誤: {e}")
    
    async def _send_notification(self, title: str, message: str, priority: NotificationPriority):
        """發送通知"""
        if self.notification_manager:
            try:
                await self.notification_manager.send_notification(
                    title=title,
                    message=message,
                    channel=NotificationChannel.EMAIL,  # 默認使用郵件
                    priority=priority,
                    metadata={"source": "monitoring_system"}
                )
            except Exception as e:
                logger.error(f"發送通知失敗: {e}")
    
    # 公共接口方法
    
    def register_status_callback(self, callback: Callable):
        """註冊狀態回調"""
        self.status_callbacks.append(callback)
    
    def register_alert_callback(self, callback: Callable):
        """註冊告警回調"""
        self.alert_callbacks.append(callback)
    
    def update_phase_status(self, phase_name: str, status: MonitoringStatus, metrics: Dict[str, Any] = None):
        """更新 Phase 狀態"""
        if phase_name in self.phase_statuses:
            phase_status = self.phase_statuses[phase_name]
            phase_status.status = status
            phase_status.last_update = datetime.now()
            if metrics:
                phase_status.metrics.update(metrics)
    
    def increment_phase_error(self, phase_name: str):
        """增加 Phase 錯誤計數"""
        if phase_name in self.phase_statuses:
            self.phase_statuses[phase_name].error_count += 1
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """獲取監控摘要"""
        current_metrics = self.system_metrics[-1] if self.system_metrics else None
        active_alerts = [alert for alert in self.alert_records if not alert.resolved]
        
        return {
            "monitoring_enabled": self.monitoring_enabled,
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "current_metrics": asdict(current_metrics) if current_metrics else None,
            "phase_statuses": {
                name: {
                    "status": status.status.value,
                    "last_update": status.last_update.isoformat(),
                    "error_count": status.error_count,
                    "uptime_seconds": status.uptime_seconds,
                    "metrics": status.metrics
                }
                for name, status in self.phase_statuses.items()
            },
            "active_alerts_count": len(active_alerts),
            "total_alerts_count": len(self.alert_records),
            "system_health": self._calculate_system_health()
        }
    
    def _calculate_system_health(self) -> str:
        """計算系統健康狀態"""
        active_alerts = [alert for alert in self.alert_records if not alert.resolved]
        critical_alerts = [alert for alert in active_alerts if alert.level == AlertLevel.CRITICAL]
        
        if critical_alerts:
            return "critical"
        elif len(active_alerts) > 5:
            return "degraded"
        elif self.monitoring_enabled:
            return "healthy"
        else:
            return "inactive"
    
    def get_recent_metrics(self, count: int = 10) -> List[Dict[str, Any]]:
        """獲取最近的指標"""
        recent = list(self.system_metrics)[-count:]
        return [asdict(metric) for metric in recent]
    
    def get_recent_alerts(self, count: int = 10) -> List[Dict[str, Any]]:
        """獲取最近的告警"""
        recent = list(self.alert_records)[-count:]
        return [asdict(alert) for alert in recent]

# 全局實例
unified_monitoring_manager = RealTimeUnifiedMonitoringManager()

# 便捷函數
async def start_unified_monitoring():
    """啟動統一監控"""
    await unified_monitoring_manager.start_monitoring()

async def stop_unified_monitoring():
    """停止統一監控"""
    await unified_monitoring_manager.stop_monitoring()

def get_monitoring_status() -> Dict[str, Any]:
    """獲取監控狀態"""
    return unified_monitoring_manager.get_monitoring_summary()
