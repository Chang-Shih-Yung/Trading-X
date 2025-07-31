#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading X Phase 3 第二優先級系統測試
測試事件信號乘數框架、動態重分配算法、週期切換機制的完整功能
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_event_signal_multiplier():
    """測試事件信號乘數框架"""
    print("\n🎯 測試事件信號乘數框架")
    print("=" * 60)
    
    try:
        from app.services.event_signal_multiplier import (
            event_signal_multiplier, 
            EventType, 
            EventSeverity,
            EventDirection
        )
        
        print("📅 創建測試市場事件...")
        
        # 創建FOMC事件 (即將開始的事件)
        fomc_time = datetime.now() + timedelta(hours=1)  # 1小時後，應該在準備期內
        fomc_id = event_signal_multiplier.create_event(
            event_type=EventType.FOMC_MEETING,
            title="聯準會利率決議會議",
            severity=EventSeverity.HIGH,
            direction=EventDirection.VOLATILE,
            event_time=fomc_time,
            affected_symbols=["BTCUSDT", "ETHUSDT"],
            confidence=0.95
        )
        print(f"   ✅ 創建 FOMC 事件: {fomc_id}")
        
        # 創建減半事件
        halving_time = datetime.now() + timedelta(days=30)
        halving_id = event_signal_multiplier.create_event(
            event_type=EventType.HALVING_EVENT,
            title="比特幣減半事件",
            severity=EventSeverity.CRITICAL,
            direction=EventDirection.BULLISH,
            event_time=halving_time,
            affected_symbols=["BTCUSDT"],
            confidence=0.98
        )
        print(f"   ✅ 創建減半事件: {halving_id}")
        
        # 創建閃崩事件 (剛剛發生，應該還在影響窗口內)
        crash_time = datetime.now() - timedelta(hours=1)  # 1小時前，應該還在影響範圍內
        crash_id = event_signal_multiplier.create_event(
            event_type=EventType.FLASH_CRASH,
            title="市場閃崩事件",
            severity=EventSeverity.HIGH,
            direction=EventDirection.BEARISH,
            event_time=crash_time,
            affected_symbols=["BTCUSDT", "ETHUSDT", "ADAUSDT"],
            confidence=0.97
        )
        print(f"   ✅ 創建閃崩事件: {crash_id}")
        
        print(f"\n💡 測試事件乘數計算...")
        
        # 計算BTCUSDT的事件乘數
        multipliers = event_signal_multiplier.calculate_event_multipliers("BTCUSDT")
        
        print(f"📊 BTCUSDT 當前乘數:")
        print(f"   應用的乘數: {multipliers.applied_multipliers}")
        print(f"   總體影響: {multipliers.total_multiplier_effect:.3f}")
        print(f"   信心調整: {multipliers.confidence_adjustment:.3f}")
        print(f"   風險調整: {multipliers.risk_adjustment:.3f}")
        print(f"   說明: {multipliers.explanation}")
        
        # 獲取事件分析
        analysis = event_signal_multiplier.export_event_analysis()
        print(f"\n📋 活躍事件總數: {analysis['active_events_count']}")
        print(f"📅 未來72小時事件: {len(analysis.get('upcoming_events', []))}")
        
        # 統計信息
        stats = analysis.get('system_stats', {})
        print(f"\n📈 系統統計:")
        print(f"   總事件數: {stats.get('total_events', 0)}")
        print(f"   活躍事件數: {stats.get('active_events', 0)}")
        print(f"   乘數計算次數: {stats.get('multiplier_calculations', 0)}")
        
        print("✅ 事件信號乘數框架測試成功!")
        return True
        
    except Exception as e:
        print(f"❌ 事件信號乘數框架測試失敗: {e}")
        return False

