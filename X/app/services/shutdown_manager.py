"""
系統停機管理器
管理多層級的系統停機機制，包含自動停機、手動停機、漸進式停機
"""

import asyncio
import json
import fcntl
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
from pathlib import Path
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShutdownReason(Enum):
    """停機原因枚舉"""
    EXTREME_MARKET = "extreme_market"
    SYSTEM_FAILURE = "system_failure"
    DATA_CORRUPTION = "data_corruption"
    MANUAL_INTERVENTION = "manual_intervention"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MAINTENANCE_MODE = "maintenance_mode"
    EMERGENCY_INTERVENTION = "emergency_intervention"

class SeverityLevel(Enum):
    """嚴重程度枚舉"""
    CRITICAL = "critical"
    EMERGENCY = "emergency"
    PRECAUTIONARY = "precautionary"

class ShutdownPhase(Enum):
    """停機階段枚舉"""
    SIGNAL_GENERATION_STOP = "signal_generation_stop"
    POSITION_MONITORING_ONLY = "position_monitoring_only"
    COMPLETE_SHUTDOWN = "complete_shutdown"

class SystemMonitor:
    """系統監控器"""
    
    def __init__(self):
        self.monitoring_active = False
        self.last_check_time = datetime.now()
        
    def check_system_health(self) -> Dict[str, Any]:
        """檢查系統健康狀況"""
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 記憶體使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # 磁碟空間
            disk = psutil.disk_usage('/')
            disk_free_gb = disk.free / (1024**3)
            disk_used_percent = (disk.used / disk.total) * 100
            
            # 網路連接狀態
            network_connections = len(psutil.net_connections())
            
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_available_gb": round(memory_available_gb, 2),
                "disk_free_gb": round(disk_free_gb, 2),
                "disk_used_percent": round(disk_used_percent, 2),
                "network_connections": network_connections,
                "health_score": self._calculate_health_score(cpu_percent, memory_percent, disk_free_gb)
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"系統健康檢查失敗: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "health_score": 0
            }
    
    def _calculate_health_score(self, cpu_percent: float, memory_percent: float, disk_free_gb: float) -> float:
        """計算系統健康分數 (0-100)"""
        cpu_score = max(0, 100 - cpu_percent)
        memory_score = max(0, 100 - memory_percent)
        disk_score = min(100, disk_free_gb * 10)  # 每GB給10分，最多100分
        
        return round((cpu_score + memory_score + disk_score) / 3, 2)
    
    def check_shutdown_conditions(self) -> List[Dict[str, Any]]:
        """檢查是否觸發停機條件"""
        triggers = []
        health = self.check_system_health()
        
        # 檢查資源耗盡
        if health.get("memory_percent", 0) > 90:
            triggers.append({
                "reason": ShutdownReason.RESOURCE_EXHAUSTION.value,
                "severity": SeverityLevel.CRITICAL.value,
                "details": f"記憶體使用率過高: {health['memory_percent']:.1f}%",
                "threshold": "90%",
                "current_value": f"{health['memory_percent']:.1f}%"
            })
        
        if health.get("disk_free_gb", 0) < 1:
            triggers.append({
                "reason": ShutdownReason.RESOURCE_EXHAUSTION.value,
                "severity": SeverityLevel.CRITICAL.value,
                "details": f"磁碟空間不足: {health['disk_free_gb']:.2f}GB",
                "threshold": "1GB",
                "current_value": f"{health['disk_free_gb']:.2f}GB"
            })
        
        if health.get("cpu_percent", 0) > 95:
            triggers.append({
                "reason": ShutdownReason.SYSTEM_FAILURE.value,
                "severity": SeverityLevel.EMERGENCY.value,
                "details": f"CPU使用率過高: {health['cpu_percent']:.1f}%",
                "threshold": "95%",
                "current_value": f"{health['cpu_percent']:.1f}%"
            })
        
        return triggers

