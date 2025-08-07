"""
🖥️ Phase4 Unified Monitoring Dashboard
=====================================

統一監控儀表板實現 - 基於配置驅動的實時系統狀態監控
與 unified_monitoring_dashboard_config.json 配置文件對應
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

# 導入Phase3決策結果
import sys
current_dir = Path(__file__).parent
sys.path.extend([
    str(current_dir.parent.parent / "phase3_execution_policy"),
    str(current_dir.parent.parent / "phase2_pre_evaluation"),
    str(current_dir.parent.parent / "phase1_signal_generation")
])

from epl_intelligent_decision_engine import EPLDecisionResult, SignalPriority, EPLDecision

logger = logging.getLogger(__name__)

@dataclass
class DashboardWidgetData:
    """儀表板組件數據"""
    widget_id: str
    widget_type: str
    data: Dict[str, Any]
    last_update: datetime
    status: str

@dataclass
class SystemHealthIndicator:
    """系統健康指標"""
    component: str
    status: str  # green, yellow, red
    metrics: Dict[str, float]
    alerts: List[str]
    last_check: datetime

class UnifiedMonitoringDashboard:
    """統一監控儀表板"""
    
    def __init__(self):
        # 載入配置文件
        self.config = self._load_config()
        
        # 儀表板狀態
        self.dashboard_enabled = True
        self.last_update = datetime.now()
        
        # 組件數據儲存
        self.widget_data: Dict[str, DashboardWidgetData] = {}
        self.system_health: Dict[str, SystemHealthIndicator] = {}
        
        # 性能監控
        self.update_latency_history = []
        self.error_count = 0
        
        # 初始化儀表板組件
        self._initialize_widgets()
        
    def _load_config(self) -> Dict[str, Any]:
        """載入配置文件"""
        try:
            config_path = Path(__file__).parent / "unified_monitoring_dashboard_config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入儀表板配置失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            "PHASE4_UNIFIED_MONITORING_DASHBOARD": {
                "dashboard_widgets": {
                    "system_status_overview": {"refresh_rate": "real_time_1s"},
                    "signal_processing_analytics": {"refresh_rate": "5_second_updates"},
                    "epl_decision_tracking": {"refresh_rate": "real_time_updates"},
                    "notification_success_monitoring": {"refresh_rate": "30_second_updates"},
                    "system_performance_monitoring": {"refresh_rate": "10_second_updates"}
                }
            }
        }
    
    def _initialize_widgets(self):
        """初始化儀表板組件"""
        dashboard_config = self.config.get("PHASE4_UNIFIED_MONITORING_DASHBOARD", {})
        widgets_config = dashboard_config.get("dashboard_widgets", {})
        
        for widget_id, widget_config in widgets_config.items():
            self.widget_data[widget_id] = DashboardWidgetData(
                widget_id=widget_id,
                widget_type=widget_config.get("widget_type", "unknown"),
                data={},
                last_update=datetime.now(),
                status="initializing"
            )
            
        logger.info(f"初始化 {len(self.widget_data)} 個儀表板組件")
    
    async def update_dashboard_data(self) -> Dict[str, Any]:
        """更新儀表板數據"""
        update_start = datetime.now()
        
        try:
            # 並行更新所有組件
            update_tasks = [
                self._update_system_status_overview(),
                self._update_signal_processing_analytics(),
                self._update_epl_decision_tracking(),
                self._update_notification_success_monitoring(),
                self._update_system_performance_monitoring()
            ]
            
            results = await asyncio.gather(*update_tasks, return_exceptions=True)
            
            # 處理更新結果
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            error_count = len(results) - success_count
            
            # 記錄性能指標
            update_latency = (datetime.now() - update_start).total_seconds() * 1000
            self.update_latency_history.append(update_latency)
            if len(self.update_latency_history) > 100:
                self.update_latency_history.pop(0)
            
            self.last_update = datetime.now()
            self.error_count += error_count
            
            return {
                "dashboard_status": "healthy" if error_count == 0 else "degraded",
                "widgets_updated": success_count,
                "update_errors": error_count,
                "update_latency_ms": update_latency,
                "last_update": self.last_update.isoformat(),
                "widget_data": {wid: asdict(data) for wid, data in self.widget_data.items()}
            }
            
        except Exception as e:
            logger.error(f"儀表板更新失敗: {e}")
            self.error_count += 1
            return {
                "dashboard_status": "error",
                "error": str(e),
                "last_update": self.last_update.isoformat()
            }
    
    async def _update_system_status_overview(self):
        """更新系統狀態概覽"""
        try:
            # 檢查各Phase的狀態
            phase_status = {
                "phase1_signal_generation": await self._check_phase1_status(),
                "phase2_pre_evaluation": await self._check_phase2_status(),
                "phase3_execution_policy": await self._check_phase3_status(),
                "notification_system": await self._check_notification_status()
            }
            
            # 計算總體健康度
            all_green = all(status["status_indicator"] == "green" for status in phase_status.values())
            has_yellow = any(status["status_indicator"] == "yellow" for status in phase_status.values())
            has_red = any(status["status_indicator"] == "red" for status in phase_status.values())
            
            overall_status = "green" if all_green else ("red" if has_red else "yellow")
            
            self.widget_data["system_status_overview"].data = {
                "overall_status": overall_status,
                "phase_status": phase_status,
                "summary": {
                    "total_phases": len(phase_status),
                    "healthy_phases": sum(1 for s in phase_status.values() if s["status_indicator"] == "green"),
                    "warning_phases": sum(1 for s in phase_status.values() if s["status_indicator"] == "yellow"),
                    "error_phases": sum(1 for s in phase_status.values() if s["status_indicator"] == "red")
                }
            }
            self.widget_data["system_status_overview"].status = "updated"
            self.widget_data["system_status_overview"].last_update = datetime.now()
            
        except Exception as e:
            logger.error(f"系統狀態概覽更新失敗: {e}")
            self.widget_data["system_status_overview"].status = "error"
    
    async def _check_phase1_status(self) -> Dict[str, Any]:
        """檢查Phase1狀態"""
        # 模擬Phase1狀態檢查
        return {
            "status_indicator": "green",
            "metrics": {
                "signals_per_minute": 45.2,
                "quality_distribution": 0.78,
                "source_availability": 0.95
            },
            "alerts": []
        }
    
    async def _check_phase2_status(self) -> Dict[str, Any]:
        """檢查Phase2狀態"""
        # 模擬Phase2狀態檢查
        return {
            "status_indicator": "green",
            "metrics": {
                "processing_latency": 12.5,
                "channel_distribution": 0.65,
                "quality_scores": 0.82
            },
            "alerts": []
        }
    
    async def _check_phase3_status(self) -> Dict[str, Any]:
        """檢查Phase3狀態"""
        # 模擬Phase3狀態檢查
        return {
            "status_indicator": "green",
            "metrics": {
                "decision_latency": 380.0,
                "decision_distribution": 0.45,
                "risk_violations": 0
            },
            "alerts": []
        }
    
    async def _check_notification_status(self) -> Dict[str, Any]:
        """檢查通知系統狀態"""
        # 模擬通知系統狀態檢查
        return {
            "status_indicator": "green",
            "metrics": {
                "delivery_success_rate": 0.98,
                "channel_health": 1.0,
                "queue_depth": 3
            },
            "alerts": []
        }
    
    async def _update_signal_processing_analytics(self):
        """更新信號處理分析"""
        try:
            # 模擬信號處理數據
            current_time = datetime.now()
            
            self.widget_data["signal_processing_analytics"].data = {
                "signal_volume_chart": {
                    "total_signals": 1247,
                    "signals_by_priority": {
                        "CRITICAL": 23,
                        "HIGH": 156,
                        "MEDIUM": 789,
                        "LOW": 279
                    },
                    "hourly_trend": [45, 52, 38, 61, 47, 55]  # 最近6小時
                },
                "processing_latency_chart": {
                    "phase1_latency": [185, 192, 178, 201, 188],
                    "phase2_latency": [12, 15, 11, 18, 13],
                    "phase3_latency": [420, 395, 445, 380, 405],
                    "total_latency": [617, 602, 634, 599, 606]
                },
                "quality_distribution": {
                    "quality_bins": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                    "signal_counts": [2, 8, 15, 45, 120, 210, 380, 350, 95, 22]
                }
            }
            self.widget_data["signal_processing_analytics"].status = "updated"
            self.widget_data["signal_processing_analytics"].last_update = current_time
            
        except Exception as e:
            logger.error(f"信號處理分析更新失敗: {e}")
            self.widget_data["signal_processing_analytics"].status = "error"
    
    async def _update_epl_decision_tracking(self):
        """更新EPL決策追蹤"""
        try:
            # 模擬EPL決策數據
            self.widget_data["epl_decision_tracking"].data = {
                "decision_type_distribution": {
                    "REPLACE_POSITION": 0.15,
                    "STRENGTHEN_POSITION": 0.25,
                    "CREATE_NEW_POSITION": 0.35,
                    "IGNORE_SIGNAL": 0.25
                },
                "recent_decisions": [
                    {
                        "timestamp": (datetime.now() - timedelta(minutes=2)).isoformat(),
                        "symbol": "BTCUSDT",
                        "decision": "CREATE_NEW_POSITION",
                        "priority": "HIGH",
                        "confidence": 0.87
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                        "symbol": "ETHUSDT", 
                        "decision": "STRENGTHEN_POSITION",
                        "priority": "MEDIUM",
                        "confidence": 0.74
                    }
                ],
                "success_rates": {
                    "overall_accuracy": 0.78,
                    "replacement_success": 0.82,
                    "strengthening_effectiveness": 0.75,
                    "new_position_performance": 0.79
                }
            }
            self.widget_data["epl_decision_tracking"].status = "updated"
            self.widget_data["epl_decision_tracking"].last_update = datetime.now()
            
        except Exception as e:
            logger.error(f"EPL決策追蹤更新失敗: {e}")
            self.widget_data["epl_decision_tracking"].status = "error"
    
    async def _update_notification_success_monitoring(self):
        """更新通知成功監控"""
        try:
            self.widget_data["notification_success_monitoring"].data = {
                "delivery_matrix": {
                    "gmail": {"CRITICAL": 0.99, "HIGH": 0.97, "MEDIUM": 0.95, "LOW": 0.93},
                    "websocket": {"CRITICAL": 1.0, "HIGH": 0.99, "MEDIUM": 0.98, "LOW": 0.97},
                    "frontend": {"CRITICAL": 1.0, "HIGH": 0.99, "MEDIUM": 0.99, "LOW": 0.98},
                    "sms": {"CRITICAL": 0.96, "HIGH": 0.0, "MEDIUM": 0.0, "LOW": 0.0}
                },
                "volume_trends": {
                    "last_6_hours": [45, 52, 38, 61, 47, 55],
                    "by_channel": {
                        "gmail": 234,
                        "websocket": 567,
                        "frontend": 567,
                        "sms": 23
                    }
                },
                "engagement_metrics": {
                    "open_rate": 0.85,
                    "click_through_rate": 0.62,
                    "action_rate": 0.45
                }
            }
            self.widget_data["notification_success_monitoring"].status = "updated"
            self.widget_data["notification_success_monitoring"].last_update = datetime.now()
            
        except Exception as e:
            logger.error(f"通知成功監控更新失敗: {e}")
            self.widget_data["notification_success_monitoring"].status = "error"
    
    async def _update_system_performance_monitoring(self):
        """更新系統性能監控"""
        try:
            self.widget_data["system_performance_monitoring"].data = {
                "resource_utilization": {
                    "cpu_usage": 0.65,
                    "memory_usage": 0.72,
                    "disk_io": 0.45,
                    "network_io": 0.38
                },
                "throughput_metrics": {
                    "signals_per_second": 12.5,
                    "decisions_per_second": 8.2,
                    "notifications_per_second": 15.7
                },
                "error_rates": {
                    "processing_errors": 0.002,
                    "notification_errors": 0.001,
                    "system_errors": 0.001
                },
                "latency_percentiles": {
                    "p50": 580,
                    "p95": 750,
                    "p99": 920
                }
            }
            self.widget_data["system_performance_monitoring"].status = "updated"
            self.widget_data["system_performance_monitoring"].last_update = datetime.now()
            
        except Exception as e:
            logger.error(f"系統性能監控更新失敗: {e}")
            self.widget_data["system_performance_monitoring"].status = "error"
    
    async def get_dashboard_export_data(self) -> Dict[str, Any]:
        """獲取儀表板匯出數據"""
        return {
            "dashboard_metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "dashboard_version": "2.1.0",
                "widgets_count": len(self.widget_data),
                "last_update": self.last_update.isoformat()
            },
            "widgets": {wid: asdict(data) for wid, data in self.widget_data.items()},
            "performance_metrics": {
                "average_update_latency": sum(self.update_latency_history) / len(self.update_latency_history) if self.update_latency_history else 0,
                "total_errors": self.error_count,
                "uptime": "99.8%"  # 模擬值
            }
        }
    
    def get_widget_data(self, widget_id: str) -> Optional[DashboardWidgetData]:
        """獲取特定組件數據"""
        return self.widget_data.get(widget_id)
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """獲取系統健康摘要"""
        widget_statuses = [data.status for data in self.widget_data.values()]
        
        return {
            "overall_health": "healthy" if all(s in ["updated", "initializing"] for s in widget_statuses) else "degraded",
            "widgets_healthy": sum(1 for s in widget_statuses if s == "updated"),
            "widgets_error": sum(1 for s in widget_statuses if s == "error"),
            "last_successful_update": max(data.last_update for data in self.widget_data.values() if data.status == "updated"),
            "average_update_latency": sum(self.update_latency_history) / len(self.update_latency_history) if self.update_latency_history else 0
        }

# 全局實例
unified_dashboard = UnifiedMonitoringDashboard()
