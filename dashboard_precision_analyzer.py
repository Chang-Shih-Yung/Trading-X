"""
🔍 統一監控儀表板精確深度分析工具
==========================================

比較 unified_monitoring_dashboard.py 與 unified_monitoring_dashboard_config.json
確保 100% 完整匹配，檢測缺失數據、邏輯斷點、多餘代碼

Author: Trading X System  
Date: 2025-08-09
Purpose: Precision Deep Analysis for Dashboard Compliance
"""

import json
import logging
from typing import Dict, List, Any, Set, Tuple
from pathlib import Path
import ast
import inspect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardPrecisionAnalyzer:
    """儀表板精確分析器"""
    
    def __init__(self):
        self.json_config = None
        self.python_code = None
        self.analysis_results = {
            "missing_components": [],
            "extra_components": [],
            "logic_mismatches": [],
            "data_flow_gaps": [],
            "compliance_score": 0.0
        }
        
    def analyze_dashboard_compliance(self) -> Dict[str, Any]:
        """執行儀表板合規性分析"""
        
        logger.info("🔍 開始儀表板精確深度分析...")
        
        # 1. 載入 JSON 配置和 Python 代碼
        self._load_configurations()
        
        # 2. 分析組件完整性
        self._analyze_widget_completeness()
        
        # 3. 分析數據結構匹配
        self._analyze_data_structure_matching()
        
        # 4. 分析方法實現完整性
        self._analyze_method_implementation()
        
        # 5. 分析配置使用情況
        self._analyze_config_usage()
        
        # 6. 分析數據流邏輯
        self._analyze_data_flow_logic()
        
        # 7. 計算合規性分數
        self._calculate_compliance_score()
        
        # 8. 生成修正建議
        self._generate_fix_recommendations()
        
        return self.analysis_results
    
    def _load_configurations(self):
        """載入配置文件和代碼"""
        try:
            # 載入 JSON 配置
            json_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring/1_unified_monitoring_dashboard/unified_monitoring_dashboard_config.json")
            with open(json_path, 'r', encoding='utf-8') as f:
                self.json_config = json.load(f)
            
            # 載入 Python 代碼
            py_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring/1_unified_monitoring_dashboard/unified_monitoring_dashboard.py")
            with open(py_path, 'r', encoding='utf-8') as f:
                self.python_code = f.read()
                
            logger.info("✅ 配置文件和代碼載入完成")
            
        except Exception as e:
            logger.error(f"❌ 載入配置失敗: {e}")
            raise
    
    def _analyze_widget_completeness(self):
        """分析組件完整性"""
        
        # 從 JSON 提取預期的組件
        json_widgets = set(self.json_config["PHASE4_UNIFIED_MONITORING_DASHBOARD"]["dashboard_widgets"].keys())
        
        # 從 Python 代碼分析實際實現的組件
        python_widgets = self._extract_python_widgets()
        
        # 檢查缺失組件
        missing_widgets = json_widgets - python_widgets
        if missing_widgets:
            self.analysis_results["missing_components"].extend([
                f"缺失組件: {widget}" for widget in missing_widgets
            ])
        
        # 檢查多餘組件
        extra_widgets = python_widgets - json_widgets
        if extra_widgets:
            self.analysis_results["extra_components"].extend([
                f"多餘組件: {widget}" for widget in extra_widgets
            ])
        
        logger.info(f"📊 組件分析: JSON定義 {len(json_widgets)} 個，Python實現 {len(python_widgets)} 個")
        logger.info(f"   缺失: {len(missing_widgets)} 個，多餘: {len(extra_widgets)} 個")
    
    def _extract_python_widgets(self) -> Set[str]:
        """從 Python 代碼提取組件"""
        widgets = set()
        
        # 分析 widget_data 字典的 keys
        lines = self.python_code.split('\n')
        for line in lines:
            if 'widget_data[' in line and '].data' in line:
                # 提取 widget_id
                start = line.find('widget_data["') + 13
                end = line.find('"]', start)
                if start > 12 and end > start:
                    widget_id = line[start:end]
                    widgets.add(widget_id)
        
        return widgets
    
    def _analyze_data_structure_matching(self):
        """分析數據結構匹配"""
        
        dashboard_config = self.json_config["PHASE4_UNIFIED_MONITORING_DASHBOARD"]
        
        # 檢查每個組件的數據結構
        for widget_id, widget_config in dashboard_config["dashboard_widgets"].items():
            self._check_widget_data_structure(widget_id, widget_config)
    
    def _check_widget_data_structure(self, widget_id: str, widget_config: Dict):
        """檢查單個組件的數據結構"""
        
        # 從 Python 代碼中找到對應的數據設置
        method_name = f"_update_{widget_id}"
        
        if method_name not in self.python_code:
            self.analysis_results["missing_components"].append(
                f"缺失方法: {method_name} (對應組件 {widget_id})"
            )
            return
        
        # 檢查組件內的子組件
        if "components" in widget_config:
            for component_name, component_config in widget_config["components"].items():
                self._check_component_implementation(widget_id, component_name, component_config)
    
    def _check_component_implementation(self, widget_id: str, component_name: str, component_config: Dict):
        """檢查組件實現"""
        
        # 檢查 metrics 是否在 Python 代碼中實現
        if "metrics" in component_config:
            for metric in component_config["metrics"]:
                if metric not in self.python_code:
                    self.analysis_results["missing_components"].append(
                        f"缺失指標實現: {widget_id}.{component_name}.{metric}"
                    )
        
        # 檢查 chart_type 對應的邏輯
        if "chart_type" in component_config:
            chart_type = component_config["chart_type"]
            # 這裡應該有對應的圖表數據準備邏輯
            if component_name not in self.python_code:
                self.analysis_results["logic_mismatches"].append(
                    f"缺失圖表邏輯: {widget_id}.{component_name} ({chart_type})"
                )
    
    def _analyze_method_implementation(self):
        """分析方法實現完整性"""
        
        # 檢查所有必需的更新方法
        required_methods = [
            "_update_system_status_overview",
            "_update_signal_processing_analytics", 
            "_update_epl_decision_tracking",
            "_update_notification_success_monitoring",
            "_update_system_performance_monitoring"
        ]
        
        for method in required_methods:
            if method not in self.python_code:
                self.analysis_results["missing_components"].append(f"缺失方法: {method}")
            else:
                # 檢查方法內部邏輯完整性
                self._check_method_logic_completeness(method)
    
    def _check_method_logic_completeness(self, method_name: str):
        """檢查方法邏輯完整性"""
        
        # 對應的 JSON 配置要求
        widget_requirements = {
            "_update_system_status_overview": [
                "phase1_signal_generation", "phase2_pre_evaluation", 
                "phase3_execution_policy", "notification_system"
            ],
            "_update_signal_processing_analytics": [
                "signal_volume_chart", "processing_latency_chart", 
                "quality_distribution_histogram"
            ],
            "_update_epl_decision_tracking": [
                "decision_type_pie_chart", "decision_timeline", 
                "success_rate_metrics"
            ],
            "_update_notification_success_monitoring": [
                "delivery_success_matrix", "notification_volume_chart", 
                "user_engagement_analytics"
            ],
            "_update_system_performance_monitoring": [
                "resource_utilization", "throughput_metrics", 
                "error_rate_monitoring"
            ]
        }
        
        if method_name in widget_requirements:
            required_components = widget_requirements[method_name]
            for component in required_components:
                if component not in self.python_code:
                    self.analysis_results["missing_components"].append(
                        f"缺失組件實現: {method_name} 中的 {component}"
                    )
    
    def _analyze_config_usage(self):
        """分析配置使用情況"""
        
        # 檢查 JSON 配置中的關鍵設定是否在 Python 中使用
        important_configs = [
            "refresh_rate",
            "alert_thresholds", 
            "performance_targets",
            "data_format_consistency"
        ]
        
        for config in important_configs:
            if config not in self.python_code:
                self.analysis_results["missing_components"].append(f"未使用的配置: {config}")
    
    def _analyze_data_flow_logic(self):
        """分析數據流邏輯"""
        
        # 檢查 upstream_integration 是否正確實現
        upstream_integration = self.json_config["PHASE4_UNIFIED_MONITORING_DASHBOARD"]["integration_standards"]["upstream_integration"]
        
        # 檢查 Phase1 整合
        if "phase1_signal_pool" in upstream_integration:
            phase1_requirements = upstream_integration["phase1_signal_pool"]
            if "unified_signal_candidate_pool_v3" not in self.python_code:
                self.analysis_results["data_flow_gaps"].append(
                    "缺失 Phase1 signal pool 整合: unified_signal_candidate_pool_v3"
                )
        
        # 檢查 Phase2 整合
        if "phase2_pre_evaluation" in upstream_integration:
            phase2_requirements = upstream_integration["phase2_pre_evaluation"]
            if "parallel_monitoring_metrics" not in self.python_code:
                self.analysis_results["data_flow_gaps"].append(
                    "缺失 Phase2 pre-evaluation 整合: parallel_monitoring_metrics"
                )
        
        # 檢查 Phase3 整合
        if "phase3_execution_policy" in upstream_integration:
            phase3_requirements = upstream_integration["phase3_execution_policy"]
            if "EPLDecisionResult" in self.python_code:
                logger.info("✅ Phase3 EPL 整合已實現")
            else:
                self.analysis_results["data_flow_gaps"].append(
                    "缺失 Phase3 EPL 整合: EPLDecisionResult"
                )
    
    def _calculate_compliance_score(self):
        """計算合規性分數"""
        
        total_issues = (
            len(self.analysis_results["missing_components"]) +
            len(self.analysis_results["extra_components"]) + 
            len(self.analysis_results["logic_mismatches"]) +
            len(self.analysis_results["data_flow_gaps"])
        )
        
        # 基準分數 100，每個問題扣 5 分
        self.analysis_results["compliance_score"] = max(0, 100 - (total_issues * 5))
        
        logger.info(f"📊 合規性分數: {self.analysis_results['compliance_score']}/100")
    
    def _generate_fix_recommendations(self):
        """生成修正建議"""
        
        self.analysis_results["fix_recommendations"] = []
        
        # 缺失組件的修正建議
        if self.analysis_results["missing_components"]:
            self.analysis_results["fix_recommendations"].append({
                "category": "缺失組件",
                "priority": "高",
                "actions": [
                    "添加所有 JSON 配置中定義的組件實現",
                    "確保每個 widget 都有對應的 _update 方法",
                    "實現所有子組件的數據準備邏輯"
                ]
            })
        
        # 多餘組件的修正建議
        if self.analysis_results["extra_components"]:
            self.analysis_results["fix_recommendations"].append({
                "category": "多餘組件", 
                "priority": "中",
                "actions": [
                    "移除所有未在 JSON 配置中定義的組件",
                    "清理不需要的方法和變數",
                    "確保代碼簡潔且符合規範"
                ]
            })
        
        # 邏輯不匹配的修正建議
        if self.analysis_results["logic_mismatches"]:
            self.analysis_results["fix_recommendations"].append({
                "category": "邏輯不匹配",
                "priority": "高", 
                "actions": [
                    "調整實現邏輯以符合 JSON 規範",
                    "確保圖表類型與配置一致",
                    "驗證數據格式和結構"
                ]
            })
        
        # 數據流缺口的修正建議
        if self.analysis_results["data_flow_gaps"]:
            self.analysis_results["fix_recommendations"].append({
                "category": "數據流缺口",
                "priority": "高",
                "actions": [
                    "實現完整的 upstream integration",
                    "添加 Phase1-Phase3 數據流整合",
                    "確保數據格式一致性"
                ]
            })
    
    def print_analysis_report(self):
        """打印分析報告"""
        
        print("\n" + "="*80)
        print("🔍 統一監控儀表板精確深度分析報告")
        print("="*80)
        print(f"📊 合規性分數: {self.analysis_results['compliance_score']}/100")
        
        if self.analysis_results['compliance_score'] == 100:
            print("🎉 完美匹配！代碼與 JSON 規範 100% 一致")
        else:
            print("⚠️  發現不匹配項目，需要修正")
        
        print()
        
        # 缺失組件
        if self.analysis_results["missing_components"]:
            print("❌ 缺失組件:")
            for item in self.analysis_results["missing_components"]:
                print(f"   • {item}")
            print()
        
        # 多餘組件
        if self.analysis_results["extra_components"]:
            print("➕ 多餘組件:")
            for item in self.analysis_results["extra_components"]:
                print(f"   • {item}")
            print()
        
        # 邏輯不匹配
        if self.analysis_results["logic_mismatches"]:
            print("🔄 邏輯不匹配:")
            for item in self.analysis_results["logic_mismatches"]:
                print(f"   • {item}")
            print()
        
        # 數據流缺口
        if self.analysis_results["data_flow_gaps"]:
            print("🔗 數據流缺口:")
            for item in self.analysis_results["data_flow_gaps"]:
                print(f"   • {item}")
            print()
        
        # 修正建議
        if self.analysis_results.get("fix_recommendations"):
            print("🔧 修正建議:")
            for rec in self.analysis_results["fix_recommendations"]:
                print(f"   📌 {rec['category']} (優先級: {rec['priority']})")
                for action in rec['actions']:
                    print(f"      - {action}")
            print()
        
        print("="*80)

def main():
    """主函數"""
    
    analyzer = DashboardPrecisionAnalyzer()
    
    print("🔍 啟動統一監控儀表板精確深度分析...")
    
    # 執行分析
    results = analyzer.analyze_dashboard_compliance()
    
    # 打印報告
    analyzer.print_analysis_report()
    
    return results

if __name__ == "__main__":
    main()
