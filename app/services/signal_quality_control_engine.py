#!/usr/bin/env python3
"""
🎯 Trading X - 信號品質控制引擎
兩階段決策架構：信號候選池 → EPL決策層 → 分級輸出

Author: Trading X Team
Version: 2.0.0
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)

class SignalPriority(Enum):
    """信號優先級"""
    CRITICAL = "CRITICAL"  # 緊急信號
    HIGH = "HIGH"         # 高品質信號  
    MEDIUM = "MEDIUM"     # 標準信號
    LOW = "LOW"           # 參考信號

class EPLAction(Enum):
    """EPL決策動作"""
    REPLACE = "REPLACE"           # 替單
    ENHANCE = "ENHANCE"           # 加倉強化
    NEW_ORDER = "NEW_ORDER"       # 新單
    IGNORE = "IGNORE"             # 忽略

@dataclass
class SignalCandidate:
    """信號候選者"""
    id: str
    symbol: str
    signal_type: str  # BUY/SELL
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    quality_score: float
    source: str  # 'sniper', 'phase1abc', 'phase23', 'pandas_ta'
    indicators_used: List[str]
    reasoning: str
    timeframe: str
    created_at: datetime
    market_conditions: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'quality_score': self.quality_score,
            'source': self.source,
            'indicators_used': self.indicators_used,
            'reasoning': self.reasoning,
            'timeframe': self.timeframe,
            'created_at': self.created_at.isoformat(),
            'market_conditions': self.market_conditions
        }

@dataclass 
class EPLDecision:
    """EPL決策結果"""
    action: EPLAction
    priority: SignalPriority
    reasoning: str
    confidence_delta: float = 0.0
    related_signal_id: Optional[str] = None
    execution_params: Dict[str, Any] = field(default_factory=dict)

class SignalQualityControlEngine:
    """🎯 信號品質控制引擎 - 兩階段決策架構核心"""
    
    def __init__(self):
        self.candidate_pool: List[SignalCandidate] = []
        self.active_positions: Dict[str, SignalCandidate] = {}  # symbol -> active signal
        self.decision_history: List[Dict[str, Any]] = []
        
        # 配置參數
        self.config = {
            'deduplication': {
                'time_threshold_minutes': 15,
                'confidence_diff_threshold': 0.03,
                'similarity_threshold': 0.85
            },
            'epl_thresholds': {
                'replace_confidence_gap': 0.15,  # 替單需要15%信心度提升
                'enhance_confidence_gap': 0.08,  # 加倉需要8%信心度提升
                'min_quality_score': 70.0,      # 最低品質分數
                'critical_threshold': 90.0,     # 緊急信號門檻
                'high_threshold': 80.0,         # 高品質信號門檻
                'medium_threshold': 70.0        # 標準信號門檻
            },
            'risk_management': {
                'max_concurrent_signals': 5,
                'max_same_symbol_signals': 2,
                'position_size_limits': {'CRITICAL': 0.1, 'HIGH': 0.08, 'MEDIUM': 0.05, 'LOW': 0.02}
            }
        }
        
        # 統計數據
        self.stats = {
            'total_candidates': 0,
            'duplicates_filtered': 0,
            'epl_processed': 0,
            'actions_taken': {'REPLACE': 0, 'ENHANCE': 0, 'NEW_ORDER': 0, 'IGNORE': 0},
            'priority_distribution': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        }
        
        logger.info("🎯 信號品質控制引擎初始化完成")

    async def process_signal_candidate(self, candidate: SignalCandidate) -> Optional[EPLDecision]:
        """
        處理信號候選者的完整流程
        
        Args:
            candidate: 信號候選者
            
        Returns:
            EPL決策結果或None（如果被過濾）
        """
        try:
            logger.info(f"🎯 開始處理信號候選: {candidate.symbol} {candidate.signal_type} (品質: {candidate.quality_score:.1f})")
            
            self.stats['total_candidates'] += 1
            
            # Phase 1: 去重分析
            if await self._is_duplicate_signal(candidate):
                logger.info(f"❌ 信號去重過濾: {candidate.symbol} (重複信號)")
                self.stats['duplicates_filtered'] += 1
                return None
            
            # Phase 2: 關聯分析 + EPL決策
            decision = await self._execute_epl_decision(candidate)
            
            if decision:
                self.stats['epl_processed'] += 1
                self.stats['actions_taken'][decision.action.value] += 1
                self.stats['priority_distribution'][decision.priority.value] += 1
                
                # 記錄決策歷史
                self._record_decision(candidate, decision)
                
                logger.info(f"✅ EPL決策完成: {decision.action.value} | 優先級: {decision.priority.value}")
                
            return decision
            
        except Exception as e:
            logger.error(f"❌ 處理信號候選時發生錯誤: {e}")
            return None

    async def _is_duplicate_signal(self, candidate: SignalCandidate) -> bool:
        """Step 1: 信號去重檢測"""
        try:
            current_time = candidate.created_at
            time_threshold = timedelta(minutes=self.config['deduplication']['time_threshold_minutes'])
            confidence_threshold = self.config['deduplication']['confidence_diff_threshold']
            
            # 檢查候選池中的相似信號
            for existing in self.candidate_pool:
                # 時間檢查
                if abs((current_time - existing.created_at).total_seconds()) > time_threshold.total_seconds():
                    continue
                
                # 標的和方向檢查
                if existing.symbol != candidate.symbol or existing.signal_type != candidate.signal_type:
                    continue
                
                # 信心度差異檢查
                confidence_diff = abs(existing.confidence - candidate.confidence)
                if confidence_diff <= confidence_threshold:
                    logger.debug(f"🔍 檢測到重複信號: {candidate.symbol} 信心度差異: {confidence_diff:.3f}")
                    return True
                
                # 指標來源相似度檢查
                if self._calculate_indicator_similarity(existing, candidate) > self.config['deduplication']['similarity_threshold']:
                    logger.debug(f"🔍 檢測到相似指標來源: {candidate.symbol}")
                    return True
            
            # 將候選者加入池中（如果不是重複的）
            self.candidate_pool.append(candidate)
            
            # 保持候選池大小（保留最近1小時的信號）
            cutoff_time = current_time - timedelta(hours=1)
            self.candidate_pool = [c for c in self.candidate_pool if c.created_at > cutoff_time]
            
            return False
            
        except Exception as e:
            logger.error(f"❌ 去重檢測錯誤: {e}")
            return False

    def _calculate_indicator_similarity(self, signal1: SignalCandidate, signal2: SignalCandidate) -> float:
        """計算兩個信號的指標相似度"""
        try:
            set1 = set(signal1.indicators_used)
            set2 = set(signal2.indicators_used)
            
            if not set1 or not set2:
                return 0.0
            
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception:
            return 0.0

    async def _execute_epl_decision(self, candidate: SignalCandidate) -> Optional[EPLDecision]:
        """Step 2: 執行EPL決策邏輯"""
        try:
            # 檢查是否有相同標的的活躍持倉
            existing_position = self.active_positions.get(candidate.symbol)
            
            if existing_position:
                return await self._decide_with_existing_position(candidate, existing_position)
            else:
                return await self._decide_new_position(candidate)
                
        except Exception as e:
            logger.error(f"❌ EPL決策錯誤: {e}")
            return None

    async def _decide_with_existing_position(self, candidate: SignalCandidate, existing: SignalCandidate) -> Optional[EPLDecision]:
        """對有持倉的標的進行決策"""
        try:
            confidence_gap = candidate.confidence - existing.confidence
            quality_gap = candidate.quality_score - existing.quality_score
            
            # 方向相同 - 考慮加倉強化
            if candidate.signal_type == existing.signal_type:
                if (confidence_gap >= self.config['epl_thresholds']['enhance_confidence_gap'] and 
                    quality_gap > 5.0):  # 品質分數提升5分以上
                    
                    priority = self._determine_priority(candidate.quality_score)
                    
                    return EPLDecision(
                        action=EPLAction.ENHANCE,
                        priority=priority,
                        reasoning=f"信心度提升 {confidence_gap:.3f}, 品質提升 {quality_gap:.1f}分",
                        confidence_delta=confidence_gap,
                        related_signal_id=existing.id,
                        execution_params={'enhancement_ratio': min(confidence_gap * 2, 0.5)}
                    )
            
            # 方向相反 - 考慮替單
            else:
                if (confidence_gap >= self.config['epl_thresholds']['replace_confidence_gap'] and
                    candidate.quality_score >= self.config['epl_thresholds']['min_quality_score']):
                    
                    priority = self._determine_priority(candidate.quality_score)
                    
                    return EPLDecision(
                        action=EPLAction.REPLACE,
                        priority=priority,
                        reasoning=f"反向高品質信號，信心度提升 {confidence_gap:.3f}",
                        confidence_delta=confidence_gap,
                        related_signal_id=existing.id
                    )
            
            # 都不符合條件 - 忽略
            return EPLDecision(
                action=EPLAction.IGNORE,
                priority=SignalPriority.LOW,
                reasoning=f"信號改善不足：信心度差異 {confidence_gap:.3f}, 品質差異 {quality_gap:.1f}",
                confidence_delta=confidence_gap,
                related_signal_id=existing.id
            )
            
        except Exception as e:
            logger.error(f"❌ 持倉決策錯誤: {e}")
            return None

    async def _decide_new_position(self, candidate: SignalCandidate) -> Optional[EPLDecision]:
        """對新標的進行決策"""
        try:
            # 檢查基本品質門檻
            if candidate.quality_score < self.config['epl_thresholds']['min_quality_score']:
                return EPLDecision(
                    action=EPLAction.IGNORE,
                    priority=SignalPriority.LOW,
                    reasoning=f"品質分數過低: {candidate.quality_score:.1f} < {self.config['epl_thresholds']['min_quality_score']}"
                )
            
            # 檢查風險管理限制
            if len(self.active_positions) >= self.config['risk_management']['max_concurrent_signals']:
                return EPLDecision(
                    action=EPLAction.IGNORE,
                    priority=SignalPriority.LOW,
                    reasoning=f"超過最大同時信號數限制: {len(self.active_positions)}"
                )
            
            # 決定新單建立
            priority = self._determine_priority(candidate.quality_score)
            
            return EPLDecision(
                action=EPLAction.NEW_ORDER,
                priority=priority,
                reasoning=f"新標的高品質信號，品質分數: {candidate.quality_score:.1f}",
                execution_params={'position_size': self.config['risk_management']['position_size_limits'][priority.value]}
            )
            
        except Exception as e:
            logger.error(f"❌ 新持倉決策錯誤: {e}")
            return None

    def _determine_priority(self, quality_score: float) -> SignalPriority:
        """根據品質分數決定優先級"""
        if quality_score >= self.config['epl_thresholds']['critical_threshold']:
            return SignalPriority.CRITICAL
        elif quality_score >= self.config['epl_thresholds']['high_threshold']:
            return SignalPriority.HIGH
        elif quality_score >= self.config['epl_thresholds']['medium_threshold']:
            return SignalPriority.MEDIUM
        else:
            return SignalPriority.LOW

    def _record_decision(self, candidate: SignalCandidate, decision: EPLDecision):
        """記錄決策歷史"""
        try:
            record = {
                'timestamp': datetime.now().isoformat(),
                'candidate': candidate.to_dict(),
                'decision': {
                    'action': decision.action.value,
                    'priority': decision.priority.value,
                    'reasoning': decision.reasoning,
                    'confidence_delta': decision.confidence_delta,
                    'related_signal_id': decision.related_signal_id,
                    'execution_params': decision.execution_params
                }
            }
            
            self.decision_history.append(record)
            
            # 保持歷史記錄大小
            if len(self.decision_history) > 1000:
                self.decision_history = self.decision_history[-500:]
                
            # 更新活躍持倉
            if decision.action == EPLAction.NEW_ORDER:
                self.active_positions[candidate.symbol] = candidate
            elif decision.action == EPLAction.REPLACE and decision.related_signal_id:
                self.active_positions[candidate.symbol] = candidate
            elif decision.action == EPLAction.ENHANCE:
                # 加倉時更新信號參數
                self.active_positions[candidate.symbol] = candidate
                
        except Exception as e:
            logger.error(f"❌ 記錄決策歷史錯誤: {e}")

    def get_engine_statistics(self) -> Dict[str, Any]:
        """獲取引擎統計資訊"""
        return {
            'stats': self.stats.copy(),
            'active_positions_count': len(self.active_positions),
            'candidate_pool_size': len(self.candidate_pool),
            'decision_history_size': len(self.decision_history),
            'config': self.config,
            'last_updated': datetime.now().isoformat()
        }

    async def cleanup_expired_positions(self):
        """清理過期持倉"""
        try:
            current_time = datetime.now()
            expired_symbols = []
            
            for symbol, position in self.active_positions.items():
                # 假設持倉有效期為24小時
                if (current_time - position.created_at).total_seconds() > 86400:
                    expired_symbols.append(symbol)
            
            for symbol in expired_symbols:
                del self.active_positions[symbol]
                logger.info(f"🧹 清理過期持倉: {symbol}")
                
        except Exception as e:
            logger.error(f"❌ 清理過期持倉錯誤: {e}")

    def reset_statistics(self):
        """重置統計數據"""
        self.stats = {
            'total_candidates': 0,
            'duplicates_filtered': 0,
            'epl_processed': 0,
            'actions_taken': {'REPLACE': 0, 'ENHANCE': 0, 'NEW_ORDER': 0, 'IGNORE': 0},
            'priority_distribution': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        }
        logger.info("📊 統計數據已重置")

# 全域引擎實例
signal_quality_engine = SignalQualityControlEngine()
