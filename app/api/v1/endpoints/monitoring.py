#!/usr/bin/env python3
"""
🎯 Trading X - 監控與通知API端點
提供完整的監控儀表板與信號處理API

Author: Trading X Team
Version: 2.0.0
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from app.services.unified_monitoring_manager import unified_monitoring
from app.services.signal_quality_control_engine import SignalPriority, EPLAction

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])

# Pydantic 模型
class SignalInput(BaseModel):
    """信號輸入模型"""
    symbol: str
    signal_type: str  # BUY/SELL
    confidence: float
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    quality_score: Optional[float] = None
    source: Optional[str] = "api"
    indicators_used: Optional[List[str]] = []
    reasoning: Optional[str] = "技術分析指標匯聚"
    timeframe: Optional[str] = "1h"
    risk_reward_ratio: Optional[float] = None
    market_conditions: Optional[Dict[str, Any]] = {}

class MonitoringConfig(BaseModel):
    """監控配置模型"""
    gmail_enabled: bool
    gmail_sender: Optional[str] = None
    gmail_password: Optional[str] = None
    gmail_recipient: Optional[str] = None
    notification_rules: Optional[Dict[str, Any]] = None

@router.post("/signals/process")
async def process_signal(signal: SignalInput):
    """
    處理新信號通過品質控制系統
    
    這是主要的信號處理端點，會通過完整的兩階段決策架構：
    1. 信號去重與關聯分析
    2. EPL決策層處理
    3. 分級輸出與通知
    """
    try:
        logger.info(f"🎯 API接收信號: {signal.symbol} {signal.signal_type}")
        
        # 轉換為字典格式
        signal_data = signal.dict()
        
        # 通過統一監控管理器處理
        result = await unified_monitoring.process_incoming_signal(signal_data)
        
        if not result:
            raise HTTPException(status_code=400, detail="信號處理失敗")
        
        return {
            "success": True,
            "message": "信號處理完成",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ API處理信號錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"處理信號時發生錯誤: {str(e)}")

@router.get("/dashboard")
async def get_monitoring_dashboard():
    """
    獲取完整的監控儀表板數據
    
    返回：
    - 系統狀態
    - 今日統計
    - 品質引擎狀態  
    - 通知統計
    - 性能指標
    """
    try:
        dashboard_data = unified_monitoring.get_monitoring_dashboard_data()
        
        return {
            "success": True,
            "data": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 獲取儀表板數據錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"獲取儀表板數據失敗: {str(e)}")

@router.get("/quality-engine/statistics")
async def get_quality_engine_stats():
    """獲取信號品質控制引擎統計"""
    try:
        stats = unified_monitoring.quality_engine.get_engine_statistics()
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 獲取品質引擎統計錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quality-engine/reset-stats")
async def reset_quality_engine_stats():
    """重置品質引擎統計數據"""
    try:
        unified_monitoring.quality_engine.reset_statistics()
        
        return {
            "success": True,
            "message": "統計數據已重置",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 重置統計錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active-positions")
async def get_active_positions():
    """獲取當前活躍持倉信號"""
    try:
        positions = unified_monitoring.quality_engine.active_positions
        
        # 轉換為API友好格式
        active_positions = {}
        for symbol, candidate in positions.items():
            active_positions[symbol] = candidate.to_dict()
        
        return {
            "success": True,
            "data": {
                "count": len(active_positions),
                "positions": active_positions
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 獲取活躍持倉錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/decision-history")
async def get_decision_history(limit: int = 50):
    """獲取EPL決策歷史"""
    try:
        history = unified_monitoring.quality_engine.decision_history
        
        # 返回最近的決策記錄
        recent_history = history[-limit:] if len(history) > limit else history
        
        return {
            "success": True,
            "data": {
                "total_decisions": len(history),
                "recent_decisions": recent_history,
                "limit": limit
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 獲取決策歷史錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configuration")
async def update_monitoring_config(config: MonitoringConfig):
    """更新監控配置"""
    try:
        # 初始化Gmail服務（如果需要）
        if config.gmail_enabled and config.gmail_sender and config.gmail_password:
            await unified_monitoring.initialize_services(
                gmail_sender=config.gmail_sender,
                gmail_password=config.gmail_password,
                gmail_recipient=config.gmail_recipient
            )
        
        # 更新通知規則
        if config.notification_rules:
            unified_monitoring.notification_config['notification_rules'].update(config.notification_rules)
        
        return {
            "success": True,
            "message": "監控配置已更新",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 更新配置錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"更新配置失敗: {str(e)}")

@router.post("/notifications/test")
async def test_notification_system():
    """測試通知系統"""
    try:
        if not unified_monitoring.gmail_service:
            raise HTTPException(status_code=400, detail="Gmail服務未配置")
        
        # 發送測試通知
        success = await unified_monitoring.gmail_service.test_notification()
        
        return {
            "success": success,
            "message": "測試通知已發送" if success else "測試通知發送失敗",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 測試通知錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-health")
async def get_system_health():
    """獲取系統健康狀態"""
    try:
        stats = unified_monitoring.monitoring_stats
        
        health_data = {
            "system_health": stats['system_health'],
            "monitoring_active": unified_monitoring.monitoring_active,
            "gmail_enabled": unified_monitoring.notification_config['gmail_enabled'],
            "signals_processed_today": stats['signals_processed_today'],
            "notifications_sent_today": stats['notifications_sent_today'],
            "last_signal_time": stats['last_signal_time'],
            "performance_metrics": stats['performance_metrics']
        }
        
        return {
            "success": True,
            "data": health_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 獲取系統健康狀態錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/signals/batch-process")
async def batch_process_signals(signals: List[SignalInput]):
    """批量處理信號"""
    try:
        logger.info(f"🎯 批量處理 {len(signals)} 個信號")
        
        results = []
        for signal in signals:
            try:
                signal_data = signal.dict()
                result = await unified_monitoring.process_incoming_signal(signal_data)
                results.append({
                    "signal": signal.dict(),
                    "result": result,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "signal": signal.dict(),
                    "error": str(e),
                    "success": False
                })
        
        success_count = sum(1 for r in results if r['success'])
        
        return {
            "success": True,
            "message": f"批量處理完成: {success_count}/{len(signals)} 成功",
            "data": {
                "total_signals": len(signals),
                "successful": success_count,
                "failed": len(signals) - success_count,
                "results": results
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 批量處理信號錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-monitoring")
async def start_monitoring(background_tasks: BackgroundTasks):
    """啟動監控循環"""
    try:
        if unified_monitoring.monitoring_active:
            return {
                "success": True,
                "message": "監控已在運行中",
                "timestamp": datetime.now().isoformat()
            }
        
        # 在背景任務中啟動監控
        background_tasks.add_task(unified_monitoring.start_monitoring)
        
        return {
            "success": True,
            "message": "監控循環已啟動",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 啟動監控錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-monitoring")
async def stop_monitoring():
    """停止監控循環"""
    try:
        unified_monitoring.stop_monitoring()
        
        return {
            "success": True,
            "message": "監控已停止",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 停止監控錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/websocket/status")
async def get_websocket_status():
    """獲取WebSocket連接狀態"""
    try:
        # 這裡可以檢查實時信號引擎的WebSocket狀態
        websocket_status = {
            "connected": False,
            "connections": 0,
            "last_update": None
        }
        
        if unified_monitoring.realtime_engine:
            # 假設實時引擎有這些屬性
            websocket_status = {
                "connected": True,
                "connections": getattr(unified_monitoring.realtime_engine, 'active_connections', 0),
                "last_update": datetime.now().isoformat()
            }
        
        return {
            "success": True,
            "data": websocket_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 獲取WebSocket狀態錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))
