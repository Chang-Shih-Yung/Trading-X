#!/usr/bin/env python3
"""
修正後JSON配置驗證腳本
驗證unified_monitoring_dashboard_config.json與實際數據流的匹配度
"""

import json
import os
from pathlib import Path

class CorrectedJSONValidator:
    def __init__(self):
        self.base_path = Path("/Users/henrychang/Desktop/Trading-X")
        self.validation_results = {}
        
    def load_json_config(self):
        """載入修正後的JSON配置"""
        config_path = self.base_path / "X/backend/phase4_output_monitoring/1_unified_monitoring_dashboard/unified_monitoring_dashboard_config.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 無法載入JSON配置: {e}")
            return None
    
    def validate_phase1_integration(self, config):
        """驗證Phase1整合"""
        score = 0
        max_score = 25
        
        try:
            phase1_config = config["PHASE4_UNIFIED_MONITORING_DASHBOARD"]["integration_standards"]["upstream_integration"]["phase1_signal_pool"]
            
            # 檢查input_source
            if phase1_config.get("input_source") == "unified_signal_candidate_pool_v3":
                score += 10
                print("✅ Phase1 input_source 匹配")
            else:
                print("❌ Phase1 input_source 不匹配")
            
            # 檢查data_validation
            if phase1_config.get("data_validation") == "0.0-1.0_range_enforcement":
                score += 10
                print("✅ Phase1 data_validation 匹配")
            else:
                print("❌ Phase1 data_validation 不匹配")
            
            # 檢查數據格式標準
            format_config = config["PHASE4_UNIFIED_MONITORING_DASHBOARD"]["integration_standards"]["data_format_consistency"]
            if format_config.get("signal_strength_range") == "0.0-1.0":
                score += 5
                print("✅ Phase1 信號強度範圍匹配")
            else:
                print("❌ Phase1 信號強度範圍不匹配")
                
        except Exception as e:
            print(f"❌ Phase1驗證錯誤: {e}")
        
        return score, max_score
    
    def validate_phase2_integration(self, config):
        """驗證修正後的Phase2整合"""
        score = 0
        max_score = 25
        
        try:
            phase2_config = config["PHASE4_UNIFIED_MONITORING_DASHBOARD"]["integration_standards"]["upstream_integration"]["phase2_pre_evaluation"]
            
            # 檢查修正後的monitoring_input
            if phase2_config.get("monitoring_input") == "EnhancedRealDataQualityMonitoringEngine":
                score += 15
                print("✅ Phase2 monitoring_input 已修正匹配")
            else:
                print(f"❌ Phase2 monitoring_input 仍不匹配: {phase2_config.get('monitoring_input')}")
            
            # 檢查修正後的quality_scores
            if phase2_config.get("quality_scores") == "real_data_quality_monitoring":
                score += 10
                print("✅ Phase2 quality_scores 已修正匹配")
            else:
                print(f"❌ Phase2 quality_scores 仍不匹配: {phase2_config.get('quality_scores')}")
                
        except Exception as e:
            print(f"❌ Phase2驗證錯誤: {e}")
        
        return score, max_score
    
    def validate_phase3_integration(self, config):
        """驗證Phase3整合"""
        score = 0
        max_score = 25
        
        try:
            phase3_config = config["PHASE4_UNIFIED_MONITORING_DASHBOARD"]["integration_standards"]["upstream_integration"]["phase3_execution_policy"]
            
            # 檢查decision_results
            if phase3_config.get("decision_results") == "EPLDecisionResult":
                score += 10
                print("✅ Phase3 decision_results 匹配")
            else:
                print("❌ Phase3 decision_results 不匹配")
            
            # 檢查priority_classification
            if phase3_config.get("priority_classification") == "SignalPriority_enum":
                score += 10
                print("✅ Phase3 priority_classification 匹配")
            else:
                print("❌ Phase3 priority_classification 不匹配")
            
            # 檢查notification_configs
            if phase3_config.get("notification_configs") == "notification_dispatch_configs":
                score += 5
                print("✅ Phase3 notification_configs 匹配")
            else:
                print("❌ Phase3 notification_configs 不匹配")
                
        except Exception as e:
            print(f"❌ Phase3驗證錯誤: {e}")
        
        return score, max_score
    
    def validate_data_format_consistency(self, config):
        """驗證數據格式一致性"""
        score = 0
        max_score = 25
        
        try:
            format_config = config["PHASE4_UNIFIED_MONITORING_DASHBOARD"]["integration_standards"]["data_format_consistency"]
            
            # 檢查各項格式標準
            format_checks = [
                ("signal_strength_range", "0.0-1.0", 5),
                ("confidence_range", "0.0-1.0", 5),
                ("priority_levels", ["CRITICAL", "HIGH", "MEDIUM", "LOW"], 5),
                ("timestamp_format", "ISO_8601_UTC", 5),
                ("sync_tolerance", "100ms", 5)
            ]
            
            for key, expected, points in format_checks:
                if format_config.get(key) == expected:
                    score += points
                    print(f"✅ {key} 格式匹配")
                else:
                    print(f"❌ {key} 格式不匹配: {format_config.get(key)} vs {expected}")
                    
        except Exception as e:
            print(f"❌ 數據格式驗證錯誤: {e}")
        
        return score, max_score
    
    def validate_dashboard_components(self, config):
        """驗證Dashboard組件完整性"""
        score = 0
        max_score = 25
        
        try:
            widgets = config["PHASE4_UNIFIED_MONITORING_DASHBOARD"]["dashboard_widgets"]
            
            # 檢查必要的widget
            required_widgets = [
                "system_status_overview",
                "signal_processing_analytics", 
                "epl_decision_tracking",
                "notification_success_monitoring",
                "system_performance_monitoring"
            ]
            
            for widget in required_widgets:
                if widget in widgets:
                    score += 5
                    print(f"✅ Widget {widget} 已定義")
                else:
                    print(f"❌ 缺少Widget: {widget}")
                    
        except Exception as e:
            print(f"❌ Dashboard組件驗證錯誤: {e}")
        
        return score, max_score
    
    def run_validation(self):
        """執行完整驗證"""
        print("🔍 開始驗證修正後的JSON配置...")
        print("=" * 60)
        
        config = self.load_json_config()
        if not config:
            return
        
        # 執行各項驗證
        phase1_score, phase1_max = self.validate_phase1_integration(config)
        print(f"\n📊 Phase1整合得分: {phase1_score}/{phase1_max}")
        
        phase2_score, phase2_max = self.validate_phase2_integration(config)
        print(f"📊 Phase2整合得分: {phase2_score}/{phase2_max}")
        
        phase3_score, phase3_max = self.validate_phase3_integration(config)
        print(f"📊 Phase3整合得分: {phase3_score}/{phase3_max}")
        
        format_score, format_max = self.validate_data_format_consistency(config)
        print(f"📊 數據格式一致性得分: {format_score}/{format_max}")
        
        dashboard_score, dashboard_max = self.validate_dashboard_components(config)
        print(f"📊 Dashboard組件完整性得分: {dashboard_score}/{dashboard_max}")
        
        # 計算總得分
        total_score = phase1_score + phase2_score + phase3_score + format_score + dashboard_score
        total_max = phase1_max + phase2_max + phase3_max + format_max + dashboard_max
        percentage = (total_score / total_max) * 100
        
        print("\n" + "=" * 60)
        print(f"🎯 總驗證結果: {total_score}/{total_max} ({percentage:.1f}%)")
        
        if percentage >= 95:
            print("✅ JSON配置修正成功，可以進行Python重寫")
        elif percentage >= 85:
            print("⚠️ JSON配置基本正確，建議小幅調整後進行Python重寫")
        else:
            print("❌ JSON配置仍需進一步修正")
        
        return percentage

if __name__ == "__main__":
    validator = CorrectedJSONValidator()
    validator.run_validation()
