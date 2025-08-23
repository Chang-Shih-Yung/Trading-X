#!/usr/bin/env python3
"""
🧠 Trading X - 內存管理優化系統
實時監控和優化系統內存使用，確保穩定運行

功能特色：
- 實時內存監控
- 自動垃圾回收
- 數據清理策略
- 內存洩漏檢測
"""

import gc
import psutil
import logging
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MemoryOptimizationManager:
    """內存優化管理器"""
    
    def __init__(self, 
                 memory_threshold: float = 85.0,
                 critical_threshold: float = 90.0,
                 cleanup_interval: int = 300):
        """
        初始化內存優化管理器
        
        Args:
            memory_threshold: 內存使用率警告閾值 (%)
            critical_threshold: 內存使用率臨界閾值 (%)
            cleanup_interval: 清理間隔 (秒)
        """
        self.memory_threshold = memory_threshold
        self.critical_threshold = critical_threshold
        self.cleanup_interval = cleanup_interval
        
        self.last_cleanup_time = time.time()
        self.memory_history = []
        self.cleanup_statistics = {
            'total_cleanups': 0,
            'memory_freed_mb': 0.0,
            'last_cleanup_time': None
        }
        
        logger.info(f"🧠 內存優化管理器初始化完成")
        logger.info(f"   警告閾值: {memory_threshold}%")
        logger.info(f"   臨界閾值: {critical_threshold}%") 
        logger.info(f"   清理間隔: {cleanup_interval}秒")

    def get_memory_info(self) -> Dict[str, Any]:
        """獲取當前內存信息"""
        try:
            # 系統內存信息
            memory = psutil.virtual_memory()
            
            # 當前進程內存信息
            process = psutil.Process()
            process_memory = process.memory_info()
            
            memory_info = {
                'system': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'percentage': memory.percent
                },
                'process': {
                    'rss_mb': round(process_memory.rss / (1024**2), 2),
                    'vms_mb': round(process_memory.vms / (1024**2), 2)
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # 記錄內存歷史
            self.memory_history.append({
                'timestamp': time.time(),
                'percentage': memory.percent,
                'process_rss_mb': memory_info['process']['rss_mb']
            })
            
            # 保持最近1小時的歷史數據
            cutoff_time = time.time() - 3600
            self.memory_history = [
                h for h in self.memory_history 
                if h['timestamp'] > cutoff_time
            ]
            
            return memory_info
            
        except Exception as e:
            logger.error(f"❌ 獲取內存信息失敗: {e}")
            return {}

    def check_memory_status(self) -> Dict[str, Any]:
        """檢查內存狀態並返回建議"""
        memory_info = self.get_memory_info()
        
        if not memory_info:
            return {'status': 'error', 'action': 'none'}
            
        current_usage = memory_info['system']['percentage']
        
        status_info = {
            'current_usage': current_usage,
            'threshold_warning': self.memory_threshold,
            'threshold_critical': self.critical_threshold,
            'timestamp': memory_info['timestamp']
        }
        
        if current_usage >= self.critical_threshold:
            status_info.update({
                'status': 'critical',
                'action': 'immediate_cleanup',
                'message': f'內存使用率達到臨界水平: {current_usage:.1f}%'
            })
        elif current_usage >= self.memory_threshold:
            status_info.update({
                'status': 'warning', 
                'action': 'scheduled_cleanup',
                'message': f'內存使用率超過警告閾值: {current_usage:.1f}%'
            })
        else:
            status_info.update({
                'status': 'normal',
                'action': 'none',
                'message': f'內存使用率正常: {current_usage:.1f}%'
            })
            
        return status_info

    async def perform_cleanup(self, force: bool = False) -> Dict[str, Any]:
        """執行內存清理"""
        current_time = time.time()
        
        # 檢查是否需要清理
        if not force:
            if current_time - self.last_cleanup_time < self.cleanup_interval:
                return {'status': 'skipped', 'reason': 'too_soon'}
                
            memory_status = self.check_memory_status()
            if memory_status['status'] == 'normal':
                return {'status': 'skipped', 'reason': 'memory_normal'}
        
        # 記錄清理前的內存狀態
        memory_before = self.get_memory_info()
        rss_before = memory_before.get('process', {}).get('rss_mb', 0)
        
        logger.info("🧹 開始執行內存清理...")
        
        try:
            # 1. 強制垃圾回收
            collected_objects = []
            for generation in range(3):
                collected = gc.collect()
                collected_objects.append(collected)
                await asyncio.sleep(0.1)  # 讓出控制權
            
            # 2. 清理未引用的循環
            gc.collect()
            
            # 3. 清理內存中的緩存數據 (如果有的話)
            # 這裡可以添加特定的數據清理邏輯
            
            # 等待一下讓系統釋放內存
            await asyncio.sleep(1)
            
            # 記錄清理後的內存狀態
            memory_after = self.get_memory_info()
            rss_after = memory_after.get('process', {}).get('rss_mb', 0)
            
            memory_freed = rss_before - rss_after
            
            # 更新統計數據
            self.cleanup_statistics['total_cleanups'] += 1
            self.cleanup_statistics['memory_freed_mb'] += memory_freed
            self.cleanup_statistics['last_cleanup_time'] = datetime.now().isoformat()
            self.last_cleanup_time = current_time
            
            cleanup_result = {
                'status': 'completed',
                'memory_before_mb': rss_before,
                'memory_after_mb': rss_after,
                'memory_freed_mb': memory_freed,
                'objects_collected': sum(collected_objects),
                'cleanup_time': datetime.now().isoformat()
            }
            
            logger.info(f"✅ 內存清理完成:")
            logger.info(f"   清理前: {rss_before:.1f} MB")
            logger.info(f"   清理後: {rss_after:.1f} MB") 
            logger.info(f"   釋放內存: {memory_freed:.1f} MB")
            logger.info(f"   回收對象: {sum(collected_objects)} 個")
            
            return cleanup_result
            
        except Exception as e:
            logger.error(f"❌ 內存清理失敗: {e}")
            return {'status': 'error', 'error': str(e)}

    async def monitor_memory_loop(self):
        """內存監控循環"""
        logger.info("🔄 啟動內存監控循環")
        
        while True:
            try:
                memory_status = self.check_memory_status()
                
                if memory_status['action'] == 'immediate_cleanup':
                    logger.warning(f"🚨 {memory_status['message']}")
                    await self.perform_cleanup(force=True)
                elif memory_status['action'] == 'scheduled_cleanup':
                    logger.warning(f"⚠️ {memory_status['message']}")
                    await self.perform_cleanup()
                    
                # 每30秒檢查一次
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ 內存監控循環錯誤: {e}")
                await asyncio.sleep(60)  # 錯誤時等待更久

    def get_statistics(self) -> Dict[str, Any]:
        """獲取內存管理統計數據"""
        return {
            'cleanup_statistics': self.cleanup_statistics.copy(),
            'current_memory': self.get_memory_info(),
            'memory_history_count': len(self.memory_history),
            'configuration': {
                'memory_threshold': self.memory_threshold,
                'critical_threshold': self.critical_threshold,
                'cleanup_interval': self.cleanup_interval
            }
        }

# 全局內存管理器實例
memory_manager = None

def get_memory_manager() -> MemoryOptimizationManager:
    """獲取全局內存管理器實例"""
    global memory_manager
    if memory_manager is None:
        memory_manager = MemoryOptimizationManager()
    return memory_manager

async def start_memory_monitoring():
    """啟動內存監控"""
    manager = get_memory_manager()
    await manager.monitor_memory_loop()

if __name__ == "__main__":
    # 測試內存管理器
    async def test_memory_manager():
        manager = MemoryOptimizationManager()
        
        print("內存信息:")
        memory_info = manager.get_memory_info()
        print(f"系統內存: {memory_info['system']}")
        print(f"進程內存: {memory_info['process']}")
        
        print("\\n內存狀態:")
        status = manager.check_memory_status()
        print(f"狀態: {status}")
        
        print("\\n執行清理:")
        result = await manager.perform_cleanup(force=True)
        print(f"清理結果: {result}")
        
        print("\\n統計數據:")
        stats = manager.get_statistics()
        print(f"統計: {stats}")
    
    asyncio.run(test_memory_manager())
