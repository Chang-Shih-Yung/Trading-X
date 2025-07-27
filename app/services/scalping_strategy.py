"""
短線交易（Scalping）專用策略引擎
專注於1-30分鐘的快速交易策略
整合 market_conditions_config.json 配置和智能時間計算
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

from ..utils.time_utils import get_taiwan_now_naive, taiwan_now_minus
from .smart_timing_service import smart_timing_service
import json
import os

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
    timing_details: Optional[Dict] = None  # 智能時間計算詳情

class ScalpingStrategyEngine:
    """短線交易策略引擎 - 整合 JSON 配置"""
    
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
        
        # 加載 JSON 配置
        self._load_config()
    
    def _load_config(self):
        """加載 market_conditions_config.json 配置"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'market_conditions_config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 極短線配置 (ultra_short)
            self.ultra_short_config = config['timeframes']['ultra_short']
            
            # 資產參數配置
            self.asset_parameters = config['custom_parameters']
            
            # 風險管理配置
            self.risk_config = config['risk_management']['timeframe_based_sizing']['ultra_short']
            
            # 市場條件配置
            self.market_conditions = config['market_conditions']
            
            logger.info("JSON 配置加載成功")
            
        except Exception as e:
            logger.warning(f"JSON 配置加載失敗，使用默認參數: {e}")
            # 使用默認參數
            self.ultra_short_config = {
                'risk_management': {
                    'stop_loss_range': [0.01, 0.03],
                    'max_drawdown': 0.02,
                    'position_hold_limit': '4小時',
                    'monitoring_frequency': '每30秒'
                }
            }
            self.asset_parameters = {}
            self.risk_config = {
                'max_per_trade': 0.03,
                'stop_loss_range': [0.01, 0.03]
            }
            self.market_conditions = {}
    
    def get_asset_config(self, symbol: str) -> dict:
        """獲取資產特定配置"""
        # 移除 USDT 後綴來匹配配置
        base_symbol = symbol.replace('USDT', '')
        return self.asset_parameters.get(base_symbol, {
            'volatility_factor': 1.0,
            'entry_padding': 1.0,
            'stop_loss_multiplier': 1.0
        })
    
    def get_stop_loss_range(self, symbol: str, market_condition: str = 'bull') -> tuple:
        """根據資產和市場條件獲取止損範圍"""
        asset_config = self.get_asset_config(symbol)
        base_range = self.ultra_short_config['risk_management']['stop_loss_range']
        
        # 根據資產波動性調整
        volatility_factor = asset_config.get('volatility_factor', 1.0)
        stop_loss_multiplier = asset_config.get('stop_loss_multiplier', 1.0)
        
        # 計算調整後的止損範圍
        adjusted_min = base_range[0] * volatility_factor * stop_loss_multiplier
        adjusted_max = base_range[1] * volatility_factor * stop_loss_multiplier
        
        return (max(0.005, adjusted_min), min(0.05, adjusted_max))  # 限制在 0.5% - 5% 範圍內
    
    async def generate_scalping_signals(self, symbol: str, timeframes: List[str] = None, real_price: float = None) -> List[ScalpingSignal]:
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
                
                # 🔥 如果提供了真實價格，使用真實價格替換模擬數據的最後一個價格
                if real_price is not None:
                    # 保持技術指標的計算基於歷史數據，但最新價格使用真實價格
                    df.iloc[-1, df.columns.get_loc('close')] = real_price
                    df.iloc[-1, df.columns.get_loc('open')] = real_price  # 也更新開盤價
                    
                    # 確保高低價合理
                    df.iloc[-1, df.columns.get_loc('high')] = max(df.iloc[-1]['high'], real_price)
                    df.iloc[-1, df.columns.get_loc('low')] = min(df.iloc[-1]['low'], real_price)
                
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
            
            # 根據 JSON 配置計算合理止損 (1-3%)
            stop_loss_range = self.get_stop_loss_range(symbol)
            stop_loss_pct = (stop_loss_range[0] + stop_loss_range[1]) / 2  # 使用平均值 (~2%)
            
            signal = self._create_signal_with_smart_timing(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.SCALP_LONG,
                entry_price=current_price,
                stop_loss=current_price * (1 - stop_loss_pct),  # 多單向下止損
                take_profit=current_price * (1 + stop_loss_pct * 3.0),  # 3倍風險回報
                confidence=confidence,
                urgency_level='high' if confidence > 0.75 else 'medium',
                strategy_name='EMA快速交叉',
                indicators={
                    'ema5': ema5_current,
                    'ema8': ema8_current,
                    'ema13': ema13_current
                },
                risk_reward_ratio=3.0,
                df=df,
                confirmation_count=2  # EMA交叉 + 價格突破
            )
            signals.append(signal)
        
        # 空頭信號：EMA5 < EMA8 < EMA13 且價格跌破EMA5
        elif (ema5_current < ema8_current < ema13_current and 
              current_price < ema5_current and 
              df['close'].iloc[-2] >= ema5.iloc[-2]):
            
            confidence = self._calculate_ema_confidence(ema5, ema8, ema13, df['volume'])
            
            # 根據 JSON 配置計算合理止損 (1-3%)
            stop_loss_range = self.get_stop_loss_range(symbol)
            stop_loss_pct = (stop_loss_range[0] + stop_loss_range[1]) / 2  # 使用平均值 (~2%)
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.SCALP_SHORT,
                entry_price=current_price,
                stop_loss=current_price * (1 + stop_loss_pct),  # 空單向上止損
                take_profit=current_price * (1 - stop_loss_pct * 3.0),  # 3倍風險回報
                confidence=confidence,
                urgency_level='high' if confidence > 0.75 else 'medium',
                strategy_name='EMA快速交叉',
                indicators={
                    'ema5': ema5_current,
                    'ema8': ema8_current,
                    'ema13': ema13_current
                },
                created_at=get_taiwan_now_naive(),
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
            
            # 根據 JSON 配置計算止損止盈
            stop_loss_range = self.get_stop_loss_range(symbol)
            asset_config = self.get_asset_config(symbol)
            
            # 使用動態止損（基於資產配置）
            stop_loss_pct = (stop_loss_range[0] + stop_loss_range[1]) / 2  # 使用平均值
            entry_padding = asset_config.get('entry_padding', 1.0)
            
            # 根據緊急程度調整止損
            urgency_multiplier = 0.5 if current_rsi > 85 else 0.8  # 更緊急的信號時間更短
            if current_rsi > 85:
                stop_loss_pct *= 0.8  # 緊急情況下收緊止損
            
            signal = self._create_signal_with_smart_timing(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.MEAN_REVERSION,
                entry_price=current_price * entry_padding,
                stop_loss=current_price * (1 + stop_loss_pct),  # SHORT 信號
                take_profit=current_price * (1 - stop_loss_pct * 1.5),  # 1.5:1 風險回報比
                confidence=confidence,
                urgency_level='urgent' if current_rsi > 85 else 'high',
                strategy_name='RSI超買反轉(JSON配置)',
                indicators={'rsi': current_rsi, 'stop_loss_pct': stop_loss_pct},
                risk_reward_ratio=1.0,
                df=df,
                confirmation_count=1,  # 單一RSI信號
                urgency_multiplier=urgency_multiplier
            )
            signals.append(signal)
        
        # 超賣反轉 (RSI < 25)
        elif current_rsi < 25 and rsi.iloc[-2] < rsi.iloc[-1]:
            confidence = min(0.9, (25 - current_rsi) / 20 + 0.6)
            
            # 根據 JSON 配置計算止損止盈
            stop_loss_range = self.get_stop_loss_range(symbol)
            asset_config = self.get_asset_config(symbol)
            
            # 使用動態止損（基於資產配置）
            stop_loss_pct = (stop_loss_range[0] + stop_loss_range[1]) / 2  # 使用平均值
            entry_padding = asset_config.get('entry_padding', 1.0)
            
            # 根據緊急程度調整止損
            if current_rsi < 15:
                stop_loss_pct *= 0.8  # 緊急情況下收緊止損
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.MEAN_REVERSION,
                entry_price=current_price * entry_padding,
                stop_loss=current_price * (1 - stop_loss_pct),  # LONG 信號
                take_profit=current_price * (1 + stop_loss_pct * 1.5),  # 1.5:1 風險回報比
                confidence=confidence,
                urgency_level='urgent' if current_rsi < 15 else 'high',
                strategy_name='RSI超賣反轉(JSON配置)',
                indicators={'rsi': current_rsi, 'stop_loss_pct': stop_loss_pct},
                created_at=get_taiwan_now_naive(),
                expires_in_minutes=self._get_expiry_minutes(timeframe) // 2,
                risk_reward_ratio=1.5
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
                created_at=get_taiwan_now_naive(),
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
                created_at=get_taiwan_now_naive(),
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
                created_at=get_taiwan_now_naive(),
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
            
            # 根據 JSON 配置計算合理止損 (1-3%)
            stop_loss_range = self.get_stop_loss_range(symbol)
            stop_loss_pct = (stop_loss_range[0] + stop_loss_range[1]) / 2  # 使用平均值 (~2%)
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.MOMENTUM_BREAKOUT,
                entry_price=current_price,
                stop_loss=current_price * (1 - stop_loss_pct),  # 多單向下止損
                take_profit=current_price * (1 + stop_loss_pct * 2.5),  # 2.5倍風險回報
                confidence=0.8,
                urgency_level='urgent',
                strategy_name='強勢動量多頭',
                indicators={
                    'roc': current_roc,
                    'ema12': ema12.iloc[-1]
                },
                created_at=get_taiwan_now_naive(),
                expires_in_minutes=self._get_expiry_minutes(timeframe) // 2,
                risk_reward_ratio=2.5
            )
            signals.append(signal)
        
        # 強勢動量空頭
        elif (current_roc < -2 and  # ROC < -2%
              df['close'].iloc[-1] < ema12.iloc[-1] < ema26.iloc[-1] and
              df['low'].iloc[-1] == df['low'].rolling(5).min().iloc[-1]):  # 創5期新低
            
            # 根據 JSON 配置計算合理止損 (1-3%)
            stop_loss_range = self.get_stop_loss_range(symbol)
            stop_loss_pct = (stop_loss_range[0] + stop_loss_range[1]) / 2  # 使用平均值 (~2%)
            
            signal = ScalpingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=ScalpingSignalType.MOMENTUM_BREAKOUT,
                entry_price=current_price,
                stop_loss=current_price * (1 + stop_loss_pct),  # 空單向上止損
                take_profit=current_price * (1 - stop_loss_pct * 2.5),  # 2.5倍風險回報
                confidence=0.8,
                urgency_level='urgent',
                strategy_name='強勢動量空頭',
                indicators={
                    'roc': current_roc,
                    'ema12': ema12.iloc[-1]
                },
                created_at=get_taiwan_now_naive(),
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
                created_at=get_taiwan_now_naive(),
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
                created_at=get_taiwan_now_naive(),
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
                created_at=get_taiwan_now_naive(),
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
                created_at=get_taiwan_now_naive(),
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
                created_at=get_taiwan_now_naive(),
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
                created_at=get_taiwan_now_naive(),
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
    
    def _create_signal_with_smart_timing(
        self,
        symbol: str,
        timeframe: str,
        signal_type: ScalpingSignalType,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        confidence: float,
        urgency_level: str,
        strategy_name: str,
        indicators: Dict,
        risk_reward_ratio: float,
        df: Optional[pd.DataFrame] = None,
        confirmation_count: int = 1,
        urgency_multiplier: float = 1.0
    ) -> ScalpingSignal:
        """
        創建帶有智能時間計算的交易信號
        
        Args:
            urgency_multiplier: 緊急程度倍數 (0.5=更短, 1.0=標準, 1.5=更長)
        """
        # 計算智能有效期
        expires_minutes, timing_details = self._get_expiry_minutes(
            timeframe=timeframe,
            signal_strength=confidence,
            signal_type=signal_type.value,
            df=df,
            confirmation_count=confirmation_count
        )
        
        # 應用緊急程度調整
        if urgency_multiplier != 1.0:
            expires_minutes = max(1, int(expires_minutes * urgency_multiplier))
            if timing_details:
                timing_details["urgency_adjustment"] = {
                    "multiplier": urgency_multiplier,
                    "original_minutes": expires_minutes / urgency_multiplier,
                    "adjusted_minutes": expires_minutes
                }
        
        return ScalpingSignal(
            symbol=symbol,
            timeframe=timeframe,
            signal_type=signal_type,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
            urgency_level=urgency_level,
            strategy_name=strategy_name,
            indicators=indicators,
            created_at=get_taiwan_now_naive(),
            expires_in_minutes=expires_minutes,
            risk_reward_ratio=risk_reward_ratio,
            timing_details=timing_details
        )

    def _get_expiry_minutes(
        self, 
        timeframe: str, 
        signal_strength: float = 0.7,
        signal_type: str = "MOMENTUM_BREAKOUT",
        df: Optional[pd.DataFrame] = None,
        confirmation_count: int = 1
    ) -> Tuple[int, Optional[Dict]]:
        """
        智能計算信號有效期
        
        Args:
            timeframe: 時間框架
            signal_strength: 信號強度
            signal_type: 信號類型 
            df: 市場數據DataFrame（用於計算波動率）
            confirmation_count: 確認次數
            
        Returns:
            (有效期分鐘數, 計算詳情)
        """
        try:
            # 計算波動率數據
            volatility_data = None
            if df is not None and len(df) >= 14:
                # 計算ATR作為波動率指標
                atr = ta.atr(df['high'], df['low'], df['close'], length=14)
                if atr is not None and len(atr) > 0:
                    # 轉換為百分比
                    volatility_data = atr / df['close'] * 100
            
            # 使用智能時間計算服務
            timing_result = smart_timing_service.calculate_smart_expiry_minutes(
                base_timeframe=timeframe,
                signal_strength=signal_strength,
                signal_type=signal_type,
                volatility_data=volatility_data,
                confirmation_count=confirmation_count,
                current_time=datetime.now()
            )
            
            return timing_result["expiry_minutes"], timing_result
            
        except Exception as e:
            logger.warning(f"智能時間計算失敗，使用傳統方法: {e}")
            # 備用方案：使用原有的固定時間邏輯
            expiry_map = {
                '1m': 5, '3m': 10, '5m': 15, '15m': 30, '30m': 60
            }
            return expiry_map.get(timeframe, 15), None
    
    async def _get_market_data(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """獲取市場數據 - 簡化版本以避免依賴問題"""
        try:
            # 暫時返回模擬數據結構來測試API端點
            import random
            
            # 為每個幣種設定合適的基礎價格（接近真實市場價格）
            price_map = {
                'BTCUSDT': 67000.0,     # Bitcoin 價格範圍
                'ETHUSDT': 3500.0,      # Ethereum 價格範圍
                'BNBUSDT': 300.0,       # Binance Coin 價格範圍
                'ADAUSDT': 0.45,        # Cardano 價格範圍
                'XRPUSDT': 0.65,        # Ripple 價格範圍
                'SOLUSDT': 180.0,       # Solana 價格範圍
                'DOGEUSDT': 0.08,       # Dogecoin 價格範圍
                'MATICUSDT': 0.85,      # Polygon 價格範圍
            }
            
            # 獲取基礎價格，如果幣種不在映射中則使用默認值
            base_price = price_map.get(symbol, 100.0)
            
            # 生成模擬K線數據
            data = []
            
            for i in range(limit):
                # 模擬價格波動
                price_change = random.uniform(-0.02, 0.02)  # ±2% 波動
                current_price = base_price * (1 + price_change)
                
                high = current_price * (1 + random.uniform(0, 0.01))
                low = current_price * (1 - random.uniform(0, 0.01))
                volume = random.uniform(1000, 10000)
                
                # 正確計算時間戳，避免分鐘數超出範圍
                timestamp = taiwan_now_minus(minutes=(limit - i))
                
                data.append({
                    'timestamp': timestamp,
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
