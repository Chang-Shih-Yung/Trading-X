#!/usr/bin/env python3
"""
🧪 Trading X - 第二階段集成測試
測試月度優化、市場適應和TradingView報告
完整驗證Phase2模組的功能與整合性
"""

import asyncio
import logging
import json
import traceback
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
import sys

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from intelligent_parameter_optimizer import IntelligentParameterOptimizer
from tradingview_style_reporter import TradingViewStyleReportGenerator
from monthly_auto_optimizer import MonthlyAutoOptimizer

logger = logging.getLogger(__name__)

class Phase2IntegrationTester:
    """第二階段集成測試器"""
    
    def __init__(self):
        self.test_results = []
        self.cleanup_files = []
        
    async def test_parameter_optimization_engine(self) -> Dict[str, Any]:
        """測試智能參數優化引擎"""
        logger.info("🔧 測試1: 智能參數優化引擎")
        
        test_result = {
            "test_name": "parameter_optimization_engine",
            "status": "unknown",
            "details": {},
            "execution_time": 0
        }
        
        start_time = datetime.now()
        
        try:
            async with IntelligentParameterOptimizer() as optimizer:
                # 測試1.1: 基本參數優化
                logger.info("  🎯 測試1.1: 基本參數優化")
                basic_result = await optimizer.run_comprehensive_optimization(
                    target_symbols=["BTCUSDT"],
                    target_timeframes=["5m"],
                    days_back=7
                )
                
                test_result["details"]["basic_optimization"] = {
                    "status": "success" if "error" not in basic_result else "failed",
                    "symbols_tested": len(basic_result.get("results", {})),
                    "improvements_found": basic_result.get("summary", {}).get("significant_improvements_count", 0)
                }
                
                # 測試1.2: 多時間框架優化
                logger.info("  📊 測試1.2: 多時間框架優化")
                multi_tf_result = await optimizer.run_comprehensive_optimization(
                    target_symbols=["BTCUSDT"],
                    target_timeframes=["1m", "5m"],
                    days_back=5
                )
                
                test_result["details"]["multi_timeframe_optimization"] = {
                    "status": "success" if "error" not in multi_tf_result else "failed",
                    "timeframes_tested": len(multi_tf_result.get("results", {})),
                    "total_combinations": sum(len(tf_data.get("results", {})) for tf_data in multi_tf_result.get("results", {}).values())
                }
                
                # 測試1.3: 參數範圍驗證
                logger.info("  ⚙️ 測試1.3: 參數範圍驗證")
                custom_ranges = {
                    "rsi_oversold": (20, 35, 5),
                    "rsi_overbought": (65, 80, 5)
                }
                
                range_result = await optimizer.optimize_single_combination(
                    symbol="BTCUSDT",
                    timeframe="5m",
                    days_back=5,
                    parameter_ranges=custom_ranges
                )
                
                test_result["details"]["parameter_range_validation"] = {
                    "status": "success" if "error" not in range_result else "failed",
                    "custom_ranges_applied": len(custom_ranges),
                    "optimization_successful": range_result.get("optimization_successful", False)
                }
                
                test_result["status"] = "success"
                logger.info("  ✅ 參數優化引擎測試完成")
                
        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)
            logger.error(f"  ❌ 參數優化測試失敗: {e}")
        
        test_result["execution_time"] = (datetime.now() - start_time).total_seconds()
        return test_result
    
    async def test_tradingview_reporter(self) -> Dict[str, Any]:
        """測試TradingView風格報告生成器"""
        logger.info("📊 測試2: TradingView風格報告生成器")
        
        test_result = {
            "test_name": "tradingview_reporter",
            "status": "unknown",
            "details": {},
            "execution_time": 0
        }
        
        start_time = datetime.now()
        
        try:
            async with TradingViewStyleReportGenerator() as reporter:
                # 測試2.1: 基本報告生成
                logger.info("  📈 測試2.1: 基本報告生成")
                basic_report = await reporter.generate_comprehensive_report(
                    symbol="BTCUSDT",
                    timeframe="5m",
                    days_back=7
                )
                
                test_result["details"]["basic_report_generation"] = {
                    "status": "success" if "error" not in basic_report else "failed",
                    "report_sections": len(basic_report) if "error" not in basic_report else 0,
                    "has_strategy_overview": "strategy_overview" in basic_report,
                    "has_performance_metrics": "performance_metrics" in basic_report
                }
                
                # 測試2.2: 多策略報告
                logger.info("  🎯 測試2.2: 多策略報告")
                strategies = ["rsi_strategy", "macd_strategy"]
                multi_strategy_report = await reporter.generate_multi_strategy_report(
                    symbol="BTCUSDT",
                    timeframe="5m",
                    strategies=strategies,
                    days_back=5
                )
                
                test_result["details"]["multi_strategy_report"] = {
                    "status": "success" if "error" not in multi_strategy_report else "failed",
                    "strategies_tested": len(strategies),
                    "comparison_available": "strategy_comparison" in multi_strategy_report
                }
                
                # 測試2.3: 風險分析
                if "error" not in basic_report:
                    logger.info("  ⚠️ 測試2.3: 風險分析驗證")
                    risk_analysis = basic_report.get("risk_analysis", {})
                    
                    test_result["details"]["risk_analysis_validation"] = {
                        "status": "success" if risk_analysis else "failed",
                        "max_drawdown_calculated": "max_drawdown" in risk_analysis,
                        "var_calculated": "value_at_risk" in risk_analysis,
                        "risk_metrics_count": len(risk_analysis)
                    }
                
                test_result["status"] = "success"
                logger.info("  ✅ TradingView報告器測試完成")
                
        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)
            logger.error(f"  ❌ TradingView報告測試失敗: {e}")
        
        test_result["execution_time"] = (datetime.now() - start_time).total_seconds()
        return test_result
    
    async def test_monthly_optimizer_integration(self) -> Dict[str, Any]:
        """測試月度優化器集成"""
        logger.info("🚀 測試3: 月度優化器集成")
        
        test_result = {
            "test_name": "monthly_optimizer_integration", 
            "status": "unknown",
            "details": {},
            "execution_time": 0
        }
        
        start_time = datetime.now()
        
        try:
            async with MonthlyAutoOptimizer() as monthly_optimizer:
                # 測試3.1: 市場條件分析
                logger.info("  📊 測試3.1: 市場條件分析")
                market_condition = await monthly_optimizer.analyze_market_conditions(
                    symbol="BTCUSDT",
                    timeframe="1h", 
                    days_back=7
                )
                
                test_result["details"]["market_condition_analysis"] = {
                    "status": "success",
                    "regime_detected": market_condition.regime.value,
                    "volatility_level": round(market_condition.volatility_level, 3),
                    "confidence": round(market_condition.confidence, 2)
                }
                
                # 測試3.2: 參數適應性調整
                logger.info("  ⚙️ 測試3.2: 參數適應性調整")
                adapted_params = monthly_optimizer.adapt_parameters_for_market_regime(market_condition)
                
                test_result["details"]["parameter_adaptation"] = {
                    "status": "success",
                    "parameters_adjusted": len(adapted_params),
                    "rsi_oversold": adapted_params.get("rsi_oversold"),
                    "confidence_threshold": adapted_params.get("confidence_threshold")
                }
                
                # 測試3.3: 簡化月度優化流程
                logger.info("  🔄 測試3.3: 簡化月度優化流程")
                # 設置更小範圍以加速測試
                monthly_optimizer.schedule_config.target_symbols = ["BTCUSDT"]
                monthly_optimizer.schedule_config.target_timeframes = ["5m"]
                
                monthly_result = await monthly_optimizer.run_monthly_optimization()
                
                test_result["details"]["monthly_optimization_flow"] = {
                    "status": "success" if "error" not in monthly_result else "failed",
                    "market_analysis_completed": bool(monthly_result.get("market_analysis")),
                    "optimization_completed": bool(monthly_result.get("optimization_results")),
                    "recommendations_generated": len(monthly_result.get("recommendations", []))
                }
                
                # 保存月度優化測試結果
                if "error" not in monthly_result:
                    test_output_file = project_root / "monthly_optimization_test_result_temp.json"
                    with open(test_output_file, 'w', encoding='utf-8') as f:
                        json.dump(monthly_result, f, indent=2, ensure_ascii=False, default=str)
                    self.cleanup_files.append(test_output_file)
                
                test_result["status"] = "success"
                logger.info("  ✅ 月度優化器集成測試完成")
                
        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)
            logger.error(f"  ❌ 月度優化器測試失敗: {e}")
            traceback.print_exc()
        
        test_result["execution_time"] = (datetime.now() - start_time).total_seconds()
        return test_result
    
    async def test_end_to_end_workflow(self) -> Dict[str, Any]:
        """測試端到端工作流程"""
        logger.info("🔄 測試4: 端到端工作流程")
        
        test_result = {
            "test_name": "end_to_end_workflow",
            "status": "unknown", 
            "details": {},
            "execution_time": 0
        }
        
        start_time = datetime.now()
        
        try:
            # 模擬完整的月度優化到報告生成流程
            symbol = "BTCUSDT"
            timeframe = "5m"
            days_back = 5
            
            # 步驟1: 參數優化
            logger.info("  🎯 步驟1: 執行參數優化")
            async with IntelligentParameterOptimizer() as optimizer:
                optimization_result = await optimizer.optimize_single_combination(
                    symbol=symbol,
                    timeframe=timeframe,
                    days_back=days_back
                )
            
            # 步驟2: 應用優化參數生成報告
            logger.info("  📊 步驟2: 生成TradingView報告")
            async with TradingViewStyleReportGenerator() as reporter:
                # 使用默認參數生成報告（實際中會使用優化後的參數）
                comprehensive_report = await reporter.generate_comprehensive_report(
                    symbol=symbol,
                    timeframe=timeframe,
                    days_back=days_back
                )
            
            # 步驟3: 市場適應性分析
            logger.info("  📈 步驟3: 市場適應性分析")
            async with MonthlyAutoOptimizer() as monthly_optimizer:
                market_condition = await monthly_optimizer.analyze_market_conditions(
                    symbol=symbol,
                    timeframe="1h",
                    days_back=7
                )
                adapted_params = monthly_optimizer.adapt_parameters_for_market_regime(market_condition)
            
            # 匯總工作流程結果
            test_result["details"]["workflow_steps"] = {
                "parameter_optimization": {
                    "status": "success" if "error" not in optimization_result else "failed",
                    "optimization_successful": optimization_result.get("optimization_successful", False)
                },
                "report_generation": {
                    "status": "success" if "error" not in comprehensive_report else "failed",
                    "report_sections": len(comprehensive_report) if "error" not in comprehensive_report else 0
                },
                "market_adaptation": {
                    "status": "success",
                    "regime_detected": market_condition.regime.value,
                    "parameters_adapted": len(adapted_params)
                }
            }
            
            # 評估整體工作流程
            all_steps_successful = all(
                step["status"] == "success" 
                for step in test_result["details"]["workflow_steps"].values()
            )
            
            test_result["status"] = "success" if all_steps_successful else "partial_success"
            logger.info(f"  ✅ 端到端工作流程測試完成 - 狀態: {test_result['status']}")
            
        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)
            logger.error(f"  ❌ 端到端工作流程測試失敗: {e}")
        
        test_result["execution_time"] = (datetime.now() - start_time).total_seconds()
        return test_result
    
    async def run_comprehensive_phase2_tests(self) -> Dict[str, Any]:
        """運行完整的第二階段測試套件"""
        logger.info("🧪 開始運行完整的第二階段測試套件")
        
        comprehensive_result = {
            "test_suite": "Phase 2 Integration Tests",
            "execution_date": datetime.now().isoformat(),
            "test_results": [],
            "summary": {},
            "overall_status": "unknown"
        }
        
        # 執行所有測試
        test_functions = [
            self.test_parameter_optimization_engine,
            self.test_tradingview_reporter,
            self.test_monthly_optimizer_integration,
            self.test_end_to_end_workflow
        ]
        
        passed_tests = 0
        failed_tests = 0
        
        for test_func in test_functions:
            try:
                result = await test_func()
                self.test_results.append(result)
                
                if result["status"] == "success":
                    passed_tests += 1
                elif result["status"] == "partial_success":
                    passed_tests += 0.5
                    failed_tests += 0.5
                else:
                    failed_tests += 1
                    
            except Exception as e:
                logger.error(f"❌ 測試函數執行失敗: {test_func.__name__} - {e}")
                failed_tests += 1
        
        # 匯總結果
        comprehensive_result["test_results"] = self.test_results
        comprehensive_result["summary"] = {
            "total_tests": len(test_functions),
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": f"{(passed_tests / len(test_functions) * 100):.1f}%",
            "total_execution_time": sum(t.get("execution_time", 0) for t in self.test_results)
        }
        
        # 判斷整體狀態
        if passed_tests == len(test_functions):
            comprehensive_result["overall_status"] = "all_passed"
        elif passed_tests >= len(test_functions) * 0.7:
            comprehensive_result["overall_status"] = "mostly_passed"
        else:
            comprehensive_result["overall_status"] = "needs_attention"
        
        # 保存詳細結果
        output_file = project_root / "phase2_integration_test_results_temp.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_result, f, indent=2, ensure_ascii=False, default=str)
        
        self.cleanup_files.append(output_file)
        
        logger.info(f"🎉 第二階段測試套件完成")
        logger.info(f"📊 通過率: {comprehensive_result['summary']['success_rate']}")
        logger.info(f"📁 詳細結果: {output_file}")
        
        return comprehensive_result
    
    def cleanup_test_files(self):
        """清理測試產生的臨時檔案"""
        logger.info("🧹 清理測試檔案")
        
        for file_path in self.cleanup_files:
            try:
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"  🗑️ 已刪除: {file_path.name}")
            except Exception as e:
                logger.warning(f"  ⚠️ 清理失敗 {file_path.name}: {e}")


