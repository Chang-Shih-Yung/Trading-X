#!/usr/bin/env python3
"""
統一測試執行器 - Phase1-4 綜合測試框架
功能：
1. 順序執行所有階段測試
2. 生成整合測試報告
3. 性能基準測試和比較
4. 錯誤分析和建議
5. 測試結果導出和歸檔
"""

import asyncio
import time
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import numpy as np

# 導入各階段測試模組
from test_websocket_realtime_driver import WebSocketDataLayerTest
from test_phase1_comprehensive import Phase1ComprehensiveTest
from test_phase2_strategy_level import Phase2StrategyLevelTest
from test_phase3_cross_integration import Phase3CrossPhaseIntegrationTest
from test_phase4_frontend_e2e import Phase4FrontendEndToEndTest

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UnifiedTestRunner:
    """統一測試執行器"""
    
    def __init__(self):
        self.test_results = {}
        self.execution_start_time = None
        self.execution_end_time = None
        self.performance_benchmarks = {
            'websocket_layer': {'target_latency_ms': 10.0, 'target_throughput': 10000},
            'phase1_processing': {'target_latency_ms': 150.0, 'target_accuracy': 90.0},
            'phase2_strategy': {'target_latency_ms': 200.0, 'target_accuracy': 85.0},
            'phase3_integration': {'target_latency_ms': 100.0, 'target_reliability': 95.0},
            'phase4_frontend': {'target_latency_ms': 200.0, 'target_ux_score': 8.0}
        }
        
    async def run_complete_test_suite(self, test_phases: List[str] = None) -> Dict[str, Any]:
        """執行完整測試套件"""
        
        if test_phases is None:
            test_phases = [
                "websocket_data_layer",
                "phase1_comprehensive", 
                "phase2_strategy_level",
                "phase3_cross_integration",
                "phase4_frontend_e2e"
            ]
        
        logger.info("🚀 開始執行統一測試套件...")
        logger.info(f"📋 測試階段: {', '.join(test_phases)}")
        
        self.execution_start_time = datetime.now()
        overall_start_time = time.time()
        
        # 執行各階段測試
        for phase in test_phases:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 執行階段: {phase}")
            logger.info(f"{'='*60}")
            
            phase_start_time = time.time()
            
            try:
                if phase == "websocket_data_layer":
                    result = await self._run_websocket_tests()
                elif phase == "phase1_comprehensive":
                    result = await self._run_phase1_tests()
                elif phase == "phase2_strategy_level":
                    result = await self._run_phase2_tests()
                elif phase == "phase3_cross_integration":
                    result = await self._run_phase3_tests()
                elif phase == "phase4_frontend_e2e":
                    result = await self._run_phase4_tests()
                else:
                    logger.warning(f"⚠️ 未知測試階段: {phase}")
                    continue
                
                phase_duration = time.time() - phase_start_time
                result['phase_duration_s'] = phase_duration
                
                self.test_results[phase] = result
                
                status = "✅ PASSED" if result.get("success", False) or result.get("overall_success_rate", 0) >= 80.0 else "❌ FAILED"
                logger.info(f"\n{status} {phase} 完成 - 耗時: {phase_duration:.2f}秒")
                
            except Exception as e:
                logger.error(f"❌ {phase} 執行失敗: {e}")
                self.test_results[phase] = {
                    "success": False,
                    "error": str(e),
                    "phase_duration_s": time.time() - phase_start_time
                }
        
        self.execution_end_time = datetime.now()
        total_duration = time.time() - overall_start_time
        
        # 生成綜合報告
        comprehensive_report = await self._generate_comprehensive_report(total_duration)
        
        logger.info(f"\n🎯 統一測試套件完成 - 總耗時: {total_duration:.2f}秒")
        logger.info(f"📊 整體狀態: {comprehensive_report['execution_summary']['overall_status']}")
        
        return comprehensive_report
    
    async def _run_websocket_tests(self) -> Dict[str, Any]:
        """執行WebSocket數據層測試"""
        tester = WebSocketDataLayerTest()
        return await tester.run_all_tests()
    
    async def _run_phase1_tests(self) -> Dict[str, Any]:
        """執行Phase1綜合測試"""
        tester = Phase1ComprehensiveTest()
        return await tester.run_all_tests()
    
    async def _run_phase2_tests(self) -> Dict[str, Any]:
        """執行Phase2策略層級測試"""
        tester = Phase2StrategyLevelTest()
        return await tester.run_all_tests()
    
    async def _run_phase3_tests(self) -> Dict[str, Any]:
        """執行Phase3跨階段整合測試"""
        tester = Phase3CrossPhaseIntegrationTest()
        return await tester.run_all_tests()
    
    async def _run_phase4_tests(self) -> Dict[str, Any]:
        """執行Phase4前端端到端測試"""
        tester = Phase4FrontendEndToEndTest()
        return await tester.run_all_tests()
    
    async def _generate_comprehensive_report(self, total_duration: float) -> Dict[str, Any]:
        """生成綜合測試報告"""
        
        # 計算整體統計
        total_phases = len(self.test_results)
        successful_phases = sum(
            1 for result in self.test_results.values() 
            if result.get("success", False) or result.get("overall_success_rate", 0) >= 80.0
        )
        
        overall_success_rate = (successful_phases / total_phases) * 100 if total_phases > 0 else 0
        
        # 性能分析
        performance_analysis = await self._analyze_performance_metrics()
        
        # 錯誤分析
        error_analysis = await self._analyze_errors_and_failures()
        
        # 基準測試比較
        benchmark_comparison = await self._compare_with_benchmarks()
        
        # 改進建議
        improvement_recommendations = await self._generate_improvement_recommendations()
        
        comprehensive_report = {
            "execution_summary": {
                "start_time": self.execution_start_time.isoformat(),
                "end_time": self.execution_end_time.isoformat(),
                "total_duration_s": total_duration,
                "total_phases": total_phases,
                "successful_phases": successful_phases,
                "failed_phases": total_phases - successful_phases,
                "overall_success_rate": overall_success_rate,
                "overall_status": "✅ PASSED" if overall_success_rate >= 80.0 else "❌ FAILED"
            },
            "phase_results": self.test_results,
            "performance_analysis": performance_analysis,
            "error_analysis": error_analysis,
            "benchmark_comparison": benchmark_comparison,
            "improvement_recommendations": improvement_recommendations,
            "test_environment": {
                "timestamp": datetime.now().isoformat(),
                "python_version": sys.version,
                "platform": sys.platform
            }
        }
        
        # 保存報告到文件
        await self._save_report_to_file(comprehensive_report)
        
        return comprehensive_report
    
    async def _analyze_performance_metrics(self) -> Dict[str, Any]:
        """分析性能指標"""
        
        performance_data = {}
        
        for phase_name, result in self.test_results.items():
            if not result.get("success") and result.get("overall_success_rate", 0) < 80.0:
                continue
            
            phase_metrics = {
                "duration_s": result.get("phase_duration_s", 0),
                "success_rate": result.get("overall_success_rate", 0),
                "performance_stats": result.get("performance_statistics", {})
            }
            
            # 提取具體性能數據
            if "performance_statistics" in result:
                stats = result["performance_statistics"]
                
                if phase_name == "websocket_data_layer":
                    phase_metrics["avg_latency_ms"] = stats.get("latency", {}).get("avg", 0)
                    phase_metrics["throughput"] = stats.get("throughput", {}).get("avg", 0)
                
                elif phase_name in ["phase1_comprehensive", "phase2_strategy_level"]:
                    # 計算各組件平均延遲
                    latencies = []
                    for key, value in stats.items():
                        if "latency" in key and isinstance(value, dict):
                            latencies.append(value.get("avg_ms", 0))
                    
                    phase_metrics["avg_component_latency_ms"] = np.mean(latencies) if latencies else 0
                
                elif phase_name == "phase3_cross_integration":
                    phase_metrics["end_to_end_latency_ms"] = stats.get("end_to_end_latency", {}).get("avg", 0)
                    phase_metrics["error_recovery_time_ms"] = stats.get("error_recovery_time", {}).get("avg", 0)
                
                elif phase_name == "phase4_frontend_e2e":
                    phase_metrics["ui_response_time_ms"] = stats.get("ui_update_latency", {}).get("avg", 0)
                    phase_metrics["user_interaction_latency_ms"] = stats.get("user_interaction_latency", {}).get("avg", 0)
            
            performance_data[phase_name] = phase_metrics
        
        # 計算整體性能分數
        overall_performance_score = self._calculate_overall_performance_score(performance_data)
        
        return {
            "phase_performance": performance_data,
            "overall_performance_score": overall_performance_score,
            "performance_trends": self._identify_performance_trends(performance_data)
        }
    
    def _calculate_overall_performance_score(self, performance_data: Dict[str, Any]) -> float:
        """計算整體性能分數"""
        
        scores = []
        
        for phase_name, metrics in performance_data.items():
            phase_score = 0
            
            # 基於成功率的分數
            success_rate = metrics.get("success_rate", 0)
            phase_score += success_rate * 0.4
            
            # 基於延遲的分數
            if phase_name in self.performance_benchmarks:
                benchmark = self.performance_benchmarks[phase_name]
                
                if "target_latency_ms" in benchmark:
                    if phase_name == "websocket_data_layer":
                        actual_latency = metrics.get("avg_latency_ms", float('inf'))
                    elif phase_name in ["phase1_comprehensive", "phase2_strategy_level"]:
                        actual_latency = metrics.get("avg_component_latency_ms", float('inf'))
                    elif phase_name == "phase3_cross_integration":
                        actual_latency = metrics.get("end_to_end_latency_ms", float('inf'))
                    else:  # phase4
                        actual_latency = metrics.get("ui_response_time_ms", float('inf'))
                    
                    target_latency = benchmark["target_latency_ms"]
                    
                    if actual_latency <= target_latency:
                        latency_score = 100
                    else:
                        latency_score = max(0, 100 - ((actual_latency - target_latency) / target_latency * 100))
                    
                    phase_score += latency_score * 0.6
                else:
                    phase_score += 60  # 默認分數如果沒有延遲基準
            
            scores.append(min(100, phase_score))
        
        return np.mean(scores) if scores else 0
    
    def _identify_performance_trends(self, performance_data: Dict[str, Any]) -> List[str]:
        """識別性能趨勢"""
        
        trends = []
        
        # 分析延遲趨勢
        latencies = []
        phase_order = ["websocket_data_layer", "phase1_comprehensive", "phase2_strategy_level", 
                      "phase3_cross_integration", "phase4_frontend_e2e"]
        
        for phase in phase_order:
            if phase in performance_data:
                metrics = performance_data[phase]
                
                if phase == "websocket_data_layer":
                    latency = metrics.get("avg_latency_ms", 0)
                elif phase in ["phase1_comprehensive", "phase2_strategy_level"]:
                    latency = metrics.get("avg_component_latency_ms", 0)
                elif phase == "phase3_cross_integration":
                    latency = metrics.get("end_to_end_latency_ms", 0)
                else:
                    latency = metrics.get("ui_response_time_ms", 0)
                
                latencies.append(latency)
        
        if len(latencies) >= 3:
            # 檢查延遲是否逐步增加
            increasing_trend = all(latencies[i] <= latencies[i+1] for i in range(len(latencies)-1))
            if increasing_trend:
                trends.append("延遲隨處理階段逐步增加，符合預期")
            
            # 檢查是否有異常高延遲
            avg_latency = np.mean(latencies)
            for i, latency in enumerate(latencies):
                if latency > avg_latency * 2:
                    trends.append(f"{phase_order[i]} 階段延遲異常偏高")
        
        # 分析成功率趨勢
        success_rates = [metrics.get("success_rate", 0) for metrics in performance_data.values()]
        if success_rates:
            min_success_rate = min(success_rates)
            if min_success_rate >= 95:
                trends.append("所有階段成功率優秀 (>=95%)")
            elif min_success_rate >= 80:
                trends.append("整體成功率良好，部分階段可優化")
            else:
                trends.append("存在成功率偏低的階段，需要重點關注")
        
        return trends
    
    async def _analyze_errors_and_failures(self) -> Dict[str, Any]:
        """分析錯誤和失敗"""
        
        error_summary = {
            "total_errors": 0,
            "error_categories": {},
            "critical_failures": [],
            "failure_patterns": []
        }
        
        for phase_name, result in self.test_results.items():
            if "error" in result:
                error_summary["total_errors"] += 1
                error_summary["critical_failures"].append({
                    "phase": phase_name,
                    "error": result["error"],
                    "impact": "critical"
                })
            
            # 分析詳細結果中的錯誤
            if "detailed_results" in result:
                for test_name, test_result in result["detailed_results"].items():
                    if not test_result.get("success", True):
                        error_summary["total_errors"] += 1
                        
                        # 分類錯誤類型
                        if "timeout" in test_result.get("error", "").lower():
                            category = "timeout_errors"
                        elif "connection" in test_result.get("error", "").lower():
                            category = "connection_errors"
                        elif "validation" in test_result.get("error", "").lower():
                            category = "validation_errors"
                        else:
                            category = "other_errors"
                        
                        error_summary["error_categories"][category] = error_summary["error_categories"].get(category, 0) + 1
        
        # 識別失敗模式
        if error_summary["total_errors"] > 0:
            if error_summary["error_categories"].get("timeout_errors", 0) > 2:
                error_summary["failure_patterns"].append("性能相關超時問題")
            
            if error_summary["error_categories"].get("connection_errors", 0) > 1:
                error_summary["failure_patterns"].append("網路連接穩定性問題")
            
            if len(error_summary["critical_failures"]) > 1:
                error_summary["failure_patterns"].append("多個關鍵階段失敗")
        
        return error_summary
    
    async def _compare_with_benchmarks(self) -> Dict[str, Any]:
        """與基準測試比較"""
        
        benchmark_results = {}
        
        for phase_name, result in self.test_results.items():
            if phase_name not in self.performance_benchmarks:
                continue
            
            benchmark = self.performance_benchmarks[phase_name]
            actual_metrics = {}
            
            # 提取實際指標
            if phase_name == "websocket_data_layer":
                # WebSocket層基準比較
                if "performance_statistics" in result:
                    stats = result["performance_statistics"]
                    actual_metrics["latency_ms"] = stats.get("latency", {}).get("avg", 0)
                    actual_metrics["throughput"] = stats.get("throughput", {}).get("avg", 0)
            
            elif phase_name in ["phase1_comprehensive", "phase2_strategy_level"]:
                # Phase1/2基準比較
                actual_metrics["success_rate"] = result.get("overall_success_rate", 0)
                
                if "performance_statistics" in result:
                    stats = result["performance_statistics"]
                    latencies = []
                    for key, value in stats.items():
                        if "latency" in key and isinstance(value, dict):
                            latencies.append(value.get("avg_ms", 0))
                    actual_metrics["avg_latency_ms"] = np.mean(latencies) if latencies else 0
            
            elif phase_name == "phase3_cross_integration":
                # Phase3基準比較
                actual_metrics["success_rate"] = result.get("overall_success_rate", 0)
                if "performance_statistics" in result:
                    stats = result["performance_statistics"]
                    actual_metrics["end_to_end_latency_ms"] = stats.get("end_to_end_latency", {}).get("avg", 0)
            
            elif phase_name == "phase4_frontend_e2e":
                # Phase4基準比較
                actual_metrics["success_rate"] = result.get("overall_success_rate", 0)
                
                # 尋找用戶體驗分數
                if "detailed_results" in result:
                    for test_result in result["detailed_results"].values():
                        if "avg_satisfaction_score" in test_result:
                            actual_metrics["ux_score"] = test_result["avg_satisfaction_score"]
                            break
            
            # 計算基準達成情況
            benchmark_achievement = {}
            for metric_name, target_value in benchmark.items():
                actual_value = actual_metrics.get(metric_name.replace("target_", ""), 0)
                
                if "latency" in metric_name:
                    # 延遲越低越好
                    achievement = min(100, (target_value / actual_value) * 100) if actual_value > 0 else 0
                else:
                    # 其他指標越高越好
                    achievement = min(100, (actual_value / target_value) * 100) if target_value > 0 else 0
                
                benchmark_achievement[metric_name] = {
                    "target": target_value,
                    "actual": actual_value,
                    "achievement_percentage": achievement,
                    "status": "✅ 達成" if achievement >= 90 else "⚠️ 部分達成" if achievement >= 70 else "❌ 未達成"
                }
            
            benchmark_results[phase_name] = benchmark_achievement
        
        return benchmark_results
    
    async def _generate_improvement_recommendations(self) -> List[Dict[str, str]]:
        """生成改進建議"""
        
        recommendations = []
        
        # 分析整體結果
        overall_success_rate = sum(
            1 for result in self.test_results.values() 
            if result.get("success", False) or result.get("overall_success_rate", 0) >= 80.0
        ) / len(self.test_results) * 100
        
        if overall_success_rate < 80:
            recommendations.append({
                "category": "整體性能",
                "priority": "高",
                "description": "整體測試成功率偏低，建議重點優化失敗的測試階段",
                "action": "檢查失敗測試的詳細錯誤日誌，優先修復關鍵路徑問題"
            })
        
        # 分析各階段具體問題
        for phase_name, result in self.test_results.items():
            phase_success = result.get("success", False) or result.get("overall_success_rate", 0) >= 80.0
            
            if not phase_success:
                if phase_name == "websocket_data_layer":
                    recommendations.append({
                        "category": "WebSocket數據層",
                        "priority": "極高",
                        "description": "WebSocket數據層是整個系統的基礎，必須優先修復",
                        "action": "檢查WebSocket連接穩定性、數據處理管道、高勝率檢測引擎"
                    })
                
                elif phase_name == "phase1_comprehensive":
                    recommendations.append({
                        "category": "Phase1信號生成",
                        "priority": "高",
                        "description": "信號生成系統存在問題，影響後續所有階段",
                        "action": "優化技術指標計算、波動率適應機制、信號標準化流程"
                    })
                
                elif phase_name == "phase2_strategy_level":
                    recommendations.append({
                        "category": "Phase2策略引擎",
                        "priority": "高",
                        "description": "策略引擎性能不達標，影響交易決策質量",
                        "action": "優化策略邏輯、多時間框架分析、風險管理算法"
                    })
                
                elif phase_name == "phase3_cross_integration":
                    recommendations.append({
                        "category": "跨階段整合",
                        "priority": "中",
                        "description": "跨組件整合存在問題，可能影響系統穩定性",
                        "action": "檢查組件間接口、錯誤處理機制、負載均衡"
                    })
                
                elif phase_name == "phase4_frontend_e2e":
                    recommendations.append({
                        "category": "前端用戶體驗",
                        "priority": "中",
                        "description": "前端體驗問題影響用戶滿意度",
                        "action": "優化UI響應速度、數據同步機制、用戶交互流程"
                    })
        
        # 性能優化建議
        performance_analysis = await self._analyze_performance_metrics()
        if performance_analysis["overall_performance_score"] < 75:
            recommendations.append({
                "category": "性能優化",
                "priority": "中",
                "description": "整體性能分數偏低，建議進行系統性能調優",
                "action": "分析性能瓶頸、優化算法效率、考慮硬體升級"
            })
        
        return recommendations
    
    async def _save_report_to_file(self, report: Dict[str, Any]) -> None:
        """保存報告到文件"""
        
        # 創建報告目錄
        report_dir = "test_reports"
        os.makedirs(report_dir, exist_ok=True)
        
        # 生成報告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"{report_dir}/comprehensive_test_report_{timestamp}.json"
        
        # 保存JSON報告
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"📄 測試報告已保存到: {report_filename}")
            
        except Exception as e:
            logger.error(f"❌ 保存報告失敗: {e}")
        
        # 生成簡化的摘要報告
        summary_filename = f"{report_dir}/test_summary_{timestamp}.txt"
        try:
            with open(summary_filename, 'w', encoding='utf-8') as f:
                f.write("=== Trading-X Phase1-4 測試摘要報告 ===\n\n")
                
                exec_summary = report["execution_summary"]
                f.write(f"執行時間: {exec_summary['start_time']} - {exec_summary['end_time']}\n")
                f.write(f"總耗時: {exec_summary['total_duration_s']:.2f} 秒\n")
                f.write(f"測試階段: {exec_summary['total_phases']}\n")
                f.write(f"成功階段: {exec_summary['successful_phases']}\n")
                f.write(f"整體成功率: {exec_summary['overall_success_rate']:.1f}%\n")
                f.write(f"狀態: {exec_summary['overall_status']}\n\n")
                
                f.write("=== 各階段結果 ===\n")
                for phase_name, result in report["phase_results"].items():
                    success = result.get("success", False) or result.get("overall_success_rate", 0) >= 80.0
                    status = "✅ PASSED" if success else "❌ FAILED"
                    duration = result.get("phase_duration_s", 0)
                    f.write(f"{phase_name}: {status} ({duration:.2f}s)\n")
                
                f.write(f"\n=== 性能分析 ===\n")
                perf_analysis = report["performance_analysis"]
                f.write(f"整體性能分數: {perf_analysis['overall_performance_score']:.1f}/100\n")
                
                f.write(f"\n=== 改進建議 ===\n")
                for i, rec in enumerate(report["improvement_recommendations"], 1):
                    f.write(f"{i}. [{rec['priority']}] {rec['category']}: {rec['description']}\n")
            
            logger.info(f"📋 測試摘要已保存到: {summary_filename}")
            
        except Exception as e:
            logger.error(f"❌ 保存摘要失敗: {e}")

