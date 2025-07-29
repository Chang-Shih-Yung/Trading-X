"""
精準信號篩選服務 - 零備選模式
基於 market_conditions_config 的多維度評分系統
只保留最精準的單一信號，備選信號直接銷毀
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np

from app.services.market_data import MarketDataService
from app.services.technical_indicators import TechnicalIndicatorsService
from app.services.market_analysis import MarketAnalysisService
from app.core.database import AsyncSessionLocal
from app.models.models import TradingSignal
from app.utils.time_utils import get_taiwan_now_naive
from sqlalchemy import delete, update, select
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

@dataclass
class PrecisionSignal:
    """精準篩選信號"""
    symbol: str
    signal_type: str  # LONG, SHORT
    strategy_name: str
    confidence: float
    precision_score: float
    entry_price: float
    stop_loss: float
    take_profit: float
    timeframe: str
    created_at: datetime
    expires_at: datetime
    
    # 市場條件評分
    market_condition_score: float
    indicator_consistency: float
    timing_score: float
    risk_adjustment: float
    
    # 原始數據
    market_data: Dict[str, Any]
    technical_indicators: Dict[str, Any]
    
    def dict(self):
        """轉換為字典格式"""
        return {
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'strategy_name': self.strategy_name,
            'confidence': self.confidence,
            'precision_score': self.precision_score,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'timeframe': self.timeframe,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'market_condition_score': self.market_condition_score,
            'indicator_consistency': self.indicator_consistency,
            'timing_score': self.timing_score,
            'risk_adjustment': self.risk_adjustment
        }

class MarketConditionsConfig:
    """市場條件配置 - 精準篩選標準"""
    
    def __init__(self):
        self.precision_thresholds = {
            # 基礎精準度要求
            "min_confidence": 0.75,        # 最低信心度
            "min_volume_ratio": 1.2,       # 最低成交量比率 (vs 平均)
            "max_spread": 0.002,           # 最大價差 (0.2%)
            
            # 技術指標精準度
            "rsi_precision": {
                "oversold_max": 25,        # 超賣上限 (更嚴格)
                "overbought_min": 75,      # 超買下限 (更嚴格)
                "neutral_exclude": True    # 排除中性區間
            },
            
            # 趨勢強度要求
            "trend_strength_min": 0.6,     # 最小趨勢強度
            "momentum_threshold": 0.7,      # 動量閾值
            
            # 波動率篩選
            "volatility_range": {
                "min": 0.015,              # 最小波動率 (1.5%)
                "max": 0.05,               # 最大波動率 (5%)
                "optimal": 0.025           # 最佳波動率 (2.5%)
            },
            
            # 時機精準度
            "time_precision": {
                "market_hours_only": True,  # 僅市場活躍時段
                "exclude_news_time": True,  # 排除重大新聞時段
                "optimal_hours": [9, 10, 14, 15, 20, 21]  # UTC 最佳交易時段
            }
        }
    
    def is_market_condition_optimal(self, market_data: dict) -> bool:
        """檢查市場條件是否達到最佳狀態"""
        
        current_hour = datetime.now().hour
        
        # 時機檢查
        if current_hour not in self.precision_thresholds["time_precision"]["optimal_hours"]:
            return False
        
        # 成交量檢查
        volume_ratio = market_data.get("volume_ratio", 0)
        if volume_ratio < self.precision_thresholds["min_volume_ratio"]:
            return False
        
        # 價差檢查
        spread = market_data.get("spread", 0)
        if spread > self.precision_thresholds["max_spread"]:
            return False
        
        # 波動率檢查
        volatility = market_data.get("volatility", 0)
        vol_range = self.precision_thresholds["volatility_range"]
        if not (vol_range["min"] <= volatility <= vol_range["max"]):
            return False
        
        return True

class PrecisionSignalFilter:
    """精準信號篩選器 - 只保留最精準的信號"""
    
    def __init__(self):
        self.market_config = MarketConditionsConfig()
        self.market_service = MarketDataService()
        self.technical_service = TechnicalIndicatorsService()
        self.market_analyzer = MarketAnalysisService()
        
        self.strategy_weights = {
            # 策略可靠性權重 (基於歷史表現)
            "momentum_scalp": 0.85,
            "breakout_scalp": 0.90,     # 突破策略較可靠
            "reversal_scalp": 0.75,     # 反轉策略風險較高
            "volume_scalp": 0.80,
            "enhanced_momentum": 0.88
        }
    
    async def execute_precision_selection(self, symbol: str) -> Optional[PrecisionSignal]:
        """執行精準篩選，只返回最佳信號或 None"""
        
        try:
            # 1. 獲取市場數據
            market_data = await self.get_comprehensive_market_data(symbol)
            
            # 2. 檢查市場條件
            if not self.market_config.is_market_condition_optimal(market_data):
                logger.info(f"{symbol} 市場條件不佳，跳過信號生成")
                return None
            
            # 3. 並行執行所有策略
            strategy_results = await self.execute_all_strategies(symbol, market_data)
            
            # 4. 精準篩選
            best_signal = await self.select_precision_signal(strategy_results, market_data)
            
            if best_signal:
                # 5. 最終驗證
                if await self.final_precision_check(best_signal, market_data):
                    logger.info(f"✅ 精準信號選出: {symbol} - {best_signal.strategy_name} "
                               f"(信心度: {best_signal.confidence:.3f}, 精準度: {best_signal.precision_score:.3f})")
                    return best_signal
                else:
                    logger.info(f"❌ 信號未通過最終驗證: {symbol}")
            
            return None
            
        except Exception as e:
            logger.error(f"精準篩選執行失敗 {symbol}: {e}")
            return None
    
    async def get_comprehensive_market_data(self, symbol: str) -> Dict[str, Any]:
        """獲取綜合市場數據"""
        
        try:
            # 獲取歷史數據
            df = await self.market_service.get_historical_data(
                symbol=symbol,
                timeframe="5m",
                limit=100,
                exchange='binance'
            )
            
            if df is None or df.empty or len(df) < 20:
                return {}
            
            # 計算市場指標
            closes = df['close'].tolist()
            volumes = df['volume'].tolist()
            highs = df['high'].tolist()
            lows = df['low'].tolist()
            
            # 當前價格
            current_price = closes[-1]
            
            # 計算波動率 (20期ATR)
            true_ranges = []
            for i in range(1, len(closes)):
                tr = max(
                    highs[i] - lows[i],
                    abs(highs[i] - closes[i-1]),
                    abs(lows[i] - closes[i-1])
                )
                true_ranges.append(tr)
            
            atr = np.mean(true_ranges[-20:]) if len(true_ranges) >= 20 else 0
            volatility = atr / current_price if current_price > 0 else 0
            
            # 計算成交量比率
            avg_volume = np.mean(volumes[-20:])
            current_volume = volumes[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            # 計算價差 (模擬)
            spread = (highs[-1] - lows[-1]) / current_price if current_price > 0 else 0
            
            # 計算趨勢強度
            sma_20 = np.mean(closes[-20:])
            trend_strength = abs(current_price - sma_20) / sma_20 if sma_20 > 0 else 0
            
            # 計算RSI (14期)
            rsi = 0.0
            if len(closes) >= 15:  # 需要至少15個數據點
                price_changes = [closes[i] - closes[i-1] for i in range(1, len(closes))]
                gains = [max(0, change) for change in price_changes]
                losses = [max(0, -change) for change in price_changes]
                
                if len(gains) >= 14:
                    avg_gain = np.mean(gains[-14:])
                    avg_loss = np.mean(losses[-14:])
                    
                    if avg_loss == 0:
                        rsi = 100.0
                    else:
                        rs = avg_gain / avg_loss
                        rsi = 100 - (100 / (1 + rs))
            
            return {
                "current_price": current_price,
                "volatility": volatility,
                "volume_ratio": volume_ratio,
                "spread": spread,
                "trend_strength": trend_strength,
                "rsi": rsi,
                "atr": atr,
                "avg_volume": avg_volume,
                "sma_20": sma_20,
                "closes": closes,
                "volumes": volumes,
                "highs": highs,
                "lows": lows
            }
            
        except Exception as e:
            logger.error(f"獲取市場數據失敗 {symbol}: {e}")
            return {}
    
    async def execute_all_strategies(self, symbol: str, market_data: dict) -> List[PrecisionSignal]:
        """執行所有策略並收集結果"""
        
        strategies = [
            ('enhanced_momentum', self.enhanced_momentum_strategy),
            ('breakout_scalp', self.enhanced_breakout_strategy),
            ('reversal_scalp', self.enhanced_reversal_strategy),
            ('volume_scalp', self.enhanced_volume_strategy)
        ]
        
        valid_signals = []
        
        for strategy_name, strategy_func in strategies:
            try:
                signal = await strategy_func(symbol, market_data)
                if signal and signal.confidence >= self.market_config.precision_thresholds["min_confidence"]:
                    # 應用策略權重
                    signal.confidence *= self.strategy_weights.get(strategy_name, 0.8)
                    valid_signals.append(signal)
                    
            except Exception as e:
                logger.error(f"策略 {strategy_name} 執行失敗: {e}")
        
        return valid_signals
    
    async def enhanced_momentum_strategy(self, symbol: str, market_data: dict) -> Optional[PrecisionSignal]:
        """增強動量策略 - 類型安全版本"""
        
        try:
            closes = market_data.get("closes", [])
            if len(closes) < 20:
                return None
            
            # 計算RSI (14期)
            price_changes = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            gains = [max(0, change) for change in price_changes]
            losses = [max(0, -change) for change in price_changes]
            
            if len(gains) < 14:
                return None
            
            avg_gain = sum(gains[-14:]) / 14
            avg_loss = sum(losses[-14:]) / 14
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            # 計算MACD
            ema_12 = self._calculate_ema(closes, 12)
            ema_26 = self._calculate_ema(closes, 26)
            macd_line = ema_12 - ema_26
            
            # 動量評分
            momentum_score = 0.0
            signal_type = None
            
            if rsi > 75 and macd_line < 0:  # 超買且MACD看空
                signal_type = "SHORT"
                momentum_score = (rsi - 75) / 25  # 0-1標準化
            elif rsi < 25 and macd_line > 0:  # 超賣且MACD看多
                signal_type = "LONG"
                momentum_score = (25 - rsi) / 25  # 0-1標準化
            
            if not signal_type:
                return None
            
            # 計算入場價格和止損止盈
            current_price = market_data["current_price"]
            atr = market_data.get("atr", current_price * 0.02)
            
            if signal_type == "LONG":
                entry_price = current_price
                stop_loss = current_price - (atr * 1.5)
                take_profit = current_price + (atr * 3.0)
            else:
                entry_price = current_price
                stop_loss = current_price + (atr * 1.5)
                take_profit = current_price - (atr * 3.0)
            
            # 基礎信心度
            base_confidence = momentum_score * 0.8 + (market_data.get("trend_strength", 0) * 0.2)
            
            signal = PrecisionSignal(
                symbol=symbol,
                signal_type=signal_type,
                strategy_name="enhanced_momentum",
                confidence=float(base_confidence),
                precision_score=0.0,  # 稍後計算
                entry_price=float(entry_price),
                stop_loss=float(stop_loss),
                take_profit=float(take_profit),
                timeframe="5m",
                created_at=get_taiwan_now_naive(),
                expires_at=get_taiwan_now_naive() + timedelta(hours=4),
                market_condition_score=0.0,  # 稍後計算
                indicator_consistency=0.0,   # 稍後計算
                timing_score=0.0,           # 稍後計算
                risk_adjustment=0.0,        # 稍後計算
                market_data=market_data,
                technical_indicators={"rsi": rsi, "macd": macd_line}
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"增強動量策略執行失敗: {e}")
            return None
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """計算指數移動平均"""
        if len(prices) < period:
            return np.mean(prices)
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    async def enhanced_breakout_strategy(self, symbol: str, market_data: dict) -> Optional[PrecisionSignal]:
        """增強突破策略"""
        
        try:
            closes = market_data.get("closes", [])
            highs = market_data.get("highs", [])
            lows = market_data.get("lows", [])
            
            if len(closes) < 20:
                return None
            
            # 計算布林帶
            sma_20 = np.mean(closes[-20:])
            std_20 = np.std(closes[-20:])
            upper_band = sma_20 + (std_20 * 2)
            lower_band = sma_20 - (std_20 * 2)
            
            current_price = closes[-1]
            
            # 檢查突破
            signal_type = None
            breakout_strength = 0.0
            
            if current_price > upper_band:
                signal_type = "LONG"
                breakout_strength = (current_price - upper_band) / upper_band
            elif current_price < lower_band:
                signal_type = "SHORT"
                breakout_strength = (lower_band - current_price) / lower_band
            
            if not signal_type or breakout_strength < 0.005:  # 至少0.5%的突破
                return None
            
            # 計算止損止盈
            atr = market_data.get("atr", current_price * 0.02)
            
            if signal_type == "LONG":
                entry_price = current_price
                stop_loss = lower_band
                take_profit = current_price + (atr * 4.0)
            else:
                entry_price = current_price
                stop_loss = upper_band
                take_profit = current_price - (atr * 4.0)
            
            # 信心度計算
            volume_confirmation = min(market_data.get("volume_ratio", 1), 3) / 3
            confidence = (breakout_strength * 0.6) + (volume_confirmation * 0.4)
            
            signal = PrecisionSignal(
                symbol=symbol,
                signal_type=signal_type,
                strategy_name="breakout_scalp",
                confidence=float(confidence),
                precision_score=0.0,
                entry_price=float(entry_price),
                stop_loss=float(stop_loss),
                take_profit=float(take_profit),
                timeframe="5m",
                created_at=get_taiwan_now_naive(),
                expires_at=get_taiwan_now_naive() + timedelta(hours=4),
                market_condition_score=0.0,
                indicator_consistency=0.0,
                timing_score=0.0,
                risk_adjustment=0.0,
                market_data=market_data,
                technical_indicators={"upper_band": upper_band, "lower_band": lower_band, "breakout_strength": breakout_strength}
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"增強突破策略執行失敗: {e}")
            return None
    
    async def enhanced_reversal_strategy(self, symbol: str, market_data: dict) -> Optional[PrecisionSignal]:
        """增強反轉策略"""
        
        try:
            closes = market_data.get("closes", [])
            if len(closes) < 14:
                return None
            
            # 計算Stochastic RSI
            rsi_values = []
            for i in range(14, len(closes)):
                period_closes = closes[i-13:i+1]
                price_changes = [period_closes[j] - period_closes[j-1] for j in range(1, len(period_closes))]
                gains = [max(0, change) for change in price_changes]
                losses = [max(0, -change) for change in price_changes]
                
                avg_gain = sum(gains) / len(gains) if gains else 0
                avg_loss = sum(losses) / len(losses) if losses else 0
                
                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                
                rsi_values.append(rsi)
            
            if len(rsi_values) < 14:
                return None
            
            # 計算Stochastic RSI
            rsi_high = max(rsi_values[-14:])
            rsi_low = min(rsi_values[-14:])
            current_rsi = rsi_values[-1]
            
            if rsi_high == rsi_low:
                stoch_rsi = 50
            else:
                stoch_rsi = (current_rsi - rsi_low) / (rsi_high - rsi_low) * 100
            
            # 反轉信號判斷
            signal_type = None
            reversal_strength = 0.0
            
            if stoch_rsi > 80:  # 超買反轉
                signal_type = "SHORT"
                reversal_strength = (stoch_rsi - 80) / 20
            elif stoch_rsi < 20:  # 超賣反轉
                signal_type = "LONG"
                reversal_strength = (20 - stoch_rsi) / 20
            
            if not signal_type:
                return None
            
            # 計算止損止盈
            current_price = market_data["current_price"]
            atr = market_data.get("atr", current_price * 0.015)
            
            if signal_type == "LONG":
                entry_price = current_price
                stop_loss = current_price - (atr * 2.0)
                take_profit = current_price + (atr * 2.5)
            else:
                entry_price = current_price
                stop_loss = current_price + (atr * 2.0)
                take_profit = current_price - (atr * 2.5)
            
            confidence = reversal_strength * 0.7  # 反轉策略相對保守
            
            signal = PrecisionSignal(
                symbol=symbol,
                signal_type=signal_type,
                strategy_name="reversal_scalp",
                confidence=float(confidence),
                precision_score=0.0,
                entry_price=float(entry_price),
                stop_loss=float(stop_loss),
                take_profit=float(take_profit),
                timeframe="5m",
                created_at=get_taiwan_now_naive(),
                expires_at=get_taiwan_now_naive() + timedelta(hours=4),
                market_condition_score=0.0,
                indicator_consistency=0.0,
                timing_score=0.0,
                risk_adjustment=0.0,
                market_data=market_data,
                technical_indicators={"stoch_rsi": stoch_rsi, "current_rsi": current_rsi}
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"增強反轉策略執行失敗: {e}")
            return None
    
    async def enhanced_volume_strategy(self, symbol: str, market_data: dict) -> Optional[PrecisionSignal]:
        """增強成交量策略"""
        
        try:
            volumes = market_data.get("volumes", [])
            closes = market_data.get("closes", [])
            
            if len(volumes) < 20 or len(closes) < 20:
                return None
            
            # 計算成交量指標
            avg_volume = np.mean(volumes[-20:])
            current_volume = volumes[-1]
            volume_spike = current_volume / avg_volume if avg_volume > 0 else 0
            
            # 計算價格變化
            price_change = (closes[-1] - closes[-2]) / closes[-2] if closes[-2] > 0 else 0
            
            # 成交量確認信號
            signal_type = None
            volume_strength = 0.0
            
            if volume_spike > 2.0:  # 成交量激增
                if price_change > 0.002:  # 價格上漲
                    signal_type = "LONG"
                    volume_strength = min(volume_spike / 5, 1.0)
                elif price_change < -0.002:  # 價格下跌
                    signal_type = "SHORT"
                    volume_strength = min(volume_spike / 5, 1.0)
            
            if not signal_type:
                return None
            
            # 計算止損止盈
            current_price = market_data["current_price"]
            atr = market_data.get("atr", current_price * 0.02)
            
            if signal_type == "LONG":
                entry_price = current_price
                stop_loss = current_price - (atr * 1.0)
                take_profit = current_price + (atr * 2.0)
            else:
                entry_price = current_price
                stop_loss = current_price + (atr * 1.0)
                take_profit = current_price - (atr * 2.0)
            
            confidence = volume_strength * abs(price_change) * 50  # 成交量 × 價格變化幅度
            
            signal = PrecisionSignal(
                symbol=symbol,
                signal_type=signal_type,
                strategy_name="volume_scalp",
                confidence=float(confidence),
                precision_score=0.0,
                entry_price=float(entry_price),
                stop_loss=float(stop_loss),
                take_profit=float(take_profit),
                timeframe="5m",
                created_at=get_taiwan_now_naive(),
                expires_at=get_taiwan_now_naive() + timedelta(hours=4),
                market_condition_score=0.0,
                indicator_consistency=0.0,
                timing_score=0.0,
                risk_adjustment=0.0,
                market_data=market_data,
                technical_indicators={"volume_spike": volume_spike, "price_change": price_change}
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"增強成交量策略執行失敗: {e}")
            return None
    
    async def select_precision_signal(self, signals: List[PrecisionSignal], 
                                    market_data: dict) -> Optional[PrecisionSignal]:
        """從信號中選擇最精準的一個"""
        
        if not signals:
            return None
        
        # 計算精準度評分
        for signal in signals:
            precision_score = await self.calculate_precision_score(signal, market_data)
            signal.precision_score = precision_score
        
        # 按精準度排序
        signals.sort(key=lambda x: x.precision_score, reverse=True)
        
        # 只有當最高分超過閾值才返回
        best_signal = signals[0]
        if best_signal.precision_score >= 0.8:  # 精準度閾值
            logger.info(f"精準信號評分: {best_signal.strategy_name} = {best_signal.precision_score:.3f}")
            return best_signal
        
        logger.info(f"所有信號精準度不足 (最高: {best_signal.precision_score:.3f})")
        return None
    
    async def calculate_precision_score(self, signal: PrecisionSignal, 
                                      market_data: dict) -> float:
        """計算信號精準度評分"""
        
        score = 0.0
        
        # 1. 基礎信心度 (40%)
        score += signal.confidence * 0.4
        
        # 2. 市場條件匹配度 (25%)
        market_match = self.calculate_market_match_score(signal, market_data)
        signal.market_condition_score = market_match
        score += market_match * 0.25
        
        # 3. 技術指標一致性 (20%)
        indicator_consistency = await self.check_indicator_consistency(signal, market_data)
        signal.indicator_consistency = indicator_consistency
        score += indicator_consistency * 0.2
        
        # 4. 時機精準度 (10%)
        timing_score = self.calculate_timing_score(signal, market_data)
        signal.timing_score = timing_score
        score += timing_score * 0.1
        
        # 5. 風險調整 (5%)
        risk_adjustment = self.calculate_risk_adjustment(signal, market_data)
        signal.risk_adjustment = risk_adjustment
        score += risk_adjustment * 0.05
        
        return min(score, 1.0)
    
    def calculate_market_match_score(self, signal: PrecisionSignal, market_data: dict) -> float:
        """計算市場條件匹配度"""
        
        match_score = 0.0
        
        # 波動率匹配
        volatility = market_data.get("volatility", 0)
        optimal_vol = self.market_config.precision_thresholds["volatility_range"]["optimal"]
        vol_deviation = abs(volatility - optimal_vol) / optimal_vol if optimal_vol > 0 else 1
        vol_score = max(0, 1.0 - vol_deviation)
        match_score += vol_score * 0.4
        
        # 成交量匹配
        volume_ratio = market_data.get("volume_ratio", 0)
        min_volume = self.market_config.precision_thresholds["min_volume_ratio"]
        vol_score = min(volume_ratio / min_volume, 2.0) / 2.0 if min_volume > 0 else 0
        match_score += vol_score * 0.3
        
        # 趨勢強度匹配
        trend_strength = market_data.get("trend_strength", 0)
        min_trend = self.market_config.precision_thresholds["trend_strength_min"]
        trend_score = max(0, min(trend_strength / min_trend, 1.0)) if min_trend > 0 else 0
        match_score += trend_score * 0.3
        
        return match_score
    
    async def check_indicator_consistency(self, signal: PrecisionSignal, market_data: dict) -> float:
        """檢查技術指標一致性"""
        
        try:
            consistency_score = 0.0
            
            # 獲取技術指標
            tech_indicators = signal.technical_indicators
            
            # RSI一致性檢查
            if "rsi" in tech_indicators:
                rsi = tech_indicators["rsi"]
                if signal.signal_type == "LONG" and rsi < 30:
                    consistency_score += 0.4
                elif signal.signal_type == "SHORT" and rsi > 70:
                    consistency_score += 0.4
            
            # MACD一致性檢查
            if "macd" in tech_indicators:
                macd = tech_indicators["macd"]
                if signal.signal_type == "LONG" and macd > 0:
                    consistency_score += 0.3
                elif signal.signal_type == "SHORT" and macd < 0:
                    consistency_score += 0.3
            
            # 成交量一致性檢查
            volume_ratio = market_data.get("volume_ratio", 1)
            if volume_ratio > 1.5:  # 成交量放大
                consistency_score += 0.3
            
            return min(consistency_score, 1.0)
            
        except Exception as e:
            logger.error(f"指標一致性檢查失敗: {e}")
            return 0.0
    
    def calculate_timing_score(self, signal: PrecisionSignal, market_data: dict) -> float:
        """計算時機精準度"""
        
        current_hour = datetime.now().hour
        optimal_hours = self.market_config.precision_thresholds["time_precision"]["optimal_hours"]
        
        # 最佳時間段評分
        if current_hour in optimal_hours:
            timing_score = 1.0
        else:
            # 次佳時間段
            secondary_hours = [8, 11, 13, 16, 19, 22]
            if current_hour in secondary_hours:
                timing_score = 0.7
            else:
                timing_score = 0.3
        
        return timing_score
    
    def calculate_risk_adjustment(self, signal: PrecisionSignal, market_data: dict) -> float:
        """計算風險調整評分"""
        
        try:
            # 計算風險回報比
            entry_price = signal.entry_price
            stop_loss = signal.stop_loss
            take_profit = signal.take_profit
            
            risk = abs(entry_price - stop_loss) / entry_price
            reward = abs(take_profit - entry_price) / entry_price
            
            if risk <= 0:
                return 0.0
            
            risk_reward_ratio = reward / risk
            
            # 風險回報比評分 (1:2以上較好)
            if risk_reward_ratio >= 2.0:
                rr_score = 1.0
            elif risk_reward_ratio >= 1.5:
                rr_score = 0.8
            elif risk_reward_ratio >= 1.0:
                rr_score = 0.6
            else:
                rr_score = 0.3
            
            # 波動率風險調整
            volatility = market_data.get("volatility", 0.02)
            if volatility > 0.04:  # 高波動率
                vol_adjustment = 0.7
            elif volatility < 0.01:  # 低波動率
                vol_adjustment = 0.8
            else:  # 適中波動率
                vol_adjustment = 1.0
            
            return rr_score * vol_adjustment
            
        except Exception as e:
            logger.error(f"風險調整計算失敗: {e}")
            return 0.5
    
    async def final_precision_check(self, signal: PrecisionSignal, market_data: dict) -> bool:
        """最終精準度檢查"""
        
        try:
            # 1. 檢查信號與當前市場價格的偏差
            current_price = market_data.get("current_price", 0)
            if current_price <= 0:
                return False
            
            price_deviation = abs(current_price - signal.entry_price) / signal.entry_price
            if price_deviation > 0.001:  # 0.1% 價格偏差容忍度
                logger.warning(f"信號價格偏差過大: {price_deviation:.4f}")
                return False
            
            # 2. 檢查風險回報比
            risk = abs(signal.entry_price - signal.stop_loss) / signal.entry_price
            reward = abs(signal.take_profit - signal.entry_price) / signal.entry_price
            
            if risk <= 0 or reward / risk < 1.0:  # 至少1:1的風險回報比
                logger.warning(f"風險回報比不佳: {reward/risk if risk > 0 else 0:.2f}")
                return False
            
            # 3. 檢查市場流動性 (通過成交量)
            volume_ratio = market_data.get("volume_ratio", 0)
            if volume_ratio < 0.5:  # 成交量過低
                logger.warning(f"市場流動性不足: {volume_ratio:.2f}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"最終精準度檢查失敗: {e}")
            return False

# 全局精準篩選器實例
precision_filter = PrecisionSignalFilter()
