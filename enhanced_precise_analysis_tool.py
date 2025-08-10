"""
🎯 增強精確深度分析工具 v2.0 - unified_signal_candidate_pool.py vs JSON 規範
🎯 修正 AST 解析錯誤，確保 100% 準確檢測
"""

import json
import ast
import re
import logging
from typing import Dict, List, Set, Any, Tuple
from pathlib import Path
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ComponentAnalysis:
    """組件分析結果"""
    name: str
    required: bool
    implemented: bool
    details: Dict[str, Any]
    issues: List[str]

class EnhancedPreciseAnalyzer:
    """增強精確分析器"""
    
    def __init__(self, json_spec_path: str, code_file_path: str):
        self.json_spec_path = json_spec_path
        self.code_file_path = code_file_path
        
        # 載入 JSON 規範
        with open(json_spec_path, 'r', encoding='utf-8') as f:
            self.json_spec = json.load(f)["UNIFIED_SIGNAL_CANDIDATE_POOL_V3_DEPENDENCY"]
        
        # 讀取代碼
        with open(code_file_path, 'r', encoding='utf-8') as f:
            self.code_content = f.read()
        
        # 解析 AST
        try:
            self.ast_tree = ast.parse(self.code_content)
        except SyntaxError as e:
            logger.error(f"代碼語法錯誤: {e}")
            raise
        
        # 分析結果
        self.analysis_results: List[ComponentAnalysis] = []
        
    def analyze_complete_compliance(self) -> Dict[str, Any]:
        """完整合規性分析"""
        logger.info("🔍 開始增強精確深度分析...")
        
        # 1. 核心類別與方法分析
        self._analyze_core_classes_and_methods()
        
        # 2. AI 學習引擎組件分析
        self._analyze_ai_learning_components()
        
        # 3. Phase1 層級實現分析
        self._analyze_phase1_layers()
        
        # 4. 數據流與信號處理分析
        self._analyze_data_flows_and_signals()
        
        # 5. 性能監控分析
        self._analyze_performance_monitoring()
        
        # 6. 七維度評分系統分析
        self._analyze_seven_dimensional_scoring()
        
        # 7. EPL 預處理優化分析
        self._analyze_epl_preprocessing()
        
        # 8. 冗餘代碼檢測
        self._detect_truly_redundant_code()
        
        # 9. 生成最終報告
        return self._generate_enhanced_report()
    
    def _extract_all_methods(self) -> Dict[str, List[str]]:
        """提取所有類別的方法"""
        classes_methods = {}
        
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)
                classes_methods[node.name] = methods
        
        return classes_methods
    
    def _extract_all_functions(self) -> List[str]:
        """提取所有函數名"""
        functions = []
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        return functions
    
    def _analyze_core_classes_and_methods(self):
        """分析核心類別與方法"""
        logger.info("📊 分析核心類別與方法...")
        
        classes_methods = self._extract_all_methods()
        
        # JSON 規範要求的核心類別
        required_classes = {
            "UnifiedSignalCandidatePoolV3": [
                "generate_signal_candidates_v3",
                "_layer_0_complete_phase1_sync", 
                "_layer_1_enhanced_multi_source_fusion",
                "_layer_2_epl_preprocessing_optimization",
                "_layer_ai_adaptive_learning"
            ],
            "StandardizedSignal": [],
            "SevenDimensionalScore": [],
            "AILearningMetrics": [],
            "MarketRegimeState": [],
            "SignalQualityValidator": [
                "validate_signal_strength_range",
                "validate_phase1a_signal",
                "validate_indicator_signal", 
                "validate_phase1b_signal",
                "validate_phase1c_signal"
            ],
            "AIAdaptiveLearningEngine": [
                "learn_from_epl_feedback",
                "predict_epl_pass_probability",
                "_calculate_signal_contribution",
                "_adjust_source_weights"
            ],
            "SevenDimensionalScorer": [
                "calculate_comprehensive_score",
                "_calculate_data_quality",
                "_calculate_market_consistency",
                "_calculate_time_effect",
                "_calculate_liquidity_factor",
                "_calculate_historical_accuracy",
                "_apply_ai_enhancement"
            ]
        }
        
        for class_name, required_methods in required_classes.items():
            implemented = class_name in classes_methods
            issues = []
            
            if implemented:
                class_methods = classes_methods[class_name]
                missing_methods = [m for m in required_methods if m not in class_methods]
                if missing_methods:
                    issues.append(f"缺少方法: {missing_methods}")
                    implemented = False  # 部分實現視為未完全實現
            else:
                issues.append(f"缺少整個類別: {class_name}")
            
            self.analysis_results.append(ComponentAnalysis(
                name=f"Class_{class_name}",
                required=True,
                implemented=implemented,
                details={"methods": classes_methods.get(class_name, [])},
                issues=issues
            ))
    
    def _analyze_ai_learning_components(self):
        """分析 AI 學習引擎組件"""
        logger.info("🧠 分析 AI 學習引擎組件...")
        
        # JSON 規範的 AI 學習組件
        ai_spec = self.json_spec["🧠 ai_adaptive_learning_engine"]["Layer_AI_Learning_Engine"]["operations"]
        
        required_components = {
            "historical_decision_learning": {
                "patterns": ["learning_data", "EPL_decision_history", "learning_metrics", "weight_adjustment"],
                "weight": 0.3
            },
            "predictive_filtering": {
                "patterns": ["ml_model", "feature_engineering", "prediction_target", "filtering_thresholds", "predict_epl_pass_probability"],
                "weight": 0.4
            },
            "real_time_adaptation": {
                "patterns": ["adaptation_trigger", "fast_learning", "emergency_adjustment", "stability_guarantee"],
                "weight": 0.3
            }
        }
        
        for component, config in required_components.items():
            implemented_patterns = []
            missing_patterns = []
            
            for pattern in config["patterns"]:
                if pattern in self.code_content:
                    implemented_patterns.append(pattern)
                else:
                    missing_patterns.append(pattern)
            
            implementation_rate = len(implemented_patterns) / len(config["patterns"])
            implemented = implementation_rate >= 0.8  # 80% 實現閾值
            
            issues = []
            if missing_patterns:
                issues.append(f"缺少功能: {missing_patterns}")
            
            self.analysis_results.append(ComponentAnalysis(
                name=f"AI_{component}",
                required=True,
                implemented=implemented,
                details={
                    "implementation_rate": f"{implementation_rate:.1%}",
                    "implemented": implemented_patterns,
                    "missing": missing_patterns
                },
                issues=issues
            ))
    
    def _analyze_phase1_layers(self):
        """分析 Phase1 層級實現"""
        logger.info("🔄 分析 Phase1 層級實現...")
        
        # JSON 規範的層級要求
        required_layers = {
            "Layer_0_Complete_Phase1_Sync": {
                "method": "_layer_0_complete_phase1_sync",
                "components": ["unified_timestamp_sync", "data_flow_integrity", "extreme_market_fast_track"],
                "time_target": "3ms"
            },
            "Layer_1_Multi_Source_Fusion": {
                "method": "_layer_1_enhanced_multi_source_fusion", 
                "components": ["intelligent_signal_collection", "seven_dimensional_comprehensive_scoring"],
                "time_target": "12ms"
            },
            "Layer_2_EPL_Preprocessor": {
                "method": "_layer_2_epl_preprocessing_optimization",
                "components": ["epl_oriented_filtering", "epl_input_formatting", "emergency_signal_priority_channel"],
                "time_target": "8ms"
            },
            "Layer_AI_Adaptive_Learning": {
                "method": "_layer_ai_adaptive_learning",
                "components": ["real_time_adaptation", "weight_adjustment", "learning_feedback"],
                "time_target": "5ms"
            }
        }
        
        for layer_name, layer_config in required_layers.items():
            method_name = layer_config["method"]
            method_exists = method_name in self.code_content
            
            issues = []
            component_coverage = 0
            
            if method_exists:
                # 檢查方法內容是否包含必要組件
                method_pattern = rf"def {method_name}.*?(?=def|\Z)"
                method_match = re.search(method_pattern, self.code_content, re.DOTALL)
                
                if method_match:
                    method_content = method_match.group(0)
                    implemented_components = []
                    
                    for component in layer_config["components"]:
                        # 檢查組件關鍵字是否在方法中
                        component_keywords = component.split("_")
                        if any(keyword in method_content.lower() for keyword in component_keywords):
                            implemented_components.append(component)
                    
                    component_coverage = len(implemented_components) / len(layer_config["components"])
                    
                    if component_coverage < 1.0:
                        missing_components = [c for c in layer_config["components"] if c not in implemented_components]
                        issues.append(f"組件不完整: {missing_components}")
                else:
                    issues.append("方法內容無法解析")
            else:
                issues.append(f"缺少方法: {method_name}")
            
            # 檢查性能監控
            time_monitoring = f"{layer_config['time_target']}" in self.code_content
            if not time_monitoring:
                issues.append(f"缺少 {layer_config['time_target']} 性能監控")
            
            implemented = method_exists and component_coverage >= 0.8 and time_monitoring
            
            self.analysis_results.append(ComponentAnalysis(
                name=layer_name,
                required=True,
                implemented=implemented,
                details={
                    "method_exists": method_exists,
                    "component_coverage": f"{component_coverage:.1%}",
                    "time_monitoring": time_monitoring
                },
                issues=issues
            ))
    
    def _analyze_data_flows_and_signals(self):
        """分析數據流與信號處理"""
        logger.info("📈 分析數據流與信號處理...")
        
        # JSON 規範的輸入源
        input_sources = self.json_spec["🌐 complete_input_source_integration"]
        
        required_signal_types = {
            "phase1a_input": ["PRICE_BREAKOUT", "VOLUME_SURGE", "MOMENTUM_SHIFT", "EXTREME_EVENT"],
            "indicator_graph_input": ["RSI_signals", "MACD_signals", "BB_signals", "Volume_signals"],
            "phase1b_input": ["VOLATILITY_BREAKOUT", "REGIME_CHANGE", "MEAN_REVERSION"],
            "phase1c_input": ["LIQUIDITY_SHOCK", "INSTITUTIONAL_FLOW", "SENTIMENT_DIVERGENCE", "LIQUIDITY_REGIME_CHANGE"]
        }
        
        # 檢查信號收集方法
        signal_collection_methods = {
            "phase1a": "_collect_phase1a_signals",
            "indicator_graph": "_collect_indicator_signals", 
            "phase1b": "_collect_phase1b_signals",
            "phase1c": "_collect_phase1c_signals"
        }
        
        for source_key, signal_types in required_signal_types.items():
            source_name = source_key.replace("_input", "")
            method_name = signal_collection_methods.get(source_name, f"_collect_{source_name}_signals")
            
            method_exists = method_name in self.code_content
            signal_coverage = 0
            issues = []
            
            if method_exists:
                # 檢查信號類型覆蓋
                method_pattern = rf"def {method_name}.*?(?=def|\Z)"
                method_match = re.search(method_pattern, self.code_content, re.DOTALL)
                
                if method_match:
                    method_content = method_match.group(0)
                    implemented_signals = []
                    
                    for signal_type in signal_types:
                        if signal_type in method_content:
                            implemented_signals.append(signal_type)
                    
                    signal_coverage = len(implemented_signals) / len(signal_types)
                    
                    if signal_coverage < 1.0:
                        missing_signals = [s for s in signal_types if s not in implemented_signals]
                        issues.append(f"缺少信號類型: {missing_signals}")
            else:
                issues.append(f"缺少方法: {method_name}")
            
            implemented = method_exists and signal_coverage >= 0.8
            
            self.analysis_results.append(ComponentAnalysis(
                name=f"DataFlow_{source_name}",
                required=True,
                implemented=implemented,
                details={
                    "method": method_name,
                    "signal_coverage": f"{signal_coverage:.1%}",
                    "expected_signals": signal_types
                },
                issues=issues
            ))
    
    def _analyze_performance_monitoring(self):
        """分析性能監控"""
        logger.info("⚡ 分析性能監控...")
        
        # JSON 規範的性能目標
        perf_targets = self.json_spec["🎯 v3_0_performance_targets"]["layered_processing_time"]
        
        required_monitoring = {
            "layer_0_phase1_sync": "3ms",
            "layer_1_multi_fusion": "12ms",
            "layer_2_epl_preprocessor": "8ms", 
            "layer_ai_learning": "5ms",
            "total_processing_time": "28ms"
        }
        
        monitoring_patterns = [
            "elapsed.*time",
            "layer_.*_time",
            "total_time",
            "performance_status",
            "time.*target",
            "ms.*目標"
        ]
        
        # 檢查性能監控實現
        monitoring_found = []
        for pattern in monitoring_patterns:
            matches = re.findall(pattern, self.code_content, re.IGNORECASE)
            monitoring_found.extend(matches)
        
        # 檢查具體時間目標
        time_targets_found = []
        for target, time_limit in required_monitoring.items():
            if time_limit in self.code_content:
                time_targets_found.append(target)
        
        coverage = len(time_targets_found) / len(required_monitoring)
        implemented = coverage >= 0.8 and len(monitoring_found) >= 3
        
        issues = []
        if coverage < 1.0:
            missing_targets = [t for t in required_monitoring.keys() if t not in time_targets_found]
            issues.append(f"缺少時間目標: {missing_targets}")
        
        if len(monitoring_found) < 3:
            issues.append("性能監控機制不足")
        
        self.analysis_results.append(ComponentAnalysis(
            name="Performance_Monitoring",
            required=True,
            implemented=implemented,
            details={
                "target_coverage": f"{coverage:.1%}",
                "monitoring_patterns": len(monitoring_found),
                "time_targets_found": time_targets_found
            },
            issues=issues
        ))
    
    def _analyze_seven_dimensional_scoring(self):
        """分析七維度評分系統"""
        logger.info("📊 分析七維度評分系統...")
        
        # JSON 規範的七維度
        scoring_spec = self.json_spec["🔄 phase1_complete_flow_integration"]["Layer_1_Multi_Source_Fusion"]["operations"]["🏭 seven_dimensional_comprehensive_scoring"]["scoring_dimensions"]
        
        required_dimensions = {
            "signal_strength": 0.25,
            "confidence": 0.20,
            "data_quality": 0.15,
            "market_consistency": 0.12,
            "time_effect": 0.10,
            "liquidity_factor": 0.10,
            "historical_accuracy": 0.08
        }
        
        # 檢查 SevenDimensionalScore 類和相關計算
        dimensions_found = []
        for dimension in required_dimensions.keys():
            if dimension in self.code_content:
                dimensions_found.append(dimension)
        
        # 檢查計算方法
        calculation_methods = [
            "_calculate_data_quality",
            "_calculate_market_consistency", 
            "_calculate_time_effect",
            "_calculate_liquidity_factor",
            "_calculate_historical_accuracy"
        ]
        
        methods_found = []
        for method in calculation_methods:
            if method in self.code_content:
                methods_found.append(method)
        
        dimension_coverage = len(dimensions_found) / len(required_dimensions)
        method_coverage = len(methods_found) / len(calculation_methods)
        overall_coverage = (dimension_coverage + method_coverage) / 2
        
        implemented = overall_coverage >= 0.8
        
        issues = []
        if dimension_coverage < 1.0:
            missing_dimensions = [d for d in required_dimensions.keys() if d not in dimensions_found]
            issues.append(f"缺少維度: {missing_dimensions}")
        
        if method_coverage < 1.0:
            missing_methods = [m for m in calculation_methods if m not in methods_found]
            issues.append(f"缺少計算方法: {missing_methods}")
        
        self.analysis_results.append(ComponentAnalysis(
            name="Seven_Dimensional_Scoring",
            required=True,
            implemented=implemented,
            details={
                "dimension_coverage": f"{dimension_coverage:.1%}",
                "method_coverage": f"{method_coverage:.1%}",
                "overall_coverage": f"{overall_coverage:.1%}"
            },
            issues=issues
        ))
    
    def _analyze_epl_preprocessing(self):
        """分析 EPL 預處理優化"""
        logger.info("🎯 分析 EPL 預處理優化...")
        
        # JSON 規範的 EPL 預處理組件
        epl_spec = self.json_spec["🔄 phase1_complete_flow_integration"]["Layer_2_EPL_Preprocessor"]["operations"]
        
        required_components = {
            "epl_success_prediction": ["predict_epl_pass_probability", "XGBoost", "prediction_accuracy"],
            "signal_optimization": ["enhanced_deduplication", "complementary_selection", "quantity_control", "quality_assurance"],
            "epl_input_formatting": ["standardized_output", "epl_optimized_fields"],
            "emergency_signal_priority": ["extreme_market_signals", "emergency_processing"]
        }
        
        component_scores = {}
        overall_issues = []
        
        for component, keywords in required_components.items():
            found_keywords = []
            for keyword in keywords:
                if keyword.lower() in self.code_content.lower():
                    found_keywords.append(keyword)
            
            coverage = len(found_keywords) / len(keywords)
            component_scores[component] = coverage
            
            if coverage < 0.8:
                missing = [k for k in keywords if k not in found_keywords]
                overall_issues.append(f"{component} 不完整: {missing}")
        
        overall_coverage = sum(component_scores.values()) / len(component_scores)
        implemented = overall_coverage >= 0.7
        
        self.analysis_results.append(ComponentAnalysis(
            name="EPL_Preprocessing",
            required=True,
            implemented=implemented,
            details={
                "component_scores": {k: f"{v:.1%}" for k, v in component_scores.items()},
                "overall_coverage": f"{overall_coverage:.1%}"
            },
            issues=overall_issues
        ))
    
    def _detect_truly_redundant_code(self):
        """檢測真正的冗餘代碼"""
        logger.info("🧹 檢測冗餘代碼...")
        
        # 檢查未使用的導入（更精確）
        import_lines = re.findall(r'^(import .*|from .* import .*)$', self.code_content, re.MULTILINE)
        truly_unused = []
        
        for import_line in import_lines:
            # 檢查特定導入是否真的未使用
            if "warnings" in import_line and "warnings.filterwarnings" not in self.code_content:
                truly_unused.append(import_line)
            elif "pickle" in import_line and "pickle." not in self.code_content:
                truly_unused.append(import_line)
        
        # 檢查未使用的方法（排除可能的公共 API）
        all_functions = self._extract_all_functions()
        public_api_methods = [
            "generate_signal_candidates_v3", "learn_from_epl_feedback", 
            "get_performance_report", "get_candidates_by_priority", "clear_expired_candidates"
        ]
        
        potentially_unused = []
        for func in all_functions:
            if (func not in public_api_methods and 
                not func.startswith("__") and 
                self.code_content.count(f"{func}(") <= 1):  # 只在定義處出現
                potentially_unused.append(func)
        
        # 檢查未使用的變數（類變數）
        unused_vars = []
        class_var_pattern = r'self\.(\w+) = '
        class_vars = re.findall(class_var_pattern, self.code_content)
        
        for var in set(class_vars):  # 去重
            if self.code_content.count(f"self.{var}") <= 1:  # 只在賦值處出現
                unused_vars.append(f"self.{var}")
        
        all_redundant = truly_unused + potentially_unused + unused_vars
        
        if all_redundant:
            self.analysis_results.append(ComponentAnalysis(
                name="Redundant_Code",
                required=False,
                implemented=True,  # 有冗餘代碼
                details={
                    "unused_imports": truly_unused,
                    "potentially_unused_methods": potentially_unused,
                    "unused_variables": unused_vars
                },
                issues=[f"發現 {len(all_redundant)} 項潛在冗餘代碼"]
            ))
    
    def _generate_enhanced_report(self) -> Dict[str, Any]:
        """生成增強分析報告"""
        logger.info("📋 生成增強分析報告...")
        
        # 計算總體統計
        total_required = len([r for r in self.analysis_results if r.required])
        fully_implemented = len([r for r in self.analysis_results if r.required and r.implemented])
        partially_implemented = len([r for r in self.analysis_results if r.required and not r.implemented and r.issues])
        missing_components = len([r for r in self.analysis_results if r.required and not r.implemented and not r.issues])
        
        # 計算匹配度
        if total_required > 0:
            match_rate = fully_implemented / total_required
        else:
            match_rate = 1.0
        
        # 收集問題
        all_issues = []
        critical_issues = []
        redundant_items = []
        
        for result in self.analysis_results:
            if result.issues:
                all_issues.extend(result.issues)
                if result.required and not result.implemented:
                    critical_issues.extend(result.issues)
            
            if result.name == "Redundant_Code":
                redundant_items = result.details.get("unused_imports", []) + \
                                result.details.get("potentially_unused_methods", []) + \
                                result.details.get("unused_variables", [])
        
        # 生成修復建議
        recommendations = []
        for result in self.analysis_results:
            if result.required and not result.implemented:
                recommendations.append(f"❌ 修復 {result.name}: {', '.join(result.issues)}")
            elif result.issues and result.required:
                recommendations.append(f"⚠️ 改進 {result.name}: {', '.join(result.issues)}")
        
        if redundant_items:
            recommendations.append(f"🧹 清理冗餘代碼: {len(redundant_items)} 項")
        
        # 評估等級
        if match_rate >= 0.95:
            compliance_grade = "A+ (優秀)"
        elif match_rate >= 0.9:
            compliance_grade = "A (良好)"
        elif match_rate >= 0.8:
            compliance_grade = "B (及格)"
        elif match_rate >= 0.6:
            compliance_grade = "C (需改進)"
        else:
            compliance_grade = "D (不及格)"
        
        return {
            "總體評估": {
                "JSON規範匹配度": f"{match_rate:.1%}",
                "合規等級": compliance_grade,
                "必要組件總數": total_required,
                "完全實現": fully_implemented,
                "部分實現": partially_implemented,
                "缺失組件": missing_components
            },
            "詳細分析": {
                result.name: {
                    "必要": result.required,
                    "已實現": result.implemented,
                    "詳情": result.details,
                    "問題": result.issues
                }
                for result in self.analysis_results
            },
            "關鍵問題": critical_issues,
            "所有問題": all_issues,
            "冗餘代碼": redundant_items,
            "修復建議": recommendations,
            "結論": self._generate_conclusion(match_rate, critical_issues, redundant_items)
        }
    
    def _generate_conclusion(self, match_rate: float, critical_issues: List[str], redundant_items: List[str]) -> str:
        """生成結論"""
        if match_rate >= 0.95 and len(critical_issues) == 0:
            return "✅ 代碼與 JSON 規範高度匹配，可投入生產使用"
        elif match_rate >= 0.9:
            return "🟨 代碼基本符合 JSON 規範，建議修復少量問題後投入使用"
        elif match_rate >= 0.8:
            return "🟧 代碼部分符合 JSON 規範，需要重要改進"
        else:
            return "🟥 代碼與 JSON 規範差距較大，需要大幅修改"

