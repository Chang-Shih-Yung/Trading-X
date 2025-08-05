"""
🎯 Trading X - 即時監控 API 端點
為X資料夾的獨立監控系統提供FastAPI介面

API端點：
- 啟動/停止監控
- 獲取即時監控數據
- 信號歷史查詢
- 系統狀態監控
- 配置管理
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

# 導入監控管理器
from .real_time_unified_monitoring_manager import (
    unified_monitoring_manager,
    SignalPriority
)

router = APIRouter(prefix="/api/v1/x-monitoring", tags=["X-Monitoring"])

# 請求/響應模型
class MonitoringConfigRequest(BaseModel):
    symbols: Optional[List[str]] = None
    processing_interval: Optional[int] = None
    enabled: Optional[bool] = None

class SignalHistoryRequest(BaseModel):
    symbol: Optional[str] = None
    priority: Optional[str] = None
    limit: int = 50

@router.post("/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    """啟動即時監控系統"""
    try:
        if unified_monitoring_manager.monitoring_enabled:
            return {
                "status": "info",
                "message": "監控系統已在運行中",
                "timestamp": datetime.now().isoformat()
            }
        
        # 在背景啟動監控
        unified_monitoring_manager.monitoring_enabled = True
        background_tasks.add_task(unified_monitoring_manager.start_monitoring)
        
        return {
            "status": "success",
            "message": "即時監控系統啟動成功",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"監控啟動失敗: {str(e)}")

@router.post("/stop")
async def stop_monitoring():
    """停止監控系統"""
    try:
        await unified_monitoring_manager.stop_monitoring()
        
        return {
            "status": "success",
            "message": "監控系統已停止",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"監控停止失敗: {str(e)}")

@router.get("/dashboard")
async def get_dashboard_data():
    """獲取監控儀表板數據"""
    try:
        dashboard_data = await unified_monitoring_manager.get_monitoring_dashboard_data()
        
        return {
            "status": "success",
            "data": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"儀表板數據獲取失敗: {str(e)}")

@router.get("/status")
async def get_monitoring_status():
    """獲取監控系統狀態"""
    try:
        stats = unified_monitoring_manager.stats
        
        return {
            "status": "success",
            "data": {
                "monitoring_enabled": unified_monitoring_manager.monitoring_enabled,
                "monitored_symbols": unified_monitoring_manager.symbols,
                "processing_interval": unified_monitoring_manager.processing_interval,
                "total_signals_processed": stats.total_signals_processed,
                "signals_by_priority": stats.signals_by_priority,
                "data_integrity_stats": stats.data_integrity_stats,
                "notification_stats": stats.notification_stats,
                "performance_metrics": stats.performance_metrics,
                "last_update": stats.last_update.isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"狀態獲取失敗: {str(e)}")

@router.get("/signals/recent")
async def get_recent_signals(
    symbol: Optional[str] = Query(None, description="標的代碼"),
    priority: Optional[str] = Query(None, description="信號優先級"),
    limit: int = Query(50, ge=1, le=200, description="結果數量限制")
):
    """獲取近期信號"""
    try:
        # 轉換優先級字符串
        priority_enum = None
        if priority:
            try:
                priority_enum = SignalPriority(priority.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"無效的優先級: {priority}")
        
        signals = await unified_monitoring_manager.get_signal_history(
            symbol=symbol,
            priority=priority_enum,
            limit=limit
        )
        
        return {
            "status": "success",
            "data": {
                "signals": signals,
                "total_count": len(signals),
                "filters": {
                    "symbol": symbol,
                    "priority": priority,
                    "limit": limit
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"信號歷史獲取失敗: {str(e)}")

@router.post("/config")
async def update_monitoring_config(config: MonitoringConfigRequest):
    """更新監控配置"""
    try:
        config_dict = config.dict(exclude_none=True)
        
        # 驗證配置
        if "symbols" in config_dict:
            if not config_dict["symbols"] or not all(isinstance(s, str) for s in config_dict["symbols"]):
                raise HTTPException(status_code=400, detail="symbols 必須是非空字符串列表")
        
        if "processing_interval" in config_dict:
            if config_dict["processing_interval"] < 10:
                raise HTTPException(status_code=400, detail="processing_interval 最少為10秒")
        
        await unified_monitoring_manager.update_monitoring_config(config_dict)
        
        return {
            "status": "success",
            "message": "監控配置已更新",
            "updated_config": config_dict,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置更新失敗: {str(e)}")

@router.get("/signals/statistics")
async def get_signal_statistics():
    """獲取信號統計數據"""
    try:
        stats = unified_monitoring_manager.stats
        
        # 計算額外統計
        total_notifications = sum(stats.notification_stats.values())
        
        return {
            "status": "success",
            "data": {
                "signal_processing": {
                    "total_processed": stats.total_signals_processed,
                    "by_priority": stats.signals_by_priority,
                    "avg_execution_confidence": stats.performance_metrics.get("avg_execution_confidence", 0)
                },
                "data_quality": {
                    "integrity_stats": stats.data_integrity_stats,
                    "last_cycle_time": stats.performance_metrics.get("last_cycle_time", 0)
                },
                "notifications": {
                    "total_sent": total_notifications,
                    "by_priority": stats.notification_stats,
                    "hourly_counts": unified_monitoring_manager.hourly_notification_counts
                },
                "system_performance": stats.performance_metrics
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"統計數據獲取失敗: {str(e)}")

@router.get("/signals/priority/{priority}")
async def get_signals_by_priority(
    priority: str,
    limit: int = Query(30, ge=1, le=100)
):
    """按優先級獲取信號"""
    try:
        # 驗證優先級
        try:
            priority_enum = SignalPriority(priority.lower())
        except ValueError:
            valid_priorities = [p.value for p in SignalPriority]
            raise HTTPException(
                status_code=400, 
                detail=f"無效的優先級: {priority}。有效值: {valid_priorities}"
            )
        
        signals = await unified_monitoring_manager.get_signal_history(
            priority=priority_enum,
            limit=limit
        )
        
        return {
            "status": "success",
            "data": {
                "priority": priority,
                "signals": signals,
                "count": len(signals)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"優先級信號獲取失敗: {str(e)}")

@router.get("/health")
async def health_check():
    """系統健康檢查"""
    try:
        dashboard_data = await unified_monitoring_manager.get_monitoring_dashboard_data()
        system_health = dashboard_data.get("system_health", {})
        
        all_healthy = all(status == "OK" for status in system_health.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "data": {
                "monitoring_enabled": unified_monitoring_manager.monitoring_enabled,
                "system_components": system_health,
                "last_update": unified_monitoring_manager.stats.last_update.isoformat(),
                "uptime_status": "running" if unified_monitoring_manager.monitoring_enabled else "stopped"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "data": {
                "error": str(e),
                "monitoring_enabled": False,
                "system_components": {},
                "last_update": None,
                "uptime_status": "error"
            },
            "timestamp": datetime.now().isoformat()
        }

@router.post("/signals/manual-trigger")
async def manual_signal_trigger(
    symbol: str = Query(..., description="標的代碼"),
    force: bool = Query(False, description="強制執行忽略冷卻時間")
):
    """手動觸發信號檢測"""
    try:
        # 手動執行一次監控循環
        data_snapshot = await unified_monitoring_manager.signal_engine.collect_real_time_data(symbol)
        
        if data_snapshot.data_integrity.value == "invalid":
            return {
                "status": "warning",
                "message": f"{symbol} 數據無效，無法生成信號",
                "data": {
                    "symbol": symbol,
                    "data_integrity": data_snapshot.data_integrity.value,
                    "missing_components": data_snapshot.missing_components
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # 生成信號候選者
        candidates = await unified_monitoring_manager.signal_engine.stage1_signal_candidate_pool(data_snapshot)
        
        if not candidates:
            return {
                "status": "info",
                "message": f"{symbol} 沒有生成任何信號候選者",
                "data": {
                    "symbol": symbol,
                    "candidates_count": 0,
                    "data_integrity": data_snapshot.data_integrity.value
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # 準備市場環境並執行決策
        market_context = await unified_monitoring_manager._prepare_market_context(symbol, data_snapshot)
        decisions = await unified_monitoring_manager.signal_engine.stage2_epl_decision_layer(candidates, market_context)
        
        # 處理決策（如果是強制模式，則忽略冷卻時間）
        if force:
            # 暫時清除冷卻記錄
            original_cooldowns = unified_monitoring_manager.notification_cooldowns.copy()
            unified_monitoring_manager.notification_cooldowns.clear()
            
            await unified_monitoring_manager._process_decisions(symbol, decisions, data_snapshot)
            
            # 恢復冷卻記錄
            unified_monitoring_manager.notification_cooldowns = original_cooldowns
        else:
            await unified_monitoring_manager._process_decisions(symbol, decisions, data_snapshot)
        
        return {
            "status": "success",
            "message": f"{symbol} 手動信號檢測完成",
            "data": {
                "symbol": symbol,
                "candidates_count": len(candidates),
                "decisions_count": len(decisions),
                "data_integrity": data_snapshot.data_integrity.value,
                "decisions": [
                    {
                        "decision_id": d.decision_id,
                        "final_priority": d.final_priority.value,
                        "execution_confidence": d.execution_confidence,
                        "recommended_action": d.recommended_action
                    }
                    for d in decisions
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"手動信號觸發失敗: {str(e)}")

# 添加路由到主應用
def include_monitoring_routes(app):
    """將監控路由添加到主應用"""
    app.include_router(router)
