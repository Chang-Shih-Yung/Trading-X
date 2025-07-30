"""
即時技術指標分析服務
提供即時計算技術指標、多維度分析、信號生成等功能
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import asyncio
import logging
from enum import Enum

from app.services.market_data import MarketDataService
from app.services.enhanced_data_storage import EnhancedDataStorage

logger = logging.getLogger(__name__)

class SignalStrength(Enum):
    """信號強度枚舉"""
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

@dataclass
class TechnicalIndicatorResult:
    """技術指標結果"""
    indicator_name: str
    current_value: float
    previous_value: Optional[float]
    signal: str  # 'buy', 'sell', 'hold'
    strength: SignalStrength
    confidence: float
    additional_data: Dict[str, Any]
    timestamp: datetime

@dataclass
class MultiTimeframeAnalysis:
    """多時間框架分析結果"""
    symbol: str
    timeframes: Dict[str, Dict[str, Any]]  # {timeframe: {indicator: result}}
    overall_signal: str
    overall_confidence: float
    consensus_indicators: List[str]
    divergent_indicators: List[str]
    timestamp: datetime

@dataclass
class RealTimeIndicatorUpdate:
    """即時指標更新"""
    symbol: str
    timeframe: str
    indicators: Dict[str, TechnicalIndicatorResult]
    price_change: float
    volume_change: float
    market_sentiment: str
    timestamp: datetime

class RealTimeTechnicalAnalysis:
    """即時技術分析服務"""
    
    def __init__(self, market_service: MarketDataService):
        self.market_service = market_service
        self.data_storage = EnhancedDataStorage()
        self.indicator_cache = {}  # 指標快取
        self.update_intervals = {  # 不同時間框架的更新間隔
            '1m': 30,   # 30秒
            '5m': 60,   # 1分鐘
            '15m': 300, # 5分鐘
            '1h': 900,  # 15分鐘
            '4h': 3600, # 1小時
            '1d': 7200  # 2小時
        }
        self.running_tasks = {}
        
    async def start_realtime_analysis(self, symbols: List[str], timeframes: List[str]):
        """啟動即時技術分析"""
        for symbol in symbols:
            for timeframe in timeframes:
                task_key = f"{symbol}_{timeframe}"
                if task_key not in self.running_tasks:
                    task = asyncio.create_task(
                        self._continuous_indicator_update(symbol, timeframe)
                    )
                    self.running_tasks[task_key] = task
                    
        logger.info(f"啟動即時技術分析: {symbols} x {timeframes}")
    
    async def stop_realtime_analysis(self):
        """停止即時技術分析"""
        for task_key, task in self.running_tasks.items():
            task.cancel()
            
        self.running_tasks.clear()
        logger.info("已停止所有即時技術分析任務")
    
    async def _continuous_indicator_update(self, symbol: str, timeframe: str):
        """持續更新指標"""
        update_interval = self.update_intervals.get(timeframe, 300)
        
        while True:
            try:
                # 獲取最新數據
                df = await self.market_service.get_kline_data(
                    symbol=symbol,
                    interval=timeframe,
                    limit=200  # 足夠的歷史數據用於指標計算
                )
                
                if df is not None and len(df) > 50:  # 確保有足夠數據
                    # 計算所有技術指標
                    indicators = await self._calculate_all_indicators(df, symbol, timeframe)
                    
                    # 更新快取
                    cache_key = f"{symbol}_{timeframe}"
                    self.indicator_cache[cache_key] = {
                        'indicators': indicators,
                        'timestamp': datetime.now(),
                        'data_points': len(df)
                    }
                    
                    # 檢查信號變化並發送通知
                    await self._check_signal_changes(symbol, timeframe, indicators)
                
                await asyncio.sleep(update_interval)
                
            except Exception as e:
                logger.error(f"更新 {symbol} {timeframe} 指標失敗: {e}")
                await asyncio.sleep(60)  # 錯誤時等待更長時間
    
    async def _calculate_all_indicators(
        self, 
        df: pd.DataFrame, 
        symbol: str, 
        timeframe: str
    ) -> Dict[str, TechnicalIndicatorResult]:
        """計算所有技術指標"""
        indicators = {}
        
        try:
            # 確保數據格式正確
            if 'close' not in df.columns:
                logger.warning(f"{symbol} 數據缺少 close 列")
                return indicators
            
            current_price = df['close'].iloc[-1]
            previous_price = df['close'].iloc[-2] if len(df) > 1 else current_price
            
            # 1. 移動平均線 (MA)
            ma_results = await self._calculate_moving_averages(df)
            indicators.update(ma_results)
            
            # 2. RSI
            rsi_result = await self._calculate_rsi(df)
            if rsi_result:
                indicators['RSI'] = rsi_result
            
            # 3. MACD
            macd_result = await self._calculate_macd(df)
            if macd_result:
                indicators['MACD'] = macd_result
            
            # 4. 布林帶
            bb_result = await self._calculate_bollinger_bands(df)
            if bb_result:
                indicators['BB'] = bb_result
            
            # 5. 隨機指標 (Stochastic)
            stoch_result = await self._calculate_stochastic(df)
            if stoch_result:
                indicators['STOCH'] = stoch_result
            
            # 6. 威廉指標 (Williams %R)
            wr_result = await self._calculate_williams_r(df)
            if wr_result:
                indicators['WR'] = wr_result
            
            # 7. CCI (商品通道指數)
            cci_result = await self._calculate_cci(df)
            if cci_result:
                indicators['CCI'] = cci_result
            
            # 8. ATR (真實波動範圍)
            atr_result = await self._calculate_atr(df)
            if atr_result:
                indicators['ATR'] = atr_result
            
            # 9. 成交量指標
            volume_result = await self._calculate_volume_indicators(df)
            if volume_result:
                indicators['VOLUME'] = volume_result
            
            # 10. 支撐阻力位
            sr_result = await self._calculate_support_resistance(df)
            if sr_result:
                indicators['SR'] = sr_result
                
        except Exception as e:
            logger.error(f"計算指標失敗 {symbol} {timeframe}: {e}")
        
        return indicators
    
    async def _calculate_moving_averages(self, df: pd.DataFrame) -> Dict[str, TechnicalIndicatorResult]:
        """計算移動平均線"""
        results = {}
        
        try:
            # 計算不同週期的 MA
            periods = [7, 14, 21, 50, 100, 200]
            current_price = df['close'].iloc[-1]
            
            for period in periods:
                if len(df) >= period:
                    ma = ta.sma(df['close'], length=period)
                    if ma is not None and not ma.empty:
                        current_ma = ma.iloc[-1]
                        previous_ma = ma.iloc[-2] if len(ma) > 1 else current_ma
                        
                        # 判斷信號
                        if current_price > current_ma:
                            signal = "buy" if current_price > previous_ma else "hold"
                        else:
                            signal = "sell" if current_price < previous_ma else "hold"
                        
                        # 計算信號強度
                        price_distance = abs(current_price - current_ma) / current_ma
                        
                        if price_distance > 0.05:
                            strength = SignalStrength.STRONG
                        elif price_distance > 0.02:
                            strength = SignalStrength.MODERATE
                        else:
                            strength = SignalStrength.WEAK
                        
                        results[f'MA{period}'] = TechnicalIndicatorResult(
                            indicator_name=f'MA{period}',
                            current_value=current_ma,
                            previous_value=previous_ma,
                            signal=signal,
                            strength=strength,
                            confidence=min(0.95, 0.5 + price_distance * 10),
                            additional_data={
                                'period': period,
                                'price_distance_pct': price_distance * 100,
                                'trend': 'up' if current_ma > previous_ma else 'down'
                            },
                            timestamp=datetime.now()
                        )
                        
        except Exception as e:
            logger.error(f"計算移動平均線失敗: {e}")
        
        return results
    
    async def _calculate_rsi(self, df: pd.DataFrame) -> Optional[TechnicalIndicatorResult]:
        """計算 RSI"""
        try:
            rsi = ta.rsi(df['close'], length=14)
            if rsi is None or rsi.empty:
                return None
            
            current_rsi = rsi.iloc[-1]
            previous_rsi = rsi.iloc[-2] if len(rsi) > 1 else current_rsi
            
            # RSI 信號判斷
            if current_rsi > 70:
                signal = "sell"
                strength = SignalStrength.STRONG if current_rsi > 80 else SignalStrength.MODERATE
            elif current_rsi < 30:
                signal = "buy"
                strength = SignalStrength.STRONG if current_rsi < 20 else SignalStrength.MODERATE
            else:
                signal = "hold"
                strength = SignalStrength.WEAK
            
            # 信心度基於 RSI 極值程度
            if current_rsi > 80 or current_rsi < 20:
                confidence = 0.9
            elif current_rsi > 70 or current_rsi < 30:
                confidence = 0.7
            else:
                confidence = 0.4
            
            return TechnicalIndicatorResult(
                indicator_name='RSI',
                current_value=current_rsi,
                previous_value=previous_rsi,
                signal=signal,
                strength=strength,
                confidence=confidence,
                additional_data={
                    'oversold': current_rsi < 30,
                    'overbought': current_rsi > 70,
                    'divergence': None  # 可以後續添加背離檢測
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"計算 RSI 失敗: {e}")
            return None
    
    async def _calculate_macd(self, df: pd.DataFrame) -> Optional[TechnicalIndicatorResult]:
        """計算 MACD"""
        try:
            macd_data = ta.macd(df['close'], fast=12, slow=26, signal=9)
            if macd_data is None or macd_data.empty:
                return None
            
            macd_line = macd_data.iloc[:, 0]  # MACD line
            signal_line = macd_data.iloc[:, 1]  # Signal line
            histogram = macd_data.iloc[:, 2]  # Histogram
            
            current_macd = macd_line.iloc[-1]
            current_signal = signal_line.iloc[-1]
            current_hist = histogram.iloc[-1]
            
            previous_macd = macd_line.iloc[-2] if len(macd_line) > 1 else current_macd
            previous_signal = signal_line.iloc[-2] if len(signal_line) > 1 else current_signal
            previous_hist = histogram.iloc[-2] if len(histogram) > 1 else current_hist
            
            # MACD 信號判斷
            if current_macd > current_signal and previous_macd <= previous_signal:
                signal = "buy"  # 金叉
                strength = SignalStrength.STRONG
                confidence = 0.8
            elif current_macd < current_signal and previous_macd >= previous_signal:
                signal = "sell"  # 死叉
                strength = SignalStrength.STRONG
                confidence = 0.8
            elif current_hist > 0 and current_hist > previous_hist:
                signal = "buy"  # 直方圖上升
                strength = SignalStrength.MODERATE
                confidence = 0.6
            elif current_hist < 0 and current_hist < previous_hist:
                signal = "sell"  # 直方圖下降
                strength = SignalStrength.MODERATE
                confidence = 0.6
            else:
                signal = "hold"
                strength = SignalStrength.WEAK
                confidence = 0.4
            
            return TechnicalIndicatorResult(
                indicator_name='MACD',
                current_value=current_macd,
                previous_value=previous_macd,
                signal=signal,
                strength=strength,
                confidence=confidence,
                additional_data={
                    'macd_line': current_macd,
                    'signal_line': current_signal,
                    'histogram': current_hist,
                    'golden_cross': current_macd > current_signal and previous_macd <= previous_signal,
                    'death_cross': current_macd < current_signal and previous_macd >= previous_signal
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"計算 MACD 失敗: {e}")
            return None
    
    async def _calculate_bollinger_bands(self, df: pd.DataFrame) -> Optional[TechnicalIndicatorResult]:
        """計算布林帶"""
        try:
            bb = ta.bbands(df['close'], length=20, std=2)
            if bb is None or bb.empty:
                return None
            
            upper_band = bb.iloc[:, 0]  # Upper band
            middle_band = bb.iloc[:, 1]  # Middle band (SMA)
            lower_band = bb.iloc[:, 2]  # Lower band
            
            current_price = df['close'].iloc[-1]
            current_upper = upper_band.iloc[-1]
            current_middle = middle_band.iloc[-1]
            current_lower = lower_band.iloc[-1]
            
            # 布林帶信號判斷
            bb_width = (current_upper - current_lower) / current_middle
            
            if current_price > current_upper:
                signal = "sell"  # 價格突破上軌
                strength = SignalStrength.MODERATE
            elif current_price < current_lower:
                signal = "buy"  # 價格跌破下軌
                strength = SignalStrength.MODERATE
            elif current_price > current_middle:
                signal = "hold"  # 價格在中軌上方
                strength = SignalStrength.WEAK
            else:
                signal = "hold"  # 價格在中軌下方
                strength = SignalStrength.WEAK
            
            # 信心度基於價格距離軌道的程度
            distance_from_middle = abs(current_price - current_middle) / current_middle
            confidence = min(0.9, 0.4 + distance_from_middle * 10)
            
            return TechnicalIndicatorResult(
                indicator_name='BB',
                current_value=current_middle,
                previous_value=middle_band.iloc[-2] if len(middle_band) > 1 else current_middle,
                signal=signal,
                strength=strength,
                confidence=confidence,
                additional_data={
                    'upper_band': current_upper,
                    'middle_band': current_middle,
                    'lower_band': current_lower,
                    'bb_width': bb_width,
                    'price_position': (current_price - current_lower) / (current_upper - current_lower),
                    'squeeze': bb_width < 0.1  # 布林帶收縮
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"計算布林帶失敗: {e}")
            return None
    
    async def _calculate_stochastic(self, df: pd.DataFrame) -> Optional[TechnicalIndicatorResult]:
        """計算隨機指標"""
        try:
            stoch = ta.stoch(df['high'], df['low'], df['close'], k=14, d=3)
            if stoch is None or stoch.empty:
                return None
            
            k_percent = stoch.iloc[:, 0]  # %K
            d_percent = stoch.iloc[:, 1]  # %D
            
            current_k = k_percent.iloc[-1]
            current_d = d_percent.iloc[-1]
            previous_k = k_percent.iloc[-2] if len(k_percent) > 1 else current_k
            previous_d = d_percent.iloc[-2] if len(d_percent) > 1 else current_d
            
            # 隨機指標信號判斷
            if current_k > 80 and current_d > 80:
                signal = "sell"  # 超買
                strength = SignalStrength.MODERATE
            elif current_k < 20 and current_d < 20:
                signal = "buy"  # 超賣
                strength = SignalStrength.MODERATE
            elif current_k > current_d and previous_k <= previous_d:
                signal = "buy"  # %K 穿越 %D 向上
                strength = SignalStrength.STRONG
            elif current_k < current_d and previous_k >= previous_d:
                signal = "sell"  # %K 穿越 %D 向下
                strength = SignalStrength.STRONG
            else:
                signal = "hold"
                strength = SignalStrength.WEAK
            
            confidence = 0.7 if (current_k > 80 or current_k < 20) else 0.5
            
            return TechnicalIndicatorResult(
                indicator_name='STOCH',
                current_value=current_k,
                previous_value=previous_k,
                signal=signal,
                strength=strength,
                confidence=confidence,
                additional_data={
                    'k_percent': current_k,
                    'd_percent': current_d,
                    'overbought': current_k > 80,
                    'oversold': current_k < 20
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"計算隨機指標失敗: {e}")
            return None
    
    async def _calculate_williams_r(self, df: pd.DataFrame) -> Optional[TechnicalIndicatorResult]:
        """計算威廉指標"""
        try:
            wr = ta.willr(df['high'], df['low'], df['close'], length=14)
            if wr is None or wr.empty:
                return None
            
            current_wr = wr.iloc[-1]
            previous_wr = wr.iloc[-2] if len(wr) > 1 else current_wr
            
            # 威廉指標信號判斷
            if current_wr > -20:
                signal = "sell"  # 超買
                strength = SignalStrength.MODERATE
                confidence = 0.7
            elif current_wr < -80:
                signal = "buy"  # 超賣
                strength = SignalStrength.MODERATE
                confidence = 0.7
            else:
                signal = "hold"
                strength = SignalStrength.WEAK
                confidence = 0.4
            
            return TechnicalIndicatorResult(
                indicator_name='WR',
                current_value=current_wr,
                previous_value=previous_wr,
                signal=signal,
                strength=strength,
                confidence=confidence,
                additional_data={
                    'overbought': current_wr > -20,
                    'oversold': current_wr < -80,
                    'trend': 'up' if current_wr > previous_wr else 'down'
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"計算威廉指標失敗: {e}")
            return None
    
    async def _calculate_cci(self, df: pd.DataFrame) -> Optional[TechnicalIndicatorResult]:
        """計算商品通道指數"""
        try:
            cci = ta.cci(df['high'], df['low'], df['close'], length=20)
            if cci is None or cci.empty:
                return None
            
            current_cci = cci.iloc[-1]
            previous_cci = cci.iloc[-2] if len(cci) > 1 else current_cci
            
            # CCI 信號判斷
            if current_cci > 100:
                signal = "sell" if current_cci > 200 else "hold"
                strength = SignalStrength.STRONG if current_cci > 200 else SignalStrength.MODERATE
            elif current_cci < -100:
                signal = "buy" if current_cci < -200 else "hold"
                strength = SignalStrength.STRONG if current_cci < -200 else SignalStrength.MODERATE
            else:
                signal = "hold"
                strength = SignalStrength.WEAK
            
            confidence = min(0.9, abs(current_cci) / 300)
            
            return TechnicalIndicatorResult(
                indicator_name='CCI',
                current_value=current_cci,
                previous_value=previous_cci,
                signal=signal,
                strength=strength,
                confidence=confidence,
                additional_data={
                    'extreme_overbought': current_cci > 200,
                    'extreme_oversold': current_cci < -200,
                    'normal_range': -100 <= current_cci <= 100
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"計算 CCI 失敗: {e}")
            return None
    
    async def _calculate_atr(self, df: pd.DataFrame) -> Optional[TechnicalIndicatorResult]:
        """計算真實波動範圍"""
        try:
            atr = ta.atr(df['high'], df['low'], df['close'], length=14)
            if atr is None or atr.empty:
                return None
            
            current_atr = atr.iloc[-1]
            previous_atr = atr.iloc[-2] if len(atr) > 1 else current_atr
            current_price = df['close'].iloc[-1]
            
            # ATR 相對於價格的百分比
            atr_percent = (current_atr / current_price) * 100
            
            # ATR 趨勢判斷
            if current_atr > previous_atr * 1.2:
                signal = "high_volatility"
                strength = SignalStrength.STRONG
            elif current_atr < previous_atr * 0.8:
                signal = "low_volatility"
                strength = SignalStrength.MODERATE
            else:
                signal = "normal_volatility"
                strength = SignalStrength.WEAK
            
            return TechnicalIndicatorResult(
                indicator_name='ATR',
                current_value=current_atr,
                previous_value=previous_atr,
                signal=signal,
                strength=strength,
                confidence=0.8,
                additional_data={
                    'atr_percent': atr_percent,
                    'volatility_trend': 'increasing' if current_atr > previous_atr else 'decreasing',
                    'support_level': current_price - current_atr,
                    'resistance_level': current_price + current_atr
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"計算 ATR 失敗: {e}")
            return None
    
    async def _calculate_volume_indicators(self, df: pd.DataFrame) -> Optional[TechnicalIndicatorResult]:
        """計算成交量指標"""
        try:
            if 'volume' not in df.columns:
                return None
            
            # 成交量移動平均
            volume_ma = ta.sma(df['volume'], length=20)
            current_volume = df['volume'].iloc[-1]
            avg_volume = volume_ma.iloc[-1] if volume_ma is not None and not volume_ma.empty else current_volume
            
            # 成交量比率
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # OBV (On Balance Volume)
            obv = ta.obv(df['close'], df['volume'])
            current_obv = obv.iloc[-1] if obv is not None and not obv.empty else 0
            previous_obv = obv.iloc[-2] if obv is not None and len(obv) > 1 else current_obv
            
            # 信號判斷
            if volume_ratio > 2:
                signal = "high_volume"
                strength = SignalStrength.STRONG
            elif volume_ratio > 1.5:
                signal = "above_average_volume"
                strength = SignalStrength.MODERATE
            elif volume_ratio < 0.5:
                signal = "low_volume"
                strength = SignalStrength.WEAK
            else:
                signal = "normal_volume"
                strength = SignalStrength.WEAK
            
            confidence = min(0.9, abs(volume_ratio - 1) + 0.3)
            
            return TechnicalIndicatorResult(
                indicator_name='VOLUME',
                current_value=current_volume,
                previous_value=df['volume'].iloc[-2] if len(df) > 1 else current_volume,
                signal=signal,
                strength=strength,
                confidence=confidence,
                additional_data={
                    'volume_ratio': volume_ratio,
                    'avg_volume': avg_volume,
                    'obv': current_obv,
                    'obv_trend': 'up' if current_obv > previous_obv else 'down',
                    'volume_surge': volume_ratio > 3
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"計算成交量指標失敗: {e}")
            return None
    
    async def _calculate_support_resistance(self, df: pd.DataFrame) -> Optional[TechnicalIndicatorResult]:
        """計算支撐阻力位"""
        try:
            current_price = df['close'].iloc[-1]
            
            # 使用最近50個數據點來計算支撐阻力
            recent_data = df.tail(50)
            
            # 尋找局部高點和低點
            highs = []
            lows = []
            
            for i in range(2, len(recent_data) - 2):
                # 局部高點
                if (recent_data['high'].iloc[i] > recent_data['high'].iloc[i-1] and 
                    recent_data['high'].iloc[i] > recent_data['high'].iloc[i+1] and
                    recent_data['high'].iloc[i] > recent_data['high'].iloc[i-2] and 
                    recent_data['high'].iloc[i] > recent_data['high'].iloc[i+2]):
                    highs.append(recent_data['high'].iloc[i])
                
                # 局部低點
                if (recent_data['low'].iloc[i] < recent_data['low'].iloc[i-1] and 
                    recent_data['low'].iloc[i] < recent_data['low'].iloc[i+1] and
                    recent_data['low'].iloc[i] < recent_data['low'].iloc[i-2] and 
                    recent_data['low'].iloc[i] < recent_data['low'].iloc[i+2]):
                    lows.append(recent_data['low'].iloc[i])
            
            # 找最近的支撐和阻力位
            resistance_levels = [h for h in highs if h > current_price]
            support_levels = [l for l in lows if l < current_price]
            
            nearest_resistance = min(resistance_levels) if resistance_levels else None
            nearest_support = max(support_levels) if support_levels else None
            
            # 信號判斷
            if nearest_resistance and current_price > nearest_resistance * 0.99:
                signal = "near_resistance"
                strength = SignalStrength.MODERATE
            elif nearest_support and current_price < nearest_support * 1.01:
                signal = "near_support"
                strength = SignalStrength.MODERATE
            else:
                signal = "neutral"
                strength = SignalStrength.WEAK
            
            return TechnicalIndicatorResult(
                indicator_name='SR',
                current_value=current_price,
                previous_value=df['close'].iloc[-2] if len(df) > 1 else current_price,
                signal=signal,
                strength=strength,
                confidence=0.6,
                additional_data={
                    'nearest_resistance': nearest_resistance,
                    'nearest_support': nearest_support,
                    'all_resistance_levels': resistance_levels[:5],  # 前5個
                    'all_support_levels': support_levels[:5],  # 前5個
                    'resistance_distance': ((nearest_resistance - current_price) / current_price * 100) if nearest_resistance else None,
                    'support_distance': ((current_price - nearest_support) / current_price * 100) if nearest_support else None
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"計算支撐阻力失敗: {e}")
            return None
    
    async def _check_signal_changes(
        self, 
        symbol: str, 
        timeframe: str, 
        current_indicators: Dict[str, TechnicalIndicatorResult]
    ):
        """檢查信號變化並發送通知"""
        try:
            cache_key = f"{symbol}_{timeframe}"
            previous_cache = self.indicator_cache.get(cache_key, {})
            previous_indicators = previous_cache.get('indicators', {})
            
            significant_changes = []
            
            for indicator_name, current_result in current_indicators.items():
                if indicator_name in previous_indicators:
                    previous_result = previous_indicators[indicator_name]
                    
                    # 檢查信號變化
                    if (current_result.signal != previous_result.signal and 
                        current_result.strength in [SignalStrength.STRONG, SignalStrength.VERY_STRONG]):
                        
                        significant_changes.append({
                            'indicator': indicator_name,
                            'previous_signal': previous_result.signal,
                            'current_signal': current_result.signal,
                            'strength': current_result.strength.value,
                            'confidence': current_result.confidence
                        })
            
            # 如果有重要信號變化，記錄並可以發送通知
            if significant_changes:
                logger.info(f"[信號變化] {symbol} {timeframe}: {significant_changes}")
                
                # 這裡可以添加通知機制，例如 WebSocket 推送、郵件、Telegram 等
                
        except Exception as e:
            logger.error(f"檢查信號變化失敗: {e}")
    
    async def get_multi_timeframe_analysis(
        self, 
        symbol: str, 
        timeframes: List[str] = None
    ) -> MultiTimeframeAnalysis:
        """獲取多時間框架分析"""
        if timeframes is None:
            timeframes = ['1m', '5m', '15m', '1h', '4h']
        
        timeframe_results = {}
        all_signals = []
        
        for tf in timeframes:
            cache_key = f"{symbol}_{tf}"
            cached_data = self.indicator_cache.get(cache_key, {})
            
            if cached_data and 'indicators' in cached_data:
                indicators = cached_data['indicators']
                
                # 彙總該時間框架的信號
                tf_signals = {
                    'buy': 0,
                    'sell': 0,
                    'hold': 0
                }
                
                tf_confidence = 0
                indicator_count = 0
                
                for indicator_name, result in indicators.items():
                    tf_signals[result.signal] += 1
                    tf_confidence += result.confidence
                    indicator_count += 1
                    all_signals.append(result.signal)
                
                timeframe_results[tf] = {
                    'signals': tf_signals,
                    'avg_confidence': tf_confidence / indicator_count if indicator_count > 0 else 0,
                    'dominant_signal': max(tf_signals, key=tf_signals.get),
                    'indicator_count': indicator_count,
                    'last_update': cached_data.get('timestamp')
                }
        
        # 計算整體信號
        signal_counts = {'buy': 0, 'sell': 0, 'hold': 0}
        for signal in all_signals:
            signal_counts[signal] += 1
        
        overall_signal = max(signal_counts, key=signal_counts.get)
        
        # 計算共識和分歧指標
        consensus_indicators = []
        divergent_indicators = []
        
        # 計算整體信心度
        total_confidence = sum([tf['avg_confidence'] for tf in timeframe_results.values()])
        overall_confidence = total_confidence / len(timeframe_results) if timeframe_results else 0
        
        return MultiTimeframeAnalysis(
            symbol=symbol,
            timeframes=timeframe_results,
            overall_signal=overall_signal,
            overall_confidence=overall_confidence,
            consensus_indicators=consensus_indicators,
            divergent_indicators=divergent_indicators,
            timestamp=datetime.now()
        )
    
    async def get_current_indicators(
        self, 
        symbol: str, 
        timeframe: str
    ) -> Optional[Dict[str, TechnicalIndicatorResult]]:
        """獲取當前快取的指標數據"""
        cache_key = f"{symbol}_{timeframe}"
        cached_data = self.indicator_cache.get(cache_key, {})
        return cached_data.get('indicators')
    
    def get_analysis_status(self) -> Dict[str, Any]:
        """獲取分析狀態"""
        return {
            'running_tasks': len(self.running_tasks),
            'active_analyses': list(self.running_tasks.keys()),
            'cached_results': len(self.indicator_cache),
            'update_intervals': self.update_intervals,
            'last_updates': {
                key: data.get('timestamp', 'Unknown') 
                for key, data in self.indicator_cache.items()
            }
        }