# 主執行函數
async def main():
    """主測試執行函數"""
    
    # 檢查命令行參數
    import argparse
    parser = argparse.ArgumentParser(description='Trading-X 統一測試執行器')
    parser.add_argument('--phases', nargs='*', 
                       choices=['websocket_data_layer', 'phase1_comprehensive', 
                               'phase2_strategy_level', 'phase3_cross_integration', 
                               'phase4_frontend_e2e'],
                       help='指定要執行的測試階段')
    parser.add_argument('--quick', action='store_true', 
                       help='快速測試模式（跳過部分耗時測試）')
    
    args = parser.parse_args()
    
    # 創建測試執行器
    runner = UnifiedTestRunner()
    
    # 執行測試
    try:
        logger.info("🎯 Trading-X 統一測試執行器啟動")
        
        report = await runner.run_complete_test_suite(args.phases)
        
        # 輸出最終結果
        print("\n" + "="*80)
        print("🏆 Trading-X Phase1-4 綜合測試完成")
        print("="*80)
        
        exec_summary = report["execution_summary"]
        print(f"📊 整體成功率: {exec_summary['overall_success_rate']:.1f}%")
        print(f"⏱️  總耗時: {exec_summary['total_duration_s']:.2f} 秒")
        print(f"🎯 最終狀態: {exec_summary['overall_status']}")
        
        print(f"\n📈 性能分數: {report['performance_analysis']['overall_performance_score']:.1f}/100")
        
        if report["improvement_recommendations"]:
            print(f"\n💡 改進建議數量: {len(report['improvement_recommendations'])}")
            for rec in report["improvement_recommendations"][:3]:  # 顯示前3個建議
                print(f"   • [{rec['priority']}] {rec['category']}: {rec['description']}")
        
        # 根據結果決定退出代碼
        exit_code = 0 if exec_summary['overall_success_rate'] >= 80.0 else 1
        return exit_code
        
    except Exception as e:
        logger.error(f"❌ 測試執行器發生嚴重錯誤: {e}")
        return 1

if __name__ == "__main__":
    # 運行統一測試執行器
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
