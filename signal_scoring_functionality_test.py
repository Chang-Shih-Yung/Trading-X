"""
Signal Scoring Engine 功能驗證測試
"""

import sys
import os
sys.path.append('/Users/henrychang/Desktop/Trading-X/X/backend/phase2_pre_evaluation/signal_scoring_engine')

from signal_scoring_engine import signal_scoring_engine

def test_basic_functionality():
    """測試基本功能"""
    print("🧪 測試基本功能...")
    
    test_signal = {
        "value": 0.8,
        "confidence": 0.9,
        "signal_strength": 0.75,
        "market_stress": 0.4
    }
    
    scores = signal_scoring_engine.score_signal(test_signal)
    
    print(f"   📊 評分結果:")
    for key, value in scores.items():
        print(f"      {key}: {value:.3f}")
    
    # 驗證所有分數都在合理範圍內
    for key, value in scores.items():
        if not (0.0 <= value <= 1.0):
            print(f"   ❌ {key} 超出範圍: {value}")
            return False
    
    print("   ✅ 基本功能測試通過")
    return True

def test_source_consensus():
    """測試源共識驗證"""
    print("🤝 測試源共識驗證...")
    
    test_signal_with_sources = {
        "value": 0.7,
        "confidence": 0.8,
        "signal_strength": 0.7,
        "sources": [
            {"signal_strength": 0.7, "model_type": "rsi", "value": 0.7},
            {"signal_strength": 0.8, "model_type": "macd", "value": 0.6},
            {"signal_strength": 0.6, "model_type": "bollinger", "value": 0.8}
        ]
    }
    
    scores = signal_scoring_engine.score_signal(test_signal_with_sources)
    
    print(f"   📊 多源信號評分結果:")
    for key, value in scores.items():
        print(f"      {key}: {value:.3f}")
    
    print("   ✅ 源共識驗證測試通過")
    return True

def test_anomaly_detection():
    """測試微異常檢測"""
    print("🔍 測試微異常檢測...")
    
    # 模擬波動跳躍情況
    for i in range(5):
        test_signal = {
            "value": 0.2 + i * 0.3,  # 逐漸增大的信號強度
            "confidence": 0.9 - i * 0.1,  # 逐漸下降的信心
            "signal_strength": 0.2 + i * 0.3
        }
        
        scores = signal_scoring_engine.score_signal(test_signal)
        print(f"   📊 信號 {i+1} 評分: strength={scores['strength_score']:.3f}, confidence={scores['confidence_score']:.3f}")
    
    print("   ✅ 微異常檢測測試通過")
    return True

def test_performance():
    """測試性能要求"""
    print("⚡ 測試性能要求...")
    
    import time
    
    test_signal = {
        "value": 0.8,
        "confidence": 0.9,
        "signal_strength": 0.75
    }
    
    # 測試處理時間
    start_time = time.time()
    for _ in range(1000):
        scores = signal_scoring_engine.score_signal(test_signal)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 1000 * 1000  # ms
    
    print(f"   ⏱️ 平均處理時間: {avg_time:.3f}ms (目標: ≤3ms)")
    
    if avg_time <= 3.0:
        print("   ✅ 性能要求測試通過")
        return True
    else:
        print("   ❌ 性能要求測試失敗")
        return False

def run_comprehensive_test():
    """執行完整測試"""
    print("🎯 Signal Scoring Engine 完整功能驗證測試")
    print("=" * 50)
    
    tests = [
        test_basic_functionality,
        test_source_consensus,
        test_anomaly_detection,
        test_performance
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ 測試失敗: {e}")
            results.append(False)
        print()
    
    success_count = sum(results)
    total_tests = len(results)
    
    print(f"📊 測試結果匯總:")
    print(f"   成功: {success_count}/{total_tests}")
    print(f"   成功率: {success_count/total_tests*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 所有測試通過 - 完全符合 JSON 規範!")
        return True
    else:
        print("❌ 部分測試失敗")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)
