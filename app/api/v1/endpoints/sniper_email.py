# 🎯 狙擊手 Email 管理 API 端點

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from app.services.sniper_email_manager import sniper_email_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sniper/email", tags=["sniper-email"])

@router.get("/status/summary", response_model=Dict[str, Any])
async def get_email_status_summary():
    """
    🎯 獲取 Email 發送狀態統計
    
    Returns:
        Dict: Email 狀態統計信息
    """
    try:
        summary = await sniper_email_manager.get_email_status_summary()
        
        return {
            "status": "success",
            "data": summary,
            "message": "Email 狀態統計獲取成功"
        }
        
    except Exception as e:
        logger.error(f"❌ 獲取 Email 狀態統計失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取統計失敗: {str(e)}")

@router.post("/resend/{signal_id}")
async def resend_signal_email(signal_id: str):
    """
    🎯 手動重新發送指定信號的 Email
    
    Args:
        signal_id: 信號 ID
        
    Returns:
        Dict: 重發結果
    """
    try:
        success = await sniper_email_manager.resend_failed_email(signal_id)
        
        if success:
            return {
                "status": "success",
                "data": {"signal_id": signal_id, "sent": True},
                "message": f"信號 {signal_id} Email 重發成功"
            }
        else:
            return {
                "status": "failed",
                "data": {"signal_id": signal_id, "sent": False},
                "message": f"信號 {signal_id} Email 重發失敗"
            }
            
    except Exception as e:
        logger.error(f"❌ 重發 Email 失敗: {e}")
        raise HTTPException(status_code=500, detail=f"重發失敗: {str(e)}")

@router.get("/signals/{signal_id}/status")
async def get_signal_email_status(signal_id: str):
    """
    🎯 獲取指定信號的 Email 發送狀態
    
    Args:
        signal_id: 信號 ID
        
    Returns:
        Dict: Email 狀態詳情
    """
    try:
        from app.core.database import get_db
        from app.models.sniper_signal_history import SniperSignalDetails
        from sqlalchemy import select
        
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            result = await db.execute(
                select(SniperSignalDetails).where(
                    SniperSignalDetails.signal_id == signal_id
                )
            )
            signal = result.scalar_one_or_none()
            
            if not signal:
                raise HTTPException(status_code=404, detail=f"找不到信號: {signal_id}")
            
            return {
                "status": "success",
                "data": {
                    "signal_id": signal_id,
                    "symbol": signal.symbol,
                    "email_status": signal.email_status.value,
                    "email_sent_at": signal.email_sent_at.isoformat() if signal.email_sent_at else None,
                    "email_retry_count": signal.email_retry_count,
                    "email_last_error": signal.email_last_error,
                    "can_resend": signal.email_status.value in ["FAILED", "PENDING"]
                },
                "message": "Email 狀態獲取成功"
            }
            
        finally:
            await db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 獲取信號 Email 狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取狀態失敗: {str(e)}")
