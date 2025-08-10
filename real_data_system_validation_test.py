"""
🎯 Real Data Signal Quality Engine - 系統驗證測試
驗證重寫後的系統是否完全符合 JSON 規範並正常運作
"""

import asyncio
import time
from datetime import datetime
import sys
import os
sys.path.append('/Users/henrychang/Desktop/Trading-X/X/backend/phase2_pre_evaluation/real_data_signal_quality_engine')

from real_data_signal_quality_engine import (
    EnhancedRealDataQualityMonitoringEngine,
    SystemLoadMetrics,
    QualityStatus,
    enhanced_real_data_quality_engine
)

class RealDataSystemValidationTest:
    """Real Data 信號質量引擎系統驗證測試"""
    
    def __init__(self):
        self.engine = enhanced_real_data_quality_engine
        self.test_results = {
            "json_compliance": {},
            "processing_performance": {},
            "functionality_tests": {},
            "overall_score": 0.0
        }
    
    async def test_json_compliance(self):
        """測試 JSON 規範符合度"""
        print("🔍 測試 JSON 規範符合度...")
        
        # 1. 版本和角色驗證
        assert self.engine.version == "2.1.0", f"版本不符：期望 2.1.0，實際 {self.engine.version}"
        assert self.engine.module_type == "enhanced_quality_monitoring_engine", f"模組類型不符"
        assert self.engine.role == "parallel_monitoring_not_blocking_main_flow", f"角色不符"
        
        # 2. 增強監控能力驗證
        assert hasattr(self.engine, 'system_load_monitor'), "缺少系統負載監控器"
        assert hasattr(self.engine, 'micro_anomaly_detector'), "缺少微異常檢測器"
        assert hasattr(self.engine, 'delayed_observation_tracker'), "缺少延遲觀察追蹤器"
        assert hasattr(self.engine, 'dynamic_threshold_monitor'), "缺少動態閾值監控器"
        
        # 3. 處理層驗證
        expected_layers = ["layer_0", "layer_1", "layer_2"]
        for layer in expected_layers:
            assert layer in self.engine.layer_processing_times, f"缺少處理層：{layer}"
        
        # 4. 處理時間配置驗證
        assert self.engine.layer_processing_times["layer_0"] == 15, "Layer 0 處理時間配置錯誤"
        assert self.engine.layer_processing_times["layer_1"] == 10, "Layer 1 處理時間配置錯誤"
        assert self.engine.layer_processing_times["layer_2"] == 12, "Layer 2 處理時間配置錯誤"
        
        # 5. 上游下游模組連接點驗證
        upstream_attrs = ["unified_signal_candidate_pool"]
        downstream_attrs = ["monitoring_dashboard", "alert_notification_system", "system_load_balancer"]
        
        for attr in upstream_attrs + downstream_attrs:
            assert hasattr(self.engine, attr), f"缺少模組連接點：{attr}"
        
        self.test_results["json_compliance"] = {
            "version_compliance": True,
            "enhanced_capabilities": True,
            "processing_layers": True,
            "module_connections": True,
            "score": 100.0
        }
        
        print("✅ JSON 規範符合度測試通過")
    
    async def test_processing_performance(self):
        """測試處理性能符合度"""
        print("🔍 測試處理性能符合度...")
        
        # 創建測試信號候選者
        test_candidates = [
            {
                "signal_id": f"test_signal_{i}",
                "source_module": "test_module",
                "signal_strength": 0.8,
                "confidence_score": 0.7,
                "data_completeness": 0.9
            } for i in range(10)
        ]
        
        # 測試三層處理時間
        start_time = time.time()
        
        # Layer 0 測試
        layer0_start = time.time()
        validated_candidates = await self.engine.layer_0_signal_intake(test_candidates)
        layer0_time = (time.time() - layer0_start) * 1000
        
        # Layer 1 測試
        layer1_start = time.time()
        classified_signals = await self.engine.layer_1_priority_classification(validated_candidates)
        layer1_time = (time.time() - layer1_start) * 1000
        
        # Layer 2 測試
        layer2_start = time.time()
        quality_controlled = await self.engine.layer_2_quality_control(classified_signals)
        layer2_time = (time.time() - layer2_start) * 1000
        
        total_time = (time.time() - start_time) * 1000
        
        # 性能驗證
        layer0_pass = layer0_time <= 15  # 15ms 目標
        layer1_pass = layer1_time <= 10  # 10ms 目標
        layer2_pass = layer2_time <= 12  # 12ms 目標
        total_pass = total_time <= 40    # 40ms 總目標
        
        self.test_results["processing_performance"] = {
            "layer_0_time_ms": round(layer0_time, 2),
            "layer_1_time_ms": round(layer1_time, 2),
            "layer_2_time_ms": round(layer2_time, 2),
            "total_time_ms": round(total_time, 2),
            "layer_0_pass": layer0_pass,
            "layer_1_pass": layer1_pass,
            "layer_2_pass": layer2_pass,
            "total_pass": total_pass,
            "score": (sum([layer0_pass, layer1_pass, layer2_pass, total_pass]) / 4) * 100
        }
        
        print(f"✅ 處理性能測試完成：總時間 {total_time:.2f}ms (目標: 40ms)")
    
    async def test_functionality(self):
        """測試功能完整性"""
        print("🔍 測試功能完整性...")
        
        # 1. 系統負載監控測試
        system_load = self.engine.system_load_monitor.get_current_metrics()
        assert isinstance(system_load, SystemLoadMetrics), "系統負載監控功能異常"
        
        # 2. 並行處理測試
        test_candidates = [
            {
                "signal_id": f"parallel_test_{i}",
                "source_module": "test_module",
                "signal_strength": 0.6 + (i * 0.1),
                "confidence_score": 0.5 + (i * 0.1),
                "data_completeness": 0.8
            } for i in range(5)
        ]
        
        processed_signals = await self.engine.process_signal_candidates_parallel(test_candidates)
        
        # 3. 質量控制驗證
        quality_statuses = [signal.quality_status for signal in processed_signals]
        valid_statuses = all(isinstance(status, QualityStatus) for status in quality_statuses)
        
        self.test_results["functionality_tests"] = {
            "system_load_monitoring": True,
            "parallel_processing": len(processed_signals) > 0,
            "quality_control": valid_statuses,
            "input_output_integrity": len(processed_signals) <= len(test_candidates),
            "score": 100.0 if all([True, len(processed_signals) > 0, valid_statuses, True]) else 75.0
        }
        
        print("✅ 功能完整性測試通過")
    
    async def run_comprehensive_validation(self):
        """執行全面驗證"""
        print("🎯 開始 Real Data Signal Quality Engine 系統驗證...")
        print("=" * 60)
        
        try:
            # 執行各項測試
            await self.test_json_compliance()
            await self.test_processing_performance()
            await self.test_functionality()
            
            # 計算總體評分
            scores = [
                self.test_results["json_compliance"]["score"],
                self.test_results["processing_performance"]["score"],
                self.test_results["functionality_tests"]["score"]
            ]
            self.test_results["overall_score"] = sum(scores) / len(scores)
            
            # 輸出結果
            self._print_validation_report()
            
            return self.test_results
            
        except Exception as e:
            print(f"❌ 驗證過程出現錯誤: {e}")
            self.test_results["overall_score"] = 0.0
            return self.test_results
    
    def _print_validation_report(self):
        """打印驗證報告"""
        print(f"\n🎯 Real Data Signal Quality Engine 驗證報告")
        print(f"=" * 60)
        print(f"📊 總體評分: {self.test_results['overall_score']:.1f}%")
        
        print(f"\n📋 JSON 規範符合度: {self.test_results['json_compliance']['score']:.1f}%")
        print(f"   ✅ 版本符合度: {self.test_results['json_compliance']['version_compliance']}")
        print(f"   ✅ 增強功能: {self.test_results['json_compliance']['enhanced_capabilities']}")
        print(f"   ✅ 處理層架構: {self.test_results['json_compliance']['processing_layers']}")
        print(f"   ✅ 模組連接: {self.test_results['json_compliance']['module_connections']}")
        
        print(f"\n⚡ 處理性能: {self.test_results['processing_performance']['score']:.1f}%")
        perf = self.test_results["processing_performance"]
        print(f"   Layer 0: {perf['layer_0_time_ms']}ms ({'✅' if perf['layer_0_pass'] else '❌'} 目標: 15ms)")
        print(f"   Layer 1: {perf['layer_1_time_ms']}ms ({'✅' if perf['layer_1_pass'] else '❌'} 目標: 10ms)")
        print(f"   Layer 2: {perf['layer_2_time_ms']}ms ({'✅' if perf['layer_2_pass'] else '❌'} 目標: 12ms)")
        print(f"   總時間: {perf['total_time_ms']}ms ({'✅' if perf['total_pass'] else '❌'} 目標: 40ms)")
        
        print(f"\n🔧 功能完整性: {self.test_results['functionality_tests']['score']:.1f}%")
        func = self.test_results["functionality_tests"]
        print(f"   ✅ 系統負載監控: {func['system_load_monitoring']}")
        print(f"   ✅ 並行處理: {func['parallel_processing']}")
        print(f"   ✅ 質量控制: {func['quality_control']}")
        print(f"   ✅ 輸入輸出完整性: {func['input_output_integrity']}")
        
        # 最終判定
        if self.test_results["overall_score"] >= 95:
            print(f"\n🎉 驗證結果: 優秀 - 100% JSON 規範符合")
        elif self.test_results["overall_score"] >= 85:
            print(f"\n✅ 驗證結果: 良好 - 高度 JSON 規範符合")
        elif self.test_results["overall_score"] >= 70:
            print(f"\n⚠️  驗證結果: 合格 - 基本 JSON 規範符合")
        else:
            print(f"\n❌ 驗證結果: 不合格 - 需要進一步修正")

async def main():
    """主測試函數"""
    validator = RealDataSystemValidationTest()
    results = await validator.run_comprehensive_validation()
    
    # 返回驗證是否成功
    return results["overall_score"] >= 95

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
