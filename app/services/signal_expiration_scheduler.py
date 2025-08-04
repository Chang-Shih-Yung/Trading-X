"""
🎯 狙擊手信號過期定時調度器
自動化處理基於智能時間分層動態計算的信號過期
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from app.services.signal_expiration_service import signal_expiration_service

logger = logging.getLogger(__name__)

class SignalExpirationScheduler:
    """🎯 狙擊手信號過期定時調度器"""
    
    def __init__(self):
        self.is_running = False
        self.task = None
        self.check_interval = 300  # 5分鐘檢查一次
        
    async def start_scheduler(self):
        """啟動定時調度器"""
        if self.is_running:
            logger.warning("🎯 調度器已經在運行中")
            return
            
        self.is_running = True
        logger.info(f"🎯 啟動狙擊手信號過期調度器 (檢查間隔: {self.check_interval}秒)")
        
        # 創建後台任務
        self.task = asyncio.create_task(self._scheduler_loop())
        
    async def stop_scheduler(self):
        """停止定時調度器"""
        if not self.is_running:
            return
            
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("🎯 狙擊手信號過期調度器已停止")
        
    async def _scheduler_loop(self):
        """調度器主循環"""
        logger.info("🎯 狙擊手信號過期調度器開始運行")
        
        while self.is_running:
            try:
                # 執行過期檢查和處理
                result = await self._execute_expiration_check()
                
                if result['expired_count'] > 0:
                    logger.info(f"🎯 定時處理完成: 處理了 {result['expired_count']} 個過期信號")
                else:
                    logger.debug("🎯 定時檢查: 無過期信號需要處理")
                
                # 等待下次檢查
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                logger.info("🎯 調度器收到取消信號，準備停止")
                break
            except Exception as e:
                logger.error(f"❌ 調度器執行過程中發生錯誤: {e}")
                # 發生錯誤時等待較短時間後重試
                await asyncio.sleep(60)
                
    async def _execute_expiration_check(self) -> Dict[str, Any]:
        """執行過期檢查"""
        try:
            # 調用信號過期服務
            result = await signal_expiration_service.check_and_process_expired_signals()
            
            if result['success'] and result['expired_count'] > 0:
                # 記錄處理的信號詳情
                for signal in result['processed_signals']:
                    logger.info(f"🎯 信號已過期: {signal['symbol']} {signal['signal_type']} (持續{signal['recommended_duration_minutes']}分鐘)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 執行過期檢查失敗: {e}")
            return {
                'success': False,
                'expired_count': 0,
                'error': str(e)
            }
    
    async def manual_trigger(self) -> Dict[str, Any]:
        """手動觸發過期處理"""
        logger.info("🎯 手動觸發狙擊手信號過期處理")
        return await self._execute_expiration_check()
    
    def get_status(self) -> Dict[str, Any]:
        """獲取調度器狀態"""
        return {
            'is_running': self.is_running,
            'check_interval_seconds': self.check_interval,
            'next_check': datetime.now() + timedelta(seconds=self.check_interval) if self.is_running else None,
            'task_status': 'running' if self.task and not self.task.done() else 'stopped'
        }

# 創建全域調度器實例
signal_expiration_scheduler = SignalExpirationScheduler()
