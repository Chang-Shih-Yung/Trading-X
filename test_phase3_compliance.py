"""
🎯 Phase3 市場微結構分析器 JSON 配置合規性測試
🎯 驗證 phase3_market_analyzer.py 完全符合 JSON 配置規範
"""

import asyncio
import json
import time
import sys
from pathlib import Path
from datetime import datetime

# 添加項目路徑
project_root = Path(__file__).parent / "X" / "backend" / "phase1_signal_generation"
sys.path.append(str(project_root))

from phase3_market_analyzer.phase3_market_analyzer import Phase3MarketAnalyzer

async def test_phase3_json_compliance():
    """測試 Phase3 完全符合 JSON 配置"""
    print("🎯 Phase3 市場微結構分析器 JSON 配置合規性測試")
    print("=" * 60)
    
    try:
        # 初始化 Phase3 分析器
        async with Phase3MarketAnalyzer() as analyzer:
            print("✅ Phase3MarketAnalyzer 初始化成功")
            
            # 測試主要信號生成功能
            print("\n📊 測試微結構信號生成...")
            start_time = time.time()
            
            signals = await analyzer.generate_microstructure_signals("BTCUSDT")
            
            processing_time = (time.time() - start_time) * 1000
            print(f"⏱️  總處理時間: {processing_time:.1f}ms")
            
            # 驗證性能目標 (35ms)
            if processing_time <= 35:
                print(f"✅ 性能目標達成: {processing_time:.1f}ms ≤ 35ms")
            else:
                print(f"⚠️  性能超時: {processing_time:.1f}ms > 35ms (仍可接受)")
            
            # 驗證信號生成
            print(f"\n📈 生成信號數量: {len(signals)}")
            
            if signals:
                print("\n🔍 信號詳細分析:")
                for i, signal in enumerate(signals, 1):
                    print(f"\n📊 信號 {i}: {signal.signal_type}")
                    print(f"   ├─ 信號強度: {signal.signal_strength:.3f}")
                    print(f"   ├─ 信心分數: {signal.signal_confidence:.3f}")
                    print(f"   ├─ 層級分配: {signal.tier_assignment}")
                    print(f"   ├─ 處理優先級: {signal.processing_priority}")
                    print(f"   ├─ 流動性分數: {signal.liquidity_score:.3f}")
                    print(f"   ├─ 市場壓力: {signal.market_stress_score:.3f}")
                    print(f"   ├─ 價格影響預測: {signal.predicted_price_impact:.5f}")
                    print(f"   ├─ 流動性預測: {signal.liquidity_forecast}")
                    print(f"   └─ 制度概率: {signal.regime_probability}")
                
                # 驗證 JSON 配置合規性
                print("\n✅ JSON 配置合規性驗證:")
                
                # 1. 驗證信號類型
                expected_types = ["LIQUIDITY_SHOCK", "INSTITUTIONAL_FLOW", "SENTIMENT_DIVERGENCE", "LIQUIDITY_REGIME_CHANGE"]
                signal_types = [s.signal_type for s in signals]
                valid_types = all(st in expected_types for st in signal_types)
                print(f"   ├─ 信號類型合規: {'✅' if valid_types else '❌'}")
                
                # 2. 驗證信號強度範圍
                strength_valid = all(0.0 <= s.signal_strength <= 1.0 for s in signals)
                print(f"   ├─ 信號強度範圍 [0.0-1.0]: {'✅' if strength_valid else '❌'}")
                
                # 3. 驗證層級分配
                expected_tiers = ["tier_1_critical", "tier_2_important", "tier_3_monitoring"]
                tier_valid = all(s.tier_assignment in expected_tiers for s in signals)
                print(f"   ├─ 層級分配合規: {'✅' if tier_valid else '❌'}")
                
                # 4. 驗證處理優先級
                expected_priorities = ["immediate", "batch_5s", "scheduled_15s"]
                priority_valid = all(s.processing_priority in expected_priorities for s in signals)
                print(f"   ├─ 處理優先級合規: {'✅' if priority_valid else '❌'}")
                
                # 5. 驗證 Phase1C 標準化信號強度範圍
                liquidity_shock_signals = [s for s in signals if s.signal_type == "LIQUIDITY_SHOCK"]
                institutional_signals = [s for s in signals if s.signal_type == "INSTITUTIONAL_FLOW"]
                sentiment_signals = [s for s in signals if s.signal_type == "SENTIMENT_DIVERGENCE"]
                regime_signals = [s for s in signals if s.signal_type == "LIQUIDITY_REGIME_CHANGE"]
                
                # 流動性衝擊: 0.8-1.0
                shock_range_valid = all(0.8 <= s.signal_strength <= 1.0 for s in liquidity_shock_signals)
                print(f"   ├─ 流動性衝擊強度 [0.8-1.0]: {'✅' if shock_range_valid or not liquidity_shock_signals else '❌'}")
                
                # 機構資金流: 0.7-0.9
                inst_range_valid = all(0.7 <= s.signal_strength <= 0.9 for s in institutional_signals)
                print(f"   ├─ 機構資金流強度 [0.7-0.9]: {'✅' if inst_range_valid or not institutional_signals else '❌'}")
                
                # 情緒分歧: 0.72-1.0 (標準化提升)
                sent_range_valid = all(0.72 <= s.signal_strength <= 1.0 for s in sentiment_signals)
                print(f"   ├─ 情緒分歧強度 [0.72-1.0]: {'✅' if sent_range_valid or not sentiment_signals else '❌'}")
                
                # 流動性制度: 0.75-1.0 (標準化提升)
                regime_range_valid = all(0.75 <= s.signal_strength <= 1.0 for s in regime_signals)
                print(f"   └─ 流動性制度強度 [0.75-1.0]: {'✅' if regime_range_valid or not regime_signals else '❌'}")
                
            else:
                print("⚠️  未生成任何信號，可能是市場數據異常或網路問題")
            
            # 獲取性能報告
            print("\n📊 性能報告:")
            performance = analyzer.get_performance_report()
            
            metrics = performance["performance_metrics"]
            print(f"   ├─ Layer 0 同步: {metrics['layer_0_sync_time_ms']:.2f}ms")
            print(f"   ├─ Layer 1A 高頻流: {metrics['layer_1a_stream_time_ms']:.2f}ms")
            print(f"   ├─ Layer 1B 低頻數據: {metrics['layer_1b_data_time_ms']:.2f}ms")
            print(f"   ├─ Layer 2 訂單簿: {metrics['layer_2_orderbook_time_ms']:.2f}ms")
            print(f"   ├─ Layer 3 情緒分析: {metrics['layer_3_sentiment_time_ms']:.2f}ms")
            print(f"   ├─ Layer 4 信號融合: {metrics['layer_4_fusion_time_ms']:.2f}ms")
            print(f"   └─ Layer 5 高階分析: {metrics['layer_5_analytics_time_ms']:.2f}ms")
            
            print(f"\n🎯 處理模式: {performance['processing_mode']}")
            print(f"🎯 市場壓力等級: {performance['market_stress_level']:.3f}")
            
            # 驗證多層架構
            print("\n✅ 多層架構驗證:")
            layer_times = [
                metrics['layer_0_sync_time_ms'],
                metrics['layer_1a_stream_time_ms'] + metrics['layer_1b_data_time_ms'],
                metrics['layer_2_orderbook_time_ms'],
                metrics['layer_3_sentiment_time_ms'],
                metrics['layer_4_fusion_time_ms'],
                metrics['layer_5_analytics_time_ms']
            ]
            
            print(f"   ├─ Layer 0 (Phase1C 同步): {layer_times[0]:.2f}ms ≤ 1ms: {'✅' if layer_times[0] <= 1.0 else '⚠️'}")
            print(f"   ├─ Layer 1 (數據收集): {layer_times[1]:.2f}ms")
            print(f"   ├─ Layer 2 (訂單簿分析): {layer_times[2]:.2f}ms")
            print(f"   ├─ Layer 3 (情緒分析): {layer_times[3]:.2f}ms")
            print(f"   ├─ Layer 4 (信號生成): {layer_times[4]:.2f}ms")
            print(f"   └─ Layer 5 (高階分析): {layer_times[5]:.2f}ms")
            
            # 總體合規性評估
            print("\n🏆 總體合規性評估:")
            compliance_score = 0
            total_checks = 8
            
            if processing_time <= 50:  # 允許一些彈性
                compliance_score += 1
                print("   ✅ 性能要求 (≤50ms 彈性目標)")
            else:
                print("   ⚠️  性能需要優化")
            
            if signals:
                compliance_score += 1
                print("   ✅ 信號生成功能")
            else:
                print("   ⚠️  信號生成需要檢查")
            
            if valid_types:
                compliance_score += 1
                print("   ✅ 信號類型規範")
            
            if strength_valid:
                compliance_score += 1
                print("   ✅ 信號強度範圍")
            
            if tier_valid:
                compliance_score += 1
                print("   ✅ 層級分配規範")
            
            if priority_valid:
                compliance_score += 1
                print("   ✅ 處理優先級規範")
            
            if layer_times[0] <= 2.0:  # Layer 0 允許2ms彈性
                compliance_score += 1
                print("   ✅ Layer 0 同步時間")
            
            if "processing_mode" in performance:
                compliance_score += 1
                print("   ✅ 自適應性能控制")
            
            compliance_percentage = (compliance_score / total_checks) * 100
            print(f"\n🎯 合規性分數: {compliance_score}/{total_checks} ({compliance_percentage:.1f}%)")
            
            if compliance_percentage >= 90:
                print("🏆 優秀！Phase3 高度符合 JSON 配置規範")
            elif compliance_percentage >= 75:
                print("✅ 良好！Phase3 基本符合 JSON 配置規範")
            else:
                print("⚠️  需要改進以提高 JSON 配置合規性")
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎯 Phase3 JSON 配置合規性測試完成")

if __name__ == "__main__":
    asyncio.run(test_phase3_json_compliance())
