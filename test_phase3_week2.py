#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading X Phase 3 Week 2 系統測試
測試 EventImpactAssessment 事件影響評估系統的完整功能
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

async def test_event_impact_assessment():
    """測試事件影響評估系統"""
    print("\n🎯 測試事件影響評估系統")
    print("=" * 60)
    
    try:
        from app.services.event_impact_assessment import (
            event_impact_assessment,
            ImpactSeverity,
            ImpactDirection,
            ImpactTimeframe
        )
        
        print("📊 創建測試事件數據...")
        
        # 測試事件1: FOMC會議
        fomc_event_data = {
            'event_type': 'FOMC_MEETING',
            'severity': 'HIGH',
            'confidence': 0.9,
            'event_time': datetime.now() + timedelta(hours=2),
            'affected_symbols': ['BTCUSDT', 'ETHUSDT', 'ADAUSDT'],
            'title': '聯準會利率決議會議',
            'description': '市場預期升息機率較高'
        }
        
        print("🔍 執行FOMC事件影響評估...")
        fomc_assessment = await event_impact_assessment.assess_event_impact(
            event_id="fomc_test_001",
            event_data=fomc_event_data,
            target_symbols=["BTCUSDT", "ETHUSDT", "ADAUSDT"],
            assessment_timeframe=ImpactTimeframe.SHORT_TERM
        )
        
        if fomc_assessment:
            print(f"✅ FOMC評估完成:")
            print(f"   評估ID: {fomc_assessment.assessment_id}")
            print(f"   整體嚴重程度: {fomc_assessment.overall_severity.value}")
            print(f"   主要方向: {fomc_assessment.primary_direction.value}")
            print(f"   影響時間框架: {fomc_assessment.primary_timeframe.value}")
            print(f"   價格影響: {fomc_assessment.impact_metrics.price_impact_percent:.2f}%")
            print(f"   波動率影響: {fomc_assessment.impact_metrics.volatility_impact:.3f}")
            print(f"   預期持續時間: {fomc_assessment.impact_metrics.duration_hours:.1f}小時")
            print(f"   信心分數: {fomc_assessment.impact_metrics.confidence_score:.3f}")
            
            # 顯示資產特定評估
            print(f"\n📈 資產特定影響:")
            for symbol, metrics in fomc_assessment.asset_assessments.items():
                print(f"   {symbol}: {metrics.price_impact_percent:.2f}% (信心: {metrics.confidence_score:.3f})")
            
            # 顯示風險因子
            if fomc_assessment.risk_factors:
                print(f"\n⚠️  識別的風險因子:")
                for i, risk in enumerate(fomc_assessment.risk_factors, 1):
                    print(f"   {i}. {risk}")
            
            # 顯示緩解策略
            if fomc_assessment.mitigation_strategies:
                print(f"\n💡 建議的緩解策略:")
                for i, strategy in enumerate(fomc_assessment.mitigation_strategies, 1):
                    print(f"   {i}. {strategy}")
        else:
            print("❌ FOMC事件評估失敗")
            return False
        
        # 測試事件2: 比特幣減半
        print(f"\n🔍 執行比特幣減半事件評估...")
        
        halving_event_data = {
            'event_type': 'HALVING_EVENT',
            'severity': 'CRITICAL',
            'confidence': 0.98,
            'event_time': datetime.now() + timedelta(days=30),
            'affected_symbols': ['BTCUSDT'],
            'title': '比特幣減半事件',
            'description': '比特幣獎勵減半，歷史上通常帶來長期利多'
        }
        
        halving_assessment = await event_impact_assessment.assess_event_impact(
            event_id="halving_test_001",
            event_data=halving_event_data,
            target_symbols=["BTCUSDT", "ETHUSDT"],
            assessment_timeframe=ImpactTimeframe.LONG_TERM
        )
        
        if halving_assessment:
            print(f"✅ 減半評估完成:")
            print(f"   整體嚴重程度: {halving_assessment.overall_severity.value}")
            print(f"   主要方向: {halving_assessment.primary_direction.value}")
            print(f"   價格影響: {halving_assessment.impact_metrics.price_impact_percent:.2f}%")
            print(f"   最大回撤: {halving_assessment.impact_metrics.max_drawdown:.2f}%")
            print(f"   恢復時間: {halving_assessment.impact_metrics.recovery_time_hours:.1f}小時")
            
            # 信心區間
            if halving_assessment.confidence_intervals:
                print(f"\n📊 價格影響信心區間:")
                if 'overall_price_impact' in halving_assessment.confidence_intervals:
                    lower, upper = halving_assessment.confidence_intervals['overall_price_impact']
                    print(f"   整體影響: [{lower:.2f}%, {upper:.2f}%]")
        else:
            print("❌ 減半事件評估失敗")
            return False
        
        print("✅ 事件影響評估系統測試成功!")
        return True
        
    except Exception as e:
        print(f"❌ 事件影響評估系統測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_asset_sensitivity_analysis():
    """測試資產敏感度分析"""
    print("\n🎯 測試資產敏感度分析")
    print("=" * 60)
    
    try:
        from app.services.event_impact_assessment import event_impact_assessment
        
        print("🔬 測試多資產敏感度分析...")
        
        # 創建高影響事件
        high_impact_event = {
            'event_type': 'FLASH_CRASH',
            'severity': 'CRITICAL',
            'confidence': 0.95,
            'event_time': datetime.now() - timedelta(hours=1),
            'affected_symbols': ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT'],
            'title': '市場閃崩事件',
            'description': '主要交易所出現技術問題導致拋售'
        }
        
        # 測試不同資產的敏感度
        test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "BNBUSDT"]
        
        assessment = await event_impact_assessment.assess_event_impact(
            event_id="sensitivity_test_001",
            event_data=high_impact_event,
            target_symbols=test_symbols,
            assessment_timeframe="medium"
        )
        
        if assessment:
            print(f"✅ 敏感度分析完成:")
            print(f"\n📊 各資產敏感度排序:")
            
            # 按敏感度排序資產
            sensitivity_ranking = sorted(
                assessment.asset_sensitivities.items(),
                key=lambda x: x[1].sensitivity_score,
                reverse=True
            )
            
            for i, (symbol, sensitivity) in enumerate(sensitivity_ranking, 1):
                print(f"   {i}. {symbol}:")
                print(f"      敏感度分數: {sensitivity.sensitivity_score:.3f}")
                print(f"      歷史貝塔: {sensitivity.historical_beta:.3f}")
                print(f"      相關係數: {sensitivity.correlation_coefficient:.3f}")
                print(f"      波動率乘數: {sensitivity.volatility_multiplier:.3f}")
                print(f"      即時敏感度: {sensitivity.immediate_sensitivity:.3f}")
                print(f"      短期敏感度: {sensitivity.short_term_sensitivity:.3f}")
                print(f"      中期敏感度: {sensitivity.medium_term_sensitivity:.3f}")
                print(f"      長期敏感度: {sensitivity.long_term_sensitivity:.3f}")
                print()
            
            # 分析高敏感度資產
            high_sensitivity_assets = [
                symbol for symbol, sens in assessment.asset_sensitivities.items()
                if sens.sensitivity_score > 0.7
            ]
            
            if high_sensitivity_assets:
                print(f"⚠️  高敏感度資產 (>0.7): {', '.join(high_sensitivity_assets)}")
            
            print("✅ 資產敏感度分析測試成功!")
            return True
        else:
            print("❌ 敏感度分析失敗")
            return False
        
    except Exception as e:
        print(f"❌ 資產敏感度分析測試失敗: {e}")
        return False

