"""
🎯 Phase 2 增強：即時API數據權重優先整合
整合 Binance 即時數據 + Alternative.me Fear & Greed Index
實現市場導向的動態權重調整
"""

import asyncio
import logging
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json

from app.utils.time_utils import get_taiwan_now_naive
from X.app.services.market_data import MarketDataService
from app.services.bull_bear_weight_manager import bull_bear_weight_manager

logger = logging.getLogger(__name__)

@dataclass
class BinanceMarketData:
    """Binance 即時市場數據 - Phase 2 增強版"""
    symbol: str
    current_price: float
    volume_24h: float
    price_change_24h: float
    price_change_percentage_24h: float
    high_24h: float
    low_24h: float
    # Phase 2 新增：交易活躍度指標
    trade_count: int
    weighted_avg_price: float
    # Phase 2 新增：買賣盤指標
    bid_price: float
    ask_price: float
    bid_qty: float
    ask_qty: float
    timestamp: datetime

@dataclass
class FearGreedAnalysis:
    """Fear & Greed 指數分析 - Alternative.me 標準"""
    value: int                    # 0-100
    value_classification: str     # 文字分類
    fear_greed_level: str        # 標準化等級
    weight_in_decision: float    # 在決策中的權重 (0.0-0.25)
    market_interpretation: str   # 市場解讀
    timestamp: datetime

