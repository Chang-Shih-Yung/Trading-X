from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List
from datetime import datetime
from enum import Enum

class SignalTypeEnum(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    CLOSE = "CLOSE"

class ScalpingSignalTypeEnum(str, Enum):
    SCALP_LONG = "SCALP_LONG"
    SCALP_SHORT = "SCALP_SHORT"
    QUICK_EXIT = "QUICK_EXIT"
    MOMENTUM_BREAKOUT = "MOMENTUM_BREAKOUT"
    MEAN_REVERSION = "MEAN_REVERSION"

class SignalStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    TRIGGERED = "TRIGGERED"
    EXPIRED = "EXPIRED"

class SignalBase(BaseModel):
    symbol: str = Field(..., description="交易對")
    timeframe: str = Field(..., description="時間框架")
    signal_type: SignalTypeEnum = Field(..., description="信號類型")
    signal_strength: float = Field(..., ge=0, le=100, description="信號強度")
    entry_price: Optional[float] = Field(None, description="進場價格")
    stop_loss: Optional[float] = Field(None, description="止損價格")
    take_profit: Optional[float] = Field(None, description="止盈價格")
    risk_reward_ratio: Optional[float] = Field(None, description="風險回報比")
    confidence: float = Field(..., ge=0, le=1, description="置信度")
    reasoning: Optional[str] = Field(None, description="信號理由")

class SignalCreate(SignalBase):
    indicators_used: Optional[Dict[str, Any]] = Field(None, description="使用的指標")
    expires_at: Optional[datetime] = Field(None, description="過期時間")

class SignalResponse(SignalBase):
    id: int
    indicators_used: Optional[Dict[str, Any]] = None
    status: SignalStatusEnum
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SignalFilter(BaseModel):
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    signal_type: Optional[SignalTypeEnum] = None
    min_confidence: Optional[float] = Field(0.0, ge=0, le=1)
    min_strength: Optional[float] = Field(0.0, ge=0, le=100)
    status: Optional[SignalStatusEnum] = None

class AnalyzeRequest(BaseModel):
    symbol: str = Field(..., description="交易對")
    timeframe: str = Field(..., description="時間框架")

class ScalpingSignalResponse(BaseModel):
    """短線交易信號響應模型"""
    id: str = Field(..., description="信號ID")
    symbol: str = Field(..., description="交易對")
    signal_type: str = Field(..., description="信號類型")
    primary_timeframe: str = Field(..., description="主要時間框架")
    confirmed_timeframes: List[str] = Field(default=[], description="確認時間框架")
    entry_price: float = Field(..., description="進場價格")
    stop_loss: float = Field(..., description="止損價格")
    take_profit: float = Field(..., description="止盈價格")
    risk_reward_ratio: float = Field(..., description="風險回報比")
    confidence: float = Field(..., ge=0, le=1, description="信心度")
    signal_strength: float = Field(..., ge=0, le=1, description="信號強度")
    urgency_level: str = Field(..., description="緊急程度")
    strategy_name: str = Field(..., description="策略名稱")
    reasoning: str = Field(..., description="信號理由")
    key_indicators: Dict[str, Any] = Field(default={}, description="關鍵指標")
    created_at: datetime = Field(..., description="創建時間")
    expires_at: Optional[datetime] = Field(None, description="過期時間")
    is_scalping: bool = Field(default=True, description="是否為短線信號")
    scalping_type: str = Field(..., description="短線類型")
    
    class Config:
        from_attributes = True
    symbol: str = Field(..., description="交易對", example="BTC/USDT")
    timeframe: str = Field("1h", description="時間框架", example="1h")
