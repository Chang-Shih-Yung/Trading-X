"""
⚡ Phase4 System Performance Metrics Monitoring
==============================================

系統性能指標監控實現 - 基於配置驅動的全方位性能追蹤
與 system_performance_metrics_monitoring_config.json 配置文件對應
"""

import asyncio
import logging
import json
import psutil
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class SystemSnapshot:
    """系統快照"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    process_count: int
    system_load: List[float]
    temperature: Optional[float] = None

@dataclass
class PerformanceMetrics:
    """性能指標"""
    metric_name: str
    current_value: float
    average_value: float
    min_value: float
    max_value: float
    threshold_warning: float
    threshold_critical: float
    trend: str  # "increasing", "decreasing", "stable"

@dataclass
class ApplicationMetrics:
    """應用程序指標"""
    timestamp: datetime
    process_id: int
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    open_files: int
    threads: int
    connections: int

class SystemPerformanceMonitor:
    """系統性能監控系統"""
    
    def __init__(self):
        # 載入配置文件
        self.config = self._load_config()
        
        # 性能數據存儲
        self.system_snapshots: deque = deque(maxlen=1440)  # 24小時的數據（每分鐘一次）
        self.app_metrics: deque = deque(maxlen=1440)
        
        # 性能閾值
        self.thresholds = {
            "cpu_warning": 80.0,
            "cpu_critical": 95.0,
            "memory_warning": 85.0,
            "memory_critical": 95.0,
            "disk_warning": 85.0,
            "disk_critical": 95.0,
            "response_time_warning": 2000,  # 2秒
            "response_time_critical": 5000  # 5秒
        }
        
        # 監控狀態
        self.monitoring_enabled = True
        self.monitoring_interval = 60  # 60秒采樣間隔
        self.last_update = datetime.now()
        
        # 性能追蹤
        self.performance_alerts: List[Dict] = []
        self.baseline_metrics: Dict[str, float] = {}
        
        # 線程池
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # 初始化監控系統
        self._initialize_monitoring()
        
    def _load_config(self) -> Dict[str, Any]:
        """載入配置文件"""
        try:
            config_path = Path(__file__).parent / "system_performance_metrics_monitoring_config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入性能監控配置失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            "PHASE4_SYSTEM_PERFORMANCE_METRICS_MONITORING": {
                "resource_monitoring": {
                    "cpu_utilization_tracking": {"sampling_rate": "1_minute"},
                    "memory_usage_monitoring": {"include_swap": True},
                    "disk_io_performance": {"track_read_write_speeds": True},
                    "network_throughput_analysis": {"track_bandwidth_usage": True}
                },
                "application_monitoring": {
                    "trading_system_performance": {"track_response_times": True},
                    "database_performance": {"track_query_times": True},
                    "api_endpoint_monitoring": {"track_request_latency": True}
                }
            }
        }
    
    def _initialize_monitoring(self):
        """初始化監控系統"""
        logger.info("初始化系統性能監控")
        
        # 設置基線指標
        self._establish_baseline_metrics()
        
        # 載入閾值配置
        self._load_threshold_configuration()
        
        # 啟動後台監控線程
        self.monitoring_thread = threading.Thread(target=self._background_monitoring, daemon=True)
        self.monitoring_thread.start()
        
    def _establish_baseline_metrics(self):
        """建立基線指標"""
        try:
            # 收集當前系統狀態作為基線
            current_snapshot = self._collect_system_snapshot()
            
            self.baseline_metrics = {
                "baseline_cpu": current_snapshot.cpu_usage,
                "baseline_memory": current_snapshot.memory_usage,
                "baseline_disk": current_snapshot.disk_usage,
                "baseline_established_at": datetime.now().isoformat()
            }
            
            logger.info(f"建立性能基線: CPU={current_snapshot.cpu_usage:.1f}%, Memory={current_snapshot.memory_usage:.1f}%")
            
        except Exception as e:
            logger.error(f"建立基線指標失敗: {e}")
    
    def _load_threshold_configuration(self):
        """載入閾值配置"""
        config = self.config.get("PHASE4_SYSTEM_PERFORMANCE_METRICS_MONITORING", {})
        
        # 更新閾值（如果配置中有定義）
        if "thresholds" in config:
            self.thresholds.update(config["thresholds"])
    
    def _background_monitoring(self):
        """後台監控線程"""
        while self.monitoring_enabled:
            try:
                # 收集系統快照
                snapshot = self._collect_system_snapshot()
                self.system_snapshots.append(snapshot)
                
                # 收集應用程序指標
                app_metrics = self._collect_application_metrics()
                if app_metrics:
                    self.app_metrics.append(app_metrics)
                
                # 檢查警報條件
                self._check_performance_alerts(snapshot)
                
                self.last_update = datetime.now()
                
                # 等待下一次采樣
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"後台監控出錯: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_system_snapshot(self) -> SystemSnapshot:
        """收集系統快照"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 記憶體使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 磁盤使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # 網絡IO
            network_io = psutil.net_io_counters()
            network_stats = {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv
            }
            
            # 進程數量
            process_count = len(psutil.pids())
            
            # 系統負載
            try:
                load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            except:
                load_avg = [0, 0, 0]
            
            # 溫度（如果可用）
            temperature = None
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    # 獲取第一個可用的溫度感測器
                    for sensor_name, sensor_list in temps.items():
                        if sensor_list:
                            temperature = sensor_list[0].current
                            break
            except:
                pass
            
            return SystemSnapshot(
                timestamp=datetime.now(),
                cpu_usage=cpu_percent,
                memory_usage=memory_percent,
                disk_usage=disk_percent,
                network_io=network_stats,
                process_count=process_count,
                system_load=list(load_avg),
                temperature=temperature
            )
            
        except Exception as e:
            logger.error(f"收集系統快照失敗: {e}")
            # 返回默認快照
            return SystemSnapshot(
                timestamp=datetime.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={},
                process_count=0,
                system_load=[0, 0, 0]
            )
    
    def _collect_application_metrics(self) -> Optional[ApplicationMetrics]:
        """收集應用程序指標"""
        try:
            # 獲取當前進程信息
            current_process = psutil.Process()
            
            # CPU使用率
            cpu_percent = current_process.cpu_percent()
            
            # 記憶體使用
            memory_info = current_process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024  # 轉換為MB
            memory_percent = current_process.memory_percent()
            
            # 打開的文件數
            try:
                open_files = len(current_process.open_files())
            except:
                open_files = 0
            
            # 線程數
            try:
                threads = current_process.num_threads()
            except:
                threads = 0
            
            # 網絡連接數
            try:
                connections = len(current_process.connections())
            except:
                connections = 0
            
            return ApplicationMetrics(
                timestamp=datetime.now(),
                process_id=current_process.pid,
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                memory_percent=memory_percent,
                open_files=open_files,
                threads=threads,
                connections=connections
            )
            
        except Exception as e:
            logger.error(f"收集應用程序指標失敗: {e}")
            return None
    
    def _check_performance_alerts(self, snapshot: SystemSnapshot):
        """檢查性能警報"""
        current_time = datetime.now()
        
        # 清理過舊的警報
        self.performance_alerts = [
            alert for alert in self.performance_alerts
            if current_time - datetime.fromisoformat(alert["timestamp"]) < timedelta(hours=1)
        ]
        
        # CPU警報
        if snapshot.cpu_usage > self.thresholds["cpu_critical"]:
            self.performance_alerts.append({
                "type": "critical",
                "metric": "cpu_usage",
                "value": snapshot.cpu_usage,
                "threshold": self.thresholds["cpu_critical"],
                "message": f"CPU使用率過高: {snapshot.cpu_usage:.1f}%",
                "timestamp": current_time.isoformat()
            })
        elif snapshot.cpu_usage > self.thresholds["cpu_warning"]:
            self.performance_alerts.append({
                "type": "warning",
                "metric": "cpu_usage",
                "value": snapshot.cpu_usage,
                "threshold": self.thresholds["cpu_warning"],
                "message": f"CPU使用率較高: {snapshot.cpu_usage:.1f}%",
                "timestamp": current_time.isoformat()
            })
        
        # 記憶體警報
        if snapshot.memory_usage > self.thresholds["memory_critical"]:
            self.performance_alerts.append({
                "type": "critical",
                "metric": "memory_usage",
                "value": snapshot.memory_usage,
                "threshold": self.thresholds["memory_critical"],
                "message": f"記憶體使用率過高: {snapshot.memory_usage:.1f}%",
                "timestamp": current_time.isoformat()
            })
        elif snapshot.memory_usage > self.thresholds["memory_warning"]:
            self.performance_alerts.append({
                "type": "warning",
                "metric": "memory_usage",
                "value": snapshot.memory_usage,
                "threshold": self.thresholds["memory_warning"],
                "message": f"記憶體使用率較高: {snapshot.memory_usage:.1f}%",
                "timestamp": current_time.isoformat()
            })
        
        # 磁盤警報
        if snapshot.disk_usage > self.thresholds["disk_critical"]:
            self.performance_alerts.append({
                "type": "critical",
                "metric": "disk_usage",
                "value": snapshot.disk_usage,
                "threshold": self.thresholds["disk_critical"],
                "message": f"磁盤使用率過高: {snapshot.disk_usage:.1f}%",
                "timestamp": current_time.isoformat()
            })
        elif snapshot.disk_usage > self.thresholds["disk_warning"]:
            self.performance_alerts.append({
                "type": "warning",
                "metric": "disk_usage",
                "value": snapshot.disk_usage,
                "threshold": self.thresholds["disk_warning"],
                "message": f"磁盤使用率較高: {snapshot.disk_usage:.1f}%",
                "timestamp": current_time.isoformat()
            })
    
    async def get_comprehensive_performance_report(self) -> Dict[str, Any]:
        """獲取綜合性能報告"""
        try:
            current_time = datetime.now()
            
            if not self.system_snapshots:
                return self._get_empty_performance_report()
            
            # 系統資源分析
            resource_analysis = self._analyze_system_resources()
            
            # 應用程序性能分析
            application_analysis = self._analyze_application_performance()
            
            # 性能趨勢分析
            trend_analysis = self._analyze_performance_trends()
            
            # 響應時間分析
            response_time_analysis = self._analyze_response_times()
            
            # 容量規劃分析
            capacity_analysis = self._analyze_capacity_planning()
            
            # 性能基準比較
            benchmark_analysis = self._compare_with_baseline()
            
            # 警報摘要
            alert_summary = self._get_alert_summary()
            
            return {
                "performance_metadata": {
                    "generated_at": current_time.isoformat(),
                    "monitoring_period": {
                        "start": min(s.timestamp for s in self.system_snapshots).isoformat(),
                        "end": max(s.timestamp for s in self.system_snapshots).isoformat()
                    },
                    "samples_collected": len(self.system_snapshots),
                    "last_update": self.last_update.isoformat()
                },
                "system_resource_analysis": resource_analysis,
                "application_performance_metrics": application_analysis,
                "performance_trend_analysis": trend_analysis,
                "response_time_insights": response_time_analysis,
                "capacity_planning_analysis": capacity_analysis,
                "baseline_comparison": benchmark_analysis,
                "alert_summary": alert_summary,
                "optimization_recommendations": self._generate_performance_recommendations()
            }
            
        except Exception as e:
            logger.error(f"生成性能報告失敗: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def _get_empty_performance_report(self) -> Dict[str, Any]:
        """獲取空性能報告"""
        return {
            "performance_metadata": {
                "generated_at": datetime.now().isoformat(),
                "samples_collected": 0,
                "status": "no_data"
            },
            "message": "沒有足夠的性能數據生成報告"
        }
    
    def _analyze_system_resources(self) -> Dict[str, Any]:
        """分析系統資源"""
        if not self.system_snapshots:
            return {}
        
        # 提取各項指標
        cpu_values = [s.cpu_usage for s in self.system_snapshots]
        memory_values = [s.memory_usage for s in self.system_snapshots]
        disk_values = [s.disk_usage for s in self.system_snapshots]
        
        # 計算統計摘要
        resource_stats = {
            "cpu_utilization": {
                "current": cpu_values[-1],
                "average": statistics.mean(cpu_values),
                "peak": max(cpu_values),
                "minimum": min(cpu_values),
                "std_deviation": statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0,
                "percentile_95": sorted(cpu_values)[int(0.95 * len(cpu_values))] if cpu_values else 0
            },
            "memory_utilization": {
                "current": memory_values[-1],
                "average": statistics.mean(memory_values),
                "peak": max(memory_values),
                "minimum": min(memory_values),
                "std_deviation": statistics.stdev(memory_values) if len(memory_values) > 1 else 0,
                "percentile_95": sorted(memory_values)[int(0.95 * len(memory_values))] if memory_values else 0
            },
            "disk_utilization": {
                "current": disk_values[-1],
                "average": statistics.mean(disk_values),
                "peak": max(disk_values),
                "minimum": min(disk_values),
                "std_deviation": statistics.stdev(disk_values) if len(disk_values) > 1 else 0,
                "percentile_95": sorted(disk_values)[int(0.95 * len(disk_values))] if disk_values else 0
            }
        }
        
        # 計算資源使用模式
        usage_patterns = self._analyze_usage_patterns()
        
        # 識別資源瓶頸
        bottlenecks = self._identify_resource_bottlenecks(resource_stats)
        
        return {
            "resource_statistics": resource_stats,
            "usage_patterns": usage_patterns,
            "resource_bottlenecks": bottlenecks,
            "resource_efficiency": self._calculate_resource_efficiency(resource_stats)
        }
    
    def _analyze_usage_patterns(self) -> Dict[str, Any]:
        """分析使用模式"""
        hourly_usage = defaultdict(lambda: {"cpu": [], "memory": [], "disk": []})
        
        for snapshot in self.system_snapshots:
            hour = snapshot.timestamp.hour
            hourly_usage[hour]["cpu"].append(snapshot.cpu_usage)
            hourly_usage[hour]["memory"].append(snapshot.memory_usage)
            hourly_usage[hour]["disk"].append(snapshot.disk_usage)
        
        # 計算各小時的平均使用率
        hourly_averages = {}
        for hour, usage_data in hourly_usage.items():
            hourly_averages[f"hour_{hour:02d}"] = {
                "cpu_avg": statistics.mean(usage_data["cpu"]) if usage_data["cpu"] else 0,
                "memory_avg": statistics.mean(usage_data["memory"]) if usage_data["memory"] else 0,
                "disk_avg": statistics.mean(usage_data["disk"]) if usage_data["disk"] else 0
            }
        
        # 找出高峰和低谷時段
        if hourly_averages:
            peak_cpu_hour = max(hourly_averages.items(), key=lambda x: x[1]["cpu_avg"])
            low_cpu_hour = min(hourly_averages.items(), key=lambda x: x[1]["cpu_avg"])
            
            return {
                "hourly_patterns": hourly_averages,
                "peak_usage_hour": {
                    "hour": peak_cpu_hour[0],
                    "cpu_usage": peak_cpu_hour[1]["cpu_avg"]
                },
                "lowest_usage_hour": {
                    "hour": low_cpu_hour[0],
                    "cpu_usage": low_cpu_hour[1]["cpu_avg"]
                }
            }
        
        return {"hourly_patterns": {}}
    
    def _identify_resource_bottlenecks(self, resource_stats: Dict) -> List[Dict[str, Any]]:
        """識別資源瓶頸"""
        bottlenecks = []
        
        # CPU瓶頸
        if resource_stats["cpu_utilization"]["average"] > 80:
            bottlenecks.append({
                "resource": "cpu",
                "severity": "high" if resource_stats["cpu_utilization"]["average"] > 90 else "medium",
                "average_usage": resource_stats["cpu_utilization"]["average"],
                "peak_usage": resource_stats["cpu_utilization"]["peak"],
                "description": "CPU使用率持續偏高，可能影響系統響應性能"
            })
        
        # 記憶體瓶頸
        if resource_stats["memory_utilization"]["average"] > 85:
            bottlenecks.append({
                "resource": "memory",
                "severity": "high" if resource_stats["memory_utilization"]["average"] > 95 else "medium",
                "average_usage": resource_stats["memory_utilization"]["average"],
                "peak_usage": resource_stats["memory_utilization"]["peak"],
                "description": "記憶體使用率接近上限，可能需要增加記憶體或優化內存使用"
            })
        
        # 磁盤瓶頸
        if resource_stats["disk_utilization"]["average"] > 90:
            bottlenecks.append({
                "resource": "disk",
                "severity": "high" if resource_stats["disk_utilization"]["average"] > 95 else "medium",
                "average_usage": resource_stats["disk_utilization"]["average"],
                "peak_usage": resource_stats["disk_utilization"]["peak"],
                "description": "磁盤空間使用率過高，需要清理或擴容"
            })
        
        return bottlenecks
    
    def _calculate_resource_efficiency(self, resource_stats: Dict) -> Dict[str, float]:
        """計算資源效率"""
        # 效率分數：基於平均使用率和變異性
        cpu_efficiency = min(1.0, (100 - resource_stats["cpu_utilization"]["std_deviation"]) / 100)
        memory_efficiency = min(1.0, (100 - resource_stats["memory_utilization"]["std_deviation"]) / 100)
        
        # 整體效率
        overall_efficiency = (cpu_efficiency + memory_efficiency) / 2
        
        return {
            "cpu_efficiency": cpu_efficiency,
            "memory_efficiency": memory_efficiency,
            "overall_efficiency": overall_efficiency,
            "efficiency_grade": self._get_efficiency_grade(overall_efficiency)
        }
    
    def _get_efficiency_grade(self, efficiency: float) -> str:
        """獲取效率等級"""
        if efficiency >= 0.9:
            return "A"
        elif efficiency >= 0.8:
            return "B"
        elif efficiency >= 0.7:
            return "C"
        elif efficiency >= 0.6:
            return "D"
        else:
            return "F"
    
    def _analyze_application_performance(self) -> Dict[str, Any]:
        """分析應用程序性能"""
        if not self.app_metrics:
            return {"status": "no_application_data"}
        
        # 提取應用程序指標
        app_cpu_values = [m.cpu_percent for m in self.app_metrics]
        app_memory_values = [m.memory_mb for m in self.app_metrics]
        thread_counts = [m.threads for m in self.app_metrics]
        connection_counts = [m.connections for m in self.app_metrics]
        
        app_performance = {
            "application_cpu_usage": {
                "current": app_cpu_values[-1],
                "average": statistics.mean(app_cpu_values),
                "peak": max(app_cpu_values),
                "trend": self._calculate_trend(app_cpu_values[-10:]) if len(app_cpu_values) >= 10 else "stable"
            },
            "application_memory_usage": {
                "current_mb": app_memory_values[-1],
                "average_mb": statistics.mean(app_memory_values),
                "peak_mb": max(app_memory_values),
                "trend": self._calculate_trend(app_memory_values[-10:]) if len(app_memory_values) >= 10 else "stable"
            },
            "thread_management": {
                "current_threads": thread_counts[-1],
                "average_threads": statistics.mean(thread_counts),
                "peak_threads": max(thread_counts)
            },
            "connection_management": {
                "current_connections": connection_counts[-1],
                "average_connections": statistics.mean(connection_counts),
                "peak_connections": max(connection_counts)
            }
        }
        
        # 應用程序健康評分
        health_score = self._calculate_application_health_score(app_performance)
        app_performance["health_score"] = health_score
        
        return app_performance
    
    def _calculate_trend(self, values: List[float]) -> str:
        """計算趨勢"""
        if len(values) < 3:
            return "stable"
        
        # 簡單線性趨勢分析
        first_half = statistics.mean(values[:len(values)//2])
        second_half = statistics.mean(values[len(values)//2:])
        
        change_ratio = (second_half - first_half) / max(first_half, 1)
        
        if change_ratio > 0.1:
            return "increasing"
        elif change_ratio < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_application_health_score(self, performance: Dict) -> Dict[str, Any]:
        """計算應用程序健康評分"""
        scores = []
        
        # CPU使用率評分（越低越好）
        cpu_avg = performance["application_cpu_usage"]["average"]
        cpu_score = max(0, 1 - (cpu_avg / 100))
        scores.append(cpu_score)
        
        # 記憶體增長評分
        memory_trend = performance["application_memory_usage"]["trend"]
        memory_score = 1.0 if memory_trend != "increasing" else 0.7
        scores.append(memory_score)
        
        # 線程數穩定性評分
        thread_trend = performance["thread_management"]
        if thread_trend["peak_threads"] / max(thread_trend["average_threads"], 1) < 1.5:
            thread_score = 1.0
        else:
            thread_score = 0.8
        scores.append(thread_score)
        
        overall_score = statistics.mean(scores)
        
        return {
            "overall_score": overall_score,
            "grade": self._get_health_grade(overall_score),
            "component_scores": {
                "cpu_efficiency": cpu_score,
                "memory_stability": memory_score,
                "thread_stability": thread_score
            }
        }
    
    def _get_health_grade(self, score: float) -> str:
        """獲取健康等級"""
        if score >= 0.9:
            return "Excellent"
        elif score >= 0.8:
            return "Good"
        elif score >= 0.7:
            return "Fair"
        elif score >= 0.6:
            return "Poor"
        else:
            return "Critical"
    
    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """分析性能趨勢"""
        if len(self.system_snapshots) < 10:
            return {"trend_analysis": "insufficient_data"}
        
        # 分析最近的趨勢
        recent_snapshots = list(self.system_snapshots)[-60:]  # 最近60個樣本
        
        # CPU趨勢
        cpu_values = [s.cpu_usage for s in recent_snapshots]
        cpu_trend = self._calculate_detailed_trend(cpu_values)
        
        # 記憶體趨勢
        memory_values = [s.memory_usage for s in recent_snapshots]
        memory_trend = self._calculate_detailed_trend(memory_values)
        
        # 性能變化檢測
        performance_changes = self._detect_performance_changes()
        
        return {
            "cpu_trend": cpu_trend,
            "memory_trend": memory_trend,
            "trend_summary": self._summarize_trends(cpu_trend, memory_trend),
            "performance_changes": performance_changes,
            "prediction": self._predict_resource_usage()
        }
    
    def _calculate_detailed_trend(self, values: List[float]) -> Dict[str, Any]:
        """計算詳細趨勢"""
        if len(values) < 5:
            return {"direction": "unknown", "strength": 0}
        
        # 計算移動平均
        window_size = min(5, len(values) // 2)
        early_avg = statistics.mean(values[:window_size])
        late_avg = statistics.mean(values[-window_size:])
        
        # 趨勢方向和強度
        change = late_avg - early_avg
        change_ratio = abs(change) / max(early_avg, 1)
        
        direction = "increasing" if change > 0 else "decreasing" if change < 0 else "stable"
        strength = min(1.0, change_ratio * 2)  # 標準化強度
        
        return {
            "direction": direction,
            "strength": strength,
            "change_value": change,
            "change_ratio": change_ratio,
            "early_average": early_avg,
            "late_average": late_avg
        }
    
    def _summarize_trends(self, cpu_trend: Dict, memory_trend: Dict) -> str:
        """總結趨勢"""
        cpu_dir = cpu_trend.get("direction", "unknown")
        memory_dir = memory_trend.get("direction", "unknown")
        
        if cpu_dir == "increasing" and memory_dir == "increasing":
            return "系統負載持續增加，需要關注資源使用"
        elif cpu_dir == "decreasing" and memory_dir == "decreasing":
            return "系統負載趨於穩定，性能表現良好"
        elif cpu_dir == "increasing":
            return "CPU使用率上升，建議優化計算密集型任務"
        elif memory_dir == "increasing":
            return "記憶體使用量增加，建議檢查內存洩漏"
        else:
            return "系統性能穩定，資源使用正常"
    
    def _detect_performance_changes(self) -> List[Dict[str, Any]]:
        """檢測性能變化"""
        changes = []
        
        if len(self.system_snapshots) < 20:
            return changes
        
        # 檢測顯著的性能變化
        recent_snapshots = list(self.system_snapshots)[-20:]
        older_snapshots = list(self.system_snapshots)[-40:-20] if len(self.system_snapshots) >= 40 else []
        
        if not older_snapshots:
            return changes
        
        # CPU變化
        recent_cpu_avg = statistics.mean(s.cpu_usage for s in recent_snapshots)
        older_cpu_avg = statistics.mean(s.cpu_usage for s in older_snapshots)
        
        if abs(recent_cpu_avg - older_cpu_avg) > 20:  # 20%的變化
            changes.append({
                "metric": "cpu_usage",
                "change_type": "increase" if recent_cpu_avg > older_cpu_avg else "decrease",
                "magnitude": abs(recent_cpu_avg - older_cpu_avg),
                "timestamp": recent_snapshots[-1].timestamp.isoformat()
            })
        
        # 記憶體變化
        recent_memory_avg = statistics.mean(s.memory_usage for s in recent_snapshots)
        older_memory_avg = statistics.mean(s.memory_usage for s in older_snapshots)
        
        if abs(recent_memory_avg - older_memory_avg) > 15:  # 15%的變化
            changes.append({
                "metric": "memory_usage",
                "change_type": "increase" if recent_memory_avg > older_memory_avg else "decrease",
                "magnitude": abs(recent_memory_avg - older_memory_avg),
                "timestamp": recent_snapshots[-1].timestamp.isoformat()
            })
        
        return changes
    
    def _predict_resource_usage(self) -> Dict[str, Any]:
        """預測資源使用"""
        if len(self.system_snapshots) < 30:
            return {"prediction": "insufficient_data"}
        
        # 簡單的線性預測
        recent_cpu = [s.cpu_usage for s in list(self.system_snapshots)[-30:]]
        recent_memory = [s.memory_usage for s in list(self.system_snapshots)[-30:]]
        
        # 計算趨勢斜率
        cpu_slope = (recent_cpu[-1] - recent_cpu[0]) / len(recent_cpu)
        memory_slope = (recent_memory[-1] - recent_memory[0]) / len(recent_memory)
        
        # 預測未來30分鐘
        predicted_cpu = recent_cpu[-1] + (cpu_slope * 30)
        predicted_memory = recent_memory[-1] + (memory_slope * 30)
        
        return {
            "prediction_horizon": "30_minutes",
            "predicted_cpu_usage": max(0, min(100, predicted_cpu)),
            "predicted_memory_usage": max(0, min(100, predicted_memory)),
            "confidence": "low" if abs(cpu_slope) < 0.1 and abs(memory_slope) < 0.1 else "medium",
            "recommendations": self._get_prediction_recommendations(predicted_cpu, predicted_memory)
        }
    
    def _get_prediction_recommendations(self, cpu_pred: float, memory_pred: float) -> List[str]:
        """獲取預測建議"""
        recommendations = []
        
        if cpu_pred > 90:
            recommendations.append("預測CPU使用率將超過90%，建議優化或擴展計算資源")
        
        if memory_pred > 95:
            recommendations.append("預測記憶體使用率將接近上限，建議釋放內存或增加RAM")
        
        if cpu_pred > 80 and memory_pred > 80:
            recommendations.append("預測系統負載將偏高，建議減少併發任務或升級硬件")
        
        return recommendations if recommendations else ["系統資源使用預測正常"]
    
    def _analyze_response_times(self) -> Dict[str, Any]:
        """分析響應時間"""
        # 這裡應該從實際的API調用中收集響應時間數據
        # 目前使用模擬數據
        simulated_response_times = [150, 200, 180, 220, 190, 175, 250, 160, 210, 195]
        
        if not simulated_response_times:
            return {"response_time_analysis": "no_data"}
        
        response_analysis = {
            "average_response_time": statistics.mean(simulated_response_times),
            "median_response_time": statistics.median(simulated_response_times),
            "p95_response_time": sorted(simulated_response_times)[int(0.95 * len(simulated_response_times))],
            "p99_response_time": sorted(simulated_response_times)[int(0.99 * len(simulated_response_times))],
            "max_response_time": max(simulated_response_times),
            "response_time_distribution": self._create_response_time_distribution(simulated_response_times)
        }
        
        # SLA合規性檢查
        sla_compliance = self._check_sla_compliance(simulated_response_times)
        response_analysis["sla_compliance"] = sla_compliance
        
        return response_analysis
    
    def _create_response_time_distribution(self, times: List[float]) -> Dict[str, int]:
        """創建響應時間分佈"""
        distribution = {
            "0-100ms": 0,
            "100-500ms": 0,
            "500ms-1s": 0,
            "1s-2s": 0,
            "2s+": 0
        }
        
        for time_ms in times:
            if time_ms < 100:
                distribution["0-100ms"] += 1
            elif time_ms < 500:
                distribution["100-500ms"] += 1
            elif time_ms < 1000:
                distribution["500ms-1s"] += 1
            elif time_ms < 2000:
                distribution["1s-2s"] += 1
            else:
                distribution["2s+"] += 1
        
        return distribution
    
    def _check_sla_compliance(self, response_times: List[float]) -> Dict[str, Any]:
        """檢查SLA合規性"""
        # 定義SLA標準
        sla_targets = {
            "p95_target": 500,  # 95%的請求應在500ms內
            "p99_target": 1000,  # 99%的請求應在1s內
            "average_target": 300  # 平均響應時間應在300ms內
        }
        
        sorted_times = sorted(response_times)
        p95_actual = sorted_times[int(0.95 * len(sorted_times))]
        p99_actual = sorted_times[int(0.99 * len(sorted_times))]
        average_actual = statistics.mean(response_times)
        
        return {
            "p95_compliance": p95_actual <= sla_targets["p95_target"],
            "p99_compliance": p99_actual <= sla_targets["p99_target"],
            "average_compliance": average_actual <= sla_targets["average_target"],
            "overall_compliance": all([
                p95_actual <= sla_targets["p95_target"],
                p99_actual <= sla_targets["p99_target"],
                average_actual <= sla_targets["average_target"]
            ]),
            "compliance_score": sum([
                1 if p95_actual <= sla_targets["p95_target"] else 0,
                1 if p99_actual <= sla_targets["p99_target"] else 0,
                1 if average_actual <= sla_targets["average_target"] else 0
            ]) / 3
        }
    
    def _analyze_capacity_planning(self) -> Dict[str, Any]:
        """分析容量規劃"""
        if not self.system_snapshots:
            return {"capacity_analysis": "no_data"}
        
        # 當前資源使用率
        latest_snapshot = self.system_snapshots[-1]
        
        # 增長率分析
        growth_analysis = self._calculate_growth_rates()
        
        # 容量預測
        capacity_predictions = self._predict_capacity_needs()
        
        # 擴容建議
        scaling_recommendations = self._generate_scaling_recommendations()
        
        return {
            "current_capacity_usage": {
                "cpu_usage": latest_snapshot.cpu_usage,
                "memory_usage": latest_snapshot.memory_usage,
                "disk_usage": latest_snapshot.disk_usage
            },
            "growth_analysis": growth_analysis,
            "capacity_predictions": capacity_predictions,
            "scaling_recommendations": scaling_recommendations,
            "capacity_alerts": self._generate_capacity_alerts()
        }
    
    def _calculate_growth_rates(self) -> Dict[str, float]:
        """計算增長率"""
        if len(self.system_snapshots) < 100:  # 需要足夠的數據點
            return {"status": "insufficient_data_for_growth_analysis"}
        
        # 比較最近一周與前一周的平均使用率
        recent_week = list(self.system_snapshots)[-168:]  # 最近一周（假設每小時一個樣本）
        previous_week = list(self.system_snapshots)[-336:-168] if len(self.system_snapshots) >= 336 else []
        
        if not previous_week:
            return {"status": "insufficient_historical_data"}
        
        recent_cpu_avg = statistics.mean(s.cpu_usage for s in recent_week)
        previous_cpu_avg = statistics.mean(s.cpu_usage for s in previous_week)
        
        recent_memory_avg = statistics.mean(s.memory_usage for s in recent_week)
        previous_memory_avg = statistics.mean(s.memory_usage for s in previous_week)
        
        cpu_growth_rate = ((recent_cpu_avg - previous_cpu_avg) / max(previous_cpu_avg, 1)) * 100
        memory_growth_rate = ((recent_memory_avg - previous_memory_avg) / max(previous_memory_avg, 1)) * 100
        
        return {
            "cpu_growth_rate_percent": cpu_growth_rate,
            "memory_growth_rate_percent": memory_growth_rate,
            "growth_trend": "increasing" if cpu_growth_rate > 5 or memory_growth_rate > 5 else "stable"
        }
    
    def _predict_capacity_needs(self) -> Dict[str, Any]:
        """預測容量需求"""
        growth_rates = self._calculate_growth_rates()
        
        if "status" in growth_rates:
            return {"prediction": "insufficient_data"}
        
        # 當前使用率
        latest_snapshot = self.system_snapshots[-1]
        current_cpu = latest_snapshot.cpu_usage
        current_memory = latest_snapshot.memory_usage
        
        # 基於增長率預測未來3個月的需求
        months_ahead = 3
        cpu_growth_monthly = growth_rates["cpu_growth_rate_percent"] / 4  # 假設月增長率為週增長率的1/4
        memory_growth_monthly = growth_rates["memory_growth_rate_percent"] / 4
        
        predicted_cpu = current_cpu * (1 + (cpu_growth_monthly / 100)) ** months_ahead
        predicted_memory = current_memory * (1 + (memory_growth_monthly / 100)) ** months_ahead
        
        return {
            "prediction_period": f"{months_ahead}_months",
            "predicted_cpu_usage": min(100, max(0, predicted_cpu)),
            "predicted_memory_usage": min(100, max(0, predicted_memory)),
            "capacity_shortage_risk": {
                "cpu_risk": "high" if predicted_cpu > 90 else "medium" if predicted_cpu > 80 else "low",
                "memory_risk": "high" if predicted_memory > 90 else "medium" if predicted_memory > 80 else "low"
            }
        }
    
    def _generate_scaling_recommendations(self) -> List[Dict[str, Any]]:
        """生成擴容建議"""
        recommendations = []
        capacity_predictions = self._predict_capacity_needs()
        
        if "prediction" in capacity_predictions:
            return [{"message": "數據不足，無法生成擴容建議"}]
        
        # CPU擴容建議
        if capacity_predictions["predicted_cpu_usage"] > 80:
            recommendations.append({
                "resource": "cpu",
                "action": "scale_up",
                "urgency": "high" if capacity_predictions["predicted_cpu_usage"] > 90 else "medium",
                "suggestion": "建議增加CPU核心數或優化CPU密集型任務",
                "timeline": "1_month" if capacity_predictions["predicted_cpu_usage"] > 90 else "3_months"
            })
        
        # 記憶體擴容建議
        if capacity_predictions["predicted_memory_usage"] > 80:
            recommendations.append({
                "resource": "memory",
                "action": "scale_up",
                "urgency": "high" if capacity_predictions["predicted_memory_usage"] > 90 else "medium",
                "suggestion": "建議增加RAM容量或優化內存使用",
                "timeline": "1_month" if capacity_predictions["predicted_memory_usage"] > 90 else "3_months"
            })
        
        return recommendations if recommendations else [{"message": "當前容量充足，暫不需要擴容"}]
    
    def _generate_capacity_alerts(self) -> List[Dict[str, Any]]:
        """生成容量警報"""
        alerts = []
        
        if not self.system_snapshots:
            return alerts
        
        latest_snapshot = self.system_snapshots[-1]
        
        # 磁盤空間警報
        if latest_snapshot.disk_usage > 90:
            alerts.append({
                "type": "critical",
                "resource": "disk",
                "message": f"磁盤使用率達到 {latest_snapshot.disk_usage:.1f}%，需要立即清理或擴容",
                "usage": latest_snapshot.disk_usage
            })
        elif latest_snapshot.disk_usage > 85:
            alerts.append({
                "type": "warning",
                "resource": "disk",
                "message": f"磁盤使用率較高 {latest_snapshot.disk_usage:.1f}%，建議準備擴容",
                "usage": latest_snapshot.disk_usage
            })
        
        return alerts
    
    def _compare_with_baseline(self) -> Dict[str, Any]:
        """與基線比較"""
        if not self.baseline_metrics or not self.system_snapshots:
            return {"baseline_comparison": "no_baseline_or_data"}
        
        latest_snapshot = self.system_snapshots[-1]
        
        # 與基線比較
        cpu_change = latest_snapshot.cpu_usage - self.baseline_metrics["baseline_cpu"]
        memory_change = latest_snapshot.memory_usage - self.baseline_metrics["baseline_memory"]
        disk_change = latest_snapshot.disk_usage - self.baseline_metrics["baseline_disk"]
        
        return {
            "baseline_established": self.baseline_metrics["baseline_established_at"],
            "current_vs_baseline": {
                "cpu_change": cpu_change,
                "memory_change": memory_change,
                "disk_change": disk_change
            },
            "performance_degradation": {
                "cpu_degraded": cpu_change > 20,
                "memory_degraded": memory_change > 15,
                "overall_degraded": cpu_change > 20 or memory_change > 15
            },
            "baseline_drift": self._calculate_baseline_drift()
        }
    
    def _calculate_baseline_drift(self) -> Dict[str, Any]:
        """計算基線漂移"""
        if len(self.system_snapshots) < 50:
            return {"drift_analysis": "insufficient_data"}
        
        # 比較最近的平均值與基線
        recent_snapshots = list(self.system_snapshots)[-50:]
        recent_cpu_avg = statistics.mean(s.cpu_usage for s in recent_snapshots)
        recent_memory_avg = statistics.mean(s.memory_usage for s in recent_snapshots)
        
        cpu_drift = abs(recent_cpu_avg - self.baseline_metrics["baseline_cpu"])
        memory_drift = abs(recent_memory_avg - self.baseline_metrics["baseline_memory"])
        
        return {
            "cpu_drift": cpu_drift,
            "memory_drift": memory_drift,
            "significant_drift": cpu_drift > 30 or memory_drift > 25,
            "baseline_update_recommended": cpu_drift > 30 or memory_drift > 25
        }
    
    def _get_alert_summary(self) -> Dict[str, Any]:
        """獲取警報摘要"""
        current_time = datetime.now()
        
        # 按嚴重程度分類警報
        critical_alerts = [a for a in self.performance_alerts if a["type"] == "critical"]
        warning_alerts = [a for a in self.performance_alerts if a["type"] == "warning"]
        
        # 最近1小時的警報
        recent_alerts = [
            a for a in self.performance_alerts
            if current_time - datetime.fromisoformat(a["timestamp"]) < timedelta(hours=1)
        ]
        
        return {
            "total_active_alerts": len(self.performance_alerts),
            "critical_alerts": len(critical_alerts),
            "warning_alerts": len(warning_alerts),
            "recent_alerts_1h": len(recent_alerts),
            "alert_details": self.performance_alerts[-5:],  # 最近5個警報
            "system_health_status": self._get_overall_health_status()
        }
    
    def _get_overall_health_status(self) -> str:
        """獲取整體健康狀態"""
        if not self.system_snapshots:
            return "unknown"
        
        critical_alerts = [a for a in self.performance_alerts if a["type"] == "critical"]
        warning_alerts = [a for a in self.performance_alerts if a["type"] == "warning"]
        
        if len(critical_alerts) > 0:
            return "critical"
        elif len(warning_alerts) > 3:
            return "degraded"
        elif len(warning_alerts) > 0:
            return "warning"
        else:
            return "healthy"
    
    def _generate_performance_recommendations(self) -> List[str]:
        """生成性能建議"""
        recommendations = []
        
        if not self.system_snapshots:
            return ["數據不足，無法生成建議"]
        
        latest_snapshot = self.system_snapshots[-1]
        
        # CPU建議
        if latest_snapshot.cpu_usage > 80:
            recommendations.append("CPU使用率較高，建議優化計算密集型任務或考慮垂直擴展")
        
        # 記憶體建議
        if latest_snapshot.memory_usage > 85:
            recommendations.append("記憶體使用率接近上限，建議檢查內存洩漏或增加RAM")
        
        # 磁盤建議
        if latest_snapshot.disk_usage > 90:
            recommendations.append("磁盤空間不足，建議清理不必要的文件或擴展存儲空間")
        
        # 基於警報的建議
        if len(self.performance_alerts) > 5:
            recommendations.append("系統警報較多，建議進行全面的性能調優")
        
        # 應用程序建議
        if self.app_metrics:
            latest_app = self.app_metrics[-1]
            if latest_app.threads > 100:
                recommendations.append("應用程序線程數較多，建議檢查線程池配置")
            
            if latest_app.connections > 1000:
                recommendations.append("網絡連接數較高，建議優化連接管理")
        
        return recommendations if recommendations else ["系統性能表現良好，暫無特殊建議"]
    
    async def get_real_time_performance_metrics(self) -> Dict[str, Any]:
        """獲取實時性能指標"""
        try:
            current_snapshot = self._collect_system_snapshot()
            current_app_metrics = self._collect_application_metrics()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "system_metrics": asdict(current_snapshot),
                "application_metrics": asdict(current_app_metrics) if current_app_metrics else None,
                "alert_count": len(self.performance_alerts),
                "health_status": self._get_overall_health_status(),
                "monitoring_status": "active" if self.monitoring_enabled else "inactive"
            }
        except Exception as e:
            logger.error(f"獲取實時性能指標失敗: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "monitoring_status": "error"
            }
    
    def stop_monitoring(self):
        """停止監控"""
        self.monitoring_enabled = False
        logger.info("性能監控已停止")
    
    def __del__(self):
        """析構函數"""
        self.monitoring_enabled = False
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

# 全局實例
performance_monitor = SystemPerformanceMonitor()
