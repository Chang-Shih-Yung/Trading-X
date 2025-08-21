#!/usr/bin/env python3
"""
🧹 File Cleanup Manager
檔案清理管理器 - 解決存儲堆積問題

功能：
- Phase2 output 檔案清理 (保留最新 3 個)
- Phase5 working 檔案清理 (保留最新 7 個)
- 系統 log 檔案清理 (保留最新 5 個)
- 定期自動清理排程
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple
import re
import json

logger = logging.getLogger(__name__)

class FileCleanupManager:
    """檔案清理管理器"""
    
    def __init__(self):
        """初始化清理管理器"""
        self.base_dir = Path(__file__).parent.parent.parent.parent  # 回到 X 目錄
        
        # 清理配置
        self.cleanup_config = {
            'phase2_output': {
                'path': self.base_dir / 'backend' / 'phase2_adaptive_learning' / 'output',
                'pattern': 'phase2_optimized_params_*.json',
                'keep_latest': 3,
                'description': 'Phase2 優化參數檔案'
            },
            'phase5_working': {
                'path': self.base_dir / 'backend' / 'phase5_backtest_validation' / 'safety_backups' / 'working',
                'pattern': 'phase1a_backup_deployment_*.json',
                'keep_latest': 7,
                'description': 'Phase5 工作備份檔案'
            },
            'system_logs': {
                'path': self.base_dir,
                'pattern': 'production_trading_*.log',
                'keep_latest': 5,
                'description': '系統運行日誌檔案'
            },
            'debug_logs': {
                'path': self.base_dir,
                'pattern': 'debug_*.log',
                'keep_latest': 3,
                'description': '除錯日誌檔案'
            }
        }
        
        # 清理統計
        self.cleanup_stats = {
            'total_files_cleaned': 0,
            'space_freed_mb': 0,
            'last_cleanup': None,
            'cleanup_history': []
        }
        
        logger.info("🧹 檔案清理管理器初始化完成")
    
    async def cleanup_all(self) -> Dict[str, Dict]:
        """執行全面清理"""
        logger.info("🧹 開始全面檔案清理...")
        
        cleanup_results = {}
        total_cleaned = 0
        total_space_freed = 0
        
        for category, config in self.cleanup_config.items():
            try:
                result = await self._cleanup_category(category, config)
                cleanup_results[category] = result
                total_cleaned += result['files_cleaned']
                total_space_freed += result['space_freed_mb']
                
            except Exception as e:
                logger.error(f"❌ {category} 清理失敗: {e}")
                cleanup_results[category] = {
                    'status': 'failed',
                    'error': str(e),
                    'files_cleaned': 0,
                    'space_freed_mb': 0
                }
        
        # 更新統計
        self.cleanup_stats['total_files_cleaned'] += total_cleaned
        self.cleanup_stats['space_freed_mb'] += total_space_freed
        self.cleanup_stats['last_cleanup'] = datetime.now()
        
        # 記錄清理歷史
        cleanup_record = {
            'timestamp': datetime.now().isoformat(),
            'files_cleaned': total_cleaned,
            'space_freed_mb': total_space_freed,
            'categories': list(cleanup_results.keys())
        }
        self.cleanup_stats['cleanup_history'].append(cleanup_record)
        
        # 保持歷史記錄不超過 20 條
        if len(self.cleanup_stats['cleanup_history']) > 20:
            self.cleanup_stats['cleanup_history'] = self.cleanup_stats['cleanup_history'][-20:]
        
        logger.info(f"✅ 清理完成: {total_cleaned} 個檔案, {total_space_freed:.2f} MB")
        return cleanup_results
    
    async def _cleanup_category(self, category: str, config: Dict) -> Dict:
        """清理特定類別的檔案"""
        try:
            path = Path(config['path'])
            pattern = config['pattern']
            keep_latest = config['keep_latest']
            description = config['description']
            
            if not path.exists():
                logger.warning(f"⚠️ 路徑不存在: {path}")
                return {
                    'status': 'skipped',
                    'reason': 'path_not_exists',
                    'files_cleaned': 0,
                    'space_freed_mb': 0
                }
            
            # 找到匹配的檔案
            files = list(path.glob(pattern))
            
            if not files:
                logger.debug(f"📂 {description}: 無檔案需要清理")
                return {
                    'status': 'no_files',
                    'files_cleaned': 0,
                    'space_freed_mb': 0
                }
            
            # 按修改時間排序 (最新的在前)
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # 決定要刪除的檔案
            files_to_delete = files[keep_latest:]
            files_to_keep = files[:keep_latest]
            
            if not files_to_delete:
                logger.debug(f"📂 {description}: 檔案數量在限制內 ({len(files)}/{keep_latest})")
                return {
                    'status': 'within_limit',
                    'files_cleaned': 0,
                    'space_freed_mb': 0,
                    'files_kept': len(files_to_keep)
                }
            
            # 執行刪除
            deleted_files = []
            space_freed = 0
            
            for file_path in files_to_delete:
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_files.append(file_path.name)
                    space_freed += file_size
                    logger.debug(f"🗑️ 已刪除: {file_path.name}")
                    
                except Exception as e:
                    logger.error(f"❌ 刪除失敗 {file_path.name}: {e}")
            
            space_freed_mb = space_freed / (1024 * 1024)
            
            logger.info(f"✅ {description}: 清理 {len(deleted_files)} 個檔案, {space_freed_mb:.2f} MB")
            
            return {
                'status': 'success',
                'files_cleaned': len(deleted_files),
                'space_freed_mb': space_freed_mb,
                'files_kept': len(files_to_keep),
                'deleted_files': deleted_files
            }
            
        except Exception as e:
            logger.error(f"❌ {category} 清理失敗: {e}")
            raise
    
    async def cleanup_phase2_output(self) -> Dict:
        """清理 Phase2 輸出檔案"""
        return await self._cleanup_category('phase2_output', self.cleanup_config['phase2_output'])
    
    async def cleanup_phase5_working(self) -> Dict:
        """清理 Phase5 工作檔案"""
        return await self._cleanup_category('phase5_working', self.cleanup_config['phase5_working'])
    
    async def cleanup_system_logs(self) -> Dict:
        """清理系統日誌檔案"""
        log_results = {}
        
        # 清理系統日誌
        log_results['system_logs'] = await self._cleanup_category(
            'system_logs', self.cleanup_config['system_logs']
        )
        
        # 清理除錯日誌
        log_results['debug_logs'] = await self._cleanup_category(
            'debug_logs', self.cleanup_config['debug_logs']
        )
        
        return log_results
    
    async def get_storage_status(self) -> Dict:
        """獲取存儲狀態"""
        try:
            status = {}
            
            for category, config in self.cleanup_config.items():
                path = Path(config['path'])
                pattern = config['pattern']
                keep_latest = config['keep_latest']
                
                if not path.exists():
                    status[category] = {
                        'status': 'path_not_exists',
                        'file_count': 0,
                        'total_size_mb': 0
                    }
                    continue
                
                files = list(path.glob(pattern))
                total_size = sum(f.stat().st_size for f in files)
                total_size_mb = total_size / (1024 * 1024)
                
                files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                files_over_limit = len(files) - keep_latest
                
                status[category] = {
                    'file_count': len(files),
                    'total_size_mb': total_size_mb,
                    'limit': keep_latest,
                    'over_limit': max(0, files_over_limit),
                    'needs_cleanup': files_over_limit > 0,
                    'latest_files': [f.name for f in files[:3]]  # 顯示最新 3 個
                }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ 存儲狀態獲取失敗: {e}")
            return {'error': str(e)}
    
    async def schedule_periodic_cleanup(self, interval_hours: int = 6):
        """定期清理排程"""
        logger.info(f"⏰ 啟動定期清理: 每 {interval_hours} 小時執行一次")
        
        while True:
            try:
                await asyncio.sleep(interval_hours * 3600)  # 轉換為秒
                
                logger.info("⏰ 執行定期清理...")
                results = await self.cleanup_all()
                
                # 檢查是否有清理操作
                total_cleaned = sum(r.get('files_cleaned', 0) for r in results.values())
                if total_cleaned > 0:
                    logger.info(f"✅ 定期清理完成: {total_cleaned} 個檔案")
                else:
                    logger.debug("📂 定期清理: 無檔案需要清理")
                    
            except Exception as e:
                logger.error(f"❌ 定期清理失敗: {e}")
                await asyncio.sleep(300)  # 錯誤後等待 5 分鐘再試
    
    def get_cleanup_statistics(self) -> Dict:
        """獲取清理統計"""
        return self.cleanup_stats.copy()
    
    async def emergency_cleanup(self, aggressive: bool = False) -> Dict:
        """緊急清理 (更激進的清理策略)"""
        logger.warning("🚨 執行緊急清理...")
        
        if aggressive:
            # 更激進的清理策略
            original_config = self.cleanup_config.copy()
            
            # 臨時調整保留數量
            self.cleanup_config['phase2_output']['keep_latest'] = 1
            self.cleanup_config['phase5_working']['keep_latest'] = 3
            self.cleanup_config['system_logs']['keep_latest'] = 2
            self.cleanup_config['debug_logs']['keep_latest'] = 1
            
            try:
                results = await self.cleanup_all()
                return results
            finally:
                # 恢復原始配置
                self.cleanup_config = original_config
        else:
            return await self.cleanup_all()

# 全局實例
file_cleanup_manager = FileCleanupManager()

async def main():
    """測試函數"""
    print("🧹 File Cleanup Manager 測試")
    
    # 獲取存儲狀態
    status = await file_cleanup_manager.get_storage_status()
    print("📊 存儲狀態:")
    for category, info in status.items():
        print(f"  {category}: {info}")
    
    # 執行清理
    results = await file_cleanup_manager.cleanup_all()
    print("\n🧹 清理結果:")
    for category, result in results.items():
        print(f"  {category}: {result}")
    
    # 獲取統計
    stats = file_cleanup_manager.get_cleanup_statistics()
    print(f"\n📈 清理統計: {stats}")
    
    print("✅ 測試完成")

if __name__ == "__main__":
    asyncio.run(main())
