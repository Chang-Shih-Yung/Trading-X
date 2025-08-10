"""
🔍 EPL Decision History Tracking 數據流匹配驗證
===============================================

檢查 JSON 配置是否與其他 Phase 的數據輸入輸出匹配
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class EPLDataFlowValidator:
    """EPL 數據流驗證器"""
    
    def __init__(self):
        self.epl_config_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring/3_epl_decision_history_tracking/epl_decision_history_tracking_config.json")
        
    def load_epl_config(self) -> Dict[str, Any]:
        """載入 EPL 配置"""
        try:
            with open(self.epl_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入 EPL 配置失敗: {e}")
            return {}
    
    def validate_phase1_data_integration(self, config: Dict) -> Dict[str, Any]:
        """驗證 Phase1 數據整合"""
        integration_score = 0
        max_score = 25
        details = {}
        
        epl_config = config.get("PHASE4_EPL_DECISION_HISTORY_TRACKING", {})
        decision_arch = epl_config.get("decision_tracking_architecture", {})
        
        # Phase1 信號候選數據 (10分)
        phase1_score = 0
        decision_creation = decision_arch.get("decision_lifecycle_monitoring", {}).get("decision_creation", {})
        input_capture = decision_creation.get("input_data_capture", {})
        
        # 檢查是否接收完整的 SignalCandidate 物件
        if "original_signal_candidate" in input_capture:
            if "complete_SignalCandidate_object" in str(input_capture["original_signal_candidate"]):
                phase1_score += 5
                details["signal_candidate_capture"] = "✅ 完整 SignalCandidate 物件"
            else:
                details["signal_candidate_capture"] = "⚠️ 不完整的信號候選資料"
        else:
            details["signal_candidate_capture"] = "❌ 缺少信號候選資料擷取"
        
        # 檢查市場上下文擷取
        if "market_context" in input_capture:
            if "real_time_market_snapshot" in str(input_capture["market_context"]):
                phase1_score += 5
                details["market_context_capture"] = "✅ 即時市場快照"
            else:
                details["market_context_capture"] = "⚠️ 市場上下文不完整"
        else:
            details["market_context_capture"] = "❌ 缺少市場上下文"
        
        integration_score += phase1_score
        
        # Phase1 信號品質追蹤 (8分)
        quality_tracking = 0
        
        # 檢查是否追蹤信號品質指標
        signal_quality_indicators = [
            "confidence_metrics", "quality_score", "technical_strength", 
            "market_timing", "source_reliability"
        ]
        
        found_quality_indicators = 0
        for indicator in signal_quality_indicators:
            if indicator in str(decision_creation):
                found_quality_indicators += 1
        
        quality_tracking = min(8, found_quality_indicators * 2)
        details["signal_quality_tracking"] = f"✅ {found_quality_indicators}/5 品質指標已追蹤"
        
        integration_score += quality_tracking
        
        # Phase1 輸出格式相容性 (7分)
        output_compatibility = 0
        
        # 檢查決策輸出是否包含 Phase1 需要的回饋
        decision_output = decision_creation.get("decision_output_capture", {})
        required_outputs = ["decision_type", "execution_parameters", "reasoning_chain", "confidence_metrics"]
        
        for output in required_outputs:
            if output in decision_output:
                output_compatibility += 1.75  # 7/4
        
        details["phase1_output_compatibility"] = f"✅ {sum(1 for out in required_outputs if out in decision_output)}/4 輸出格式"
        
        integration_score += int(output_compatibility)
        
        return {
            "phase1_integration_score": integration_score,
            "max_score": max_score,
            "percentage": (integration_score / max_score) * 100,
            "details": details,
            "status": "excellent" if integration_score >= 20 else "good" if integration_score >= 15 else "needs_improvement"
        }
    
    def validate_phase2_data_integration(self, config: Dict) -> Dict[str, Any]:
        """驗證 Phase2 數據整合"""
        integration_score = 0
        max_score = 25
        details = {}
        
        epl_config = config.get("PHASE4_EPL_DECISION_HISTORY_TRACKING", {})
        decision_arch = epl_config.get("decision_tracking_architecture", {})
        
        # Phase2 預評估結果 (10分)
        phase2_score = 0
        decision_creation = decision_arch.get("decision_lifecycle_monitoring", {}).get("decision_creation", {})
        input_capture = decision_creation.get("input_data_capture", {})
        
        # 檢查是否接收 Phase2 預評估結果
        if "pre_evaluation_result" in input_capture:
            if "Phase2_PreEvaluationResult" in str(input_capture["pre_evaluation_result"]):
                phase2_score += 5
                details["pre_evaluation_capture"] = "✅ Phase2 預評估結果"
            else:
                details["pre_evaluation_capture"] = "⚠️ 預評估結果格式不符"
        else:
            details["pre_evaluation_capture"] = "❌ 缺少預評估結果"
        
        # 檢查投資組合狀態
        if "portfolio_state" in input_capture:
            if "current_positions_and_risk_metrics" in str(input_capture["portfolio_state"]):
                phase2_score += 5
                details["portfolio_state_capture"] = "✅ 投資組合狀態和風險指標"
            else:
                details["portfolio_state_capture"] = "⚠️ 投資組合狀態不完整"
        else:
            details["portfolio_state_capture"] = "❌ 缺少投資組合狀態"
        
        integration_score += phase2_score
        
        # Phase2 決策引擎整合 (10分)
        engine_integration = 0
        decision_engine = decision_creation.get("decision_engine_process", {})
        
        # 檢查決策引擎流程
        required_processes = [
            "scenario_routing", "parallel_evaluation", 
            "risk_validation", "priority_classification"
        ]
        
        for process in required_processes:
            if process in decision_engine:
                engine_integration += 2.5  # 10/4
        
        details["decision_engine_integration"] = f"✅ {sum(1 for proc in required_processes if proc in decision_engine)}/4 決策流程"
        
        integration_score += int(engine_integration)
        
        # Phase2 風險評估整合 (5分)
        risk_integration = 0
        
        # 檢查多層風險評估
        if "multi_level_risk_assessment" in str(decision_engine.get("risk_validation", "")):
            risk_integration += 5
            details["risk_assessment_integration"] = "✅ 多層風險評估"
        else:
            details["risk_assessment_integration"] = "❌ 缺少多層風險評估"
        
        integration_score += risk_integration
        
        return {
            "phase2_integration_score": integration_score,
            "max_score": max_score,
            "percentage": (integration_score / max_score) * 100,
            "details": details,
            "status": "excellent" if integration_score >= 20 else "good" if integration_score >= 15 else "needs_improvement"
        }
    
    def validate_phase3_data_integration(self, config: Dict) -> Dict[str, Any]:
        """驗證 Phase3 數據整合"""
        integration_score = 0
        max_score = 30
        details = {}
        
        epl_config = config.get("PHASE4_EPL_DECISION_HISTORY_TRACKING", {})
        decision_arch = epl_config.get("decision_tracking_architecture", {})
        
        # Phase3 執行追蹤 (12分)
        execution_tracking = 0
        execution_track = decision_arch.get("decision_lifecycle_monitoring", {}).get("decision_execution_tracking", {})
        
        # 執行啟動追蹤
        execution_initiation = execution_track.get("execution_initiation", {})
        required_initiation = ["execution_timestamp", "execution_latency", "market_conditions_at_execution", "slippage_measurement"]
        
        for item in required_initiation:
            if item in execution_initiation:
                execution_tracking += 3  # 12/4
        
        details["execution_initiation_tracking"] = f"✅ {sum(1 for item in required_initiation if item in execution_initiation)}/4 執行啟動指標"
        
        integration_score += int(execution_tracking)
        
        # Phase3 執行監控 (12分)
        execution_monitoring = 0
        exec_monitoring = execution_track.get("execution_monitoring", {})
        
        required_monitoring = [
            "position_establishment", "risk_parameter_application",
            "portfolio_impact", "correlation_effects"
        ]
        
        for item in required_monitoring:
            if item in exec_monitoring:
                execution_monitoring += 3  # 12/4
        
        details["execution_monitoring"] = f"✅ {sum(1 for item in required_monitoring if item in exec_monitoring)}/4 執行監控指標"
        
        integration_score += int(execution_monitoring)
        
        # Phase3 結果測量 (6分)
        outcome_measurement = 0
        outcome_track = decision_arch.get("decision_lifecycle_monitoring", {}).get("outcome_measurement", {})
        
        # 即時結果
        immediate_outcomes = outcome_track.get("immediate_outcomes", {})
        if len(immediate_outcomes) >= 3:  # 至少3個即時結果指標
            outcome_measurement += 3
            details["immediate_outcomes"] = "✅ 即時結果追蹤"
        else:
            details["immediate_outcomes"] = "⚠️ 即時結果追蹤不足"
        
        # 延伸結果
        extended_outcomes = outcome_track.get("extended_outcomes", {})
        if len(extended_outcomes) >= 3:  # 至少3個延伸結果指標
            outcome_measurement += 3
            details["extended_outcomes"] = "✅ 延伸結果追蹤"
        else:
            details["extended_outcomes"] = "⚠️ 延伸結果追蹤不足"
        
        integration_score += outcome_measurement
        
        return {
            "phase3_integration_score": integration_score,
            "max_score": max_score,
            "percentage": (integration_score / max_score) * 100,
            "details": details,
            "status": "excellent" if integration_score >= 24 else "good" if integration_score >= 18 else "needs_improvement"
        }
    
    def validate_phase4_internal_consistency(self, config: Dict) -> Dict[str, Any]:
        """驗證 Phase4 內部一致性"""
        consistency_score = 0
        max_score = 20
        details = {}
        
        epl_config = config.get("PHASE4_EPL_DECISION_HISTORY_TRACKING", {})
        
        # 決策類型分析一致性 (8分)
        decision_analytics = 0
        decision_type_analytics = epl_config.get("decision_tracking_architecture", {}).get("decision_type_analytics", {})
        
        # 檢查四種決策類型的完整追蹤
        required_decision_types = [
            "replacement_decision_tracking",
            "strengthening_decision_tracking", 
            "new_position_decision_tracking",
            "ignore_decision_tracking"
        ]
        
        for decision_type in required_decision_types:
            if decision_type in decision_type_analytics:
                decision_analytics += 2  # 8/4
        
        details["decision_type_completeness"] = f"✅ {sum(1 for dt in required_decision_types if dt in decision_type_analytics)}/4 決策類型追蹤"
        
        consistency_score += int(decision_analytics)
        
        # 學習系統一致性 (6分)
        learning_consistency = 0
        learning_config = epl_config.get("learning_and_optimization", {})
        
        required_learning = ["pattern_recognition", "adaptive_learning", "feedback_integration"]
        
        for learning_component in required_learning:
            if learning_component in learning_config:
                learning_consistency += 2  # 6/3
        
        details["learning_system_consistency"] = f"✅ {sum(1 for lc in required_learning if lc in learning_config)}/3 學習組件"
        
        consistency_score += int(learning_consistency)
        
        # 報告分析一致性 (6分)
        reporting_consistency = 0
        reporting_config = epl_config.get("reporting_and_analytics", {})
        
        if "real_time_dashboards" in reporting_config:
            reporting_consistency += 3
            details["real_time_reporting"] = "✅ 即時報告"
        else:
            details["real_time_reporting"] = "❌ 缺少即時報告"
        
        if "historical_analysis" in reporting_config:
            reporting_consistency += 3
            details["historical_analysis"] = "✅ 歷史分析"
        else:
            details["historical_analysis"] = "❌ 缺少歷史分析"
        
        consistency_score += reporting_consistency
        
        return {
            "phase4_consistency_score": consistency_score,
            "max_score": max_score,
            "percentage": (consistency_score / max_score) * 100,
            "details": details,
            "status": "excellent" if consistency_score >= 16 else "good" if consistency_score >= 12 else "needs_improvement"
        }
    
    def check_data_flow_completeness(self, config: Dict) -> Dict[str, Any]:
        """檢查數據流完整性"""
        completeness_score = 0
        max_score = 20
        details = {}
        
        epl_config = config.get("PHASE4_EPL_DECISION_HISTORY_TRACKING", {})
        
        # 數據存儲完整性 (10分)
        storage_completeness = 0
        storage_config = epl_config.get("data_storage_and_retrieval", {})
        
        if "decision_data_storage" in storage_config:
            storage_data = storage_config["decision_data_storage"]
            
            if "raw_decision_data" in storage_data:
                storage_completeness += 5
                details["raw_data_storage"] = "✅ 原始決策數據存儲"
            else:
                details["raw_data_storage"] = "❌ 缺少原始數據存儲"
            
            if "aggregated_analytics" in storage_data:
                storage_completeness += 5
                details["aggregated_storage"] = "✅ 聚合分析數據存儲"
            else:
                details["aggregated_storage"] = "❌ 缺少聚合數據存儲"
        
        completeness_score += storage_completeness
        
        # API 接口完整性 (10分)
        api_completeness = 0
        api_config = epl_config.get("api_interfaces", {})
        
        required_apis = ["decision_tracking_api", "performance_analytics_api", "learning_data_api"]
        
        for api in required_apis:
            if api in api_config:
                api_completeness += 3.33  # 10/3
        
        details["api_completeness"] = f"✅ {sum(1 for api in required_apis if api in api_config)}/3 API 接口"
        
        completeness_score += int(api_completeness)
        
        return {
            "completeness_score": completeness_score,
            "max_score": max_score,
            "percentage": (completeness_score / max_score) * 100,
            "details": details,
            "status": "excellent" if completeness_score >= 16 else "good" if completeness_score >= 12 else "needs_improvement"
        }
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """生成驗證報告"""
        print("🔍 EPL Decision History Tracking 數據流匹配驗證")
        print("=" * 70)
        
        # 載入配置
        config = self.load_epl_config()
        if not config:
            return {"validation_status": "failed", "error": "無法載入配置"}
        
        print("✅ EPL 配置載入成功")
        
        # 各項驗證
        phase1_validation = self.validate_phase1_data_integration(config)
        phase2_validation = self.validate_phase2_data_integration(config)
        phase3_validation = self.validate_phase3_data_integration(config)
        phase4_validation = self.validate_phase4_internal_consistency(config)
        completeness_validation = self.check_data_flow_completeness(config)
        
        # 計算總分
        total_score = (
            phase1_validation["phase1_integration_score"] +
            phase2_validation["phase2_integration_score"] +
            phase3_validation["phase3_integration_score"] +
            phase4_validation["phase4_consistency_score"] +
            completeness_validation["completeness_score"]
        )
        max_total_score = (
            phase1_validation["max_score"] +
            phase2_validation["max_score"] +
            phase3_validation["max_score"] +
            phase4_validation["max_score"] +
            completeness_validation["max_score"]
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
            "detailed_validations": {
                "phase1_integration": phase1_validation,
                "phase2_integration": phase2_validation,
                "phase3_integration": phase3_validation,
                "phase4_consistency": phase4_validation,
                "data_flow_completeness": completeness_validation
            },
            "recommendations": self._generate_recommendations(overall_percentage, [
                phase1_validation, phase2_validation, phase3_validation, 
                phase4_validation, completeness_validation
            ])
        }
        
        # 打印結果
        self._print_results(report)
        
        return report
    
    def _get_grade(self, percentage: float) -> str:
        """獲取評級"""
        if percentage >= 95:
            return "A+ (完美匹配)"
        elif percentage >= 85:
            return "A (優秀匹配)"
        elif percentage >= 75:
            return "B+ (良好匹配)"
        elif percentage >= 65:
            return "B (可接受匹配)"
        elif percentage >= 55:
            return "C (需改進匹配)"
        else:
            return "D (需重構匹配)"
    
    def _generate_recommendations(self, overall_percentage, validations) -> List[str]:
        """生成建議"""
        recommendations = []
        
        if overall_percentage >= 90:
            recommendations.append("數據流匹配優秀，可以繼續 Python 實現優化")
        elif overall_percentage >= 80:
            recommendations.append("數據流匹配良好，建議小幅調整後繼續")
        else:
            # 檢查具體問題
            for validation in validations:
                if validation.get("percentage", 0) < 70:
                    recommendations.append("需要修正低分驗證項目的數據流配置")
        
        # 具體建議
        if validations[0].get("percentage", 0) < 80:  # Phase1
            recommendations.append("改進 Phase1 信號數據擷取配置")
        if validations[1].get("percentage", 0) < 80:  # Phase2
            recommendations.append("完善 Phase2 預評估結果整合")
        if validations[2].get("percentage", 0) < 80:  # Phase3
            recommendations.append("加強 Phase3 執行追蹤配置")
        
        return recommendations if recommendations else ["數據流配置需要全面檢討"]
    
    def _print_results(self, report: Dict):
        """打印結果"""
        print(f"\n📊 總體評分: {report['overall_score']['percentage']} - {report['overall_score']['grade']}")
        
        print("\n📋 詳細驗證:")
        for category, details in report["detailed_validations"].items():
            percentage = details["percentage"]
            status_icon = "✅" if percentage >= 80 else "⚠️" if percentage >= 60 else "❌"
            print(f"  {status_icon} {category}: {percentage:.1f}% ({details['status']})")
            
            if 'details' in details:
                for detail_key, detail_value in details["details"].items():
                    print(f"    {detail_value}")
        
        print("\n💡 建議:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")

def main():
    """主函數"""
    validator = EPLDataFlowValidator()
    report = validator.generate_validation_report()
    
    print(f"\n🎯 EPL 數據流匹配驗證完成")
    print(f"📊 最終評分: {report['overall_score']['percentage']}")
    
    # 判斷是否可以繼續
    percentage = float(report['overall_score']['percentage'].rstrip('%'))
    if percentage >= 80:
        print("✅ 數據流匹配良好，可以繼續 Python 實現優化")
        return True
    else:
        print("❌ 數據流匹配需要改進，建議先修正 JSON 配置")
        return False

if __name__ == "__main__":
    main()