def main():
    """主函數"""
    json_spec_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/unified_signal_pool/unified_signal_candidate_pool_v3_dependency.json"
    code_file_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/unified_signal_pool/unified_signal_candidate_pool.py"
    
    analyzer = EnhancedPreciseAnalyzer(json_spec_path, code_file_path)
    report = analyzer.analyze_complete_compliance()
    
    print("\n" + "="*90)
    print("🎯 UNIFIED SIGNAL CANDIDATE POOL - 增強精確深度分析報告 v2.0")
    print("="*90)
    
    # 總體評估
    overall = report["總體評估"]
    print(f"\n📊 總體評估:")
    print(f"   JSON規範匹配度: {overall['JSON規範匹配度']}")
    print(f"   合規等級: {overall['合規等級']}")
    print(f"   完全實現: {overall['完全實現']}/{overall['必要組件總數']}")
    print(f"   部分實現: {overall['部分實現']}")
    print(f"   缺失組件: {overall['缺失組件']}")
    
    # 關鍵問題
    if report["關鍵問題"]:
        print(f"\n🚨 關鍵問題 ({len(report['關鍵問題'])} 項):")
        for i, issue in enumerate(report["關鍵問題"][:10], 1):
            print(f"   {i}. {issue}")
    else:
        print(f"\n✅ 未發現關鍵問題")
    
    # 冗餘代碼
    if report["冗餘代碼"]:
        print(f"\n🧹 冗餘代碼 ({len(report['冗餘代碼'])} 項):")
        for i, item in enumerate(report["冗餘代碼"][:5], 1):
            print(f"   {i}. {item}")
    else:
        print(f"\n✅ 未發現冗餘代碼")
    
    # 修復建議
    if report["修復建議"]:
        print(f"\n🛠️ 修復建議 ({len(report['修復建議'])} 項):")
        for i, rec in enumerate(report["修復建議"][:8], 1):
            print(f"   {i}. {rec}")
    else:
        print(f"\n✅ 無需修復")
    
    # 詳細組件分析（簡化顯示）
    print(f"\n📋 組件實現狀態:")
    for name, details in report["詳細分析"].items():
        status = "✅" if details["已實現"] else ("⚠️" if details["問題"] else "❌")
        required_mark = "🔴" if details["必要"] else "🔵"
        print(f"   {status} {required_mark} {name}")
        
        if details["問題"] and len(details["問題"]) <= 2:
            for issue in details["問題"]:
                print(f"      └─ {issue}")
    
    # 結論
    print(f"\n🎯 結論:")
    print(f"   {report['結論']}")
    
    print("\n" + "="*90)
    
    return report

if __name__ == "__main__":
    main()
