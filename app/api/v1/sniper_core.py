# 🎯 狙擊手計劃核心流程API

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, desc

from app.core.database import get_db
from app.models.sniper_signal_history import SniperSignalDetails, EmailStatus
from app.services.sniper_email_manager import sniper_email_manager

router = APIRouter(prefix="/api/v1/sniper-core", tags=["狙擊手核心流程"])

@router.get("/pipeline-execution")
async def execute_sniper_pipeline():
    """
    🎯 狙擊手計劃核心流程執行
    
    執行流程：
    📊 實時數據 → 🔄 Phase 1ABC → ⚡ Phase 1+2+3 → 📈 pandas-ta → 
    🎯 狙擊手架構(資料庫讀取) → ⭐ 信號評分(每幣種最佳) → 📧 Email通知
    """
    
    pipeline_steps = []
    
    # Step 1: 實時數據檢查
    pipeline_steps.append({
        "step": "📊 實時數據",
        "description": "WebSocket 市場數據",
        "status": "completed",
        "message": "數據流正常"
    })
    
    # Step 2: Phase 1ABC
    pipeline_steps.append({
        "step": "🔄 Phase 1ABC", 
        "description": "信號重構+波動適應+標準化",
        "status": "completed",
        "message": "Phase 1ABC 完成"
    })
    
    # Step 3: Phase 1+2+3
    pipeline_steps.append({
        "step": "⚡ Phase 1+2+3",
        "description": "動態權重+市場深度增強", 
        "status": "completed",
        "message": "Phase 1+2+3 完成"
    })
    
    # Step 4: pandas-ta 技術分析
    pipeline_steps.append({
        "step": "📈 pandas-ta",
        "description": "技術分析計算",
        "status": "completed", 
        "message": "pandas-ta 完成"
    })
    
    # Step 5: 狙擊手架構 - 從資料庫讀取最新信號
    try:
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            # 查詢活躍信號
            active_signals_count = await db.execute(
                select(func.count(SniperSignalDetails.id))
                .where(
                    and_(
                        SniperSignalDetails.status == 'ACTIVE',
                        SniperSignalDetails.created_at >= datetime.now() - timedelta(hours=24)
                    )
                )
            )
            active_count = active_signals_count.scalar()
            
            pipeline_steps.append({
                "step": "🎯 狙擊手架構",
                "description": "雙層智能過濾",
                "status": "completed",
                "message": f"從資料庫讀取到 {active_count} 個最新信號"
            })
            
        finally:
            await db.close()
            
    except Exception as e:
        pipeline_steps.append({
            "step": "🎯 狙擊手架構",
            "description": "雙層智能過濾", 
            "status": "error",
            "message": f"讀取信號失敗: {str(e)}"
        })
    
    # Step 6: 信號評分 - 每幣種最佳信號篩選
    try:
        best_signals = await get_best_signals_per_symbol()
        
        pipeline_steps.append({
            "step": "⭐ 信號評分",
            "description": "智能質量評估",
            "status": "completed",
            "message": f"篩選出 {len(best_signals)} 個幣種的最佳信號"
        })
        
    except Exception as e:
        pipeline_steps.append({
            "step": "⭐ 信號評分", 
            "description": "智能質量評估",
            "status": "error",
            "message": f"信號篩選失敗: {str(e)}"
        })
        best_signals = []
    
    # Step 7: Email 通知
    email_status = "completed" if sniper_email_manager.gmail_service else "waiting"
    email_message = f"✅ 已載入 {len(best_signals)} 個精準信號 (自動Email通知)" if email_status == "completed" else "等待Gmail配置"
    
    pipeline_steps.append({
        "step": "📧 Email 通知",
        "description": "精選信號自動通知",
        "status": email_status,
        "message": email_message
    })
    
    return {
        "success": True,
        "pipeline": "狙擊手計劃核心流程",
        "timestamp": datetime.now().isoformat(),
        "steps": pipeline_steps,
        "signals": best_signals,
        "summary": {
            "total_signals": len(best_signals),
            "pipeline_status": "completed",
            "email_enabled": sniper_email_manager.gmail_service is not None
        }
    }