async def main():
    """主測試函數"""
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🚀 啟動Trading X第二階段集成測試")
    
    tester = Phase2IntegrationTester()
    
    try:
        # 運行完整測試套件
        results = await tester.run_comprehensive_phase2_tests()
        
        # 輸出測試摘要
        logger.info("\n" + "="*60)
        logger.info("📋 第二階段測試摘要")
        logger.info("="*60)
        logger.info(f"🎯 測試套件: {results['test_suite']}")
        logger.info(f"📊 通過率: {results['summary']['success_rate']}")
        logger.info(f"✅ 通過測試: {results['summary']['passed_tests']}")
        logger.info(f"❌ 失敗測試: {results['summary']['failed_tests']}")
        logger.info(f"⏱️ 總執行時間: {results['summary']['total_execution_time']:.1f}秒")
        logger.info(f"🏆 整體狀態: {results['overall_status']}")
        
        # 輸出各項測試結果
        for test_result in results['test_results']:
            status_emoji = "✅" if test_result['status'] == "success" else "❌" 
            logger.info(f"{status_emoji} {test_result['test_name']}: {test_result['status']}")
        
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ 測試套件執行失敗: {e}")
        traceback.print_exc()
    
    finally:
        # 清理臨時檔案
        tester.cleanup_test_files()
        logger.info("🎉 第二階段集成測試完成")


if __name__ == "__main__":
    asyncio.run(main())
