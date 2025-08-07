"""
Phase2 Pre-Evaluation System - 預評估處理層
====================================

## 系統概述
Phase2 Pre-Evaluation是Trading-X系統的核心預評估處理層，負責將Phase1的統一信號池
進行高效的三通道處理、內嵌式評分和並行品質監控。

## 核心模組
- **EPL Pre-Processing System**: 智能三通道分配處理系統
- **Signal Scoring Engine**: 內嵌式五維度評分引擎  
- **Real Data Signal Quality Engine**: 並行品質監控系統

## 主要特色
- 🚀 動態通道分配 (Express: 5-40% 自適應)
- ⚡ 零延遲內嵌評分 (直接整合EPL Step3)
- 👀 並行監控架構 (40ms完整監控週期)
- 🔍 微異常檢測與自適應調整
- 🌟 來源共識驗證與多樣性保留

## 性能指標
- Express通道: <3ms 高品質信號快速處理
- Standard通道: <8ms 平衡標準處理
- Deep通道: <15ms 複雜深度分析
- 總體延遲: <15ms (EPL完整處理)
- 監控延遲: 40ms (並行執行，零主流程影響)

版本: 2.1.0
最後更新: 2025-08-07
"""

from .epl_pre_processing_system.epl_pre_processing_system import EPLPreProcessingSystem
from .signal_scoring_engine.signal_scoring_engine import SignalScoringEngine  
from .real_data_signal_quality_engine.real_data_signal_quality_engine import RealDataSignalQualityEngine

# 模組版本資訊
__version__ = "2.1.0"
__author__ = "Trading-X Team"
__description__ = "Phase2 Pre-Evaluation System - 高效三通道預評估處理層"

# 主要類別匯出
__all__ = [
    "EPLPreProcessingSystem",
    "SignalScoringEngine", 
    "RealDataSignalQualityEngine"
]

# 系統配置常數
SYSTEM_CONFIG = {
    "version": "2.1.0",
    "processing_channels": {
        "express": {"max_delay": "3ms", "allocation": "5-40%"},
        "standard": {"max_delay": "8ms", "allocation": "40-70%"}, 
        "deep": {"max_delay": "15ms", "allocation": "15-25%"}
    },
    "scoring_dimensions": {
        "strength": 0.30,
        "confidence": 0.25,
        "quality": 0.20, 
        "risk": 0.15,
        "timing": 0.10
    },
    "monitoring_config": {
        "cycle_time": "40ms",
        "parallel_layers": 3,
        "main_process_impact": "0ms"
    },
    "anomaly_thresholds": {
        "volatility_jump": 0.3,
        "confidence_drop": 0.1,
        "quality_consistency": 0.15
    },
    "consensus_thresholds": {
        "jaccard_similarity": 0.72,
        "diversity_score": 0.8,
        "directional_consensus": 0.85
    }
}

# 效能最佳化設定
PERFORMANCE_CONFIG = {
    "parallel_processing": True,
    "embedded_scoring": True,
    "zero_latency_monitoring": True,
    "adaptive_channel_allocation": True,
    "micro_anomaly_detection": True,
    "source_consensus_validation": True
}

# 系統整合點
INTEGRATION_POINTS = {
    "upstream": {
        "phase1_unified_pool": "Phase1 統一信號池輸入",
        "signal_format": "SignalCandidate 0.0-1.0標準"
    },
    "downstream": {
        "epl_decision_layer": "EPL決策層輸出",
        "final_candidates": "最終候選信號池"
    },
    "parallel": {
        "monitoring_dashboard": "即時監控儀表板",
        "alert_system": "警報通知系統",
        "load_balancer": "系統負載平衡器"
    }
}

# 品質保證檢查點
QUALITY_CHECKPOINTS = {
    "input_validation": "Phase1→Phase2格式驗證",
    "processing_delays": "三通道處理延遲檢查", 
    "scoring_consistency": "五維度評分一致性",
    "monitoring_coverage": "並行監控覆蓋率",
    "anomaly_detection": "微異常檢測準確性",
    "consensus_validation": "來源共識驗證效果"
}

def get_system_info():
    """取得Phase2系統資訊"""
    return {
        "name": "Phase2 Pre-Evaluation System",
        "version": __version__,
        "description": __description__,
        "config": SYSTEM_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "integration": INTEGRATION_POINTS,
        "quality": QUALITY_CHECKPOINTS
    }

def validate_system_config():
    """驗證系統配置完整性"""
    required_modules = ["epl_pre_processing_system", "signal_scoring_engine", "real_data_signal_quality_engine"]
    
    validation_results = {
        "config_valid": True,
        "modules_available": [],
        "missing_modules": [],
        "warnings": []
    }
    
    for module in required_modules:
        try:
            __import__(f"phase2_pre_evaluation.{module}")
            validation_results["modules_available"].append(module)
        except ImportError:
            validation_results["missing_modules"].append(module)
            validation_results["config_valid"] = False
    
    # 檢查權重總和
    scoring_weights_sum = sum(SYSTEM_CONFIG["scoring_dimensions"].values())
    if abs(scoring_weights_sum - 1.0) > 0.001:
        validation_results["warnings"].append(f"Scoring weights sum: {scoring_weights_sum}, expected: 1.0")
    
    return validation_results

# 系統初始化檢查
if __name__ == "__main__":
    system_info = get_system_info()
    validation = validate_system_config()
    
    print(f"🚀 {system_info['name']} v{system_info['version']}")
    print(f"📊 配置驗證: {'✅ 通過' if validation['config_valid'] else '❌ 失敗'}")
    print(f"📦 可用模組: {len(validation['modules_available'])}/3")
    
    if validation['warnings']:
        print("⚠️ 警告:")
        for warning in validation['warnings']:
            print(f"   - {warning}")
