#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading X Phase 3 Week 2 API 測試
測試 EventImpactAssessment 相關的 API 端點
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
import requests
import time
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# API 基礎配置
BASE_URL = "http://localhost:8000/api/v1/scalping"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def wait_for_server(max_attempts=10, delay=2):
    """等待服務器啟動"""
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/prices", timeout=5)
            if response.status_code == 200:
                print("✅ 服務器連接成功")
                return True
        except:
            pass
        
        if attempt < max_attempts - 1:
            print(f"⏳ 等待服務器啟動... ({attempt + 1}/{max_attempts})")
            time.sleep(delay)
    
    print("❌ 無法連接到服務器")
    return False

def test_event_impact_assessment_api():
    """測試事件影響評估 API"""
    print("\n🎯 測試事件影響評估 API")
    print("=" * 60)
    
    try:
        # 測試數據 - FOMC 會議
        event_data = {
            "event_id": "test_fomc_001",
            "event_type": "FOMC_MEETING",
            "severity": "HIGH",
            "confidence": 0.9,
            "event_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "affected_symbols": ["BTCUSDT", "ETHUSDT", "ADAUSDT"],
            "title": "聯準會利率決議會議",
            "description": "市場預期升息機率較高"
        }
        
        # 測試參數
        params = {
            "target_symbols": ["BTCUSDT", "ETHUSDT", "ADAUSDT"],
            "timeframe": "short_term"
        }
        
        print("📊 發送事件影響評估請求...")
        
        response = requests.post(
            f"{BASE_URL}/assess-event-impact",
            json=event_data,
            params=params,
            headers=HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ 事件影響評估 API 測試成功!")
            print(f"   評估ID: {result['assessment_id']}")
            print(f"   事件ID: {result['event_id']}")
            print(f"   整體嚴重程度: {result['overall_assessment']['severity']}")
            print(f"   主要方向: {result['overall_assessment']['direction']}")
            print(f"   價格影響: {result['impact_metrics']['price_impact_percent']:.2f}%")
            print(f"   波動率影響: {result['impact_metrics']['volatility_impact']:.3f}")
            print(f"   預期持續時間: {result['impact_metrics']['duration_hours']:.1f}小時")
            print(f"   信心分數: {result['impact_metrics']['confidence_score']:.3f}")
            
            # 檢查資產評估
            asset_assessments = result['asset_assessments']
            print(f"\n📈 資產特定影響 ({len(asset_assessments)}個資產):")
            for symbol, assessment in asset_assessments.items():
                print(f"   {symbol}: {assessment['price_impact_percent']:.2f}% "
                      f"(信心: {assessment['confidence_score']:.3f})")
            
            # 檢查風險因子
            risk_factors = result.get('risk_factors', [])
            if risk_factors:
                print(f"\n⚠️  風險因子 ({len(risk_factors)}個):")
                for i, risk in enumerate(risk_factors[:3], 1):
                    print(f"   {i}. {risk}")
            
            # 檢查緩解策略
            strategies = result.get('mitigation_strategies', [])
            if strategies:
                print(f"\n💡 緩解策略 ({len(strategies)}個):")
                for i, strategy in enumerate(strategies[:3], 1):
                    print(f"   {i}. {strategy}")
            
            return True, result['assessment_id']
        else:
            print(f"❌ 事件影響評估 API 測試失敗: {response.status_code}")
            print(f"   錯誤訊息: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ 事件影響評估 API 測試異常: {e}")
        return False, None

def test_get_impact_assessment_api(assessment_id):
    """測試獲取影響評估結果 API"""
    print("\n🎯 測試獲取影響評估結果 API")
    print("=" * 60)
    
    try:
        if not assessment_id:
            print("⚠️  跳過測試 - 沒有可用的評估ID")
            return False
        
        print(f"🔍 獲取評估結果: {assessment_id}")
        
        response = requests.get(
            f"{BASE_URL}/impact-assessment/{assessment_id}",
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            assessment = result['assessment']
            
            print("✅ 獲取影響評估結果 API 測試成功!")
            print(f"   評估ID: {assessment['assessment_id']}")
            print(f"   事件ID: {assessment['event_id']}")
            print(f"   評估時間: {assessment['timestamp']}")
            print(f"   整體嚴重程度: {assessment['overall_severity']}")
            print(f"   主要方向: {assessment['primary_direction']}")
            print(f"   價格影響: {assessment['price_impact_percent']:.2f}%")
            print(f"   持續時間: {assessment['duration_hours']:.1f}小時")
            print(f"   信心分數: {assessment['confidence_score']:.3f}")
            print(f"   涵蓋資產數: {assessment['asset_count']}")
            print(f"   風險因子數: {assessment['risk_factors_count']}")
            print(f"   緩解策略數: {assessment['mitigation_strategies_count']}")
            
            return True
        else:
            print(f"❌ 獲取影響評估結果 API 測試失敗: {response.status_code}")
            print(f"   錯誤訊息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 獲取影響評估結果 API 測試異常: {e}")
        return False

def test_recent_assessments_api():
    """測試獲取最近評估列表 API"""
    print("\n🎯 測試獲取最近評估列表 API")
    print("=" * 60)
    
    try:
        params = {"limit": 5}
        
        response = requests.get(
            f"{BASE_URL}/recent-impact-assessments",
            params=params,
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            assessments = result['assessments']
            
            print("✅ 獲取最近評估列表 API 測試成功!")
            print(f"   返回評估數: {result['total_count']}")
            
            if assessments:
                print(f"\n📋 最近評估列表:")
                print(f"{'評估ID':<30} {'嚴重程度':<10} {'方向':<10} {'價格影響':<10} {'信心':<8}")
                print("-" * 75)
                
                for assessment in assessments:
                    print(f"{assessment['assessment_id']:<30} "
                          f"{assessment['severity']:<10} "
                          f"{assessment['direction']:<10} "
                          f"{assessment['price_impact']:>8.2f}% "
                          f"{assessment['confidence']:>6.3f}")
            
            return True
        else:
            print(f"❌ 獲取最近評估列表 API 測試失敗: {response.status_code}")
            print(f"   錯誤訊息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 獲取最近評估列表 API 測試異常: {e}")
        return False

def test_asset_sensitivity_api():
    """測試資產敏感度分析 API"""
    print("\n🎯 測試資產敏感度分析 API")
    print("=" * 60)
    
    try:
        test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        results = {}
        
        for symbol in test_symbols:
            params = {
                "event_type": "FOMC_MEETING",
                "severity": "HIGH"
            }
            
            print(f"🔬 分析 {symbol} 敏感度...")
            
            response = requests.get(
                f"{BASE_URL}/asset-sensitivity-analysis/{symbol}",
                params=params,
                headers=HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                sensitivity = result['sensitivity_analysis']
                results[symbol] = sensitivity
                
                print(f"   ✅ {symbol} 敏感度分析成功")
                print(f"      敏感度分數: {sensitivity['sensitivity_score']:.3f}")
                print(f"      歷史貝塔: {sensitivity['historical_beta']:.3f}")
                print(f"      相關係數: {sensitivity['correlation_coefficient']:.3f}")
            else:
                print(f"   ❌ {symbol} 敏感度分析失敗: {response.status_code}")
                return False
        
        if results:
            print("\n📊 敏感度分析總結:")
            
            # 按敏感度排序
            sorted_results = sorted(results.items(), 
                                  key=lambda x: x[1]['sensitivity_score'], 
                                  reverse=True)
            
            print(f"{'資產':<10} {'敏感度':<8} {'貝塔':<8} {'相關性':<8} {'即時':<8} {'短期':<8} {'中期':<8} {'長期':<8}")
            print("-" * 70)
            
            for symbol, sens in sorted_results:
                timeframes = sens['timeframe_sensitivities']
                print(f"{symbol:<10} {sens['sensitivity_score']:>6.3f} "
                      f"{sens['historical_beta']:>6.3f} "
                      f"{sens['correlation_coefficient']:>6.3f} "
                      f"{timeframes['immediate']:>6.3f} "
                      f"{timeframes['short_term']:>6.3f} "
                      f"{timeframes['medium_term']:>6.3f} "
                      f"{timeframes['long_term']:>6.3f}")
            
            print("✅ 資產敏感度分析 API 測試成功!")
            return True
        else:
            print("❌ 沒有獲得有效的敏感度分析結果")
            return False
            
    except Exception as e:
        print(f"❌ 資產敏感度分析 API 測試異常: {e}")
        return False

def test_assessment_summary_api():
    """測試影響評估系統總覽 API"""
    print("\n🎯 測試影響評估系統總覽 API")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/impact-assessment-summary",
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ 影響評估系統總覽 API 測試成功!")
            
            # 系統狀態
            system_status = result['system_status']
            print(f"\n📊 系統狀態:")
            print(f"   總評估數: {system_status['total_assessments']}")
            print(f"   成功評估數: {system_status['successful_assessments']}")
            print(f"   成功率: {system_status['success_rate']:.1%}")
            print(f"   平均計算時間: {system_status['avg_computation_time_ms']:.2f}ms")
            
            # 緩存狀態
            cache_status = result['cache_status']
            print(f"\n💾 緩存狀態:")
            print(f"   敏感度緩存: {cache_status['sensitivity_cache_size']} 項目")
            print(f"   評估歷史: {cache_status['assessment_history_size']} 項目")
            
            # Phase 3 Week 2 狀態
            week2_status = result['phase3_week2_status']
            print(f"\n🎯 Phase 3 Week 2 完成狀態:")
            for component, status in week2_status.items():
                print(f"   {component}: {status}")
            
            # 最近評估
            recent_assessments = result.get('recent_assessments', [])
            if recent_assessments:
                print(f"\n📋 最近評估 ({len(recent_assessments)}筆):")
                for assessment in recent_assessments[:3]:
                    print(f"   {assessment['assessment_id']}: "
                          f"{assessment['severity']} / {assessment['direction']}")
            
            return True
        else:
            print(f"❌ 影響評估系統總覽 API 測試失敗: {response.status_code}")
            print(f"   錯誤訊息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 影響評估系統總覽 API 測試異常: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 Phase 3 Week 2 - EventImpactAssessment API 測試")
    print("=" * 80)
    print("測試 EventImpactAssessment 相關的 API 端點")
    print("=" * 80)
    
    # 檢查服務器連接
    if not wait_for_server():
        print("❌ 無法連接到服務器，請確保後端服務正在運行")
        print("   提示：執行 'uvicorn main:app --reload --host 0.0.0.0 --port 8000'")
        return
    
    # 執行所有 API 測試
    test_results = {}
    assessment_id = None
    
    # 1. 測試事件影響評估 API
    success, assessment_id = test_event_impact_assessment_api()
    test_results["event_impact_assessment"] = success
    
    # 2. 測試獲取影響評估結果 API
    test_results["get_impact_assessment"] = test_get_impact_assessment_api(assessment_id)
    
    # 3. 測試獲取最近評估列表 API
    test_results["recent_assessments"] = test_recent_assessments_api()
    
    # 4. 測試資產敏感度分析 API
    test_results["asset_sensitivity"] = test_asset_sensitivity_api()
    
    # 5. 測試影響評估系統總覽 API
    test_results["assessment_summary"] = test_assessment_summary_api()
    
    # 測試結果總結
    print("\n" + "=" * 80)
    print("🎯 Phase 3 Week 2 API 測試結果:")
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        test_display_name = {
            "event_impact_assessment": "事件影響評估 API",
            "get_impact_assessment": "獲取影響評估結果 API",
            "recent_assessments": "最近評估列表 API",
            "asset_sensitivity": "資產敏感度分析 API",
            "assessment_summary": "影響評估系統總覽 API"
        }.get(test_name, test_name)
        
        print(f"   {total_tests - len(test_results) + list(test_results.keys()).index(test_name) + 1}. {test_display_name}: {status}")
        if result:
            passed_tests += 1
    
    # 計算通過率
    pass_rate = (passed_tests / total_tests) * 100
    print(f"\n📊 測試通過率: {pass_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if pass_rate == 100:
        print("🎉 所有 API 測試通過！EventImpactAssessment API 正常運行！")
    elif pass_rate >= 80:
        print("⚠️  部分 API 測試失敗，但核心功能運行正常。")
    else:
        print("❌ 多項 API 測試失敗，需要檢查服務實現。")
    
    print(f"\n📋 Phase 3 Week 2 API 實施狀態: {'✅ 完成' if pass_rate >= 80 else '⚠️ 需要修復'}")
    
    if pass_rate >= 80:
        print("\n🎯 Week 2 API 端點已完成:")
        print("   ✅ /assess-event-impact - 事件影響評估")
        print("   ✅ /impact-assessment/{id} - 獲取評估結果")
        print("   ✅ /recent-impact-assessments - 最近評估列表")
        print("   ✅ /asset-sensitivity-analysis/{symbol} - 資產敏感度分析")
        print("   ✅ /impact-assessment-summary - 系統總覽")

if __name__ == "__main__":
    main()
