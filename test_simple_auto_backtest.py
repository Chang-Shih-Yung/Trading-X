"""
🧪 自動回測驗證器測試腳本
驗證 auto_backtest_validator.py 實現的正確性
"""

import sys
import os
sys.path.append('/Users/henrychang/Desktop/Trading-X/X/backend')

import json
from datetime import datetime, timedelta

def test_json_config_loading():
    """測試JSON配置載入"""
    try:
        config_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase5_backtest_validation/auto_backtest_validator/auto_backtest_config.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 驗證核心配置
        assert 'backtest_validator' in config
        assert 'validation_methodology' in config
        assert 'dynamic_threshold_system' in config
        assert 'signal_categorization' in config
        
        # 驗證具體配置值
        validator_config = config['backtest_validator']
        assert validator_config['validation_window_hours'] == 48
        assert validator_config['update_frequency_minutes'] == 30
        assert validator_config['parallel_validation'] is True
        
        print("✅ JSON配置載入正確")
        return True
        
    except Exception as e:
        print(f"❌ JSON配置載入失敗: {e}")
        return False

def test_data_structures():
    """測試數據結構定義"""
    try:
        from phase5_backtest_validation.auto_backtest_validator import (
            BacktestSignal, PerformanceMetrics, DynamicThresholds, 
            ValidationWindow, ValidationStatus, SignalPerformanceClass, 
            MarketConditionType
        )
        
        # 測試BacktestSignal
        signal = BacktestSignal(
            signal_id="test_001",
            symbol="BTCUSDT",
            signal_type="BUY",
            priority="HIGH",
            confidence=0.85,
            win_rate_prediction=0.75,
            entry_price=50000.0,
            entry_time=datetime.now()
        )
        assert signal.status == ValidationStatus.PENDING
        
        # 測試枚舉
        assert ValidationStatus.TRACKING.value == "tracking"
        assert SignalPerformanceClass.EXCELLENT.value == "excellent"
        assert MarketConditionType.TREND_BULLISH.value == "trend_bullish"
        
        # 測試DynamicThresholds
        thresholds = DynamicThresholds(
            win_rate_threshold=0.70,
            profit_loss_threshold=1.5,
            confidence_threshold=0.80,
            last_updated=datetime.now(),
            adjustment_reason="test",
            market_condition_factor=1.0,
            volatility_factor=1.0
        )
        assert thresholds.win_rate_threshold == 0.70
        
        print("✅ 數據結構定義完整")
        return True
        
    except Exception as e:
        print(f"❌ 數據結構測試失敗: {e}")
        return False

def test_validator_initialization():
    """測試驗證器初始化"""
    try:
        from phase5_backtest_validation.auto_backtest_validator import AutoBacktestValidator
        
        # 使用預設配置初始化
        validator = AutoBacktestValidator()
        
        # 驗證基本屬性
        assert validator.is_running is False
        assert validator.validation_window_hours == 48
        assert len(validator.active_signals) == 0
        assert len(validator.completed_validations) == 0
        assert len(validator.performance_history) == 0
        
        # 驗證統計數據
        expected_stats_keys = [
            'total_signals_tracked', 'completed_validations', 'excellent_signals',
            'good_signals', 'marginal_signals', 'poor_signals', 
            'threshold_adjustments', 'emergency_stops'
        ]
        for key in expected_stats_keys:
            assert key in validator.stats
            assert validator.stats[key] == 0
        
        # 驗證閾值初始化
        assert validator.current_thresholds.win_rate_threshold == 0.70
        assert validator.current_thresholds.profit_loss_threshold == 1.5
        
        print("✅ 驗證器初始化正確")
        return True
        
    except Exception as e:
        print(f"❌ 驗證器初始化失敗: {e}")
        return False

def test_signal_tracking():
    """測試信號追蹤"""
    try:
        from phase5_backtest_validation.auto_backtest_validator import AutoBacktestValidator
        
        validator = AutoBacktestValidator()
        
        # 模擬信號數據
        signal_data = {
            'signal_id': 'test_signal_001',
            'symbol': 'BTCUSDT',
            'signal_type': 'BUY',
            'priority': 'HIGH',
            'confidence': 0.85,
            'win_rate_prediction': 0.75,
            'current_price': 50000.0,
            'market_conditions': ['trend_bullish'],
            'technical_analysis': {'rsi': 65, 'macd': 'bullish'},
            'risk_metrics': {'volatility': 0.03},
            'trigger_metadata': {'source': 'intelligent_trigger'}
        }
        
        # 模擬異步追蹤 (同步測試)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        signal_id = loop.run_until_complete(validator.track_signal(signal_data))
        
        # 驗證追蹤結果
        assert signal_id == 'test_signal_001'
        assert signal_id in validator.active_signals
        assert validator.stats['total_signals_tracked'] == 1
        
        # 驗證信號狀態
        tracked_signal = validator.active_signals[signal_id]
        assert tracked_signal.symbol == 'BTCUSDT'
        assert tracked_signal.confidence == 0.85
        assert tracked_signal.status.value == 'tracking'
        
        loop.close()
        
        print("✅ 信號追蹤功能正確")
        return True
        
    except Exception as e:
        print(f"❌ 信號追蹤測試失敗: {e}")
        return False

