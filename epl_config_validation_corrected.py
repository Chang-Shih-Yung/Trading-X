"""
🔍 EPL Decision History Tracking JSON 配置驗證 (修正版)
=======================================================

基於實際配置結構的驗證腳本
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class EPLConfigValidatorCorrected:
    """EPL 決策歷史追蹤配置驗證器 (修正版)"""
    
    def __init__(self):
        self.config_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring/3_epl_decision_history_tracking/epl_decision_history_tracking_config.json")
        
    def load_and_analyze_config(self) -> Dict[str, Any]:
        """載入並分析配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return {
                "config_loaded": True,
                "config_data": config,
                "file_size": self.config_path.stat().st_size,
                "structure_analysis": self._analyze_real_structure(config)
            }
            
        except Exception as e:
            return {
                "config_loaded": False,
                "error": str(e),
                "file_exists": self.config_path.exists()
            }
    
    def _analyze_real_structure(self, config: Dict) -> Dict[str, Any]:
        """分析實際配置結構"""
        epl_config = config.get("PHASE4_EPL_DECISION_HISTORY_TRACKING", {})
        
        return {
            "main_sections": list(epl_config.keys()),
            "has_decision_tracking": "decision_tracking_architecture" in epl_config,
            "has_analytics": "analytics_and_reporting" in epl_config,
            "has_data_management": "data_management_and_retention" in epl_config,
            "has_api_integration": "api_integration_points" in epl_config,
            "decision_lifecycle": "decision_lifecycle_monitoring" in epl_config.get("decision_tracking_architecture", {}),
            "outcome_measurement": "outcome_measurement" in epl_config.get("decision_tracking_architecture", {}),
            "historical_analysis": "historical_analysis_capabilities" in epl_config.get("analytics_and_reporting", {})
        }
    
    def validate_phase_integration(self, config: Dict) -> Dict[str, Any]:
        """驗證 Phase 整合 (基於實際結構)"""
        integration_score = 0
        max_score = 40
        details = {}
        
        epl_config = config.get("PHASE4_EPL_DECISION_HISTORY_TRACKING", {})
        decision_arch = epl_config.get("decision_tracking_architecture", {})
        
        # Phase1 信號追蹤 (10分)
        phase1_score = 0
        decision_creation = decision_arch.get("decision_lifecycle_monitoring", {}).get("decision_creation", {})
        if "original_signal_candidate" in decision_creation.get("input_data_capture", {}):
            phase1_score += 5
        if "pre_evaluation_result" in decision_creation.get("input_data_capture", {}):
            phase1_score += 5
        
        details["phase1_signal_integration"] = f"{phase1_score}/10"
        integration_score += phase1_score
        
        # Phase2 預評估整合 (10分)
        phase2_score = 0
        if "pre_evaluation_result" in decision_creation.get("input_data_capture", {}):
            phase2_score += 5
        if "decision_engine_process" in decision_creation:
            phase2_score += 5
        
        details["phase2_pre_evaluation"] = f"{phase2_score}/10"
        integration_score += phase2_score
        
        # Phase3 執行政策追蹤 (10分)
        phase3_score = 0
        execution_tracking = decision_arch.get("decision_lifecycle_monitoring", {}).get("decision_execution_tracking", {})
        if "execution_initiation" in execution_tracking:
            phase3_score += 5
        if "execution_monitoring" in execution_tracking:
            phase3_score += 5
        
        details["phase3_execution_tracking"] = f"{phase3_score}/10"
        integration_score += phase3_score
        
        # Phase4 內部整合 (10分)
        phase4_score = 0
        outcome_measurement = decision_arch.get("decision_lifecycle_monitoring", {}).get("outcome_measurement", {})
        if "immediate_outcomes" in outcome_measurement:
            phase4_score += 5
        if "long_term_performance" in outcome_measurement:
            phase4_score += 5
        
        details["phase4_outcome_tracking"] = f"{phase4_score}/10"
        integration_score += phase4_score
        
        return {
            "integration_score": integration_score,
            "max_score": max_score,
            "percentage": (integration_score / max_score) * 100,
            "details": details,
            "status": "excellent" if integration_score >= 32 else "good" if integration_score >= 24 else "needs_improvement"
        }
    
    def validate_data_structures(self, config: Dict) -> Dict[str, Any]:
        """驗證數據結構相容性"""
        compatibility_score = 0
        max_score = 30
        details = {}
        
        epl_config = config.get("PHASE4_EPL_DECISION_HISTORY_TRACKING", {})
        
        # 決策記錄結構 (10分)
        decision_structure = 0
        decision_lifecycle = epl_config.get("decision_tracking_architecture", {}).get("decision_lifecycle_monitoring", {})
        if "decision_creation" in decision_lifecycle:
            decision_structure += 5
        if "decision_execution_tracking" in decision_lifecycle:
            decision_structure += 5
        
        details["decision_record_structure"] = f"{decision_structure}/10"
        compatibility_score += decision_structure
        
        # 數據管理 (10分)
        data_management = 0
        data_mgmt = epl_config.get("data_management_and_retention", {})
        if "retention_policies" in data_mgmt:
            data_management += 5
        if "data_archival" in data_mgmt:
            data_management += 5
        
        details["data_management"] = f"{data_management}/10"
        compatibility_score += data_management
        
        # API 整合 (10分)
        api_integration = 0
        api_config = epl_config.get("api_integration_points", {})
        if "data_export_endpoints" in api_config:
            api_integration += 5
        if "historical_query_endpoints" in api_config:
            api_integration += 5
        
        details["api_integration"] = f"{api_integration}/10"
        compatibility_score += api_integration
        
        return {
            "compatibility_score": compatibility_score,
            "max_score": max_score,
            "percentage": (compatibility_score / max_score) * 100,
            "details": details,
            "status": "excellent" if compatibility_score >= 24 else "good" if compatibility_score >= 18 else "needs_improvement"
        }
    
    def validate_monitoring_features(self, config: Dict) -> Dict[str, Any]:
        """驗證監控功能"""
        monitoring_score = 0
        max_score = 30
        details = {}
        
        epl_config = config.get("PHASE4_EPL_DECISION_HISTORY_TRACKING", {})
        
        # 分析能力 (10分)
        analytics_score = 0
        analytics = epl_config.get("analytics_and_reporting", {})
        if "historical_analysis_capabilities" in analytics:
            analytics_score += 5
        if "performance_analytics" in analytics:
            analytics_score += 5
        
        details["analytics_capabilities"] = f"{analytics_score}/10"
        monitoring_score += analytics_score
        
        # 決策成效追蹤 (10分)
        effectiveness_score = 0
        outcome_measurement = epl_config.get("decision_tracking_architecture", {}).get("decision_lifecycle_monitoring", {}).get("outcome_measurement", {})
        if "immediate_outcomes" in outcome_measurement:
            effectiveness_score += 5
        if "long_term_performance" in outcome_measurement:
            effectiveness_score += 5
        
        details["decision_effectiveness"] = f"{effectiveness_score}/10"
        monitoring_score += effectiveness_score
        
        # 學習系統 (10分)
        learning_score = 0
        learning_system = epl_config.get("decision_learning_system", {})
        if "pattern_recognition" in learning_system:
            learning_score += 5
        if "strategy_optimization" in learning_system:
            learning_score += 5
        
        details["learning_system"] = f"{learning_score}/10"
        monitoring_score += learning_score
        
        return {
            "monitoring_score": monitoring_score,
            "max_score": max_score,
            "percentage": (monitoring_score / max_score) * 100,
            "details": details,
            "status": "excellent" if monitoring_score >= 24 else "good" if monitoring_score >= 18 else "needs_improvement"
        }
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """生成驗證報告"""
        print("🔍 EPL Decision History Tracking JSON 配置驗證 (修正版)")
        print("=" * 70)
        
        # 載入配置
        config_analysis = self.load_and_analyze_config()
        
        if not config_analysis.get("config_loaded"):
            return {
                "validation_status": "failed",
                "error": config_analysis.get("error")
            }
        
        config = config_analysis["config_data"]
        structure = config_analysis["structure_analysis"]
        
        print(f"✅ 配置載入成功 ({config_analysis['file_size']} bytes)")
        print("📊 實際配置結構分析:")
        for key, value in structure.items():
            icon = "✅" if value else "❌"
            print(f"  {icon} {key}: {value}")
        
        # 各項驗證
        phase_integration = self.validate_phase_integration(config)
        data_compatibility = self.validate_data_structures(config)
        monitoring_features = self.validate_monitoring_features(config)
        
        # 計算總分
        total_score = (
            phase_integration["integration_score"] +
            data_compatibility["compatibility_score"] +
            monitoring_features["monitoring_score"]
        )
        max_total_score = (
            phase_integration["max_score"] +
            data_compatibility["max_score"] +
            monitoring_features["max_score"]
        )
        
        overall_percentage = (total_score / max_total_score) * 100
        
        # 生成報告
        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "overall_score": {
                "total_points": f"{total_score}/{max_total_score}",
                "percentage": f"{overall_percentage:.1f}%",
                "grade": self._get_grade(overall_percentage)
            },
            "detailed_scores": {
                "phase_integration": phase_integration,
                "data_compatibility": data_compatibility,
                "monitoring_features": monitoring_features
            },
            "structure_analysis": structure,
            "recommendations": self._generate_recommendations(
                phase_integration, data_compatibility, monitoring_features, overall_percentage
            )
        }
        
        # 打印結果
        self._print_results(report)
        
        return report
    
    def _get_grade(self, percentage: float) -> str:
        """獲取評級"""
        if percentage >= 90:
            return "A+ (優秀)"
        elif percentage >= 80:
            return "A (良好)" 
        elif percentage >= 70:
            return "B (可接受)"
        elif percentage >= 60:
            return "C (需改進)"
        else:
            return "D (需重構)"
    
    def _generate_recommendations(self, phase_integration, data_compatibility, monitoring_features, overall_percentage) -> List[str]:
        """生成建議"""
        recommendations = []
        
        if overall_percentage >= 85:
            recommendations.append("配置品質優秀，建議維持現狀")
        elif overall_percentage >= 70:
            recommendations.append("配置良好，可進行小幅優化")
        else:
            if phase_integration["percentage"] < 70:
                recommendations.append("需要改進 Phase 間整合配置")
            if data_compatibility["percentage"] < 70:
                recommendations.append("需要優化數據結構設計")
            if monitoring_features["percentage"] < 70:
                recommendations.append("需要完善監控功能")
        
        return recommendations
    
    def _print_results(self, report: Dict):
        """打印結果"""
        print(f"\n📊 總體評分: {report['overall_score']['percentage']} - {report['overall_score']['grade']}")
        
        print("\n📋 詳細評分:")
        for category, details in report["detailed_scores"].items():
            percentage = details["percentage"]
            status_icon = "✅" if percentage >= 70 else "⚠️" if percentage >= 50 else "❌"
            print(f"  {status_icon} {category}: {percentage:.1f}% ({details['status']})")
            
            for detail_key, detail_value in details["details"].items():
                print(f"    - {detail_key}: {detail_value}")
        
        print("\n💡 建議:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")

def main():
    """主函數"""
    validator = EPLConfigValidatorCorrected()
    report = validator.generate_validation_report()
    
    print(f"\n🎯 EPL Decision History Tracking JSON 驗證完成")
    print(f"📊 總分: {report['overall_score']['percentage']}")

if __name__ == "__main__":
    main()
