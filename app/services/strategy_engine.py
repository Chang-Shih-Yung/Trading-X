import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from app.services.market_data import MarketDataService
from app.services.technical_indicators import TechnicalIndicatorsService, IndicatorResult
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.models import TradingSignal
import logging

logger = logging.getLogger(__name__)

class SignalType(Enum):
    """信號類型"""
    LONG = "LONG"
    SHORT = "SHORT"
    CLOSE = "CLOSE"
    HOLD = "HOLD"

@dataclass
class TradeSignal:
    """交易信號結構"""
    symbol: str
    timeframe: str
    signal_type: SignalType
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    confidence: float
    signal_strength: float
    reasoning: str
    indicators_used: Dict
    expires_at: datetime

class StrategyEngine:
    """進階策略引擎"""
    
    def __init__(self):
        self.market_service = MarketDataService()
        self.running = False
        self.active_signals = {}
        
        # 策略參數
        self.min_risk_reward = settings.MIN_RISK_REWARD_RATIO
        self.risk_percentage = settings.DEFAULT_RISK_PERCENTAGE
        
    async def start_signal_generation(self):
        """啟動信號生成"""
        self.running = True
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'XRP/USDT']
        timeframes = ['1h', '4h', '1d']
        
        while self.running:
            try:
                tasks = []
                for symbol in symbols:
                    for timeframe in timeframes:
                        task = asyncio.create_task(
                            self.analyze_symbol(symbol, timeframe)
                        )
                        tasks.append(task)
                
                # 並行分析所有交易對
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # 每5分鐘重新分析
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"策略引擎錯誤: {e}")
                await asyncio.sleep(60)
    
    async def analyze_symbol(self, symbol: str, timeframe: str) -> Optional[TradeSignal]:
        """分析單一交易對"""
        try:
            # 獲取市場數據
            df = await self.market_service.get_market_data_from_db(
                symbol, timeframe, limit=200
            )
            
            if df.empty or len(df) < 50:
                # 如果資料庫沒有數據，從交易所獲取
                df = await self.market_service.get_historical_data(
                    symbol, timeframe, limit=200
                )
                if not df.empty:
                    await self.market_service.save_market_data(df)
            
            if df.empty:
                return None
            
            # 計算技術指標
            indicators = TechnicalIndicatorsService.calculate_all_indicators(df)
            
            # 生成交易信號
            signal = await self.generate_signal(df, indicators, symbol, timeframe)
            
            if signal and signal.confidence >= 0.7:  # 只處理高置信度信號
                await self.save_signal(signal)
                logger.info(f"生成信號: {symbol} {timeframe} {signal.signal_type.value}")
            
            return signal
            
        except Exception as e:
            logger.error(f"分析 {symbol} {timeframe} 失敗: {e}")
            return None
    
    async def generate_signal(
        self,
        df: pd.DataFrame,
        indicators: Dict[str, IndicatorResult],
        symbol: str,
        timeframe: str
    ) -> Optional[TradeSignal]:
        """生成交易信號 - 進階多重確認策略"""
        
        current_price = float(df['close'].iloc[-1])
        
        # 多重時間框架分析
        multi_timeframe_signals = await self._analyze_multiple_timeframes(symbol, df)
        
        # 計算綜合信號強度
        signal_scores = self._calculate_signal_scores(indicators, multi_timeframe_signals)
        
        # 判斷主要信號方向
        long_score = signal_scores['long_score']
        short_score = signal_scores['short_score']
        
        # 信號閾值 (需要足夠強的信號才觸發)
        signal_threshold = 60
        
        if long_score >= signal_threshold and long_score > short_score:
            return await self._create_long_signal(
                df, indicators, symbol, timeframe, current_price, long_score, signal_scores
            )
        elif short_score >= signal_threshold and short_score > long_score:
            return await self._create_short_signal(
                df, indicators, symbol, timeframe, current_price, short_score, signal_scores
            )
        
        return None
    
    def _calculate_signal_scores(
        self,
        indicators: Dict[str, IndicatorResult],
        multi_timeframe_signals: Dict
    ) -> Dict[str, float]:
        """計算綜合信號評分"""
        
        long_score = 0
        short_score = 0
        
        # 權重配置
        weights = {
            'trend': 0.3,      # 趨勢指標權重
            'momentum': 0.25,   # 動量指標權重
            'volatility': 0.2,  # 波動性指標權重
            'volume': 0.15,     # 成交量指標權重
            'support_resistance': 0.1  # 支撐阻力權重
        }
        
        # 趨勢指標評分
        trend_indicators = ['EMA', 'MACD', 'ICHIMOKU']
        trend_long, trend_short = self._score_indicators(indicators, trend_indicators)
        
        # 動量指標評分
        momentum_indicators = ['RSI', 'STOCH', 'WILLR']
        momentum_long, momentum_short = self._score_indicators(indicators, momentum_indicators)
        
        # 波動性指標評分
        volatility_indicators = ['BBANDS', 'ATR']
        vol_long, vol_short = self._score_indicators(indicators, volatility_indicators)
        
        # 成交量指標評分
        volume_indicators = ['OBV', 'VWAP']
        volume_long, volume_short = self._score_indicators(indicators, volume_indicators)
        
        # 支撐阻力評分
        sr_indicators = ['PIVOT', 'FIBONACCI']
        sr_long, sr_short = self._score_indicators(indicators, sr_indicators)
        
        # 計算加權總分
        long_score = (
            trend_long * weights['trend'] +
            momentum_long * weights['momentum'] +
            vol_long * weights['volatility'] +
            volume_long * weights['volume'] +
            sr_long * weights['support_resistance']
        )
        
        short_score = (
            trend_short * weights['trend'] +
            momentum_short * weights['momentum'] +
            vol_short * weights['volatility'] +
            volume_short * weights['volume'] +
            sr_short * weights['support_resistance']
        )
        
        # 多重時間框架確認加分
        if multi_timeframe_signals.get('higher_tf_bullish', False):
            long_score += 10
        if multi_timeframe_signals.get('higher_tf_bearish', False):
            short_score += 10
        
        # 市場結構確認
        market_structure = self._analyze_market_structure(indicators)
        if market_structure == 'BULLISH':
            long_score += 15
        elif market_structure == 'BEARISH':
            short_score += 15
        
        return {
            'long_score': min(long_score, 100),
            'short_score': min(short_score, 100),
            'trend_long': trend_long,
            'trend_short': trend_short,
            'momentum_long': momentum_long,
            'momentum_short': momentum_short,
            'market_structure': market_structure
        }
    
    def _score_indicators(
        self,
        indicators: Dict[str, IndicatorResult],
        indicator_names: List[str]
    ) -> Tuple[float, float]:
        """對指定指標進行評分"""
        long_score = 0
        short_score = 0
        count = 0
        
        for name in indicator_names:
            if name in indicators:
                indicator = indicators[name]
                if indicator.signal == "BUY":
                    long_score += indicator.strength
                elif indicator.signal == "SELL":
                    short_score += indicator.strength
                count += 1
        
        if count > 0:
            long_score /= count
            short_score /= count
        
        return long_score, short_score
    
    def _analyze_market_structure(self, indicators: Dict[str, IndicatorResult]) -> str:
        """分析市場結構"""
        structure_signals = []
        
        # EMA排列
        if 'EMA' in indicators:
            ema_meta = indicators['EMA'].metadata
            if ema_meta['ema_20'] > ema_meta['ema_50']:
                structure_signals.append('BULLISH')
            else:
                structure_signals.append('BEARISH')
        
        # MACD位置
        if 'MACD' in indicators:
            macd_meta = indicators['MACD'].metadata
            if macd_meta['macd'] > 0 and macd_meta['histogram'] > 0:
                structure_signals.append('BULLISH')
            elif macd_meta['macd'] < 0 and macd_meta['histogram'] < 0:
                structure_signals.append('BEARISH')
        
        # 一目均衡表雲層
        if 'ICHIMOKU' in indicators:
            if indicators['ICHIMOKU'].signal == 'BUY':
                structure_signals.append('BULLISH')
            elif indicators['ICHIMOKU'].signal == 'SELL':
                structure_signals.append('BEARISH')
        
        # 統計結果
        bullish_count = structure_signals.count('BULLISH')
        bearish_count = structure_signals.count('BEARISH')
        
        if bullish_count > bearish_count:
            return 'BULLISH'
        elif bearish_count > bullish_count:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    async def _analyze_multiple_timeframes(self, symbol: str, current_df: pd.DataFrame) -> Dict:
        """多重時間框架分析"""
        results = {
            'higher_tf_bullish': False,
            'higher_tf_bearish': False,
            'lower_tf_confirmation': False
        }
        
        try:
            # 分析更高時間框架 (如果當前是1h，則分析4h)
            timeframe_map = {'1h': '4h', '4h': '1d', '1d': '1w'}
            current_tf = current_df['timeframe'].iloc[0] if not current_df.empty else '1h'
            higher_tf = timeframe_map.get(current_tf)
            
            if higher_tf:
                higher_df = await self.market_service.get_market_data_from_db(
                    symbol, higher_tf, limit=50
                )
                
                if not higher_df.empty and len(higher_df) >= 20:
                    higher_indicators = TechnicalIndicatorsService.calculate_all_indicators(higher_df)
                    
                    # 檢查更高時間框架的趨勢
                    trend_bullish = 0
                    trend_bearish = 0
                    
                    for name in ['EMA', 'MACD', 'ICHIMOKU']:
                        if name in higher_indicators:
                            if higher_indicators[name].signal == 'BUY':
                                trend_bullish += 1
                            elif higher_indicators[name].signal == 'SELL':
                                trend_bearish += 1
                    
                    results['higher_tf_bullish'] = trend_bullish >= 2
                    results['higher_tf_bearish'] = trend_bearish >= 2
            
        except Exception as e:
            logger.error(f"多重時間框架分析失敗: {e}")
        
        return results
    
    async def _create_long_signal(
        self,
        df: pd.DataFrame,
        indicators: Dict[str, IndicatorResult],
        symbol: str,
        timeframe: str,
        current_price: float,
        signal_strength: float,
        signal_scores: Dict
    ) -> TradeSignal:
        """創建做多信號"""
        
        # 計算止損價位 (使用ATR或近期低點)
        stop_loss = self._calculate_stop_loss_long(df, indicators, current_price)
        
        # 計算止盈價位 (基於風險回報比)
        risk_amount = current_price - stop_loss
        target_reward = risk_amount * self.min_risk_reward
        take_profit = current_price + target_reward
        
        # 計算風險回報比
        risk_reward_ratio = target_reward / risk_amount if risk_amount > 0 else 0
        
        # 計算置信度
        confidence = self._calculate_confidence(signal_strength, signal_scores, risk_reward_ratio)
        
        # 生成推理說明
        reasoning = self._generate_reasoning('LONG', indicators, signal_scores)
        
        return TradeSignal(
            symbol=symbol,
            timeframe=timeframe,
            signal_type=SignalType.LONG,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=risk_reward_ratio,
            confidence=confidence,
            signal_strength=signal_strength,
            reasoning=reasoning,
            indicators_used={k: v.signal for k, v in indicators.items()},
            expires_at=datetime.now() + timedelta(hours=24)
        )
    
    async def _create_short_signal(
        self,
        df: pd.DataFrame,
        indicators: Dict[str, IndicatorResult],
        symbol: str,
        timeframe: str,
        current_price: float,
        signal_strength: float,
        signal_scores: Dict
    ) -> TradeSignal:
        """創建做空信號"""
        
        # 計算止損價位
        stop_loss = self._calculate_stop_loss_short(df, indicators, current_price)
        
        # 計算止盈價位
        risk_amount = stop_loss - current_price
        target_reward = risk_amount * self.min_risk_reward
        take_profit = current_price - target_reward
        
        # 計算風險回報比
        risk_reward_ratio = target_reward / risk_amount if risk_amount > 0 else 0
        
        # 計算置信度
        confidence = self._calculate_confidence(signal_strength, signal_scores, risk_reward_ratio)
        
        # 生成推理說明
        reasoning = self._generate_reasoning('SHORT', indicators, signal_scores)
        
        return TradeSignal(
            symbol=symbol,
            timeframe=timeframe,
            signal_type=SignalType.SHORT,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=risk_reward_ratio,
            confidence=confidence,
            signal_strength=signal_strength,
            reasoning=reasoning,
            indicators_used={k: v.signal for k, v in indicators.items()},
            expires_at=datetime.now() + timedelta(hours=24)
        )
    
    def _calculate_stop_loss_long(
        self,
        df: pd.DataFrame,
        indicators: Dict[str, IndicatorResult],
        current_price: float
    ) -> float:
        """計算做多止損價位"""
        
        stop_options = []
        
        # 1. ATR止損
        if 'ATR' in indicators:
            atr_value = indicators['ATR'].metadata['atr_value']
            atr_stop = current_price - (atr_value * 2)
            stop_options.append(atr_stop)
        
        # 2. 近期低點止損
        recent_low = df['low'].tail(20).min()
        if recent_low < current_price:
            stop_options.append(recent_low * 0.995)  # 稍微低於低點
        
        # 3. 支撐位止損
        if 'PIVOT' in indicators:
            pivot_data = indicators['PIVOT'].metadata
            if 's1' in pivot_data and pivot_data['s1'] < current_price:
                stop_options.append(pivot_data['s1'])
        
        # 4. 布林通道下軌
        if 'BBANDS' in indicators:
            bb_lower = indicators['BBANDS'].metadata['lower']
            if bb_lower < current_price:
                stop_options.append(bb_lower)
        
        # 選擇最保守的止損 (最接近當前價格但不超過3%風險)
        if stop_options:
            max_risk_stop = current_price * 0.97  # 最大3%風險
            valid_stops = [s for s in stop_options if s >= max_risk_stop]
            return max(valid_stops) if valid_stops else max_risk_stop
        
        return current_price * 0.98  # 預設2%止損
    
    def _calculate_stop_loss_short(
        self,
        df: pd.DataFrame,
        indicators: Dict[str, IndicatorResult],
        current_price: float
    ) -> float:
        """計算做空止損價位"""
        
        stop_options = []
        
        # 1. ATR止損
        if 'ATR' in indicators:
            atr_value = indicators['ATR'].metadata['atr_value']
            atr_stop = current_price + (atr_value * 2)
            stop_options.append(atr_stop)
        
        # 2. 近期高點止損
        recent_high = df['high'].tail(20).max()
        if recent_high > current_price:
            stop_options.append(recent_high * 1.005)  # 稍微高於高點
        
        # 3. 阻力位止損
        if 'PIVOT' in indicators:
            pivot_data = indicators['PIVOT'].metadata
            if 'r1' in pivot_data and pivot_data['r1'] > current_price:
                stop_options.append(pivot_data['r1'])
        
        # 4. 布林通道上軌
        if 'BBANDS' in indicators:
            bb_upper = indicators['BBANDS'].metadata['upper']
            if bb_upper > current_price:
                stop_options.append(bb_upper)
        
        # 選擇最保守的止損
        if stop_options:
            max_risk_stop = current_price * 1.03  # 最大3%風險
            valid_stops = [s for s in stop_options if s <= max_risk_stop]
            return min(valid_stops) if valid_stops else max_risk_stop
        
        return current_price * 1.02  # 預設2%止損
    
    def _calculate_confidence(
        self,
        signal_strength: float,
        signal_scores: Dict,
        risk_reward_ratio: float
    ) -> float:
        """計算信號置信度"""
        
        confidence = 0
        
        # 基礎信號強度 (40%權重)
        confidence += (signal_strength / 100) * 0.4
        
        # 風險回報比 (30%權重)
        rr_score = min(risk_reward_ratio / 3, 1)  # 3:1比例得滿分
        confidence += rr_score * 0.3
        
        # 市場結構確認 (20%權重)
        if signal_scores.get('market_structure') in ['BULLISH', 'BEARISH']:
            confidence += 0.2
        
        # 多重指標確認 (10%權重)
        indicator_agreement = self._calculate_indicator_agreement(signal_scores)
        confidence += indicator_agreement * 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_indicator_agreement(self, signal_scores: Dict) -> float:
        """計算指標一致性"""
        scores = [
            signal_scores.get('trend_long', 0) - signal_scores.get('trend_short', 0),
            signal_scores.get('momentum_long', 0) - signal_scores.get('momentum_short', 0)
        ]
        
        # 計算指標方向一致性
        positive_scores = len([s for s in scores if s > 0])
        total_scores = len(scores)
        
        return positive_scores / total_scores if total_scores > 0 else 0
    
    def _generate_reasoning(
        self,
        signal_type: str,
        indicators: Dict[str, IndicatorResult],
        signal_scores: Dict
    ) -> str:
        """生成信號推理說明"""
        
        reasons = []
        
        # 市場結構
        market_structure = signal_scores.get('market_structure', 'NEUTRAL')
        if market_structure != 'NEUTRAL':
            reasons.append(f"市場結構呈現{market_structure}態勢")
        
        # 強勢指標
        strong_indicators = []
        for name, indicator in indicators.items():
            if indicator.strength > 70 and indicator.signal != 'NEUTRAL':
                strong_indicators.append(f"{name}({indicator.signal})")
        
        if strong_indicators:
            reasons.append(f"強勢指標: {', '.join(strong_indicators)}")
        
        # 趨勢確認
        trend_score = signal_scores.get('trend_long', 0) if signal_type == 'LONG' else signal_scores.get('trend_short', 0)
        if trend_score > 60:
            reasons.append(f"趨勢指標強力支持{signal_type}方向")
        
        # 動量確認
        momentum_score = signal_scores.get('momentum_long', 0) if signal_type == 'LONG' else signal_scores.get('momentum_short', 0)
        if momentum_score > 60:
            reasons.append(f"動量指標確認{signal_type}信號")
        
        if not reasons:
            reasons.append(f"多重技術指標收斂指向{signal_type}方向")
        
        return "; ".join(reasons)
    
    async def save_signal(self, signal: TradeSignal):
        """儲存交易信號到資料庫"""
        async with AsyncSessionLocal() as session:
            try:
                trading_signal = TradingSignal(
                    symbol=signal.symbol,
                    timeframe=signal.timeframe,
                    signal_type=signal.signal_type.value,
                    signal_strength=signal.signal_strength,
                    entry_price=signal.entry_price,
                    stop_loss=signal.stop_loss,
                    take_profit=signal.take_profit,
                    risk_reward_ratio=signal.risk_reward_ratio,
                    confidence=signal.confidence,
                    indicators_used=signal.indicators_used,
                    reasoning=signal.reasoning,
                    expires_at=signal.expires_at
                )
                
                session.add(trading_signal)
                await session.commit()
                
                # 儲存到活躍信號快取
                key = f"{signal.symbol}_{signal.timeframe}"
                self.active_signals[key] = signal
                
            except Exception as e:
                await session.rollback()
                logger.error(f"儲存信號失敗: {e}")
    
    async def stop(self):
        """停止策略引擎"""
        self.running = False
        logger.info("策略引擎已停止")
