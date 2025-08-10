#!/usr/bin/env python3
"""
🎯 精確深度分析工具 - phase1b_volatility_adaptation.py vs JSON 規範
不可繞過任何細節，進行精確匹配檢查
"""

import sys
import os
import json
import re
import ast
from typing import Dict, List, Any, Set

print("🔍 開始精確深度分析 - phase1b_volatility_adaptation.py vs JSON 規範")
print("=" * 100)

class Phase1BPreciseAnalyzer:
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
            with open("/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/phase1b_volatility_adaptation/phase1b_volatility_adaptation_dependency.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 無法載入 JSON 規範: {e}")
            return {}
    
    def _load_python_code(self) -> str:
        """載入 Python 代碼"""
        try:
            with open("/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/phase1b_volatility_adaptation/phase1b_volatility_adaptation.py", 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ 無法載入 Python 代碼: {e}")
            return ""
    
    def analyze_computation_layers(self):
        """分析計算層級 - 檢查 4 層架構實現"""
        print("\n📊 計算層級精確分析")
        print("-" * 60)
        
        computation_flow = self.json_spec['strategy_dependency_graph']['computation_flow']
        
        layer_mapping = {
            'layer_1_data_collection': {
                'operations': ['historical_volatility_calculation', 'realized_volatility_calculation', 'volatility_regime_detection'],
                'expected_methods': ['_calculate_historical_volatility', '_calculate_realized_volatility', '_detect_volatility_regime']
            },
            'layer_2_volatility_metrics': {
                'operations': ['volatility_percentile', 'volatility_trend', 'regime_stability', 'market_activity_factor', 'signal_smoothing'],
                'expected_methods': ['_calculate_volatility_percentile', '_calculate_volatility_trend', '_calculate_regime_stability', '_calculate_market_activity_factor', '_smooth_signals']
            },
            'layer_3_adaptive_parameters': {
                'operations': ['signal_threshold_adaptation', 'position_size_scaling', 'timeframe_optimization', 'market_sentiment_integration'],
                'expected_methods': ['_adapt_signal_threshold', '_scale_position_size', '_optimize_timeframe', '_integrate_market_sentiment']
            },
            'layer_4_strategy_signals': {
                'operations': ['volatility_breakout_signal', 'volatility_mean_reversion_signal', 'volatility_regime_change_signal'],
                'expected_methods': ['_generate_breakout_signal', '_generate_mean_reversion_signal', '_generate_regime_change_signal']
            }
        }
        
        implementation_score = 0
        total_layers = len(layer_mapping)
        
        for layer_name, layer_info in layer_mapping.items():
            print(f"\n🔍 檢查 {layer_name}:")
            
            # 檢查 JSON 規範中的操作
            if layer_name in computation_flow:
                json_operations = computation_flow[layer_name]['operations']
                print(f"  📋 JSON 規範操作: {list(json_operations.keys())}")
                
                # 檢查對應的 Python 方法實現
                implemented_methods = 0
                for expected_method in layer_info['expected_methods']:
                    if expected_method in self.py_code:
                        implemented_methods += 1
                        print(f"    ✅ {expected_method}: 已實現")
                    else:
                        print(f"    ❌ {expected_method}: 缺失")
                        self.analysis_results['missing'].append(f"{layer_name}.{expected_method}")
                
                # 檢查數據流依賴
                dependencies = computation_flow[layer_name].get('dependencies', [])
                print(f"  📋 依賴關係: {dependencies}")
                
                if implemented_methods == len(layer_info['expected_methods']):
                    implementation_score += 1
                    print(f"  🟢 {layer_name}: 完全實現 ({implemented_methods}/{len(layer_info['expected_methods'])})")
                elif implemented_methods > 0:
                    implementation_score += 0.5
                    print(f"  🟡 {layer_name}: 部分實現 ({implemented_methods}/{len(layer_info['expected_methods'])})")
                else:
                    print(f"  🔴 {layer_name}: 未實現")
            else:
                print(f"  ❌ JSON 規範中缺少 {layer_name}")
        
        print(f"\n📊 計算層級匹配度: {implementation_score/total_layers:.1%}")
        return implementation_score/total_layers
    
    def analyze_data_structures(self):
        """分析數據結構完整性"""
        print("\n📊 數據結構分析")
        print("-" * 60)
        
        # 從 JSON 中提取所需的數據結構
        required_data_structures = {
            'VolatilityMetrics': [
                'current_volatility', 'volatility_trend', 'volatility_percentile', 
                'regime_stability', 'enhanced_volatility_percentile', 'volatility_regime',
                'market_activity_factor', 'regime_change_probability'
            ],
            'AdaptiveSignalAdjustment': [
                'original_signal', 'adjusted_signal', 'adjustment_factor', 
                'adjustment_reason', 'confidence_boost', 'risk_mitigation'
            ],
            'VolatilityRegime': ['LOW', 'NORMAL', 'HIGH', 'EXTREME'],
            'MarketActivityLevel': ['LOW', 'NORMAL', 'HIGH']
        }
        
        structure_score = 0
        total_structures = len(required_data_structures)
        
        for structure_name, required_fields in required_data_structures.items():
            print(f"\n🔍 檢查數據結構: {structure_name}")
            
            if f"class {structure_name}" in self.py_code or f"{structure_name}(Enum)" in self.py_code:
                print(f"  ✅ {structure_name} 類別存在")
                
                # 檢查字段
                implemented_fields = 0
                for field in required_fields:
                    if field in self.py_code:
                        implemented_fields += 1
                        print(f"    ✅ {field}: 已實現")
                    else:
                        print(f"    ❌ {field}: 缺失")
                
                if implemented_fields == len(required_fields):
                    structure_score += 1
                elif implemented_fields > 0:
                    structure_score += 0.5
            else:
                print(f"  ❌ {structure_name} 類別缺失")
        
        print(f"\n📊 數據結構匹配度: {structure_score/total_structures:.1%}")
        return structure_score/total_structures
    
    def analyze_signal_generation_logic(self):
        """分析信號生成邏輯"""
        print("\n📊 信號生成邏輯分析")
        print("-" * 60)
        
        # 從 JSON 中提取信號生成邏輯
        layer_4_operations = self.json_spec['strategy_dependency_graph']['computation_flow']['layer_4_strategy_signals']['operations']
        
        signal_types = {
            'volatility_breakout_signal': {
                'condition': 'volatility_percentile > 0.9 AND volatility_trend > 0.5 AND volume_confirmation',
                'method': '_generate_breakout_signal',
                'output': 'enhanced_breakout_signal'
            },
            'volatility_mean_reversion_signal': {
                'condition': 'volatility_percentile > 0.8 AND regime_stability > 0.7 AND volume_confirmation',
                'method': '_generate_mean_reversion_signal',
                'output': 'enhanced_mean_reversion_signal'
            },
            'volatility_regime_change_signal': {
                'condition': 'regime_change_detected AND regime_stability < 0.3 AND multi_confirmation',
                'method': '_generate_regime_change_signal',
                'output': 'enhanced_regime_change_signal'
            }
        }
        
        logic_score = 0
        total_signals = len(signal_types)
        
        for signal_name, signal_info in signal_types.items():
            print(f"\n🔍 檢查信號: {signal_name}")
            
            # 檢查 JSON 規範
            if signal_name in layer_4_operations:
                json_condition = layer_4_operations[signal_name]['condition']
                print(f"  📋 JSON 條件: {json_condition}")
                
                # 檢查方法實現
                method_name = signal_info['method']
                if method_name in self.py_code:
                    print(f"  ✅ 方法: {method_name} 已實現")
                    
                    # 檢查邏輯條件
                    condition_keywords = ['volatility_percentile', 'volatility_trend', 'regime_stability']
                    condition_implemented = any(keyword in self.py_code for keyword in condition_keywords)
                    
                    if condition_implemented:
                        logic_score += 1
                        print(f"  ✅ 邏輯條件: 已實現")
                    else:
                        logic_score += 0.5
                        print(f"  🟡 邏輯條件: 部分實現")
                else:
                    print(f"  ❌ 方法: {method_name} 缺失")
            else:
                print(f"  ❌ JSON 規範中缺少 {signal_name}")
        
        print(f"\n📊 信號生成邏輯匹配度: {logic_score/total_signals:.1%}")
        return logic_score/total_signals
    
    def analyze_data_flow_integrity(self):
        """分析數據流完整性"""
        print("\n📊 數據流完整性分析")
        print("-" * 60)
        
        # 分析數據流鏈路
        data_flows = [
            {
                'source': 'historical_volatility_calculation',
                'data': 'OHLCV歷史數據',
                'output': 'historical_volatility',
                'next_layer': 'volatility_percentile'
            },
            {
                'source': 'realized_volatility_calculation',
                'data': '高頻價格數據',
                'output': 'realized_volatility',
                'next_layer': 'volatility_trend'
            },
            {
                'source': 'volatility_regime_detection',
                'data': 'volatility_timeseries',
                'output': 'enhanced_volatility_regime',
                'next_layer': 'adaptive_parameters'
            },
            {
                'source': 'adaptive_parameters',
                'data': 'volatility_metrics',
                'output': 'adaptive_signal_threshold',
                'next_layer': 'strategy_signals'
            }
        ]
        
        flow_integrity_score = 0
        total_flows = len(data_flows)
        
        for i, flow in enumerate(data_flows):
            print(f"\n🔍 數據流 {i+1}: {flow['source']} → {flow['next_layer']}")
            
            # 檢查數據輸入/輸出
            source_exists = flow['source'].replace('_', '') in self.py_code.replace('_', '')
            output_used = flow['output'].replace('_', '') in self.py_code.replace('_', '')
            
            print(f"  📋 數據來源: {flow['data']}")
            print(f"  📋 處理函數: {flow['source']} {'✅' if source_exists else '❌'}")
            print(f"  📋 輸出使用: {flow['output']} {'✅' if output_used else '❌'}")
            
            if source_exists and output_used:
                flow_integrity_score += 1
                print(f"  🟢 數據流完整")
            elif source_exists or output_used:
                flow_integrity_score += 0.5
                print(f"  🟡 數據流部分實現")
                self.analysis_results['data_flow_breaks'].append(f"Flow {i+1}: {flow['source']}")
            else:
                print(f"  🔴 數據流斷點")
                self.analysis_results['data_flow_breaks'].append(f"Flow {i+1}: {flow['source']}")
        
        print(f"\n📊 數據流完整性: {flow_integrity_score/total_flows:.1%}")
        return flow_integrity_score/total_flows
    
    def analyze_performance_optimization(self):
        """分析性能優化實現"""
        print("\n📊 性能優化分析")
        print("-" * 60)
        
        # 從 JSON 中提取性能優化要求
        optimization_strategies = self.json_spec['strategy_dependency_graph']['enhanced_optimization_strategies']
        
        optimization_features = {
            'multi_confirmation_system': 'multi_confirmation',
            'vectorized_volatility_calculation': 'numpy',
            'weighted_percentile_optimization': 'weighted_percentile',
            'layered_caching_strategy': 'cache',
            'signal_smoothing_optimization': 'smoothing',
            'market_sentiment_integration': 'sentiment',
            'smart_timeframe_switching': 'timeframe'
        }
        
        optimization_score = 0
        total_optimizations = len(optimization_features)
        
        for feature_name, keyword in optimization_features.items():
            print(f"\n🔍 檢查優化: {feature_name}")
            
            if keyword in self.py_code.lower():
                optimization_score += 1
                print(f"  ✅ {feature_name}: 已實現")
            else:
                print(f"  ❌ {feature_name}: 缺失")
                self.analysis_results['missing'].append(f"optimization.{feature_name}")
        
        print(f"\n📊 性能優化匹配度: {optimization_score/total_optimizations:.1%}")
        return optimization_score/total_optimizations
    
    def analyze_integration_points(self):
        """分析整合點"""
        print("\n📊 整合點分析")
        print("-" * 60)
        
        integration_points = self.json_spec['strategy_dependency_graph']['integration_points']
        
        # 檢查輸入來源
        receives_from = integration_points['receives_from']
        feeds_to = integration_points['feeds_to']
        cross_validation = integration_points['cross_validation_with']
        
        integration_score = 0
        total_integrations = len(receives_from) + len(feeds_to) + len(cross_validation)
        
        print(f"🔍 輸入來源檢查:")
        for source in receives_from:
            source_keyword = source.replace('_', '').lower()
            if source_keyword in self.py_code.lower().replace('_', ''):
                integration_score += 1
                print(f"  ✅ {source}: 已整合")
            else:
                print(f"  ❌ {source}: 缺失")
        
        print(f"\n🔍 輸出目標檢查:")
        for target in feeds_to:
            target_keyword = target.replace('_', '').lower()
            if target_keyword in self.py_code.lower().replace('_', ''):
                integration_score += 1
                print(f"  ✅ {target}: 已整合")
            else:
                print(f"  ❌ {target}: 缺失")
        
        print(f"\n🔍 跨模組驗證檢查:")
        for module in cross_validation:
            module_keyword = module.replace('_', '').lower()
            if module_keyword in self.py_code.lower().replace('_', ''):
                integration_score += 1
                print(f"  ✅ {module}: 已整合")
            else:
                print(f"  ❌ {module}: 缺失")
        
        print(f"\n📊 整合點匹配度: {integration_score/total_integrations:.1%}")
        return integration_score/total_integrations
    
    def analyze_signal_output_format(self):
        """分析信號輸出格式"""
        print("\n📊 信號輸出格式分析")
        print("-" * 60)
        
        signal_format = self.json_spec['strategy_dependency_graph']['signal_output_format']['enhanced_volatility_adapted_signal']
        
        required_fields = [
            'signal_type', 'signal_strength', 'signal_confidence', 'execution_priority',
            'adaptive_parameters', 'market_context', 'quality_indicators', 'timestamp', 'source'
        ]
        
        format_score = 0
        total_fields = len(required_fields)
        
        for field in required_fields:
            if field in self.py_code:
                format_score += 1
                print(f"  ✅ {field}: 已實現")
            else:
                print(f"  ❌ {field}: 缺失")
                self.analysis_results['missing'].append(f"signal_format.{field}")
        
        print(f"\n📊 信號輸出格式匹配度: {format_score/total_fields:.1%}")
        return format_score/total_fields
    
    def generate_final_report(self):
        """生成最終精確分析報告"""
        print("\n" + "=" * 100)
        print("🎯 最終精確深度分析報告")
        print("=" * 100)
        
        # 執行所有分析
        scores = {}
        scores['computation_layers'] = self.analyze_computation_layers()
        scores['data_structures'] = self.analyze_data_structures()
        scores['signal_generation_logic'] = self.analyze_signal_generation_logic()
        scores['data_flow_integrity'] = self.analyze_data_flow_integrity()
        scores['performance_optimization'] = self.analyze_performance_optimization()
        scores['integration_points'] = self.analyze_integration_points()
        scores['signal_output_format'] = self.analyze_signal_output_format()
        
        # 計算總體匹配度
        total_score = sum(scores.values()) / len(scores)
        
        print(f"\n📊 各組件匹配度詳細結果:")
        print("-" * 60)
        for component, score in scores.items():
            status = "🟢" if score >= 0.8 else "🟡" if score >= 0.6 else "🔴"
            print(f"  {status} {component:25}: {score:6.1%}")
        
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
        if self.analysis_results['missing']:
            print(f"\n🔍 關鍵缺失項目:")
            for missing_item in self.analysis_results['missing'][:10]:  # 顯示前10個
                print(f"  ⚠️  {missing_item}")
            if len(self.analysis_results['missing']) > 10:
                print(f"  ... 及其他 {len(self.analysis_results['missing']) - 10} 個項目")
        
        # 重點改進建議
        print(f"\n🔍 重點改進建議:")
        for component, score in scores.items():
            if score < 0.8:
                print(f"  ⚠️  {component}: 需要重點改進 ({score:.1%})")
        
        return total_score, scores

if __name__ == "__main__":
    analyzer = Phase1BPreciseAnalyzer()
    total_score, detailed_scores = analyzer.generate_final_report()
    
    print(f"\n✅ 精確深度分析完成")
    print(f"📊 最終評分: {total_score:.1%}")
