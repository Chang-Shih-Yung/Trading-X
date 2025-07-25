import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from app.services.market_data import MarketDataService
from app.services.technical_indicators import TechnicalIndicatorsService, IndicatorResult
from app.services.candlestick_patterns import analyze_candlestick_patterns, PatternResult, PatternType
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

class MarketTrend(Enum):
    """市場趨勢類型"""
    BULL = "BULL"
    BEAR = "BEAR"
    NEUTRAL = "NEUTRAL"
    SIDEWAYS = "SIDEWAYS"

@dataclass
class MarketCondition:
    """市場狀況結構"""
    trend: MarketTrend
    strength: float  # 趨勢強度 0-1
    duration_days: int  # 趨勢持續天數
    confidence: float  # 判斷信心度 0-1
    key_levels: Dict[str, float]  # 關鍵支撐阻力位
    volatility: str  # 高/中/低波動
    momentum: str  # 強/中/弱動量

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
    """進階策略引擎 - 整合K線形態與多時間框架分析"""
    
    def __init__(self):
        self.market_service = MarketDataService()
        self.indicators_service = TechnicalIndicatorsService()
        self.running = False
        self.active_signals = {}
        
        # 策略參數
        self.min_risk_reward = settings.MIN_RISK_REWARD_RATIO
        self.risk_percentage = settings.DEFAULT_RISK_PERCENTAGE
        
        # 牛熊市趨勢緩存
        self.market_conditions = {}
        self.last_trend_analysis = {}
        
        # 新增：多時間框架權重配置
        self.timeframe_weights = {
            '1w': 0.40,   # 週線權重最高
            '1d': 0.35,   # 日線權重次之
            '4h': 0.15,   # 4小時權重較低
            '1h': 0.10    # 1小時權重最低
        }
        
        # 新增：分析優先級 - K線形態優先於技術指標
        self.analysis_priority = {
            'candlestick_patterns': 0.60,  # K線形態佔60%權重
            'technical_indicators': 0.40   # 技術指標佔40%權重  
        }
        
        # 牛熊市策略參數調整
        self.bull_market_params = {
            'confidence_threshold': 0.65,  # 牛市較低信心度門檻
            'risk_reward_min': 1.5,        # 牛市較低風險回報比
            'stop_loss_pct': 0.035,        # 牛市較緊止損 3.5%
            'take_profit_pct': 0.08,       # 牛市較緊止盈 8%
            'long_bias': 0.15              # 做多傾向加成
        }
        
        self.bear_market_params = {
            'confidence_threshold': 0.75,  # 熊市較高信心度門檻
            'risk_reward_min': 2.5,        # 熊市較高風險回報比
            'stop_loss_pct': 0.025,        # 熊市較緊止損 2.5%
            'take_profit_pct': 0.06,       # 熊市較保守止盈 6%
            'short_bias': 0.15             # 做空傾向加成
        }
        
    async def start_signal_generation(self):
        """啟動信號生成 - 多時間框架分析"""
        self.running = True
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']  # 五個主要幣種
        timeframes = ['1h', '4h', '1d', '1w']  # 增加週線分析
        
        while self.running:
            try:
                tasks = []
                for symbol in symbols:
                    # 每個幣種進行多時間框架綜合分析
                    task = asyncio.create_task(
                        self.multi_timeframe_analysis(symbol, timeframes)
                    )
                    tasks.append(task)
                
                # 並行分析所有交易對
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 記錄分析結果
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"分析{symbols[i]}時發生錯誤: {result}")
                    elif result:
                        logger.info(f"生成{symbols[i]}交易信號: {result.signal_type.value}, 信心度: {result.confidence:.2f}")
                
                # 每5分鐘重新分析
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"策略引擎錯誤: {e}")
                await asyncio.sleep(60)
    
    async def analyze_market_trend(self, symbol: str) -> MarketCondition:
        """分析市場趨勢 - 牛熊市判斷"""
        try:
            # 獲取長期歷史數據進行趨勢分析
            daily_data = await self.market_service.get_historical_data(symbol, '1d', limit=90)  # 90天數據
            weekly_data = await self.market_service.get_historical_data(symbol, '1w', limit=26) # 26週數據
            
            if daily_data.empty or weekly_data.empty:
                return MarketCondition(
                    trend=MarketTrend.NEUTRAL,
                    strength=0.5,
                    duration_days=0,
                    confidence=0.3,
                    key_levels={},
                    volatility="中",
                    momentum="中"
                )
            
            # 1. 價格趨勢分析
            current_price = daily_data['close'].iloc[-1]
            ma20 = daily_data['close'].rolling(20).mean().iloc[-1]
            ma50 = daily_data['close'].rolling(50).mean().iloc[-1]
            ma200 = weekly_data['close'].rolling(20).mean().iloc[-1] if len(weekly_data) >= 20 else current_price
            
            # 2. 動量分析
            price_change_30d = (current_price - daily_data['close'].iloc[-30]) / daily_data['close'].iloc[-30]
            price_change_7d = (current_price - daily_data['close'].iloc[-7]) / daily_data['close'].iloc[-7]
            
            # 3. 波動性分析
            volatility_30d = daily_data['close'].pct_change().rolling(30).std().iloc[-1]
            
            # 4. 趨勢強度計算
            trend_score = 0.0
            trend_indicators = []
            
            # 移動平均線排列
            if current_price > ma20 > ma50:
                trend_score += 0.3
                trend_indicators.append("均線多頭排列")
            elif current_price < ma20 < ma50:
                trend_score -= 0.3
                trend_indicators.append("均線空頭排列")
            
            # 價格相對於長期均線位置
            if current_price > ma200 * 1.1:  # 高於年線10%
                trend_score += 0.25
                trend_indicators.append("強勢突破年線")
            elif current_price < ma200 * 0.9:  # 低於年線10%
                trend_score -= 0.25
                trend_indicators.append("弱勢跌破年線")
            
            # 短期動量
            if price_change_7d > 0.05:  # 7天漲超過5%
                trend_score += 0.2
                trend_indicators.append("短期強勢")
            elif price_change_7d < -0.05:  # 7天跌超過5%
                trend_score -= 0.2
                trend_indicators.append("短期弱勢")
            
            # 中期動量
            if price_change_30d > 0.15:  # 30天漲超過15%
                trend_score += 0.25
                trend_indicators.append("中期牛市")
            elif price_change_30d < -0.15:  # 30天跌超過15%
                trend_score -= 0.25
                trend_indicators.append("中期熊市")
            
            # 5. 確定趨勢類型
            if trend_score > 0.5:
                trend = MarketTrend.BULL
                strength = min(trend_score, 1.0)
            elif trend_score < -0.5:
                trend = MarketTrend.BEAR
                strength = min(abs(trend_score), 1.0)
            elif abs(trend_score) <= 0.2:
                trend = MarketTrend.SIDEWAYS
                strength = 0.3
            else:
                trend = MarketTrend.NEUTRAL
                strength = abs(trend_score)
            
            # 6. 波動性分級
            if volatility_30d > 0.05:
                volatility = "高"
            elif volatility_30d > 0.03:
                volatility = "中"
            else:
                volatility = "低"
            
            # 7. 動量分級
            momentum_score = (price_change_7d * 0.3 + price_change_30d * 0.7)
            if momentum_score > 0.1:
                momentum = "強"
            elif momentum_score > 0.02:
                momentum = "中"
            elif momentum_score > -0.02:
                momentum = "中"
            elif momentum_score > -0.1:
                momentum = "弱"
            else:
                momentum = "極弱"
            
            # 8. 關鍵支撐阻力位
            recent_high = daily_data['high'].rolling(20).max().iloc[-1]
            recent_low = daily_data['low'].rolling(20).min().iloc[-1]
            
            key_levels = {
                'support': recent_low,
                'resistance': recent_high,
                'ma20': ma20,
                'ma50': ma50,
                'ma200': ma200
            }
            
            # 9. 信心度計算
            confidence = 0.5 + abs(trend_score) * 0.4  # 基礎信心度
            if len(trend_indicators) >= 3:
                confidence += 0.1  # 多重確認加成
            if volatility == "低":
                confidence += 0.05  # 低波動加成
            
            confidence = min(confidence, 0.95)
            
            # 10. 趨勢持續天數估算
            duration_days = self._estimate_trend_duration(daily_data, trend)
            
            market_condition = MarketCondition(
                trend=trend,
                strength=strength,
                duration_days=duration_days,
                confidence=confidence,
                key_levels=key_levels,
                volatility=volatility,
                momentum=momentum
            )
            
            # 緩存結果（5分鐘有效）
            self.market_conditions[symbol] = market_condition
            self.last_trend_analysis[symbol] = datetime.now()
            
            logger.info(f"{symbol} 市場趨勢分析: {trend.value} 強度:{strength:.2f} 信心度:{confidence:.2f}")
            
            return market_condition
            
        except Exception as e:
            logger.error(f"市場趨勢分析失敗 {symbol}: {e}")
            return MarketCondition(
                trend=MarketTrend.NEUTRAL,
                strength=0.5,
                duration_days=0,
                confidence=0.3,
                key_levels={},
                volatility="中",
                momentum="中"
            )
    
    def _estimate_trend_duration(self, data: pd.DataFrame, trend: MarketTrend) -> int:
        """估算趨勢持續天數"""
        if len(data) < 10:
            return 0
        
        try:
            ma20 = data['close'].rolling(20).mean()
            current_price = data['close'].iloc[-1]
            
            if trend == MarketTrend.BULL:
                # 尋找價格持續高於MA20的天數
                above_ma = data['close'] > ma20
                duration = 0
                for i in range(len(above_ma)-1, -1, -1):
                    if above_ma.iloc[i]:
                        duration += 1
                    else:
                        break
                return duration
            
            elif trend == MarketTrend.BEAR:
                # 尋找價格持續低於MA20的天數
                below_ma = data['close'] < ma20
                duration = 0
                for i in range(len(below_ma)-1, -1, -1):
                    if below_ma.iloc[i]:
                        duration += 1
                    else:
                        break
                return duration
            
            return 0
        except:
            return 0
    
    async def multi_timeframe_analysis(self, symbol: str, timeframes: List[str]) -> Optional[TradeSignal]:
        """多時間框架綜合分析 - 整合牛熊市判斷"""
        try:
            # 0. 首要步驟：分析市場趨勢（牛熊市判斷）
            market_condition = await self.get_or_analyze_market_trend(symbol)
            
            timeframe_signals = {}
            pattern_signals = {}
            
            # 1. 對每個時間框架進行分析
            for tf in timeframes:
                # 獲取市場數據
                df = await self.market_service.get_market_data_from_db(symbol, tf, limit=200)
                
                if df.empty or len(df) < 50:
                    # 如果資料庫沒有數據，從交易所獲取
                    df = await self.market_service.get_historical_data(symbol, tf, limit=200)
                    if not df.empty:
                        await self.market_service.save_market_data(df)
                
                if df.empty:
                    continue
                
                # 技術指標分析
                indicators = self.indicators_service.calculate_all_indicators(df)
                indicator_signal = self._analyze_technical_indicators(indicators, df, tf)
                
                # K線形態分析（重點！）
                pattern_analysis = analyze_candlestick_patterns(df, tf)
                
                timeframe_signals[tf] = {
                    'indicators': indicator_signal,
                    'patterns': pattern_analysis,
                    'price': float(df['close'].iloc[-1])
                }
            
            # 2. 綜合多時間框架信號 - 加入市場趨勢判斷
            final_signal = self._combine_timeframe_signals_with_trend(timeframe_signals, symbol, market_condition)
            
            if final_signal:
                # 根據牛熊市調整信心度門檻
                confidence_threshold = self._get_confidence_threshold(market_condition)
                
                if final_signal.confidence >= confidence_threshold:
                    await self.save_signal(final_signal)
                    logger.info(f"生成{market_condition.trend.value}市場信號: {symbol} {final_signal.signal_type.value} 信心度: {final_signal.confidence:.2f}")
                    return final_signal
            
            return None
            
        except Exception as e:
            logger.error(f"多時間框架分析 {symbol} 失敗: {e}")
            return None
    
    async def get_or_analyze_market_trend(self, symbol: str) -> MarketCondition:
        """獲取或分析市場趨勢（帶緩存）"""
        # 檢查緩存是否有效（5分鐘內的分析結果）
        if symbol in self.market_conditions and symbol in self.last_trend_analysis:
            last_analysis_time = self.last_trend_analysis[symbol]
            if (datetime.now() - last_analysis_time).total_seconds() < 300:  # 5分鐘緩存
                return self.market_conditions[symbol]
        
        # 重新分析
        return await self.analyze_market_trend(symbol)
    
    def _get_confidence_threshold(self, market_condition: MarketCondition) -> float:
        """根據市場狀況獲取信心度門檻"""
        if market_condition.trend == MarketTrend.BULL:
            return self.bull_market_params['confidence_threshold']
        elif market_condition.trend == MarketTrend.BEAR:
            return self.bear_market_params['confidence_threshold']
        else:
            return 0.7  # 中性/橫盤市場使用標準門檻

    def _combine_timeframe_signals_with_trend(self, timeframe_signals: Dict, symbol: str, market_condition: MarketCondition) -> Optional[TradeSignal]:
        """綜合多時間框架信號 - 整合牛熊市判斷的高敏感度設計"""
        
        if not timeframe_signals:
            return None
        
        # 初始化得分
        total_bullish_score = 0.0
        total_bearish_score = 0.0
        total_weight = 0.0
        
        # 關鍵價位信息
        entry_prices = []
        stop_losses = []
        take_profits = []
        
        primary_timeframe = None
        primary_pattern = None
        confidence_boost = 0.0
        
        # 【關鍵】牛熊市敏感度調整 - 根據市場趨勢調整權重
        trend_bias = 0.0
        if market_condition.trend == MarketTrend.BULL:
            trend_bias = self.bull_market_params['long_bias']  # 牛市做多偏向
            logger.info(f"{symbol} 牛市環境，做多偏向 +{trend_bias:.2f}")
        elif market_condition.trend == MarketTrend.BEAR:
            trend_bias = -self.bear_market_params['short_bias']  # 熊市做空偏向
            logger.info(f"{symbol} 熊市環境，做空偏向 {trend_bias:.2f}")
        
        # 遍歷每個時間框架
        for tf, signals in timeframe_signals.items():
            tf_weight = self.timeframe_weights.get(tf, 0.1)
            
            # 1. K線形態分析（優先級最高）
            pattern_data = signals.get('patterns', {})
            if pattern_data.get('has_pattern', False):
                primary_pattern = pattern_data['primary_pattern']
                pattern_score = pattern_data['combined_score']
                
                # K線形態權重加成
                pattern_weight = self.analysis_priority['candlestick_patterns'] * tf_weight
                
                if primary_pattern.pattern_type == PatternType.BULLISH:
                    bullish_adjustment = pattern_score * pattern_weight
                    # 【核心】牛市環境下，看多形態獲得額外加成
                    if market_condition.trend == MarketTrend.BULL:
                        bullish_adjustment *= (1 + market_condition.strength * 0.3)
                        logger.debug(f"{symbol} {tf} 牛市看多形態加成: {bullish_adjustment:.3f}")
                    total_bullish_score += bullish_adjustment
                    
                elif primary_pattern.pattern_type == PatternType.BEARISH:
                    bearish_adjustment = pattern_score * pattern_weight
                    # 【核心】熊市環境下，看空形態獲得額外加成
                    if market_condition.trend == MarketTrend.BEAR:
                        bearish_adjustment *= (1 + market_condition.strength * 0.3)
                        logger.debug(f"{symbol} {tf} 熊市看空形態加成: {bearish_adjustment:.3f}")
                    total_bearish_score += bearish_adjustment
                
                # 如果是高級形態，給予額外信心度加成
                high_priority_patterns = ['頭肩頂', '黃昏十字星', '黃昏之星', '早晨之星', '早晨十字星']
                if primary_pattern.pattern_name in high_priority_patterns:
                    confidence_boost = 0.15
                    primary_timeframe = tf
                
                # 收集價位信息
                entry_prices.append(primary_pattern.entry_price)
                stop_losses.append(primary_pattern.stop_loss)
                take_profits.append(primary_pattern.take_profit)
            
            # 2. 技術指標分析（輔助確認）
            indicator_signal = signals.get('indicators', {})
            if indicator_signal:
                indicator_weight = self.analysis_priority['technical_indicators'] * tf_weight
                
                if indicator_signal.get('overall_signal') == 'BUY':
                    buy_adjustment = indicator_signal.get('confidence', 0.5) * indicator_weight
                    # 牛市環境下，買入信號獲得加成
                    if market_condition.trend == MarketTrend.BULL:
                        buy_adjustment *= (1 + market_condition.strength * 0.2)
                    total_bullish_score += buy_adjustment
                    
                elif indicator_signal.get('overall_signal') == 'SELL':
                    sell_adjustment = indicator_signal.get('confidence', 0.5) * indicator_weight
                    # 熊市環境下，賣出信號獲得加成
                    if market_condition.trend == MarketTrend.BEAR:
                        sell_adjustment *= (1 + market_condition.strength * 0.2)
                    total_bearish_score += sell_adjustment
            
            total_weight += tf_weight
        
        # 標準化得分
        if total_weight > 0:
            total_bullish_score /= total_weight
            total_bearish_score /= total_weight
        
        # 【關鍵】應用牛熊市偏向調整
        total_bullish_score += max(0, trend_bias)  # 牛市加成做多
        total_bearish_score += max(0, -trend_bias)  # 熊市加成做空
        
        # 決定最終信號 - 根據市場環境調整門檻
        signal_type = None
        confidence = 0.0
        
        # 牛市環境：降低做多門檻，提高做空門檻
        if market_condition.trend == MarketTrend.BULL:
            long_threshold = 0.55  # 牛市做多門檻降低
            short_threshold = 0.75  # 牛市做空門檻提高
        # 熊市環境：提高做多門檻，降低做空門檻
        elif market_condition.trend == MarketTrend.BEAR:
            long_threshold = 0.75  # 熊市做多門檻提高
            short_threshold = 0.55  # 熊市做空門檻降低
        # 中性/橫盤市場：使用標準門檻
        else:
            long_threshold = 0.65
            short_threshold = 0.65
        
        if total_bullish_score > total_bearish_score and total_bullish_score > long_threshold:
            signal_type = SignalType.LONG
            confidence = total_bullish_score + confidence_boost
            logger.info(f"{symbol} 生成做多信號 (牛熊敏感): 得分{total_bullish_score:.3f} > 門檻{long_threshold}")
            
        elif total_bearish_score > total_bullish_score and total_bearish_score > short_threshold:
            signal_type = SignalType.SHORT
            confidence = total_bearish_score + confidence_boost
            logger.info(f"{symbol} 生成做空信號 (牛熊敏感): 得分{total_bearish_score:.3f} > 門檻{short_threshold}")
            
        else:
            signal_type = SignalType.HOLD
            confidence = max(total_bullish_score, total_bearish_score)
        
        # 市場條件加成：強趨勢市場額外信心度
        if market_condition.strength > 0.7:
            confidence += 0.05
            logger.debug(f"{symbol} 強趨勢市場信心度加成 +0.05")
        
        # 確保信心度不超過1.0
        confidence = min(confidence, 0.98)
        
        # 根據市場環境調整信心度門檻
        min_confidence = self._get_confidence_threshold(market_condition)
        if confidence < min_confidence:
            logger.debug(f"{symbol} 信心度 {confidence:.3f} 低於 {market_condition.trend.value} 市場門檻 {min_confidence:.3f}")
            return None
        
        # 計算進場參數 - 根據牛熊市調整
        if entry_prices:
            avg_entry = np.mean(entry_prices)
            avg_stop = np.mean(stop_losses) 
            avg_target = np.mean(take_profits)
        else:
            # 根據市場環境調整風險管理參數
            current_price = list(timeframe_signals.values())[0]['price']
            
            if market_condition.trend == MarketTrend.BULL:
                # 牛市參數：較緊止損，較寬止盈
                stop_pct = self.bull_market_params['stop_loss_pct']
                profit_pct = self.bull_market_params['take_profit_pct']
            elif market_condition.trend == MarketTrend.BEAR:
                # 熊市參數：較緊止損，較保守止盈
                stop_pct = self.bear_market_params['stop_loss_pct']
                profit_pct = self.bear_market_params['take_profit_pct']
            else:
                # 中性市場：標準參數
                stop_pct = 0.03
                profit_pct = 0.06
            
            if signal_type == SignalType.LONG:
                avg_entry = current_price * 1.002
                avg_stop = current_price * (1 - stop_pct)
                avg_target = current_price * (1 + profit_pct)
            else:
                avg_entry = current_price * 0.998
                avg_stop = current_price * (1 + stop_pct)
                avg_target = current_price * (1 - profit_pct)
        
        # 計算風險回報比
        risk_amount = abs(avg_entry - avg_stop)
        reward_amount = abs(avg_target - avg_entry)
        risk_reward_ratio = reward_amount / risk_amount if risk_amount > 0 else 0
        
        # 根據市場環境檢查最小風險回報比
        min_rr = self._get_min_risk_reward(market_condition)
        if risk_reward_ratio < min_rr:
            logger.debug(f"{symbol} 風險回報比 {risk_reward_ratio:.2f} 低於 {market_condition.trend.value} 市場要求 {min_rr:.2f}")
            return None
        
        # 計算信號過期時間
        expires_at = datetime.now() + timedelta(hours=24)
        
        # 構建推理說明
        reasoning_parts = [
            f"多時間框架分析 ({len(timeframe_signals)}個時間軸)",
            f"{market_condition.trend.value}市場環境 (強度:{market_condition.strength:.2f})",
            f"信心度: {confidence:.2f}"
        ]
        
        if primary_pattern:
            reasoning_parts.append(f"關鍵形態: {primary_pattern.pattern_name}")
        
        reasoning = " | ".join(reasoning_parts)
        
        # 創建交易信號
        signal = TradeSignal(
            symbol=symbol,
            timeframe=primary_timeframe or '4h',
            signal_type=signal_type,
            entry_price=avg_entry,
            stop_loss=avg_stop,
            take_profit=avg_target,
            risk_reward_ratio=risk_reward_ratio,
            confidence=confidence,
            signal_strength=max(total_bullish_score, total_bearish_score),
            reasoning=reasoning,
            indicators_used={
                'market_trend': market_condition.trend.value,
                'trend_strength': market_condition.strength,
                'bullish_score': total_bullish_score,
                'bearish_score': total_bearish_score,
                'trend_bias': trend_bias
            },
            expires_at=expires_at
        )
        
        return signal
    
    def _get_min_risk_reward(self, market_condition: MarketCondition) -> float:
        """根據市場狀況獲取最小風險回報比"""
        if market_condition.trend == MarketTrend.BULL:
            return self.bull_market_params['risk_reward_min']
        elif market_condition.trend == MarketTrend.BEAR:
            return self.bear_market_params['risk_reward_min']
        else:
            return 2.0  # 中性/橫盤市場使用標準比例
        """綜合多時間框架信號 - K線形態優先策略"""
        
        if not timeframe_signals:
            return None
        
        # 初始化得分
        total_bullish_score = 0.0
        total_bearish_score = 0.0
        total_weight = 0.0
        
        # 關鍵價位信息
        entry_prices = []
        stop_losses = []
        take_profits = []
        
        primary_timeframe = None
        primary_pattern = None
        confidence_boost = 0.0
        
        # 遍歷每個時間框架
        for tf, signals in timeframe_signals.items():
            tf_weight = self.timeframe_weights.get(tf, 0.1)
            
            # 1. K線形態分析（優先級最高）
            pattern_data = signals.get('patterns', {})
            if pattern_data.get('has_pattern', False):
                primary_pattern = pattern_data['primary_pattern']
                pattern_score = pattern_data['combined_score']
                
                # K線形態權重加成
                pattern_weight = self.analysis_priority['candlestick_patterns'] * tf_weight
                
                if primary_pattern.pattern_type == PatternType.BULLISH:
                    total_bullish_score += pattern_score * pattern_weight
                elif primary_pattern.pattern_type == PatternType.BEARISH:
                    total_bearish_score += pattern_score * pattern_weight
                
                # 如果是高級形態（頭肩頂、黃昏十字星等），給予額外信心度加成
                high_priority_patterns = ['頭肩頂', '黃昏十字星', '黃昏之星', '早晨之星', '早晨十字星']
                if primary_pattern.pattern_name in high_priority_patterns:
                    confidence_boost = 0.15  # 15%信心度加成
                    primary_timeframe = tf
                
                # 收集價位信息
                entry_prices.append(primary_pattern.entry_price)
                stop_losses.append(primary_pattern.stop_loss)
                take_profits.append(primary_pattern.take_profit)
            
            # 2. 技術指標分析（輔助確認）
            indicator_signal = signals.get('indicators', {})
            if indicator_signal:
                indicator_weight = self.analysis_priority['technical_indicators'] * tf_weight
                
                if indicator_signal.get('overall_signal') == 'BUY':
                    total_bullish_score += indicator_signal.get('confidence', 0.5) * indicator_weight
                elif indicator_signal.get('overall_signal') == 'SELL':
                    total_bearish_score += indicator_signal.get('confidence', 0.5) * indicator_weight
            
            total_weight += tf_weight
        
        # 標準化得分
        if total_weight > 0:
            total_bullish_score /= total_weight
            total_bearish_score /= total_weight
        
        # 決定最終信號
        signal_type = None
        confidence = 0.0
        
        if total_bullish_score > total_bearish_score and total_bullish_score > 0.6:
            signal_type = SignalType.LONG
            confidence = total_bullish_score + confidence_boost
        elif total_bearish_score > total_bullish_score and total_bearish_score > 0.6:
            signal_type = SignalType.SHORT
            confidence = total_bearish_score + confidence_boost
        else:
            signal_type = SignalType.HOLD
            confidence = max(total_bullish_score, total_bearish_score)
        
        # 確保信心度不超過1.0
        confidence = min(confidence, 0.98)
        
        # 如果沒有足夠的信號強度，返回None
        if confidence < 0.6:
            return None
        
        # 計算進場參數
        if entry_prices:
            avg_entry = np.mean(entry_prices)
            avg_stop = np.mean(stop_losses) 
            avg_target = np.mean(take_profits)
        else:
            # 如果沒有形態信號，使用技術指標的默認設置
            current_price = list(timeframe_signals.values())[0]['price']
            if signal_type == SignalType.LONG:
                avg_entry = current_price * 1.002
                avg_stop = current_price * 0.96  # 4%止損
                avg_target = current_price * 1.12  # 12%獲利
            else:
                avg_entry = current_price * 0.998
                avg_stop = current_price * 1.04  # 4%止損
                avg_target = current_price * 0.88  # 12%獲利
        
        # 計算風險報酬比
        risk_reward = abs(avg_target - avg_entry) / abs(avg_stop - avg_entry) if avg_stop != avg_entry else 1.0
        
        # 生成推理說明
        reasoning_parts = []
        if primary_pattern:
            reasoning_parts.append(f"檢測到{primary_pattern.pattern_name}形態(信心度:{primary_pattern.confidence:.2f})")
        
        if primary_timeframe:
            reasoning_parts.append(f"主要信號來自{primary_timeframe}時間框架")
        
        reasoning_parts.append(f"多時間框架綜合分析結果")
        
        return TradeSignal(
            symbol=symbol,
            timeframe=primary_timeframe or '1d',
            signal_type=signal_type,
            entry_price=avg_entry,
            stop_loss=avg_stop,
            take_profit=avg_target,
            risk_reward_ratio=risk_reward,
            confidence=confidence,
            signal_strength=confidence,
            reasoning=' | '.join(reasoning_parts),
            indicators_used={'pattern_analysis': True, 'multi_timeframe': True},
            expires_at=datetime.now() + timedelta(hours=24)
        )

    async def analyze_symbol(self, symbol: str, timeframe: str) -> Optional[TradeSignal]:
        
        # 計算綜合信號強度
        signal_scores = self._calculate_signal_scores(indicators, multi_timeframe_signals)
        
        # 判斷主要信號方向
        long_score = signal_scores['long_score']
        short_score = signal_scores['short_score']
        
        # 信號閾值 (降低閾值，更容易觸發信號)
        signal_threshold = 40  # 從 60 降低到 40
        
        if long_score >= signal_threshold and long_score > short_score:
            return await self._create_long_signal(
                df, indicators, symbol, timeframe, current_price, long_score, signal_scores
            )
        elif short_score >= signal_threshold and short_score > long_score:
            return await self._create_short_signal(
                df, indicators, symbol, timeframe, current_price, short_score, signal_scores
            )
        
        return None
    
    def _detect_market_panic(self, indicators: Dict[str, IndicatorResult]) -> float:
        """檢測市場恐慌情況，返回恐慌倍數"""
        panic_score = 0
        multiplier = 1.0
        
        # RSI 急速下跌
        if 'rsi' in indicators:
            rsi_val = indicators['rsi'].value
            if rsi_val < 25:  # 極度超賣
                panic_score += 3
            elif rsi_val < 30:  # 超賣
                panic_score += 2
        
        # MACD 急轉直下
        if 'macd' in indicators:
            macd = indicators['macd']
            # 假設我們有歷史 MACD 數據比較
            if macd.signal == "SELL" and macd.strength > 0.7:
                panic_score += 2
        
        # 布林帶下穿
        if 'bollinger_bands' in indicators:
            bb = indicators['bollinger_bands']
            if bb.signal == "SELL" and bb.strength > 0.6:
                panic_score += 2
        
        # 成交量放大確認
        if 'volume_sma' in indicators:
            vol = indicators['volume_sma']
            if vol.strength > 0.7:  # 成交量放大
                panic_score += 1
        
        # 計算恐慌倍數
        if panic_score >= 6:
            multiplier = 1.5  # 高度恐慌
        elif panic_score >= 4:
            multiplier = 1.3  # 中度恐慌
        elif panic_score >= 2:
            multiplier = 1.1  # 輕微恐慌
        
        return multiplier
    
    def _calculate_signal_scores(
        self,
        indicators: Dict[str, IndicatorResult],
        multi_timeframe_signals: Dict
    ) -> Dict[str, float]:
        """計算綜合信號評分 - 優化權重配置"""
        
        long_score = 0
        short_score = 0
        
        # 🔥 重新優化的權重配置 - 更敏感的做空信號
        weights = {
            'trend': 0.35,      # 趨勢指標權重提高
            'momentum': 0.30,   # 動量指標權重提高（RSI過熱很重要）
            'volatility': 0.20,  # 波動性指標（布林帶突破）
            'volume': 0.10,     # 成交量確認
            'support_resistance': 0.05  # 支撐阻力輔助
        }
        
        # 🎯 增強趨勢判斷
        trend_long_total = 0
        trend_short_total = 0
        trend_count = 0
        
        # EMA 趨勢
        if 'ema' in indicators:
            ema = indicators['ema']
            if ema.signal == "BUY":
                trend_long_total += ema.strength * 100
            elif ema.signal == "SELL":
                trend_short_total += ema.strength * 100
            trend_count += 1
        
        # MACD 動量
        if 'macd' in indicators:
            macd = indicators['macd']
            if macd.signal == "BUY":
                trend_long_total += macd.strength * 100
            elif macd.signal == "SELL":
                trend_short_total += macd.strength * 100
            trend_count += 1
        
        trend_long = trend_long_total / max(trend_count, 1)
        trend_short = trend_short_total / max(trend_count, 1)
        
        # 🚀 增強動量判斷 - 對超買超賣更敏感
        momentum_long_total = 0
        momentum_short_total = 0
        momentum_count = 0
        
        # RSI 超買超賣
        if 'rsi' in indicators:
            rsi = indicators['rsi']
            rsi_val = rsi.value
            
            # 🔥 更激進的 RSI 閾值
            if rsi_val >= 65:  # 降低超買閾值
                momentum_short_total += min((rsi_val - 65) / 35 * 100, 100)
            elif rsi_val <= 35:  # 提高超賣閾值
                momentum_long_total += min((35 - rsi_val) / 35 * 100, 100)
            momentum_count += 1
        
        # Stochastic
        if 'stochastic' in indicators:
            stoch = indicators['stochastic']
            if stoch.signal == "BUY":
                momentum_long_total += stoch.strength * 100
            elif stoch.signal == "SELL":
                momentum_short_total += stoch.strength * 100
            momentum_count += 1
        
        # Williams %R
        if 'williams_r' in indicators:
            willr = indicators['williams_r']
            if willr.signal == "BUY":
                momentum_long_total += willr.strength * 100
            elif willr.signal == "SELL":
                momentum_short_total += willr.strength * 100
            momentum_count += 1
        
        momentum_long = momentum_long_total / max(momentum_count, 1)
        momentum_short = momentum_short_total / max(momentum_count, 1)
        
        # 🎯 波動性指標
        volatility_long_total = 0
        volatility_short_total = 0
        volatility_count = 0
        
        if 'bollinger_bands' in indicators:
            bb = indicators['bollinger_bands']
            if bb.signal == "BUY":
                volatility_long_total += bb.strength * 100
            elif bb.signal == "SELL":
                volatility_short_total += bb.strength * 100
            volatility_count += 1
        
        vol_long = volatility_long_total / max(volatility_count, 1)
        vol_short = volatility_short_total / max(volatility_count, 1)
        
        # 🔊 成交量確認
        volume_long = 0
        volume_short = 0
        
        if 'volume_sma' in indicators:
            vol_sma = indicators['volume_sma']
            if vol_sma.signal == "BUY":
                volume_long = vol_sma.strength * 100
            elif vol_sma.signal == "SELL":
                volume_short = vol_sma.strength * 100
        
        # 📊 支撐阻力
        sr_long = 0
        sr_short = 0
        
        if 'support_resistance' in indicators:
            sr = indicators['support_resistance']
            if sr.signal == "BUY":
                sr_long = sr.strength * 100
            elif sr.signal == "SELL":
                sr_short = sr.strength * 100
        
        # 🎯 計算加權總分
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
        
        # 🚨 市場恐慌加成 - 檢測急跌
        panic_multiplier = self._detect_market_panic(indicators)
        if panic_multiplier > 1:
            short_score *= panic_multiplier
            logger.info(f"市場恐慌檢測，做空信號加強 {panic_multiplier:.2f}x")
        
        # 🔥 多重時間框架確認加分
        if multi_timeframe_signals.get('higher_tf_bullish', False):
            long_score += 15
        if multi_timeframe_signals.get('higher_tf_bearish', False):
            short_score += 20  # 給做空更多加分
        
        # 🎯 市場結構確認
        market_structure = self._analyze_market_structure(indicators)
        if market_structure == 'BULLISH':
            long_score += 10
        elif market_structure == 'BEARISH':
            short_score += 15  # 空頭結構給更多分數
        
        return {
            'long_score': min(long_score, 100),
            'short_score': min(short_score, 100),
            'trend_long': trend_long,
            'trend_short': trend_short,
            'momentum_long': momentum_long,
            'momentum_short': momentum_short,
            'market_structure': market_structure,
            'panic_multiplier': panic_multiplier
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
