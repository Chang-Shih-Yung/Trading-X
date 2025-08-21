#!/usr/bin/env python3
"""
數據流衝突保護增強系統
加強fcntl文件鎖定機制，實施跨Phase事務協調
"""

import asyncio
import fcntl
import json
import time
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from contextlib import asynccontextmanager
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFlowProtectionManager:
    """數據流保護管理器"""
    
    def __init__(self):
        # 修正為動態路徑
        self.base_dir = Path(__file__).parent.parent.parent
        self.lock_dir = self.base_dir / "data" / "locks"
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        
        # 鎖定超時設置
        self.lock_timeout = 30  # 30秒超時
        self.retry_interval = 0.1  # 重試間隔
        
        # 事務日誌
        self.transaction_log = self.base_dir / "logs" / "transactions.json"
        self.transaction_log.parent.mkdir(exist_ok=True)
        
        # 衝突記錄
        self.conflict_log = self.base_dir / "logs" / "conflicts.json"
        
        # Phase協調檔案
        self.phase_coordination_file = self.base_dir / "coordination" / "phase_status.json"
        self.phase_coordination_file.parent.mkdir(exist_ok=True)
        
        # 鎖定狀態追蹤
        self.active_locks = {}
        self.lock_history = []
    
    def _generate_lock_id(self, resource: str, operation: str) -> str:
        """生成鎖定ID"""
        timestamp = str(int(time.time() * 1000))
        content = f"{resource}_{operation}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _get_lock_file_path(self, resource: str) -> Path:
        """獲取鎖定檔案路徑"""
        safe_name = resource.replace("/", "_").replace("\\", "_")
        return self.locks_dir / f"{safe_name}.lock"
    
    @asynccontextmanager
    async def enhanced_file_lock(self, 
                                file_path: str, 
                                operation: str = "write",
                                phase: str = "unknown"):
        """增強的檔案鎖定上下文管理器"""
        
        lock_id = self._generate_lock_id(file_path, operation)
        lock_file_path = self._get_lock_file_path(file_path)
        lock_acquired = False
        lock_file = None
        
        try:
            # 記錄鎖定嘗試
            lock_attempt = {
                "lock_id": lock_id,
                "file_path": file_path,
                "operation": operation,
                "phase": phase,
                "attempt_time": datetime.now().isoformat(),
                "status": "attempting"
            }
            
            self.active_locks[lock_id] = lock_attempt
            
            # 嘗試獲取鎖定
            start_time = time.time()
            while time.time() - start_time < self.lock_timeout:
                try:
                    lock_file = open(lock_file_path, 'w+')
                    
                    # 根據操作類型選擇鎖定模式
                    if operation == "read":
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
                    else:  # write, update, delete
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    
                    lock_acquired = True
                    
                    # 寫入鎖定資訊
                    lock_info = {
                        "lock_id": lock_id,
                        "file_path": file_path,
                        "operation": operation,
                        "phase": phase,
                        "locked_at": datetime.now().isoformat(),
                        "process_id": os.getpid()
                    }
                    lock_file.write(json.dumps(lock_info, indent=2))
                    lock_file.flush()
                    
                    # 更新狀態
                    self.active_locks[lock_id]["status"] = "acquired"
                    self.active_locks[lock_id]["acquired_time"] = datetime.now().isoformat()
                    
                    logger.info(f"獲取鎖定成功: {lock_id} - {file_path} ({operation})")
                    break
                    
                except (IOError, OSError) as e:
                    if lock_file:
                        lock_file.close()
                        lock_file = None
                    
                    # 記錄衝突
                    await self._log_conflict(lock_id, file_path, operation, phase, str(e))
                    await asyncio.sleep(self.retry_interval)
            
            if not lock_acquired:
                raise TimeoutError(f"無法在 {self.lock_timeout} 秒內獲取鎖定: {file_path}")
            
            # 讓出控制權，允許受保護的操作執行
            yield lock_id
            
        except Exception as e:
            self.active_locks[lock_id]["status"] = "failed"
            self.active_locks[lock_id]["error"] = str(e)
            logger.error(f"檔案鎖定失敗: {lock_id} - {e}")
            raise
        
        finally:
            # 釋放鎖定
            if lock_acquired and lock_file:
                try:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    lock_file.close()
                    
                    # 清理鎖定檔案
                    if lock_file_path.exists():
                        lock_file_path.unlink()
                    
                    self.active_locks[lock_id]["status"] = "released"
                    self.active_locks[lock_id]["released_time"] = datetime.now().isoformat()
                    
                    logger.info(f"釋放鎖定: {lock_id}")
                    
                except Exception as e:
                    logger.error(f"釋放鎖定失敗: {lock_id} - {e}")
            
            # 移至歷史記錄
            if lock_id in self.active_locks:
                self.lock_history.append(self.active_locks[lock_id])
                del self.active_locks[lock_id]
                
                # 保留最近1000個記錄
                if len(self.lock_history) > 1000:
                    self.lock_history = self.lock_history[-1000:]
    
    async def _log_conflict(self, lock_id: str, file_path: str, operation: str, phase: str, error: str):
        """記錄衝突事件"""
        try:
            conflicts = []
            if self.conflict_log.exists():
                with open(self.conflict_log, 'r', encoding='utf-8') as f:
                    conflicts = json.load(f)
            
            conflict = {
                "conflict_id": f"conflict_{int(time.time())}",
                "lock_id": lock_id,
                "file_path": file_path,
                "operation": operation,
                "phase": phase,
                "error": error,
                "timestamp": datetime.now().isoformat(),
                "active_locks_count": len(self.active_locks)
            }
            
            conflicts.append(conflict)
            
            # 保留最近100個衝突記錄
            if len(conflicts) > 100:
                conflicts = conflicts[-100:]
            
            with open(self.conflict_log, 'w', encoding='utf-8') as f:
                json.dump(conflicts, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"記錄衝突失敗: {e}")
    
    async def coordinate_phase_access(self, 
                                    phase: str, 
                                    operation: str,
                                    resources: List[str]) -> bool:
        """協調Phase存取"""
        
        coordination_lock_path = str(self.phase_coordination_file)
        
        async with self.enhanced_file_lock(coordination_lock_path, "write", phase):
            try:
                # 讀取當前Phase狀態
                current_status = {}
                if self.phase_coordination_file.exists():
                    with open(self.phase_coordination_file, 'r', encoding='utf-8') as f:
                        current_status = json.load(f)
                
                # 檢查是否可以執行操作
                can_proceed = self._check_phase_conflicts(phase, operation, resources, current_status)
                
                if can_proceed:
                    # 更新Phase狀態
                    if phase not in current_status:
                        current_status[phase] = {}
                    
                    current_status[phase].update({
                        "operation": operation,
                        "resources": resources,
                        "started_at": datetime.now().isoformat(),
                        "status": "active"
                    })
                    
                    # 寫回狀態檔案
                    with open(self.phase_coordination_file, 'w', encoding='utf-8') as f:
                        json.dump(current_status, f, ensure_ascii=False, indent=2)
                
                return can_proceed
                
            except Exception as e:
                logger.error(f"Phase協調失敗: {e}")
                return False
    
    def _check_phase_conflicts(self, 
                              phase: str, 
                              operation: str, 
                              resources: List[str], 
                              current_status: Dict) -> bool:
        """檢查Phase衝突"""
        
        # Phase優先級 (數字越小優先級越高)
        phase_priorities = {
            "phase1a": 1,
            "phase2": 2,
            "phase3": 3,
            "phase5": 4
        }
        
        current_priority = phase_priorities.get(phase.lower(), 99)
        
        for active_phase, phase_info in current_status.items():
            if phase_info.get("status") != "active":
                continue
            
            active_priority = phase_priorities.get(active_phase.lower(), 99)
            active_resources = phase_info.get("resources", [])
            
            # 檢查資源衝突
            resource_conflict = bool(set(resources) & set(active_resources))
            
            if resource_conflict:
                # 如果當前Phase優先級更高，允許執行
                if current_priority < active_priority:
                    logger.warning(f"{phase} 搶佔 {active_phase} 的資源: {list(set(resources) & set(active_resources))}")
                    return True
                else:
                    logger.info(f"{phase} 等待 {active_phase} 完成")
                    return False
        
        return True
    
    async def complete_phase_operation(self, phase: str):
        """完成Phase操作"""
        coordination_lock_path = str(self.phase_coordination_file)
        
        async with self.enhanced_file_lock(coordination_lock_path, "write", phase):
            try:
                if self.phase_coordination_file.exists():
                    with open(self.phase_coordination_file, 'r', encoding='utf-8') as f:
                        current_status = json.load(f)
                    
                    if phase in current_status:
                        current_status[phase]["status"] = "completed"
                        current_status[phase]["completed_at"] = datetime.now().isoformat()
                    
                    with open(self.phase_coordination_file, 'w', encoding='utf-8') as f:
                        json.dump(current_status, f, ensure_ascii=False, indent=2)
                
            except Exception as e:
                logger.error(f"完成Phase操作失敗: {e}")
    
    def get_protection_status(self) -> Dict[str, Any]:
        """獲取保護狀態"""
        return {
            "active_locks": len(self.active_locks),
            "active_lock_details": list(self.active_locks.values()),
            "recent_conflicts": len([h for h in self.lock_history if h.get("status") == "failed"]),
            "total_lock_operations": len(self.lock_history),
            "protection_enabled": True,
            "last_update": datetime.now().isoformat()
        }

