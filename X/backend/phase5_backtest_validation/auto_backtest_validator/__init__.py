"""
🎯 Trading X - Phase5 自動回測驗證器模組
導出所有核心組件和便捷函數
"""

from .auto_backtest_validator import (
    # 核心類
    AutoBacktestValidator,
    
    # 數據結構
    BacktestSignal,
    PerformanceMetrics,
    DynamicThresholds,
    ValidationWindow,
    ValidationStatus,
    SignalPerformanceClass,
    MarketConditionType,
    
    # 全局實例
    auto_backtest_validator,
    
    # 便捷函數
    start_auto_backtest_validator,
    stop_auto_backtest_validator,
    track_signal_for_validation,
    update_signal_validation_price,
    subscribe_to_validation_results,
    subscribe_to_threshold_updates,
    get_backtest_validator_status,
    get_backtest_performance_summary,
)

__all__ = [
    # 核心類
    'AutoBacktestValidator',
    
    # 數據結構
    'BacktestSignal',
    'PerformanceMetrics', 
    'DynamicThresholds',
    'ValidationWindow',
    'ValidationStatus',
    'SignalPerformanceClass',
    'MarketConditionType',
    
    # 全局實例
    'auto_backtest_validator',
    
    # 便捷函數
    'start_auto_backtest_validator',
    'stop_auto_backtest_validator',
    'track_signal_for_validation',
    'update_signal_validation_price',
    'subscribe_to_validation_results',
    'subscribe_to_threshold_updates',
    'get_backtest_validator_status',
    'get_backtest_performance_summary',
]
