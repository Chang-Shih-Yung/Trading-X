"""
信號可用性監控系統 - Trading X Phase 3
實時監控各信號區塊的健康狀態、可用性和品質指標
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import time
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class SignalStatus(Enum):
    """信號狀態枚舉"""
    AVAILABLE = "available"        # 可用
    UNAVAILABLE = "unavailable"    # 不可用
    DEGRADED = "degraded"         # 性能降級
    ERROR = "error"               # 錯誤狀態
    UNKNOWN = "unknown"           # 未知狀態

class AlertLevel(Enum):
    """告警級別"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class SignalHealthMetrics:
    """信號健康指標"""
    signal_name: str
    status: SignalStatus
    availability_rate: float       # 可用性率 (0.0-1.0)
    average_latency_ms: float      # 平均延遲（毫秒）
    success_rate: float           # 成功率 (0.0-1.0)
    error_count_24h: int          # 24小時錯誤數
    last_success_time: Optional[datetime]
    last_error_time: Optional[datetime]
    last_check_time: datetime
    quality_score: float          # 品質評分 (0.0-1.0)
    confidence_score: float       # 信心度評分 (0.0-1.0)
    
    # 性能統計
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    success_history: deque = field(default_factory=lambda: deque(maxlen=100))
    error_history: deque = field(default_factory=lambda: deque(maxlen=50))

@dataclass
class MonitoringAlert:
    """監控告警"""
    alert_id: str
    signal_name: str
    alert_level: AlertLevel
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_time: Optional[datetime] = None

@dataclass
class SignalMonitorConfig:
    """信號監控配置"""
    signal_name: str
    check_interval_seconds: int = 60      # 檢查間隔
    timeout_seconds: int = 30             # 超時時間
    max_latency_ms: float = 5000          # 最大延遲閾值
    min_success_rate: float = 0.8         # 最小成功率
    min_availability_rate: float = 0.9    # 最小可用性
    enable_alerts: bool = True            # 是否啟用告警
    custom_check_function: Optional[Callable] = None  # 自定義檢查函數

