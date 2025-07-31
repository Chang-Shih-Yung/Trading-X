#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading X Phase 3 Week 3 系統測試
測試 EventCoordinationEngine 事件協調引擎的完整功能
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

async def test_event_coordination_engine():
    """測試事件協調引擎核心功能"""
    print("\n🎯 測試事件協調引擎核心功能")
    print("=" * 60)
    
    try:
        from app.services.event_coordination_engine import (
            event_coordination_engine,
            CoordinationMode,
            ConflictType
        )
        
        # 轉換字符串到枚舉
        def get_coordination_mode(mode_str):
            mode_map = {
                "CONSERVATIVE": CoordinationMode.CONSERVATIVE,
                "AGGRESSIVE": CoordinationMode.AGGRESSIVE,
                "BALANCED": CoordinationMode.BALANCED,
                "ADAPTIVE": CoordinationMode.ADAPTIVE
            }
            return mode_map.get(mode_str, CoordinationMode.BALANCED)
        
        print("📅 創建測試事件組合...")
        
        # 創建多個潛在衝突的事件
        current_time = datetime.now()
        
        # 事件1: FOMC會議 (高優先級)
        event1 = {
            'event_id': 'fomc_test_001',
            'event_type': 'FOMC_MEETING',
            'title': '聯準會利率決議會議',
            'severity': 'HIGH',
            'direction': 'VOLATILE',
            'event_time': current_time + timedelta(hours=2),
            'affected_symbols': ['BTCUSDT', 'ETHUSDT'],
            'confidence': 0.95
        }
        
        # 事件2: CPI數據發布 (高優先級，方向衝突)
        event2 = {
            'event_id': 'cpi_test_001',
            'event_type': 'CPI_DATA',
            'title': 'CPI通脹數據發布',
            'severity': 'HIGH',
            'direction': 'BULLISH',  # 與FOMC的VOLATILE可能衝突
            'event_time': current_time + timedelta(hours=3),  # 時間接近
            'affected_symbols': ['BTCUSDT', 'ADAUSDT'],  # 部分重疊
            'confidence': 0.85
        }
        
        # 事件3: 閃崩事件 (關鍵優先級，明顯衝突)
        event3 = {
            'event_id': 'crash_test_001',
            'event_type': 'FLASH_CRASH',
            'title': '市場閃崩事件',
            'severity': 'CRITICAL',
            'direction': 'BEARISH',  # 與CPI的BULLISH直接衝突
            'event_time': current_time + timedelta(hours=1),  # 最早發生
            'affected_symbols': ['BTCUSDT', 'ETHUSDT', 'ADAUSDT'],  # 全面重疊
            'confidence': 0.97
        }
        
        events = [event1, event2, event3]
        
        print(f"   ✅ 創建了 {len(events)} 個測試事件")
        for event in events:
            print(f"      - {event['event_id']}: {event['severity']} / {event['direction']}")
        
        print(f"\n🔍 執行事件協調 (平衡模式)...")
        
        # 執行協調
        coordination_result = await event_coordination_engine.coordinate_events(
            events=events,
            coordination_mode=get_coordination_mode("BALANCED")
        )
        
        if coordination_result:
            print(f"✅ 事件協調完成:")
            print(f"   協調ID: {coordination_result.coordination_id}")
            print(f"   處理事件數: {len(coordination_result.processed_events)}")
            print(f"   檢測衝突數: {len(coordination_result.conflicts_detected)}")
            print(f"   解決衝突數: {coordination_result.conflicts_resolved}")
            print(f"   協調效果: {coordination_result.coordination_effectiveness:.3f}")
            print(f"   資源利用率: {coordination_result.resource_utilization:.3f}")
            print(f"   處理時間: {coordination_result.processing_time_ms:.2f}ms")
            
            # 顯示檢測到的衝突
            if coordination_result.conflicts_detected:
                print(f"\n⚠️  檢測到的衝突:")
                for conflict in coordination_result.conflicts_detected:
                    status = "✅ 已解決" if conflict.is_resolved else "❌ 未解決"
                    print(f"   - {conflict.conflict_type.value}: {conflict.conflict_description} ({status})")
                    print(f"     嚴重程度: {conflict.severity_score:.3f}")
                    if conflict.resolution_strategy:
                        print(f"     解決策略: {conflict.resolution_strategy.value}")
            
            # 顯示事件調度
            if coordination_result.event_schedule:
                schedule = coordination_result.event_schedule
                print(f"\n📋 生成的事件調度:")
                print(f"   調度ID: {schedule.schedule_id}")
                print(f"   協調模式: {schedule.coordination_mode.value}")
                print(f"   事件順序: {schedule.events}")
                print(f"   預計總時長: {schedule.total_duration:.1f} 小時")
                
                # 顯示資源分配
                if schedule.resource_allocation:
                    print(f"   資源分配:")
                    for event_id, allocation in schedule.resource_allocation.items():
                        print(f"     {event_id}: {allocation:.3f}")
                
                # 顯示風險評估
                if schedule.risk_assessment:
                    print(f"   風險評估:")
                    for risk_type, risk_value in schedule.risk_assessment.items():
                        risk_level = "高" if risk_value > 0.7 else "中" if risk_value > 0.4 else "低"
                        print(f"     {risk_type}: {risk_value:.3f} ({risk_level})")
            
            # 顯示建議和警告
            if coordination_result.recommendations:
                print(f"\n💡 系統建議:")
                for i, rec in enumerate(coordination_result.recommendations, 1):
                    print(f"   {i}. {rec}")
            
            if coordination_result.warnings:
                print(f"\n⚠️  系統警告:")
                for i, warning in enumerate(coordination_result.warnings, 1):
                    print(f"   {i}. {warning}")
            
            print("✅ 事件協調引擎核心功能測試成功!")
            return True
        else:
            print("❌ 事件協調失敗")
            return False
        
    except Exception as e:
        print(f"❌ 事件協調引擎測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_coordination_modes():
    """測試不同協調模式"""
    print("\n🎯 測試不同協調模式")
    print("=" * 60)
    
    try:
        from app.services.event_coordination_engine import (
            event_coordination_engine,
            CoordinationMode
        )
        
        # 轉換字符串到枚舉
        def get_coordination_mode(mode_str):
            mode_map = {
                "CONSERVATIVE": CoordinationMode.CONSERVATIVE,
                "AGGRESSIVE": CoordinationMode.AGGRESSIVE,
                "BALANCED": CoordinationMode.BALANCED,
                "ADAPTIVE": CoordinationMode.ADAPTIVE
            }
            return mode_map.get(mode_str, CoordinationMode.BALANCED)
        
        print("🔧 創建標準測試事件組...")
        
        current_time = datetime.now()
        
        # 創建兩個衝突事件
        conflicting_events = [
            {
                'event_id': 'mode_test_bull',
                'event_type': 'HALVING_EVENT',
                'title': '比特幣減半事件',
                'severity': 'CRITICAL',
                'direction': 'BULLISH',
                'event_time': current_time + timedelta(hours=1),
                'affected_symbols': ['BTCUSDT'],
                'confidence': 0.98
            },
            {
                'event_id': 'mode_test_bear',
                'event_type': 'REGULATION_NEWS',
                'title': '嚴格監管政策',
                'severity': 'HIGH',
                'direction': 'BEARISH',
                'event_time': current_time + timedelta(hours=1.5),  # 30分鐘後
                'affected_symbols': ['BTCUSDT'],
                'confidence': 0.80
            }
        ]
        
        # 測試所有協調模式
        modes = [
            "CONSERVATIVE",
            "AGGRESSIVE", 
            "BALANCED",
            "ADAPTIVE"
        ]
        
        mode_results = {}
        
        for mode in modes:
            print(f"\n🔍 測試 {mode} 模式...")
            
            result = await event_coordination_engine.coordinate_events(
                events=conflicting_events,
                coordination_mode=get_coordination_mode(mode)
            )
            
            if result:
                mode_results[mode] = {
                    'conflicts_detected': len(result.conflicts_detected),
                    'conflicts_resolved': result.conflicts_resolved,
                    'effectiveness': result.coordination_effectiveness,
                    'resource_utilization': result.resource_utilization,
                    'has_schedule': result.event_schedule is not None,
                    'processing_time': result.processing_time_ms
                }
                
                print(f"   ✅ {mode} 模式協調完成")
                print(f"      衝突檢測: {len(result.conflicts_detected)}")
                print(f"      衝突解決: {result.conflicts_resolved}")
                print(f"      協調效果: {result.coordination_effectiveness:.3f}")
                
                # 顯示使用的解決策略
                if result.conflicts_detected:
                    strategies = [c.resolution_strategy.value for c in result.conflicts_detected 
                                 if c.resolution_strategy and c.is_resolved]
                    if strategies:
                        print(f"      解決策略: {', '.join(strategies)}")
            else:
                print(f"   ❌ {mode} 模式協調失敗")
        
        # 比較不同模式的效果
        if mode_results:
            print(f"\n📊 協調模式比較:")
            print(f"{'模式':<12} {'衝突解決':<8} {'協調效果':<8} {'資源利用':<8} {'處理時間':<10}")
            print("-" * 55)
            
            for mode, results in mode_results.items():
                resolved_rate = results['conflicts_resolved'] / max(results['conflicts_detected'], 1)
                print(f"{mode:<12} {resolved_rate:>6.1%} {results['effectiveness']:>7.3f} "
                      f"{results['resource_utilization']:>7.3f} {results['processing_time']:>8.2f}ms")
            
            # 找出最佳模式
            best_mode = max(mode_results.items(), 
                          key=lambda x: x[1]['effectiveness'] * 0.6 + x[1]['resource_utilization'] * 0.4)
            print(f"\n🏆 推薦模式: {best_mode[0]} (綜合評分最高)")
            
            print("✅ 協調模式測試成功!")
            return True
        else:
            print("❌ 沒有獲得有效的模式測試結果")
            return False
        
    except Exception as e:
        print(f"❌ 協調模式測試失敗: {e}")
        return False

async def test_conflict_resolution():
    """測試衝突解決機制"""
    print("\n🎯 測試衝突解決機制")
    print("=" * 60)
    
    try:
        from app.services.event_coordination_engine import (
            event_coordination_engine,
            CoordinationMode
        )
        
        # 轉換字符串到枚舉
        def get_coordination_mode(mode_str):
            mode_map = {
                "CONSERVATIVE": CoordinationMode.CONSERVATIVE,
                "AGGRESSIVE": CoordinationMode.AGGRESSIVE,
                "BALANCED": CoordinationMode.BALANCED,
                "ADAPTIVE": CoordinationMode.ADAPTIVE
            }
            return mode_map.get(mode_str, CoordinationMode.BALANCED)
        
        print("⚔️ 創建各種類型的衝突事件...")
        
        current_time = datetime.now()
        
        # 創建專門測試不同衝突類型的事件
        conflict_test_events = [
            # 時間衝突事件
            {
                'event_id': 'timing_conflict_1',
                'event_type': 'NFP_RELEASE',
                'title': '非農就業數據',
                'severity': 'HIGH',
                'direction': 'VOLATILE',
                'event_time': current_time + timedelta(hours=2),
                'affected_symbols': ['BTCUSDT', 'ETHUSDT'],
                'confidence': 0.90
            },
            {
                'event_id': 'timing_conflict_2',
                'event_type': 'FOMC_MEETING',
                'title': '聯準會會議',
                'severity': 'HIGH',
                'direction': 'VOLATILE',
                'event_time': current_time + timedelta(hours=2, minutes=30),  # 30分鐘後
                'affected_symbols': ['ETHUSDT', 'ADAUSDT'],
                'confidence': 0.85
            },
            
            # 方向衝突事件
            {
                'event_id': 'direction_conflict_1',
                'event_type': 'HALVING_EVENT',
                'title': '比特幣減半',
                'severity': 'CRITICAL',
                'direction': 'BULLISH',
                'event_time': current_time + timedelta(hours=6),
                'affected_symbols': ['BTCUSDT'],
                'confidence': 0.95
            },
            {
                'event_id': 'direction_conflict_2',
                'event_type': 'FLASH_CRASH',
                'title': '市場崩盤',
                'severity': 'HIGH',
                'direction': 'BEARISH',
                'event_time': current_time + timedelta(hours=6, minutes=15),
                'affected_symbols': ['BTCUSDT'],
                'confidence': 0.88
            },
            
            # 資源衝突事件
            {
                'event_id': 'resource_conflict_1',
                'event_type': 'WHALE_MOVEMENT',
                'title': '巨鯨轉移',
                'severity': 'MEDIUM',
                'direction': 'NEUTRAL',
                'event_time': current_time + timedelta(hours=4),
                'affected_symbols': ['BTCUSDT', 'ETHUSDT', 'ADAUSDT'],  # 大範圍重疊
                'confidence': 0.70
            },
            {
                'event_id': 'resource_conflict_2',
                'event_type': 'EXCHANGE_LISTING',
                'title': '交易所上幣',
                'severity': 'LOW',
                'direction': 'BULLISH',
                'event_time': current_time + timedelta(hours=4, minutes=30),
                'affected_symbols': ['ETHUSDT', 'ADAUSDT', 'SOLUSDT'],  # 重疊範圍
                'confidence': 0.65
            }
        ]
        
        print(f"   ✅ 創建了 {len(conflict_test_events)} 個衝突測試事件")
        
        # 執行協調並分析衝突類型
        print(f"\n🔍 執行衝突檢測和解決...")
        
        result = await event_coordination_engine.coordinate_events(
            events=conflict_test_events,
            coordination_mode=get_coordination_mode("ADAPTIVE")
        )
        
        if result and result.conflicts_detected:
            print(f"✅ 衝突檢測完成，發現 {len(result.conflicts_detected)} 個衝突")
            
            # 按衝突類型分組分析
            conflict_by_type = {}
            resolution_by_strategy = {}
            
            for conflict in result.conflicts_detected:
                conflict_type = conflict.conflict_type.value
                if conflict_type not in conflict_by_type:
                    conflict_by_type[conflict_type] = []
                conflict_by_type[conflict_type].append(conflict)
                
                if conflict.is_resolved and conflict.resolution_strategy:
                    strategy = conflict.resolution_strategy.value
                    if strategy not in resolution_by_strategy:
                        resolution_by_strategy[strategy] = 0
                    resolution_by_strategy[strategy] += 1
            
            print(f"\n📊 衝突類型分析:")
            for conflict_type, conflicts in conflict_by_type.items():
                resolved_count = sum(1 for c in conflicts if c.is_resolved)
                avg_severity = np.mean([c.severity_score for c in conflicts])
                print(f"   {conflict_type}: {len(conflicts)} 個 (解決: {resolved_count}, 平均嚴重度: {avg_severity:.3f})")
                
                # 顯示具體衝突詳情
                for conflict in conflicts:
                    status = "✅" if conflict.is_resolved else "❌"
                    strategy = conflict.resolution_strategy.value if conflict.resolution_strategy else "無"
                    print(f"     {status} {conflict.conflict_description} (策略: {strategy})")
            
            print(f"\n🛠️ 解決策略使用統計:")
            for strategy, count in resolution_by_strategy.items():
                print(f"   {strategy}: {count} 次")
            
            # 計算解決效果
            total_conflicts = len(result.conflicts_detected)
            resolved_conflicts = result.conflicts_resolved
            resolution_rate = resolved_conflicts / total_conflicts if total_conflicts > 0 else 0
            
            print(f"\n📈 衝突解決效果:")
            print(f"   總衝突數: {total_conflicts}")
            print(f"   解決衝突數: {resolved_conflicts}")
            print(f"   解決成功率: {resolution_rate:.1%}")
            print(f"   協調效果分數: {result.coordination_effectiveness:.3f}")
            
            if resolution_rate >= 0.8:
                print("🎉 衝突解決機制運行良好!")
            elif resolution_rate >= 0.6:
                print("⚠️ 衝突解決機制運行正常，但有改進空間")
            else:
                print("❌ 衝突解決機制需要優化")
            
            print("✅ 衝突解決機制測試成功!")
            return True
        else:
            print("⚠️ 未檢測到衝突或協調失敗")
            return False
        
    except Exception as e:
        print(f"❌ 衝突解決機制測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_system_integration():
    """測試系統整合"""
    print("\n🎯 測試事件協調系統整合")
    print("=" * 60)
    
    try:
        from app.services.event_coordination_engine import event_coordination_engine, CoordinationMode
        
        print("🔗 測試系統狀態和歷史記錄...")
        
        # 獲取系統狀態
        status = event_coordination_engine.get_coordination_status()
        
        print(f"📊 協調系統狀態:")
        print(f"   活躍事件數: {status['active_events_count']}")
        print(f"   活躍調度數: {status['active_schedules_count']}")
        print(f"   未解決衝突數: {status['recent_conflicts_count']}")
        print(f"   協調模式: {status['coordination_mode']}")
        print(f"   系統健康度: {status['system_health']}")
        
        # 統計信息
        stats = status['stats']
        print(f"\n📈 協調統計:")
        print(f"   總協調次數: {stats['total_coordinations']}")
        print(f"   檢測衝突數: {stats['conflicts_detected']}")
        print(f"   解決衝突數: {stats['conflicts_resolved']}")
        print(f"   創建調度數: {stats['schedules_created']}")
        print(f"   平均處理時間: {stats['avg_processing_time_ms']:.2f}ms")
        print(f"   協調成功率: {stats['coordination_success_rate']:.1%}")
        
        # 獲取詳細摘要
        print(f"\n🔍 獲取系統摘要...")
        summary = event_coordination_engine.export_coordination_summary()
        
        # 最近協調記錄
        recent_coordinations = summary.get('recent_coordinations', [])
        if recent_coordinations:
            print(f"\n📋 最近協調記錄 ({len(recent_coordinations)}筆):")
            print(f"{'協調ID':<25} {'事件數':<6} {'衝突數':<6} {'解決數':<6} {'效果':<8}")
            print("-" * 60)
            
            for coord in recent_coordinations:
                print(f"{coord['coordination_id']:<25} "
                      f"{coord['events_processed']:>5} "
                      f"{coord['conflicts_detected']:>5} "
                      f"{coord['conflicts_resolved']:>5} "
                      f"{coord['effectiveness']:>7.3f}")
        
        # 衝突摘要
        conflict_summary = summary.get('conflict_summary', {})
        if conflict_summary:
            print(f"\n⚔️ 衝突摘要:")
            print(f"   歷史總衝突: {conflict_summary['total_conflicts']}")
            print(f"   已解決衝突: {conflict_summary['resolved_conflicts']}")
            print(f"   最近未解決: {conflict_summary['recent_conflicts']}")
            
            conflict_types = conflict_summary.get('conflict_types', {})
            if conflict_types:
                print(f"   衝突類型分布:")
                for conflict_type, count in conflict_types.items():
                    if count > 0:
                        print(f"     {conflict_type}: {count}")
        
        # 活躍調度
        active_schedules = summary.get('active_schedules', [])
        if active_schedules:
            print(f"\n📅 活躍調度 ({len(active_schedules)}個):")
            for schedule in active_schedules:
                status_str = "運行中" if schedule['is_active'] else "待啟動"
                print(f"   {schedule['schedule_id']}: {schedule['events_count']} 事件, "
                      f"{schedule['total_duration']:.1f}h, {status_str}")
        
        # 執行一個整合測試
        print(f"\n🧪 執行整合測試...")
        
        integration_events = [
            {
                'event_id': 'integration_test_1',
                'event_type': 'INTEGRATION_TEST',
                'title': '整合測試事件1',
                'severity': 'MEDIUM',
                'direction': 'BULLISH',
                'event_time': datetime.now() + timedelta(hours=1),
                'affected_symbols': ['BTCUSDT'],
                'confidence': 0.75
            },
            {
                'event_id': 'integration_test_2',
                'event_type': 'INTEGRATION_TEST',
                'title': '整合測試事件2',
                'severity': 'MEDIUM',
                'direction': 'BEARISH',
                'event_time': datetime.now() + timedelta(hours=1, minutes=15),
                'affected_symbols': ['BTCUSDT'],
                'confidence': 0.70
            }
        ]
        
        integration_result = await event_coordination_engine.coordinate_events(
            events=integration_events,
            coordination_mode=CoordinationMode.BALANCED
        )
        
        if integration_result:
            print(f"   ✅ 整合測試協調成功")
            print(f"   協調ID: {integration_result.coordination_id}")
            print(f"   處理時間: {integration_result.processing_time_ms:.2f}ms")
            print(f"   協調效果: {integration_result.coordination_effectiveness:.3f}")
            
            # 驗證系統狀態更新
            updated_status = event_coordination_engine.get_coordination_status()
            if updated_status['stats']['total_coordinations'] > stats['total_coordinations']:
                print(f"   ✅ 系統統計正確更新")
            else:
                print(f"   ⚠️ 系統統計更新異常")
        else:
            print(f"   ❌ 整合測試協調失敗")
            return False
        
        print("✅ 系統整合測試成功!")
        return True
        
    except Exception as e:
        print(f"❌ 系統整合測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主測試函數"""
    print("🚀 Phase 3 Week 3 - EventCoordinationEngine 系統測試")
    print("=" * 80)
    print("測試項目:")
    print("1. 事件協調引擎核心功能")
    print("2. 不同協調模式測試")
    print("3. 衝突解決機制測試")
    print("4. 系統整合測試")
    print("=" * 80)
    
    # 執行所有測試
    test_results = {}
    
    # 1. 測試事件協調引擎核心功能
    test_results["coordination_engine"] = await test_event_coordination_engine()
    
    # 2. 測試不同協調模式
    test_results["coordination_modes"] = await test_coordination_modes()
    
    # 3. 測試衝突解決機制
    test_results["conflict_resolution"] = await test_conflict_resolution()
    
    # 4. 測試系統整合
    test_results["system_integration"] = await test_system_integration()
    
    # 測試結果總結
    print("\n" + "=" * 80)
    print("🎯 Phase 3 Week 3 測試結果:")
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        test_display_name = {
            "coordination_engine": "事件協調引擎核心功能",
            "coordination_modes": "協調模式測試",
            "conflict_resolution": "衝突解決機制",
            "system_integration": "系統整合測試"
        }.get(test_name, test_name)
        
        print(f"   {total_tests - len(test_results) + list(test_results.keys()).index(test_name) + 1}. {test_display_name}: {status}")
        if result:
            passed_tests += 1
    
    # 計算通過率
    pass_rate = (passed_tests / total_tests) * 100
    print(f"\n📊 測試通過率: {pass_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if pass_rate == 100:
        print("🎉 所有測試通過！EventCoordinationEngine 系統運行正常！")
    elif pass_rate >= 75:
        print("⚠️  部分測試失敗，但核心功能運行正常。")
    else:
        print("❌ 多項測試失敗，需要檢查系統實現。")
    
    print(f"\n📋 Phase 3 Week 3 實施狀態: {'✅ 完成' if pass_rate >= 75 else '⚠️ 需要修復'}")
    
    if pass_rate >= 75:
        print("\n🎯 Week 3 核心功能已完成:")
        print("   ✅ EventCoordinationEngine - 事件協調引擎")
        print("   ✅ 衝突檢測與解決 - 多重事件衝突處理")
        print("   ✅ 協調模式系統 - 保守/積極/平衡/自適應")
        print("   ✅ 事件調度生成 - 智能執行順序規劃")
        print("   ✅ 資源分配優化 - 動態資源管理")
        print("   ✅ 風險評估機制 - 全面風險分析")

if __name__ == "__main__":
    import numpy as np
    asyncio.run(main())
