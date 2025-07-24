"""
短線交易（Scalping）專用策略引擎
專注於1-30分鐘的快速交易策略
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)

class ScalpingSignalType(Enum):
    """短線信號類型"""
    SCALP_LONG = "SCALP_LONG"
    SCALP_SHORT = "SCALP_SHORT"
    QUICK_EXIT = "QUICK_EXIT"
    MOMENTUM_BREAKOUT = "MOMENTUM_BREAKOUT"
    MEAN_REVERSION = "MEAN_REVERSION"

@dataclass
class ScalpingSignal:
    """短線交易信號"""
    symbol: str
    timeframe: str
    signal_type: ScalpingSignalType
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    urgency_level: str  # urgent, high, medium
    strategy_name: str
    indicators: Dict
    created_at: datetime
    expires_in_minutes: int
    risk_reward_ratio: float

class ScalpingStrategyEngine:
    """短線交易策略引擎"""
    
    def __init__(self):
        self.strategies = {
            'ema_crossover': self._ema_crossover_strategy,
            'rsi_divergence': self._rsi_divergence_strategy,
            'bollinger_squeeze': self._bollinger_squeeze_strategy,
            'volume_breakout': self._volume_breakout_strategy,
            'momentum_scalp': self._momentum_scalp_strategy,
            'support_resistance': self._support_resistance_strategy,
            'macd_quick': self._macd_quick_strategy,
            'stochastic_cross': self._stochastic_cross_strategy
        }
    
    async def generate_scalping_signals(self, symbol: str, timeframes: List[str] = None) -> List[ScalpingSignal]:
        """生成短線交易信號"""
        if timeframes is None:
            timeframes = ['1m', '3m', '5m', '15m', '30m']
        
        signals = []
        
        try:
            for timeframe in timeframes:
                # 獲取市場數據
                df = await self._get_market_data(symbol, timeframe, limit=100)
                if df is None or len(df) < 50:
                    continue
                
                # 執行各種短線策略
                for strategy_name, strategy_func in self.strategies.items():
                    try:
                        strategy_signals = await strategy_func(df, symbol, timeframe)
                        if strategy_signals:
                            signals.extend(strategy_signals)
                    except Exception as e:
                        logger.error(f"策略 {strategy_name} 執行失敗: {e}")
                        continue
            
            # 對信號進行篩選和排序
            signals = self._filter_and_rank_signals(signals)
            
        except Exception as e:
            logger.error(f"生成短線信號失敗: {e}")
        
        return signals[:15]  # 返回前15個最佳信號
    
    async def _ema_crossover_strategy(self, df: pd.DataFrame, symbol: str, timeframe: str) -> List[ScalpingSignal]:
        """EMA 快速交叉策略 - 適合短線"""
        signals = []
        
        # 短期EMA (5, 8, 13)
        ema5 = ta.ema(df['close'], length=5)
        ema8 = ta.ema(df['close'], length=8)
        ema13 = ta.ema(df['close'], length=13)
        
        if len(ema5) < 3 or len(ema8) < 3 or len(ema13) < 3:
            return signals
        
        current_price = df['close'].iloc[-1]
        
        # 多重EMA對齊檢查
        ema5_current = ema5.iloc[-1]
        ema8_current = ema8.iloc[-1]
        ema13_current = ema13.iloc[-1]
        
        # 多頭信號：EMA5 > EMA8 > EMA13 且價格突破EMA5
        if (ema5_current > ema8_current > ema13_current and 
            current_price > ema5_current and 
            df['close'].iloc[-2] <= ema5.iloc[-2]):
            
            confidence = self._calculate_ema_confidence(ema5, ema8, ema13, df['volume'])
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.SCALP_LONG,
                entry_price=current_price,
                stop_loss=current_price - (current_price - ema13_current) * 0.5,
                take_profit=current_price + (current_price - ema13_current) * 1.5,
                confidence=confidence,
                urgency_level='high' if confidence > 0.75 else 'medium',
                strategy_name='EMA快速交叉',
                indicators={
                    'ema5': ema5_current,
                    'ema8': ema8_current,
                    'ema13': ema13_current
                },
                created_at=datetime.now(),
                expires_in_minutes=self._get_expiry_minutes(timeframe),
                risk_reward_ratio=3.0
            )
            signals.append(signal)
        
        # 空頭信號：EMA5 < EMA8 < EMA13 且價格跌破EMA5
        elif (ema5_current < ema8_current < ema13_current and 
              current_price < ema5_current and 
              df['close'].iloc[-2] >= ema5.iloc[-2]):
            
            confidence = self._calculate_ema_confidence(ema5, ema8, ema13, df['volume'])
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.SCALP_SHORT,
                entry_price=current_price,
                stop_loss=current_price + (ema13_current - current_price) * 0.5,
                take_profit=current_price - (ema13_current - current_price) * 1.5,
                confidence=confidence,
                urgency_level='high' if confidence > 0.75 else 'medium',
                strategy_name='EMA快速交叉',
                indicators={
                    'ema5': ema5_current,
                    'ema8': ema8_current,
                    'ema13': ema13_current
                },
                created_at=datetime.now(),
                expires_in_minutes=self._get_expiry_minutes(timeframe),
                risk_reward_ratio=3.0
            )
            signals.append(signal)
        
        return signals
    
    async def _rsi_divergence_strategy(self, df: pd.DataFrame, symbol: str, timeframe: str) -> List[ScalpingSignal]:
        """RSI 背離策略 - 短線反轉"""
        signals = []
        
        # 快速RSI (期間較短)
        rsi = ta.rsi(df['close'], length=7)  # 7期RSI更敏感
        
        if len(rsi) < 10:
            return signals
        
        current_price = df['close'].iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        # 超買反轉 (RSI > 75)
        if current_rsi > 75 and rsi.iloc[-2] > rsi.iloc[-1]:
            confidence = min(0.9, (current_rsi - 75) / 20 + 0.6)
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.MEAN_REVERSION,
                entry_price=current_price,
                stop_loss=current_price * 1.015,  # 1.5% 止損
                take_profit=current_price * 0.985,  # 1.5% 止盈
                confidence=confidence,
                urgency_level='urgent' if current_rsi > 85 else 'high',
                strategy_name='RSI超買反轉',
                indicators={'rsi': current_rsi},
                created_at=datetime.now(),
                expires_in_minutes=self._get_expiry_minutes(timeframe) // 2,  # 更短的有效期
                risk_reward_ratio=1.0
            )
            signals.append(signal)
        
        # 超賣反轉 (RSI < 25)
        elif current_rsi < 25 and rsi.iloc[-2] < rsi.iloc[-1]:
            confidence = min(0.9, (25 - current_rsi) / 20 + 0.6)
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.MEAN_REVERSION,
                entry_price=current_price,
                stop_loss=current_price * 0.985,  # 1.5% 止損
                take_profit=current_price * 1.015,  # 1.5% 止盈
                confidence=confidence,
                urgency_level='urgent' if current_rsi < 15 else 'high',
                strategy_name='RSI超賣反轉',
                indicators={'rsi': current_rsi},
                created_at=datetime.now(),
                expires_in_minutes=self._get_expiry_minutes(timeframe) // 2,
                risk_reward_ratio=1.0
            )
            signals.append(signal)
        
        return signals
    
    async def _bollinger_squeeze_strategy(self, df: pd.DataFrame, symbol: str, timeframe: str) -> List[ScalpingSignal]:
        """布林通道擠壓突破策略"""
        signals = []
        
        # 布林通道 (20期, 2標準差)
        bb = ta.bbands(df['close'], length=20, std=2)
        
        if bb is None or len(bb) < 5:
            return signals
        
        current_price = df['close'].iloc[-1]
        upper_band = bb['BBU_20_2.0'].iloc[-1]
        lower_band = bb['BBL_20_2.0'].iloc[-1]
        middle_band = bb['BBM_20_2.0'].iloc[-1]
        
        # 計算通道寬度
        band_width = (upper_band - lower_band) / middle_band
        avg_band_width = ((bb['BBU_20_2.0'] - bb['BBL_20_2.0']) / bb['BBM_20_2.0']).rolling(10).mean().iloc[-1]
        
        # 突破上軌
        if (current_price > upper_band and 
            df['close'].iloc[-2] <= bb['BBU_20_2.0'].iloc[-2] and
            band_width > avg_band_width * 1.2):
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.MOMENTUM_BREAKOUT,
                entry_price=current_price,
                stop_loss=middle_band,
                take_profit=current_price + (current_price - middle_band),
                confidence=0.75,
                urgency_level='high',
                strategy_name='布林上軌突破',
                indicators={
                    'upper_band': upper_band,
                    'lower_band': lower_band,
                    'band_width': band_width
                },
                created_at=datetime.now(),
                expires_in_minutes=self._get_expiry_minutes(timeframe),
                risk_reward_ratio=2.0
            )
            signals.append(signal)
        
        # 突破下軌
        elif (current_price < lower_band and 
              df['close'].iloc[-2] >= bb['BBL_20_2.0'].iloc[-2] and
              band_width > avg_band_width * 1.2):
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.MOMENTUM_BREAKOUT,
                entry_price=current_price,
                stop_loss=middle_band,
                take_profit=current_price - (middle_band - current_price),
                confidence=0.75,
                urgency_level='high',
                strategy_name='布林下軌突破',
                indicators={
                    'upper_band': upper_band,
                    'lower_band': lower_band,
                    'band_width': band_width
                },
                created_at=datetime.now(),
                expires_in_minutes=self._get_expiry_minutes(timeframe),
                risk_reward_ratio=2.0
            )
            signals.append(signal)
        
        return signals
    
    async def _volume_breakout_strategy(self, df: pd.DataFrame, symbol: str, timeframe: str) -> List[ScalpingSignal]:
        """成交量突破策略"""
        signals = []
        
        if 'volume' not in df.columns or len(df) < 20:
            return signals
        
        current_price = df['close'].iloc[-1]
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].rolling(20).mean().iloc[-1]
        
        # 價格突破 + 成交量放大
        price_change = (current_price - df['close'].iloc[-2]) / df['close'].iloc[-2]
        volume_ratio = current_volume / avg_volume
        
        # 突破條件：價格變動 > 0.3% 且成交量 > 平均2倍
        if abs(price_change) > 0.003 and volume_ratio > 2.0:
            signal_type = ScalpingSignalType.SCALP_LONG if price_change > 0 else ScalpingSignalType.SCALP_SHORT
            
            if price_change > 0:  # 向上突破
                stop_loss = current_price * 0.995
                take_profit = current_price * 1.01
            else:  # 向下突破
                stop_loss = current_price * 1.005
                take_profit = current_price * 0.99
            
            confidence = min(0.85, volume_ratio / 5 + abs(price_change) * 100)
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=signal_type,
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                urgency_level='urgent' if volume_ratio > 4 else 'high',
                strategy_name='成交量突破',
                indicators={
                    'volume_ratio': volume_ratio,
                    'price_change': price_change
                },
                created_at=datetime.now(),
                expires_in_minutes=self._get_expiry_minutes(timeframe) // 3,  # 很短的有效期
                risk_reward_ratio=2.0
            )
            signals.append(signal)
        
        return signals
    
    async def _momentum_scalp_strategy(self, df: pd.DataFrame, symbol: str, timeframe: str) -> List[ScalpingSignal]:
        """動量短線策略"""
        signals = []
        
        # 計算動量指標
        roc = ta.roc(df['close'], length=5)  # 5期變化率
        ema12 = ta.ema(df['close'], length=12)
        ema26 = ta.ema(df['close'], length=26)
        
        if len(roc) < 3 or len(ema12) < 3:
            return signals
        
        current_price = df['close'].iloc[-1]
        current_roc = roc.iloc[-1]
        
        # 強勢動量多頭
        if (current_roc > 2 and  # ROC > 2%
            df['close'].iloc[-1] > ema12.iloc[-1] > ema26.iloc[-1] and
            df['high'].iloc[-1] == df['high'].rolling(5).max().iloc[-1]):  # 創5期新高
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.MOMENTUM_BREAKOUT,
                entry_price=current_price,
                stop_loss=ema12.iloc[-1],
                take_profit=current_price * 1.02,  # 2% 目標
                confidence=0.8,
                urgency_level='urgent',
                strategy_name='強勢動量多頭',
                indicators={
                    'roc': current_roc,
                    'ema12': ema12.iloc[-1]
                },
                created_at=datetime.now(),
                expires_in_minutes=self._get_expiry_minutes(timeframe) // 2,
                risk_reward_ratio=2.5
            )
            signals.append(signal)
        
        # 強勢動量空頭
        elif (current_roc < -2 and  # ROC < -2%
              df['close'].iloc[-1] < ema12.iloc[-1] < ema26.iloc[-1] and
              df['low'].iloc[-1] == df['low'].rolling(5).min().iloc[-1]):  # 創5期新低
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.MOMENTUM_BREAKOUT,
                entry_price=current_price,
                stop_loss=ema12.iloc[-1],
                take_profit=current_price * 0.98,  # 2% 目標
                confidence=0.8,
                urgency_level='urgent',
                strategy_name='強勢動量空頭',
                indicators={
                    'roc': current_roc,
                    'ema12': ema12.iloc[-1]
                },
                created_at=datetime.now(),
                expires_in_minutes=self._get_expiry_minutes(timeframe) // 2,
                risk_reward_ratio=2.5
            )
            signals.append(signal)
        
        return signals
    
    async def _support_resistance_strategy(self, df: pd.DataFrame, symbol: str, timeframe: str) -> List[ScalpingSignal]:
        """支撐阻力位策略"""
        signals = []
        
        # 計算支撐阻力位
        highs = df['high'].rolling(5).max()
        lows = df['low'].rolling(5).min()
        
        current_price = df['close'].iloc[-1]
        
        # 找到最近的支撐阻力位
        recent_resistance = highs.iloc[-10:-1].max()
        recent_support = lows.iloc[-10:-1].min()
        
        # 突破阻力位
        if (current_price > recent_resistance and 
            df['close'].iloc[-2] <= recent_resistance):
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.SCALP_LONG,
                entry_price=current_price,
                stop_loss=recent_resistance * 0.999,  # 阻力位下方
                take_profit=current_price + (current_price - recent_resistance) * 2,
                confidence=0.7,
                urgency_level='medium',
                strategy_name='阻力位突破',
                indicators={
                    'resistance': recent_resistance,
                    'support': recent_support
                },
                created_at=datetime.now(),
                expires_in_minutes=self._get_expiry_minutes(timeframe),
                risk_reward_ratio=2.0
            )
            signals.append(signal)
        
        # 跌破支撐位
        elif (current_price < recent_support and 
              df['close'].iloc[-2] >= recent_support):
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.SCALP_SHORT,
                entry_price=current_price,
                stop_loss=recent_support * 1.001,  # 支撐位上方
                take_profit=current_price - (recent_support - current_price) * 2,
                confidence=0.7,
                urgency_level='medium',
                strategy_name='支撐位跌破',
                indicators={
                    'resistance': recent_resistance,
                    'support': recent_support
                },
                created_at=datetime.now(),
                expires_in_minutes=self._get_expiry_minutes(timeframe),
                risk_reward_ratio=2.0
            )
            signals.append(signal)
        
        return signals
    
    async def _macd_quick_strategy(self, df: pd.DataFrame, symbol: str, timeframe: str) -> List[ScalpingSignal]:
        """快速MACD策略"""
        signals = []
        
        # 快速MACD (5,13,5)
        macd = ta.macd(df['close'], fast=5, slow=13, signal=5)
        
        if macd is None or len(macd) < 3:
            return signals
        
        current_price = df['close'].iloc[-1]
        macd_line = macd['MACD_5_13_5'].iloc[-1]
        signal_line = macd['MACDs_5_13_5'].iloc[-1]
        histogram = macd['MACDh_5_13_5'].iloc[-1]
        
        prev_histogram = macd['MACDh_5_13_5'].iloc[-2]
        
        # MACD金叉且柱狀圖轉正
        if (macd_line > signal_line and 
            macd['MACD_5_13_5'].iloc[-2] <= macd['MACDs_5_13_5'].iloc[-2] and
            histogram > 0 and prev_histogram <= 0):
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.SCALP_LONG,
                entry_price=current_price,
                stop_loss=current_price * 0.995,
                take_profit=current_price * 1.015,
                confidence=0.75,
                urgency_level='medium',
                strategy_name='MACD快速金叉',
                indicators={
                    'macd': macd_line,
                    'signal': signal_line,
                    'histogram': histogram
                },
                created_at=datetime.now(),
                expires_in_minutes=self._get_expiry_minutes(timeframe),
                risk_reward_ratio=3.0
            )
            signals.append(signal)
        
        # MACD死叉且柱狀圖轉負
        elif (macd_line < signal_line and 
              macd['MACD_5_13_5'].iloc[-2] >= macd['MACDs_5_13_5'].iloc[-2] and
              histogram < 0 and prev_histogram >= 0):
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.SCALP_SHORT,
                entry_price=current_price,
                stop_loss=current_price * 1.005,
                take_profit=current_price * 0.985,
                confidence=0.75,
                urgency_level='medium',
                strategy_name='MACD快速死叉',
                indicators={
                    'macd': macd_line,
                    'signal': signal_line,
                    'histogram': histogram
                },
                created_at=datetime.now(),
                expires_in_minutes=self._get_expiry_minutes(timeframe),
                risk_reward_ratio=3.0
            )
            signals.append(signal)
        
        return signals
    
    async def _stochastic_cross_strategy(self, df: pd.DataFrame, symbol: str, timeframe: str) -> List[ScalpingSignal]:
        """隨機指標交叉策略"""
        signals = []
        
        # 快速隨機指標
        stoch = ta.stoch(df['high'], df['low'], df['close'], k=5, d=3)
        
        if stoch is None or len(stoch) < 3:
            return signals
        
        current_price = df['close'].iloc[-1]
        k_percent = stoch['STOCHk_5_3_3'].iloc[-1]
        d_percent = stoch['STOCHd_5_3_3'].iloc[-1]
        
        prev_k = stoch['STOCHk_5_3_3'].iloc[-2]
        prev_d = stoch['STOCHd_5_3_3'].iloc[-2]
        
        # 超賣區金叉
        if (k_percent < 30 and d_percent < 30 and 
            k_percent > d_percent and prev_k <= prev_d):
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.SCALP_LONG,
                entry_price=current_price,
                stop_loss=current_price * 0.992,
                take_profit=current_price * 1.016,
                confidence=0.65,
                urgency_level='medium',
                strategy_name='隨機指標超賣金叉',
                indicators={
                    'stoch_k': k_percent,
                    'stoch_d': d_percent
                },
                created_at=datetime.now(),
                expires_in_minutes=self._get_expiry_minutes(timeframe),
                risk_reward_ratio=2.0
            )
            signals.append(signal)
        
        # 超買區死叉
        elif (k_percent > 70 and d_percent > 70 and 
              k_percent < d_percent and prev_k >= prev_d):
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.SCALP_SHORT,
                entry_price=current_price,
                stop_loss=current_price * 1.008,
                take_profit=current_price * 0.984,
                confidence=0.65,
                urgency_level='medium',
                strategy_name='隨機指標超買死叉',
                indicators={
                    'stoch_k': k_percent,
                    'stoch_d': d_percent
                },
                created_at=datetime.now(),
                expires_in_minutes=self._get_expiry_minutes(timeframe),
                risk_reward_ratio=2.0
            )
            signals.append(signal)
        
        return signals
    
    def _filter_and_rank_signals(self, signals: List[ScalpingSignal]) -> List[ScalpingSignal]:
        """篩選和排序信號"""
        if not signals:
            return signals
        
        # 按信心度和緊急程度排序
        urgency_weight = {'urgent': 3, 'high': 2, 'medium': 1}
        
        def signal_score(signal):
            urgency_score = urgency_weight.get(signal.urgency_level, 0)
            return signal.confidence * 0.7 + urgency_score * 0.3
        
        sorted_signals = sorted(signals, key=signal_score, reverse=True)
        
        # 去除重複的交易對
        seen_symbols = set()
        filtered_signals = []
        
        for signal in sorted_signals:
            key = f"{signal.symbol}_{signal.timeframe}"
            if key not in seen_symbols:
                seen_symbols.add(key)
                filtered_signals.append(signal)
        
        return filtered_signals
    
    def _calculate_ema_confidence(self, ema5: pd.Series, ema8: pd.Series, ema13: pd.Series, volume: pd.Series) -> float:
        """計算EMA信號信心度"""
        # EMA間距
        ema_separation = abs(ema5.iloc[-1] - ema13.iloc[-1]) / ema13.iloc[-1]
        
        # 成交量確認
        volume_ratio = volume.iloc[-1] / volume.rolling(10).mean().iloc[-1] if len(volume) >= 10 else 1
        
        confidence = min(0.9, 0.5 + ema_separation * 50 + min(0.3, volume_ratio / 5))
        return round(confidence, 3)
    
    def _get_expiry_minutes(self, timeframe: str) -> int:
        """根據時間框架獲取信號有效期"""
        expiry_map = {
            '1m': 5,
            '3m': 10,
            '5m': 15,
            '15m': 30,
            '30m': 60
        }
        return expiry_map.get(timeframe, 15)
    
    async def _get_market_data(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """獲取市場數據 - 簡化版本以避免依賴問題"""
        try:
            # 暫時返回模擬數據結構來測試API端點
            import random
            
            # 生成模擬K線數據
            data = []
            base_price = 50000.0 if symbol == 'BTCUSDT' else 3000.0
            
            for i in range(limit):
                # 模擬價格波動
                price_change = random.uniform(-0.02, 0.02)  # ±2% 波動
                current_price = base_price * (1 + price_change)
                
                high = current_price * (1 + random.uniform(0, 0.01))
                low = current_price * (1 - random.uniform(0, 0.01))
                volume = random.uniform(1000, 10000)
                
                data.append({
                    'timestamp': datetime.now().replace(minute=datetime.now().minute - (limit - i)),
                    'open': current_price,
                    'high': high,
                    'low': low,
                    'close': current_price,
                    'volume': volume
                })
                
                base_price = current_price
            
            df = pd.DataFrame(data)
            df = df.set_index('timestamp')
            
            # 確保數據有足夠的長度用於技術指標計算
            if len(df) >= 50:
                return df
            else:
                logger.warning(f"模擬數據長度不足: {len(df)}")
                return None
                
        except Exception as e:
            logger.error(f"獲取市場數據失敗: {e}")
            return None
