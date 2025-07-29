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
    """增強信號模型"""
    __tablename__ = "trading_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)  # 添加timeframe字段以匹配舊表
    signal_type = Column(String(20), nullable=False, index=True)  # LONG, SHORT, SCALPING_LONG, SCALPING_SHORT
    signal_strength = Column(Float, nullable=False)   # 0-1
    confidence = Column(Float, nullable=False)        # 0-1
    
    # 價格相關
    entry_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    risk_reward_ratio = Column(Float, nullable=True)
    
    # 時間框架
    primary_timeframe = Column(String(10), nullable=False, index=True)
    confirmed_timeframes = Column(JSON, nullable=True)  # 多時間框架確認
    
    # 信號元數據
    strategy_name = Column(String(100), nullable=True)
    urgency_level = Column(String(20), nullable=True, index=True)  # urgent, high, medium, low
    reasoning = Column(Text, nullable=True)
    key_indicators = Column(JSON, nullable=True)
    indicators_used = Column(JSON, nullable=True)  # 添加以匹配舊表
    
    # 市場分析相關（新增）
    market_condition = Column(JSON, nullable=True)  # 市場狀況分析
    bull_score = Column(Float, nullable=True)       # 牛市分數
    bear_score = Column(Float, nullable=True)       # 熊市分數
    market_phase = Column(String(50), nullable=True) # 市場階段
    
    # 突破分析相關（新增）
    is_breakout_signal = Column(Boolean, default=False)
    breakout_analysis = Column(JSON, nullable=True)  # 突破分析詳情
    volatility_level = Column(String(20), nullable=True)  # high, medium, low
    
    # 動態調整相關（新增）
    atr_adjusted = Column(Boolean, default=False)
    market_condition_adjusted = Column(Boolean, default=False)
    
    # 狀態管理
    status = Column(String(20), nullable=True, index=True)  # 添加status字段以匹配舊表
    is_active = Column(Boolean, default=True, index=True)
    is_scalping = Column(Boolean, default=False, index=True)  # 是否為短線信號
    
    # 交易結果相關（新增）
    trade_result = Column(String(20), nullable=True, index=True)  # win, loss, breakeven, expired, pending
    profit_loss_pct = Column(Float, nullable=True)  # 盈虧百分比
    max_profit_pct = Column(Float, nullable=True)   # 最大盈利百分比
    max_loss_pct = Column(Float, nullable=True)     # 最大虧損百分比
    time_to_result = Column(Integer, nullable=True) # 結果產生時間（秒）
    
    # 精準度相關欄位（新增）
    precision_score = Column(Float, nullable=True, index=True)           # 精準度評分
    is_precision_selected = Column(Boolean, default=False, index=True)   # 是否為精準篩選
    market_condition_score = Column(Float, nullable=True)                # 市場條件評分
    indicator_consistency = Column(Float, nullable=True)                 # 指標一致性
    timing_score = Column(Float, nullable=True)                          # 時機評分
    risk_adjustment = Column(Float, nullable=True)                       # 風險調整評分
    
    # 時間戳
    created_at = Column(DateTime, default=func.now(), index=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    archived_at = Column(DateTime, nullable=True, index=True)  # 歸檔時間
    
    # 智能時間計算相關（新增）
    smart_timing_enabled = Column(Boolean, default=True)  # 是否啟用智能時間計算
    smart_timing_details = Column(JSON, nullable=True)    # 智能時間計算詳情
    base_expiry_minutes = Column(Integer, nullable=True)  # 基礎有效期（分鐘）
    calculated_expiry_minutes = Column(Integer, nullable=True)  # 計算後的有效期（分鐘）
    timing_multipliers = Column(JSON, nullable=True)      # 各種倍數信息
    timing_reasoning = Column(Text, nullable=True)        # 時間計算推理

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

# 為了向後兼容，建立 Signal 別名
Signal = TradingSignal
