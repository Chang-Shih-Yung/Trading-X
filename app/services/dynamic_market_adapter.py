"""
動態市場適應引擎 - Phase 1+2 增強版本
Phase 1: 移除雙重信心度過濾，實現 ATR 動態止損止盈，基於成交量動態調整 RSI 閾值
Phase 2: 整合市場機制識別和Fear & Greed Index，實現機制適應性調整
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
import pandas as pd
import requests
from app.services.market_data import MarketDataService
from app.services.external_market_apis import external_market_apis
from app.utils.time_utils import get_taiwan_now_naive

logger = logging.getLogger(__name__)

@dataclass
class MarketState:
    """市場狀態數據結構 - Phase 1+2 增強版本"""
    symbol: str
    current_price: float
    volatility_score: float     # 0.0-3.0，波動率評分
    volume_strength: float      # 0.0-3.0，成交量強度
    liquidity_score: float      # 0.0-2.0，流動性評分  
    sentiment_multiplier: float # 0.5-2.0，情緒倍數
    atr_value: float           # ATR數值
    atr_percentage: float      # ATR百分比
    
    # Phase 2 新增：市場機制相關
    market_regime: str         # BULL_TREND, BEAR_TREND, SIDEWAYS, etc.
    regime_confidence: float   # 0.0-1.0，機制識別信心度
    fear_greed_index: int      # 0-100，Fear & Greed Index
    fear_greed_level: str      # EXTREME_FEAR, FEAR, NEUTRAL, GREED, EXTREME_GREED
    trend_alignment_score: float  # 0.0-1.0，多時間框架趨勢一致性
    
    analysis_timestamp: datetime

@dataclass  
class DynamicThresholds:
    """動態閾值數據結構 - Phase 1+2 增強版本"""
    confidence_threshold: float    # 動態信心度閾值（移除35%固定限制）
    rsi_oversold: int             # 動態RSI超賣閾值
    rsi_overbought: int           # 動態RSI超買閾值
    stop_loss_percent: float      # ATR動態止損百分比
    take_profit_percent: float    # 動態止盈百分比
    
    # Phase 2 新增：機制適應性參數
    regime_adapted_rsi_period: int       # 基於市場機制的RSI周期
    regime_adapted_ma_fast: int          # 快速移動平均週期
    regime_adapted_ma_slow: int          # 慢速移動平均週期
    regime_adapted_bb_period: int        # 布林帶週期
    position_size_multiplier: float      # 倉位大小倍數（基於機制和F&G）
    holding_period_hours: int            # 建議持倉時間
    
    calculation_timestamp: datetime

class DynamicMarketAdapter:
    """動態市場適應引擎 - Phase 2 增強版本（整合外部 API）"""
    
    def __init__(self):
        self.market_service = MarketDataService()
        self.external_apis = external_market_apis
        self.fear_greed_cache = {"value": 50, "updated": None}
        
    async def get_market_state(self, symbol: str) -> MarketState:
        """
        🎯 Phase 2 增強：權重導向即時市場狀態分析
        優先使用幣安即時API (65%) + Fear & Greed (15%) + 技術分析 (20%)
        """
        try:
            # 🚀 Phase 2 核心：使用權重導向API分析
            phase2_analysis = await self.external_apis.get_phase2_market_analysis(symbol)
            
            # 📊 提取權重數據
            binance_data = phase2_analysis.get("binance_realtime")
            fear_greed_data = phase2_analysis.get("fear_greed_analysis")
            data_weights = phase2_analysis.get("data_weights", {})
            
            # 🔥 優先使用即時幣安數據
            if binance_data:
                current_price = binance_data["current_price"]
                volatility_score = min(3.0, abs(binance_data["price_change_percentage_24h"]) / 3.0)
                volume_strength = binance_data.get("market_activity_score", 1.0)
                liquidity_score = binance_data.get("liquidity_score", 1.0)
                
                logger.info(f"🚀 {symbol} 使用即時API數據: ${current_price:.4f} "
                           f"(權重: {data_weights.get('binance_realtime_weight', 0.65):.0%})")
            else:
                # 🔄 備用：內部計算
                logger.warning(f"⚠️ {symbol} 即時API不可用，使用備用計算")
                df = await self.market_service.get_historical_data(
                    symbol=symbol, timeframe="5m", limit=50, exchange='binance'
                )
                
                if df is None or df.empty:
                    logger.warning(f"無法獲取 {symbol} 備用數據")
                    return self._get_default_market_state(symbol)
                
                current_price = float(df['close'].iloc[-1])
                volatility_score = self._calculate_atr_volatility(df) * 50  # 調整到0-3範圍
                volume_strength = self._calculate_volume_surge(df)
                liquidity_score = max(0.5, 2.0 - self._estimate_spread_ratio(current_price) * 100)
            
            # 😨 優先使用Fear & Greed分析
            if fear_greed_data:
                fear_greed_index = fear_greed_data["value"]
                fear_greed_level = fear_greed_data["level"]
                fg_weight = fear_greed_data["weight_in_decision"]
                
                # 基於真實F&G指數計算情緒倍數
                sentiment_multiplier = 0.6 + (fear_greed_index / 100) * 0.8
                
                logger.info(f"😨 {symbol} 使用真實F&G: {fear_greed_index} ({fear_greed_level}) "
                           f"權重: {fg_weight:.0%}")
            else:
                # 備用情緒計算
                fear_greed_index = 50
                fear_greed_level = "NEUTRAL"
                sentiment_multiplier = 1.0
                logger.warning(f"⚠️ {symbol} F&G API不可用，使用中性值")
            
            # 🎯 Phase 2 市場機制分析（融合即時數據）
            if binance_data:
                # 基於即時數據的機制識別
                price_change_24h = binance_data["price_change_percentage_24h"]
                market_activity = binance_data.get("market_activity_score", 1.0)
                
                if price_change_24h > 3.0 and market_activity > 2.0:
                    market_regime = "BULL_MOMENTUM"
                    regime_confidence = 0.85
                elif price_change_24h < -3.0 and market_activity > 2.0:
                    market_regime = "BEAR_MOMENTUM"  
                    regime_confidence = 0.85
                elif abs(price_change_24h) < 1.0:
                    market_regime = "SIDEWAYS"
                    regime_confidence = 0.70
                elif market_activity > 2.5:
                    market_regime = "VOLATILE"
                    regime_confidence = 0.75
                else:
                    market_regime = "TRENDING"
                    regime_confidence = 0.60
            else:
                # 備用機制識別
                market_regime, regime_confidence = await self._identify_market_regime_simple(symbol)
            
            # 🎯 多時間框架趨勢一致性（基於權重評分）
            market_score = phase2_analysis.get("market_score", 50.0)
            trend_alignment_score = min(1.0, market_score / 100.0)
            
            # 🔹 ATR計算（技術分析20%權重部分）
            atr_percentage = await self._calculate_atr_from_api_or_backup(symbol, binance_data)
            
            return MarketState(
                symbol=symbol,
                current_price=current_price,
                volatility_score=volatility_score,
                volume_strength=volume_strength,
                liquidity_score=liquidity_score,
                sentiment_multiplier=sentiment_multiplier,
                atr_value=atr_percentage * current_price,
                atr_percentage=atr_percentage,
                
                # Phase 2 增強
                market_regime=market_regime,
                regime_confidence=regime_confidence,
                fear_greed_index=fear_greed_index,
                fear_greed_level=fear_greed_level,
                trend_alignment_score=trend_alignment_score,
                
                analysis_timestamp=get_taiwan_now_naive()
            )
            
        except Exception as e:
            logger.error(f"計算 {symbol} Phase 2 市場狀態失敗: {e}")
            return self._get_default_market_state(symbol)
    async def _calculate_atr_from_api_or_backup(self, symbol: str, binance_data: Optional[Dict]) -> float:
        """計算ATR：優先使用API數據，備用歷史計算"""
        try:
            if binance_data and "high_24h" in binance_data and "low_24h" in binance_data:
                # 使用24小時高低點估算ATR
                price_range = binance_data["high_24h"] - binance_data["low_24h"]
                current_price = binance_data["current_price"]
                atr_estimate = price_range / current_price
                
                logger.info(f"🎯 {symbol} 使用API ATR估算: {atr_estimate:.4f}")
                return atr_estimate
            else:
                # 備用：歷史數據計算
                df = await self.market_service.get_historical_data(
                    symbol=symbol, timeframe="5m", limit=50, exchange='binance'
                )
                if df is not None and len(df) > 14:
                    atr_backup = self._calculate_atr_volatility(df)
                    logger.info(f"🔄 {symbol} 使用備用ATR計算: {atr_backup:.4f}")
                    return atr_backup
                else:
                    return 0.02  # 預設2%
        except Exception as e:
            logger.error(f"ATR計算失敗 {symbol}: {e}")
            return 0.02
    
    async def _identify_market_regime_simple(self, symbol: str) -> Tuple[str, float]:
        """簡化版市場機制識別（備用方法）"""
        try:
            df = await self.market_service.get_historical_data(
                symbol=symbol, timeframe="15m", limit=100, exchange='binance'
            )
            
            if df is None or len(df) < 20:
                return "UNKNOWN", 0.5
            
            # 簡單趨勢判斷
            price_change_pct = ((df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20]) * 100
            volatility = df['close'].pct_change().std() * 100
            
            if price_change_pct > 2 and volatility < 3:
                return "BULL_TREND", 0.75
            elif price_change_pct < -2 and volatility < 3:
                return "BEAR_TREND", 0.75
            elif volatility > 5:
                return "VOLATILE", 0.80
            else:
                return "SIDEWAYS", 0.70
                
        except Exception as e:
            logger.error(f"備用機制識別失敗 {symbol}: {e}")
            return "UNKNOWN", 0.5
    
    def _calculate_atr_volatility(self, df: pd.DataFrame, period: int = 14) -> float:
        """計算 ATR 波動率百分比"""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            # 計算真實範圍
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            
            current_atr = atr.iloc[-1]
            current_price = close.iloc[-1]
            
            atr_percent = current_atr / current_price
            return float(atr_percent)
            
        except Exception as e:
            logger.error(f"計算 ATR 失敗: {e}")
            return 0.02  # 預設2%
    
    def _calculate_volume_surge(self, df: pd.DataFrame, period: int = 20) -> float:
        """計算成交量暴增倍數"""
        try:
            volume = df['volume']
            avg_volume = volume.rolling(window=period).mean()
            current_volume = volume.iloc[-1]
            avg_vol = avg_volume.iloc[-1]
            
            if avg_vol > 0:
                volume_ratio = current_volume / avg_vol
                return float(volume_ratio)
            else:
                return 1.0
                
        except Exception as e:
            logger.error(f"計算成交量暴增失敗: {e}")
            return 1.0
    
    def _estimate_spread_ratio(self, price: float) -> float:
        """估算價差比率（基於價格區間）"""
        try:
            # 根據價格區間估算典型價差
            if price > 50000:      # BTC 級別
                return 0.0005      # 0.05%
            elif price > 3000:     # ETH 級別
                return 0.001       # 0.1%
            elif price > 300:      # BNB 級別
                return 0.002       # 0.2%
            elif price > 1:        # 主流幣
                return 0.003       # 0.3%
            else:                  # 小幣種
                return 0.005       # 0.5%
                
        except Exception as e:
            logger.error(f"估算價差失敗: {e}")
            return 0.002
    
    async def _get_sentiment_multiplier(self) -> float:
        """獲取市場情緒倍數（優先使用真實 Fear & Greed API）"""
        try:
            # 🎯 Phase 2 優化：優先使用真實 Fear & Greed Index
            fear_greed = await self.external_apis.get_fear_greed_index()
            
            if fear_greed != 50:  # 50 是 API 失敗時的默認值
                # 使用真實 Fear & Greed Index
                sentiment_multiplier = 0.6 + (fear_greed / 100) * 0.8
                logger.info(f"✅ 使用真實 Fear & Greed Index: {fear_greed} -> {sentiment_multiplier:.3f}")
                return float(sentiment_multiplier)
            
            # 備用：檢查快取的模擬值
            now = datetime.now()
            if (self.fear_greed_cache.get("updated") and 
                now - self.fear_greed_cache["updated"] < timedelta(hours=1)):
                fear_greed = self.fear_greed_cache["value"]
            else:
                # 使用模擬計算
                fear_greed = await self._get_simulated_fear_greed()
                self.fear_greed_cache = {"value": fear_greed, "updated": now}
            
            # 轉換為情緒倍數
            sentiment_multiplier = 0.6 + (fear_greed / 100) * 0.8
            logger.info(f"🔄 使用備用模擬 F&G: {fear_greed} -> {sentiment_multiplier:.3f}")
            return float(sentiment_multiplier)
            
        except Exception as e:
            logger.error(f"獲取情緒倍數失敗: {e}")
            return 1.0  # 預設中性
    
    async def _get_simulated_fear_greed(self) -> float:
        """模擬恐懼貪婪指數（基於價格動量）"""
        try:
            # 使用 BTC 價格動量模擬市場情緒
            df = await self.market_service.get_historical_data(
                symbol="BTCUSDT",
                timeframe="1h",
                limit=24,  # 24小時
                exchange='binance'
            )
            
            if df is not None and len(df) >= 2:
                # 計算24小時漲跌幅
                price_change = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]
                
                # 轉換為0-100分數 (-10%跌 = 0分, +10%漲 = 100分)
                fear_greed = max(0, min(100, 50 + price_change * 500))
                return float(fear_greed)
            else:
                return 50.0  # 預設中性
                
        except Exception as e:
            logger.error(f"模擬恐懼貪婪指數失敗: {e}")
            return 50.0
    
    def calculate_dynamic_confidence_threshold(self, market_state: MarketState) -> float:
        """🎯 Phase 1 核心：動態計算信心度閾值（移除雙重過濾）"""
        
        base_threshold = 0.25  # 基礎25%（移除35%的第二層過濾）
        
        # 🌊 波動率調整：高波動市場降低門檻
        volatility_adjust = max(0.15, 0.35 - (market_state.volatility_score - 1.0) * 0.05)
        
        # 📊 成交量調整：高成交量降低門檻
        volume_adjust = max(0.15, 0.30 - (market_state.volume_strength - 1.0) * 0.03)
        
        # 💧 流動性調整：高流動性降低門檻
        liquidity_adjust = max(0.15, 0.28 - (market_state.liquidity_score - 1.0) * 0.02)
        
        # 🧠 情緒調整：極端情緒時放寬條件
        if market_state.sentiment_multiplier < 0.7 or market_state.sentiment_multiplier > 1.3:
            sentiment_adjust = 0.20  # 極端情緒：更寬鬆
        else:
            sentiment_adjust = min(volatility_adjust, volume_adjust, liquidity_adjust)
        
        final_threshold = min(sentiment_adjust, 0.35)  # 上限35%
        
        logger.info(f"🎯 {market_state.symbol} 動態信心度閾值: {final_threshold:.3f} "
                   f"(波動: {market_state.volatility_score:.2f}, "
                   f"成交量: {market_state.volume_strength:.2f}, "
                   f"情緒: {market_state.sentiment_multiplier:.2f})")
        
        return final_threshold
    
    def get_dynamic_indicator_params(self, market_state: MarketState) -> DynamicThresholds:
        """🔥 Phase 1+2：基於市場狀態和機制動態調整技術指標參數"""
        
        # Phase 1: 基於市場狀態的動態參數
        
        # 🔥 RSI 動態閾值（基於成交量強度）
        if market_state.volume_strength > 2.0:
            # 高成交量：放寬RSI範圍，更多信號機會
            rsi_oversold = 20      # 從30放寬至20
            rsi_overbought = 80    # 從70提高至80
        elif market_state.volume_strength > 1.5:
            # 中高成交量：適度調整
            rsi_oversold = 25
            rsi_overbought = 75
        else:
            # 標準成交量：保守設置
            rsi_oversold = 30
            rsi_overbought = 70
        
        # 🎯 ATR 動態止損止盈
        base_stop_loss = 0.02  # 基礎2%
        atr_multiplier = 1.0 + (market_state.volatility_score - 1.0) * 0.5
        liquidity_multiplier = 2.0 / market_state.liquidity_score
        
        dynamic_stop_loss = base_stop_loss * atr_multiplier * liquidity_multiplier
        dynamic_stop_loss = max(0.01, min(0.05, dynamic_stop_loss))  # 1%-5%範圍
        
        # 動態止盈：基於成交量 + 情緒
        base_take_profit = 0.04  # 基礎4%
        volume_multiplier = 1.0 + (market_state.volume_strength - 1.0) * 0.3
        sentiment_multiplier = market_state.sentiment_multiplier
        
        dynamic_take_profit = base_take_profit * volume_multiplier * sentiment_multiplier
        dynamic_take_profit = max(0.02, min(0.08, dynamic_take_profit))  # 2%-8%範圍
        
        # Phase 2: 基於市場機制的參數調整
        
        # 🎯 機制適應性RSI週期
        if market_state.market_regime == "BULL_TREND":
            regime_rsi_period = 10  # 牛市用更短週期
            regime_ma_fast, regime_ma_slow = 8, 21
            regime_bb_period = 15
        elif market_state.market_regime == "BEAR_TREND":
            regime_rsi_period = 18  # 熊市用更長週期
            regime_ma_fast, regime_ma_slow = 12, 40
            regime_bb_period = 25
        elif market_state.market_regime == "VOLATILE":
            regime_rsi_period = 21  # 高波動用最長週期
            regime_ma_fast, regime_ma_slow = 15, 50
            regime_bb_period = 30
        else:  # SIDEWAYS, ACCUMULATION, DISTRIBUTION
            regime_rsi_period = 14  # 標準週期
            regime_ma_fast, regime_ma_slow = 10, 30
            regime_bb_period = 20
        
        # 🎯 Fear & Greed 調整
        if market_state.fear_greed_level == "EXTREME_FEAR":
            # 極度恐懼：更積極的參數，搶反彈
            position_size_multiplier = 1.2
            holding_period_hours = 2
        elif market_state.fear_greed_level == "EXTREME_GREED":
            # 極度貪婪：更保守的參數
            position_size_multiplier = 0.6
            holding_period_hours = 8
        elif market_state.fear_greed_level in ["FEAR", "GREED"]:
            position_size_multiplier = 0.8
            holding_period_hours = 4
        else:  # NEUTRAL
            position_size_multiplier = 1.0
            holding_period_hours = 6
        
        # 趨勢一致性調整
        if market_state.trend_alignment_score > 0.8:
            # 高趨勢一致性：增加倉位信心
            position_size_multiplier *= 1.3
        elif market_state.trend_alignment_score < 0.3:
            # 低趨勢一致性：減少倉位
            position_size_multiplier *= 0.7
        
        # 機制信心度調整
        position_size_multiplier *= market_state.regime_confidence
        
        return DynamicThresholds(
            confidence_threshold=self.calculate_dynamic_confidence_threshold(market_state),
            rsi_oversold=rsi_oversold,
            rsi_overbought=rsi_overbought,
            stop_loss_percent=dynamic_stop_loss,
            take_profit_percent=dynamic_take_profit,
            
            # Phase 2 新增
            regime_adapted_rsi_period=regime_rsi_period,
            regime_adapted_ma_fast=regime_ma_fast,
            regime_adapted_ma_slow=regime_ma_slow,
            regime_adapted_bb_period=regime_bb_period,
            position_size_multiplier=min(2.0, max(0.2, position_size_multiplier)),
            holding_period_hours=holding_period_hours,
            
            calculation_timestamp=get_taiwan_now_naive()
        )
    
    def _get_default_market_state(self, symbol: str) -> MarketState:
        """返回默認市場狀態 - Phase 1+2 版本"""
        return MarketState(
            symbol=symbol,
            current_price=1.0,
            volatility_score=1.5,
            volume_strength=1.2,
            liquidity_score=1.0,
            sentiment_multiplier=1.0,
            atr_value=0.02,
            atr_percentage=0.02,
            
            # Phase 2 默認值
            market_regime="SIDEWAYS",
            regime_confidence=0.5,
            fear_greed_index=50,
            fear_greed_level="NEUTRAL",
            trend_alignment_score=0.5,
            
            analysis_timestamp=get_taiwan_now_naive()
        )
    
    # ========== Phase 2 新增方法（增強版） ==========
    
    async def _identify_market_regime_enhanced(self, df: pd.DataFrame, external_data: Dict[str, Any]) -> Tuple[str, float]:
        """Phase 2 簡化：市場機制識別（使用內部計算 + Binance 數據）"""
        try:
            # 基礎技術分析（內部計算）
            current_price = df['close'].iloc[-1]
            ma_20 = df['close'].rolling(20).mean().iloc[-1]
            ma_50 = df['close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else ma_20
            
            # 使用內部 RSI 計算
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not rsi.empty else 50
            
            # 機制識別邏輯
            if current_price > ma_20 > ma_50 and current_rsi > 55:
                regime = "BULL_TREND"
                confidence = 0.8
            elif current_price < ma_20 < ma_50 and current_rsi < 45:
                regime = "BEAR_TREND"
                confidence = 0.8
            elif 30 < current_rsi < 70 and abs(ma_20 - ma_50) / ma_50 < 0.02:
                regime = "SIDEWAYS"
                confidence = 0.7
            else:
                regime = "VOLATILE"
                confidence = 0.6
            
            logger.info(f"🔄 使用內部機制識別: {regime} (信心度: {confidence:.2f})")
            
            # 🎯 結合 Binance 24h 數據調整信心度
            if external_data.get("market_data"):
                market_data = external_data["market_data"]
                price_change_24h = market_data.get("price_change_percentage_24h", 0)
                
                # 根據24小時變化調整信心度
                if abs(price_change_24h) > 10:  # 大幅波動
                    if regime == "VOLATILE":
                        confidence = min(0.9, confidence + 0.1)  # 提高 VOLATILE 信心度
                    else:
                        confidence = max(0.5, confidence - 0.1)   # 降低其他機制信心度
                
                logger.info(f"📊 24h變化 {price_change_24h:.2f}% 調整信心度: {confidence:.2f}")
            
            return regime, confidence
            
        except Exception as e:
            logger.error(f"市場機制識別失敗: {e}")
            return "SIDEWAYS", 0.5
    
    async def _calculate_trend_alignment(self, symbol: str) -> float:
        """Phase 2: 計算多時間框架趨勢一致性"""
        try:
            timeframes = ["1m", "5m", "15m"]
            trend_scores = []
            
            for tf in timeframes:
                try:
                    df = await self.market_service.get_historical_data(
                        symbol=symbol, timeframe=tf, limit=20, exchange='binance'
                    )
                    
                    if df is not None and len(df) >= 10:
                        current_price = df['close'].iloc[-1]
                        ma_10 = df['close'].rolling(10).mean().iloc[-1]
                        
                        if current_price > ma_10:
                            trend_scores.append(1.0)  # 上升趨勢
                        elif current_price < ma_10:
                            trend_scores.append(-1.0)  # 下降趨勢
                        else:
                            trend_scores.append(0.0)  # 中性
                            
                except Exception:
                    trend_scores.append(0.0)
            
            # 計算一致性分數（-1到1）
            if trend_scores:
                alignment = abs(sum(trend_scores)) / len(trend_scores)
                return alignment
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"計算趨勢一致性失敗: {e}")
            return 0.5
    
    async def _calculate_fear_greed_index(self, df: pd.DataFrame, symbol: str) -> int:
        """Phase 2：計算Fear & Greed Index（使用外部 API）"""
        try:
            # 使用真實 Fear & Greed Index API
            fear_greed = await self.external_apis.get_fear_greed_index()
            logger.info(f"✅ 使用真實 Fear & Greed Index: {fear_greed}")
            return fear_greed
            
        except Exception as e:
            logger.error(f"獲取Fear & Greed Index失敗: {e}")
            return 50  # 中性默認值
    
    def _get_fear_greed_level(self, index: int) -> str:
        """根據數值確定Fear & Greed等級"""
        if index <= 25:
            return "EXTREME_FEAR"
        elif index <= 45:
            return "FEAR"
        elif index <= 55:
            return "NEUTRAL"
        elif index <= 75:
            return "GREED"
        else:
            return "EXTREME_GREED"

# 全局實例
dynamic_adapter = DynamicMarketAdapter()
