"""
🎯 精確深度分析工具 - unified_signal_candidate_pool.py vs JSON 規範
🎯 確保 100% 完整匹配，無邏輯斷點，無冗餘代碼
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
class AnalysisResult:
    """分析結果"""
    component_name: str
    json_spec: Dict[str, Any]
    code_implementation: Dict[str, Any]
    match_status: str  # "COMPLETE" | "PARTIAL" | "MISSING" | "REDUNDANT"
    missing_elements: List[str]
    redundant_elements: List[str]
    logic_gaps: List[str]
    data_flow_issues: List[str]

class PreciseDepthAnalyzer:
    """精確深度分析器"""
    
    def __init__(self, json_spec_path: str, code_file_path: str):
        self.json_spec_path = json_spec_path
        self.code_file_path = code_file_path
        
        # 載入 JSON 規範
        with open(json_spec_path, 'r', encoding='utf-8') as f:
            self.json_spec = json.load(f)
        
        # 讀取代碼
        with open(code_file_path, 'r', encoding='utf-8') as f:
            self.code_content = f.read()
        
        # 解析 AST
        self.ast_tree = ast.parse(self.code_content)
        
        # 分析結果
        self.analysis_results: List[AnalysisResult] = []
        
    def analyze_complete_compliance(self) -> Dict[str, Any]:
        """完整合規性分析"""
        logger.info("🔍 開始精確深度分析...")
        
        # 1. 核心組件分析
        self._analyze_core_components()
        
        # 2. AI 學習引擎分析
        self._analyze_ai_learning_engine()
        
        # 3. Phase1 流程整合分析
        self._analyze_phase1_integration()
        
        # 4. 數據流分析
        self._analyze_data_flows()
        
        # 5. 性能目標分析
        self._analyze_performance_targets()
        
        # 6. 冗餘代碼檢測
        self._detect_redundant_code()
        
        # 7. 邏輯斷點檢測
        self._detect_logic_gaps()
        
        # 8. 生成最終報告
        return self._generate_final_report()
    
    def _analyze_core_components(self):
        """分析核心組件"""
        logger.info("📊 分析核心組件...")
        
        # 檢查主要類別
        required_classes = [
            "UnifiedSignalCandidatePoolV3",
            "StandardizedSignal", 
            "SevenDimensionalScore",
            "AILearningMetrics",
            "MarketRegimeState",
            "SignalQualityValidator",
            "AIAdaptiveLearningEngine",
            "SevenDimensionalScorer"
        ]
        
        code_classes = self._extract_classes()
        
        for class_name in required_classes:
            if class_name in code_classes:
                # 檢查類別方法完整性
                self._analyze_class_methods(class_name, code_classes[class_name])
            else:
                self.analysis_results.append(AnalysisResult(
                    component_name=f"Class_{class_name}",
                    json_spec={"required": True},
                    code_implementation={"exists": False},
                    match_status="MISSING",
                    missing_elements=[class_name],
                    redundant_elements=[],
                    logic_gaps=[f"缺少核心類別: {class_name}"],
                    data_flow_issues=[]
                ))
    
    def _analyze_ai_learning_engine(self):
        """分析 AI 學習引擎"""
        logger.info("🧠 分析 AI 學習引擎...")
        
        # JSON 規範要求
        ai_spec = self.json_spec["UNIFIED_SIGNAL_CANDIDATE_POOL_V3_DEPENDENCY"]["🧠 ai_adaptive_learning_engine"]
        
        # 檢查學習組件
        required_ai_components = {
            "historical_decision_learning": [
                "learning_data", "learning_metrics", "weight_adjustment"
            ],
            "predictive_filtering": [
                "ml_model", "feature_engineering", "prediction_target", "filtering_thresholds"
            ],
            "real_time_adaptation": [
                "adaptation_trigger", "fast_learning", "emergency_adjustment", "stability_guarantee"
            ]
        }
        
        # 檢查代碼實現
        ai_methods = self._find_ai_methods()
        
        missing_components = []
        for component, features in required_ai_components.items():
            if component not in ai_methods:
                missing_components.extend([f"{component}.{feature}" for feature in features])
        
        if missing_components:
            self.analysis_results.append(AnalysisResult(
                component_name="AI_Learning_Engine",
                json_spec=ai_spec,
                code_implementation=ai_methods,
                match_status="PARTIAL",
                missing_elements=missing_components,
                redundant_elements=[],
                logic_gaps=[f"AI 學習引擎功能不完整: {missing_components}"],
                data_flow_issues=[]
            ))
    
    def _analyze_phase1_integration(self):
        """分析 Phase1 整合"""
        logger.info("🔄 分析 Phase1 整合...")
        
        # JSON 規範 Phase1 流程
        phase1_spec = self.json_spec["UNIFIED_SIGNAL_CANDIDATE_POOL_V3_DEPENDENCY"]["🔄 phase1_complete_flow_integration"]
        
        # 檢查 Layer 實現
        required_layers = {
            "Layer_0_Complete_Phase1_Sync": ["unified_timestamp_sync", "data_flow_integrity", "extreme_market_fast_track"],
            "Layer_1_Multi_Source_Fusion": ["intelligent_signal_collection", "seven_dimensional_comprehensive_scoring"],
            "Layer_2_EPL_Preprocessor": ["epl_oriented_filtering", "epl_input_formatting", "emergency_signal_priority_channel"]
        }
        
        # 檢查代碼中的層實現
        layer_methods = self._find_layer_methods()
        
        missing_layers = []
        for layer, components in required_layers.items():
            layer_method = f"_layer_{layer.split('_')[1].lower()}"
            if layer_method not in layer_methods:
                missing_layers.append(layer)
            else:
                # 檢查組件完整性
                for component in components:
                    if not self._check_component_in_method(layer_method, component):
                        missing_layers.append(f"{layer}.{component}")
        
        if missing_layers:
            self.analysis_results.append(AnalysisResult(
                component_name="Phase1_Integration",
                json_spec=phase1_spec,
                code_implementation=layer_methods,
                match_status="PARTIAL",
                missing_elements=missing_layers,
                redundant_elements=[],
                logic_gaps=[f"Phase1 整合不完整: {missing_layers}"],
                data_flow_issues=[]
            ))
    
    def _analyze_data_flows(self):
        """分析數據流"""
        logger.info("📈 分析數據流...")
        
        # JSON 規範數據流
        input_sources = self.json_spec["UNIFIED_SIGNAL_CANDIDATE_POOL_V3_DEPENDENCY"]["🌐 complete_input_source_integration"]
        
        required_inputs = {
            "phase1a_input": ["PRICE_BREAKOUT", "VOLUME_SURGE", "MOMENTUM_SHIFT", "EXTREME_EVENT"],
            "indicator_graph_input": ["RSI_signals", "MACD_signals", "BB_signals", "Volume_signals"],
            "phase1b_input": ["VOLATILITY_BREAKOUT", "REGIME_CHANGE", "MEAN_REVERSION"],
            "phase1c_input": ["LIQUIDITY_SHOCK", "INSTITUTIONAL_FLOW", "SENTIMENT_DIVERGENCE"]
        }
        
        # 檢查代碼中的數據流處理
        data_flow_methods = self._find_data_flow_methods()
        
        missing_data_flows = []
        for source, signal_types in required_inputs.items():
            method_name = f"_collect_{source.replace('_input', '')}_signals"
            if method_name not in data_flow_methods:
                missing_data_flows.append(source)
            else:
                # 檢查信號類型處理
                for signal_type in signal_types:
                    if not self._check_signal_type_handling(method_name, signal_type):
                        missing_data_flows.append(f"{source}.{signal_type}")
        
        if missing_data_flows:
            self.analysis_results.append(AnalysisResult(
                component_name="Data_Flows",
                json_spec=input_sources,
                code_implementation=data_flow_methods,
                match_status="PARTIAL",
                missing_elements=missing_data_flows,
                redundant_elements=[],
                logic_gaps=[],
                data_flow_issues=[f"數據流處理不完整: {missing_data_flows}"]
            ))
    
    def _analyze_performance_targets(self):
        """分析性能目標"""
        logger.info("⚡ 分析性能目標...")
        
        # JSON 規範性能目標
        perf_spec = self.json_spec["UNIFIED_SIGNAL_CANDIDATE_POOL_V3_DEPENDENCY"]["🎯 v3_0_performance_targets"]
        
        required_targets = {
            "layer_0_phase1_sync": "3ms",
            "layer_1_multi_fusion": "12ms", 
            "layer_2_epl_preprocessor": "8ms",
            "layer_ai_learning": "5ms",
            "total_processing_time": "28ms"
        }
        
        # 檢查代碼中的性能監控
        perf_monitoring = self._find_performance_monitoring()
        
        missing_monitoring = []
        for target, time_limit in required_targets.items():
            if target not in perf_monitoring:
                missing_monitoring.append(f"{target} ({time_limit})")
        
        if missing_monitoring:
            self.analysis_results.append(AnalysisResult(
                component_name="Performance_Targets",
                json_spec=perf_spec,
                code_implementation=perf_monitoring,
                match_status="PARTIAL",
                missing_elements=missing_monitoring,
                redundant_elements=[],
                logic_gaps=[f"性能監控不完整: {missing_monitoring}"],
                data_flow_issues=[]
            ))
    
    def _detect_redundant_code(self):
        """檢測冗餘代碼"""
        logger.info("🧹 檢測冗餘代碼...")
        
        # 檢查未使用的導入
        unused_imports = self._find_unused_imports()
        
        # 檢查未使用的方法
        unused_methods = self._find_unused_methods()
        
        # 檢查未使用的變數
        unused_variables = self._find_unused_variables()
        
        redundant_elements = unused_imports + unused_methods + unused_variables
        
        if redundant_elements:
            self.analysis_results.append(AnalysisResult(
                component_name="Redundant_Code",
                json_spec={"required": "clean_code"},
                code_implementation={"redundant_items": redundant_elements},
                match_status="REDUNDANT",
                missing_elements=[],
                redundant_elements=redundant_elements,
                logic_gaps=[],
                data_flow_issues=[]
            ))
    
    def _detect_logic_gaps(self):
        """檢測邏輯斷點"""
        logger.info("🔍 檢測邏輯斷點...")
        
        # 檢查方法調用鏈
        call_chains = self._analyze_method_call_chains()
        
        # 檢查數據傳遞
        data_passing = self._analyze_data_passing()
        
        # 檢查錯誤處理
        error_handling = self._analyze_error_handling()
        
        logic_gaps = []
        
        # 檢查調用鏈斷點
        for chain in call_chains:
            if chain["broken"]:
                logic_gaps.append(f"調用鏈斷點: {chain['chain']}")
        
        # 檢查數據傳遞斷點
        for data in data_passing:
            if data["missing"]:
                logic_gaps.append(f"數據傳遞斷點: {data['flow']}")
        
        if logic_gaps:
            self.analysis_results.append(AnalysisResult(
                component_name="Logic_Gaps",
                json_spec={"required": "complete_logic_flow"},
                code_implementation={"gaps": logic_gaps},
                match_status="PARTIAL",
                missing_elements=[],
                redundant_elements=[],
                logic_gaps=logic_gaps,
                data_flow_issues=[]
            ))
    
    def _extract_classes(self) -> Dict[str, Dict]:
        """提取類別定義"""
        classes = {}
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)
                classes[node.name] = {
                    "methods": methods,
                    "line": node.lineno
                }
        return classes
    
    def _analyze_class_methods(self, class_name: str, class_info: Dict):
        """分析類別方法完整性"""
        # 根據 JSON 規範檢查必要方法
        if class_name == "UnifiedSignalCandidatePoolV3":
            required_methods = [
                "generate_signal_candidates_v3",
                "_layer_0_complete_phase1_sync",
                "_layer_1_enhanced_multi_source_fusion", 
                "_layer_2_epl_preprocessing_optimization",
                "_layer_ai_adaptive_learning"
            ]
            
            missing_methods = [m for m in required_methods if m not in class_info["methods"]]
            if missing_methods:
                self.analysis_results.append(AnalysisResult(
                    component_name=f"Class_{class_name}_Methods",
                    json_spec={"required_methods": required_methods},
                    code_implementation={"methods": class_info["methods"]},
                    match_status="PARTIAL",
                    missing_elements=missing_methods,
                    redundant_elements=[],
                    logic_gaps=[f"缺少必要方法: {missing_methods}"],
                    data_flow_issues=[]
                ))
    
    def _find_ai_methods(self) -> Dict[str, bool]:
        """查找 AI 相關方法"""
        ai_methods = {}
        pattern = r"(learn_from_epl_feedback|predict_epl_pass_probability|calculate_signal_contribution|adjust_source_weights)"
        matches = re.findall(pattern, self.code_content)
        for match in matches:
            ai_methods[match] = True
        return ai_methods
    
    def _find_layer_methods(self) -> Dict[str, bool]:
        """查找層級方法"""
        layer_methods = {}
        pattern = r"(_layer_\d+_\w+|_layer_ai_\w+)"
        matches = re.findall(pattern, self.code_content)
        for match in matches:
            layer_methods[match] = True
        return layer_methods
    
    def _find_data_flow_methods(self) -> Dict[str, bool]:
        """查找數據流方法"""
        data_methods = {}
        pattern = r"(_collect_\w+_signals)"
        matches = re.findall(pattern, self.code_content)
        for match in matches:
            data_methods[match] = True
        return data_methods
    
    def _find_performance_monitoring(self) -> Dict[str, bool]:
        """查找性能監控"""
        perf_monitoring = {}
        patterns = [
            r"layer_\d+_time",
            r"total_time",
            r"elapsed.*time",
            r"performance_status"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, self.code_content)
            for match in matches:
                perf_monitoring[match] = True
        return perf_monitoring
    
    def _check_component_in_method(self, method_name: str, component: str) -> bool:
        """檢查方法中是否包含組件"""
        # 簡化實現，實際需要更複雜的 AST 分析
        method_pattern = rf"def {method_name}.*?(?=def|\Z)"
        method_match = re.search(method_pattern, self.code_content, re.DOTALL)
        if method_match:
            method_content = method_match.group(0)
            return component.lower() in method_content.lower()
        return False
    
    def _check_signal_type_handling(self, method_name: str, signal_type: str) -> bool:
        """檢查信號類型處理"""
        method_pattern = rf"def {method_name}.*?(?=def|\Z)"
        method_match = re.search(method_pattern, self.code_content, re.DOTALL)
        if method_match:
            method_content = method_match.group(0)
            return signal_type in method_content
        return False
    
    def _find_unused_imports(self) -> List[str]:
        """查找未使用的導入"""
        # 簡化實現
        import_pattern = r"^(from .* import .*|import .*)"
        imports = re.findall(import_pattern, self.code_content, re.MULTILINE)
        
        unused = []
        for imp in imports:
            # 檢查是否在代碼中使用
            if "warnings" in imp and "warnings.filterwarnings" not in self.code_content:
                unused.append(imp)
        return unused
    
    def _find_unused_methods(self) -> List[str]:
        """查找未使用的方法"""
        # 提取所有方法定義
        method_pattern = r"def (\w+)\("
        defined_methods = re.findall(method_pattern, self.code_content)
        
        unused = []
        for method in defined_methods:
            # 檢查是否被調用（排除魔術方法和主要入口方法）
            if (not method.startswith("__") and 
                method not in ["generate_signal_candidates_v3", "learn_from_epl_feedback", "get_performance_report"] and
                self.code_content.count(f"{method}(") <= 1):  # 只出現在定義中
                unused.append(method)
        return unused
    
    def _find_unused_variables(self) -> List[str]:
        """查找未使用的變數"""
        # 簡化實現，實際需要更複雜的分析
        unused = []
        
        # 檢查類級別變數
        class_var_pattern = r"self\.(\w+) = "
        class_vars = re.findall(class_var_pattern, self.code_content)
        
        for var in class_vars:
            if self.code_content.count(f"self.{var}") <= 1:  # 只在賦值時出現
                unused.append(f"self.{var}")
        
        return unused
    
    def _analyze_method_call_chains(self) -> List[Dict[str, Any]]:
        """分析方法調用鏈"""
        # 簡化實現
        chains = []
        
        # 檢查主要流程鏈
        main_chain = [
            "_layer_0_complete_phase1_sync",
            "_layer_1_enhanced_multi_source_fusion",
            "_layer_2_epl_preprocessing_optimization", 
            "_layer_ai_adaptive_learning"
        ]
        
        broken = False
        for method in main_chain:
            if method not in self.code_content:
                broken = True
                break
        
        chains.append({
            "chain": " -> ".join(main_chain),
            "broken": broken
        })
        
        return chains
    
    def _analyze_data_passing(self) -> List[Dict[str, Any]]:
        """分析數據傳遞"""
        # 簡化實現
        data_flows = []
        
        # 檢查數據傳遞流
        expected_flows = [
            "raw_signals -> epl_optimized_signals",
            "epl_optimized_signals -> final_signals",
            "signals -> StandardizedSignal"
        ]
        
        for flow in expected_flows:
            variables = flow.split(" -> ")
            missing = False
            for var in variables:
                if var not in self.code_content:
                    missing = True
                    break
                    
            data_flows.append({
                "flow": flow,
                "missing": missing
            })
        
        return data_flows
    
    def _analyze_error_handling(self) -> Dict[str, Any]:
        """分析錯誤處理"""
        # 檢查 try-except 覆蓋率
        try_count = self.code_content.count("try:")
        except_count = self.code_content.count("except")
        
        return {
            "try_blocks": try_count,
            "except_blocks": except_count,
            "adequate_coverage": try_count >= 5  # 主要方法都應該有錯誤處理
        }
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """生成最終報告"""
        logger.info("📋 生成最終分析報告...")
        
        total_components = len(self.analysis_results)
        complete_matches = len([r for r in self.analysis_results if r.match_status == "COMPLETE"])
        partial_matches = len([r for r in self.analysis_results if r.match_status == "PARTIAL"])
        missing_components = len([r for r in self.analysis_results if r.match_status == "MISSING"])
        redundant_components = len([r for r in self.analysis_results if r.match_status == "REDUNDANT"])
        
        # 計算總體匹配度
        overall_match_rate = complete_matches / total_components if total_components > 0 else 0
        
        # 收集所有問題
        all_missing = []
        all_redundant = []
        all_logic_gaps = []
        all_data_issues = []
        
        for result in self.analysis_results:
            all_missing.extend(result.missing_elements)
            all_redundant.extend(result.redundant_elements)
            all_logic_gaps.extend(result.logic_gaps)
            all_data_issues.extend(result.data_flow_issues)
        
        return {
            "總體匹配度": f"{overall_match_rate:.1%}",
            "組件分析": {
                "總組件數": total_components,
                "完全匹配": complete_matches,
                "部分匹配": partial_matches,
                "缺失組件": missing_components,
                "冗餘組件": redundant_components
            },
            "詳細問題": {
                "缺失元素": all_missing,
                "冗餘元素": all_redundant,
                "邏輯斷點": all_logic_gaps,
                "數據流問題": all_data_issues
            },
            "分析結果": [
                {
                    "組件": result.component_name,
                    "狀態": result.match_status,
                    "缺失": result.missing_elements,
                    "冗餘": result.redundant_elements,
                    "邏輯問題": result.logic_gaps,
                    "數據問題": result.data_flow_issues
                }
                for result in self.analysis_results
            ],
            "建議動作": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成修復建議"""
        recommendations = []
        
        for result in self.analysis_results:
            if result.match_status == "MISSING":
                recommendations.append(f"❌ 實現缺失組件: {result.component_name}")
            elif result.match_status == "PARTIAL":
                recommendations.append(f"⚠️ 完善部分實現: {result.component_name} - {result.missing_elements}")
            elif result.match_status == "REDUNDANT":
                recommendations.append(f"🧹 清理冗餘代碼: {result.redundant_elements}")
            
            if result.logic_gaps:
                recommendations.append(f"🔧 修復邏輯斷點: {result.logic_gaps}")
            
            if result.data_flow_issues:
                recommendations.append(f"📊 修復數據流: {result.data_flow_issues}")
        
        return recommendations