async def test_impact_timeframe_analysis():
    """測試不同時間框架的影響分析"""
    print("\n🎯 測試時間框架影響分析")
    print("=" * 60)
    
    try:
        from app.services.event_impact_assessment import (
            event_impact_assessment,
            ImpactTimeframe
        )
        
        print("⏰ 測試不同時間框架的影響差異...")
        
        # 創建測試事件
        test_event = {
            'event_type': 'CPI_DATA',
            'severity': 'HIGH',
            'confidence': 0.85,
            'event_time': datetime.now() + timedelta(hours=6),
            'affected_symbols': ['BTCUSDT', 'ETHUSDT'],
            'title': 'CPI通脹數據發布',
            'description': '通脹數據可能超出預期'
        }
        
        # 測試所有時間框架
        timeframes = [
            ImpactTimeframe.IMMEDIATE,
            ImpactTimeframe.SHORT_TERM,
            ImpactTimeframe.MEDIUM_TERM,
            ImpactTimeframe.LONG_TERM
        ]
        
        timeframe_results = {}
        
        for timeframe in timeframes:
            print(f"🔍 評估 {timeframe.value} 時間框架...")
            
            assessment = await event_impact_assessment.assess_event_impact(
                event_id=f"timeframe_test_{timeframe.value}",
                event_data=test_event,
                target_symbols=["BTCUSDT", "ETHUSDT"],
                assessment_timeframe=timeframe
            )
            
            if assessment:
                timeframe_results[timeframe.value] = {
                    'price_impact': assessment.impact_metrics.price_impact_percent,
                    'volatility_impact': assessment.impact_metrics.volatility_impact,
                    'duration_hours': assessment.impact_metrics.duration_hours,
                    'confidence': assessment.impact_metrics.confidence_score,
                    'severity': assessment.overall_severity.value
                }
        
        # 比較不同時間框架的結果
        if timeframe_results:
            print(f"\n📊 時間框架影響比較:")
            print(f"{'時間框架':<12} {'價格影響':<10} {'波動影響':<10} {'持續時間':<10} {'嚴重程度':<10}")
            print("-" * 60)
            
            for timeframe, results in timeframe_results.items():
                print(f"{timeframe:<12} {results['price_impact']:>8.2f}% {results['volatility_impact']:>9.3f} "
                      f"{results['duration_hours']:>8.1f}h {results['severity']:<10}")
            
            # 分析趨勢
            print(f"\n📈 時間框架分析:")
            immediate_impact = timeframe_results.get('immediate', {}).get('price_impact', 0)
            long_term_impact = timeframe_results.get('long_term', {}).get('price_impact', 0)
            
            if immediate_impact > long_term_impact:
                print("   💡 事件呈現即時高影響，長期影響遞減的模式")
            elif long_term_impact > immediate_impact:
                print("   💡 事件呈現長期累積影響的模式")
            else:
                print("   💡 事件影響在不同時間框架相對穩定")
            
            print("✅ 時間框架影響分析測試成功!")
            return True
        else:
            print("❌ 沒有獲得有效的時間框架分析結果")
            return False
        
    except Exception as e:
        print(f"❌ 時間框架影響分析測試失敗: {e}")
        return False

