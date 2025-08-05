#!/usr/bin/env python3
"""
🎯 真實策略分析引擎
基於技術指標集合分析，生成策略級別的交易信號，拒絕使用任何模擬數據
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class StrategySignalType(Enum):
    """策略信號類型"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"

class StrategyConfidenceLevel(Enum):
    """策略信心水準"""
    VERY_HIGH = "VERY_HIGH"   # 90%+
    HIGH = "HIGH"             # 80-90%
    MEDIUM = "MEDIUM"         # 60-80%
    LOW = "LOW"               # 40-60%
    VERY_LOW = "VERY_LOW"     # <40%

@dataclass
class IndicatorResult:
    """技術指標結果"""
    name: str
    signal: str  # BUY, SELL, HOLD
    confidence: float  # 0.0 - 1.0
    value: float
    threshold: float
    direction: str  # UP, DOWN, NEUTRAL

@dataclass
class StrategyAnalysisResult:
    """策略分析結果"""
    symbol: str
    signal_type: StrategySignalType
    confidence: float
    confluence_count: int
    supporting_indicators: List[IndicatorResult]
    opposing_indicators: List[IndicatorResult]
    market_regime: str  # BULL, BEAR, SIDEWAYS
    volatility_assessment: str  # HIGH, MEDIUM, LOW
    reasoning: str
    risk_assessment: str
    timeframe: str
    timestamp: datetime

