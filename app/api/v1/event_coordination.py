#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading X Phase 3 Week 3 Event Coordination API
事件協調引擎的API端點實現
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from app.services.event_coordination_engine import (
    event_coordination_engine,
    CoordinationMode
)

router = APIRouter()

# 請求和響應模型
class EventCoordinationRequest(BaseModel):
    events: List[Dict[str, Any]]
    coordination_mode: Optional[str] = "BALANCED"

class CoordinationModeUpdateRequest(BaseModel):
    coordination_mode: str

class EventCoordinationResponse(BaseModel):
    coordination_id: str
    events_processed: int
    conflicts_detected: int
    conflicts_resolved: int
    coordination_effectiveness: float
    resource_utilization: float
    processing_time_ms: float
    conflicts: List[Dict[str, Any]]
    event_schedule: Optional[Dict[str, Any]]
    recommendations: List[str]
    warnings: List[str]

@router.post("/coordinate", response_model=EventCoordinationResponse)
async def coordinate_events(request: EventCoordinationRequest):
    """
    協調多個事件
    
    Args:
        request: 包含事件列表和協調模式的請求
        
    Returns:
        EventCoordinationResponse: 協調結果
    """
    try:
        # 轉換協調模式字符串到枚舉
        mode_map = {
            "CONSERVATIVE": CoordinationMode.CONSERVATIVE,
            "AGGRESSIVE": CoordinationMode.AGGRESSIVE,
            "BALANCED": CoordinationMode.BALANCED,
            "ADAPTIVE": CoordinationMode.ADAPTIVE
        }
        
        coordination_mode = mode_map.get(request.coordination_mode.upper(), CoordinationMode.BALANCED)
        
        # 執行事件協調
        result = await event_coordination_engine.coordinate_events(
            events=request.events,
            coordination_mode=coordination_mode
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="事件協調失敗")
        
        # 準備衝突信息
        conflicts = []
        for conflict in result.conflicts_detected:
            conflicts.append({
                "conflict_type": conflict.conflict_type.value,
                "description": conflict.conflict_description,
                "severity_score": conflict.severity_score,
                "is_resolved": conflict.is_resolved,
                "resolution_strategy": conflict.resolution_strategy.value if conflict.resolution_strategy else None,
                "event_ids": conflict.event_ids,
                "detection_time": conflict.detection_time.isoformat()
            })
        
        # 準備事件調度信息
        event_schedule = None
        if result.event_schedule:
            schedule = result.event_schedule
            event_schedule = {
                "schedule_id": schedule.schedule_id,
                "coordination_mode": schedule.coordination_mode.value,
                "events": schedule.events,
                "total_duration": schedule.total_duration,
                "resource_allocation": schedule.resource_allocation,
                "risk_assessment": schedule.risk_assessment,
                "is_active": schedule.is_active,
                "start_time": schedule.start_time.isoformat() if schedule.start_time else None,
                "completion_time": schedule.completion_time.isoformat() if schedule.completion_time else None
            }
        
        return EventCoordinationResponse(
            coordination_id=result.coordination_id,
            events_processed=len(result.processed_events),
            conflicts_detected=len(result.conflicts_detected),
            conflicts_resolved=result.conflicts_resolved,
            coordination_effectiveness=result.coordination_effectiveness,
            resource_utilization=result.resource_utilization,
            processing_time_ms=result.processing_time_ms,
            conflicts=conflicts,
            event_schedule=event_schedule,
            recommendations=result.recommendations,
            warnings=result.warnings
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"協調處理錯誤: {str(e)}")

@router.get("/coordination-status")
async def get_coordination_status():
    """
    獲取協調系統狀態
    
    Returns:
        Dict: 協調系統狀態信息
    """
    try:
        status = event_coordination_engine.get_coordination_status()
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取狀態失敗: {str(e)}")

