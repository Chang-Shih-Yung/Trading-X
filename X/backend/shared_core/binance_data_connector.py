"""
🎯 Trading X - 幣安即時數據連接器
真實 Binance API 數據獲取模組
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import numpy as np

logger = logging.getLogger(__name__)

class BinanceDataConnector:
    """幣安數據連接器 - 獲取真實市場數據"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com"
        self.fapi_url = "https://fapi.binance.com"  # 期貨API
        self.session = None
        
        # API 限制與緩存
        self.request_weights = {}
        self.cache = {}
        self.cache_ttl = 5  # 緩存5秒
        
    async def __aenter__(self):
        """異步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def _request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """執行API請求"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # 檢查緩存
            cache_key = f"{url}_{str(params)}"
            if cache_key in self.cache:
                cache_time, cache_data = self.cache[cache_key]
                if datetime.now() - cache_time < timedelta(seconds=self.cache_ttl):
                    return cache_data
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    # 更新緩存
                    self.cache[cache_key] = (datetime.now(), data)
                    return data
                else:
                    logger.error(f"API請求失敗: {response.status} - {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"API請求異常: {e}")
            return None
    
    async def get_kline_data(self, symbol: str = "BTCUSDT", interval: str = "1m", 
                           limit: int = 100) -> List[List]:
        """獲取K線數據"""
        try:
            url = f"{self.base_url}/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            data = await self._request(url, params)
            if data:
                return data
            return []
            
        except Exception as e:
            logger.error(f"K線數據獲取失敗: {e}")
            return []
    
    async def get_ticker_price(self, symbol: str = "BTCUSDT") -> Optional[float]:
        """獲取當前價格"""
        try:
            url = f"{self.base_url}/api/v3/ticker/price"
            params = {"symbol": symbol}
            
            data = await self._request(url, params)
            if data and "price" in data:
                return float(data["price"])
            return None
            
        except Exception as e:
            logger.error(f"價格獲取失敗: {e}")
            return None
    
    async def get_24hr_ticker(self, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """獲取24小時價格變動數據"""
        try:
            url = f"{self.base_url}/api/v3/ticker/24hr"
            params = {"symbol": symbol}
            
            data = await self._request(url, params)
            return data
            
        except Exception as e:
            logger.error(f"24小時數據獲取失敗: {e}")
            return None
    
    async def get_order_book(self, symbol: str = "BTCUSDT", limit: int = 100) -> Optional[Dict]:
        """獲取訂單簿數據"""
        try:
            url = f"{self.base_url}/api/v3/depth"
            params = {
                "symbol": symbol,
                "limit": limit
            }
            
            data = await self._request(url, params)
            return data
            
        except Exception as e:
            logger.error(f"訂單簿數據獲取失敗: {e}")
            return None
    
    async def get_funding_rate(self, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """獲取資金費率（期貨）"""
        try:
            url = f"{self.fapi_url}/fapi/v1/fundingRate"
            params = {
                "symbol": symbol,
                "limit": 1
            }
            
            data = await self._request(url, params)
            if data and len(data) > 0:
                return data[0]
            return None
            
        except Exception as e:
            logger.error(f"資金費率獲取失敗: {e}")
            return None
    
    async def get_mark_price(self, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """獲取標記價格（期貨）"""
        try:
            url = f"{self.fapi_url}/fapi/v1/premiumIndex"
            params = {"symbol": symbol}
            
            data = await self._request(url, params)
            return data
            
        except Exception as e:
            logger.error(f"標記價格獲取失敗: {e}")
            return None
    
    async def get_exchange_info(self, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """獲取交易所信息"""
        try:
            url = f"{self.base_url}/api/v3/exchangeInfo"
            params = {"symbol": symbol}
            
            data = await self._request(url, params)
            return data
            
        except Exception as e:
            logger.error(f"交易所信息獲取失敗: {e}")
            return None
    
    async def calculate_price_series(self, symbol: str = "BTCUSDT", 
                                   period: int = 50) -> List[float]:
        """計算價格序列"""
        try:
            klines = await self.get_kline_data(symbol, "1m", period)
            if not klines:
                return []
            
            # 提取收盤價
            prices = [float(kline[4]) for kline in klines]  # kline[4] 是收盤價
            return prices
            
        except Exception as e:
            logger.error(f"價格序列計算失敗: {e}")
            return []
    
    async def calculate_volume_analysis(self, symbol: str = "BTCUSDT") -> Dict[str, float]:
        """計算成交量分析"""
        try:
            klines = await self.get_kline_data(symbol, "1m", 20)
            if not klines:
                return {}
            
            volumes = [float(kline[5]) for kline in klines]  # kline[5] 是成交量
            
            current_volume = volumes[-1] if volumes else 0
            avg_volume = np.mean(volumes) if volumes else 0
            volume_trend = (current_volume / avg_volume - 1) if avg_volume > 0 else 0
            
            return {
                "current_volume": current_volume,
                "average_volume": avg_volume,
                "volume_trend": volume_trend,
                "volume_ratio": current_volume / avg_volume if avg_volume > 0 else 1
            }
            
        except Exception as e:
            logger.error(f"成交量分析失敗: {e}")
            return {}
    
    async def calculate_volatility_metrics(self, symbol: str = "BTCUSDT") -> Dict[str, float]:
        """計算波動性指標"""
        try:
            prices = await self.calculate_price_series(symbol, 50)
            if len(prices) < 2:
                return {}
            
            # 計算價格變化率
            returns = []
            for i in range(1, len(prices)):
                returns.append((prices[i] - prices[i-1]) / prices[i-1])
            
            if not returns:
                return {}
            
            # 波動性指標
            volatility = np.std(returns) * np.sqrt(1440)  # 年化波動率（分鐘數據）
            current_price = prices[-1]
            price_change_24h = ((prices[-1] - prices[0]) / prices[0]) if len(prices) > 1 else 0
            
            return {
                "current_volatility": volatility,
                "price_change_24h": price_change_24h,
                "current_price": current_price,
                "returns_std": np.std(returns),
                "returns_mean": np.mean(returns)
            }
            
        except Exception as e:
            logger.error(f"波動性計算失敗: {e}")
            return {}
    
    async def get_comprehensive_market_data(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """獲取綜合市場數據"""
        try:
            # 並行獲取所有數據
            tasks = [
                self.get_ticker_price(symbol),
                self.get_24hr_ticker(symbol),
                self.get_order_book(symbol, 20),
                self.get_funding_rate(symbol),
                self.get_mark_price(symbol),
                self.calculate_price_series(symbol, 50),
                self.calculate_volume_analysis(symbol),
                self.calculate_volatility_metrics(symbol)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            current_price, ticker_24h, order_book, funding_rate, mark_price, \
            price_series, volume_analysis, volatility_metrics = results
            
            # 組合結果
            market_data = {
                "timestamp": datetime.now(),
                "symbol": symbol,
                "current_price": current_price if not isinstance(current_price, Exception) else None,
                "ticker_24h": ticker_24h if not isinstance(ticker_24h, Exception) else {},
                "order_book": order_book if not isinstance(order_book, Exception) else {},
                "funding_rate": funding_rate if not isinstance(funding_rate, Exception) else {},
                "mark_price": mark_price if not isinstance(mark_price, Exception) else {},
                "price_series": price_series if not isinstance(price_series, Exception) else [],
                "volume_analysis": volume_analysis if not isinstance(volume_analysis, Exception) else {},
                "volatility_metrics": volatility_metrics if not isinstance(volatility_metrics, Exception) else {}
            }
            
            # 計算數據完整性
            total_fields = 8
            valid_fields = sum(1 for key, value in market_data.items() 
                             if key not in ["timestamp", "symbol"] and value)
            data_completeness = valid_fields / (total_fields - 2)
            
            market_data["data_completeness"] = data_completeness
            market_data["data_quality"] = "high" if data_completeness >= 0.8 else \
                                        "medium" if data_completeness >= 0.6 else "low"
            
            return market_data
            
        except Exception as e:
            logger.error(f"綜合市場數據獲取失敗: {e}")
            return {
                "timestamp": datetime.now(),
                "symbol": symbol,
                "data_completeness": 0.0,
                "data_quality": "failed",
                "error": str(e)
            }

# 全局連接器實例
binance_connector = BinanceDataConnector()
