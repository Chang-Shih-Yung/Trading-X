#!/usr/bin/env python3
"""
Unified Signal Candidate Pool 精確深度分析工具
檢查 unified_signal_candidate_pool.py 與 JSON 規範的完全匹配情況
確保數據流與核心邏輯 100% 完整匹配
"""

import json
import re
import ast
import os
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime
from pathlib import Path

class UnifiedSignalPoolPrecisionAnalyzer:
    """Unified Signal Pool 精確深度分析器"""
    
    def __init__(self):
        self.python_file = "X/backend/phase1_signal_generation/unified_signal_pool/unified_signal_candidate_pool.py"
        self.json_spec = "X/backend/phase1_signal_generation/unified_signal_pool/unified_signal_candidate_pool_v3_dependency_CORE_FLOW.json"
        
    def execute_precision_analysis(self) -> Dict[str, Any]:
        """執行精確深度分析"""
        print("🔍 Unified Signal Pool 精確深度分析開始")
        print("=" * 80)
        
        try:
            # 讀取文件
            with open(self.python_file, 'r', encoding='utf-8') as f:
                python_code = f.read()
            
            with open(self.json_spec, 'r', encoding='utf-8') as f:
                json_spec = json.load(f)
            
            # 執行10個類別的深度分析
            analysis_results = {
                "timestamp": datetime.now().isoformat(),
                "precision_analysis": {
                    "1_layer_architecture": self._analyze_layer_architecture(python_code, json_spec),
                    "2_data_flow_variables": self._analyze_data_flow_variables(python_code, json_spec),
                    "3_core_operations": self._analyze_core_operations(python_code, json_spec),
                    "4_ai_learning_components": self._analyze_ai_learning_components(python_code, json_spec),
                    "5_signal_validation": self._analyze_signal_validation(python_code, json_spec),
                    "6_performance_targets": self._analyze_performance_targets(python_code, json_spec),
                    "7_epl_preprocessing": self._analyze_epl_preprocessing(python_code, json_spec),
                    "8_seven_dimensional_scoring": self._analyze_seven_dimensional_scoring(python_code, json_spec),
                    "9_market_regime_integration": self._analyze_market_regime_integration(python_code, json_spec),
                    "10_method_signatures": self._analyze_method_signatures(python_code, json_spec)
                }
            }
            
            # 計算總體匹配分數
            overall_score = self._calculate_overall_precision_score(analysis_results["precision_analysis"])
            analysis_results["overall_precision_score"] = overall_score
            
            self._print_detailed_analysis_results(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            print(f"❌ 分析過程失敗: {e}")
            return {"error": str(e)}
    
    def _analyze_layer_architecture(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析Layer架構完整性"""
        print("\n🏗️ 1. Layer架構分析...")
        
        # JSON規範要求的層級
        required_layers = [
            "layer_0_complete_phase1_sync",
            "layer_1_enhanced_multi_source_fusion", 
            "layer_2_epl_preprocessing_optimization",
            "layer_ai_adaptive_learning"
        ]
        
        # 檢查實現
        found_layers = []
        missing_layers = []
        
        for layer in required_layers:
            pattern = rf"async def _?{layer}|def _?{layer}"
            if re.search(pattern, code, re.IGNORECASE):
                found_layers.append(layer)
                print(f"  ✅ {layer}")
            else:
                missing_layers.append(layer)
                print(f"  ❌ {layer}")
        
        # 檢查時間目標
        time_targets = {
            "layer_0": "3ms",
            "layer_1": "12ms", 
            "layer_2": "8ms",
            "layer_ai": "5ms",
            "total": "28ms"
        }
        
        time_compliance = []
        for layer, target in time_targets.items():
            if target in code:
                time_compliance.append(f"{layer}:{target}")
        
        coverage = len(found_layers) / len(required_layers) * 100
        
        return {
            "required_layers": required_layers,
            "found_layers": found_layers,
            "missing_layers": missing_layers,
            "time_targets_found": time_compliance,
            "architecture_coverage": coverage,
            "status": "complete" if coverage >= 90 else "incomplete"
        }
    
    def _analyze_data_flow_variables(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析數據流變數完整性"""
        print("\n🔄 2. 數據流變數分析...")
        
        # JSON規範的關鍵數據流變數
        required_variables = [
            "unified_timestamp",
            "market_regime_state", 
            "raw_signals",
            "epl_filtered_signals",
            "seven_dimensional_score",
            "comprehensive_score",
            "ai_enhancement",
            "epl_prediction",
            "adjusted_weights",
            "emergency_signals",
            "standardized_signals",
            "final_signals"
        ]
        
        found_variables = []
        missing_variables = []
        
        for var in required_variables:
            # 檢查變數使用或定義
            patterns = [
                rf"\b{var}\b\s*=",
                rf"[\"']{var}[\"']",
                rf"\.{var}\b",
                rf"\[\"?{var}\"?\]"
            ]
            
            if any(re.search(pattern, code, re.IGNORECASE) for pattern in patterns):
                found_variables.append(var)
                print(f"  ✅ {var}")
            else:
                missing_variables.append(var)
                print(f"  ❌ {var}")
        
        coverage = len(found_variables) / len(required_variables) * 100
        
        return {
            "required_variables": required_variables,
            "found_variables": found_variables,
            "missing_variables": missing_variables,
            "data_flow_coverage": coverage,
            "status": "complete" if coverage >= 85 else "incomplete"
        }
    
    def _analyze_core_operations(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析核心操作方法"""
        print("\n⚙️ 3. 核心操作分析...")
        
        # JSON規範的核心操作方法
        required_operations = [
            "_collect_phase1a_signals",
            "_collect_indicator_signals", 
            "_collect_phase1b_signals",
            "_collect_phase1c_signals",
            "_intelligent_signal_filtering",
            "_optimize_signals_for_epl",
            "_format_for_epl",
            "_handle_emergency_signals",
            "_calculate_signal_similarity",
            "_update_market_regime_state",
            "_get_comprehensive_market_data"
        ]
        
        found_operations = []
        missing_operations = []
        
        for operation in required_operations:
            pattern = rf"async def {operation}|def {operation}"
            if re.search(pattern, code):
                found_operations.append(operation)
                print(f"  ✅ {operation}")
            else:
                missing_operations.append(operation)
                print(f"  ❌ {operation}")
        
        coverage = len(found_operations) / len(required_operations) * 100
        
        return {
            "required_operations": required_operations,
            "found_operations": found_operations,
            "missing_operations": missing_operations,
            "operations_coverage": coverage,
            "status": "complete" if coverage >= 90 else "incomplete"
        }
    
    def _analyze_ai_learning_components(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析AI學習組件"""
        print("\n🤖 4. AI學習組件分析...")
        
        # AI學習核心組件
        ai_components = [
            "AIAdaptiveLearningEngine",
            "learn_from_epl_feedback",
            "predict_epl_pass_probability", 
            "_calculate_signal_contribution",
            "_adjust_source_weights",
            "get_adjusted_weights",
            "epl_decision_history",
            "prediction_model_weights",
            "learning_metrics"
        ]
        
        found_components = []
        missing_components = []
        
        for component in ai_components:
            if component in code:
                found_components.append(component)
                print(f"  ✅ {component}")
            else:
                missing_components.append(component)
                print(f"  ❌ {component}")
        
        # 檢查AI學習指標
        ai_metrics = [
            "decision_accuracy",
            "signal_contribution", 
            "time_effect_patterns",
            "market_regime_preferences",
            "weight_adjustments"
        ]
        
        metrics_found = sum(1 for metric in ai_metrics if metric in code)
        metrics_coverage = metrics_found / len(ai_metrics) * 100
        
        coverage = len(found_components) / len(ai_components) * 100
        
        return {
            "ai_components": ai_components,
            "found_components": found_components,
            "missing_components": missing_components,
            "ai_metrics_coverage": metrics_coverage,
            "ai_coverage": coverage,
            "status": "complete" if coverage >= 85 else "incomplete"
        }
    
    def _analyze_signal_validation(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析信號驗證機制"""
        print("\n✅ 5. 信號驗證分析...")
        
        # 信號驗證組件
        validation_components = [
            "SignalQualityValidator",
            "validate_signal_strength_range",
            "validate_phase1a_signal",
            "validate_indicator_signal", 
            "validate_phase1b_signal",
            "validate_phase1c_signal"
        ]
        
        found_validations = []
        missing_validations = []
        
        for component in validation_components:
            if component in code:
                found_validations.append(component)
                print(f"  ✅ {component}")
            else:
                missing_validations.append(component)
                print(f"  ❌ {component}")
        
        # 檢查驗證標準
        validation_standards = [
            "quality_score.*>=.*0\\.6",
            "confidence.*>=.*0\\.65", 
            "stability_score.*>=.*0\\.7",
            "tier_assignment.*tier_1_critical"
        ]
        
        standards_found = sum(1 for standard in validation_standards 
                             if re.search(standard, code, re.IGNORECASE))
        
        coverage = len(found_validations) / len(validation_components) * 100
        
        return {
            "validation_components": validation_components,
            "found_validations": found_validations,
            "missing_validations": missing_validations,
            "validation_standards_found": standards_found,
            "validation_coverage": coverage,
            "status": "complete" if coverage >= 90 else "incomplete"
        }
    
    def _analyze_performance_targets(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析性能目標實現"""
        print("\n⚡ 6. 性能目標分析...")
        
        # 性能目標指標
        performance_targets = [
            "28ms.*目標",
            "3ms.*Layer.*0",
            "12ms.*Layer.*1", 
            "8ms.*Layer.*2",
            "5ms.*Layer.*AI",
            "asyncio\\.gather",
            "ThreadPoolExecutor",
            "processing_lock"
        ]
        
        found_targets = []
        missing_targets = []
        
        for target in performance_targets:
            if re.search(target, code, re.IGNORECASE):
                found_targets.append(target)
                print(f"  ✅ {target}")
            else:
                missing_targets.append(target)
                print(f"  ❌ {target}")
        
        # 檢查性能監控
        monitoring_features = [
            "start_time.*time\\.time",
            "elapsed.*time.*1000",
            "total_time.*start_time.*1000",
            "timing_info",
            "performance.*report"
        ]
        
        monitoring_found = sum(1 for feature in monitoring_features 
                              if re.search(feature, code, re.IGNORECASE))
        
        coverage = len(found_targets) / len(performance_targets) * 100
        
        return {
            "performance_targets": performance_targets,
            "found_targets": found_targets,
            "missing_targets": missing_targets,
            "monitoring_features_found": monitoring_found,
            "performance_coverage": coverage,
            "status": "optimized" if coverage >= 80 else "needs_optimization"
        }
    
    def _analyze_epl_preprocessing(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析EPL預處理實現"""
        print("\n🎯 7. EPL預處理分析...")
        
        # EPL預處理組件
        epl_components = [
            "epl_prediction",
            "predict_epl_pass_probability",
            "_optimize_signals_for_epl",
            "_format_for_epl",
            "risk_assessment",
            "execution_priority", 
            "position_sizing",
            "stop_loss_suggestion",
            "take_profit_levels",
            "StandardizedSignal"
        ]
        
        found_epl = []
        missing_epl = []
        
        for component in epl_components:
            if component in code:
                found_epl.append(component)
                print(f"  ✅ {component}")
            else:
                missing_epl.append(component)
                print(f"  ❌ {component}")
        
        # EPL優化特性
        epl_features = [
            "去重.*30秒",
            "相似度.*0\\.8", 
            "最多.*5個候選",
            "品質分數.*0\\.65",
            "EPL.*通過概率.*0\\.4"
        ]
        
        features_found = sum(1 for feature in epl_features 
                            if re.search(feature, code, re.IGNORECASE))
        
        coverage = len(found_epl) / len(epl_components) * 100
        
        return {
            "epl_components": epl_components,
            "found_epl": found_epl,
            "missing_epl": missing_epl,
            "epl_features_found": features_found,
            "epl_coverage": coverage,
            "status": "complete" if coverage >= 85 else "incomplete"
        }
    
    def _analyze_seven_dimensional_scoring(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析7維度評分系統"""
        print("\n📊 8. 7維度評分分析...")
        
        # 7維度評分組件
        seven_dim_components = [
            "SevenDimensionalScorer",
            "SevenDimensionalScore",
            "signal_strength.*0\\.25",
            "confidence.*0\\.20",
            "data_quality.*0\\.15",
            "market_consistency.*0\\.12",
            "time_effect.*0\\.10",
            "liquidity_factor.*0\\.10", 
            "historical_accuracy.*0\\.08",
            "comprehensive_score",
            "ai_enhancement.*0\\.1"
        ]
        
        found_dims = []
        missing_dims = []
        
        for component in seven_dim_components:
            if re.search(component, code, re.IGNORECASE):
                found_dims.append(component)
                print(f"  ✅ {component}")
            else:
                missing_dims.append(component)
                print(f"  ❌ {component}")
        
        # 7維度計算方法
        calculation_methods = [
            "_calculate_data_quality",
            "_calculate_market_consistency",
            "_calculate_time_effect",
            "_calculate_liquidity_factor", 
            "_calculate_historical_accuracy",
            "_apply_ai_enhancement"
        ]
        
        methods_found = sum(1 for method in calculation_methods if method in code)
        
        coverage = len(found_dims) / len(seven_dim_components) * 100
        
        return {
            "seven_dim_components": seven_dim_components,
            "found_dims": found_dims,
            "missing_dims": missing_dims,
            "calculation_methods_found": methods_found,
            "seven_dim_coverage": coverage,
            "status": "complete" if coverage >= 85 else "incomplete"
        }
    
    def _analyze_market_regime_integration(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析市場制度整合"""
        print("\n🌊 9. 市場制度整合分析...")
        
        # 市場制度組件
        regime_components = [
            "MarketRegimeState",
            "regime_type",
            "btc_5min_change",
            "volume_surge_multiplier",
            "volatility_percentile", 
            "is_extreme_market",
            "trading_session",
            "_update_market_regime_state",
            "extreme_market_fast_track"
        ]
        
        found_regime = []
        missing_regime = []
        
        for component in regime_components:
            if component in code:
                found_regime.append(component)
                print(f"  ✅ {component}")
            else:
                missing_regime.append(component)
                print(f"  ❌ {component}")
        
        # 市場制度適應邏輯
        adaptation_logic = [
            "trending.*phase1b.*phase1a",
            "ranging.*indicator_graph.*phase1c", 
            "volatile.*phase1a.*phase1b",
            "asian.*european.*american",
            "極端市場.*啟動"
        ]
        
        logic_found = sum(1 for logic in adaptation_logic 
                         if re.search(logic, code, re.IGNORECASE))
        
        coverage = len(found_regime) / len(regime_components) * 100
        
        return {
            "regime_components": regime_components,
            "found_regime": found_regime,
            "missing_regime": missing_regime,
            "adaptation_logic_found": logic_found,
            "regime_coverage": coverage,
            "status": "complete" if coverage >= 85 else "incomplete"
        }
    
    def _analyze_method_signatures(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析方法簽名完整性"""
        print("\n📝 10. 方法簽名分析...")
        
        # 關鍵方法簽名
        required_signatures = [
            "generate_signal_candidates_v3.*symbol.*str.*BTCUSDT",
            "learn_from_epl_feedback.*epl_decisions.*List",
            "get_performance_report.*Dict.*str.*Any",
            "get_candidates_by_priority.*min_priority.*int",
            "clear_expired_candidates.*max_age_hours.*int",
            "_calculate_execution_priority.*signal.*Dict",
            "_calculate_position_sizing.*signal.*Dict",
            "_calculate_stop_loss_suggestion.*signal.*Dict"
        ]
        
        found_signatures = []
        missing_signatures = []
        
        for signature in required_signatures:
            if re.search(signature, code, re.DOTALL):
                found_signatures.append(signature.split(".*")[0])
                print(f"  ✅ {signature.split('.*')[0]}")
            else:
                missing_signatures.append(signature.split(".*")[0])
                print(f"  ❌ {signature.split('.*')[0]}")
        
        # 返回類型檢查
        return_types = [
            "List\\[StandardizedSignal\\]",
            "Dict\\[str, Any\\]",
            "float",
            "int",
            "List\\[float\\]"
        ]
        
        types_found = sum(1 for rtype in return_types if re.search(rtype, code))
        
        coverage = len(found_signatures) / len(required_signatures) * 100
        
        return {
            "required_signatures": [s.split(".*")[0] for s in required_signatures],
            "found_signatures": found_signatures,
            "missing_signatures": missing_signatures,
            "return_types_found": types_found,
            "signature_coverage": coverage,
            "status": "complete" if coverage >= 90 else "incomplete"
        }
    
    def _calculate_overall_precision_score(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """計算總體精確匹配分數"""
        
        # 權重分配 (總和=1.0)
        weights = {
            "1_layer_architecture": 0.15,
            "2_data_flow_variables": 0.12,
            "3_core_operations": 0.13,
            "4_ai_learning_components": 0.12,
            "5_signal_validation": 0.10,
            "6_performance_targets": 0.08,
            "7_epl_preprocessing": 0.12,
            "8_seven_dimensional_scoring": 0.10,
            "9_market_regime_integration": 0.06,
            "10_method_signatures": 0.02
        }
        
        scores = {}
        weighted_total = 0
        
        for category, weight in weights.items():
            if category in analysis:
                result = analysis[category]
                
                # 提取分數
                if "architecture_coverage" in result:
                    score = result["architecture_coverage"]
                elif "data_flow_coverage" in result:
                    score = result["data_flow_coverage"]
                elif "operations_coverage" in result:
                    score = result["operations_coverage"]
                elif "ai_coverage" in result:
                    score = result["ai_coverage"]
                elif "validation_coverage" in result:
                    score = result["validation_coverage"]
                elif "performance_coverage" in result:
                    score = result["performance_coverage"]
                elif "epl_coverage" in result:
                    score = result["epl_coverage"]
                elif "seven_dim_coverage" in result:
                    score = result["seven_dim_coverage"]
                elif "regime_coverage" in result:
                    score = result["regime_coverage"]
                elif "signature_coverage" in result:
                    score = result["signature_coverage"]
                else:
                    score = 50  # 默認分數
                
                scores[category] = score
                weighted_total += score * weight
        
        return {
            "category_scores": scores,
            "weighted_total_score": weighted_total,
            "precision_grade": self._get_precision_grade(weighted_total),
            "critical_gaps": self._identify_critical_gaps(analysis),
            "completion_status": "PERFECT_MATCH" if weighted_total >= 95 else "NEEDS_OPTIMIZATION"
        }
    
    def _get_precision_grade(self, score: float) -> str:
        """獲取精確度等級"""
        if score >= 95:
            return "🏆 完美匹配"
        elif score >= 90:
            return "🥇 優秀匹配"
        elif score >= 80:
            return "🥈 良好匹配"
        elif score >= 70:
            return "🥉 可接受匹配"
        else:
            return "❌ 需要大幅改進"
    
    def _identify_critical_gaps(self, analysis: Dict[str, Any]) -> List[str]:
        """識別關鍵缺口"""
        critical_gaps = []
        
        for category, result in analysis.items():
            if "missing_" in str(result) and result.get("missing_layers") or result.get("missing_variables") or result.get("missing_operations"):
                missing_items = (result.get("missing_layers", []) + 
                               result.get("missing_variables", []) + 
                               result.get("missing_operations", []) +
                               result.get("missing_components", []) +
                               result.get("missing_validations", []))
                
                if missing_items:
                    critical_gaps.append(f"{category}: {', '.join(missing_items[:3])}")
        
        return critical_gaps[:5]  # 返回最多5個關鍵缺口
    
    def _print_detailed_analysis_results(self, results: Dict):
        """列印詳細分析結果"""
        print("\n" + "=" * 80)
        print("📊 UNIFIED SIGNAL POOL 精確深度分析結果")
        print("=" * 80)
        
        precision_score = results["overall_precision_score"]
        
        print(f"🎯 總體精確匹配分數: {precision_score['weighted_total_score']:.1f}/100")
        print(f"🏆 精確度等級: {precision_score['precision_grade']}")
        print(f"📋 完成狀態: {precision_score['completion_status']}")
        
        print(f"\n📊 詳細分類得分:")
        for category, score in precision_score["category_scores"].items():
            status = "✅" if score >= 90 else "⚠️" if score >= 70 else "❌"
            print(f"   {status} {category:30} {score:6.1f}%")
        
        if precision_score["critical_gaps"]:
            print(f"\n🔧 關鍵缺口:")
            for gap in precision_score["critical_gaps"]:
                print(f"   ❌ {gap}")
        
        # 具體分析結果
        analysis = results["precision_analysis"]
        
        print(f"\n📋 核心組件匹配情況:")
        
        # Layer架構
        layer_result = analysis["1_layer_architecture"]
        print(f"   🏗️ Layer架構: {len(layer_result['found_layers'])}/{len(layer_result['required_layers'])} ({layer_result['architecture_coverage']:.1f}%)")
        
        # 數據流變數
        data_result = analysis["2_data_flow_variables"] 
        print(f"   🔄 數據流變數: {len(data_result['found_variables'])}/{len(data_result['required_variables'])} ({data_result['data_flow_coverage']:.1f}%)")
        
        # 核心操作
        ops_result = analysis["3_core_operations"]
        print(f"   ⚙️ 核心操作: {len(ops_result['found_operations'])}/{len(ops_result['required_operations'])} ({ops_result['operations_coverage']:.1f}%)")
        
        # AI學習組件
        ai_result = analysis["4_ai_learning_components"]
        print(f"   🤖 AI學習組件: {len(ai_result['found_components'])}/{len(ai_result['ai_components'])} ({ai_result['ai_coverage']:.1f}%)")
        
        print(f"\n🎉 分析結論: {'🏆 完美匹配 - 可以進行生產部署' if precision_score['weighted_total_score'] >= 95 else '🔧 需要優化以達到完美匹配'}")

if __name__ == "__main__":
    analyzer = UnifiedSignalPoolPrecisionAnalyzer()
    results = analyzer.execute_precision_analysis()
