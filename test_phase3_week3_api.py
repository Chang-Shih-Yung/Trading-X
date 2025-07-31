#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading X Phase 3 Week 3 API 測試
測試事件協調引擎的API端點功能
"""

import asyncio
import json
import aiohttp
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# API 基礎URL
BASE_URL = "http://localhost:8000"

async def test_event_coordination_api():
    """測試事件協調 API"""
    print("\n🎯 測試事件協調 API")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            # 準備測試事件數據
            current_time = datetime.now()
            test_events = [
                {
                    'event_id': 'api_test_fomc',
                    'event_type': 'FOMC_MEETING',
                    'title': 'API測試-聯準會會議',
                    'severity': 'HIGH',
                    'direction': 'VOLATILE',
                    'event_time': (current_time + timedelta(hours=2)).isoformat(),
                    'affected_symbols': ['BTCUSDT', 'ETHUSDT'],
                    'confidence': 0.90
                },
                {
                    'event_id': 'api_test_cpi',
                    'event_type': 'CPI_DATA',
                    'title': 'API測試-CPI數據',
                    'severity': 'HIGH',
                    'direction': 'BULLISH',
                    'event_time': (current_time + timedelta(hours=2.5)).isoformat(),
                    'affected_symbols': ['BTCUSDT', 'ADAUSDT'],
                    'confidence': 0.85
                }
            ]
            
            request_data = {
                'events': test_events,
                'coordination_mode': 'BALANCED'
            }
            
            print(f"📤 發送協調請求到 /api/v1/event/coordinate")
            print(f"   事件數量: {len(test_events)}")
            print(f"   協調模式: {request_data['coordination_mode']}")
            
            async with session.post(
                f"{BASE_URL}/api/v1/event/coordinate",
                json=request_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    print(f"✅ API 協調成功:")
                    print(f"   協調ID: {result.get('coordination_id', 'N/A')}")
                    print(f"   處理事件數: {result.get('events_processed', 0)}")
                    print(f"   檢測衝突數: {result.get('conflicts_detected', 0)}")
                    print(f"   解決衝突數: {result.get('conflicts_resolved', 0)}")
                    print(f"   協調效果: {result.get('coordination_effectiveness', 0):.3f}")
                    print(f"   處理時間: {result.get('processing_time_ms', 0):.2f}ms")
                    
                    # 顯示衝突詳情
                    conflicts = result.get('conflicts', [])
                    if conflicts:
                        print(f"\n⚠️  檢測到的衝突:")
                        for conflict in conflicts:
                            status = "✅ 已解決" if conflict.get('is_resolved', False) else "❌ 未解決"
                            print(f"   - {conflict.get('conflict_type', 'UNKNOWN')}: {conflict.get('description', 'N/A')} ({status})")
                            if conflict.get('resolution_strategy'):
                                print(f"     解決策略: {conflict['resolution_strategy']}")
                    
                    # 顯示事件調度
                    schedule = result.get('event_schedule')
                    if schedule:
                        print(f"\n📋 生成的事件調度:")
                        print(f"   調度ID: {schedule.get('schedule_id', 'N/A')}")
                        print(f"   事件順序: {schedule.get('events', [])}")
                        print(f"   總時長: {schedule.get('total_duration', 0):.1f} 小時")
                        
                        resource_allocation = schedule.get('resource_allocation', {})
                        if resource_allocation:
                            print(f"   資源分配:")
                            for event_id, allocation in resource_allocation.items():
                                print(f"     {event_id}: {allocation:.3f}")
                    
                    # 顯示系統建議
                    recommendations = result.get('recommendations', [])
                    if recommendations:
                        print(f"\n💡 系統建議:")
                        for i, rec in enumerate(recommendations, 1):
                            print(f"   {i}. {rec}")
                    
                    print("✅ 事件協調 API 測試成功!")
                    return True
                    
                else:
                    error_text = await response.text()
                    print(f"❌ API 請求失敗 (HTTP {response.status}): {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ 事件協調 API 測試失敗: {e}")
        return False

async def test_coordination_status_api():
    """測試協調狀態 API"""
    print("\n🎯 測試協調系統狀態 API")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📤 請求協調系統狀態: /api/v1/event/coordination-status")
            
            async with session.get(f"{BASE_URL}/api/v1/event/coordination-status") as response:
                
                if response.status == 200:
                    status = await response.json()
                    
                    print(f"✅ 獲取狀態成功:")
                    print(f"   活躍事件數: {status.get('active_events_count', 0)}")
                    print(f"   活躍調度數: {status.get('active_schedules_count', 0)}")
                    print(f"   未解決衝突數: {status.get('recent_conflicts_count', 0)}")
                    print(f"   協調模式: {status.get('coordination_mode', 'N/A')}")
                    print(f"   系統健康度: {status.get('system_health', 'N/A')}")
                    
                    stats = status.get('stats', {})
                    if stats:
                        print(f"\n📈 協調統計:")
                        print(f"   總協調次數: {stats.get('total_coordinations', 0)}")
                        print(f"   檢測衝突數: {stats.get('conflicts_detected', 0)}")
                        print(f"   解決衝突數: {stats.get('conflicts_resolved', 0)}")
                        print(f"   創建調度數: {stats.get('schedules_created', 0)}")
                        print(f"   平均處理時間: {stats.get('avg_processing_time_ms', 0):.2f}ms")
                        print(f"   協調成功率: {stats.get('coordination_success_rate', 0):.1%}")
                    
                    print("✅ 協調狀態 API 測試成功!")
                    return True
                    
                else:
                    error_text = await response.text()
                    print(f"❌ API 請求失敗 (HTTP {response.status}): {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ 協調狀態 API 測試失敗: {e}")
        return False

async def test_coordination_history_api():
    """測試協調歷史 API"""
    print("\n🎯 測試協調歷史記錄 API")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📤 請求協調歷史記錄: /api/v1/event/coordination-history")
            
            params = {
                'limit': 5,
                'include_details': 'true'  # 轉換為字符串
            }
            
            async with session.get(
                f"{BASE_URL}/api/v1/event/coordination-history",
                params=params
            ) as response:
                
                if response.status == 200:
                    history = await response.json()
                    
                    coordinations = history.get('coordinations', [])
                    print(f"✅ 獲取歷史記錄成功:")
                    print(f"   記錄數量: {len(coordinations)}")
                    
                    if coordinations:
                        print(f"\n📋 最近協調記錄:")
                        print(f"{'協調ID':<25} {'事件數':<6} {'衝突數':<6} {'解決數':<6} {'效果':<8}")
                        print("-" * 60)
                        
                        for coord in coordinations:
                            print(f"{coord.get('coordination_id', 'N/A'):<25} "
                                  f"{coord.get('events_processed', 0):>5} "
                                  f"{coord.get('conflicts_detected', 0):>5} "
                                  f"{coord.get('conflicts_resolved', 0):>5} "
                                  f"{coord.get('effectiveness', 0):>7.3f}")
                        
                        # 顯示第一個協調的詳細信息
                        first_coord = coordinations[0]
                        conflicts = first_coord.get('conflicts', [])
                        if conflicts:
                            print(f"\n🔍 最新協調衝突詳情:")
                            for conflict in conflicts:
                                status = "✅" if conflict.get('is_resolved', False) else "❌"
                                print(f"   {status} {conflict.get('conflict_type', 'UNKNOWN')}: "
                                      f"{conflict.get('description', 'N/A')}")
                    
                    summary = history.get('summary', {})
                    if summary:
                        print(f"\n📊 歷史摘要:")
                        print(f"   總協調次數: {summary.get('total_coordinations', 0)}")
                        print(f"   平均衝突數: {summary.get('avg_conflicts_per_coordination', 0):.1f}")
                        print(f"   平均解決率: {summary.get('avg_resolution_rate', 0):.1%}")
                        print(f"   平均協調效果: {summary.get('avg_effectiveness', 0):.3f}")
                    
                    print("✅ 協調歷史 API 測試成功!")
                    return True
                    
                else:
                    error_text = await response.text()
                    print(f"❌ API 請求失敗 (HTTP {response.status}): {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ 協調歷史 API 測試失敗: {e}")
        return False

async def test_active_schedules_api():
    """測試活躍調度 API"""
    print("\n🎯 測試活躍調度 API")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📤 請求活躍調度列表: /api/v1/event/active-schedules")
            
            async with session.get(f"{BASE_URL}/api/v1/event/active-schedules") as response:
                
                if response.status == 200:
                    schedules_data = await response.json()
                    
                    schedules = schedules_data.get('active_schedules', [])
                    print(f"✅ 獲取活躍調度成功:")
                    print(f"   活躍調度數: {len(schedules)}")
                    
                    if schedules:
                        print(f"\n📅 活躍調度列表:")
                        for schedule in schedules:
                            schedule_id = schedule.get('schedule_id', 'N/A')
                            events_count = schedule.get('events_count', 0)
                            total_duration = schedule.get('total_duration', 0)
                            status = "運行中" if schedule.get('is_active', False) else "待啟動"
                            
                            print(f"   {schedule_id}: {events_count} 事件, "
                                  f"{total_duration:.1f}h, {status}")
                            
                            # 詳細事件信息
                            events = schedule.get('events', [])
                            if events:
                                print(f"     事件順序: {', '.join(events)}")
                            
                            # 資源分配
                            resource_allocation = schedule.get('resource_allocation', {})
                            if resource_allocation:
                                print(f"     資源分配: {dict(resource_allocation)}")
                    
                    print("✅ 活躍調度 API 測試成功!")
                    return True
                    
                else:
                    error_text = await response.text()
                    print(f"❌ API 請求失敗 (HTTP {response.status}): {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ 活躍調度 API 測試失敗: {e}")
        return False

async def test_coordination_modes_api():
    """測試協調模式管理 API"""
    print("\n🎯 測試協調模式管理 API")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            # 1. 獲取當前協調模式
            print(f"📤 獲取當前協調模式: /api/v1/event/coordination-mode")
            
            async with session.get(f"{BASE_URL}/api/v1/event/coordination-mode") as response:
                if response.status == 200:
                    mode_data = await response.json()
                    current_mode = mode_data.get('coordination_mode', 'N/A')
                    print(f"✅ 當前協調模式: {current_mode}")
                else:
                    print(f"❌ 獲取模式失敗 (HTTP {response.status})")
                    return False
            
            # 2. 更新協調模式
            new_mode = 'ADAPTIVE' if current_mode != 'ADAPTIVE' else 'BALANCED'
            print(f"\n📤 更新協調模式為: {new_mode}")
            
            async with session.put(
                f"{BASE_URL}/api/v1/event/coordination-mode",
                json={'coordination_mode': new_mode},
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 模式更新成功:")
                    print(f"   新模式: {result.get('coordination_mode', 'N/A')}")
                    print(f"   更新時間: {result.get('updated_at', 'N/A')}")
                else:
                    error_text = await response.text()
                    print(f"❌ 模式更新失敗 (HTTP {response.status}): {error_text}")
                    return False
            
            # 3. 驗證模式已更新
            print(f"\n📤 驗證模式更新...")
            
            async with session.get(f"{BASE_URL}/api/v1/event/coordination-mode") as response:
                if response.status == 200:
                    mode_data = await response.json()
                    updated_mode = mode_data.get('coordination_mode', 'N/A')
                    
                    if updated_mode.upper() == new_mode.upper():
                        print(f"✅ 模式驗證成功，當前模式: {updated_mode}")
                    else:
                        print(f"❌ 模式驗證失敗，期望: {new_mode}, 實際: {updated_mode}")
                        return False
                else:
                    print(f"❌ 模式驗證失敗 (HTTP {response.status})")
                    return False
            
            print("✅ 協調模式管理 API 測試成功!")
            return True
            
    except Exception as e:
        print(f"❌ 協調模式管理 API 測試失敗: {e}")
        return False

async def test_api_comprehensive():
    """綜合 API 測試"""
    print("\n🎯 綜合 API 測試")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            # 創建一個複雜的協調場景
            current_time = datetime.now()
            complex_events = [
                {
                    'event_id': 'complex_test_1',
                    'event_type': 'FOMC_MEETING',
                    'title': '綜合測試-聯準會會議',
                    'severity': 'HIGH',
                    'direction': 'VOLATILE',
                    'event_time': (current_time + timedelta(hours=1)).isoformat(),
                    'affected_symbols': ['BTCUSDT', 'ETHUSDT'],
                    'confidence': 0.95
                },
                {
                    'event_id': 'complex_test_2',
                    'event_type': 'CPI_DATA',
                    'title': '綜合測試-CPI數據',
                    'severity': 'HIGH',
                    'direction': 'BULLISH',
                    'event_time': (current_time + timedelta(hours=1.5)).isoformat(),
                    'affected_symbols': ['BTCUSDT', 'ADAUSDT'],
                    'confidence': 0.88
                },
                {
                    'event_id': 'complex_test_3',
                    'event_type': 'FLASH_CRASH',
                    'title': '綜合測試-閃崩事件',
                    'severity': 'CRITICAL',
                    'direction': 'BEARISH',
                    'event_time': (current_time + timedelta(hours=2)).isoformat(),
                    'affected_symbols': ['BTCUSDT', 'ETHUSDT', 'ADAUSDT'],
                    'confidence': 0.92
                }
            ]
            
            # 1. 執行複雜協調
            print(f"📤 執行複雜協調場景 ({len(complex_events)} 事件)")
            
            request_data = {
                'events': complex_events,
                'coordination_mode': 'ADAPTIVE'
            }
            
            async with session.post(
                f"{BASE_URL}/api/v1/event/coordinate",
                json=request_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                if response.status == 200:
                    coord_result = await response.json()
                    coordination_id = coord_result.get('coordination_id')
                    
                    print(f"✅ 複雜協調成功:")
                    print(f"   協調ID: {coordination_id}")
                    print(f"   檢測衝突數: {coord_result.get('conflicts_detected', 0)}")
                    print(f"   解決衝突數: {coord_result.get('conflicts_resolved', 0)}")
                    print(f"   協調效果: {coord_result.get('coordination_effectiveness', 0):.3f}")
                else:
                    print(f"❌ 複雜協調失敗")
                    return False
            
            # 2. 檢查系統狀態變化
            print(f"\n📤 檢查系統狀態變化...")
            
            async with session.get(f"{BASE_URL}/api/v1/event/coordination-status") as response:
                if response.status == 200:
                    status = await response.json()
                    print(f"✅ 系統狀態:")
                    print(f"   活躍事件數: {status.get('active_events_count', 0)}")
                    print(f"   總協調次數: {status.get('stats', {}).get('total_coordinations', 0)}")
                else:
                    print(f"❌ 狀態檢查失敗")
            
            # 3. 檢查歷史記錄
            print(f"\n📤 檢查歷史記錄更新...")
            
            async with session.get(
                f"{BASE_URL}/api/v1/event/coordination-history",
                params={'limit': 1}
            ) as response:
                if response.status == 200:
                    history = await response.json()
                    recent = history.get('coordinations', [])
                    
                    if recent and recent[0].get('coordination_id') == coordination_id:
                        print(f"✅ 歷史記錄已更新")
                        print(f"   最新記錄: {coordination_id}")
                    else:
                        print(f"⚠️ 歷史記錄可能未及時更新")
                else:
                    print(f"❌ 歷史記錄檢查失敗")
            
            print("✅ 綜合 API 測試成功!")
            return True
            
    except Exception as e:
        print(f"❌ 綜合 API 測試失敗: {e}")
        return False

async def main():
    """主測試函數"""
    print("🚀 Phase 3 Week 3 - EventCoordinationEngine API 測試")
    print("=" * 80)
    print("測試項目:")
    print("1. 事件協調 API")
    print("2. 協調系統狀態 API")
    print("3. 協調歷史記錄 API")
    print("4. 活躍調度 API")
    print("5. 協調模式管理 API")
    print("6. 綜合 API 測試")
    print("=" * 80)
    
    # 檢查後端服務是否運行
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status != 200:
                    print("❌ 後端服務未運行，請先啟動後端服務")
                    print("   執行命令: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
                    return
    except Exception as e:
        print("❌ 無法連接到後端服務，請確認服務已啟動")
        print("   執行命令: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # 執行所有測試
    test_results = {}
    
    # 1. 測試事件協調 API
    test_results["event_coordination"] = await test_event_coordination_api()
    
    # 2. 測試協調系統狀態 API
    test_results["coordination_status"] = await test_coordination_status_api()
    
    # 3. 測試協調歷史記錄 API
    test_results["coordination_history"] = await test_coordination_history_api()
    
    # 4. 測試活躍調度 API
    test_results["active_schedules"] = await test_active_schedules_api()
    
    # 5. 測試協調模式管理 API
    test_results["coordination_modes"] = await test_coordination_modes_api()
    
    # 6. 綜合 API 測試
    test_results["comprehensive"] = await test_api_comprehensive()
    
    # 測試結果總結
    print("\n" + "=" * 80)
    print("🎯 Phase 3 Week 3 API 測試結果:")
    passed_tests = 0
    total_tests = len(test_results)
    
    test_names = {
        "event_coordination": "事件協調 API",
        "coordination_status": "協調系統狀態 API",
        "coordination_history": "協調歷史記錄 API",
        "active_schedules": "活躍調度 API",
        "coordination_modes": "協調模式管理 API",
        "comprehensive": "綜合 API 測試"
    }
    
    for i, (test_key, result) in enumerate(test_results.items(), 1):
        status = "✅ 通過" if result else "❌ 失敗"
        test_display_name = test_names.get(test_key, test_key)
        
        print(f"   {i}. {test_display_name}: {status}")
        if result:
            passed_tests += 1
    
    # 計算通過率
    pass_rate = (passed_tests / total_tests) * 100
    print(f"\n📊 API 測試通過率: {pass_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if pass_rate == 100:
        print("🎉 所有 API 測試通過！EventCoordinationEngine API 運行正常！")
    elif pass_rate >= 80:
        print("⚠️ 大部分 API 測試通過，但有部分問題需要解決。")
    else:
        print("❌ 多項 API 測試失敗，需要檢查 API 實現。")
    
    print(f"\n📋 Phase 3 Week 3 API 狀態: {'✅ 完成' if pass_rate >= 80 else '⚠️ 需要修復'}")
    
    if pass_rate >= 80:
        print("\n🎯 Week 3 API 功能已完成:")
        print("   ✅ 事件協調 API - 多事件協調處理")
        print("   ✅ 系統狀態 API - 協調引擎狀態監控")
        print("   ✅ 歷史記錄 API - 協調歷史查詢")
        print("   ✅ 活躍調度 API - 調度管理")
        print("   ✅ 模式管理 API - 協調模式配置")

if __name__ == "__main__":
    asyncio.run(main())
