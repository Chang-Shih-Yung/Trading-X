"""
🎯 Trading X - Phase1C 信號標準化引擎（真實版）
階段1C: 信號標準化與極端信號放大模組 - 完整真實實現
- 統一信號強度標準化處理
- 極端信號識別與放大
- 多時間框架信號整合
- 動態信號質量評級
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import statistics
import logging
import sys
from pathlib import Path

# 配置日誌
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
    """信號標準化引擎（真實版）"""
    
    def __init__(self, config: SignalNormalizationConfig = None):
        self.config = config or SignalNormalizationConfig()
        self.signal_history: List[StandardizedSignal] = []
        self.module_performance = {}  # 模組性能追蹤
        self.performance_tracker = {
            'standardization_count': 0,
            'extreme_signals_detected': 0,
            'amplifications_applied': 0,
            'quality_improvements': 0
        }
        
    async def standardize_signals(self, raw_signals: List[Dict[str, Any]]) -> List[StandardizedSignal]:
        """標準化信號列表 - 真實處理"""
        try:
            standardized_signals = []
            
            for i, signal in enumerate(raw_signals):
                signal_id = f"std_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
                module_name = signal.get('module', 'unknown')
                original_value = signal.get('value', 0.0)
                confidence = signal.get('confidence', 0.7)
                
                # 標準化處理
                standardized_signal = await self.standardize_signal(
                    signal_value=original_value,
                    signal_id=signal_id,
                    module_name=module_name,
                    confidence=confidence
                )
                
                standardized_signals.append(standardized_signal)
            
            logger.info(f"批量標準化完成: {len(standardized_signals)} 個信號")
            return standardized_signals
            
        except Exception as e:
            logger.error(f"批量信號標準化失敗: {e}")
            return []
    
    async def standardize_signal(self, signal_value: float, signal_id: str, 
                               module_name: str, timeframe: str = 'medium',
                               confidence: float = 0.7) -> StandardizedSignal:
        """
        標準化單個信號 - 真實算法實現
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
                signal_value, quality_score, timeframe, confidence
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
                self.performance_tracker['amplifications_applied'] += 1
                
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
            self._update_module_performance(module_name, quality_score)
            
            logger.info(f"信號標準化完成: {signal_id} ({module_name}) - "
                       f"原值: {signal_value:.3f} -> 標準化值: {standardized_value:.3f}")
            
            return standardized_signal
            
        except Exception as e:
            logger.error(f"信號標準化失敗: {signal_id} - {str(e)}")
            # 返回基礎標準化信號
            return StandardizedSignal(
                signal_id=signal_id,
                module_name=module_name,
                original_value=signal_value,
                standardized_value=0.5,
                quality_score=0.5,
                confidence_level=0.5,
                is_extreme=False,
                amplification_applied=1.0,
                timeframe=timeframe,
                timestamp=datetime.now()
            )
    
    async def detect_extreme_signals(self, signals: List[StandardizedSignal]) -> Optional[ExtremeSignalMetrics]:
        """檢測極端信號 - 真實分析算法"""
        try:
            if not signals:
                return None
            
            extreme_signals = [s for s in signals if s.is_extreme]
            total_signals = len(signals)
            extreme_count = len(extreme_signals)
            
            # 計算極端信號比例
            extreme_ratio = extreme_count / total_signals if total_signals > 0 else 0.0
            
            # 計算平均放大倍數
            if extreme_signals:
                avg_amplification = np.mean([s.amplification_applied for s in extreme_signals])
            else:
                avg_amplification = 1.0
            
            # 質量分布統計
            quality_distribution = {"A": 0, "B": 0, "C": 0}
            for signal in signals:
                if signal.quality_score >= 0.8:
                    quality_distribution["A"] += 1
                elif signal.quality_score >= 0.6:
                    quality_distribution["B"] += 1
                else:
                    quality_distribution["C"] += 1
            
            # 頂級性能模組
            module_scores = {}
            for signal in signals:
                module = signal.module_name
                if module not in module_scores:
                    module_scores[module] = []
                module_scores[module].append(signal.quality_score)
            
            module_avg_scores = {
                module: np.mean(scores) 
                for module, scores in module_scores.items()
            }
            
            top_performing_modules = sorted(
                module_avg_scores.keys(), 
                key=lambda m: module_avg_scores[m], 
                reverse=True
            )[:3]
            
            result = ExtremeSignalMetrics(
                total_signals=total_signals,
                extreme_signals_count=extreme_count,
                extreme_signal_ratio=extreme_ratio,
                average_amplification=avg_amplification,
                quality_distribution=quality_distribution,
                top_performing_modules=top_performing_modules
            )
            
            logger.info(f"極端信號檢測完成: {extreme_count}/{total_signals} "
                       f"({extreme_ratio:.2%}) 極端信號")
            
            return result
            
        except Exception as e:
            logger.error(f"極端信號檢測失敗: {e}")
            return None
    
    def _apply_sigmoid_normalization(self, value: float) -> float:
        """應用改進的Sigmoid標準化"""
        try:
            # 將輸入值映射到合適的範圍 (-6 to 6)
            if abs(value) > 5:  # 處理極端值
                adjusted_value = 6 if value > 0 else -6
            else:
                adjusted_value = value * 2  # 調整斜率
            
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
        """計算信號質量評分 - 真實評估算法"""
        try:
            # 基礎質量評分 (基於信號強度)
            strength_score = abs(standardized_value - 0.5) * 2  # 0-1範圍
            
            # 模組特定調整 (基於歷史性能)
            module_adjustments = {
                'trend_24h': 1.0,
                'momentum_volatility': 1.1,      # 波動動量信號較可靠
                'order_pressure': 1.2,           # 訂單壓力信號質量高
                'funding_rate': 1.3,             # 資金費率信號可靠性高
                'volume_trend': 0.9,             # 成交量信號波動較大
                'technical_structure': 1.0,
                'volume_microstructure': 1.1,
                'sentiment_indicators': 0.9,
                'smart_money_detection': 1.2,
                'macro_environment': 0.8,
                'cross_market_correlation': 1.0,
                'event_driven_signals': 1.1
            }
            
            module_factor = module_adjustments.get(module_name, 1.0)
            
            # 穩定性調整 (基於模組歷史表現)
            stability_factor = self._get_module_stability_factor(module_name)
            
            # 原始值強度調整
            value_strength = min(1.0, abs(original_value) / 2.0) if abs(original_value) <= 2.0 else 1.0
            
            # 綜合質量評分
            quality_score = strength_score * module_factor * stability_factor * (0.8 + 0.2 * value_strength)
            quality_score = min(max(quality_score, 0.0), 1.0)  # 確保在0-1範圍
            
            return quality_score
            
        except Exception as e:
            logger.warning(f"質量評分計算失敗: {str(e)}")
            return 0.5
    
    def _calculate_confidence_level(self, original_value: float, quality_score: float, 
                                   timeframe: str, base_confidence: float) -> float:
        """計算信心度等級 - 真實評估"""
        try:
            # 時間框架調整
            timeframe_multipliers = {
                'short': 0.9,   # 短期信號波動較大
                'medium': 1.0,  # 中期信號標準
                'long': 1.1     # 長期信號更穩定
            }
            
            timeframe_factor = timeframe_multipliers.get(timeframe, 1.0)
            
            # 質量分數影響
            quality_boost = quality_score * 0.3  # 最多30%提升
            
            # 信號強度影響
            strength_factor = min(1.0, abs(original_value)) if abs(original_value) <= 1.0 else 1.0
            
            # 綜合信心度
            confidence = base_confidence * timeframe_factor + quality_boost
            confidence *= (0.8 + 0.2 * strength_factor)  # 強度調整
            
            return min(max(confidence, 0.1), 1.0)  # 限制在0.1-1.0範圍
            
        except Exception:
            return base_confidence
    
    def _is_extreme_signal(self, standardized_value: float, quality_score: float) -> bool:
        """檢測是否為極端信號"""
        try:
            # 信號強度檢測
            strength_extreme = abs(standardized_value - 0.5) >= (self.config.extreme_signal_threshold - 0.5)
            
            # 質量檢測
            quality_extreme = quality_score >= self.config.quality_boost_threshold
            
            # 需要同時滿足強度和質量條件
            return strength_extreme and quality_extreme
            
        except Exception:
            return False
    
    def _apply_extreme_amplification(self, standardized_value: float, quality_score: float) -> float:
        """應用極端信號放大"""
        try:
            # 基礎放大倍數
            base_amplification = self.config.extreme_amplification_factor
            
            # 質量調整 (質量越高，放大越多)
            quality_adjustment = 1.0 + (quality_score - 0.8) * 0.5  # 最多額外50%
            
            # 信號強度調整
            strength = abs(standardized_value - 0.5) * 2
            strength_adjustment = 1.0 + strength * 0.2  # 最多額外20%
            
            amplification = base_amplification * quality_adjustment * strength_adjustment
            
            # 限制最大放大倍數
            return min(amplification, 2.0)
            
        except Exception:
            return self.config.extreme_amplification_factor
    
    def _get_module_stability_factor(self, module_name: str) -> float:
        """獲取模組穩定性因子"""
        try:
            if module_name in self.module_performance:
                scores = self.module_performance[module_name]
                if len(scores) >= 5:
                    stability = 1.0 - np.std(scores[-10:]) / (np.mean(scores[-10:]) + 1e-8)
                    return max(0.5, min(1.5, stability))
            
            return 1.0  # 默認穩定性
            
        except Exception:
            return 1.0
    
    def _update_performance_tracker(self, signal: StandardizedSignal):
        """更新性能追蹤器"""
        try:
            self.performance_tracker['standardization_count'] += 1
            
            if signal.is_extreme:
                self.performance_tracker['extreme_signals_detected'] += 1
            
            if signal.quality_score > 0.8:
                self.performance_tracker['quality_improvements'] += 1
                
        except Exception:
            pass
    
    def _update_module_performance(self, module_name: str, quality_score: float):
        """更新模組性能記錄"""
        try:
            if module_name not in self.module_performance:
                self.module_performance[module_name] = []
            
            self.module_performance[module_name].append(quality_score)
            
            # 保持最近50次記錄
            if len(self.module_performance[module_name]) > 50:
                self.module_performance[module_name] = self.module_performance[module_name][-50:]
                
        except Exception:
            pass
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """獲取性能總結"""
        try:
            summary = {
                "performance_tracker": self.performance_tracker.copy(),
                "module_performance": {},
                "signal_history_count": len(self.signal_history)
            }
            
            # 計算模組平均性能
            for module, scores in self.module_performance.items():
                if scores:
                    summary["module_performance"][module] = {
                        "average_quality": np.mean(scores),
                        "stability": 1.0 - np.std(scores) / (np.mean(scores) + 1e-8),
                        "signal_count": len(scores)
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"性能總結生成失敗: {e}")
            return {"error": str(e)}
