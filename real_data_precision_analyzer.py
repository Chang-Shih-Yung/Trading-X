"""
🎯 Real Data Signal Quality Engine - 精確深度分析工具
專門分析 real_data_signal_quality_engine.py 與 JSON 規範的100%匹配度
"""

import json
import ast
import re
from typing import Dict, List, Any, Tuple
from pathlib import Path

class RealDataPrecisionAnalyzer:
    """Real Data 信號質量引擎精確分析器"""
    
    def __init__(self):
        self.json_spec_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase2_pre_evaluation/real_data_signal_quality_engine/real_data_signal_quality_engine.json"
        self.python_file_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase2_pre_evaluation/real_data_signal_quality_engine/real_data_signal_quality_engine.py"
        
        self.analysis_results = {
            "compliance_issues": [],
            "missing_components": [],
            "unused_code": [],
            "logic_mismatches": [],
            "data_flow_breaks": [],
            "performance_issues": []
        }
    
    def load_specifications(self) -> Tuple[Dict, str]:
        """載入 JSON 規範和 Python 代碼"""
        # 載入 JSON 規範
        with open(self.json_spec_path, 'r', encoding='utf-8') as f:
            json_spec = json.load(f)
        
        # 載入 Python 代碼
        with open(self.python_file_path, 'r', encoding='utf-8') as f:
            python_code = f.read()
        
        return json_spec, python_code
    
    def analyze_strategy_compliance(self, json_spec: Dict, python_code: str):
        """分析策略規範符合度"""
        engine_spec = json_spec["real_data_signal_quality_engine_dependency"]
        
        # 1. 檢查策略基本信息
        required_version = engine_spec["version"]  # "2.1.0"
        required_role = engine_spec["role"]  # "parallel_monitoring_not_blocking_main_flow"
        
        if required_version not in python_code:
            self.analysis_results["compliance_issues"].append({
                "category": "VERSION_MISMATCH",
                "severity": "HIGH",
                "details": f"JSON 規範版本 {required_version} 在代碼中未找到"
            })
        
        if "parallel" not in python_code.lower() or "monitoring" not in python_code.lower():
            self.analysis_results["compliance_issues"].append({
                "category": "ROLE_MISMATCH", 
                "severity": "CRITICAL",
                "details": f"代碼未體現所需角色: {required_role}"
            })
        
        # 2. 檢查模組類型
        module_type = engine_spec["module_type"]  # "enhanced_quality_monitoring_engine"
        if "enhanced" not in python_code.lower() or "quality_monitoring" not in python_code.lower():
            self.analysis_results["compliance_issues"].append({
                "category": "MODULE_TYPE_MISMATCH",
                "severity": "HIGH", 
                "details": f"代碼未體現模組類型: {module_type}"
            })
    
    def analyze_dependency_compliance(self, json_spec: Dict, python_code: str):
        """分析依賴規範符合度"""
        dependencies = json_spec["real_data_signal_quality_engine_dependency"]["strategy_dependency_graph"]["core_dependencies"]
        
        # 1. 檢查增強監控系統
        enhanced_monitoring = dependencies["enhanced_monitoring_systems"]
        
        # Phase1B 依賴檢查
        phase1b_spec = enhanced_monitoring["phase1b_volatility_adaptation"]
        if "phase1b_volatility_adaptation" not in python_code:
            self.analysis_results["missing_components"].append({
                "component": "phase1b_volatility_adaptation",
                "severity": "CRITICAL",
                "required_data_type": phase1b_spec["data_type"],
                "update_frequency": phase1b_spec["update_frequency"]
            })
        
        # Phase1C 依賴檢查
        phase1c_spec = enhanced_monitoring["phase1c_signal_standardization"]
        if "phase1c_signal_standardization" not in python_code:
            self.analysis_results["missing_components"].append({
                "component": "phase1c_signal_standardization", 
                "severity": "CRITICAL",
                "required_data_type": phase1c_spec["data_type"],
                "update_frequency": phase1c_spec["update_frequency"]
            })
        
        # 系統負載監控檢查 - 這是 JSON 中的新需求
        system_load_spec = enhanced_monitoring.get("system_load_monitor")
        if system_load_spec:
            if "system_load" not in python_code.lower() or "cpu_usage" not in python_code.lower():
                self.analysis_results["missing_components"].append({
                    "component": "system_load_monitor",
                    "severity": "CRITICAL", 
                    "required_data_type": system_load_spec["data_type"],
                    "thresholds": system_load_spec["thresholds"],
                    "details": "JSON 規範要求系統負載監控但代碼中缺失"
                })
        
        # Phase3 依賴檢查
        phase3_spec = enhanced_monitoring["phase3_market_analyzer"]
        if "phase3_market_analyzer" not in python_code:
            self.analysis_results["missing_components"].append({
                "component": "phase3_market_analyzer",
                "severity": "HIGH",
                "required_data_type": phase3_spec["data_type"],
                "update_frequency": phase3_spec["update_frequency"]
            })
        
        # pandas-ta 依賴檢查
        pandas_ta_spec = enhanced_monitoring["pandas_ta_indicators"] 
        if "pandas_ta" not in python_code.lower():
            self.analysis_results["missing_components"].append({
                "component": "pandas_ta_indicators",
                "severity": "HIGH", 
                "required_data_type": pandas_ta_spec["data_type"],
                "update_frequency": pandas_ta_spec["update_frequency"]
            })
    
    def analyze_enhanced_capabilities(self, json_spec: Dict, python_code: str):
        """分析增強功能符合度"""
        enhanced_capabilities = json_spec["real_data_signal_quality_engine_dependency"]["strategy_dependency_graph"]["core_dependencies"]["enhanced_monitoring_capabilities"]
        
        # 1. 微異常檢測
        micro_anomaly_spec = enhanced_capabilities["micro_anomaly_detection"]
        if "micro_anomaly" not in python_code.lower() and "anomaly_detection" not in python_code.lower():
            self.analysis_results["missing_components"].append({
                "component": "micro_anomaly_detection",
                "severity": "MEDIUM",
                "required_data_type": micro_anomaly_spec["data_type"],
                "monitoring_scope": micro_anomaly_spec["monitoring_scope"],
                "details": "JSON 規範要求微異常檢測功能"
            })
        
        # 2. 延遲觀察追蹤
        delayed_obs_spec = enhanced_capabilities["delayed_observation_tracking"]
        if "delayed_observation" not in python_code.lower() and "performance_tracking" not in python_code.lower():
            self.analysis_results["missing_components"].append({
                "component": "delayed_observation_tracking",
                "severity": "MEDIUM", 
                "required_data_type": delayed_obs_spec["data_type"],
                "tracking_duration": delayed_obs_spec["tracking_duration"],
                "details": "JSON 規範要求延遲觀察追蹤功能"
            })
        
        # 3. 動態閾值監控
        dynamic_threshold_spec = enhanced_capabilities["dynamic_threshold_monitoring"]
        if "dynamic_threshold" not in python_code.lower() and "adaptive_threshold" not in python_code.lower():
            self.analysis_results["missing_components"].append({
                "component": "dynamic_threshold_monitoring",
                "severity": "MEDIUM",
                "required_data_type": dynamic_threshold_spec["data_type"],
                "update_frequency": dynamic_threshold_spec["update_frequency"],
                "details": "JSON 規範要求動態閾值監控功能"
            })
    
    def analyze_computation_flow(self, json_spec: Dict, python_code: str):
        """分析計算流程符合度"""
        try:
            # 檢查不同可能的結構位置
            if "computation_flow" in json_spec:
                flow_spec = json_spec["computation_flow"]
            elif "computation_flow" in json_spec.get("real_data_signal_quality_engine_dependency", {}):
                flow_spec = json_spec["real_data_signal_quality_engine_dependency"]["computation_flow"]
            else:
                self.analysis_results["logic_mismatches"].append({
                    "category": "MISSING_COMPUTATION_FLOW",
                    "severity": "CRITICAL",
                    "details": "JSON 規範中找不到 computation_flow 配置"
                })
                return
            
            processing_layers = flow_spec["processing_layers"]
        except KeyError as e:
            self.analysis_results["logic_mismatches"].append({
                "category": "JSON_STRUCTURE_ERROR",
                "severity": "CRITICAL", 
                "details": f"JSON 規範結構錯誤，無法找到 computation_flow: {e}"
            })
            return
        
        # 1. 檢查處理層
        layer_0_spec = processing_layers["layer_0_signal_intake"]
        if "signal_intake" not in python_code.lower() and "real_data_quality_validation" not in python_code.lower():
            self.analysis_results["logic_mismatches"].append({
                "layer": "layer_0_signal_intake",
                "severity": "CRITICAL",
                "expected_input": layer_0_spec["input"], 
                "expected_processing": layer_0_spec["processing"],
                "expected_output": layer_0_spec["output"],
                "expected_time": layer_0_spec["expected_processing_time"],
                "details": "Layer 0 信號接收和驗證邏輯缺失"
            })
        
        layer_1_spec = processing_layers["layer_1_priority_classification"]
        if "priority_classification" not in python_code.lower() and "signal_priority_scoring" not in python_code.lower():
            self.analysis_results["logic_mismatches"].append({
                "layer": "layer_1_priority_classification",
                "severity": "CRITICAL",
                "expected_input": layer_1_spec["input"],
                "expected_processing": layer_1_spec["processing"], 
                "expected_output": layer_1_spec["output"],
                "expected_time": layer_1_spec["expected_processing_time"],
                "details": "Layer 1 優先級分類邏輯缺失"
            })
        
        layer_2_spec = processing_layers["layer_2_quality_control"]
        if "quality_control" not in python_code.lower() and "comprehensive_quality_assessment" not in python_code.lower():
            self.analysis_results["logic_mismatches"].append({
                "layer": "layer_2_quality_control", 
                "severity": "CRITICAL",
                "expected_input": layer_2_spec["input"],
                "expected_processing": layer_2_spec["processing"],
                "expected_output": layer_2_spec["output"],
                "expected_time": layer_2_spec["expected_processing_time"],
                "details": "Layer 2 質量控制邏輯缺失"
            })
        
        # 2. 檢查性能要求
        total_time = flow_spec["total_expected_processing_time"]  # "40ms (enhanced monitoring)"
        if "40ms" not in python_code and "enhanced monitoring" not in python_code.lower():
            self.analysis_results["performance_issues"].append({
                "category": "PROCESSING_TIME_COMPLIANCE",
                "severity": "HIGH",
                "expected": total_time,
                "details": "代碼中未體現總處理時間要求"
            })
        
        # 3. 檢查併發要求
        concurrency = flow_spec["concurrency_level"]  # "multi_threaded_async"
        if "multi_threaded" not in python_code.lower() and "async" not in python_code.lower():
            self.analysis_results["performance_issues"].append({
                "category": "CONCURRENCY_COMPLIANCE",
                "severity": "HIGH", 
                "expected": concurrency,
                "details": "代碼未體現多線程異步處理要求"
            })
    
    def analyze_unused_code(self, python_code: str):
        """分析未使用的代碼"""
        # 解析 AST
        try:
            tree = ast.parse(python_code)
        except SyntaxError as e:
            self.analysis_results["unused_code"].append({
                "category": "SYNTAX_ERROR",
                "severity": "CRITICAL",
                "details": f"代碼語法錯誤: {e}"
            })
            return
        
        # 收集定義的類和函數
        defined_classes = []
        defined_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                defined_classes.append(node.name)
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                defined_functions.append(node.name)
        
        # 檢查是否有未使用的元素
        for class_name in defined_classes:
            if python_code.count(class_name) <= 2:  # 只出現在定義處，未被使用
                self.analysis_results["unused_code"].append({
                    "category": "UNUSED_CLASS",
                    "severity": "LOW",
                    "name": class_name,
                    "details": f"類 {class_name} 可能未被使用"
                })
        
        # 檢查導入但未使用的模組
        imports = re.findall(r'from\s+(\S+)\s+import|import\s+(\S+)', python_code)
        for imp in imports:
            module = imp[0] or imp[1]
            if module and python_code.count(module) <= 1:
                self.analysis_results["unused_code"].append({
                    "category": "UNUSED_IMPORT",
                    "severity": "LOW", 
                    "name": module,
                    "details": f"導入的模組 {module} 可能未被使用"
                })
    
    def analyze_data_flow_integrity(self, json_spec: Dict, python_code: str):
        """分析數據流完整性"""
        # 檢查上游模組連接
        try:
            if "dependencies" in json_spec:
                deps_spec = json_spec["dependencies"]
            elif "dependencies" in json_spec.get("real_data_signal_quality_engine_dependency", {}):
                deps_spec = json_spec["real_data_signal_quality_engine_dependency"]["dependencies"]
            else:
                self.analysis_results["data_flow_breaks"].append({
                    "category": "MISSING_DEPENDENCIES_CONFIG",
                    "severity": "HIGH",
                    "details": "JSON 規範中找不到 dependencies 配置"
                })
                return
            
            upstream_modules = deps_spec.get("upstream_modules", [])
        except KeyError as e:
            self.analysis_results["data_flow_breaks"].append({
                "category": "DEPENDENCIES_STRUCTURE_ERROR",
                "severity": "HIGH",
                "details": f"依賴結構錯誤: {e}"
            })
            return
        
        for upstream in upstream_modules:
            module_name = upstream["module"]
            if module_name not in python_code:
                self.analysis_results["data_flow_breaks"].append({
                    "category": "MISSING_UPSTREAM_CONNECTION",
                    "severity": "CRITICAL" if upstream["critical"] else "HIGH",
                    "module": module_name,
                    "type": upstream["type"],
                    "timeout": upstream["timeout"],
                    "details": f"缺少與上游模組 {module_name} 的連接"
                })
        
        # 檢查下游模組連接
        downstream_modules = deps_spec.get("downstream_modules", [])
        
        for downstream in downstream_modules:
            module_name = downstream["module"]
            if module_name not in python_code:
                self.analysis_results["data_flow_breaks"].append({
                    "category": "MISSING_DOWNSTREAM_CONNECTION",
                    "severity": "HIGH",
                    "module": module_name,
                    "type": downstream["type"],
                    "delivery_guarantee": downstream["delivery_guarantee"],
                    "details": f"缺少與下游模組 {module_name} 的連接"
                })
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """執行全面分析"""
        print("🎯 開始 Real Data Signal Quality Engine 精確深度分析...")
        
        # 載入規範和代碼
        json_spec, python_code = self.load_specifications()
        
        # 執行各項分析
        self.analyze_strategy_compliance(json_spec, python_code)
        self.analyze_dependency_compliance(json_spec, python_code)
        self.analyze_enhanced_capabilities(json_spec, python_code)
        self.analyze_computation_flow(json_spec, python_code)
        self.analyze_unused_code(python_code)
        self.analyze_data_flow_integrity(json_spec, python_code)
        
        # 計算總體符合度
        total_issues = sum(len(issues) for issues in self.analysis_results.values())
        critical_issues = sum(1 for issues in self.analysis_results.values() 
                            for issue in issues if issue.get("severity") == "CRITICAL")
        high_issues = sum(1 for issues in self.analysis_results.values()
                         for issue in issues if issue.get("severity") == "HIGH")
        
        compliance_percentage = max(0, 100 - (critical_issues * 20 + high_issues * 10 + (total_issues - critical_issues - high_issues) * 5))
        
        return {
            "overall_compliance": f"{compliance_percentage:.1f}%",
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "detailed_analysis": self.analysis_results,
            "recommendation": "REWRITE_REQUIRED" if compliance_percentage < 60 else 
                            "MAJOR_FIXES_NEEDED" if compliance_percentage < 80 else
                            "MINOR_ADJUSTMENTS" if compliance_percentage < 95 else "COMPLIANT"
        }

if __name__ == "__main__":
    analyzer = RealDataPrecisionAnalyzer()
    results = analyzer.run_comprehensive_analysis()
    
    print(f"\n🎯 Real Data Signal Quality Engine 精確分析報告")
    print(f"=" * 60)
    print(f"📊 總體符合度: {results['overall_compliance']}")
    print(f"🔍 總問題數: {results['total_issues']}")
    print(f"🔴 嚴重問題: {results['critical_issues']}")
    print(f"🟡 高級問題: {results['high_issues']}")
    print(f"📋 建議: {results['recommendation']}")
    
    print(f"\n📋 詳細問題分析:")
    for category, issues in results['detailed_analysis'].items():
        if issues:
            print(f"\n🔍 {category.upper()}:")
            for i, issue in enumerate(issues, 1):
                severity = issue.get('severity', 'UNKNOWN')
                emoji = "🔴" if severity == "CRITICAL" else "🟡" if severity == "HIGH" else "🟠" if severity == "MEDIUM" else "🟢"
                print(f"  {emoji} {i}. [{severity}] {issue.get('details', issue.get('name', str(issue)))}")