async def test_dynamic_reallocation():
    """測試動態重分配算法"""
    print("\n🎯 測試動態重分配算法")
    print("=" * 60)
    
    try:
        from app.services.dynamic_reallocation_engine import dynamic_reallocation_engine
        
        print("⚙️ 測試動態重分配引擎...")
        
        # 測試手動重分配
        print("🔧 執行手動重分配測試...")
        
        test_weights = {
            "precision_filter_weight": 0.25,
            "market_condition_weight": 0.20,
            "technical_analysis_weight": 0.20,
            "regime_analysis_weight": 0.15,
            "fear_greed_weight": 0.10,
            "trend_alignment_weight": 0.05,
            "market_depth_weight": 0.03,
            "funding_rate_weight": 0.01,
            "smart_money_weight": 0.01
        }
        
        optimization_result = await dynamic_reallocation_engine.execute_reallocation(
            symbol="BTCUSDT",
            timeframe="medium",
            trigger="manual_override",
            current_weights=test_weights
        )
        
        if optimization_result:
            print(f"✅ 重分配優化成功:")
            print(f"   原始權重: {optimization_result.original_weights}")
            print(f"   優化權重: {optimization_result.optimized_weights}")
            print(f"   預期改善: {optimization_result.expected_improvement:.4f}")
            # 安全地訪問 optimization_method
            method_str = optimization_result.optimization_method.value if hasattr(optimization_result.optimization_method, 'value') else str(optimization_result.optimization_method)
            print(f"   優化方法: {method_str}")
            print(f"   迭代次數: {optimization_result.iterations}")
            print(f"   收斂狀態: {optimization_result.convergence_achieved}")
        else:
            print("⚠️ 重分配未執行（條件不滿足）")
        
        # 檢查引擎狀態
        status = dynamic_reallocation_engine.export_engine_status()
        print(f"\n📊 引擎狀態:")
        print(f"   監控狀態: {'運行中' if status['is_monitoring'] else '未運行'}")
        stats = status['stats']
        print(f"   總重分配數: {stats['total_reallocations']}")
        print(f"   成功重分配數: {stats['successful_reallocations']}")
        print(f"   平均改善: {stats.get('avg_improvement', 0):.4f}")
        
        # 測試監控系統
        print(f"\n🚀 測試監控系統...")
        await dynamic_reallocation_engine.start_monitoring()
        print("   ✅ 監控系統啟動成功")
        
        # 讓監控運行一小段時間
        await asyncio.sleep(2)
        
        await dynamic_reallocation_engine.stop_monitoring()
        print("   ⏹️ 監控系統停止成功")
        
        print("✅ 動態重分配算法測試成功!")
        return True
        
    except Exception as e:
        print(f"❌ 動態重分配算法測試失敗: {e}")
        return False

