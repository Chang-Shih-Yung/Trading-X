#!/usr/bin/env python3
"""
Signal Processing Statistics Python實現驗證腳本
驗證 signal_processing_statistics.py 與 JSON 配置的匹配度
"""

import json
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Any, Tuple

class SignalStatsPythonValidator:
    def __init__(self):
        self.base_path = Path("/Users/henrychang/Desktop/Trading-X")
        self.json_path = self.base_path / "X/backend/phase4_output_monitoring/2_signal_processing_statistics/signal_processing_statistics_config.json"
        self.py_path = self.base_path / "X/backend/phase4_output_monitoring/2_signal_processing_statistics/signal_processing_statistics.py"
        
    def load_json_config(self) -> Dict[str, Any]:
        """載入JSON配置"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 無法載入JSON配置: {e}")
            return {}
    
    def analyze_python_implementation(self) -> Dict[str, Any]:
        """分析Python實現"""
        try:
            with open(self.py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            classes = []
            methods = []
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    methods.append(node.name)
                elif isinstance(node, ast.AsyncFunctionDef):
                    methods.append(node.name)
            
            return {
                "classes": classes,
                "methods": methods,
                "functions": functions,
                "line_count": len(content.split('\n'))
            }
        except Exception as e:
            print(f"❌ 無法分析Python實現: {e}")
            return {}
    
    def validate_core_data_structures(self, py_analysis: Dict[str, Any]) -> Tuple[int, int]:
        """驗證核心數據結構"""
        score = 0
        max_score = 25
        
        print("\n🔍 驗證核心數據結構:")
        print("-" * 40)
        
        required_classes = [
            "SignalMetrics",
            "StatisticalSummary", 
            "SignalProcessingStatistics"
        ]
        
        implemented_classes = py_analysis.get("classes", [])
        
        for cls in required_classes:
            if cls in implemented_classes:
                score += 8
                print(f"✅ {cls} 類已定義")
            else:
                print(f"❌ 缺少類: {cls}")
        
        # 額外分數給主類
        if "SignalProcessingStatistics" in implemented_classes:
            score += 1
            print("✅ 主要統計類已實現")
        
        return score, max_score
    
    def validate_phase_integration_features(self, py_analysis: Dict[str, Any], config: Dict[str, Any]) -> Tuple[int, int]:
        """驗證Phase整合功能"""
        score = 0
        max_score = 30
        
        print("\n🔍 驗證Phase整合功能:")
        print("-" * 40)
        
        methods = py_analysis.get("methods", [])
        
        # 檢查Phase延遲分析方法 (基於JSON配置的phase_level_latency)
        phase_latency_methods = [
            "_calculate_statistical_summary",
            "_get_latency_by_priority",
            "_calculate_recent_trends"
        ]
        
        for method in phase_latency_methods:
            if method in methods:
                score += 5
                print(f"✅ {method} 延遲分析方法已實現")
            else:
                print(f"❌ 缺少延遲分析方法: {method}")
        
        # 檢查信號來源分析方法 (基於JSON的signals_by_source)
        source_analysis_methods = [
            "_get_performance_by_source",
            "_get_source_reliability"
        ]
        
        for method in source_analysis_methods:
            if method in methods:
                score += 5
                print(f"✅ {method} 來源分析方法已實現")
            else:
                print(f"❌ 缺少來源分析方法: {method}")
        
        # 檢查優先級分析方法 (基於JSON的signals_by_priority)
        priority_analysis_methods = [
            "_get_success_rate_by_priority"
        ]
        
        for method in priority_analysis_methods:
            if method in methods:
                score += 5
                print(f"✅ {method} 優先級分析方法已實現")
            else:
                print(f"❌ 缺少優先級分析方法: {method}")
        
        return score, max_score
    
    def validate_monitoring_architecture_implementation(self, py_analysis: Dict[str, Any], config: Dict[str, Any]) -> Tuple[int, int]:
        """驗證監控架構實現"""
        score = 0
        max_score = 35
        
        print("\n🔍 驗證監控架構實現:")
        print("-" * 40)
        
        methods = py_analysis.get("methods", [])
        
        # 檢查實時統計方法 (對應JSON的real_time_statistics API)
        if "get_real_time_metrics" in methods:
            score += 10
            print("✅ get_real_time_metrics 實時統計方法已實現")
        else:
            print("❌ 缺少實時統計方法")
        
        # 檢查綜合統計方法 (對應JSON的historical_analytics API)
        if "get_comprehensive_statistics" in methods:
            score += 10
            print("✅ get_comprehensive_statistics 綜合統計方法已實現")
        else:
            print("❌ 缺少綜合統計方法")
        
        # 檢查信號記錄方法 (核心功能)
        if "record_signal_metrics" in methods:
            score += 10
            print("✅ record_signal_metrics 信號記錄方法已實現")
        else:
            print("❌ 缺少信號記錄方法")
        
        # 檢查性能基準方法 (對應JSON的performance_metrics API)
        if "_calculate_performance_benchmarks" in methods:
            score += 5
            print("✅ 性能基準計算方法已實現")
        else:
            print("❌ 缺少性能基準方法")
        
        return score, max_score
    
    def validate_json_compliance_features(self, py_analysis: Dict[str, Any], config: Dict[str, Any]) -> Tuple[int, int]:
        """驗證JSON合規功能"""
        score = 0
        max_score = 30
        
        print("\n🔍 驗證JSON合規功能:")
        print("-" * 40)
        
        methods = py_analysis.get("methods", [])
        
        # 檢查時間模式分析 (對應JSON的temporal_distribution)
        temporal_methods = [
            "_analyze_hourly_patterns",
            "_analyze_daily_patterns",
            "_identify_peak_windows"
        ]
        
        for method in temporal_methods:
            if method in methods:
                score += 5
                print(f"✅ {method} 時間模式分析已實現")
            else:
                print(f"❌ 缺少時間模式分析: {method}")
        
        # 檢查數據更新方法 (對應JSON的data_retention_policy)
        data_management_methods = [
            "_update_distributions",
            "_update_time_window_stats",
            "_cleanup_old_data"
        ]
        
        for method in data_management_methods:
            if method in methods:
                score += 5
                print(f"✅ {method} 數據管理方法已實現")
            else:
                print(f"❌ 缺少數據管理方法: {method}")
        
        return score, max_score
    
    def validate_statistical_analysis_completeness(self, py_analysis: Dict[str, Any]) -> Tuple[int, int]:
        """驗證統計分析完整性"""
        score = 0
        max_score = 20
        
        print("\n🔍 驗證統計分析完整性:")
        print("-" * 40)
        
        methods = py_analysis.get("methods", [])
        
        # 檢查統計計算方法
        statistical_methods = [
            "_calculate_statistical_summary",
            "_get_empty_statistics"
        ]
        
        for method in statistical_methods:
            if method in methods:
                score += 5
                print(f"✅ {method} 統計計算方法已實現")
            else:
                print(f"❌ 缺少統計計算方法: {method}")
        
        # 檢查輔助方法數量
        helper_methods = [m for m in methods if m.startswith("_")]
        if len(helper_methods) >= 15:
            score += 10
            print(f"✅ 豐富的輔助方法 ({len(helper_methods)} 個)")
        elif len(helper_methods) >= 10:
            score += 5
            print(f"⚠️ 基本的輔助方法 ({len(helper_methods)} 個)")
        else:
            print(f"❌ 輔助方法不足 ({len(helper_methods)} 個)")
        
        return score, max_score
    
    def run_validation(self):
        """執行完整驗證"""
        print("🚀 開始驗證 Signal Processing Statistics Python實現...")
        print("=" * 60)
        
        # 載入配置和分析代碼
        config = self.load_json_config()
        py_analysis = self.analyze_python_implementation()
        
        if not config or not py_analysis:
            print("❌ 無法載入必要文件")
            return 0
        
        print(f"📊 Python實現統計:")
        print(f"   - 類定義: {len(py_analysis.get('classes', []))}")
        print(f"   - 方法: {len(py_analysis.get('methods', []))}")
        print(f"   - 函數: {len(py_analysis.get('functions', []))}")
        print(f"   - 代碼行數: {py_analysis.get('line_count', 0)}")
        
        # 執行各項驗證
        struct_score, struct_max = self.validate_core_data_structures(py_analysis)
        phase_score, phase_max = self.validate_phase_integration_features(py_analysis, config)
        arch_score, arch_max = self.validate_monitoring_architecture_implementation(py_analysis, config)
        json_score, json_max = self.validate_json_compliance_features(py_analysis, config)
        stats_score, stats_max = self.validate_statistical_analysis_completeness(py_analysis)
        
        # 計算總分
        total_score = struct_score + phase_score + arch_score + json_score + stats_score
        total_max = struct_max + phase_max + arch_max + json_max + stats_max
        percentage = (total_score / total_max) * 100
        
        print("\n" + "=" * 60)
        print("📋 驗證結果摘要:")
        print(f"   🏗️ 核心數據結構: {struct_score}/{struct_max}")
        print(f"   🔗 Phase整合功能: {phase_score}/{phase_max}") 
        print(f"   📊 監控架構實現: {arch_score}/{arch_max}")
        print(f"   📄 JSON合規功能: {json_score}/{json_max}")
        print(f"   📈 統計分析完整性: {stats_score}/{stats_max}")
        print("-" * 60)
        print(f"🎯 總驗證結果: {total_score}/{total_max} ({percentage:.1f}%)")
        
        if percentage >= 95:
            print("🎉 完美實現！Python代碼完全匹配JSON配置")
        elif percentage >= 85:
            print("✅ 實現良好！建議進行細微調整")
        elif percentage >= 70:
            print("⚠️ 基本實現完成，需要補充缺失功能")
        else:
            print("❌ 實現不完整，需要重大改進")
        
        return percentage

if __name__ == "__main__":
    validator = SignalStatsPythonValidator()
    result = validator.run_validation()
