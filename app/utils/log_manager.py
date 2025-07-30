"""
日誌管理和清理工具
提供自動清理舊日誌文件的功能
"""

import os
import glob
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import shutil

logger = logging.getLogger(__name__)

class LogManager:
    """日誌管理器 - 負責清理和維護日誌文件"""
    
    def __init__(self, 
                 log_dir: str = ".",
                 max_log_size_mb: int = 100,  # 單個日誌文件最大大小 (MB)
                 max_backup_age_hours: int = 24,  # 備份文件保留時間 (小時)
                 max_backup_count: int = 10,  # 最多保留備份文件數量
                 cleanup_interval_hours: int = 1):  # 清理間隔 (小時)
        
        self.log_dir = Path(log_dir)
        self.max_log_size_bytes = max_log_size_mb * 1024 * 1024
        self.max_backup_age = timedelta(hours=max_backup_age_hours)
        self.max_backup_count = max_backup_count
        self.cleanup_interval = timedelta(hours=cleanup_interval_hours)
        
        self.running = False
        self.cleanup_task = None
        
        # 確保日誌目錄存在
        self.log_dir.mkdir(exist_ok=True)
        
    async def start_auto_cleanup(self):
        """啟動自動清理任務"""
        if self.running:
            logger.warning("日誌清理任務已在運行")
            return
            
        self.running = True
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info(f"✅ 日誌自動清理已啟動 - 每 {self.cleanup_interval.total_seconds()/3600:.1f} 小時執行一次")
        
    async def stop_auto_cleanup(self):
        """停止自動清理任務"""
        if not self.running:
            return
            
        self.running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
                
        logger.info("✅ 日誌自動清理已停止")
        
    async def _cleanup_loop(self):
        """清理循環"""
        while self.running:
            try:
                # 執行清理
                await self.cleanup_logs()
                
                # 等待下次清理
                await asyncio.sleep(self.cleanup_interval.total_seconds())
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"日誌清理循環錯誤: {e}")
                # 出錯時等待較短時間再重試
                await asyncio.sleep(300)  # 5分鐘
                
    async def cleanup_logs(self):
        """執行日誌清理"""
        try:
            cleaned_files = []
            freed_space = 0
            
            # 1. 檢查主日誌文件大小
            main_log_files = ["server.log", "app.log", "trading.log"]
            for log_name in main_log_files:
                log_path = self.log_dir / log_name
                if log_path.exists():
                    size_mb = log_path.stat().st_size / (1024 * 1024)
                    if log_path.stat().st_size > self.max_log_size_bytes:
                        backup_name = f"{log_name}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        backup_path = self.log_dir / backup_name
                        
                        # 移動到備份
                        shutil.move(str(log_path), str(backup_path))
                        cleaned_files.append(f"輪轉 {log_name} ({size_mb:.1f}MB)")
                        
                        logger.info(f"📦 日誌輪轉: {log_name} -> {backup_name}")
            
            # 2. 清理舊的備份文件
            backup_patterns = [
                "*.log.backup_*",
                "server_backup_*.log",
                "app_backup_*.log",
                "*.log.*"
            ]
            
            current_time = datetime.now()
            
            for pattern in backup_patterns:
                backup_files = list(self.log_dir.glob(pattern))
                
                # 按修改時間排序
                backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                for i, backup_file in enumerate(backup_files):
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    file_age = current_time - file_time
                    file_size = backup_file.stat().st_size
                    
                    should_delete = False
                    reason = ""
                    
                    # 檢查年齡
                    if file_age > self.max_backup_age:
                        should_delete = True
                        reason = f"過期 ({file_age.total_seconds()/3600:.1f}h)"
                    
                    # 檢查數量限制
                    elif i >= self.max_backup_count:
                        should_delete = True
                        reason = f"超出數量限制 (#{i+1})"
                    
                    if should_delete:
                        try:
                            backup_file.unlink()
                            freed_space += file_size
                            cleaned_files.append(f"刪除 {backup_file.name} ({reason})")
                            logger.info(f"🗑️ 清理備份: {backup_file.name} - {reason}")
                        except Exception as e:
                            logger.error(f"❌ 清理失敗 {backup_file.name}: {e}")
            
            # 3. 清理空的或損壞的日誌文件
            all_log_files = list(self.log_dir.glob("*.log*"))
            for log_file in all_log_files:
                try:
                    if log_file.stat().st_size == 0:
                        log_file.unlink()
                        cleaned_files.append(f"刪除空文件 {log_file.name}")
                        logger.info(f"🗑️ 清理空文件: {log_file.name}")
                except Exception as e:
                    logger.error(f"❌ 檢查文件失敗 {log_file.name}: {e}")
            
            # 4. 報告清理結果
            if cleaned_files:
                freed_mb = freed_space / (1024 * 1024)
                logger.info(f"🧹 日誌清理完成:")
                logger.info(f"   - 處理了 {len(cleaned_files)} 個文件")
                logger.info(f"   - 釋放了 {freed_mb:.1f} MB 空間")
                for action in cleaned_files[:5]:  # 只顯示前5個
                    logger.info(f"   - {action}")
                if len(cleaned_files) > 5:
                    logger.info(f"   - ... 還有 {len(cleaned_files) - 5} 個文件")
            else:
                logger.debug("🧹 日誌清理: 沒有需要清理的文件")
                
        except Exception as e:
            logger.error(f"❌ 日誌清理失敗: {e}")
            
    def get_log_statistics(self) -> dict:
        """獲取日誌統計信息"""
        try:
            stats = {
                "main_logs": {},
                "backup_logs": [],
                "total_size_mb": 0,
                "oldest_backup": None,
                "newest_backup": None
            }
            
            # 主日誌文件
            main_logs = ["server.log", "app.log", "trading.log"]
            for log_name in main_logs:
                log_path = self.log_dir / log_name
                if log_path.exists():
                    size_mb = log_path.stat().st_size / (1024 * 1024)
                    modified = datetime.fromtimestamp(log_path.stat().st_mtime)
                    stats["main_logs"][log_name] = {
                        "size_mb": round(size_mb, 2),
                        "modified": modified.isoformat(),
                        "needs_rotation": size_mb > (self.max_log_size_bytes / (1024 * 1024))
                    }
                    stats["total_size_mb"] += size_mb
            
            # 備份文件
            backup_patterns = ["*.log.backup_*", "server_backup_*.log", "app_backup_*.log"]
            backup_files = []
            
            for pattern in backup_patterns:
                backup_files.extend(self.log_dir.glob(pattern))
            
            current_time = datetime.now()
            backup_times = []
            
            for backup_file in backup_files:
                size_mb = backup_file.stat().st_size / (1024 * 1024)
                modified = datetime.fromtimestamp(backup_file.stat().st_mtime)
                age_hours = (current_time - modified).total_seconds() / 3600
                
                backup_info = {
                    "name": backup_file.name,
                    "size_mb": round(size_mb, 2),
                    "modified": modified.isoformat(),
                    "age_hours": round(age_hours, 1),
                    "expired": age_hours > self.max_backup_age.total_seconds() / 3600
                }
                
                stats["backup_logs"].append(backup_info)
                stats["total_size_mb"] += size_mb
                backup_times.append(modified)
            
            if backup_times:
                stats["oldest_backup"] = min(backup_times).isoformat()
                stats["newest_backup"] = max(backup_times).isoformat()
            
            stats["total_size_mb"] = round(stats["total_size_mb"], 2)
            stats["backup_count"] = len(backup_files)
            
            return stats
            
        except Exception as e:
            logger.error(f"獲取日誌統計失敗: {e}")
            return {"error": str(e)}
            
    async def force_cleanup(self) -> dict:
        """手動觸發清理並返回結果"""
        logger.info("🧹 手動觸發日誌清理...")
        
        before_stats = self.get_log_statistics()
        await self.cleanup_logs()
        after_stats = self.get_log_statistics()
        
        return {
            "before": before_stats,
            "after": after_stats,
            "space_freed_mb": round(before_stats.get("total_size_mb", 0) - after_stats.get("total_size_mb", 0), 2)
        }

# 全局日誌管理器實例
log_manager = LogManager(
    log_dir="/Users/henrychang/Desktop/Trading-X",
    max_log_size_mb=50,  # 50MB 後輪轉
    max_backup_age_hours=24,  # 保留24小時
    max_backup_count=5,  # 最多5個備份
    cleanup_interval_hours=1  # 每小時清理
)

async def start_log_management():
    """啟動日誌管理"""
    await log_manager.start_auto_cleanup()

async def stop_log_management():
    """停止日誌管理"""
    await log_manager.stop_auto_cleanup()

def get_log_stats():
    """獲取日誌統計信息"""
    return log_manager.get_log_statistics()

async def manual_cleanup():
    """手動清理日誌"""
    return await log_manager.force_cleanup()
