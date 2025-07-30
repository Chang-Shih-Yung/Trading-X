"""
🎯 Phase 3: 高階市場適應 - Order Book 深度分析和資金費率情緒指標
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from app.utils.time_utils import get_taiwan_now_naive

logger = logging.getLogger(__name__)

@dataclass
class OrderBookData:
    """Order Book 數據結構"""
    symbol: str
    timestamp: datetime
    bids: List[Tuple[float, float]]  # (price, quantity)
    asks: List[Tuple[float, float]]  # (price, quantity)
    total_bid_volume: float
    total_ask_volume: float
    pressure_ratio: float
    market_sentiment: str
    bid_ask_spread: float
    mid_price: float
    
@dataclass
class FundingRateData:
    """資金費率數據結構"""
    symbol: str
    funding_rate: float
    funding_time: datetime
    next_funding_time: datetime
    mark_price: float
    sentiment: str
    market_interpretation: str
    annual_rate: float  # 年化費率

@dataclass
class Phase3Analysis:
    """Phase 3 綜合分析"""
    symbol: str
    timestamp: datetime
    order_book: OrderBookData
    funding_rate: FundingRateData
    combined_sentiment: str
    market_pressure_score: float
    trading_recommendation: str
    risk_level: str

class Phase3MarketAnalyzer:
    """Phase 3 高階市場分析器"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_order_book_depth(self, symbol: str = "BTCUSDT", limit: int = 20) -> OrderBookData:
        """
        獲取 Order Book 深度數據
        """
        try:
            url = f"https://api.binance.com/api/v3/depth"
            params = {"symbol": symbol, "limit": limit}
            
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"API 請求失敗: {response.status}")
                    
                data = await response.json()
                
                # 解析買賣盤數據
                bids = [(float(p), float(q)) for p, q in data['bids']]
                asks = [(float(p), float(q)) for p, q in data['asks']]
                
                # 計算總成交量
                total_bid_volume = sum(q for _, q in bids)
                total_ask_volume = sum(q for _, q in asks)
                
                # 計算壓力比
                pressure_ratio = total_bid_volume / (total_ask_volume + 1e-9)
                
                # 分析市場情緒
                if pressure_ratio > 1.5:
                    sentiment = "BULLISH_PRESSURE"  # 買單強勢
                elif pressure_ratio < 0.7:
                    sentiment = "BEARISH_PRESSURE"  # 賣單強勢
                else:
                    sentiment = "BALANCED"  # 平衡
                
                # 計算價差和中間價
                best_bid = bids[0][0] if bids else 0
                best_ask = asks[0][0] if asks else 0
                bid_ask_spread = abs(best_ask - best_bid)
                mid_price = (best_bid + best_ask) / 2 if best_bid > 0 and best_ask > 0 else 0
                
                return OrderBookData(
                    symbol=symbol,
                    timestamp=get_taiwan_now_naive(),
                    bids=bids,
                    asks=asks,
                    total_bid_volume=total_bid_volume,
                    total_ask_volume=total_ask_volume,
                    pressure_ratio=pressure_ratio,
                    market_sentiment=sentiment,
                    bid_ask_spread=bid_ask_spread,
                    mid_price=mid_price
                )
                
        except Exception as e:
            logger.error(f"❌ Order Book 深度分析失敗 {symbol}: {e}")
            raise
    
    async def get_funding_rate(self, symbol: str = "BTCUSDT") -> FundingRateData:
        """
        獲取資金費率數據
        """
        try:
            # 獲取最新資金費率
            funding_url = f"https://fapi.binance.com/fapi/v1/fundingRate"
            params = {"symbol": symbol, "limit": 1}
            
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(funding_url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"資金費率 API 請求失敗: {response.status}")
                    
                funding_data = await response.json()
                
                if not funding_data:
                    raise Exception("資金費率數據為空")
                
                funding_rate = float(funding_data[0]['fundingRate'])
                funding_time = datetime.fromtimestamp(int(funding_data[0]['fundingTime']) / 1000)
                
            # 獲取標記價格和下次資金費率時間
            premium_url = f"https://fapi.binance.com/fapi/v1/premiumIndex"
            params = {"symbol": symbol}
            
            async with self.session.get(premium_url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"標記價格 API 請求失敗: {response.status}")
                    
                premium_data = await response.json()
                mark_price = float(premium_data['markPrice'])
                next_funding_time = datetime.fromtimestamp(int(premium_data['nextFundingTime']) / 1000)
            
            # 分析資金費率情緒
            annual_rate = funding_rate * 365 * 3  # 年化費率 (每8小時一次)
            
            if funding_rate > 0.0007:
                sentiment = "OVERHEATED_LONG"  # 多頭過熱
                interpretation = "資金費率偏高，多單成本昂貴，市場可能過熱需回調"
            elif funding_rate < -0.0007:
                sentiment = "OVERSOLD_SHORT"  # 空頭擁擠
                interpretation = "資金費率偏空，空單擁擠，可能發生空頭擠壓"
            elif funding_rate > 0.0003:
                sentiment = "MILD_BULLISH"  # 溫和看多
                interpretation = "資金費率溫和偏多，市場情緒正面但未過熱"
            elif funding_rate < -0.0003:
                sentiment = "MILD_BEARISH"  # 溫和看空
                interpretation = "資金費率溫和偏空，市場情緒謹慎"
            else:
                sentiment = "NEUTRAL"  # 中性
                interpretation = "資金費率中性，等待其他訊號確認方向"
                
            return FundingRateData(
                symbol=symbol,
                funding_rate=funding_rate,
                funding_time=funding_time,
                next_funding_time=next_funding_time,
                mark_price=mark_price,
                sentiment=sentiment,
                market_interpretation=interpretation,
                annual_rate=annual_rate
            )
                
        except Exception as e:
            logger.error(f"❌ 資金費率分析失敗 {symbol}: {e}")
            raise
    
    async def get_phase3_analysis(self, symbol: str = "BTCUSDT") -> Phase3Analysis:
        """
        🎯 Phase 3 綜合高階市場分析
        整合 Order Book 深度和資金費率情緒指標
        """
        try:
            # 並行獲取數據
            order_book_task = self.get_order_book_depth(symbol)
            funding_rate_task = self.get_funding_rate(symbol)
            
            order_book, funding_rate = await asyncio.gather(
                order_book_task, funding_rate_task
            )
            
            # 綜合情緒分析
            combined_sentiment = self._analyze_combined_sentiment(order_book, funding_rate)
            
            # 市場壓力評分 (0-100)
            market_pressure_score = self._calculate_market_pressure_score(order_book, funding_rate)
            
            # 交易建議
            trading_recommendation = self._generate_trading_recommendation(
                order_book, funding_rate, combined_sentiment, market_pressure_score
            )
            
            # 風險等級
            risk_level = self._assess_risk_level(order_book, funding_rate, market_pressure_score)
            
            return Phase3Analysis(
                symbol=symbol,
                timestamp=get_taiwan_now_naive(),
                order_book=order_book,
                funding_rate=funding_rate,
                combined_sentiment=combined_sentiment,
                market_pressure_score=market_pressure_score,
                trading_recommendation=trading_recommendation,
                risk_level=risk_level
            )
            
        except Exception as e:
            logger.error(f"❌ Phase 3 綜合分析失敗 {symbol}: {e}")
            raise
    
    def _analyze_combined_sentiment(self, order_book: OrderBookData, funding_rate: FundingRateData) -> str:
        """綜合情緒分析"""
        ob_sentiment = order_book.market_sentiment
        fr_sentiment = funding_rate.sentiment
        
        # 組合分析邏輯
        if ob_sentiment == "BULLISH_PRESSURE" and fr_sentiment in ["MILD_BULLISH", "NEUTRAL"]:
            return "STRONG_BULLISH"
        elif ob_sentiment == "BULLISH_PRESSURE" and fr_sentiment == "OVERHEATED_LONG":
            return "BULLISH_BUT_OVERHEATED"
        elif ob_sentiment == "BEARISH_PRESSURE" and fr_sentiment in ["MILD_BEARISH", "NEUTRAL"]:
            return "STRONG_BEARISH"
        elif ob_sentiment == "BEARISH_PRESSURE" and fr_sentiment == "OVERSOLD_SHORT":
            return "BEARISH_BUT_OVERSOLD"
        elif ob_sentiment == "BALANCED" and fr_sentiment == "NEUTRAL":
            return "MARKET_NEUTRAL"
        elif ob_sentiment == "BALANCED" and fr_sentiment == "OVERHEATED_LONG":
            return "CONSOLIDATION_OVERHEATED"
        elif ob_sentiment == "BALANCED" and fr_sentiment == "OVERSOLD_SHORT":
            return "CONSOLIDATION_OVERSOLD"
        else:
            return "MIXED_SIGNALS"
    
    def _calculate_market_pressure_score(self, order_book: OrderBookData, funding_rate: FundingRateData) -> float:
        """計算市場壓力評分 (0-100)"""
        # Order Book 評分 (50%)
        pressure_ratio = order_book.pressure_ratio
        if pressure_ratio > 2.0:
            ob_score = 85  # 強多頭壓力
        elif pressure_ratio > 1.5:
            ob_score = 70  # 溫和多頭壓力
        elif pressure_ratio > 1.2:
            ob_score = 60  # 輕微多頭壓力
        elif pressure_ratio < 0.5:
            ob_score = 15  # 強空頭壓力
        elif pressure_ratio < 0.7:
            ob_score = 30  # 溫和空頭壓力
        elif pressure_ratio < 0.8:
            ob_score = 40  # 輕微空頭壓力
        else:
            ob_score = 50  # 平衡
        
        # Funding Rate 評分 (50%)
        fr = abs(funding_rate.funding_rate)
        if fr > 0.001:
            fr_score = 90 if funding_rate.funding_rate > 0 else 10
        elif fr > 0.0007:
            fr_score = 75 if funding_rate.funding_rate > 0 else 25
        elif fr > 0.0003:
            fr_score = 65 if funding_rate.funding_rate > 0 else 35
        else:
            fr_score = 50
        
        return (ob_score * 0.5) + (fr_score * 0.5)
    
    def _generate_trading_recommendation(self, order_book: OrderBookData, funding_rate: FundingRateData, 
                                       sentiment: str, pressure_score: float) -> str:
        """生成交易建議"""
        if sentiment == "STRONG_BULLISH" and pressure_score > 70:
            return "積極做多，但設置合理止損"
        elif sentiment == "BULLISH_BUT_OVERHEATED":
            return "謹慎做多，注意回調風險"
        elif sentiment == "STRONG_BEARISH" and pressure_score < 30:
            return "考慮做空，但注意反彈"
        elif sentiment == "BEARISH_BUT_OVERSOLD":
            return "謹慎做空，注意空頭擠壓"
        elif sentiment == "MARKET_NEUTRAL":
            return "觀望為主，等待明確方向"
        elif sentiment == "CONSOLIDATION_OVERHEATED":
            return "高位整理，減倉觀望"
        elif sentiment == "CONSOLIDATION_OVERSOLD":
            return "低位整理，可考慮分批進場"
        else:
            return "信號混雜，謹慎觀察"
    
    def _assess_risk_level(self, order_book: OrderBookData, funding_rate: FundingRateData, 
                          pressure_score: float) -> str:
        """評估風險等級"""
        high_spread = order_book.bid_ask_spread > order_book.mid_price * 0.001  # 價差超過0.1%
        extreme_funding = abs(funding_rate.funding_rate) > 0.001
        extreme_pressure = pressure_score > 85 or pressure_score < 15
        
        risk_factors = sum([high_spread, extreme_funding, extreme_pressure])
        
        if risk_factors >= 2:
            return "HIGH"
        elif risk_factors == 1:
            return "MEDIUM"
        else:
            return "LOW"

# 全局實例
phase3_analyzer = Phase3MarketAnalyzer()
