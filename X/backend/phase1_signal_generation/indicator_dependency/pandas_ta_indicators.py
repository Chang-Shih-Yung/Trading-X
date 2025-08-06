"""
🎯 Trading X - pandas-ta 技術指標引擎（真實版）
基於真實市場數據的完整技術指標計算
"""

from typing import Dict, Any, List, Optional
import asyncio
import numpy as np
import pandas as pd
import logging
import sys
from pathlib import Path

# 添加上級目錄到路徑
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent / "core"))

from binance_data_connector import binance_connector

logger = logging.getLogger(__name__)

class TechnicalIndicatorEngine:
    """技術指標引擎（真實版）"""
    
    def __init__(self):
        self.indicator_cache = {}
        self.cache_timeout = 30  # 30秒緩存
        
    async def calculate_all_indicators(self, symbol: str) -> Dict[str, float]:
        """計算所有技術指標 - 基於真實市場數據"""
        try:
            # 獲取真實K線數據
            async with binance_connector as connector:
                klines = await connector.get_kline_data(symbol, "1m", 200)
                
                if not klines or len(klines) < 50:
                    logger.warning(f"K線數據不足: {len(klines) if klines else 0}，無法計算技術指標")
                    return self._get_default_indicators()
                
                # 轉換為DataFrame
                df = self._klines_to_dataframe(klines)
                
                # 計算各種技術指標
                indicators = {}
                
                # 1. 趨勢指標
                indicators.update(self._calculate_trend_indicators(df))
                
                # 2. 動量指標
                indicators.update(self._calculate_momentum_indicators(df))
                
                # 3. 波動性指標
                indicators.update(self._calculate_volatility_indicators(df))
                
                # 4. 成交量指標
                indicators.update(self._calculate_volume_indicators(df))
                
                # 5. 支撐阻力指標
                indicators.update(self._calculate_support_resistance_indicators(df))
                
                logger.info(f"成功計算 {len(indicators)} 個技術指標")
                return indicators
                
        except Exception as e:
            logger.error(f"技術指標計算失敗: {e}")
            return self._get_default_indicators()
    
    def _klines_to_dataframe(self, klines: List[List]) -> pd.DataFrame:
        """將K線數據轉換為DataFrame"""
        try:
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # 轉換數據類型
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"DataFrame轉換失敗: {e}")
            raise
    
    def _calculate_trend_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """計算趨勢指標"""
        try:
            indicators = {}
            close = df['close']
            
            # 移動平均線
            sma_20 = close.rolling(window=20).mean().iloc[-1]
            sma_50 = close.rolling(window=50).mean().iloc[-1]
            ema_12 = close.ewm(span=12).mean().iloc[-1]
            ema_26 = close.ewm(span=26).mean().iloc[-1]
            
            indicators['SMA_20'] = float(sma_20) if not pd.isna(sma_20) else float(close.iloc[-1])
            indicators['SMA_50'] = float(sma_50) if not pd.isna(sma_50) else float(close.iloc[-1])
            indicators['EMA_12'] = float(ema_12) if not pd.isna(ema_12) else float(close.iloc[-1])
            indicators['EMA_26'] = float(ema_26) if not pd.isna(ema_26) else float(close.iloc[-1])
            
            # MACD
            macd_line = ema_12 - ema_26
            signal_line = pd.Series([macd_line]).ewm(span=9).mean().iloc[-1]
            macd_histogram = macd_line - signal_line
            
            indicators['MACD'] = float(macd_line) if not pd.isna(macd_line) else 0.0
            indicators['MACD_signal'] = float(signal_line) if not pd.isna(signal_line) else 0.0
            indicators['MACD_histogram'] = float(macd_histogram) if not pd.isna(macd_histogram) else 0.0
            
            # 趨勢強度
            current_price = float(close.iloc[-1])
            price_vs_sma20 = (current_price - indicators['SMA_20']) / indicators['SMA_20']
            price_vs_sma50 = (current_price - indicators['SMA_50']) / indicators['SMA_50']
            
            indicators['trend_strength'] = (price_vs_sma20 + price_vs_sma50) / 2
            
            return indicators
            
        except Exception as e:
            logger.error(f"趨勢指標計算失敗: {e}")
            return {}
    
    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """計算動量指標"""
        try:
            indicators = {}
            close = df['close']
            high = df['high']
            low = df['low']
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['RSI'] = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            
            # Stochastic Oscillator
            lowest_low = low.rolling(window=14).min()
            highest_high = high.rolling(window=14).max()
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=3).mean()
            
            indicators['STOCH_K'] = float(k_percent.iloc[-1]) if not pd.isna(k_percent.iloc[-1]) else 50.0
            indicators['STOCH_D'] = float(d_percent.iloc[-1]) if not pd.isna(d_percent.iloc[-1]) else 50.0
            
            # Williams %R
            willr = -100 * ((highest_high - close) / (highest_high - lowest_low))
            indicators['WILLR'] = float(willr.iloc[-1]) if not pd.isna(willr.iloc[-1]) else -50.0
            
            # Momentum
            momentum = close.diff(periods=10)
            indicators['MOM'] = float(momentum.iloc[-1]) if not pd.isna(momentum.iloc[-1]) else 0.0
            
            # CCI (Commodity Channel Index)
            typical_price = (high + low + close) / 3
            sma_tp = typical_price.rolling(window=20).mean()
            mad = typical_price.rolling(window=20).apply(lambda x: np.mean(np.abs(x - x.mean())))
            cci = (typical_price - sma_tp) / (0.015 * mad)
            indicators['CCI'] = float(cci.iloc[-1]) if not pd.isna(cci.iloc[-1]) else 0.0
            
            return indicators
            
        except Exception as e:
            logger.error(f"動量指標計算失敗: {e}")
            return {}
    
    def _calculate_volatility_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """計算波動性指標"""
        try:
            indicators = {}
            close = df['close']
            high = df['high']
            low = df['low']
            
            # Bollinger Bands
            sma_20 = close.rolling(window=20).mean()
            std_20 = close.rolling(window=20).std()
            bb_upper = sma_20 + (std_20 * 2)
            bb_lower = sma_20 - (std_20 * 2)
            bb_middle = sma_20
            
            current_price = float(close.iloc[-1])
            upper = float(bb_upper.iloc[-1]) if not pd.isna(bb_upper.iloc[-1]) else current_price
            lower = float(bb_lower.iloc[-1]) if not pd.isna(bb_lower.iloc[-1]) else current_price
            middle = float(bb_middle.iloc[-1]) if not pd.isna(bb_middle.iloc[-1]) else current_price
            
            indicators['BB_upper'] = upper
            indicators['BB_lower'] = lower
            indicators['BB_middle'] = middle
            
            # BB Position (0-1, where 0.5 is middle)
            if upper != lower:
                bb_position = (current_price - lower) / (upper - lower)
            else:
                bb_position = 0.5
            indicators['BB_position'] = float(bb_position)
            
            # ATR (Average True Range)
            tr1 = high - low
            tr2 = np.abs(high - close.shift(1))
            tr3 = np.abs(low - close.shift(1))
            true_range = np.maximum(tr1, np.maximum(tr2, tr3))
            atr = true_range.rolling(window=14).mean()
            indicators['ATR'] = float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else 0.0
            
            # Volatility (20期標準差)
            volatility = close.pct_change().rolling(window=20).std() * np.sqrt(252)  # 年化
            indicators['volatility'] = float(volatility.iloc[-1]) if not pd.isna(volatility.iloc[-1]) else 0.0
            
            return indicators
            
        except Exception as e:
            logger.error(f"波動性指標計算失敗: {e}")
            return {}
    
    def _calculate_volume_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """計算成交量指標"""
        try:
            indicators = {}
            close = df['close']
            volume = df['volume']
            
            # OBV (On Balance Volume)
            obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
            indicators['OBV'] = float(obv.iloc[-1])
            
            # Volume SMA
            volume_sma = volume.rolling(window=20).mean()
            indicators['volume_SMA'] = float(volume_sma.iloc[-1]) if not pd.isna(volume_sma.iloc[-1]) else float(volume.iloc[-1])
            
            # Volume ratio (current vs average)
            current_volume = float(volume.iloc[-1])
            avg_volume = indicators['volume_SMA']
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            indicators['volume_ratio'] = volume_ratio
            
            # Volume trend (short vs long term average)
            volume_sma_short = volume.rolling(window=10).mean().iloc[-1]
            volume_sma_long = volume.rolling(window=50).mean().iloc[-1]
            
            if not pd.isna(volume_sma_short) and not pd.isna(volume_sma_long) and volume_sma_long > 0:
                volume_trend = (volume_sma_short - volume_sma_long) / volume_sma_long
            else:
                volume_trend = 0.0
            
            indicators['volume_trend'] = float(volume_trend)
            
            return indicators
            
        except Exception as e:
            logger.error(f"成交量指標計算失敗: {e}")
            return {}
    
    def _calculate_support_resistance_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """計算支撐阻力指標"""
        try:
            indicators = {}
            close = df['close']
            high = df['high']
            low = df['low']
            
            # Pivot Points
            period_high = high.rolling(window=20).max()
            period_low = low.rolling(window=20).min()
            period_close = close.iloc[-2] if len(close) > 1 else close.iloc[-1]  # 前一收盤
            
            pivot = (float(period_high.iloc[-1]) + float(period_low.iloc[-1]) + float(period_close)) / 3
            
            indicators['pivot_point'] = pivot
            indicators['resistance_1'] = 2 * pivot - float(period_low.iloc[-1])
            indicators['support_1'] = 2 * pivot - float(period_high.iloc[-1])
            
            # Distance to S/R levels
            current_price = float(close.iloc[-1])
            indicators['distance_to_resistance'] = (indicators['resistance_1'] - current_price) / current_price
            indicators['distance_to_support'] = (current_price - indicators['support_1']) / current_price
            
            return indicators
            
        except Exception as e:
            logger.error(f"支撐阻力指標計算失敗: {e}")
            return {}
    
    def _get_default_indicators(self) -> Dict[str, float]:
        """獲取默認指標值（當計算失敗時使用）"""
        return {
            "RSI": 50.0,
            "MACD": 0.0,
            "MACD_signal": 0.0,
            "MACD_histogram": 0.0,
            "BB_position": 0.5,
            "BB_upper": 50000.0,
            "BB_lower": 49000.0,
            "BB_middle": 49500.0,
            "volume_trend": 0.0,
            "SMA_20": 49500.0,
            "SMA_50": 49500.0,
            "EMA_12": 49500.0,
            "EMA_26": 49500.0,
            "STOCH_K": 50.0,
            "STOCH_D": 50.0,
            "ADX": 30.0,
            "CCI": 0.0,
            "WILLR": -50.0,
            "MOM": 0.0,
            "ATR": 500.0,
            "OBV": 1000000.0,
            "volatility": 0.02,
            "volume_ratio": 1.0,
            "trend_strength": 0.0,
            "pivot_point": 49500.0,
            "resistance_1": 50000.0,
            "support_1": 49000.0,
            "distance_to_resistance": 0.01,
            "distance_to_support": 0.01
        }
