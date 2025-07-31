"""
複合事件處理器 - Trading X Phase 3 Week 1
處理多個同時發生或相關聯的複雜事件系統
"""

import logging
import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
from collections import defaultdict, deque
import networkx as nx

logger = logging.getLogger(__name__)

class EventRelationType(Enum):
    """事件關聯類型"""
    CAUSAL = "causal"              # 因果關係
    CORRELATED = "correlated"      # 相關關係  
    CONFLICTING = "conflicting"    # 衝突關係
    REINFORCING = "reinforcing"    # 增強關係
    SEQUENTIAL = "sequential"      # 序列關係
    INDEPENDENT = "independent"    # 獨立關係

class CompositePriority(Enum):
    """複合事件優先級"""
    CRITICAL = "critical"          # 關鍵級
    HIGH = "high"                 # 高級
    MEDIUM = "medium"             # 中級  
    LOW = "low"                   # 低級
    MONITORING = "monitoring"      # 監控級

@dataclass
class EventRelation:
    """事件關聯"""
    source_event_id: str
    target_event_id: str
    relation_type: EventRelationType
    correlation_strength: float    # 關聯強度 (0.0-1.0)
    time_lag_hours: float         # 時間滯後（小時）
    confidence: float             # 關聯信心度
    historical_validation_count: int  # 歷史驗證次數
    last_observed: datetime

@dataclass
class CompositeEvent:
    """複合事件"""
    composite_id: str
    component_event_ids: List[str]
    event_relations: List[EventRelation]
    composite_priority: CompositePriority
    aggregate_confidence: float
    composite_impact_magnitude: float
    expected_start_time: datetime
    expected_duration_hours: float
    affected_symbols: List[str]
    dominant_event_category: str
    conflict_resolution_strategy: str
    composite_timestamp: datetime

@dataclass
class EventChain:
    """事件鏈"""
    chain_id: str
    event_sequence: List[str]     # 事件ID序列
    chain_confidence: float
    total_expected_duration: float
    chain_impact_profile: Dict[str, float]  # 各階段影響
    trigger_conditions: Dict[str, Any]
    chain_completion_probability: float
    created_timestamp: datetime

@dataclass
class ConflictResolution:
    """衝突解決結果"""
    conflict_id: str
    conflicting_event_ids: List[str]
    resolution_strategy: str
    resolved_weights: Dict[str, float]  # 各事件的解決權重
    resolution_confidence: float
    impact_adjustment: float
    resolution_timestamp: datetime

