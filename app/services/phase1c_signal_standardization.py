"""
階段1C: 信號標準化與極端信號放大模組
- 統一信號強度標準化處理
- 極端信號識別與放大
- 多時間框架信號整合
- 動態信號質量評級

與階段1A+1B的整合點:
- 基於階段1A的7個標準化模組
- 使用階段1B的波動適應性數據
- 提供增強的信號處理能力
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import statistics
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SignalNormalizationConfig:
    """信號標準化配置"""
    # 標準化參數
    min_signal_threshold: float = 0.1  # 最小信號閾值
    max_signal_threshold: float = 0.9  # 最大信號閾值
    extreme_signal_threshold: float = 0.8  # 極端信號閾值
    
    # 時間框架權重
    short_term_weight: float = 0.5  # 短時間框架權重
    medium_term_weight: float = 0.3  # 中時間框架權重
    long_term_weight: float = 0.2   # 長時間框架權重
    
    # 極端信號放大參數
    extreme_amplification_factor: float = 1.5  # 極端信號放大倍數
    quality_boost_threshold: float = 0.85      # 質量提升閾值

@dataclass
class StandardizedSignal:
    """標準化信號結構"""
    signal_id: str
    module_name: str
    original_value: float
    standardized_value: float
    quality_score: float
    confidence_level: float
    is_extreme: bool
    amplification_applied: float
    timeframe: str
    timestamp: datetime

@dataclass
class ExtremeSignalMetrics:
    """極端信號指標"""
    total_signals: int
    extreme_signals_count: int
    extreme_signal_ratio: float
    average_amplification: float
    quality_distribution: Dict[str, int]  # A/B/C級別分布
    top_performing_modules: List[str]

@dataclass
class MultiTimeframeAnalysis:
    """多時間框架分析結果"""
    short_term_signals: List[StandardizedSignal]
    medium_term_signals: List[StandardizedSignal]
    long_term_signals: List[StandardizedSignal]
    integrated_score: float
    consensus_strength: float
    timeframe_alignment: float

class SignalStandardizationEngine:
    """信號標準化引擎"""
    
    def __init__(self, config: SignalNormalizationConfig = None):
        self.config = config or SignalNormalizationConfig()
        self.signal_history: List[StandardizedSignal] = []
        self.performance_tracker = {
            'standardization_count': 0,
            'extreme_signals_detected': 0,
            'amplifications_applied': 0,
            'quality_improvements': 0
        }
        
    def standardize_signal(self, signal_value: float, signal_id: str, 
                          module_name: str, timeframe: str = 'medium') -> StandardizedSignal:
        """
        標準化單個信號
        將原始信號值轉換為0-1標準化值，並計算質量評分
        """
        try:
            # 1. 基礎標準化 (使用改進的Sigmoid函數)
            standardized_value = self._apply_sigmoid_normalization(signal_value)
            
            # 2. 計算信號質量評分
            quality_score = self._calculate_signal_quality(
                signal_value, standardized_value, module_name
            )
            
            # 3. 計算信心度
            confidence_level = self._calculate_confidence_level(
                signal_value, quality_score, timeframe
            )
            
            # 4. 檢測是否為極端信號
            is_extreme = self._is_extreme_signal(standardized_value, quality_score)
            
            # 5. 應用極端信號放大
            amplification_applied = 1.0
            if is_extreme:
                amplification_applied = self._apply_extreme_amplification(
                    standardized_value, quality_score
                )
                standardized_value *= amplification_applied
                standardized_value = min(standardized_value, 1.0)  # 確保不超過1
                
            # 6. 創建標準化信號對象
            standardized_signal = StandardizedSignal(
                signal_id=signal_id,
                module_name=module_name,
                original_value=signal_value,
                standardized_value=standardized_value,
                quality_score=quality_score,
                confidence_level=confidence_level,
                is_extreme=is_extreme,
                amplification_applied=amplification_applied,
                timeframe=timeframe,
                timestamp=datetime.now()
            )
            
            # 7. 記錄到歷史
            self.signal_history.append(standardized_signal)
            self._update_performance_tracker(standardized_signal)
            
            logger.info(f"信號標準化完成: {signal_id} ({module_name}) - "
                       f"原值: {signal_value:.3f} -> 標準化值: {standardized_value:.3f}")
            
            return standardized_signal
            
        except Exception as e:
            logger.error(f"信號標準化失敗: {signal_id} - {str(e)}")
            raise
    
    def _apply_sigmoid_normalization(self, value: float) -> float:
        """應用改進的Sigmoid標準化"""
        # 使用調整後的Sigmoid函數，提高中等信號的區分度
        try:
            # 將輸入值映射到合適的範圍
            adjusted_value = (value - 0.5) * 6  # 調整斜率
            normalized = 1 / (1 + np.exp(-adjusted_value))
            
            # 應用閾值截斷
            if normalized < self.config.min_signal_threshold:
                normalized = self.config.min_signal_threshold
            elif normalized > self.config.max_signal_threshold:
                normalized = self.config.max_signal_threshold
                
            return float(normalized)
        except:
            return 0.5  # 默認中性值
    
    def _calculate_signal_quality(self, original_value: float, 
                                 standardized_value: float, module_name: str) -> float:
        """計算信號質量評分"""
        try:
            # 基礎質量評分 (基於信號強度)
            strength_score = abs(standardized_value - 0.5) * 2  # 0-1範圍
            
            # 模組特定調整
            module_adjustments = {
                'technical_structure': 1.0,
                'volume_microstructure': 1.1,     # 微結構信號通常更可靠
                'sentiment_indicators': 0.9,       # 情緒信號波動較大
                'smart_money_detection': 1.2,      # 機構信號質量較高  
                'macro_environment': 0.8,          # 宏觀信號變化較慢
                'cross_market_correlation': 1.0,
                'event_driven_signals': 1.1        # 事件驅動信號時效性強
            }
            
            module_factor = module_adjustments.get(module_name, 1.0)
            
            # 穩定性調整 (基於歷史表現)
            stability_factor = self._get_module_stability_factor(module_name)
            
            # 綜合質量評分
            quality_score = strength_score * module_factor * stability_factor
            quality_score = min(max(quality_score, 0.0), 1.0)  # 確保在0-1範圍
            
            return quality_score
            
        except Exception as e:
            logger.warning(f"質量評分計算失敗: {str(e)}")
            return 0.5
    
    def _calculate_confidence_level(self, original_value: float, 
                                   quality_score: float, timeframe: str) -> float:
        """計算信心度"""
        try:
            # 基礎信心度 (基於質量和信號強度)
            base_confidence = (quality_score + abs(original_value - 0.5)) / 2
            
            # 時間框架調整
            timeframe_adjustments = {
                'short': 0.9,   # 短線信號噪音較多
                'medium': 1.0,  # 中線基準
                'long': 1.1     # 長線信號更穩定
            }
            
            timeframe_factor = timeframe_adjustments.get(timeframe, 1.0)
            confidence = base_confidence * timeframe_factor
            
            return min(max(confidence, 0.0), 1.0)
            
        except:
            return 0.6  # 默認信心度
    
    def _is_extreme_signal(self, standardized_value: float, quality_score: float) -> bool:
        """檢測是否為極端信號"""
        # 極端信號判定條件:
        # 1. 標準化值超過閾值
        # 2. 質量評分較高
        signal_extreme = abs(standardized_value - 0.5) > (self.config.extreme_signal_threshold - 0.5)
        quality_extreme = quality_score > self.config.quality_boost_threshold
        
        return signal_extreme and quality_extreme
    
    def _apply_extreme_amplification(self, standardized_value: float, 
                                   quality_score: float) -> float:
        """應用極端信號放大"""
        try:
            # 基礎放大倍數
            base_amplification = self.config.extreme_amplification_factor
            
            # 基於質量的動態調整
            quality_boost = 1.0 + (quality_score - 0.8) * 0.5  # 質量越高放大越多
            
            # 基於信號強度的調整
            strength_factor = abs(standardized_value - 0.5) * 2  # 0-1範圍
            strength_boost = 1.0 + strength_factor * 0.3
            
            # 綜合放大倍數
            amplification = base_amplification * quality_boost * strength_boost
            amplification = min(amplification, 2.0)  # 限制最大放大倍數
            
            self.performance_tracker['amplifications_applied'] += 1
            
            return amplification
            
        except:
            return self.config.extreme_amplification_factor
    
    def _update_performance_tracker(self, signal: StandardizedSignal):
        """更新性能追蹤器"""
        self.performance_tracker['standardization_count'] += 1
        
        if signal.is_extreme:
            self.performance_tracker['extreme_signals_detected'] += 1
        
        if signal.amplification_applied > 1.0:
            self.performance_tracker['amplifications_applied'] += 1
        
        # 質量改進檢測
        raw_quality = abs(signal.original_value - 0.5) * 2
        if signal.quality_score > raw_quality:
            self.performance_tracker['quality_improvements'] += 1
    
    def _get_module_stability_factor(self, module_name: str) -> float:
        """獲取模組穩定性因子"""
        # 基於歷史表現的穩定性評估
        stability_factors = {
            'technical_structure': 0.9,
            'volume_microstructure': 0.85,
            'sentiment_indicators': 0.75,
            'smart_money_detection': 0.95,
            'macro_environment': 0.8,
            'cross_market_correlation': 0.85,
            'event_driven_signals': 0.7
        }
        return stability_factors.get(module_name, 0.8)

class MultiTimeframeIntegrator:
    """多時間框架整合器"""
    
    def __init__(self, standardization_engine: SignalStandardizationEngine):
        self.standardization_engine = standardization_engine
        self.config = standardization_engine.config
        
    def integrate_multi_timeframe_signals(self, signals_by_timeframe: Dict[str, List[Dict]]) -> MultiTimeframeAnalysis:
        """整合多時間框架信號"""
        try:
            # 1. 標準化各時間框架的信號
            standardized_signals = {}
            
            for timeframe, signals in signals_by_timeframe.items():
                standardized_signals[timeframe] = []
                for signal_data in signals:
                    standardized_signal = self.standardization_engine.standardize_signal(
                        signal_value=signal_data['value'],
                        signal_id=signal_data['id'],
                        module_name=signal_data['module'],
                        timeframe=timeframe
                    )
                    standardized_signals[timeframe].append(standardized_signal)
            
            # 2. 計算各時間框架的綜合評分
            timeframe_scores = {}
            for timeframe, signals in standardized_signals.items():
                if signals:
                    avg_score = statistics.mean([s.standardized_value for s in signals])
                    weighted_score = avg_score * self._get_timeframe_weight(timeframe)
                    timeframe_scores[timeframe] = weighted_score
            
            # 3. 計算整合評分
            integrated_score = sum(timeframe_scores.values())
            
            # 4. 計算共識強度
            consensus_strength = self._calculate_consensus_strength(standardized_signals)
            
            # 5. 計算時間框架對齊度
            timeframe_alignment = self._calculate_timeframe_alignment(timeframe_scores)
            
            # 6. 創建分析結果
            analysis = MultiTimeframeAnalysis(
                short_term_signals=standardized_signals.get('short', []),
                medium_term_signals=standardized_signals.get('medium', []),
                long_term_signals=standardized_signals.get('long', []),
                integrated_score=integrated_score,
                consensus_strength=consensus_strength,
                timeframe_alignment=timeframe_alignment
            )
            
            logger.info(f"多時間框架整合完成 - 整合評分: {integrated_score:.3f}, "
                       f"共識強度: {consensus_strength:.3f}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"多時間框架整合失敗: {str(e)}")
            raise
    
    def _get_timeframe_weight(self, timeframe: str) -> float:
        """獲取時間框架權重"""
        weights = {
            'short': self.config.short_term_weight,
            'medium': self.config.medium_term_weight,
            'long': self.config.long_term_weight
        }
        return weights.get(timeframe, 0.3)
    
    def _calculate_consensus_strength(self, standardized_signals: Dict[str, List[StandardizedSignal]]) -> float:
        """計算共識強度"""
        try:
            all_values = []
            for signals in standardized_signals.values():
                all_values.extend([s.standardized_value for s in signals])
            
            if len(all_values) < 2:
                return 0.5
            
            # 計算標準差，低標準差表示高共識
            std_dev = statistics.stdev(all_values)
            consensus = max(0.0, 1.0 - std_dev * 2)  # 轉換為0-1範圍
            
            return consensus
            
        except:
            return 0.5
    
    def _calculate_timeframe_alignment(self, timeframe_scores: Dict[str, float]) -> float:
        """計算時間框架對齊度"""
        try:
            if len(timeframe_scores) < 2:
                return 0.5
            
            scores = list(timeframe_scores.values())
            
            # 計算評分之間的一致性
            mean_score = statistics.mean(scores)
            deviations = [abs(score - mean_score) for score in scores]
            avg_deviation = statistics.mean(deviations)
            
            # 轉換為對齊度 (低偏差 = 高對齊)
            alignment = max(0.0, 1.0 - avg_deviation * 4)
            
            return alignment
            
        except:
            return 0.5

class Phase1CSignalProcessor:
    """階段1C主要處理器 - 整合所有功能"""
    
    def __init__(self, config: SignalNormalizationConfig = None):
        self.config = config or SignalNormalizationConfig()
        self.standardization_engine = SignalStandardizationEngine(self.config)
        self.multi_timeframe_integrator = MultiTimeframeIntegrator(self.standardization_engine)
        
        # 與階段1A+1B的整合點
        self.phase1ab_integration_ready = True
        
        logger.info("階段1C信號處理器初始化完成")
    
    def process_enhanced_signals(self, raw_signals: Dict[str, Any], 
                                phase1ab_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        處理增強信號 - 階段1C的主要入口點
        整合階段1A的模組分類和階段1B的波動適應性
        """
        try:
            # 1. 提取階段1A+1B的上下文信息
            if phase1ab_context:
                volatility_metrics = phase1ab_context.get('volatility_metrics', {})
                continuity_metrics = phase1ab_context.get('continuity_metrics', {})
                active_cycle = phase1ab_context.get('active_cycle', 'medium')
            else:
                volatility_metrics = {}
                continuity_metrics = {}
                active_cycle = 'medium'
            
            # 2. 根據階段1B的波動性調整標準化參數
            self._adjust_config_by_volatility(volatility_metrics)
            
            # 3. 準備多時間框架信號數據
            signals_by_timeframe = self._prepare_timeframe_signals(raw_signals, active_cycle)
            
            # 4. 執行多時間框架整合
            multiframe_analysis = self.multi_timeframe_integrator.integrate_multi_timeframe_signals(
                signals_by_timeframe
            )
            
            # 5. 生成極端信號指標
            extreme_metrics = self._generate_extreme_signal_metrics()
            
            # 6. 計算階段1C增強評分
            enhanced_score = self._calculate_enhanced_score(
                multiframe_analysis, extreme_metrics, continuity_metrics
            )
            
            # 7. 準備返回結果
            result = {
                'phase': '階段1C - 信號標準化與極端信號放大',
                'enhancement_applied': True,
                'phase1c_metrics': {
                    'standardization_metrics': {
                        'total_signals_processed': self.standardization_engine.performance_tracker['standardization_count'],
                        'extreme_signals_detected': self.standardization_engine.performance_tracker['extreme_signals_detected'],
                        'amplifications_applied': self.standardization_engine.performance_tracker['amplifications_applied'],
                        'average_quality_score': self._calculate_average_quality()
                    },
                    'multiframe_analysis': asdict(multiframe_analysis),
                    'extreme_signal_metrics': asdict(extreme_metrics)
                },
                'enhanced_score': enhanced_score,
                'integration_status': {
                    'phase1a_compatibility': True,
                    'phase1b_volatility_adapted': bool(volatility_metrics),
                    'signal_continuity_enhanced': bool(continuity_metrics)
                },
                'performance_improvements': {
                    'signal_standardization_quality': self._calculate_standardization_improvement(),
                    'extreme_signal_detection_rate': self._calculate_extreme_detection_rate(),
                    'multi_timeframe_consensus': multiframe_analysis.consensus_strength
                }
            }
            
            logger.info(f"階段1C信號處理完成 - 增強評分: {enhanced_score:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"階段1C信號處理失敗: {str(e)}")
            raise
    
    def _adjust_config_by_volatility(self, volatility_metrics: Dict[str, Any]):
        """根據階段1B的波動性指標調整配置"""
        try:
            current_volatility = volatility_metrics.get('current_volatility', 0.5)
            
            if current_volatility > 0.8:  # 高波動環境
                # 提高極端信號檢測靈敏度
                self.config.extreme_signal_threshold = 0.75
                self.config.extreme_amplification_factor = 1.6
                logger.info("高波動環境 - 調整極端信號檢測參數")
                
            elif current_volatility < 0.3:  # 低波動環境
                # 降低檢測靈敏度，避免誤判
                self.config.extreme_signal_threshold = 0.85
                self.config.extreme_amplification_factor = 1.3
                logger.info("低波動環境 - 調整極端信號檢測參數")
                
        except Exception as e:
            logger.warning(f"波動性調整失敗: {str(e)}")
    
    def _prepare_timeframe_signals(self, raw_signals: Dict[str, Any], 
                                  active_cycle: str) -> Dict[str, List[Dict]]:
        """準備多時間框架信號數據"""
        try:
            # 基於活躍週期調整時間框架權重
            if active_cycle.lower() == 'short':
                self.config.short_term_weight = 0.6
                self.config.medium_term_weight = 0.3
                self.config.long_term_weight = 0.1
            elif active_cycle.lower() == 'long':
                self.config.short_term_weight = 0.2
                self.config.medium_term_weight = 0.3
                self.config.long_term_weight = 0.5
            else:  # medium
                self.config.short_term_weight = 0.3
                self.config.medium_term_weight = 0.4
                self.config.long_term_weight = 0.3
            
            # 構建時間框架信號結構
            signals_by_timeframe = {
                'short': [],
                'medium': [],
                'long': []
            }
            
            # 從原始信號中提取並分配到不同時間框架
            for module_name, signal_data in raw_signals.items():
                if isinstance(signal_data, dict) and 'value' in signal_data:
                    # 根據模組特性分配到合適的時間框架
                    primary_timeframe = self._get_module_primary_timeframe(module_name)
                    
                    signal_info = {
                        'id': f"{module_name}_{datetime.now().strftime('%H%M%S')}",
                        'module': module_name,
                        'value': signal_data['value']
                    }
                    
                    signals_by_timeframe[primary_timeframe].append(signal_info)
                    
                    # 某些重要信號同時加入其他時間框架
                    if module_name in ['smart_money_detection', 'technical_structure']:
                        for tf in ['short', 'medium', 'long']:
                            if tf != primary_timeframe:
                                signals_by_timeframe[tf].append(signal_info.copy())
            
            return signals_by_timeframe
            
        except Exception as e:
            logger.error(f"時間框架信號準備失敗: {str(e)}")
            return {'short': [], 'medium': [], 'long': []}
    
    def _get_module_primary_timeframe(self, module_name: str) -> str:
        """獲取模組的主要時間框架"""
        module_timeframes = {
            'volume_microstructure': 'short',      # 微結構適合短線
            'technical_structure': 'medium',       # 技術結構適合中線
            'sentiment_indicators': 'short',       # 情緒變化較快
            'smart_money_detection': 'medium',     # 機構行為中線為主
            'macro_environment': 'long',           # 宏觀環境長線
            'cross_market_correlation': 'long',    # 跨市場關聯長線
            'event_driven_signals': 'short'        # 事件驅動短線反應
        }
        return module_timeframes.get(module_name, 'medium')

    def _generate_extreme_signal_metrics(self) -> ExtremeSignalMetrics:
        """生成極端信號指標"""
        try:
            total_signals = len(self.standardization_engine.signal_history)
            extreme_signals = [s for s in self.standardization_engine.signal_history if s.is_extreme]
            extreme_count = len(extreme_signals)
            
            extreme_ratio = extreme_count / total_signals if total_signals > 0 else 0
            
            avg_amplification = statistics.mean([s.amplification_applied for s in extreme_signals]) if extreme_signals else 1.0
            
            # 質量分布統計
            quality_distribution = {'A': 0, 'B': 0, 'C': 0}
            for signal in self.standardization_engine.signal_history:
                if signal.quality_score > 0.8:
                    quality_distribution['A'] += 1
                elif signal.quality_score > 0.6:
                    quality_distribution['B'] += 1
                else:
                    quality_distribution['C'] += 1
            
            # 頂級表現模組
            module_performance = {}
            for signal in extreme_signals:
                if signal.module_name not in module_performance:
                    module_performance[signal.module_name] = []
                module_performance[signal.module_name].append(signal.quality_score)
            
            top_modules = sorted(
                module_performance.items(),
                key=lambda x: statistics.mean(x[1]) if x[1] else 0,
                reverse=True
            )[:3]
            
            top_performing_modules = [module[0] for module in top_modules]
            
            return ExtremeSignalMetrics(
                total_signals=total_signals,
                extreme_signals_count=extreme_count,
                extreme_signal_ratio=extreme_ratio,
                average_amplification=avg_amplification,
                quality_distribution=quality_distribution,
                top_performing_modules=top_performing_modules
            )
            
        except Exception as e:
            logger.error(f"極端信號指標生成失敗: {str(e)}")
            return ExtremeSignalMetrics(0, 0, 0.0, 1.0, {'A': 0, 'B': 0, 'C': 0}, [])

    def _calculate_enhanced_score(self, multiframe_analysis: MultiTimeframeAnalysis, 
                                 extreme_metrics: ExtremeSignalMetrics,
                                 continuity_metrics: Dict[str, Any]) -> float:
        """計算階段1C增強評分"""
        try:
            # 基礎多時間框架評分
            base_score = multiframe_analysis.integrated_score
            
            # 共識強度加成
            consensus_bonus = multiframe_analysis.consensus_strength * 0.2
            
            # 時間框架對齊加成
            alignment_bonus = multiframe_analysis.timeframe_alignment * 0.1
            
            # 極端信號質量加成
            extreme_bonus = extreme_metrics.extreme_signal_ratio * 0.15
            
            # 階段1B連續性整合
            continuity_bonus = 0
            if continuity_metrics:
                signal_persistence = continuity_metrics.get('signal_persistence', 0.5)
                consensus_strength = continuity_metrics.get('consensus_strength', 0.5)
                continuity_bonus = (signal_persistence + consensus_strength) * 0.1
            
            # 綜合增強評分
            enhanced_score = base_score + consensus_bonus + alignment_bonus + extreme_bonus + continuity_bonus
            enhanced_score = min(enhanced_score, 1.0)  # 確保不超過1.0
            
            return enhanced_score
            
        except Exception as e:
            logger.error(f"增強評分計算失敗: {str(e)}")
            return 0.5

    def _calculate_average_quality(self) -> float:
        """計算平均質量評分"""
        if not self.standardization_engine.signal_history:
            return 0.5
        return statistics.mean([s.quality_score for s in self.standardization_engine.signal_history])

    def _calculate_standardization_improvement(self) -> float:
        """計算標準化改進度"""
        if not self.standardization_engine.signal_history:
            return 0.0
        
        # 比較標準化前後的質量提升
        quality_improvements = []
        for signal in self.standardization_engine.signal_history:
            # 模擬標準化前的質量（基於原始值）
            raw_quality = abs(signal.original_value - 0.5) * 2
            improvement = signal.quality_score - raw_quality
            quality_improvements.append(max(improvement, 0))
        
        return statistics.mean(quality_improvements) if quality_improvements else 0.0

    def _calculate_extreme_detection_rate(self) -> float:
        """計算極端信號檢測率"""
        total_signals = len(self.standardization_engine.signal_history)
        if total_signals == 0:
            return 0.0
        
        extreme_signals = sum(1 for s in self.standardization_engine.signal_history if s.is_extreme)
        return extreme_signals / total_signals

# 全局實例
phase1c_processor = Phase1CSignalProcessor()

def get_phase1c_processor() -> Phase1CSignalProcessor:
    """獲取階段1C處理器實例"""
    return phase1c_processor

# 為了與現有階段1A+1B系統整合的兼容性函數
def integrate_with_phase1ab(phase1ab_result: Dict[str, Any], 
                           raw_signals: Dict[str, Any]) -> Dict[str, Any]:
    """與階段1A+1B整合的主要函數"""
    try:
        processor = get_phase1c_processor()
        
        # 提取階段1A+1B的上下文
        phase1ab_context = {
            'volatility_metrics': phase1ab_result.get('phase_1b_metrics', {}).get('volatility_metrics', {}),
            'continuity_metrics': phase1ab_result.get('phase_1b_metrics', {}).get('continuity_metrics', {}),
            'active_cycle': phase1ab_result.get('active_cycle', 'medium')
        }
        
        # 執行階段1C處理
        phase1c_result = processor.process_enhanced_signals(raw_signals, phase1ab_context)
        
        # 整合結果
        integrated_result = {
            **phase1ab_result,  # 包含階段1A+1B的所有結果
            'phase1c_enhancement': phase1c_result,
            'final_enhanced_score': phase1c_result['enhanced_score'],
            'integration_summary': {
                'phase1a_signal_modules': 7,
                'phase1b_volatility_adaptation': True,
                'phase1c_signal_standardization': True,
                'total_enhancement_applied': True
            }
        }
        
        logger.info("階段1A+1B+1C完全整合成功")
        return integrated_result
        
    except Exception as e:
        logger.error(f"階段1A+1B+1C整合失敗: {str(e)}")
        raise
