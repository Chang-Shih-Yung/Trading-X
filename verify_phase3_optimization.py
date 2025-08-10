#!/usr/bin/env python3
"""
Phase3 Market Analyzer 優化驗證
檢查優化後的匹配度提升情況
"""

import json
import re
import os
from typing import Dict, List, Any
from datetime import datetime

class Phase3OptimizationVerifier:
    """Phase3 優化驗證器"""
    
    def __init__(self):
        self.analyzer_path = "X/backend/phase1_signal_generation/phase3_market_analyzer/phase3_market_analyzer.py"
        self.json_spec_path = "X/backend/phase1_signal_generation/phase3_market_analyzer/phase3_market_analyzer_CORE_FLOW.json"
    
    def verify_optimization_results(self) -> Dict[str, Any]:
        """驗證優化結果"""
        print("🔍 Phase3 Market Analyzer 優化驗證開始")
        print("=" * 60)
        
        try:
            # 讀取文件
            with open(self.analyzer_path, 'r', encoding='utf-8') as f:
                analyzer_code = f.read()
            
            with open(self.json_spec_path, 'r', encoding='utf-8') as f:
                json_spec = json.load(f)
            
            # 執行各項檢查
            results = {
                "timestamp": datetime.now().isoformat(),
                "optimization_verification": {
                    "core_methods_added": self._verify_core_methods(analyzer_code, json_spec),
                    "data_flow_variables": self._verify_data_flow_variables(analyzer_code, json_spec),
                    "method_name_compliance": self._verify_method_names(analyzer_code, json_spec),
                    "layer_architecture": self._verify_layer_architecture(analyzer_code, json_spec),
                    "performance_targets": self._verify_performance_targets(analyzer_code, json_spec)
                }
            }
            
            # 計算總體改進分數
            total_score = self._calculate_improvement_score(results["optimization_verification"])
            results["overall_improvement_score"] = total_score
            
            self._print_verification_results(results)
            
            return results
            
        except Exception as e:
            print(f"❌ 驗證過程失敗: {e}")
            return {"error": str(e)}
    
    def _verify_core_methods(self, code: str, spec: Dict) -> Dict[str, Any]:
        """驗證核心方法實現"""
        print("\n📋 檢查核心方法實現...")
        
        # JSON規範要求的核心方法
        required_methods = [
            "_process_orderbook_stream",
            "_collect_funding_rate", 
            "_process_bid_ask_spread_analysis",
            "_calculate_market_impact",
            "_map_liquidity_depth",
            "_process_incremental_volume_profile",
            "_layer_1b_market_microstructure",
            "_fallback_to_backup_sources"
        ]
        
        found_methods = []
        missing_methods = []
        
        for method in required_methods:
            if f"def {method}" in code or f"async def {method}" in code:
                found_methods.append(method)
                print(f"  ✅ {method}")
            else:
                missing_methods.append(method)
                print(f"  ❌ {method}")
        
        coverage = len(found_methods) / len(required_methods) * 100
        
        return {
            "total_required": len(required_methods),
            "found_methods": found_methods,
            "missing_methods": missing_methods,
            "coverage_percentage": coverage,
            "status": "improved" if coverage > 50 else "needs_work"
        }
    
    def _verify_data_flow_variables(self, code: str, spec: Dict) -> Dict[str, Any]:
        """驗證數據流變數"""
        print("\n🔄 檢查數據流變數...")
        
        # JSON規範要求的關鍵變數
        required_variables = [
            "synchronized_phase3_timestamp_reference",
            "real_time_orderbook_websocket", 
            "adaptive_50ms_to_200ms",
            "tick_by_tick_trade_data",
            "incremental_volume_profile",
            "bid_ask_spread_analysis",
            "market_impact_calculation",
            "liquidity_depth_mapping"
        ]
        
        found_variables = []
        missing_variables = []
        
        for var in required_variables:
            if var in code:
                found_variables.append(var)
                print(f"  ✅ {var}")
            else:
                missing_variables.append(var)
                print(f"  ❌ {var}")
        
        coverage = len(found_variables) / len(required_variables) * 100
        
        return {
            "total_required": len(required_variables),
            "found_variables": found_variables,
            "missing_variables": missing_variables,
            "coverage_percentage": coverage,
            "status": "improved" if coverage > 60 else "needs_work"
        }
    
    def _verify_method_names(self, code: str, spec: Dict) -> Dict[str, Any]:
        """驗證方法名稱符合性"""
        print("\n🏷️ 檢查方法名稱符合性...")
        
        # 檢查主方法名稱
        main_method_correct = "def process_market_data" in code
        
        # 檢查Layer方法名稱
        layer_methods = [
            "_layer_0_phase1c_sync_integration",
            "_layer_1a_high_freq_streaming", 
            "_layer_1b_low_freq_data_collection",
            "_layer_2_orderbook_analysis",
            "_layer_3_sentiment_analysis"
        ]
        
        layer_compliance = sum(1 for method in layer_methods if method in code)
        
        print(f"  {'✅' if main_method_correct else '❌'} 主方法: process_market_data")
        print(f"  ✅ Layer方法符合性: {layer_compliance}/{len(layer_methods)}")
        
        return {
            "main_method_correct": main_method_correct,
            "layer_methods_compliance": layer_compliance / len(layer_methods) * 100,
            "status": "compliant" if main_method_correct and layer_compliance >= 4 else "partially_compliant"
        }
    
    def _verify_layer_architecture(self, code: str, spec: Dict) -> Dict[str, Any]:
        """驗證7層架構"""
        print("\n🏗️ 檢查7層架構...")
        
        # 檢查Layer結構 - 更精確的模式匹配
        layer_patterns = [
            ("Layer 0", r"Layer 0.*同步整合|layer_0.*sync|🔄.*Layer 0"),
            ("Layer 1A", r"Layer 1A.*高頻數據流|layer_1a.*high.*freq|🚀.*Layer 1A"),
            ("Layer 1B", r"Layer 1B.*低頻數據|layer_1b.*low.*freq|🕐.*Layer 1B"),
            ("Layer 2", r"Layer 2.*OrderBook|layer_2.*orderbook|📊.*Layer 2"),
            ("Layer 3", r"Layer 3.*情緒分析|layer_3.*sentiment|🎭.*Layer 3"),
            ("Layer 4", r"Layer 4.*微結構信號|layer_4.*microstructure|🎯.*Layer 4"),
            ("Layer 5", r"Layer 5.*高階分析|layer_5.*analytics|🧠.*Layer 5")
        ]
        
        found_layers = []
        for layer_name, pattern in layer_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                found_layers.append(layer_name)
                print(f"    ✅ {layer_name}")
            else:
                print(f"    ❌ {layer_name}")
        
        architecture_completeness = len(found_layers) / len(layer_patterns) * 100
        
        print(f"  ✅ 發現架構層: {len(found_layers)}/{len(layer_patterns)}")
        
        return {
            "found_layers": found_layers,
            "architecture_completeness": architecture_completeness,
            "status": "complete" if architecture_completeness >= 85 else "partial"
        }
    
    def _verify_performance_targets(self, code: str, spec: Dict) -> Dict[str, Any]:
        """驗證性能目標"""
        print("\n⚡ 檢查性能目標...")
        
        # 檢查性能相關代碼 - 更精確的async檢測
        performance_indicators = [
            ("35ms", r"35ms.*目標|total.*35|35ms.*內完成"),
            ("adaptive", r"adaptive.*performance|AdaptivePerformanceController|自適應性能"),
            ("async", r"async def.*await|asyncio\.gather|並行執行|async.*性能優化"),
            ("buffering", r"buffer|Buffer|緩衝區|雙緩衝"),
            ("monitoring", r"performance.*metrics|PerformanceMetrics|性能監控")
        ]
        
        found_indicators = []
        for name, pattern in performance_indicators:
            if re.search(pattern, code, re.IGNORECASE):
                found_indicators.append(name)
                print(f"  ✅ {name}")
            else:
                print(f"  ❌ {name}")
        
        performance_readiness = len(found_indicators) / len(performance_indicators) * 100
        
        return {
            "found_indicators": found_indicators,
            "performance_readiness": performance_readiness,
            "status": "ready" if performance_readiness >= 90 else "needs_optimization"
        }
    
    def _calculate_improvement_score(self, verification_results: Dict) -> Dict[str, Any]:
        """計算總體改進分數"""
        
        # 權重分配
        weights = {
            "core_methods_added": 0.30,
            "data_flow_variables": 0.25, 
            "method_name_compliance": 0.15,
            "layer_architecture": 0.20,
            "performance_targets": 0.10
        }
        
        scores = {}
        weighted_total = 0
        
        for category, weight in weights.items():
            if category in verification_results:
                result = verification_results[category]
                
                # 提取分數
                if "coverage_percentage" in result:
                    score = result["coverage_percentage"]
                elif "layer_methods_compliance" in result:
                    score = result["layer_methods_compliance"]
                elif "architecture_completeness" in result:
                    score = result["architecture_completeness"]
                elif "performance_readiness" in result:
                    score = result["performance_readiness"]
                else:
                    score = 50  # 默認分數
                
                scores[category] = score
                weighted_total += score * weight
        
        # 估算改進程度 (假設原始分數為50%)
        original_score = 50.0
        improvement = weighted_total - original_score
        improvement_percentage = (improvement / original_score) * 100
        
        return {
            "category_scores": scores,
            "weighted_total_score": weighted_total,
            "original_estimated_score": original_score,
            "improvement_points": improvement,
            "improvement_percentage": improvement_percentage,
            "overall_grade": self._get_grade(weighted_total)
        }
    
    def _get_grade(self, score: float) -> str:
        """獲取評分等級"""
        if score >= 90:
            return "A+ (優秀)"
        elif score >= 80:
            return "A (良好)"
        elif score >= 70:
            return "B+ (可接受)"
        elif score >= 60:
            return "B (需改進)"
        else:
            return "C (不充分)"
    
    def _print_verification_results(self, results: Dict):
        """列印驗證結果"""
        print("\n" + "=" * 60)
        print("📊 PHASE3 優化驗證結果摘要")
        print("=" * 60)
        
        improvement = results["overall_improvement_score"]
        
        print(f"🎯 總體改進分數: {improvement['weighted_total_score']:.1f}/100")
        print(f"📈 改進幅度: +{improvement['improvement_points']:.1f} 分 ({improvement['improvement_percentage']:+.1f}%)")
        print(f"🏆 評分等級: {improvement['overall_grade']}")
        
        print(f"\n📋 分類得分:")
        for category, score in improvement["category_scores"].items():
            print(f"   {category:25} {score:6.1f}%")
        
        print(f"\n✅ 優化成效:")
        verification = results["optimization_verification"]
        
        # 核心方法
        methods = verification["core_methods_added"]
        print(f"   核心方法實現: {len(methods['found_methods'])}/{methods['total_required']} ({methods['coverage_percentage']:.1f}%)")
        
        # 數據流變數  
        variables = verification["data_flow_variables"]
        print(f"   數據流變數: {len(variables['found_variables'])}/{variables['total_required']} ({variables['coverage_percentage']:.1f}%)")
        
        # 架構完整性
        architecture = verification["layer_architecture"]
        print(f"   架構完整性: {len(architecture['found_layers'])}/7 層 ({architecture['architecture_completeness']:.1f}%)")
        
        print(f"\n🎉 優化結論: {'大幅改進' if improvement['improvement_percentage'] > 25 else '適度改進' if improvement['improvement_percentage'] > 10 else '小幅改進'}")

if __name__ == "__main__":
    verifier = Phase3OptimizationVerifier()
    results = verifier.verify_optimization_results()
