#!/usr/bin/env python3
"""
🔍 Phase3 Market Analyzer 精確深度分析工具
驗證 phase3_market_analyzer.py 與 phase3_market_analyzer_CORE_FLOW.json 的完整匹配度
"""

import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass

@dataclass
class AnalysisResult:
    category: str
    item: str
    status: str  # PASS, FAIL, PARTIAL
    details: str
    score: float  # 0.0 - 1.0

class Phase3PrecisionAnalyzer:
    """Phase3 市場分析器精確分析工具"""
    
    def __init__(self):
        self.analysis_results: List[AnalysisResult] = []
        self.total_score = 0.0
        self.max_score = 0.0
        
    def analyze_complete_implementation(self, py_file: str, json_file: str) -> Dict[str, Any]:
        """執行完整的實現分析"""
        print("🔍 開始 Phase3 Market Analyzer 精確深度分析...")
        
        # 載入文件
        py_content = self._load_file(py_file)
        json_spec = self._load_json(json_file)
        
        if not py_content or not json_spec:
            print("❌ 文件載入失敗")
            return {}
        
        # 1. 7層架構完整性檢查
        self._verify_7_layer_architecture(py_content, json_spec)
        
        # 2. 數據流變數連續性檢查
        self._verify_data_flow_continuity(py_content, json_spec)
        
        # 3. Layer操作方法完整性檢查
        self._verify_layer_operations(py_content, json_spec)
        
        # 4. 性能優化機制檢查
        self._verify_performance_optimizations(py_content, json_spec)
        
        # 5. 信號類型與強度檢查
        self._verify_signal_types_and_strength(py_content, json_spec)
        
        # 6. Phase1C整合檢查
        self._verify_phase1c_integration(py_content, json_spec)
        
        # 7. 事件驅動與適應性檢查
        self._verify_event_driven_adaptive(py_content, json_spec)
        
        # 8. 故障恢復機制檢查
        self._verify_failover_mechanisms(py_content, json_spec)
        
        # 計算總分
        return self._generate_comprehensive_report()
    
    def _verify_7_layer_architecture(self, py_content: str, json_spec: Dict):
        """驗證7層架構完整性"""
        print("\n🏗️ 驗證7層架構完整性...")
        
        # JSON規範中的層級
        required_layers = {
            "layer_0": "Phase1C 時間戳同步整合層",
            "layer_1a": "高頻數據流處理層", 
            "layer_1b": "低頻數據收集層",
            "layer_2": "OrderBook 深度分析層",
            "layer_3": "市場情緒與資金流向分析層",
            "layer_4": "市場微結構信號生成層",
            "layer_5": "高階分析與預測信號層"
        }
        
        # 檢查每層的實現
        for layer_key, layer_name in required_layers.items():
            layer_method = f"_layer_{layer_key.replace('layer_', '')}"
            
            if re.search(rf"def {layer_method}|async def {layer_method}", py_content):
                self._add_result("7層架構", f"{layer_key} ({layer_name})", "PASS", 
                               "Layer方法已實現", 1.0)
            else:
                self._add_result("7層架構", f"{layer_key} ({layer_name})", "FAIL", 
                               "Layer方法未實現", 0.0)
        
        # 檢查主處理流程
        if "process_market_data" in py_content:
            self._add_result("7層架構", "主處理流程", "PASS", "主處理方法存在", 1.0)
        else:
            self._add_result("7層架構", "主處理流程", "FAIL", "主處理方法缺失", 0.0)
    
    def _verify_data_flow_continuity(self, py_content: str, json_spec: Dict):
        """驗證數據流變數連續性"""
        print("\n📊 驗證數據流變數連續性...")
        
        # JSON規範中的關鍵數據流變數
        data_flow_variables = {
            "layer_0": [
                "synchronized_phase3_timestamp_reference"
            ],
            "layer_1a": [
                "real_time_orderbook_websocket",
                "tick_by_tick_trade_data", 
                "adaptive_50ms_to_200ms",
                "incremental_volume_profile"
            ],
            "layer_1b": [
                "funding_rate_8_hours",
                "open_interest_30_seconds",
                "market_regime_daily"
            ],
            "layer_2": [
                "bid_ask_imbalance",
                "order_flow_intensity",
                "market_depth_analysis",
                "sliding_window_analysis"
            ],
            "layer_3": [
                "funding_sentiment_score",
                "oi_momentum_signal",
                "volume_sentiment_indicators"
            ],
            "layer_4": [
                "liquidity_shock_signal",
                "institutional_flow_signal", 
                "sentiment_divergence_signal",
                "liquidity_regime_change_signal"
            ],
            "layer_5": [
                "price_impact_prediction",
                "liquidity_forecast",
                "market_stress_indicator"
            ]
        }
        
        # 檢查變數在代碼中的使用
        for layer, variables in data_flow_variables.items():
            for var in variables:
                if var in py_content:
                    self._add_result("數據流連續性", f"{layer}.{var}", "PASS", 
                                   "變數已使用", 1.0)
                else:
                    self._add_result("數據流連續性", f"{layer}.{var}", "FAIL", 
                                   "變數未使用", 0.0)
    
    def _verify_layer_operations(self, py_content: str, json_spec: Dict):
        """驗證Layer操作方法完整性"""
        print("\n🔧 驗證Layer操作方法完整性...")
        
        # 關鍵操作方法
        required_operations = {
            "layer_1a": [
                "_process_orderbook_stream",
                "_process_tick_data",
                "_detect_large_orders"
            ],
            "layer_1b": [
                "_collect_funding_rate",
                "_monitor_open_interest",
                "_analyze_market_regime"
            ],
            "layer_2": [
                "_calculate_bid_ask_imbalance",
                "_analyze_order_flow_intensity",
                "_analyze_market_depth"
            ],
            "layer_3": [
                "_analyze_funding_sentiment",
                "_calculate_oi_momentum",
                "_analyze_volume_sentiment"
            ],
            "layer_4": [
                "_detect_liquidity_shock",
                "_detect_institutional_flow",
                "_detect_sentiment_divergence",
                "_detect_liquidity_regime_change"
            ],
            "layer_5": [
                "_predict_price_impact",
                "_forecast_liquidity",
                "_calculate_market_stress"
            ]
        }
        
        for layer, operations in required_operations.items():
            for operation in operations:
                if f"def {operation}" in py_content or f"async def {operation}" in py_content:
                    self._add_result("Layer操作方法", f"{layer}.{operation}", "PASS", 
                                   "操作方法已實現", 1.0)
                else:
                    self._add_result("Layer操作方法", f"{layer}.{operation}", "FAIL", 
                                   "操作方法未實現", 0.0)
    
    def _verify_performance_optimizations(self, py_content: str, json_spec: Dict):
        """驗證性能優化機制"""
        print("\n⚡ 驗證性能優化機制...")
        
        # JSON規範要求的優化機制
        optimization_features = [
            "DoubleBuffer",  # 雙緩衝
            "RingBuffer",   # 環狀緩衝
            "AdaptivePerformanceController",  # 適應性能控制
            "EventDrivenProcessor",  # 事件驅動處理
            "adaptive_50ms_to_200ms",  # 適應性採樣
            "incremental_volume_profile",  # 增量計算
            "sliding_window_analysis"  # 滑動窗口
        ]
        
        for feature in optimization_features:
            if feature in py_content:
                self._add_result("性能優化", feature, "PASS", "優化機制已實現", 1.0)
            else:
                self._add_result("性能優化", feature, "FAIL", "優化機制未實現", 0.0)
        
        # 檢查時間目標
        time_targets = [
            "35ms",  # 總處理時間
            "30ms",  # Tier1高波動目標
            "50ms",  # Tier1正常目標
            "9ms",   # Layer1A目標
            "6ms"    # Layer1B目標
        ]
        
        for target in time_targets:
            if target in py_content:
                self._add_result("性能目標", target, "PASS", "時間目標已設定", 1.0)
            else:
                self._add_result("性能目標", target, "FAIL", "時間目標未設定", 0.0)
    
    def _verify_signal_types_and_strength(self, py_content: str, json_spec: Dict):
        """驗證信號類型與強度"""
        print("\n🎯 驗證信號類型與強度...")
        
        # JSON規範中的信號類型
        signal_types = {
            "LIQUIDITY_SHOCK": {
                "strength": "0.8-1.0",
                "tier": "tier_1_critical"
            },
            "INSTITUTIONAL_FLOW": {
                "strength": "0.7-0.9", 
                "tier": "tier_1_critical"
            },
            "SENTIMENT_DIVERGENCE": {
                "strength": "0.72-1.0",
                "tier": "tier_2_important"
            },
            "LIQUIDITY_REGIME_CHANGE": {
                "strength": "0.75-1.0",
                "tier": "tier_3_monitoring"
            }
        }
        
        for signal_type, specs in signal_types.items():
            if signal_type in py_content:
                self._add_result("信號類型", signal_type, "PASS", "信號類型已定義", 1.0)
            else:
                self._add_result("信號類型", signal_type, "FAIL", "信號類型未定義", 0.0)
            
            # 檢查tier分配
            if specs["tier"] in py_content:
                self._add_result("信號層級", f"{signal_type}.{specs['tier']}", "PASS", 
                               "Tier分配正確", 1.0)
            else:
                self._add_result("信號層級", f"{signal_type}.{specs['tier']}", "FAIL", 
                               "Tier分配缺失", 0.0)
    
    def _verify_phase1c_integration(self, py_content: str, json_spec: Dict):
        """驗證Phase1C整合"""
        print("\n🔗 驗證Phase1C整合...")
        
        # Phase1C整合要求
        integration_features = [
            "phase1c_signal_standardization",
            "layer_0_cross_module_sync",
            "Phase1C",
            "unified_signal_candidate_pool",
            "200ms",  # 同步容錯
            "signal_strength",  # 0.0-1.0標準
            "tier_assignment"
        ]
        
        for feature in integration_features:
            if feature in py_content:
                self._add_result("Phase1C整合", feature, "PASS", "整合特性已實現", 1.0)
            else:
                self._add_result("Phase1C整合", feature, "FAIL", "整合特性缺失", 0.0)
        
        # 檢查標準化信號格式
        if "MarketMicrostructureSignal" in py_content:
            self._add_result("Phase1C整合", "標準化信號格式", "PASS", 
                           "信號格式已標準化", 1.0)
        else:
            self._add_result("Phase1C整合", "標準化信號格式", "FAIL", 
                           "信號格式未標準化", 0.0)
    
    def _verify_event_driven_adaptive(self, py_content: str, json_spec: Dict):
        """驗證事件驅動與適應性"""
        print("\n🎯 驗證事件驅動與適應性...")
        
        # 事件驅動特性
        event_driven_features = [
            "should_trigger_liquidity_shock_analysis",
            "large_order_volume_multiplier",
            "spread_widening_multiplier",
            "depth_decrease_threshold",
            "market_stress_level",
            "processing_mode"
        ]
        
        for feature in event_driven_features:
            if feature in py_content:
                self._add_result("事件驅動", feature, "PASS", "事件驅動特性已實現", 1.0)
            else:
                self._add_result("事件驅動", feature, "FAIL", "事件驅動特性缺失", 0.0)
        
        # 適應性特性
        adaptive_features = [
            "high_volatility",
            "low_volatility", 
            "normal",
            "update_market_stress",
            "get_processing_frequency_ms",
            "dynamic_weight_adaptation"
        ]
        
        for feature in adaptive_features:
            if feature in py_content:
                self._add_result("適應性機制", feature, "PASS", "適應性特性已實現", 1.0)
            else:
                self._add_result("適應性機制", feature, "FAIL", "適應性特性缺失", 0.0)
    
    def _verify_failover_mechanisms(self, py_content: str, json_spec: Dict):
        """驗證故障恢復機制"""
        print("\n🛡️ 驗證故障恢復機制...")
        
        # 故障恢復特性
        failover_features = [
            "binance",
            "okx",
            "bybit",
            "备援",
            "備援",
            "fallback",
            "5s",  # 切換時間
            "health_check",
            "api_availability"
        ]
        
        for feature in failover_features:
            if feature.lower() in py_content.lower():
                self._add_result("故障恢復", feature, "PASS", "故障恢復特性已實現", 1.0)
            else:
                self._add_result("故障恢復", feature, "FAIL", "故障恢復特性缺失", 0.0)
    
    def _add_result(self, category: str, item: str, status: str, details: str, score: float):
        """添加分析結果"""
        result = AnalysisResult(category, item, status, details, score)
        self.analysis_results.append(result)
        self.total_score += score
        self.max_score += 1.0
    
    def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成綜合報告"""
        print("\n📋 生成綜合分析報告...")
        
        # 按類別統計
        category_stats = {}
        for result in self.analysis_results:
            if result.category not in category_stats:
                category_stats[result.category] = {"pass": 0, "fail": 0, "partial": 0, "total": 0, "score": 0}
            
            category_stats[result.category][result.status.lower()] += 1
            category_stats[result.category]["total"] += 1
            category_stats[result.category]["score"] += result.score
        
        # 計算類別分數
        for category, stats in category_stats.items():
            if stats["total"] > 0:
                stats["percentage"] = (stats["score"] / stats["total"]) * 100
        
        overall_percentage = (self.total_score / self.max_score) * 100 if self.max_score > 0 else 0
        
        # 判定最終狀態
        if overall_percentage >= 95:
            final_status = "✅ EXCELLENT - 接近完美匹配"
        elif overall_percentage >= 85:
            final_status = "🟢 GOOD - 大部分特性已實現"
        elif overall_percentage >= 70:
            final_status = "🟡 PARTIAL - 需要重要改進"
        else:
            final_status = "🔴 POOR - 需要重大重構"
        
        report = {
            "overall_score": overall_percentage,
            "final_status": final_status,
            "category_breakdown": category_stats,
            "critical_missing": self._get_critical_missing(),
            "architecture_gaps": self._get_architecture_gaps(),
            "performance_issues": self._get_performance_issues(),
            "recommendations": self._get_recommendations(overall_percentage)
        }
        
        return report
    
    def _get_critical_missing(self) -> List[str]:
        """獲取關鍵缺失項目"""
        missing = []
        critical_categories = ["7層架構", "數據流連續性", "Layer操作方法"]
        
        for result in self.analysis_results:
            if result.category in critical_categories and result.status == "FAIL":
                missing.append(f"{result.category}: {result.item}")
        
        return missing
    
    def _get_architecture_gaps(self) -> List[str]:
        """獲取架構差距"""
        gaps = []
        
        for result in self.analysis_results:
            if result.category in ["7層架構", "Phase1C整合"] and result.status == "FAIL":
                gaps.append(f"{result.item}: {result.details}")
        
        return gaps
    
    def _get_performance_issues(self) -> List[str]:
        """獲取性能問題"""
        issues = []
        
        for result in self.analysis_results:
            if result.category in ["性能優化", "性能目標"] and result.status == "FAIL":
                issues.append(f"{result.item}: {result.details}")
        
        return issues
    
    def _get_recommendations(self, score: float) -> List[str]:
        """獲取改進建議"""
        recommendations = []
        
        if score < 95:
            recommendations.append("實現所有失敗的分析項目")
        
        if score < 85:
            recommendations.append("重點關注7層架構完整性和數據流連續性")
        
        if score < 70:
            recommendations.append("需要重新設計核心架構以符合JSON規範")
        
        # 具體建議
        if score < 90:
            recommendations.append("完善事件驅動和適應性機制")
            recommendations.append("實現完整的性能優化特性")
            recommendations.append("確保Phase1C整合的完整性")
        
        return recommendations
    
    def _load_file(self, filepath: str) -> str:
        """載入文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"載入文件失敗 {filepath}: {e}")
            return ""
    
    def _load_json(self, filepath: str) -> Dict:
        """載入JSON文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"載入JSON失敗 {filepath}: {e}")
            return {}

def main():
    """主函數"""
    analyzer = Phase3PrecisionAnalyzer()
    
    # 文件路徑
    py_file = "X/backend/phase1_signal_generation/phase3_market_analyzer/phase3_market_analyzer.py"
    json_file = "X/backend/phase1_signal_generation/phase3_market_analyzer/phase3_market_analyzer_CORE_FLOW.json"
    
    # 執行分析
    report = analyzer.analyze_complete_implementation(py_file, json_file)
    
    # 顯示結果
    print("\n" + "="*80)
    print("🎯 PHASE3 MARKET ANALYZER 精確深度分析報告")
    print("="*80)
    print(f"總體分數: {report['overall_score']:.1f}%")
    print(f"最終狀態: {report['final_status']}")
    
    print("\n📊 類別分析:")
    for category, stats in report['category_breakdown'].items():
        print(f"  {category}: {stats['percentage']:.1f}% "
              f"(✅{stats['pass']} ❌{stats['fail']})")
    
    if report['critical_missing']:
        print("\n🚨 關鍵缺失:")
        for missing in report['critical_missing'][:10]:  # 顯示前10個
            print(f"  • {missing}")
    
    if report['architecture_gaps']:
        print("\n🏗️ 架構差距:")
        for gap in report['architecture_gaps'][:5]:  # 顯示前5個
            print(f"  • {gap}")
    
    if report['performance_issues']:
        print("\n⚡ 性能問題:")
        for issue in report['performance_issues'][:5]:  # 顯示前5個
            print(f"  • {issue}")
    
    if report['recommendations']:
        print("\n💡 改進建議:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
    
    print("\n" + "="*80)
    
    return report

if __name__ == "__main__":
    main()