async def test_timeframe_switching():
    """測試週期切換機制"""
    print("\n🎯 測試週期切換機制")
    print("=" * 60)
    
    try:
        from app.services.timeframe_switch_engine import (
            timeframe_switch_engine,
            SwitchTrigger
        )
        
        print("🔄 測試時間框架切換引擎...")
        
        # 獲取當前時間框架
        current_timeframes = timeframe_switch_engine.get_current_timeframes()
        print(f"📊 當前時間框架分配:")
        for symbol, timeframe in current_timeframes.items():
            print(f"   {symbol}: {timeframe}")
        
        # 執行手動切換測試
        print(f"\n🔧 執行手動切換測試...")
        
        # 獲取市場條件快照
        market_condition = await timeframe_switch_engine._get_market_condition_snapshot("BTCUSDT")
        if market_condition:
            print(f"📈 BTCUSDT 市場條件:")
            print(f"   波動率: {market_condition.realized_volatility:.3f}")
            print(f"   趨勢強度: {market_condition.trend_strength:.3f}")
            # 安全地訪問 current_regime
            regime_str = market_condition.current_regime.value if hasattr(market_condition.current_regime, 'value') else str(market_condition.current_regime)
            print(f"   當前制度: {regime_str}")
            print(f"   制度信心: {market_condition.regime_confidence:.3f}")
        
        # 執行時間框架切換
        switch_event = await timeframe_switch_engine.execute_timeframe_switch(
            symbol="BTCUSDT",
            target_timeframe="short",
            trigger=SwitchTrigger.MANUAL_OVERRIDE,
            market_condition=market_condition,
            confidence_score=0.8,
            manual_override=True
        )
        
        if switch_event:
            print(f"✅ 時間框架切換成功:")
            print(f"   切換方向: {switch_event.from_timeframe} → {switch_event.to_timeframe}")
            # 安全地訪問 enum 字段
            direction_str = switch_event.switch_direction.value if hasattr(switch_event.switch_direction, 'value') else str(switch_event.switch_direction)
            trigger_str = switch_event.trigger.value if hasattr(switch_event.trigger, 'value') else str(switch_event.trigger)
            print(f"   切換方向類型: {direction_str}")
            print(f"   觸發條件: {trigger_str}")
            print(f"   信心評分: {switch_event.confidence_score:.3f}")
            print(f"   預期改善: {switch_event.expected_performance_improvement:.4f}")
            print(f"   預期持續: {switch_event.expected_duration_hours} 小時")
        else:
            print("⚠️ 時間框架切換未執行")
        
        # 獲取切換歷史
        switch_analysis = timeframe_switch_engine.export_switch_analysis()
        history = switch_analysis.get("switch_history_24h", [])
        print(f"\n📋 24小時切換歷史: {len(history)} 筆")
        
        # 檢查引擎狀態
        engine_status = switch_analysis.get("engine_status", {})
        print(f"\n📊 切換引擎狀態:")
        print(f"   監控狀態: {'運行中' if engine_status.get('is_monitoring', False) else '未運行'}")
        stats = engine_status.get("stats", {})
        print(f"   總切換數: {stats.get('total_switches', 0)}")
        print(f"   成功切換數: {stats.get('successful_switches', 0)}")
        print(f"   切換準確率: {stats.get('switch_accuracy', 0):.3f}")
        
        # 性能檔案
        performance_summary = switch_analysis.get("timeframe_performance_summary", {})
        print(f"\n📈 性能檔案摘要: {len(performance_summary)} 個檔案")
        
        # 測試監控系統
        print(f"\n🚀 測試監控系統...")
        await timeframe_switch_engine.start_monitoring()
        print("   ✅ 切換監控啟動成功")
        
        await asyncio.sleep(1)
        
        await timeframe_switch_engine.stop_monitoring()
        print("   ⏹️ 切換監控停止成功")
        
        print("✅ 週期切換機制測試成功!")
        return True
        
    except Exception as e:
        print(f"❌ 週期切換機制測試失敗: {e}")
        return False

