#!/usr/bin/env python3
"""
🎯 Trading X - TradingView風格報告生成器
第二階段：專業級回測分析報告
模擬TradingView策略測試器的報告格式和指標
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import math
from dataclasses import dataclass, asdict
import sys

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from historical_data_extension import HistoricalDataExtension
from multiframe_backtest_engine import MultiTimeframeBacktestEngine

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """TradingView風格的績效指標"""
    # 基本績效
    net_profit: float
    net_profit_percent: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # 收益指標
    gross_profit: float
    gross_loss: float
    profit_factor: float
    max_runup: float
    max_drawdown: float
    
    # 平均值
    avg_trade: float
    avg_winning_trade: float
    avg_losing_trade: float
    avg_bars_in_trade: float
    
    # 連續性
    max_consecutive_wins: int
    max_consecutive_losses: int
    
    # 風險指標
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    # 期望值
    expectancy: float
    sqn: float  # System Quality Number

@dataclass
class TradeRecord:
    """交易記錄"""
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: float
    trade_type: str  # 'long' or 'short'
    profit_loss: float
    profit_loss_percent: float
    bars_in_trade: int
    signal_type: str
    mae: float  # Maximum Adverse Excursion
    mfe: float  # Maximum Favorable Excursion

class TradingViewStyleReportGenerator:
    """TradingView風格報告生成器"""
    
    def __init__(self):
        self.data_extension = None
        self.backtest_engine = None
        
    async def __aenter__(self):
        """異步初始化"""
        self.data_extension = await HistoricalDataExtension().__aenter__()
        self.backtest_engine = await MultiTimeframeBacktestEngine().__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """清理資源"""
        if self.data_extension:
            await self.data_extension.__aexit__(exc_type, exc_val, exc_tb)
        if self.backtest_engine:
            await self.backtest_engine.__aexit__(exc_type, exc_val, exc_tb)
    
    def calculate_mae_mfe(self, entry_price: float, exit_price: float, 
                         high_prices: List[float], low_prices: List[float], 
                         trade_type: str) -> Tuple[float, float]:
        """計算最大不利偏移(MAE)和最大有利偏移(MFE)"""
        if trade_type.lower() == 'long':
            # 多頭交易
            mae = min([(low - entry_price) / entry_price for low in low_prices])
            mfe = max([(high - entry_price) / entry_price for high in high_prices])
        else:
            # 空頭交易
            mae = max([(high - entry_price) / entry_price for high in high_prices])
            mfe = min([(low - entry_price) / entry_price for low in low_prices])
        
        return mae, mfe
    
    async def generate_detailed_trade_records(self, symbol: str, timeframe: str, 
                                            days_back: int = 30) -> List[TradeRecord]:
        """生成詳細的交易記錄"""
        logger.info(f"📊 生成 {symbol} {timeframe} 詳細交易記錄")
        
        # 獲取歷史數據
        historical_data = await self.data_extension.fetch_extended_historical_data(
            symbol=symbol, interval=timeframe, days_back=days_back
        )
        
        if not historical_data:
            return []
        
        df = self.data_extension.convert_to_dataframe(historical_data)
        df['symbol'] = symbol
        
        # 生成交易信號
        signals = self.backtest_engine.generate_signals_from_indicators(df)
        
        trade_records = []
        
        # 假設固定持有期間
        holding_periods = {
            "1m": 60,    # 1小時
            "5m": 12,    # 1小時  
            "15m": 4,    # 1小時
            "1h": 24,    # 1天
            "4h": 6      # 1天
        }
        
        holding_period = holding_periods.get(timeframe, 60)
        
        for signal in signals:
            try:
                entry_time = signal['timestamp']
                entry_price = signal['entry_price']
                
                # 找到退出時間和價格
                entry_idx = df.index.get_loc(entry_time)
                exit_idx = min(entry_idx + holding_period, len(df) - 1)
                
                if exit_idx >= len(df):
                    continue
                
                exit_time = df.index[exit_idx]
                exit_price = df.iloc[exit_idx]['close']
                
                # 確定交易類型
                trade_type = 'long' if 'BUY' in signal['signal_type'] else 'short'
                
                # 計算盈虧
                if trade_type == 'long':
                    profit_loss = exit_price - entry_price
                    profit_loss_percent = (exit_price - entry_price) / entry_price
                else:
                    profit_loss = entry_price - exit_price
                    profit_loss_percent = (entry_price - exit_price) / entry_price
                
                # 獲取持有期間的高低點
                period_data = df.iloc[entry_idx:exit_idx+1]
                high_prices = period_data['high'].tolist()
                low_prices = period_data['low'].tolist()
                
                # 計算MAE和MFE
                mae, mfe = self.calculate_mae_mfe(
                    entry_price, exit_price, high_prices, low_prices, trade_type
                )
                
                trade_record = TradeRecord(
                    entry_time=entry_time,
                    exit_time=exit_time,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    quantity=1.0,  # 假設固定數量
                    trade_type=trade_type,
                    profit_loss=profit_loss,
                    profit_loss_percent=profit_loss_percent,
                    bars_in_trade=exit_idx - entry_idx,
                    signal_type=signal['signal_type'],
                    mae=mae,
                    mfe=mfe
                )
                
                trade_records.append(trade_record)
                
            except Exception as e:
                logger.warning(f"⚠️ 處理信號失敗: {e}")
                continue
        
        logger.info(f"✅ 生成 {len(trade_records)} 筆交易記錄")
        return trade_records
    
    def calculate_performance_metrics(self, trade_records: List[TradeRecord], 
                                    initial_capital: float = 10000) -> PerformanceMetrics:
        """計算TradingView風格的績效指標"""
        if not trade_records:
            return PerformanceMetrics(
                net_profit=0, net_profit_percent=0, total_trades=0,
                winning_trades=0, losing_trades=0, win_rate=0,
                gross_profit=0, gross_loss=0, profit_factor=0,
                max_runup=0, max_drawdown=0,
                avg_trade=0, avg_winning_trade=0, avg_losing_trade=0,
                avg_bars_in_trade=0, max_consecutive_wins=0, max_consecutive_losses=0,
                sharpe_ratio=0, sortino_ratio=0, calmar_ratio=0,
                expectancy=0, sqn=0
            )
        
        # 基本統計
        profits = [trade.profit_loss for trade in trade_records]
        winning_trades = [trade for trade in trade_records if trade.profit_loss > 0]
        losing_trades = [trade for trade in trade_records if trade.profit_loss < 0]
        
        total_trades = len(trade_records)
        winning_count = len(winning_trades)
        losing_count = len(losing_trades)
        win_rate = winning_count / total_trades if total_trades > 0 else 0
        
        # 盈虧計算
        gross_profit = sum([trade.profit_loss for trade in winning_trades])
        gross_loss = abs(sum([trade.profit_loss for trade in losing_trades]))
        net_profit = gross_profit - gross_loss
        net_profit_percent = (net_profit / initial_capital) * 100
        
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # 平均值
        avg_trade = net_profit / total_trades if total_trades > 0 else 0
        avg_winning_trade = gross_profit / winning_count if winning_count > 0 else 0
        avg_losing_trade = -gross_loss / losing_count if losing_count > 0 else 0
        avg_bars_in_trade = sum([trade.bars_in_trade for trade in trade_records]) / total_trades if total_trades > 0 else 0
        
        # 計算資金曲線和回撤
        capital_curve = [initial_capital]
        for trade in trade_records:
            capital_curve.append(capital_curve[-1] + trade.profit_loss)
        
        # 最大回撤和最大上升
        peak = initial_capital
        max_drawdown = 0
        max_runup = 0
        
        for capital in capital_curve[1:]:
            if capital > peak:
                max_runup = max(max_runup, capital - peak)
                peak = capital
            else:
                drawdown = peak - capital
                max_drawdown = max(max_drawdown, drawdown)
        
        max_drawdown_percent = (max_drawdown / initial_capital) * 100
        max_runup_percent = (max_runup / initial_capital) * 100
        
        # 連續勝負次數
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        
        for trade in trade_records:
            if trade.profit_loss > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            else:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        
        # 風險指標
        returns = [trade.profit_loss / initial_capital for trade in trade_records]
        
        if len(returns) > 1:
            returns_std = np.std(returns)
            avg_return = np.mean(returns)
            
            # Sharpe Ratio (假設無風險利率為0)
            sharpe_ratio = avg_return / returns_std if returns_std > 0 else 0
            
            # Sortino Ratio (只考慮下行風險)
            negative_returns = [r for r in returns if r < 0]
            downside_std = np.std(negative_returns) if negative_returns else 0
            sortino_ratio = avg_return / downside_std if downside_std > 0 else 0
            
            # Calmar Ratio
            annual_return = avg_return * 252 * 24 * 60  # 假設1分鐘數據
            calmar_ratio = annual_return / (max_drawdown_percent / 100) if max_drawdown_percent > 0 else 0
        else:
            sharpe_ratio = sortino_ratio = calmar_ratio = 0
        
        # 期望值和SQN
        expectancy = avg_trade
        
        # System Quality Number (Van Tharp)
        if len(profits) > 1:
            sqn = (np.mean(profits) / np.std(profits)) * math.sqrt(len(profits))
        else:
            sqn = 0
        
        return PerformanceMetrics(
            net_profit=net_profit,
            net_profit_percent=net_profit_percent,
            total_trades=total_trades,
            winning_trades=winning_count,
            losing_trades=losing_count,
            win_rate=win_rate,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            profit_factor=profit_factor,
            max_runup=max_runup_percent,
            max_drawdown=max_drawdown_percent,
            avg_trade=avg_trade,
            avg_winning_trade=avg_winning_trade,
            avg_losing_trade=avg_losing_trade,
            avg_bars_in_trade=avg_bars_in_trade,
            max_consecutive_wins=max_consecutive_wins,
            max_consecutive_losses=max_consecutive_losses,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            expectancy=expectancy,
            sqn=sqn
        )
    
    def generate_tradingview_style_report(self, symbol: str, timeframe: str, 
                                        trade_records: List[TradeRecord],
                                        performance_metrics: PerformanceMetrics) -> Dict[str, Any]:
        """生成TradingView風格的完整報告"""
        
        # 性能分類
        def classify_performance(metrics: PerformanceMetrics) -> str:
            score = 0
            
            # 勝率評分 (0-30分)
            if metrics.win_rate >= 0.7:
                score += 30
            elif metrics.win_rate >= 0.6:
                score += 25
            elif metrics.win_rate >= 0.5:
                score += 20
            elif metrics.win_rate >= 0.4:
                score += 15
            else:
                score += 10
            
            # 盈虧比評分 (0-25分)
            if metrics.profit_factor >= 2.0:
                score += 25
            elif metrics.profit_factor >= 1.5:
                score += 20
            elif metrics.profit_factor >= 1.2:
                score += 15
            elif metrics.profit_factor >= 1.0:
                score += 10
            else:
                score += 5
            
            # Sharpe Ratio評分 (0-20分)
            if metrics.sharpe_ratio >= 1.5:
                score += 20
            elif metrics.sharpe_ratio >= 1.0:
                score += 15
            elif metrics.sharpe_ratio >= 0.5:
                score += 10
            else:
                score += 5
            
            # 最大回撤評分 (0-25分)
            if metrics.max_drawdown <= 5:
                score += 25
            elif metrics.max_drawdown <= 10:
                score += 20
            elif metrics.max_drawdown <= 15:
                score += 15
            elif metrics.max_drawdown <= 25:
                score += 10
            else:
                score += 5
            
            if score >= 85:
                return "🏆 Excellent"
            elif score >= 70:
                return "✅ Good"
            elif score >= 55:
                return "⚡ Average"
            elif score >= 40:
                return "⚠️ Below Average"
            else:
                return "❌ Poor"
        
        performance_rating = classify_performance(performance_metrics)
        
        # 生成月度統計
        monthly_stats = {}
        if trade_records:
            df_trades = pd.DataFrame([asdict(trade) for trade in trade_records])
            df_trades['entry_time'] = pd.to_datetime(df_trades['entry_time'])
            df_trades['month'] = df_trades['entry_time'].dt.to_period('M')
            
            for month, group in df_trades.groupby('month'):
                monthly_profit = group['profit_loss'].sum()
                monthly_trades = len(group)
                monthly_wins = len(group[group['profit_loss'] > 0])
                monthly_win_rate = monthly_wins / monthly_trades if monthly_trades > 0 else 0
                
                monthly_stats[str(month)] = {
                    "trades": monthly_trades,
                    "profit_loss": monthly_profit,
                    "win_rate": monthly_win_rate,
                    "avg_trade": monthly_profit / monthly_trades if monthly_trades > 0 else 0
                }
        
        report = {
            "strategy_overview": {
                "strategy_name": f"Trading-X Multi-Indicator Strategy",
                "symbol": symbol,
                "timeframe": timeframe,
                "backtest_period": {
                    "start": trade_records[0].entry_time.isoformat() if trade_records else None,
                    "end": trade_records[-1].exit_time.isoformat() if trade_records else None,
                    "total_days": (trade_records[-1].exit_time - trade_records[0].entry_time).days if trade_records else 0
                },
                "performance_rating": performance_rating
            },
            
            "performance_summary": {
                "net_profit": f"${performance_metrics.net_profit:,.2f}",
                "net_profit_percent": f"{performance_metrics.net_profit_percent:+.2f}%",
                "total_trades": performance_metrics.total_trades,
                "win_rate": f"{performance_metrics.win_rate:.1%}",
                "profit_factor": f"{performance_metrics.profit_factor:.2f}",
                "max_drawdown": f"{performance_metrics.max_drawdown:.2f}%",
                "sharpe_ratio": f"{performance_metrics.sharpe_ratio:.2f}",
                "expectancy": f"${performance_metrics.expectancy:.2f}"
            },
            
            "detailed_statistics": asdict(performance_metrics),
            
            "trade_distribution": {
                "winning_trades": performance_metrics.winning_trades,
                "losing_trades": performance_metrics.losing_trades,
                "largest_winning_trade": max([trade.profit_loss for trade in trade_records], default=0),
                "largest_losing_trade": min([trade.profit_loss for trade in trade_records], default=0),
                "avg_winning_trade": f"${performance_metrics.avg_winning_trade:.2f}",
                "avg_losing_trade": f"${performance_metrics.avg_losing_trade:.2f}",
                "max_consecutive_wins": performance_metrics.max_consecutive_wins,
                "max_consecutive_losses": performance_metrics.max_consecutive_losses
            },
            
            "monthly_breakdown": monthly_stats,
            
            "risk_analysis": {
                "max_drawdown_details": {
                    "percentage": f"{performance_metrics.max_drawdown:.2f}%",
                    "rating": "Low Risk" if performance_metrics.max_drawdown < 10 else 
                             "Medium Risk" if performance_metrics.max_drawdown < 20 else "High Risk"
                },
                "volatility_metrics": {
                    "sharpe_ratio": performance_metrics.sharpe_ratio,
                    "sortino_ratio": performance_metrics.sortino_ratio,
                    "calmar_ratio": performance_metrics.calmar_ratio
                },
                "system_quality": {
                    "sqn_score": performance_metrics.sqn,
                    "sqn_rating": "Excellent" if performance_metrics.sqn > 3.0 else
                                 "Good" if performance_metrics.sqn > 2.0 else
                                 "Average" if performance_metrics.sqn > 1.0 else "Poor"
                }
            },
            
            "recommendations": self._generate_strategy_recommendations(performance_metrics),
            
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_version": "tradingview_style_v1.0",
                "total_trades_analyzed": len(trade_records)
            }
        }
        
        return report
    
    def _generate_strategy_recommendations(self, metrics: PerformanceMetrics) -> List[str]:
        """生成策略改進建議"""
        recommendations = []
        
        # 勝率建議
        if metrics.win_rate < 0.5:
            recommendations.append("⚠️ 勝率偏低，建議調整進場條件或增加過濾器")
        elif metrics.win_rate > 0.8:
            recommendations.append("⚡ 勝率過高，可能信號頻率過低，考慮放寬進場條件")
        
        # 盈虧比建議
        if metrics.profit_factor < 1.2:
            recommendations.append("📈 盈虧比偏低，建議優化止盈止損策略")
        elif metrics.profit_factor > 3.0:
            recommendations.append("🎯 優秀的盈虧比，可考慮增加倉位或信號頻率")
        
        # 回撤建議
        if metrics.max_drawdown > 20:
            recommendations.append("🛡️ 最大回撤過大，強烈建議加強風險控制")
        elif metrics.max_drawdown < 5:
            recommendations.append("💎 回撤控制優秀，可考慮適度增加風險暴露")
        
        # Sharpe比率建議
        if metrics.sharpe_ratio < 0.5:
            recommendations.append("📊 夏普比率偏低，建議平衡收益與風險")
        elif metrics.sharpe_ratio > 2.0:
            recommendations.append("🏆 優秀的風險調整收益，策略表現卓越")
        
        # 交易頻率建議
        if metrics.total_trades < 20:
            recommendations.append("🔄 交易次數偏少，統計意義有限，建議增加樣本數")
        elif metrics.total_trades > 500:
            recommendations.append("⚡ 交易頻率很高，注意交易成本的影響")
        
        # 連續虧損建議
        if metrics.max_consecutive_losses > 10:
            recommendations.append("🚨 連續虧損次數過多，建議增加停損機制")
        
        if not recommendations:
            recommendations.append("✨ 策略表現均衡，建議持續監控並定期優化")
        
        return recommendations
    
    async def generate_comprehensive_report(self, symbol: str = "BTCUSDT", 
                                          timeframe: str = "1m", 
                                          days_back: int = 7) -> Dict[str, Any]:
        """生成完整的TradingView風格報告"""
        logger.info(f"📊 生成 {symbol} {timeframe} 完整報告")
        
        # 生成交易記錄
        trade_records = await self.generate_detailed_trade_records(symbol, timeframe, days_back)
        
        if not trade_records:
            logger.warning("⚠️ 無交易記錄，無法生成報告")
            return {"error": "No trade records generated"}
        
        # 計算績效指標
        performance_metrics = self.calculate_performance_metrics(trade_records)
        
        # 生成完整報告
        report = self.generate_tradingview_style_report(symbol, timeframe, trade_records, performance_metrics)
        
        logger.info(f"✅ 報告生成完成: {len(trade_records)} 筆交易，"
                   f"勝率 {performance_metrics.win_rate:.1%}，"
                   f"盈虧比 {performance_metrics.profit_factor:.2f}")
        
        return report


async def test_tradingview_report():
    """測試TradingView風格報告生成"""
    logger.info("🧪 開始測試TradingView風格報告生成器")
    
    async with TradingViewStyleReportGenerator() as report_gen:
        # 生成測試報告
        report = await report_gen.generate_comprehensive_report(
            symbol="BTCUSDT",
            timeframe="5m", 
            days_back=7
        )
        
        if "error" in report:
            logger.error(f"❌ 報告生成失敗: {report['error']}")
            return None
        
        # 輸出報告摘要
        overview = report["strategy_overview"]
        performance = report["performance_summary"]
        
        logger.info(f"📊 策略概覽:")
        logger.info(f"   - 交易對: {overview['symbol']} {overview['timeframe']}")
        logger.info(f"   - 回測期間: {overview['backtest_period']['total_days']} 天")
        logger.info(f"   - 表現評級: {overview['performance_rating']}")
        
        logger.info(f"📈 績效摘要:")
        logger.info(f"   - 淨利潤: {performance['net_profit']}")
        logger.info(f"   - 勝率: {performance['win_rate']}")
        logger.info(f"   - 盈虧比: {performance['profit_factor']}")
        logger.info(f"   - 最大回撤: {performance['max_drawdown']}")
        logger.info(f"   - 夏普比率: {performance['sharpe_ratio']}")
        
        # 顯示建議
        logger.info(f"💡 策略建議:")
        for i, rec in enumerate(report["recommendations"][:3], 1):
            logger.info(f"   {i}. {rec}")
        
        # 保存報告到臨時檔案
        output_file = Path(__file__).parent / "tradingview_report_temp.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📁 報告已保存到: {output_file}")
        return report


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 運行測試
    asyncio.run(test_tradingview_report())