class SignalAvailabilityMonitor:
    """信號可用性監控器"""
    
    def __init__(self):
        self.signal_health_metrics: Dict[str, SignalHealthMetrics] = {}
        self.monitoring_configs: Dict[str, SignalMonitorConfig] = {}
        self.active_alerts: Dict[str, MonitoringAlert] = {}
        self.alert_history: List[MonitoringAlert] = []
        
        # 監控任務
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
        
        # 統計數據
        self.system_stats = {
            "total_checks": 0,
            "total_errors": 0,
            "total_alerts": 0,
            "uptime_start": datetime.now()
        }
        
        # 初始化預設信號監控配置
        self._initialize_default_configs()
        
        logger.info("✅ 信號可用性監控系統初始化完成")
    
    def _initialize_default_configs(self):
        """初始化預設的信號監控配置"""
        
        # Phase 1 核心信號
        default_signals = [
            ("precision_filter", "精準篩選器", 30, 60),
            ("market_condition", "市場條件分析", 45, 90),
            ("technical_analysis", "技術分析", 60, 120),
            
            # Phase 2 機制適應信號
            ("regime_analysis", "市場機制分析", 120, 300),
            ("fear_greed", "Fear & Greed 指標", 300, 600),
            ("trend_alignment", "趨勢一致性分析", 90, 180),
            
            # Phase 3 高階信號 (預留)
            ("market_depth", "市場深度分析", 60, 120),
            ("funding_rate", "資金費率分析", 600, 1200),
            ("smart_money", "聰明錢流向", 300, 600)
        ]
        
        for signal_name, description, interval, timeout in default_signals:
            self.monitoring_configs[signal_name] = SignalMonitorConfig(
                signal_name=signal_name,
                check_interval_seconds=interval,
                timeout_seconds=timeout,
                max_latency_ms=5000 if "analysis" in signal_name else 3000,
                min_success_rate=0.85 if signal_name in ["precision_filter", "technical_analysis"] else 0.80,
                min_availability_rate=0.95 if signal_name == "precision_filter" else 0.90
            )
            
            # 初始化健康指標
            self.signal_health_metrics[signal_name] = SignalHealthMetrics(
                signal_name=signal_name,
                status=SignalStatus.UNKNOWN,
                availability_rate=0.0,
                average_latency_ms=0.0,
                success_rate=0.0,
                error_count_24h=0,
                last_success_time=None,
                last_error_time=None,
                last_check_time=datetime.now(),
                quality_score=0.0,
                confidence_score=0.0
            )
        
        logger.info(f"📊 初始化 {len(default_signals)} 個信號監控配置")
    
    async def start_monitoring(self):
        """啟動監控系統"""
        if self.is_running:
            logger.warning("⚠️ 監控系統已經在運行中")
            return
        
        self.is_running = True
        logger.info("🚀 啟動信號可用性監控系統")
        
        # 為每個信號啟動監控任務
        for signal_name, config in self.monitoring_configs.items():
            task = asyncio.create_task(
                self._monitor_signal_loop(signal_name, config)
            )
            self.monitoring_tasks[signal_name] = task
            logger.info(f"📡 啟動 {signal_name} 監控任務 (間隔: {config.check_interval_seconds}s)")
        
        # 啟動統計和清理任務
        self.monitoring_tasks["stats_updater"] = asyncio.create_task(
            self._update_stats_loop()
        )
        self.monitoring_tasks["alert_cleaner"] = asyncio.create_task(
            self._cleanup_alerts_loop()
        )
    
    async def stop_monitoring(self):
        """停止監控系統"""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("🛑 停止信號可用性監控系統")
        
        # 取消所有監控任務
        for signal_name, task in self.monitoring_tasks.items():
            if not task.cancelled():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.monitoring_tasks.clear()
        logger.info("✅ 所有監控任務已停止")
    
    async def _monitor_signal_loop(self, signal_name: str, config: SignalMonitorConfig):
        """信號監控循環"""
        while self.is_running:
            try:
                start_time = time.time()
                
                # 執行信號檢查
                check_result = await self._check_signal_health(signal_name, config)
                
                # 更新健康指標
                await self._update_health_metrics(signal_name, check_result, start_time)
                
                # 檢查是否需要發送告警
                await self._check_and_send_alerts(signal_name)
                
                # 等待下次檢查
                await asyncio.sleep(config.check_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ {signal_name} 監控循環錯誤: {e}")
                await asyncio.sleep(min(config.check_interval_seconds, 60))
    
    async def _check_signal_health(self, signal_name: str, config: SignalMonitorConfig) -> Dict[str, Any]:
        """檢查信號健康狀態"""
        check_result = {
            "success": False,
            "latency_ms": 0.0,
            "error_message": None,
            "quality_score": 0.0,
            "confidence_score": 0.0,
            "additional_data": {}
        }
        
        try:
            # 如果有自定義檢查函數，使用它
            if config.custom_check_function:
                custom_result = await asyncio.wait_for(
                    config.custom_check_function(signal_name),
                    timeout=config.timeout_seconds
                )
                check_result.update(custom_result)
            else:
                # 預設檢查邏輯
                check_result.update(await self._default_signal_check(signal_name, config))
            
            self.system_stats["total_checks"] += 1
            
        except asyncio.TimeoutError:
            check_result["error_message"] = f"檢查超時 ({config.timeout_seconds}s)"
            self.system_stats["total_errors"] += 1
            
        except Exception as e:
            check_result["error_message"] = f"檢查異常: {str(e)}"
            self.system_stats["total_errors"] += 1
        
        return check_result
    
    async def _default_signal_check(self, signal_name: str, config: SignalMonitorConfig) -> Dict[str, Any]:
        """預設信號檢查邏輯"""
        start_time = time.time()
        
        # 模擬信號檢查過程
        result = {
            "success": True,
            "quality_score": 0.8,  # 預設品質評分
            "confidence_score": 0.75,  # 預設信心度
            "additional_data": {
                "check_type": "default",
                "signal_name": signal_name
            }
        }
        
        # 根據信號類型調整檢查邏輯
        if signal_name == "precision_filter":
            # 精準篩選器 - 高品質要求
            result["quality_score"] = 0.9
            result["confidence_score"] = 0.85
            
        elif signal_name == "market_condition":
            # 市場條件 - 中等品質要求
            result["quality_score"] = 0.8
            result["confidence_score"] = 0.75
            
        elif signal_name == "technical_analysis":
            # 技術分析 - 標準品質要求
            result["quality_score"] = 0.75
            result["confidence_score"] = 0.7
            
        elif "analysis" in signal_name:
            # 分析類信號 - 較長檢查時間
            await asyncio.sleep(0.1)  # 模擬計算時間
            result["quality_score"] = 0.7
            result["confidence_score"] = 0.65
        
        # 模擬偶爾的錯誤
        if signal_name == "market_depth" and time.time() % 100 < 5:  # 5% 錯誤率
            result["success"] = False
            result["quality_score"] = 0.0
            result["confidence_score"] = 0.0
            
        end_time = time.time()
        result["latency_ms"] = (end_time - start_time) * 1000
        
        return result
    
    async def _update_health_metrics(self, signal_name: str, check_result: Dict, start_time: float):
        """更新健康指標"""
        if signal_name not in self.signal_health_metrics:
            return
        
        metrics = self.signal_health_metrics[signal_name]
        current_time = datetime.now()
        latency = check_result["latency_ms"]
        
        # 更新響應時間歷史
        metrics.response_times.append(latency)
        metrics.average_latency_ms = sum(metrics.response_times) / len(metrics.response_times)
        
        # 更新成功/失敗歷史
        success = check_result["success"]
        metrics.success_history.append(success)
        
        if success:
            metrics.last_success_time = current_time
            metrics.quality_score = check_result.get("quality_score", 0.0)
            metrics.confidence_score = check_result.get("confidence_score", 0.0)
        else:
            metrics.last_error_time = current_time
            metrics.error_history.append({
                "timestamp": current_time,
                "error": check_result.get("error_message", "未知錯誤")
            })
            metrics.error_count_24h += 1
            metrics.quality_score = 0.0
            metrics.confidence_score = 0.0
        
        # 計算可用性和成功率
        metrics.success_rate = sum(metrics.success_history) / len(metrics.success_history)
        metrics.availability_rate = metrics.success_rate  # 簡化：可用性等於成功率
        
        # 更新狀態
        config = self.monitoring_configs[signal_name]
        
        if not success:
            metrics.status = SignalStatus.ERROR
        elif latency > config.max_latency_ms:
            metrics.status = SignalStatus.DEGRADED
        elif metrics.success_rate < config.min_success_rate:
            metrics.status = SignalStatus.DEGRADED
        elif metrics.availability_rate < config.min_availability_rate:
            metrics.status = SignalStatus.DEGRADED
        else:
            metrics.status = SignalStatus.AVAILABLE
        
        metrics.last_check_time = current_time
    
    async def _check_and_send_alerts(self, signal_name: str):
        """檢查並發送告警"""
        if signal_name not in self.signal_health_metrics:
            return
        
        metrics = self.signal_health_metrics[signal_name]
        config = self.monitoring_configs[signal_name]
        
        if not config.enable_alerts:
            return
        
        current_time = datetime.now()
        alert_id = f"{signal_name}_{current_time.strftime('%Y%m%d_%H%M%S')}"
        
        # 檢查各種告警條件
        alerts_to_send = []
        
        # 錯誤狀態告警
        if metrics.status == SignalStatus.ERROR:
            alerts_to_send.append(MonitoringAlert(
                alert_id=f"{alert_id}_error",
                signal_name=signal_name,
                alert_level=AlertLevel.ERROR,
                message=f"{signal_name} 信號處於錯誤狀態",
                timestamp=current_time
            ))
        
        # 性能降級告警
        elif metrics.status == SignalStatus.DEGRADED:
            alerts_to_send.append(MonitoringAlert(
                alert_id=f"{alert_id}_degraded",
                signal_name=signal_name,
                alert_level=AlertLevel.WARNING,
                message=f"{signal_name} 信號性能降級 (成功率: {metrics.success_rate:.1%})",
                timestamp=current_time
            ))
        
        # 高延遲告警
        if metrics.average_latency_ms > config.max_latency_ms:
            alerts_to_send.append(MonitoringAlert(
                alert_id=f"{alert_id}_latency",
                signal_name=signal_name,
                alert_level=AlertLevel.WARNING,
                message=f"{signal_name} 延遲過高: {metrics.average_latency_ms:.1f}ms",
                timestamp=current_time
            ))
        
        # 成功率低告警
        if metrics.success_rate < config.min_success_rate:
            alerts_to_send.append(MonitoringAlert(
                alert_id=f"{alert_id}_success_rate",
                signal_name=signal_name,
                alert_level=AlertLevel.WARNING,
                message=f"{signal_name} 成功率過低: {metrics.success_rate:.1%}",
                timestamp=current_time
            ))
        
        # 發送告警
        for alert in alerts_to_send:
            self.active_alerts[alert.alert_id] = alert
            self.alert_history.append(alert)
            self.system_stats["total_alerts"] += 1
            
            logger.warning(f"🚨 [{alert.alert_level.value.upper()}] {alert.message}")
    
    async def _update_stats_loop(self):
        """更新統計數據循環"""
        while self.is_running:
            try:
                # 清理24小時前的錯誤計數
                current_time = datetime.now()
                for metrics in self.signal_health_metrics.values():
                    # 清理過期的錯誤歷史
                    cutoff_time = current_time - timedelta(hours=24)
                    metrics.error_history = deque([
                        error for error in metrics.error_history 
                        if error["timestamp"] > cutoff_time
                    ], maxlen=50)
                    metrics.error_count_24h = len(metrics.error_history)
                
                await asyncio.sleep(3600)  # 每小時執行一次
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 統計更新錯誤: {e}")
                await asyncio.sleep(300)
    
    def record_signal_check(self, signal_name: str, success: bool, latency_ms: float, timestamp: datetime) -> str:
        """
        記錄信號檢查結果
        
        Args:
            signal_name: 信號名稱
            success: 檢查是否成功
            latency_ms: 延遲時間(毫秒)
            timestamp: 檢查時間戳
            
        Returns:
            str: 記錄結果描述
        """
        if signal_name not in self.signal_health_metrics:
            # 如果信號不存在，先初始化
            self.signal_health_metrics[signal_name] = SignalHealthMetrics(
                signal_name=signal_name,
                status=SignalStatus.UNKNOWN,
                availability_rate=0.0,
                average_latency_ms=0.0,
                success_rate=0.0,
                error_count_24h=0,
                last_success_time=None,
                last_error_time=None,
                last_check_time=timestamp,
                quality_score=0.0,
                confidence_score=0.0
            )
        
        metrics = self.signal_health_metrics[signal_name]
        
        # 更新檢查時間
        metrics.last_check_time = timestamp
        
        if success:
            # 成功檢查
            metrics.last_success_time = timestamp
            metrics.status = SignalStatus.AVAILABLE
            
            # 更新延遲統計 (簡單移動平均)
            if metrics.average_latency_ms == 0:
                metrics.average_latency_ms = latency_ms
            else:
                metrics.average_latency_ms = (metrics.average_latency_ms * 0.8 + latency_ms * 0.2)
            
            # 更新品質評分 (基於延遲)
            if latency_ms < 100:
                quality_bonus = 0.95
            elif latency_ms < 500:
                quality_bonus = 0.85
            elif latency_ms < 1000:
                quality_bonus = 0.75
            else:
                quality_bonus = 0.60
                
            metrics.quality_score = (metrics.quality_score * 0.7 + quality_bonus * 0.3)
            metrics.confidence_score = min(0.95, metrics.quality_score + 0.1)
            
            # 更新成功率 (簡化統計)
            if metrics.success_rate == 0:
                metrics.success_rate = 1.0
            else:
                metrics.success_rate = min(1.0, metrics.success_rate * 0.95 + 0.05)
            
            return f"✅ {signal_name} 檢查成功 (延遲: {latency_ms:.1f}ms)"
            
        else:
            # 失敗檢查
            metrics.last_error_time = timestamp
            metrics.status = SignalStatus.ERROR
            
            # 記錄錯誤
            error_record = {
                "timestamp": timestamp,
                "latency_ms": latency_ms,
                "error_type": "check_failure"
            }
            metrics.error_history.append(error_record)
            metrics.error_count_24h = len(metrics.error_history)
            
            # 降低成功率
            metrics.success_rate = max(0.0, metrics.success_rate * 0.9)
            
            # 降低品質評分
            metrics.quality_score = max(0.0, metrics.quality_score * 0.8)
            metrics.confidence_score = max(0.0, metrics.confidence_score * 0.8)
            
            return f"❌ {signal_name} 檢查失敗 (延遲: {latency_ms:.1f}ms)"

    async def _cleanup_alerts_loop(self):
        """清理告警循環"""
        while self.is_running:
            try:
                current_time = datetime.now()
                cutoff_time = current_time - timedelta(hours=72)  # 保留72小時
                
                # 清理舊告警
                self.alert_history = [
                    alert for alert in self.alert_history 
                    if alert.timestamp > cutoff_time
                ]
                
                # 清理已解決的活躍告警
                resolved_alerts = [
                    alert_id for alert_id, alert in self.active_alerts.items()
                    if alert.resolved and alert.resolved_time and alert.resolved_time < cutoff_time
                ]
                
                for alert_id in resolved_alerts:
                    del self.active_alerts[alert_id]
                
                await asyncio.sleep(3600)  # 每小時執行一次
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 告警清理錯誤: {e}")
                await asyncio.sleep(300)
    
    def register_custom_check(self, signal_name: str, check_function: Callable):
        """註冊自定義檢查函數"""
        if signal_name in self.monitoring_configs:
            self.monitoring_configs[signal_name].custom_check_function = check_function
            logger.info(f"✅ 為 {signal_name} 註冊自定義檢查函數")
        else:
            logger.error(f"❌ 信號 {signal_name} 不存在於監控配置中")
    
    def get_signal_health(self, signal_name: str) -> Optional[SignalHealthMetrics]:
        """獲取信號健康指標"""
        return self.signal_health_metrics.get(signal_name)
    
    def get_all_signal_health(self) -> Dict[str, SignalHealthMetrics]:
        """獲取所有信號健康指標"""
        return self.signal_health_metrics.copy()
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態概覽"""
        total_signals = len(self.signal_health_metrics)
        available_signals = sum(1 for m in self.signal_health_metrics.values() 
                              if m.status == SignalStatus.AVAILABLE)
        error_signals = sum(1 for m in self.signal_health_metrics.values() 
                          if m.status == SignalStatus.ERROR)
        degraded_signals = sum(1 for m in self.signal_health_metrics.values() 
                             if m.status == SignalStatus.DEGRADED)
        
        uptime = datetime.now() - self.system_stats["uptime_start"]
        
        return {
            "system_name": "Signal Availability Monitor",
            "is_running": self.is_running,
            "uptime_hours": uptime.total_seconds() / 3600,
            "total_signals": total_signals,
            "available_signals": available_signals,
            "error_signals": error_signals,
            "degraded_signals": degraded_signals,
            "system_health_rate": available_signals / total_signals if total_signals > 0 else 0,
            "active_alerts": len(self.active_alerts),
            "total_checks": self.system_stats["total_checks"],
            "total_errors": self.system_stats["total_errors"],
            "total_alerts": self.system_stats["total_alerts"],
            "error_rate": self.system_stats["total_errors"] / max(1, self.system_stats["total_checks"])
        }
    
    def get_alerts(self, 
                   level: Optional[AlertLevel] = None,
                   signal_name: Optional[str] = None,
                   active_only: bool = False) -> List[MonitoringAlert]:
        """獲取告警列表"""
        alerts = self.active_alerts.values() if active_only else self.alert_history
        
        filtered_alerts = alerts
        
        if level:
            filtered_alerts = [a for a in filtered_alerts if a.alert_level == level]
        
        if signal_name:
            filtered_alerts = [a for a in filtered_alerts if a.signal_name == signal_name]
        
        return list(filtered_alerts)

# 全局監控實例
signal_availability_monitor = SignalAvailabilityMonitor()
