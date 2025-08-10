"""
🧪 EPL Decision History Tracking 修正驗證測試
===========================================

測試修正後的 EPL Decision History Tracking 實現
"""

import sys
import asyncio
from datetime import datetime
from pathlib import Path

# 添加路徑
sys.path.append("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring/3_epl_decision_history_tracking")

try:
    from epl_decision_history_tracking import (
        EPLDecisionHistoryTracker, 
        EPLDecisionType, 
        SignalPriority,
        EPLDecisionRecord
    )
    print("✅ 成功導入所有必要模組")
except ImportError as e:
    print(f"❌ 導入失敗: {e}")
    sys.exit(1)

async def test_initialization():
    """測試初始化"""
    print("\n📝 測試 1: 系統初始化")
    try:
        epl_tracker = EPLDecisionHistoryTracker()
        print("✅ EPL 追蹤器初始化成功")
        
        # 檢查關鍵屬性
        required_attrs = ['config', 'decision_history', 'outcome_history', 'retention_days', 'track_all_decisions']
        for attr in required_attrs:
            if hasattr(epl_tracker, attr):
                print(f"✅ 屬性 {attr}: 存在")
            else:
                print(f"❌ 屬性 {attr}: 缺失")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 初始化失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_decision_recording():
    """測試決策記錄"""
    print("\n📝 測試 2: 決策記錄功能")
    try:
        epl_tracker = EPLDecisionHistoryTracker()
        
        # 測試記錄決策
        decision_data = {
            "symbol": "BTCUSDT",
            "signal_priority": "HIGH",
            "decision_type": "REPLACE_POSITION",
            "confidence_score": 0.85,
            "risk_assessment": {
                "max_risk": 0.02,
                "expected_return": 0.05
            },
            "position_context": {
                "current_size": 1000,
                "new_size": 1200
            },
            "execution_details": {
                "price": 45000,
                "slippage": 0.001
            }
        }
        
        decision_id = await epl_tracker.record_epl_decision(decision_data)
        print(f"✅ 記錄決策成功: {decision_id[:12]}...")
        
        # 驗證決策已記錄
        if len(epl_tracker.decision_history) > 0:
            print("✅ 決策歷史已更新")
            return True
        else:
            print("❌ 決策歷史未更新")
            return False
        
    except Exception as e:
        print(f"❌ 決策記錄失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_outcome_recording():
    """測試結果記錄"""
    print("\n📝 測試 3: 結果記錄功能")
    try:
        epl_tracker = EPLDecisionHistoryTracker()
        
        # 先記錄一個決策
        decision_data = {
            "symbol": "ETHUSDT",
            "signal_priority": "CRITICAL",
            "decision_type": "CREATE_NEW_POSITION",
            "confidence_score": 0.92,
            "risk_assessment": {"max_risk": 0.015},
            "position_context": {"allocation": 0.15}
        }
        
        decision_id = await epl_tracker.record_epl_decision(decision_data)
        
        # 記錄結果
        outcome_data = {
            "success": True,
            "pnl": 850.50,
            "risk_realized": 0.018,
            "execution_quality": 0.95
        }
        
        success = await epl_tracker.record_decision_outcome(decision_id, outcome_data)
        print(f"✅ 記錄結果成功: {success}")
        
        # 驗證結果已記錄
        if decision_id in epl_tracker.outcome_history:
            print("✅ 結果歷史已更新")
            return True
        else:
            print("❌ 結果歷史未更新")
            return False
        
    except Exception as e:
        print(f"❌ 結果記錄失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_analytics_methods():
    """測試分析方法"""
    print("\n📝 測試 4: 分析方法")
    try:
        epl_tracker = EPLDecisionHistoryTracker()
        
        # 記錄幾個測試決策
        test_decisions = [
            {
                "symbol": "BTCUSDT", "signal_priority": "HIGH", "decision_type": "REPLACE_POSITION",
                "confidence_score": 0.85, "risk_assessment": {"max_risk": 0.02}
            },
            {
                "symbol": "ETHUSDT", "signal_priority": "CRITICAL", "decision_type": "CREATE_NEW_POSITION", 
                "confidence_score": 0.92, "risk_assessment": {"max_risk": 0.015}
            },
            {
                "symbol": "ADAUSDT", "signal_priority": "LOW", "decision_type": "IGNORE_SIGNAL",
                "confidence_score": 0.35, "risk_assessment": {"risk_too_high": True}
            }
        ]
        
        decision_ids = []
        for decision in test_decisions:
            decision_id = await epl_tracker.record_epl_decision(decision)
            decision_ids.append(decision_id)
        
        # 記錄一些結果
        outcomes = [
            {"success": True, "pnl": 750.0, "risk_realized": 0.019},
            {"success": True, "pnl": 1200.0, "risk_realized": 0.012},
            {"success": False, "pnl": 0, "risk_realized": 0}
        ]
        
        for decision_id, outcome in zip(decision_ids, outcomes):
            await epl_tracker.record_decision_outcome(decision_id, outcome)
        
        # 測試各種分析方法
        analysis_methods = [
            ("綜合分析", epl_tracker.get_comprehensive_analytics),
            ("性能指標", epl_tracker.get_performance_metrics),
            ("決策模式", epl_tracker.analyze_decision_patterns),
            ("風險分析", epl_tracker.get_risk_analytics),
            ("系統狀態", epl_tracker.get_system_status)
        ]
        
        results = {}
        for name, method in analysis_methods:
            try:
                result = await method()
                if result and not result.get('error'):
                    print(f"✅ {name}: 成功")
                    results[name] = True
                else:
                    print(f"❌ {name}: 失敗 - {result.get('error', '無結果')}")
                    results[name] = False
            except Exception as e:
                print(f"❌ {name}: 異常 - {e}")
                results[name] = False
        
        success_count = sum(results.values())
        total_count = len(results)
        
        print(f"📊 分析方法測試: {success_count}/{total_count} 成功")
        return success_count >= total_count * 0.8  # 80% 成功率
        
    except Exception as e:
        print(f"❌ 分析方法測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_query_methods():
    """測試查詢方法"""
    print("\n📝 測試 5: 查詢方法")
    try:
        epl_tracker = EPLDecisionHistoryTracker()
        
        # 記錄測試數據
        decision_id = await epl_tracker.record_epl_decision({
            "symbol": "BTCUSDT", "signal_priority": "HIGH", "decision_type": "REPLACE_POSITION",
            "confidence_score": 0.88, "risk_assessment": {"max_risk": 0.02}
        })
        
        # 測試查詢方法
        query_methods = [
            ("最近決策", epl_tracker.get_recent_decisions, {"hours": 24}),
            ("按類型查詢", epl_tracker.get_decisions_by_type, {"decision_type": "REPLACE_POSITION"}),
            ("決策時間線", epl_tracker.get_decision_timeline, {})
        ]
        
        results = {}
        for name, method, kwargs in query_methods:
            try:
                if kwargs:
                    result = await method(**kwargs)
                else:
                    result = await method()
                
                if isinstance(result, list) and len(result) >= 0:
                    print(f"✅ {name}: 成功 ({len(result)} 項)")
                    results[name] = True
                else:
                    print(f"❌ {name}: 無效結果")
                    results[name] = False
            except Exception as e:
                print(f"❌ {name}: 異常 - {e}")
                results[name] = False
        
        success_count = sum(results.values())
        total_count = len(results)
        
        print(f"📊 查詢方法測試: {success_count}/{total_count} 成功")
        return success_count == total_count
        
    except Exception as e:
        print(f"❌ 查詢方法測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主測試函數"""
    print("🔧 EPL Decision History Tracking 修正驗證測試")
    print("=" * 70)
    
    # 執行所有測試
    tests = [
        ("初始化", test_initialization),
        ("決策記錄", test_decision_recording), 
        ("結果記錄", test_outcome_recording),
        ("分析方法", test_analytics_methods),
        ("查詢方法", test_query_methods)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ 測試 {test_name} 發生異常: {e}")
            results[test_name] = False
    
    # 計算總體結果
    print("\n🎯 測試結果總結")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {status} {test_name}")
    
    success_count = sum(results.values())
    total_count = len(results)
    success_rate = (success_count / total_count) * 100
    
    print(f"\n📊 總體成功率: {success_rate:.1f}% ({success_count}/{total_count})")
    
    if success_rate >= 90:
        print("🎉 EPL Decision History Tracking 修正成功!")
        print("✅ 實現品質: 優秀")
        print("🚀 準備繼續下一個組件...")
        return True
    elif success_rate >= 80:
        print("👍 EPL Decision History Tracking 修正良好")
        print("⚠️ 部分功能需要進一步改進")
        return True
    else:
        print("❌ EPL Decision History Tracking 仍需改進")
        print("🔧 建議檢查失敗的測試項目")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
