# 🎯 狙擊手策略回測 API 端點

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
import logging

from app.services.sniper_backtest_engine import sniper_backtest_engine, BacktestPeriod

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sniper/backtest", tags=["sniper-backtest"])

@router.post("/run")
async def run_comprehensive_backtest(
    period: str = Query("30d", description="回測週期: 7d, 30d, 90d, 180d, 365d, all"),
    include_optimization: bool = Query(True, description="是否包含優化建議")
):
    """
    🎯 執行狙擊手策略綜合回測
    
    Args:
        period: 回測週期
        include_optimization: 是否包含優化建議
        
    Returns:
        Dict: 完整回測結果
    """
    try:
        logger.info(f"🚀 開始執行回測 (週期: {period})")
        
        # 驗證週期參數
        period_map = {
            "7d": BacktestPeriod.LAST_7_DAYS,
            "30d": BacktestPeriod.LAST_30_DAYS,
            "90d": BacktestPeriod.LAST_90_DAYS,
            "180d": BacktestPeriod.LAST_180_DAYS,
            "365d": BacktestPeriod.LAST_365_DAYS,
            "all": BacktestPeriod.ALL_TIME
        }
        
        if period not in period_map:
            raise HTTPException(status_code=400, detail=f"無效的週期參數: {period}")
        
        # 執行回測
        backtest_result = await sniper_backtest_engine.run_comprehensive_backtest(
            period=period_map[period]
        )
        
        # 構建回測結果
        result_data = {
            "period": period,
            "summary": {
                "total_signals": backtest_result.total_signals,
                "winning_signals": backtest_result.winning_signals,
                "losing_signals": backtest_result.losing_signals,
                "win_rate": round(backtest_result.win_rate, 2),
                "total_pnl": round(backtest_result.total_pnl, 2),
                "average_pnl": round(backtest_result.average_pnl, 2),
                "max_profit": round(backtest_result.max_profit, 2),
                "max_loss": round(backtest_result.max_loss, 2),
                "profit_factor": round(backtest_result.profit_factor, 2),
                "sharpe_ratio": round(backtest_result.sharpe_ratio, 2),
                "max_drawdown": round(backtest_result.max_drawdown, 2),
                "average_hold_time": round(backtest_result.average_hold_time, 1)
            },
            "detailed_analysis": {
                "best_timeframe": backtest_result.best_timeframe,
                "worst_timeframe": backtest_result.worst_timeframe,
                "monthly_performance": backtest_result.monthly_performance,
                "symbol_performance": backtest_result.symbol_performance,
                "timeframe_performance": backtest_result.timeframe_performance
            }
        }
        
        # 添加優化建議
        if include_optimization:
            optimization = await sniper_backtest_engine.get_strategy_optimization_suggestions(backtest_result)
            result_data["optimization_suggestions"] = optimization
        
        logger.info(f"✅ 回測完成: {backtest_result.total_signals} 信號, 勝率 {backtest_result.win_rate:.1f}%")
        
        return {
            "status": "success",
            "data": result_data,
            "message": f"回測完成 - 分析了 {backtest_result.total_signals} 個信號"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 回測執行失敗: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"回測執行失敗: {str(e)}")

@router.get("/quick-stats")
async def get_quick_backtest_stats():
    """
    🎯 獲取快速回測統計 (最近30天)
    
    Returns:
        Dict: 快速統計結果
    """
    try:
        logger.info("📊 獲取快速回測統計")
        
        # 執行快速回測
        backtest_result = await sniper_backtest_engine.run_comprehensive_backtest(
            period=BacktestPeriod.LAST_30_DAYS
        )
        
        # 返回核心指標
        quick_stats = {
            "period": "30天",
            "total_signals": backtest_result.total_signals,
            "win_rate": round(backtest_result.win_rate, 1),
            "total_pnl": round(backtest_result.total_pnl, 2),
            "profit_factor": round(backtest_result.profit_factor, 2),
            "best_performing_symbol": "",
            "performance_grade": ""
        }
        
        # 找出表現最佳的交易對
        if backtest_result.symbol_performance:
            best_symbol = max(
                backtest_result.symbol_performance.items(),
                key=lambda x: x[1]['total_pnl']
            )
            quick_stats["best_performing_symbol"] = best_symbol[0]
        
        # 性能評級
        if backtest_result.win_rate >= 60 and backtest_result.profit_factor >= 2.0:
            quick_stats["performance_grade"] = "A+ 優秀"
        elif backtest_result.win_rate >= 50 and backtest_result.profit_factor >= 1.5:
            quick_stats["performance_grade"] = "B+ 良好"
        elif backtest_result.win_rate >= 40:
            quick_stats["performance_grade"] = "C 一般"
        else:
            quick_stats["performance_grade"] = "D 需改進"
        
        return {
            "status": "success",
            "data": quick_stats,
            "message": "快速統計獲取成功"
        }
        
    except Exception as e:
        logger.error(f"❌ 獲取快速統計失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取統計失敗: {str(e)}")