async def test_system_integration():
    """測試系統整合"""
    print("\n🎯 測試第二優先級系統整合")
    print("=" * 60)
    
    try:
        from app.services.event_signal_multiplier import (
            event_signal_multiplier, 
            EventType, 
            EventSeverity,
            EventDirection
        )
        from app.services.dynamic_reallocation_engine import dynamic_reallocation_engine
        from app.services.timeframe_switch_engine import timeframe_switch_engine
        from app.services.signal_availability_monitor import signal_availability_monitor
        
        print("🔗 測試系統間協作...")
        
        # 1. 創建市場事件
        event_time = datetime.now() + timedelta(hours=2)
        event_id = event_signal_multiplier.create_event(
            event_type=EventType.NFP_RELEASE,
            title="非農就業數據發布",
            severity=EventSeverity.HIGH,
            direction=EventDirection.VOLATILE,
            event_time=event_time,
            affected_symbols=["BTCUSDT"],
            confidence=0.85
        )
        print(f"   ✅ 創建整合測試事件: {event_id}")
        
        # 2. 計算事件乘數
        multipliers = event_signal_multiplier.calculate_event_multipliers("BTCUSDT")
        print(f"   📊 事件乘數計算完成: {len(multipliers.applied_multipliers)} 個乘數")
        
        # 3. 觸發重分配（模擬事件影響）
        if multipliers.applied_multipliers:
            print("   🔧 觸發動態重分配...")
            reallocation_result = await dynamic_reallocation_engine.execute_reallocation(
                symbol="BTCUSDT",
                timeframe="medium",
                trigger="signal_quality_change"
            )
            
            if reallocation_result:
                print(f"   ✅ 重分配執行成功，預期改善: {reallocation_result.expected_improvement:.4f}")
            else:
                print("   ⚠️ 重分配未執行（改善不足）")
        
        # 4. 檢查時間框架切換建議
        market_condition = await timeframe_switch_engine._get_market_condition_snapshot("BTCUSDT")
        if market_condition and market_condition.realized_volatility > 0.6:
            print("   🔄 高波動檢測，建議短線切換...")
            switch_result = await timeframe_switch_engine.execute_timeframe_switch(
                symbol="BTCUSDT",
                target_timeframe="short",
                trigger="volatility_regime_change",
                market_condition=market_condition,
                confidence_score=0.75
            )
            
            if switch_result:
                print(f"   ✅ 時間框架切換至: {switch_result.to_timeframe}")
        
        # 5. 系統狀態總覽
        print(f"\n📊 系統狀態總覽:")
        
        # 事件系統狀態
        event_analysis = event_signal_multiplier.export_event_analysis()
        print(f"   事件系統: {event_analysis['active_events_count']} 個活躍事件")
        
        # 重分配系統狀態
        reallocation_status = dynamic_reallocation_engine.export_engine_status()
        print(f"   重分配系統: {reallocation_status['stats']['total_reallocations']} 次重分配")
        
        # 切換系統狀態
        switch_status = timeframe_switch_engine.export_switch_analysis()
        print(f"   切換系統: {switch_status['engine_status']['stats']['total_switches']} 次切換")
        
        # 信號監控狀態
        signal_status = signal_availability_monitor.get_system_status()
        print(f"   信號監控: {signal_status['available_signals']}/{signal_status['total_signals']} 可用")
        
        print("✅ 系統整合測試成功!")
        return True
        
    except Exception as e:
        print(f"❌ 系統整合測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主測試函數"""
    print("🚀 第二優先級系統測試 - 完整測試套件")
    print("=" * 80)
    print("測試項目:")
    print("1. 事件信號乘數框架")
    print("2. 動態重分配算法")
    print("3. 週期切換機制")
    print("4. 系統整合")
    print("=" * 80)
    
    # 執行所有測試
    test_results = {}
    
    # 1. 測試事件信號乘數框架
    test_results["event_multiplier"] = test_event_signal_multiplier()
    
    # 2. 測試動態重分配算法
    test_results["dynamic_reallocation"] = await test_dynamic_reallocation()
    
    # 3. 測試週期切換機制
    test_results["timeframe_switching"] = await test_timeframe_switching()
    
    # 4. 測試系統整合
    test_results["system_integration"] = await test_system_integration()
    
    # 測試結果總結
    print("\n" + "=" * 80)
    print("🎯 第二優先級系統測試結果:")
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        test_display_name = {
            "event_multiplier": "事件信號乘數框架",
            "dynamic_reallocation": "動態重分配算法", 
            "timeframe_switching": "週期切換機制",
            "system_integration": "系統整合"
        }.get(test_name, test_name)
        
        print(f"   {total_tests - len(test_results) + list(test_results.keys()).index(test_name) + 1}. {test_display_name}: {status}")
        if result:
            passed_tests += 1
    
    # 計算通過率
    pass_rate = (passed_tests / total_tests) * 100
    print(f"\n📊 測試通過率: {pass_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if pass_rate == 100:
        print("🎉 所有測試通過！")
    elif pass_rate >= 75:
        print("⚠️  部分測試失敗，請檢查相關模組。")
    else:
        print("❌ 多項測試失敗，需要檢查系統實現。")
    
    print(f"\n📋 第二優先級（2週內）實施狀態: {'✅ 完成' if pass_rate >= 75 else '⚠️ 需要修復'}")

if __name__ == "__main__":
    asyncio.run(main())