async def test_data_flow_protection():
    """測試數據流保護系統"""
    print("🔒 測試數據流衝突保護增強系統...")
    
    manager = DataFlowProtectionManager()
    
    # 測試1: 基本檔案鎖定
    print("\n📝 測試基本檔案鎖定:")
    base_dir = Path(__file__).parent.parent.parent
    test_file = base_dir / "test_lock_file.json"
    
    try:
        async with manager.enhanced_file_lock(test_file, "write", "phase2") as lock_id:
            print(f"   獲取鎖定成功: {lock_id}")
            
            # 模擬檔案操作
            with open(test_file, 'w') as f:
                json.dump({"test": "data", "timestamp": datetime.now().isoformat()}, f)
            
            await asyncio.sleep(0.1)  # 模擬處理時間
        
        print(f"   鎖定釋放成功")
        
    except Exception as e:
        print(f"   鎖定測試失敗: {e}")
    
    # 測試2: Phase協調
    print(f"\n🔄 測試Phase協調:")
    
    resources = ["parameter_file.json", "signal_data.json"]
    
    # 模擬Phase2操作
    phase2_can_proceed = await manager.coordinate_phase_access("phase2", "parameter_update", resources)
    print(f"   Phase2 可以執行: {phase2_can_proceed}")
    
    if phase2_can_proceed:
        await asyncio.sleep(0.1)  # 模擬操作
        await manager.complete_phase_operation("phase2")
        print(f"   Phase2 操作完成")
    
    # 模擬Phase5操作
    phase5_can_proceed = await manager.coordinate_phase_access("phase5", "backtest_validation", resources)
    print(f"   Phase5 可以執行: {phase5_can_proceed}")
    
    # 測試3: 並發鎖定衝突
    print(f"\n⚡ 測試並發鎖定衝突:")
    
    async def concurrent_operation(phase_name: str, delay: float):
        try:
            await asyncio.sleep(delay)
            async with manager.enhanced_file_lock(test_file, "write", phase_name) as lock_id:
                print(f"   {phase_name} 獲取鎖定: {lock_id}")
                await asyncio.sleep(0.2)
                return True
        except Exception as e:
            print(f"   {phase_name} 鎖定失敗: {e}")
            return False
    
    # 同時啟動多個操作
    tasks = [
        concurrent_operation("phase1a", 0),
        concurrent_operation("phase2", 0.05),
        concurrent_operation("phase3", 0.1)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    successful_operations = sum(1 for r in results if r is True)
    print(f"   成功操作數: {successful_operations}/3")
    
    # 顯示保護狀態
    print(f"\n📊 保護狀態:")
    status = manager.get_protection_status()
    print(f"   活躍鎖定: {status['active_locks']}")
    print(f"   總操作數: {status['total_lock_operations']}")
    print(f"   衝突次數: {status['recent_conflicts']}")
    
    # 清理測試檔案
    if Path(test_file).exists():
        Path(test_file).unlink()
    
    print(f"\n✅ 數據流保護系統測試完成")
    return status

if __name__ == "__main__":
    asyncio.run(test_data_flow_protection())
