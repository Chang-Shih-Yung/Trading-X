#!/usr/bin/env python3
"""
🧠 Advanced Market Regime Detector
增強版市場狀態檢測系統 - Step 1 組件

整合技術指標、統計分析和機器學習，提供精確的市場狀態識別
基於現有 9 種 MarketRegime，增加智能模式識別能力

Phase 2 - Step 1: 市場狀態檢測增強
- 6特徵分析：波動度、趨勢強度、動量、成交量、價格行為、週期位置
- 置信度評分：基於特徵一致性的信心度計算
- 狀態轉換檢測：識別市場狀態變化
- 預測能力：基於歷史模式預測未來狀態
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import logging
from pathlib import Path
import sys

# 導入現有系統組件 - 避免循環依賴，使用本地定義
logger = logging.getLogger(__name__)

# 使用本地 MarketRegime 定義，避免循環導入
class MarketRegime(Enum):
    """市場狀態枚舉 - 本地定義版本"""
    UNKNOWN = "UNKNOWN"
    BULL_TREND = "BULL_TREND"
    BEAR_TREND = "BEAR_TREND"
    BREAKOUT_UP = "BREAKOUT_UP"
    BREAKOUT_DOWN = "BREAKOUT_DOWN"
    VOLATILE = "VOLATILE"
    SIDEWAYS = "SIDEWAYS"
    CONSOLIDATION = "CONSOLIDATION"
    TRENDING = "TRENDING"
    REVERSAL = "REVERSAL"
    RANGE_HIGH = "RANGE_HIGH"
    RANGE_MID = "RANGE_MID"
    RANGE_LOW = "RANGE_LOW"
    TREND_UP_HIGH = "TREND_UP_HIGH"
    TREND_UP_MID = "TREND_UP_MID"
    TREND_DOWN_HIGH = "TREND_DOWN_HIGH"
    TREND_DOWN_MID = "TREND_DOWN_MID"
    
# MarketData 本地定義
@dataclass
class MarketData:
    """市場數據結構"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

logger.info("✅ MarketRegime 本地定義已載入")

@dataclass
class MarketFeatures:
    """市場特徵數據結構"""
    volatility: float               # 波動度 (0-1)
    trend_strength: float           # 趨勢強度 (-1到1, 負數為下跌)
    momentum: float                 # 動量 (-1到1)
    volume_profile: float           # 成交量特徵 (0-2, 1為正常)
    price_action: float             # 價格行為 (-1到1)
    cycle_position: float           # 週期位置 (0-1)

@dataclass
class RegimeConfidence:
    """市場狀態信心度"""
    regime: MarketRegime
    confidence: float               # 信心度 (0-1)
    feature_scores: Dict[str, float]
    detection_time: datetime
    stability_score: float          # 穩定性分數 (0-1)

@dataclass
class RegimeTransition:
    """市場狀態轉換"""
    from_regime: MarketRegime
    to_regime: MarketRegime
    transition_time: datetime
    transition_strength: float
    key_indicators: List[str]

