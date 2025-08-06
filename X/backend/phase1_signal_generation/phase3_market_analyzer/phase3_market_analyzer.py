"""
🎯 Trading X - Phase3 市場分析器（真實版）
🎯 Phase 3: 高階市場適應 - Order Book 深度分析和資金費率情緒指標
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import sys
from pathlib import Path

# 添加上級目錄到路徑
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent.parent / "core"))

from binance_data_connector import binance_connector

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
    """Phase 3 高階市場分析器（真實版）"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def analyze_market_depth(self, symbol: str = "BTCUSDT") -> Optional[Phase3Analysis]:
        """分析市場深度 - 使用真實幣安API數據"""
        try:
            # 並行獲取訂單簿和資金費率數據
            async with binance_connector as connector:
                order_book_task = self.get_order_book_depth(symbol)
                funding_rate_task = self.get_funding_rate(symbol)
                
                order_book_data, funding_rate_data = await asyncio.gather(
                    order_book_task, funding_rate_task, return_exceptions=True
                )
                
                # 檢查數據有效性
                if isinstance(order_book_data, Exception):
                    logger.error(f"訂單簿數據獲取失敗: {order_book_data}")
                    order_book_data = None
                
                if isinstance(funding_rate_data, Exception):
                    logger.error(f"資金費率數據獲取失敗: {funding_rate_data}")
                    funding_rate_data = None
                
                if not order_book_data or not funding_rate_data:
                    logger.warning("Phase3數據不完整")
                    return None
                
                # 綜合分析
                combined_sentiment = self._analyze_combined_sentiment(
                    order_book_data, funding_rate_data
                )
                
                market_pressure_score = self._calculate_market_pressure_score(
                    order_book_data, funding_rate_data
                )
                
                trading_recommendation = self._generate_trading_recommendation(
                    combined_sentiment, market_pressure_score
                )
                
                risk_level = self._assess_risk_level(
                    order_book_data, funding_rate_data, market_pressure_score
                )
                
                return Phase3Analysis(
                    symbol=symbol,
                    timestamp=datetime.now(),
                    order_book=order_book_data,
                    funding_rate=funding_rate_data,
                    combined_sentiment=combined_sentiment,
                    market_pressure_score=market_pressure_score,
                    trading_recommendation=trading_recommendation,
                    risk_level=risk_level
                )
                
        except Exception as e:
            logger.error(f"Phase3市場深度分析失敗: {e}")
            return None
    
    async def get_order_book_depth(self, symbol: str = "BTCUSDT", limit: int = 20) -> Optional[OrderBookData]:
        """
        獲取 Order Book 深度數據 - 真實API調用
        """
        try:
            async with binance_connector as connector:
                order_book = await connector.get_order_book(symbol, limit)
                
                if not order_book or 'bids' not in order_book or 'asks' not in order_book:
                    logger.warning(f"訂單簿數據無效: {symbol}")
                    return None
                
                # 解析買賣盤數據
                bids = [(float(p), float(q)) for p, q in order_book['bids']]
                asks = [(float(p), float(q)) for p, q in order_book['asks']]
                
                if not bids or not asks:
                    logger.warning(f"買賣盤數據為空: {symbol}")
                    return None
                
                # 計算總成交量
                total_bid_volume = sum(q for _, q in bids)
                total_ask_volume = sum(q for _, q in asks)
                
                # 計算壓力比
                if total_ask_volume > 0:
                    pressure_ratio = total_bid_volume / total_ask_volume
                else:
                    pressure_ratio = 10.0  # 賣盤為零時設為極高買壓
                
                # 分析市場情緒
                if pressure_ratio > 2.0:
                    sentiment = "STRONG_BULLISH"  # 強烈看漲
                elif pressure_ratio > 1.5:
                    sentiment = "BULLISH_PRESSURE"  # 買單強勢
                elif pressure_ratio > 1.1:
                    sentiment = "MILD_BULLISH"  # 輕微看漲
                elif pressure_ratio > 0.9:
                    sentiment = "BALANCED"  # 平衡
                elif pressure_ratio > 0.7:
                    sentiment = "MILD_BEARISH"  # 輕微看跌
                elif pressure_ratio > 0.5:
                    sentiment = "BEARISH_PRESSURE"  # 賣單強勢
                else:
                    sentiment = "STRONG_BEARISH"  # 強烈看跌
                
                # 計算價差和中間價
                best_bid = bids[0][0]
                best_ask = asks[0][0]
                bid_ask_spread = best_ask - best_bid
                mid_price = (best_bid + best_ask) / 2
                
                return OrderBookData(
                    symbol=symbol,
                    timestamp=datetime.now(),
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
            return None
    
    async def get_funding_rate(self, symbol: str = "BTCUSDT") -> Optional[FundingRateData]:
        """
        獲取資金費率數據 - 真實API調用
        """
        try:
            async with binance_connector as connector:
                # 獲取最新資金費率
                funding_rate = await connector.get_funding_rate(symbol)
                mark_price_data = await connector.get_mark_price(symbol)
                
                if not funding_rate:
                    logger.warning(f"資金費率數據無效: {symbol}")
                    return None
                
                rate = float(funding_rate.get('fundingRate', 0))
                funding_time = datetime.fromtimestamp(
                    int(funding_rate.get('fundingTime', 0)) / 1000
                )
                
                # 獲取標記價格
                mark_price = 0.0
                if mark_price_data:
                    mark_price = float(mark_price_data.get('markPrice', 0))
                
                # 計算年化費率
                annual_rate = rate * 365 * 3  # 每天3次資金費率
                
                # 分析資金費率情緒
                if rate > 0.0003:  # > 0.03%
                    sentiment = "EXTREME_BULLISH"
                    interpretation = "多頭過度樂觀，可能面臨回調"
                elif rate > 0.0001:  # > 0.01%
                    sentiment = "BULLISH"
                    interpretation = "市場看漲情緒濃厚"
                elif rate > 0:
                    sentiment = "MILD_BULLISH"
                    interpretation = "輕微看漲偏向"
                elif rate > -0.0001:  # > -0.01%
                    sentiment = "NEUTRAL"
                    interpretation = "市場情緒中性"
                elif rate > -0.0003:  # > -0.03%
                    sentiment = "BEARISH"
                    interpretation = "市場看跌情緒增強"
                else:
                    sentiment = "EXTREME_BEARISH"
                    interpretation = "空頭過度悲觀，可能面臨反彈"
                
                # 計算下次資金費率時間 (每8小時)
                next_funding_time = funding_time + timedelta(hours=8)
                
                return FundingRateData(
                    symbol=symbol,
                    funding_rate=rate,
                    funding_time=funding_time,
                    next_funding_time=next_funding_time,
                    mark_price=mark_price,
                    sentiment=sentiment,
                    market_interpretation=interpretation,
                    annual_rate=annual_rate
                )
                
        except Exception as e:
            logger.error(f"❌ 資金費率獲取失敗 {symbol}: {e}")
            return None
    
    def _analyze_combined_sentiment(self, order_book: OrderBookData, 
                                   funding_rate: FundingRateData) -> str:
        """分析綜合市場情緒"""
        try:
            # 訂單簿情緒權重 60%，資金費率情緒權重 40%
            ob_sentiment_score = self._sentiment_to_score(order_book.market_sentiment)
            fr_sentiment_score = self._sentiment_to_score(funding_rate.sentiment)
            
            combined_score = ob_sentiment_score * 0.6 + fr_sentiment_score * 0.4
            
            # 轉換回情緒標籤
            if combined_score >= 0.8:
                return "EXTREMELY_BULLISH"
            elif combined_score >= 0.6:
                return "BULLISH"
            elif combined_score >= 0.4:
                return "NEUTRAL"
            elif combined_score >= 0.2:
                return "BEARISH"
            else:
                return "EXTREMELY_BEARISH"
                
        except Exception as e:
            logger.error(f"綜合情緒分析失敗: {e}")
            return "NEUTRAL"
    
    def _sentiment_to_score(self, sentiment: str) -> float:
        """將情緒標籤轉換為數值分數"""
        sentiment_scores = {
            "STRONG_BULLISH": 1.0,
            "EXTREME_BULLISH": 1.0,
            "BULLISH_PRESSURE": 0.8,
            "BULLISH": 0.8,
            "MILD_BULLISH": 0.6,
            "BALANCED": 0.5,
            "NEUTRAL": 0.5,
            "MILD_BEARISH": 0.4,
            "BEARISH_PRESSURE": 0.2,
            "BEARISH": 0.2,
            "STRONG_BEARISH": 0.0,
            "EXTREME_BEARISH": 0.0
        }
        return sentiment_scores.get(sentiment, 0.5)
    
    def _calculate_market_pressure_score(self, order_book: OrderBookData, 
                                        funding_rate: FundingRateData) -> float:
        """計算市場壓力分數"""
        try:
            # 訂單簿壓力 (基於買賣比例)
            ob_pressure = min(1.0, order_book.pressure_ratio / 2.0) if order_book.pressure_ratio <= 2.0 else 1.0
            
            # 資金費率壓力 (絕對值越大壓力越大)
            fr_pressure = min(1.0, abs(funding_rate.funding_rate) * 10000)  # 0.01% = 1.0 pressure
            
            # 價差壓力 (價差越大流動性越差，壓力越大)
            spread_pressure = min(1.0, order_book.bid_ask_spread / order_book.mid_price * 1000)
            
            # 綜合壓力分數
            total_pressure = (ob_pressure * 0.5 + fr_pressure * 0.3 + spread_pressure * 0.2)
            
            return min(1.0, total_pressure)
            
        except Exception as e:
            logger.error(f"市場壓力計算失敗: {e}")
            return 0.5
    
    def _generate_trading_recommendation(self, sentiment: str, pressure_score: float) -> str:
        """生成交易建議"""
        try:
            if sentiment in ["EXTREMELY_BULLISH", "BULLISH"] and pressure_score < 0.7:
                return "STRONG_BUY"
            elif sentiment in ["EXTREMELY_BULLISH", "BULLISH"]:
                return "BUY_WITH_CAUTION"
            elif sentiment == "NEUTRAL" and pressure_score < 0.5:
                return "HOLD"
            elif sentiment == "NEUTRAL":
                return "WAIT_FOR_SIGNAL"
            elif sentiment in ["BEARISH", "EXTREMELY_BEARISH"] and pressure_score < 0.7:
                return "STRONG_SELL"
            else:
                return "SELL_WITH_CAUTION"
                
        except Exception:
            return "HOLD"
    
    def _assess_risk_level(self, order_book: OrderBookData, funding_rate: FundingRateData,
                          pressure_score: float) -> str:
        """評估風險等級"""
        try:
            risk_factors = 0
            
            # 高壓力環境
            if pressure_score > 0.8:
                risk_factors += 2
            elif pressure_score > 0.6:
                risk_factors += 1
            
            # 極端資金費率
            if abs(funding_rate.funding_rate) > 0.0005:  # > 0.05%
                risk_factors += 2
            elif abs(funding_rate.funding_rate) > 0.0002:  # > 0.02%
                risk_factors += 1
            
            # 訂單簿不平衡
            if order_book.pressure_ratio > 3.0 or order_book.pressure_ratio < 0.33:
                risk_factors += 2
            elif order_book.pressure_ratio > 2.0 or order_book.pressure_ratio < 0.5:
                risk_factors += 1
            
            # 大幅價差
            spread_ratio = order_book.bid_ask_spread / order_book.mid_price
            if spread_ratio > 0.001:  # > 0.1%
                risk_factors += 1
            
            # 風險等級評估
            if risk_factors >= 5:
                return "VERY_HIGH"
            elif risk_factors >= 3:
                return "HIGH"
            elif risk_factors >= 1:
                return "MEDIUM"
            else:
                return "LOW"
                
        except Exception:
            return "MEDIUM"
