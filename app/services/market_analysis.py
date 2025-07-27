"""
高級市場分析服務
包含牛熊市判斷、動態止盈止損計算、市場情緒分析等功能
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

from ..utils.time_utils import get_taiwan_now_naive
from enum import Enum
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MarketTrend(Enum):
    """市場趨勢枚舉"""
    BULL = "bull"          # 牛市
    BEAR = "bear"          # 熊市
    NEUTRAL = "neutral"    # 中性盤整
    TRANSITION = "transition"  # 轉換期

class MarketPhase(Enum):
    """牛市階段枚舉"""
    EARLY_BULL = "early_bull"      # 初升段
    MAIN_BULL = "main_bull"        # 主升段  
    HIGH_VOLATILITY = "high_volatility"  # 高位震盪段
    LATE_BULL = "late_bull"        # 牛尾末期

class SignalDirection(Enum):
    """信號方向"""
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"

@dataclass
class MarketCondition:
    """市場狀況數據類"""
    trend: MarketTrend
    phase: Optional[MarketPhase]
    bull_score: float  # 0-10 牛市分數
    bear_score: float  # 0-10 熊市分數
    confidence: float  # 0-1 判斷信心度
    key_factors: List[str]  # 關鍵影響因素
    analysis_timestamp: datetime

@dataclass
class DynamicStopLoss:
    """動態止盈止損數據類"""
    stop_loss_price: float
    take_profit_price: float
    stop_loss_pct: float
    take_profit_pct: float
    risk_reward_ratio: float
    atr_adjusted: bool
    market_condition_adjusted: bool
    reasoning: str

@dataclass
class BreakoutSignal:
    """突破信號數據類"""
    is_breakout: bool
    breakout_type: str  # volume_spike, price_breakout, macd_cross, rsi_momentum, bb_break
    strength: float  # 0-1
    volume_ratio: float
    price_momentum: float
    indicators_confirmation: Dict[str, bool]

class MarketAnalysisService:
    """高級市場分析服務"""
    
    def __init__(self):
        self.ma200_weight = 3
        self.adx_weight = 2
        self.structure_weight = 2
        self.fear_greed_weight = 1
        self.funding_rate_weight = 1
        self.halving_cycle_weight = 2
        
    def analyze_market_condition(self, 
                               price_data: pd.DataFrame,
                               fear_greed_index: Optional[float] = None,
                               funding_rate: Optional[float] = None) -> MarketCondition:
        """
        綜合分析市場狀況
        
        Args:
            price_data: OHLCV 數據
            fear_greed_index: 恐懼貪婪指數 (0-100)
            funding_rate: 資金費率
            
        Returns:
            MarketCondition: 市場狀況分析結果
        """
        try:
            bull_score = 0
            key_factors = []
            
            # 1. MA200 趨勢分析
            ma200 = ta.sma(price_data['close'], length=200)
            current_price = price_data['close'].iloc[-1]
            
            if len(ma200) > 1:
                ma200_current = ma200.iloc[-1]
                ma200_prev = ma200.iloc[-2]
                ma200_slope = ma200_current - ma200_prev
                
                if current_price > ma200_current and ma200_slope > 0:
                    bull_score += self.ma200_weight
                    key_factors.append(f"價格突破MA200且向上({current_price:.2f} > {ma200_current:.2f})")
                elif current_price < ma200_current and ma200_slope < 0:
                    bull_score -= self.ma200_weight
                    key_factors.append(f"價格跌破MA200且向下({current_price:.2f} < {ma200_current:.2f})")
            
            # 2. ADX 趨勢強度分析
            adx_data = ta.adx(price_data['high'], price_data['low'], price_data['close'], length=14)
            if adx_data is not None and not adx_data.empty:
                adx = adx_data.iloc[-1, 0] if len(adx_data.columns) > 0 else 0
                di_plus = adx_data.iloc[-1, 1] if len(adx_data.columns) > 1 else 0
                di_minus = adx_data.iloc[-1, 2] if len(adx_data.columns) > 2 else 0
                
                if adx > 25 and di_plus > di_minus:
                    bull_score += self.adx_weight
                    key_factors.append(f"ADX強勢上漲({adx:.1f}, +DI > -DI)")
                elif adx > 25 and di_minus > di_plus:
                    bull_score -= self.adx_weight
                    key_factors.append(f"ADX強勢下跌({adx:.1f}, -DI > +DI)")
            
            # 3. 價格結構分析 (高點低點)
            structure_score = self._analyze_price_structure(price_data)
            bull_score += structure_score * self.structure_weight
            
            if structure_score > 0.5:
                key_factors.append("價格結構呈現上升趨勢(高點墊高、低點墊高)")
            elif structure_score < -0.5:
                key_factors.append("價格結構呈現下降趨勢(高點走低、低點走低)")
            
            # 4. 恐懼貪婪指數
            if fear_greed_index is not None:
                if fear_greed_index > 55:
                    bull_score += self.fear_greed_weight
                    key_factors.append(f"恐懼貪婪指數偏樂觀({fear_greed_index})")
                elif fear_greed_index < 25:
                    bull_score -= self.fear_greed_weight
                    key_factors.append(f"恐懼貪婪指數極度恐懼({fear_greed_index})")
            
            # 5. 資金費率分析
            if funding_rate is not None:
                if funding_rate >= 0.01:  # 1%
                    bull_score += self.funding_rate_weight
                    key_factors.append(f"資金費率偏高({funding_rate:.3f}%)")
                elif funding_rate <= -0.01:
                    bull_score -= self.funding_rate_weight
                    key_factors.append(f"資金費率為負({funding_rate:.3f}%)")
            
            # 6. 減半週期判斷 (簡化版本)
            if self._is_within_halving_window():
                bull_score += self.halving_cycle_weight
                key_factors.append("處於比特幣減半後的牛市窗口期")
            
            # 計算熊市分數
            bear_score = max(0, -bull_score + 5)  # 相對熊市強度
            bull_score = max(0, bull_score)       # 確保非負
            
            # 判斷趨勢
            if bull_score >= 6:
                trend = MarketTrend.BULL
                phase = self._determine_bull_phase(price_data, bull_score)
            elif bear_score >= 6:
                trend = MarketTrend.BEAR
                phase = None
            elif bull_score >= 3:
                trend = MarketTrend.NEUTRAL
                phase = None
            else:
                trend = MarketTrend.TRANSITION
                phase = None
            
            # 計算信心度
            confidence = min(max(abs(bull_score - bear_score) / 10, 0.3), 0.95)
            
            return MarketCondition(
                trend=trend,
                phase=phase,
                bull_score=bull_score,
                bear_score=bear_score,
                confidence=confidence,
                key_factors=key_factors,
                analysis_timestamp=get_taiwan_now_naive()
            )
            
        except Exception as e:
            logger.error(f"市場分析失敗: {e}")
            return MarketCondition(
                trend=MarketTrend.NEUTRAL,
                phase=None,
                bull_score=5.0,
                bear_score=5.0,
                confidence=0.3,
                key_factors=["分析失敗，使用預設中性判斷"],
                analysis_timestamp=get_taiwan_now_naive()
            )
    
    def calculate_dynamic_stop_loss(self, 
                                  entry_price: float,
                                  signal_direction: SignalDirection,
                                  price_data: pd.DataFrame,
                                  market_condition: MarketCondition,
                                  timeframe: str = "1h") -> DynamicStopLoss:
        """
        計算動態止盈止損
        
        Args:
            entry_price: 進場價格
            signal_direction: 信號方向 (LONG/SHORT)
            price_data: 價格數據
            market_condition: 市場狀況
            timeframe: 時間框架
            
        Returns:
            DynamicStopLoss: 動態止盈止損結果
        """
        try:
            # 計算 ATR
            atr_14 = ta.atr(price_data['high'], price_data['low'], price_data['close'], length=14)
            atr = atr_14.iloc[-1] if not pd.isna(atr_14.iloc[-1]) else entry_price * 0.02
            
            # 基礎止損百分比
            if signal_direction == SignalDirection.LONG:
                base_stop_pct = 0.012  # 多單基礎 1.2%
            else:
                base_stop_pct = 0.01   # 空單基礎 1.0%
            
            # 根據市場狀況調整
            if market_condition.trend == MarketTrend.BULL:
                if signal_direction == SignalDirection.LONG:
                    # 牛市多單：正常或放寬止損
                    if market_condition.phase == MarketPhase.MAIN_BULL:
                        risk_reward_ratio = 4.0  # 主升段放大盈虧比
                    elif market_condition.phase == MarketPhase.HIGH_VOLATILITY:
                        risk_reward_ratio = 2.5  # 高位震盪縮小
                        base_stop_pct = 0.008    # 縮緊止損
                    else:
                        risk_reward_ratio = 3.0  # 初升段保守
                else:
                    # 牛市空單：快進快出
                    risk_reward_ratio = 2.0
                    base_stop_pct = 0.008  # 更緊的止損
                    
            elif market_condition.trend == MarketTrend.BEAR:
                if signal_direction == SignalDirection.SHORT:
                    # 熊市空單：順勢操作
                    risk_reward_ratio = 4.0
                    base_stop_pct = 0.01
                else:
                    # 熊市多單：高風險
                    risk_reward_ratio = 2.0
                    base_stop_pct = 0.008
            else:
                # 中性市場
                risk_reward_ratio = 2.5
            
            # ATR 調整
            atr_pct = atr / entry_price
            if atr_pct > 0.03:  # ATR > 3%，增加止損空間
                base_stop_pct *= 1.2
                atr_adjusted = True
            elif atr_pct < 0.01:  # ATR < 1%，縮小止損空間
                base_stop_pct *= 0.8
                atr_adjusted = True
            else:
                atr_adjusted = False
            
            # 計算具體價格
            risk = entry_price * base_stop_pct
            reward = risk * risk_reward_ratio
            
            if signal_direction == SignalDirection.LONG:
                stop_loss_price = entry_price - risk
                take_profit_price = entry_price + reward
                stop_loss_pct = -base_stop_pct * 100
                take_profit_pct = (reward / entry_price) * 100
            else:  # SHORT
                stop_loss_price = entry_price + risk
                take_profit_price = entry_price - reward
                stop_loss_pct = base_stop_pct * 100
                take_profit_pct = -(reward / entry_price) * 100
            
            reasoning = f"{market_condition.trend.value}市場，{signal_direction.value}信號，風險回報比{risk_reward_ratio}:1"
            if atr_adjusted:
                reasoning += f"，ATR調整({atr_pct:.2%})"
            
            return DynamicStopLoss(
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                stop_loss_pct=stop_loss_pct,
                take_profit_pct=take_profit_pct,
                risk_reward_ratio=risk_reward_ratio,
                atr_adjusted=atr_adjusted,
                market_condition_adjusted=True,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"動態止盈止損計算失敗: {e}")
            # 返回保守的預設值
            risk_pct = 0.01
            reward_ratio = 2.0
            
            if signal_direction == SignalDirection.LONG:
                return DynamicStopLoss(
                    stop_loss_price=entry_price * (1 - risk_pct),
                    take_profit_price=entry_price * (1 + risk_pct * reward_ratio),
                    stop_loss_pct=-risk_pct * 100,
                    take_profit_pct=risk_pct * reward_ratio * 100,
                    risk_reward_ratio=reward_ratio,
                    atr_adjusted=False,
                    market_condition_adjusted=False,
                    reasoning="計算失敗，使用預設保守值"
                )
            else:
                return DynamicStopLoss(
                    stop_loss_price=entry_price * (1 + risk_pct),
                    take_profit_price=entry_price * (1 - risk_pct * reward_ratio),
                    stop_loss_pct=risk_pct * 100,
                    take_profit_pct=-risk_pct * reward_ratio * 100,
                    risk_reward_ratio=reward_ratio,
                    atr_adjusted=False,
                    market_condition_adjusted=False,
                    reasoning="計算失敗，使用預設保守值"
                )
    
    def detect_breakout_signals(self, 
                              price_data: pd.DataFrame,
                              volume_data: Optional[pd.DataFrame] = None) -> BreakoutSignal:
        """
        檢測突破信號
        
        Args:
            price_data: OHLCV 數據
            volume_data: 額外的交易量數據
            
        Returns:
            BreakoutSignal: 突破信號結果
        """
        try:
            breakout_signals = {}
            total_strength = 0
            
            # 1. 成交量突破檢測
            volume_sma = ta.sma(price_data['volume'], length=20)
            current_volume = price_data['volume'].iloc[-1]
            avg_volume = volume_sma.iloc[-1] if not pd.isna(volume_sma.iloc[-1]) else current_volume
            
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            if volume_ratio > 1.5:  # 成交量暴增50%
                breakout_signals['volume_spike'] = True
                total_strength += min(volume_ratio - 1, 1.0)  # 最多貢獻1.0
            else:
                breakout_signals['volume_spike'] = False
            
            # 2. 價格突破檢測
            high_20 = ta.max(price_data['high'], length=20)
            low_20 = ta.min(price_data['low'], length=20)
            current_price = price_data['close'].iloc[-1]
            
            recent_high = high_20.iloc[-1] if not pd.isna(high_20.iloc[-1]) else current_price
            recent_low = low_20.iloc[-1] if not pd.isna(low_20.iloc[-1]) else current_price
            
            if current_price > recent_high:
                breakout_signals['price_breakout'] = True
                price_momentum = (current_price - recent_high) / recent_high
                total_strength += min(price_momentum * 10, 1.0)
            elif current_price < recent_low:
                breakout_signals['price_breakout'] = True
                price_momentum = (recent_low - current_price) / recent_low
                total_strength += min(price_momentum * 10, 1.0)
            else:
                breakout_signals['price_breakout'] = False
                price_momentum = 0
            
            # 3. MACD 交叉檢測
            macd_data = ta.macd(price_data['close'], fast=12, slow=26, signal=9)
            if macd_data is not None and len(macd_data) >= 2:
                macd_current = macd_data.iloc[-1, 0]
                signal_current = macd_data.iloc[-1, 1]
                macd_prev = macd_data.iloc[-2, 0]
                signal_prev = macd_data.iloc[-2, 1]
                
                # 檢測交叉
                if (macd_current > signal_current and macd_prev <= signal_prev) or \
                   (macd_current < signal_current and macd_prev >= signal_prev):
                    breakout_signals['macd_cross'] = True
                    total_strength += 0.6
                else:
                    breakout_signals['macd_cross'] = False
            else:
                breakout_signals['macd_cross'] = False
            
            # 4. RSI 動量檢測
            rsi = ta.rsi(price_data['close'], length=14)
            if len(rsi) >= 2:
                rsi_current = rsi.iloc[-1]
                rsi_prev = rsi.iloc[-2]
                
                # RSI 快速變化
                rsi_change = abs(rsi_current - rsi_prev)
                if rsi_change > 5 and (rsi_current > 70 or rsi_current < 30):
                    breakout_signals['rsi_momentum'] = True
                    total_strength += min(rsi_change / 20, 0.8)
                else:
                    breakout_signals['rsi_momentum'] = False
            else:
                breakout_signals['rsi_momentum'] = False
            
            # 5. 布林帶突破檢測
            bb = ta.bbands(price_data['close'], length=20, std=2)
            if bb is not None and not bb.empty:
                bb_upper = bb.iloc[-1, 0]  # BBU_20_2.0
                bb_lower = bb.iloc[-1, 2]  # BBL_20_2.0
                
                if current_price > bb_upper or current_price < bb_lower:
                    breakout_signals['bb_break'] = True
                    # 計算突破程度
                    if current_price > bb_upper:
                        bb_strength = (current_price - bb_upper) / bb_upper
                    else:
                        bb_strength = (bb_lower - current_price) / bb_lower
                    total_strength += min(bb_strength * 5, 0.7)
                else:
                    breakout_signals['bb_break'] = False
            else:
                breakout_signals['bb_break'] = False
            
            # 判斷是否為突破
            confirmed_signals = sum(breakout_signals.values())
            is_breakout = confirmed_signals >= 2  # 至少2個指標確認
            
            # 確定突破類型
            if breakout_signals['volume_spike'] and breakout_signals['price_breakout']:
                breakout_type = "volume_price_breakout"
            elif breakout_signals['macd_cross'] and breakout_signals['rsi_momentum']:
                breakout_type = "momentum_breakout"
            elif breakout_signals['bb_break']:
                breakout_type = "volatility_breakout"
            elif confirmed_signals > 0:
                breakout_type = "partial_breakout"
            else:
                breakout_type = "no_breakout"
            
            # 標準化強度
            final_strength = min(total_strength / 3, 1.0)  # 歸一化到0-1
            
            return BreakoutSignal(
                is_breakout=is_breakout,
                breakout_type=breakout_type,
                strength=final_strength,
                volume_ratio=volume_ratio,
                price_momentum=price_momentum,
                indicators_confirmation=breakout_signals
            )
            
        except Exception as e:
            logger.error(f"突破信號檢測失敗: {e}")
            return BreakoutSignal(
                is_breakout=False,
                breakout_type="detection_failed",
                strength=0.0,
                volume_ratio=1.0,
                price_momentum=0.0,
                indicators_confirmation={}
            )
    
    def _analyze_price_structure(self, price_data: pd.DataFrame, lookback: int = 50) -> float:
        """
        分析價格結構（高點低點趨勢）
        
        Returns:
            float: -1 到 1，正值表示上升結構，負值表示下降結構
        """
        try:
            if len(price_data) < lookback:
                return 0
            
            recent_data = price_data.tail(lookback)
            
            # 尋找局部高點和低點
            highs = []
            lows = []
            
            for i in range(2, len(recent_data) - 2):
                # 局部高點：比前後都高
                if (recent_data['high'].iloc[i] > recent_data['high'].iloc[i-1] and 
                    recent_data['high'].iloc[i] > recent_data['high'].iloc[i+1] and
                    recent_data['high'].iloc[i] > recent_data['high'].iloc[i-2] and 
                    recent_data['high'].iloc[i] > recent_data['high'].iloc[i+2]):
                    highs.append((i, recent_data['high'].iloc[i]))
                
                # 局部低點：比前後都低
                if (recent_data['low'].iloc[i] < recent_data['low'].iloc[i-1] and 
                    recent_data['low'].iloc[i] < recent_data['low'].iloc[i+1] and
                    recent_data['low'].iloc[i] < recent_data['low'].iloc[i-2] and 
                    recent_data['low'].iloc[i] < recent_data['low'].iloc[i+2]):
                    lows.append((i, recent_data['low'].iloc[i]))
            
            # 計算趨勢
            structure_score = 0
            
            # 高點趨勢
            if len(highs) >= 2:
                recent_highs = sorted(highs, key=lambda x: x[0])[-3:]  # 最近3個高點
                if len(recent_highs) >= 2:
                    high_trend = recent_highs[-1][1] - recent_highs[0][1]
                    structure_score += high_trend / recent_highs[0][1]
            
            # 低點趨勢
            if len(lows) >= 2:
                recent_lows = sorted(lows, key=lambda x: x[0])[-3:]  # 最近3個低點
                if len(recent_lows) >= 2:
                    low_trend = recent_lows[-1][1] - recent_lows[0][1]
                    structure_score += low_trend / recent_lows[0][1]
            
            # 標準化到 -1 到 1
            return max(-1, min(1, structure_score * 10))
            
        except Exception as e:
            logger.error(f"價格結構分析失敗: {e}")
            return 0
    
    def _determine_bull_phase(self, price_data: pd.DataFrame, bull_score: float) -> MarketPhase:
        """確定牛市階段"""
        try:
            # 計算價格相對於不同MA的位置
            ma50 = ta.sma(price_data['close'], length=50)
            ma200 = ta.sma(price_data['close'], length=200)
            current_price = price_data['close'].iloc[-1]
            
            # 計算漲幅
            if len(price_data) >= 100:
                price_100_days_ago = price_data['close'].iloc[-100]
                gain_100d = (current_price - price_100_days_ago) / price_100_days_ago
            else:
                gain_100d = 0
            
            # 計算波動率
            returns = price_data['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(365) if len(returns) > 10 else 0
            
            # 判斷階段
            if bull_score >= 8 and gain_100d > 0.5 and volatility > 0.3:
                return MarketPhase.LATE_BULL  # 牛尾末期：高分數+大漲幅+高波動
            elif bull_score >= 7 and volatility > 0.25:
                return MarketPhase.HIGH_VOLATILITY  # 高位震盪
            elif bull_score >= 7 and gain_100d > 0.2:
                return MarketPhase.MAIN_BULL  # 主升段
            else:
                return MarketPhase.EARLY_BULL  # 初升段
                
        except Exception as e:
            logger.error(f"牛市階段判斷失敗: {e}")
            return MarketPhase.EARLY_BULL
    
    def _is_within_halving_window(self) -> bool:
        """
        簡化的減半週期判斷
        實際應用中需要接入真實的比特幣減半時間數據
        """
        # 這裡是一個簡化的實現
        # 實際應該根據真實的比特幣減半時間來計算
        current_year = get_taiwan_now_naive().year
        
        # 已知的減半年份：2012, 2016, 2020, 2024
        last_halving_years = [2020, 2024]
        
        for halving_year in last_halving_years:
            months_since_halving = (current_year - halving_year) * 12
            if 6 <= months_since_halving <= 18:  # 減半後6-18個月
                return True
        
        return False
