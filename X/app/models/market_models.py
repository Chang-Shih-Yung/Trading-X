#!/usr/bin/env python3
"""
市場數據模型 - market_data.db
包含K線數據、技術指標、價格警報
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, Index
from sqlalchemy.sql import func
import sys
import os

# 添加正確的路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from app.core.database_separated import db_manager

# 獲取市場數據資料庫的基礎類
MarketBase = db_manager.get_base("market_data")

class MarketData(MarketBase):
    """K線市場數據"""
    __tablename__ = "kline_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    # 市場數據特有欄位
    quote_volume = Column(Float, nullable=True)
    trade_count = Column(Integer, nullable=True)
    taker_buy_volume = Column(Float, nullable=True)
    taker_buy_quote_volume = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    
    # 複合索引優化查詢
    __table_args__ = (
        Index('idx_symbol_timeframe_timestamp', 'symbol', 'timeframe', 'timestamp'),
        Index('idx_timestamp_symbol', 'timestamp', 'symbol'),
    )

class TechnicalIndicator(MarketBase):
    """技術指標數據"""
    __tablename__ = "market_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 常用指標
    rsi = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    macd_histogram = Column(Float, nullable=True)
    
    # 布林帶
    bb_upper = Column(Float, nullable=True)
    bb_middle = Column(Float, nullable=True)
    bb_lower = Column(Float, nullable=True)
    bb_width = Column(Float, nullable=True)
    
    # 移動平均
    sma_20 = Column(Float, nullable=True)
    sma_50 = Column(Float, nullable=True)
    sma_200 = Column(Float, nullable=True)
    ema_12 = Column(Float, nullable=True)
    ema_26 = Column(Float, nullable=True)
    
    # 其他指標
    atr = Column(Float, nullable=True)
    adx = Column(Float, nullable=True)
    stoch_k = Column(Float, nullable=True)
    stoch_d = Column(Float, nullable=True)
    
    # 自定義指標 JSON 存儲
    custom_indicators = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_timeframe_timestamp', 'timeframe', 'timestamp'),
    )

class PriceAlert(MarketBase):
    """價格警報"""
    __tablename__ = "price_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    alert_type = Column(String(20), nullable=False, index=True)  # price_above, price_below, volatility, volume
    threshold = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    
    # 警報狀態
    is_triggered = Column(Boolean, default=False, index=True)
    trigger_count = Column(Integer, default=0)
    
    # 警報配置
    alert_config = Column(JSON, nullable=True)  # 警報特殊配置
    notification_sent = Column(Boolean, default=False)
    
    # 時間戳
    created_at = Column(DateTime, default=func.now())
    triggered_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_symbol_alert_type', 'symbol', 'alert_type'),
        Index('idx_triggered_expires', 'is_triggered', 'expires_at'),
    )

class MarketCondition(MarketBase):
    """市場狀況分析"""
    __tablename__ = "market_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 市場狀況評分
    bull_score = Column(Float, nullable=True)  # 0-1
    bear_score = Column(Float, nullable=True)  # 0-1
    neutral_score = Column(Float, nullable=True)  # 0-1
    
    # 市場階段
    market_phase = Column(String(20), nullable=True)  # accumulation, uptrend, distribution, downtrend
    trend_strength = Column(Float, nullable=True)  # 0-1
    volatility_level = Column(String(10), nullable=True)  # low, medium, high
    
    # 支撐阻力
    support_levels = Column(JSON, nullable=True)
    resistance_levels = Column(JSON, nullable=True)
    
    # 市場情緒
    fear_greed_index = Column(Float, nullable=True)
    volume_profile = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_symbol_timeframe_timestamp', 'symbol', 'timeframe', 'timestamp'),
    )
