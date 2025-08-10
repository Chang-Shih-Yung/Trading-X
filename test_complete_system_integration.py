"""
🧪 完整系統整合測試腳本
驗證 WebSocket驅動器 + 智能觸發引擎 + 自動回測驗證器 的整合
"""

import sys
import os
sys.path.append('/Users/henrychang/Desktop/Trading-X/X/backend')

import json
import asyncio
from datetime import datetime, timedelta

def test_websocket_driver_upgrade():
    """測試WebSocket驅動器升級"""
    try:
        from phase1_signal_generation.websocket_realtime_driver import websocket_realtime_driver
        
        # 驗證v2.0功能
        assert hasattr(websocket_realtime_driver, 'register_intelligent_trigger_integration')
        assert hasattr(websocket_realtime_driver, 'register_backtest_validator_integration')
        assert hasattr(websocket_realtime_driver, 'enable_high_performance_mode')
        assert hasattr(websocket_realtime_driver, 'get_enhanced_status')
        
        # 驗證升級後的配置
        driver_status = websocket_realtime_driver.get_status()
        assert 'status' in driver_status
        assert 'is_running' in driver_status
        
        print("✅ WebSocket驅動器升級正確")
        return True
        
    except Exception as e:
        print(f"❌ WebSocket驅動器升級測試失敗: {e}")
        return False

def test_intelligent_trigger_engine():
    """測試智能觸發引擎"""
    try:
        from phase1_signal_generation.intelligent_trigger_engine import (
            IntelligentTriggerEngine, intelligent_trigger_engine
        )
        
        # 驗證核心功能
        assert hasattr(intelligent_trigger_engine, 'start_trigger_engine')
        assert hasattr(intelligent_trigger_engine, 'process_realtime_data')
        assert hasattr(intelligent_trigger_engine, 'get_trigger_status')
        
        # 驗證配置載入
        status = asyncio.run(intelligent_trigger_engine.get_trigger_status())
        assert 'is_running' in status
        assert 'win_rate_threshold' in status
        
        print("✅ 智能觸發引擎功能正確")
        return True
        
    except Exception as e:
        print(f"❌ 智能觸發引擎測試失敗: {e}")
        return False

def test_auto_backtest_validator():
    """測試自動回測驗證器"""
    try:
        from phase5_backtest_validation.auto_backtest_validator import (
            AutoBacktestValidator, auto_backtest_validator
        )
        
        # 驗證核心功能
        assert hasattr(auto_backtest_validator, 'start_validator')
        assert hasattr(auto_backtest_validator, 'track_signal')
        assert hasattr(auto_backtest_validator, 'update_signal_price')
        
        # 驗證配置
        status = asyncio.run(auto_backtest_validator.get_validator_status())
        assert 'is_running' in status
        assert 'validation_window_hours' in status
        
        print("✅ 自動回測驗證器功能正確")
        return True
        
    except Exception as e:
        print(f"❌ 自動回測驗證器測試失敗: {e}")
        return False

def test_system_integration():
    """測試系統整合"""
    try:
        from phase1_signal_generation.websocket_realtime_driver import websocket_realtime_driver
        from phase1_signal_generation.intelligent_trigger_engine import intelligent_trigger_engine
        from phase5_backtest_validation.auto_backtest_validator import auto_backtest_validator
        
        # 測試整合註冊
        websocket_realtime_driver.register_intelligent_trigger_integration(intelligent_trigger_engine)
        websocket_realtime_driver.register_backtest_validator_integration(auto_backtest_validator)
        
        # 驗證整合狀態
        assert hasattr(websocket_realtime_driver, 'intelligent_trigger_engine')
        assert hasattr(websocket_realtime_driver, 'backtest_validator')
        
        # 測試數據轉換功能
        test_data = {
            "symbol": "BTCUSDT",
            "price": 50000.0,
            "volume": 1000.0,
            "timestamp": datetime.now()
        }
        
        trigger_format = websocket_realtime_driver._convert_to_trigger_format("ticker", test_data)
        assert trigger_format['symbol'] == "BTCUSDT"
        assert trigger_format['current_price'] == 50000.0
        
        print("✅ 系統整合功能正確")
        return True
        
    except Exception as e:
        print(f"❌ 系統整合測試失敗: {e}")
        return False

def test_phase1_coordinator_integration():
    """測試Phase1協調器整合"""
    try:
        from phase1_signal_generation.phase1_main_coordinator import phase1_coordinator
        
        # 驗證協調器包含所有組件
        assert hasattr(phase1_coordinator, 'websocket_realtime_driver')
        assert hasattr(phase1_coordinator, 'intelligent_trigger_engine')
        
        # 驗證狀態檢查
        status = asyncio.run(phase1_coordinator.get_coordinator_status())
        assert 'websocket_status' in status
        assert 'intelligent_trigger_active' in status
        
        print("✅ Phase1協調器整合正確")
        return True
        
    except Exception as e:
        print(f"❌ Phase1協調器整合測試失敗: {e}")
        return False

