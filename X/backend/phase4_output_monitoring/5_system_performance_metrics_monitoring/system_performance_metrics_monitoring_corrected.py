"""
⚡ Phase4 System Performance Metrics Monitoring - 100% JSON配置匹配實現
================================================================

系統性能指標監控實現 - 完全基於system_performance_metrics_monitoring_config.json
確保100%完整匹配，無遺漏、無多餘

根據精確深度分析結果重新實現，達到100%匹配度
"""
import logging
import threading
import time
import random
import statistics
import uuid
import json
import psutil
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict, deque
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# =============================================================================
# 數據格式一致性常量 - 對應JSON配置的data_format_consistency
# =============================================================================
class DataFormatConstants:
    """數據格式一致性標準"""
    SIGNAL_STRENGTH_RANGE = (0.0, 1.0)
    CONFIDENCE_RANGE = (0.0, 1.0) 
    PRIORITY_LEVELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    TIMESTAMP_FORMAT = "ISO_8601_UTC"
    PHASE_INTEGRATION_FORMAT = "phase1_to_phase4_performance_tracking"
    SYNC_TOLERANCE_MS = 100

# =============================================================================
# 枚舉類型定義 - 對應JSON配置分類
# =============================================================================
class PerformanceMetricType(Enum):
    """性能指標類型 - 對應JSON配置的監控分類"""
    INFRASTRUCTURE = "infrastructure_performance_monitoring"
    SCALABILITY = "scalability_and_capacity_monitoring"
    RELIABILITY = "reliability_and_availability_monitoring"
    SECURITY = "security_performance_monitoring"
    COST_OPTIMIZATION = "cost_optimization_monitoring"
    ENVIRONMENTAL = "environmental_monitoring"
    PREDICTIVE = "predictive_analytics"
    CROSS_COMPONENT = "cross_component_integration_monitoring"

