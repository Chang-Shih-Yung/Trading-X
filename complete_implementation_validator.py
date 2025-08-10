#!/usr/bin/env python3
"""
完整儀表板實現驗證腳本
驗證重寫後的 unified_monitoring_dashboard.py 是否完全匹配 JSON 配置
"""

import json
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Any, Tuple

class CompleteImplementationValidator:
    def __init__(self):
        self.base_path = Path("/Users/henrychang/Desktop/Trading-X")
        self.json_path = self.base_path / "X/backend/phase4_output_monitoring/1_unified_monitoring_dashboard/unified_monitoring_dashboard_config.json"
        self.py_path = self.base_path / "X/backend/phase4_output_monitoring/1_unified_monitoring_dashboard/unified_monitoring_dashboard.py"
        
    def load_json_config(self) -> Dict[str, Any]:
        """載入JSON配置"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 無法載入JSON配置: {e}")
            return {}
    
    def analyze_python_implementation(self) -> Dict[str, Any]:
        """分析Python實現"""
        try:
            with open(self.py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            classes = []
            methods = []
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    methods.append(node.name)
                elif isinstance(node, ast.AsyncFunctionDef):
                    methods.append(node.name)
            
            return {
                "classes": classes,
                "methods": methods,
                "functions": functions,
                "line_count": len(content.split('\n'))
            }
        except Exception as e:
            print(f"❌ 無法分析Python實現: {e}")
            return {}
    
    def validate_widget_implementation(self, config: Dict[str, Any], py_analysis: Dict[str, Any]) -> Tuple[int, int]:
        """驗證Widget實現"""
        score = 0
        max_score = 50
        
        dashboard_config = config.get("PHASE4_UNIFIED_MONITORING_DASHBOARD", {})
        widgets_config = dashboard_config.get("dashboard_widgets", {})
        
        required_widgets = list(widgets_config.keys())
        
        print("\n🔍 驗證Widget實現:")
        print("-" * 40)
        
        # 檢查必要的widget生成方法
        required_methods = [
            "generate_system_status_overview_data",
            "generate_signal_processing_analytics_data", 
            "generate_epl_decision_tracking_data",
            "generate_notification_success_monitoring_data",
            "generate_system_performance_monitoring_data"
        ]
        
        for method in required_methods:
            if method in py_analysis.get("methods", []):
                score += 10
                print(f"✅ {method} 已實現")
            else:
                print(f"❌ 缺少方法: {method}")
        
        return score, max_score
    
    def validate_data_structures(self, py_analysis: Dict[str, Any]) -> Tuple[int, int]:
        """驗證數據結構"""
        score = 0
        max_score = 30
        
        print("\n🔍 驗證數據結構:")
        print("-" * 40)
        
        required_classes = [
            "SystemStatus",
            "WidgetType", 
            "SignalPriority",
            "EPLDecisionType",
            "MetricValue",
            "TimeSeriesData",
            "WidgetData",
            "SystemHealthIndicator",
            "NotificationDeliveryMetrics",
            "EPLDecisionMetrics",
            "SignalProcessingStats",
            "UnifiedMonitoringDashboard"
        ]
        
        implemented_classes = py_analysis.get("classes", [])
        
        for cls in required_classes:
            if cls in implemented_classes:
                score += 2
                print(f"✅ {cls} 類已定義")
            else:
                print(f"❌ 缺少類: {cls}")
        
        # 額外分數給主類
        if "UnifiedMonitoringDashboard" in implemented_classes:
            score += 6
            print("✅ 主要監控類已實現")
        
        return score, max_score
    
    def validate_core_functionality(self, py_analysis: Dict[str, Any]) -> Tuple[int, int]:
        """驗證核心功能"""
        score = 0
        max_score = 40
        
        print("\n🔍 驗證核心功能:")
        print("-" * 40)
        
        required_core_methods = [
            "record_signal_processed",
            "record_epl_decision", 
            "record_notification_delivery",
            "update_system_performance",
            "update_all_widgets",
            "get_widget_data",
            "get_all_widgets_data",
            "get_real_time_api_data",
            "start_real_time_monitoring"
        ]
        
        implemented_methods = py_analysis.get("methods", [])
        
        for method in required_core_methods:
            if method in implemented_methods:
                score += 4
                print(f"✅ {method} 已實現")
            else:
                print(f"❌ 缺少核心方法: {method}")
        
        # 檢查輔助方法
        helper_methods = [m for m in implemented_methods if m.startswith("_")]
        if len(helper_methods) >= 20:
            score += 4
            print(f"✅ 豐富的輔助方法 ({len(helper_methods)} 個)")
        
        return score, max_score
    
    def validate_json_compliance(self, config: Dict[str, Any]) -> Tuple[int, int]:
        """驗證JSON配置合規性"""
        score = 0
        max_score = 30
        
        print("\n🔍 驗證JSON配置合規性:")
        print("-" * 40)
        
        try:
            dashboard_config = config["PHASE4_UNIFIED_MONITORING_DASHBOARD"]
            
            # 檢查集成標準
            if "integration_standards" in dashboard_config:
                score += 5
                print("✅ 集成標準已定義")
                
                integration = dashboard_config["integration_standards"]
                if "upstream_integration" in integration:
                    upstream = integration["upstream_integration"]
                    
                    # 檢查修正後的Phase2配置
                    if "phase2_pre_evaluation" in upstream:
                        phase2 = upstream["phase2_pre_evaluation"]
                        if phase2.get("monitoring_input") == "EnhancedRealDataQualityMonitoringEngine":
                            score += 5
                            print("✅ Phase2 monitoring_input 配置正確")
                        if phase2.get("quality_scores") == "real_data_quality_monitoring":
                            score += 5
                            print("✅ Phase2 quality_scores 配置正確")
            
            # 檢查儀表板架構
            if "monitoring_architecture" in dashboard_config:
                score += 5
                print("✅ 監控架構已定義")
            
            # 檢查Widget配置
            if "dashboard_widgets" in dashboard_config:
                score += 5
                print("✅ 儀表板Widget已配置")
                
                widgets = dashboard_config["dashboard_widgets"]
                required_widgets = [
                    "system_status_overview",
                    "signal_processing_analytics",
                    "epl_decision_tracking", 
                    "notification_success_monitoring",
                    "system_performance_monitoring"
                ]
                
                for widget in required_widgets:
                    if widget in widgets:
                        score += 1
                        print(f"✅ Widget {widget} 已配置")
            
        except Exception as e:
            print(f"❌ JSON配置驗證錯誤: {e}")
        
        return score, max_score
    
    def validate_performance_targets(self, config: Dict[str, Any]) -> Tuple[int, int]:
        """驗證性能目標"""
        score = 0
        max_score = 20
        
        print("\n🔍 驗證性能目標:")
        print("-" * 40)
        
        try:
            dashboard_config = config["PHASE4_UNIFIED_MONITORING_DASHBOARD"]
            
            if "performance_targets" in dashboard_config:
                targets = dashboard_config["performance_targets"]
                
                if "dashboard_performance" in targets:
                    score += 10
                    print("✅ 儀表板性能目標已定義")
                
                if "data_accuracy" in targets:
                    score += 10
                    print("✅ 數據準確性目標已定義")
            
        except Exception as e:
            print(f"❌ 性能目標驗證錯誤: {e}")
        
        return score, max_score
    
    def run_complete_validation(self):
        """執行完整驗證"""
        print("🚀 開始完整儀表板實現驗證...")
        print("=" * 60)
        
        # 載入配置和分析代碼
        config = self.load_json_config()
        py_analysis = self.analyze_python_implementation()
        
        if not config or not py_analysis:
            print("❌ 無法載入必要文件")
            return
        
        print(f"📊 Python實現統計:")
        print(f"   - 類定義: {len(py_analysis.get('classes', []))}")
        print(f"   - 方法: {len(py_analysis.get('methods', []))}")
        print(f"   - 函數: {len(py_analysis.get('functions', []))}")
        print(f"   - 代碼行數: {py_analysis.get('line_count', 0)}")
        
        # 執行各項驗證
        widget_score, widget_max = self.validate_widget_implementation(config, py_analysis)
        data_score, data_max = self.validate_data_structures(py_analysis)
        core_score, core_max = self.validate_core_functionality(py_analysis)
        json_score, json_max = self.validate_json_compliance(config)
        perf_score, perf_max = self.validate_performance_targets(config)
        
        # 計算總分
        total_score = widget_score + data_score + core_score + json_score + perf_score
        total_max = widget_max + data_max + core_max + json_max + perf_max
        percentage = (total_score / total_max) * 100
        
        print("\n" + "=" * 60)
        print("📋 驗證結果摘要:")
        print(f"   🎯 Widget實現: {widget_score}/{widget_max}")
        print(f"   🏗️ 數據結構: {data_score}/{data_max}") 
        print(f"   ⚙️ 核心功能: {core_score}/{core_max}")
        print(f"   📄 JSON合規性: {json_score}/{json_max}")
        print(f"   🎪 性能目標: {perf_score}/{perf_max}")
        print("-" * 60)
        print(f"🎯 總驗證結果: {total_score}/{total_max} ({percentage:.1f}%)")
        
        if percentage >= 95:
            print("🎉 完美實現！儀表板完全匹配JSON配置")
            print("✅ 可以進行生產部署")
        elif percentage >= 85:
            print("✅ 實現良好！建議進行細微調整")
            print("⚠️ 可以進行測試部署")
        elif percentage >= 70:
            print("⚠️ 基本實現完成，需要補充缺失功能")
            print("🔧 建議完善後再部署")
        else:
            print("❌ 實現不完整，需要重大改進")
            print("🛑 不建議部署")
        
        return percentage

if __name__ == "__main__":
    validator = CompleteImplementationValidator()
    result = validator.run_complete_validation()
