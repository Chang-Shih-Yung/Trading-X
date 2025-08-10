"""
🔍 EPL Decision History Tracking JSON 配置驗證
=============================================

第3組件配置結構分析和驗證
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class EPLConfigValidator:
    """EPL 決策歷史追蹤配置驗證器"""
    
    def __init__(self):
        self.config_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring/3_epl_decision_history_tracking/epl_decision_history_tracking_config.json")
        self.python_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring/3_epl_decision_history_tracking/epl_decision_history_tracking.py")
        
    def load_and_analyze_config(self) -> Dict[str, Any]:
        """載入並分析配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return {
                "config_loaded": True,
                "config_data": config,
                "file_size": self.config_path.stat().st_size,
                "structure_analysis": self._analyze_config_structure(config)
            }
            
        except Exception as e:
            return {
                "config_loaded": False,
                "error": str(e),
                "file_exists": self.config_path.exists()
            }
    
    def _analyze_config_structure(self, config: Dict) -> Dict[str, Any]:
        """分析配置結構"""
        analysis = {
            "root_keys": list(config.keys()),
            "structure_depth": self._calculate_depth(config),
            "total_config_items": self._count_config_items(config),
            "section_analysis": {}
        }
        
        # 檢查主要部分
        if "PHASE4_EPL_DECISION_HISTORY_TRACKING" in config:
            epl_config = config["PHASE4_EPL_DECISION_HISTORY_TRACKING"]
            analysis["section_analysis"] = {
                "main_sections": list(epl_config.keys()),
                "decision_tracking": "decision_tracking_architecture" in epl_config,
                "historical_analytics": "historical_analytics" in epl_config,
                "performance_monitoring": "performance_monitoring" in epl_config,
                "data_management": "data_management" in epl_config
            }
        
        return analysis
    
    def _calculate_depth(self, obj, current_depth=0):
        """計算配置深度"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth
    
    def _count_config_items(self, obj):
        """計算配置項目數量"""
        if isinstance(obj, dict):
            return len(obj) + sum(self._count_config_items(v) for v in obj.values())
        elif isinstance(obj, list):
            return len(obj) + sum(self._count_config_items(item) for item in obj)
        else:
            return 1
    
    def validate_phase_integration(self, config: Dict) -> Dict[str, Any]:
        """驗證 Phase 整合"""
        integration_score = 0
        max_score = 40
        details = {}
        
        epl_config = config.get("PHASE4_EPL_DECISION_HISTORY_TRACKING", {})
        
        # Phase1 整合檢查 (10分)
        phase1_integration = 0
        if "decision_tracking_architecture" in epl_config:
            decision_arch = epl_config["decision_tracking_architecture"]
            if "signal_decision_correlation" in decision_arch:
                phase1_integration += 5
            if "signal_outcome_tracking" in decision_arch:
                phase1_integration += 5
        
        details["phase1_signal_correlation"] = f"{phase1_integration}/10"
        integration_score += phase1_integration
        
        # Phase2 整合檢查 (10分)
        phase2_integration = 0
        if "decision_tracking_architecture" in epl_config:
            decision_arch = epl_config["decision_tracking_architecture"]
            if "epl_decision_recording" in decision_arch:
                phase2_integration += 5
            if "context_preservation" in decision_arch:
                phase2_integration += 5
        
        details["phase2_epl_integration"] = f"{phase2_integration}/10"
        integration_score += phase2_integration
        
        # Phase3 整合檢查 (10分)
        phase3_integration = 0
        if "performance_monitoring" in epl_config:
            perf_config = epl_config["performance_monitoring"]
            if "execution_outcome_tracking" in perf_config:
                phase3_integration += 5
            if "decision_effectiveness" in perf_config:
                phase3_integration += 5
        
        details["phase3_execution_tracking"] = f"{phase3_integration}/10"
        integration_score += phase3_integration
        
        # Phase4 自身整合檢查 (10分)
        phase4_integration = 0
        if "historical_analytics" in epl_config:
            hist_config = epl_config["historical_analytics"]
            if "decision_pattern_analysis" in hist_config:
                phase4_integration += 3
            if "performance_trend_analysis" in hist_config:
                phase4_integration += 3
            if "success_rate_analytics" in hist_config:
                phase4_integration += 4
        
        details["phase4_analytics"] = f"{phase4_integration}/10"
        integration_score += phase4_integration
        
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
        if "decision_tracking_architecture" in epl_config:
            arch = epl_config["decision_tracking_architecture"]
            if "decision_record_format" in arch:
                decision_structure += 5
            if "metadata_structure" in arch:
                decision_structure += 5
        
        details["decision_record_structure"] = f"{decision_structure}/10"
        compatibility_score += decision_structure
        
        # 歷史數據管理 (10分)  
        history_management = 0
        if "data_management" in epl_config:
            data_mgmt = epl_config["data_management"]
            if "retention_policies" in data_mgmt:
                history_management += 5
            if "archival_strategies" in data_mgmt:
                history_management += 5
        
        details["history_data_management"] = f"{history_management}/10"
        compatibility_score += history_management
        
        # 查詢和檢索 (10分)
        query_capabilities = 0
        if "historical_analytics" in epl_config:
            analytics = epl_config["historical_analytics"]
            if "query_optimization" in analytics:
                query_capabilities += 5
            if "search_capabilities" in analytics:
                query_capabilities += 5
        
        details["query_and_retrieval"] = f"{query_capabilities}/10"
        compatibility_score += query_capabilities
        
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
        
        # 決策效果監控 (10分)
        effectiveness_monitoring = 0
        if "performance_monitoring" in epl_config:
            perf = epl_config["performance_monitoring"]
            if "decision_effectiveness" in perf:
                effectiveness_monitoring += 5
            if "success_rate_tracking" in perf:
                effectiveness_monitoring += 5
        
        details["decision_effectiveness"] = f"{effectiveness_monitoring}/10"
        monitoring_score += effectiveness_monitoring
        
        # 模式分析 (10分)
        pattern_analysis = 0
        if "historical_analytics" in epl_config:
            analytics = epl_config["historical_analytics"]
            if "decision_pattern_analysis" in analytics:
                pattern_analysis += 5
            if "trend_identification" in analytics:
                pattern_analysis += 5
        
        details["pattern_analysis"] = f"{pattern_analysis}/10"
        monitoring_score += pattern_analysis
        
        # 實時追蹤 (10分)
        realtime_tracking = 0
        if "decision_tracking_architecture" in epl_config:
            tracking = epl_config["decision_tracking_architecture"]
            if "real_time_recording" in tracking:
                realtime_tracking += 5
            if "immediate_feedback" in tracking:
                realtime_tracking += 5
        
        details["realtime_tracking"] = f"{realtime_tracking}/10"
        monitoring_score += realtime_tracking
        
        return {
            "monitoring_score": monitoring_score,
            "max_score": max_score,
            "percentage": (monitoring_score / max_score) * 100,
            "details": details,
            "status": "excellent" if monitoring_score >= 24 else "good" if monitoring_score >= 18 else "needs_improvement"
        }
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """生成驗證報告"""
        print("🔍 開始 EPL Decision History Tracking JSON 配置驗證")
        print("=" * 60)
        
        # 載入配置
        config_analysis = self.load_and_analyze_config()
        
        if not config_analysis.get("config_loaded"):
            return {
                "validation_status": "failed",
                "error": config_analysis.get("error"),
                "recommendations": ["檢查配置文件路徑", "修復 JSON 格式錯誤"]
            }
        
        config = config_analysis["config_data"]
        structure = config_analysis["structure_analysis"]
        
        print(f"✅ 配置檔案載入成功 ({config_analysis['file_size']} bytes)")
        print(f"📊 配置結構深度: {structure['structure_depth']}")
        print(f"📋 總配置項目: {structure['total_config_items']}")
        print(f"🔧 主要根鍵: {structure['root_keys']}")
        
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
            "config_file": str(self.config_path),
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
            "config_structure": structure,
            "recommendations": self._generate_recommendations(
                phase_integration, data_compatibility, monitoring_features
            )
        }
        
        # 打印詳細結果
        self._print_detailed_results(report)
        
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
    
    def _generate_recommendations(self, phase_integration, data_compatibility, monitoring_features) -> List[str]:
        """生成建議"""
        recommendations = []
        
        if phase_integration["percentage"] < 80:
            recommendations.append("加強 Phase 間整合配置")
        
        if data_compatibility["percentage"] < 80:
            recommendations.append("優化數據結構相容性")
        
        if monitoring_features["percentage"] < 80:
            recommendations.append("完善監控功能配置")
        
        if not recommendations:
            recommendations.append("配置品質優秀，建議維持現狀")
        
        return recommendations
    
    def _print_detailed_results(self, report: Dict):
        """打印詳細結果"""
        print(f"\n📊 總體評分: {report['overall_score']['percentage']} - {report['overall_score']['grade']}")
        
        print("\n📋 詳細評分:")
        for category, details in report["detailed_scores"].items():
            percentage = details["percentage"]
            status_icon = "✅" if percentage >= 80 else "⚠️" if percentage >= 60 else "❌"
            print(f"  {status_icon} {category}: {percentage:.1f}% ({details['status']})")
            
            for detail_key, detail_value in details["details"].items():
                print(f"    - {detail_key}: {detail_value}")
        
        print("\n💡 建議事項:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")

def main():
    """主函數"""
    validator = EPLConfigValidator()
    report = validator.generate_validation_report()
    
    # 儲存報告
    report_path = Path("epl_config_validation_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 詳細報告已儲存至: {report_path}")

if __name__ == "__main__":
    main()
