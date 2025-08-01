"""
階段1A+1B：三週期信號打分模組重構 + 波動適應性優化 - Trading X Phase 4
標準化信號模組分類與週期適配權重模板系統 + 動態波動適應與信號連續性增強
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import asyncio
import math
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# ==================== 核心信號模組分類 ====================

class SignalModuleType(Enum):
    """核心信號模組標準化分類"""
    TECHNICAL_STRUCTURE = "technical_structure"      # 技術結構分析模組
    VOLUME_MICROSTRUCTURE = "volume_microstructure"  # 成交量微結構模組
    SENTIMENT_INDICATORS = "sentiment_indicators"    # 情緒指標模組
    SMART_MONEY_DETECTION = "smart_money_detection"  # 機構參與度模組
    MACRO_ENVIRONMENT = "macro_environment"          # 宏觀環境監控模組
    CROSS_MARKET_CORRELATION = "cross_market_correlation"  # 跨市場聯動模組
    EVENT_DRIVEN_SIGNALS = "event_driven_signals"   # 事件驅動模組

class TradingCycle(Enum):
    """交易週期枚舉"""
    SHORT_TERM = "short"     # 短線模式 (1m-30m)
    MEDIUM_TERM = "medium"   # 中線模式 (4h-1d)
    LONG_TERM = "long"       # 長線模式 (1w+)

@dataclass
class SignalModuleScore:
    """信號模組評分"""
    module_type: SignalModuleType
    raw_score: float              # 原始信號分數 (0-1)
    confidence: float             # 信心度 (0-1)  
    strength: float               # 信號強度 (0-1)
    timestamp: datetime           # 信號時間戳
    source_data: Dict[str, Any]   # 源數據
    reliability: float = 0.8      # 可靠性評分 (0-1)
    latency_ms: float = 0.0       # 延遲毫秒數
    
    def get_weighted_score(self, weight: float) -> float:
        """獲取加權後信號分數"""
        return self.raw_score * self.confidence * weight

@dataclass  
class CycleWeightTemplate:
    """週期適配權重模板"""
    cycle: TradingCycle
    template_name: str
    description: str
    
    # 核心信號模組權重配置
    technical_structure_weight: float      # 技術結構分析模組權重
    volume_microstructure_weight: float    # 成交量微結構模組權重
    sentiment_indicators_weight: float     # 情緒指標模組權重
    smart_money_detection_weight: float    # 機構參與度模組權重
    macro_environment_weight: float        # 宏觀環境監控模組權重
    cross_market_correlation_weight: float # 跨市場聯動模組權重
    event_driven_weight: float             # 事件驅動模組權重
    
    # 週期特定參數
    holding_expectation_hours: int         # 持倉預期時間(小時)
    signal_density_threshold: float        # 高頻信號密度閾值
    trend_confirmation_required: bool      # 是否需要趨勢確認
    macro_factor_importance: float         # 宏觀因子權重需求
    
    # 動態適應參數
    volatility_adaptation_factor: float    # 波動適應因子
    trend_following_sensitivity: float     # 趨勢跟蹤敏感度
    mean_reversion_tendency: float         # 均值回歸傾向
    
    def validate_weights(self) -> bool:
        """驗證權重總和是否為1.0"""
        total_weight = (
            self.technical_structure_weight +
            self.volume_microstructure_weight +
            self.sentiment_indicators_weight +
            self.smart_money_detection_weight +
            self.macro_environment_weight +
            self.cross_market_correlation_weight +
            self.event_driven_weight
        )
        return 0.99 <= total_weight <= 1.01  # 允許1%誤差
    
    def get_total_weight(self) -> float:
        """獲取總權重"""
        return (
            self.technical_structure_weight +
            self.volume_microstructure_weight +
            self.sentiment_indicators_weight +
            self.smart_money_detection_weight +
            self.macro_environment_weight +
            self.cross_market_correlation_weight +
            self.event_driven_weight
        )

# ==================== 週期切換觸發機制 ====================

@dataclass
class CycleSwitchTrigger:
    """週期切換觸發條件"""
    trigger_type: str
    current_cycle: TradingCycle
    target_cycle: TradingCycle
    confidence_score: float
    trigger_reason: str
    market_conditions: Dict[str, Any]
    timestamp: datetime

class CycleSwitchConditions:
    """自動週期識別條件"""
    
    @staticmethod
    def evaluate_short_term_trigger(holding_expectation_hours: float, 
                                  signal_density: float,
                                  current_volatility: float) -> bool:
        """短線觸發條件：持倉預期 < 2小時 + 高頻信號密度 > 閾值"""
        return (
            holding_expectation_hours < 2.0 and
            signal_density > 0.7 and
            current_volatility > 0.6  # 高波動有利短線
        )
    
    @staticmethod
    def evaluate_medium_term_trigger(holding_expectation_hours: float,
                                   trend_confirmation: bool,
                                   trend_strength: float) -> bool:
        """中線觸發：持倉預期 2-48小時 + 趨勢確認指標激活"""
        return (
            2.0 <= holding_expectation_hours <= 48.0 and
            trend_confirmation and
            trend_strength > 0.5
        )
    
    @staticmethod  
    def evaluate_long_term_trigger(holding_expectation_hours: float,
                                 macro_factor_weight: float,
                                 market_regime_stability: float) -> bool:
        """長線觸發：持倉預期 > 48小時 + 宏觀因子權重需求"""
        return (
            holding_expectation_hours > 48.0 and
            macro_factor_weight > 0.2 and
            market_regime_stability > 0.6
        )

# ==================== 標準化週期權重模板管理器 ====================

class StandardizedCycleTemplates:
    """標準化週期權重模板管理器"""
    
    def __init__(self):
        self.templates = self._initialize_standard_templates()
        self.active_cycle = TradingCycle.MEDIUM_TERM  # 預設中線
        self.switch_history: List[CycleSwitchTrigger] = []
        logger.info("✅ 標準化週期權重模板系統初始化完成")
    
    def _initialize_standard_templates(self) -> Dict[TradingCycle, CycleWeightTemplate]:
        """初始化標準化週期權重模板"""
        templates = {}
        
        # ========== 短線模式權重模板 (1m-30m) ==========
        templates[TradingCycle.SHORT_TERM] = CycleWeightTemplate(
            cycle=TradingCycle.SHORT_TERM,
            template_name="短線高頻交易模板",
            description="1分鐘-30分鐘持倉，重視微結構和機構資金",
            
            # 短線權重配置 (按你的設計)
            technical_structure_weight=0.20,        # 技術結構分析：20%
            volume_microstructure_weight=0.40,      # 成交量微結構：40% (核心)
            sentiment_indicators_weight=0.10,       # 情緒指標：10%
            smart_money_detection_weight=0.25,      # 機構參與度：25% (Smart Money追蹤)
            macro_environment_weight=0.00,          # 宏觀環境監控：0% (不適用)
            cross_market_correlation_weight=0.05,   # 跨市場聯動：5%
            event_driven_weight=0.00,               # 事件驅動：動態觸發(單獨處理)
            
            # 短線特定參數
            holding_expectation_hours=1,            # 1小時內
            signal_density_threshold=0.8,           # 高信號密度要求
            trend_confirmation_required=False,      # 不強制趨勢確認
            macro_factor_importance=0.0,            # 無宏觀因子需求
            
            # 動態適應參數
            volatility_adaptation_factor=0.9,       # 高波動適應
            trend_following_sensitivity=0.6,        # 中等趨勢敏感度
            mean_reversion_tendency=0.7            # 較高均值回歸傾向
        )
        
        # ========== 中線模式權重模板 (4h-1d) ==========
        templates[TradingCycle.MEDIUM_TERM] = CycleWeightTemplate(
            cycle=TradingCycle.MEDIUM_TERM,
            template_name="中線平衡策略模板", 
            description="4小時-1天持倉，資金流向與技術分析並重",
            
            # 中線權重配置 (總和=1.00)
            technical_structure_weight=0.25,        # 技術結構分析：25%
            volume_microstructure_weight=0.20,      # 成交量微結構：20%
            sentiment_indicators_weight=0.15,       # 情緒指標：15%
            smart_money_detection_weight=0.30,      # 機構參與度：30% (資金流向)
            macro_environment_weight=0.10,          # 宏觀環境監控：10%
            cross_market_correlation_weight=0.00,   # 跨市場聯動：0% (修正)
            event_driven_weight=0.00,               # 事件驅動：變權重激活(單獨處理)
            
            # 中線特定參數
            holding_expectation_hours=12,           # 12小時平均
            signal_density_threshold=0.5,           # 中等信號密度
            trend_confirmation_required=True,       # 需要趨勢確認
            macro_factor_importance=0.15,           # 適度宏觀因子需求
            
            # 動態適應參數  
            volatility_adaptation_factor=0.7,       # 中等波動適應
            trend_following_sensitivity=0.8,        # 高趨勢敏感度
            mean_reversion_tendency=0.5            # 平衡均值回歸
        )
        
        # ========== 長線模式權重模板 (1w+) ==========
        templates[TradingCycle.LONG_TERM] = CycleWeightTemplate(
            cycle=TradingCycle.LONG_TERM,
            template_name="長線宏觀趨勢模板",
            description="1週以上持倉，宏觀環境與機構行為主導",
            
            # 長線權重配置 (總和=1.00)
            technical_structure_weight=0.15,        # 技術結構分析：15%
            volume_microstructure_weight=0.05,      # 成交量微結構：5%
            sentiment_indicators_weight=0.10,       # 情緒指標：10%
            smart_money_detection_weight=0.25,      # 機構參與度：25%
            macro_environment_weight=0.35,          # 宏觀環境監控：35% (核心)
            cross_market_correlation_weight=0.10,   # 跨市場聯動：10% (修正從15%到10%)
            event_driven_weight=0.00,               # 事件驅動：重大事件可達20%(單獨處理)
            
            # 長線特定參數
            holding_expectation_hours=168,          # 168小時(1週)
            signal_density_threshold=0.2,           # 低信號密度要求
            trend_confirmation_required=True,       # 強制趨勢確認
            macro_factor_importance=0.4,            # 高宏觀因子需求
            
            # 動態適應參數
            volatility_adaptation_factor=0.4,       # 低波動適應  
            trend_following_sensitivity=0.9,        # 最高趨勢敏感度
            mean_reversion_tendency=0.3            # 低均值回歸傾向
        )
        
        # 驗證所有模板權重
        for cycle, template in templates.items():
            if template.validate_weights():
                logger.info(f"✅ {cycle.value} 週期模板權重驗證通過: {template.get_total_weight():.3f}")
            else:
                logger.error(f"❌ {cycle.value} 週期模板權重驗證失敗: {template.get_total_weight():.3f}")
        
        return templates
    
    def get_template(self, cycle: TradingCycle) -> Optional[CycleWeightTemplate]:
        """獲取指定週期的權重模板"""
        return self.templates.get(cycle)
    
    def get_all_templates(self) -> Dict[TradingCycle, CycleWeightTemplate]:
        """獲取所有週期模板"""
        return self.templates.copy()
    
    def auto_cycle_identification(self, 
                                market_conditions: Dict[str, Any],
                                signal_analysis: Dict[str, Any]) -> Optional[TradingCycle]:
        """自動週期識別邏輯"""
        try:
            # 提取市場條件指標
            holding_expectation = market_conditions.get('holding_expectation_hours', 12)
            signal_density = signal_analysis.get('signal_density', 0.5)
            current_volatility = market_conditions.get('current_volatility', 0.5)
            trend_confirmation = signal_analysis.get('trend_confirmed', False)
            trend_strength = market_conditions.get('trend_strength', 0.5)
            macro_factor_weight = signal_analysis.get('macro_factor_weight', 0.1)
            market_regime_stability = market_conditions.get('regime_stability', 0.5)
            
            # 短線觸發檢查
            if CycleSwitchConditions.evaluate_short_term_trigger(
                holding_expectation, signal_density, current_volatility
            ):
                logger.info(f"🔥 短線觸發條件滿足: 持倉{holding_expectation}h, 密度{signal_density:.2f}, 波動{current_volatility:.2f}")
                return TradingCycle.SHORT_TERM
            
            # 長線觸發檢查  
            elif CycleSwitchConditions.evaluate_long_term_trigger(
                holding_expectation, macro_factor_weight, market_regime_stability
            ):
                logger.info(f"📈 長線觸發條件滿足: 持倉{holding_expectation}h, 宏觀權重{macro_factor_weight:.2f}")
                return TradingCycle.LONG_TERM
            
            # 中線觸發檢查
            elif CycleSwitchConditions.evaluate_medium_term_trigger(
                holding_expectation, trend_confirmation, trend_strength
            ):
                logger.info(f"⚖️ 中線觸發條件滿足: 持倉{holding_expectation}h, 趨勢確認{trend_confirmation}")
                return TradingCycle.MEDIUM_TERM
            
            # 如果沒有明確觸發條件，保持當前週期
            else:
                logger.info("🔄 未達到週期切換條件，保持當前週期")
                return None
                
        except Exception as e:
            logger.error(f"❌ 自動週期識別失敗: {e}")
            return None
    
    def execute_cycle_switch(self,
                           target_cycle: TradingCycle,
                           trigger_reason: str,
                           market_conditions: Dict[str, Any],
                           confidence_score: float = 0.8) -> bool:
        """執行週期切換"""
        try:
            if target_cycle == self.active_cycle:
                logger.info(f"📍 目標週期 {target_cycle.value} 與當前週期相同，無需切換")
                return True
            
            # 記錄切換事件
            switch_trigger = CycleSwitchTrigger(
                trigger_type="auto_identification",
                current_cycle=self.active_cycle,
                target_cycle=target_cycle,
                confidence_score=confidence_score,
                trigger_reason=trigger_reason,
                market_conditions=market_conditions,
                timestamp=datetime.now()
            )
            
            # 執行切換
            old_cycle = self.active_cycle
            self.active_cycle = target_cycle
            self.switch_history.append(switch_trigger)
            
            logger.info(f"🔄 週期切換成功: {old_cycle.value} → {target_cycle.value} (信心度: {confidence_score:.2f})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 週期切換失敗: {e}")
            return False
    
    def get_current_active_template(self) -> Optional[CycleWeightTemplate]:
        """獲取當前活躍的週期模板"""
        return self.get_template(self.active_cycle)
    
    def get_switch_history(self, limit: int = 10) -> List[CycleSwitchTrigger]:
        """獲取週期切換歷史"""
        return self.switch_history[-limit:]

# ==================== 信號打分引擎 ====================

class SignalScoringEngine:
    """信號打分引擎 - 整合各信號模組評分"""
    
    def __init__(self):
        self.cycle_templates = StandardizedCycleTemplates()
        self.module_scores: Dict[SignalModuleType, SignalModuleScore] = {}
        logger.info("✅ 信號打分引擎初始化完成")
    
    async def calculate_weighted_signal_score(self,
                                         symbols: List[str],
                                         target_cycle: Optional[TradingCycle] = None,
                                         custom_template: Optional[CycleWeightTemplate] = None) -> Dict[str, Any]:
        """計算加權信號總分 (支援自定義模板)"""
        try:
            logger.info(f"🎯 開始信號加權評分: {symbols}, 目標週期: {target_cycle}")
            
            # 獲取模擬信號數據
            signal_scores = await self._get_mock_signal_scores_dict()
            
            # 決定使用的週期和模板
            if custom_template:
                template = custom_template
                target_cycle = custom_template.cycle
                logger.info(f"🔧 使用自定義模板: {template.template_name}")
            elif target_cycle:
                template = self.cycle_templates.get_template(target_cycle)
            else:
                # 自動識別週期
                market_conditions = {
                    'volatility': 0.6,
                    'trend_strength': 0.7,
                    'macro_importance': 0.2
                }
                
                signal_analysis = {
                    'signal_density': len(signal_scores) / 7,
                    'trend_confirmed': market_conditions['trend_strength'] > 0.6,
                    'macro_factor_weight': market_conditions['macro_importance']
                }
                
                target_cycle = self.cycle_templates.auto_cycle_identification(
                    market_conditions, signal_analysis
                ) or TradingCycle.MEDIUM_TERM
                
                template = self.cycle_templates.get_template(target_cycle)
            
            # 權重映射
            weight_mapping = {
                SignalModuleType.TECHNICAL_STRUCTURE: template.technical_structure_weight,
                SignalModuleType.VOLUME_MICROSTRUCTURE: template.volume_microstructure_weight,
                SignalModuleType.SENTIMENT_INDICATORS: template.sentiment_indicators_weight,
                SignalModuleType.SMART_MONEY_DETECTION: template.smart_money_detection_weight,
                SignalModuleType.MACRO_ENVIRONMENT: template.macro_environment_weight,
                SignalModuleType.CROSS_MARKET_CORRELATION: template.cross_market_correlation_weight,
                SignalModuleType.EVENT_DRIVEN_SIGNALS: template.event_driven_weight
            }
            
            # 計算加權分數
            weighted_scores = {}
            total_weighted_score = 0.0
            total_confidence = 0.0
            available_modules = 0
            
            for module_type, weight in weight_mapping.items():
                if module_type in signal_scores and weight > 0:
                    score = signal_scores[module_type]
                    weighted_score = score.get_weighted_score(weight)
                    weighted_scores[module_type.value] = {
                        'raw_score': score.raw_score,
                        'confidence': score.confidence,
                        'weight': weight,
                        'weighted_score': weighted_score,
                        'reliability': score.reliability
                    }
                    total_weighted_score += weighted_score
                    total_confidence += score.confidence * weight
                    available_modules += 1
            
            # 計算信號覆蓋率
            signal_coverage = available_modules / 7
            
            # 最終評分結果
            result = {
                'active_cycle': target_cycle.value,
                'template_name': template.template_name,
                'signal_coverage': signal_coverage,
                'total_weighted_score': total_weighted_score,
                'average_confidence': total_confidence,
                'module_scores': weighted_scores,
                'template_info': {
                    'holding_expectation_hours': template.holding_expectation_hours,
                    'trend_confirmation_required': template.trend_confirmation_required,
                    'volatility_adaptation': template.volatility_adaptation_factor
                },
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"📊 信號加權評分完成: {target_cycle.value} - 總分 {total_weighted_score:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 信號加權評分失敗: {e}")
            return {"error": str(e)}
    
    async def _get_mock_signal_scores_dict(self) -> Dict[SignalModuleType, SignalModuleScore]:
        """獲取模擬信號分數字典"""
        return {
            SignalModuleType.TECHNICAL_STRUCTURE: SignalModuleScore(
                SignalModuleType.TECHNICAL_STRUCTURE, 0.72, 0.85, 0.68, datetime.now(), {}
            ),
            SignalModuleType.VOLUME_MICROSTRUCTURE: SignalModuleScore(
                SignalModuleType.VOLUME_MICROSTRUCTURE, 0.65, 0.78, 0.71, datetime.now(), {}
            ),
            SignalModuleType.SENTIMENT_INDICATORS: SignalModuleScore(
                SignalModuleType.SENTIMENT_INDICATORS, 0.58, 0.63, 0.59, datetime.now(), {}
            ),
            SignalModuleType.SMART_MONEY_DETECTION: SignalModuleScore(
                SignalModuleType.SMART_MONEY_DETECTION, 0.79, 0.88, 0.82, datetime.now(), {}
            ),
            SignalModuleType.MACRO_ENVIRONMENT: SignalModuleScore(
                SignalModuleType.MACRO_ENVIRONMENT, 0.45, 0.55, 0.48, datetime.now(), {}
            ),
            SignalModuleType.CROSS_MARKET_CORRELATION: SignalModuleScore(
                SignalModuleType.CROSS_MARKET_CORRELATION, 0.52, 0.67, 0.55, datetime.now(), {}
            ),
            SignalModuleType.EVENT_DRIVEN_SIGNALS: SignalModuleScore(
                SignalModuleType.EVENT_DRIVEN_SIGNALS, 0.30, 0.40, 0.35, datetime.now(), {}
            )
        }
    
    @property 
    def templates(self) -> 'StandardizedCycleTemplates':
        """獲取週期模板管理器"""
        return self.cycle_templates

# 全局實例
signal_scoring_engine = SignalScoringEngine()

# ==================== 階段1B：波動適應性優化與信號連續性增強 ====================

from typing import Deque
from collections import deque
import numpy as np

@dataclass
class VolatilityMetrics:
    """波動性指標"""
    current_volatility: float      # 當前波動率 (0-1)
    volatility_trend: float        # 波動趨勢 (-1 to 1)
    volatility_percentile: float   # 波動率百分位 (0-1)
    regime_stability: float        # 制度穩定性 (0-1)
    micro_volatility: float        # 微觀波動 (0-1)
    intraday_volatility: float     # 日內波動 (0-1)
    timestamp: datetime

@dataclass
class SignalContinuityMetrics:
    """信號連續性指標"""
    signal_persistence: float      # 信號持續性 (0-1)
    signal_divergence: float       # 信號分歧度 (0-1)
    consensus_strength: float      # 共識強度 (0-1)
    temporal_consistency: float    # 時間一致性 (0-1)
    cross_module_correlation: float # 跨模組相關性 (0-1)
    signal_decay_rate: float       # 信號衰減率 (0-1)

class VolatilityAdaptiveEngine:
    """波動適應性引擎"""
    
    def __init__(self, lookback_periods: int = 100):
        self.lookback_periods = lookback_periods
        self.volatility_history: Deque[float] = deque(maxlen=lookback_periods)
        self.signal_history: Deque[Dict] = deque(maxlen=lookback_periods)
        
    def calculate_volatility_metrics(self, price_data: List[float]) -> VolatilityMetrics:
        """計算綜合波動性指標"""
        try:
            if len(price_data) < 20:
                logger.warning("價格數據不足，使用默認波動指標")
                return VolatilityMetrics(
                    current_volatility=0.5,
                    volatility_trend=0.0,
                    volatility_percentile=0.5,
                    regime_stability=0.7,
                    micro_volatility=0.5,
                    intraday_volatility=0.5,
                    timestamp=datetime.now()
                )
            
            prices = np.array(price_data)
            returns = np.diff(np.log(prices))
            
            # 1. 當前波動率 (21期滾動標準差)
            current_volatility = np.std(returns[-21:]) if len(returns) >= 21 else np.std(returns)
            
            # 2. 波動趨勢 (短期vs長期波動比較)
            short_vol = np.std(returns[-10:]) if len(returns) >= 10 else current_volatility
            long_vol = np.std(returns[-50:]) if len(returns) >= 50 else current_volatility
            volatility_trend = (short_vol - long_vol) / (long_vol + 1e-8)
            volatility_trend = max(-1, min(1, volatility_trend))
            
            # 3. 波動率百分位
            self.volatility_history.append(current_volatility)
            if len(self.volatility_history) >= 20:
                volatility_percentile = np.percentile(list(self.volatility_history), 
                                                   [current_volatility * 100])[0] / 100
            else:
                volatility_percentile = 0.5
            
            # 4. 制度穩定性 (波動的波動)
            if len(self.volatility_history) >= 10:
                vol_stability = 1.0 - np.std(list(self.volatility_history)[-10:]) / (np.mean(list(self.volatility_history)[-10:]) + 1e-8)
                regime_stability = max(0, min(1, vol_stability))
            else:
                regime_stability = 0.7
            
            # 5. 微觀波動 (高頻價格變動)
            if len(returns) >= 10:
                micro_moves = np.abs(returns[-10:])
                micro_volatility = np.mean(micro_moves) / (current_volatility + 1e-8)
                micro_volatility = max(0, min(1, micro_volatility))
            else:
                micro_volatility = 0.5
            
            # 6. 日內波動 (開盤到收盤的波動範圍)
            if len(prices) >= 24:  # 假設24小時數據
                daily_ranges = []
                for i in range(0, len(prices) - 24, 24):
                    day_prices = prices[i:i+24]
                    daily_range = (np.max(day_prices) - np.min(day_prices)) / np.mean(day_prices)
                    daily_ranges.append(daily_range)
                intraday_volatility = np.mean(daily_ranges[-5:]) if daily_ranges else 0.5
            else:
                intraday_volatility = 0.5
            
            # 標準化到0-1範圍
            current_volatility = max(0, min(1, current_volatility * 100))  # 假設正常波動範圍0-1%
            
            return VolatilityMetrics(
                current_volatility=current_volatility,
                volatility_trend=volatility_trend,
                volatility_percentile=volatility_percentile,
                regime_stability=regime_stability,
                micro_volatility=micro_volatility,
                intraday_volatility=intraday_volatility,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ 波動性指標計算失敗: {e}")
            return VolatilityMetrics(
                current_volatility=0.5, volatility_trend=0.0, volatility_percentile=0.5,
                regime_stability=0.7, micro_volatility=0.5, intraday_volatility=0.5,
                timestamp=datetime.now()
            )
    
    def calculate_signal_continuity(self, current_signals: Dict[str, SignalModuleScore]) -> SignalContinuityMetrics:
        """計算信號連續性指標"""
        try:
            # 記錄當前信號
            signal_snapshot = {
                'timestamp': datetime.now(),
                'signals': {k: {'score': v.raw_score, 'confidence': v.confidence} 
                           for k, v in current_signals.items()}
            }
            self.signal_history.append(signal_snapshot)
            
            if len(self.signal_history) < 5:
                # 信號歷史不足，返回中性值
                return SignalContinuityMetrics(
                    signal_persistence=0.7,
                    signal_divergence=0.3,
                    consensus_strength=0.6,
                    temporal_consistency=0.7,
                    cross_module_correlation=0.5,
                    signal_decay_rate=0.2
                )
            
            # 1. 信號持續性 (信號方向穩定性)
            signal_directions = []
            for hist in list(self.signal_history)[-10:]:  # 最近10個信號
                for module, signal_data in hist['signals'].items():
                    direction = 1 if signal_data['score'] > 0.5 else -1
                    signal_directions.append(direction)
            
            if signal_directions:
                direction_consistency = abs(np.mean(signal_directions))
                signal_persistence = direction_consistency
            else:
                signal_persistence = 0.7
            
            # 2. 信號分歧度 (模組間分歧程度)
            current_scores = [s.raw_score for s in current_signals.values()]
            if len(current_scores) >= 3:
                signal_divergence = np.std(current_scores) / (np.mean(current_scores) + 1e-8)
                signal_divergence = max(0, min(1, signal_divergence))
            else:
                signal_divergence = 0.3
            
            # 3. 共識強度 (高置信度信號的比例)
            high_confidence_signals = sum(1 for s in current_signals.values() if s.confidence > 0.7)
            consensus_strength = high_confidence_signals / max(1, len(current_signals))
            
            # 4. 時間一致性 (信號在時間維度的穩定性)
            if len(self.signal_history) >= 5:
                recent_avg_scores = []
                for hist in list(self.signal_history)[-5:]:
                    scores = [s['score'] for s in hist['signals'].values()]
                    if scores:
                        recent_avg_scores.append(np.mean(scores))
                
                if len(recent_avg_scores) >= 3:
                    temporal_consistency = 1.0 - np.std(recent_avg_scores) / (np.mean(recent_avg_scores) + 1e-8)
                    temporal_consistency = max(0, min(1, temporal_consistency))
                else:
                    temporal_consistency = 0.7
            else:
                temporal_consistency = 0.7
            
            # 5. 跨模組相關性
            if len(current_scores) >= 3:
                # 計算信號分數的變異係數
                cv = np.std(current_scores) / (np.mean(current_scores) + 1e-8)
                cross_module_correlation = max(0, 1.0 - cv)  # 變異係數越小，相關性越高
            else:
                cross_module_correlation = 0.5
            
            # 6. 信號衰減率 (信號強度隨時間衰減的速度)
            if len(self.signal_history) >= 10:
                # 計算最近信號強度的線性回歸斜率
                recent_strengths = []
                for i, hist in enumerate(list(self.signal_history)[-10:]):
                    avg_strength = np.mean([s['confidence'] * s['score'] 
                                          for s in hist['signals'].values()])
                    recent_strengths.append(avg_strength)
                
                if len(recent_strengths) >= 5:
                    # 簡化的線性趨勢計算
                    x = np.arange(len(recent_strengths))
                    slope = np.polyfit(x, recent_strengths, 1)[0]
                    signal_decay_rate = max(0, -slope)  # 負斜率表示衰減
                else:
                    signal_decay_rate = 0.2
            else:
                signal_decay_rate = 0.2
            
            return SignalContinuityMetrics(
                signal_persistence=signal_persistence,
                signal_divergence=signal_divergence,
                consensus_strength=consensus_strength,
                temporal_consistency=temporal_consistency,
                cross_module_correlation=cross_module_correlation,
                signal_decay_rate=signal_decay_rate
            )
            
        except Exception as e:
            logger.error(f"❌ 信號連續性計算失敗: {e}")
            return SignalContinuityMetrics(
                signal_persistence=0.7, signal_divergence=0.3, consensus_strength=0.6,
                temporal_consistency=0.7, cross_module_correlation=0.5, signal_decay_rate=0.2
            )

class AdaptiveWeightEngine:
    """自適應權重引擎"""
    
    def __init__(self):
        self.base_templates = StandardizedCycleTemplates()
        
    def adjust_weights_for_volatility(self, 
                                    base_template: CycleWeightTemplate,
                                    volatility_metrics: VolatilityMetrics,
                                    continuity_metrics: SignalContinuityMetrics) -> CycleWeightTemplate:
        """根據波動性和連續性調整權重"""
        try:
            # 複製基礎模板
            adjusted_template = CycleWeightTemplate(
                cycle=base_template.cycle,
                template_name=f"{base_template.template_name} (波動適應)",
                description=f"{base_template.description} + 動態調整",
                technical_structure_weight=base_template.technical_structure_weight,
                volume_microstructure_weight=base_template.volume_microstructure_weight,
                sentiment_indicators_weight=base_template.sentiment_indicators_weight,
                smart_money_detection_weight=base_template.smart_money_detection_weight,
                macro_environment_weight=base_template.macro_environment_weight,
                cross_market_correlation_weight=base_template.cross_market_correlation_weight,
                event_driven_weight=base_template.event_driven_weight,
                holding_expectation_hours=base_template.holding_expectation_hours,
                signal_density_threshold=base_template.signal_density_threshold,
                trend_confirmation_required=base_template.trend_confirmation_required,
                macro_factor_importance=base_template.macro_factor_importance,
                volatility_adaptation_factor=base_template.volatility_adaptation_factor,
                trend_following_sensitivity=base_template.trend_following_sensitivity,
                mean_reversion_tendency=base_template.mean_reversion_tendency
            )
            
            # 波動適應性調整係數
            volatility_factor = volatility_metrics.current_volatility
            stability_factor = volatility_metrics.regime_stability
            persistence_factor = continuity_metrics.signal_persistence
            
            # 1. 高波動環境：增加微結構和技術指標權重
            if volatility_factor > 0.7:
                vol_boost = (volatility_factor - 0.7) * 0.5  # 最大增加15%
                adjusted_template.volume_microstructure_weight *= (1 + vol_boost)
                adjusted_template.technical_structure_weight *= (1 + vol_boost * 0.5)
                # 相應減少宏觀和長期指標權重
                adjusted_template.macro_environment_weight *= (1 - vol_boost)
                adjusted_template.smart_money_detection_weight *= (1 - vol_boost * 0.3)
            
            # 2. 低穩定性環境：增加情緒指標權重
            if stability_factor < 0.5:
                instability_boost = (0.5 - stability_factor) * 0.8
                adjusted_template.sentiment_indicators_weight *= (1 + instability_boost)
                adjusted_template.cross_market_correlation_weight *= (1 + instability_boost * 0.6)
            
            # 3. 低持續性信號：增加短期指標權重
            if persistence_factor < 0.6:
                short_term_boost = (0.6 - persistence_factor) * 0.6
                adjusted_template.volume_microstructure_weight *= (1 + short_term_boost)
                # 減少長期指標
                adjusted_template.macro_environment_weight *= (1 - short_term_boost)
            
            # 4. 重新標準化權重
            total_weight = (
                adjusted_template.technical_structure_weight +
                adjusted_template.volume_microstructure_weight +
                adjusted_template.sentiment_indicators_weight +
                adjusted_template.smart_money_detection_weight +
                adjusted_template.macro_environment_weight +
                adjusted_template.cross_market_correlation_weight +
                adjusted_template.event_driven_weight
            )
            
            if total_weight > 0:
                adjusted_template.technical_structure_weight /= total_weight
                adjusted_template.volume_microstructure_weight /= total_weight
                adjusted_template.sentiment_indicators_weight /= total_weight
                adjusted_template.smart_money_detection_weight /= total_weight
                adjusted_template.macro_environment_weight /= total_weight
                adjusted_template.cross_market_correlation_weight /= total_weight
                adjusted_template.event_driven_weight /= total_weight
            
            logger.info(f"🔧 權重動態調整完成: {base_template.cycle.value} -> 波動率{volatility_factor:.2f}, 穩定性{stability_factor:.2f}")
            return adjusted_template
            
        except Exception as e:
            logger.error(f"❌ 權重調整失敗: {e}")
            return base_template

class EnhancedSignalScoringEngine:
    """增強版信號打分引擎 (階段1A+1B)"""
    
    def __init__(self):
        self.base_engine = SignalScoringEngine()
        self.volatility_engine = VolatilityAdaptiveEngine()
        self.weight_engine = AdaptiveWeightEngine()
        self.performance_metrics = {
            'total_adaptations': 0,
            'volatility_adjustments': 0,
            'continuity_improvements': 0,
            'weight_optimizations': 0
        }
    
    async def enhanced_signal_scoring(self, 
                                    symbols: List[str],
                                    target_cycle: Optional[TradingCycle] = None,
                                    price_data: Optional[Dict[str, List[float]]] = None,
                                    enable_adaptation: bool = True) -> Dict[str, Any]:
        """增強版信號打分（包含波動適應性）"""
        try:
            logger.info(f"🚀 啟動階段1B增強信號打分: {symbols}, 適應性={enable_adaptation}")
            
            # 1. 基礎信號打分 (階段1A)
            base_result = await self.base_engine.calculate_weighted_signal_score(symbols, target_cycle)
            
            if not enable_adaptation or price_data is None:
                base_result['enhancement_applied'] = False
                return base_result
            
            # 2. 獲取當前信號分數
            current_signals = await self._get_mock_signal_scores()
            
            # 3. 計算波動性指標
            volatility_metrics_by_symbol = {}
            for symbol in symbols:
                if symbol in price_data and price_data[symbol]:
                    vol_metrics = self.volatility_engine.calculate_volatility_metrics(price_data[symbol])
                    volatility_metrics_by_symbol[symbol] = vol_metrics
            
            # 使用主要交易對的波動指標
            primary_symbol = symbols[0] if symbols else 'BTCUSDT'
            vol_metrics = volatility_metrics_by_symbol.get(
                primary_symbol, 
                VolatilityMetrics(0.5, 0.0, 0.5, 0.7, 0.5, 0.5, datetime.now())
            )
            
            # 4. 計算信號連續性指標
            continuity_metrics = self.volatility_engine.calculate_signal_continuity(current_signals)
            
            # 5. 動態調整權重
            if 'active_cycle' in base_result:
                cycle = TradingCycle(base_result['active_cycle'])
                base_template = self.base_engine.templates.get_template(cycle)
                
                adjusted_template = self.weight_engine.adjust_weights_for_volatility(
                    base_template, vol_metrics, continuity_metrics
                )
                
                # 6. 使用調整後的權重重新計算
                enhanced_result = await self.base_engine.calculate_weighted_signal_score(
                    symbols, cycle, custom_template=adjusted_template
                )
                
                # 7. 添加階段1B的增強信息
                enhanced_result.update({
                    'enhancement_applied': True,
                    'phase_1b_metrics': {
                        'volatility_metrics': {
                            'current_volatility': vol_metrics.current_volatility,
                            'volatility_trend': vol_metrics.volatility_trend,
                            'regime_stability': vol_metrics.regime_stability,
                            'micro_volatility': vol_metrics.micro_volatility
                        },
                        'continuity_metrics': {
                            'signal_persistence': continuity_metrics.signal_persistence,
                            'signal_divergence': continuity_metrics.signal_divergence,
                            'consensus_strength': continuity_metrics.consensus_strength,
                            'temporal_consistency': continuity_metrics.temporal_consistency
                        },
                        'adaptation_summary': {
                            'volatility_factor': vol_metrics.current_volatility,
                            'stability_factor': vol_metrics.regime_stability,
                            'persistence_factor': continuity_metrics.signal_persistence,
                            'weight_adjustments_applied': abs(adjusted_template.get_total_weight() - base_template.get_total_weight()) > 0.01
                        }
                    },
                    'performance_improvements': {
                        'signal_stability_score': continuity_metrics.temporal_consistency,
                        'adaptation_effectiveness': min(1.0, vol_metrics.regime_stability + continuity_metrics.consensus_strength),
                        'risk_adjusted_score': enhanced_result.get('total_weighted_score', 0) * continuity_metrics.signal_persistence
                    }
                })
                
                # 更新性能指標
                self.performance_metrics['total_adaptations'] += 1
                if vol_metrics.current_volatility > 0.6:
                    self.performance_metrics['volatility_adjustments'] += 1
                if continuity_metrics.temporal_consistency > 0.7:
                    self.performance_metrics['continuity_improvements'] += 1
                
                logger.info(f"✅ 階段1B增強完成: 波動適應={vol_metrics.current_volatility:.2f}, 信號持續性={continuity_metrics.signal_persistence:.2f}")
                return enhanced_result
            
            else:
                # 如果基礎結果有問題，返回基礎結果
                base_result['enhancement_applied'] = False
                return base_result
                
        except Exception as e:
            logger.error(f"❌ 階段1B增強信號打分失敗: {e}")
            base_result = await self.base_engine.calculate_weighted_signal_score(symbols, target_cycle)
            base_result['enhancement_applied'] = False
            base_result['enhancement_error'] = str(e)
            return base_result
    
    async def _get_mock_signal_scores(self) -> Dict[str, SignalModuleScore]:
        """獲取模擬信號分數"""
        return {
            'technical_structure': SignalModuleScore(
                SignalModuleType.TECHNICAL_STRUCTURE, 0.72, 0.85, 0.68, datetime.now(), {}
            ),
            'volume_microstructure': SignalModuleScore(
                SignalModuleType.VOLUME_MICROSTRUCTURE, 0.65, 0.78, 0.71, datetime.now(), {}
            ),
            'sentiment_indicators': SignalModuleScore(
                SignalModuleType.SENTIMENT_INDICATORS, 0.58, 0.63, 0.59, datetime.now(), {}
            ),
            'smart_money_detection': SignalModuleScore(
                SignalModuleType.SMART_MONEY_DETECTION, 0.79, 0.88, 0.82, datetime.now(), {}
            )
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """獲取階段1B性能總結"""
        return {
            'phase': '階段1B - 波動適應性優化',
            'metrics': self.performance_metrics,
            'capabilities': {
                'volatility_adaptation': '根據市場波動自動調整權重配置',
                'signal_continuity': '監控信號持續性和一致性',
                'dynamic_weighting': '實時優化信號模組權重分配',
                'risk_adjustment': '風險調整後的信號評分'
            }
        }

# 階段1B全局實例
enhanced_signal_scoring_engine = EnhancedSignalScoringEngine()
