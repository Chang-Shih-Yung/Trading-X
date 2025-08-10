#!/usr/bin/env python3
"""
Signal Processing Statistics JSON配置驗證腳本
驗證 signal_processing_statistics_config.json 與實際數據流的匹配度
"""

import json
import os
from pathlib import Path

class SignalStatsJSONValidator:
    def __init__(self):
        self.base_path = Path("/Users/henrychang/Desktop/Trading-X")
        self.validation_results = {}
        
    def load_json_config(self):
        """載入JSON配置"""
        config_path = self.base_path / "X/backend/phase4_output_monitoring/2_signal_processing_statistics/signal_processing_statistics_config.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 無法載入JSON配置: {e}")
            return None
    
    def validate_phase_integration_compatibility(self, config):
        """驗證Phase整合兼容性"""
        score = 0
        max_score = 40
        
        print("\n🔍 驗證Phase整合兼容性:")
        print("-" * 40)
        
        try:
            main_config = config.get("PHASE4_SIGNAL_PROCESSING_STATISTICS", {})
            
            # 檢查系統元數據中的整合驗證
            if "system_metadata" in main_config:
                metadata = main_config["system_metadata"]
                if metadata.get("integration_validation") == "phase1_to_phase3_data_flow_verified":
                    score += 10
                    print("✅ Phase1-3數據流驗證已確認")
                else:
                    print("❌ 缺少Phase整合驗證")
            
            # 檢查統計架構中的Phase相關配置
            if "statistics_architecture" in main_config:
                stats_arch = main_config["statistics_architecture"]
                
                # 檢查實時處理分析
                if "real_time_processing_analytics" in stats_arch:
                    real_time = stats_arch["real_time_processing_analytics"]
                    
                    # 檢查處理延遲分析中的Phase配置
                    if "processing_latency_analytics" in real_time:
                        latency_config = real_time["processing_latency_analytics"]
                        
                        if "phase_level_latency" in latency_config:
                            phase_latency = latency_config["phase_level_latency"]
                            
                            # 檢查各Phase的延遲配置
                            phase_checks = [
                                ("phase1_signal_generation", "Phase1信號生成延遲配置"),
                                ("phase2_pre_evaluation", "Phase2預評估延遲配置"),
                                ("phase3_execution_policy", "Phase3執行策略延遲配置")
                            ]
                            
                            for phase_key, description in phase_checks:
                                if phase_key in phase_latency:
                                    phase_config = phase_latency[phase_key]
                                    if "target_latency" in phase_config and "alert_threshold" in phase_config:
                                        score += 5
                                        print(f"✅ {description}完整")
                                    else:
                                        print(f"⚠️ {description}不完整")
                                else:
                                    print(f"❌ 缺少{description}")
                        else:
                            print("❌ 缺少phase_level_latency配置")
                    else:
                        print("❌ 缺少processing_latency_analytics配置")
                else:
                    print("❌ 缺少real_time_processing_analytics配置")
            else:
                print("❌ 缺少statistics_architecture配置")
                
            # 檢查信號來源配置是否與Phase1匹配
            if "statistics_architecture" in main_config:
                if "real_time_processing_analytics" in main_config["statistics_architecture"]:
                    real_time = main_config["statistics_architecture"]["real_time_processing_analytics"]
                    if "signal_volume_tracking" in real_time:
                        volume_tracking = real_time["signal_volume_tracking"]
                        if "signals_by_source" in volume_tracking:
                            source_config = volume_tracking["signals_by_source"]
                            if "source_categories" in source_config:
                                # 檢查是否包含主要的技術指標來源（Phase1相關）
                                sources = source_config["source_categories"]
                                expected_sources = ["BOLLINGER_BANDS", "RSI_DIVERGENCE", "MACD_SIGNAL"]
                                found_sources = sum(1 for src in expected_sources if src in sources)
                                score += (found_sources * 2)  # 每個來源2分
                                print(f"✅ 發現 {found_sources}/{len(expected_sources)} 個Phase1技術指標來源")
                
        except Exception as e:
            print(f"❌ Phase整合驗證錯誤: {e}")
        
        return score, max_score
    
    def validate_data_structure_compatibility(self, config):
        """驗證數據結構兼容性"""
        score = 0
        max_score = 30
        
        print("\n🔍 驗證數據結構兼容性:")
        print("-" * 40)
        
        try:
            main_config = config.get("PHASE4_SIGNAL_PROCESSING_STATISTICS", {})
            
            # 檢查信號優先級配置
            if "statistics_architecture" in main_config:
                stats_arch = main_config["statistics_architecture"]
                if "real_time_processing_analytics" in stats_arch:
                    real_time = stats_arch["real_time_processing_analytics"]
                    if "signal_volume_tracking" in real_time:
                        volume = real_time["signal_volume_tracking"]
                        if "signals_by_priority" in volume:
                            priority_config = volume["signals_by_priority"]
                            if "categories" in priority_config:
                                categories = priority_config["categories"]
                                # 檢查是否包含標準優先級
                                expected_priorities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
                                found_priorities = sum(1 for p in expected_priorities if p in categories)
                                if found_priorities == 4:
                                    score += 10
                                    print("✅ 優先級分類完整匹配SignalPriority枚舉")
                                else:
                                    score += found_priorities * 2
                                    print(f"⚠️ 優先級分類部分匹配: {found_priorities}/4")
            
            # 檢查質量評分配置
            if "statistics_architecture" in main_config:
                stats_arch = main_config["statistics_architecture"]
                if "real_time_processing_analytics" in stats_arch:
                    real_time = stats_arch["real_time_processing_analytics"]
                    if "quality_analytics" in real_time:
                        quality = real_time["quality_analytics"]
                        if "signal_quality_distribution" in quality:
                            qual_dist = quality["signal_quality_distribution"]
                            if "quality_score_histogram" in qual_dist:
                                histogram = qual_dist["quality_score_histogram"]
                                if "bins" in histogram and "0.05_increments_from_0_to_1" in histogram["bins"]:
                                    score += 10
                                    print("✅ 質量分數配置匹配0.0-1.0範圍")
                                else:
                                    print("❌ 質量分數配置不匹配標準範圍")
            
            # 檢查嵌入評分維度配置
            if "statistics_architecture" in main_config:
                stats_arch = main_config["statistics_architecture"]
                if "real_time_processing_analytics" in stats_arch:
                    real_time = stats_arch["real_time_processing_analytics"]
                    if "quality_analytics" in real_time:
                        quality = real_time["quality_analytics"]
                        if "embedded_scoring_analytics" in quality:
                            embedded = quality["embedded_scoring_analytics"]
                            if "five_dimension_analysis" in embedded:
                                five_dim = embedded["five_dimension_analysis"]
                                # 檢查五維度評分
                                expected_dimensions = [
                                    "technical_strength", "market_timing", "risk_assessment", 
                                    "source_reliability", "execution_feasibility"
                                ]
                                found_dimensions = sum(1 for dim in expected_dimensions if dim in five_dim)
                                if found_dimensions == 5:
                                    score += 10
                                    print("✅ 五維度評分配置完整")
                                else:
                                    score += found_dimensions * 2
                                    print(f"⚠️ 五維度評分配置部分完整: {found_dimensions}/5")
                
        except Exception as e:
            print(f"❌ 數據結構驗證錯誤: {e}")
        
        return score, max_score
    
    def validate_monitoring_features(self, config):
        """驗證監控功能配置"""
        score = 0
        max_score = 30
        
        print("\n🔍 驗證監控功能配置:")
        print("-" * 40)
        
        try:
            main_config = config.get("PHASE4_SIGNAL_PROCESSING_STATISTICS", {})
            
            # 檢查報告配置
            if "reporting_configuration" in main_config:
                reporting = main_config["reporting_configuration"]
                
                # 檢查實時儀表板
                if "real_time_dashboards" in reporting:
                    dashboards = reporting["real_time_dashboards"]
                    expected_dashboards = [
                        "signal_volume_dashboard",
                        "latency_monitoring_dashboard", 
                        "quality_analytics_dashboard"
                    ]
                    found_dashboards = sum(1 for dash in expected_dashboards if dash in dashboards)
                    score += found_dashboards * 3
                    print(f"✅ 實時儀表板配置: {found_dashboards}/{len(expected_dashboards)}")
                
                # 檢查歷史報告
                if "historical_reports" in reporting:
                    reports = reporting["historical_reports"]
                    expected_reports = [
                        "daily_statistics_report",
                        "weekly_performance_report",
                        "monthly_analytics_report"
                    ]
                    found_reports = sum(1 for report in expected_reports if report in reports)
                    score += found_reports * 3
                    print(f"✅ 歷史報告配置: {found_reports}/{len(expected_reports)}")
            
            # 檢查API端點配置
            if "api_endpoints" in main_config:
                api_config = main_config["api_endpoints"]
                expected_endpoints = [
                    "real_time_statistics",
                    "historical_analytics",
                    "performance_metrics"
                ]
                found_endpoints = sum(1 for endpoint in expected_endpoints if endpoint in api_config)
                score += found_endpoints * 3
                print(f"✅ API端點配置: {found_endpoints}/{len(expected_endpoints)}")
            
            # 檢查數據保留策略
            if "data_retention_policy" in main_config:
                retention = main_config["data_retention_policy"]
                expected_retention = [
                    "real_time_data",
                    "hourly_aggregates", 
                    "daily_summaries",
                    "monthly_analytics"
                ]
                found_retention = sum(1 for policy in expected_retention if policy in retention)
                score += found_retention * 2
                print(f"✅ 數據保留策略: {found_retention}/{len(expected_retention)}")
                
        except Exception as e:
            print(f"❌ 監控功能驗證錯誤: {e}")
        
        return score, max_score
    
    def run_validation(self):
        """執行完整驗證"""
        print("🔍 開始驗證 Signal Processing Statistics JSON配置...")
        print("=" * 60)
        
        config = self.load_json_config()
        if not config:
            return 0
        
        # 執行各項驗證
        phase_score, phase_max = self.validate_phase_integration_compatibility(config)
        data_score, data_max = self.validate_data_structure_compatibility(config)
        monitor_score, monitor_max = self.validate_monitoring_features(config)
        
        # 計算總得分
        total_score = phase_score + data_score + monitor_score
        total_max = phase_max + data_max + monitor_max
        percentage = (total_score / total_max) * 100
        
        print("\n" + "=" * 60)
        print(f"📊 Phase整合兼容性得分: {phase_score}/{phase_max}")
        print(f"📊 數據結構兼容性得分: {data_score}/{data_max}")
        print(f"📊 監控功能配置得分: {monitor_score}/{monitor_max}")
        print("-" * 60)
        print(f"🎯 總驗證結果: {total_score}/{total_max} ({percentage:.1f}%)")
        
        if percentage >= 95:
            print("✅ JSON配置優秀，無需修正")
        elif percentage >= 80:
            print("⚠️ JSON配置良好，建議小幅調整")
        elif percentage >= 60:
            print("⚠️ JSON配置基本可用，需要補充整合配置")
        else:
            print("❌ JSON配置需要重大修正")
        
        return percentage

if __name__ == "__main__":
    validator = SignalStatsJSONValidator()
    validator.run_validation()