class AdvancedMarketRegimeDetector:
    """增強版市場狀態檢測器 - Phase 2 Step 1"""
    
    def __init__(self):
        self.current_regime = MarketRegime.UNKNOWN
        self.regime_history = []
        self.feature_weights = self._initialize_feature_weights()
        self.regime_thresholds = self._initialize_regime_thresholds()
        self.detection_cache = {}
        
        # 檢測統計
        self.detection_stats = {
            'total_detections': 0,
            'regime_transitions': 0,
            'confidence_scores': [],
            'stability_scores': []
        }
        
        logger.info("✅ AdvancedMarketRegimeDetector 初始化完成")
    
    def _initialize_feature_weights(self) -> Dict[str, float]:
        """初始化特徵權重"""
        return {
            'volatility': 0.2,
            'trend_strength': 0.25,
            'momentum': 0.2,
            'volume_profile': 0.15,
            'price_action': 0.15,
            'cycle_position': 0.05
        }
    
    def _initialize_regime_thresholds(self) -> Dict[MarketRegime, Dict[str, float]]:
        """初始化市場狀態閾值"""
        return {
            MarketRegime.BULL_TREND: {
                'trend_strength': 0.6,
                'momentum': 0.4,
                'volatility': 0.3,
                'confidence_threshold': 0.7
            },
            MarketRegime.BEAR_TREND: {
                'trend_strength': -0.6,
                'momentum': -0.4,
                'volatility': 0.3,
                'confidence_threshold': 0.7
            },
            MarketRegime.BREAKOUT_UP: {
                'momentum': 0.7,
                'volume_profile': 1.5,
                'price_action': 0.6,
                'confidence_threshold': 0.75
            },
            MarketRegime.BREAKOUT_DOWN: {
                'momentum': -0.7,
                'volume_profile': 1.5,
                'price_action': -0.6,
                'confidence_threshold': 0.75
            },
            MarketRegime.VOLATILE: {
                'volatility': 0.7,
                'trend_strength': 0.2,  # 低趨勢
                'confidence_threshold': 0.6
            },
            MarketRegime.SIDEWAYS: {
                'trend_strength': 0.15,  # 非常低趨勢
                'volatility': 0.4,
                'confidence_threshold': 0.65
            },
            MarketRegime.CONSOLIDATION: {
                'volatility': 0.25,  # 低波動
                'volume_profile': 0.7,  # 低成交量
                'confidence_threshold': 0.6
            },
            MarketRegime.TRENDING: {
                'trend_strength': 0.5,
                'momentum': 0.3,
                'confidence_threshold': 0.65
            }
        }
    
    async def detect_regime_change(self, market_data: pd.DataFrame, symbol: str) -> RegimeConfidence:
        """檢測市場狀態變化"""
        try:
            # 計算市場特徵
            features = self._calculate_market_features(market_data)
            
            # 評估所有可能的狀態
            regime_scores = {}
            for regime in MarketRegime:
                if regime != MarketRegime.UNKNOWN:
                    score = self._calculate_regime_score(features, regime)
                    regime_scores[regime] = score
            
            # 找出最佳匹配狀態
            best_regime = max(regime_scores, key=regime_scores.get)
            confidence = regime_scores[best_regime]
            
            # 計算穩定性分數
            stability = self._calculate_stability_score(features, best_regime)
            
            # 檢測狀態轉換
            if self.current_regime != best_regime and self.current_regime != MarketRegime.UNKNOWN:
                self._record_regime_transition(self.current_regime, best_regime)
                self.detection_stats['regime_transitions'] += 1
            
            self.current_regime = best_regime
            self.detection_stats['total_detections'] += 1
            self.detection_stats['confidence_scores'].append(confidence)
            self.detection_stats['stability_scores'].append(stability)
            
            # 創建結果
            result = RegimeConfidence(
                regime=best_regime,
                confidence=confidence,
                feature_scores={
                    'volatility': features.volatility,
                    'trend_strength': features.trend_strength,
                    'momentum': features.momentum,
                    'volume_profile': features.volume_profile,
                    'price_action': features.price_action,
                    'cycle_position': features.cycle_position
                },
                detection_time=datetime.now(),
                stability_score=stability
            )
            
            # 更新歷史記錄
            self.regime_history.append(result)
            if len(self.regime_history) > 100:  # 保持最近100條記錄
                self.regime_history = self.regime_history[-100:]
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 市場狀態檢測失敗: {e}")
            return RegimeConfidence(
                regime=MarketRegime.UNKNOWN,
                confidence=0.0,
                feature_scores={},
                detection_time=datetime.now(),
                stability_score=0.0
            )
    
    def _calculate_market_features(self, data: pd.DataFrame) -> MarketFeatures:
        """計算市場特徵"""
        try:
            # 確保有足夠的數據
            if len(data) < 20:
                return self._default_features()
            
            prices = data['close'].values
            volumes = data['volume'].values
            highs = data['high'].values
            lows = data['low'].values
            
            # 1. 波動度計算 (基於價格變化標準差)
            returns = np.diff(prices) / prices[:-1]
            volatility = min(1.0, np.std(returns) * np.sqrt(24) * 5)  # 年化波動度，限制在0-1
            
            # 2. 趨勢強度 (基於線性回歸斜率)
            x = np.arange(len(prices))
            trend_coef = np.polyfit(x, prices, 1)[0]
            trend_strength = np.tanh(trend_coef / np.mean(prices) * 100)  # 標準化到-1到1
            
            # 3. 動量 (基於價格變化和移動平均)
            if len(prices) >= 14:
                sma_fast = np.mean(prices[-7:])
                sma_slow = np.mean(prices[-14:])
                momentum = np.tanh((sma_fast - sma_slow) / sma_slow * 10)
            else:
                momentum = 0.0
            
            # 4. 成交量特徵 (相對於平均成交量)
            avg_volume = np.mean(volumes)
            recent_volume = np.mean(volumes[-5:])
            volume_profile = min(2.0, recent_volume / avg_volume) if avg_volume > 0 else 1.0
            
            # 5. 價格行為 (基於高低點分析)
            if len(prices) >= 5:
                recent_high = np.max(highs[-5:])
                recent_low = np.min(lows[-5:])
                current_price = prices[-1]
                price_range = recent_high - recent_low
                if price_range > 0:
                    price_position = (current_price - recent_low) / price_range
                    price_action = (price_position - 0.5) * 2  # 標準化到-1到1
                else:
                    price_action = 0.0
            else:
                price_action = 0.0
            
            # 6. 週期位置 (基於數據位置)
            cycle_position = min(1.0, len(data) / 100)  # 假設100為完整週期
            
            return MarketFeatures(
                volatility=volatility,
                trend_strength=trend_strength,
                momentum=momentum,
                volume_profile=volume_profile,
                price_action=price_action,
                cycle_position=cycle_position
            )
            
        except Exception as e:
            logger.error(f"❌ 市場特徵計算失敗: {e}")
            return self._default_features()
    
    def _default_features(self) -> MarketFeatures:
        """默認特徵值"""
        return MarketFeatures(
            volatility=0.3,
            trend_strength=0.0,
            momentum=0.0,
            volume_profile=1.0,
            price_action=0.0,
            cycle_position=0.5
        )
    
    def _calculate_regime_score(self, features: MarketFeatures, regime: MarketRegime) -> float:
        """計算特定狀態的匹配分數"""
        try:
            if regime not in self.regime_thresholds:
                return 0.0
            
            thresholds = self.regime_thresholds[regime]
            score = 0.0
            
            # 根據狀態類型計算匹配分數
            if regime == MarketRegime.BULL_TREND:
                score += self._score_threshold(features.trend_strength, thresholds['trend_strength'], True)
                score += self._score_threshold(features.momentum, thresholds['momentum'], True)
                score += self._score_threshold(features.volatility, thresholds['volatility'], False)
                
            elif regime == MarketRegime.BEAR_TREND:
                score += self._score_threshold(features.trend_strength, thresholds['trend_strength'], False)
                score += self._score_threshold(features.momentum, thresholds['momentum'], False)
                score += self._score_threshold(features.volatility, thresholds['volatility'], False)
                
            elif regime == MarketRegime.BREAKOUT_UP:
                score += self._score_threshold(features.momentum, thresholds['momentum'], True)
                score += self._score_threshold(features.volume_profile, thresholds['volume_profile'], True)
                score += self._score_threshold(features.price_action, thresholds['price_action'], True)
                
            elif regime == MarketRegime.BREAKOUT_DOWN:
                score += self._score_threshold(features.momentum, thresholds['momentum'], False)
                score += self._score_threshold(features.volume_profile, thresholds['volume_profile'], True)
                score += self._score_threshold(features.price_action, thresholds['price_action'], False)
                
            elif regime == MarketRegime.VOLATILE:
                score += self._score_threshold(features.volatility, thresholds['volatility'], True)
                score += self._score_threshold(abs(features.trend_strength), thresholds['trend_strength'], False)
                
            elif regime == MarketRegime.SIDEWAYS:
                score += self._score_threshold(abs(features.trend_strength), thresholds['trend_strength'], False)
                score += self._score_threshold(features.volatility, thresholds['volatility'], False)
                
            elif regime == MarketRegime.CONSOLIDATION:
                score += self._score_threshold(features.volatility, thresholds['volatility'], False)
                score += self._score_threshold(features.volume_profile, thresholds['volume_profile'], False)
                
            elif regime == MarketRegime.TRENDING:
                score += self._score_threshold(abs(features.trend_strength), thresholds['trend_strength'], True)
                score += self._score_threshold(abs(features.momentum), thresholds['momentum'], True)
            
            return min(1.0, max(0.0, score / 3))  # 標準化到0-1
            
        except Exception as e:
            logger.error(f"❌ 狀態分數計算失敗: {e}")
            return 0.0
    
    def _score_threshold(self, value: float, threshold: float, higher_is_better: bool) -> float:
        """計算閾值分數"""
        if higher_is_better:
            if value >= threshold:
                return 1.0
            else:
                return max(0.0, value / threshold)
        else:
            if value <= threshold:
                return 1.0
            else:
                return max(0.0, 1.0 - (value - threshold) / threshold)
    
    def _calculate_stability_score(self, features: MarketFeatures, regime: MarketRegime) -> float:
        """計算狀態穩定性分數"""
        try:
            # 基於特徵的一致性計算穩定性
            consistency_scores = []
            
            # 波動度一致性
            if regime in [MarketRegime.VOLATILE]:
                consistency_scores.append(features.volatility)
            elif regime in [MarketRegime.CONSOLIDATION, MarketRegime.SIDEWAYS]:
                consistency_scores.append(1.0 - features.volatility)
            else:
                consistency_scores.append(0.5)
            
            # 趨勢一致性
            if regime in [MarketRegime.BULL_TREND, MarketRegime.TRENDING]:
                consistency_scores.append(abs(features.trend_strength))
            elif regime in [MarketRegime.BEAR_TREND]:
                consistency_scores.append(abs(features.trend_strength))
            elif regime in [MarketRegime.SIDEWAYS, MarketRegime.CONSOLIDATION]:
                consistency_scores.append(1.0 - abs(features.trend_strength))
            else:
                consistency_scores.append(0.5)
            
            # 動量一致性
            if regime in [MarketRegime.BREAKOUT_UP, MarketRegime.BULL_TREND]:
                consistency_scores.append(max(0, features.momentum))
            elif regime in [MarketRegime.BREAKOUT_DOWN, MarketRegime.BEAR_TREND]:
                consistency_scores.append(max(0, -features.momentum))
            else:
                consistency_scores.append(1.0 - abs(features.momentum))
            
            return np.mean(consistency_scores)
            
        except Exception as e:
            logger.error(f"❌ 穩定性分數計算失敗: {e}")
            return 0.5
    
    def _record_regime_transition(self, from_regime: MarketRegime, to_regime: MarketRegime):
        """記錄狀態轉換"""
        transition = RegimeTransition(
            from_regime=from_regime,
            to_regime=to_regime,
            transition_time=datetime.now(),
            transition_strength=1.0,  # 簡化實現
            key_indicators=["volatility", "trend_strength", "momentum"]
        )
        
        logger.info(f"🔄 市場狀態轉換: {from_regime.value} → {to_regime.value}")
    
    async def get_regime_forecast(self) -> Dict[MarketRegime, float]:
        """獲取市場狀態預測"""
        try:
            if len(self.regime_history) < 5:
                # 如果歷史數據不足，返回均等概率
                regimes = [r for r in MarketRegime if r != MarketRegime.UNKNOWN]
                equal_prob = 1.0 / len(regimes)
                return {regime: equal_prob for regime in regimes}
            
            # 基於歷史模式預測
            recent_regimes = [r.regime for r in self.regime_history[-10:]]
            regime_counts = {}
            
            for regime in MarketRegime:
                if regime != MarketRegime.UNKNOWN:
                    count = recent_regimes.count(regime)
                    regime_counts[regime] = count
            
            total_count = sum(regime_counts.values())
            if total_count == 0:
                equal_prob = 1.0 / len(regime_counts)
                return {regime: equal_prob for regime in regime_counts.keys()}
            
            # 轉換為概率
            probabilities = {}
            for regime, count in regime_counts.items():
                probabilities[regime] = count / total_count
            
            return probabilities
            
        except Exception as e:
            logger.error(f"❌ 市場狀態預測失敗: {e}")
            regimes = [r for r in MarketRegime if r != MarketRegime.UNKNOWN]
            equal_prob = 1.0 / len(regimes)
            return {regime: equal_prob for regime in regimes}
    
    def get_detection_summary(self) -> Dict[str, Any]:
        """獲取檢測摘要"""
        try:
            avg_confidence = np.mean(self.detection_stats['confidence_scores']) if self.detection_stats['confidence_scores'] else 0.0
            avg_stability = np.mean(self.detection_stats['stability_scores']) if self.detection_stats['stability_scores'] else 0.0
            
            return {
                'total_detections': self.detection_stats['total_detections'],
                'regime_transitions': self.detection_stats['regime_transitions'],
                'average_confidence': avg_confidence,
                'average_stability': avg_stability,
                'current_regime': self.current_regime.value,
                'detection_accuracy': avg_confidence * avg_stability,
                'system_status': '運行正常' if avg_confidence > 0.5 else '需要調優'
            }
            
        except Exception as e:
            logger.error(f"❌ 檢測摘要生成失敗: {e}")
            return {"status": "摘要生成失敗", "error": str(e)}

async def main():
    """測試函數"""
    print("🧠 Advanced Market Regime Detector 測試")
    
    # 創建實例進行測試
    detector = AdvancedMarketRegimeDetector()
    
    # 創建測試數據
    dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
    test_data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 102,
        'low': np.random.randn(100).cumsum() + 98,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    # 測試檢測
    result = await detector.detect_regime_change(test_data, "TEST")
    
    print(f"檢測結果: {result.regime.value}")
    print(f"信心度: {result.confidence:.3f}")
    print(f"穩定性: {result.stability_score:.3f}")
    
    # 測試預測
    forecast = await detector.get_regime_forecast()
    print("\n預測結果:")
    for regime, prob in forecast.items():
        print(f"  {regime.value}: {prob:.3f}")
    
    print("\n✅ 測試完成")

if __name__ == "__main__":
    asyncio.run(main())
