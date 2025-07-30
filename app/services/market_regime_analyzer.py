"""
🎯 Phase 2: Market Regime Analyzer (市場機制分析器)
實現多時間框架市場機制識別和Fear & Greed Index模擬

核心功能：
1. Market Regime 識別（牛市/熊市/橫盤/混亂）
2. Fear & Greed Index 模擬計算
3. 多時間框架趨勢確認
4. 動態技術指標參數推薦
"""

import logging
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import numpy as np
import pandas as pd

from app.services.market_data import MarketDataService
from app.utils.time_utils import get_taiwan_now_naive

logger = logging.getLogger(__name__)

class MarketRegime(Enum):
    """市場機制分類"""
    BULL_TREND = "BULL_TREND"      # 牛市趨勢
    BEAR_TREND = "BEAR_TREND"      # 熊市趨勢  
    SIDEWAYS = "SIDEWAYS"          # 橫盤震蕩
    VOLATILE = "VOLATILE"          # 高波動混亂
    ACCUMULATION = "ACCUMULATION"  # 積累階段
    DISTRIBUTION = "DISTRIBUTION"  # 分發階段

class FearGreedLevel(Enum):
    """Fear & Greed 情緒等級"""
    EXTREME_FEAR = "EXTREME_FEAR"      # 極度恐懼 (0-25)
    FEAR = "FEAR"                      # 恐懼 (25-45)
    NEUTRAL = "NEUTRAL"                # 中性 (45-55)
    GREED = "GREED"                    # 貪婪 (55-75)
    EXTREME_GREED = "EXTREME_GREED"    # 極度貪婪 (75-100)

@dataclass
class TimeframeAnalysis:
    """時間框架分析結果"""
    timeframe: str
    trend_direction: str  # UP, DOWN, SIDEWAYS
    trend_strength: float  # 0.0-1.0
    momentum_score: float
    volume_profile: float
    price_action_quality: float

@dataclass
class MarketRegimeAnalysis:
    """市場機制分析結果"""
    symbol: str
    primary_regime: MarketRegime
    regime_confidence: float
    fear_greed_index: int
    fear_greed_level: FearGreedLevel
    
    # 多時間框架分析
    timeframe_analysis: Dict[str, TimeframeAnalysis]
    
    # 綜合評分
    bullish_score: float
    bearish_score: float
    sideways_score: float
    volatility_score: float
    
    # 技術指標推薦參數
    recommended_rsi_period: int
    recommended_ma_periods: Tuple[int, int]  # (fast, slow)
    recommended_bb_period: int
    recommended_macd_periods: Tuple[int, int, int]  # (fast, slow, signal)
    
    # 風險管理建議
    suggested_position_size: float  # 0.0-1.0
    suggested_max_drawdown: float
    suggested_holding_period_hours: int
    
    analysis_timestamp: datetime

