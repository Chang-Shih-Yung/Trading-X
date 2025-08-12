"""
階段1B：波動適應性優化增強模組 - Trading X Phase 4
獨立的波動適應性和信號連續性分析模組
"""

from typing import Dict, List, Optional, Tuple, Any, Deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
import logging
import numpy as np
from app.services.signal_scoring_engine import (
    SignalModuleScore, SignalModuleType, TradingCycle, 
    CycleWeightTemplate, StandardizedCycleTemplates,
    signal_scoring_engine
)

logger = logging.getLogger(__name__)

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
                sorted_vol = sorted(list(self.volatility_history))
                rank = sorted_vol.index(current_volatility)
                volatility_percentile = rank / len(sorted_vol)
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
        self.base_engine = signal_scoring_engine  # 使用現有的階段1A引擎
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
            # 獲取即時信號分數
            current_signals = await self._get_realtime_signal_scores()
            if not current_signals:
                logger.error("無法獲取即時信號分數")
                raise ValueError("即時信號數據不可用")
            
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
    
    async def _get_realtime_signal_scores(self) -> Dict[str, SignalModuleScore]:
        """獲取即時信號分數"""
        # 這裡應該整合真實的信號評分系統
        raise NotImplementedError("需要整合真實的即時信號評分系統")
    
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