class ExternalMarketAPIs:
    """Phase 2 增強：即時API數據權重優先管理器"""
    
    def __init__(self):
        self.market_service = MarketDataService()
        
        # 🎯 Phase 2 權重分配
        self.data_weights = {
            "binance_realtime": 0.65,    # 65% - 幣安即時數據權重
            "technical_analysis": 0.20,  # 20% - 技術分析權重  
            "fear_greed_sentiment": 0.15 # 15% - 情緒指標權重
        }
        
        # 快取配置：優先即時性
        self.binance_cache = {}
        self.fear_greed_cache = {"value": 50, "level": "NEUTRAL", "updated": None}
        
        # API 配置
        self.alternative_api_url = "https://api.alternative.me"
        self.binance_api_url = "https://api.binance.com/api/v3"
        
        # 請求限制：優化即時性
        self.request_timeout = 8.0
        self.binance_cache_duration = timedelta(minutes=2)    # 2分鐘快取
        self.fear_greed_cache_duration = timedelta(hours=1)   # 每小時更新
    
    async def get_binance_realtime_data(self, symbol: str) -> Optional[BinanceMarketData]:
        """
        🎯 Phase 2 核心：獲取幣安即時數據 (權重 65%)
        僅使用即時 API，不提供備用數據
        """
        try:
            # 檢查快取
            cache_key = f"binance_realtime_{symbol}"
            if self._is_binance_cache_valid(cache_key):
                cached_data = self.binance_cache[cache_key]["data"]
                logger.info(f"📊 使用快取的 {symbol} 即時數據: ${cached_data.current_price:.4f}")
                return cached_data
            
            # 🔥 直接調用 Binance API
            realtime_data = await self._get_binance_api_direct(symbol)
            if realtime_data:
                logger.info(f"🚀 成功獲取 {symbol} 即時API數據: ${realtime_data.current_price:.4f}")
                return realtime_data
            
            # 沒有即時數據時拋出錯誤
            raise ConnectionError(f"無法獲取 {symbol} 的即時數據")
                
        except Exception as e:
            logger.error(f"❌ {symbol} 即時數據獲取失敗: {e}")
            raise e

    async def _get_binance_api_direct(self, symbol: str) -> Optional[BinanceMarketData]:
        """直接調用幣安API獲取即時數據"""
        try:
            async with httpx.AsyncClient(timeout=self.request_timeout) as client:
                # 獲取24小時統計
                ticker_response = await client.get(f"{self.binance_api_url}/ticker/24hr?symbol={symbol}")
                
                if ticker_response.status_code == 200:
                    ticker_data = ticker_response.json()
                    
                    # 構建增強數據結構
                    market_data = BinanceMarketData(
                        symbol=symbol,
                        current_price=float(ticker_data["lastPrice"]),
                        volume_24h=float(ticker_data["volume"]),
                        price_change_24h=float(ticker_data["priceChange"]),
                        price_change_percentage_24h=float(ticker_data["priceChangePercent"]),
                        high_24h=float(ticker_data["highPrice"]),
                        low_24h=float(ticker_data["lowPrice"]),
                        # Phase 2 新增字段
                        trade_count=int(ticker_data["count"]),
                        weighted_avg_price=float(ticker_data["weightedAvgPrice"]),
                        bid_price=float(ticker_data["bidPrice"]),
                        ask_price=float(ticker_data["askPrice"]),
                        bid_qty=float(ticker_data["bidQty"]),
                        ask_qty=float(ticker_data["askQty"]),
                        timestamp=get_taiwan_now_naive()
                    )
                    
                    # 更新快取
                    self.binance_cache[f"binance_realtime_{symbol}"] = {
                        "data": market_data,
                        "timestamp": get_taiwan_now_naive()
                    }
                    
                    return market_data
                
        except Exception as e:
            logger.error(f"直接API調用失敗 {symbol}: {e}")
            # 不提供備用數據，直接拋出錯誤
            raise e
    
    async def get_fear_greed_analysis(self) -> FearGreedAnalysis:
        """
        🎯 獲取 Alternative.me Fear & Greed Index 詳細分析
        每小時更新一次，權重15%
        """
        try:
            # 檢查快取（1小時更新）
            now = get_taiwan_now_naive()
            if (self.fear_greed_cache.get("updated") and 
                now - self.fear_greed_cache["updated"] < self.fear_greed_cache_duration):
                cached_data = self.fear_greed_cache
                return FearGreedAnalysis(
                    value=cached_data["value"],
                    value_classification=cached_data.get("classification", "Neutral"),
                    fear_greed_level=cached_data["level"],
                    weight_in_decision=self._calculate_fear_greed_weight(cached_data["value"]),
                    market_interpretation=self._get_market_interpretation(cached_data["value"]),
                    timestamp=cached_data["updated"]
                )
            
            # 🎯 調用 Alternative.me API
            async with httpx.AsyncClient(timeout=self.request_timeout) as client:
                response = await client.get(f"{self.alternative_api_url}/fng/")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("data") and len(data["data"]) > 0:
                        fear_greed_value = int(data["data"][0]["value"])
                        classification = data["data"][0].get("value_classification", "Neutral")
                        
                        # 📊 Alternative.me 標準分類
                        level = self._get_alternative_fear_greed_level(fear_greed_value)
                        
                        # 更新快取（每小時更新）
                        self.fear_greed_cache = {
                            "value": fear_greed_value,
                            "classification": classification,
                            "level": level,
                            "updated": now
                        }
                        
                        analysis = FearGreedAnalysis(
                            value=fear_greed_value,
                            value_classification=classification,
                            fear_greed_level=level,
                            weight_in_decision=self._calculate_fear_greed_weight(fear_greed_value),
                            market_interpretation=self._get_market_interpretation(fear_greed_value),
                            timestamp=now
                        )
                        
                        logger.info(f"✅ Fear & Greed 更新: {fear_greed_value} ({level}) - 權重: {analysis.weight_in_decision:.1%}")
                        return analysis
                
                logger.warning(f"⚠️ Fear & Greed API 響應異常: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Fear & Greed API 請求失敗: {e}")
            # 不提供默認值，直接拋出錯誤
            raise e
    
    def _get_alternative_fear_greed_level(self, value: int) -> str:
        """
        📊 Alternative.me 官方分類標準
        0–24: Extreme Fear, 25–49: Fear, 50: Neutral, 51–74: Greed, 75–100: Extreme Greed
        """
        if value <= 24:
            return "EXTREME_FEAR"      # 極度恐慌
        elif value <= 49:
            return "FEAR"              # 恐懼  
        elif value == 50:
            return "NEUTRAL"           # 中性
        elif value <= 74:
            return "GREED"             # 貪婪
        else:  # 75-100
            return "EXTREME_GREED"     # 極度貪婪
    
    def _calculate_fear_greed_weight(self, value: int) -> float:
        """
        🎯 Phase 2 動態權重計算
        基礎權重15%，極值時適度調整
        """
        base_weight = self.data_weights["fear_greed_sentiment"]  # 15%
        
        # 極值時稍微提升權重（但不超過25%）
        if value <= 20 or value >= 80:
            return min(0.25, base_weight + 0.10)  # 提升至25%
        elif value <= 30 or value >= 70:
            return min(0.20, base_weight + 0.05)  # 提升至20%
        
        return base_weight  # 標準15%
    
    def _get_market_interpretation(self, value: int) -> str:
        """市場解讀建議"""
        if value <= 24:
            return "極度恐慌，可能是絕佳買入機會，但需謹慎確認底部"
        elif value <= 49:
            return "市場恐懼，投資者保守，可考慮逐步建倉"  
        elif value == 50:
            return "市場情緒中性，無明顯方向偏好"
        elif value <= 74:
            return "市場貪婪，投資者積極，注意風險控制"
        else:
            return "極度貪婪，修正風險加劇，建議謹慎或減倉"
    
    async def get_phase2_market_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        🎯 Phase 2 核心：牛熊動態權重導向市場分析
        自動識別牛熊市場並動態調整權重分配
        """
        try:
            # 🚀 並行獲取高權重數據源
            binance_task = self.get_binance_realtime_data(symbol)
            fear_greed_task = self.get_fear_greed_analysis()
            
            binance_data, fg_analysis = await asyncio.gather(
                binance_task, fear_greed_task, return_exceptions=True
            )
            
            # 處理數據結果
            binance_market = binance_data if not isinstance(binance_data, Exception) else None
            fear_greed = fg_analysis if not isinstance(fg_analysis, Exception) else None
            
            # 🎯 構建市場數據用於牛熊分析
            market_analysis_data = {}
            if binance_market:
                market_analysis_data.update({
                    "price_change_percentage_24h": binance_market.price_change_percentage_24h,
                    "market_activity_score": self._calculate_activity_score(binance_market),
                    "liquidity_score": self._calculate_liquidity_score(binance_market),
                    "volume_24h": binance_market.volume_24h,
                    "trade_count": binance_market.trade_count
                })
            
            if fear_greed:
                market_analysis_data["fear_greed_value"] = fear_greed.value
            
            # 估算ATR（如果有歷史數據）
            market_analysis_data["atr_percentage"] = 0.02  # 預設值，實際可從歷史數據計算
            
            # 🎯 牛熊市場分析和動態權重計算
            regime, regime_confidence, indicator_scores = bull_bear_weight_manager.analyze_market_regime(market_analysis_data)
            dynamic_weights = bull_bear_weight_manager.calculate_dynamic_weights(regime, regime_confidence, market_analysis_data)
            
            # 📊 計算數據質量評分
            data_quality_score = 0.0
            if binance_market:
                data_quality_score += dynamic_weights.binance_realtime_weight * 100
            if fear_greed:
                data_quality_score += dynamic_weights.fear_greed_weight * 100
            
            # 構建 Phase 2 分析結果
            analysis = {
                "symbol": symbol,
                "timestamp": get_taiwan_now_naive().isoformat(),
                "phase": "Phase 2 Bull-Bear Dynamic",
                
                # 🎯 牛熊動態權重狀態
                "market_regime_analysis": {
                    "regime": regime,
                    "confidence": regime_confidence,
                    "regime_indicators": indicator_scores,
                    "justification": dynamic_weights.justification
                },
                
                # 🎯 動態權重分配
                "data_weights": {
                    "binance_realtime_weight": dynamic_weights.binance_realtime_weight,
                    "technical_analysis_weight": dynamic_weights.technical_analysis_weight, 
                    "fear_greed_weight": dynamic_weights.fear_greed_weight,
                    "total_data_quality": data_quality_score,
                    "weight_adjustment_reason": dynamic_weights.justification
                },
                
                # 🎯 數據來源狀態
                "data_sources": {
                    "binance_realtime_available": binance_market is not None,
                    "fear_greed_available": fear_greed is not None,
                    "api_priority": f"{regime.lower()}_optimized"
                },
                
                # 🔥 幣安即時數據 (動態權重)
                "binance_realtime": None,
                
                # 😨 情緒分析 (動態權重)  
                "fear_greed_analysis": None,
                
                # 📊 牛熊指標評分
                "bull_bear_indicators": {
                    "bull_score": sum([0.1 for key, value in indicator_scores.items() if "bull" in key or key in ["activity_surge", "greed_sentiment", "strong_liquidity"]]),
                    "bear_score": sum([0.1 for key, value in indicator_scores.items() if "bear" in key or key in ["fear_sentiment", "weak_liquidity", "high_volatility"]]),
                    "active_indicators": list(indicator_scores.keys())
                },
                
                # 📊 綜合評分
                "market_score": self._calculate_market_score(binance_market, fear_greed),
                "api_status": "success" if binance_market else "partial"
            }
            
            # 🔥 添加幣安即時數據
            if binance_market:
                analysis["binance_realtime"] = {
                    "current_price": binance_market.current_price,
                    "volume_24h": binance_market.volume_24h,
                    "price_change_24h": binance_market.price_change_24h,
                    "price_change_percentage_24h": binance_market.price_change_percentage_24h,
                    "high_24h": binance_market.high_24h,
                    "low_24h": binance_market.low_24h,
                    # Phase 2 新增指標
                    "trade_count_24h": binance_market.trade_count,
                    "weighted_avg_price": binance_market.weighted_avg_price,
                    "current_spread": abs(binance_market.ask_price - binance_market.bid_price),
                    "bid_ask_ratio": binance_market.bid_qty / binance_market.ask_qty if binance_market.ask_qty > 0 else 1.0,
                    # 即時活躍度評分
                    "market_activity_score": self._calculate_activity_score(binance_market),
                    "liquidity_score": self._calculate_liquidity_score(binance_market)
                }
            
            # 😨 添加情緒分析
            if fear_greed:
                analysis["fear_greed_analysis"] = {
                    "value": fear_greed.value,
                    "classification": fear_greed.value_classification,
                    "level": fear_greed.fear_greed_level,
                    "weight_in_decision": dynamic_weights.fear_greed_weight,  # 使用動態權重
                    "market_interpretation": fear_greed.market_interpretation,
                    "last_updated": fear_greed.timestamp.isoformat()
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Phase 2 牛熊動態分析失敗 {symbol}: {e}")
            return {
                "symbol": symbol,
                "timestamp": get_taiwan_now_naive().isoformat(),
                "phase": "Phase 2 Bull-Bear Dynamic",
                "api_status": "error",
                "error": str(e),
                "data_weights": self.data_weights
            }
    
    def _calculate_activity_score(self, binance_data: BinanceMarketData) -> float:
        """計算市場活躍度評分 (0.0-3.0)"""
        try:
            # 交易次數評分 (每小時1000次為基準)
            trade_freq_score = min(2.0, binance_data.trade_count / (24 * 1000))
            
            # 價格波動評分
            volatility_score = min(1.0, abs(binance_data.price_change_percentage_24h) / 10)
            
            return trade_freq_score + volatility_score
        except:
            return 1.0
    
    def _calculate_liquidity_score(self, binance_data: BinanceMarketData) -> float:
        """計算流動性評分 (0.0-2.0)"""
        try:
            # 價差評分 (越小越好)
            spread_percent = abs(binance_data.ask_price - binance_data.bid_price) / binance_data.current_price
            spread_score = max(0.0, 1.0 - spread_percent * 1000)  # 0.1%價差 = 1.0分
            
            # 深度平衡評分
            depth_balance = min(binance_data.bid_qty, binance_data.ask_qty) / max(binance_data.bid_qty, binance_data.ask_qty)
            balance_score = depth_balance
            
            return spread_score + balance_score
        except:
            return 1.0
    
    def _calculate_market_score(self, binance_data: Optional[BinanceMarketData], 
                               fear_greed: Optional[FearGreedAnalysis]) -> float:
        """計算綜合市場評分 (0.0-100.0)"""
        score = 0.0
        
        # 幣安數據評分 (65%權重)
        if binance_data:
            activity_score = self._calculate_activity_score(binance_data)
            liquidity_score = self._calculate_liquidity_score(binance_data)
            binance_score = (activity_score + liquidity_score) / 5.0 * 65  # 歸一化到65分
            score += binance_score
        
        # 情緒評分 (15%權重)
        if fear_greed:
            # 極值時高分，中性時低分
            if fear_greed.value <= 25 or fear_greed.value >= 75:
                emotion_score = 15.0  # 極值給滿分
            elif fear_greed.value <= 35 or fear_greed.value >= 65:
                emotion_score = 10.0  # 中高值
            else:
                emotion_score = 5.0   # 中性低分
            score += emotion_score
        
        # 技術分析預留權重 (20%)
        technical_score = 10.0  # 預設中等分數
        score += technical_score
        
        return round(score, 2)
    
    def _is_binance_cache_valid(self, cache_key: str) -> bool:
        """檢查幣安快取是否有效（2分鐘）"""
        if cache_key not in self.binance_cache:
            return False
            
        cache_time = self.binance_cache[cache_key]["timestamp"]
        return get_taiwan_now_naive() - cache_time < self.binance_cache_duration

# 全局實例
external_market_apis = ExternalMarketAPIs()
