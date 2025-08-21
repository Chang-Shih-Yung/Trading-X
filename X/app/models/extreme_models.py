#!/usr/bin/env python3
"""
極端事件模型 - extreme_events.db
包含閃崩檢測、系統保護、流動性事件、相關性崩潰
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

# 獲取極端事件資料庫的基礎類
ExtremeBase = db_manager.get_base("extreme_events")

class CrashDetection(ExtremeBase):
    """閃崩檢測事件"""
    __tablename__ = "crash_detection"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), nullable=False, unique=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # 閃崩類型
    crash_type = Column(String(30), nullable=False, index=True)  # flash_crash_5min, rapid_decline_15min, sustained_crash_1hour, extreme_crash_24hour
    
    # 價格數據
    price_before = Column(Float, nullable=False)
    price_after = Column(Float, nullable=False)
    price_lowest = Column(Float, nullable=False)
    drop_percentage = Column(Float, nullable=False, index=True)
    
    # 時間框架
    timeframe = Column(String(10), nullable=False)
    detection_duration_minutes = Column(Integer, nullable=False)
    recovery_duration_minutes = Column(Integer, nullable=True)
    
    # 觸發條件
    trigger_conditions = Column(JSON, nullable=False)
    confirmation_count = Column(Integer, default=1)
    false_alarm = Column(Boolean, default=False, index=True)
    
    # 市場環境
    volume_before = Column(Float, nullable=True)
    volume_during = Column(Float, nullable=True)
    volume_multiplier = Column(Float, nullable=True)
    market_cap_impact = Column(Float, nullable=True)
    
    # 系統反應
    protection_triggered = Column(Boolean, default=False, index=True)
    actions_taken = Column(JSON, nullable=True)
    recovery_actions = Column(JSON, nullable=True)
    
    # 時間戳
    detected_at = Column(DateTime, nullable=False, index=True)
    crash_started_at = Column(DateTime, nullable=False)
    crash_ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_symbol_crash_type', 'symbol', 'crash_type'),
        Index('idx_drop_percentage_detected', 'drop_percentage', 'detected_at'),
        Index('idx_protection_triggered', 'protection_triggered'),
    )

class SystemProtection(ExtremeBase):
    """系統保護事件"""
    __tablename__ = "system_protections"
    
    id = Column(Integer, primary_key=True, index=True)
    protection_id = Column(String(50), nullable=False, unique=True, index=True)
    
    # 保護類型
    protection_type = Column(String(30), nullable=False, index=True)  # signal_pause, trading_halt, emergency_shutdown, gradual_shutdown
    severity_level = Column(String(10), nullable=False, index=True)  # low, medium, high, critical
    
    # 觸發條件
    trigger_condition = Column(JSON, nullable=False)
    trigger_event_id = Column(String(50), nullable=True, index=True)  # 關聯觸發事件
    
    # 保護動作
    action_taken = Column(JSON, nullable=False)
    affected_symbols = Column(JSON, nullable=True)
    affected_phases = Column(JSON, nullable=True)
    
    # 持續時間
    protection_duration_minutes = Column(Integer, nullable=True)
    recovery_time_minutes = Column(Integer, nullable=True)
    
    # 恢復
    auto_recovery = Column(Boolean, default=False)
    manual_intervention_required = Column(Boolean, default=False)
    recovery_checklist = Column(JSON, nullable=True)
    recovery_status = Column(String(20), default="active", index=True)  # active, recovering, recovered, failed
    
    # 影響評估
    signals_affected = Column(Integer, nullable=True)
    trades_affected = Column(Integer, nullable=True)
    estimated_loss_prevention = Column(Float, nullable=True)
    
    # 時間戳
    triggered_at = Column(DateTime, nullable=False, index=True)
    recovered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_protection_type_severity', 'protection_type', 'severity_level'),
        Index('idx_recovery_status_triggered', 'recovery_status', 'triggered_at'),
    )

class LiquidityEvent(ExtremeBase):
    """流動性事件"""
    __tablename__ = "liquidity_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), nullable=False, unique=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # 流動性指標
    liquidity_level = Column(String(10), nullable=False, index=True)  # very_low, low, medium, high
    bid_ask_spread = Column(Float, nullable=False)
    spread_percentage = Column(Float, nullable=False, index=True)
    
    # 成交量分析
    volume_before = Column(Float, nullable=True)
    volume_during = Column(Float, nullable=False)
    volume_drop_percentage = Column(Float, nullable=True)
    average_volume_30d = Column(Float, nullable=True)
    
    # 訂單簿深度
    bid_depth = Column(Float, nullable=True)
    ask_depth = Column(Float, nullable=True)
    order_book_imbalance = Column(Float, nullable=True)
    
    # 影響評估
    impact_assessment = Column(JSON, nullable=False)
    trading_difficulty = Column(String(10), nullable=True)  # easy, moderate, difficult, impossible
    slippage_risk = Column(String(10), nullable=True)  # low, medium, high, extreme
    
    # 事件持續
    duration_minutes = Column(Integer, nullable=False)
    is_ongoing = Column(Boolean, default=False, index=True)
    
    # 相關事件
    related_crash_event_id = Column(String(50), nullable=True, index=True)
    market_wide_event = Column(Boolean, default=False)
    
    detected_at = Column(DateTime, nullable=False, index=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_symbol_liquidity_level', 'symbol', 'liquidity_level'),
        Index('idx_spread_detected', 'spread_percentage', 'detected_at'),
    )

class CorrelationBreakdown(ExtremeBase):
    """相關性崩潰事件"""
    __tablename__ = "correlation_breakdown"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), nullable=False, unique=True, index=True)
    
    # 交易對相關性
    symbol_pair = Column(String(50), nullable=False, index=True)  # "BTCUSDT,ETHUSDT"
    
    # 相關性數據
    normal_correlation = Column(Float, nullable=False)
    breakdown_correlation = Column(Float, nullable=False)
    correlation_change = Column(Float, nullable=False, index=True)
    
    # 時間框架
    calculation_period_days = Column(Integer, nullable=False)
    breakdown_duration_hours = Column(Integer, nullable=False)
    
    # 市場影響
    market_impact = Column(JSON, nullable=False)
    volatility_increase = Column(Float, nullable=True)
    trading_volume_change = Column(Float, nullable=True)
    
    # 結構性變化
    structural_change = Column(Boolean, default=False)
    trend_divergence = Column(String(20), nullable=True)  # weak, moderate, strong
    
    # 恢復狀態
    correlation_recovered = Column(Boolean, default=False)
    recovery_level = Column(Float, nullable=True)
    
    detected_at = Column(DateTime, nullable=False, index=True)
    breakdown_started_at = Column(DateTime, nullable=False)
    recovered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_symbol_pair_detected', 'symbol_pair', 'detected_at'),
        Index('idx_correlation_change', 'correlation_change'),
    )

class ExtremeEventSummary(ExtremeBase):
    """極端事件摘要統計"""
    __tablename__ = "extreme_event_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    
    # 事件計數
    total_crashes = Column(Integer, default=0)
    total_protections = Column(Integer, default=0)
    total_liquidity_events = Column(Integer, default=0)
    total_correlation_breakdowns = Column(Integer, default=0)
    
    # 嚴重度分布
    critical_events = Column(Integer, default=0)
    high_severity_events = Column(Integer, default=0)
    medium_severity_events = Column(Integer, default=0)
    low_severity_events = Column(Integer, default=0)
    
    # 影響統計
    total_downtime_minutes = Column(Integer, default=0)
    total_signals_affected = Column(Integer, default=0)
    estimated_loss_prevented = Column(Float, nullable=True)
    
    # 恢復統計
    auto_recoveries = Column(Integer, default=0)
    manual_interventions = Column(Integer, default=0)
    failed_recoveries = Column(Integer, default=0)
    avg_recovery_time_minutes = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_period_start_end', 'period_start', 'period_end'),
    )
