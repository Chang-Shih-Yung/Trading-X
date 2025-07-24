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
    """技術指標結果數據類"""
    value: float
    signal: str  # 'BUY', 'SELL', 'NEUTRAL'
    strength: float  # 0-1, 信號強度
    description: str
    type: IndicatorType

class TechnicalIndicatorsService:
    """技術指標服務類"""
    
    def __init__(self):
        self.required_columns = ['open', 'high', 'low', 'close', 'volume']
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """驗證數據格式"""
        return all(col in df.columns for col in self.required_columns)
    
    def calculate_trend_indicators(self, df: pd.DataFrame) -> Dict[str, IndicatorResult]:
        """計算趨勢指標"""
        if not self.validate_data(df):
            raise ValueError("數據格式不正確，缺少必要欄位")
        
        results = {}
        
        # EMA 指標
        ema_20 = ta.ema(df['close'], length=20)
        ema_50 = ta.ema(df['close'], length=50)
        
        current_price = df['close'].iloc[-1]
        ema_20_val = ema_20.iloc[-1] if not pd.isna(ema_20.iloc[-1]) else current_price
        ema_50_val = ema_50.iloc[-1] if not pd.isna(ema_50.iloc[-1]) else current_price
        
        # EMA 交叉信號
        if current_price > ema_20_val > ema_50_val:
            ema_signal = "BUY"
            ema_strength = 0.8
        elif current_price < ema_20_val < ema_50_val:
            ema_signal = "SELL"
            ema_strength = 0.8
        else:
            ema_signal = "NEUTRAL"
            ema_strength = 0.3
            
        results['ema'] = IndicatorResult(
            value=ema_20_val,
            signal=ema_signal,
            strength=ema_strength,
            description=f"EMA20: {ema_20_val:.4f}, EMA50: {ema_50_val:.4f}",
            type=IndicatorType.TREND
        )
        
        # MACD 指標 - 增強敏感度
        macd_data = ta.macd(df['close'], fast=12, slow=26, signal=9)
        if macd_data is not None and not macd_data.empty:
            macd_line = macd_data.iloc[-1, 0] if not pd.isna(macd_data.iloc[-1, 0]) else 0
            signal_line = macd_data.iloc[-1, 1] if not pd.isna(macd_data.iloc[-1, 1]) else 0
            histogram = macd_data.iloc[-1, 2] if not pd.isna(macd_data.iloc[-1, 2]) else 0
            
            # 🚀 更敏感的 MACD 判斷
            if macd_line > signal_line and histogram > 0:
                macd_signal = "BUY"
                # 增強信號強度計算
                macd_strength = min(abs(histogram) * 20 + 0.3, 1.0)
            elif macd_line < signal_line and histogram < 0:
                macd_signal = "SELL"
                # 對做空信號給予更高強度
                macd_strength = min(abs(histogram) * 25 + 0.4, 1.0)
            else:
                # 即使沒有明確交叉，也根據位置給予方向性
                if macd_line > 0 and signal_line > 0:
                    macd_signal = "BUY"
                    macd_strength = 0.3
                elif macd_line < 0 and signal_line < 0:
                    macd_signal = "SELL"
                    macd_strength = 0.4  # 空頭環境給更高權重
                else:
                    macd_signal = "NEUTRAL"
                    macd_strength = 0.1
        else:
            macd_line = signal_line = histogram = 0
            macd_signal = "NEUTRAL"
            macd_strength = 0.1
            
        results['macd'] = IndicatorResult(
            value=macd_line,
            signal=macd_signal,
            strength=macd_strength,
            description=f"MACD: {macd_line:.4f}, Signal: {signal_line:.4f}, Hist: {histogram:.4f}",
            type=IndicatorType.TREND
        )
        
        return results
    
    def calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict[str, IndicatorResult]:
        """計算動量指標"""
        if not self.validate_data(df):
            raise ValueError("數據格式不正確，缺少必要欄位")
        
        results = {}
        
        # RSI 指標 - 更敏感的超買超賣設定
        rsi = ta.rsi(df['close'], length=14)
        rsi_val = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
        
        # 🔥 更激進的 RSI 閾值設定
        if rsi_val > 65:  # 降低超買閾值從 70 到 65
            rsi_signal = "SELL"
            rsi_strength = min((rsi_val - 65) / 35, 1.0)  # 調整計算公式
        elif rsi_val < 35:  # 提高超賣閾值從 30 到 35
            rsi_signal = "BUY"
            rsi_strength = min((35 - rsi_val) / 35, 1.0)  # 調整計算公式
        else:
            rsi_signal = "NEUTRAL"
            # 即使在中性區間也給予一定的方向性
            if rsi_val > 55:
                rsi_strength = 0.3  # 偏向超買
            elif rsi_val < 45:
                rsi_strength = 0.3  # 偏向超賣
            else:
                rsi_strength = 0.1
            
        results['rsi'] = IndicatorResult(
            value=rsi_val,
            signal=rsi_signal,
            strength=rsi_strength,
            description=f"RSI: {rsi_val:.2f}",
            type=IndicatorType.MOMENTUM
        )
        
        # Stochastic 指標
        stoch = ta.stoch(df['high'], df['low'], df['close'])
        if stoch is not None and not stoch.empty:
            stoch_k = stoch.iloc[-1, 0] if not pd.isna(stoch.iloc[-1, 0]) else 50
            stoch_d = stoch.iloc[-1, 1] if not pd.isna(stoch.iloc[-1, 1]) else 50
            
            if stoch_k > 80 and stoch_d > 80:
                stoch_signal = "SELL"
                stoch_strength = 0.7
            elif stoch_k < 20 and stoch_d < 20:
                stoch_signal = "BUY"
                stoch_strength = 0.7
            else:
                stoch_signal = "NEUTRAL"
                stoch_strength = 0.3
        else:
            stoch_k = stoch_d = 50
            stoch_signal = "NEUTRAL"
            stoch_strength = 0.3
            
        results['stochastic'] = IndicatorResult(
            value=stoch_k,
            signal=stoch_signal,
            strength=stoch_strength,
            description=f"Stoch K: {stoch_k:.2f}, D: {stoch_d:.2f}",
            type=IndicatorType.MOMENTUM
        )
        
        # Williams %R
        willr = ta.willr(df['high'], df['low'], df['close'], length=14)
        willr_val = willr.iloc[-1] if not pd.isna(willr.iloc[-1]) else -50
        
        if willr_val > -20:
            willr_signal = "SELL"
            willr_strength = 0.6
        elif willr_val < -80:
            willr_signal = "BUY"
            willr_strength = 0.6
        else:
            willr_signal = "NEUTRAL"
            willr_strength = 0.2
            
        results['williams_r'] = IndicatorResult(
            value=willr_val,
            signal=willr_signal,
            strength=willr_strength,
            description=f"Williams %R: {willr_val:.2f}",
            type=IndicatorType.MOMENTUM
        )
        
        return results
    
    def calculate_volatility_indicators(self, df: pd.DataFrame) -> Dict[str, IndicatorResult]:
        """計算波動性指標"""
        if not self.validate_data(df):
            raise ValueError("數據格式不正確，缺少必要欄位")
        
        results = {}
        
        # Bollinger Bands
        bb = ta.bbands(df['close'], length=20, std=2)
        if bb is not None and not bb.empty:
            bb_upper = bb.iloc[-1, 0] if not pd.isna(bb.iloc[-1, 0]) else df['close'].iloc[-1] * 1.02
            bb_middle = bb.iloc[-1, 1] if not pd.isna(bb.iloc[-1, 1]) else df['close'].iloc[-1]
            bb_lower = bb.iloc[-1, 2] if not pd.isna(bb.iloc[-1, 2]) else df['close'].iloc[-1] * 0.98
        else:
            current_price = df['close'].iloc[-1]
            bb_upper = current_price * 1.02
            bb_middle = current_price
            bb_lower = current_price * 0.98
        
        current_price = df['close'].iloc[-1]
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
        
        if bb_position > 0.8:
            bb_signal = "SELL"
            bb_strength = 0.7
        elif bb_position < 0.2:
            bb_signal = "BUY"
            bb_strength = 0.7
        else:
            bb_signal = "NEUTRAL"
            bb_strength = 0.3
            
        results['bollinger_bands'] = IndicatorResult(
            value=bb_position,
            signal=bb_signal,
            strength=bb_strength,
            description=f"BB Position: {bb_position:.2f}, Upper: {bb_upper:.4f}, Lower: {bb_lower:.4f}",
            type=IndicatorType.VOLATILITY
        )
        
        # ATR (Average True Range)
        atr = ta.atr(df['high'], df['low'], df['close'], length=14)
        atr_val = atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else current_price * 0.02
        
        # ATR 相對於價格的百分比
        atr_percent = (atr_val / current_price) * 100
        
        if atr_percent > 3:
            atr_signal = "NEUTRAL"  # 高波動性，謹慎交易
            atr_strength = 0.8
        else:
            atr_signal = "NEUTRAL"
            atr_strength = 0.4
            
        results['atr'] = IndicatorResult(
            value=atr_val,
            signal=atr_signal,
            strength=atr_strength,
            description=f"ATR: {atr_val:.4f} ({atr_percent:.2f}%)",
            type=IndicatorType.VOLATILITY
        )
        
        return results
    
    def calculate_volume_indicators(self, df: pd.DataFrame) -> Dict[str, IndicatorResult]:
        """計算成交量指標"""
        if not self.validate_data(df):
            raise ValueError("數據格式不正確，缺少必要欄位")
        
        results = {}
        
        # OBV (On-Balance Volume)
        obv = ta.obv(df['close'], df['volume'])
        if obv is not None and not obv.empty:
            obv_val = obv.iloc[-1] if not pd.isna(obv.iloc[-1]) else 0
            obv_sma = ta.sma(obv, length=20)
            obv_sma_val = obv_sma.iloc[-1] if obv_sma is not None and not pd.isna(obv_sma.iloc[-1]) else 0
            
            if obv_val > obv_sma_val:
                obv_signal = "BUY"
                obv_strength = 0.6
            elif obv_val < obv_sma_val:
                obv_signal = "SELL"
                obv_strength = 0.6
            else:
                obv_signal = "NEUTRAL"
                obv_strength = 0.3
        else:
            obv_val = obv_sma_val = 0
            obv_signal = "NEUTRAL"
            obv_strength = 0.3
            
        results['obv'] = IndicatorResult(
            value=obv_val,
            signal=obv_signal,
            strength=obv_strength,
            description=f"OBV: {obv_val:.0f}, OBV SMA: {obv_sma_val:.0f}",
            type=IndicatorType.VOLUME
        )
        
        # Volume SMA
        volume_sma = ta.sma(df['volume'], length=20)
        current_volume = df['volume'].iloc[-1]
        avg_volume = volume_sma.iloc[-1] if not pd.isna(volume_sma.iloc[-1]) else current_volume
        
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        if volume_ratio > 1.5:
            volume_signal = "BUY"  # 高成交量通常是好信號
            volume_strength = min(volume_ratio / 3, 1.0)
        else:
            volume_signal = "NEUTRAL"
            volume_strength = 0.3
            
        results['volume'] = IndicatorResult(
            value=volume_ratio,
            signal=volume_signal,
            strength=volume_strength,
            description=f"Volume Ratio: {volume_ratio:.2f}",
            type=IndicatorType.VOLUME
        )
        
        return results
    
    def calculate_support_resistance(self, df: pd.DataFrame) -> Dict[str, IndicatorResult]:
        """計算支撐阻力位"""
        if not self.validate_data(df):
            raise ValueError("數據格式不正確，缺少必要欄位")
        
        results = {}
        
        # 計算近期高低點
        high_20 = df['high'].rolling(window=20).max()
        low_20 = df['low'].rolling(window=20).min()
        
        current_price = df['close'].iloc[-1]
        resistance = high_20.iloc[-1]
        support = low_20.iloc[-1]
        
        # 計算價格在支撐阻力區間的位置
        price_position = (current_price - support) / (resistance - support) if resistance > support else 0.5
        
        if price_position > 0.8:
            sr_signal = "SELL"  # 接近阻力位
            sr_strength = 0.7
        elif price_position < 0.2:
            sr_signal = "BUY"  # 接近支撐位
            sr_strength = 0.7
        else:
            sr_signal = "NEUTRAL"
            sr_strength = 0.3
            
        results['support_resistance'] = IndicatorResult(
            value=price_position,
            signal=sr_signal,
            strength=sr_strength,
            description=f"Position: {price_position:.2f}, Support: {support:.4f}, Resistance: {resistance:.4f}",
            type=IndicatorType.SUPPORT_RESISTANCE
        )
        
        return results
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> Dict[str, IndicatorResult]:
        """計算所有技術指標"""
        service = TechnicalIndicatorsService()
        all_indicators = {}
        
        try:
            all_indicators.update(service.calculate_trend_indicators(df))
        except Exception as e:
            print(f"趨勢指標計算錯誤: {e}")
            
        try:
            all_indicators.update(service.calculate_momentum_indicators(df))
        except Exception as e:
            print(f"動量指標計算錯誤: {e}")
            
        try:
            all_indicators.update(service.calculate_volatility_indicators(df))
        except Exception as e:
            print(f"波動性指標計算錯誤: {e}")
            
        try:
            all_indicators.update(service.calculate_volume_indicators(df))
        except Exception as e:
            print(f"成交量指標計算錯誤: {e}")
            
        try:
            all_indicators.update(service.calculate_support_resistance(df))
        except Exception as e:
            print(f"支撐阻力計算錯誤: {e}")
            
        return all_indicators
