from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
from typing import Optional

class MarketData(Base):
    """市場數據模型"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())

class TechnicalIndicator(Base):
    """技術指標模型"""
    __tablename__ = "technical_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    indicator_name = Column(String(50), nullable=False, index=True)
    value = Column(Float, nullable=True)
    indicator_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())

class TradingSignal(Base):
    """交易信號模型"""
    __tablename__ = "trading_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    signal_type = Column(String(10), nullable=False)  # LONG, SHORT, CLOSE
    signal_strength = Column(Float, nullable=False)   # 0-100
    entry_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    risk_reward_ratio = Column(Float, nullable=True)
    confidence = Column(Float, nullable=False)        # 0-1
    indicators_used = Column(JSON, nullable=True)
    reasoning = Column(Text, nullable=True)
    status = Column(String(20), default="ACTIVE")     # ACTIVE, TRIGGERED, EXPIRED
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)

class Strategy(Base):
    """策略模型"""
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    config = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class BacktestResult(Base):
    """回測結果模型"""
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, nullable=False)
    final_capital = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)
    total_trades = Column(Integer, nullable=False)
    winning_trades = Column(Integer, nullable=False)
    losing_trades = Column(Integer, nullable=False)
    win_rate = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)
    avg_trade_return = Column(Float, nullable=True)
    detailed_results = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())

class RiskMetrics(Base):
    """風險指標模型"""
    __tablename__ = "risk_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    volatility = Column(Float, nullable=True)
    var_95 = Column(Float, nullable=True)          # 95% Value at Risk
    var_99 = Column(Float, nullable=True)          # 99% Value at Risk
    beta = Column(Float, nullable=True)
    correlation_btc = Column(Float, nullable=True)
    liquidity_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())
