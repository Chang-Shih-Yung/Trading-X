#!/usr/bin/env python3
"""
學習記錄模型 - learning_records.db
包含Phase2學習參數、Phase5回測結果、參數演化
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

# 獲取學習記錄資料庫的基礎類
LearningBase = db_manager.get_base("learning_records")

class Phase2Learning(LearningBase):
    """Phase2 自適應學習記錄"""
    __tablename__ = "phase2_learning"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # 學習參數 (JSON格式存儲)
    parameters_before = Column(JSON, nullable=False)
    parameters_after = Column(JSON, nullable=False)
    parameter_changes = Column(JSON, nullable=True)  # 參數變化詳情
    
    # 效能指標
    performance_before = Column(Float, nullable=False)
    performance_after = Column(Float, nullable=False)
    performance_improvement = Column(Float, nullable=False)
    
    # 學習結果
    learning_success = Column(Boolean, nullable=False)
    rollback_flag = Column(Boolean, default=False, index=True)
    rollback_reason = Column(Text, nullable=True)
    
    # 學習元數據
    signal_count = Column(Integer, nullable=False)
    time_elapsed_hours = Column(Float, nullable=False)
    market_condition = Column(JSON, nullable=True)
    
    # 信號分析
    signals_analyzed = Column(Integer, nullable=True)
    win_rate_improvement = Column(Float, nullable=True)
    avg_profit_improvement = Column(Float, nullable=True)
    risk_reduction = Column(Float, nullable=True)
    
    # 時間戳
    created_at = Column(DateTime, default=func.now())
    learning_started_at = Column(DateTime, nullable=False)
    learning_completed_at = Column(DateTime, nullable=False)
    
    __table_args__ = (
        Index('idx_symbol_session', 'symbol', 'session_id'),
        Index('idx_rollback_created', 'rollback_flag', 'created_at'),
        Index('idx_performance_improvement', 'performance_improvement'),
    )

class Phase5Backtest(LearningBase):
    """Phase5 回測驗證記錄"""
    __tablename__ = "phase5_backtests"
    
    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(String(50), nullable=False, unique=True, index=True)
    
    # 策略配置
    strategy_config = Column(JSON, nullable=False)
    lean_config = Column(JSON, nullable=True)
    
    # 多時間框架結果
    h4_results = Column(JSON, nullable=True)  # 4小時結果
    d1_results = Column(JSON, nullable=True)  # 日線結果
    w1_results = Column(JSON, nullable=True)  # 週線結果
    
    # Lean 相似度分析
    lean_similarity_score = Column(Float, nullable=True)
    lean_consensus = Column(JSON, nullable=True)
    lean_validation_passed = Column(Boolean, default=False)
    
    # 回測統計
    total_trades = Column(Integer, nullable=True)
    win_rate = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    
    # 驗證狀態
    validation_status = Column(String(20), nullable=False, index=True)  # pending, passed, failed, expired
    validation_score = Column(Float, nullable=True)
    validation_notes = Column(Text, nullable=True)
    
    # 時間戳
    created_at = Column(DateTime, default=func.now())
    backtest_started_at = Column(DateTime, nullable=False)
    backtest_completed_at = Column(DateTime, nullable=True)
    validation_expires_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_validation_status', 'validation_status'),
        Index('idx_lean_similarity', 'lean_similarity_score'),
        Index('idx_created_validation', 'created_at', 'validation_status'),
    )

class ParameterEvolution(LearningBase):
    """參數演化追蹤"""
    __tablename__ = "parameter_evolution"
    
    id = Column(Integer, primary_key=True, index=True)
    parameter_name = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # 參數變化
    old_value = Column(Float, nullable=False)
    new_value = Column(Float, nullable=False)
    value_change_pct = Column(Float, nullable=False)
    
    # 變化原因
    change_reason = Column(String(100), nullable=False, index=True)  # phase2_learning, phase5_validation, manual_adjustment
    trigger_event = Column(String(100), nullable=True)
    
    # 影響分析
    performance_impact = Column(Float, nullable=True)
    signal_count_impact = Column(Integer, nullable=True)
    risk_impact = Column(Float, nullable=True)
    
    # 關聯記錄
    phase2_session_id = Column(String(50), nullable=True, index=True)
    phase5_backtest_id = Column(String(50), nullable=True, index=True)
    
    # 驗證
    change_validated = Column(Boolean, default=False)
    validation_period_days = Column(Integer, nullable=True)
    validation_results = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_parameter_symbol', 'parameter_name', 'symbol'),
        Index('idx_change_reason_created', 'change_reason', 'created_at'),
    )

class LearningStatistics(LearningBase):
    """學習統計摘要"""
    __tablename__ = "learning_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    
    # Phase2 學習統計
    phase2_sessions = Column(Integer, default=0)
    phase2_successful = Column(Integer, default=0)
    phase2_rollbacks = Column(Integer, default=0)
    phase2_avg_improvement = Column(Float, nullable=True)
    
    # Phase5 回測統計
    phase5_backtests = Column(Integer, default=0)
    phase5_validations_passed = Column(Integer, default=0)
    phase5_avg_similarity = Column(Float, nullable=True)
    
    # 整體效能
    overall_performance_trend = Column(Float, nullable=True)
    parameter_stability_score = Column(Float, nullable=True)
    learning_efficiency = Column(Float, nullable=True)
    
    # 統計元數據
    total_signals_processed = Column(Integer, default=0)
    total_parameter_changes = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_symbol_period', 'symbol', 'period_start', 'period_end'),
    )
