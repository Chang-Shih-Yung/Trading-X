# 用戶交易狀態管理模型
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from typing import Optional

class UserTradingPosition(Base):
    """用戶交易倉位模型"""
    __tablename__ = "user_trading_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)  # 用戶標識
    symbol = Column(String(20), nullable=False, index=True)    # 交易對
    
    # 倉位基本信息
    position_type = Column(String(20), nullable=False, index=True)  # LONG, SHORT
    position_size = Column(Float, nullable=False)     # 倉位大小
    entry_price = Column(Float, nullable=False)       # 進場價格
    current_price = Column(Float, nullable=True)      # 當前價格
    
    # 交易設定
    stop_loss = Column(Float, nullable=True)          # 止損價
    take_profit = Column(Float, nullable=True)        # 止盈價
    leverage = Column(Float, default=1.0)             # 槓桿倍數
    
    # 倉位狀態
    status = Column(String(20), nullable=False, index=True, default="ACTIVE")  
    # ACTIVE, CLOSED, PARTIAL_CLOSED, STOPPED_OUT, TAKE_PROFIT_HIT
    
    # 關聯信號
    original_signal_id = Column(Integer, nullable=True)  # 原始信號ID
    signal_metadata = Column(JSON, nullable=True)        # 信號相關數據
    
    # 盈虧追蹤
    unrealized_pnl = Column(Float, nullable=True)     # 未實現盈虧
    realized_pnl = Column(Float, nullable=True)       # 已實現盈虧
    max_profit = Column(Float, nullable=True)         # 最大盈利
    max_loss = Column(Float, nullable=True)           # 最大虧損
    
    # 風險管理
    risk_level = Column(String(20), nullable=True)    # LOW, MEDIUM, HIGH
    portfolio_percentage = Column(Float, nullable=True) # 占投資組合百分比
    
    # 時間管理
    opened_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime, nullable=True)
    
    # 交易策略相關
    strategy_type = Column(String(50), nullable=True)  # SCALPING, SWING, SNIPER等
    timeframe = Column(String(10), nullable=True)      # 時間框架
    
class UserTradingPreference(Base):
    """用戶交易偏好設定"""
    __tablename__ = "user_trading_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, unique=True, index=True)
    
    # 同幣種信號處理偏好
    same_symbol_policy = Column(String(50), default="ALERT_ONLY")  
    # IGNORE_NEW, ALERT_ONLY, AUTO_AVERAGE, AUTO_REPLACE, ASK_USER
    
    # 風險管理偏好
    max_positions_per_symbol = Column(Integer, default=1)
    max_total_positions = Column(Integer, default=10)
    default_risk_per_trade = Column(Float, default=0.02)  # 2%
    
    # 通知偏好
    notify_better_signals = Column(Boolean, default=True)
    notify_position_conflicts = Column(Boolean, default=True)
    notify_risk_warnings = Column(Boolean, default=True)
    
    # 自動化設定
    auto_close_expired_signals = Column(Boolean, default=False)
    auto_update_stop_loss = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class TradingSignalConflict(Base):
    """信號衝突記錄"""
    __tablename__ = "trading_signal_conflicts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # 衝突信號信息
    existing_position_id = Column(Integer, nullable=True)  # 現有倉位ID
    new_signal_id = Column(Integer, nullable=False)        # 新信號ID
    conflict_type = Column(String(50), nullable=False)     # 衝突類型
    
    # 比較分析
    existing_confidence = Column(Float, nullable=True)
    new_signal_confidence = Column(Float, nullable=False)
    confidence_improvement = Column(Float, nullable=True)  # 信心度提升
    
    # 建議行動
    recommended_action = Column(String(50), nullable=True)
    # IGNORE, ALERT, PARTIAL_CLOSE, FULL_REPLACE, AVERAGE_IN, HEDGE
    action_reasoning = Column(Text, nullable=True)
    
    # 處理狀態
    status = Column(String(20), default="PENDING")  # PENDING, RESOLVED, IGNORED
    user_action = Column(String(50), nullable=True)  # 用戶實際採取的行動
    
    created_at = Column(DateTime, default=func.now(), index=True)
    resolved_at = Column(DateTime, nullable=True)