class MarketRegimeAnalyzer:
    """Phase 2 市場機制分析器"""
    
    def __init__(self):
        self.market_service = MarketDataService()
        self.timeframes = ["1m", "5m", "15m", "1h"]
        
    async def analyze_market_regime(self, symbol: str) -> MarketRegimeAnalysis:
        """執行完整的市場機制分析"""
        try:
            logger.info(f"🎯 Phase 2: 開始 {symbol} 市場機制分析...")
            
            # 獲取多時間框架數據
            timeframe_data = await self._gather_multi_timeframe_data(symbol)
            
            # 分析各時間框架
            timeframe_analysis = {}
            for tf, df in timeframe_data.items():
                timeframe_analysis[tf] = self._analyze_timeframe(df, tf)
            
            # 計算 Fear & Greed Index
            fear_greed_index = await self._calculate_fear_greed_index(symbol, timeframe_data)
            fear_greed_level = self._get_fear_greed_level(fear_greed_index)
            
            # 市場機制識別
            regime_scores = self._calculate_regime_scores(timeframe_analysis, fear_greed_index)
            primary_regime = self._determine_primary_regime(regime_scores)
            regime_confidence = max(regime_scores.values())
            
            # 技術指標參數推薦
            indicator_params = self._recommend_indicator_parameters(
                primary_regime, fear_greed_level, timeframe_analysis
            )
            
            # 風險管理建議
            risk_params = self._calculate_risk_parameters(
                primary_regime, regime_confidence, fear_greed_index
            )
            
            # 構建分析結果
            analysis = MarketRegimeAnalysis(
                symbol=symbol,
                primary_regime=primary_regime,
                regime_confidence=regime_confidence,
                fear_greed_index=fear_greed_index,
                fear_greed_level=fear_greed_level,
                timeframe_analysis=timeframe_analysis,
                bullish_score=regime_scores.get(MarketRegime.BULL_TREND, 0.0),
                bearish_score=regime_scores.get(MarketRegime.BEAR_TREND, 0.0),
                sideways_score=regime_scores.get(MarketRegime.SIDEWAYS, 0.0),
                volatility_score=regime_scores.get(MarketRegime.VOLATILE, 0.0),
                recommended_rsi_period=indicator_params['rsi_period'],
                recommended_ma_periods=indicator_params['ma_periods'],
                recommended_bb_period=indicator_params['bb_period'],
                recommended_macd_periods=indicator_params['macd_periods'],
                suggested_position_size=risk_params['position_size'],
                suggested_max_drawdown=risk_params['max_drawdown'],
                suggested_holding_period_hours=risk_params['holding_period'],
                analysis_timestamp=get_taiwan_now_naive()
            )
            
            # 手動添加趨勢一致性評分
            trend_alignment_score = await self._calculate_trend_alignment(symbol)
            analysis.trend_alignment_score = trend_alignment_score
            
            logger.info(f"✅ {symbol} 市場機制分析完成: {primary_regime.value} "
                       f"(信心度: {regime_confidence:.2f}, F&G: {fear_greed_index})")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ {symbol} 市場機制分析失敗: {e}")
            raise e
    
    async def _gather_multi_timeframe_data(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """收集多時間框架數據"""
        timeframe_data = {}
        
        for timeframe in self.timeframes:
            try:
                limit = {
                    "1m": 300,   # 5 小時
                    "5m": 288,   # 24 小時
                    "15m": 192,  # 48 小時
                    "1h": 168    # 7 天
                }[timeframe]
                
                df = await self.market_service.get_historical_data(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=limit,
                    exchange='binance'
                )
                
                if df is not None and len(df) >= 50:
                    timeframe_data[timeframe] = df
                    logger.info(f"✅ {symbol} {timeframe}: {len(df)} 根K線")
                else:
                    logger.warning(f"⚠️ {symbol} {timeframe}: 數據不足")
                    
            except Exception as e:
                logger.error(f"❌ 獲取 {symbol} {timeframe} 數據失敗: {e}")
        
        return timeframe_data
    
    def _analyze_timeframe(self, df: pd.DataFrame, timeframe: str) -> TimeframeAnalysis:
        """分析單一時間框架"""
        try:
            # 計算趨勢方向和強度
            ma_short = df['close'].rolling(10).mean()
            ma_long = df['close'].rolling(30).mean()
            
            current_price = df['close'].iloc[-1]
            ma_short_current = ma_short.iloc[-1]
            ma_long_current = ma_long.iloc[-1]
            
            # 趨勢方向
            if ma_short_current > ma_long_current and current_price > ma_short_current:
                trend_direction = "UP"
                trend_strength = min(1.0, (ma_short_current - ma_long_current) / ma_long_current * 10)
            elif ma_short_current < ma_long_current and current_price < ma_short_current:
                trend_direction = "DOWN"
                trend_strength = min(1.0, (ma_long_current - ma_short_current) / ma_long_current * 10)
            else:
                trend_direction = "SIDEWAYS"
                trend_strength = 0.3
            
            # 動量評分
            momentum = (current_price - df['close'].iloc[-20]) / df['close'].iloc[-20]
            momentum_score = min(1.0, abs(momentum) * 5)
            
            # 成交量分析
            volume_ma = df['volume'].rolling(20).mean()
            current_volume = df['volume'].iloc[-10:].mean()
            volume_profile = min(2.0, current_volume / volume_ma.iloc[-1])
            
            # 價格行為質量
            volatility = df['close'].pct_change().std()
            price_action_quality = 1.0 - min(1.0, volatility * 50)
            
            return TimeframeAnalysis(
                timeframe=timeframe,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                momentum_score=momentum_score,
                volume_profile=volume_profile,
                price_action_quality=price_action_quality
            )
            
        except Exception as e:
            logger.error(f"時間框架 {timeframe} 分析失敗: {e}")
            return TimeframeAnalysis(
                timeframe=timeframe,
                trend_direction="SIDEWAYS",
                trend_strength=0.0,
                momentum_score=0.0,
                volume_profile=1.0,
                price_action_quality=0.5
            )
    
    async def _calculate_fear_greed_index(self, symbol: str, timeframe_data: Dict[str, pd.DataFrame]) -> int:
        """Phase 2: 計算 Fear & Greed Index 模擬值"""
        try:
            fear_greed_score = 50  # 中性起點
            
            # 使用5分鐘數據作為主要分析
            if "5m" not in timeframe_data:
                return fear_greed_score
                
            df = timeframe_data["5m"]
            
            # 1. 價格變動幅度 (25% 權重)
            price_change_7d = (df['close'].iloc[-1] - df['close'].iloc[-144]) / df['close'].iloc[-144]
            price_momentum = min(25, max(-25, price_change_7d * 500))
            fear_greed_score += price_momentum
            
            # 2. 成交量分析 (25% 權重)
            volume_ratio = df['volume'].iloc[-20:].mean() / df['volume'].iloc[-100:-20].mean()
            volume_score = min(25, max(-25, (volume_ratio - 1.0) * 50))
            fear_greed_score += volume_score
            
            # 3. 波動率分析 (20% 權重)
            volatility = df['close'].pct_change().iloc[-50:].std()
            volatility_score = min(20, max(-20, (0.02 - volatility) * 500))
            fear_greed_score += volatility_score
            
            # 4. 技術指標綜合 (20% 權重)
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            rsi_score = 0
            if current_rsi > 70:
                rsi_score = -10  # 超買，恐懼
            elif current_rsi < 30:
                rsi_score = 10   # 超賣，貪婪
            
            # MACD
            exp1 = df['close'].ewm(span=12).mean()
            exp2 = df['close'].ewm(span=26).mean()
            macd = exp1 - exp2
            macd_signal = macd.ewm(span=9).mean()
            macd_histogram = macd - macd_signal
            
            macd_score = 0
            if macd_histogram.iloc[-1] > macd_histogram.iloc[-5:].mean():
                macd_score = 5  # 正面動量
            else:
                macd_score = -5  # 負面動量
            
            technical_score = rsi_score + macd_score
            fear_greed_score += technical_score
            
            # 5. 市場支撐/阻力 (10% 權重)
            high_20 = df['high'].rolling(20).max()
            low_20 = df['low'].rolling(20).min()
            current_price = df['close'].iloc[-1]
            
            position_in_range = (current_price - low_20.iloc[-1]) / (high_20.iloc[-1] - low_20.iloc[-1])
            support_resistance_score = min(10, max(-10, (position_in_range - 0.5) * 20))
            fear_greed_score += support_resistance_score
            
            # 確保範圍在 0-100
            fear_greed_score = max(0, min(100, int(fear_greed_score)))
            
            logger.info(f"📊 {symbol} Fear & Greed Index: {fear_greed_score} "
                       f"(價格:{price_momentum:.1f}, 成交量:{volume_score:.1f}, "
                       f"波動:{volatility_score:.1f}, 技術:{technical_score:.1f})")
            
            return fear_greed_score
            
        except Exception as e:
            logger.error(f"計算 Fear & Greed Index 失敗: {e}")
            return 50  # 默認中性值
    
    def _get_fear_greed_level(self, index: int) -> FearGreedLevel:
        """根據數值確定Fear & Greed等級"""
        if index <= 25:
            return FearGreedLevel.EXTREME_FEAR
        elif index <= 45:
            return FearGreedLevel.FEAR
        elif index <= 55:
            return FearGreedLevel.NEUTRAL
        elif index <= 75:
            return FearGreedLevel.GREED
        else:
            return FearGreedLevel.EXTREME_GREED
    
    def _calculate_regime_scores(self, timeframe_analysis: Dict[str, TimeframeAnalysis], 
                                fear_greed_index: int) -> Dict[MarketRegime, float]:
        """計算各市場機制評分"""
        scores = {regime: 0.0 for regime in MarketRegime}
        
        # 時間框架權重
        tf_weights = {"1m": 0.1, "5m": 0.4, "15m": 0.3, "1h": 0.2}
        
        for tf, analysis in timeframe_analysis.items():
            weight = tf_weights.get(tf, 0.0)
            
            # 牛市評分
            if analysis.trend_direction == "UP":
                bull_score = analysis.trend_strength * analysis.momentum_score * weight
                scores[MarketRegime.BULL_TREND] += bull_score
                
                # Fear & Greed 調整
                if fear_greed_index > 55:
                    scores[MarketRegime.BULL_TREND] += 0.1 * weight
            
            # 熊市評分  
            elif analysis.trend_direction == "DOWN":
                bear_score = analysis.trend_strength * analysis.momentum_score * weight
                scores[MarketRegime.BEAR_TREND] += bear_score
                
                if fear_greed_index < 45:
                    scores[MarketRegime.BEAR_TREND] += 0.1 * weight
            
            # 橫盤評分
            else:
                sideways_score = analysis.price_action_quality * weight
                scores[MarketRegime.SIDEWAYS] += sideways_score
            
            # 波動率評分
            if analysis.momentum_score > 0.7 and analysis.price_action_quality < 0.4:
                scores[MarketRegime.VOLATILE] += 0.2 * weight
        
        # Fear & Greed 特殊調整
        if fear_greed_index <= 25:  # 極度恐懼
            scores[MarketRegime.ACCUMULATION] += 0.3
        elif fear_greed_index >= 75:  # 極度貪婪
            scores[MarketRegime.DISTRIBUTION] += 0.3
        
        return scores
    
    def _determine_primary_regime(self, regime_scores: Dict[MarketRegime, float]) -> MarketRegime:
        """確定主要市場機制"""
        return max(regime_scores.keys(), key=lambda k: regime_scores[k])
    
    def _recommend_indicator_parameters(self, primary_regime: MarketRegime, 
                                      fear_greed_level: FearGreedLevel,
                                      timeframe_analysis: Dict[str, TimeframeAnalysis]) -> Dict:
        """Phase 2: 根據市場機制推薦技術指標參數"""
        
        # 基礎參數
        base_params = {
            'rsi_period': 14,
            'ma_periods': (10, 30),
            'bb_period': 20,
            'macd_periods': (12, 26, 9)
        }
        
        # 根據市場機制調整
        if primary_regime == MarketRegime.BULL_TREND:
            # 牛市：更敏感的參數
            base_params['rsi_period'] = 10
            base_params['ma_periods'] = (8, 21)
            base_params['bb_period'] = 15
            base_params['macd_periods'] = (10, 21, 7)
            
        elif primary_regime == MarketRegime.BEAR_TREND:
            # 熊市：更保守的參數
            base_params['rsi_period'] = 18
            base_params['ma_periods'] = (12, 40)
            base_params['bb_period'] = 25
            base_params['macd_periods'] = (15, 30, 12)
            
        elif primary_regime == MarketRegime.VOLATILE:
            # 高波動：更長週期
            base_params['rsi_period'] = 21
            base_params['ma_periods'] = (15, 50)
            base_params['bb_period'] = 30
            base_params['macd_periods'] = (18, 35, 15)
            
        # Fear & Greed 微調
        if fear_greed_level in [FearGreedLevel.EXTREME_FEAR, FearGreedLevel.EXTREME_GREED]:
            # 極端情緒：參數稍微延長
            base_params['rsi_period'] += 2
            base_params['bb_period'] += 3
        
        return base_params
    
    def _calculate_risk_parameters(self, primary_regime: MarketRegime, 
                                 regime_confidence: float, fear_greed_index: int) -> Dict:
        """計算風險管理參數"""
        
        # 基礎風險參數
        base_position_size = 0.1  # 10%
        base_max_drawdown = 0.02  # 2%
        base_holding_period = 4   # 4小時
        
        # 根據市場機制調整
        if primary_regime == MarketRegime.BULL_TREND:
            position_multiplier = 1.5
            drawdown_multiplier = 1.2
            holding_multiplier = 1.5
            
        elif primary_regime == MarketRegime.BEAR_TREND:
            position_multiplier = 0.8
            drawdown_multiplier = 0.8
            holding_multiplier = 0.7
            
        elif primary_regime == MarketRegime.VOLATILE:
            position_multiplier = 0.6
            drawdown_multiplier = 0.6
            holding_multiplier = 0.5
            
        else:  # SIDEWAYS, ACCUMULATION, DISTRIBUTION
            position_multiplier = 1.0
            drawdown_multiplier = 1.0
            holding_multiplier = 1.0
        
        # 信心度調整
        confidence_multiplier = min(1.5, max(0.5, regime_confidence * 2))
        
        # Fear & Greed 調整
        if fear_greed_index <= 25 or fear_greed_index >= 75:
            # 極端情緒：減少倉位
            position_multiplier *= 0.8
        
        return {
            'position_size': min(0.3, base_position_size * position_multiplier * confidence_multiplier),
            'max_drawdown': base_max_drawdown * drawdown_multiplier,
            'holding_period': int(base_holding_period * holding_multiplier)
        }

# 全局實例
market_regime_analyzer = MarketRegimeAnalyzer()
