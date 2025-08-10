#!/usr/bin/env python3
"""
🔍 Trading X - Phase1 深度代碼審計工具
全盤檢查6大模組的每一行代碼，確保100%符合JSON規範
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple

class DeepPhase1Auditor:
    """Phase1深度代碼審計器"""
    
    def __init__(self):
        self.base_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation")
        self.audit_results = {}
        self.critical_issues = []
        self.data_format_mismatches = []
        self.flow_issues = []
        
        # 6大模組配置
        self.modules = {
            "websocket_realtime_driver": {
                "py_file": "websocket_realtime_driver/websocket_realtime_driver.py",
                "json_file": "websocket_realtime_driver/websocket_realtime_driver_dependency.json"
            },
            "phase1a_basic_signal_generation": {
                "py_file": "phase1a_basic_signal_generation/phase1a_basic_signal_generation.py",
                "json_file": "phase1a_basic_signal_generation/phase1a_basic_signal_generation.json"
            },
            "indicator_dependency_graph": {
                "py_file": "indicator_dependency/indicator_dependency_graph.py",
                "json_file": "indicator_dependency/indicator_dependency_graph.json"
            },
            "phase1b_volatility_adaptation": {
                "py_file": "phase1b_volatility_adaptation/phase1b_volatility_adaptation.py",
                "json_file": "phase1b_volatility_adaptation/phase1b_volatility_adaptation_dependency.json"
            },
            "phase1c_signal_standardization": {
                "py_file": "phase1c_signal_standardization/phase1c_signal_standardization.py",
                "json_file": "phase1c_signal_standardization/phase1c_signal_standardization.json"
            },
            "unified_signal_candidate_pool": {
                "py_file": "unified_signal_pool/unified_signal_candidate_pool.py",
                "json_file": "unified_signal_pool/unified_signal_candidate_pool_v3_dependency.json"
            }
        }
    
    def audit_all_modules(self):
        """審計所有模組"""
        print("🔍 開始Phase1深度代碼審計...")
        print("=" * 80)
        
        for module_name, config in self.modules.items():
            print(f"\n🔍 審計模組: {module_name}")
            print("-" * 60)
            
            self.audit_module(module_name, config)
        
        self.generate_comprehensive_report()
    
    def audit_module(self, module_name: str, config: Dict[str, str]):
        """審計單個模組"""
        try:
            # 讀取Python文件
            py_path = self.base_path / config["py_file"]
            with open(py_path, 'r', encoding='utf-8') as f:
                py_content = f.read()
            
            # 讀取JSON規範
            json_path = self.base_path / config["json_file"]
            with open(json_path, 'r', encoding='utf-8') as f:
                json_spec = json.load(f)
            
            print(f"📄 Python文件: {py_path.name} ({len(py_content.splitlines())} 行)")
            print(f"📋 JSON規範: {json_path.name}")
            
            # 進行深度檢查
            self.check_data_formats(module_name, py_content, json_spec)
            self.check_method_signatures(module_name, py_content, json_spec)
            self.check_data_flow_consistency(module_name, py_content, json_spec)
            self.check_input_output_mapping(module_name, py_content, json_spec)
            
        except Exception as e:
            error = f"❌ {module_name}: 無法讀取文件 - {e}"
            self.critical_issues.append(error)
            print(error)
    
    def check_data_formats(self, module_name: str, py_content: str, json_spec: Dict):
        """檢查數據格式是否符合JSON規範"""
        print("  🔍 檢查數據格式...")
        
        # 提取JSON中定義的數據類型
        json_data_types = self.extract_json_data_types(json_spec)
        
        # 檢查Python代碼中的數據類型使用
        for data_type in json_data_types:
            if data_type not in py_content:
                mismatch = f"⚠️ {module_name}: 缺少JSON定義的數據類型 '{data_type}'"
                self.data_format_mismatches.append(mismatch)
                print(f"    {mismatch}")
            else:
                print(f"    ✅ 發現數據類型: {data_type}")
        
        # 檢查Python中是否有未定義的數據類型
        py_data_types = self.extract_py_data_types(py_content)
        for data_type in py_data_types:
            if data_type not in json_data_types and data_type not in ['str', 'int', 'float', 'bool', 'Dict', 'List']:
                warning = f"⚠️ {module_name}: Python中使用了未在JSON中定義的數據類型 '{data_type}'"
                self.data_format_mismatches.append(warning)
                print(f"    {warning}")
    
    def extract_json_data_types(self, json_spec: Dict) -> List[str]:
        """從JSON規範中提取數據類型"""
        data_types = set()
        
        def extract_recursive(obj, key=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if 'data_type' in k.lower() or 'type' in k.lower():
                        if isinstance(v, str):
                            data_types.add(v)
                        elif isinstance(v, list):
                            data_types.update(v)
                    if 'output' in k.lower() or 'input' in k.lower():
                        if isinstance(v, str):
                            data_types.add(v)
                        elif isinstance(v, list):
                            data_types.update(v)
                    extract_recursive(v, k)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item, key)
        
        extract_recursive(json_spec)
        return list(data_types)
    
    def extract_py_data_types(self, py_content: str) -> List[str]:
        """從Python代碼中提取數據類型"""
        # 查找類定義
        class_pattern = r'class\s+(\w+)'
        classes = re.findall(class_pattern, py_content)
        
        # 查找dataclass定義
        dataclass_pattern = r'@dataclass\s+class\s+(\w+)'
        dataclasses = re.findall(dataclass_pattern, py_content)
        
        # 查找字符串字面量中的類型定義
        type_pattern = r'"type":\s*"([^"]+)"'
        types = re.findall(type_pattern, py_content)
        
        return list(set(classes + dataclasses + types))
    
    def check_method_signatures(self, module_name: str, py_content: str, json_spec: Dict):
        """檢查方法簽名是否符合JSON規範"""
        print("  🔍 檢查方法簽名...")
        
        # 提取JSON中要求的方法
        required_methods = self.extract_required_methods(json_spec)
        
        for method in required_methods:
            # 將方法名轉換為Python格式
            py_method = method.replace(" ", "_").replace("'", "").replace("\"", "")
            
            if f"def {method}" in py_content or f"async def {method}" in py_content or \
               f"def {py_method}" in py_content or f"async def {py_method}" in py_content:
                print(f"    ✅ 發現必要方法: {method}")
            else:
                issue = f"❌ {module_name}: 缺少必要方法 '{method}'"
                self.critical_issues.append(issue)
                print(f"    {issue}")
    
    def extract_required_methods(self, json_spec: Dict) -> List[str]:
        """從JSON規範中提取必要方法"""
        methods = set()
        
        def extract_methods_recursive(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if 'method' in k.lower() or 'function' in k.lower():
                        if isinstance(v, str):
                            methods.add(v)
                        elif isinstance(v, list):
                            methods.update(v)
                    extract_methods_recursive(v)
            elif isinstance(obj, list):
                for item in obj:
                    extract_methods_recursive(item)
        
        extract_methods_recursive(json_spec)
        return list(methods)
    
    def check_data_flow_consistency(self, module_name: str, py_content: str, json_spec: Dict):
        """檢查數據流一致性"""
        print("  🔍 檢查數據流一致性...")
        
        # 檢查輸入處理
        inputs = self.extract_inputs_from_json(json_spec)
        for input_type in inputs:
            if input_type not in py_content:
                issue = f"⚠️ {module_name}: 數據流缺少輸入處理 '{input_type}'"
                self.flow_issues.append(issue)
                print(f"    {issue}")
            else:
                print(f"    ✅ 輸入處理: {input_type}")
        
        # 檢查輸出生成
        outputs = self.extract_outputs_from_json(json_spec)
        for output_type in outputs:
            if output_type not in py_content:
                issue = f"⚠️ {module_name}: 數據流缺少輸出生成 '{output_type}'"
                self.flow_issues.append(issue)
                print(f"    {issue}")
            else:
                print(f"    ✅ 輸出生成: {output_type}")
    
    def extract_inputs_from_json(self, json_spec: Dict) -> List[str]:
        """從JSON中提取輸入類型"""
        inputs = set()
        
        def extract_recursive(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if 'input' in k.lower() and not 'output' in k.lower():
                        if isinstance(v, str):
                            inputs.add(v)
                        elif isinstance(v, list):
                            inputs.update(v)
                        elif isinstance(v, dict):
                            if 'data_types' in v:
                                if isinstance(v['data_types'], list):
                                    inputs.update(v['data_types'])
                    extract_recursive(v)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
        
        extract_recursive(json_spec)
        return list(inputs)
    
    def extract_outputs_from_json(self, json_spec: Dict) -> List[str]:
        """從JSON中提取輸出類型"""
        outputs = set()
        
        def extract_recursive(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if 'output' in k.lower():
                        if isinstance(v, str):
                            outputs.add(v)
                        elif isinstance(v, list):
                            outputs.update(v)
                        elif isinstance(v, dict):
                            if 'data_types' in v:
                                if isinstance(v['data_types'], list):
                                    outputs.update(v['data_types'])
                    extract_recursive(v)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
        
        extract_recursive(json_spec)
        return list(outputs)
    
    def check_input_output_mapping(self, module_name: str, py_content: str, json_spec: Dict):
        """檢查輸入輸出映射"""
        print("  🔍 檢查輸入輸出映射...")
        
        # 這是更詳細的流程檢查
        # 檢查是否有完整的處理鏈
        processing_chain_keywords = [
            'process_', 'handle_', 'generate_', 'calculate_', 'analyze_', 'aggregate_', 'standardize_'
        ]
        
        found_processors = []
        for keyword in processing_chain_keywords:
            if keyword in py_content:
                found_processors.append(keyword)
        
        if found_processors:
            print(f"    ✅ 發現處理器: {', '.join(found_processors)}")
        else:
            issue = f"⚠️ {module_name}: 缺少數據處理方法"
            self.flow_issues.append(issue)
            print(f"    {issue}")
    
    def generate_comprehensive_report(self):
        """生成綜合報告"""
        print("\n" + "=" * 80)
        print("📊 Phase1深度代碼審計報告")
        print("=" * 80)
        
        total_critical = len(self.critical_issues)
        total_format_issues = len(self.data_format_mismatches)
        total_flow_issues = len(self.flow_issues)
        total_issues = total_critical + total_format_issues + total_flow_issues
        
        if total_issues == 0:
            print("🎉 恭喜！所有6大模組完全符合JSON規範")
            score = 100
        else:
            score = max(0, 100 - total_issues * 5)
            print(f"📊 總體評分: {score}/100")
        
        print(f"\n📈 問題統計:")
        print(f"   ❌ 嚴重問題: {total_critical}")
        print(f"   ⚠️ 數據格式不匹配: {total_format_issues}")
        print(f"   🔄 數據流問題: {total_flow_issues}")
        print(f"   📊 總計: {total_issues}")
        
        if self.critical_issues:
            print(f"\n❌ 嚴重問題 ({len(self.critical_issues)}):")
            for issue in self.critical_issues:
                print(f"   {issue}")
        
        if self.data_format_mismatches:
            print(f"\n⚠️ 數據格式不匹配 ({len(self.data_format_mismatches)}):")
            for issue in self.data_format_mismatches[:10]:  # 限制顯示數量
                print(f"   {issue}")
            if len(self.data_format_mismatches) > 10:
                print(f"   ... 還有 {len(self.data_format_mismatches) - 10} 項")
        
        if self.flow_issues:
            print(f"\n🔄 數據流問題 ({len(self.flow_issues)}):")
            for issue in self.flow_issues[:10]:  # 限制顯示數量
                print(f"   {issue}")
            if len(self.flow_issues) > 10:
                print(f"   ... 還有 {len(self.flow_issues) - 10} 項")
        
        return {
            'score': score,
            'critical_issues': self.critical_issues,
            'format_issues': self.data_format_mismatches,
            'flow_issues': self.flow_issues
        }

if __name__ == "__main__":
    auditor = DeepPhase1Auditor()
    auditor.audit_all_modules()
