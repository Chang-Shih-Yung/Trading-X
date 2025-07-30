#!/usr/bin/env python3
"""
基於 pandas-ta 的進階技術指標服務
取代手動計算，提供標準化、自適應的技術分析
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class MarketRegime(Enum):
    """市場狀態"""
    BULL_STRONG = "bull_strong"      # 強勢多頭
    BULL_WEAK = "bull_weak"          # 弱勢多頭
    BEAR_STRONG = "bear_strong"      # 強勢空頭  
    BEAR_WEAK = "bear_weak"          # 弱勢空頭
    SIDEWAYS = "sideways"            # 盤整
    VOLATILE = "volatile"            # 高波動

class SignalStrength(Enum):
    """信號強度"""
    VERY_STRONG = "very_strong"      # 90-100%
    STRONG = "strong"                # 75-89%
    MODERATE = "moderate"            # 60-74%
    WEAK = "weak"                    # 40-59%
    VERY_WEAK = "very_weak"          # 0-39%

@dataclass
class TechnicalSignal:
    """技術信號結果"""
    indicator_name: str
    signal_type: str  # 'BUY', 'SELL', 'NEUTRAL'
    strength: float   # 0-1
    confidence: float # 0-1
    value: float
    description: str
    timeframe: str
    timestamp: str

@dataclass
class MarketCondition:
    """市場狀況"""
    regime: MarketRegime
    trend_strength: float    # 0-1, ADX 基礎
    volatility: float       # 0-1, ATR 基礎
    momentum: float         # 0-1, ROC 基礎
    confidence: float       # 綜合信心度
    key_levels: Dict[str, float]  # 支撐阻力位

class PandasTAIndicators:
    """基於 pandas-ta 的進階技術指標分析引擎"""
    
    def __init__(self):
        self.required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        # 策略模板定義
        self.strategy_templates = {
            'scalping': self._create_scalping_strategy(),
            'swing': self._create_swing_strategy(),
            'trend': self._create_trend_strategy(),
            'momentum': self._create_momentum_strategy()
        }
        
        # 自適應參數範圍
        self.adaptive_params = {
            'rsi_length': (7, 21),      # RSI 週期範圍
            'ema_fast': (8, 21),        # 快速均線範圍
            'ema_slow': (21, 55),       # 慢速均線範圍
            'macd_fast': (8, 15),       # MACD 快線範圍
            'macd_slow': (21, 35),      # MACD 慢線範圍
            'bb_length': (10, 25),      # 布林帶週期範圍
            'atr_length': (10, 20)      # ATR 週期範圍
        }

    def _create_scalping_strategy(self) -> ta.Strategy:
        """創建短線剝頭皮策略"""
        return ta.Strategy(
            name="短線剝頭皮",
            ta=[
                {"kind": "rsi", "length": 7},           # 快速 RSI
                {"kind": "ema", "length": [8, 13, 21]}, # 多週期快速均線
                {"kind": "macd", "fast": 8, "slow": 21}, # 快速 MACD
                {"kind": "bbands", "length": 10},        # 緊縮布林帶
                {"kind": "stoch", "k": 5, "d": 3},      # 快速 KD
                {"kind": "atr", "length": 10},          # 波動性
                {"kind": "adx", "length": 14},          # 趨勢強度
            ]
        )

    def _create_swing_strategy(self) -> ta.Strategy:
        """創建波段交易策略"""
        return ta.Strategy(
            name="波段交易",
            ta=[
                {"kind": "rsi", "length": 14},           # 標準 RSI
                {"kind": "ema", "length": [20, 50]},     # 標準均線組合
                {"kind": "macd", "fast": 12, "slow": 26}, # 標準 MACD
                {"kind": "bbands", "length": 20},        # 標準布林帶
                {"kind": "stoch", "k": 14, "d": 3},     # 標準 KD
                {"kind": "atr", "length": 14},          # 波動性
                {"kind": "adx", "length": 14},          # 趨勢強度
                {"kind": "aroon", "length": 14},        # 趨勢方向
            ]
        )

    def _create_trend_strategy(self) -> ta.Strategy:
        """創建趨勢跟隨策略"""
        return ta.Strategy(
            name="趨勢跟隨",
            ta=[
                {"kind": "ema", "length": [20, 50, 200]}, # 長週期均線
                {"kind": "macd", "fast": 12, "slow": 26}, # 標準 MACD
                {"kind": "adx", "length": 14},            # 趨勢強度
                {"kind": "aroon", "length": 25},          # 趨勢方向
                {"kind": "psar"},                         # 拋物線 SAR
                {"kind": "supertrend", "length": 10, "multiplier": 3}, # 超級趨勢
                {"kind": "atr", "length": 14},            # 波動性
            ]
        )

    def _create_momentum_strategy(self) -> ta.Strategy:
        """創建動量策略"""
        return ta.Strategy(
            name="動量策略",
            ta=[
                {"kind": "rsi", "length": 14},           # RSI
                {"kind": "stoch", "k": 14, "d": 3},     # KD 指標
                {"kind": "willr", "length": 14},        # Williams %R
                {"kind": "cci", "length": 20},          # 商品通道指數
                {"kind": "roc", "length": 10},          # 變化率
                {"kind": "cmo", "length": 14},          # 錢德動量
                {"kind": "atr", "length": 14},          # 波動性
            ]
        )

    def validate_data(self, df: pd.DataFrame) -> bool:
        """驗證數據格式"""
        if df is None or df.empty:
            return False
        return all(col in df.columns for col in self.required_columns)

    def detect_market_regime(self, df: pd.DataFrame) -> MarketCondition:
        """自動檢測市場狀態"""
        if not self.validate_data(df):
            raise ValueError("數據格式不正確")

        # 計算關鍵指標
        df.ta.adx(length=14, append=True)     # 趨勢強度
        df.ta.aroon(length=14, append=True)   # 趨勢方向
        df.ta.cci(length=20, append=True)     # 商品通道指數
        df.ta.atr(length=14, append=True)     # 波動性
        df.ta.roc(length=10, append=True)     # 變化率

        # 獲取最新值
        adx = df['ADX_14'].iloc[-1] if 'ADX_14' in df.columns else 20
        aroon_up = df['AROONU_14'].iloc[-1] if 'AROONU_14' in df.columns else 50
        aroon_down = df['AROOND_14'].iloc[-1] if 'AROOND_14' in df.columns else 50
        cci = df['CCI_20_0.015'].iloc[-1] if 'CCI_20_0.015' in df.columns else 0
        atr = df['ATR_14'].iloc[-1] if 'ATR_14' in df.columns else 0
        roc = df['ROC_10'].iloc[-1] if 'ROC_10' in df.columns else 0

        # 計算趨勢強度 (0-1)
        trend_strength = min(adx / 50, 1.0) if adx > 0 else 0

        # 計算波動性 (0-1)
        price = df['close'].iloc[-1]
        volatility = min((atr / price) * 100, 1.0) if atr > 0 and price > 0 else 0

        # 計算動量 (0-1)
        momentum = min(abs(roc) / 10, 1.0) if not pd.isna(roc) else 0

        # 判斷市場狀態
        if adx > 25:  # 強趨勢
            if aroon_up > 70 and cci > 100:
                regime = MarketRegime.BULL_STRONG
            elif aroon_up > 50 and cci > 0:
                regime = MarketRegime.BULL_WEAK
            elif aroon_down > 70 and cci < -100:
                regime = MarketRegime.BEAR_STRONG
            elif aroon_down > 50 and cci < 0:
                regime = MarketRegime.BEAR_WEAK
            else:
                regime = MarketRegime.SIDEWAYS
        else:  # 弱趨勢或盤整
            if volatility > 0.5:
                regime = MarketRegime.VOLATILE
            else:
                regime = MarketRegime.SIDEWAYS

        # 計算綜合信心度
        confidence = (trend_strength + (1 - volatility) + momentum) / 3

        # 計算關鍵支撐阻力位
        high_20 = df['high'].rolling(20).max().iloc[-1]
        low_20 = df['low'].rolling(20).min().iloc[-1]
        key_levels = {
            'resistance': high_20,
            'support': low_20,
            'current': price
        }

        return MarketCondition(
            regime=regime,
            trend_strength=trend_strength,
            volatility=volatility,
            momentum=momentum,
            confidence=confidence,
            key_levels=key_levels
        )

    def calculate_adaptive_indicators(self, df: pd.DataFrame, strategy_type: str = 'scalping') -> Dict[str, TechnicalSignal]:
        """自適應技術指標計算"""
        if not self.validate_data(df):
            raise ValueError("數據格式不正確")

        # 檢測市場狀態
        market_condition = self.detect_market_regime(df)
        
        # 根據市場狀態調整參數
        adapted_params = self._adapt_parameters(market_condition, strategy_type)
        
        # 應用策略
        strategy = self._create_adaptive_strategy(adapted_params, strategy_type)
        df.ta.strategy(strategy)
        
        # 分析信號
        signals = {}
        
        # RSI 信號分析
        if f'RSI_{adapted_params["rsi_length"]}' in df.columns:
            rsi_signal = self._analyze_rsi_signal(df, adapted_params["rsi_length"], market_condition)
            signals['rsi'] = rsi_signal

        # MACD 信號分析
        macd_cols = [col for col in df.columns if 'MACD' in col]
        if macd_cols:
            macd_signal = self._analyze_macd_signal(df, adapted_params, market_condition)
            signals['macd'] = macd_signal

        # EMA 信號分析
        ema_fast_col = f'EMA_{adapted_params["ema_fast"]}'
        ema_slow_col = f'EMA_{adapted_params["ema_slow"]}'
        if ema_fast_col in df.columns and ema_slow_col in df.columns:
            ema_signal = self._analyze_ema_signal(df, adapted_params, market_condition)
            signals['ema'] = ema_signal

        # 布林帶信號分析
        bb_cols = [col for col in df.columns if 'BB' in col]
        if bb_cols:
            bb_signal = self._analyze_bollinger_signal(df, adapted_params, market_condition)
            signals['bollinger'] = bb_signal

        return signals

    def _adapt_parameters(self, market_condition: MarketCondition, strategy_type: str) -> Dict[str, int]:
        """根據市場狀態自適應調整參數"""
        base_params = {
            'rsi_length': 14,
            'ema_fast': 12,
            'ema_slow': 26,
            'macd_fast': 12,
            'macd_slow': 26,
            'bb_length': 20,
            'atr_length': 14
        }

        # 根據波動性調整
        volatility = getattr(market_condition, 'volatility', 0.3)
        trend_strength = getattr(market_condition, 'trend_strength', 0.5)
        
        if volatility > 0.7:  # 高波動
            base_params['rsi_length'] = max(7, base_params['rsi_length'] - 3)
            base_params['ema_fast'] = max(8, base_params['ema_fast'] - 3)
            base_params['bb_length'] = max(10, base_params['bb_length'] - 5)
        elif volatility < 0.3:  # 低波動
            base_params['rsi_length'] = min(21, base_params['rsi_length'] + 3)
            base_params['ema_fast'] = min(21, base_params['ema_fast'] + 3)
            base_params['bb_length'] = min(25, base_params['bb_length'] + 5)

        # 根據趨勢強度調整
        if trend_strength > 0.8:  # 強趨勢
            base_params['macd_fast'] = max(8, base_params['macd_fast'] - 2)
            base_params['macd_slow'] = max(21, base_params['macd_slow'] - 3)

        # 根據策略類型調整
        if strategy_type == 'scalping':
            base_params['rsi_length'] = max(7, base_params['rsi_length'] - 2)
            base_params['ema_fast'] = max(8, base_params['ema_fast'] - 2)
            base_params['ema_slow'] = max(13, base_params['ema_slow'] - 5)

        return base_params

    def _create_adaptive_strategy(self, params: Dict[str, int], strategy_type: str) -> ta.Strategy:
        """創建自適應策略"""
        strategy_ta = [
            {"kind": "rsi", "length": params['rsi_length']},
            {"kind": "ema", "length": params['ema_fast']},
            {"kind": "ema", "length": params['ema_slow']},
            {"kind": "macd", "fast": params['macd_fast'], "slow": params['macd_slow']},
            {"kind": "bbands", "length": params['bb_length']},
            {"kind": "atr", "length": params['atr_length']},
            {"kind": "adx", "length": 14},
        ]

        if strategy_type in ['swing', 'trend']:
            strategy_ta.extend([
                {"kind": "aroon", "length": 14},
                {"kind": "stoch", "k": 14, "d": 3},
            ])

        if strategy_type == 'scalping':
            strategy_ta.append({"kind": "stoch", "k": 5, "d": 3})

        return ta.Strategy(
            name=f"自適應_{strategy_type}",
            ta=strategy_ta
        )

    def _analyze_rsi_signal(self, df: pd.DataFrame, length: int, market_condition: MarketCondition) -> TechnicalSignal:
        """分析 RSI 信號"""
        rsi_col = f'RSI_{length}'
        rsi_val = df[rsi_col].iloc[-1]

        # 根據市場狀態調整閾值
        if market_condition.regime in [MarketRegime.BULL_STRONG, MarketRegime.BULL_WEAK]:
            oversold, overbought = 25, 75  # 牛市調整閾值
        elif market_condition.regime in [MarketRegime.BEAR_STRONG, MarketRegime.BEAR_WEAK]:
            oversold, overbought = 35, 65  # 熊市調整閾值
        else:
            oversold, overbought = 30, 70  # 標準閾值

        # 信號判斷
        if rsi_val < oversold:
            signal_type = "BUY"
            strength = min((oversold - rsi_val) / oversold, 1.0)
        elif rsi_val > overbought:
            signal_type = "SELL"
            strength = min((rsi_val - overbought) / (100 - overbought), 1.0)
        else:
            signal_type = "NEUTRAL"
            strength = 0.3

        # 考慮市場狀態調整信心度
        confidence = strength * market_condition.confidence

        return TechnicalSignal(
            indicator_name="RSI",
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            value=rsi_val,
            description=f"RSI({length}): {rsi_val:.2f}, 閾值: {oversold}-{overbought}",
            timeframe="current",
            timestamp=pd.Timestamp.now().isoformat()
        )

    def _analyze_macd_signal(self, df: pd.DataFrame, params: Dict[str, int], market_condition: MarketCondition) -> TechnicalSignal:
        """分析 MACD 信號"""
        macd_col = f'MACD_{params["macd_fast"]}_{params["macd_slow"]}_9'
        signal_col = f'MACDs_{params["macd_fast"]}_{params["macd_slow"]}_9'
        hist_col = f'MACDh_{params["macd_fast"]}_{params["macd_slow"]}_9'

        macd_val = df[macd_col].iloc[-1] if macd_col in df.columns else 0
        signal_val = df[signal_col].iloc[-1] if signal_col in df.columns else 0
        hist_val = df[hist_col].iloc[-1] if hist_col in df.columns else 0

        # 信號判斷
        if macd_val > signal_val and hist_val > 0:
            signal_type = "BUY"
            strength = min(abs(hist_val) * 50 + 0.3, 1.0)
        elif macd_val < signal_val and hist_val < 0:
            signal_type = "SELL"
            strength = min(abs(hist_val) * 50 + 0.3, 1.0)
        else:
            signal_type = "NEUTRAL"
            strength = 0.2

        # 根據市場狀態調整
        if market_condition.regime in [MarketRegime.BULL_STRONG, MarketRegime.BULL_WEAK] and signal_type == "BUY":
            strength *= 1.2
        elif market_condition.regime in [MarketRegime.BEAR_STRONG, MarketRegime.BEAR_WEAK] and signal_type == "SELL":
            strength *= 1.2

        confidence = min(strength * market_condition.confidence, 1.0)

        return TechnicalSignal(
            indicator_name="MACD",
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            value=macd_val,
            description=f"MACD: {macd_val:.4f}, Signal: {signal_val:.4f}, Hist: {hist_val:.4f}",
            timeframe="current",
            timestamp=pd.Timestamp.now().isoformat()
        )

    def _analyze_ema_signal(self, df: pd.DataFrame, params: Dict[str, int], market_condition: MarketCondition) -> TechnicalSignal:
        """分析 EMA 信號"""
        ema_fast_col = f'EMA_{params["ema_fast"]}'
        ema_slow_col = f'EMA_{params["ema_slow"]}'

        ema_fast = df[ema_fast_col].iloc[-1]
        ema_slow = df[ema_slow_col].iloc[-1]
        current_price = df['close'].iloc[-1]

        # 信號判斷
        if current_price > ema_fast > ema_slow:
            signal_type = "BUY"
            strength = min((current_price - ema_fast) / ema_fast * 100 + 0.5, 1.0)
        elif current_price < ema_fast < ema_slow:
            signal_type = "SELL"
            strength = min((ema_fast - current_price) / current_price * 100 + 0.5, 1.0)
        else:
            signal_type = "NEUTRAL"
            strength = 0.3

        confidence = strength * market_condition.confidence

        return TechnicalSignal(
            indicator_name="EMA",
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            value=ema_fast,
            description=f"EMA{params['ema_fast']}: {ema_fast:.4f}, EMA{params['ema_slow']}: {ema_slow:.4f}",
            timeframe="current",
            timestamp=pd.Timestamp.now().isoformat()
        )

    def _analyze_bollinger_signal(self, df: pd.DataFrame, params: Dict[str, int], market_condition: MarketCondition) -> TechnicalSignal:
        """分析布林帶信號"""
        bb_length = params['bb_length']
        upper_col = f'BBU_{bb_length}_2.0'
        middle_col = f'BBM_{bb_length}_2.0'
        lower_col = f'BBL_{bb_length}_2.0'

        if not all(col in df.columns for col in [upper_col, middle_col, lower_col]):
            return TechnicalSignal("BOLLINGER", "NEUTRAL", 0.1, 0.1, 0, "數據不足", "current", pd.Timestamp.now().isoformat())

        upper = df[upper_col].iloc[-1]
        middle = df[middle_col].iloc[-1]
        lower = df[lower_col].iloc[-1]
        current_price = df['close'].iloc[-1]

        # 信號判斷
        if current_price <= lower:
            signal_type = "BUY"
            strength = min((lower - current_price) / (middle - lower) + 0.6, 1.0)
        elif current_price >= upper:
            signal_type = "SELL"
            strength = min((current_price - upper) / (upper - middle) + 0.6, 1.0)
        else:
            signal_type = "NEUTRAL"
            # 根據價格在布林帶中的位置給予方向性
            position = (current_price - lower) / (upper - lower)
            if position > 0.7:
                strength = 0.4  # 偏向上軌
            elif position < 0.3:
                strength = 0.4  # 偏向下軌
            else:
                strength = 0.2

        confidence = strength * market_condition.confidence

        return TechnicalSignal(
            indicator_name="BOLLINGER",
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            value=current_price,
            description=f"BB: Upper={upper:.4f}, Mid={middle:.4f}, Lower={lower:.4f}, Price={current_price:.4f}",
            timeframe="current",
            timestamp=pd.Timestamp.now().isoformat()
        )

    def get_comprehensive_analysis(self, df: pd.DataFrame, strategy_type: str = 'scalping') -> Dict[str, Any]:
        """獲取綜合技術分析結果"""
        try:
            # 市場狀態檢測
            market_condition = self.detect_market_regime(df)
            
            # 技術指標分析
            technical_signals = self.calculate_adaptive_indicators(df, strategy_type)
            
            # 計算綜合得分
            total_signals = len(technical_signals)
            if total_signals == 0:
                overall_signal = "NEUTRAL"
                overall_confidence = 0.1
            else:
                buy_signals = sum(1 for s in technical_signals.values() if s.signal_type == "BUY")
                sell_signals = sum(1 for s in technical_signals.values() if s.signal_type == "SELL")
                
                buy_strength = sum(s.strength for s in technical_signals.values() if s.signal_type == "BUY")
                sell_strength = sum(s.strength for s in technical_signals.values() if s.signal_type == "SELL")
                
                # 綜合判斷
                if buy_signals > sell_signals and buy_strength > sell_strength:
                    overall_signal = "BUY"
                    overall_confidence = buy_strength / max(buy_signals, 1)
                elif sell_signals > buy_signals and sell_strength > buy_strength:
                    overall_signal = "SELL"
                    overall_confidence = sell_strength / max(sell_signals, 1)
                else:
                    overall_signal = "NEUTRAL"
                    overall_confidence = 0.3

            return {
                'market_condition': asdict(market_condition),
                'technical_signals': {k: asdict(v) for k, v in technical_signals.items()},
                'overall_signal': overall_signal,
                'overall_confidence': min(overall_confidence * market_condition.confidence, 1.0),
                'strategy_type': strategy_type,
                'analysis_timestamp': pd.Timestamp.now().isoformat()
            }

        except Exception as e:
            logger.error(f"綜合分析錯誤: {e}")
            return {
                'error': str(e),
                'market_condition': None,
                'technical_signals': {},
                'overall_signal': "NEUTRAL",
                'overall_confidence': 0.1,
                'strategy_type': strategy_type,
                'analysis_timestamp': pd.Timestamp.now().isoformat()
            }
