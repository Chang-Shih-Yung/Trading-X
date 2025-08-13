#!/usr/bin/env python3
"""
🎬 Trading X 第二階段功能演示
展示月度優化、參數調整和TradingView報告的完整流程
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
import sys

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from intelligent_parameter_optimizer import IntelligentParameterOptimizer
from tradingview_style_reporter import TradingViewStyleReportGenerator
from monthly_auto_optimizer import MonthlyAutoOptimizer

logger = logging.getLogger(__name__)

async def trading_x_phase2_demo():
    """Trading X 第二階段完整功能演示"""
    
    print("\n" + "="*60)
    print("🎬 Trading X 第二階段功能演示")
    print("="*60)
    print(f"⏰ 演示時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 演示內容: 智能參數優化 + 市場適應 + TradingView報告")
    print("="*60)
    
    # 第一部分：市場分析與參數適應
    print("\n📊 第一步：市場條件分析與智能參數適應")
    print("-" * 40)
    
    async with MonthlyAutoOptimizer() as monthly_optimizer:
        # 分析當前市場條件
        market_condition = await monthly_optimizer.analyze_market_conditions(
            symbol="BTCUSDT", 
            timeframe="1h", 
            days_back=7
        )
        
        print(f"🏛️ 市場制度: {market_condition.regime.value}")
        print(f"📈 波動率: {market_condition.volatility_level:.3f}")
        print(f"💪 趨勢強度: {market_condition.trend_strength:.2f}")
        print(f"📊 成交量模式: {market_condition.volume_pattern}")
        print(f"🎯 分析信心度: {market_condition.confidence:.2f}")
        
        # 根據市場條件調整參數
        adapted_params = monthly_optimizer.adapt_parameters_for_market_regime(market_condition)
        
        print(f"\n⚙️ 適應性參數調整:")
        for param, value in adapted_params.items():
            print(f"   • {param}: {value}")
    
    # 第二部分：智能參數優化
    print(f"\n🔧 第二步：智能參數優化")
    print("-" * 40)
    
    async with IntelligentParameterOptimizer() as optimizer:
        # 運行簡化的參數優化
        optimization_result = await optimizer.run_comprehensive_optimization(
            target_symbols=["BTCUSDT"],
            target_timeframes=["5m"],
            days_back=7
        )
        
        print(f"📊 優化結果:")
        if "summary" in optimization_result:
            summary = optimization_result["summary"]
            print(f"   • 顯著改進: {summary.get('significant_improvements_count', 0)} 個參數")
            print(f"   • 測試組合: {summary.get('total_combinations_tested', 0)} 組")
            print(f"   • 平均改進: {summary.get('average_improvement', 0):.3f}")
    
    # 第三部分：TradingView風格報告
    print(f"\n📈 第三步：TradingView專業回測報告")
    print("-" * 40)
    
    async with TradingViewStyleReportGenerator() as reporter:
        # 生成完整報告
        report = await reporter.generate_comprehensive_report(
            symbol="BTCUSDT",
            timeframe="5m",
            days_back=7
        )
        
        if "strategy_overview" in report:
            overview = report["strategy_overview"]
            print(f"📊 策略概覽:")
            print(f"   • 總交易次數: {overview.get('total_trades', 0)}")
            print(f"   • 勝率: {overview.get('win_rate', 0):.1f}%")
            print(f"   • 盈虧比: {overview.get('profit_loss_ratio', 0):.2f}")
            print(f"   • 總收益: {overview.get('total_return', 0):.3f}%")
            print(f"   • 最大回撤: {overview.get('max_drawdown', 0):.3f}%")
            print(f"   • 性能評級: {overview.get('performance_rating', 'N/A')}")
        
        if "performance_metrics" in report:
            metrics = report["performance_metrics"]
            print(f"\n🎯 關鍵指標:")
            print(f"   • Sharpe比率: {metrics.get('sharpe_ratio', 0):.2f}")
            print(f"   • 利潤因子: {metrics.get('profit_factor', 0):.2f}")
            print(f"   • 平均交易: {metrics.get('average_trade', 0):.4f}%")
    
    # 演示總結
    print(f"\n🎉 第四步：演示總結")
    print("-" * 40)
    
    print("✅ 已完成功能演示:")
    print("   1. 🏛️ 市場制度識別與分析")
    print("   2. ⚙️ 智能參數自適應調整") 
    print("   3. 🔧 多參數網格搜索優化")
    print("   4. 📊 TradingView風格專業報告")
    
    print(f"\n💡 系統優勢:")
    print("   • 🤖 全自動化月度優化")
    print("   • 📈 真實市場數據驗證")
    print("   • 🎯 精準參數調整")
    print("   • 📊 專業級性能分析")
    
    print(f"\n🚀 下次優化建議時間:")
    async with MonthlyAutoOptimizer() as optimizer:
        next_schedule = optimizer.get_next_optimization_schedule()
        print(f"   📅 {next_schedule}")
    
    print("\n" + "="*60)
    print("🎬 Trading X 第二階段演示完成")
    print("="*60)


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(
        level=logging.WARNING,  # 減少日誌輸出以便演示
        format='%(levelname)s - %(message)s'
    )
    
    # 運行演示
    asyncio.run(trading_x_phase2_demo())