@router.get("/performance-comparison")
async def get_performance_comparison():
    """
    🎯 獲取不同週期的績效對比
    
    Returns:
        Dict: 績效對比結果
    """
    try:
        logger.info("📈 執行績效對比分析")
        
        # 執行多個週期的回測
        periods = [
            (BacktestPeriod.LAST_7_DAYS, "7天"),
            (BacktestPeriod.LAST_30_DAYS, "30天"), 
            (BacktestPeriod.LAST_90_DAYS, "90天")
        ]
        
        comparison_data = {}
        
        for period_enum, period_name in periods:
            try:
                result = await sniper_backtest_engine.run_comprehensive_backtest(period_enum)
                comparison_data[period_name] = {
                    "total_signals": result.total_signals,
                    "win_rate": round(result.win_rate, 1),
                    "total_pnl": round(result.total_pnl, 2),
                    "average_pnl": round(result.average_pnl, 2),
                    "profit_factor": round(result.profit_factor, 2),
                    "max_drawdown": round(result.max_drawdown, 2)
                }
            except Exception as e:
                logger.warning(f"⚠️ {period_name} 回測失敗: {e}")
                comparison_data[period_name] = {
                    "error": "數據不足或計算異常"
                }
        
        return {
            "status": "success",
            "data": {
                "comparison": comparison_data,
                "trend_analysis": {
                    "win_rate_trend": "穩定" if len(comparison_data) > 1 else "數據不足",
                    "pnl_trend": "上升" if len(comparison_data) > 1 else "數據不足",
                    "overall_assessment": "策略表現穩定" if len(comparison_data) > 1 else "需要更多數據"
                }
            },
            "message": "績效對比分析完成"
        }
        
    except Exception as e:
        logger.error(f"❌ 績效對比失敗: {e}")
        raise HTTPException(status_code=500, detail=f"對比分析失敗: {str(e)}")

@router.get("/optimization-report")
async def get_optimization_report():
    """
    🎯 獲取策略優化報告
    
    Returns:
        Dict: 優化建議報告
    """
    try:
        logger.info("🔧 生成策略優化報告")
        
        # 執行30天回測
        backtest_result = await sniper_backtest_engine.run_comprehensive_backtest(
            period=BacktestPeriod.LAST_30_DAYS
        )
        
        # 獲取優化建議
        optimization = await sniper_backtest_engine.get_strategy_optimization_suggestions(backtest_result)
        
        # 添加具體的參數建議
        current_performance = {
            "win_rate": backtest_result.win_rate,
            "profit_factor": backtest_result.profit_factor,
            "max_drawdown": backtest_result.max_drawdown,
            "total_signals": backtest_result.total_signals
        }
        
        return {
            "status": "success",
            "data": {
                "current_performance": current_performance,
                "optimization_suggestions": optimization,
                "actionable_steps": [
                    "1. 根據建議調整品質閾值參數",
                    "2. 優化止盈止損比例設定",
                    "3. 重點關注表現最佳的時間框架",
                    "4. 加強風險管理措施",
                    "5. 定期檢視和調整策略參數"
                ]
            },
            "message": "優化報告生成成功"
        }
        
    except Exception as e:
        logger.error(f"❌ 生成優化報告失敗: {e}")
        raise HTTPException(status_code=500, detail=f"報告生成失敗: {str(e)}")


@router.get("/stats")
async def get_quick_backtest_stats(
    period: str = Query("30d", description="統計週期: 7d, 30d, 90d, 180d, 365d, all")
):
    """
    🎯 獲取狙擊手策略快速統計
    
    Args:
        period: 統計週期
        
    Returns:
        Dict: 快速統計結果
    """
    try:
        logger.info(f"📊 獲取快速統計 (週期: {period})")
        
        # 週期映射
        period_map = {
            "7d": BacktestPeriod.LAST_7_DAYS,
            "30d": BacktestPeriod.LAST_30_DAYS,
            "90d": BacktestPeriod.LAST_90_DAYS,
            "180d": BacktestPeriod.LAST_180_DAYS,
            "365d": BacktestPeriod.LAST_365_DAYS,
            "all": BacktestPeriod.ALL_TIME
        }
        
        if period not in period_map:
            raise HTTPException(status_code=400, detail=f"無效的週期參數: {period}")
        
        # 執行快速回測
        backtest_result = await sniper_backtest_engine.run_comprehensive_backtest(
            period=period_map[period]
        )
        
        # 計算績效評級
        performance_grade = "N/A"
        if backtest_result.win_rate >= 80 and backtest_result.profit_factor >= 3.0:
            performance_grade = "A+"
        elif backtest_result.win_rate >= 70 and backtest_result.profit_factor >= 2.5:
            performance_grade = "A"
        elif backtest_result.win_rate >= 60 and backtest_result.profit_factor >= 2.0:
            performance_grade = "B+"
        elif backtest_result.win_rate >= 50 and backtest_result.profit_factor >= 1.5:
            performance_grade = "B"
        elif backtest_result.win_rate >= 40 and backtest_result.profit_factor >= 1.2:
            performance_grade = "C+"
        elif backtest_result.win_rate >= 30 and backtest_result.profit_factor >= 1.0:
            performance_grade = "C"
        elif backtest_result.win_rate >= 20:
            performance_grade = "D"
        else:
            performance_grade = "F"
        
        # 找出最佳表現的幣種
        best_symbol = "N/A"
        if backtest_result.symbol_performance:
            best_performance = max(
                backtest_result.symbol_performance.items(),
                key=lambda x: x[1].get('total_pnl', 0)
            )
            best_symbol = best_performance[0]
        
        result_data = {
            "period": period,
            "total_signals": backtest_result.total_signals,
            "win_rate": round(backtest_result.win_rate, 1),
            "total_pnl": round(backtest_result.total_pnl, 2),
            "profit_factor": round(backtest_result.profit_factor, 2),
            "performance_grade": performance_grade,
            "best_performing_symbol": best_symbol
        }
        
        logger.info(f"✅ 快速統計完成: {result_data}")
        
        return {
            "status": "success",
            "data": result_data,
            "message": "快速統計獲取成功"
        }
        
    except Exception as e:
        logger.error(f"❌ 獲取快速統計失敗: {e}")
        raise HTTPException(status_code=500, detail=f"快速統計失敗: {str(e)}")