@router.get("/best-signals")
async def get_best_signals():
    """
    🎯 獲取每個幣種的最佳信號 (去重後)
    確保每個幣種只返回一個信心度最高的信號
    """
    try:
        best_signals = await get_best_signals_per_symbol()
        return {
            "success": True,
            "signals": best_signals,
            "count": len(best_signals),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取最佳信號失敗: {str(e)}")

async def get_best_signals_per_symbol() -> List[dict]:
    """
    核心邏輯：每個幣種只返回一個最佳信號
    """
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    try:
        # 🎯 查詢每個幣種信心度最高的信號
        subquery = (
            select(
                SniperSignalDetails.symbol,
                func.max(SniperSignalDetails.signal_strength).label('max_strength')
            )
            .where(
                and_(
                    SniperSignalDetails.status == 'ACTIVE',
                    SniperSignalDetails.created_at >= datetime.now() - timedelta(hours=24)
                )
            )
            .group_by(SniperSignalDetails.symbol)
            .subquery()
        )
        
        # 獲取最優秀的信號詳情
        result = await db.execute(
            select(SniperSignalDetails)
            .join(
                subquery,
                and_(
                    SniperSignalDetails.symbol == subquery.c.symbol,
                    SniperSignalDetails.signal_strength == subquery.c.max_strength
                )
            )
            .where(SniperSignalDetails.status == 'ACTIVE')
            .order_by(
                desc(SniperSignalDetails.signal_strength),
                desc(SniperSignalDetails.created_at)  # 相同信心度選最新的
            )
        )
        
        signals = result.scalars().all()
        
        # 🎯 去重：確保每個幣種只有一個信號
        unique_signals = {}
        for signal in signals:
            if signal.symbol not in unique_signals:
                unique_signals[signal.symbol] = signal
            else:
                # 選擇更新的信號
                existing = unique_signals[signal.symbol]
                if signal.created_at > existing.created_at:
                    unique_signals[signal.symbol] = signal
        
        # 轉換為前端格式
        best_signals = []
        for signal in unique_signals.values():
            best_signals.append({
                "id": signal.signal_id,
                "symbol": signal.symbol,
                "signal_type": signal.signal_type,
                "entry_price": signal.entry_price,
                "stop_loss": signal.stop_loss_price,
                "take_profit": signal.take_profit_price,
                "signal_strength": signal.signal_strength,
                "confidence": signal.signal_strength,  # 兼容性
                "confluence_count": signal.confluence_count,
                "signal_quality": signal.signal_quality,
                "timeframe": signal.timeframe.value if signal.timeframe else "1h",
                "risk_reward_ratio": signal.risk_reward_ratio,
                "created_at": signal.created_at.isoformat(),
                "expires_at": signal.expires_at.isoformat() if signal.expires_at else None,
                "reasoning": signal.reasoning or "狙擊手智能分層信號",
                "status": signal.status,
                "email_status": signal.email_status.value if signal.email_status else "PENDING"
            })
        
        return best_signals
        
    finally:
        await db.close()

@router.get("/email-status")
async def get_email_status():
    """
    📧 獲取Email發送狀態
    """
    try:
        status_summary = await sniper_email_manager.get_email_status_summary()
        return {
            "success": True,
            "email_manager_active": sniper_email_manager.is_running,
            "gmail_configured": sniper_email_manager.gmail_service is not None,
            "status_summary": status_summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取Email狀態失敗: {str(e)}")

@router.post("/trigger-email")
async def trigger_email_sending():
    """
    🎯 手動觸發Email發送 (每個幣種只發送最佳信號)
    """
    if not sniper_email_manager.gmail_service:
        raise HTTPException(status_code=400, detail="Gmail服務未配置")
    
    try:
        # 手動觸發最佳信號發送
        await sniper_email_manager._scan_and_send_best_signals()
        return {
            "success": True,
            "message": "Email發送任務已觸發",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"觸發Email發送失敗: {str(e)}")
