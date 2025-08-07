"""
🚀 Phase4 Output Monitoring API Routes
=====================================

Phase4輸出監控API路由 - 提供統一的RESTful API接口
整合所有監控組件，支援實時數據查詢和歷史分析
"""

from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path as PathLib
import logging
import sys

# 添加監控核心路徑
current_dir = PathLib(__file__).parent
sys.path.append(str(current_dir / "core"))

try:
    from monitoring_coordinator import monitoring_coordinator
    COORDINATOR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"監控協調器不可用: {e}")
    COORDINATOR_AVAILABLE = False

logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/api/v1/monitoring", tags=["Phase4 Output Monitoring"])

@router.get("/", response_model=Dict[str, Any])
async def get_monitoring_overview():
    """
    獲取Phase4監控系統總覽
    
    返回整個監控系統的健康狀態、可用組件和基本統計信息
    """
    try:
        if not COORDINATOR_AVAILABLE:
            return {
                "status": "coordinator_unavailable",
                "message": "監控協調器不可用",
                "timestamp": datetime.now().isoformat()
            }
        
        # 獲取協調器狀態
        coordinator_status = monitoring_coordinator.get_coordinator_status()
        
        # 獲取綜合概覽
        comprehensive_overview = await monitoring_coordinator.get_comprehensive_monitoring_overview()
        
        return {
            "monitoring_system_status": "active",
            "coordinator_status": coordinator_status,
            "comprehensive_overview": comprehensive_overview,
            "api_version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取監控概覽失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取監控概覽失敗: {str(e)}")

