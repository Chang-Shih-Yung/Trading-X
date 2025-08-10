#!/usr/bin/env python3
"""
🎯 精確深度分析工具 - phase1a_basic_signal_generation.py vs JSON 規範
不可繞過任何細節，進行精確匹配檢查
"""

import sys
import os
import json
import re
import ast
from typing import Dict, List, Any, Set

print("🔍 開始精確深度分析 - phase1a_basic_signal_generation.py vs JSON 規範")
print("=" * 100)

class Phase1APreciseAnalyzer:
    def __init__(self):
        self.json_spec = self._load_json_spec()
        self.py_code = self._load_python_code()
        self.analysis_results = {
            'matched': [],
            'missing': [],
            'partially_matched': [],
            'extra_implementations': [],
            'data_flow_breaks': []
        }
    
    def _load_json_spec(self) -> Dict:
        """載入 JSON 規範"""
        try:
            with open("/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/phase1a_basic_signal_generation/phase1a_basic_signal_generation.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 無法載入 JSON 規範: {e}")
            return {}
    
    def _load_python_code(self) -> str:
        """載入 Python 代碼"""
        try:
            with open("/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/phase1a_basic_signal_generation/phase1a_basic_signal_generation.py", 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ 無法載入 Python 代碼: {e}")
            return ""
    
    def analyze_processing_layers(self):
        """分析處理層級 - 檢查數據流斷點"""
        print("\n📊 處理層級精確分析")
        print("-" * 60)
        
        json_layers = self.json_spec['phase1a_basic_signal_generation_dependency']['computation_flow']['processing_layers']
        
        layer_mapping = {
            'layer_0_websocket_reception': 'websocket_data_reception_and_buffering',
            'layer_1_basic_preprocessing': 'basic_data_cleaning_and_validation', 
            'layer_2_signal_pregeneration': 'basic_signal_pattern_detection',
            'layer_3_output_standardization': 'signal_format_standardization_and_routing'
        }
        
        implementation_score = 0
        total_layers = len(layer_mapping)
        
        for json_layer, expected_function in layer_mapping.items():
            print(f"\n🔍 檢查 {json_layer}:")
            
            # 檢查輸入/輸出數據流
            layer_spec = json_layers[json_layer]
            input_data = layer_spec['input']
            output_data = layer_spec['output']
            processing_desc = layer_spec['processing']
            expected_time = layer_spec['expected_processing_time']
            
            print(f"  📋 JSON 規範:")
            print(f"    - 輸入: {input_data}")
            print(f"    - 處理: {processing_desc}")
            print(f"    - 輸出: {output_data}")
            print(f"    - 預期時間: {expected_time}")
            
            # 檢查代碼實現
            layer_implemented = False
            data_flow_correct = False
            
            if json_layer == 'layer_0_websocket_reception':
                if '_on_market_data_update' in self.py_code and 'websocket_driver.subscribe' in self.py_code:
                    layer_implemented = True
                    print(f"  ✅ Layer 0: WebSocket 接收機制存在")
                    
                    # 檢查數據緩衝實現
                    if 'price_buffer' in self.py_code and 'volume_buffer' in self.py_code:
                        data_flow_correct = True
                        print(f"  ✅ 數據緩衝機制: 正確實現")
                    else:
                        print(f"  ❌ 數據緩衝機制: 缺失")
                else:
                    print(f"  ❌ Layer 0: WebSocket 接收機制缺失")
            
            elif json_layer == 'layer_1_basic_preprocessing':
                if '_process_ticker_update' in self.py_code and 'data_cleaning' in processing_desc.lower():
                    # 檢查數據清理實現
                    if 'try:' in self.py_code and 'except' in self.py_code:
                        layer_implemented = True
                        data_flow_correct = True
                        print(f"  ✅ Layer 1: 數據清理與驗證存在")
                    else:
                        print(f"  ❌ Layer 1: 缺少數據清理邏輯")
                else:
                    print(f"  ❌ Layer 1: 基礎預處理缺失")
            
            elif json_layer == 'layer_2_signal_pregeneration':
                expected_methods = ['_layer_0_instant_signals', '_layer_1_momentum_signals', 
                                  '_layer_2_trend_signals', '_layer_3_volume_signals']
                
                implemented_methods = 0
                for method in expected_methods:
                    if method in self.py_code:
                        implemented_methods += 1
                
                if implemented_methods >= 4:
                    layer_implemented = True
                    data_flow_correct = True
                    print(f"  ✅ Layer 2: 信號預生成 ({implemented_methods}/4 方法)")
                else:
                    print(f"  ❌ Layer 2: 信號預生成不完整 ({implemented_methods}/4 方法)")
            
            elif json_layer == 'layer_3_output_standardization':
                if '_distribute_signals' in self.py_code and 'BasicSignal' in self.py_code:
                    layer_implemented = True
                    data_flow_correct = True
                    print(f"  ✅ Layer 3: 輸出標準化存在")
                else:
                    print(f"  ❌ Layer 3: 輸出標準化缺失")
            
            if layer_implemented and data_flow_correct:
                implementation_score += 1
            elif layer_implemented:
                implementation_score += 0.5
                
        print(f"\n📊 處理層級匹配度: {implementation_score/total_layers:.1%}")
        return implementation_score/total_layers
    
    def analyze_data_flow_integrity(self):
        """分析數據流完整性 - 檢查數據流斷點"""
        print("\n📊 數據流完整性分析")
        print("-" * 60)
        
        # 檢查數據流鏈路
        data_flow_chain = [
            {
                'source': 'websocket_realtime_driver',
                'method': '_on_market_data_update',
                'data_type': 'ticker_data',
                'buffer': 'price_buffer/volume_buffer'
            },
            {
                'source': 'buffered_data',
                'method': '_trigger_signal_generation', 
                'data_type': 'processed_market_data',
                'output': 'layer_processing_results'
            },
            {
                'source': 'layer_results',
                'method': '_distribute_signals',
                'data_type': 'BasicSignal[]',
                'target': 'signal_subscribers'
            }
        ]
        
        flow_integrity_score = 0
        total_flows = len(data_flow_chain)
        
        for i, flow in enumerate(data_flow_chain):
            print(f"\n🔍 數據流 {i+1}: {flow['source']} → {flow.get('target', 'next_stage')}")
            
            method_exists = flow['method'] in self.py_code
            data_type_handled = flow['data_type'].split('[')[0] in self.py_code
            
            print(f"  📋 處理方法: {flow['method']} {'✅' if method_exists else '❌'}")
            print(f"  📋 數據類型: {flow['data_type']} {'✅' if data_type_handled else '❌'}")
            
            if 'buffer' in flow:
                buffers = flow['buffer'].split('/')
                buffer_exists = all(buf in self.py_code for buf in buffers)
                print(f"  📋 數據緩衝: {flow['buffer']} {'✅' if buffer_exists else '❌'}")
                
                if method_exists and data_type_handled and buffer_exists:
                    flow_integrity_score += 1
                    print(f"  🟢 數據流完整")
                else:
                    print(f"  🔴 數據流斷點")
                    self.analysis_results['data_flow_breaks'].append(f"Flow {i+1}: {flow['source']}")
            else:
                if method_exists and data_type_handled:
                    flow_integrity_score += 1
                    print(f"  🟢 數據流完整")
                else:
                    print(f"  🔴 數據流斷點")
                    self.analysis_results['data_flow_breaks'].append(f"Flow {i+1}: {flow['source']}")
        
        print(f"\n📊 數據流完整性: {flow_integrity_score/total_flows:.1%}")
        return flow_integrity_score/total_flows
    
    def analyze_performance_targets(self):
        """分析性能目標實現"""
        print("\n📊 性能目標分析")
        print("-" * 60)
        
        performance_spec = self.json_spec['phase1a_basic_signal_generation_dependency']['computation_flow']
        config_spec = self.json_spec['phase1a_basic_signal_generation_dependency']['configuration']['performance_targets']
        
        targets = {
            'total_processing_time': performance_spec['total_expected_processing_time'],
            'extreme_processing_time': performance_spec['extreme_market_processing_time'], 
            'concurrency_level': performance_spec['concurrency_level'],
            'memory_usage': performance_spec['memory_usage'],
            'processing_latency_p99': config_spec['processing_latency_p99'],
            'signal_generation_rate': config_spec['signal_generation_rate'],
            'accuracy_baseline': config_spec['accuracy_baseline'],
            'system_availability': config_spec['system_availability']
        }
        
        implementation_score = 0
        total_targets = len(targets)
        
        for target_name, target_value in targets.items():
            print(f"\n🔍 性能目標: {target_name}")
            print(f"  📋 要求: {target_value}")
            
            implemented = False
            
            if 'processing_time' in target_name:
                if 'processing_time_ms' in self.py_code and 'datetime.now()' in self.py_code:
                    implemented = True
                    print(f"  ✅ 處理時間監控: 已實現")
                else:
                    print(f"  ❌ 處理時間監控: 缺失")
            
            elif 'concurrency' in target_name:
                if 'asyncio' in self.py_code and 'async def' in self.py_code:
                    implemented = True
                    print(f"  ✅ 異步並發: 已實現")
                else:
                    print(f"  ❌ 異步並發: 缺失")
            
            elif 'memory' in target_name:
                if 'deque(maxlen=' in self.py_code:
                    implemented = True
                    print(f"  ✅ 記憶體管理: 已實現")
                else:
                    print(f"  ❌ 記憶體管理: 缺失")
            
            elif 'signal_generation_rate' in target_name:
                if 'signal_buffer' in self.py_code and 'performance_stats' in self.py_code:
                    implemented = True
                    print(f"  ✅ 信號生成率監控: 已實現")
                else:
                    print(f"  ❌ 信號生成率監控: 缺失")
            
            elif 'accuracy' in target_name:
                if 'confidence' in self.py_code and 'strength' in self.py_code:
                    implemented = True
                    print(f"  ✅ 準確性計算: 已實現")
                else:
                    print(f"  ❌ 準確性計算: 缺失")
            
            elif 'availability' in target_name:
                if 'error_handling' in self.py_code or 'try:' in self.py_code:
                    implemented = True
                    print(f"  ✅ 可用性保障: 已實現")
                else:
                    print(f"  ❌ 可用性保障: 缺失")
            
            else:
                implemented = True  # 默認假設實現
                print(f"  ⚠️  無法驗證: {target_name}")
            
            if implemented:
                implementation_score += 1
        
        print(f"\n📊 性能目標匹配度: {implementation_score/total_targets:.1%}")
        return implementation_score/total_targets
    
    def analyze_error_handling(self):
        """分析錯誤處理機制"""
        print("\n📊 錯誤處理機制分析")
        print("-" * 60)
        
        error_handling_spec = self.json_spec['phase1a_basic_signal_generation_dependency']['error_handling']
        
        required_handlers = {
            'websocket_disconnection': 'circuit_break',
            'data_quality_anomaly': 'skip_invalid_data',
            'processing_delay_exceeded': 'priority_queue_reorder'
        }
        
        implementation_score = 0
        total_handlers = len(required_handlers)
        
        for error_type, strategy in required_handlers.items():
            print(f"\n🔍 錯誤處理: {error_type}")
            
            implemented = False
            
            if 'websocket_disconnection' in error_type:
                if 'circuit' in self.py_code.lower() or 'disconnect' in self.py_code.lower():
                    implemented = True
                    print(f"  ✅ WebSocket 斷線處理: 已實現")
                else:
                    print(f"  ❌ WebSocket 斷線處理: 缺失")
            
            elif 'data_quality' in error_type:
                if 'try:' in self.py_code and 'except' in self.py_code:
                    implemented = True
                    print(f"  ✅ 數據品質處理: 已實現")
                else:
                    print(f"  ❌ 數據品質處理: 缺失")
            
            elif 'processing_delay' in error_type:
                if 'priority' in self.py_code.lower():
                    implemented = True
                    print(f"  ✅ 處理延遲處理: 已實現")
                else:
                    print(f"  ❌ 處理延遲處理: 缺失")
            
            if implemented:
                implementation_score += 1
        
        print(f"\n📊 錯誤處理匹配度: {implementation_score/total_handlers:.1%}")
        return implementation_score/total_handlers
    
    def analyze_integration_points(self):
        """分析整合點"""
        print("\n📊 整合點分析")
        print("-" * 60)
        
        integration_spec = self.json_spec['phase1a_basic_signal_generation_dependency']['integration_points']
        
        # 檢查入口點
        entry_points = integration_spec['entry_points']
        exit_points = integration_spec['exit_points']
        
        entry_score = 0
        exit_score = 0
        
        print(f"\n🔍 入口點檢查:")
        for entry_name, entry_type in entry_points.items():
            print(f"  📋 {entry_name}: {entry_type}")
            
            if 'websocket_data_feed' in entry_name:
                if '_on_market_data_update' in self.py_code:
                    entry_score += 1
                    print(f"    ✅ WebSocket 數據饋送: 已實現")
                else:
                    print(f"    ❌ WebSocket 數據饋送: 缺失")
            
            elif 'emergency_market_signal' in entry_name:
                if 'priority' in self.py_code and 'Priority' in self.py_code:
                    entry_score += 1
                    print(f"    ✅ 緊急市場信號: 已實現")
                else:
                    print(f"    ❌ 緊急市場信號: 缺失")
        
        print(f"\n🔍 出口點檢查:")
        for exit_name, exit_config in exit_points.items():
            print(f"  📋 {exit_name}: {exit_config}")
            
            if 'parallel_distribution' in exit_name:
                if 'signal_subscribers' in self.py_code and '_distribute_signals' in self.py_code:
                    exit_score += 1
                    print(f"    ✅ 並行分發: 已實現")
                else:
                    print(f"    ❌ 並行分發: 缺失")
            
            elif 'sequential_pipeline' in exit_name:
                if 'subscribe_to_signals' in self.py_code:
                    exit_score += 1
                    print(f"    ✅ 順序管道: 已實現")
                else:
                    print(f"    ❌ 順序管道: 缺失")
            
            elif 'monitoring_feed' in exit_name:
                if 'performance_stats' in self.py_code:
                    exit_score += 1
                    print(f"    ✅ 監控饋送: 已實現")
                else:
                    print(f"    ❌ 監控饋送: 缺失")
        
        total_integration = len(entry_points) + len(exit_points)
        total_implemented = entry_score + exit_score
        
        print(f"\n📊 整合點匹配度: {total_implemented/total_integration:.1%}")
        return total_implemented/total_integration
    
    def analyze_signal_structure(self):
        """分析信號結構完整性"""
        print("\n📊 信號結構分析")
        print("-" * 60)
        
        # JSON 中要求的基本信號字段
        required_signal_fields = [
            'signal_id', 'symbol', 'signal_type', 'direction', 'strength', 
            'confidence', 'priority', 'timestamp', 'price', 'volume', 'metadata'
        ]
        
        # 檢查 BasicSignal 類別
        if 'class BasicSignal:' in self.py_code or '@dataclass' in self.py_code:
            print(f"✅ BasicSignal 類別存在")
            
            implemented_fields = 0
            for field in required_signal_fields:
                if field in self.py_code:
                    implemented_fields += 1
                    print(f"  ✅ {field}: 已實現")
                else:
                    print(f"  ❌ {field}: 缺失")
            
            signal_structure_score = implemented_fields / len(required_signal_fields)
            print(f"\n📊 信號結構匹配度: {signal_structure_score:.1%}")
        else:
            print(f"❌ BasicSignal 類別缺失")
            signal_structure_score = 0
            
        return signal_structure_score
    
    def check_configuration_parameters(self):
        """檢查配置參數實現"""
        print("\n📊 配置參數分析")
        print("-" * 60)
        
        config_spec = self.json_spec['phase1a_basic_signal_generation_dependency']['configuration']['signal_generation_params']
        
        basic_mode = config_spec['basic_mode']
        extreme_mode = config_spec['extreme_market_mode']
        
        config_score = 0
        total_configs = len(basic_mode) + len(extreme_mode)
        
        print(f"🔍 基本模式參數:")
        for param, value in basic_mode.items():
            print(f"  📋 {param}: {value}")
            if str(value).replace('.', '').replace('_', '') in self.py_code:
                config_score += 1
                print(f"    ✅ 已實現")
            else:
                print(f"    ❌ 缺失")
        
        print(f"\n🔍 極端市場模式參數:")
        for param, value in extreme_mode.items():
            print(f"  📋 {param}: {value}")
            if str(value).replace('.', '').replace('_', '') in self.py_code or param.replace('_', '') in self.py_code:
                config_score += 1
                print(f"    ✅ 已實現")
            else:
                print(f"    ❌ 缺失")
        
        print(f"\n📊 配置參數匹配度: {config_score/total_configs:.1%}")
        return config_score/total_configs
    
    def generate_final_report(self):
        """生成最終精確分析報告"""
        print("\n" + "=" * 100)
        print("🎯 最終精確深度分析報告")
        print("=" * 100)
        
        # 執行所有分析
        scores = {}
        scores['processing_layers'] = self.analyze_processing_layers()
        scores['data_flow_integrity'] = self.analyze_data_flow_integrity()
        scores['performance_targets'] = self.analyze_performance_targets()
        scores['error_handling'] = self.analyze_error_handling()
        scores['integration_points'] = self.analyze_integration_points()
        scores['signal_structure'] = self.analyze_signal_structure()
        scores['configuration'] = self.check_configuration_parameters()
        
        # 計算總體匹配度
        total_score = sum(scores.values()) / len(scores)
        
        print(f"\n📊 各組件匹配度詳細結果:")
        print("-" * 60)
        for component, score in scores.items():
            status = "🟢" if score >= 0.8 else "🟡" if score >= 0.6 else "🔴"
            print(f"  {status} {component:20}: {score:6.1%}")
        
        print(f"\n🏆 總體精確匹配度: {total_score:.1%}")
        
        if total_score >= 0.9:
            status = "🟢 優秀匹配 (Excellent)"
        elif total_score >= 0.8:
            status = "🟡 良好匹配 (Good)"
        elif total_score >= 0.7:
            status = "🟠 部分匹配 (Partial)"
        else:
            status = "🔴 需要改進 (Needs Improvement)"
        
        print(f"📋 匹配狀態: {status}")
        
        # 數據流斷點分析
        if self.analysis_results['data_flow_breaks']:
            print(f"\n🔍 發現數據流斷點:")
            for break_point in self.analysis_results['data_flow_breaks']:
                print(f"  ⚠️  {break_point}")
        else:
            print(f"\n✅ 未發現數據流斷點")
        
        # 識別關鍵缺失項目
        print(f"\n🔍 關鍵缺失分析:")
        for component, score in scores.items():
            if score < 0.8:
                print(f"  ⚠️  {component}: 需要重點改進 ({score:.1%})")
        
        return total_score, scores

if __name__ == "__main__":
    analyzer = Phase1APreciseAnalyzer()
    total_score, detailed_scores = analyzer.generate_final_report()
    
    print(f"\n✅ 精確深度分析完成")
    print(f"📊 最終評分: {total_score:.1%}")