class RealStrategyAnalysisEngine:
    """真實策略分析引擎"""
    
    def __init__(self, 
                 min_confluence_count: int = 3,
                 min_confidence_threshold: float = 0.65):
        self.min_confluence_count = min_confluence_count
        self.min_confidence_threshold = min_confidence_threshold
        self.analysis_count = 0
        self.successful_analyses = 0
        
        # 📊 技術指標權重配置
        self.indicator_weights = {
            'RSI': 0.15,
            'MACD': 0.18,
            'EMA_crossover': 0.16,
            'Bollinger_Bands': 0.12,
            'Stochastic': 0.10,
            'Williams_R': 0.08,
            'Momentum': 0.08,
            'Volume': 0.13
        }
    
    def _analyze_rsi(self, df: pd.DataFrame) -> IndicatorResult:
        """分析 RSI 指標"""
        try:
            if 'RSI_14' not in df.columns or df['RSI_14'].empty:
                raise ValueError("RSI 數據不可用")
            
            rsi_value = df['RSI_14'].iloc[-1]
            
            if pd.isna(rsi_value):
                raise ValueError("RSI 值為 NaN")
            
            # 🎯 RSI 信號邏輯
            if rsi_value <= 30:
                signal = "BUY"
                confidence = min(0.9, (30 - rsi_value) / 10)
                direction = "UP"
            elif rsi_value >= 70:
                signal = "SELL"
                confidence = min(0.9, (rsi_value - 70) / 10)
                direction = "DOWN"
            elif rsi_value <= 40:
                signal = "BUY"
                confidence = 0.6
                direction = "UP"
            elif rsi_value >= 60:
                signal = "SELL"
                confidence = 0.6
                direction = "DOWN"
            else:
                signal = "HOLD"
                confidence = 0.4
                direction = "NEUTRAL"
            
            return IndicatorResult(
                name="RSI",
                signal=signal,
                confidence=confidence,
                value=rsi_value,
                threshold=50.0,
                direction=direction
            )
            
        except Exception as e:
            logger.error(f"❌ RSI 分析失敗: {e}")
            raise ValueError(f"RSI 指標分析失敗: {e}")
    
    def _analyze_macd(self, df: pd.DataFrame) -> IndicatorResult:
        """分析 MACD 指標"""
        try:
            if 'MACD_12_26_9' not in df.columns or 'MACDs_12_26_9' not in df.columns:
                raise ValueError("MACD 數據不可用")
            
            macd = df['MACD_12_26_9'].iloc[-1]
            signal_line = df['MACDs_12_26_9'].iloc[-1]
            
            if pd.isna(macd) or pd.isna(signal_line):
                raise ValueError("MACD 值為 NaN")
            
            # 🎯 MACD 信號邏輯
            macd_diff = macd - signal_line
            
            if macd > signal_line and macd > 0:
                signal = "BUY"
                confidence = min(0.9, abs(macd_diff) * 100)
                direction = "UP"
            elif macd < signal_line and macd < 0:
                signal = "SELL"
                confidence = min(0.9, abs(macd_diff) * 100)
                direction = "DOWN"
            elif macd > signal_line:
                signal = "BUY"
                confidence = 0.6
                direction = "UP"
            elif macd < signal_line:
                signal = "SELL"
                confidence = 0.6
                direction = "DOWN"
            else:
                signal = "HOLD"
                confidence = 0.4
                direction = "NEUTRAL"
            
            return IndicatorResult(
                name="MACD",
                signal=signal,
                confidence=confidence,
                value=macd,
                threshold=signal_line,
                direction=direction
            )
            
        except Exception as e:
            logger.error(f"❌ MACD 分析失敗: {e}")
            raise ValueError(f"MACD 指標分析失敗: {e}")
    
    def _analyze_ema_crossover(self, df: pd.DataFrame) -> IndicatorResult:
        """分析 EMA 交叉"""
        try:
            if 'EMA_12' not in df.columns or 'EMA_26' not in df.columns:
                raise ValueError("EMA 數據不可用")
            
            ema_fast = df['EMA_12'].iloc[-1]
            ema_slow = df['EMA_26'].iloc[-1]
            current_price = df['close'].iloc[-1]
            
            if pd.isna(ema_fast) or pd.isna(ema_slow) or pd.isna(current_price):
                raise ValueError("EMA 值為 NaN")
            
            # 🎯 EMA 交叉信號邏輯
            ema_diff_pct = ((ema_fast - ema_slow) / ema_slow) * 100
            
            if ema_fast > ema_slow and current_price > ema_fast:
                signal = "BUY"
                confidence = min(0.9, abs(ema_diff_pct) * 10)
                direction = "UP"
            elif ema_fast < ema_slow and current_price < ema_fast:
                signal = "SELL"
                confidence = min(0.9, abs(ema_diff_pct) * 10)
                direction = "DOWN"
            elif current_price > ema_fast:
                signal = "BUY"
                confidence = 0.5
                direction = "UP"
            elif current_price < ema_fast:
                signal = "SELL"
                confidence = 0.5
                direction = "DOWN"
            else:
                signal = "HOLD"
                confidence = 0.4
                direction = "NEUTRAL"
            
            return IndicatorResult(
                name="EMA_Crossover",
                signal=signal,
                confidence=confidence,
                value=ema_fast,
                threshold=ema_slow,
                direction=direction
            )
            
        except Exception as e:
            logger.error(f"❌ EMA 交叉分析失敗: {e}")
            raise ValueError(f"EMA 指標分析失敗: {e}")
    
    def _analyze_bollinger_bands(self, df: pd.DataFrame) -> IndicatorResult:
        """分析布林帶"""
        try:
            if 'BBU_20_2.0' not in df.columns or 'BBL_20_2.0' not in df.columns:
                raise ValueError("布林帶數據不可用")
            
            upper_band = df['BBU_20_2.0'].iloc[-1]
            lower_band = df['BBL_20_2.0'].iloc[-1]
            current_price = df['close'].iloc[-1]
            
            if pd.isna(upper_band) or pd.isna(lower_band) or pd.isna(current_price):
                raise ValueError("布林帶值為 NaN")
            
            # 🎯 布林帶信號邏輯
            band_width = upper_band - lower_band
            price_position = (current_price - lower_band) / band_width
            
            if price_position <= 0.1:  # 接近下軌
                signal = "BUY"
                confidence = min(0.9, (0.1 - price_position) * 10)
                direction = "UP"
            elif price_position >= 0.9:  # 接近上軌
                signal = "SELL"
                confidence = min(0.9, (price_position - 0.9) * 10)
                direction = "DOWN"
            elif price_position <= 0.3:
                signal = "BUY"
                confidence = 0.6
                direction = "UP"
            elif price_position >= 0.7:
                signal = "SELL"
                confidence = 0.6
                direction = "DOWN"
            else:
                signal = "HOLD"
                confidence = 0.4
                direction = "NEUTRAL"
            
            return IndicatorResult(
                name="Bollinger_Bands",
                signal=signal,
                confidence=confidence,
                value=current_price,
                threshold=(upper_band + lower_band) / 2,
                direction=direction
            )
            
        except Exception as e:
            logger.error(f"❌ 布林帶分析失敗: {e}")
            raise ValueError(f"布林帶指標分析失敗: {e}")
    
    def _determine_market_regime(self, df: pd.DataFrame) -> str:
        """判斷市場趨勢"""
        try:
            if len(df) < 50:
                raise ValueError("數據不足以判斷市場趨勢")
            
            # 使用 20 日和 50 日 EMA 判斷趨勢
            short_ema = df['close'].ewm(span=20).mean().iloc[-1]
            long_ema = df['close'].ewm(span=50).mean().iloc[-1]
            current_price = df['close'].iloc[-1]
            
            if pd.isna(short_ema) or pd.isna(long_ema):
                raise ValueError("趨勢判斷數據不可用")
            
            if current_price > short_ema > long_ema:
                return "BULL"
            elif current_price < short_ema < long_ema:
                return "BEAR"
            else:
                return "SIDEWAYS"
                
        except Exception as e:
            logger.warning(f"⚠️ 市場趨勢判斷失敗: {e}")
            return "UNKNOWN"
    
    def _assess_volatility(self, df: pd.DataFrame) -> str:
        """評估市場波動性"""
        try:
            if len(df) < 20:
                raise ValueError("數據不足以評估波動性")
            
            # 計算 20 日波動率
            returns = df['close'].pct_change().dropna()
            volatility = returns.rolling(window=20).std().iloc[-1] * np.sqrt(252)
            
            if pd.isna(volatility):
                raise ValueError("波動率計算失敗")
            
            if volatility > 0.4:
                return "HIGH"
            elif volatility > 0.2:
                return "MEDIUM"
            else:
                return "LOW"
                
        except Exception as e:
            logger.warning(f"⚠️ 波動性評估失敗: {e}")
            return "UNKNOWN"
    
    async def analyze_strategy_signal(
        self, 
        df: pd.DataFrame, 
        symbol: str,
        timeframe: str = "1h"
    ) -> StrategyAnalysisResult:
        """
        執行完整的策略分析
        
        Args:
            df: 包含技術指標的DataFrame
            symbol: 交易對符號
            timeframe: 時間框架
            
        Returns:
            StrategyAnalysisResult: 策略分析結果
        """
        self.analysis_count += 1
        
        try:
            # 🚫 絕對禁止空數據或模擬數據
            if df.empty or len(df) < 50:
                raise ValueError(f"數據不足: {len(df)} 行，需要至少 50 行歷史數據")
            
            # 🔍 執行所有技術指標分析
            indicator_results = []
            
            try:
                rsi_result = self._analyze_rsi(df)
                indicator_results.append(rsi_result)
            except Exception as e:
                logger.warning(f"⚠️ RSI 分析跳過: {e}")
            
            try:
                macd_result = self._analyze_macd(df)
                indicator_results.append(macd_result)
            except Exception as e:
                logger.warning(f"⚠️ MACD 分析跳過: {e}")
            
            try:
                ema_result = self._analyze_ema_crossover(df)
                indicator_results.append(ema_result)
            except Exception as e:
                logger.warning(f"⚠️ EMA 分析跳過: {e}")
            
            try:
                bb_result = self._analyze_bollinger_bands(df)
                indicator_results.append(bb_result)
            except Exception as e:
                logger.warning(f"⚠️ 布林帶分析跳過: {e}")
            
            # 🚫 確保有足夠的有效指標
            if len(indicator_results) < 2:
                raise ValueError(f"可用技術指標不足: {len(indicator_results)}")
            
            # 🎯 計算信號匯合
            buy_signals = [r for r in indicator_results if r.signal == "BUY"]
            sell_signals = [r for r in indicator_results if r.signal == "SELL"]
            hold_signals = [r for r in indicator_results if r.signal == "HOLD"]
            
            # 📊 加權信心度計算
            total_weight = sum(self.indicator_weights.get(r.name, 0.1) for r in indicator_results)
            weighted_confidence = sum(
                r.confidence * self.indicator_weights.get(r.name, 0.1) 
                for r in indicator_results
            ) / total_weight if total_weight > 0 else 0
            
            # 🎯 決定最終策略信號
            buy_count = len(buy_signals)
            sell_count = len(sell_signals)
            confluence_count = max(buy_count, sell_count)
            
            if buy_count >= self.min_confluence_count and buy_count > sell_count:
                if weighted_confidence >= 0.8:
                    signal_type = StrategySignalType.STRONG_BUY
                else:
                    signal_type = StrategySignalType.BUY
                supporting_indicators = buy_signals
                opposing_indicators = sell_signals
            elif sell_count >= self.min_confluence_count and sell_count > buy_count:
                if weighted_confidence >= 0.8:
                    signal_type = StrategySignalType.STRONG_SELL
                else:
                    signal_type = StrategySignalType.SELL
                supporting_indicators = sell_signals
                opposing_indicators = buy_signals
            else:
                signal_type = StrategySignalType.HOLD
                supporting_indicators = hold_signals
                opposing_indicators = buy_signals + sell_signals
            
            # 🌐 市場環境分析
            market_regime = self._determine_market_regime(df)
            volatility_assessment = self._assess_volatility(df)
            
            # 📝 生成分析理由
            reasoning = (
                f"策略分析基於 {len(indicator_results)} 個技術指標: "
                f"做多信號 {buy_count} 個, 做空信號 {sell_count} 個, "
                f"匯合度 {confluence_count}, 加權信心度 {weighted_confidence:.3f}, "
                f"市場趨勢: {market_regime}, 波動性: {volatility_assessment}"
            )
            
            # 🛡️ 風險評估
            if confluence_count >= 4 and weighted_confidence >= 0.8:
                risk_assessment = "LOW"
            elif confluence_count >= 3 and weighted_confidence >= 0.6:
                risk_assessment = "MEDIUM"
            else:
                risk_assessment = "HIGH"
            
            # ✅ 信心度門檻檢查
            if weighted_confidence < self.min_confidence_threshold:
                signal_type = StrategySignalType.HOLD
                reasoning += f" (信心度不足: {weighted_confidence:.3f} < {self.min_confidence_threshold})"
                risk_assessment = "HIGH"
            
            self.successful_analyses += 1
            
            result = StrategyAnalysisResult(
                symbol=symbol,
                signal_type=signal_type,
                confidence=weighted_confidence,
                confluence_count=confluence_count,
                supporting_indicators=supporting_indicators,
                opposing_indicators=opposing_indicators,
                market_regime=market_regime,
                volatility_assessment=volatility_assessment,
                reasoning=reasoning,
                risk_assessment=risk_assessment,
                timeframe=timeframe,
                timestamp=datetime.now()
            )
            
            logger.info(f"✅ 策略分析完成: {symbol} -> {signal_type.value}, 信心度: {weighted_confidence:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 策略分析失敗 ({symbol}): {e}")
            raise ValueError(f"策略分析引擎故障: {e}")
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """獲取分析統計"""
        success_rate = (self.successful_analyses / self.analysis_count * 100) if self.analysis_count > 0 else 0
        
        return {
            'total_analyses': self.analysis_count,
            'successful_analyses': self.successful_analyses,
            'failed_analyses': self.analysis_count - self.successful_analyses,
            'success_rate': round(success_rate, 2),
            'min_confluence_count': self.min_confluence_count,
            'min_confidence_threshold': self.min_confidence_threshold
        }

# 全局策略分析引擎實例
strategy_engine = RealStrategyAnalysisEngine(
    min_confluence_count=3,
    min_confidence_threshold=0.65
)

async def analyze_trading_strategy(df: pd.DataFrame, symbol: str, timeframe: str = "1h") -> StrategyAnalysisResult:
    """全局策略分析函數"""
    return await strategy_engine.analyze_strategy_signal(df, symbol, timeframe)

if __name__ == "__main__":
    print("🎯 真實策略分析引擎已載入")
    print(f"📊 配置: 最小匯合數={strategy_engine.min_confluence_count}, 最小信心度={strategy_engine.min_confidence_threshold}")
