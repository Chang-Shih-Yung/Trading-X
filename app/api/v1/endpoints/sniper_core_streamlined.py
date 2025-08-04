from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ========================================
# 🎯 狙擊手策略核心API - 精簡版
# 只保留前端實際使用的端點
# ========================================

@router.get("/dashboard-precision-signals")
async def get_dashboard_precision_signals():
    """📊 核心API: 為儀表板提供精準篩選的信號"""
    try:
        from app.services.sniper_smart_layer import sniper_smart_layer
        
        current_signals = await sniper_smart_layer.get_all_active_signals()
        if not current_signals:
            return {
                "status": "success",
                "signals": [],
                "message": "當前無活躍信號",
                "timestamp": datetime.now().isoformat()
            }
        
        # 信號去重和篩選邏輯
        signal_map = {}
        for signal in current_signals:
            symbol = signal['symbol']
            if symbol not in signal_map:
                signal_map[symbol] = signal
            else:
                # 保留品質更高的信號
                existing_quality = signal_map[symbol].get('quality_score', 0)
                current_quality = signal.get('quality_score', 0)
                if current_quality > existing_quality:
                    signal_map[symbol] = signal
        
        return {
            "status": "success",
            "signals": list(signal_map.values()),
            "count": len(signal_map),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取精準信號失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sniper-unified-data-layer")
async def get_sniper_unified_data():
    """🎯 核心API: 狙擊手統一數據層"""
    try:
        from app.services.sniper_smart_layer import sniper_smart_layer
        
        # 獲取統一數據
        data = await sniper_smart_layer.get_unified_market_data()
        
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取統一數據失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals")
async def get_signals():
    """📊 核心API: 獲取基礎信號列表"""
    try:
        from app.services.sniper_smart_layer import sniper_smart_layer
        
        signals = await sniper_smart_layer.get_all_active_signals()
        
        return {
            "status": "success",
            "signals": signals,
            "count": len(signals),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取信號失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pandas-ta-direct")
async def get_pandas_ta_analysis():
    """📈 核心API: 直接技術分析結果"""
    try:
        from app.services.technical_analysis import get_technical_analysis
        
        analysis = await get_technical_analysis()
        
        return {
            "status": "success", 
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"技術分析失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/expired")
async def get_expired_signals():
    """⏰ 核心API: 獲取過期信號"""
    try:
        from app.services.sniper_signal_history_service import get_expired_signals
        
        expired = await get_expired_signals()
        
        return {
            "status": "success",
            "expired_signals": expired,
            "count": len(expired),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取過期信號失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# 🎯 狙擊手歷史管理 - 精簡版
# ========================================

@router.get("/history/signals")
async def get_signal_history(
    days: int = 7,
    limit: int = 50,
    symbol: Optional[str] = None
):
    """📜 核心API: 獲取信號歷史"""
    try:
        from app.services.sniper_signal_history_service import get_signal_history
        
        history = await get_signal_history(
            days=days,
            limit=limit, 
            symbol=symbol
        )
        
        return {
            "status": "success",
            "signals": history,
            "count": len(history),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取歷史信號失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/statistics")
async def get_signal_statistics():
    """📊 核心API: 獲取信號統計"""
    try:
        from app.services.sniper_signal_history_service import get_statistics
        
        stats = await get_statistics()
        
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取統計失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# 🎯 狙擊手策略配置 - 精簡版  
# ========================================

@router.get("/dynamic-parameters")
async def get_dynamic_parameters():
    """⚙️ 核心API: 獲取動態參數"""
    try:
        from app.services.signal_scoring_engine import signal_scoring_engine
        
        params = await signal_scoring_engine.get_current_parameters()
        
        return {
            "status": "success",
            "parameters": params,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取參數失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/phase1abc-integration-status") 
async def get_phase_integration_status():
    """🔄 核心API: Phase 整合狀態"""
    try:
        from app.services.phase_integration import get_integration_status
        
        status = await get_integration_status()
        
        return {
            "status": "success",
            "integration": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取整合狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/phase3-market-depth")
async def get_phase3_market_depth():
    """📊 核心API: Phase 3 市場深度分析"""
    try:
        from app.services.phase3_analysis import get_market_depth_analysis
        
        analysis = await get_market_depth_analysis()
        
        return {
            "status": "success",
            "market_depth": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"市場深度分析失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# 🎯 系統狀態監控 - 精簡版
# ========================================

@router.get("/status")
async def get_system_status():
    """💓 核心API: 系統狀態檢查"""
    try:
        from app.services.system_monitor import get_system_health
        
        health = await get_system_health()
        
        return {
            "status": "success",
            "system_health": health,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"系統狀態檢查失敗: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
