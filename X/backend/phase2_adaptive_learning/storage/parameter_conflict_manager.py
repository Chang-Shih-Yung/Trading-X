#!/usr/bin/env python3
"""
⚖️ Parameter Conflict Resolution Manager
參數衝突解決管理器 - 改進參數衝突記錄與處理

功能：
- 詳細記錄 Phase2 和 Phase5 參數衝突
- 衝突解決策略追蹤
- 自動回滾機制
- A/B 測試支援
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class ConflictResolutionMethod(Enum):
    """衝突解決方法"""
    WEIGHTED_AVERAGE = "weighted_average"
    PHASE2_DOMINANT = "phase2_dominant"
    PHASE5_DOMINANT = "phase5_dominant"
    A_B_TESTING = "a_b_testing"
    PERFORMANCE_BASED = "performance_based"

class ConflictSeverity(Enum):
    """衝突嚴重程度"""
    LOW = "low"           # 差異 < 10%
    MEDIUM = "medium"     # 差異 10-25%
    HIGH = "high"         # 差異 25-50%
    CRITICAL = "critical" # 差異 > 50%

@dataclass
class ParameterConflict:
    """參數衝突記錄"""
    parameter_name: str
    phase2_value: float
    phase5_value: float
    conflict_timestamp: datetime
    severity: ConflictSeverity
    resolution_method: ConflictResolutionMethod
    final_value: float
    confidence_score: float
    
    # 上下文信息
    market_conditions: Dict[str, Any]
    signal_count_context: int
    recent_performance: float
    
    # 解決結果追蹤
    resolution_success: Optional[bool] = None
    performance_impact: Optional[float] = None
    rollback_triggered: bool = False

@dataclass
class ConflictResolutionStats:
    """衝突解決統計"""
    total_conflicts: int
    resolution_success_rate: float
    most_conflicted_parameters: List[str]
    avg_resolution_time: float
    rollback_rate: float
    performance_improvement: float

class ParameterConflictManager:
    """參數衝突解決管理器"""
    
    def __init__(self):
        """初始化衝突管理器"""
        self.storage_dir = Path(__file__).parent
        self.storage_dir.mkdir(exist_ok=True)
        
        self.conflicts_file = self.storage_dir / "parameter_conflicts.json"
        self.stats_file = self.storage_dir / "conflict_resolution_stats.json"
        
        # 衝突歷史
        self.conflict_history: List[ParameterConflict] = []
        self.load_conflict_history()
        
        # 解決策略配置
        self.resolution_config = {
            'default_method': ConflictResolutionMethod.WEIGHTED_AVERAGE,
            'severity_thresholds': {
                'low': 0.10,
                'medium': 0.25,
                'high': 0.50
            },
            'performance_monitor_window': 100,  # 100 個信號
            'rollback_threshold': 0.15,  # 15% 性能下降觸發回滾
            'a_b_test_duration': 50  # A/B 測試持續 50 個信號
        }
        
        # 當前 A/B 測試
        self.active_ab_tests: Dict[str, Dict] = {}
        
        logger.info("⚖️ 參數衝突管理器初始化完成")
    
    def detect_conflict(self, parameter_name: str, phase2_value: float, 
                       phase5_value: float, context: Dict[str, Any] = None) -> ParameterConflict:
        """檢測參數衝突"""
        try:
            # 計算差異百分比
            if phase5_value != 0:
                diff_percentage = abs(phase2_value - phase5_value) / abs(phase5_value)
            else:
                diff_percentage = abs(phase2_value - phase5_value)
            
            # 確定嚴重程度
            if diff_percentage < self.resolution_config['severity_thresholds']['low']:
                severity = ConflictSeverity.LOW
            elif diff_percentage < self.resolution_config['severity_thresholds']['medium']:
                severity = ConflictSeverity.MEDIUM
            elif diff_percentage < self.resolution_config['severity_thresholds']['high']:
                severity = ConflictSeverity.HIGH
            else:
                severity = ConflictSeverity.CRITICAL
            
            # 選擇解決方法
            resolution_method = self._select_resolution_method(parameter_name, severity, context)
            
            # 計算最終值
            final_value = self._resolve_conflict_value(
                parameter_name, phase2_value, phase5_value, resolution_method, context
            )
            
            # 計算信心度
            confidence_score = self._calculate_confidence_score(
                parameter_name, severity, resolution_method, context
            )
            
            # 創建衝突記錄
            conflict = ParameterConflict(
                parameter_name=parameter_name,
                phase2_value=phase2_value,
                phase5_value=phase5_value,
                conflict_timestamp=datetime.now(),
                severity=severity,
                resolution_method=resolution_method,
                final_value=final_value,
                confidence_score=confidence_score,
                market_conditions=context.get('market_conditions', {}),
                signal_count_context=context.get('signal_count', 0),
                recent_performance=context.get('recent_performance', 0.0)
            )
            
            # 記錄衝突
            self.conflict_history.append(conflict)
            self.save_conflict_history()
            
            logger.info(f"⚖️ 檢測到 {severity.value} 級別衝突: {parameter_name}")
            logger.info(f"   Phase2: {phase2_value:.4f}, Phase5: {phase5_value:.4f}")
            logger.info(f"   解決方法: {resolution_method.value}, 最終值: {final_value:.4f}")
            
            return conflict
            
        except Exception as e:
            logger.error(f"❌ 衝突檢測失敗: {e}")
            raise
    
    def _select_resolution_method(self, parameter_name: str, severity: ConflictSeverity, 
                                 context: Dict[str, Any] = None) -> ConflictResolutionMethod:
        """選擇衝突解決方法"""
        # 根據參數類型和嚴重程度選擇方法
        if severity == ConflictSeverity.CRITICAL:
            # 嚴重衝突啟動 A/B 測試
            return ConflictResolutionMethod.A_B_TESTING
        
        # 根據參數權威性配置選擇
        phase2_dominant_params = ['signal_threshold', 'momentum_weight', 'volatility_adjustment']
        phase5_dominant_params = ['risk_multiplier', 'position_sizing_factor']
        
        if parameter_name in phase2_dominant_params:
            return ConflictResolutionMethod.PHASE2_DOMINANT
        elif parameter_name in phase5_dominant_params:
            return ConflictResolutionMethod.PHASE5_DOMINANT
        else:
            return ConflictResolutionMethod.WEIGHTED_AVERAGE
    
    def _resolve_conflict_value(self, parameter_name: str, phase2_value: float, 
                               phase5_value: float, method: ConflictResolutionMethod,
                               context: Dict[str, Any] = None) -> float:
        """解決衝突計算最終值"""
        if method == ConflictResolutionMethod.PHASE2_DOMINANT:
            weight = 0.8  # Phase2 佔 80%
            return phase2_value * weight + phase5_value * (1 - weight)
        
        elif method == ConflictResolutionMethod.PHASE5_DOMINANT:
            weight = 0.3  # Phase2 只佔 30%
            return phase2_value * weight + phase5_value * (1 - weight)
        
        elif method == ConflictResolutionMethod.WEIGHTED_AVERAGE:
            # 基於最近性能動態調整權重
            recent_performance = context.get('recent_performance', 0.5)
            if recent_performance > 0.6:
                weight = 0.7  # 性能好時更信任 Phase2
            else:
                weight = 0.4  # 性能差時更保守，信任 Phase5
            return phase2_value * weight + phase5_value * (1 - weight)
        
        elif method == ConflictResolutionMethod.A_B_TESTING:
            # A/B 測試初始使用 Phase5 值
            self._start_ab_test(parameter_name, phase2_value, phase5_value)
            return phase5_value
        
        else:
            # 默認使用加權平均
            return (phase2_value + phase5_value) / 2
    
    def _calculate_confidence_score(self, parameter_name: str, severity: ConflictSeverity,
                                   method: ConflictResolutionMethod, context: Dict[str, Any] = None) -> float:
        """計算解決方案信心度"""
        base_confidence = {
            ConflictSeverity.LOW: 0.9,
            ConflictSeverity.MEDIUM: 0.7,
            ConflictSeverity.HIGH: 0.5,
            ConflictSeverity.CRITICAL: 0.3
        }[severity]
        
        # 根據信號數量調整信心度
        signal_count = context.get('signal_count', 0) if context else 0
        if signal_count > 200:
            confidence_boost = 0.1
        elif signal_count > 100:
            confidence_boost = 0.05
        else:
            confidence_boost = 0.0
        
        # 根據解決方法調整
        method_confidence = {
            ConflictResolutionMethod.WEIGHTED_AVERAGE: 0.8,
            ConflictResolutionMethod.PHASE2_DOMINANT: 0.7,
            ConflictResolutionMethod.PHASE5_DOMINANT: 0.9,
            ConflictResolutionMethod.A_B_TESTING: 0.6,
            ConflictResolutionMethod.PERFORMANCE_BASED: 0.8
        }[method]
        
        final_confidence = min(1.0, base_confidence + confidence_boost) * method_confidence
        return final_confidence
    
    def _start_ab_test(self, parameter_name: str, value_a: float, value_b: float):
        """啟動 A/B 測試"""
        test_id = f"{parameter_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.active_ab_tests[test_id] = {
            'parameter_name': parameter_name,
            'value_a': value_a,  # Phase2 值
            'value_b': value_b,  # Phase5 值
            'start_time': datetime.now(),
            'signals_count': 0,
            'performance_a': [],
            'performance_b': [],
            'current_variant': 'b',  # 開始使用 Phase5 值
            'duration': self.resolution_config['a_b_test_duration']
        }
        
        logger.info(f"🧪 啟動 A/B 測試: {parameter_name}")
        logger.info(f"   變體 A (Phase2): {value_a:.4f}")
        logger.info(f"   變體 B (Phase5): {value_b:.4f}")
    
    def update_ab_test_performance(self, parameter_name: str, performance_score: float):
        """更新 A/B 測試性能"""
        for test_id, test_data in self.active_ab_tests.items():
            if test_data['parameter_name'] == parameter_name:
                variant = test_data['current_variant']
                
                if variant == 'a':
                    test_data['performance_a'].append(performance_score)
                else:
                    test_data['performance_b'].append(performance_score)
                
                test_data['signals_count'] += 1
                
                # 檢查是否需要切換變體
                if test_data['signals_count'] % 10 == 0:
                    test_data['current_variant'] = 'a' if variant == 'b' else 'b'
                    logger.debug(f"🧪 A/B 測試切換到變體 {test_data['current_variant']}")
                
                # 檢查測試是否完成
                if test_data['signals_count'] >= test_data['duration']:
                    self._complete_ab_test(test_id)
                
                break
    
    def _complete_ab_test(self, test_id: str):
        """完成 A/B 測試"""
        test_data = self.active_ab_tests[test_id]
        
        # 計算平均性能
        avg_performance_a = np.mean(test_data['performance_a']) if test_data['performance_a'] else 0
        avg_performance_b = np.mean(test_data['performance_b']) if test_data['performance_b'] else 0
        
        # 選擇獲勝者
        winner = 'a' if avg_performance_a > avg_performance_b else 'b'
        winning_value = test_data['value_a'] if winner == 'a' else test_data['value_b']
        
        logger.info(f"🏆 A/B 測試完成: {test_data['parameter_name']}")
        logger.info(f"   變體 A 性能: {avg_performance_a:.4f}")
        logger.info(f"   變體 B 性能: {avg_performance_b:.4f}")
        logger.info(f"   獲勝者: 變體 {winner}, 值: {winning_value:.4f}")
        
        # 移除已完成的測試
        del self.active_ab_tests[test_id]
        
        return winning_value
    
    def check_rollback_needed(self, parameter_name: str, recent_performance: List[float]) -> bool:
        """檢查是否需要回滾"""
        if len(recent_performance) < 20:
            return False
        
        # 計算最近性能趨勢
        recent_avg = np.mean(recent_performance[-10:])
        baseline_avg = np.mean(recent_performance[-20:-10])
        
        if baseline_avg > 0:
            performance_change = (recent_avg - baseline_avg) / baseline_avg
            
            if performance_change < -self.resolution_config['rollback_threshold']:
                logger.warning(f"🔄 參數 {parameter_name} 觸發回滾: 性能下降 {performance_change:.2%}")
                return True
        
        return False
    
    def get_conflict_statistics(self) -> ConflictResolutionStats:
        """獲取衝突解決統計"""
        if not self.conflict_history:
            return ConflictResolutionStats(
                total_conflicts=0,
                resolution_success_rate=0.0,
                most_conflicted_parameters=[],
                avg_resolution_time=0.0,
                rollback_rate=0.0,
                performance_improvement=0.0
            )
        
        # 統計衝突參數
        parameter_counts = {}
        successful_resolutions = 0
        rollbacks = 0
        
        for conflict in self.conflict_history:
            param = conflict.parameter_name
            parameter_counts[param] = parameter_counts.get(param, 0) + 1
            
            if conflict.resolution_success:
                successful_resolutions += 1
            
            if conflict.rollback_triggered:
                rollbacks += 1
        
        # 排序最常衝突的參數
        most_conflicted = sorted(parameter_counts.items(), key=lambda x: x[1], reverse=True)
        most_conflicted_params = [param for param, count in most_conflicted[:5]]
        
        return ConflictResolutionStats(
            total_conflicts=len(self.conflict_history),
            resolution_success_rate=successful_resolutions / len(self.conflict_history),
            most_conflicted_parameters=most_conflicted_params,
            avg_resolution_time=0.0,  # 簡化實現
            rollback_rate=rollbacks / len(self.conflict_history),
            performance_improvement=0.0  # 需要更多數據計算
        )
    
    def save_conflict_history(self):
        """保存衝突歷史"""
        try:
            data = []
            for conflict in self.conflict_history:
                conflict_dict = asdict(conflict)
                conflict_dict['conflict_timestamp'] = conflict.conflict_timestamp.isoformat()
                conflict_dict['severity'] = conflict.severity.value
                conflict_dict['resolution_method'] = conflict.resolution_method.value
                data.append(conflict_dict)
            
            with open(self.conflicts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"❌ 衝突歷史保存失敗: {e}")
    
    def load_conflict_history(self):
        """載入衝突歷史"""
        try:
            if self.conflicts_file.exists():
                with open(self.conflicts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.conflict_history = []
                for item in data:
                    # 轉換回枚舉和日期類型
                    item['conflict_timestamp'] = datetime.fromisoformat(item['conflict_timestamp'])
                    item['severity'] = ConflictSeverity(item['severity'])
                    item['resolution_method'] = ConflictResolutionMethod(item['resolution_method'])
                    
                    conflict = ParameterConflict(**item)
                    self.conflict_history.append(conflict)
                
                logger.info(f"📚 載入衝突歷史: {len(self.conflict_history)} 條記錄")
                
        except Exception as e:
            logger.error(f"❌ 衝突歷史載入失敗: {e}")
            self.conflict_history = []

# 全局實例
conflict_manager = ParameterConflictManager()

async def main():
    """測試函數"""
    print("⚖️ Parameter Conflict Manager 測試")
    
    # 模擬衝突檢測
    conflict = conflict_manager.detect_conflict(
        'signal_threshold',
        0.65,  # Phase2 值
        0.55,  # Phase5 值
        {
            'market_conditions': {'volatility': 0.3},
            'signal_count': 150,
            'recent_performance': 0.7
        }
    )
    
    print(f"衝突檢測: {conflict.severity.value}, 最終值: {conflict.final_value:.4f}")
    
    # 獲取統計
    stats = conflict_manager.get_conflict_statistics()
    print(f"衝突統計: {stats}")
    
    print("✅ 測試完成")

if __name__ == "__main__":
    asyncio.run(main())
