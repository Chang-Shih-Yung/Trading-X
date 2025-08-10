"""
🎯 Phase1B 精確深度分析工具
檢查 phase1b_volatility_adaptation.py 是否完全匹配 JSON 規範
重點：數據流、核心邏輯、各層級數據使用的精確性分析
"""

import json
import ast
import re
from typing import Dict, List, Any, Set, Tuple
from pathlib import Path

class Phase1BPreciseAnalyzer:
    def __init__(self):
        self.json_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/phase1b_volatility_adaptation/phase1b_volatility_adaptation_dependency.json"
        self.py_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/phase1b_volatility_adaptation/phase1b_volatility_adaptation.py"
        
    def run_precise_analysis(self):
        """執行精確深度分析"""
        print("🔍 Phase1B 精確深度分析開始")
        print("="*80)
        
        # 1. 載入規範與代碼
        json_spec = self.load_json_spec()
        py_content = self.load_python_code()
        
        if not json_spec or not py_content:
            print("❌ 檔案載入失敗")
            return
        
        # 2. 架構角色確認
        print("\n📋 1. 架構角色確認")
        role_analysis = self.analyze_architectural_role(json_spec, py_content)
        
        # 3. 數據流精確分析
        print("\n🔄 2. 數據流精確分析")
        dataflow_analysis = self.analyze_dataflow_precision(json_spec, py_content)
        
        # 4. 層級邏輯深度檢查
        print("\n🏗️ 3. 層級邏輯深度檢查")
        layer_analysis = self.analyze_layer_logic(json_spec, py_content)
        
        # 5. 數據使用一致性驗證
        print("\n📊 4. 數據使用一致性驗證")
        data_usage_analysis = self.analyze_data_usage_consistency(json_spec, py_content)
        
        # 6. 核心演算法對應性
        print("\n⚡ 5. 核心演算法對應性")
        algorithm_analysis = self.analyze_algorithm_correspondence(json_spec, py_content)
        
        # 7. 整合度與完整性評估
        print("\n🎯 6. 整合度與完整性評估")
        integration_analysis = self.analyze_integration_completeness(json_spec, py_content)
        
        # 8. 生成精確匹配報告
        print("\n📈 7. 精確匹配報告")
        final_report = self.generate_final_report({
            'role': role_analysis,
            'dataflow': dataflow_analysis, 
            'layers': layer_analysis,
            'data_usage': data_usage_analysis,
            'algorithms': algorithm_analysis,
            'integration': integration_analysis
        })
        
        return final_report
    
    def load_json_spec(self) -> Dict[str, Any]:
        """載入 JSON 規範"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ JSON 載入失敗: {e}")
            return {}
    
    def load_python_code(self) -> str:
        """載入 Python 代碼"""
        try:
            with open(self.py_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Python 代碼載入失敗: {e}")
            return ""
    
    def analyze_architectural_role(self, json_spec: Dict, py_content: str) -> Dict[str, Any]:
        """分析架構角色 - 確認是信號適應器而非生成器"""
        print("   檢查架構角色定位...")
        
        analysis = {
            'json_role': None,
            'python_role': None,
            'role_match': False,
            'evidence': []
        }
        
        # 正確訪問 JSON 結構
        strategy_graph = json_spec.get('strategy_dependency_graph', {})
        integration_points = strategy_graph.get('integration_points', {})
        input_format = strategy_graph.get('input_format_compatibility', {})
        
        # JSON 規範角色分析
        receives_from = integration_points.get('receives_from', [])
        feeds_to = integration_points.get('feeds_to', [])
        
        if receives_from:
            analysis['json_role'] = 'signal_adapter'
            analysis['evidence'].append(f"JSON: receives_from = {receives_from}")
        
        processes_outputs = input_format.get('processes_standardized_outputs', False)
        if processes_outputs:
            analysis['json_role'] = 'signal_adapter'
            analysis['evidence'].append("JSON: processes_standardized_outputs = true (信號適應器)")
        
        if feeds_to:
            analysis['evidence'].append(f"JSON: feeds_to = {feeds_to}")
        
        # 檢查 JSON 中的描述
        description = strategy_graph.get('description', '')
        if '動態波動性監測與策略參數自適應調整系統' in description:
            analysis['json_role'] = 'signal_adapter'
            analysis['evidence'].append("JSON: 描述為'動態波動性監測與策略參數自適應調整系統' (信號適應器)")
        
        # Python 代碼角色分析
        if 'process_signals_with_volatility_adaptation' in py_content:
            analysis['python_role'] = 'signal_adapter'
            analysis['evidence'].append("Python: 主要入口點為 process_signals_with_volatility_adaptation()")
        
        # 檢查是否有錯誤的信號生成方法
        generation_methods = [
            '_generate_breakout_signal',
            '_generate_momentum_signal', 
            '_generate_reversal_signal'
        ]
        
        found_generation = False
        for method in generation_methods:
            if method in py_content:
                found_generation = True
                analysis['evidence'].append(f"Python: 發現信號生成方法 {method} (角色錯誤)")
        
        if not found_generation:
            analysis['evidence'].append("Python: 未發現信號生成方法 (角色正確)")
        
        # 角色匹配判斷
        analysis['role_match'] = (
            analysis['json_role'] == 'signal_adapter' and 
            analysis['python_role'] == 'signal_adapter' and 
            not found_generation
        )
        
        print(f"   JSON 角色: {analysis['json_role']}")
        print(f"   Python 角色: {analysis['python_role']}")
        print(f"   角色匹配: {'✅' if analysis['role_match'] else '❌'}")
        
        return analysis
    
    def analyze_dataflow_precision(self, json_spec: Dict, py_content: str) -> Dict[str, Any]:
        """精確分析數據流"""
        print("   檢查數據流精確性...")
        
        analysis = {
            'input_sources': {'json': [], 'python': []},
            'output_targets': {'json': [], 'python': []},
            'data_transformations': {'json': [], 'python': []},
            'flow_consistency': 0.0,
            'missing_flows': [],
            'extra_flows': []
        }
        
        # 正確訪問 JSON 結構
        strategy_graph = json_spec.get('strategy_dependency_graph', {})
        integration_points = strategy_graph.get('integration_points', {})
        computation_flow = strategy_graph.get('computation_flow', {})
        
        # JSON 數據流分析
        receives_from = integration_points.get('receives_from', [])
        feeds_to = integration_points.get('feeds_to', [])
        
        analysis['input_sources']['json'] = receives_from
        analysis['output_targets']['json'] = feeds_to
        
        # JSON 轉換流程
        layer_names = list(computation_flow.keys())
        analysis['data_transformations']['json'] = layer_names
        
        # Python 數據流分析
        # 檢查輸入處理
        if 'signals: List[Dict[str, Any]]' in py_content:
            analysis['input_sources']['python'].append('signals_parameter')
        
        if 'market_data: Dict[str, Any]' in py_content:
            analysis['input_sources']['python'].append('market_data_parameter')
        
        # 檢查輸出生成
        if 'AdaptiveSignalAdjustment' in py_content:
            analysis['output_targets']['python'].append('adaptive_signal_adjustments')
        
        # 檢查數據轉換
        layer_methods = [
            'layer_1_data_collection',
            'layer_2_volatility_metrics', 
            'layer_3_signal_adjustment',
            'layer_4_final_optimization'
        ]
        
        for method in layer_methods:
            if f'_layer_' in py_content and method.split('_', 2)[-1] in py_content:
                analysis['data_transformations']['python'].append(method)
        
        # 檢查缺失和額外流程
        json_layers = set(analysis['data_transformations']['json'])
        python_layers = set(analysis['data_transformations']['python'])
        
        analysis['missing_flows'] = list(json_layers - python_layers)
        analysis['extra_flows'] = list(python_layers - json_layers)
        
        # 計算流程一致性
        if len(analysis['input_sources']['json']) > 0:
            input_match = len(set(analysis['input_sources']['json']) & 
                             set(analysis['input_sources']['python'])) / len(analysis['input_sources']['json'])
        else:
            input_match = 1.0
        
        if len(analysis['output_targets']['json']) > 0:
            output_match = len(set(analysis['output_targets']['json']) & 
                              set(analysis['output_targets']['python'])) / len(analysis['output_targets']['json'])
        else:
            output_match = 1.0
        
        if len(analysis['data_transformations']['json']) > 0:
            transform_match = len(set(analysis['data_transformations']['python'])) / len(analysis['data_transformations']['json'])
        else:
            transform_match = 1.0
        
        analysis['flow_consistency'] = (input_match + output_match + transform_match) / 3
        
        print(f"   JSON 輸入源: {analysis['input_sources']['json']}")
        print(f"   Python 輸入源: {analysis['input_sources']['python']}")
        print(f"   JSON 輸出目標: {analysis['output_targets']['json']}")  
        print(f"   Python 輸出目標: {analysis['output_targets']['python']}")
        print(f"   JSON 層級: {analysis['data_transformations']['json']}")
        print(f"   Python 層級: {analysis['data_transformations']['python']}")
        print(f"   整體流程一致性: {analysis['flow_consistency']:.1%}")
        
        return analysis
    
    def analyze_layer_logic(self, json_spec: Dict, py_content: str) -> Dict[str, Any]:
        """分析層級邏輯深度檢查"""
        print("   檢查層級邏輯實現...")
        
        analysis = {
            'json_layers': {},
            'python_layers': {},
            'layer_alignment': {},
            'logic_completeness': 0.0,
            'missing_logic': [],
            'layer_data_flow': {}
        }
        
        # 正確訪問 JSON 結構
        strategy_graph = json_spec.get('strategy_dependency_graph', {})
        computation_flow = strategy_graph.get('computation_flow', {})
        
        # JSON 層級規範
        for layer_name, layer_config in computation_flow.items():
            operations = layer_config.get('operations', {})
            dependencies = layer_config.get('dependencies', [])
            description = layer_config.get('description', '')
            
            analysis['json_layers'][layer_name] = {
                'operations': list(operations.keys()),
                'dependencies': dependencies,
                'description': description,
                'operation_count': len(operations)
            }
        
        # Python 層級實現
        layer_patterns = {
            'layer_1_data_collection': r'async def _layer_1_data_collection.*?(?=async def|\Z)',
            'layer_2_volatility_metrics': r'async def _layer_2_volatility_metrics.*?(?=async def|\Z)',
            'layer_3_adaptive_parameters': r'async def _layer_3_signal_adjustment.*?(?=async def|\Z)',
            'layer_4_strategy_signals': r'async def _layer_4_final_optimization.*?(?=async def|\Z)'
        }
        
        for layer_name, pattern in layer_patterns.items():
            match = re.search(pattern, py_content, re.DOTALL)
            if match:
                layer_code = match.group(0)
                analysis['python_layers'][layer_name] = {
                    'implemented': True,
                    'code_length': len(layer_code),
                    'has_error_handling': 'try:' in layer_code and 'except' in layer_code,
                    'has_timing': 'time.time()' in layer_code,
                    'data_operations': self.extract_data_operations(layer_code)
                }
            else:
                analysis['python_layers'][layer_name] = {'implemented': False}
        
        # 層級對齊分析
        for layer_name in analysis['json_layers']:
            python_layer_name = layer_name
            # 映射名稱差異
            if layer_name == 'layer_3_adaptive_parameters':
                python_layer_name = 'layer_3_signal_adjustment'
            elif layer_name == 'layer_4_strategy_signals':
                python_layer_name = 'layer_4_final_optimization'
            
            if python_layer_name in analysis['python_layers'] and analysis['python_layers'][python_layer_name].get('implemented', False):
                json_layer = analysis['json_layers'][layer_name]
                python_layer = analysis['python_layers'][python_layer_name]
                
                # 檢查操作覆蓋率
                json_operations = json_layer['operations']
                python_operations = python_layer['data_operations']
                
                operation_coverage = 0.0
                if json_operations:
                    matched_operations = sum(1 for op in json_operations 
                                           if any(op.lower() in py_op.lower() for py_op in python_operations))
                    operation_coverage = matched_operations / len(json_operations)
                
                analysis['layer_alignment'][layer_name] = {
                    'operation_coverage': operation_coverage,
                    'has_error_handling': python_layer['has_error_handling'],
                    'has_timing': python_layer['has_timing'],
                    'python_layer_name': python_layer_name
                }
            else:
                analysis['layer_alignment'][layer_name] = {'implemented': False}
        
        # 計算邏輯完整性
        implemented_count = sum(1 for alignment in analysis['layer_alignment'].values() 
                               if alignment.get('implemented', True))
        total_layers = len(analysis['json_layers'])
        
        if total_layers > 0:
            analysis['logic_completeness'] = implemented_count / total_layers
        
        print(f"   JSON 層級數: {total_layers}")
        print(f"   Python 實現層級: {implemented_count}")
        print(f"   邏輯完整性: {analysis['logic_completeness']:.1%}")
        
        for layer_name, alignment in analysis['layer_alignment'].items():
            if alignment.get('implemented', True):
                coverage = alignment.get('operation_coverage', 0)
                print(f"   - {layer_name}: 操作覆蓋率 {coverage:.1%}")
        
        return analysis
    
    def extract_data_operations(self, code: str) -> List[str]:
        """提取代碼中的數據操作"""
        operations = []
        
        # 常見數據操作模式
        patterns = [
            r'(\w+_volatility)',
            r'(\w+_metrics)', 
            r'(\w+_calculation)',
            r'(\w+_adjustment)',
            r'(\w+_analysis)',
            r'(\w+_detection)',
            r'self\.(\w+)',
            r'np\.(\w+)',
            r'market_data\.get\([\'"](\w+)[\'"]'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, code)
            operations.extend(matches)
        
        return list(set(operations))  # 去重
    
    def analyze_data_usage_consistency(self, json_spec: Dict, py_content: str) -> Dict[str, Any]:
        """分析數據使用一致性"""
        print("   檢查數據使用一致性...")
        
        analysis = {
            'json_data_types': {},
            'python_data_types': {},
            'type_consistency': 0.0,
            'missing_data_types': [],
            'dataclass_alignment': {}
        }
        
        # JSON 數據類型規範
        if 'data_structures' in json_spec:
            for struct_name, struct_config in json_spec['data_structures'].items():
                analysis['json_data_types'][struct_name] = {
                    'fields': struct_config.get('fields', {}),
                    'required': struct_config.get('required', []),
                    'validation': struct_config.get('validation', {})
                }
        
        # Python 數據類型實現
        dataclass_pattern = r'@dataclass\s*\nclass\s+(\w+)'
        matches = re.finditer(dataclass_pattern, py_content, re.MULTILINE)
        
        for match in matches:
            class_name = match.group(1)
            start_pos = match.start()
            
            # 找到類的結束位置
            rest_content = py_content[start_pos:]
            
            # 查找下一個類或函數定義
            next_def = re.search(r'\n(class\s+\w+|def\s+\w+|@dataclass)', rest_content[100:])
            if next_def:
                class_content = rest_content[:100 + next_def.start()]
            else:
                class_content = rest_content[:1000]  # 取前1000字符
            
            # 提取欄位
            field_pattern = r'(\w+):\s*([\w\[\],\s\.\|]+?)(?=\s*#|\s*\n|$)'
            fields = re.findall(field_pattern, class_content, re.MULTILINE)
            
            analysis['python_data_types'][class_name] = {
                'fields': {field.strip(): field_type.strip() for field, field_type in fields},
                'field_count': len(fields)
            }'
        matches = re.findall(dataclass_pattern, py_content, re.DOTALL)
        
        for match in matches:
            class_name = match
            # 查找類定義
            class_pattern = f'@dataclass\\s+class\\s+{class_name}.*?(?=@dataclass|class\\s+\\w+(?!.*:)|def\\s+\\w+|\\Z)'
            class_match = re.search(class_pattern, py_content, re.DOTALL)
            
            if class_match:
                class_code = class_match.group(0)
                fields = re.findall(r'(\w+):\s*([\w\[\],\s]+)', class_code)
                analysis['python_data_types'][class_name] = {
                    'fields': {field: field_type for field, field_type in fields},
                    'field_count': len(fields)
                }
        
        # DataClass 對齊分析
        for json_struct in analysis['json_data_types']:
            if json_struct in analysis['python_data_types']:
                json_fields = set(analysis['json_data_types'][json_struct]['fields'].keys())
                python_fields = set(analysis['python_data_types'][json_struct]['fields'].keys())
                
                common_fields = json_fields & python_fields
                missing_fields = json_fields - python_fields
                extra_fields = python_fields - json_fields
                
                analysis['dataclass_alignment'][json_struct] = {
                    'field_coverage': len(common_fields) / max(1, len(json_fields)),
                    'missing_fields': list(missing_fields),
                    'extra_fields': list(extra_fields)
                }
        
        # 計算類型一致性
        if analysis['json_data_types'] and analysis['python_data_types']:
            aligned_count = len(analysis['dataclass_alignment'])
            total_json_types = len(analysis['json_data_types'])
            analysis['type_consistency'] = aligned_count / total_json_types
        
        print(f"   數據結構對齊: {len(analysis['dataclass_alignment'])}/{len(analysis['json_data_types'])}")
        print(f"   類型一致性: {analysis['type_consistency']:.1%}")
        
        return analysis
    
    def analyze_algorithm_correspondence(self, json_spec: Dict, py_content: str) -> Dict[str, Any]:
        """分析核心演算法對應性"""
        print("   檢查核心演算法對應性...")
        
        analysis = {
            'json_algorithms': {},
            'python_algorithms': {},
            'algorithm_coverage': 0.0,
            'implementation_quality': {},
            'missing_algorithms': []
        }
        
        # 正確訪問 JSON 結構
        strategy_graph = json_spec.get('strategy_dependency_graph', {})
        computation_flow = strategy_graph.get('computation_flow', {})
        
        # JSON 演算法規範（從 computation_flow 提取）
        for layer_name, layer_config in computation_flow.items():
            operations = layer_config.get('operations', {})
            analysis['json_algorithms'][layer_name] = list(operations.keys())
        
        # Python 演算法實現檢查
        algorithm_patterns = {
            'volatility_calculation': [
                '_calculate_historical_volatility',
                '_calculate_realized_volatility'
            ],
            'regime_detection': [
                '_detect_volatility_regime',
                '_assess_regime_stability'
            ],
            'signal_adjustment': [
                '_calculate_volatility_adjustment',
                '_calculate_regime_adjustment',
                '_calculate_activity_adjustment'
            ],
            'optimization': [
                '_resolve_signal_conflicts',
                '_optimize_signal_portfolio',
                '_apply_risk_adjustments'
            ]
        }
        
        for algo_category, methods in algorithm_patterns.items():
            implemented_methods = []
            for method in methods:
                if method in py_content:
                    implemented_methods.append(method)
                    
                    # 檢查實現質量
                    method_pattern = f'def {method}.*?(?=def |\\Z)'
                    method_match = re.search(method_pattern, py_content, re.DOTALL)
                    if method_match:
                        method_code = method_match.group(0)
                        quality_score = self.assess_implementation_quality(method_code)
                        analysis['implementation_quality'][method] = quality_score
            
            analysis['python_algorithms'][algo_category] = {
                'methods': implemented_methods,
                'coverage': len(implemented_methods) / len(methods) if methods else 1.0
            }
        
        # 計算整體演算法覆蓋率
        if algorithm_patterns:
            total_coverage = sum(cat['coverage'] for cat in analysis['python_algorithms'].values())
            analysis['algorithm_coverage'] = total_coverage / len(algorithm_patterns)
        
        # 檢查缺失演算法
        for category, info in analysis['python_algorithms'].items():
            if info['coverage'] < 1.0:
                total_methods = len(algorithm_patterns[category])
                implemented_count = len(info['methods'])
                missing_count = total_methods - implemented_count
                analysis['missing_algorithms'].append(f"{category}: {missing_count} 個方法缺失")
        
        print(f"   JSON 演算法層級: {len(analysis['json_algorithms'])}")
        print(f"   Python 演算法類別: {len(analysis['python_algorithms'])}")
        print(f"   演算法覆蓋率: {analysis['algorithm_coverage']:.1%}")
        
        for category, info in analysis['python_algorithms'].items():
            print(f"   - {category}: {info['coverage']:.1%} ({len(info['methods'])} 個方法)")
        
        return analysis
    
    def assess_implementation_quality(self, method_code: str) -> float:
        """評估實現質量"""
        quality_score = 0.0
        
        # 檢查項目
        checks = [
            ('error_handling', 'try:' in method_code and 'except' in method_code),
            ('input_validation', 'if len(' in method_code or 'if not ' in method_code),
            ('numpy_usage', 'np.' in method_code),
            ('logging', 'logger.' in method_code),
            ('return_validation', 'max(' in method_code and 'min(' in method_code),
            ('documentation', '"""' in method_code or "'''" in method_code)
        ]
        
        for check_name, passed in checks:
            if passed:
                quality_score += 1.0 / len(checks)
        
        return quality_score
    
    def analyze_integration_completeness(self, json_spec: Dict, py_content: str) -> Dict[str, Any]:
        """分析整合度與完整性"""
        print("   檢查整合度與完整性...")
        
        analysis = {
            'configuration_integration': 0.0,
            'error_handling_coverage': 0.0,
            'performance_monitoring': 0.0,
            'external_dependencies': {'json': [], 'python': []},
            'integration_score': 0.0
        }
        
        # 配置整合度
        config_usage = [
            'self.config',
            '_load_config',
            'config_path'
        ]
        config_found = sum(1 for usage in config_usage if usage in py_content)
        analysis['configuration_integration'] = config_found / len(config_usage)
        
        # 錯誤處理覆蓋率
        error_patterns = [
            'try:',
            'except Exception',
            'logger.error',
            'logger.warning'
        ]
        error_found = sum(1 for pattern in error_patterns if pattern in py_content)
        analysis['error_handling_coverage'] = min(1.0, error_found / len(error_patterns))
        
        # 性能監控
        performance_patterns = [
            'time.time()',
            'processing_time',
            'performance',
            'time_budget'
        ]
        perf_found = sum(1 for pattern in performance_patterns if pattern in py_content)
        analysis['performance_monitoring'] = min(1.0, perf_found / len(performance_patterns))
        
        # JSON 外部依賴
        if 'external_dependencies' in json_spec:
            analysis['external_dependencies']['json'] = json_spec['external_dependencies']
        
        # Python 外部依賴
        import_patterns = re.findall(r'import\s+(\w+)|from\s+(\w+)', py_content)
        python_imports = [imp[0] or imp[1] for imp in import_patterns]
        analysis['external_dependencies']['python'] = python_imports
        
        # 計算整合評分
        analysis['integration_score'] = (
            analysis['configuration_integration'] * 0.3 +
            analysis['error_handling_coverage'] * 0.3 +
            analysis['performance_monitoring'] * 0.4
        )
        
        print(f"   配置整合: {analysis['configuration_integration']:.1%}")
        print(f"   錯誤處理: {analysis['error_handling_coverage']:.1%}")
        print(f"   性能監控: {analysis['performance_monitoring']:.1%}")
        print(f"   整合評分: {analysis['integration_score']:.1%}")
        
        return analysis
    
    def generate_final_report(self, all_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成最終精確匹配報告"""
        
        # 計算各項權重評分
        weights = {
            'role': 0.20,      # 架構角色 20%
            'dataflow': 0.25,  # 數據流 25%
            'layers': 0.20,    # 層級邏輯 20%
            'data_usage': 0.15, # 數據使用 15%
            'algorithms': 0.15, # 演算法 15%
            'integration': 0.05 # 整合度 5%
        }
        
        scores = {
            'role': 1.0 if all_analysis['role']['role_match'] else 0.0,
            'dataflow': all_analysis['dataflow']['flow_consistency'],
            'layers': all_analysis['layers']['logic_completeness'],
            'data_usage': all_analysis['data_usage']['type_consistency'],
            'algorithms': all_analysis['algorithms']['algorithm_coverage'],
            'integration': all_analysis['integration']['integration_score']
        }
        
        # 計算總體匹配度
        total_score = sum(scores[key] * weights[key] for key in weights)
        
        # 識別關鍵問題
        critical_issues = []
        if scores['role'] < 1.0:
            critical_issues.append("架構角色定位不準確")
        if scores['dataflow'] < 0.8:
            critical_issues.append("數據流不完整")
        if scores['layers'] < 0.8:
            critical_issues.append("層級邏輯實現不足")
        if scores['algorithms'] < 0.7:
            critical_issues.append("核心演算法覆蓋不足")
        
        # 優秀實現點
        strengths = []
        if scores['role'] >= 1.0:
            strengths.append("架構角色定位正確")
        if scores['dataflow'] >= 0.9:
            strengths.append("數據流設計優秀")
        if scores['layers'] >= 0.9:
            strengths.append("層級邏輯實現完整")
        if scores['algorithms'] >= 0.8:
            strengths.append("演算法實現覆蓋良好")
        if scores['integration'] >= 0.8:
            strengths.append("系統整合度高")
        
        report = {
            'total_match_percentage': total_score * 100,
            'component_scores': {k: v * 100 for k, v in scores.items()},
            'critical_issues': critical_issues,
            'strengths': strengths,
            'detailed_analysis': all_analysis,
            'recommendations': self.generate_recommendations(scores, all_analysis)
        }
        
        # 打印報告
        print(f"\n📊 總體匹配度: {report['total_match_percentage']:.1f}%")
        print(f"🏗️ 架構角色: {scores['role']*100:.1f}%")
        print(f"🔄 數據流: {scores['dataflow']*100:.1f}%") 
        print(f"🏢 層級邏輯: {scores['layers']*100:.1f}%")
        print(f"📊 數據使用: {scores['data_usage']*100:.1f}%")
        print(f"⚡ 演算法: {scores['algorithms']*100:.1f}%")
        print(f"🔗 整合度: {scores['integration']*100:.1f}%")
        
        if critical_issues:
            print(f"\n❌ 關鍵問題: {', '.join(critical_issues)}")
        
        if strengths:
            print(f"\n✅ 優秀實現: {', '.join(strengths)}")
        
        return report
    
    def generate_recommendations(self, scores: Dict[str, float], all_analysis: Dict[str, Any]) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        if scores['role'] < 1.0:
            recommendations.append("確認並修正架構角色定位為信號適應器")
        
        if scores['dataflow'] < 0.8:
            recommendations.append("補充缺失的數據流接口和轉換邏輯")
        
        if scores['layers'] < 0.8:
            recommendations.append("完善層級處理邏輯和錯誤處理機制")
        
        if scores['data_usage'] < 0.8:
            recommendations.append("對齊數據結構定義和使用方式")
        
        if scores['algorithms'] < 0.7:
            recommendations.append("實現缺失的核心演算法模組")
        
        if scores['integration'] < 0.7:
            recommendations.append("加強配置整合和性能監控")
        
        return recommendations

if __name__ == "__main__":
    analyzer = Phase1BPreciseAnalyzer()
    report = analyzer.run_precise_analysis()