def test_performance_calculation():
    """測試性能計算"""
    try:
        from phase5_backtest_validation.auto_backtest_validator import AutoBacktestValidator, BacktestSignal, ValidationStatus
        
        validator = AutoBacktestValidator()
        
        # 創建測試信號
        signals = []
        for i in range(10):
            signal = BacktestSignal(
                signal_id=f"test_{i}",
                symbol="BTCUSDT",
                signal_type="BUY",
                priority="HIGH",
                confidence=0.8,
                win_rate_prediction=0.7,
                entry_price=50000.0,
                entry_time=datetime.now() - timedelta(hours=i),
                exit_price=50000.0 * (1.02 if i % 2 == 0 else 0.98),  # 50%勝率
                exit_time=datetime.now() - timedelta(hours=i-1),
                status=ValidationStatus.COMPLETED,
                holding_duration=timedelta(hours=1)
            )
            # 計算盈虧
            signal.profit_loss_pct = (signal.exit_price - signal.entry_price) / signal.entry_price
            signals.append(signal)
        
        # 計算性能指標
        performance = validator._calculate_performance_metrics(signals)
        
        # 驗證計算結果
        assert performance is not None
        assert performance.total_trades == 10
        assert performance.successful_trades == 5  # 50%勝率
        assert abs(performance.win_rate - 0.5) < 0.01
        assert performance.sample_size == 10
        
        print("✅ 性能計算功能正確")
        return True
        
    except Exception as e:
        print(f"❌ 性能計算測試失敗: {e}")
        return False

def test_global_functions():
    """測試全局函數"""
    try:
        from phase5_backtest_validation.auto_backtest_validator import (
            auto_backtest_validator,
            start_auto_backtest_validator,
            track_signal_for_validation,
            subscribe_to_validation_results,
            get_backtest_validator_status
        )
        
        # 驗證全局實例
        assert auto_backtest_validator is not None
        assert hasattr(auto_backtest_validator, 'start_validator')
        assert hasattr(auto_backtest_validator, 'track_signal')
        
        # 驗證函數存在
        assert callable(start_auto_backtest_validator)
        assert callable(track_signal_for_validation)
        assert callable(subscribe_to_validation_results)
        assert callable(get_backtest_validator_status)
        
        print("✅ 全局函數定義正確")
        return True
        
    except Exception as e:
        print(f"❌ 全局函數測試失敗: {e}")
        return False

def test_config_consistency():
    """測試配置與代碼一致性"""
    try:
        config_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase5_backtest_validation/auto_backtest_validator/auto_backtest_config.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        from phase5_backtest_validation.auto_backtest_validator import AutoBacktestValidator
        
        validator = AutoBacktestValidator()
        
        # 驗證配置一致性
        assert validator.validation_window_hours == config['backtest_validator']['validation_window_hours']
        
        performance_config = config['validation_methodology']['performance_metrics']
        assert validator.current_thresholds.win_rate_threshold == performance_config['win_rate']['target_threshold']
        assert validator.current_thresholds.profit_loss_threshold == performance_config['profit_loss_ratio']['target_threshold']
        
        # 驗證閾值邊界
        bounds = config['dynamic_threshold_system']['threshold_bounds']
        assert 'win_rate_min' in bounds
        assert 'win_rate_max' in bounds
        assert 'profit_loss_min' in bounds
        assert 'profit_loss_max' in bounds
        
        print("✅ 配置與代碼一致")
        return True
        
    except Exception as e:
        print(f"❌ 配置一致性測試失敗: {e}")
        return False

def main():
    """運行所有測試"""
    print("🧪 自動回測驗證器實現測試開始...\n")
    
    tests = [
        ("JSON配置載入", test_json_config_loading),
        ("數據結構定義", test_data_structures),
        ("驗證器初始化", test_validator_initialization),
        ("信號追蹤功能", test_signal_tracking),
        ("性能計算功能", test_performance_calculation),
        ("全局函數定義", test_global_functions),
        ("配置與代碼一致性", test_config_consistency),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🔬 測試: {test_name}")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 自動回測驗證器Python實現測試通過！")
        print("✅ JSON配置載入正確")
        print("✅ 數據結構定義完整") 
        print("✅ 驗證器初始化正確")
        print("✅ 信號追蹤功能正確")
        print("✅ 性能計算功能正確")
        print("✅ 全局函數定義正確")
        print("✅ 配置與代碼一致")
    else:
        print("❌ 部分測試失敗，需要檢查實現")

if __name__ == "__main__":
    main()
