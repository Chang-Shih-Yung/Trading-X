"""
🎯 Trading X - Phase1B 波動適應引擎（真實版）
階段1B：波動適應性優化增強模組 - 完整真實實現
"""

from typing import Dict, List, Optional, Tuple, Any, Deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
import logging
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# 添加上級目錄到路徑
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent.parent / "core"))

from binance_data_connector import binance_connector

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
    """波動適應性引擎（真實版）"""
    
    def __init__(self, lookback_periods: int = 100):
        self.lookback_periods = lookback_periods
        self.volatility_history: Deque[float] = deque(maxlen=lookback_periods)
        self.signal_history: Deque[Dict] = deque(maxlen=lookback_periods)
        
    async def calculate_volatility_metrics(self, price_data: List[float] = None, symbol: str = "BTCUSDT") -> VolatilityMetrics:
        """計算綜合波動性指標 - 基於真實市場數據"""
        try:
            # 如果沒有提供價格數據，從幣安API獲取
            if not price_data:
                async with binance_connector as connector:
                    price_data = await connector.calculate_price_series(symbol, 200)
            
            if len(price_data) < 20:
                logger.warning("價格數據不足，使用最小可用數據計算")
                return self._get_minimal_volatility_metrics()
            
            prices = np.array(price_data)
            returns = np.diff(np.log(prices))
            
            # 1. 當前波動率 (21期滾動標準差)
            if len(returns) >= 21:
                current_volatility = np.std(returns[-21:])
            else:
                current_volatility = np.std(returns)
            
            # 年化並標準化到 0-1 範圍
            annualized_vol = current_volatility * np.sqrt(365 * 24 * 60)  # 分鐘數據年化
            current_volatility = min(1.0, annualized_vol / 2.0)  # 假設200%年化波動率為上限
            
            # 2. 波動趨勢 (短期vs長期波動比較)
            if len(returns) >= 50:
                short_vol = np.std(returns[-10:])
                long_vol = np.std(returns[-50:])
                volatility_trend = (short_vol - long_vol) / (long_vol + 1e-8)
                volatility_trend = max(-1, min(1, volatility_trend))
            else:
                volatility_trend = 0.0
            
            # 3. 波動率百分位
            self.volatility_history.append(current_volatility)
            if len(self.volatility_history) >= 20:
                sorted_vol = sorted(list(self.volatility_history))
                rank = sum(1 for v in sorted_vol if v <= current_volatility)
                volatility_percentile = rank / len(sorted_vol)
            else:
                volatility_percentile = 0.5
            
            # 4. 制度穩定性 (波動的波動)
            if len(self.volatility_history) >= 10:
                recent_vols = list(self.volatility_history)[-10:]
                vol_mean = np.mean(recent_vols)
                vol_std = np.std(recent_vols)
                regime_stability = 1.0 - (vol_std / (vol_mean + 1e-8))
                regime_stability = max(0, min(1, regime_stability))
            else:
                regime_stability = 0.7
            
            # 5. 微觀波動 (高頻價格變動強度)
            if len(returns) >= 10:
                micro_moves = np.abs(returns[-10:])
                micro_volatility = np.mean(micro_moves) / (current_volatility + 1e-8)
                micro_volatility = max(0, min(1, micro_volatility))
            else:
                micro_volatility = 0.5
            
            # 6. 日內波動 (基於價格範圍)
            if len(prices) >= 60:  # 至少1小時數據
                hourly_high = max(prices[-60:])
                hourly_low = min(prices[-60:])
                hourly_range = (hourly_high - hourly_low) / hourly_low
                intraday_volatility = min(1.0, hourly_range * 10)  # 10%為上限
            else:
                intraday_volatility = current_volatility
            
            result = VolatilityMetrics(
                current_volatility=current_volatility,
                volatility_trend=volatility_trend,
                volatility_percentile=volatility_percentile,
                regime_stability=regime_stability,
                micro_volatility=micro_volatility,
                intraday_volatility=intraday_volatility,
                timestamp=datetime.now()
            )
            
            logger.info(f"波動性指標計算完成: 當前波動率={current_volatility:.4f}, 趨勢={volatility_trend:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"波動性指標計算失敗: {e}")
            return self._get_minimal_volatility_metrics()
    
    async def analyze_signal_continuity(self, signals: List[Dict[str, Any]], symbol: str = "BTCUSDT") -> SignalContinuityMetrics:
        """分析信號連續性 - 基於真實信號歷史"""
        try:
            # 記錄當前信號到歷史
            current_signals = {
                "timestamp": datetime.now(),
                "signals": signals,
                "signal_count": len(signals)
            }
            self.signal_history.append(current_signals)
            
            if len(self.signal_history) < 3:
                logger.info("信號歷史不足，使用基礎評估")
                return self._get_basic_continuity_metrics(signals)
            
            # 1. 信號持續性 (信號在連續時間段內的出現率)
            recent_periods = list(self.signal_history)[-10:]
            signal_appearances = sum(1 for period in recent_periods if period["signal_count"] > 0)
            signal_persistence = signal_appearances / len(recent_periods)
            
            # 2. 信號分歧度 (不同信號源的一致性)
            if signals:
                signal_values = [s.get("value", 0) for s in signals if "value" in s]
                if len(signal_values) > 1:
                    signal_std = np.std(signal_values)
                    signal_mean = np.mean(signal_values)
                    signal_divergence = signal_std / (abs(signal_mean) + 1e-8)
                    signal_divergence = min(1.0, signal_divergence)
                else:
                    signal_divergence = 0.0
            else:
                signal_divergence = 1.0  # 沒有信號時分歧度最高
            
            # 3. 共識強度 (多個信號指向同一方向的程度)
            if signals:
                positive_signals = sum(1 for s in signals if s.get("value", 0) > 0)
                negative_signals = sum(1 for s in signals if s.get("value", 0) < 0)
                total_signals = len(signals)
                
                if total_signals > 0:
                    max_consensus = max(positive_signals, negative_signals)
                    consensus_strength = max_consensus / total_signals
                else:
                    consensus_strength = 0.0
            else:
                consensus_strength = 0.0
            
            # 4. 時間一致性 (信號強度在時間上的穩定性)
            if len(recent_periods) >= 5:
                signal_counts = [p["signal_count"] for p in recent_periods[-5:]]
                avg_count = np.mean(signal_counts)
                count_std = np.std(signal_counts)
                temporal_consistency = 1.0 - (count_std / (avg_count + 1e-8))
                temporal_consistency = max(0, min(1, temporal_consistency))
            else:
                temporal_consistency = 0.6
            
            # 5. 跨模組相關性 (不同模組信號的相關性)
            if len(signals) >= 2:
                module_values = {}
                for signal in signals:
                    module = signal.get("module", "unknown")
                    value = signal.get("value", 0)
                    if module not in module_values:
                        module_values[module] = []
                    module_values[module].append(value)
                
                # 計算模組間相關性
                modules = list(module_values.keys())
                if len(modules) >= 2:
                    correlations = []
                    for i in range(len(modules)):
                        for j in range(i+1, len(modules)):
                            module1_values = module_values[modules[i]]
                            module2_values = module_values[modules[j]]
                            
                            # 簡化相關性計算
                            avg1 = np.mean(module1_values)
                            avg2 = np.mean(module2_values)
                            correlation = 1.0 - abs(avg1 - avg2) / 2.0  # 簡化的相關性度量
                            correlations.append(max(0, correlation))
                    
                    cross_module_correlation = np.mean(correlations) if correlations else 0.5
                else:
                    cross_module_correlation = 0.5
            else:
                cross_module_correlation = 0.5
            
            # 6. 信號衰減率 (信號強度隨時間的衰減)
            if len(recent_periods) >= 3:
                recent_counts = [p["signal_count"] for p in recent_periods[-3:]]
                if recent_counts[0] > 0:
                    decay_rate = (recent_counts[0] - recent_counts[-1]) / recent_counts[0]
                    decay_rate = max(0, min(1, decay_rate))
                else:
                    decay_rate = 0.5
            else:
                decay_rate = 0.3
            
            result = SignalContinuityMetrics(
                signal_persistence=signal_persistence,
                signal_divergence=signal_divergence,
                consensus_strength=consensus_strength,
                temporal_consistency=temporal_consistency,
                cross_module_correlation=cross_module_correlation,
                signal_decay_rate=decay_rate
            )
            
            logger.info(f"信號連續性分析完成: 持續性={signal_persistence:.3f}, 共識={consensus_strength:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"信號連續性分析失敗: {e}")
            return self._get_basic_continuity_metrics(signals)
    
    def _get_minimal_volatility_metrics(self) -> VolatilityMetrics:
        """獲取最小波動性指標（數據不足時使用）"""
        return VolatilityMetrics(
            current_volatility=0.02,  # 2% 基礎波動率
            volatility_trend=0.0,
            volatility_percentile=0.5,
            regime_stability=0.7,
            micro_volatility=0.5,
            intraday_volatility=0.5,
            timestamp=datetime.now()
        )
    
    def _get_basic_continuity_metrics(self, signals: List[Dict[str, Any]]) -> SignalContinuityMetrics:
        """獲取基礎連續性指標（歷史不足時使用）"""
        signal_count = len(signals)
        
        # 基於當前信號數量的簡單評估
        signal_persistence = min(1.0, signal_count / 5.0)  # 5個信號為滿分
        consensus_strength = min(1.0, signal_count / 3.0)  # 3個信號為基礎共識
        
        return SignalContinuityMetrics(
            signal_persistence=signal_persistence,
            signal_divergence=0.3,
            consensus_strength=consensus_strength,
            temporal_consistency=0.6,
            cross_module_correlation=0.7,
            signal_decay_rate=0.3
        )