class ShutdownManager:
    """系統停機管理器"""
    
    def __init__(self):
        # 設定基礎路徑
        self.base_dir = Path(__file__).parent.parent.parent
        
        # 系統鎖定和日誌文件 (修正為X資料夾內)
        self.lock_file_path = self.base_dir / "data" / "locks" / "shutdown_manager.lock"
        self.lock_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.shutdown_log_path = self.base_dir / "data" / "logs" / "shutdown_events.log"
        self.shutdown_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.system_monitor = SystemMonitor()
        self.is_shutdown_in_progress = False
        self.current_shutdown_phase = None
        self.shutdown_start_time = None
        
        # 交易對列表
        self.symbols = ["XRPUSDT", "DOGEUSDT", "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
        
        # 停機狀態文件 (修正為X資料夾內)
        self.base_dir = Path(__file__).parent.parent.parent
        self.shutdown_status_file = self.base_dir / "data" / "system_status" / "shutdown_status.json"
        self.shutdown_status_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化停機狀態
        self._initialize_shutdown_status()
    
    def _initialize_shutdown_status(self):
        """初始化停機狀態"""
        default_status = {
            "system_running": True,
            "shutdown_in_progress": False,
            "current_phase": None,
            "shutdown_reason": None,
            "shutdown_start_time": None,
            "last_health_check": None,
            "protected_symbols": {},
            "system_health": {}
        }
        
        if not self.shutdown_status_file.exists():
            self._save_shutdown_status(default_status)
    
    def _save_shutdown_status(self, status: Dict[str, Any]):
        """保存停機狀態到檔案"""
        try:
            with open(self.shutdown_status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存停機狀態失敗: {e}")
    
    def _load_shutdown_status(self) -> Dict[str, Any]:
        """載入停機狀態"""
        try:
            if self.shutdown_status_file.exists():
                with open(self.shutdown_status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"載入停機狀態失敗: {e}")
        
        # 返回默認狀態
        return {
            "system_running": True,
            "shutdown_in_progress": False,
            "current_phase": None
        }
    
    async def _log_shutdown_event(self, event_data: Dict[str, Any]):
        """記錄停機事件"""
        try:
            with open(self.shutdown_log_path, 'a', encoding='utf-8') as f:
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    **event_data
                }
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"記錄停機事件失敗: {e}")
    
    async def check_automatic_shutdown_conditions(self) -> Optional[Dict[str, Any]]:
        """檢查自動停機條件"""
        try:
            # 檢查系統健康狀況
            triggers = self.system_monitor.check_shutdown_conditions()
            
            if triggers:
                # 選擇最嚴重的觸發條件
                critical_triggers = [t for t in triggers if t["severity"] == SeverityLevel.CRITICAL.value]
                if critical_triggers:
                    return critical_triggers[0]
                
                emergency_triggers = [t for t in triggers if t["severity"] == SeverityLevel.EMERGENCY.value]
                if emergency_triggers:
                    return emergency_triggers[0]
                
                return triggers[0]
            
            # 檢查市場極端條件（需要整合閃崩檢測器）
            await self._check_market_extreme_conditions()
            
            # 檢查效能惡化（需要整合Phase2學習結果）
            await self._check_performance_degradation()
            
            # 檢查數據完整性（需要整合數據驗證）
            await self._check_data_integrity()
            
            return None
            
        except Exception as e:
            logger.error(f"檢查自動停機條件失敗: {e}")
            return {
                "reason": ShutdownReason.SYSTEM_FAILURE.value,
                "severity": SeverityLevel.CRITICAL.value,
                "details": f"停機條件檢查失敗: {e}"
            }
    
    async def _check_market_extreme_conditions(self):
        """檢查市場極端條件"""
        # TODO: 整合閃崩檢測器的結果
        # 這裡會檢查是否有多個交易對同時觸發極端崩盤檢測
        pass
    
    async def _check_performance_degradation(self):
        """檢查效能惡化"""
        # TODO: 整合Phase2學習結果
        # 檢查是否連續5次學習導致效能下降>20%
        pass
    
    async def _check_data_integrity(self):
        """檢查數據完整性"""
        # TODO: 整合數據驗證機制
        # 檢查市場數據是否缺失或錯誤>10%
        pass
    
    async def initiate_shutdown(self, reason: ShutdownReason, severity: SeverityLevel, 
                              details: str, manual: bool = False) -> bool:
        """啟動系統停機程序"""
        
        # 檔案鎖定保護
        try:
            with open(self.lock_file_path, 'w') as lock_file:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                
                try:
                    # 檢查是否已在停機過程中
                    if self.is_shutdown_in_progress:
                        logger.warning("停機程序已在進行中，忽略新的停機請求")
                        return False
                    
                    self.is_shutdown_in_progress = True
                    self.shutdown_start_time = datetime.now()
                    
                    # 生成停機ID
                    shutdown_id = f"shutdown_{int(time.time())}"
                    
                    # 記錄停機事件
                    shutdown_event = {
                        "shutdown_id": shutdown_id,
                        "reason": reason.value,
                        "severity": severity.value,
                        "details": details,
                        "manual": manual,
                        "start_time": self.shutdown_start_time.isoformat(),
                        "system_health": self.system_monitor.check_system_health()
                    }
                    
                    await self._log_shutdown_event(shutdown_event)
                    
                    logger.critical(f"🚨 啟動系統停機程序")
                    logger.critical(f"   停機ID: {shutdown_id}")
                    logger.critical(f"   原因: {reason.value}")
                    logger.critical(f"   嚴重程度: {severity.value}")
                    logger.critical(f"   詳情: {details}")
                    logger.critical(f"   手動觸發: {manual}")
                    
                    # 執行漸進式停機
                    await self._execute_gradual_shutdown(shutdown_event)
                    
                    return True
                    
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    
        except Exception as e:
            logger.error(f"啟動停機程序失敗: {e}")
            return False
    
    async def _execute_gradual_shutdown(self, shutdown_event: Dict[str, Any]):
        """執行漸進式停機"""
        try:
            # 階段1: 停止信號生成
            await self._shutdown_phase_1(shutdown_event)
            await asyncio.sleep(5)  # 給系統5秒緩衝時間
            
            # 階段2: 僅監控現有持倉
            await self._shutdown_phase_2(shutdown_event)
            await asyncio.sleep(30)  # 給持倉30秒處理時間
            
            # 階段3: 完全停機
            await self._shutdown_phase_3(shutdown_event)
            
        except Exception as e:
            logger.error(f"漸進式停機執行失敗: {e}")
            # 緊急強制停機
            await self._emergency_force_shutdown(shutdown_event)
    
    async def _shutdown_phase_1(self, shutdown_event: Dict[str, Any]):
        """停機階段1: 停止信號生成"""
        self.current_shutdown_phase = ShutdownPhase.SIGNAL_GENERATION_STOP
        
        logger.warning("🔄 停機階段1: 停止信號生成")
        
        # 更新停機狀態
        status = self._load_shutdown_status()
        status.update({
            "current_phase": self.current_shutdown_phase.value,
            "phase_1_completed": datetime.now().isoformat()
        })
        self._save_shutdown_status(status)
        
        # TODO: 通知Phase1A停止生成新信號
        # 這裡需要與Phase1A信號生成器整合
        
        await self._log_shutdown_event({
            "shutdown_id": shutdown_event["shutdown_id"],
            "phase": "phase_1_completed",
            "action": "停止信號生成",
            "details": "Phase1A信號生成已停止"
        })
        
        logger.info("✅ 階段1完成: 信號生成已停止")
    
    async def _shutdown_phase_2(self, shutdown_event: Dict[str, Any]):
        """停機階段2: 僅監控現有持倉"""
        self.current_shutdown_phase = ShutdownPhase.POSITION_MONITORING_ONLY
        
        logger.warning("🔄 停機階段2: 僅監控現有持倉")
        
        # 更新停機狀態
        status = self._load_shutdown_status()
        status.update({
            "current_phase": self.current_shutdown_phase.value,
            "phase_2_completed": datetime.now().isoformat()
        })
        self._save_shutdown_status(status)
        
        # TODO: 停止新的交易執行，僅保持風險控制
        # 這裡需要與交易執行器整合
        
        await self._log_shutdown_event({
            "shutdown_id": shutdown_event["shutdown_id"],
            "phase": "phase_2_completed",
            "action": "僅監控持倉",
            "details": "新交易已停止，僅保持風險控制"
        })
        
        logger.info("✅ 階段2完成: 僅監控現有持倉")
    
    async def _shutdown_phase_3(self, shutdown_event: Dict[str, Any]):
        """停機階段3: 完全停機"""
        self.current_shutdown_phase = ShutdownPhase.COMPLETE_SHUTDOWN
        
        logger.critical("🔄 停機階段3: 完全停機")
        
        # 更新停機狀態
        status = self._load_shutdown_status()
        status.update({
            "system_running": False,
            "current_phase": self.current_shutdown_phase.value,
            "phase_3_completed": datetime.now().isoformat(),
            "shutdown_completed": True
        })
        self._save_shutdown_status(status)
        
        # TODO: 完全停止所有操作
        # 保存重要數據
        # 關閉數據庫連接
        # 清理資源
        
        shutdown_duration = (datetime.now() - self.shutdown_start_time).total_seconds()
        
        await self._log_shutdown_event({
            "shutdown_id": shutdown_event["shutdown_id"],
            "phase": "phase_3_completed",
            "action": "完全停機",
            "details": f"系統已完全停機，耗時 {shutdown_duration:.2f} 秒",
            "shutdown_duration_seconds": shutdown_duration
        })
        
        logger.critical("🛑 系統已完全停機，進入安全模式")
        
        # 最終狀態保存
        final_status = {
            "system_running": False,
            "shutdown_completed": True,
            "shutdown_duration_seconds": shutdown_duration,
            "final_shutdown_time": datetime.now().isoformat()
        }
        self._save_shutdown_status(final_status)
    
    async def _emergency_force_shutdown(self, shutdown_event: Dict[str, Any]):
        """緊急強制停機"""
        logger.critical("⚠️ 執行緊急強制停機")
        
        await self._log_shutdown_event({
            "shutdown_id": shutdown_event["shutdown_id"],
            "phase": "emergency_force_shutdown",
            "action": "緊急強制停機",
            "details": "正常停機程序失敗，執行緊急強制停機"
        })
        
        # 強制更新狀態
        status = {
            "system_running": False,
            "shutdown_completed": True,
            "emergency_shutdown": True,
            "emergency_shutdown_time": datetime.now().isoformat()
        }
        self._save_shutdown_status(status)
    
    async def manual_shutdown(self, reason: str, details: str = "") -> bool:
        """手動停機"""
        logger.warning(f"收到手動停機請求: {reason}")
        
        if reason == "maintenance":
            shutdown_reason = ShutdownReason.MAINTENANCE_MODE
            severity = SeverityLevel.PRECAUTIONARY
        elif reason == "emergency":
            shutdown_reason = ShutdownReason.EMERGENCY_INTERVENTION
            severity = SeverityLevel.EMERGENCY
        else:
            shutdown_reason = ShutdownReason.MANUAL_INTERVENTION
            severity = SeverityLevel.PRECAUTIONARY
        
        return await self.initiate_shutdown(
            shutdown_reason, 
            severity, 
            details or f"手動停機: {reason}",
            manual=True
        )
    
    def get_shutdown_status(self) -> Dict[str, Any]:
        """獲取停機狀態"""
        status = self._load_shutdown_status()
        
        # 添加實時系統健康信息
        if status.get("system_running", False):
            status["system_health"] = self.system_monitor.check_system_health()
            status["last_health_check"] = datetime.now().isoformat()
        
        return status
    
    def is_system_running(self) -> bool:
        """檢查系統是否在運行"""
        status = self._load_shutdown_status()
        return status.get("system_running", True) and not status.get("shutdown_in_progress", False)
    
    async def start_monitoring(self):
        """啟動停機監控"""
        logger.info("🚀 啟動系統停機監控")
        
        while True:
            try:
                if not self.is_system_running():
                    logger.info("系統已停機，停止監控")
                    break
                
                # 檢查自動停機條件
                trigger = await self.check_automatic_shutdown_conditions()
                
                if trigger:
                    logger.warning(f"檢測到停機觸發條件: {trigger}")
                    
                    reason = ShutdownReason(trigger["reason"])
                    severity = SeverityLevel(trigger["severity"])
                    
                    await self.initiate_shutdown(
                        reason,
                        severity,
                        trigger["details"],
                        manual=False
                    )
                    break
                
                # 每30秒檢查一次
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"停機監控過程錯誤: {e}")
                await asyncio.sleep(60)  # 錯誤時等待更久再重試
    
    async def recovery_check(self) -> Dict[str, Any]:
        """恢復檢查"""
        status = self._load_shutdown_status()
        
        if not status.get("system_running", True):
            health = self.system_monitor.check_system_health()
            
            recovery_status = {
                "can_recover": health.get("health_score", 0) > 70,
                "health_score": health.get("health_score", 0),
                "system_health": health,
                "recovery_recommendations": []
            }
            
            if health.get("memory_percent", 0) > 80:
                recovery_status["recovery_recommendations"].append("清理記憶體使用")
            
            if health.get("disk_free_gb", 0) < 2:
                recovery_status["recovery_recommendations"].append("清理磁碟空間")
            
            if health.get("cpu_percent", 0) > 80:
                recovery_status["recovery_recommendations"].append("降低CPU負載")
            
            return recovery_status
        
        return {"can_recover": True, "system_running": True}

# 全域停機管理器實例
shutdown_manager = ShutdownManager()

async def main():
    """測試函數"""
    logger.info("測試系統停機管理器")
    
    # 測試系統健康檢查
    health = shutdown_manager.system_monitor.check_system_health()
    logger.info(f"系統健康狀況: {json.dumps(health, ensure_ascii=False, indent=2)}")
    
    # 測試停機狀態
    status = shutdown_manager.get_shutdown_status()
    logger.info(f"停機狀態: {json.dumps(status, ensure_ascii=False, indent=2)}")
    
    # 測試恢復檢查
    recovery = await shutdown_manager.recovery_check()
    logger.info(f"恢復檢查: {json.dumps(recovery, ensure_ascii=False, indent=2)}")
    
    logger.info("系統停機管理器測試完成")

if __name__ == "__main__":
    asyncio.run(main())
