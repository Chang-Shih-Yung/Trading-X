#!/usr/bin/env python3
"""
🛡️ Trading X - JSON配置安全管理器 (生產版本)
確保原始配置永不被破壞的安全機制

實施階段1：立即部署的安全機制
"""

import json
import shutil
import logging
import asyncio
from pathlib import Path
import datetime
from typing import Dict, Any, Optional
import hashlib

logger = logging.getLogger(__name__)

class Phase1AConfigSafetyManager:
    """
    Phase1A配置安全管理器 - 生產版本
    
    核心功能：
    1. 原始配置永久保護
    2. 自動備份與恢復
    3. 完整性驗證
    4. 安全的參數更新
    5. 備份清理機制
    """
    
    def __init__(self, config_path: str):
        """初始化安全管理器"""
        self.config_path = Path(config_path)
        self.original_backup_dir = Path("safety_backups/original")
        self.working_backup_dir = Path("safety_backups/working")
        self.original_backup_path = self.original_backup_dir / "phase1a_basic_signal_generation_ORIGINAL.json"
        
        # 備份清理配置
        self.backup_retention = {
            "max_backups": 10,      # 最多保留10個工作備份
            "max_age_days": 7,      # 超過7天的備份會被清理
            "cleanup_on_deploy": True  # 部署時自動清理
        }
        
        # 安全狀態追踪
        self.safety_state = {
            "is_deployed": False,
            "original_hash": None,
            "modification_count": 0,
            "last_verification": None,
            "integrity_confirmed": False
        }
    
    async def deploy_safety_system(self) -> Dict[str, Any]:
        """部署安全系統"""
        try:
            logger.info("🚀 部署Phase1A安全系統...")
            
            deployment_actions = []
            
            # Step 1: 創建安全備份目錄
            self.original_backup_dir.mkdir(parents=True, exist_ok=True)
            self.working_backup_dir.mkdir(parents=True, exist_ok=True)
            deployment_actions.append("created_directories")
            
            # Step 2: 創建原始配置的永久備份
            if not self.original_backup_path.exists():
                shutil.copy2(self.config_path, self.original_backup_path)
                deployment_actions.append("created_original_backup")
                logger.info(f"✅ 原始配置已安全備份: {self.original_backup_path}")
            
            # Step 3: 計算原始配置指紋
            self.safety_state["original_hash"] = await self._calculate_file_hash(self.config_path)
            deployment_actions.append("calculated_hash")
            
            # Step 4: 驗證配置完整性
            integrity_check = await self._verify_json_integrity()
            if not integrity_check["valid"]:
                raise Exception(f"配置完整性檢查失敗: {integrity_check['error']}")
            deployment_actions.append("verified_integrity")
            
            # Step 5: 初始工作備份
            await self._create_safety_backup("deployment_initial")
            deployment_actions.append("created_initial_backup")
            
            # Step 6: 清理舊備份（如果啟用）
            if self.backup_retention["cleanup_on_deploy"]:
                cleanup_result = await self._cleanup_old_backups()
                if cleanup_result["cleaned_count"] > 0:
                    deployment_actions.append(f"cleaned_{cleanup_result['cleaned_count']}_old_backups")
            
            # 標記為已部署
            self.safety_state["is_deployed"] = True
            self.safety_state["last_verification"] = datetime.datetime.now().isoformat()
            self.safety_state["integrity_confirmed"] = True
            
            # 返回部署結果
            config_stats = await self._get_config_stats()
            
            return {
                "status": "success",
                "message": "Phase1A安全系統部署完成",
                "actions_performed": deployment_actions,
                "original_config_fingerprint": self.safety_state["original_hash"][:12],
                "config_size": f"{config_stats['size']:.2f}KB",
                "deployment_timestamp": self.safety_state["last_verification"]
            }
            
        except Exception as e:
            logger.error(f"❌ 安全系統部署失敗: {e}")
            return {
                "status": "error",
                "message": f"部署失敗: {str(e)}",
                "actions_performed": deployment_actions
            }
    
    async def safe_parameter_update(self, parameter_updates: Dict[str, Any], 
                                   backup_label: str = None) -> Dict[str, Any]:
        """安全的參數更新"""
        try:
            if not self.safety_state["is_deployed"]:
                raise Exception("安全系統尚未部署，請先執行 deploy_safety_system()")
            
            logger.info(f"🔧 開始安全參數更新: {len(parameter_updates)} 個參數")
            
            # 增加修改計數器
            self.safety_state["modification_count"] += 1
            
            update_result = {
                "status": "success",
                "updated_parameters": [],
                "locations_updated": {},
                "modification_count": self.safety_state["modification_count"]
            }
            
            # Step 3: 創建修改前備份
            backup_result = await self._create_safety_backup(f"before_update_{self.safety_state['modification_count']}")
            update_result["backup_created"] = backup_result["success"]
            
            # Step 3.1: 適時清理舊備份
            if self.safety_state["modification_count"] % 5 == 0:  # 每5次修改清理一次
                cleanup_result = await self._cleanup_old_backups()
                if cleanup_result["cleaned_count"] > 0:
                    update_result["backups_cleaned"] = cleanup_result["cleaned_count"]
            
            # Step 4: 載入配置
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Step 5: 安全更新參數
            for param_name, new_value in parameter_updates.items():
                logger.info(f"  更新參數: {param_name} = {new_value}")
                locations = await self._update_parameter_recursive(config, param_name, new_value)
                update_result["locations_updated"][param_name] = locations
                update_result["updated_parameters"].append({
                    "name": param_name,
                    "value": new_value,
                    "locations_count": len(locations)
                })
            
            # Step 6: 保存配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Step 7: 驗證更新
            verification = await self._verify_json_integrity()
            if not verification["valid"]:
                # 自動恢復
                await self.emergency_restore()
                raise Exception(f"更新後驗證失敗，已自動恢復: {verification['error']}")
            
            update_result["verification_passed"] = True
            logger.info(f"✅ 參數更新完成: {len(parameter_updates)} 個參數")
            
            return update_result
            
        except Exception as e:
            logger.error(f"❌ 參數更新失敗: {e}")
            # 嘗試緊急恢復
            restore_result = await self.emergency_restore()
            return {
                "status": "error",
                "message": f"更新失敗: {str(e)}",
                "emergency_restore": restore_result
            }
    
    async def emergency_restore(self) -> Dict[str, Any]:
        """緊急恢復到原始配置"""
        try:
            logger.warning("🚨 執行緊急恢復...")
            
            if not self.original_backup_path.exists():
                raise Exception("原始備份不存在，無法恢復")
            
            # 恢復原始配置
            shutil.copy2(self.original_backup_path, self.config_path)
            
            # 重置安全狀態
            self.safety_state["modification_count"] = 0
            self.safety_state["last_verification"] = datetime.datetime.now().isoformat()
            
            # 驗證恢復
            verification = await self._verify_json_integrity()
            
            return {
                "status": "success",
                "message": "緊急恢復完成",
                "restored_from": str(self.original_backup_path),
                "verification_passed": verification["valid"],
                "timestamp": datetime.datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"❌ 緊急恢復失敗: {e}")
            return {
                "status": "critical_error",
                "message": f"緊急恢復失敗: {str(e)}"
            }
    
    async def _cleanup_old_backups(self) -> Dict[str, Any]:
        """清理舊的備份檔案"""
        try:
            logger.info("🧹 清理舊備份檔案...")
            
            if not self.working_backup_dir.exists():
                return {"cleaned_count": 0, "status": "no_backups"}
            
            backup_files = list(self.working_backup_dir.glob("*.json"))
            if not backup_files:
                return {"cleaned_count": 0, "status": "no_backups"}
            
            # 按修改時間排序（最新的在前）
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            cleaned_count = 0
            current_time = datetime.datetime.now()
            
            # 清理策略1: 保留最新的N個備份
            if len(backup_files) > self.backup_retention["max_backups"]:
                excess_files = backup_files[self.backup_retention["max_backups"]:]
                for file_path in excess_files:
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                        logger.info(f"  已清理多餘備份: {file_path.name}")
                    except Exception as e:
                        logger.warning(f"  清理檔案失敗 {file_path.name}: {e}")
            
            # 清理策略2: 清理超過時間限制的備份
            remaining_files = backup_files[:self.backup_retention["max_backups"]]
            for file_path in remaining_files:
                try:
                    file_time = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                    age_days = (current_time - file_time).days
                    
                    if age_days > self.backup_retention["max_age_days"]:
                        file_path.unlink()
                        cleaned_count += 1
                        logger.info(f"  已清理過期備份: {file_path.name} (存在{age_days}天)")
                except Exception as e:
                    logger.warning(f"  清理檔案失敗 {file_path.name}: {e}")
            
            logger.info(f"✅ 備份清理完成，共清理 {cleaned_count} 個檔案")
            
            return {
                "cleaned_count": cleaned_count,
                "status": "success",
                "retention_policy": self.backup_retention
            }
            
        except Exception as e:
            logger.error(f"❌ 備份清理失敗: {e}")
            return {
                "cleaned_count": 0,
                "status": "error",
                "error": str(e)
            }
    
    async def _create_safety_backup(self, label: str) -> Dict[str, Any]:
        """創建安全備份"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"phase1a_backup_{label}_{timestamp}.json"
            backup_path = self.working_backup_dir / backup_filename
            
            shutil.copy2(self.config_path, backup_path)
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"❌ 創建備份失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _verify_json_integrity(self) -> Dict[str, Any]:
        """驗證JSON配置完整性"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                json.load(f)
            
            self.safety_state["last_verification"] = datetime.datetime.now().isoformat()
            
            return {
                "valid": True,
                "verification_time": self.safety_state["last_verification"]
            }
            
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": f"JSON語法錯誤: {str(e)}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"檔案讀取錯誤: {str(e)}"
            }
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """計算檔案哈希值"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    async def _get_config_stats(self) -> Dict[str, Any]:
        """獲取配置檔案統計信息"""
        stats = self.config_path.stat()
        return {
            "size": stats.st_size / 1024,  # KB
            "modified": datetime.datetime.fromtimestamp(stats.st_mtime).isoformat()
        }
    
    async def _update_parameter_recursive(self, obj: Any, param_name: str, new_value: Any, 
                                         current_path: str = "", locations: list = None) -> list:
        """遞歸更新參數，支援新增參數"""
        if locations is None:
            locations = []
        
        if isinstance(obj, dict):
            # 檢查是否需要新增參數到根層級
            if current_path == "" and param_name not in obj:
                obj[param_name] = new_value
                locations.append(param_name)
                logger.info(f"    ✅ 新增參數: {param_name} = {new_value}")
                return locations
            
            for key, value in obj.items():
                new_path = f"{current_path}.{key}" if current_path else key
                
                if key == param_name:
                    obj[key] = new_value
                    locations.append(new_path)
                    logger.info(f"    ✅ 更新位置: {new_path} = {new_value}")
                else:
                    await self._update_parameter_recursive(value, param_name, new_value, new_path, locations)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{current_path}[{i}]"
                await self._update_parameter_recursive(item, param_name, new_value, new_path, locations)
        
        return locations
    
    async def get_safety_status(self) -> Dict[str, Any]:
        """獲取安全狀態報告"""
        try:
            # 統計備份檔案
            backup_count = len(list(self.working_backup_dir.glob("*.json"))) if self.working_backup_dir.exists() else 0
            
            # 驗證原始備份
            original_exists = self.original_backup_path.exists()
            
            # 當前配置哈希
            current_hash = await self._calculate_file_hash(self.config_path)
            
            # 完整性檢查
            integrity_check = await self._verify_json_integrity()
            
            return {
                "safety_deployed": self.safety_state["is_deployed"],
                "original_backup_exists": original_exists,
                "current_config_hash": current_hash[:12],
                "original_config_hash": self.safety_state["original_hash"][:12] if self.safety_state["original_hash"] else None,
                "config_modified": current_hash != self.safety_state["original_hash"],
                "modification_count": self.safety_state["modification_count"],
                "working_backups_count": backup_count,
                "last_verification": self.safety_state["last_verification"],
                "integrity_confirmed": integrity_check["valid"],
                "backup_retention_policy": self.backup_retention
            }
            
        except Exception as e:
            return {
                "error": f"狀態檢查失敗: {str(e)}"
            }


async def main():
    """主程序 - 部署安全系統"""
    # 配置路徑
    config_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/phase1a_basic_signal_generation/phase1a_basic_signal_generation.json"
    
    # 創建安全管理器
    safety_manager = Phase1AConfigSafetyManager(config_path)
    
    print("🛡️ Trading X - Phase1A 安全管理器")
    print("=" * 50)
    
    # 部署安全系統
    print("\n📋 部署安全系統...")
    result = await safety_manager.deploy_safety_system()
    
    if result["status"] == "success":
        print(f"✅ {result['message']}")
        print(f"   執行動作: {len(result['actions_performed'])} 個")
        print(f"   原始配置指紋: {result['original_config_fingerprint']}")
        print(f"   配置檔案大小: {result['config_size']}")
        
        # 顯示安全狀態
        print("\n📊 安全狀態報告:")
        status = await safety_manager.get_safety_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
        
    else:
        print(f"❌ {result['message']}")


if __name__ == "__main__":
    asyncio.run(main())
