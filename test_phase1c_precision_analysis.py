#!/usr/bin/env python3
"""
🎯 Phase1C 精確深度分析工具
對 phase1c_signal_standardization.py 與 JSON 規範進行逐層逐項精確匹配分析
檢測邏輯斷點、數據流缺失、實現差異
"""

import json
import ast
import os
import importlib.util
from typing import Dict, Any, List, Set, Tuple
import re
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AnalysisResult:
    """分析結果"""
    category: str
    item: str
    status: str  # MATCH, MISSING, PARTIAL, INCORRECT
    details: str
    severity: str  # HIGH, MEDIUM, LOW

class Phase1CPrecisionAnalyzer:
    """Phase1C 精確分析器"""
    
    def __init__(self):
        self.json_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/phase1c_signal_standardization/phase1c_signal_standardization.json"
        self.python_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/phase1c_signal_standardization/phase1c_signal_standardization.py"
        
        self.analysis_results: List[AnalysisResult] = []
        
    def load_specifications(self) -> Tuple[Dict[str, Any], str]:
        """載入 JSON 規範和 Python 代碼"""
        # 載入 JSON
        with open(self.json_path, 'r', encoding='utf-8') as f:
            json_spec = json.load(f)
        
        # 載入 Python 代碼
        with open(self.python_path, 'r', encoding='utf-8') as f:
            python_code = f.read()
            
        return json_spec, python_code
    
    def analyze_layer_architecture(self, json_spec: Dict, python_code: str):
        """分析 4 層架構實現"""
        computation_flow = json_spec["strategy_dependency_graph"]["computation_flow"]
        
        # 檢查每一層的實現
        layers = [
            "layer_0_cross_module_sync",
            "layer_1_signal_collection", 
            "layer_2_signal_standardization",
            "layer_3_signal_prioritization",
            "layer_4_output_generation"
        ]
        
        for layer in layers:
            if layer in computation_flow:
                self._analyze_single_layer(layer, computation_flow[layer], python_code)
    
    def _analyze_single_layer(self, layer_name: str, layer_spec: Dict, python_code: str):
        """分析單一層的實現"""
        # 檢查主方法是否存在
        method_name = f"_{layer_name}"
        method_exists = method_name in python_code
        
        if method_exists:
            self.analysis_results.append(AnalysisResult(
                category="Layer Architecture",
                item=f"{layer_name}_method",
                status="MATCH",
                details=f"方法 {method_name} 存在",
                severity="HIGH"
            ))
        else:
            self.analysis_results.append(AnalysisResult(
                category="Layer Architecture", 
                item=f"{layer_name}_method",
                status="MISSING",
                details=f"缺少方法 {method_name}",
                severity="HIGH"
            ))
            
        # 檢查層內操作
        if "operations" in layer_spec:
            self._analyze_layer_operations(layer_name, layer_spec["operations"], python_code)
    
    def _analyze_layer_operations(self, layer_name: str, operations: Dict, python_code: str):
        """分析層內具體操作"""
        for operation_name, operation_spec in operations.items():
            # 轉換為方法名格式
            method_name = f"_{operation_name}"
            
            # 檢查方法是否存在
            if method_name in python_code:
                self.analysis_results.append(AnalysisResult(
                    category=f"{layer_name}_operations",
                    item=operation_name,
                    status="MATCH",
                    details=f"操作方法 {method_name} 存在",
                    severity="MEDIUM"
                ))
                
                # 深度分析操作內容
                self._analyze_operation_content(operation_name, operation_spec, python_code)
            else:
                self.analysis_results.append(AnalysisResult(
                    category=f"{layer_name}_operations",
                    item=operation_name,
                    status="MISSING", 
                    details=f"缺少操作方法 {method_name}",
                    severity="MEDIUM"
                ))
    
    def _analyze_operation_content(self, operation_name: str, operation_spec: Dict, python_code: str):
        """深度分析操作內容"""
        # 檢查輸入輸出
        if "input" in operation_spec:
            input_var = operation_spec["input"]
            if isinstance(input_var, str):
                # 檢查方法中是否處理了這個輸入
                method_pattern = f"_{operation_name}.*{input_var}|{input_var}.*_{operation_name}"
                if not re.search(method_pattern, python_code, re.IGNORECASE):
                    self.analysis_results.append(AnalysisResult(
                        category=f"{operation_name}_data_flow",
                        item=f"input_{input_var}",
                        status="MISSING",
                        details=f"操作 {operation_name} 未處理輸入 {input_var}",
                        severity="MEDIUM"
                    ))
        
        if "output" in operation_spec:
            output_var = operation_spec["output"]
            if isinstance(output_var, str):
                # 檢查方法中是否返回這個輸出
                output_pattern = f"return.*{output_var}|{output_var}.*=.*"
                if not re.search(output_pattern, python_code, re.IGNORECASE):
                    self.analysis_results.append(AnalysisResult(
                        category=f"{operation_name}_data_flow",
                        item=f"output_{output_var}",
                        status="MISSING",
                        details=f"操作 {operation_name} 未生成輸出 {output_var}",
                        severity="MEDIUM"
                    ))
    
    def analyze_signal_format_adapters(self, json_spec: Dict, python_code: str):
        """分析信號格式適配器"""
        # 檢查 Phase1B 適配器
        layer1_ops = json_spec["strategy_dependency_graph"]["computation_flow"]["layer_1_signal_collection"]["operations"]
        
        if "signal_format_adapter" in layer1_ops:
            adapter_spec = layer1_ops["signal_format_adapter"]["adapters"]
            
            # 檢查 Phase1B 適配器
            if "phase1b_adapter" in adapter_spec:
                phase1b_spec = adapter_spec["phase1b_adapter"]
                self._analyze_phase1b_adapter(phase1b_spec, python_code)
            
            # 檢查指標適配器
            if "indicator_adapter" in adapter_spec:
                indicator_spec = adapter_spec["indicator_adapter"]
                self._analyze_indicator_adapter(indicator_spec, python_code)
    
    def _analyze_phase1b_adapter(self, adapter_spec: Dict, python_code: str):
        """分析 Phase1B 適配器實現"""
        # 檢查映射規則
        if "output_mapping" in adapter_spec and "mapping_rules" in adapter_spec["output_mapping"]:
            mapping_rules = adapter_spec["output_mapping"]["mapping_rules"]
            
            # 檢查每個映射規則是否在代碼中實現
            for json_key, expected_value in mapping_rules.items():
                # 在 _phase1b_adapter 方法中查找這個映射
                pattern = f"{json_key}.*{expected_value}|{expected_value}.*{json_key}"
                if re.search(pattern, python_code):
                    self.analysis_results.append(AnalysisResult(
                        category="Phase1B_Adapter",
                        item=f"mapping_{json_key}",
                        status="MATCH",
                        details=f"映射規則 {json_key} -> {expected_value} 已實現",
                        severity="MEDIUM"
                    ))
                else:
                    self.analysis_results.append(AnalysisResult(
                        category="Phase1B_Adapter",
                        item=f"mapping_{json_key}",
                        status="MISSING",
                        details=f"缺少映射規則 {json_key} -> {expected_value}",
                        severity="MEDIUM"
                    ))
    
    def _analyze_indicator_adapter(self, adapter_spec: Dict, python_code: str):
        """分析指標適配器實現"""
        if "output_mapping" in adapter_spec and "mapping_rules" in adapter_spec["output_mapping"]:
            mapping_rules = adapter_spec["output_mapping"]["mapping_rules"]
            
            for json_key, expected_value in mapping_rules.items():
                pattern = f"{json_key}.*{expected_value}|{expected_value}.*{json_key}"
                if re.search(pattern, python_code):
                    self.analysis_results.append(AnalysisResult(
                        category="Indicator_Adapter",
                        item=f"mapping_{json_key}",
                        status="MATCH",
                        details=f"映射規則 {json_key} -> {expected_value} 已實現",
                        severity="MEDIUM"
                    ))
                else:
                    self.analysis_results.append(AnalysisResult(
                        category="Indicator_Adapter",
                        item=f"mapping_{json_key}",
                        status="MISSING",
                        details=f"缺少映射規則 {json_key} -> {expected_value}",
                        severity="MEDIUM"
                    ))
    
    def analyze_quality_score_standardization(self, json_spec: Dict, python_code: str):
        """分析質量評分標準化"""
        layer1_ops = json_spec["strategy_dependency_graph"]["computation_flow"]["layer_1_signal_collection"]["operations"]
        
        if "quality_score_standardization" in layer1_ops:
            quality_spec = layer1_ops["quality_score_standardization"]["conversions"]
            
            # 檢查 Phase1B 質量轉換
            if "phase1b_to_standard" in quality_spec:
                phase1b_conversion = quality_spec["phase1b_to_standard"]
                self._analyze_quality_conversion(phase1b_conversion, python_code, "Phase1B")
            
            # 檢查指標質量轉換
            if "indicator_to_standard" in quality_spec:
                indicator_conversion = quality_spec["indicator_to_standard"]
                self._analyze_quality_conversion(indicator_conversion, python_code, "Indicator")
    
    def _analyze_quality_conversion(self, conversion_spec: Dict, python_code: str, adapter_type: str):
        """分析質量轉換實現"""
        for field, formula in conversion_spec.items():
            if isinstance(formula, str):
                # 檢查公式中的關鍵詞是否在代碼中
                key_terms = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', formula)
                for term in key_terms:
                    if term in python_code:
                        self.analysis_results.append(AnalysisResult(
                            category=f"{adapter_type}_Quality_Conversion",
                            item=f"{field}_{term}",
                            status="MATCH",
                            details=f"質量轉換項 {term} 已實現",
                            severity="LOW"
                        ))
                    else:
                        self.analysis_results.append(AnalysisResult(
                            category=f"{adapter_type}_Quality_Conversion",
                            item=f"{field}_{term}",
                            status="MISSING",
                            details=f"缺少質量轉換項 {term}",
                            severity="LOW"
                        ))
    
    def analyze_extreme_market_handling(self, json_spec: Dict, python_code: str):
        """分析極端市場處理"""
        # 檢查極端市場檢測
        if "_detect_extreme_market" in python_code:
            self.analysis_results.append(AnalysisResult(
                category="Extreme_Market",
                item="detection_method",
                status="MATCH",
                details="極端市場檢測方法存在",
                severity="HIGH"
            ))
        else:
            self.analysis_results.append(AnalysisResult(
                category="Extreme_Market",
                item="detection_method",
                status="MISSING", 
                details="缺少極端市場檢測方法",
                severity="HIGH"
            ))
        
        # 檢查快速通道
        if "_extreme_market_fast_track" in python_code:
            self.analysis_results.append(AnalysisResult(
                category="Extreme_Market",
                item="fast_track_method",
                status="MATCH",
                details="極端市場快速通道存在",
                severity="HIGH"
            ))
        else:
            self.analysis_results.append(AnalysisResult(
                category="Extreme_Market",
                item="fast_track_method",
                status="MISSING",
                details="缺少極端市場快速通道",
                severity="HIGH"
            ))
        
        # 檢查 15ms SLA 目標
        layer3_spec = json_spec["strategy_dependency_graph"]["computation_flow"]["layer_3_signal_prioritization"]
        if "extreme_market_fast_track" in layer3_spec:
            target_latency = layer3_spec["extreme_market_fast_track"]["tier_1_fast_track"]["target_latency_ms"]
            if "15" in python_code and "SLA" in python_code.upper():
                self.analysis_results.append(AnalysisResult(
                    category="Extreme_Market",
                    item="15ms_sla",
                    status="MATCH",
                    details="15ms SLA 目標已識別",
                    severity="HIGH"
                ))
            else:
                self.analysis_results.append(AnalysisResult(
                    category="Extreme_Market", 
                    item="15ms_sla",
                    status="MISSING",
                    details="未找到 15ms SLA 目標實現",
                    severity="HIGH"
                ))
    
    def analyze_cross_market_validation(self, json_spec: Dict, python_code: str):
        """分析跨市場驗證"""
        layer2_ops = json_spec["strategy_dependency_graph"]["computation_flow"]["layer_2_signal_standardization"]["operations"]
        
        if "quality_score_enhancement" in layer2_ops:
            enhancement_spec = layer2_ops["quality_score_enhancement"]
            
            # 檢查跨市場驗證
            if "cross_market_validation" in enhancement_spec:
                cross_market_spec = enhancement_spec["cross_market_validation"]
                
                # BTC 相關性檢查
                if "btc_correlation_check" in cross_market_spec:
                    btc_spec = cross_market_spec["btc_correlation_check"]
                    
                    if "btc_correlation" in python_code:
                        self.analysis_results.append(AnalysisResult(
                            category="Cross_Market_Validation",
                            item="btc_correlation",
                            status="MATCH",
                            details="BTC 相關性檢查已實現",
                            severity="MEDIUM"
                        ))
                    else:
                        self.analysis_results.append(AnalysisResult(
                            category="Cross_Market_Validation",
                            item="btc_correlation",
                            status="MISSING",
                            details="缺少 BTC 相關性檢查",
                            severity="MEDIUM"
                        ))
                
                # 流動性權重
                if "liquidity_weighting" in cross_market_spec:
                    if "liquidity" in python_code and "weight" in python_code:
                        self.analysis_results.append(AnalysisResult(
                            category="Cross_Market_Validation",
                            item="liquidity_weighting",
                            status="MATCH",
                            details="流動性權重已實現",
                            severity="MEDIUM"
                        ))
                    else:
                        self.analysis_results.append(AnalysisResult(
                            category="Cross_Market_Validation",
                            item="liquidity_weighting",
                            status="MISSING",
                            details="缺少流動性權重實現",
                            severity="MEDIUM"
                        ))
    
    def analyze_trading_session_adaptation(self, json_spec: Dict, python_code: str):
        """分析交易時段適應"""
        layer2_ops = json_spec["strategy_dependency_graph"]["computation_flow"]["layer_2_signal_standardization"]["operations"]
        
        if "quality_score_enhancement" in layer2_ops:
            enhancement_spec = layer2_ops["quality_score_enhancement"]
            
            if "trading_session_adaptation" in enhancement_spec:
                session_spec = enhancement_spec["trading_session_adaptation"]
                
                sessions = ["asian_session", "european_session", "american_session"]
                for session in sessions:
                    if session in session_spec:
                        session_name = session.replace("_session", "").upper()
                        if session_name in python_code:
                            self.analysis_results.append(AnalysisResult(
                                category="Trading_Session_Adaptation",
                                item=session,
                                status="MATCH",
                                details=f"{session} 適應已實現",
                                severity="LOW"
                            ))
                        else:
                            self.analysis_results.append(AnalysisResult(
                                category="Trading_Session_Adaptation",
                                item=session,
                                status="MISSING",
                                details=f"缺少 {session} 適應",
                                severity="LOW"
                            ))
    
    def analyze_multi_dimensional_scoring(self, json_spec: Dict, python_code: str):
        """分析多維度評分"""
        layer3_ops = json_spec["strategy_dependency_graph"]["computation_flow"]["layer_3_signal_prioritization"]["operations"]
        
        if "multi_dimensional_scoring" in layer3_ops:
            scoring_spec = layer3_ops["multi_dimensional_scoring"]["scoring_dimensions"]
            
            dimensions = [
                "signal_strength",
                "confidence_score", 
                "execution_priority",
                "market_timing",
                "risk_reward_ratio"
            ]
            
            for dimension in dimensions:
                if dimension in scoring_spec:
                    if dimension in python_code:
                        self.analysis_results.append(AnalysisResult(
                            category="Multi_Dimensional_Scoring",
                            item=dimension,
                            status="MATCH", 
                            details=f"評分維度 {dimension} 已實現",
                            severity="MEDIUM"
                        ))
                    else:
                        self.analysis_results.append(AnalysisResult(
                            category="Multi_Dimensional_Scoring",
                            item=dimension,
                            status="MISSING",
                            details=f"缺少評分維度 {dimension}",
                            severity="MEDIUM"
                        ))
    
    def analyze_signal_filtering_rules(self, json_spec: Dict, python_code: str):
        """分析信號過濾規則"""
        layer3_ops = json_spec["strategy_dependency_graph"]["computation_flow"]["layer_3_signal_prioritization"]["operations"]
        
        if "signal_filtering_rules" in layer3_ops:
            filtering_spec = layer3_ops["signal_filtering_rules"]
            
            # 檢查過濾標準
            if "filtering_criteria" in filtering_spec:
                criteria = filtering_spec["filtering_criteria"]
                
                criteria_items = [
                    "minimum_quality_threshold",
                    "maximum_signals_per_symbol", 
                    "maximum_signals_per_timeframe",
                    "signal_diversity_requirement",
                    "temporal_filtering"
                ]
                
                for criterion in criteria_items:
                    if criterion in criteria:
                        criterion_key = criterion.replace("_", "")
                        if criterion_key in python_code or criterion in python_code:
                            self.analysis_results.append(AnalysisResult(
                                category="Signal_Filtering_Rules",
                                item=criterion,
                                status="MATCH",
                                details=f"過濾標準 {criterion} 已實現",
                                severity="MEDIUM"
                            ))
                        else:
                            self.analysis_results.append(AnalysisResult(
                                category="Signal_Filtering_Rules", 
                                item=criterion,
                                status="MISSING",
                                details=f"缺少過濾標準 {criterion}",
                                severity="MEDIUM"
                            ))
            
            # 檢查反向信號衝突抑制
            if "reverse_signal_conflict_suppression" in filtering_spec:
                if "reverse_signal" in python_code and "conflict" in python_code:
                    self.analysis_results.append(AnalysisResult(
                        category="Signal_Filtering_Rules",
                        item="reverse_signal_conflict_suppression",
                        status="MATCH",
                        details="反向信號衝突抑制已實現",
                        severity="HIGH"
                    ))
                else:
                    self.analysis_results.append(AnalysisResult(
                        category="Signal_Filtering_Rules",
                        item="reverse_signal_conflict_suppression", 
                        status="MISSING",
                        details="缺少反向信號衝突抑制",
                        severity="HIGH"
                    ))
    
    def analyze_streaming_output(self, json_spec: Dict, python_code: str):
        """分析流式輸出"""
        layer4_ops = json_spec["strategy_dependency_graph"]["computation_flow"]["layer_4_output_generation"]["operations"]
        
        if "signal_distribution" in layer4_ops:
            distribution_spec = layer4_ops["signal_distribution"]
            
            # 檢查流式輸出
            if "streaming_output" in distribution_spec:
                streaming_spec = distribution_spec["streaming_output"]
                
                streaming_items = [
                    "tier_1_immediate_push",
                    "tier_2_batch_push", 
                    "tier_3_scheduled_push"
                ]
                
                for item in streaming_items:
                    if item in streaming_spec:
                        item_key = item.replace("_", "")
                        if item_key in python_code or "immediate_push" in python_code:
                            self.analysis_results.append(AnalysisResult(
                                category="Streaming_Output",
                                item=item,
                                status="MATCH",
                                details=f"流式輸出 {item} 已實現",
                                severity="MEDIUM"
                            ))
                        else:
                            self.analysis_results.append(AnalysisResult(
                                category="Streaming_Output",
                                item=item,
                                status="MISSING",
                                details=f"缺少流式輸出 {item}",
                                severity="MEDIUM"
                            ))
    
    def analyze_performance_targets(self, json_spec: Dict, python_code: str):
        """分析性能目標"""
        performance_targets = json_spec["strategy_dependency_graph"]["performance_targets"]
        
        # 檢查總計算時間
        if "total_computation_time_ms" in performance_targets:
            target_time = performance_targets["total_computation_time_ms"]
            if str(target_time) in python_code or "25ms" in python_code:
                self.analysis_results.append(AnalysisResult(
                    category="Performance_Targets",
                    item="total_computation_time",
                    status="MATCH",
                    details=f"總計算時間目標 {target_time}ms 已識別",
                    severity="HIGH"
                ))
            else:
                self.analysis_results.append(AnalysisResult(
                    category="Performance_Targets",
                    item="total_computation_time",
                    status="MISSING",
                    details=f"未找到總計算時間目標 {target_time}ms",
                    severity="HIGH"
                ))
        
        # 檢查分層處理時間
        if "layered_processing_times" in performance_targets:
            layered_times = performance_targets["layered_processing_times"]
            
            for layer, target_time in layered_times.items():
                time_value = re.search(r'(\d+)ms', target_time)
                if time_value:
                    time_str = time_value.group(1)
                    if time_str in python_code:
                        self.analysis_results.append(AnalysisResult(
                            category="Performance_Targets",
                            item=f"{layer}_time",
                            status="MATCH",
                            details=f"{layer} 時間目標 {time_str}ms 已識別",
                            severity="MEDIUM"
                        ))
                    else:
                        self.analysis_results.append(AnalysisResult(
                            category="Performance_Targets",
                            item=f"{layer}_time",
                            status="MISSING",
                            details=f"未找到 {layer} 時間目標 {time_str}ms",
                            severity="MEDIUM"
                        ))
    
    def analyze_data_structures(self, json_spec: Dict, python_code: str):
        """分析數據結構"""
        signal_format = json_spec["strategy_dependency_graph"]["signal_output_format"]["standardized_trading_signal"]
        
        required_fields = [
            "signal_id", "symbol", "timeframe", "strategy", "signal_type",
            "signal_strength", "confidence_score", "execution_priority",
            "composite_score", "tier_classification", "market_context",
            "risk_metrics", "execution_guidance", "quality_indicators", "metadata"
        ]
        
        for field in required_fields:
            if field in signal_format:
                if field in python_code:
                    self.analysis_results.append(AnalysisResult(
                        category="Data_Structures",
                        item=field,
                        status="MATCH",
                        details=f"數據結構字段 {field} 已實現",
                        severity="MEDIUM"
                    ))
                else:
                    self.analysis_results.append(AnalysisResult(
                        category="Data_Structures",
                        item=field,
                        status="MISSING",
                        details=f"缺少數據結構字段 {field}",
                        severity="MEDIUM"
                    ))
    
    def calculate_match_score(self) -> Dict[str, Any]:
        """計算匹配分數"""
        category_scores = {}
        
        for result in self.analysis_results:
            category = result.category
            if category not in category_scores:
                category_scores[category] = {"total": 0, "matched": 0}
            
            category_scores[category]["total"] += 1
            if result.status == "MATCH":
                category_scores[category]["matched"] += 1
        
        # 計算每個類別的得分
        for category in category_scores:
            total = category_scores[category]["total"]
            matched = category_scores[category]["matched"]
            category_scores[category]["score"] = matched / total if total > 0 else 0
        
        # 計算總體得分
        total_items = len(self.analysis_results)
        matched_items = len([r for r in self.analysis_results if r.status == "MATCH"])
        overall_score = matched_items / total_items if total_items > 0 else 0
        
        return {
            "overall_score": overall_score,
            "category_scores": category_scores,
            "total_items": total_items,
            "matched_items": matched_items
        }
    
    def generate_detailed_report(self, scores: Dict[str, Any]) -> str:
        """生成詳細報告"""
        report = []
        report.append("=" * 80)
        report.append("🎯 PHASE1C 精確深度分析報告")
        report.append("=" * 80)
        
        # 總體評分
        overall_score = scores["overall_score"]
        report.append(f"\n📊 總體匹配度: {overall_score:.1%}")
        
        # 匹配度評級
        if overall_score >= 0.9:
            grade = "A+ (優秀)"
        elif overall_score >= 0.8:
            grade = "A (良好)"  
        elif overall_score >= 0.7:
            grade = "B (一般)"
        elif overall_score >= 0.6:
            grade = "C (需改進)"
        else:
            grade = "D (嚴重不匹配)"
        
        report.append(f"📈 匹配等級: {grade}")
        
        report.append("\n" + "=" * 50)
        report.append("📋 分類詳細分析:")
        report.append("=" * 50)
        
        # 按類別顯示結果
        categories = {}
        for result in self.analysis_results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        for category, results in categories.items():
            category_score = scores["category_scores"].get(category, {}).get("score", 0)
            status_icon = "✅" if category_score >= 0.8 else "⚠️" if category_score >= 0.6 else "❌"
            
            report.append(f"\n{status_icon} {category}: {category_score:.1%}")
            
            # 顯示具體項目
            for result in results:
                status_icon = {"MATCH": "✓", "MISSING": "✗", "PARTIAL": "◐", "INCORRECT": "✗"}[result.status]
                severity_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[result.severity]
                
                report.append(f"    {status_icon} {severity_icon} {result.item}: {result.details}")
        
        # 高優先級問題總結
        high_priority_issues = [r for r in self.analysis_results 
                              if r.severity == "HIGH" and r.status != "MATCH"]
        
        if high_priority_issues:
            report.append("\n" + "=" * 50)
            report.append("🚨 高優先級問題:")
            report.append("=" * 50)
            
            for issue in high_priority_issues:
                report.append(f"🔴 {issue.category}.{issue.item}: {issue.details}")
        
        # 邏輯斷點分析
        report.append("\n" + "=" * 50)
        report.append("🔍 邏輯斷點分析:")
        report.append("=" * 50)
        
        # 檢查數據流連續性
        data_flow_issues = [r for r in self.analysis_results 
                           if "data_flow" in r.category and r.status != "MATCH"]
        
        if data_flow_issues:
            report.append("\n📊 數據流斷點:")
            for issue in data_flow_issues:
                report.append(f"  ❌ {issue.details}")
        else:
            report.append("\n✅ 數據流連續性良好")
        
        # 檢查架構層次完整性
        layer_issues = [r for r in self.analysis_results 
                       if "Layer Architecture" in r.category and r.status != "MATCH"]
        
        if layer_issues:
            report.append("\n🏗️ 架構層次缺失:")
            for issue in layer_issues:
                report.append(f"  ❌ {issue.details}")
        else:
            report.append("\n✅ 4層架構完整")
        
        # 性能目標達成度
        performance_issues = [r for r in self.analysis_results 
                            if "Performance_Targets" in r.category and r.status != "MATCH"]
        
        if performance_issues:
            report.append("\n⚡ 性能目標缺失:")
            for issue in performance_issues:
                report.append(f"  ❌ {issue.details}")
        else:
            report.append("\n✅ 性能目標明確")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def run_analysis(self) -> Tuple[Dict[str, Any], str]:
        """運行完整分析"""
        print("🚀 開始 Phase1C 精確深度分析...")
        
        # 載入規範和代碼
        json_spec, python_code = self.load_specifications()
        
        # 執行各項分析
        self.analyze_layer_architecture(json_spec, python_code)
        self.analyze_signal_format_adapters(json_spec, python_code)
        self.analyze_quality_score_standardization(json_spec, python_code)
        self.analyze_extreme_market_handling(json_spec, python_code)
        self.analyze_cross_market_validation(json_spec, python_code)
        self.analyze_trading_session_adaptation(json_spec, python_code)
        self.analyze_multi_dimensional_scoring(json_spec, python_code)
        self.analyze_signal_filtering_rules(json_spec, python_code)
        self.analyze_streaming_output(json_spec, python_code)
        self.analyze_performance_targets(json_spec, python_code)
        self.analyze_data_structures(json_spec, python_code)
        
        # 計算得分
        scores = self.calculate_match_score()
        
        # 生成報告
        report = self.generate_detailed_report(scores)
        
        return scores, report

if __name__ == "__main__":
    analyzer = Phase1CPrecisionAnalyzer()
    scores, report = analyzer.run_analysis()
    print(report)
    
    # 返回結果供後續使用
    print(f"\n總體匹配度: {scores['overall_score']:.1%}")
    print(f"分析項目總數: {scores['total_items']}")
    print(f"匹配項目數: {scores['matched_items']}")
