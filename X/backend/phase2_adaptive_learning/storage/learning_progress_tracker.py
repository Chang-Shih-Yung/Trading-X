#!/usr/bin/env python3
"""
📊 Learning Progress Tracker
學習進度追蹤器 - 監控和可視化學習進度

功能：
- 信號累積進度追蹤
- 學習階段管理
- 性能指標監控
- 進度預測和預警
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

class LearningStage(Enum):
    """學習階段"""
    COLD_START = "cold_start"           # 冷啟動階段 (0-50 信號)
    INITIAL_LEARNING = "initial_learning" # 初始學習 (50-200 信號)
    STABLE_LEARNING = "stable_learning"   # 穩定學習 (200-500 信號)
    ADVANCED_LEARNING = "advanced_learning" # 高級學習 (500+ 信號)
    OPTIMIZING = "optimizing"             # 優化階段

class ProgressAlert(Enum):
    """進度警報"""
    NORMAL = "normal"
    SLOW_PROGRESS = "slow_progress"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    LEARNING_STAGNATION = "learning_stagnation"

@dataclass
class LearningMilestone:
    """學習里程碑"""
    stage: LearningStage
    signal_threshold: int
    description: str
    expected_accuracy: float
    unlocked_features: List[str]

@dataclass
class ProgressSnapshot:
    """進度快照"""
    timestamp: datetime
    signal_count: int
    learning_stage: LearningStage
    performance_score: float
    accuracy_rate: float
    confidence_level: float
    
    # 性能指標
    successful_predictions: int
    total_predictions: int
    avg_return_rate: float
    
    # 學習指標
    parameter_stability: float
    pattern_recognition_score: float
    adaptation_speed: float

class LearningProgressTracker:
    """學習進度追蹤器"""
    
    def __init__(self):
        """初始化進度追蹤器"""
        self.storage_dir = Path(__file__).parent
        self.storage_dir.mkdir(exist_ok=True)
        
        self.progress_file = self.storage_dir / "learning_progress.json"
        self.milestones_file = self.storage_dir / "learning_milestones.json"
        
        # 進度數據
        self.progress_history: List[ProgressSnapshot] = []
        self.milestones = self._initialize_milestones()
        self.current_alerts: List[Dict] = []
        
        # 載入歷史數據
        self.load_progress_history()
        
        logger.info("📊 學習進度追蹤器初始化完成")
    
    def _initialize_milestones(self) -> List[LearningMilestone]:
        """初始化學習里程碑"""
        return [
            LearningMilestone(
                stage=LearningStage.COLD_START,
                signal_threshold=0,
                description="系統啟動，開始數據收集",
                expected_accuracy=0.0,
                unlocked_features=["基礎信號記錄"]
            ),
            LearningMilestone(
                stage=LearningStage.INITIAL_LEARNING,
                signal_threshold=50,
                description="達到最小學習閾值，啟用基礎學習",
                expected_accuracy=0.52,
                unlocked_features=["模式識別", "基礎參數優化"]
            ),
            LearningMilestone(
                stage=LearningStage.STABLE_LEARNING,
                signal_threshold=200,
                description="進入穩定學習階段，啟用高級功能",
                expected_accuracy=0.58,
                unlocked_features=["市場狀態適應", "動態參數調整", "衝突解決"]
            ),
            LearningMilestone(
                stage=LearningStage.ADVANCED_LEARNING,
                signal_threshold=500,
                description="高級學習模式，啟用預測功能",
                expected_accuracy=0.65,
                unlocked_features=["趨勢預測", "風險評估", "A/B 測試"]
            ),
            LearningMilestone(
                stage=LearningStage.OPTIMIZING,
                signal_threshold=1000,
                description="進入優化階段，持續改進",
                expected_accuracy=0.70,
                unlocked_features=["深度優化", "自動調參", "智能預警"]
            )
        ]
    
    async def update_progress(self, signal_count: int, performance_metrics: Dict[str, Any]) -> ProgressSnapshot:
        """更新學習進度"""
        try:
            # 確定當前學習階段
            current_stage = self._determine_learning_stage(signal_count)
            
            # 計算性能指標
            performance_score = performance_metrics.get('performance_score', 0.0)
            accuracy_rate = performance_metrics.get('accuracy_rate', 0.0)
            successful_predictions = performance_metrics.get('successful_predictions', 0)
            total_predictions = performance_metrics.get('total_predictions', 1)
            
            # 計算學習指標
            parameter_stability = self._calculate_parameter_stability()
            pattern_recognition_score = self._calculate_pattern_recognition_score(performance_metrics)
            adaptation_speed = self._calculate_adaptation_speed()
            
            # 創建進度快照
            snapshot = ProgressSnapshot(
                timestamp=datetime.now(),
                signal_count=signal_count,
                learning_stage=current_stage,
                performance_score=performance_score,
                accuracy_rate=accuracy_rate,
                confidence_level=performance_metrics.get('confidence_level', 0.5),
                successful_predictions=successful_predictions,
                total_predictions=total_predictions,
                avg_return_rate=performance_metrics.get('avg_return_rate', 0.0),
                parameter_stability=parameter_stability,
                pattern_recognition_score=pattern_recognition_score,
                adaptation_speed=adaptation_speed
            )
            
            # 添加到歷史記錄
            self.progress_history.append(snapshot)
            
            # 保持歷史記錄不超過 1000 條
            if len(self.progress_history) > 1000:
                self.progress_history = self.progress_history[-1000:]
            
            # 檢查里程碑
            self._check_milestones(snapshot)
            
            # 檢查警報
            self._check_alerts(snapshot)
            
            # 保存進度
            self.save_progress_history()
            
            logger.debug(f"📊 進度已更新: {signal_count} 信號, {current_stage.value} 階段")
            
            return snapshot
            
        except Exception as e:
            logger.error(f"❌ 進度更新失敗: {e}")
            raise
    
    def _determine_learning_stage(self, signal_count: int) -> LearningStage:
        """確定當前學習階段"""
        if signal_count >= 1000:
            return LearningStage.OPTIMIZING
        elif signal_count >= 500:
            return LearningStage.ADVANCED_LEARNING
        elif signal_count >= 200:
            return LearningStage.STABLE_LEARNING
        elif signal_count >= 50:
            return LearningStage.INITIAL_LEARNING
        else:
            return LearningStage.COLD_START
    
    def _calculate_parameter_stability(self) -> float:
        """計算參數穩定性"""
        if len(self.progress_history) < 10:
            return 0.5
        
        # 取最近 10 個快照的性能分數
        recent_scores = [s.performance_score for s in self.progress_history[-10:]]
        
        # 計算變異係數 (標準差/平均值)
        if np.mean(recent_scores) > 0:
            cv = np.std(recent_scores) / np.mean(recent_scores)
            stability = max(0.0, 1.0 - cv)  # 變異係數越小，穩定性越高
        else:
            stability = 0.0
        
        return min(1.0, stability)
    
    def _calculate_pattern_recognition_score(self, metrics: Dict[str, Any]) -> float:
        """計算模式識別分數"""
        # 基於成功率和一致性計算
        accuracy = metrics.get('accuracy_rate', 0.0)
        consistency = metrics.get('consistency_score', 0.5)
        
        # 結合準確率和一致性
        pattern_score = (accuracy * 0.7) + (consistency * 0.3)
        return min(1.0, pattern_score)
    
    def _calculate_adaptation_speed(self) -> float:
        """計算適應速度"""
        if len(self.progress_history) < 5:
            return 0.5
        
        # 計算最近 5 個週期的性能改善率
        recent_scores = [s.performance_score for s in self.progress_history[-5:]]
        
        if len(recent_scores) >= 2:
            # 計算線性趨勢
            x = np.arange(len(recent_scores))
            slope = np.polyfit(x, recent_scores, 1)[0]
            
            # 將斜率轉換為 0-1 分數
            adaptation_speed = max(0.0, min(1.0, 0.5 + slope * 10))
        else:
            adaptation_speed = 0.5
        
        return adaptation_speed
    
    def _check_milestones(self, snapshot: ProgressSnapshot):
        """檢查里程碑達成"""
        for milestone in self.milestones:
            if (snapshot.signal_count >= milestone.signal_threshold and 
                snapshot.learning_stage == milestone.stage):
                
                # 檢查是否已經記錄過這個里程碑
                recent_milestone_logs = [
                    alert for alert in self.current_alerts 
                    if alert.get('type') == 'milestone' and 
                    alert.get('stage') == milestone.stage.value
                ]
                
                if not recent_milestone_logs:
                    logger.info(f"🎯 達成學習里程碑: {milestone.description}")
                    logger.info(f"   解鎖功能: {', '.join(milestone.unlocked_features)}")
                    
                    self.current_alerts.append({
                        'type': 'milestone',
                        'stage': milestone.stage.value,
                        'description': milestone.description,
                        'timestamp': datetime.now().isoformat(),
                        'unlocked_features': milestone.unlocked_features
                    })
    
    def _check_alerts(self, snapshot: ProgressSnapshot):
        """檢查警報條件"""
        alerts_to_add = []
        
        # 檢查性能下降
        if len(self.progress_history) >= 10:
            recent_avg = np.mean([s.performance_score for s in self.progress_history[-5:]])
            baseline_avg = np.mean([s.performance_score for s in self.progress_history[-10:-5]])
            
            if baseline_avg > 0 and (recent_avg / baseline_avg) < 0.85:
                alerts_to_add.append({
                    'type': 'performance_degradation',
                    'severity': 'warning',
                    'message': f'性能下降: {((recent_avg / baseline_avg - 1) * 100):.1f}%',
                    'timestamp': datetime.now().isoformat()
                })
        
        # 檢查學習停滯
        if snapshot.learning_stage != LearningStage.COLD_START:
            if snapshot.adaptation_speed < 0.3:
                alerts_to_add.append({
                    'type': 'learning_stagnation',
                    'severity': 'info',
                    'message': '學習適應速度較慢，可能需要調整參數',
                    'timestamp': datetime.now().isoformat()
                })
        
        # 檢查數據質量
        if snapshot.total_predictions > 20 and snapshot.accuracy_rate < 0.4:
            alerts_to_add.append({
                'type': 'data_quality_issue',
                'severity': 'warning',
                'message': f'預測準確率過低: {snapshot.accuracy_rate:.1%}',
                'timestamp': datetime.now().isoformat()
            })
        
        # 添加新警報
        self.current_alerts.extend(alerts_to_add)
        
        # 保持警報列表不超過 50 條
        if len(self.current_alerts) > 50:
            self.current_alerts = self.current_alerts[-50:]
    
    def get_learning_status(self) -> Dict[str, Any]:
        """獲取學習狀態總覽"""
        if not self.progress_history:
            return {
                'status': 'no_data',
                'message': '尚無學習數據'
            }
        
        latest = self.progress_history[-1]
        
        # 計算進度百分比
        next_milestone = None
        progress_percentage = 0.0
        
        for milestone in self.milestones:
            if latest.signal_count < milestone.signal_threshold:
                next_milestone = milestone
                if milestone.signal_threshold > 0:
                    progress_percentage = (latest.signal_count / milestone.signal_threshold) * 100
                break
        
        if next_milestone is None:
            # 已達到最高階段
            progress_percentage = 100.0
            next_milestone = self.milestones[-1]  # 最後一個里程碑
        
        # 計算趨勢
        trend = self._calculate_trend()
        
        return {
            'current_stage': latest.learning_stage.value,
            'signal_count': latest.signal_count,
            'progress_percentage': min(100.0, progress_percentage),
            'next_milestone': {
                'stage': next_milestone.stage.value,
                'threshold': next_milestone.signal_threshold,
                'description': next_milestone.description,
                'signals_needed': max(0, next_milestone.signal_threshold - latest.signal_count)
            },
            'performance_metrics': {
                'accuracy_rate': latest.accuracy_rate,
                'performance_score': latest.performance_score,
                'confidence_level': latest.confidence_level,
                'parameter_stability': latest.parameter_stability
            },
            'trend': trend,
            'active_alerts': len([a for a in self.current_alerts if a.get('severity') in ['warning', 'error']]),
            'learning_health': self._assess_learning_health(latest)
        }
    
    def _calculate_trend(self) -> str:
        """計算學習趨勢"""
        if len(self.progress_history) < 5:
            return "insufficient_data"
        
        recent_scores = [s.performance_score for s in self.progress_history[-5:]]
        
        # 計算線性趨勢
        x = np.arange(len(recent_scores))
        slope = np.polyfit(x, recent_scores, 1)[0]
        
        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "declining"
        else:
            return "stable"
    
    def _assess_learning_health(self, snapshot: ProgressSnapshot) -> str:
        """評估學習健康狀況"""
        health_score = 0
        
        # 性能分數
        if snapshot.performance_score > 0.7:
            health_score += 3
        elif snapshot.performance_score > 0.5:
            health_score += 2
        elif snapshot.performance_score > 0.3:
            health_score += 1
        
        # 準確率
        if snapshot.accuracy_rate > 0.6:
            health_score += 2
        elif snapshot.accuracy_rate > 0.5:
            health_score += 1
        
        # 穩定性
        if snapshot.parameter_stability > 0.7:
            health_score += 2
        elif snapshot.parameter_stability > 0.5:
            health_score += 1
        
        # 適應速度
        if snapshot.adaptation_speed > 0.6:
            health_score += 1
        
        # 評級
        if health_score >= 7:
            return "excellent"
        elif health_score >= 5:
            return "good"
        elif health_score >= 3:
            return "fair"
        else:
            return "poor"
    
    def get_progress_chart_data(self, days: int = 7) -> Dict[str, List]:
        """獲取進度圖表數據"""
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_snapshots = [
            s for s in self.progress_history 
            if s.timestamp >= cutoff_time
        ]
        
        if not recent_snapshots:
            return {'timestamps': [], 'performance': [], 'accuracy': [], 'signal_count': []}
        
        return {
            'timestamps': [s.timestamp.isoformat() for s in recent_snapshots],
            'performance': [s.performance_score for s in recent_snapshots],
            'accuracy': [s.accuracy_rate for s in recent_snapshots],
            'signal_count': [s.signal_count for s in recent_snapshots],
            'confidence': [s.confidence_level for s in recent_snapshots]
        }
    
    def save_progress_history(self):
        """保存進度歷史"""
        try:
            data = []
            for snapshot in self.progress_history:
                snapshot_dict = asdict(snapshot)
                snapshot_dict['timestamp'] = snapshot.timestamp.isoformat()
                snapshot_dict['learning_stage'] = snapshot.learning_stage.value
                data.append(snapshot_dict)
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"❌ 進度歷史保存失敗: {e}")
    
    def load_progress_history(self):
        """載入進度歷史"""
        try:
            if self.progress_file.exists():
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.progress_history = []
                for item in data:
                    # 轉換回枚舉和日期類型
                    item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                    item['learning_stage'] = LearningStage(item['learning_stage'])
                    
                    snapshot = ProgressSnapshot(**item)
                    self.progress_history.append(snapshot)
                
                logger.info(f"📚 載入進度歷史: {len(self.progress_history)} 條記錄")
                
        except Exception as e:
            logger.error(f"❌ 進度歷史載入失敗: {e}")
            self.progress_history = []

# 全局實例
progress_tracker = LearningProgressTracker()

async def main():
    """測試函數"""
    print("📊 Learning Progress Tracker 測試")
    
    # 模擬進度更新
    snapshot = await progress_tracker.update_progress(
        signal_count=75,
        performance_metrics={
            'performance_score': 0.65,
            'accuracy_rate': 0.58,
            'successful_predictions': 45,
            'total_predictions': 75,
            'confidence_level': 0.7,
            'avg_return_rate': 0.025
        }
    )
    
    print(f"進度快照: {snapshot.learning_stage.value}, 性能: {snapshot.performance_score:.3f}")
    
    # 獲取學習狀態
    status = progress_tracker.get_learning_status()
    print(f"學習狀態: {status}")
    
    print("✅ 測試完成")

if __name__ == "__main__":
    asyncio.run(main())
