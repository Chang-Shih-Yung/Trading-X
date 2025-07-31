#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Coordination Engine
事件協調引擎 - Phase 3 Week 3

這個模組提供高級事件協調功能，包括：
- 多重事件衝突檢測和解決
- 事件優先級排序和調度
- 事件間協同效應分析
- 智能事件響應策略生成
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque
import uuid
import json

# 設置日誌
logger = logging.getLogger(__name__)

class EventPriority(Enum):
    """事件優先級"""
    CRITICAL = "critical"       # 最高優先級
    HIGH = "high"              # 高優先級
    MEDIUM = "medium"          # 中等優先級
    LOW = "low"               # 低優先級
    BACKGROUND = "background"  # 背景優先級

class ConflictType(Enum):
    """衝突類型"""
    TIMING_CONFLICT = "timing_conflict"         # 時間衝突
    RESOURCE_CONFLICT = "resource_conflict"     # 資源衝突
    DIRECTION_CONFLICT = "direction_conflict"   # 方向衝突
    MAGNITUDE_CONFLICT = "magnitude_conflict"   # 強度衝突
    DEPENDENCY_CONFLICT = "dependency_conflict" # 依賴衝突

class ResolutionStrategy(Enum):
    """衝突解決策略"""
    PRIORITY_OVERRIDE = "priority_override"     # 優先級覆蓋
    MERGE_EFFECTS = "merge_effects"            # 合併效應
    TIME_SEPARATION = "time_separation"        # 時間分離
    RESOURCE_SHARING = "resource_sharing"      # 資源共享
    CANCEL_LOWER = "cancel_lower"             # 取消低優先級

class CoordinationMode(Enum):
    """協調模式"""
    CONSERVATIVE = "conservative"  # 保守模式
    AGGRESSIVE = "aggressive"     # 積極模式
    BALANCED = "balanced"        # 平衡模式
    ADAPTIVE = "adaptive"        # 自適應模式

@dataclass
class EventConflict:
    """事件衝突描述"""
    conflict_id: str
    event_ids: List[str]
    conflict_type: ConflictType
    severity_score: float  # 0-1，1為最嚴重
    affected_symbols: Set[str]
    detection_time: datetime
    
    # 衝突詳情
    conflict_description: str = ""
    impact_assessment: Dict[str, float] = field(default_factory=dict)
    resolution_options: List[ResolutionStrategy] = field(default_factory=list)
    
    # 狀態
    is_resolved: bool = False
    resolution_strategy: Optional[ResolutionStrategy] = None
    resolution_time: Optional[datetime] = None

@dataclass
class EventSchedule:
    """事件調度計畫"""
    schedule_id: str
    events: List[str]  # 事件ID列表，按執行順序排列
    coordination_mode: CoordinationMode
    total_duration: float  # 預計總執行時間（小時）
    
    # 調度詳情
    schedule_rationale: str = ""
    resource_allocation: Dict[str, float] = field(default_factory=dict)
    risk_assessment: Dict[str, float] = field(default_factory=dict)
    
    # 執行狀態
    is_active: bool = False
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None

