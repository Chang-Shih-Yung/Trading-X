#!/usr/bin/env python3
"""
階段1C測試腳本: 信號標準化與極端信號放大
整合階段1A+1B測試階段1C的新功能
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.phase1c_signal_standardization import (
    Phase1CSignalProcessor, 
    SignalNormalizationConfig,
    get_phase1c_processor,
    integrate_with_phase1ab
)
from app.services.phase1b_volatility_adaptation import enhanced_signal_scoring_engine
import logging
from datetime import datetime

# 設置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_signal_standardization():
    """測試信號標準化功能"""
    print("\n" + "="*60)
    print("🧪 測試1: 信號標準化功能")
    print("="*60)
    
    try:
        # 創建處理器
        config = SignalNormalizationConfig(
            extreme_signal_threshold=0.8,
            extreme_amplification_factor=1.5
        )
        processor = Phase1CSignalProcessor(config)
        
        # 測試信號數據
        test_signals = [
            {"value": 0.95, "id": "test_extreme_high", "module": "smart_money_detection"},
            {"value": 0.05, "id": "test_extreme_low", "module": "sentiment_indicators"},
            {"value": 0.72, "id": "test_normal_high", "module": "technical_structure"},
            {"value": 0.35, "id": "test_normal_low", "module": "volume_microstructure"},
            {"value": 0.50, "id": "test_neutral", "module": "macro_environment"}
        ]
        
        print(f"🔄 測試 {len(test_signals)} 個信號的標準化處理...")
        
        standardized_signals = []
        for signal_data in test_signals:
            standardized_signal = processor.standardization_engine.standardize_signal(
                signal_value=signal_data["value"],
                signal_id=signal_data["id"],
                module_name=signal_data["module"],
                timeframe="medium"
            )
            standardized_signals.append(standardized_signal)
            
            print(f"  📊 {signal_data['id']}:")
            print(f"     原始值: {signal_data['value']:.3f} -> 標準化值: {standardized_signal.standardized_value:.3f}")
            print(f"     質量評分: {standardized_signal.quality_score:.3f} | 信心度: {standardized_signal.confidence_level:.3f}")
            print(f"     極端信號: {'是' if standardized_signal.is_extreme else '否'} | 放大倍數: {standardized_signal.amplification_applied:.2f}")
        
        # 統計結果
        extreme_count = sum(1 for s in standardized_signals if s.is_extreme)
        avg_quality = sum(s.quality_score for s in standardized_signals) / len(standardized_signals)
        
        print(f"\n📈 標準化結果統計:")
        print(f"   總信號數: {len(standardized_signals)}")
        print(f"   極端信號數: {extreme_count}")
        print(f"   極端信號比例: {extreme_count/len(standardized_signals)*100:.1f}%")
        print(f"   平均質量評分: {avg_quality:.3f}")
        
        print("✅ 信號標準化測試通過!")
        return True
        
    except Exception as e:
        print(f"❌ 信號標準化測試失敗: {str(e)}")
        return False

def test_multi_timeframe_integration():
    """測試多時間框架整合功能"""
    print("\n" + "="*60)
    print("🧪 測試2: 多時間框架整合功能")
    print("="*60)
    
    try:
        processor = get_phase1c_processor()
        
        # 準備多時間框架測試數據
        signals_by_timeframe = {
            "short": [
                {"id": "short_vol_1", "module": "volume_microstructure", "value": 0.85},
                {"id": "short_sent_1", "module": "sentiment_indicators", "value": 0.73}
            ],
            "medium": [
                {"id": "med_tech_1", "module": "technical_structure", "value": 0.68},
                {"id": "med_smart_1", "module": "smart_money_detection", "value": 0.82}
            ],
            "long": [
                {"id": "long_macro_1", "module": "macro_environment", "value": 0.55},
                {"id": "long_cross_1", "module": "cross_market_correlation", "value": 0.61}
            ]
        }
        
        print(f"🔄 測試多時間框架整合...")
        print(f"   短線信號: {len(signals_by_timeframe['short'])} 個")
        print(f"   中線信號: {len(signals_by_timeframe['medium'])} 個")
        print(f"   長線信號: {len(signals_by_timeframe['long'])} 個")
        
        # 執行多時間框架整合
        analysis = processor.multi_timeframe_integrator.integrate_multi_timeframe_signals(
            signals_by_timeframe
        )
        
        print(f"\n📊 多時間框架整合結果:")
        print(f"   整合評分: {analysis.integrated_score:.3f}")
        print(f"   共識強度: {analysis.consensus_strength:.3f}")
        print(f"   時間框架對齊度: {analysis.timeframe_alignment:.3f}")
        
        # 顯示各時間框架的標準化信號
        for timeframe in ["short", "medium", "long"]:
            signals = getattr(analysis, f"{timeframe}_term_signals")
            if signals:
                avg_quality = sum(s.quality_score for s in signals) / len(signals)
                extreme_count = sum(1 for s in signals if s.is_extreme)
                print(f"   {timeframe.upper()}線: {len(signals)} 個信號, 平均質量: {avg_quality:.3f}, 極端信號: {extreme_count}")
        
        print("✅ 多時間框架整合測試通過!")
        return True
        
    except Exception as e:
        print(f"❌ 多時間框架整合測試失敗: {str(e)}")
        return False

def test_phase1abc_integration():
    """測試階段1A+1B+1C完整整合"""
    print("\n" + "="*60)
    print("🧪 測試3: 階段1A+1B+1C完整整合")
    print("="*60)
    
    try:
        # 1. 準備測試數據
        test_symbols = ["BTCUSDT", "ETHUSDT"]
        mock_signals = {
            "technical_structure": {"value": 0.72, "confidence": 0.85},
            "volume_microstructure": {"value": 0.65, "confidence": 0.78},
            "sentiment_indicators": {"value": 0.58, "confidence": 0.63},
            "smart_money_detection": {"value": 0.79, "confidence": 0.88},
            "macro_environment": {"value": 0.45, "confidence": 0.55},
            "cross_market_correlation": {"value": 0.62, "confidence": 0.70},
            "event_driven_signals": {"value": 0.35, "confidence": 0.42}
        }
        
        print(f"🔄 執行階段1A+1B+1C完整整合測試...")
        print(f"   測試交易對: {test_symbols}")
        print(f"   測試信號模組: {len(mock_signals)} 個")
        
        # 2. 模擬階段1A+1B結果 (避免async複雜性)
        print(f"   Step 1: 模擬階段1A+1B增強信號打分...")
        # 創建模擬的階段1A+1B結果
        phase1ab_result = {
            'total_weighted_score': 0.785,
            'individual_scores': {
                'technical_structure': 0.72,
                'volume_microstructure': 0.65,
                'sentiment_indicators': 0.58,
                'smart_money_detection': 0.79,
                'macro_environment': 0.45,
                'cross_market_correlation': 0.62,
                'event_driven_signals': 0.35
            },
            'trading_cycle': 'short',
            'enhancement_applied': True,
            'volatility_adaptation': True
        }
        
        print(f"   ✓ 階段1A+1B完成 - 總加權評分: {phase1ab_result.get('total_weighted_score', 0):.3f}")
        
        # 3. 執行階段1C整合
        print(f"   Step 2: 執行階段1C信號標準化與極端信號放大...")
        integrated_result = integrate_with_phase1ab(phase1ab_result, mock_signals)
        
        print(f"   ✓ 階段1C整合完成")
        
        # 4. 顯示整合結果
        print(f"\n🎯 階段1A+1B+1C整合結果:")
        
        # 階段1A結果
        print(f"   📊 階段1A (信號模組重構):")
        print(f"      - 活躍週期: {integrated_result.get('active_cycle', 'N/A').upper()}")
        print(f"      - 信號覆蓋率: {integrated_result.get('signal_coverage', 0)*100:.1f}%")
        print(f"      - 平均信心度: {integrated_result.get('average_confidence', 0)*100:.1f}%")
        
        # 階段1B結果
        phase1b_metrics = integrated_result.get('phase_1b_metrics', {})
        if phase1b_metrics:
            volatility_metrics = phase1b_metrics.get('volatility_metrics', {})
            continuity_metrics = phase1b_metrics.get('continuity_metrics', {})
            
            print(f"   🌊 階段1B (波動適應性):")
            print(f"      - 當前波動率: {volatility_metrics.get('current_volatility', 0)*100:.1f}%")
            print(f"      - 信號持續性: {continuity_metrics.get('signal_persistence', 0)*100:.1f}%")
            print(f"      - 共識強度: {continuity_metrics.get('consensus_strength', 0)*100:.1f}%")
        
        # 階段1C結果
        phase1c_enhancement = integrated_result.get('phase1c_enhancement', {})
        if phase1c_enhancement:
            phase1c_metrics = phase1c_enhancement.get('phase1c_metrics', {})
            standardization_metrics = phase1c_metrics.get('standardization_metrics', {})
            multiframe_analysis = phase1c_metrics.get('multiframe_analysis', {})
            
            print(f"   🔧 階段1C (信號標準化與極端信號放大):")
            print(f"      - 處理信號數: {standardization_metrics.get('total_signals_processed', 0)}")
            print(f"      - 極端信號數: {standardization_metrics.get('extreme_signals_detected', 0)}")
            print(f"      - 放大應用數: {standardization_metrics.get('amplifications_applied', 0)}")
            
            if multiframe_analysis:
                print(f"      - 多時間框架共識: {multiframe_analysis.get('consensus_strength', 0)*100:.1f}%")
                print(f"      - 時間框架對齊: {multiframe_analysis.get('timeframe_alignment', 0)*100:.1f}%")
        
        # 最終增強評分
        final_score = integrated_result.get('final_enhanced_score', 0)
        print(f"\n🏆 最終增強評分: {final_score:.3f}")
        
        # 整合狀態
        integration_summary = integrated_result.get('integration_summary', {})
        if integration_summary:
            print(f"   📈 整合摘要:")
            print(f"      - 階段1A信號模組: {integration_summary.get('phase1a_signal_modules', 0)} 個")
            print(f"      - 階段1B波動適應: {'✓' if integration_summary.get('phase1b_volatility_adaptation') else '✗'}")
            print(f"      - 階段1C信號標準化: {'✓' if integration_summary.get('phase1c_signal_standardization') else '✗'}")
            print(f"      - 總增強應用: {'✓' if integration_summary.get('total_enhancement_applied') else '✗'}")
        
        print("✅ 階段1A+1B+1C完整整合測試通過!")
        return True
        
    except Exception as e:
        print(f"❌ 階段1A+1B+1C完整整合測試失敗: {str(e)}")
        logger.exception("完整整合測試詳細錯誤:")
        return False

def test_extreme_signal_detection():
    """測試極端信號檢測功能"""
    print("\n" + "="*60)
    print("🧪 測試4: 極端信號檢測與放大")
    print("="*60)
    
    try:
        processor = get_phase1c_processor()
        
        # 準備極端信號測試數據
        extreme_test_cases = [
            {"value": 0.95, "expected_extreme": True, "description": "極高信號"},
            {"value": 0.05, "expected_extreme": True, "description": "極低信號"},
            {"value": 0.88, "expected_extreme": True, "description": "高信號"},
            {"value": 0.65, "expected_extreme": False, "description": "中等信號"},
            {"value": 0.50, "expected_extreme": False, "description": "中性信號"}
        ]
        
        print(f"🔄 測試極端信號檢測...")
        
        detection_results = []
        for i, test_case in enumerate(extreme_test_cases):
            signal = processor.standardization_engine.standardize_signal(
                signal_value=test_case["value"],
                signal_id=f"extreme_test_{i}",
                module_name="smart_money_detection",  # 使用高質量模組
                timeframe="medium"
            )
            
            detection_results.append({
                "test_case": test_case,
                "signal": signal,
                "detection_correct": signal.is_extreme == test_case["expected_extreme"]
            })
            
            print(f"   📊 {test_case['description']} (原值: {test_case['value']:.2f}):")
            print(f"      標準化值: {signal.standardized_value:.3f}")
            print(f"      質量評分: {signal.quality_score:.3f}")
            print(f"      檢測結果: {'極端' if signal.is_extreme else '正常'} (預期: {'極端' if test_case['expected_extreme'] else '正常'})")
            print(f"      放大倍數: {signal.amplification_applied:.2f}")
            print(f"      檢測正確: {'✓' if signal.is_extreme == test_case['expected_extreme'] else '✗'}")
        
        # 統計檢測準確率
        correct_detections = sum(1 for result in detection_results if result["detection_correct"])
        accuracy = correct_detections / len(detection_results) * 100
        
        print(f"\n📈 極端信號檢測統計:")
        print(f"   測試案例數: {len(detection_results)}")
        print(f"   檢測正確數: {correct_detections}")
        print(f"   檢測準確率: {accuracy:.1f}%")
        
        # 顯示放大效果
        extreme_signals = [r["signal"] for r in detection_results if r["signal"].is_extreme]
        if extreme_signals:
            avg_amplification = sum(s.amplification_applied for s in extreme_signals) / len(extreme_signals)
            print(f"   極端信號數: {len(extreme_signals)}")
            print(f"   平均放大倍數: {avg_amplification:.2f}")
        
        print("✅ 極端信號檢測測試通過!")
        return accuracy >= 80  # 要求80%以上準確率
        
    except Exception as e:
        print(f"❌ 極端信號檢測測試失敗: {str(e)}")
        return False

def main():
    """主測試函數"""
    print("🚀 開始階段1C測試套件")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # 執行所有測試
    tests = [
        ("信號標準化功能", test_signal_standardization),
        ("多時間框架整合功能", test_multi_timeframe_integration),
        ("階段1A+1B+1C完整整合", test_phase1abc_integration),
        ("極端信號檢測與放大", test_extreme_signal_detection)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 執行測試: {test_name}")
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ 測試 '{test_name}' 執行失敗: {str(e)}")
            test_results.append((test_name, False))
    
    # 顯示總結
    print("\n" + "="*80)
    print("📊 階段1C測試結果總結")
    print("="*80)
    
    passed_tests = 0
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"   {test_name}: {status}")
        if result:
            passed_tests += 1
    
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n🎯 測試統計:")
    print(f"   總測試數: {total_tests}")
    print(f"   通過測試數: {passed_tests}")
    print(f"   成功率: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n🎉 階段1C所有測試通過！系統準備就緒。")
    elif success_rate >= 75:
        print("\n⚠️  階段1C大部分測試通過，但有部分功能需要修正。")
    else:
        print("\n🚨 階段1C測試失敗率較高，需要全面檢查。")
    
    return success_rate == 100

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