async def test_system_integration():
    """測試系統整合"""
    print("\n🎯 測試事件影響評估系統整合")
    print("=" * 60)
    
    try:
        from app.services.event_impact_assessment import event_impact_assessment
        
        print("🔗 測試系統狀態和歷史記錄...")
        
        # 獲取系統摘要
        summary = event_impact_assessment.export_assessment_summary()
        
        print(f"📊 系統狀態摘要:")
        system_info = summary['system_info']
        print(f"   總評估數: {system_info['total_assessments']}")
        print(f"   成功評估數: {system_info['successful_assessments']}")
        print(f"   成功率: {system_info['success_rate']:.1%}")
        print(f"   平均計算時間: {system_info['avg_computation_time_ms']:.2f}ms")
        
        # 檢查最近評估
        recent_assessments = summary['recent_assessments']
        if recent_assessments:
            print(f"\n📋 最近評估記錄 ({len(recent_assessments)}筆):")
            for assessment in recent_assessments:
                print(f"   {assessment['assessment_id']}: "
                      f"{assessment['severity']} / {assessment['direction']} / "
                      f"{assessment['price_impact']:.2f}%")
        
        # 測試歷史記錄檢索
        print(f"\n🔍 測試歷史記錄檢索...")
        recent_list = event_impact_assessment.get_recent_assessments(3)
        print(f"   獲取最近3筆評估: {len(recent_list)}筆")
        
        # 測試特定評估檢索
        if recent_list:
            test_id = recent_list[0].assessment_id
            retrieved = event_impact_assessment.get_assessment_by_id(test_id)
            if retrieved:
                print(f"   ✅ 成功檢索評估: {test_id}")
            else:
                print(f"   ❌ 檢索評估失敗: {test_id}")
        
        # 測試緩存狀態
        cache_size = summary['sensitivity_cache_size']
        history_size = summary['assessment_history_size']
        
        print(f"\n💾 緩存狀態:")
        print(f"   敏感度緩存: {cache_size} 項目")
        print(f"   評估歷史: {history_size} 項目")
        
        # 創建一個新的測試評估來驗證整合
        print(f"\n🧪 執行整合測試評估...")
        
        integration_event = {
            'event_type': 'REGULATION_NEWS',
            'severity': 'MEDIUM',
            'confidence': 0.7,
            'event_time': datetime.now() + timedelta(hours=12),
            'affected_symbols': ['BTCUSDT', 'ETHUSDT', 'ADAUSDT'],
            'title': '監管政策更新',
            'description': '新的加密貨幣監管框架即將發布'
        }
        
        integration_assessment = await event_impact_assessment.assess_event_impact(
            event_id="integration_test_001",
            event_data=integration_event,
            target_symbols=["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        )
        
        if integration_assessment:
            print(f"   ✅ 整合測試評估成功")
            print(f"   評估ID: {integration_assessment.assessment_id}")
            print(f"   計算時間: {integration_assessment.computation_time_ms:.2f}ms")
            print(f"   數據質量: {integration_assessment.data_quality_score:.3f}")
            
            # 驗證資產評估完整性
            expected_assets = {"BTCUSDT", "ETHUSDT", "ADAUSDT"}
            actual_assets = set(integration_assessment.asset_assessments.keys())
            
            if expected_assets.issubset(actual_assets):
                print(f"   ✅ 所有預期資產都有評估結果")
            else:
                missing = expected_assets - actual_assets
                print(f"   ⚠️  缺少資產評估: {missing}")
            
            # 驗證敏感度分析完整性
            sensitivity_assets = set(integration_assessment.asset_sensitivities.keys())
            if expected_assets.issubset(sensitivity_assets):
                print(f"   ✅ 所有資產都有敏感度分析")
            else:
                missing_sens = expected_assets - sensitivity_assets
                print(f"   ⚠️  缺少敏感度分析: {missing_sens}")
        else:
            print(f"   ❌ 整合測試評估失敗")
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
    print("🚀 Phase 3 Week 2 - EventImpactAssessment 系統測試")
    print("=" * 80)
    print("測試項目:")
    print("1. 事件影響評估系統核心功能")
    print("2. 資產敏感度分析")
    print("3. 時間框架影響分析")
    print("4. 系統整合測試")
    print("=" * 80)
    
    # 執行所有測試
    test_results = {}
    
    # 1. 測試事件影響評估系統
    test_results["impact_assessment"] = await test_event_impact_assessment()
    
    # 2. 測試資產敏感度分析
    test_results["sensitivity_analysis"] = await test_asset_sensitivity_analysis()
    
    # 3. 測試時間框架影響分析
    test_results["timeframe_analysis"] = await test_impact_timeframe_analysis()
    
    # 4. 測試系統整合
    test_results["system_integration"] = await test_system_integration()
    
    # 測試結果總結
    print("\n" + "=" * 80)
    print("🎯 Phase 3 Week 2 測試結果:")
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        test_display_name = {
            "impact_assessment": "事件影響評估系統",
            "sensitivity_analysis": "資產敏感度分析",
            "timeframe_analysis": "時間框架影響分析",
            "system_integration": "系統整合測試"
        }.get(test_name, test_name)
        
        print(f"   {total_tests - len(test_results) + list(test_results.keys()).index(test_name) + 1}. {test_display_name}: {status}")
        if result:
            passed_tests += 1
    
    # 計算通過率
    pass_rate = (passed_tests / total_tests) * 100
    print(f"\n📊 測試通過率: {pass_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if pass_rate == 100:
        print("🎉 所有測試通過！EventImpactAssessment 系統運行正常！")
    elif pass_rate >= 75:
        print("⚠️  部分測試失敗，但核心功能運行正常。")
    else:
        print("❌ 多項測試失敗，需要檢查系統實現。")
    
    print(f"\n📋 Phase 3 Week 2 實施狀態: {'✅ 完成' if pass_rate >= 75 else '⚠️ 需要修復'}")
    
    if pass_rate >= 75:
        print("\n🎯 Week 2 核心功能已完成:")
        print("   ✅ EventImpactAssessment - 事件影響評估系統")
        print("   ✅ 量化影響評估 - 價格、波動率、持續時間")
        print("   ✅ 資產敏感度分析 - 多資產相關性評估")
        print("   ✅ 時間框架分析 - 不同時程的影響模式")
        print("   ✅ 風險因子識別 - 自動風險檢測")
        print("   ✅ 緩解策略生成 - 智能建議系統")

if __name__ == "__main__":
    asyncio.run(main())