@dataclass
class CoordinationResult:
    """協調結果"""
    coordination_id: str
    timestamp: datetime
    processed_events: List[str]
    
    # 檢測到的衝突
    conflicts_detected: List[EventConflict]
    conflicts_resolved: int
    
    # 生成的調度
    event_schedule: Optional[EventSchedule]
    
    # 協調統計
    processing_time_ms: float
    coordination_effectiveness: float  # 0-1
    resource_utilization: float  # 0-1
    
    # 建議和警告
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class EventCoordinationEngine:
    """事件協調引擎"""
    
    def __init__(self):
        self.active_events: Dict[str, Dict[str, Any]] = {}
        self.coordination_history: Dict[str, CoordinationResult] = {}
        self.conflict_history: List[EventConflict] = []
        self.active_schedules: Dict[str, EventSchedule] = {}
        
        # 配置參數
        self.max_concurrent_events = 5
        self.conflict_detection_window_hours = 24
        self.coordination_mode = CoordinationMode.BALANCED
        
        # 統計信息
        self.coordination_stats = {
            "total_coordinations": 0,
            "conflicts_detected": 0,
            "conflicts_resolved": 0,
            "schedules_created": 0,
            "avg_processing_time_ms": 0.0,
            "coordination_success_rate": 0.0
        }
        
        logger.info("EventCoordinationEngine 引擎初始化完成")
    
    async def coordinate_events(
        self,
        events: List[Dict[str, Any]],
        coordination_mode: CoordinationMode = None
    ) -> CoordinationResult:
        """
        協調多個事件
        
        Args:
            events: 事件列表
            coordination_mode: 協調模式
            
        Returns:
            CoordinationResult: 協調結果
        """
        start_time = datetime.now()
        coordination_id = f"coord_{int(start_time.timestamp())}"
        
        try:
            # 使用指定的協調模式或默認模式
            mode = coordination_mode or self.coordination_mode
            
            # 更新活躍事件
            event_ids = []
            for event in events:
                event_id = event.get('event_id', str(uuid.uuid4()))
                self.active_events[event_id] = event
                event_ids.append(event_id)
            
            # 檢測事件衝突
            conflicts = await self._detect_conflicts(event_ids)
            
            # 解決衝突
            resolved_conflicts = 0
            for conflict in conflicts:
                if await self._resolve_conflict(conflict, mode):
                    resolved_conflicts += 1
                    conflict.is_resolved = True
                    conflict.resolution_time = datetime.now()
            
            # 生成事件調度
            schedule = await self._generate_schedule(event_ids, mode)
            
            # 計算協調效果
            effectiveness = await self._calculate_coordination_effectiveness(
                conflicts, resolved_conflicts, schedule
            )
            
            # 生成建議和警告
            recommendations, warnings = await self._generate_recommendations(
                conflicts, schedule, mode
            )
            
            # 計算執行時間
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # 創建協調結果
            result = CoordinationResult(
                coordination_id=coordination_id,
                timestamp=start_time,
                processed_events=event_ids,
                conflicts_detected=conflicts,
                conflicts_resolved=resolved_conflicts,
                event_schedule=schedule,
                processing_time_ms=processing_time,
                coordination_effectiveness=effectiveness,
                resource_utilization=await self._calculate_resource_utilization(schedule),
                recommendations=recommendations,
                warnings=warnings
            )
            
            # 儲存結果
            self.coordination_history[coordination_id] = result
            self.conflict_history.extend(conflicts)
            
            if schedule:
                self.active_schedules[schedule.schedule_id] = schedule
            
            # 更新統計
            self._update_coordination_stats(processing_time, True)
            
            logger.info(f"事件協調完成: {coordination_id}, 處理 {len(event_ids)} 個事件")
            return result
            
        except Exception as e:
            logger.error(f"事件協調失敗: {e}")
            self._update_coordination_stats(0, False)
            
            # 返回錯誤結果
            return CoordinationResult(
                coordination_id=coordination_id,
                timestamp=start_time,
                processed_events=[],
                conflicts_detected=[],
                conflicts_resolved=0,
                event_schedule=None,
                processing_time_ms=0,
                coordination_effectiveness=0.0,
                resource_utilization=0.0,
                warnings=[f"協調失敗: {str(e)}"]
            )
    
    async def _detect_conflicts(self, event_ids: List[str]) -> List[EventConflict]:
        """檢測事件間的衝突"""
        conflicts = []
        
        try:
            # 獲取事件信息
            events_data = {eid: self.active_events.get(eid) for eid in event_ids}
            
            # 兩兩檢查衝突
            for i, event_id1 in enumerate(event_ids):
                for event_id2 in event_ids[i+1:]:
                    event1 = events_data[event_id1]
                    event2 = events_data[event_id2]
                    
                    if not event1 or not event2:
                        continue
                    
                    # 檢測各種類型的衝突
                    detected_conflicts = await self._check_event_pair_conflicts(
                        event_id1, event1, event_id2, event2
                    )
                    conflicts.extend(detected_conflicts)
            
            return conflicts
            
        except Exception as e:
            logger.error(f"衝突檢測失敗: {e}")
            return []
    
    async def _check_event_pair_conflicts(
        self,
        event_id1: str, event1: Dict[str, Any],
        event_id2: str, event2: Dict[str, Any]
    ) -> List[EventConflict]:
        """檢查兩個事件間的衝突"""
        conflicts = []
        
        try:
            # 獲取事件時間
            time1 = event1.get('event_time')
            time2 = event2.get('event_time')
            
            if not isinstance(time1, datetime):
                time1 = datetime.fromisoformat(str(time1).replace('Z', '+00:00'))
            if not isinstance(time2, datetime):
                time2 = datetime.fromisoformat(str(time2).replace('Z', '+00:00'))
            
            # 檢查時間衝突
            time_diff = abs((time1 - time2).total_seconds() / 3600)  # 小時
            if time_diff < 2:  # 2小時內認為有時間衝突
                conflict = EventConflict(
                    conflict_id=f"timing_{event_id1}_{event_id2}",
                    event_ids=[event_id1, event_id2],
                    conflict_type=ConflictType.TIMING_CONFLICT,
                    severity_score=max(0.1, 1.0 - time_diff / 2),
                    affected_symbols=set(event1.get('affected_symbols', [])) & 
                                   set(event2.get('affected_symbols', [])),
                    detection_time=datetime.now(),
                    conflict_description=f"事件時間間隔過短: {time_diff:.1f}小時"
                )
                conflicts.append(conflict)
            
            # 檢查方向衝突
            direction1 = event1.get('direction', 'NEUTRAL')
            direction2 = event2.get('direction', 'NEUTRAL')
            
            if self._is_direction_conflict(direction1, direction2):
                severity = 0.8 if time_diff < 6 else 0.4
                conflict = EventConflict(
                    conflict_id=f"direction_{event_id1}_{event_id2}",
                    event_ids=[event_id1, event_id2],
                    conflict_type=ConflictType.DIRECTION_CONFLICT,
                    severity_score=severity,
                    affected_symbols=set(event1.get('affected_symbols', [])) & 
                                   set(event2.get('affected_symbols', [])),
                    detection_time=datetime.now(),
                    conflict_description=f"事件方向衝突: {direction1} vs {direction2}"
                )
                conflicts.append(conflict)
            
            # 檢查資源衝突
            symbols1 = set(event1.get('affected_symbols', []))
            symbols2 = set(event2.get('affected_symbols', []))
            common_symbols = symbols1 & symbols2
            
            if common_symbols and time_diff < 4:
                severity = len(common_symbols) / max(len(symbols1), len(symbols2))
                conflict = EventConflict(
                    conflict_id=f"resource_{event_id1}_{event_id2}",
                    event_ids=[event_id1, event_id2],
                    conflict_type=ConflictType.RESOURCE_CONFLICT,
                    severity_score=severity,
                    affected_symbols=common_symbols,
                    detection_time=datetime.now(),
                    conflict_description=f"共同影響資產: {', '.join(common_symbols)}"
                )
                conflicts.append(conflict)
            
            return conflicts
            
        except Exception as e:
            logger.error(f"事件對衝突檢查失敗: {e}")
            return []
    
    def _is_direction_conflict(self, direction1: str, direction2: str) -> bool:
        """判斷兩個方向是否衝突"""
        conflict_pairs = [
            ('BULLISH', 'BEARISH'),
            ('BEARISH', 'BULLISH'),
            ('VOLATILE', 'NEUTRAL')  # 波動與中性也算輕微衝突
        ]
        
        for d1, d2 in conflict_pairs:
            if (direction1 == d1 and direction2 == d2) or \
               (direction1 == d2 and direction2 == d1):
                return True
        
        return False
    
    async def _resolve_conflict(
        self,
        conflict: EventConflict,
        mode: CoordinationMode
    ) -> bool:
        """解決單個衝突"""
        try:
            # 根據模式選擇解決策略
            strategy = await self._select_resolution_strategy(conflict, mode)
            
            if not strategy:
                return False
            
            # 執行解決策略
            success = await self._execute_resolution_strategy(conflict, strategy)
            
            if success:
                conflict.resolution_strategy = strategy
                logger.info(f"衝突解決成功: {conflict.conflict_id} 使用策略 {strategy.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"衝突解決失敗 {conflict.conflict_id}: {e}")
            return False
    
    async def _select_resolution_strategy(
        self,
        conflict: EventConflict,
        mode: CoordinationMode
    ) -> Optional[ResolutionStrategy]:
        """選擇衝突解決策略"""
        try:
            strategies = []
            
            # 根據衝突類型推薦策略
            if conflict.conflict_type == ConflictType.TIMING_CONFLICT:
                strategies = [ResolutionStrategy.TIME_SEPARATION, ResolutionStrategy.MERGE_EFFECTS]
            elif conflict.conflict_type == ConflictType.DIRECTION_CONFLICT:
                strategies = [ResolutionStrategy.PRIORITY_OVERRIDE, ResolutionStrategy.CANCEL_LOWER]
            elif conflict.conflict_type == ConflictType.RESOURCE_CONFLICT:
                strategies = [ResolutionStrategy.RESOURCE_SHARING, ResolutionStrategy.TIME_SEPARATION]
            
            # 根據協調模式調整策略選擇
            if mode == CoordinationMode.CONSERVATIVE:
                # 保守模式傾向於分離和取消
                if ResolutionStrategy.TIME_SEPARATION in strategies:
                    return ResolutionStrategy.TIME_SEPARATION
                elif ResolutionStrategy.CANCEL_LOWER in strategies:
                    return ResolutionStrategy.CANCEL_LOWER
            elif mode == CoordinationMode.AGGRESSIVE:
                # 積極模式傾向於合併和覆蓋
                if ResolutionStrategy.MERGE_EFFECTS in strategies:
                    return ResolutionStrategy.MERGE_EFFECTS
                elif ResolutionStrategy.PRIORITY_OVERRIDE in strategies:
                    return ResolutionStrategy.PRIORITY_OVERRIDE
            elif mode == CoordinationMode.BALANCED:
                # 平衡模式選擇中等策略
                if ResolutionStrategy.RESOURCE_SHARING in strategies:
                    return ResolutionStrategy.RESOURCE_SHARING
                elif strategies:
                    return strategies[0]
            
            # 自適應模式根據衝突嚴重程度選擇
            if mode == CoordinationMode.ADAPTIVE:
                if conflict.severity_score > 0.7:
                    return ResolutionStrategy.PRIORITY_OVERRIDE
                elif conflict.severity_score > 0.4:
                    return ResolutionStrategy.TIME_SEPARATION
                else:
                    return ResolutionStrategy.RESOURCE_SHARING
            
            return strategies[0] if strategies else None
            
        except Exception as e:
            logger.error(f"解決策略選擇失敗: {e}")
            return None
    
    async def _execute_resolution_strategy(
        self,
        conflict: EventConflict,
        strategy: ResolutionStrategy
    ) -> bool:
        """執行衝突解決策略"""
        try:
            if strategy == ResolutionStrategy.TIME_SEPARATION:
                return await self._apply_time_separation(conflict)
            elif strategy == ResolutionStrategy.MERGE_EFFECTS:
                return await self._apply_merge_effects(conflict)
            elif strategy == ResolutionStrategy.PRIORITY_OVERRIDE:
                return await self._apply_priority_override(conflict)
            elif strategy == ResolutionStrategy.RESOURCE_SHARING:
                return await self._apply_resource_sharing(conflict)
            elif strategy == ResolutionStrategy.CANCEL_LOWER:
                return await self._apply_cancel_lower(conflict)
            
            return False
            
        except Exception as e:
            logger.error(f"解決策略執行失敗: {e}")
            return False
    
    async def _apply_time_separation(self, conflict: EventConflict) -> bool:
        """應用時間分離策略"""
        try:
            # 調整事件時間以避免衝突
            for i, event_id in enumerate(conflict.event_ids):
                if event_id in self.active_events:
                    event = self.active_events[event_id]
                    current_time = event.get('event_time')
                    
                    if isinstance(current_time, str):
                        current_time = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
                    
                    # 第二個事件延後4小時
                    if i == 1:
                        new_time = current_time + timedelta(hours=4)
                        event['event_time'] = new_time
                        event['coordination_adjusted'] = True
            
            return True
            
        except Exception as e:
            logger.error(f"時間分離策略執行失敗: {e}")
            return False
    
    async def _apply_merge_effects(self, conflict: EventConflict) -> bool:
        """應用合併效應策略"""
        try:
            # 合併事件效應，創建複合事件
            if len(conflict.event_ids) >= 2:
                primary_event_id = conflict.event_ids[0]
                secondary_event_id = conflict.event_ids[1]
                
                primary_event = self.active_events.get(primary_event_id)
                secondary_event = self.active_events.get(secondary_event_id)
                
                if primary_event and secondary_event:
                    # 合併影響範圍
                    primary_symbols = set(primary_event.get('affected_symbols', []))
                    secondary_symbols = set(secondary_event.get('affected_symbols', []))
                    merged_symbols = list(primary_symbols | secondary_symbols)
                    
                    primary_event['affected_symbols'] = merged_symbols
                    primary_event['is_composite'] = True
                    primary_event['merged_from'] = [secondary_event_id]
                    
                    # 調整信心度
                    primary_confidence = primary_event.get('confidence', 0.5)
                    secondary_confidence = secondary_event.get('confidence', 0.5)
                    merged_confidence = (primary_confidence + secondary_confidence) / 2
                    primary_event['confidence'] = merged_confidence
                    
                    # 移除次要事件
                    if secondary_event_id in self.active_events:
                        del self.active_events[secondary_event_id]
            
            return True
            
        except Exception as e:
            logger.error(f"合併效應策略執行失敗: {e}")
            return False
    
    async def _apply_priority_override(self, conflict: EventConflict) -> bool:
        """應用優先級覆蓋策略"""
        try:
            # 根據事件嚴重程度和信心度確定優先級
            event_priorities = []
            
            for event_id in conflict.event_ids:
                event = self.active_events.get(event_id)
                if event:
                    severity_score = self._get_severity_score(event.get('severity', 'MEDIUM'))
                    confidence = event.get('confidence', 0.5)
                    priority_score = severity_score * confidence
                    
                    event_priorities.append((event_id, priority_score))
            
            # 按優先級排序
            event_priorities.sort(key=lambda x: x[1], reverse=True)
            
            # 保留最高優先級事件，降低其他事件的優先級
            for i, (event_id, score) in enumerate(event_priorities):
                event = self.active_events.get(event_id)
                if event:
                    if i == 0:
                        event['priority_boosted'] = True
                    else:
                        event['priority_reduced'] = True
                        # 降低信心度
                        original_confidence = event.get('confidence', 0.5)
                        event['confidence'] = original_confidence * 0.7
            
            return True
            
        except Exception as e:
            logger.error(f"優先級覆蓋策略執行失敗: {e}")
            return False
    
    async def _apply_resource_sharing(self, conflict: EventConflict) -> bool:
        """應用資源共享策略"""
        try:
            # 在衝突事件間分配資源權重
            total_weight = 1.0
            num_events = len(conflict.event_ids)
            base_weight = total_weight / num_events
            
            for event_id in conflict.event_ids:
                event = self.active_events.get(event_id)
                if event:
                    event['resource_weight'] = base_weight
                    event['resource_shared'] = True
            
            return True
            
        except Exception as e:
            logger.error(f"資源共享策略執行失敗: {e}")
            return False
    
    async def _apply_cancel_lower(self, conflict: EventConflict) -> bool:
        """應用取消低優先級策略"""
        try:
            # 找到優先級最低的事件並取消
            lowest_priority_event = None
            lowest_score = float('inf')
            
            for event_id in conflict.event_ids:
                event = self.active_events.get(event_id)
                if event:
                    severity_score = self._get_severity_score(event.get('severity', 'MEDIUM'))
                    confidence = event.get('confidence', 0.5)
                    priority_score = severity_score * confidence
                    
                    if priority_score < lowest_score:
                        lowest_score = priority_score
                        lowest_priority_event = event_id
            
            # 取消最低優先級事件
            if lowest_priority_event and lowest_priority_event in self.active_events:
                self.active_events[lowest_priority_event]['cancelled'] = True
                self.active_events[lowest_priority_event]['cancellation_reason'] = 'conflict_resolution'
            
            return True
            
        except Exception as e:
            logger.error(f"取消低優先級策略執行失敗: {e}")
            return False
    
    def _get_severity_score(self, severity: str) -> float:
        """獲取嚴重程度分數"""
        severity_mapping = {
            'CRITICAL': 1.0,
            'HIGH': 0.8,
            'MEDIUM': 0.5,
            'LOW': 0.3
        }
        return severity_mapping.get(severity, 0.5)
    
    async def _generate_schedule(
        self,
        event_ids: List[str],
        mode: CoordinationMode
    ) -> Optional[EventSchedule]:
        """生成事件調度計畫"""
        try:
            # 過濾有效事件
            valid_events = []
            for event_id in event_ids:
                event = self.active_events.get(event_id)
                if event and not event.get('cancelled', False):
                    valid_events.append(event_id)
            
            if not valid_events:
                return None
            
            # 按時間和優先級排序
            sorted_events = await self._sort_events_for_schedule(valid_events)
            
            # 計算總執行時間
            total_duration = await self._calculate_schedule_duration(sorted_events)
            
            # 生成調度
            schedule = EventSchedule(
                schedule_id=f"schedule_{int(datetime.now().timestamp())}",
                events=sorted_events,
                coordination_mode=mode,
                total_duration=total_duration,
                schedule_rationale=f"基於 {mode.value} 模式生成的事件調度",
                resource_allocation=await self._calculate_resource_allocation(sorted_events),
                risk_assessment=await self._assess_schedule_risks(sorted_events)
            )
            
            return schedule
            
        except Exception as e:
            logger.error(f"事件調度生成失敗: {e}")
            return None
    
    async def _sort_events_for_schedule(self, event_ids: List[str]) -> List[str]:
        """為調度排序事件"""
        try:
            event_scores = []
            
            for event_id in event_ids:
                event = self.active_events.get(event_id)
                if event:
                    # 計算排序分數（時間緊急性 + 優先級）
                    event_time = event.get('event_time')
                    if isinstance(event_time, str):
                        event_time = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
                    
                    time_urgency = 1.0 / max(1, (event_time - datetime.now()).total_seconds() / 3600)
                    severity_score = self._get_severity_score(event.get('severity', 'MEDIUM'))
                    confidence = event.get('confidence', 0.5)
                    
                    total_score = (time_urgency * 0.4 + severity_score * 0.4 + confidence * 0.2)
                    event_scores.append((event_id, total_score))
            
            # 按分數排序
            event_scores.sort(key=lambda x: x[1], reverse=True)
            return [event_id for event_id, _ in event_scores]
            
        except Exception as e:
            logger.error(f"事件排序失敗: {e}")
            return event_ids
    
    async def _calculate_schedule_duration(self, event_ids: List[str]) -> float:
        """計算調度總執行時間"""
        try:
            total_hours = 0.0
            
            for event_id in event_ids:
                event = self.active_events.get(event_id)
                if event:
                    # 估算事件處理時間
                    severity = event.get('severity', 'MEDIUM')
                    affected_count = len(event.get('affected_symbols', []))
                    
                    base_duration = {
                        'CRITICAL': 4.0,
                        'HIGH': 2.0,
                        'MEDIUM': 1.0,
                        'LOW': 0.5
                    }.get(severity, 1.0)
                    
                    # 根據影響範圍調整
                    duration = base_duration * (1 + affected_count * 0.1)
                    total_hours += duration
            
            return total_hours
            
        except Exception as e:
            logger.error(f"調度時間計算失敗: {e}")
            return 0.0
    
    async def _calculate_resource_allocation(self, event_ids: List[str]) -> Dict[str, float]:
        """計算資源分配"""
        try:
            allocation = {}
            total_weight = sum(
                self.active_events.get(eid, {}).get('resource_weight', 1.0) 
                for eid in event_ids
            )
            
            for event_id in event_ids:
                event = self.active_events.get(event_id)
                if event:
                    weight = event.get('resource_weight', 1.0)
                    allocation[event_id] = weight / total_weight if total_weight > 0 else 0.0
            
            return allocation
            
        except Exception as e:
            logger.error(f"資源分配計算失敗: {e}")
            return {}
    
    async def _assess_schedule_risks(self, event_ids: List[str]) -> Dict[str, float]:
        """評估調度風險"""
        try:
            risks = {
                'timing_risk': 0.0,
                'resource_risk': 0.0,
                'coordination_risk': 0.0,
                'execution_risk': 0.0
            }
            
            # 時間風險
            for i in range(len(event_ids) - 1):
                event1 = self.active_events.get(event_ids[i])
                event2 = self.active_events.get(event_ids[i + 1])
                
                if event1 and event2:
                    time1 = event1.get('event_time')
                    time2 = event2.get('event_time')
                    
                    if isinstance(time1, str):
                        time1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
                    if isinstance(time2, str):
                        time2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))
                    
                    time_gap = abs((time2 - time1).total_seconds() / 3600)
                    if time_gap < 2:
                        risks['timing_risk'] += 0.2
            
            # 資源風險
            symbol_conflicts = defaultdict(int)
            for event_id in event_ids:
                event = self.active_events.get(event_id)
                if event:
                    for symbol in event.get('affected_symbols', []):
                        symbol_conflicts[symbol] += 1
            
            max_conflicts = max(symbol_conflicts.values()) if symbol_conflicts else 1
            risks['resource_risk'] = min(1.0, (max_conflicts - 1) * 0.3)
            
            # 協調風險
            risks['coordination_risk'] = min(1.0, len(event_ids) * 0.1)
            
            # 執行風險
            avg_confidence = np.mean([
                self.active_events.get(eid, {}).get('confidence', 0.5)
                for eid in event_ids
            ])
            risks['execution_risk'] = 1.0 - avg_confidence
            
            return risks
            
        except Exception as e:
            logger.error(f"風險評估失敗: {e}")
            return {}
    
    async def _calculate_coordination_effectiveness(
        self,
        conflicts: List[EventConflict],
        resolved_conflicts: int,
        schedule: Optional[EventSchedule]
    ) -> float:
        """計算協調效果"""
        try:
            effectiveness = 1.0
            
            # 衝突解決效果
            if conflicts:
                resolution_rate = resolved_conflicts / len(conflicts)
                effectiveness *= resolution_rate
            
            # 調度生成效果
            if schedule:
                effectiveness *= 1.2  # 成功生成調度加分
                
                # 考慮風險評估
                risks = schedule.risk_assessment
                if risks:
                    avg_risk = np.mean(list(risks.values()))
                    effectiveness *= (1.0 - avg_risk * 0.5)
            else:
                effectiveness *= 0.7  # 未能生成調度扣分
            
            return min(1.0, max(0.0, effectiveness))
            
        except Exception as e:
            logger.error(f"協調效果計算失敗: {e}")
            return 0.5
    
    async def _calculate_resource_utilization(self, schedule: Optional[EventSchedule]) -> float:
        """計算資源利用率"""
        try:
            if not schedule:
                return 0.0
            
            allocation = schedule.resource_allocation
            if not allocation:
                return 0.0
            
            # 計算分配均勻性
            values = list(allocation.values())
            if not values:
                return 0.0
            
            # 使用變異係數的倒數作為利用率指標
            mean_allocation = np.mean(values)
            std_allocation = np.std(values)
            
            if mean_allocation == 0:
                return 0.0
            
            cv = std_allocation / mean_allocation if mean_allocation > 0 else 1.0
            utilization = 1.0 / (1.0 + cv)
            
            return min(1.0, utilization)
            
        except Exception as e:
            logger.error(f"資源利用率計算失敗: {e}")
            return 0.0
    
    async def _generate_recommendations(
        self,
        conflicts: List[EventConflict],
        schedule: Optional[EventSchedule],
        mode: CoordinationMode
    ) -> Tuple[List[str], List[str]]:
        """生成建議和警告"""
        recommendations = []
        warnings = []
        
        try:
            # 基於衝突的建議
            if conflicts:
                unresolved_conflicts = [c for c in conflicts if not c.is_resolved]
                if unresolved_conflicts:
                    warnings.append(f"發現 {len(unresolved_conflicts)} 個未解決的衝突")
                    recommendations.append("考慮調整事件時間或優先級以減少衝突")
                
                high_severity_conflicts = [c for c in conflicts if c.severity_score > 0.7]
                if high_severity_conflicts:
                    warnings.append(f"檢測到 {len(high_severity_conflicts)} 個高嚴重程度衝突")
                    recommendations.append("建議重新評估高嚴重程度事件的執行策略")
            
            # 基於調度的建議
            if schedule:
                if schedule.total_duration > 12:
                    warnings.append(f"調度執行時間較長: {schedule.total_duration:.1f} 小時")
                    recommendations.append("考慮分批執行或並行處理部分事件")
                
                risks = schedule.risk_assessment
                if risks:
                    high_risks = [risk_type for risk_type, risk_value in risks.items() if risk_value > 0.7]
                    if high_risks:
                        warnings.append(f"高風險項目: {', '.join(high_risks)}")
                        recommendations.append("建議增加風險緩解措施")
            
            # 基於模式的建議
            if mode == CoordinationMode.AGGRESSIVE:
                recommendations.append("積極模式: 建議密切監控事件執行效果")
            elif mode == CoordinationMode.CONSERVATIVE:
                recommendations.append("保守模式: 可考慮適度提高並行處理效率")
            
            return recommendations, warnings
            
        except Exception as e:
            logger.error(f"建議生成失敗: {e}")
            return ["系統建議生成異常"], ["建議生成過程中出現錯誤"]
    
    def _update_coordination_stats(self, processing_time_ms: float, success: bool):
        """更新協調統計"""
        self.coordination_stats["total_coordinations"] += 1
        
        if success:
            # 更新平均處理時間
            current_avg = self.coordination_stats["avg_processing_time_ms"]
            total = self.coordination_stats["total_coordinations"]
            new_avg = ((current_avg * (total - 1)) + processing_time_ms) / total
            self.coordination_stats["avg_processing_time_ms"] = new_avg
            
            # 更新成功率
            success_count = self.coordination_stats["total_coordinations"] * \
                          self.coordination_stats["coordination_success_rate"] + 1
            self.coordination_stats["coordination_success_rate"] = success_count / total
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """獲取協調系統狀態"""
        return {
            "active_events_count": len(self.active_events),
            "active_schedules_count": len(self.active_schedules),
            "recent_conflicts_count": len([c for c in self.conflict_history[-10:] if not c.is_resolved]),
            "coordination_mode": self.coordination_mode.value,
            "stats": self.coordination_stats.copy(),
            "system_health": "正常" if self.coordination_stats["coordination_success_rate"] > 0.8 else "需要關注"
        }
    
    def export_coordination_summary(self) -> Dict[str, Any]:
        """導出協調系統摘要"""
        recent_coordinations = list(self.coordination_history.values())[-5:]
        
        return {
            "system_status": self.get_coordination_status(),
            "recent_coordinations": [
                {
                    "coordination_id": coord.coordination_id,
                    "timestamp": coord.timestamp.isoformat(),
                    "events_processed": len(coord.processed_events),
                    "conflicts_detected": len(coord.conflicts_detected),
                    "conflicts_resolved": coord.conflicts_resolved,
                    "effectiveness": coord.coordination_effectiveness,
                    "has_schedule": coord.event_schedule is not None
                }
                for coord in recent_coordinations
            ],
            "conflict_summary": {
                "total_conflicts": len(self.conflict_history),
                "resolved_conflicts": len([c for c in self.conflict_history if c.is_resolved]),
                "recent_conflicts": len([c for c in self.conflict_history[-24:] if not c.is_resolved]),
                "conflict_types": {
                    conflict_type.value: len([
                        c for c in self.conflict_history 
                        if c.conflict_type == conflict_type
                    ])
                    for conflict_type in ConflictType
                }
            },
            "active_schedules": [
                {
                    "schedule_id": schedule.schedule_id,
                    "events_count": len(schedule.events),
                    "coordination_mode": schedule.coordination_mode.value,
                    "total_duration": schedule.total_duration,
                    "is_active": schedule.is_active
                }
                for schedule in self.active_schedules.values()
            ]
        }

# 全局實例
event_coordination_engine = EventCoordinationEngine()
