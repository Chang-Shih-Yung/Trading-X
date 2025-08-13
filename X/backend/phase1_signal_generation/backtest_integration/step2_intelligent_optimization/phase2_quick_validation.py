#!/usr/bin/env python3
"""
🧪 Trading X - 第二階段快速驗證測試
驗證月度優化、市場適應和TradingView報告的核心功能
"""

import asyncio
import logging
import json
from typing import Dict, Any
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

async def quick_phase2_validation():
    """快速驗證第二階段核心功能"""
    logger.info("🚀 開始Trading X第二階段快速驗證")
    
    validation_results = {
        "test_date": datetime.now().isoformat(),
        "tests": {},
        "summary": {}
    }
    
    # 測試1: 智能參數優化基本功能
    logger.info("🔧 測試1: 智能參數優化器")
    try:
        async with IntelligentParameterOptimizer() as optimizer:
            # 簡化測試：只測試一個參數
            result = await optimizer.run_comprehensive_optimization(
                target_symbols=["BTCUSDT"],
                target_timeframes=["5m"], 
                days_back=5
            )
            
            validation_results["tests"]["parameter_optimizer"] = {
                "status": "success" if "error" not in result else "failed",
                "symbols_tested": len(result.get("results", {})),
                "improvements_found": result.get("summary", {}).get("significant_improvements_count", 0)
            }
            logger.info(f"✅ 參數優化測試完成: {validation_results['tests']['parameter_optimizer']['status']}")
            
    except Exception as e:
        validation_results["tests"]["parameter_optimizer"] = {
            "status": "failed",
            "error": str(e)
        }
        logger.error(f"❌ 參數優化測試失敗: {e}")
    
    # 測試2: TradingView報告生成器
    logger.info("📊 測試2: TradingView報告生成器")
    try:
        async with TradingViewStyleReportGenerator() as reporter:
            report = await reporter.generate_comprehensive_report(
                symbol="BTCUSDT",
                timeframe="5m",
                days_back=5
            )
            
            validation_results["tests"]["tradingview_reporter"] = {
                "status": "success" if "error" not in report else "failed",
                "report_sections": len(report) if "error" not in report else 0,
                "has_performance_metrics": "performance_metrics" in report
            }
            logger.info(f"✅ TradingView報告測試完成: {validation_results['tests']['tradingview_reporter']['status']}")
            
    except Exception as e:
        validation_results["tests"]["tradingview_reporter"] = {
            "status": "failed", 
            "error": str(e)
        }
        logger.error(f"❌ TradingView報告測試失敗: {e}")
    
    # 測試3: 月度優化器核心功能
    logger.info("🚀 測試3: 月度優化器")
    try:
        async with MonthlyAutoOptimizer() as monthly_optimizer:
            # 測試市場分析
            market_condition = await monthly_optimizer.analyze_market_conditions(
                symbol="BTCUSDT",
                timeframe="1h",
                days_back=5
            )
            
            # 測試參數適應
            adapted_params = monthly_optimizer.adapt_parameters_for_market_regime(market_condition)
            
            validation_results["tests"]["monthly_optimizer"] = {
                "status": "success",
                "market_regime": market_condition.regime.value,
                "volatility_level": round(market_condition.volatility_level, 3),
                "parameters_adapted": len(adapted_params),
                "confidence": round(market_condition.confidence, 2)
            }
            logger.info(f"✅ 月度優化器測試完成: {validation_results['tests']['monthly_optimizer']['status']}")
            
    except Exception as e:
        validation_results["tests"]["monthly_optimizer"] = {
            "status": "failed",
            "error": str(e)
        }
        logger.error(f"❌ 月度優化器測試失敗: {e}")
    
    # 計算測試摘要
    total_tests = len(validation_results["tests"])
    passed_tests = sum(1 for test in validation_results["tests"].values() if test["status"] == "success")
    
    validation_results["summary"] = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": f"{(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%",
        "overall_status": "success" if passed_tests == total_tests else "partial_success" if passed_tests > 0 else "failed"
    }
    
    # 保存結果
    output_file = project_root / "phase2_quick_validation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2, ensure_ascii=False, default=str)
    
    # 輸出測試結果
    logger.info("\n" + "="*50)
    logger.info("📋 第二階段快速驗證結果")
    logger.info("="*50)
    logger.info(f"🎯 總測試數: {validation_results['summary']['total_tests']}")
    logger.info(f"✅ 通過測試: {validation_results['summary']['passed_tests']}")
    logger.info(f"❌ 失敗測試: {validation_results['summary']['failed_tests']}")
    logger.info(f"📊 成功率: {validation_results['summary']['success_rate']}")
    logger.info(f"🏆 整體狀態: {validation_results['summary']['overall_status']}")
    
    for test_name, test_result in validation_results['tests'].items():
        status_emoji = "✅" if test_result['status'] == "success" else "❌"
        logger.info(f"{status_emoji} {test_name}: {test_result['status']}")
    
    logger.info(f"📁 詳細結果: {output_file}")
    logger.info("="*50)
    
    # 清理臨時檔案
    try:
        temp_files = list(project_root.glob("*temp*.json"))
        for temp_file in temp_files:
            temp_file.unlink()
            logger.info(f"🗑️ 已清理: {temp_file.name}")
    except Exception as e:
        logger.warning(f"⚠️ 清理臨時檔案失敗: {e}")
    
    return validation_results

if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 運行快速驗證
    asyncio.run(quick_phase2_validation())