def main():
    """主函數"""
    json_spec_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/unified_signal_pool/unified_signal_candidate_pool_v3_dependency.json"
    code_file_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/unified_signal_pool/unified_signal_candidate_pool.py"
    
    analyzer = PreciseDepthAnalyzer(json_spec_path, code_file_path)
    report = analyzer.analyze_complete_compliance()
    
    print("\n" + "="*80)
    print("🎯 UNIFIED SIGNAL CANDIDATE POOL - 精確深度分析報告")
    print("="*80)
    
    print(f"\n📊 總體評估:")
    print(f"   匹配度: {report['總體匹配度']}")
    print(f"   完全匹配: {report['組件分析']['完全匹配']}/{report['組件分析']['總組件數']}")
    print(f"   部分匹配: {report['組件分析']['部分匹配']}/{report['組件分析']['總組件數']}")
    print(f"   缺失組件: {report['組件分析']['缺失組件']}")
    print(f"   冗餘組件: {report['組件分析']['冗餘組件']}")
    
    print(f"\n🚨 關鍵問題:")
    if report['詳細問題']['缺失元素']:
        print(f"   缺失元素: {len(report['詳細問題']['缺失元素'])} 項")
        for item in report['詳細問題']['缺失元素'][:5]:  # 顯示前5項
            print(f"     - {item}")
    
    if report['詳細問題']['冗餘元素']:
        print(f"   冗餘元素: {len(report['詳細問題']['冗餘元素'])} 項")
        for item in report['詳細問題']['冗餘元素'][:3]:  # 顯示前3項
            print(f"     - {item}")
    
    if report['詳細問題']['邏輯斷點']:
        print(f"   邏輯斷點: {len(report['詳細問題']['邏輯斷點'])} 項")
        for item in report['詳細問題']['邏輯斷點']:
            print(f"     - {item}")
    
    print(f"\n🛠️ 修復建議:")
    for i, recommendation in enumerate(report['建議動作'][:10], 1):  # 顯示前10項建議
        print(f"   {i}. {recommendation}")
    
    print(f"\n📋 詳細分析結果:")
    for result in report['分析結果']:
        status_emoji = {
            "COMPLETE": "✅",
            "PARTIAL": "⚠️", 
            "MISSING": "❌",
            "REDUNDANT": "🧹"
        }
        print(f"   {status_emoji.get(result['狀態'], '❓')} {result['組件']}: {result['狀態']}")
        
        if result['缺失']:
            print(f"      缺失: {result['缺失']}")
        if result['冗餘']:
            print(f"      冗餘: {result['冗餘']}")
        if result['邏輯問題']:
            print(f"      邏輯: {result['邏輯問題']}")
    
    print("\n" + "="*80)
    
    return report

if __name__ == "__main__":
    main()