@router.get("/coordination-history")
async def get_coordination_history(
    limit: int = Query(10, ge=1, le=100, description="返回記錄數量限制"),
    include_details: bool = Query(True, description="是否包含詳細信息")
):
    """
    獲取協調歷史記錄
    
    Args:
        limit: 返回記錄數量限制
        include_details: 是否包含詳細信息
        
    Returns:
        Dict: 協調歷史記錄
    """
    try:
        summary = event_coordination_engine.export_coordination_summary()
        
        # 獲取最近的協調記錄
        recent_coordinations = summary.get('recent_coordinations', [])
        limited_coordinations = recent_coordinations[:limit]
        
        # 如果不需要詳細信息，簡化返回
        if not include_details:
            simplified = []
            for coord in limited_coordinations:
                simplified.append({
                    "coordination_id": coord["coordination_id"],
                    "events_processed": coord["events_processed"],
                    "conflicts_detected": coord["conflicts_detected"],
                    "conflicts_resolved": coord["conflicts_resolved"],
                    "effectiveness": coord["effectiveness"],
                    "created_at": coord.get("created_at", "")
                })
            limited_coordinations = simplified
        
        # 計算歷史摘要
        total_coordinations = len(recent_coordinations)
        avg_conflicts = sum(c["conflicts_detected"] for c in recent_coordinations) / max(total_coordinations, 1)
        avg_resolution_rate = sum(c["conflicts_resolved"] / max(c["conflicts_detected"], 1) for c in recent_coordinations) / max(total_coordinations, 1)
        avg_effectiveness = sum(c["effectiveness"] for c in recent_coordinations) / max(total_coordinations, 1)
        
        return {
            "coordinations": limited_coordinations,
            "summary": {
                "total_coordinations": total_coordinations,
                "avg_conflicts_per_coordination": avg_conflicts,
                "avg_resolution_rate": avg_resolution_rate,
                "avg_effectiveness": avg_effectiveness
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取歷史記錄失敗: {str(e)}")

@router.get("/active-schedules")
async def get_active_schedules():
    """
    獲取活躍的事件調度
    
    Returns:
        Dict: 活躍調度列表
    """
    try:
        summary = event_coordination_engine.export_coordination_summary()
        
        active_schedules = summary.get('active_schedules', [])
        
        return {
            "active_schedules": active_schedules,
            "count": len(active_schedules)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取活躍調度失敗: {str(e)}")

@router.get("/coordination-mode")
async def get_coordination_mode():
    """
    獲取當前協調模式
    
    Returns:
        Dict: 當前協調模式
    """
    try:
        status = event_coordination_engine.get_coordination_status()
        
        return {
            "coordination_mode": status.get("coordination_mode", "BALANCED"),
            "mode_description": {
                "CONSERVATIVE": "保守模式 - 優先避免風險",
                "AGGRESSIVE": "積極模式 - 追求最大效果",
                "BALANCED": "平衡模式 - 均衡風險和效果",
                "ADAPTIVE": "自適應模式 - 根據情況動態調整"
            }.get(status.get("coordination_mode", "BALANCED"), "未知模式")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取協調模式失敗: {str(e)}")

@router.put("/coordination-mode")
async def update_coordination_mode(request: CoordinationModeUpdateRequest):
    """
    更新協調模式
    
    Args:
        request: 包含新協調模式的請求
        
    Returns:
        Dict: 更新結果
    """
    try:
        # 驗證協調模式
        valid_modes = ["CONSERVATIVE", "AGGRESSIVE", "BALANCED", "ADAPTIVE"]
        mode = request.coordination_mode.upper()
        
        if mode not in valid_modes:
            raise HTTPException(
                status_code=400, 
                detail=f"無效的協調模式: {mode}. 有效模式: {', '.join(valid_modes)}"
            )
        
        # 轉換到枚舉
        mode_map = {
            "CONSERVATIVE": CoordinationMode.CONSERVATIVE,
            "AGGRESSIVE": CoordinationMode.AGGRESSIVE,
            "BALANCED": CoordinationMode.BALANCED,
            "ADAPTIVE": CoordinationMode.ADAPTIVE
        }
        
        coordination_mode = mode_map[mode]
        
        # 更新協調模式
        event_coordination_engine.coordination_mode = coordination_mode
        
        return {
            "coordination_mode": mode,
            "updated_at": datetime.now().isoformat(),
            "status": "success",
            "message": f"協調模式已更新為 {mode}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新協調模式失敗: {str(e)}")

@router.delete("/coordination-history")
async def clear_coordination_history():
    """
    清空協調歷史記錄
    
    Returns:
        Dict: 清空結果
    """
    try:
        # 清空協調歷史
        event_coordination_engine.coordination_history.clear()
        event_coordination_engine.active_schedules.clear()
        
        return {
            "status": "success",
            "message": "協調歷史記錄已清空",
            "cleared_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空歷史記錄失敗: {str(e)}")

@router.get("/conflict-types")
async def get_conflict_types():
    """
    獲取支持的衝突類型
    
    Returns:
        Dict: 衝突類型列表
    """
    try:
        from app.services.event_coordination_engine import ConflictType, ResolutionStrategy
        
        conflict_types = []
        for conflict_type in ConflictType:
            conflict_types.append({
                "type": conflict_type.value,
                "name": conflict_type.name,
                "description": {
                    "TIMING_CONFLICT": "時間衝突 - 事件時間過於接近",
                    "RESOURCE_CONFLICT": "資源衝突 - 影響相同資產",
                    "DIRECTION_CONFLICT": "方向衝突 - 事件方向相反",
                    "MAGNITUDE_CONFLICT": "強度衝突 - 事件強度衝突",
                    "DEPENDENCY_CONFLICT": "依賴衝突 - 事件間存在依賴關係"
                }.get(conflict_type.name, "未知衝突類型")
            })
        
        resolution_strategies = []
        for strategy in ResolutionStrategy:
            resolution_strategies.append({
                "strategy": strategy.value,
                "name": strategy.name,
                "description": {
                    "PRIORITY_OVERRIDE": "優先級覆蓋 - 高優先級事件優先",
                    "MERGE_EFFECTS": "效果合併 - 合併事件效果",
                    "TIME_SEPARATION": "時間分離 - 調整事件時間",
                    "RESOURCE_SHARING": "資源共享 - 分配資源權重",
                    "CANCEL_LOWER": "取消低優先級 - 取消低優先級事件"
                }.get(strategy.name, "未知解決策略")
            })
        
        return {
            "conflict_types": conflict_types,
            "resolution_strategies": resolution_strategies,
            "coordination_modes": [
                {
                    "mode": "CONSERVATIVE",
                    "description": "保守模式 - 優先避免風險，更多使用時間分離和取消策略"
                },
                {
                    "mode": "AGGRESSIVE", 
                    "description": "積極模式 - 追求最大效果，優先使用優先級覆蓋策略"
                },
                {
                    "mode": "BALANCED",
                    "description": "平衡模式 - 均衡風險和效果，綜合使用各種策略"
                },
                {
                    "mode": "ADAPTIVE",
                    "description": "自適應模式 - 根據具體情況動態選擇最佳策略"
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取衝突類型失敗: {str(e)}")

@router.get("/coordination-stats")
async def get_coordination_statistics():
    """
    獲取協調統計信息
    
    Returns:
        Dict: 詳細統計信息
    """
    try:
        status = event_coordination_engine.get_coordination_status()
        summary = event_coordination_engine.export_coordination_summary()
        
        # 基本統計
        stats = status.get('stats', {})
        
        # 衝突統計
        conflict_summary = summary.get('conflict_summary', {})
        
        # 最近協調記錄
        recent_coordinations = summary.get('recent_coordinations', [])
        
        # 效果分析
        effectiveness_scores = [c.get('effectiveness', 0) for c in recent_coordinations]
        avg_effectiveness = sum(effectiveness_scores) / max(len(effectiveness_scores), 1)
        
        # 處理時間分析
        processing_times = [c.get('processing_time_ms', 0) for c in recent_coordinations]
        avg_processing_time = sum(processing_times) / max(len(processing_times), 1)
        
        return {
            "basic_stats": stats,
            "conflict_stats": conflict_summary,
            "performance_metrics": {
                "avg_effectiveness": avg_effectiveness,
                "avg_processing_time_ms": avg_processing_time,
                "total_coordinations": len(recent_coordinations),
                "success_rate": stats.get('coordination_success_rate', 0)
            },
            "system_health": {
                "health_status": status.get('system_health', '未知'),
                "active_events": status.get('active_events_count', 0),
                "active_schedules": status.get('active_schedules_count', 0),
                "recent_conflicts": status.get('recent_conflicts_count', 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取統計信息失敗: {str(e)}")