@router.get("/health", response_model=Dict[str, Any])
async def get_system_health():
    """
    獲取系統健康狀態
    
    返回系統整體健康評分、關鍵指標和警報信息
    """
    try:
        if not COORDINATOR_AVAILABLE:
            return {
                "health_status": "unknown",
                "message": "監控協調器不可用",
                "timestamp": datetime.now().isoformat()
            }
        
        overview = await monitoring_coordinator.get_comprehensive_monitoring_overview()
        system_health = overview.get("overall_system_health", {})
        
        return {
            "health_check_result": "completed",
            "overall_health": system_health,
            "component_health": overview.get("component_health_summary", {}),
            "critical_alerts": system_health.get("critical_issues", []),
            "warnings": system_health.get("warnings", []),
            "recommendations": system_health.get("recommendations", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取系統健康狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取系統健康狀態失敗: {str(e)}")

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_unified_dashboard():
    """
    獲取統一監控儀表板數據
    
    返回所有監控組件的儀表板數據，適用於前端展示
    """
    try:
        if not COORDINATOR_AVAILABLE:
            return {
                "status": "coordinator_unavailable",
                "timestamp": datetime.now().isoformat()
            }
        
        dashboard_data = await monitoring_coordinator.get_component_specific_data(
            "unified_dashboard", "full"
        )
        
        return {
            "dashboard_type": "unified_monitoring",
            "data": dashboard_data,
            "last_refresh": datetime.now().isoformat(),
            "refresh_interval": "real_time"
        }
        
    except Exception as e:
        logger.error(f"獲取統一儀表板失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取統一儀表板失敗: {str(e)}")

@router.get("/signals", response_model=Dict[str, Any])
async def get_signal_statistics(
    timeframe: str = Query("24h", description="時間框架: 1h, 6h, 24h, 7d"),
    include_details: bool = Query(False, description="是否包含詳細統計")
):
    """
    獲取信號處理統計數據
    
    提供信號質量分佈、處理延遲、優先級分析等統計信息
    """
    try:
        if not COORDINATOR_AVAILABLE:
            return {
                "status": "coordinator_unavailable",
                "timestamp": datetime.now().isoformat()
            }
        
        data_type = "full" if include_details else "summary"
        signal_data = await monitoring_coordinator.get_component_specific_data(
            "signal_statistics", data_type
        )
        
        return {
            "statistics_type": "signal_processing",
            "timeframe": timeframe,
            "data": signal_data,
            "includes_details": include_details,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取信號統計失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取信號統計失敗: {str(e)}")

@router.get("/epl-decisions", response_model=Dict[str, Any])
async def get_epl_decision_analysis(
    hours: int = Query(24, description="查詢最近N小時的決策", ge=1, le=168),
    include_outcomes: bool = Query(True, description="是否包含決策結果")
):
    """
    獲取EPL決策歷史與分析
    
    提供決策類型分佈、成功率分析、置信度關聯等信息
    """
    try:
        if not COORDINATOR_AVAILABLE:
            return {
                "status": "coordinator_unavailable",
                "timestamp": datetime.now().isoformat()
            }
        
        data_type = "full" if include_outcomes else "summary"
        epl_data = await monitoring_coordinator.get_component_specific_data(
            "epl_decision_tracker", data_type
        )
        
        return {
            "analysis_type": "epl_decisions",
            "time_range_hours": hours,
            "includes_outcomes": include_outcomes,
            "data": epl_data,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取EPL決策分析失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取EPL決策分析失敗: {str(e)}")

@router.get("/notifications", response_model=Dict[str, Any])
async def get_notification_monitoring(
    channel: Optional[str] = Query(None, description="特定通道: gmail, websocket, frontend, sms"),
    include_engagement: bool = Query(True, description="是否包含參與度指標")
):
    """
    獲取通知成功率監控數據
    
    提供各通道投遞成功率、參與度指標、故障分析等信息
    """
    try:
        if not COORDINATOR_AVAILABLE:
            return {
                "status": "coordinator_unavailable",
                "timestamp": datetime.now().isoformat()
            }
        
        data_type = "full" if include_engagement else "summary"
        notification_data = await monitoring_coordinator.get_component_specific_data(
            "notification_monitor", data_type
        )
        
        # 如果指定了特定通道，過濾數據
        if channel and "data" in notification_data:
            # 這裡可以添加通道過濾邏輯
            pass
        
        return {
            "monitoring_type": "notifications",
            "filtered_channel": channel,
            "includes_engagement": include_engagement,
            "data": notification_data,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取通知監控失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取通知監控失敗: {str(e)}")

@router.get("/performance", response_model=Dict[str, Any])
async def get_system_performance(
    include_predictions: bool = Query(False, description="是否包含性能預測"),
    include_recommendations: bool = Query(True, description="是否包含優化建議")
):
    """
    獲取系統性能監控數據
    
    提供CPU、記憶體、磁盤使用率，應用程序性能指標等信息
    """
    try:
        if not COORDINATOR_AVAILABLE:
            return {
                "status": "coordinator_unavailable",
                "timestamp": datetime.now().isoformat()
            }
        
        data_type = "full" if include_predictions else "summary"
        performance_data = await monitoring_coordinator.get_component_specific_data(
            "performance_monitor", data_type
        )
        
        return {
            "monitoring_type": "system_performance",
            "includes_predictions": include_predictions,
            "includes_recommendations": include_recommendations,
            "data": performance_data,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取系統性能失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取系統性能失敗: {str(e)}")

@router.get("/insights", response_model=Dict[str, Any])
async def get_cross_component_insights():
    """
    獲取跨組件洞察分析
    
    提供性能關聯分析、瓶頸識別、優化建議等跨組件智能分析
    """
    try:
        if not COORDINATOR_AVAILABLE:
            return {
                "status": "coordinator_unavailable",
                "timestamp": datetime.now().isoformat()
            }
        
        overview = await monitoring_coordinator.get_comprehensive_monitoring_overview()
        insights = overview.get("cross_component_insights", {})
        
        return {
            "insights_type": "cross_component_analysis",
            "analysis_scope": "all_monitoring_components",
            "insights": insights,
            "system_health": overview.get("overall_system_health", {}),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取跨組件洞察失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取跨組件洞察失敗: {str(e)}")

@router.post("/events", response_model=Dict[str, Any])
async def record_monitoring_event(event_data: Dict[str, Any]):
    """
    記錄監控事件
    
    接收來自各系統組件的事件，用於實時監控和歷史分析
    """
    try:
        if not COORDINATOR_AVAILABLE:
            return {
                "status": "coordinator_unavailable",
                "message": "監控協調器不可用，無法記錄事件",
                "timestamp": datetime.now().isoformat()
            }
        
        # 添加時間戳
        if "timestamp" not in event_data:
            event_data["timestamp"] = datetime.now().isoformat()
        
        # 記錄事件
        success = await monitoring_coordinator.record_system_event(event_data)
        
        return {
            "event_recorded": success,
            "event_type": event_data.get("type", "unknown"),
            "component": event_data.get("component", "system"),
            "timestamp": event_data["timestamp"],
            "message": "事件記錄成功" if success else "事件記錄失敗"
        }
        
    except Exception as e:
        logger.error(f"記錄監控事件失敗: {e}")
        raise HTTPException(status_code=500, detail=f"記錄監控事件失敗: {str(e)}")

@router.get("/components/{component_name}", response_model=Dict[str, Any])
async def get_component_details(
    component_name: str = Path(..., description="組件名稱"),
    data_type: str = Query("summary", description="數據類型: summary, full")
):
    """
    獲取特定監控組件的詳細數據
    
    支援的組件: unified_dashboard, signal_statistics, epl_decision_tracker, 
    notification_monitor, performance_monitor
    """
    try:
        if not COORDINATOR_AVAILABLE:
            return {
                "status": "coordinator_unavailable",
                "timestamp": datetime.now().isoformat()
            }
        
        valid_components = [
            "unified_dashboard", "signal_statistics", "epl_decision_tracker",
            "notification_monitor", "performance_monitor"
        ]
        
        if component_name not in valid_components:
            raise HTTPException(
                status_code=400, 
                detail=f"無效的組件名稱。支援的組件: {', '.join(valid_components)}"
            )
        
        component_data = await monitoring_coordinator.get_component_specific_data(
            component_name, data_type
        )
        
        return {
            "component_name": component_name,
            "data_type": data_type,
            "data": component_data,
            "retrieved_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取組件詳細數據失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取組件詳細數據失敗: {str(e)}")

@router.get("/real-time", response_model=Dict[str, Any])
async def get_real_time_metrics():
    """
    獲取實時監控指標
    
    提供所有組件的最新狀態，適用於實時儀表板展示
    """
    try:
        if not COORDINATOR_AVAILABLE:
            return {
                "status": "coordinator_unavailable",
                "timestamp": datetime.now().isoformat()
            }
        
        # 並行獲取各組件實時數據
        real_time_data = {}
        
        components = [
            "unified_dashboard", "signal_statistics", "epl_decision_tracker",
            "notification_monitor", "performance_monitor"
        ]
        
        for component in components:
            try:
                component_data = await monitoring_coordinator.get_component_specific_data(
                    component, "summary"
                )
                real_time_data[component] = component_data
            except Exception as e:
                logger.warning(f"獲取 {component} 實時數據失敗: {e}")
                real_time_data[component] = {"status": "error", "error": str(e)}
        
        return {
            "real_time_status": "active",
            "components": real_time_data,
            "coordinator_status": monitoring_coordinator.get_coordinator_status(),
            "timestamp": datetime.now().isoformat(),
            "refresh_rate": "1_second"
        }
        
    except Exception as e:
        logger.error(f"獲取實時指標失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取實時指標失敗: {str(e)}")

@router.post("/cache/clear", response_model=Dict[str, Any])
async def clear_monitoring_cache():
    """
    清理監控系統緩存
    
    清理協調器和各組件的緩存數據，強制重新計算指標
    """
    try:
        if not COORDINATOR_AVAILABLE:
            return {
                "status": "coordinator_unavailable",
                "timestamp": datetime.now().isoformat()
            }
        
        monitoring_coordinator.clear_cache()
        
        return {
            "cache_cleared": True,
            "message": "監控系統緩存已清理",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"清理緩存失敗: {e}")
        raise HTTPException(status_code=500, detail=f"清理緩存失敗: {str(e)}")

@router.get("/export", response_model=Dict[str, Any])
async def export_monitoring_data(
    components: List[str] = Query([], description="要導出的組件列表"),
    format_type: str = Query("json", description="導出格式: json, csv"),
    include_history: bool = Query(True, description="是否包含歷史數據")
):
    """
    導出監控數據
    
    支援導出所有或指定組件的監控數據，用於離線分析或備份
    """
    try:
        if not COORDINATOR_AVAILABLE:
            return {
                "status": "coordinator_unavailable",
                "timestamp": datetime.now().isoformat()
            }
        
        # 如果沒有指定組件，導出所有組件
        if not components:
            components = [
                "unified_dashboard", "signal_statistics", "epl_decision_tracker",
                "notification_monitor", "performance_monitor"
            ]
        
        export_data = {}
        
        for component in components:
            try:
                data_type = "full" if include_history else "summary"
                component_data = await monitoring_coordinator.get_component_specific_data(
                    component, data_type
                )
                export_data[component] = component_data
            except Exception as e:
                logger.warning(f"導出 {component} 數據失敗: {e}")
                export_data[component] = {"status": "export_error", "error": str(e)}
        
        # 添加導出元數據
        export_metadata = {
            "export_timestamp": datetime.now().isoformat(),
            "export_format": format_type,
            "components_exported": components,
            "includes_history": include_history,
            "coordinator_status": monitoring_coordinator.get_coordinator_status()
        }
        
        return {
            "export_successful": True,
            "metadata": export_metadata,
            "data": export_data,
            "total_components": len(components),
            "successful_exports": len([c for c in export_data.values() if c.get("status") != "export_error"])
        }
        
    except Exception as e:
        logger.error(f"導出監控數據失敗: {e}")
        raise HTTPException(status_code=500, detail=f"導出監控數據失敗: {str(e)}")

@router.get("/status", response_model=Dict[str, Any])
async def get_monitoring_system_status():
    """
    獲取監控系統狀態
    
    提供監控系統本身的狀態信息，包括各組件可用性、錯誤統計等
    """
    try:
        if not COORDINATOR_AVAILABLE:
            return {
                "system_status": "coordinator_unavailable",
                "message": "監控協調器不可用",
                "timestamp": datetime.now().isoformat()
            }
        
        coordinator_status = monitoring_coordinator.get_coordinator_status()
        
        # 添加API狀態信息
        api_status = {
            "api_version": "1.0.0",
            "endpoints_available": 12,
            "uptime": "99.9%",  # 這應該是實際的運行時間
            "last_restart": datetime.now().isoformat()  # 這應該是實際的重啟時間
        }
        
        return {
            "system_status": "operational",
            "coordinator": coordinator_status,
            "api": api_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取監控系統狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取監控系統狀態失敗: {str(e)}")

# 健康檢查端點（不需要認證）
@router.get("/ping", response_model=Dict[str, str])
async def ping():
    """
    簡單的健康檢查端點
    
    用於監控系統自身的可用性檢查
    """
    return {
        "status": "ok",
        "message": "Phase4 Output Monitoring API is running",
        "timestamp": datetime.now().isoformat()
    }
