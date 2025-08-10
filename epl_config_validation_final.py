"""
🔍 EPL Decision History Tracking JSON 配置驗證 (完整版)
=====================================================

基於完整配置結構的準確驗證
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class EPLConfigValidatorFinal:
    """EPL 決策歷史追蹤配置驗證器 (最終版)"""
    
    def __init__(self):
        self.config_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring/3_epl_decision_history_tracking/epl_decision_history_tracking_config.json")
        
    def load_config(self) -> Dict[str, Any]:
        """載入配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入配置失敗: {e}")
            return {}
    
    def validate_phase_integration(self, config: Dict) -> Dict[str, Any]:
        """驗證 Phase 整合 (基於實際結構)"""
        integration_score = 0
        max_score = 40
        details = {}
        
        epl_config = config.get("PHASE4_EPL_DECISION_HISTORY_TRACKING", {})
        decision_arch = epl_config.get("decision_tracking_architecture", {})
        
        # Phase1 信號追蹤 (10分)
        phase1_score = 0
        decision_lifecycle = decision_arch.get("decision_lifecycle_monitoring", {})
        if "decision_creation" in decision_lifecycle:
            creation = decision_lifecycle["decision_creation"]
            if "input_data_capture" in creation:
                input_data = creation["input_data_capture"]
                if "original_signal_candidate" in input_data:
                    phase1_score += 5
                if "pre_evaluation_result" in input_data:
                    phase1_score += 5
        
        details["phase1_signal_integration"] = f"{phase1_score}/10"
        integration_score += phase1_score
        
        # Phase2 預評估整合 (10分)
        phase2_score = 0
        if "decision_creation" in decision_lifecycle:
            creation = decision_lifecycle["decision_creation"]
            if "decision_engine_process" in creation:
                phase2_score += 5
            if "decision_output_capture" in creation:
                phase2_score += 5
        
        details["phase2_decision_engine"] = f"{phase2_score}/10"
        integration_score += phase2_score
        
        # Phase3 執行追蹤 (10分)
        phase3_score = 0
        if "decision_execution_tracking" in decision_lifecycle:
            execution = decision_lifecycle["decision_execution_tracking"]
            if "execution_initiation" in execution:
                phase3_score += 5
            if "execution_monitoring" in execution:
                phase3_score += 5
        
        details["phase3_execution_tracking"] = f"{phase3_score}/10"
        integration_score += phase3_score
        
        # Phase4 成效測量 (10分)
        phase4_score = 0
        if "outcome_measurement" in decision_lifecycle:
            outcome = decision_lifecycle["outcome_measurement"]
            if "immediate_outcomes" in outcome:
                phase4_score += 5
            if "extended_outcomes" in outcome:
                phase4_score += 5
        
        details["phase4_outcome_measurement"] = f"{phase4_score}/10"
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
        
        # 決策類型分析 (10分)
        decision_analytics = 0
        if "decision_type_analytics" in epl_config.get("decision_tracking_architecture", {}):
            analytics = epl_config["decision_tracking_architecture"]["decision_type_analytics"]
            if "replacement_decision_tracking" in analytics:
                decision_analytics += 3
            if "strengthening_decision_tracking" in analytics:
                decision_analytics += 3
            if "new_position_decision_tracking" in analytics:
                decision_analytics += 2
            if "ignore_decision_tracking" in analytics:
                decision_analytics += 2
        
        details["decision_analytics_structure"] = f"{decision_analytics}/10"
        compatibility_score += decision_analytics
        
        # 數據存儲和檢索 (10分)
        data_storage = 0
        storage_config = epl_config.get("data_storage_and_retrieval", {})
        if "decision_data_storage" in storage_config:
            storage = storage_config["decision_data_storage"]
            if "raw_decision_data" in storage:
                data_storage += 5
            if "aggregated_analytics" in storage:
                data_storage += 5
        
        details["data_storage_structure"] = f"{data_storage}/10"
        compatibility_score += data_storage
        
        # API 接口 (10分)
        api_score = 0
        api_config = epl_config.get("api_interfaces", {})
        if "decision_tracking_api" in api_config:
            api_score += 4
        if "performance_analytics_api" in api_config:
            api_score += 3
        if "learning_data_api" in api_config:
            api_score += 3
        
        details["api_interfaces"] = f"{api_score}/10"
        compatibility_score += api_score
        
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
        
        # 學習和優化 (10分)
        learning_score = 0
        learning_config = epl_config.get("learning_and_optimization", {})
        if "pattern_recognition" in learning_config:
            learning_score += 4
        if "adaptive_learning" in learning_config:
            learning_score += 3
        if "feedback_integration" in learning_config:
            learning_score += 3
        
        details["learning_optimization"] = f"{learning_score}/10"
        monitoring_score += learning_score
        
        # 報告和分析 (10分)
        reporting_score = 0
        reporting_config = epl_config.get("reporting_and_analytics", {})
        if "real_time_dashboards" in reporting_config:
            reporting_score += 5
        if "historical_analysis" in reporting_config:
            reporting_score += 5
        
        details["reporting_analytics"] = f"{reporting_score}/10"
        monitoring_score += reporting_score
        
        # 優先級分類分析 (10分)
        priority_score = 0
        decision_arch = epl_config.get("decision_tracking_architecture", {})
        if "priority_classification_analytics" in decision_arch:
            priority_analytics = decision_arch["priority_classification_analytics"]
            if "critical_priority_tracking" in priority_analytics:
                priority_score += 5
            if "priority_calibration" in priority_analytics:
                priority_score += 5
        
        details["priority_classification"] = f"{priority_score}/10"
        monitoring_score += priority_score
        
        return {
            "monitoring_score": monitoring_score,
            "max_score": max_score,
            "percentage": (monitoring_score / max_score) * 100,
            "details": details,
            "status": "excellent" if monitoring_score >= 24 else "good" if monitoring_score >= 18 else "needs_improvement"
        }
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """生成驗證報告"""
        print("🔍 EPL Decision History Tracking JSON 配置驗證 (完整版)")
        print("=" * 70)
        
        # 載入配置
        config = self.load_config()
        if not config:
            return {"validation_status": "failed", "error": "無法載入配置"}
        
        epl_config = config.get("PHASE4_EPL_DECISION_HISTORY_TRACKING", {})
        
        print(f"✅ 配置載入成功")
        print(f"📊 主要組件: {list(epl_config.keys())}")
        print(f"📝 系統版本: {epl_config.get('system_metadata', {}).get('version', 'N/A')}")
        
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
            "recommendations": self._generate_recommendations(overall_percentage)
        }
        
        # 打印結果
        self._print_results(report)
        
        return report
    
    def _get_grade(self, percentage: float) -> str:
        """獲取評級"""
        if percentage >= 95:
            return "A+ (完美)"
        elif percentage >= 85:
            return "A (優秀)"
        elif percentage >= 75:
            return "B+ (良好)"
        elif percentage >= 65:
            return "B (可接受)"
        elif percentage >= 55:
            return "C (需改進)"
        else:
            return "D (需重構)"
    
    def _generate_recommendations(self, overall_percentage) -> List[str]:
        """生成建議"""
        if overall_percentage >= 90:
            return ["配置品質優秀，建議維持現狀並繼續下一組件"]
        elif overall_percentage >= 80:
            return ["配置良好，可進行小幅優化", "建議繼續下一組件驗證"]
        elif overall_percentage >= 70:
            return ["配置可接受，建議進行適度優化", "重點關注低分項目"]
        else:
            return ["配置需要重大改進", "建議優化後再繼續", "重構低分組件"]
    
    def _print_results(self, report: Dict):
        """打印結果"""
        print(f"\n📊 總體評分: {report['overall_score']['percentage']} - {report['overall_score']['grade']}")
        
        print("\n📋 詳細評分:")
        for category, details in report["detailed_scores"].items():
            percentage = details["percentage"]
            status_icon = "✅" if percentage >= 80 else "⚠️" if percentage >= 60 else "❌"
            print(f"  {status_icon} {category}: {percentage:.1f}% ({details['status']})")
            
            for detail_key, detail_value in details["details"].items():
                print(f"    - {detail_key}: {detail_value}")
        
        print("\n💡 建議:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")

def main():
    """主函數"""
    validator = EPLConfigValidatorFinal()
    report = validator.generate_validation_report()
    
    print(f"\n🎯 EPL Decision History Tracking JSON 驗證完成")
    print(f"📊 最終評分: {report['overall_score']['percentage']}")

if __name__ == "__main__":
    main()
