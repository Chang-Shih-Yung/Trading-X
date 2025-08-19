#!/usr/bin/env python3
"""
🔄 Phase2 參數輸出管理器
實現類似 Phase5 的 JSON 配置輸出機制
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class ParameterGenerationMetrics:
    """參數生成指標"""
    generation_time: datetime
    trigger_type: str  # "time_based" | "signal_based" | "performance_based"
    signal_count_since_last: int
    hours_since_last: float
    performance_improvement: float
    learning_confidence: float
    market_regime: str

@dataclass
class ParameterConflictResolution:
    """參數衝突解決記錄"""
    parameter_name: str
    phase2_value: float
    phase5_value: float
    fusion_weight: float
    final_value: float
    resolution_method: str
    confidence_score: float

class Phase2ParameterManager:
    """Phase2 參數管理器 - 類似 Phase5 的配置輸出機制"""
    
    def __init__(self, config_path: str = None):
        """初始化參數管理器"""
        self.config_path = Path(config_path) if config_path else Path(__file__).parent / "config" / "phase2_parameter_config.json"
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # 載入配置
        self.config = self._load_config()
        
        # 狀態追蹤
        self.last_generation_time = None
        self.signal_count_since_last = 0
        self.current_parameters = {}
        self.generation_history = []
        self.conflict_history = []
        
        # 性能監控
        self.performance_baseline = None
        self.performance_history = []
        self.rollback_stack = []
        
        logger.info("📊 Phase2 參數管理器初始化完成")
    
    def _load_config(self) -> Dict[str, Any]:
        """載入配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"✅ 載入配置: {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"❌ 配置載入失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            "generation_frequency": {
                "interval_hours": 2,
                "signal_count": 200,
                "trigger_mode": "either"
            },
            "parameter_authority": {
                "phase2_dominant": {
                    "signal_threshold": {"base_value": 0.6, "adjustment_range": [0.4, 0.8], "fusion_weight": 0.8},
                    "momentum_weight": {"base_value": 1.0, "adjustment_range": [0.5, 2.0], "fusion_weight": 0.8},
                    "volatility_adjustment": {"base_value": 1.0, "adjustment_range": [0.3, 2.5], "fusion_weight": 0.8}
                }
            },
            "performance_monitoring": {
                "rollback_threshold": {"performance_drop_percent": 15},
                "warning_threshold": {"performance_drop_percent": 8}
            }
        }
    
    def should_generate_new_parameters(self) -> tuple[bool, str]:
        """檢查是否應該生成新參數"""
        try:
            freq_config = self.config.get("generation_frequency", {})
            
            # 時間條件
            time_trigger = False
            if self.last_generation_time:
                interval_hours = freq_config.get("interval_hours", 2)
                hours_since = (datetime.now() - self.last_generation_time).total_seconds() / 3600
                time_trigger = hours_since >= interval_hours
            else:
                time_trigger = True  # 首次生成
            
            # 信號數量條件
            signal_count_threshold = freq_config.get("signal_count", 200)
            signal_trigger = self.signal_count_since_last >= signal_count_threshold
            
            # 觸發模式
            trigger_mode = freq_config.get("trigger_mode", "either")
            
            if trigger_mode == "either":
                should_trigger = time_trigger or signal_trigger
            elif trigger_mode == "both":
                should_trigger = time_trigger and signal_trigger
            else:
                should_trigger = time_trigger
            
            # 確定觸發原因
            if should_trigger:
                if time_trigger and signal_trigger:
                    reason = "time_and_signal"
                elif time_trigger:
                    reason = "time_based"
                else:
                    reason = "signal_based"
            else:
                reason = "no_trigger"
            
            return should_trigger, reason
            
        except Exception as e:
            logger.error(f"❌ 參數生成檢查失敗: {e}")
            return False, "error"
    
    async def generate_optimized_parameters(self, learning_engine, market_detector) -> Optional[Dict[str, Any]]:
        """生成優化參數 - 核心邏輯"""
        try:
            logger.info("🔄 開始生成 Phase2 優化參數...")
            
            # 檢查是否應該生成
            should_generate, trigger_reason = self.should_generate_new_parameters()
            if not should_generate:
                logger.debug(f"⏭️ 跳過參數生成: {trigger_reason}")
                return None
            
            # 獲取當前市場狀態
            try:
                if market_detector and hasattr(market_detector, 'detect_current_regime'):
                    market_regime = await market_detector.detect_current_regime()
                else:
                    market_regime = "NORMAL"  # 默認市場狀態
            except Exception as e:
                logger.warning(f"⚠️ 市場狀態檢測失敗: {e}，使用默認狀態")
                market_regime = "NORMAL"
            
            # 獲取學習引擎的優化參數
            try:
                if learning_engine and hasattr(learning_engine, 'get_optimized_parameters_async'):
                    phase2_parameters = await learning_engine.get_optimized_parameters_async()
                elif learning_engine and hasattr(learning_engine, 'get_optimized_parameters'):
                    phase2_parameters = learning_engine.get_optimized_parameters()
                else:
                    # 使用默認參數
                    phase2_parameters = {
                        'signal_threshold': 0.6,
                        'momentum_weight': 1.0,
                        'volatility_adjustment': 1.0,
                        'trend_sensitivity': 1.0,
                        'volume_weight': 0.8,
                        'risk_multiplier': 1.0
                    }
                    logger.warning("⚠️ 使用默認 Phase2 參數")
            except Exception as e:
                logger.error(f"❌ 獲取學習參數失敗: {e}")
                return None
            
            # 載入 Phase5 參數（如果存在）
            phase5_parameters = await self._load_phase5_parameters()
            
            # 參數融合
            fused_parameters = await self._fuse_parameters(phase2_parameters, phase5_parameters)
            
            # 驗證參數合理性
            validated_parameters = self._validate_parameters(fused_parameters)
            
            # 生成輸出文件
            output_file = await self._save_parameter_file(validated_parameters, trigger_reason, market_regime)
            
            # 更新狀態
            self._update_generation_state(trigger_reason, market_regime)
            
            logger.info(f"✅ 參數生成完成: {output_file}")
            return validated_parameters
            
        except Exception as e:
            logger.error(f"❌ 參數生成失敗: {e}")
            return None
    
    async def _load_phase5_parameters(self) -> Dict[str, Any]:
        """載入 Phase5 參數"""
        try:
            # 尋找最新的 Phase5 配置文件
            phase5_dir = Path(__file__).parent.parent.parent / "phase5_backtesting" / "output"
            if not phase5_dir.exists():
                logger.warning("⚠️ Phase5 輸出目錄不存在")
                return {}
            
            # 獲取最新文件
            phase5_files = list(phase5_dir.glob("optimized_config_*.json"))
            if not phase5_files:
                logger.warning("⚠️ 未找到 Phase5 配置文件")
                return {}
            
            latest_file = max(phase5_files, key=lambda f: f.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                phase5_config = json.load(f)
            
            logger.info(f"📁 載入 Phase5 參數: {latest_file.name}")
            return phase5_config.get("parameters", {})
            
        except Exception as e:
            logger.error(f"❌ 載入 Phase5 參數失敗: {e}")
            return {}
    
    async def _fuse_parameters(self, phase2_params: Dict, phase5_params: Dict) -> Dict[str, Any]:
        """融合 Phase2 和 Phase5 參數"""
        fused_params = {}
        conflict_resolutions = []
        
        authority_config = self.config["parameter_authority"]
        
        # 處理 Phase2 主導參數
        for param_name, param_config in authority_config.get("phase2_dominant", {}).items():
            phase2_value = phase2_params.get(param_name, param_config["base_value"])
            phase5_value = phase5_params.get(param_name, param_config["base_value"])
            fusion_weight = param_config["fusion_weight"]
            
            # 加權平均
            final_value = phase2_value * fusion_weight + phase5_value * (1 - fusion_weight)
            
            # 範圍檢查
            value_range = param_config["adjustment_range"]
            final_value = np.clip(final_value, value_range[0], value_range[1])
            
            fused_params[param_name] = final_value
            
            # 記錄衝突解決
            if abs(phase2_value - phase5_value) > 0.1:  # 有顯著差異
                conflict_resolutions.append(ParameterConflictResolution(
                    parameter_name=param_name,
                    phase2_value=phase2_value,
                    phase5_value=phase5_value,
                    fusion_weight=fusion_weight,
                    final_value=final_value,
                    resolution_method="weighted_average",
                    confidence_score=fusion_weight
                ))
        
        # 處理 Phase5 主導參數
        for param_name, param_config in authority_config.get("phase5_dominant", {}).items():
            phase2_value = phase2_params.get(param_name, param_config["base_value"])
            phase5_value = phase5_params.get(param_name, param_config["base_value"])
            fusion_weight = param_config["fusion_weight"]  # Phase2 的權重
            
            # Phase5 主導，所以 Phase5 權重更高
            final_value = phase2_value * fusion_weight + phase5_value * (1 - fusion_weight)
            
            value_range = param_config["adjustment_range"]
            final_value = np.clip(final_value, value_range[0], value_range[1])
            
            fused_params[param_name] = final_value
        
        # 處理平衡參數
        for param_name, param_config in authority_config.get("balanced", {}).items():
            phase2_value = phase2_params.get(param_name, param_config["base_value"])
            phase5_value = phase5_params.get(param_name, param_config["base_value"])
            
            # 50-50 平衡
            final_value = (phase2_value + phase5_value) / 2
            
            value_range = param_config["adjustment_range"]
            final_value = np.clip(final_value, value_range[0], value_range[1])
            
            fused_params[param_name] = final_value
        
        # 保存衝突解決記錄
        self.conflict_history.extend(conflict_resolutions)
        
        if conflict_resolutions:
            logger.info(f"⚖️ 解決 {len(conflict_resolutions)} 個參數衝突")
        
        return fused_params
    
    def _validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """驗證參數合理性"""
        validated = {}
        authority_config = self.config["parameter_authority"]
        
        # 收集所有參數配置
        all_param_configs = {}
        for category in ["phase2_dominant", "phase5_dominant", "balanced"]:
            all_param_configs.update(authority_config.get(category, {}))
        
        for param_name, value in parameters.items():
            if param_name in all_param_configs:
                param_config = all_param_configs[param_name]
                value_range = param_config["adjustment_range"]
                
                # 範圍驗證
                validated_value = np.clip(value, value_range[0], value_range[1])
                
                # 類型驗證
                if isinstance(param_config["base_value"], int):
                    validated_value = int(validated_value)
                else:
                    validated_value = float(validated_value)
                
                validated[param_name] = validated_value
                
                if validated_value != value:
                    logger.warning(f"⚠️ 參數 {param_name} 被調整: {value:.4f} -> {validated_value:.4f}")
            else:
                # 未知參數保持原值
                validated[param_name] = value
        
        return validated
    
    async def _save_parameter_file(self, parameters: Dict, trigger_reason: str, market_regime: str) -> str:
        """保存參數文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"phase2_optimized_params_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # 生成指標
        metrics = ParameterGenerationMetrics(
            generation_time=datetime.now(),
            trigger_type=trigger_reason,
            signal_count_since_last=self.signal_count_since_last,
            hours_since_last=self._get_hours_since_last(),
            performance_improvement=self._calculate_performance_improvement(),
            learning_confidence=0.75,  # 暫時固定，後續可以從學習引擎獲取
            market_regime=market_regime
        )
        
        # 構建輸出數據
        output_data = {
            "version": "2.0.0",
            "generation_time": timestamp,
            "config_name": "Phase2 自適應優化參數",
            "description": "Phase2 學習引擎生成的優化參數",
            "parameters": parameters,
            "generation_metrics": asdict(metrics),
            "conflict_resolutions": [asdict(cr) for cr in self.conflict_history[-10:]],  # 最近10個衝突
            "validation_status": {
                "validated": True,
                "parameter_count": len(parameters),
                "range_violations": 0
            },
            "integration_info": {
                "phase1a_compatible": True,
                "phase5_conflicts_resolved": len(self.conflict_history),
                "recommended_validation_signals": 50
            }
        }
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"💾 參數文件已保存: {filename}")
        
        # 清理舊文件
        await self._cleanup_old_files()
        
        return str(filepath)
    
    def _get_hours_since_last(self) -> float:
        """獲取距離上次生成的小時數"""
        if self.last_generation_time:
            return (datetime.now() - self.last_generation_time).total_seconds() / 3600
        return 0.0
    
    def _calculate_performance_improvement(self) -> float:
        """計算性能改善"""
        if len(self.performance_history) < 2:
            return 0.0
        
        current = self.performance_history[-1]
        previous = self.performance_history[-2]
        
        return (current - previous) / previous * 100 if previous != 0 else 0.0
    
    def _update_generation_state(self, trigger_reason: str, market_regime: str):
        """更新生成狀態"""
        self.last_generation_time = datetime.now()
        self.signal_count_since_last = 0
        
        # 記錄生成歷史
        self.generation_history.append({
            "timestamp": datetime.now(),
            "trigger_reason": trigger_reason,
            "market_regime": market_regime
        })
        
        # 保持歷史記錄在合理範圍內
        if len(self.generation_history) > 100:
            self.generation_history = self.generation_history[-50:]
    
    async def _cleanup_old_files(self):
        """清理舊的參數文件"""
        try:
            retention_hours = self.config.get("output_schema", {}).get("backup_retention_hours", 168)
            cutoff_time = datetime.now() - timedelta(hours=retention_hours)
            
            for file in self.output_dir.glob("phase2_optimized_params_*.json"):
                if file.stat().st_mtime < cutoff_time.timestamp():
                    file.unlink()
                    logger.debug(f"🗑️ 清理舊文件: {file.name}")
        
        except Exception as e:
            logger.error(f"❌ 清理舊文件失敗: {e}")
    
    def increment_signal_count(self):
        """增加信號計數"""
        self.signal_count_since_last += 1
    
    def report_performance(self, performance_score: float):
        """報告性能分數"""
        self.performance_history.append(performance_score)
        
        # 檢查是否需要回滾
        if self._should_rollback(performance_score):
            asyncio.create_task(self._perform_rollback())
    
    def _should_rollback(self, current_performance: float) -> bool:
        """檢查是否應該回滾"""
        if not self.performance_baseline or len(self.performance_history) < 2:
            return False
        
        rollback_threshold = self.config["performance_monitoring"]["rollback_threshold"]["performance_drop_percent"]
        performance_drop = (self.performance_baseline - current_performance) / self.performance_baseline * 100
        
        return performance_drop >= rollback_threshold
    
    async def _perform_rollback(self):
        """執行參數回滾"""
        if not self.rollback_stack:
            logger.warning("⚠️ 無法回滾：沒有歷史參數")
            return
        
        previous_params = self.rollback_stack[-1]
        logger.warning(f"🔙 執行緊急回滾到: {previous_params['timestamp']}")
        
        # 創建回滾文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rollback_file = self.output_dir / f"phase2_rollback_params_{timestamp}.json"
        
        rollback_data = {
            "version": "2.0.0",
            "generation_time": timestamp,
            "config_name": "Phase2 緊急回滾參數",
            "description": "由於性能下降觸發的緊急參數回滾",
            "parameters": previous_params["parameters"],
            "rollback_info": {
                "trigger_reason": "performance_degradation",
                "rollback_timestamp": timestamp,
                "original_timestamp": previous_params["timestamp"]
            }
        }
        
        with open(rollback_file, 'w', encoding='utf-8') as f:
            json.dump(rollback_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ 回滾參數已保存: {rollback_file.name}")

# 全局實例
phase2_parameter_manager = Phase2ParameterManager()
