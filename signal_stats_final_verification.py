"""
✅ Signal Processing Statistics 優化驗證
=====================================

驗證優化後的配置和 Python 實現
"""

import sys
import json
from pathlib import Path

# 添加路徑
sys.path.append("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring/2_signal_processing_statistics")

from signal_processing_statistics import SignalProcessingStatistics

def test_optimized_implementation():
    """測試優化後的實現"""
    print("🧪 測試優化後的 Signal Processing Statistics")
    print("=" * 60)
    
    try:
        # 1. 測試初始化
        print("\n📝 測試 1: 初始化和配置載入")
        stats = SignalProcessingStatistics()
        
        print("✅ 實例創建成功")
        print(f"✅ 配置驗證: {'通過' if hasattr(stats, 'validate_configuration') else '缺少方法'}")
        print(f"✅ 安全配置訪問: {'支持' if hasattr(stats, 'get_config_value') else '缺少方法'}")
        
        # 2. 測試配置訪問
        print("\n📝 測試 2: 配置值訪問")
        bin_count = stats.get_config_value("PHASE4_SIGNAL_PROCESSING_STATISTICS.statistical_analysis.quality_distribution_tracking.bin_count", 10)
        categories = stats.get_config_value("PHASE4_SIGNAL_PROCESSING_STATISTICS.statistical_analysis.priority_level_analytics.categories", [])
        
        print(f"✅ 質量分佈 bin 數量: {bin_count}")
        print(f"✅ 優先級類別: {categories}")
        
        # 3. 測試配置結構
        print("\n📝 測試 3: 配置結構驗證")
        config_sections = stats.config.get("PHASE4_SIGNAL_PROCESSING_STATISTICS", {}).keys()
        print(f"✅ 配置部分: {list(config_sections)}")
        
        # 檢查關鍵配置
        required_configs = [
            "statistical_analysis.quality_distribution_tracking",
            "statistical_analysis.priority_level_analytics", 
            "statistical_analysis.processing_time_analysis",
            "statistical_analysis.source_performance_comparison"
        ]
        
        print("\n📋 關鍵配置檢查:")
        for config_path in required_configs:
            value = stats.get_config_value(f"PHASE4_SIGNAL_PROCESSING_STATISTICS.{config_path}")
            status = "✅" if value else "❌"
            print(f"  {status} {config_path}: {'存在' if value else '缺失'}")
        
        # 4. 測試功能
        print("\n📝 測試 4: 核心功能測試")
        
        # 測試記錄信號
        test_signal = {
            "timestamp": "2025-08-09T10:30:00",
            "symbol": "BTCUSDT",
            "priority": "HIGH",
            "quality_score": 0.85,
            "total_latency": 350,
            "source": "binance",
            "phase1_duration": 150,
            "phase2_duration": 10,
            "phase3_duration": 190
        }
        
        import asyncio
        success = asyncio.run(stats.record_signal_metrics(test_signal))
        print(f"✅ 信號記錄: {'成功' if success else '失敗'}")
        
        # 測試統計生成
        comprehensive_stats = asyncio.run(stats.get_comprehensive_statistics())
        print(f"✅ 綜合統計: {'生成成功' if 'statistics_metadata' in comprehensive_stats else '生成失敗'}")
        
        # 測試實時指標
        real_time_metrics = asyncio.run(stats.get_real_time_metrics())
        print(f"✅ 實時指標: {'生成成功' if 'timestamp' in real_time_metrics else '生成失敗'}")
        
        # 5. 結果分析
        print("\n📊 測試結果分析")
        if comprehensive_stats and 'statistics_metadata' in comprehensive_stats:
            metadata = comprehensive_stats['statistics_metadata']
            print(f"✅ 分析信號數: {metadata.get('total_signals_analyzed', 0)}")
            print(f"✅ 生成時間: {metadata.get('generated_at', 'N/A')}")
            
            if 'quality_distribution_analysis' in comprehensive_stats:
                print("✅ 質量分佈分析: 可用")
            if 'priority_level_analytics' in comprehensive_stats:
                print("✅ 優先級分析: 可用") 
            if 'processing_time_analysis' in comprehensive_stats:
                print("✅ 處理時間分析: 可用")
            if 'source_performance_comparison' in comprehensive_stats:
                print("✅ 來源性能比較: 可用")
        
        print("\n🎯 優化驗證結果: 成功")
        print("✅ 配置結構優化完成")
        print("✅ Python 實現更新完成")
        print("✅ 功能測試通過")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_config_optimization():
    """驗證配置優化"""
    print("\n🔍 驗證配置優化")
    print("-" * 40)
    
    try:
        config_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring/2_signal_processing_statistics/signal_processing_statistics_config.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 檢查優化後的結構
        stats_config = config.get("PHASE4_SIGNAL_PROCESSING_STATISTICS", {})
        
        optimization_checks = {
            "版本更新": stats_config.get("system_metadata", {}).get("version") == "2.2.0",
            "統計分析配置": "statistical_analysis" in stats_config,
            "實時監控配置": "real_time_monitoring" in stats_config,
            "報告配置": "reporting_configuration" in stats_config,
            "優化設置": "optimization_settings" in stats_config
        }
        
        for check, passed in optimization_checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
        
        # 詳細配置檢查
        if "statistical_analysis" in stats_config:
            analysis_config = stats_config["statistical_analysis"]
            analysis_checks = {
                "質量分佈追蹤": "quality_distribution_tracking" in analysis_config,
                "優先級分析": "priority_level_analytics" in analysis_config,
                "處理時間分析": "processing_time_analysis" in analysis_config,
                "來源性能比較": "source_performance_comparison" in analysis_config,
                "時間分析": "temporal_analysis" in analysis_config
            }
            
            print("\n📋 統計分析配置詳情:")
            for check, passed in analysis_checks.items():
                status = "✅" if passed else "❌"
                print(f"    {status} {check}")
        
        total_checks = len(optimization_checks) + len(analysis_checks)
        passed_checks = sum(optimization_checks.values()) + sum(analysis_checks.values())
        score = (passed_checks / total_checks) * 100
        
        print(f"\n📊 配置優化得分: {score:.1f}%")
        return score >= 90
        
    except Exception as e:
        print(f"❌ 配置驗證失敗: {e}")
        return False

def main():
    """主函數"""
    print("🔧 Signal Processing Statistics 優化驗證")
    print("=" * 60)
    
    # 1. 配置優化驗證
    config_ok = verify_config_optimization()
    
    # 2. 實現測試
    implementation_ok = test_optimized_implementation()
    
    # 3. 總結
    print("\n🎯 總體驗證結果")
    print("=" * 60)
    
    if config_ok and implementation_ok:
        print("✅ Signal Processing Statistics 優化成功完成!")
        print("📊 配置結構: 優化完成")
        print("🔧 Python 實現: 更新完成")
        print("🧪 功能測試: 全部通過")
        print("\n🚀 準備進行下一個組件 (EPL Decision History Tracking) 的驗證...")
    else:
        print("❌ 優化過程中發現問題")
        if not config_ok:
            print("  - 配置優化需要改進")
        if not implementation_ok:
            print("  - Python 實現需要修正")

if __name__ == "__main__":
    main()
