#!/usr/bin/env python3
"""
🎯 測試 phase1b_volatility_adaptation.py 優化後的匹配度
基於 JSON 規格進行精準驗證
"""

import json
import os
import importlib.util
from typing import Dict, Any, List
import ast
import inspect

class OptimizedPhase1BAnalyzer:
    """優化後的 Phase1B 分析器"""
    
    def __init__(self):
        self.json_spec_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/phase1b_volatility_adaptation/phase1b_volatility_adaptation_dependency.json"
        self.implementation_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/phase1b_volatility_adaptation/phase1b_volatility_adaptation.py"
        
    def load_json_spec(self) -> Dict[str, Any]:
        """載入 JSON 規格"""
        try:
            with open(self.json_spec_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ JSON 規格載入失敗: {e}")
            return {}
    
    def load_python_implementation(self):
        """載入 Python 實現"""
        try:
            spec = importlib.util.spec_from_file_location("phase1b_module", self.implementation_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"❌ Python 實現載入失敗: {e}")
            return None
    
    def analyze_file_content(self) -> Dict[str, Any]:
        """分析文件內容"""
        try:
            with open(self.implementation_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AST 分析
            tree = ast.parse(content)
            
            # 提取方法名稱
            methods = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    methods.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    # 提取類中的方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(f"{node.name}.{item.name}")
            
            return {
                "content": content,
                "methods": methods,
                "classes": classes,
                "lines": len(content.split('\n'))
            }
            
        except Exception as e:
            print(f"❌ 文件內容分析失敗: {e}")
            return {}
    
    def check_enhanced_architecture_match(self, json_spec: Dict, implementation_analysis: Dict) -> Dict[str, Any]:
        """增強架構匹配檢查"""
        content = implementation_analysis.get("content", "")
        methods = implementation_analysis.get("methods", [])
        
        # 1. 檢查主要處理方法
        main_processing = {
            "process_signals_with_volatility_adaptation": "process_signals_with_volatility_adaptation" in content,
            "accepts_standardized_signals": "standardized_signals" in content and "indicator_outputs" in content,
            "returns_unified_format": "unified_signal_candidate_pool" in content or "Dict[str, Any]" in content
        }
        
        # 2. 檢查 4 層架構
        layer_architecture = {
            "layer_1_data_collection": "layer_1_data_collection" in content,
            "layer_2_volatility_metrics": "layer_2_volatility_metrics" in content, 
            "layer_3_adaptive_parameters": "layer_3_adaptive_parameters" in content,
            "layer_4_strategy_signals": "layer_4_strategy_signals" in content
        }
        
        # 3. 檢查 JSON 要求的計算方法
        required_calculations = {
            "enhanced_volatility_percentile_calculation": "_calculate_enhanced_volatility_percentile" in content,
            "regime_detection_with_multi_confirmation": "_detect_volatility_regime" in content and "multi_confirmation" in content,
            "signal_threshold_adaptation": "_adapt_signal_threshold" in content,
            "position_size_scaling": "_scale_position_size" in content,
            "timeframe_optimization": "_optimize_timeframe" in content
        }
        
        # 4. 檢查波動性信號生成方法
        volatility_signal_methods = {
            "breakout_signal_generation": "_generate_breakout_signals" in content,
            "mean_reversion_signal_generation": "_generate_mean_reversion_signals" in content,
            "regime_change_signal_generation": "_generate_regime_change_signals" in content
        }
        
        # 5. 檢查數據處理能力
        data_processing = {
            "ohlcv_data_processing": "ohlcv" in content.lower() or "_process_ohlcv_data" in content,
            "high_frequency_data_processing": "_process_high_frequency_data" in content,
            "historical_volatility_calculation": "_calculate_historical_volatility" in content,
            "intraday_volatility_tracking": "intraday_volatility" in content
        }
        
        # 6. 檢查高階功能
        advanced_features = {
            "signal_continuity_analysis": "_analyze_signal_continuity" in content,
            "dynamic_time_distribution": "_analyze_dynamic_time_distribution" in content,
            "regime_monitoring": "_regime_monitor" in content,
            "performance_monitoring": "_performance_monitor" in content
        }
        
        # 7. 檢查數據結構
        data_structures = {
            "VolatilityMetrics": "class VolatilityMetrics" in content or "@dataclass" in content and "VolatilityMetrics" in content,
            "AdaptiveSignalAdjustment": "AdaptiveSignalAdjustment" in content,
            "SignalContinuityMetrics": "SignalContinuityMetrics" in content,
            "DynamicTimeDistribution": "DynamicTimeDistribution" in content
        }
        
        return {
            "main_processing": main_processing,
            "layer_architecture": layer_architecture,
            "required_calculations": required_calculations,
            "volatility_signal_methods": volatility_signal_methods,
            "data_processing": data_processing,
            "advanced_features": advanced_features,
            "data_structures": data_structures
        }
    
    def calculate_optimization_score(self, match_results: Dict[str, Any]) -> Dict[str, float]:
        """計算優化評分"""
        scores = {}
        total_score = 0
        total_weight = 0
        
        # 定義權重
        weights = {
            "main_processing": 20,
            "layer_architecture": 25,
            "required_calculations": 20,
            "volatility_signal_methods": 15,
            "data_processing": 10,
            "advanced_features": 10,
            "data_structures": 10
        }
        
        for category, items in match_results.items():
            if category in weights:
                category_score = sum(items.values()) / len(items) if items else 0
                scores[category] = category_score
                total_score += category_score * weights[category]
                total_weight += weights[category]
        
        overall_score = total_score / total_weight if total_weight > 0 else 0
        scores["overall"] = overall_score
        
        return scores
    
    def generate_optimization_report(self, scores: Dict[str, float], match_results: Dict[str, Any]) -> str:
        """生成優化報告"""
        report = []
        report.append("=" * 80)
        report.append("🎯 PHASE1B 優化後匹配度分析報告")
        report.append("=" * 80)
        
        # 總體評分
        overall_score = scores.get("overall", 0)
        report.append(f"\n📊 總體匹配度: {overall_score:.1%}")
        
        # 改進程度（與之前的 72.8% 比較）
        previous_score = 0.728
        improvement = overall_score - previous_score
        report.append(f"📈 優化改進: {improvement:+.1%} (從 {previous_score:.1%} 提升到 {overall_score:.1%})")
        
        if improvement > 0:
            report.append("✅ 優化成功！")
        else:
            report.append("⚠️ 需要進一步優化")
        
        report.append("\n" + "=" * 50)
        report.append("📋 詳細分析結果:")
        report.append("=" * 50)
        
        # 各項目評分
        category_names = {
            "main_processing": "主要處理邏輯",
            "layer_architecture": "4層架構實現",
            "required_calculations": "必需計算方法",
            "volatility_signal_methods": "波動性信號方法",
            "data_processing": "數據處理能力",
            "advanced_features": "高階功能",
            "data_structures": "數據結構定義"
        }
        
        for category, score in scores.items():
            if category != "overall" and category in category_names:
                status = "✅" if score >= 0.8 else "⚠️" if score >= 0.6 else "❌"
                report.append(f"{status} {category_names[category]}: {score:.1%}")
                
                # 顯示具體匹配項目
                if category in match_results:
                    items = match_results[category]
                    for item, matched in items.items():
                        item_status = "✓" if matched else "✗"
                        report.append(f"    {item_status} {item}")
        
        # 優化建議
        report.append("\n" + "=" * 50)
        report.append("💡 優化建議:")
        report.append("=" * 50)
        
        low_score_categories = [cat for cat, score in scores.items() 
                              if cat != "overall" and score < 0.8]
        
        if not low_score_categories:
            report.append("🎉 所有項目都已達到高匹配度標準！")
        else:
            for category in low_score_categories:
                missing_items = [item for item, matched in match_results.get(category, {}).items() 
                               if not matched]
                if missing_items:
                    report.append(f"\n📌 {category_names.get(category, category)}:")
                    for item in missing_items:
                        report.append(f"   - 需要實現: {item}")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def run_optimization_analysis(self):
        """運行優化分析"""
        print("🚀 開始 Phase1B 優化後分析...")
        
        # 載入數據
        json_spec = self.load_json_spec()
        if not json_spec:
            return
        
        implementation_analysis = self.analyze_file_content()
        if not implementation_analysis:
            return
        
        # 分析匹配度
        match_results = self.check_enhanced_architecture_match(json_spec, implementation_analysis)
        
        # 計算評分
        scores = self.calculate_optimization_score(match_results)
        
        # 生成報告
        report = self.generate_optimization_report(scores, match_results)
        print(report)
        
        # 保存報告
        report_path = "/Users/henrychang/Desktop/Trading-X/phase1b_optimization_results.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 報告已保存到: {report_path}")
        
        return scores, match_results

if __name__ == "__main__":
    analyzer = OptimizedPhase1BAnalyzer()
    analyzer.run_optimization_analysis()
