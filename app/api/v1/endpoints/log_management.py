"""
日誌管理 API 端點
提供日誌統計、手動清理等功能
"""

from fastapi import APIRouter, HTTPException
from app.utils.log_manager import get_log_stats, manual_cleanup, log_manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/logs/stats")
async def get_logs_statistics():
    """
    獲取日誌統計信息
    
    返回:
    - 主日誌文件大小和狀態
    - 備份文件列表和年齡
    - 總佔用空間
    - 清理建議
    """
    try:
        stats = get_log_stats()
        
        # 添加清理建議
        recommendations = []
        
        # 檢查主日誌是否需要輪轉
        for log_name, info in stats.get("main_logs", {}).items():
            if info.get("needs_rotation", False):
                recommendations.append(f"{log_name} 需要輪轉 ({info['size_mb']}MB)")
        
        # 檢查過期備份
        expired_count = sum(1 for backup in stats.get("backup_logs", []) if backup.get("expired", False))
        if expired_count > 0:
            recommendations.append(f"{expired_count} 個備份文件已過期")
        
        # 檢查總大小
        total_size = stats.get("total_size_mb", 0)
        if total_size > 200:  # 超過200MB
            recommendations.append(f"總日誌大小過大 ({total_size}MB)")
        
        return {
            "success": True,
            "data": {
                **stats,
                "recommendations": recommendations,
                "cleanup_config": {
                    "max_log_size_mb": log_manager.max_log_size_bytes // (1024 * 1024),
                    "max_backup_age_hours": log_manager.max_backup_age.total_seconds() // 3600,
                    "max_backup_count": log_manager.max_backup_count,
                    "cleanup_interval_hours": log_manager.cleanup_interval.total_seconds() // 3600,
                    "auto_cleanup_running": log_manager.running
                }
            }
        }
        
    except Exception as e:
        logger.error(f"獲取日誌統計失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取日誌統計失敗: {str(e)}")

@router.post("/logs/cleanup")
async def manual_log_cleanup():
    """
    手動觸發日誌清理
    
    立即執行日誌清理，不等待定時任務
    返回清理前後的統計對比
    """
    try:
        logger.info("🧹 API觸發手動日誌清理...")
        
        result = await manual_cleanup()
        
        return {
            "success": True,
            "message": "日誌清理完成",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"手動日誌清理失敗: {e}")
        raise HTTPException(status_code=500, detail=f"日誌清理失敗: {str(e)}")

@router.get("/logs/status")
async def get_log_management_status():
    """
    獲取日誌管理系統狀態
    
    返回自動清理任務的運行狀態和配置
    """
    try:
        return {
            "success": True,
            "data": {
                "auto_cleanup_enabled": log_manager.running,
                "cleanup_interval_hours": log_manager.cleanup_interval.total_seconds() // 3600,
                "next_cleanup_in_seconds": None,  # 可以添加下次清理時間計算
                "config": {
                    "log_directory": str(log_manager.log_dir),
                    "max_log_size_mb": log_manager.max_log_size_bytes // (1024 * 1024),
                    "max_backup_age_hours": log_manager.max_backup_age.total_seconds() // 3600,
                    "max_backup_count": log_manager.max_backup_count
                }
            }
        }
        
    except Exception as e:
        logger.error(f"獲取日誌管理狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取狀態失敗: {str(e)}")

@router.post("/logs/restart-cleanup")
async def restart_log_cleanup():
    """
    重啟日誌清理任務
    
    停止並重新啟動自動清理任務
    """
    try:
        logger.info("🔄 重啟日誌清理任務...")
        
        # 停止現有任務
        await log_manager.stop_auto_cleanup()
        
        # 重新啟動
        await log_manager.start_auto_cleanup()
        
        return {
            "success": True,
            "message": "日誌清理任務已重啟",
            "data": {
                "status": "running",
                "interval_hours": log_manager.cleanup_interval.total_seconds() // 3600
            }
        }
        
    except Exception as e:
        logger.error(f"重啟日誌清理任務失敗: {e}")
        raise HTTPException(status_code=500, detail=f"重啟失敗: {str(e)}")
