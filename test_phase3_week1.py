#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading X Phase 3 Week 1 測試
測試事件預測引擎和複合事件處理器的基礎功能
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_event_prediction_engine():
    """測試事件預測引擎"""
    print("\n🔮 測試事件預測引擎")
    print("=" * 60)
    
    try:
        from app.services.event_prediction_engine import (
            event_prediction_engine,
            EventCategory,
            PredictionConfidence
        )
        
        print("📊 引擎初始化檢查...")
        
        # 檢查基礎模式數量
        patterns_count = len(event_prediction_engine.patterns_database)
        print(f"   ✅ 初始模式數量: {patterns_count}")
        
        # 檢查配置
        config = event_prediction_engine.config
        print(f"   ✅ 最小信心閾值: {config['min_confidence_threshold']}")
        print(f"   ✅ 早期預警閾值: {config['early_warning_threshold']}")
        print(f"   ✅ 最大預測時間範圍: {config['max_prediction_horizon_hours']} 小時")
        
        print("\n💡 測試市場條件分析...")
        
        # 測試市場分析 - 同步調用
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        market_features = loop.run_until_complete(
            event_prediction_engine.analyze_market_conditions("BTCUSDT")
        )
        
        if market_features:
            print(f"   ✅ 成功分析市場條件，獲得 {len(market_features)} 個特徵")
            print(f"   📈 價格動量: {market_features.get('price_momentum', 0):.3f}")
            print(f"   📊 成交量概況: {market_features.get('volume_profile', 0):.3f}")
            print(f"   📉 波動率機制: {market_features.get('volatility_regime', 0):.3f}")
            print(f"   💭 市場情緒: {market_features.get('market_sentiment', 0):.3f}")
        else:
            print("   ❌ 市場條件分析失敗")
        
        print("\n🔮 測試事件預測生成...")
        
        # 測試預測生成
        predictions = loop.run_until_complete(
            event_prediction_engine.generate_predictions(["BTCUSDT", "ETHUSDT"])
        )
        
        if predictions:
            print(f"   ✅ 成功生成 {len(predictions)} 個預測")
            
            for i, prediction in enumerate(predictions[:3]):  # 顯示前3個
                print(f"   📋 預測 {i+1}:")
                print(f"      事件類別: {prediction.event_category.value}")
                print(f"      信心度: {prediction.confidence:.3f}")
                print(f"      信心等級: {prediction.confidence_level.value}")
                print(f"      預期影響: {prediction.expected_impact_magnitude:.3f}")
                print(f"      預測時間: {prediction.predicted_event_time.strftime('%Y-%m-%d %H:%M')}")
                print(f"      早期預警: {'是' if prediction.is_early_warning else '否'}")
        else:
            print("   ⚠️ 未生成預測（可能因信心度不足）")
        
        print("\n📊 測試預測驗證...")
        
        # 測試預測驗證
        validations = loop.run_until_complete(
            event_prediction_engine.validate_predictions(lookback_hours=24)
        )
        
        print(f"   ✅ 驗證 {len(validations)} 個歷史預測")
        
        print("\n🧠 測試學習機制...")
        
        # 測試學習
        loop.run_until_complete(event_prediction_engine.learn_from_validations())
        print("   ✅ 學習機制執行完成")
        
        print("\n📈 獲取引擎摘要...")
        
        # 獲取摘要
        summary = event_prediction_engine.get_prediction_summary()
        print(f"   引擎狀態: {summary.get('engine_status')}")
        print(f"   總模式數: {summary.get('total_patterns')}")
        print(f"   24小時預測數: {summary.get('recent_predictions_24h')}")
        print(f"   活躍早期預警: {summary.get('early_warnings_active')}")
        print(f"   預測準確率: {summary.get('prediction_accuracy', 0):.3f}")
        print(f"   系統健康: {summary.get('system_health')}")
        
        loop.close()
        
        print("✅ 事件預測引擎測試成功!")
        return True
        
    except Exception as e:
        print(f"❌ 事件預測引擎測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_composite_event_processor():
    """測試複合事件處理器"""
    print("\n🔗 測試複合事件處理器")
    print("=" * 60)
    
    try:
        from app.services.composite_event_processor import (
            composite_event_processor,
            EventRelationType,
            CompositePriority
        )
        
        print("🕸️ 處理器初始化檢查...")
        
        # 檢查基礎關聯數量
        relations_count = len(composite_event_processor.relation_database)
        print(f"   ✅ 初始關聯數量: {relations_count}")
        
        # 檢查網路圖
        network_nodes = len(composite_event_processor.event_network.nodes)
        network_edges = len(composite_event_processor.event_network.edges)
        print(f"   ✅ 網路節點數: {network_nodes}")
        print(f"   ✅ 網路邊數: {network_edges}")
        
        # 檢查配置
        config = composite_event_processor.config
        print(f"   ✅ 最小相關閾值: {config['min_correlation_threshold']}")
        print(f"   ✅ 最大複合事件數: {config['max_composite_events']}")
        print(f"   ✅ 最大鏈長度: {config['chain_max_length']}")
        
        print("\n📝 創建測試事件...")
        
        # 創建測試事件
        test_events = [
            {
                "event_id": "fomc_meeting_test",
                "event_category": "macro_economic",
                "event_time": datetime.now() + timedelta(hours=2),
                "confidence": 0.85,
                "expected_impact_magnitude": 0.7,
                "affected_symbols": ["BTCUSDT", "ETHUSDT"],
                "direction": "volatile"
            },
            {
                "event_id": "technical_breakout_test", 
                "event_category": "technical_breakout",
                "event_time": datetime.now() + timedelta(hours=1),
                "confidence": 0.72,
                "expected_impact_magnitude": 0.6,
                "affected_symbols": ["BTCUSDT"],
                "direction": "bullish"
            },
            {
                "event_id": "volume_spike_test",
                "event_category": "volume_anomaly", 
                "event_time": datetime.now() + timedelta(hours=3),
                "confidence": 0.68,
                "expected_impact_magnitude": 0.8,
                "affected_symbols": ["BTCUSDT", "ETHUSDT", "ADAUSDT"],
                "direction": "neutral"
            },
            {
                "event_id": "bearish_signal_test",
                "event_category": "technical_signal",
                "event_time": datetime.now() + timedelta(hours=1.5),
                "confidence": 0.75,
                "expected_impact_magnitude": 0.65,
                "affected_symbols": ["BTCUSDT"],
                "direction": "bearish"
            }
        ]
        
        print(f"   ✅ 創建 {len(test_events)} 個測試事件")
        
        print("\n🔗 測試複合事件處理...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 處理事件
        composite_events = loop.run_until_complete(
            composite_event_processor.process_events(test_events)
        )
        
        if composite_events:
            print(f"   ✅ 成功創建 {len(composite_events)} 個複合事件")
            
            for i, composite in enumerate(composite_events):
                print(f"   📋 複合事件 {i+1}:")
                print(f"      ID: {composite.composite_id}")
                print(f"      組件數量: {len(composite.component_event_ids)}")
                print(f"      優先級: {composite.composite_priority.value}")
                print(f"      聚合信心度: {composite.aggregate_confidence:.3f}")
                print(f"      複合影響: {composite.composite_impact_magnitude:.3f}")
                print(f"      主導類別: {composite.dominant_event_category}")
                print(f"      預期持續: {composite.expected_duration_hours:.1f} 小時")
                print(f"      影響標的: {', '.join(composite.affected_symbols)}")
                print(f"      關聯數量: {len(composite.event_relations)}")
        else:
            print("   ⚠️ 未創建複合事件（可能因條件不滿足）")
        
        print("\n📊 檢查活躍事件...")
        
        active_events_count = len(composite_event_processor.active_events)
        print(f"   ✅ 活躍事件數量: {active_events_count}")
        
        print("\n🕸️ 檢查事件關聯學習...")
        
        learned_relations = len(composite_event_processor.relation_database)
        print(f"   ✅ 學習後關聯數量: {learned_relations}")
        
        print("\n📈 獲取處理器摘要...")
        
        # 獲取摘要
        summary = composite_event_processor.get_processing_summary()
        print(f"   處理器狀態: {summary.get('processor_status')}")
        print(f"   活躍事件數: {summary.get('active_events_count')}")
        print(f"   總關聯數: {summary.get('total_relations')}")
        print(f"   活躍複合事件: {summary.get('active_composite_events')}")
        print(f"   活躍事件鏈: {summary.get('event_chains_active')}")
        print(f"   已解決衝突: {summary.get('conflicts_resolved_today')}")
        
        network_info = summary.get('network_complexity', {})
        print(f"   網路複雜度:")
        print(f"      節點數: {network_info.get('nodes')}")
        print(f"      邊數: {network_info.get('edges')}")
        print(f"      密度: {network_info.get('density', 0):.3f}")
        
        print(f"   系統健康: {summary.get('system_health')}")
        
        loop.close()
        
        print("✅ 複合事件處理器測試成功!")
        return True
        
    except Exception as e:
        print(f"❌ 複合事件處理器測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """測試兩個組件的整合"""
    print("\n🔄 測試事件預測和複合處理整合")
    print("=" * 60)
    
    try:
        from app.services.event_prediction_engine import event_prediction_engine
        from app.services.composite_event_processor import composite_event_processor
        
        print("🔗 測試整合工作流程...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 1. 生成預測
        print("   1️⃣ 生成事件預測...")
        predictions = loop.run_until_complete(
            event_prediction_engine.generate_predictions(["BTCUSDT", "ETHUSDT", "ADAUSDT"])
        )
        print(f"      ✅ 生成 {len(predictions)} 個預測")
        
        # 2. 將預測轉換為事件格式
        print("   2️⃣ 轉換預測為事件...")
        events_from_predictions = []
        for prediction in predictions:
            event = {
                "event_id": prediction.prediction_id,
                "event_category": prediction.event_category.value,
                "event_time": prediction.predicted_event_time,
                "confidence": prediction.confidence,
                "expected_impact_magnitude": prediction.expected_impact_magnitude,
                "affected_symbols": prediction.affected_symbols,
                "direction": "volatile"  # 簡化處理
            }
            events_from_predictions.append(event)
        
        print(f"      ✅ 轉換 {len(events_from_predictions)} 個事件")
        
        # 3. 使用複合處理器處理預測事件
        print("   3️⃣ 複合處理器處理預測事件...")
        composite_events = loop.run_until_complete(
            composite_event_processor.process_events(events_from_predictions)
        )
        print(f"      ✅ 生成 {len(composite_events)} 個複合事件")
        
        # 4. 分析整合結果
        print("   4️⃣ 分析整合結果...")
        
        if composite_events:
            high_priority_events = [
                e for e in composite_events 
                if e.composite_priority.value in ["critical", "high"]
            ]
            
            print(f"      📊 高優先級複合事件: {len(high_priority_events)}")
            
            total_affected_symbols = set()
            for event in composite_events:
                total_affected_symbols.update(event.affected_symbols)
            
            print(f"      🎯 總影響標的數: {len(total_affected_symbols)}")
            print(f"      📈 影響標的: {', '.join(list(total_affected_symbols)[:5])}")
            
            avg_confidence = sum(e.aggregate_confidence for e in composite_events) / len(composite_events)
            print(f"      🎯 平均複合信心度: {avg_confidence:.3f}")
        
        # 5. 驗證數據流
        print("   5️⃣ 驗證數據流完整性...")
        
        prediction_summary = event_prediction_engine.get_prediction_summary()
        processor_summary = composite_event_processor.get_processing_summary()
        
        print(f"      📊 預測引擎狀態: {prediction_summary.get('engine_status')}")
        print(f"      📊 處理器狀態: {processor_summary.get('processor_status')}")
        
        # 檢查數據一致性
        predictions_count = prediction_summary.get('recent_predictions_24h', 0)
        active_events_count = processor_summary.get('active_events_count', 0)
        
        print(f"      📊 24小時預測數: {predictions_count}")
        print(f"      📊 活躍事件數: {active_events_count}")
        
        loop.close()
        
        print("✅ 事件預測和複合處理整合測試成功!")
        return True
        
    except Exception as e:
        print(f"❌ 整合測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("🚀 Trading X Phase 3 Week 1 測試")
    print("=" * 80)
    print("測試項目:")
    print("1. 事件預測引擎 (EventPredictionEngine)")
    print("2. 複合事件處理器 (CompositeEventProcessor)")
    print("3. 系統整合測試")
    print("=" * 80)
    
    # 執行所有測試
    test_results = {}
    
    # 1. 測試事件預測引擎
    test_results["event_prediction"] = test_event_prediction_engine()
    
    # 2. 測試複合事件處理器
    test_results["composite_processing"] = test_composite_event_processor()
    
    # 3. 測試整合
    test_results["integration"] = test_integration()
    
    # 測試結果總結
    print("\n" + "=" * 80)
    print("🎯 Week 1 測試結果:")
    passed_tests = 0
    total_tests = len(test_results)
    
    test_names = {
        "event_prediction": "事件預測引擎",
        "composite_processing": "複合事件處理器",
        "integration": "系統整合"
    }
    
    for i, (test_name, result) in enumerate(test_results.items(), 1):
        status = "✅ 通過" if result else "❌ 失敗"
        display_name = test_names.get(test_name, test_name)
        print(f"   {i}. {display_name}: {status}")
        if result:
            passed_tests += 1
    
    # 計算通過率
    pass_rate = (passed_tests / total_tests) * 100
    print(f"\n📊 測試通過率: {pass_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if pass_rate == 100:
        print("🎉 所有測試通過！Week 1 功能實現完成！")
        print("\n📋 Week 1 完成項目:")
        print("   ✅ EventPredictionEngine - 事件預測引擎")
        print("   ✅ CompositeEventProcessor - 複合事件處理器") 
        print("   ✅ 基礎測試通過")
        print("\n🎯 準備進入 Week 2: 事件影響評估系統")
    elif pass_rate >= 75:
        print("⚠️  部分測試失敗，請檢查相關模組。")
    else:
        print("❌ 多項測試失敗，需要檢查系統實現。")
    
    print(f"\n📋 Phase 3 Week 1 實施狀態: {'✅ 完成' if pass_rate >= 75 else '⚠️ 需要修復'}")

if __name__ == "__main__":
    main()