class CompositeEventProcessor:
    """複合事件處理器"""
    
    def __init__(self):
        # 事件關聯網路
        self.event_network = nx.DiGraph()
        
        # 資料存儲
        self.active_events = {}           # 當前活躍事件
        self.composite_events = {}        # 複合事件
        self.event_chains = {}           # 事件鏈
        self.conflict_resolutions = {}   # 衝突解決記錄
        self.relation_database = {}      # 關聯數據庫
        
        # 處理歷史
        self.processing_history = deque(maxlen=500)
        
        # 配置
        self.config = {
            "min_correlation_threshold": 0.3,
            "max_composite_events": 10,
            "conflict_resolution_timeout": 300,  # 5分鐘
            "chain_max_length": 8,
            "relation_decay_hours": 168,  # 7天
            "composite_confidence_threshold": 0.4,
            "priority_weights": {
                CompositePriority.CRITICAL: 1.0,
                CompositePriority.HIGH: 0.8, 
                CompositePriority.MEDIUM: 0.6,
                CompositePriority.LOW: 0.4,
                CompositePriority.MONITORING: 0.2
            }
        }
        
        # 統計數據
        self.stats = {
            "total_composite_events": 0,
            "active_composite_events": 0,
            "total_conflicts_resolved": 0,
            "event_chains_detected": 0,
            "avg_composite_accuracy": 0.0,
            "relation_learning_count": 0,
            "processing_efficiency": 0.0
        }
        
        # 初始化基礎關聯
        self._initialize_base_relations()
        logger.info("✅ 複合事件處理器初始化完成")
    
    def _initialize_base_relations(self):
        """初始化基礎事件關聯"""
        base_relations = [
            # FOMC會議 → 市場波動
            EventRelation(
                source_event_id="fomc_meeting",
                target_event_id="volatility_spike",
                relation_type=EventRelationType.CAUSAL,
                correlation_strength=0.85,
                time_lag_hours=2.0,
                confidence=0.78,
                historical_validation_count=24,
                last_observed=datetime.now() - timedelta(days=30)
            ),
            
            # 技術突破 → 成交量激增
            EventRelation(
                source_event_id="technical_breakout",
                target_event_id="volume_spike",
                relation_type=EventRelationType.CAUSAL,
                correlation_strength=0.72,
                time_lag_hours=1.0,
                confidence=0.68,
                historical_validation_count=89,
                last_observed=datetime.now() - timedelta(days=7)
            ),
            
            # 宏觀事件 ↔ 流動性變化 (相關)
            EventRelation(
                source_event_id="macro_economic_event",
                target_event_id="liquidity_change",
                relation_type=EventRelationType.CORRELATED,
                correlation_strength=0.65,
                time_lag_hours=4.0,
                confidence=0.71,
                historical_validation_count=156,
                last_observed=datetime.now() - timedelta(days=14)
            ),
            
            # 牛市信號 ↔ 熊市信號 (衝突)
            EventRelation(
                source_event_id="bullish_signal",
                target_event_id="bearish_signal",
                relation_type=EventRelationType.CONFLICTING,
                correlation_strength=0.90,
                time_lag_hours=0.0,
                confidence=0.95,
                historical_validation_count=234,
                last_observed=datetime.now() - timedelta(days=2)
            ),
            
            # 成交量異常 → 價格突破 (序列)
            EventRelation(
                source_event_id="volume_anomaly",
                target_event_id="price_breakout",
                relation_type=EventRelationType.SEQUENTIAL,
                correlation_strength=0.58,
                time_lag_hours=6.0,
                confidence=0.62,
                historical_validation_count=78,
                last_observed=datetime.now() - timedelta(days=5)
            )
        ]
        
        for relation in base_relations:
            relation_key = f"{relation.source_event_id}_{relation.target_event_id}"
            self.relation_database[relation_key] = relation
            
            # 添加到網路圖
            self.event_network.add_edge(
                relation.source_event_id,
                relation.target_event_id,
                relation_type=relation.relation_type,
                weight=relation.correlation_strength
            )
        
        logger.info(f"🕸️ 初始化 {len(base_relations)} 個基礎事件關聯")
    
    async def process_events(self, events: List[Dict]) -> List[CompositeEvent]:
        """處理事件並識別複合事件"""
        try:
            # 更新活躍事件
            self._update_active_events(events)
            
            # 識別事件關聯
            detected_relations = await self._detect_event_relations()
            
            # 構建複合事件
            composite_events = await self._build_composite_events(detected_relations)
            
            # 解決衝突
            resolved_composites = await self._resolve_conflicts(composite_events)
            
            # 檢測事件鏈
            event_chains = await self._detect_event_chains()
            
            # 更新統計
            self.stats["total_composite_events"] += len(resolved_composites)
            self.stats["active_composite_events"] = len(resolved_composites)
            
            logger.info(f"🔗 處理完成: {len(resolved_composites)} 個複合事件, {len(event_chains)} 個事件鏈")
            return resolved_composites
            
        except Exception as e:
            logger.error(f"❌ 複合事件處理失敗: {e}")
            return []
    
    def _update_active_events(self, events: List[Dict]):
        """更新活躍事件列表"""
        current_time = datetime.now()
        
        # 添加新事件
        for event in events:
            event_id = event.get("event_id", f"event_{len(self.active_events)}")
            self.active_events[event_id] = {
                **event,
                "last_updated": current_time
            }
        
        # 清理過期事件
        expired_events = []
        for event_id, event_data in self.active_events.items():
            last_updated = event_data.get("last_updated", current_time)
            if (current_time - last_updated).total_seconds() > 3600:  # 1小時過期
                expired_events.append(event_id)
        
        for event_id in expired_events:
            del self.active_events[event_id]
    
    async def _detect_event_relations(self) -> List[EventRelation]:
        """檢測事件間關聯"""
        try:
            detected_relations = []
            active_event_ids = list(self.active_events.keys())
            
            # 檢查每對事件的關聯
            for i, event_id_1 in enumerate(active_event_ids):
                for event_id_2 in active_event_ids[i+1:]:
                    relation = await self._analyze_event_pair(event_id_1, event_id_2)
                    if relation:
                        detected_relations.append(relation)
            
            # 學習新關聯
            await self._learn_new_relations(detected_relations)
            
            return detected_relations
            
        except Exception as e:
            logger.error(f"❌ 事件關聯檢測失敗: {e}")
            return []
    
    async def _analyze_event_pair(self, event_id_1: str, event_id_2: str) -> Optional[EventRelation]:
        """分析兩個事件間的關聯"""
        try:
            event_1 = self.active_events.get(event_id_1)
            event_2 = self.active_events.get(event_id_2)
            
            if not event_1 or not event_2:
                return None
            
            # 檢查是否已有已知關聯
            relation_key = f"{event_id_1}_{event_id_2}"
            reverse_key = f"{event_id_2}_{event_id_1}"
            
            if relation_key in self.relation_database:
                return self.relation_database[relation_key]
            elif reverse_key in self.relation_database:
                return self.relation_database[reverse_key]
            
            # 計算新關聯
            correlation_strength = self._calculate_correlation(event_1, event_2)
            
            if correlation_strength < self.config["min_correlation_threshold"]:
                return None
            
            # 確定關聯類型
            relation_type = self._determine_relation_type(event_1, event_2)
            
            # 計算時間滯後
            time_lag = self._calculate_time_lag(event_1, event_2)
            
            # 創建新關聯
            new_relation = EventRelation(
                source_event_id=event_id_1,
                target_event_id=event_id_2,
                relation_type=relation_type,
                correlation_strength=correlation_strength,
                time_lag_hours=time_lag,
                confidence=correlation_strength * 0.8,  # 新關聯的信心度較低
                historical_validation_count=1,
                last_observed=datetime.now()
            )
            
            return new_relation
            
        except Exception as e:
            logger.error(f"❌ 事件對分析失敗: {e}")
            return None
    
    def _calculate_correlation(self, event_1: Dict, event_2: Dict) -> float:
        """計算事件相關性"""
        try:
            # 基於事件屬性計算相關性
            correlation_factors = []
            
            # 1. 時間相關性
            time_1 = event_1.get("event_time", datetime.now())
            time_2 = event_2.get("event_time", datetime.now())
            if isinstance(time_1, str):
                time_1 = datetime.fromisoformat(time_1.replace('Z', '+00:00'))
            if isinstance(time_2, str):
                time_2 = datetime.fromisoformat(time_2.replace('Z', '+00:00'))
            
            time_diff_hours = abs((time_1 - time_2).total_seconds() / 3600)
            time_correlation = max(0.0, 1.0 - (time_diff_hours / 48))  # 48小時內相關性線性衰減
            correlation_factors.append(time_correlation * 0.3)
            
            # 2. 影響標的相關性
            symbols_1 = set(event_1.get("affected_symbols", []))
            symbols_2 = set(event_2.get("affected_symbols", []))
            if symbols_1 or symbols_2:
                symbol_overlap = len(symbols_1.intersection(symbols_2)) / len(symbols_1.union(symbols_2))
                correlation_factors.append(symbol_overlap * 0.4)
            
            # 3. 事件類型相關性
            category_1 = event_1.get("event_category", "unknown")
            category_2 = event_2.get("event_category", "unknown")
            category_correlation = 1.0 if category_1 == category_2 else 0.5
            correlation_factors.append(category_correlation * 0.2)
            
            # 4. 影響幅度相關性
            impact_1 = event_1.get("expected_impact_magnitude", 0.5)
            impact_2 = event_2.get("expected_impact_magnitude", 0.5)
            impact_correlation = 1.0 - abs(impact_1 - impact_2)
            correlation_factors.append(impact_correlation * 0.1)
            
            return sum(correlation_factors)
            
        except Exception as e:
            logger.error(f"❌ 相關性計算失敗: {e}")
            return 0.0
    
    def _determine_relation_type(self, event_1: Dict, event_2: Dict) -> EventRelationType:
        """確定關聯類型"""
        try:
            # 基於事件特徵確定關聯類型
            direction_1 = event_1.get("direction", "neutral")
            direction_2 = event_2.get("direction", "neutral")
            
            # 檢查衝突關係
            if (direction_1 == "bullish" and direction_2 == "bearish") or \
               (direction_1 == "bearish" and direction_2 == "bullish"):
                return EventRelationType.CONFLICTING
            
            # 檢查增強關係
            if direction_1 == direction_2 and direction_1 != "neutral":
                return EventRelationType.REINFORCING
            
            # 檢查因果關係 (基於事件類型)
            category_1 = event_1.get("event_category", "")
            category_2 = event_2.get("event_category", "")
            
            causal_pairs = [
                ("macro_economic", "volatility_spike"),
                ("technical_breakout", "volume_anomaly"),
                ("news_event", "sentiment_change")
            ]
            
            for cause, effect in causal_pairs:
                if (cause in category_1 and effect in category_2) or \
                   (effect in category_1 and cause in category_2):
                    return EventRelationType.CAUSAL
            
            # 默認為相關關係
            return EventRelationType.CORRELATED
            
        except Exception as e:
            logger.error(f"❌ 關聯類型確定失敗: {e}")
            return EventRelationType.CORRELATED
    
    def _calculate_time_lag(self, event_1: Dict, event_2: Dict) -> float:
        """計算時間滯後"""
        try:
            time_1 = event_1.get("event_time", datetime.now())
            time_2 = event_2.get("event_time", datetime.now())
            
            if isinstance(time_1, str):
                time_1 = datetime.fromisoformat(time_1.replace('Z', '+00:00'))
            if isinstance(time_2, str):
                time_2 = datetime.fromisoformat(time_2.replace('Z', '+00:00'))
            
            time_diff = (time_2 - time_1).total_seconds() / 3600  # 轉換為小時
            return abs(time_diff)
            
        except Exception as e:
            logger.error(f"❌ 時間滯後計算失敗: {e}")
            return 0.0
    
    async def _learn_new_relations(self, detected_relations: List[EventRelation]):
        """學習新的事件關聯"""
        try:
            learned_count = 0
            
            for relation in detected_relations:
                relation_key = f"{relation.source_event_id}_{relation.target_event_id}"
                
                if relation_key not in self.relation_database:
                    # 添加新關聯
                    self.relation_database[relation_key] = relation
                    
                    # 更新網路圖
                    self.event_network.add_edge(
                        relation.source_event_id,
                        relation.target_event_id,
                        relation_type=relation.relation_type,
                        weight=relation.correlation_strength
                    )
                    
                    learned_count += 1
                else:
                    # 更新已有關聯
                    existing_relation = self.relation_database[relation_key]
                    existing_relation.historical_validation_count += 1
                    existing_relation.last_observed = datetime.now()
                    
                    # 調整信心度
                    existing_relation.confidence = min(1.0, 
                        existing_relation.confidence * 0.9 + relation.confidence * 0.1
                    )
            
            self.stats["relation_learning_count"] += learned_count
            logger.info(f"🧠 學習 {learned_count} 個新的事件關聯")
            
        except Exception as e:
            logger.error(f"❌ 關聯學習失敗: {e}")
    
    async def _build_composite_events(self, relations: List[EventRelation]) -> List[CompositeEvent]:
        """構建複合事件"""
        try:
            composite_events = []
            processed_events = set()
            
            # 根據關聯構建複合事件
            for relation in relations:
                if relation.source_event_id in processed_events or \
                   relation.target_event_id in processed_events:
                    continue
                
                # 找到相關的事件組
                event_group = self._find_connected_events(relation, relations)
                
                if len(event_group) >= 2:  # 至少需要2個事件
                    composite = await self._create_composite_event(event_group, relations)
                    if composite:
                        composite_events.append(composite)
                        processed_events.update(event_group)
            
            return composite_events
            
        except Exception as e:
            logger.error(f"❌ 複合事件構建失敗: {e}")
            return []
    
    def _find_connected_events(self, seed_relation: EventRelation, 
                              all_relations: List[EventRelation]) -> Set[str]:
        """找到連接的事件組"""
        try:
            connected_events = {seed_relation.source_event_id, seed_relation.target_event_id}
            
            # 廣度優先搜索找到所有連接的事件
            to_explore = list(connected_events)
            explored = set()
            
            while to_explore:
                current_event = to_explore.pop(0)
                if current_event in explored:
                    continue
                explored.add(current_event)
                
                # 找到與當前事件相關的所有關聯
                for relation in all_relations:
                    if relation.source_event_id == current_event:
                        if relation.target_event_id not in connected_events:
                            connected_events.add(relation.target_event_id)
                            to_explore.append(relation.target_event_id)
                    elif relation.target_event_id == current_event:
                        if relation.source_event_id not in connected_events:
                            connected_events.add(relation.source_event_id)
                            to_explore.append(relation.source_event_id)
            
            return connected_events
            
        except Exception as e:
            logger.error(f"❌ 連接事件查找失敗: {e}")
            return set()
    
    async def _create_composite_event(self, event_group: Set[str], 
                                    relations: List[EventRelation]) -> Optional[CompositeEvent]:
        """創建複合事件"""
        try:
            event_ids = list(event_group)
            
            # 獲取相關關聯
            relevant_relations = [
                r for r in relations 
                if r.source_event_id in event_group and r.target_event_id in event_group
            ]
            
            # 計算聚合信心度
            confidences = []
            for event_id in event_ids:
                event = self.active_events.get(event_id)
                if event:
                    confidences.append(event.get("confidence", 0.5))
            
            if not confidences:
                return None
            
            aggregate_confidence = np.mean(confidences)
            
            # 檢查信心度閾值
            if aggregate_confidence < self.config["composite_confidence_threshold"]:
                return None
            
            # 計算複合影響幅度
            impact_magnitudes = []
            for event_id in event_ids:
                event = self.active_events.get(event_id)
                if event:
                    impact_magnitudes.append(event.get("expected_impact_magnitude", 0.0))
            
            composite_impact = np.sqrt(np.sum(np.square(impact_magnitudes)))  # 向量和
            composite_impact = min(1.0, composite_impact)
            
            # 確定主導事件類別
            categories = []
            for event_id in event_ids:
                event = self.active_events.get(event_id)
                if event:
                    categories.append(event.get("event_category", "unknown"))
            
            dominant_category = max(set(categories), key=categories.count) if categories else "composite"
            
            # 計算預期開始時間
            start_times = []
            for event_id in event_ids:
                event = self.active_events.get(event_id)
                if event:
                    event_time = event.get("event_time", datetime.now())
                    if isinstance(event_time, str):
                        event_time = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
                    start_times.append(event_time)
            
            expected_start = min(start_times) if start_times else datetime.now()
            
            # 收集影響標的
            all_symbols = set()
            for event_id in event_ids:
                event = self.active_events.get(event_id)
                if event:
                    all_symbols.update(event.get("affected_symbols", []))
            
            # 確定優先級
            priority = self._determine_composite_priority(aggregate_confidence, composite_impact)
            
            # 創建複合事件
            composite = CompositeEvent(
                composite_id=f"composite_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(event_ids)}",
                component_event_ids=event_ids,
                event_relations=relevant_relations,
                composite_priority=priority,
                aggregate_confidence=aggregate_confidence,
                composite_impact_magnitude=composite_impact,
                expected_start_time=expected_start,
                expected_duration_hours=self._estimate_composite_duration(event_ids),
                affected_symbols=list(all_symbols),
                dominant_event_category=dominant_category,
                conflict_resolution_strategy="weighted_average",  # 默認策略
                composite_timestamp=datetime.now()
            )
            
            return composite
            
        except Exception as e:
            logger.error(f"❌ 複合事件創建失敗: {e}")
            return None
    
    def _determine_composite_priority(self, confidence: float, impact: float) -> CompositePriority:
        """確定複合事件優先級"""
        composite_score = (confidence * 0.6 + impact * 0.4)
        
        if composite_score >= 0.85:
            return CompositePriority.CRITICAL
        elif composite_score >= 0.7:
            return CompositePriority.HIGH
        elif composite_score >= 0.5:
            return CompositePriority.MEDIUM
        elif composite_score >= 0.3:
            return CompositePriority.LOW
        else:
            return CompositePriority.MONITORING
    
    def _estimate_composite_duration(self, event_ids: List[str]) -> float:
        """估算複合事件持續時間"""
        try:
            durations = []
            for event_id in event_ids:
                event = self.active_events.get(event_id)
                if event:
                    duration = event.get("expected_duration_hours", 24.0)
                    durations.append(duration)
            
            if durations:
                # 使用最長持續時間作為複合事件持續時間
                return max(durations)
            else:
                return 24.0  # 默認24小時
                
        except Exception as e:
            logger.error(f"❌ 複合事件持續時間估算失敗: {e}")
            return 24.0
    
    async def _resolve_conflicts(self, composite_events: List[CompositeEvent]) -> List[CompositeEvent]:
        """解決衝突事件"""
        try:
            resolved_events = []
            conflict_groups = self._identify_conflicts(composite_events)
            
            for conflict_group in conflict_groups:
                if len(conflict_group) > 1:
                    # 有衝突需要解決
                    resolution = await self._resolve_conflict_group(conflict_group)
                    if resolution:
                        # 應用衝突解決
                        resolved_event = self._apply_conflict_resolution(conflict_group, resolution)
                        if resolved_event:
                            resolved_events.append(resolved_event)
                else:
                    # 無衝突，直接添加
                    resolved_events.append(conflict_group[0])
            
            return resolved_events
            
        except Exception as e:
            logger.error(f"❌ 衝突解決失敗: {e}")
            return composite_events
    
    def _identify_conflicts(self, composite_events: List[CompositeEvent]) -> List[List[CompositeEvent]]:
        """識別衝突事件組"""
        try:
            conflict_groups = []
            processed = set()
            
            for i, event_1 in enumerate(composite_events):
                if i in processed:
                    continue
                
                conflict_group = [event_1]
                processed.add(i)
                
                for j, event_2 in enumerate(composite_events[i+1:], i+1):
                    if j in processed:
                        continue
                    
                    # 檢查是否有衝突關聯
                    has_conflict = False
                    for relation in event_1.event_relations:
                        if (relation.relation_type == EventRelationType.CONFLICTING and
                            (relation.source_event_id in event_2.component_event_ids or
                             relation.target_event_id in event_2.component_event_ids)):
                            has_conflict = True
                            break
                    
                    if has_conflict:
                        conflict_group.append(event_2)
                        processed.add(j)
                
                conflict_groups.append(conflict_group)
            
            return conflict_groups
            
        except Exception as e:
            logger.error(f"❌ 衝突識別失敗: {e}")
            return [[event] for event in composite_events]
    
    async def _resolve_conflict_group(self, conflict_group: List[CompositeEvent]) -> Optional[ConflictResolution]:
        """解決衝突組"""
        try:
            if len(conflict_group) <= 1:
                return None
            
            conflict_id = f"conflict_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            event_ids = [event.composite_id for event in conflict_group]
            
            # 計算權重 (基於信心度和影響)
            weights = {}
            total_weight = 0.0
            
            for event in conflict_group:
                weight = (event.aggregate_confidence * 0.7 + 
                         event.composite_impact_magnitude * 0.3)
                weights[event.composite_id] = weight
                total_weight += weight
            
            # 標準化權重
            if total_weight > 0:
                for event_id in weights:
                    weights[event_id] /= total_weight
            
            # 計算解決信心度
            confidence_scores = [event.aggregate_confidence for event in conflict_group]
            resolution_confidence = np.mean(confidence_scores) * 0.8  # 衝突降低信心度
            
            # 計算影響調整
            impact_adjustment = 0.9  # 衝突通常降低整體影響
            
            resolution = ConflictResolution(
                conflict_id=conflict_id,
                conflicting_event_ids=event_ids,
                resolution_strategy="confidence_weighted",
                resolved_weights=weights,
                resolution_confidence=resolution_confidence,
                impact_adjustment=impact_adjustment,
                resolution_timestamp=datetime.now()
            )
            
            # 保存解決記錄
            self.conflict_resolutions[conflict_id] = resolution
            self.stats["total_conflicts_resolved"] += 1
            
            return resolution
            
        except Exception as e:
            logger.error(f"❌ 衝突組解決失敗: {e}")
            return None
    
    def _apply_conflict_resolution(self, conflict_group: List[CompositeEvent], 
                                 resolution: ConflictResolution) -> Optional[CompositeEvent]:
        """應用衝突解決"""
        try:
            if not conflict_group:
                return None
            
            # 選擇主導事件 (權重最高的)
            dominant_event = max(conflict_group, 
                               key=lambda e: resolution.resolved_weights.get(e.composite_id, 0))
            
            # 調整主導事件的屬性
            resolved_event = CompositeEvent(
                composite_id=f"resolved_{dominant_event.composite_id}",
                component_event_ids=dominant_event.component_event_ids,
                event_relations=dominant_event.event_relations,
                composite_priority=dominant_event.composite_priority,
                aggregate_confidence=resolution.resolution_confidence,
                composite_impact_magnitude=dominant_event.composite_impact_magnitude * resolution.impact_adjustment,
                expected_start_time=dominant_event.expected_start_time,
                expected_duration_hours=dominant_event.expected_duration_hours,
                affected_symbols=dominant_event.affected_symbols,
                dominant_event_category=dominant_event.dominant_event_category,
                conflict_resolution_strategy=resolution.resolution_strategy,
                composite_timestamp=datetime.now()
            )
            
            return resolved_event
            
        except Exception as e:
            logger.error(f"❌ 衝突解決應用失敗: {e}")
            return None
    
    async def _detect_event_chains(self) -> List[EventChain]:
        """檢測事件鏈"""
        try:
            event_chains = []
            
            # 使用網路圖檢測路徑
            if len(self.event_network.nodes) < 2:
                return []
            
            # 找到所有可能的路徑
            nodes = list(self.event_network.nodes)
            for start_node in nodes:
                for end_node in nodes:
                    if start_node != end_node:
                        try:
                            # 找到所有簡單路徑
                            paths = list(nx.all_simple_paths(
                                self.event_network, 
                                start_node, 
                                end_node, 
                                cutoff=self.config["chain_max_length"]
                            ))
                            
                            for path in paths:
                                if len(path) >= 3:  # 至少3個事件才組成鏈
                                    chain = await self._create_event_chain(path)
                                    if chain:
                                        event_chains.append(chain)
                                        
                        except nx.NetworkXNoPath:
                            continue
            
            # 保存事件鏈
            for chain in event_chains:
                self.event_chains[chain.chain_id] = chain
            
            self.stats["event_chains_detected"] += len(event_chains)
            return event_chains
            
        except Exception as e:
            logger.error(f"❌ 事件鏈檢測失敗: {e}")
            return []
    
    async def _create_event_chain(self, event_path: List[str]) -> Optional[EventChain]:
        """創建事件鏈"""
        try:
            if len(event_path) < 3:
                return None
            
            # 計算鏈的信心度
            path_confidences = []
            for i in range(len(event_path) - 1):
                relation_key = f"{event_path[i]}_{event_path[i+1]}"
                if relation_key in self.relation_database:
                    relation = self.relation_database[relation_key]
                    path_confidences.append(relation.confidence)
            
            if not path_confidences:
                return None
            
            chain_confidence = np.prod(path_confidences) ** (1.0 / len(path_confidences))  # 幾何平均
            
            # 計算總持續時間
            total_duration = 0.0
            for i in range(len(event_path) - 1):
                relation_key = f"{event_path[i]}_{event_path[i+1]}"
                if relation_key in self.relation_database:
                    relation = self.relation_database[relation_key]
                    total_duration += relation.time_lag_hours
            
            # 計算完成概率
            completion_probability = chain_confidence * 0.8  # 鏈越長完成概率越低
            
            chain = EventChain(
                chain_id=f"chain_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(event_path)}",
                event_sequence=event_path,
                chain_confidence=chain_confidence,
                total_expected_duration=total_duration,
                chain_impact_profile={f"stage_{i}": 1.0/len(event_path) for i in range(len(event_path))},
                trigger_conditions={"chain_start": event_path[0]},
                chain_completion_probability=completion_probability,
                created_timestamp=datetime.now()
            )
            
            return chain
            
        except Exception as e:
            logger.error(f"❌ 事件鏈創建失敗: {e}")
            return None
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """獲取處理器摘要"""
        try:
            return {
                "processor_status": "active",
                "active_events_count": len(self.active_events),
                "total_relations": len(self.relation_database),
                "active_composite_events": self.stats["active_composite_events"],
                "event_chains_active": len(self.event_chains),
                "conflicts_resolved_today": self.stats["total_conflicts_resolved"],
                "processing_stats": self.stats,
                "network_complexity": {
                    "nodes": len(self.event_network.nodes),
                    "edges": len(self.event_network.edges),
                    "density": nx.density(self.event_network) if len(self.event_network.nodes) > 1 else 0.0
                },
                "last_processing_time": datetime.now().isoformat(),
                "system_health": "good" if self.stats["avg_composite_accuracy"] > 0.6 else "needs_attention"
            }
            
        except Exception as e:
            logger.error(f"❌ 處理器摘要生成失敗: {e}")
            return {"processor_status": "error", "error": str(e)}

# 全局實例
composite_event_processor = CompositeEventProcessor()
