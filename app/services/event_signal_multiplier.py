"""
事件信號乘數框架 - Trading X Phase 3
基於重大市場事件動態調整信號權重的乘數系統
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import asyncio
from collections import deque

logger = logging.getLogger(__name__)

class EventType(Enum):
    """市場事件類型"""
    # 宏觀經濟事件
    FOMC_MEETING = "fomc_meeting"           # 聯準會會議
    NFP_RELEASE = "nfp_release"             # 非農就業數據
    CPI_RELEASE = "cpi_release"             # 通脹數據
    GDP_RELEASE = "gdp_release"             # GDP 數據
    
    # 加密貨幣特定事件
    HALVING_EVENT = "halving_event"         # 比特幣減半
    MAJOR_LISTING = "major_listing"         # 主要交易所上幣
    PROTOCOL_UPGRADE = "protocol_upgrade"    # 協議升級
    REGULATORY_NEWS = "regulatory_news"      # 監管消息
    
    # 市場結構事件
    FLASH_CRASH = "flash_crash"             # 閃崩事件
    WHALE_MOVEMENT = "whale_movement"       # 巨鯨轉移
    EXCHANGE_INCIDENT = "exchange_incident"  # 交易所事件
    MARKET_MANIPULATION = "market_manipulation" # 市場操縱
    
    # 技術指標事件
    GOLDEN_CROSS = "golden_cross"           # 黃金交叉
    DEATH_CROSS = "death_cross"             # 死亡交叉
    BREAKOUT_EVENT = "breakout_event"       # 突破事件
    VOLUME_SPIKE = "volume_spike"           # 成交量異常

class EventSeverity(Enum):
    """事件嚴重程度"""
    LOW = "low"           # 輕微影響 (1.0-1.2倍)
    MEDIUM = "medium"     # 中等影響 (1.2-1.5倍)
    HIGH = "high"         # 高度影響 (1.5-2.0倍)
    CRITICAL = "critical" # 極度影響 (2.0-3.0倍)

class EventDirection(Enum):
    """事件方向性影響"""
    BULLISH = "bullish"     # 利多
    BEARISH = "bearish"     # 利空
    NEUTRAL = "neutral"     # 中性
    VOLATILE = "volatile"   # 增加波動

@dataclass
class MarketEvent:
    """市場事件定義"""
    event_id: str
    event_type: EventType
    title: str
    description: str
    
    # 事件屬性
    severity: EventSeverity
    direction: EventDirection
    confidence: float              # 事件確定性 (0.0-1.0)
    
    # 時間屬性
    event_time: datetime
    duration_hours: int           # 事件影響持續時間
    preparation_hours: int = 2    # 事件前準備時間
    
    # 影響範圍
    affected_symbols: List[str] = field(default_factory=list)
    affected_sectors: List[str] = field(default_factory=list)
    
    # 權重乘數配置
    signal_multipliers: Dict[str, float] = field(default_factory=dict)
    
    # 元數據
    created_time: datetime = field(default_factory=datetime.now)
    source: str = "system"
    tags: List[str] = field(default_factory=list)

@dataclass
class EventMultiplierResult:
    """事件乘數計算結果"""
    event_id: str
    applied_multipliers: Dict[str, float]
    total_multiplier_effect: float
    confidence_adjustment: float
    risk_adjustment: float
    explanation: str
    calculation_time: datetime = field(default_factory=datetime.now)

class EventSignalMultiplier:
    """事件信號乘數管理器"""
    
    def __init__(self):
        self.active_events: Dict[str, MarketEvent] = {}
        self.event_history: deque = deque(maxlen=1000)
        self.event_templates: Dict[EventType, Dict] = {}
        
        # 配置參數
        self.max_total_multiplier = 3.0      # 最大總乘數
        self.min_total_multiplier = 0.5      # 最小總乘數
        self.decay_factor = 0.95             # 時間衰減因子
        
        # 統計數據
        self.stats = {
            "total_events": 0,
            "active_events": 0,
            "multiplier_calculations": 0,
            "average_impact": 0.0
        }
        
        # 初始化事件模板
        self._initialize_event_templates()
        
        logger.info("✅ 事件信號乘數框架初始化完成")
    
    def _initialize_event_templates(self):
        """初始化事件模板"""
        
        # FOMC 會議模板
        self.event_templates[EventType.FOMC_MEETING] = {
            "default_multipliers": {
                "market_condition_weight": 1.8,    # 市場條件權重大幅提升
                "fear_greed_weight": 2.0,          # 情緒指標權重提升
                "regime_analysis_weight": 1.5,     # 制度分析權重提升
                "technical_analysis_weight": 0.8,  # 技術分析權重降低
                "precision_filter_weight": 1.2    # 精準篩選輕微提升
            },
            "duration_hours": 48,
            "preparation_hours": 6
        }
        
        # 非農就業數據模板
        self.event_templates[EventType.NFP_RELEASE] = {
            "default_multipliers": {
                "market_condition_weight": 2.2,
                "fear_greed_weight": 1.8,
                "technical_analysis_weight": 0.7,
                "trend_alignment_weight": 1.4
            },
            "duration_hours": 8,
            "preparation_hours": 2
        }
        
        # 比特幣減半事件模板
        self.event_templates[EventType.HALVING_EVENT] = {
            "default_multipliers": {
                "regime_analysis_weight": 2.5,     # 制度變化最重要
                "trend_alignment_weight": 2.0,     # 長期趨勢重要
                "smart_money_weight": 1.8,         # 聰明資金流向重要
                "fear_greed_weight": 1.5,
                "precision_filter_weight": 0.8     # 短期精準度降低
            },
            "duration_hours": 168,  # 7天影響
            "preparation_hours": 24
        }
        
        # 閃崩事件模板
        self.event_templates[EventType.FLASH_CRASH] = {
            "default_multipliers": {
                "precision_filter_weight": 2.5,    # 精準篩選最重要
                "market_condition_weight": 2.2,    # 市場條件緊急
                "market_depth_weight": 2.0,        # 市場深度重要
                "technical_analysis_weight": 0.6,  # 技術分析失效
                "fear_greed_weight": 1.8           # 情緒極度重要
            },
            "duration_hours": 6,
            "preparation_hours": 0  # 無法預測
        }
        
        # 監管消息模板
        self.event_templates[EventType.REGULATORY_NEWS] = {
            "default_multipliers": {
                "fear_greed_weight": 2.2,          # 情緒反應強烈
                "market_condition_weight": 1.8,
                "regime_analysis_weight": 1.6,     # 制度變化重要
                "smart_money_weight": 1.4,         # 資金流向重要
                "technical_analysis_weight": 0.7
            },
            "duration_hours": 72,
            "preparation_hours": 1
        }
        
        # 成交量異常模板
        self.event_templates[EventType.VOLUME_SPIKE] = {
            "default_multipliers": {
                "technical_analysis_weight": 1.8,  # 技術分析重要
                "market_condition_weight": 1.6,
                "precision_filter_weight": 1.4,
                "market_depth_weight": 1.5
            },
            "duration_hours": 4,
            "preparation_hours": 0
        }
        
        logger.info(f"📋 初始化 {len(self.event_templates)} 個事件模板")
    
    def create_event(self, 
                    event_type: EventType,
                    title: str,
                    severity: EventSeverity,
                    direction: EventDirection,
                    event_time: datetime,
                    affected_symbols: List[str] = None,
                    custom_multipliers: Dict[str, float] = None,
                    confidence: float = 0.8) -> str:
        """
        創建新的市場事件
        
        Args:
            event_type: 事件類型
            title: 事件標題
            severity: 事件嚴重程度
            direction: 事件方向性
            event_time: 事件時間
            affected_symbols: 受影響的交易對
            custom_multipliers: 自定義乘數
            confidence: 事件確定性
            
        Returns:
            str: 事件ID
        """
        event_id = f"{event_type.value}_{int(event_time.timestamp())}"
        
        # 獲取事件模板
        template = self.event_templates.get(event_type, {})
        
        # 建立信號乘數
        signal_multipliers = template.get("default_multipliers", {}).copy()
        if custom_multipliers:
            signal_multipliers.update(custom_multipliers)
        
        # 根據嚴重程度調整乘數
        severity_factor = {
            EventSeverity.LOW: 1.0,
            EventSeverity.MEDIUM: 1.2,
            EventSeverity.HIGH: 1.5,
            EventSeverity.CRITICAL: 2.0
        }[severity]
        
        # 應用嚴重程度調整
        adjusted_multipliers = {}
        for signal_name, multiplier in signal_multipliers.items():
            if multiplier > 1.0:
                # 放大正面影響
                adjusted_multipliers[signal_name] = 1.0 + (multiplier - 1.0) * severity_factor
            else:
                # 放大負面影響
                adjusted_multipliers[signal_name] = 1.0 - (1.0 - multiplier) * severity_factor
        
        # 創建事件對象
        event = MarketEvent(
            event_id=event_id,
            event_type=event_type,
            title=title,
            description=f"{severity.value.upper()} {direction.value} 事件: {title}",
            severity=severity,
            direction=direction,
            confidence=confidence,
            event_time=event_time,
            duration_hours=template.get("duration_hours", 24),
            preparation_hours=template.get("preparation_hours", 2),
            affected_symbols=affected_symbols or [],
            signal_multipliers=adjusted_multipliers
        )
        
        # 添加到活躍事件
        self.active_events[event_id] = event
        self.event_history.append(event)
        self.stats["total_events"] += 1
        self.stats["active_events"] = len(self.active_events)
        
        logger.info(f"📅 創建事件: {title} (ID: {event_id}, 嚴重程度: {severity.value})")
        
        return event_id
    
    def calculate_event_multipliers(self, 
                                  symbol: str,
                                  current_time: datetime = None) -> EventMultiplierResult:
        """
        計算當前時間的事件乘數
        
        Args:
            symbol: 交易對
            current_time: 當前時間
            
        Returns:
            EventMultiplierResult: 乘數計算結果
        """
        if current_time is None:
            current_time = datetime.now()
        
        # 清理過期事件
        self._cleanup_expired_events(current_time)
        
        applied_multipliers = {}
        total_multiplier_effects = []
        explanations = []
        
        for event_id, event in self.active_events.items():
            # 檢查事件是否影響該交易對
            if event.affected_symbols and symbol not in event.affected_symbols:
                continue
            
            # 計算時間衰減
            event_start = event.event_time - timedelta(hours=event.preparation_hours)
            event_end = event.event_time + timedelta(hours=event.duration_hours)
            
            if event_start <= current_time <= event_end:
                # 計算時間衰減因子
                total_duration = event.duration_hours + event.preparation_hours
                elapsed_hours = (current_time - event_start).total_seconds() / 3600
                
                # 使用高斯衰減 (事件時間點影響最大)
                time_to_event = abs((current_time - event.event_time).total_seconds() / 3600)
                decay_factor = max(0.1, 1.0 - (time_to_event / total_duration) ** 2)
                
                # 應用信心度調整
                confidence_factor = 0.5 + 0.5 * event.confidence
                
                # 計算該事件的乘數
                for signal_name, base_multiplier in event.signal_multipliers.items():
                    adjusted_multiplier = 1.0 + (base_multiplier - 1.0) * decay_factor * confidence_factor
                    
                    if signal_name not in applied_multipliers:
                        applied_multipliers[signal_name] = []
                    
                    applied_multipliers[signal_name].append({
                        "event_id": event_id,
                        "multiplier": adjusted_multiplier,
                        "decay_factor": decay_factor,
                        "confidence_factor": confidence_factor
                    })
                
                total_multiplier_effects.append(decay_factor * confidence_factor)
                explanations.append(f"{event.title} (衰減: {decay_factor:.2f}, 信心: {confidence_factor:.2f})")
        
        # 合併多個事件的乘數影響
        final_multipliers = {}
        for signal_name, multiplier_list in applied_multipliers.items():
            if len(multiplier_list) == 1:
                # 單一事件
                final_multipliers[signal_name] = multiplier_list[0]["multiplier"]
            else:
                # 多個事件：使用加權平均
                total_weight = sum(m["decay_factor"] * m["confidence_factor"] for m in multiplier_list)
                if total_weight > 0:
                    weighted_multiplier = sum(
                        m["multiplier"] * m["decay_factor"] * m["confidence_factor"] 
                        for m in multiplier_list
                    ) / total_weight
                    final_multipliers[signal_name] = weighted_multiplier
                else:
                    final_multipliers[signal_name] = 1.0
        
        # 應用總乘數限制
        for signal_name in final_multipliers:
            final_multipliers[signal_name] = max(
                self.min_total_multiplier,
                min(self.max_total_multiplier, final_multipliers[signal_name])
            )
        
        # 計算綜合指標
        total_effect = sum(total_multiplier_effects) if total_multiplier_effects else 0.0
        confidence_adjustment = sum(
            event.confidence for event in self.active_events.values()
        ) / max(1, len(self.active_events))
        
        risk_adjustment = 1.0 + total_effect * 0.1  # 事件增加風險
        
        self.stats["multiplier_calculations"] += 1
        
        return EventMultiplierResult(
            event_id=f"combined_{int(current_time.timestamp())}",
            applied_multipliers=final_multipliers,
            total_multiplier_effect=total_effect,
            confidence_adjustment=confidence_adjustment,
            risk_adjustment=risk_adjustment,
            explanation="; ".join(explanations) if explanations else "無活躍事件",
            calculation_time=current_time
        )
    
    def _cleanup_expired_events(self, current_time: datetime):
        """清理過期事件"""
        expired_events = []
        
        for event_id, event in self.active_events.items():
            event_end = event.event_time + timedelta(hours=event.duration_hours)
            if current_time > event_end:
                expired_events.append(event_id)
        
        for event_id in expired_events:
            del self.active_events[event_id]
            logger.info(f"🗑️ 清理過期事件: {event_id}")
        
        self.stats["active_events"] = len(self.active_events)
    
    def get_active_events(self) -> Dict[str, MarketEvent]:
        """獲取當前活躍事件"""
        return self.active_events.copy()
    
    def cancel_event(self, event_id: str) -> bool:
        """取消指定事件"""
        if event_id in self.active_events:
            del self.active_events[event_id]
            self.stats["active_events"] = len(self.active_events)
            logger.info(f"❌ 取消事件: {event_id}")
            return True
        return False
    
    def get_upcoming_events(self, hours_ahead: int = 24) -> List[MarketEvent]:
        """獲取未來指定時間內的事件"""
        current_time = datetime.now()
        future_time = current_time + timedelta(hours=hours_ahead)
        
        upcoming_events = []
        for event in self.active_events.values():
            if current_time <= event.event_time <= future_time:
                upcoming_events.append(event)
        
        return sorted(upcoming_events, key=lambda e: e.event_time)
    
    def export_event_analysis(self) -> Dict:
        """導出事件分析摘要"""
        current_time = datetime.now()
        
        return {
            "system_stats": self.stats,
            "active_events_count": len(self.active_events),
            "active_events": [
                {
                    "event_id": event.event_id,
                    "title": event.title,
                    "type": event.event_type.value,
                    "severity": event.severity.value,
                    "direction": event.direction.value,
                    "confidence": event.confidence,
                    "time_to_event": (event.event_time - current_time).total_seconds() / 3600,
                    "affected_symbols": event.affected_symbols,
                    "signal_multipliers": event.signal_multipliers
                }
                for event in self.active_events.values()
            ],
            "upcoming_events": [
                {
                    "title": event.title,
                    "event_time": event.event_time.isoformat(),
                    "hours_until": (event.event_time - current_time).total_seconds() / 3600
                }
                for event in self.get_upcoming_events(72)
            ],
            "event_templates": list(self.event_templates.keys()),
            "export_time": current_time.isoformat()
        }

# 全局實例
event_signal_multiplier = EventSignalMultiplier()