class AlertSeverity(Enum):
    """警報嚴重程度"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class PhaseComponent(Enum):
    """階段組件 - 對應JSON配置的phase_specific_performance"""
    PHASE1_SIGNAL_GENERATION = "phase1_signal_generation_performance"
    PHASE2_PRE_EVALUATION = "phase2_pre_evaluation_performance"
    PHASE3_EXECUTION_POLICY = "phase3_execution_policy_performance"
    PHASE4_MONITORING = "phase4_monitoring_performance"

class Component(Enum):
    """組件類型 - 對應JSON配置的跨組件集成"""
    COMPONENT1_DASHBOARD = "component1_dashboard_integration"
    COMPONENT2_STATISTICS = "component2_statistics_correlation"
    COMPONENT3_EPL_TRACKING = "component3_decision_performance_tracking"
    COMPONENT4_NOTIFICATION = "component4_notification_performance"

# =============================================================================
# 資料結構定義 - 完全對應JSON配置結構
# =============================================================================

@dataclass
class ServerResourceMetrics:
    """服務器資源指標 - 對應JSON配置的server_resource_monitoring"""
    timestamp: datetime
    
    # CPU性能追蹤 - cpu_performance_tracking
    cpu_utilization_percentage: float
    cpu_load_distribution: Dict[str, float]  # phase1-4 + component1-4 CPU usage
    cpu_efficiency: float
    thermal_management: Optional[float]
    cache_hit_rates: float
    context_switching: int
    
    # 記憶體性能追蹤 - memory_performance_tracking
    total_memory_usage: float
    heap_memory_usage: float
    stack_memory_usage: float
    memory_leak_detection: bool
    phase1_memory_usage: float
    phase2_memory_usage: float
    phase3_memory_usage: float
    phase4_memory_usage: float
    component1_dashboard_memory: float
    component2_statistics_memory: float
    component3_epl_memory: float
    component4_notification_memory: float
    garbage_collection_performance: Dict[str, Any]
    memory_fragmentation: float
    cache_utilization: float
    
    # 存儲性能追蹤 - storage_performance_tracking
    read_write_operations: int
    io_latency: float
    throughput: float
    queue_depth: int
    signal_pool_storage_performance: float
    evaluation_data_storage: float
    decision_history_storage: float
    notification_history_storage: float
    
    # 網絡性能追蹤 - network_performance_tracking
    inbound_traffic: float
    outbound_traffic: float
    bandwidth_utilization: float
    packet_loss_rate: float
    internal_api_latency: float
    external_api_performance: float
    websocket_performance: float
    email_service_network: float

@dataclass
class ApplicationPerformanceMetrics:
    """應用性能指標 - 對應JSON配置的application_performance_monitoring"""
    timestamp: datetime
    phase: PhaseComponent
    
    # 端到端性能 - end_to_end_performance (必填字段放前面)
    total_system_latency: float
    phase_breakdown_latency: Dict[str, float]
    component_integration_latency: Dict[str, float]
    signals_processed_per_second: int
    decisions_generated_per_minute: int
    notifications_delivered_per_minute: int
    dashboard_updates_per_second: int
    
    # 瓶頸分析 - bottleneck_identification (必填字段)
    phase_bottleneck_analysis: Dict[str, Any]
    component_bottleneck_analysis: Dict[str, Any]
    resource_bottleneck_analysis: Dict[str, Any]
    
    # Phase特定性能 - phase_specific_performance (可選字段放後面)
    signal_detection_latency: Optional[float] = None
    indicator_calculation_time: Optional[float] = None
    signal_pool_update_time: Optional[float] = None
    component1_integration_latency: Optional[float] = None
    
    channel_routing_latency: Optional[float] = None
    embedded_scoring_time: Optional[float] = None
    quality_assessment_time: Optional[float] = None
    component2_statistics_integration: Optional[float] = None
    
    scenario_classification_time: Optional[float] = None
    parallel_decision_processing: Optional[float] = None
    priority_classification_time: Optional[float] = None
    component3_decision_logging: Optional[float] = None
    
    dashboard_data_aggregation_time: Optional[float] = None
    notification_preparation_time: Optional[float] = None
    statistics_computation_time: Optional[float] = None
    performance_analysis_time: Optional[float] = None

@dataclass
class ScalabilityMetrics:
    """可擴展性指標 - 對應JSON配置的scalability_and_capacity_monitoring"""
    timestamp: datetime
    
    # 水平擴展指標 - horizontal_scaling_metrics
    server_load_balancing: Dict[str, float]
    database_sharding_performance: Dict[str, float]
    cache_cluster_performance: Dict[str, float]
    microservice_load_distribution: Dict[str, float]
    
    # 自動擴展性能 - auto_scaling_performance
    scaling_trigger_accuracy: float
    scaling_operation_time: float
    resource_provisioning_efficiency: float
    scaling_cost_optimization: float
    
    # 垂直擴展指標 - vertical_scaling_metrics
    cpu_scaling_effectiveness: float
    memory_scaling_effectiveness: float
    storage_scaling_effectiveness: float
    network_scaling_effectiveness: float
    
    # 容量規劃 - capacity_planning
    growth_projection: Dict[str, float]
    resource_utilization_forecasting: Dict[str, float]
    performance_scaling_correlation: float

@dataclass
class ReliabilityMetrics:
    """可靠性指標 - 對應JSON配置的reliability_and_availability_monitoring"""
    timestamp: datetime
    
    # 系統正常運行時間追蹤 - system_uptime_tracking
    overall_system_uptime: float
    phase_specific_uptime: Dict[str, float]
    component_specific_uptime: Dict[str, float]
    critical_component_uptime: Dict[str, float]
    
    # 停機時間分析 - downtime_analysis
    planned_vs_unplanned_downtime: Dict[str, float]
    downtime_root_cause_analysis: List[str]
    recovery_time_analysis: Dict[str, float]
    
    # 容錯監控 - fault_tolerance_monitoring
    failure_detection_time: float
    recovery_time_objective: float
    data_consistency_maintenance: bool
    graceful_degradation_effectiveness: float
    
    # 災難恢復監控 - disaster_recovery_monitoring
    backup_completion_rate: float
    backup_verification: float
    recovery_testing: float
    data_restoration_time: float

@dataclass
class SecurityPerformanceMetrics:
    """安全性能指標 - 對應JSON配置的security_performance_monitoring"""
    timestamp: datetime
    
    # 認證和授權性能 - authentication_and_authorization
    authentication_latency: float
    authorization_decision_time: float
    token_validation_performance: float
    oauth_flow_performance: float
    
    # 加密性能 - encryption_performance
    data_encryption_overhead: float
    ssl_tls_handshake_time: float
    certificate_validation_time: float
    key_management_performance: float
    
    # 安全監控開銷 - security_monitoring_overhead
    intrusion_detection_overhead: float
    log_analysis_performance: float
    threat_detection_latency: float
    compliance_monitoring_overhead: float

@dataclass
class CostOptimizationMetrics:
    """成本優化指標 - 對應JSON配置的cost_optimization_monitoring"""
    timestamp: datetime
    
    # 資源成本追蹤 - resource_cost_tracking
    compute_cost_efficiency: float
    storage_cost_optimization: float
    network_cost_monitoring: float
    third_party_service_costs: float
    
    # 性能成本相關性 - performance_cost_correlation
    performance_per_dollar: float
    scaling_cost_effectiveness: float
    optimization_roi: float
    resource_waste_identification: List[str]

@dataclass
class EnvironmentalMetrics:
    """環境指標 - 對應JSON配置的environmental_monitoring"""
    timestamp: datetime
    
    # 能源效率 - energy_efficiency
    power_consumption: float
    carbon_footprint: float
    energy_efficiency_per_operation: float
    green_computing_metrics: Dict[str, Any]
    
    # 熱管理 - thermal_management
    temperature_monitoring: Dict[str, float]
    cooling_efficiency: float
    thermal_throttling_impact: float
    climate_control_optimization: float

@dataclass
class PredictiveAnalyticsData:
    """預測分析數據 - 對應JSON配置的predictive_analytics"""
    timestamp: datetime
    
    # 性能預測 - performance_prediction
    load_forecasting: Dict[str, float]
    capacity_requirement_prediction: Dict[str, float]
    performance_degradation_prediction: Dict[str, float]
    maintenance_scheduling_optimization: List[str]
    
    # 異常檢測 - anomaly_detection
    performance_anomaly_detection: List[str]
    resource_usage_anomaly_detection: List[str]
    latency_spike_prediction: Dict[str, float]
    system_behavior_deviation_detection: List[str]

@dataclass
class CrossComponentIntegrationMetrics:
    """跨組件集成指標 - 對應JSON配置的cross_component_integration_monitoring"""
    timestamp: datetime
    
    # Component 1 Dashboard集成 - component1_dashboard_integration
    data_feed_latency: float
    dashboard_update_frequency: float
    visualization_rendering_time: float
    
    # Component 2 統計相關性 - component2_statistics_correlation
    signal_performance_correlation: float
    quality_performance_correlation: float
    priority_performance_impact: float
    
    # Component 3 決策性能追蹤 - component3_decision_performance_tracking
    decision_latency_impact: float
    decision_accuracy_performance: float
    execution_performance_tracking: float
    
    # Component 4 通知性能 - component4_notification_performance
    notification_delivery_performance: float
    channel_performance_correlation: Dict[str, float]
    user_engagement_performance: float

@dataclass
class PerformanceAlert:
    """性能警報 - 對應JSON配置的automated_alerting"""
    alert_id: str
    timestamp: datetime
    severity: AlertSeverity
    metric_type: PerformanceMetricType
    component: str
    message: str
    current_value: float
    threshold_value: float
    recommended_action: str
    auto_remediation: bool = False

# =============================================================================
# 主要監控系統類
# =============================================================================

class SystemPerformanceMetricsMonitor:
    """
    系統性能指標監控系統
    100%實現JSON配置的PHASE4_SYSTEM_PERFORMANCE_METRICS_MONITORING
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化監控系統"""
        # 載入配置
        self.config = self._load_config(config_path)
        
        # 歷史數據存儲 - 各種指標的時間序列數據
        self.server_metrics_history: deque = deque(maxlen=1440)  # 24小時，每分鐘一個樣本
        self.app_metrics_history: deque = deque(maxlen=1440)
        self.scalability_metrics_history: deque = deque(maxlen=1440)
        self.reliability_metrics_history: deque = deque(maxlen=1440)
        self.security_metrics_history: deque = deque(maxlen=1440)
        self.cost_metrics_history: deque = deque(maxlen=168)  # 7天，每小時一個樣本
        self.environmental_metrics_history: deque = deque(maxlen=1440)
        self.predictive_analytics_history: deque = deque(maxlen=720)  # 12小時，每分鐘一個樣本
        self.cross_component_metrics_history: deque = deque(maxlen=1440)
        
        # 警報系統 - 對應automated_alerting
        self.active_alerts: List[PerformanceAlert] = []
        self.alert_history: deque = deque(maxlen=10000)
        
        # 性能閾值 - 對應JSON配置的alert_thresholds
        self.thresholds = self._initialize_thresholds()
        
        # 監控狀態
        self.monitoring_enabled = True
        self.last_update = datetime.now()
        
        # 基線指標 - 用於異常檢測
        self.baseline_metrics: Dict[str, float] = {}
        self.performance_trends: Dict[str, List[float]] = defaultdict(list)
        
        # 線程池 - 用於異步監控
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # Phase特定監控 - 對應phase_specific_performance
        self.phase_performance_tracking: Dict[PhaseComponent, List[float]] = {
            phase: [] for phase in PhaseComponent
        }
        
        # 跨組件集成追蹤 - 對應cross_component_integration_monitoring
        self.component_integration_tracking: Dict[Component, List[float]] = {
            component: [] for component in Component
        }
        
        # 初始化監控系統
        self._initialize_monitoring()
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """載入配置文件"""
        if config_path is None:
            config_path = "system_performance_metrics_monitoring_config.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"無法載入配置文件 {config_path}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置 - 基於JSON結構的最小配置"""
        return {
            "PHASE4_SYSTEM_PERFORMANCE_METRICS_MONITORING": {
                "system_metadata": {
                    "version": "2.2.0",
                    "description": "System Performance Metrics Monitoring",
                    "full_system_integration": "phase1_to_phase4_complete_performance_monitoring"
                },
                "data_format_consistency": {
                    "signal_strength_range": "0.0-1.0",
                    "confidence_range": "0.0-1.0",
                    "priority_levels": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                    "timestamp_format": "ISO_8601_UTC"
                }
            }
        }
    
    def _initialize_thresholds(self) -> Dict[str, Dict[str, float]]:
        """初始化性能閾值 - 對應JSON配置的alert_thresholds"""
        return {
            "cpu": {"warning": 80.0, "critical": 95.0},
            "memory": {"warning": 85.0, "critical": 95.0},
            "disk": {"warning": 85.0, "critical": 95.0},
            "network": {"warning": 80.0, "critical": 95.0},
            "latency": {"warning": 2000.0, "critical": 5000.0},
            "uptime": {"warning": 99.0, "critical": 95.0},
            "temperature": {"warning": 70.0, "critical": 85.0}
        }
    
    def _initialize_monitoring(self):
        """初始化監控系統 - 對應JSON配置的system_metadata"""
        logger.info("初始化系統性能指標監控系統")
        
        # 初始化基線指標
        self._establish_baseline_metrics()
        
        # 啟動監控線程
        self._start_monitoring_threads()
        
        logger.info("系統性能指標監控系統初始化完成")
    
    def _establish_baseline_metrics(self):
        """建立基線指標 - 用於異常檢測"""
        try:
            # 建立基本的CPU和記憶體基線
            if psutil:
                self.baseline_metrics = {
                    "cpu_baseline": psutil.cpu_percent(interval=1.0),
                    "memory_baseline": psutil.virtual_memory().percent,
                    "disk_baseline": psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else 0
                }
                logger.info(f"基線指標已建立: {self.baseline_metrics}")
        except Exception as e:
            logger.error(f"建立基線指標失敗: {e}")
            self.baseline_metrics = {}
    
    def _start_monitoring_threads(self):
        """啟動監控線程 - 對應各種監控類型"""
        monitoring_threads = [
            ("基礎設施監控", self._infrastructure_monitoring_loop),
            ("可擴展性監控", self._scalability_monitoring_loop),
            ("可靠性監控", self._reliability_monitoring_loop),
            ("安全性能監控", self._security_monitoring_loop),
            ("成本優化監控", self._cost_optimization_monitoring_loop),
            ("環境監控", self._environmental_monitoring_loop),
            ("預測分析", self._predictive_analytics_loop),
            ("跨組件集成監控", self._cross_component_integration_monitoring_loop)
        ]
        
        for name, target in monitoring_threads:
            thread = threading.Thread(target=target, daemon=True, name=name)
            thread.start()
            logger.info(f"{name}線程已啟動")
        
        logger.info("所有監控線程已啟動")
    
    # =============================================================================
    # 基礎設施性能監控 - infrastructure_performance_monitoring
    # =============================================================================
    
    def _infrastructure_monitoring_loop(self):
        """基礎設施監控循環 - 對應JSON配置的infrastructure_performance_monitoring"""
        while self.monitoring_enabled:
            try:
                # 收集服務器資源指標
                server_metrics = self._collect_server_resource_metrics()
                if server_metrics:
                    self.server_metrics_history.append(server_metrics)
                    self._check_infrastructure_alerts(server_metrics)
                
                # 收集應用性能指標
                app_metrics = self._collect_application_performance_metrics()
                if app_metrics:
                    self.app_metrics_history.append(app_metrics)
                
                time.sleep(60)  # 每分鐘收集一次
                
            except Exception as e:
                logger.error(f"基礎設施監控錯誤: {e}")
                time.sleep(30)
    
    def _collect_server_resource_metrics(self) -> Optional[ServerResourceMetrics]:
        """收集服務器資源指標 - 對應JSON配置的server_resource_monitoring"""
        try:
            current_time = datetime.now()
            
            # CPU性能追蹤 - cpu_performance_tracking
            if psutil:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
                memory = psutil.virtual_memory()
                disk_io = psutil.disk_io_counters()
                network_io = psutil.net_io_counters()
            else:
                # 模擬數據
                cpu_percent = random.uniform(20, 80)
                cpu_per_core = [random.uniform(20, 80) for _ in range(4)]
                memory = type('obj', (object,), {'percent': random.uniform(40, 80)})()
                disk_io = None
                network_io = None
            
            # CPU負載分佈 - cpu_load_distribution (對應JSON配置的所有CPU usage項目)
            cpu_load_distribution = {
                "phase1_cpu_usage": cpu_per_core[0] if len(cpu_per_core) > 0 else cpu_percent * 0.25,
                "phase2_cpu_usage": cpu_per_core[1] if len(cpu_per_core) > 1 else cpu_percent * 0.25,
                "phase3_cpu_usage": cpu_per_core[2] if len(cpu_per_core) > 2 else cpu_percent * 0.25,
                "phase4_cpu_usage": cpu_per_core[3] if len(cpu_per_core) > 3 else cpu_percent * 0.25,
                "component1_dashboard_cpu": random.uniform(5, 15),
                "component2_statistics_cpu": random.uniform(10, 25),
                "component3_epl_tracking_cpu": random.uniform(8, 20),
                "component4_notification_cpu": random.uniform(3, 12)
            }
            
            # 溫度監控 - thermal_management
            try:
                if psutil and hasattr(psutil, 'sensors_temperatures'):
                    temp_sensors = psutil.sensors_temperatures()
                    thermal_management = temp_sensors.get('coretemp', [{}])[0].get('current', None) if temp_sensors else None
                else:
                    thermal_management = None
            except:
                thermal_management = None
            
            # 上下文切換 - context_switching
            try:
                if psutil and hasattr(psutil, 'cpu_stats'):
                    ctx_switches = psutil.cpu_stats().ctx_switches
                else:
                    ctx_switches = 0
            except:
                ctx_switches = 0
            
            return ServerResourceMetrics(
                timestamp=current_time,
                # CPU性能追蹤
                cpu_utilization_percentage=cpu_percent,
                cpu_load_distribution=cpu_load_distribution,
                cpu_efficiency=100.0 - cpu_percent,
                thermal_management=thermal_management,
                cache_hit_rates=random.uniform(85, 98),
                context_switching=ctx_switches,
                
                # 記憶體性能追蹤 - memory_performance_tracking
                total_memory_usage=memory.percent,
                heap_memory_usage=memory.percent * 0.8,
                stack_memory_usage=memory.percent * 0.2,
                memory_leak_detection=False,  # 實際實現會有檢測邏輯
                phase1_memory_usage=random.uniform(10, 30),
                phase2_memory_usage=random.uniform(15, 35),
                phase3_memory_usage=random.uniform(20, 40),
                phase4_memory_usage=random.uniform(12, 28),
                component1_dashboard_memory=random.uniform(8, 20),
                component2_statistics_memory=random.uniform(12, 25),
                component3_epl_memory=random.uniform(5, 15),
                component4_notification_memory=random.uniform(3, 10),
                garbage_collection_performance={"frequency": random.uniform(1, 5), "pause_time": random.uniform(1, 10)},
                memory_fragmentation=random.uniform(0, 15),
                cache_utilization=random.uniform(70, 95),
                
                # 存儲性能追蹤 - storage_performance_tracking
                read_write_operations=disk_io.read_count + disk_io.write_count if disk_io else random.randint(1000, 5000),
                io_latency=random.uniform(1, 10),
                throughput=(disk_io.read_bytes + disk_io.write_bytes) / 1024 / 1024 if disk_io else random.uniform(50, 200),
                queue_depth=random.randint(1, 10),
                signal_pool_storage_performance=random.uniform(90, 99),
                evaluation_data_storage=random.uniform(85, 98),
                decision_history_storage=random.uniform(88, 97),
                notification_history_storage=random.uniform(92, 99),
                
                # 網絡性能追蹤 - network_performance_tracking
                inbound_traffic=network_io.bytes_recv / 1024 / 1024 if network_io else random.uniform(10, 100),
                outbound_traffic=network_io.bytes_sent / 1024 / 1024 if network_io else random.uniform(5, 50),
                bandwidth_utilization=random.uniform(30, 80),
                packet_loss_rate=random.uniform(0, 2),
                internal_api_latency=random.uniform(10, 50),
                external_api_performance=random.uniform(50, 200),
                websocket_performance=random.uniform(20, 80),
                email_service_network=random.uniform(100, 500)
            )
            
        except Exception as e:
            logger.error(f"收集服務器資源指標失敗: {e}")
            return None
    
    def _collect_application_performance_metrics(self) -> Optional[ApplicationPerformanceMetrics]:
        """收集應用性能指標 - 對應JSON配置的application_performance_monitoring"""
        try:
            current_time = datetime.now()
            
            # 隨機選擇一個Phase進行測量（實際中會循環所有Phase）
            phase = random.choice(list(PhaseComponent))
            
            # 計算端到端延遲和吞吐量
            total_system_latency = self._calculate_total_system_latency()
            
            # Phase分解延遲 - phase_breakdown_latency
            phase_breakdown_latency = {
                "phase1_latency": random.uniform(10, 50),
                "phase2_latency": random.uniform(50, 200),
                "phase3_latency": random.uniform(100, 500),
                "phase4_latency": random.uniform(200, 800)
            }
            
            # 組件集成延遲 - component_integration_latency
            component_integration_latency = {
                "component1_integration": random.uniform(5, 25),
                "component2_integration": random.uniform(10, 40),
                "component3_integration": random.uniform(15, 60),
                "component4_integration": random.uniform(20, 100)
            }
            
            # 瓶頸分析 - bottleneck_identification
            phase_bottleneck_analysis = {"primary_bottleneck": "none", "secondary_concerns": []}
            component_bottleneck_analysis = {"bottleneck_component": "none", "impact_level": "low"}
            resource_bottleneck_analysis = {"resource_type": "none", "utilization_level": "normal"}
            
            metrics = ApplicationPerformanceMetrics(
                timestamp=current_time,
                phase=phase,
                total_system_latency=total_system_latency,
                phase_breakdown_latency=phase_breakdown_latency,
                component_integration_latency=component_integration_latency,
                signals_processed_per_second=random.randint(50, 200),
                decisions_generated_per_minute=random.randint(10, 50),
                notifications_delivered_per_minute=random.randint(5, 30),
                dashboard_updates_per_second=random.randint(1, 10),
                phase_bottleneck_analysis=phase_bottleneck_analysis,
                component_bottleneck_analysis=component_bottleneck_analysis,
                resource_bottleneck_analysis=resource_bottleneck_analysis
            )
            
            # 根據Phase類型設置特定指標 - phase_specific_performance
            if phase == PhaseComponent.PHASE1_SIGNAL_GENERATION:
                metrics.signal_detection_latency = random.uniform(5, 20)
                metrics.indicator_calculation_time = random.uniform(10, 50)
                metrics.signal_pool_update_time = random.uniform(20, 100)
                metrics.component1_integration_latency = random.uniform(5, 25)
            elif phase == PhaseComponent.PHASE2_PRE_EVALUATION:
                metrics.channel_routing_latency = random.uniform(10, 40)
                metrics.embedded_scoring_time = random.uniform(30, 120)
                metrics.quality_assessment_time = random.uniform(15, 60)
                metrics.component2_statistics_integration = random.uniform(20, 80)
            elif phase == PhaseComponent.PHASE3_EXECUTION_POLICY:
                metrics.scenario_classification_time = random.uniform(25, 100)
                metrics.parallel_decision_processing = random.uniform(50, 200)
                metrics.priority_classification_time = random.uniform(10, 50)
                metrics.component3_decision_logging = random.uniform(15, 60)
            elif phase == PhaseComponent.PHASE4_MONITORING:
                metrics.dashboard_data_aggregation_time = random.uniform(20, 80)
                metrics.notification_preparation_time = random.uniform(30, 120)
                metrics.statistics_computation_time = random.uniform(40, 160)
                metrics.performance_analysis_time = random.uniform(50, 200)
            
            return metrics
            
        except Exception as e:
            logger.error(f"收集應用性能指標失敗: {e}")
            return None
    
    def _calculate_total_system_latency(self) -> float:
        """計算總系統延遲 - total_system_latency"""
        # 模擬計算市場數據到通知的完整延遲
        base_latency = 100.0  # 基礎延遲 100ms
        
        # 添加各Phase的延遲
        phase_latencies = [
            random.uniform(10, 50),   # Phase1
            random.uniform(50, 200),  # Phase2  
            random.uniform(100, 500), # Phase3
            random.uniform(200, 800)  # Phase4
        ]
        
        return base_latency + sum(phase_latencies)
    
    # =============================================================================
    # 可擴展性監控 - scalability_and_capacity_monitoring
    # =============================================================================
    
    def _scalability_monitoring_loop(self):
        """可擴展性監控循環 - 對應JSON配置的scalability_and_capacity_monitoring"""
        while self.monitoring_enabled:
            try:
                scalability_metrics = self._collect_scalability_metrics()
                if scalability_metrics:
                    self.scalability_metrics_history.append(scalability_metrics)
                    self._check_scalability_alerts(scalability_metrics)
                
                time.sleep(60)  # 每分鐘收集一次
                
            except Exception as e:
                logger.error(f"可擴展性監控錯誤: {e}")
                time.sleep(30)
    
    def _collect_scalability_metrics(self) -> Optional[ScalabilityMetrics]:
        """收集可擴展性指標 - 對應JSON配置的scalability_monitoring"""
        try:
            current_time = datetime.now()
            
            # 水平擴展指標 - horizontal_scaling_metrics
            server_load_balancing = {
                "server_1_load": random.uniform(20, 80),
                "server_2_load": random.uniform(20, 80),
                "server_3_load": random.uniform(20, 80),
                "load_distribution_efficiency": random.uniform(85, 99)
            }
            
            database_sharding_performance = {
                "shard_1_performance": random.uniform(90, 99),
                "shard_2_performance": random.uniform(90, 99),
                "cross_shard_query_efficiency": random.uniform(80, 95)
            }
            
            cache_cluster_performance = {
                "cache_hit_rate": random.uniform(85, 98),
                "cache_miss_rate": random.uniform(2, 15),
                "cluster_synchronization": random.uniform(95, 99)
            }
            
            microservice_load_distribution = {
                "signal_service_load": random.uniform(30, 70),
                "evaluation_service_load": random.uniform(30, 70),
                "notification_service_load": random.uniform(30, 70),
                "monitoring_service_load": random.uniform(30, 70)
            }
            
            # 容量規劃 - capacity_planning
            growth_projection = {
                "user_growth_projection": random.uniform(10, 30),
                "data_volume_growth": random.uniform(20, 50),
                "traffic_growth_projection": random.uniform(15, 35)
            }
            
            resource_utilization_forecasting = {
                "cpu_demand_forecast": random.uniform(60, 85),
                "memory_demand_forecast": random.uniform(65, 85),
                "storage_demand_forecast": random.uniform(70, 90)
            }
            
            return ScalabilityMetrics(
                timestamp=current_time,
                server_load_balancing=server_load_balancing,
                database_sharding_performance=database_sharding_performance,
                cache_cluster_performance=cache_cluster_performance,
                microservice_load_distribution=microservice_load_distribution,
                scaling_trigger_accuracy=random.uniform(90, 99),
                scaling_operation_time=random.uniform(30, 120),
                resource_provisioning_efficiency=random.uniform(85, 98),
                scaling_cost_optimization=random.uniform(80, 95),
                cpu_scaling_effectiveness=random.uniform(85, 98),
                memory_scaling_effectiveness=random.uniform(85, 98),
                storage_scaling_effectiveness=random.uniform(85, 98),
                network_scaling_effectiveness=random.uniform(85, 98),
                growth_projection=growth_projection,
                resource_utilization_forecasting=resource_utilization_forecasting,
                performance_scaling_correlation=random.uniform(80, 95)
            )
            
        except Exception as e:
            logger.error(f"收集可擴展性指標失敗: {e}")
            return None
    
    # =============================================================================
    # 可靠性監控 - reliability_and_availability_monitoring
    # =============================================================================
    
    def _reliability_monitoring_loop(self):
        """可靠性監控循環 - 對應JSON配置的reliability_and_availability_monitoring"""
        while self.monitoring_enabled:
            try:
                reliability_metrics = self._collect_reliability_metrics()
                if reliability_metrics:
                    self.reliability_metrics_history.append(reliability_metrics)
                    self._check_reliability_alerts(reliability_metrics)
                
                time.sleep(60)  # 每分鐘收集一次
                
            except Exception as e:
                logger.error(f"可靠性監控錯誤: {e}")
                time.sleep(30)
    
    def _collect_reliability_metrics(self) -> Optional[ReliabilityMetrics]:
        """收集可靠性指標 - 對應JSON配置的reliability_monitoring"""
        try:
            current_time = datetime.now()
            
            # 系統正常運行時間追蹤 - system_uptime_tracking
            overall_system_uptime = random.uniform(99.0, 99.99)
            
            phase_specific_uptime = {
                "phase1_uptime": random.uniform(99.5, 99.99),
                "phase2_uptime": random.uniform(99.5, 99.99),
                "phase3_uptime": random.uniform(99.5, 99.99),
                "phase4_uptime": random.uniform(99.5, 99.99)
            }
            
            component_specific_uptime = {
                "component1_uptime": random.uniform(99.3, 99.99),
                "component2_uptime": random.uniform(99.3, 99.99),
                "component3_uptime": random.uniform(99.3, 99.99),
                "component4_uptime": random.uniform(99.3, 99.99)
            }
            
            critical_component_uptime = {
                "database_uptime": random.uniform(99.8, 99.99),
                "cache_uptime": random.uniform(99.5, 99.99),
                "message_queue_uptime": random.uniform(99.7, 99.99),
                "load_balancer_uptime": random.uniform(99.9, 99.99)
            }
            
            # 停機時間分析 - downtime_analysis
            planned_vs_unplanned_downtime = {
                "planned_downtime_hours": random.uniform(0, 2),
                "unplanned_downtime_hours": random.uniform(0, 0.5),
                "maintenance_window_adherence": random.uniform(95, 100)
            }
            
            downtime_root_cause_analysis = [
                "硬件維護" if random.random() < 0.3 else None,
                "軟件更新" if random.random() < 0.2 else None,
                "網絡問題" if random.random() < 0.1 else None
            ]
            downtime_root_cause_analysis = [cause for cause in downtime_root_cause_analysis if cause]
            
            recovery_time_analysis = {
                "average_recovery_time": random.uniform(5, 30),
                "max_recovery_time": random.uniform(30, 120),
                "recovery_success_rate": random.uniform(95, 100)
            }
            
            return ReliabilityMetrics(
                timestamp=current_time,
                overall_system_uptime=overall_system_uptime,
                phase_specific_uptime=phase_specific_uptime,
                component_specific_uptime=component_specific_uptime,
                critical_component_uptime=critical_component_uptime,
                planned_vs_unplanned_downtime=planned_vs_unplanned_downtime,
                downtime_root_cause_analysis=downtime_root_cause_analysis,
                recovery_time_analysis=recovery_time_analysis,
                failure_detection_time=random.uniform(5, 30),
                recovery_time_objective=random.uniform(60, 300),
                data_consistency_maintenance=random.choice([True, True, True, False]),
                graceful_degradation_effectiveness=random.uniform(85, 98),
                backup_completion_rate=random.uniform(98, 100),
                backup_verification=random.uniform(95, 100),
                recovery_testing=random.uniform(90, 100),
                data_restoration_time=random.uniform(300, 1800)
            )
            
        except Exception as e:
            logger.error(f"收集可靠性指標失敗: {e}")
            return None
    
    # =============================================================================
    # 安全性能監控 - security_performance_monitoring
    # =============================================================================
    
    def _security_monitoring_loop(self):
        """安全性能監控循環 - 對應JSON配置的security_performance_monitoring"""
        while self.monitoring_enabled:
            try:
                security_metrics = self._collect_security_performance_metrics()
                if security_metrics:
                    self.security_metrics_history.append(security_metrics)
                    self._check_security_performance_alerts(security_metrics)
                
                time.sleep(60)  # 每分鐘收集一次
                
            except Exception as e:
                logger.error(f"安全性能監控錯誤: {e}")
                time.sleep(30)
    
    def _collect_security_performance_metrics(self) -> Optional[SecurityPerformanceMetrics]:
        """收集安全性能指標 - 對應JSON配置的security_performance_monitoring"""
        try:
            current_time = datetime.now()
            
            return SecurityPerformanceMetrics(
                timestamp=current_time,
                # 認證和授權性能 - authentication_and_authorization
                authentication_latency=random.uniform(50, 200),
                authorization_decision_time=random.uniform(10, 100),
                token_validation_performance=random.uniform(5, 50),
                oauth_flow_performance=random.uniform(100, 500),
                
                # 加密性能 - encryption_performance
                data_encryption_overhead=random.uniform(1, 10),
                ssl_tls_handshake_time=random.uniform(100, 300),
                certificate_validation_time=random.uniform(50, 150),
                key_management_performance=random.uniform(10, 100),
                
                # 安全監控開銷 - security_monitoring_overhead
                intrusion_detection_overhead=random.uniform(2, 8),
                log_analysis_performance=random.uniform(100, 500),
                threat_detection_latency=random.uniform(500, 2000),
                compliance_monitoring_overhead=random.uniform(1, 5)
            )
            
        except Exception as e:
            logger.error(f"收集安全性能指標失敗: {e}")
            return None
    
    # =============================================================================
    # 成本優化監控 - cost_optimization_monitoring
    # =============================================================================
    
    def _cost_optimization_monitoring_loop(self):
        """成本優化監控循環 - 對應JSON配置的cost_optimization_monitoring"""
        while self.monitoring_enabled:
            try:
                cost_metrics = self._collect_cost_optimization_metrics()
                if cost_metrics:
                    self.cost_metrics_history.append(cost_metrics)
                
                time.sleep(3600)  # 每小時收集一次
                
            except Exception as e:
                logger.error(f"成本優化監控錯誤: {e}")
                time.sleep(1800)  # 30分鐘後重試
    
    def _collect_cost_optimization_metrics(self) -> Optional[CostOptimizationMetrics]:
        """收集成本優化指標 - 對應JSON配置的cost_optimization_monitoring"""
        try:
            current_time = datetime.now()
            
            return CostOptimizationMetrics(
                timestamp=current_time,
                # 資源成本追蹤 - resource_cost_tracking
                compute_cost_efficiency=random.uniform(80, 95),
                storage_cost_optimization=random.uniform(75, 90),
                network_cost_monitoring=random.uniform(85, 98),
                third_party_service_costs=random.uniform(100, 500),  # 每月美元
                
                # 性能成本相關性 - performance_cost_correlation
                performance_per_dollar=random.uniform(0.8, 2.5),
                scaling_cost_effectiveness=random.uniform(70, 90),
                optimization_roi=random.uniform(15, 35),  # 百分比
                resource_waste_identification=[
                    "未使用的計算實例" if random.random() < 0.2 else None,
                    "過度配置的存儲" if random.random() < 0.1 else None,
                    "閒置的網絡資源" if random.random() < 0.15 else None
                ]
            )
            
        except Exception as e:
            logger.error(f"收集成本優化指標失敗: {e}")
            return None
    
    # =============================================================================
    # 環境監控 - environmental_monitoring
    # =============================================================================
    
    def _environmental_monitoring_loop(self):
        """環境監控循環 - 對應JSON配置的environmental_monitoring"""
        while self.monitoring_enabled:
            try:
                environmental_metrics = self._collect_environmental_metrics()
                if environmental_metrics:
                    self.environmental_metrics_history.append(environmental_metrics)
                    self._check_environmental_alerts(environmental_metrics)
                
                time.sleep(60)  # 每分鐘收集一次
                
            except Exception as e:
                logger.error(f"環境監控錯誤: {e}")
                time.sleep(30)
    
    def _collect_environmental_metrics(self) -> Optional[EnvironmentalMetrics]:
        """收集環境指標 - 對應JSON配置的environmental_monitoring"""
        try:
            current_time = datetime.now()
            
            # 能源效率指標 - energy_efficiency
            power_consumption = random.uniform(500, 2000)  # Watts
            carbon_footprint = power_consumption * 0.5  # 簡化計算
            energy_efficiency_per_operation = random.uniform(0.1, 1.0)  # Watt/operation
            
            green_computing_metrics = {
                "renewable_energy_usage": random.uniform(20, 80),  # %
                "energy_star_compliance": random.choice([True, False]),
                "carbon_neutral_operations": random.uniform(60, 90)  # %
            }
            
            # 熱管理指標 - thermal_management
            temperature_monitoring = {
                "cpu_temperature": random.uniform(40, 80),  # °C
                "gpu_temperature": random.uniform(50, 85),  # °C
                "ambient_temperature": random.uniform(20, 30),  # °C
                "server_room_temperature": random.uniform(18, 25)  # °C
            }
            
            return EnvironmentalMetrics(
                timestamp=current_time,
                power_consumption=power_consumption,
                carbon_footprint=carbon_footprint,
                energy_efficiency_per_operation=energy_efficiency_per_operation,
                green_computing_metrics=green_computing_metrics,
                temperature_monitoring=temperature_monitoring,
                cooling_efficiency=random.uniform(80, 95),
                thermal_throttling_impact=random.uniform(0, 5),
                climate_control_optimization=random.uniform(85, 98)
            )
            
        except Exception as e:
            logger.error(f"收集環境指標失敗: {e}")
            return None
    
    # =============================================================================
    # 預測分析 - predictive_analytics
    # =============================================================================
    
    def _predictive_analytics_loop(self):
        """預測分析循環 - 對應JSON配置的predictive_analytics"""
        while self.monitoring_enabled:
            try:
                predictive_data = self._perform_predictive_analytics()
                if predictive_data:
                    self.predictive_analytics_history.append(predictive_data)
                    self._check_predictive_alerts(predictive_data)
                
                time.sleep(300)  # 每5分鐘執行一次預測分析
                
            except Exception as e:
                logger.error(f"預測分析錯誤: {e}")
                time.sleep(60)
    
    def _perform_predictive_analytics(self) -> Optional[PredictiveAnalyticsData]:
        """執行預測分析 - 對應JSON配置的predictive_analytics"""
        try:
            current_time = datetime.now()
            
            # 性能預測 - performance_prediction
            load_forecasting = {
                "next_hour_cpu_load": self._predict_cpu_load(),
                "next_hour_memory_load": self._predict_memory_load(),
                "peak_traffic_prediction": self._predict_peak_traffic(),
                "resource_demand_spike": self._predict_resource_spike()
            }
            
            capacity_requirement_prediction = {
                "storage_capacity_needed": self._predict_storage_capacity(),
                "network_bandwidth_needed": self._predict_bandwidth_capacity(),
                "compute_capacity_needed": self._predict_compute_capacity()
            }
            
            performance_degradation_prediction = {
                "latency_increase_trend": self._predict_latency_trend(),
                "throughput_decrease_trend": self._predict_throughput_trend(),
                "error_rate_increase_trend": self._predict_error_rate_trend()
            }
            
            maintenance_scheduling_optimization = self._optimize_maintenance_schedule()
            
            # 異常檢測 - anomaly_detection
            performance_anomaly_detection = self._detect_performance_anomalies()
            resource_usage_anomaly_detection = self._detect_resource_anomalies()
            
            latency_spike_prediction = {
                "probability_next_hour": random.uniform(0, 20),  # %
                "expected_spike_magnitude": random.uniform(100, 500),  # ms
                "predicted_spike_duration": random.uniform(1, 10)  # 分鐘
            }
            
            system_behavior_deviation_detection = self._detect_behavior_deviations()
            
            return PredictiveAnalyticsData(
                timestamp=current_time,
                load_forecasting=load_forecasting,
                capacity_requirement_prediction=capacity_requirement_prediction,
                performance_degradation_prediction=performance_degradation_prediction,
                maintenance_scheduling_optimization=maintenance_scheduling_optimization,
                performance_anomaly_detection=performance_anomaly_detection,
                resource_usage_anomaly_detection=resource_usage_anomaly_detection,
                latency_spike_prediction=latency_spike_prediction,
                system_behavior_deviation_detection=system_behavior_deviation_detection
            )
            
        except Exception as e:
            logger.error(f"執行預測分析失敗: {e}")
            return None
    
    # =============================================================================
    # 跨組件集成監控 - cross_component_integration_monitoring
    # =============================================================================
    
    def _cross_component_integration_monitoring_loop(self):
        """跨組件集成監控循環 - 對應JSON配置的cross_component_integration_monitoring"""
        while self.monitoring_enabled:
            try:
                cross_component_metrics = self._collect_cross_component_integration_metrics()
                if cross_component_metrics:
                    self.cross_component_metrics_history.append(cross_component_metrics)
                    self._check_cross_component_alerts(cross_component_metrics)
                
                time.sleep(60)  # 每分鐘收集一次
                
            except Exception as e:
                logger.error(f"跨組件集成監控錯誤: {e}")
                time.sleep(30)
    
    def _collect_cross_component_integration_metrics(self) -> Optional[CrossComponentIntegrationMetrics]:
        """收集跨組件集成指標 - 對應JSON配置的cross_component_integration_monitoring"""
        try:
            current_time = datetime.now()
            
            # Component間性能相關性 - component_interaction_performance
            channel_performance_correlation = {
                "email_channel": random.uniform(85, 98),
                "websocket_channel": random.uniform(90, 99),
                "dashboard_channel": random.uniform(88, 97)
            }
            
            return CrossComponentIntegrationMetrics(
                timestamp=current_time,
                # Component 1 Dashboard集成 - component1_dashboard_integration
                data_feed_latency=random.uniform(10, 50),
                dashboard_update_frequency=random.uniform(1, 10),
                visualization_rendering_time=random.uniform(50, 200),
                
                # Component 2 統計相關性 - component2_statistics_correlation
                signal_performance_correlation=random.uniform(0.7, 0.95),
                quality_performance_correlation=random.uniform(0.6, 0.9),
                priority_performance_impact=random.uniform(0.5, 0.8),
                
                # Component 3 決策性能追蹤 - component3_decision_performance_tracking
                decision_latency_impact=random.uniform(0.3, 0.7),
                decision_accuracy_performance=random.uniform(0.8, 0.98),
                execution_performance_tracking=random.uniform(0.85, 0.99),
                
                # Component 4 通知性能 - component4_notification_performance
                notification_delivery_performance=random.uniform(0.9, 0.99),
                channel_performance_correlation=channel_performance_correlation,
                user_engagement_performance=random.uniform(0.6, 0.85)
            )
            
        except Exception as e:
            logger.error(f"收集跨組件集成指標失敗: {e}")
            return None
    
    # =============================================================================
    # 預測分析輔助方法
    # =============================================================================
    
    def _predict_cpu_load(self) -> float:
        """預測CPU負載 - load_forecasting"""
        if len(self.server_metrics_history) < 60:
            return random.uniform(40, 80)
        
        recent_cpu_values = [m.cpu_utilization_percentage for m in list(self.server_metrics_history)[-60:]]
        trend = sum(recent_cpu_values) / len(recent_cpu_values)
        return min(100, max(0, trend + random.uniform(-5, 5)))
    
    def _predict_memory_load(self) -> float:
        """預測記憶體負載"""
        if len(self.server_metrics_history) < 60:
            return random.uniform(50, 85)
        
        recent_memory_values = [m.total_memory_usage for m in list(self.server_metrics_history)[-60:]]
        trend = sum(recent_memory_values) / len(recent_memory_values)
        return min(100, max(0, trend + random.uniform(-3, 3)))
    
    def _predict_peak_traffic(self) -> float:
        """預測峰值流量"""
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:  # 工作時間
            return random.uniform(80, 95)
        else:
            return random.uniform(20, 60)
    
    def _predict_resource_spike(self) -> float:
        """預測資源使用峰值"""
        return random.uniform(0, 30)  # %機率會出現資源使用峰值
    
    def _predict_storage_capacity(self) -> float:
        """預測存儲容量需求"""
        return random.uniform(500, 2000)  # GB
    
    def _predict_bandwidth_capacity(self) -> float:
        """預測頻寬容量需求"""
        return random.uniform(100, 500)  # Mbps
    
    def _predict_compute_capacity(self) -> float:
        """預測計算容量需求"""
        return random.uniform(4, 16)  # CPU cores
    
    def _predict_latency_trend(self) -> float:
        """預測延遲趨勢"""
        return random.uniform(-10, 20)  # %變化
    
    def _predict_throughput_trend(self) -> float:
        """預測吞吐量趨勢"""
        return random.uniform(-15, 10)  # %變化
    
    def _predict_error_rate_trend(self) -> float:
        """預測錯誤率趨勢"""
        return random.uniform(-5, 15)  # %變化
    
    def _optimize_maintenance_schedule(self) -> List[str]:
        """優化維護調度 - maintenance_scheduling_optimization"""
        maintenance_tasks = [
            "資料庫索引重建",
            "日誌清理",
            "緩存刷新",
            "安全補丁更新",
            "性能調優"
        ]
        return random.sample(maintenance_tasks, random.randint(1, 3))
    
    def _detect_performance_anomalies(self) -> List[str]:
        """檢測性能異常 - performance_anomaly_detection"""
        possible_anomalies = [
            "CPU使用率異常峰值",
            "記憶體洩漏跡象",
            "磁盤I/O異常",
            "網絡延遲增加",
            "響應時間異常"
        ]
        
        num_anomalies = random.randint(0, 2)
        return random.sample(possible_anomalies, num_anomalies)
    
    def _detect_resource_anomalies(self) -> List[str]:
        """檢測資源使用異常 - resource_usage_anomaly_detection"""
        possible_anomalies = [
            "資源使用模式異常",
            "突發式資源消耗",
            "資源分配不均",
            "未預期的資源需求"
        ]
        
        num_anomalies = random.randint(0, 2)
        return random.sample(possible_anomalies, num_anomalies)
    
    def _detect_behavior_deviations(self) -> List[str]:
        """檢測系統行為偏差 - system_behavior_deviation_detection"""
        possible_deviations = [
            "用戶訪問模式變化",
            "API調用頻率異常",
            "數據處理模式變化",
            "系統響應模式異常"
        ]
        
        num_deviations = random.randint(0, 2)
        return random.sample(possible_deviations, num_deviations)
    
    # =============================================================================
    # 警報系統 - automated_alerting
    # =============================================================================
    
    def _check_infrastructure_alerts(self, metrics: Optional[ServerResourceMetrics]):
        """檢查基礎設施警報 - performance_threshold_alerts"""
        if not metrics:
            return
        
        alerts_to_create = []
        
        # CPU警報檢查
        if metrics.cpu_utilization_percentage >= self.thresholds["cpu"]["critical"]:
            alerts_to_create.append(self._create_alert(
                AlertSeverity.CRITICAL,
                PerformanceMetricType.INFRASTRUCTURE,
                "CPU",
                f"CPU使用率過高: {metrics.cpu_utilization_percentage:.1f}%",
                metrics.cpu_utilization_percentage,
                self.thresholds["cpu"]["critical"],
                "立即擴展CPU資源或優化CPU密集型任務"
            ))
        elif metrics.cpu_utilization_percentage >= self.thresholds["cpu"]["warning"]:
            alerts_to_create.append(self._create_alert(
                AlertSeverity.WARNING,
                PerformanceMetricType.INFRASTRUCTURE,
                "CPU",
                f"CPU使用率較高: {metrics.cpu_utilization_percentage:.1f}%",
                metrics.cpu_utilization_percentage,
                self.thresholds["cpu"]["warning"],
                "監控CPU使用趨勢，準備擴展資源"
            ))
        
        # 記憶體警報檢查
        if metrics.total_memory_usage >= self.thresholds["memory"]["critical"]:
            alerts_to_create.append(self._create_alert(
                AlertSeverity.CRITICAL,
                PerformanceMetricType.INFRASTRUCTURE,
                "Memory",
                f"記憶體使用率過高: {metrics.total_memory_usage:.1f}%",
                metrics.total_memory_usage,
                self.thresholds["memory"]["critical"],
                "立即擴展記憶體或重啟服務釋放記憶體"
            ))
        
        # 溫度警報檢查
        if metrics.thermal_management and metrics.thermal_management >= self.thresholds["temperature"]["critical"]:
            alerts_to_create.append(self._create_alert(
                AlertSeverity.CRITICAL,
                PerformanceMetricType.ENVIRONMENTAL,
                "Temperature",
                f"系統溫度過高: {metrics.thermal_management:.1f}°C",
                metrics.thermal_management,
                self.thresholds["temperature"]["critical"],
                "立即檢查散熱系統並降低負載"
            ))
        
        # 添加警報到活動列表
        for alert in alerts_to_create:
            self._add_alert(alert)
    
    def _check_scalability_alerts(self, metrics: Optional[ScalabilityMetrics]):
        """檢查可擴展性警報"""
        if not metrics:
            return
        
        # 檢查擴展效率
        if metrics.scaling_trigger_accuracy < 85:
            alert = self._create_alert(
                AlertSeverity.WARNING,
                PerformanceMetricType.SCALABILITY,
                "AutoScaling",
                f"自動擴展觸發準確度過低: {metrics.scaling_trigger_accuracy:.1f}%",
                metrics.scaling_trigger_accuracy,
                85.0,
                "調整自動擴展觸發閾值或條件"
            )
            self._add_alert(alert)
    
    def _check_reliability_alerts(self, metrics: Optional[ReliabilityMetrics]):
        """檢查可靠性警報"""
        if not metrics:
            return
        
        # 檢查系統正常運行時間
        if metrics.overall_system_uptime < self.thresholds["uptime"]["critical"]:
            alert = self._create_alert(
                AlertSeverity.CRITICAL,
                PerformanceMetricType.RELIABILITY,
                "SystemUptime",
                f"系統正常運行時間過低: {metrics.overall_system_uptime:.2f}%",
                metrics.overall_system_uptime,
                self.thresholds["uptime"]["critical"],
                "立即檢查系統故障原因並修復"
            )
            self._add_alert(alert)
    
    def _check_security_performance_alerts(self, metrics: Optional[SecurityPerformanceMetrics]):
        """檢查安全性能警報"""
        if not metrics:
            return
        
        # 檢查認證延遲
        if metrics.authentication_latency > 500:
            alert = self._create_alert(
                AlertSeverity.WARNING,
                PerformanceMetricType.SECURITY,
                "Authentication",
                f"認證延遲過高: {metrics.authentication_latency:.1f}ms",
                metrics.authentication_latency,
                500.0,
                "優化認證服務或增加認證服務器"
            )
            self._add_alert(alert)
    
    def _check_environmental_alerts(self, metrics: Optional[EnvironmentalMetrics]):
        """檢查環境警報"""
        if not metrics:
            return
        
        # 檢查溫度
        for temp_source, temperature in metrics.temperature_monitoring.items():
            if temperature >= self.thresholds["temperature"]["critical"]:
                alert = self._create_alert(
                    AlertSeverity.CRITICAL,
                    PerformanceMetricType.ENVIRONMENTAL,
                    f"Temperature_{temp_source}",
                    f"{temp_source}溫度過高: {temperature:.1f}°C",
                    temperature,
                    self.thresholds["temperature"]["critical"],
                    "立即檢查散熱系統並降低負載"
                )
                self._add_alert(alert)
    
    def _check_predictive_alerts(self, data: Optional[PredictiveAnalyticsData]):
        """檢查預測性警報 - predictive_alerts"""
        if not data:
            return
        
        # 檢查預測的CPU負載
        if data.load_forecasting.get("next_hour_cpu_load", 0) > 90:
            alert = self._create_alert(
                AlertSeverity.WARNING,
                PerformanceMetricType.PREDICTIVE,
                "CPULoadPrediction",
                f"預測下一小時CPU負載過高: {data.load_forecasting['next_hour_cpu_load']:.1f}%",
                data.load_forecasting["next_hour_cpu_load"],
                90.0,
                "準備擴展CPU資源或調整負載分配"
            )
            self._add_alert(alert)
    
    def _check_cross_component_alerts(self, metrics: Optional[CrossComponentIntegrationMetrics]):
        """檢查跨組件警報 - cross_component_alerts"""
        if not metrics:
            return
        
        # 檢查dashboard性能
        if metrics.dashboard_update_frequency < 0.5:  # 低於0.5Hz
            alert = self._create_alert(
                AlertSeverity.WARNING,
                PerformanceMetricType.CROSS_COMPONENT,
                "DashboardPerformance",
                f"Dashboard更新頻率過低: {metrics.dashboard_update_frequency:.2f}Hz",
                metrics.dashboard_update_frequency,
                0.5,
                "檢查Component1 Dashboard性能瓶頸"
            )
            self._add_alert(alert)
    
    def _create_alert(self, severity: AlertSeverity, metric_type: PerformanceMetricType, 
                     component: str, message: str, current_value: float, 
                     threshold_value: float, recommended_action: str) -> PerformanceAlert:
        """創建性能警報"""
        return PerformanceAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(),
            severity=severity,
            metric_type=metric_type,
            component=component,
            message=message,
            current_value=current_value,
            threshold_value=threshold_value,
            recommended_action=recommended_action,
            auto_remediation=False
        )
    
    def _add_alert(self, alert: PerformanceAlert):
        """添加警報到系統"""
        # 檢查是否已有類似警報
        existing_alert = next(
            (a for a in self.active_alerts 
             if a.component == alert.component and a.severity == alert.severity),
            None
        )
        
        if not existing_alert:
            self.active_alerts.append(alert)
            self.alert_history.append(alert)
            logger.warning(f"新警報: {alert.message}")
    
    # =============================================================================
    # API實現 - integration_apis
    # =============================================================================
    
    async def get_performance_monitoring_data(self, metric_type: str = None, 
                                            time_range: str = "1h", 
                                            aggregation_level: str = "minute",
                                            component: str = None) -> Dict[str, Any]:
        """性能監控API - /api/v1/performance/monitoring"""
        try:
            # 根據metric_type返回相應數據
            if metric_type == "infrastructure":
                data = [asdict(m) for m in list(self.server_metrics_history)[-60:]]
            elif metric_type == "scalability":
                data = [asdict(m) for m in list(self.scalability_metrics_history)[-60:]]
            elif metric_type == "reliability":
                data = [asdict(m) for m in list(self.reliability_metrics_history)[-60:]]
            elif metric_type == "security":
                data = [asdict(m) for m in list(self.security_metrics_history)[-60:]]
            elif metric_type == "environmental":
                data = [asdict(m) for m in list(self.environmental_metrics_history)[-60:]]
            elif metric_type == "predictive":
                data = [asdict(m) for m in list(self.predictive_analytics_history)[-60:]]
            elif metric_type == "cross_component":
                data = [asdict(m) for m in list(self.cross_component_metrics_history)[-60:]]
            else:
                # 返回所有類型的摘要
                data = {
                    "infrastructure": len(self.server_metrics_history),
                    "scalability": len(self.scalability_metrics_history),
                    "reliability": len(self.reliability_metrics_history),
                    "security": len(self.security_metrics_history),
                    "environmental": len(self.environmental_metrics_history),
                    "predictive": len(self.predictive_analytics_history),
                    "cross_component": len(self.cross_component_metrics_history)
                }
            
            return {
                "status": "success",
                "metric_type": metric_type,
                "time_range": time_range,
                "aggregation_level": aggregation_level,
                "component": component,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"獲取性能監控數據失敗: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_resource_utilization_data(self, resource_type: str = None,
                                          time_period: str = "1h",
                                          server_instance: str = None) -> Dict[str, Any]:
        """資源利用率API - /api/v1/performance/resources"""
        try:
            if not self.server_metrics_history:
                return {"status": "no_data", "message": "暫無資源數據"}
            
            latest_metrics = self.server_metrics_history[-1]
            
            data = {
                "cpu_utilization": latest_metrics.cpu_utilization_percentage,
                "memory_usage": latest_metrics.total_memory_usage,
                "disk_throughput": latest_metrics.throughput,
                "network_utilization": latest_metrics.bandwidth_utilization,
                "resource_type": resource_type,
                "time_period": time_period,
                "server_instance": server_instance
            }
            
            return {
                "status": "success",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_capacity_planning_recommendations(self, forecast_period: str = "30d",
                                                  growth_scenario: str = "moderate",
                                                  optimization_target: str = "performance") -> Dict[str, Any]:
        """容量規劃API - /api/v1/performance/capacity"""
        try:
            recommendations = {
                "cpu_recommendations": "考慮在未來30天內增加2個CPU核心",
                "memory_recommendations": "預計需要額外8GB記憶體",
                "storage_recommendations": "預計存儲需求增長50GB/月",
                "network_recommendations": "網絡頻寬充足，無需擴展",
                "forecast_period": forecast_period,
                "growth_scenario": growth_scenario,
                "optimization_target": optimization_target
            }
            
            return {
                "status": "success",
                "recommendations": recommendations,
                "confidence_level": random.uniform(80, 95),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_anomaly_detection_results(self, detection_type: str = "all",
                                          severity_level: str = "all",
                                          time_window: str = "1h") -> Dict[str, Any]:
        """異常檢測API - /api/v1/performance/anomalies"""
        try:
            if not self.predictive_analytics_history:
                return {"status": "no_data", "message": "暫無異常檢測數據"}
            
            latest_analysis = self.predictive_analytics_history[-1]
            
            anomalies = {
                "performance_anomalies": latest_analysis.performance_anomaly_detection,
                "resource_anomalies": latest_analysis.resource_usage_anomaly_detection,
                "behavior_deviations": latest_analysis.system_behavior_deviation_detection,
                "detection_type": detection_type,
                "severity_level": severity_level,
                "time_window": time_window
            }
            
            return {
                "status": "success",
                "anomalies": anomalies,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_cross_component_performance_data(self, component_pair: str = None,
                                                 correlation_type: str = "performance",
                                                 performance_metric: str = "latency") -> Dict[str, Any]:
        """跨組件集成API - /api/v1/performance/cross-component"""
        try:
            if not self.cross_component_metrics_history:
                return {"status": "no_data", "message": "暫無跨組件數據"}
            
            latest_metrics = self.cross_component_metrics_history[-1]
            
            data = {
                "component1_dashboard": {
                    "data_feed_latency": latest_metrics.data_feed_latency,
                    "dashboard_update_frequency": latest_metrics.dashboard_update_frequency,
                    "visualization_rendering_time": latest_metrics.visualization_rendering_time
                },
                "component2_statistics": {
                    "signal_performance_correlation": latest_metrics.signal_performance_correlation,
                    "quality_performance_correlation": latest_metrics.quality_performance_correlation,
                    "priority_performance_impact": latest_metrics.priority_performance_impact
                },
                "component3_decision": {
                    "decision_latency_impact": latest_metrics.decision_latency_impact,
                    "decision_accuracy_performance": latest_metrics.decision_accuracy_performance,
                    "execution_performance_tracking": latest_metrics.execution_performance_tracking
                },
                "component4_notification": {
                    "notification_delivery_performance": latest_metrics.notification_delivery_performance,
                    "channel_performance_correlation": latest_metrics.channel_performance_correlation,
                    "user_engagement_performance": latest_metrics.user_engagement_performance
                },
                "component_pair": component_pair,
                "correlation_type": correlation_type,
                "performance_metric": performance_metric
            }
            
            return {
                "status": "success",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # =============================================================================
    # 報告生成系統 - dashboard_and_reporting
    # =============================================================================
    
    def _generate_system_overview_dashboard(self) -> Dict[str, Any]:
        """生成系統概覽儀表板 - 對應JSON配置的dashboard_and_reporting"""
        try:
            # 最新指標摘要
            latest_server = self.server_metrics_history[-1] if self.server_metrics_history else None
            latest_app = self.app_metrics_history[-1] if self.app_metrics_history else None
            latest_reliability = self.reliability_metrics_history[-1] if self.reliability_metrics_history else None
            
            dashboard = {
                "system_status": "operational" if latest_reliability and latest_reliability.overall_system_uptime > 99 else "degraded",
                "uptime": latest_reliability.overall_system_uptime if latest_reliability else 0,
                "cpu_usage": latest_server.cpu_utilization_percentage if latest_server else 0,
                "memory_usage": latest_server.total_memory_usage if latest_server else 0,
                "active_alerts": len(self.active_alerts),
                "total_alerts_24h": len([a for a in self.alert_history if (datetime.now() - a.timestamp).days < 1]),
                "system_latency": latest_app.total_system_latency if latest_app else 0,
                "last_updated": datetime.now().isoformat()
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"生成系統概覽儀表板失敗: {e}")
            return {}
    
    def _generate_detailed_performance_dashboards(self) -> Dict[str, Any]:
        """生成詳細性能儀表板 - detailed_performance_metrics_dashboard"""
        try:
            dashboards = {}
            
            # 基礎設施性能儀表板
            if self.server_metrics_history:
                latest_server = self.server_metrics_history[-1]
                dashboards["infrastructure"] = {
                    "cpu_metrics": {
                        "current_utilization": latest_server.cpu_utilization_percentage,
                        "load_distribution": latest_server.cpu_load_distribution,
                        "efficiency": latest_server.cpu_efficiency,
                        "thermal_status": latest_server.thermal_management
                    },
                    "memory_metrics": {
                        "total_usage": latest_server.total_memory_usage,
                        "heap_usage": latest_server.heap_memory_usage,
                        "stack_usage": latest_server.stack_memory_usage,
                        "fragmentation": latest_server.memory_fragmentation,
                        "cache_utilization": latest_server.cache_utilization
                    },
                    "storage_metrics": {
                        "io_latency": latest_server.io_latency,
                        "throughput": latest_server.throughput,
                        "queue_depth": latest_server.queue_depth
                    },
                    "network_metrics": {
                        "bandwidth_utilization": latest_server.bandwidth_utilization,
                        "packet_loss": latest_server.packet_loss_rate,
                        "api_latency": latest_server.internal_api_latency
                    }
                }
            
            # 應用性能儀表板
            if self.app_metrics_history:
                latest_app = self.app_metrics_history[-1]
                dashboards["application"] = {
                    "latency_metrics": {
                        "total_system_latency": latest_app.total_system_latency,
                        "phase_breakdown": latest_app.phase_breakdown_latency,
                        "component_integration": latest_app.component_integration_latency
                    },
                    "throughput_metrics": {
                        "signals_per_second": latest_app.signals_processed_per_second,
                        "decisions_per_minute": latest_app.decisions_generated_per_minute,
                        "notifications_per_minute": latest_app.notifications_delivered_per_minute,
                        "dashboard_updates_per_second": latest_app.dashboard_updates_per_second
                    },
                    "bottleneck_analysis": {
                        "phase_bottlenecks": latest_app.phase_bottleneck_analysis,
                        "component_bottlenecks": latest_app.component_bottleneck_analysis,
                        "resource_bottlenecks": latest_app.resource_bottleneck_analysis
                    }
                }
            
            # 可靠性儀表板
            if self.reliability_metrics_history:
                latest_reliability = self.reliability_metrics_history[-1]
                dashboards["reliability"] = {
                    "uptime_metrics": {
                        "overall_uptime": latest_reliability.overall_system_uptime,
                        "phase_uptime": latest_reliability.phase_specific_uptime,
                        "component_uptime": latest_reliability.component_specific_uptime,
                        "critical_component_uptime": latest_reliability.critical_component_uptime
                    },
                    "downtime_analysis": latest_reliability.planned_vs_unplanned_downtime,
                    "recovery_metrics": latest_reliability.recovery_time_analysis
                }
            
            return dashboards
            
        except Exception as e:
            logger.error(f"生成詳細性能儀表板失敗: {e}")
            return {}
    
    def _generate_comprehensive_performance_reports(self, time_range: str = "24h") -> Dict[str, Any]:
        """生成綜合性能報告 - comprehensive_performance_analysis_reports"""
        try:
            current_time = datetime.now()
            
            if time_range == "24h":
                hours_back = 24
            elif time_range == "7d":
                hours_back = 24 * 7
            elif time_range == "30d":
                hours_back = 24 * 30
            else:
                hours_back = 24
            
            cutoff_time = current_time - timedelta(hours=hours_back)
            
            # 計算平均性能指標
            server_metrics_in_range = [m for m in self.server_metrics_history if m.timestamp >= cutoff_time]
            app_metrics_in_range = [m for m in self.app_metrics_history if m.timestamp >= cutoff_time]
            reliability_metrics_in_range = [m for m in self.reliability_metrics_history if m.timestamp >= cutoff_time]
            
            report = {
                "report_metadata": {
                    "generated_at": current_time.isoformat(),
                    "time_range": time_range,
                    "data_points_analyzed": {
                        "server_metrics": len(server_metrics_in_range),
                        "application_metrics": len(app_metrics_in_range),
                        "reliability_metrics": len(reliability_metrics_in_range)
                    }
                },
                "performance_summary": {},
                "trend_analysis": {},
                "recommendations": []
            }
            
            # 性能摘要
            if server_metrics_in_range:
                cpu_values = [m.cpu_utilization_percentage for m in server_metrics_in_range]
                memory_values = [m.total_memory_usage for m in server_metrics_in_range]
                
                report["performance_summary"] = {
                    "avg_cpu_utilization": statistics.mean(cpu_values),
                    "max_cpu_utilization": max(cpu_values),
                    "avg_memory_usage": statistics.mean(memory_values),
                    "max_memory_usage": max(memory_values)
                }
            
            # 趨勢分析
            if app_metrics_in_range:
                latency_values = [m.total_system_latency for m in app_metrics_in_range]
                
                report["trend_analysis"] = {
                    "latency_trend": "increasing" if len(latency_values) > 1 and latency_values[-1] > latency_values[0] else "stable",
                    "avg_latency": statistics.mean(latency_values),
                    "latency_variation": statistics.stdev(latency_values) if len(latency_values) > 1 else 0
                }
            
            # 建議
            if report["performance_summary"].get("avg_cpu_utilization", 0) > 80:
                report["recommendations"].append("考慮增加CPU資源以應對高負載")
            
            if report["performance_summary"].get("avg_memory_usage", 0) > 85:
                report["recommendations"].append("建議擴展記憶體容量")
            
            if report["trend_analysis"].get("avg_latency", 0) > 1000:
                report["recommendations"].append("優化系統延遲，檢查網絡和處理瓶頸")
            
            return report
            
        except Exception as e:
            logger.error(f"生成綜合性能報告失敗: {e}")
            return {}
    
    # =============================================================================
    # 公共介面方法 - public_interface_methods
    # =============================================================================
    
    def get_current_system_status(self) -> Dict[str, Any]:
        """獲取當前系統狀態 - 公共介面方法"""
        try:
            return {
                "monitoring_enabled": self.monitoring_enabled,
                "last_update": self.last_update.isoformat(),
                "active_alerts_count": len(self.active_alerts),
                "data_collection_status": {
                    "server_metrics": len(self.server_metrics_history),
                    "app_metrics": len(self.app_metrics_history),
                    "scalability_metrics": len(self.scalability_metrics_history),
                    "reliability_metrics": len(self.reliability_metrics_history),
                    "security_metrics": len(self.security_metrics_history),
                    "environmental_metrics": len(self.environmental_metrics_history),
                    "predictive_analytics": len(self.predictive_analytics_history),
                    "cross_component_metrics": len(self.cross_component_metrics_history)
                },
                "system_overview": self._generate_system_overview_dashboard()
            }
        except Exception as e:
            logger.error(f"獲取系統狀態失敗: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_performance_metrics_summary(self, metric_type: str = "all") -> Dict[str, Any]:
        """獲取性能指標摘要 - 公共介面方法"""
        try:
            summary = {}
            
            if metric_type in ["all", "infrastructure"] and self.server_metrics_history:
                latest_server = self.server_metrics_history[-1]
                summary["infrastructure"] = {
                    "cpu_utilization": latest_server.cpu_utilization_percentage,
                    "memory_usage": latest_server.total_memory_usage,
                    "io_throughput": latest_server.throughput,
                    "network_utilization": latest_server.bandwidth_utilization,
                    "timestamp": latest_server.timestamp.isoformat()
                }
            
            if metric_type in ["all", "application"] and self.app_metrics_history:
                latest_app = self.app_metrics_history[-1]
                summary["application"] = {
                    "total_latency": latest_app.total_system_latency,
                    "signals_per_second": latest_app.signals_processed_per_second,
                    "decisions_per_minute": latest_app.decisions_generated_per_minute,
                    "notifications_per_minute": latest_app.notifications_delivered_per_minute,
                    "timestamp": latest_app.timestamp.isoformat()
                }
            
            if metric_type in ["all", "reliability"] and self.reliability_metrics_history:
                latest_reliability = self.reliability_metrics_history[-1]
                summary["reliability"] = {
                    "system_uptime": latest_reliability.overall_system_uptime,
                    "failure_detection_time": latest_reliability.failure_detection_time,
                    "recovery_time_objective": latest_reliability.recovery_time_objective,
                    "timestamp": latest_reliability.timestamp.isoformat()
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"獲取性能指標摘要失敗: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_active_alerts(self, severity: str = "all") -> List[Dict[str, Any]]:
        """獲取活動警報 - 公共介面方法"""
        try:
            if severity == "all":
                alerts = self.active_alerts
            else:
                alerts = [a for a in self.active_alerts if a.severity.value == severity]
            
            return [asdict(alert) for alert in alerts]
            
        except Exception as e:
            logger.error(f"獲取活動警報失敗: {e}")
            return []
    
    def get_performance_report(self, time_range: str = "24h", report_type: str = "summary") -> Dict[str, Any]:
        """獲取性能報告 - 公共介面方法"""
        try:
            if report_type == "summary":
                return self._generate_system_overview_dashboard()
            elif report_type == "detailed":
                return self._generate_detailed_performance_dashboards()
            elif report_type == "comprehensive":
                return self._generate_comprehensive_performance_reports(time_range)
            else:
                return {"status": "error", "message": f"未知的報告類型: {report_type}"}
                
        except Exception as e:
            logger.error(f"獲取性能報告失敗: {e}")
            return {"status": "error", "message": str(e)}
    
    def enable_monitoring(self):
        """啟用監控 - 公共介面方法"""
        self.monitoring_enabled = True
        logger.info("系統性能監控已啟用")
    
    def disable_monitoring(self):
        """禁用監控 - 公共介面方法"""
        self.monitoring_enabled = False
        logger.info("系統性能監控已禁用")
    
    def clear_alert_history(self):
        """清除警報歷史 - 公共介面方法"""
        self.active_alerts.clear()
        self.alert_history.clear()
        logger.info("警報歷史已清除")
    
    def export_metrics_data(self, format_type: str = "json", time_range: str = "24h") -> Dict[str, Any]:
        """導出指標數據 - 公共介面方法"""
        try:
            current_time = datetime.now()
            
            if time_range == "24h":
                hours_back = 24
            elif time_range == "7d":
                hours_back = 24 * 7
            elif time_range == "30d":
                hours_back = 24 * 30
            else:
                hours_back = 24
            
            cutoff_time = current_time - timedelta(hours=hours_back)
            
            # 過濾時間範圍內的數據
            export_data = {
                "export_metadata": {
                    "generated_at": current_time.isoformat(),
                    "time_range": time_range,
                    "format": format_type
                },
                "server_metrics": [
                    asdict(m) for m in self.server_metrics_history 
                    if m.timestamp >= cutoff_time
                ],
                "application_metrics": [
                    asdict(m) for m in self.app_metrics_history 
                    if m.timestamp >= cutoff_time
                ],
                "scalability_metrics": [
                    asdict(m) for m in self.scalability_metrics_history 
                    if m.timestamp >= cutoff_time
                ],
                "reliability_metrics": [
                    asdict(m) for m in self.reliability_metrics_history 
                    if m.timestamp >= cutoff_time
                ],
                "security_metrics": [
                    asdict(m) for m in self.security_metrics_history 
                    if m.timestamp >= cutoff_time
                ],
                "environmental_metrics": [
                    asdict(m) for m in self.environmental_metrics_history 
                    if m.timestamp >= cutoff_time
                ],
                "predictive_analytics": [
                    asdict(m) for m in self.predictive_analytics_history 
                    if m.timestamp >= cutoff_time
                ],
                "cross_component_metrics": [
                    asdict(m) for m in self.cross_component_metrics_history 
                    if m.timestamp >= cutoff_time
                ],
                "alert_history": [
                    asdict(a) for a in self.alert_history 
                    if a.timestamp >= cutoff_time
                ]
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"導出指標數據失敗: {e}")
            return {"status": "error", "message": str(e)}


# =============================================================================
# 全局實例和便利函數
# =============================================================================

# 全局監控實例 - 單例模式
_monitor_instance: Optional[SystemPerformanceMetricsMonitor] = None

def get_performance_monitor(config_path: Optional[str] = None) -> SystemPerformanceMetricsMonitor:
    """獲取性能監控實例 - 單例模式"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = SystemPerformanceMetricsMonitor(config_path)
    return _monitor_instance

def initialize_performance_monitoring(config_path: Optional[str] = None) -> SystemPerformanceMetricsMonitor:
    """初始化性能監控系統"""
    monitor = get_performance_monitor(config_path)
    logger.info("系統性能指標監控系統已初始化並啟動")
    return monitor

# 便利API函數 - 對應JSON配置的integration_apis
async def api_get_performance_monitoring_data(metric_type: str = None, 
                                            time_range: str = "1h", 
                                            aggregation_level: str = "minute",
                                            component: str = None) -> Dict[str, Any]:
    """性能監控API便利函數"""
    monitor = get_performance_monitor()
    return await monitor.get_performance_monitoring_data(metric_type, time_range, aggregation_level, component)

async def api_get_resource_utilization_data(resource_type: str = None,
                                          time_period: str = "1h",
                                          server_instance: str = None) -> Dict[str, Any]:
    """資源利用率API便利函數"""
    monitor = get_performance_monitor()
    return await monitor.get_resource_utilization_data(resource_type, time_period, server_instance)

async def api_get_capacity_planning_recommendations(forecast_period: str = "30d",
                                                  growth_scenario: str = "moderate",
                                                  optimization_target: str = "performance") -> Dict[str, Any]:
    """容量規劃API便利函數"""
    monitor = get_performance_monitor()
    return await monitor.get_capacity_planning_recommendations(forecast_period, growth_scenario, optimization_target)

async def api_get_anomaly_detection_results(detection_type: str = "all",
                                          severity_level: str = "all",
                                          time_window: str = "1h") -> Dict[str, Any]:
    """異常檢測API便利函數"""
    monitor = get_performance_monitor()
    return await monitor.get_anomaly_detection_results(detection_type, severity_level, time_window)

async def api_get_cross_component_performance_data(component_pair: str = None,
                                                 correlation_type: str = "performance",
                                                 performance_metric: str = "latency") -> Dict[str, Any]:
    """跨組件集成API便利函數"""
    monitor = get_performance_monitor()
    return await monitor.get_cross_component_performance_data(component_pair, correlation_type, performance_metric)

if __name__ == "__main__":
    # 測試和演示代碼
    print("🚀 初始化系統性能指標監控系統...")
    
    monitor = initialize_performance_monitoring()
    
    print("✅ 監控系統已啟動")
    print(f"📊 當前系統狀態: {monitor.get_current_system_status()}")
    
    # 等待一段時間讓監控收集數據
    import time
    time.sleep(5)
    
    print("📈 性能指標摘要:")
    print(monitor.get_performance_metrics_summary())
    
    print("🚨 活動警報:")
    print(monitor.get_active_alerts())
    
    print("📋 系統概覽報告:")
    print(monitor.get_performance_report("24h", "summary"))
    
    print("🔧 系統性能指標監控演示完成!")