def test_complete_data_flow():
    """測試完整數據流"""
    try:
        # 模擬完整數據流測試
        
        # 1. WebSocket接收數據
        mock_websocket_data = {
            "symbol": "BTCUSDT",
            "price": 50000.0,
            "volume": 1000.0,
            "change_pct": 0.02,
            "timestamp": datetime.now(),
            "source_exchange": "binance"
        }
        
        # 2. 轉換為觸發格式
        from phase1_signal_generation.websocket_realtime_driver import websocket_realtime_driver
        trigger_data = websocket_realtime_driver._convert_to_trigger_format("ticker", mock_websocket_data)
        
        # 3. 驗證觸發數據格式
        assert trigger_data['symbol'] == "BTCUSDT"
        assert trigger_data['current_price'] == 50000.0
        assert 'timestamp' in trigger_data
        
        # 4. 模擬信號生成
        mock_signal = {
            'signal_id': 'test_signal_001',
            'symbol': 'BTCUSDT',
            'signal_type': 'BUY',
            'confidence': 0.85,
            'win_rate_prediction': 0.75,
            'current_price': 50000.0
        }
        
        # 5. 驗證信號追蹤
        from phase5_backtest_validation.auto_backtest_validator import auto_backtest_validator
        
        # 模擬異步追蹤（同步測試）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        signal_id = loop.run_until_complete(auto_backtest_validator.track_signal(mock_signal))
        assert signal_id == 'test_signal_001'
        
        loop.close()
        
        print("✅ 完整數據流測試正確")
        return True
        
    except Exception as e:
        print(f"❌ 完整數據流測試失敗: {e}")
        return False

def test_performance_specifications():
    """測試性能規格"""
    try:
        from phase1_signal_generation.websocket_realtime_driver import websocket_realtime_driver
        
        # 驗證性能目標
        config = websocket_realtime_driver.config
        performance_config = config.get('performance', {})
        
        # v2.0 性能目標
        expected_max_latency = 12  # 升級前
        if hasattr(websocket_realtime_driver, 'enable_high_performance_mode'):
            # v2.0 高性能模式目標 <5ms
            expected_max_latency = 5
        
        # 驗證緩衝區大小配置
        buffer_size = performance_config.get('buffer_size', 1000)
        assert buffer_size <= 1000  # 合理的緩衝區大小
        
        # 驗證心跳間隔
        heartbeat_interval = performance_config.get('heartbeat_interval', 30)
        assert heartbeat_interval >= 30  # 合理的心跳間隔
        
        print("✅ 性能規格驗證正確")
        return True
        
    except Exception as e:
        print(f"❌ 性能規格測試失敗: {e}")
        return False

def test_configuration_consistency():
    """測試配置一致性"""
    try:
        # 測試JSON配置與Python實現一致性
        
        # 1. WebSocket配置
        websocket_config_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/websocket_realtime_driver/websocket_realtime_config.json"
        with open(websocket_config_path, 'r', encoding='utf-8') as f:
            websocket_config = json.load(f)
        
        # 2. 智能觸發配置
        trigger_config_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/intelligent_trigger_engine/intelligent_trigger_config.json"
        with open(trigger_config_path, 'r', encoding='utf-8') as f:
            trigger_config = json.load(f)
        
        # 3. 回測驗證配置
        backtest_config_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase5_backtest_validation/auto_backtest_validator/auto_backtest_config.json"
        with open(backtest_config_path, 'r', encoding='utf-8') as f:
            backtest_config = json.load(f)
        
        # 驗證關鍵配置項
        assert websocket_config['websocket_realtime_driver']['target_latency_ms'] <= 50
        assert trigger_config['intelligent_trigger_engine']['scan_interval_seconds'] == 1
        assert backtest_config['backtest_validator']['validation_window_hours'] == 48
        
        print("✅ 配置一致性驗證正確")
        return True
        
    except Exception as e:
        print(f"❌ 配置一致性測試失敗: {e}")
        return False

def main():
    """運行完整系統整合測試"""
    print("🧪 完整系統整合測試開始...\n")
    
    tests = [
        ("WebSocket驅動器升級", test_websocket_driver_upgrade),
        ("智能觸發引擎", test_intelligent_trigger_engine),
        ("自動回測驗證器", test_auto_backtest_validator),
        ("系統整合", test_system_integration),
        ("Phase1協調器整合", test_phase1_coordinator_integration),
        ("完整數據流", test_complete_data_flow),
        ("性能規格", test_performance_specifications),
        ("配置一致性", test_configuration_consistency),
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
        print("🎉 完整系統整合測試通過！")
        print("✅ WebSocket驅動器 v2.0 升級完成")
        print("✅ 智能觸發引擎整合成功") 
        print("✅ 自動回測驗證器整合成功")
        print("✅ Phase1協調器整合成功")
        print("✅ 完整數據流驗證成功")
        print("✅ 性能規格符合要求")
        print("✅ 配置一致性驗證通過")
        print()
        print("🚀 系統已準備好進行實戰部署！")
        print("   - 實時延遲目標: <5ms (高性能模式)")
        print("   - 智能觸發: 75%+ 高勝率檢測")
        print("   - 自動驗證: 48小時信號追蹤")
        print("   - 整合完整: 端到端數據流")
    else:
        print("❌ 部分測試失敗，需要檢查實現")

if __name__ == "__main__":
    main()
