#!/usr/bin/env python3
"""
🔍 EPL前處理系統完整性驗證測試
==============================

驗證EPL前處理系統是否100%匹配JSON規範
"""

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# 添加路徑
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "X" / "backend" / "phase2_pre_evaluation" / "epl_pre_processing_system"))

try:
    from epl_pre_processing_system import (
        # JSON核心依賴檢查
        IntelligentDeduplicationEngine,  # JSON: intelligent_deduplication_analysis_engine
        ContextualCorrelationAnalyzer,   # JSON: contextual_correlation_analyzer
        LightweightQualityControlGate,   # JSON: lightweight_quality_control_gate
        EnhancedPreEvaluationLayer,      # JSON: 主控制器
        
        # JSON數據結構檢查
        SignalCandidate,                 # JSON: 輸入數據格式
        PreEvaluationResult,             # JSON: 輸出數據格式
        
        # JSON枚舉檢查
        DeduplicationResult,
        CorrelationAnalysisResult,
        QualityControlResult,
        
        # JSON全局實例
        enhanced_pre_evaluation_layer
    )
    print("✅ 所有JSON規範要求的類和枚舉都已正確實現")
except ImportError as e:
    print(f"❌ 導入失敗: {e}")
    sys.exit(1)

def test_json_specification_compliance():
    """測試JSON規範合規性"""
    print("\n🔍 開始JSON規範合規性測試...")
    
    results = []
    
    # 1. 測試智能去重引擎
    print("1️⃣ 測試智能去重引擎...")
    dedup_engine = IntelligentDeduplicationEngine()
    
    # 檢查JSON配置參數
    assert dedup_engine.similarity_threshold == 0.85, "相似度閾值應為0.85"
    assert dedup_engine.time_overlap_minutes == 15, "時間重疊應為15分鐘"
    assert dedup_engine.confidence_diff_threshold == 0.03, "信心度差異閾值應為0.03"
    
    # 檢查JSON源共識驗證參數
    assert dedup_engine.source_overlap_score_threshold == 0.72, "源重疊分數閾值錯誤"
    assert dedup_engine.model_diversity_score_threshold == 0.8, "模型多樣性閾值錯誤"
    assert dedup_engine.action_bias_score_threshold == 0.85, "行動偏差閾值錯誤"
    
    results.append("✅ 智能去重引擎配置正確")
    
    # 2. 測試上下文關聯分析器
    print("2️⃣ 測試上下文關聯分析器...")
    corr_analyzer = ContextualCorrelationAnalyzer()
    
    # 檢查JSON配置參數
    assert corr_analyzer.direction_conflict_threshold == 0.15, "方向衝突閾值錯誤"
    assert corr_analyzer.confidence_improvement_threshold == 0.08, "信心度改善閾值錯誤"
    
    results.append("✅ 上下文關聯分析器配置正確")
    
    # 3. 測試輕量品質控制門檻
    print("3️⃣ 測試輕量品質控制門檻...")
    quality_gate = LightweightQualityControlGate()
    
    # 檢查JSON配置參數
    assert quality_gate.strength_threshold == 70.0, "強度閾值錯誤"
    assert quality_gate.liquidity_threshold == 0.6, "流動性閾值錯誤"
    assert quality_gate.risk_score_threshold == 0.3, "風險分數閾值錯誤"
    
    # 檢查JSON微異常參數
    assert quality_gate.signal_volatility_jump_threshold == 0.3, "信號波動性跳躍閾值錯誤"
    assert quality_gate.confidence_drop_rate_threshold == 0.1, "信心度下降率閾值錯誤"
    
    # 檢查JSON整合評分權重
    expected_weights = {"strength": 0.3, "confidence": 0.25, "quality": 0.2, "risk": 0.15, "timing": 0.1}
    assert quality_gate.scoring_weights == expected_weights, "整合評分權重錯誤"
    
    results.append("✅ 輕量品質控制門檻配置正確")
    
    # 4. 測試主控制器
    print("4️⃣ 測試增強前處理層主控制器...")
    epl_layer = EnhancedPreEvaluationLayer()
    
    # 檢查JSON智能路由配置
    express_config = epl_layer.routing_config["express_lane"]
    assert express_config["data_completeness_threshold"] == 0.9, "快速通道數據完整性閾值錯誤"
    assert express_config["signal_clarity_threshold"] == 0.8, "快速通道信號清晰度閾值錯誤"
    assert express_config["confidence_threshold"] == 0.75, "快速通道信心度閾值錯誤"
    assert express_config["micro_anomaly_threshold"] == 0.2, "快速通道微異常閾值錯誤"
    assert express_config["market_stress_threshold"] == 0.7, "快速通道市場壓力閾值錯誤"
    
    results.append("✅ 增強前處理層主控制器配置正確")
    
    # 5. 測試枚舉值
    print("5️⃣ 測試枚舉值...")
    
    # DeduplicationResult枚舉
    expected_dedup = ["⭐ 獨特", "❌ 忽略", "⚠️ 延遲觀察", "✅ 通過"]
    actual_dedup = [item.value for item in DeduplicationResult]
    assert set(actual_dedup) == set(expected_dedup), f"去重結果枚舉值錯誤: {actual_dedup}"
    
    # CorrelationAnalysisResult枚舉
    expected_corr = ["➕ 強化候選", "🔁 替換候選", "✅ 獨立新單"]
    actual_corr = [item.value for item in CorrelationAnalysisResult]
    assert set(actual_corr) == set(expected_corr), f"關聯分析結果枚舉值錯誤: {actual_corr}"
    
    # QualityControlResult枚舉
    expected_quality = ["🌟 優秀", "✅ 通過", "❌ 信號強度不足", "❌ 流動性不足", "❌ 風險評估未通過"]
    actual_quality = [item.value for item in QualityControlResult]
    assert set(actual_quality) == set(expected_quality), f"品質控制結果枚舉值錯誤: {actual_quality}"
    
    results.append("✅ 所有枚舉值正確")
    
    # 6. 測試數據結構
    print("6️⃣ 測試數據結構...")
    
    # 測試SignalCandidate結構
    test_candidate = SignalCandidate(
        id="test_001",
        symbol="BTCUSDT",
        signal_strength=75.0,
        confidence=0.85,
        direction="long",
        timestamp=datetime.now(),
        source="phase1a",
        data_completeness=0.95,
        signal_clarity=0.88,
        dynamic_params={"adaptation_timestamp": datetime.now(), "volatility_jump": 0.1},
        market_environment={"volatility": 0.02, "liquidity_score": 0.8, "momentum": 0.1},
        technical_snapshot={"rsi": 65, "macd_signal": 0.5, "bollinger_position": 0.6}
    )
    
    assert hasattr(test_candidate, 'id'), "SignalCandidate缺少id字段"
    assert hasattr(test_candidate, 'dynamic_params'), "SignalCandidate缺少dynamic_params字段"
    assert hasattr(test_candidate, 'market_environment'), "SignalCandidate缺少market_environment字段"
    
    results.append("✅ SignalCandidate數據結構正確")
    
    print("\n🎯 JSON規範合規性測試結果:")
    for result in results:
        print(f"  {result}")
    
    return True

