import pandas as pd
import numpy as np
import pandas_ta as ta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class IndicatorType(Enum):
    """指標類型枚舉"""
    TREND = "trend"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    SUPPORT_RESISTANCE = "support_resistance"

@dataclass
class IndicatorResult:
    """指標計算結果"""
    name: str
    value: float
    signal: str  # BUY, SELL, NEUTRAL
    strength: float  # 0-100
    metadata: Dict

class TechnicalIndicators:
    """技術指標計算類"""
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> Dict[str, IndicatorResult]:
        """計算所有技術指標"""
        if df.empty or len(df) < 50:
            return {}
        
        results = {}
        
        # 趨勢指標
        results.update(TechnicalIndicators.calculate_trend_indicators(df))
        
        # 動量指標
        results.update(TechnicalIndicators.calculate_momentum_indicators(df))
        
        # 波動性指標
        results.update(TechnicalIndicators.calculate_volatility_indicators(df))
        
        # 成交量指標
        results.update(TechnicalIndicators.calculate_volume_indicators(df))
        
        # 支撐阻力指標
        results.update(TechnicalIndicators.calculate_support_resistance(df))
        
        return results
    
    @staticmethod
    def calculate_trend_indicators(df: pd.DataFrame) -> Dict[str, IndicatorResult]:
        """計算趨勢指標"""
        results = {}
        
        # EMA
        ema_20 = talib.EMA(df['close'], timeperiod=20)
        ema_50 = talib.EMA(df['close'], timeperiod=50)
        current_price = df['close'].iloc[-1]
        
        ema_signal = "BUY" if current_price > ema_20.iloc[-1] > ema_50.iloc[-1] else \
                    "SELL" if current_price < ema_20.iloc[-1] < ema_50.iloc[-1] else "NEUTRAL"
        
        results['EMA'] = IndicatorResult(
            name="EMA",
            value=ema_20.iloc[-1],
            signal=ema_signal,
            strength=TechnicalIndicators._calculate_trend_strength(current_price, ema_20.iloc[-1], ema_50.iloc[-1]),
            metadata={"ema_20": ema_20.iloc[-1], "ema_50": ema_50.iloc[-1]}
        )
        
        # MACD
        macd, macdsignal, macdhist = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        
        macd_signal = "BUY" if macd.iloc[-1] > macdsignal.iloc[-1] and macdhist.iloc[-1] > 0 else \
                     "SELL" if macd.iloc[-1] < macdsignal.iloc[-1] and macdhist.iloc[-1] < 0 else "NEUTRAL"
        
        results['MACD'] = IndicatorResult(
            name="MACD",
            value=macd.iloc[-1],
            signal=macd_signal,
            strength=min(abs(macdhist.iloc[-1]) * 100, 100),
            metadata={
                "macd": macd.iloc[-1],
                "signal": macdsignal.iloc[-1],
                "histogram": macdhist.iloc[-1]
            }
        )
        
        # 一目均衡表
        ichimoku = TechnicalIndicators._calculate_ichimoku(df)
        results['ICHIMOKU'] = ichimoku
        
        return results
    
    @staticmethod
    def calculate_momentum_indicators(df: pd.DataFrame) -> Dict[str, IndicatorResult]:
        """計算動量指標"""
        results = {}
        
        # RSI
        rsi = talib.RSI(df['close'], timeperiod=14)
        rsi_value = rsi.iloc[-1]
        
        rsi_signal = "SELL" if rsi_value > 70 else \
                    "BUY" if rsi_value < 30 else "NEUTRAL"
        
        rsi_strength = abs(50 - rsi_value) * 2  # 0-100範圍
        
        results['RSI'] = IndicatorResult(
            name="RSI",
            value=rsi_value,
            signal=rsi_signal,
            strength=rsi_strength,
            metadata={"overbought": rsi_value > 70, "oversold": rsi_value < 30}
        )
        
        # Stochastic
        slowk, slowd = talib.STOCH(df['high'], df['low'], df['close'])
        
        stoch_signal = "SELL" if slowk.iloc[-1] > 80 and slowd.iloc[-1] > 80 else \
                      "BUY" if slowk.iloc[-1] < 20 and slowd.iloc[-1] < 20 else "NEUTRAL"
        
        results['STOCH'] = IndicatorResult(
            name="STOCH",
            value=slowk.iloc[-1],
            signal=stoch_signal,
            strength=abs(50 - slowk.iloc[-1]) * 2,
            metadata={"k": slowk.iloc[-1], "d": slowd.iloc[-1]}
        )
        
        # Williams %R
        willr = talib.WILLR(df['high'], df['low'], df['close'], timeperiod=14)
        willr_value = willr.iloc[-1]
        
        willr_signal = "BUY" if willr_value < -80 else \
                      "SELL" if willr_value > -20 else "NEUTRAL"
        
        results['WILLR'] = IndicatorResult(
            name="WILLR",
            value=willr_value,
            signal=willr_signal,
            strength=abs(-50 - willr_value) * 2,
            metadata={"oversold": willr_value < -80, "overbought": willr_value > -20}
        )
        
        return results
    
    @staticmethod
    def calculate_volatility_indicators(df: pd.DataFrame) -> Dict[str, IndicatorResult]:
        """計算波動性指標"""
        results = {}
        
        # 布林通道
        bb_upper, bb_middle, bb_lower = talib.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2)
        current_price = df['close'].iloc[-1]
        
        bb_position = (current_price - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
        
        bb_signal = "SELL" if bb_position > 0.8 else \
                   "BUY" if bb_position < 0.2 else "NEUTRAL"
        
        results['BBANDS'] = IndicatorResult(
            name="BBANDS",
            value=bb_position,
            signal=bb_signal,
            strength=abs(bb_position - 0.5) * 200,
            metadata={
                "upper": bb_upper.iloc[-1],
                "middle": bb_middle.iloc[-1],
                "lower": bb_lower.iloc[-1],
                "position": bb_position
            }
        )
        
        # ATR
        atr = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
        atr_value = atr.iloc[-1]
        atr_percentage = (atr_value / current_price) * 100
        
        results['ATR'] = IndicatorResult(
            name="ATR",
            value=atr_value,
            signal="NEUTRAL",
            strength=min(atr_percentage * 10, 100),
            metadata={
                "atr_value": atr_value,
                "atr_percentage": atr_percentage,
                "volatility_level": "HIGH" if atr_percentage > 3 else "MEDIUM" if atr_percentage > 1.5 else "LOW"
            }
        )
        
        return results
    
    @staticmethod
    def calculate_volume_indicators(df: pd.DataFrame) -> Dict[str, IndicatorResult]:
        """計算成交量指標"""
        results = {}
        
        # OBV (On Balance Volume)
        obv = talib.OBV(df['close'], df['volume'])
        obv_sma = talib.SMA(obv, timeperiod=20)
        
        obv_signal = "BUY" if obv.iloc[-1] > obv_sma.iloc[-1] else \
                    "SELL" if obv.iloc[-1] < obv_sma.iloc[-1] else "NEUTRAL"
        
        results['OBV'] = IndicatorResult(
            name="OBV",
            value=obv.iloc[-1],
            signal=obv_signal,
            strength=50,  # 簡化強度計算
            metadata={"obv": obv.iloc[-1], "obv_sma": obv_sma.iloc[-1]}
        )
        
        # VWAP (Volume Weighted Average Price)
        vwap = TechnicalIndicators._calculate_vwap(df)
        
        vwap_signal = "BUY" if df['close'].iloc[-1] > vwap else \
                     "SELL" if df['close'].iloc[-1] < vwap else "NEUTRAL"
        
        results['VWAP'] = IndicatorResult(
            name="VWAP",
            value=vwap,
            signal=vwap_signal,
            strength=abs((df['close'].iloc[-1] - vwap) / vwap) * 1000,
            metadata={"vwap": vwap, "distance": df['close'].iloc[-1] - vwap}
        )
        
        return results
    
    @staticmethod
    def calculate_support_resistance(df: pd.DataFrame) -> Dict[str, IndicatorResult]:
        """計算支撐阻力指標"""
        results = {}
        
        # Pivot Points
        pivot_points = TechnicalIndicators._calculate_pivot_points(df)
        current_price = df['close'].iloc[-1]
        
        # 判斷當前價格相對於支撐阻力的位置
        if current_price > pivot_points['r2']:
            pivot_signal = "SELL"
            strength = 80
        elif current_price < pivot_points['s2']:
            pivot_signal = "BUY"
            strength = 80
        elif current_price > pivot_points['r1']:
            pivot_signal = "SELL"
            strength = 60
        elif current_price < pivot_points['s1']:
            pivot_signal = "BUY"
            strength = 60
        else:
            pivot_signal = "NEUTRAL"
            strength = 30
        
        results['PIVOT'] = IndicatorResult(
            name="PIVOT",
            value=pivot_points['pivot'],
            signal=pivot_signal,
            strength=strength,
            metadata=pivot_points
        )
        
        # 斐波那契回調
        fib_levels = TechnicalIndicators._calculate_fibonacci_retracement(df)
        results['FIBONACCI'] = IndicatorResult(
            name="FIBONACCI",
            value=fib_levels['50%'],
            signal="NEUTRAL",
            strength=50,
            metadata=fib_levels
        )
        
        return results
    
    @staticmethod
    def _calculate_trend_strength(current_price: float, ema_20: float, ema_50: float) -> float:
        """計算趨勢強度"""
        if ema_20 > ema_50:  # 上升趨勢
            strength = ((current_price - ema_50) / ema_50) * 1000
        else:  # 下降趨勢
            strength = ((ema_50 - current_price) / ema_50) * 1000
        
        return min(max(abs(strength), 0), 100)
    
    @staticmethod
    def _calculate_ichimoku(df: pd.DataFrame) -> IndicatorResult:
        """計算一目均衡表"""
        # 轉換線 (Conversion Line)
        high_9 = df['high'].rolling(window=9).max()
        low_9 = df['low'].rolling(window=9).min()
        conversion_line = (high_9 + low_9) / 2
        
        # 基準線 (Base Line)
        high_26 = df['high'].rolling(window=26).max()
        low_26 = df['low'].rolling(window=26).min()
        base_line = (high_26 + low_26) / 2
        
        # 先行帶A (Leading Span A)
        leading_span_a = ((conversion_line + base_line) / 2).shift(26)
        
        # 先行帶B (Leading Span B)
        high_52 = df['high'].rolling(window=52).max()
        low_52 = df['low'].rolling(window=52).min()
        leading_span_b = ((high_52 + low_52) / 2).shift(26)
        
        current_price = df['close'].iloc[-1]
        
        # 判斷信號
        if (current_price > leading_span_a.iloc[-1] and 
            current_price > leading_span_b.iloc[-1] and
            conversion_line.iloc[-1] > base_line.iloc[-1]):
            signal = "BUY"
            strength = 75
        elif (current_price < leading_span_a.iloc[-1] and 
              current_price < leading_span_b.iloc[-1] and
              conversion_line.iloc[-1] < base_line.iloc[-1]):
            signal = "SELL"
            strength = 75
        else:
            signal = "NEUTRAL"
            strength = 30
        
        return IndicatorResult(
            name="ICHIMOKU",
            value=conversion_line.iloc[-1],
            signal=signal,
            strength=strength,
            metadata={
                "conversion_line": conversion_line.iloc[-1],
                "base_line": base_line.iloc[-1],
                "leading_span_a": leading_span_a.iloc[-1],
                "leading_span_b": leading_span_b.iloc[-1]
            }
        )
    
    @staticmethod
    def _calculate_vwap(df: pd.DataFrame) -> float:
        """計算VWAP"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        vwap = (typical_price * df['volume']).sum() / df['volume'].sum()
        return float(vwap)
    
    @staticmethod
    def _calculate_pivot_points(df: pd.DataFrame) -> Dict[str, float]:
        """計算樞軸點"""
        # 使用前一天的高低收
        if len(df) < 2:
            return {}
        
        prev_high = df['high'].iloc[-2]
        prev_low = df['low'].iloc[-2]
        prev_close = df['close'].iloc[-2]
        
        # 標準樞軸點計算
        pivot = (prev_high + prev_low + prev_close) / 3
        
        # 阻力位
        r1 = 2 * pivot - prev_low
        r2 = pivot + (prev_high - prev_low)
        r3 = prev_high + 2 * (pivot - prev_low)
        
        # 支撐位
        s1 = 2 * pivot - prev_high
        s2 = pivot - (prev_high - prev_low)
        s3 = prev_low - 2 * (prev_high - pivot)
        
        return {
            'pivot': pivot,
            'r1': r1, 'r2': r2, 'r3': r3,
            's1': s1, 's2': s2, 's3': s3
        }
    
    @staticmethod
    def _calculate_fibonacci_retracement(df: pd.DataFrame, period: int = 50) -> Dict[str, float]:
        """計算斐波那契回調"""
        if len(df) < period:
            return {}
        
        recent_data = df.tail(period)
        high = recent_data['high'].max()
        low = recent_data['low'].min()
        
        diff = high - low
        
        return {
            '0%': high,
            '23.6%': high - 0.236 * diff,
            '38.2%': high - 0.382 * diff,
            '50%': high - 0.5 * diff,
            '61.8%': high - 0.618 * diff,
            '78.6%': high - 0.786 * diff,
            '100%': low
        }
