"""
🔍 EPL Decision History Tracking Python 實現驗證
===============================================

分析 Python 實現與 JSON 配置的對應程度
"""

import sys
import ast
import inspect
from pathlib import Path
from typing import Dict, Any, List, Set
from datetime import datetime

class EPLPythonValidator:
    """EPL Python 實現驗證器"""
    
    def __init__(self):
        self.python_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring/3_epl_decision_history_tracking/epl_decision_history_tracking.py")
        
    def analyze_python_implementation(self) -> Dict[str, Any]:
        """分析 Python 實現"""
        try:
            with open(self.python_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # 解析 AST
            tree = ast.parse(code_content)
            
            analysis = {
                "file_size": len(code_content),
                "line_count": len(code_content.split('\n')),
                "classes": self._extract_classes(tree),
                "functions": self._extract_functions(tree),
                "imports": self._extract_imports(tree),
                "dataclasses": self._extract_dataclasses(tree),
                "async_methods": self._extract_async_methods(tree)
            }
            
            return analysis
            
        except Exception as e:
            return {"error": f"分析 Python 文件失敗: {e}"}
    
    def _extract_classes(self, tree: ast.AST) -> List[str]:
        """提取類別"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
        return classes
    
    def _extract_functions(self, tree: ast.AST) -> List[str]:
        """提取函數"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        return functions
    
    def _extract_async_methods(self, tree: ast.AST) -> List[str]:
        """提取異步方法"""
        async_methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                async_methods.append(node.name)
        return async_methods
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """提取導入"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports
    
    def _extract_dataclasses(self, tree: ast.AST) -> List[str]:
        """提取數據類"""
        dataclasses = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for decorator in node.decorator_list:
                    if (isinstance(decorator, ast.Name) and decorator.id == 'dataclass') or \
                       (isinstance(decorator, ast.Attribute) and decorator.attr == 'dataclass'):
                        dataclasses.append(node.name)
        return dataclasses
    
    def validate_core_structures(self, analysis: Dict) -> Dict[str, Any]:
        """驗證核心結構"""
        structure_score = 0
        max_score = 25
        details = {}
        
        # 主要類別檢查 (8分)
        required_classes = ["EPLDecisionHistoryTracker", "EPLDecisionRecord", "DecisionAnalytics"]
        class_score = 0
        found_classes = analysis.get("classes", [])
        
        for required_class in required_classes:
            if any(required_class.lower() in cls.lower() for cls in found_classes):
                class_score += 2
        
        # 額外分數給相關類別
        if len(found_classes) >= 3:
            class_score += 2
        
        details["core_classes"] = f"{class_score}/8"
        structure_score += class_score
        
        # 數據類檢查 (5分)
        dataclass_score = 0
        dataclasses = analysis.get("dataclasses", [])
        if len(dataclasses) >= 2:
            dataclass_score = 5
        elif len(dataclasses) >= 1:
            dataclass_score = 3
        
        details["data_structures"] = f"{dataclass_score}/5"
        structure_score += dataclass_score
        
        # 異步方法檢查 (7分)
        async_score = 0
        async_methods = analysis.get("async_methods", [])
        required_async = ["record_decision", "get_decision_analytics", "get_performance_metrics"]
        
        for method in required_async:
            if any(method.lower() in async_method.lower() for async_method in async_methods):
                async_score += 2
        
        if len(async_methods) >= 5:
            async_score += 1
        
        details["async_operations"] = f"{async_score}/7"
        structure_score += async_score
        
        # 導入檢查 (5分)
        import_score = 0
        imports = analysis.get("imports", [])
        required_imports = ["asyncio", "dataclass", "datetime", "typing", "json"]
        
        for imp in required_imports:
            if any(imp in import_str for import_str in imports):
                import_score += 1
        
        details["required_imports"] = f"{import_score}/5"
        structure_score += import_score
        
        return {
            "structure_score": structure_score,
            "max_score": max_score,
            "percentage": (structure_score / max_score) * 100,
            "details": details,
            "status": "excellent" if structure_score >= 20 else "good" if structure_score >= 15 else "needs_improvement"
        }
    
    def validate_phase_integration(self, analysis: Dict) -> Dict[str, Any]:
        """驗證 Phase 整合實現"""
        integration_score = 0
        max_score = 30
        details = {}
        
        functions = analysis.get("functions", []) + analysis.get("async_methods", [])
        
        # Phase1 信號關聯 (8分)
        phase1_score = 0
        phase1_methods = ["record_signal_decision", "correlate_signal", "track_signal_outcome"]
        for method in phase1_methods:
            if any(method.lower() in func.lower() for func in functions):
                phase1_score += 2
        
        if phase1_score >= 4:
            phase1_score += 2
        
        details["phase1_signal_correlation"] = f"{phase1_score}/8"
        integration_score += phase1_score
        
        # Phase2 決策引擎整合 (8分)
        phase2_score = 0
        phase2_methods = ["record_epl_decision", "capture_decision_context", "track_decision_reasoning"]
        for method in phase2_methods:
            if any(method.lower() in func.lower() for func in functions):
                phase2_score += 2
        
        if phase2_score >= 4:
            phase2_score += 2
        
        details["phase2_decision_integration"] = f"{phase2_score}/8"
        integration_score += phase2_score
        
        # Phase3 執行追蹤 (7分)
        phase3_score = 0
        phase3_methods = ["track_execution", "monitor_execution", "record_execution_outcome"]
        for method in phase3_methods:
            if any(method.lower() in func.lower() for func in functions):
                phase3_score += 2
        
        if len([f for f in functions if "execution" in f.lower()]) >= 2:
            phase3_score += 1
        
        details["phase3_execution_tracking"] = f"{phase3_score}/7"
        integration_score += phase3_score
        
        # Phase4 分析能力 (7分)
        phase4_score = 0
        phase4_methods = ["generate_analytics", "calculate_performance", "analyze_patterns"]
        for method in phase4_methods:
            if any(method.lower() in func.lower() for func in functions):
                phase4_score += 2
        
        if len([f for f in functions if "analyt" in f.lower() or "pattern" in f.lower()]) >= 2:
            phase4_score += 1
        
        details["phase4_analytics"] = f"{phase4_score}/7"
        integration_score += phase4_score
        
        return {
            "integration_score": integration_score,
            "max_score": max_score,
            "percentage": (integration_score / max_score) * 100,
            "details": details,
            "status": "excellent" if integration_score >= 24 else "good" if integration_score >= 18 else "needs_improvement"
        }
    
    def validate_monitoring_architecture(self, analysis: Dict) -> Dict[str, Any]:
        """驗證監控架構實現"""
        monitoring_score = 0
        max_score = 35
        details = {}
        
        functions = analysis.get("functions", []) + analysis.get("async_methods", [])
        classes = analysis.get("classes", [])
        
        # 決策追蹤能力 (12分)
        tracking_score = 0
        tracking_methods = ["record_decision", "track_decision_lifecycle", "update_decision_status", "get_decision_history"]
        for method in tracking_methods:
            if any(method.lower() in func.lower() for func in functions):
                tracking_score += 3
        
        details["decision_tracking"] = f"{tracking_score}/12"
        monitoring_score += tracking_score
        
        # 分析和報告 (12分)
        analytics_score = 0
        analytics_methods = ["generate_performance_report", "analyze_decision_patterns", "calculate_success_rates", "get_analytics"]
        for method in analytics_methods:
            if any(method.lower() in func.lower() for func in functions):
                analytics_score += 3
        
        details["analytics_reporting"] = f"{analytics_score}/12"
        monitoring_score += analytics_score
        
        # 學習和優化 (11分)
        learning_score = 0
        learning_methods = ["learn_from_outcomes", "optimize_thresholds", "identify_patterns"]
        for method in learning_methods:
            if any(method.lower() in func.lower() for func in functions):
                learning_score += 3
        
        # 檢查是否有學習相關的類別
        if any("learning" in cls.lower() or "optimization" in cls.lower() for cls in classes):
            learning_score += 2
        
        details["learning_optimization"] = f"{learning_score}/11"
        monitoring_score += learning_score
        
        return {
            "monitoring_score": monitoring_score,
            "max_score": max_score,
            "percentage": (monitoring_score / max_score) * 100,
            "details": details,
            "status": "excellent" if monitoring_score >= 28 else "good" if monitoring_score >= 21 else "needs_improvement"
        }
    
    def validate_json_compliance(self, analysis: Dict) -> Dict[str, Any]:
        """驗證 JSON 配置合規性"""
        compliance_score = 0
        max_score = 30
        details = {}
        
        functions = analysis.get("functions", []) + analysis.get("async_methods", [])
        
        # 配置載入和驗證 (10分)
        config_score = 0
        config_methods = ["load_config", "validate_config", "_get_config_value"]
        for method in config_methods:
            if any(method.lower() in func.lower() for func in functions):
                config_score += 3
        
        if config_score >= 6:
            config_score += 1
        
        details["config_management"] = f"{config_score}/10"
        compliance_score += config_score
        
        # 數據結構對應 (10分)
        structure_score = 0
        expected_structures = ["decision_record", "analytics_result", "performance_metrics"]
        classes = analysis.get("classes", [])
        
        for structure in expected_structures:
            if any(structure.replace("_", "").lower() in cls.lower() for cls in classes):
                structure_score += 3
        
        if structure_score >= 6:
            structure_score += 1
        
        details["data_structure_mapping"] = f"{structure_score}/10"
        compliance_score += structure_score
        
        # API 端點實現 (10分)
        api_score = 0
        api_methods = ["get_decision_tracking", "get_performance_analytics", "get_learning_data"]
        for method in api_methods:
            if any(method.lower() in func.lower() for func in functions):
                api_score += 3
        
        if api_score >= 6:
            api_score += 1
        
        details["api_compliance"] = f"{api_score}/10"
        compliance_score += api_score
        
        return {
            "compliance_score": compliance_score,
            "max_score": max_score,
            "percentage": (compliance_score / max_score) * 100,
            "details": details,
            "status": "excellent" if compliance_score >= 24 else "good" if compliance_score >= 18 else "needs_improvement"
        }
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """生成驗證報告"""
        print("🔍 EPL Decision History Tracking Python 實現驗證")
        print("=" * 60)
        
        # 分析 Python 實現
        analysis = self.analyze_python_implementation()
        
        if "error" in analysis:
            return {"validation_status": "failed", "error": analysis["error"]}
        
        print(f"✅ Python 文件分析完成")
        print(f"📄 文件大小: {analysis['file_size']} bytes")
        print(f"📝 代碼行數: {analysis['line_count']}")
        print(f"🏗️ 類別數量: {len(analysis['classes'])}")
        print(f"⚡ 異步方法: {len(analysis['async_methods'])}")
        
        # 各項驗證
        core_structures = self.validate_core_structures(analysis)
        phase_integration = self.validate_phase_integration(analysis)
        monitoring_architecture = self.validate_monitoring_architecture(analysis)
        json_compliance = self.validate_json_compliance(analysis)
        
        # 計算總分
        total_score = (
            core_structures["structure_score"] +
            phase_integration["integration_score"] +
            monitoring_architecture["monitoring_score"] +
            json_compliance["compliance_score"]
        )
        max_total_score = (
            core_structures["max_score"] +
            phase_integration["max_score"] +
            monitoring_architecture["max_score"] +
            json_compliance["max_score"]
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
                "core_structures": core_structures,
                "phase_integration": phase_integration,
                "monitoring_architecture": monitoring_architecture,
                "json_compliance": json_compliance
            },
            "implementation_analysis": analysis,
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
            return ["Python 實現品質優秀", "建議進行功能測試驗證"]
        elif overall_percentage >= 80:
            return ["實現良好，建議小幅優化", "可以進行功能測試"]
        elif overall_percentage >= 70:
            return ["實現可接受，建議改進低分項目", "優化後進行測試"]
        else:
            return ["實現需要重大改進", "建議重構關鍵組件", "完成改進後再測試"]
    
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
    validator = EPLPythonValidator()
    report = validator.generate_validation_report()
    
    print(f"\n🎯 EPL Decision History Tracking Python 驗證完成")
    print(f"📊 最終評分: {report['overall_score']['percentage']}")

if __name__ == "__main__":
    main()
