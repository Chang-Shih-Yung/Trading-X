from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class MarketDataResponse(BaseModel):
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class IndicatorResponse(BaseModel):
    name: str
    value: float
    signal: str
    strength: float
    metadata: Dict[str, Any]

class IndicatorsResponse(BaseModel):
    symbol: str
    timeframe: str
    timestamp: datetime
    indicators: Dict[str, IndicatorResponse]

class KlineData(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class KlinesResponse(BaseModel):
    symbol: str
    timeframe: str
    exchange: str
    count: int
    data: List[KlineData]

class OrderbookEntry(BaseModel):
    price: float
    quantity: float

class OrderbookResponse(BaseModel):
    symbol: str
    exchange: str
    timestamp: Optional[datetime]
    bids: List[List[float]]  # [price, quantity]
    asks: List[List[float]]  # [price, quantity]

class MarketSummaryData(BaseModel):
    symbol: str
    price: float
    change_24h: float

class MarketSummaryResponse(BaseModel):
    timestamp: datetime
    market_data: List[MarketSummaryData]
    total_symbols: int

class PriceResponse(BaseModel):
    symbol: str
    price: float
    exchange: str
    timestamp: datetime