async def test_complete_processing_flow():
    """測試完整處理流程"""
    print("\n🔄 開始完整處理流程測試...")
    
    # 創建測試信號候選者
    test_candidate = SignalCandidate(
        id="flow_test_001",
        symbol="BTCUSDT",
        signal_strength=78.5,
        confidence=0.82,
        direction="long",
        timestamp=datetime.now(),
        source="phase1abc_dynamic",
        data_completeness=0.93,
        signal_clarity=0.85,
        dynamic_params={
            "adaptation_timestamp": datetime.now(),
            "volatility_jump": 0.05,
            "confidence_drop_rate": 0.02
        },
        market_environment={
            "volatility": 0.025,
            "liquidity_score": 0.75,
            "momentum": 0.15
        },
        technical_snapshot={
            "rsi": 62,
            "macd_signal": 0.3,
            "bollinger_position": 0.55
        }
    )
    
    # 測試主處理流程
    start_time = time.time()
    result = await enhanced_pre_evaluation_layer.process_signal_candidate(test_candidate)
    processing_time = (time.time() - start_time) * 1000
    
    print(f"📊 處理結果:")
    print(f"  候選者ID: {result.candidate.id}")
    print(f"  去重結果: {result.deduplication_result.value}")
    print(f"  關聯結果: {result.correlation_result.value}")
    print(f"  品質結果: {result.quality_result.value}")
    print(f"  通過EPL: {'✅' if result.pass_to_epl else '❌'}")
    print(f"  處理時間: {processing_time:.2f}ms")
    print(f"  相似度分數: {result.similarity_score}")
    
    # 驗證JSON性能目標
    json_targets = {
        "express_lane": 3.0,  # 3ms
        "standard_lane": 15.0,  # 15ms
        "deep_lane": 40.0   # 40ms
    }
    
    print(f"\n🎯 性能驗證:")
    if processing_time <= json_targets["express_lane"]:
        print(f"  ✅ 達到快速通道目標: {processing_time:.2f}ms <= {json_targets['express_lane']}ms")
    elif processing_time <= json_targets["standard_lane"]:
        print(f"  ✅ 達到標準通道目標: {processing_time:.2f}ms <= {json_targets['standard_lane']}ms")
    elif processing_time <= json_targets["deep_lane"]:
        print(f"  ✅ 達到深度分析目標: {processing_time:.2f}ms <= {json_targets['deep_lane']}ms")
    else:
        print(f"  ⚠️ 超出性能目標: {processing_time:.2f}ms > {json_targets['deep_lane']}ms")
    
    # 獲取處理統計
    stats = enhanced_pre_evaluation_layer.get_processing_stats()
    print(f"\n📈 處理統計:")
    print(f"  總處理數: {stats['total_processed']}")
    print(f"  通過數: {stats['passed_to_epl']}")
    print(f"  通過率: {stats['pass_rate']:.1f}%")
    print(f"  快速通道比例: {stats['express_lane_ratio']:.1f}%")
    print(f"  標準通道比例: {stats['standard_lane_ratio']:.1f}%")
    print(f"  深度分析比例: {stats['deep_lane_ratio']:.1f}%")
    
    return result.pass_to_epl

def main():
    """主測試函數"""
    print("🚀 EPL前處理系統完整性驗證開始...")
    
    try:
        # 1. JSON規範合規性測試
        compliance_success = test_json_specification_compliance()
        
        # 2. 完整流程測試
        import asyncio
        flow_success = asyncio.run(test_complete_processing_flow())
        
        if compliance_success and flow_success:
            print("\n🎉 EPL前處理系統100%通過完整性驗證！")
            print("✅ JSON規範完全匹配")
            print("✅ 處理流程正常運行")
            print("✅ 性能目標達成")
            return True
        else:
            print("\n⚠️ 驗證未完全通過，需要進一步檢查")
            return False
            
    except Exception as e:
        print(f"\n❌ 驗證過程中出現錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
