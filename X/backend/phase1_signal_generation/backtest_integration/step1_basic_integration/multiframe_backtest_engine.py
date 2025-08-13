#!/usr/bin/env python3
"""
🎯 Trading X - 多時間框架回測引擎
整合現有Phase5驗證機制，擴展支援多時間框架回測
保持原有JSON Schema，純功能擴展
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from historical_data_extension import HistoricalDataExtension

logger = logging.getLogger(__name__)

class MultiTimeframeBacktestEngine:
    """多時間框架回測引擎 - 基於真實歷史數據"""
    
    def __init__(self):
        self.timeframes = ["1m", "5m", "15m", "1h", "4h"]
        self.test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT"]
        self.backtest_results = {}
        self.data_extension = None
        
    async def __aenter__(self):
        self.data_extension = await HistoricalDataExtension().__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.data_extension:
            await self.data_extension.__aexit__(exc_type, exc_val, exc_tb)
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """計算RSI指標"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """計算MACD指標"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_ema(self, prices: pd.Series, period: int = 20) -> pd.Series:
        """計算EMA指標"""
        return prices.ewm(span=period).mean()
    
    def generate_signals_from_indicators(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        基於技術指標生成交易信號 (模擬Phase1A邏輯)
        使用真實的技術分析邏輯
        """
        signals = []
        
        if len(df) < 50:  # 數據不足
            return signals
        
        # 計算技術指標
        df['rsi'] = self.calculate_rsi(df['close'])
        macd_data = self.calculate_macd(df['close'])
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_histogram'] = macd_data['histogram']
        df['ema_20'] = self.calculate_ema(df['close'], 20)
        df['ema_50'] = self.calculate_ema(df['close'], 50)
        
        # 計算成交量指標
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        # 信號生成邏輯 (模擬Phase1A的真實邏輯)
        for i in range(50, len(df)):
            current_time = df.index[i]
            current_data = df.iloc[i]
            prev_data = df.iloc[i-1]
            
            signal_strength = 0.0
            signal_type = None
            signal_confidence = 0.0
            
            # RSI超買超賣信號
            if current_data['rsi'] < 30 and prev_data['rsi'] >= 30:
                signal_type = "BUY_RSI_OVERSOLD"
                signal_strength = 0.7
                signal_confidence = 0.8
            elif current_data['rsi'] > 70 and prev_data['rsi'] <= 70:
                signal_type = "SELL_RSI_OVERBOUGHT"
                signal_strength = 0.7
                signal_confidence = 0.8
            
            # MACD金叉死叉信號
            elif (current_data['macd'] > current_data['macd_signal'] and 
                  prev_data['macd'] <= prev_data['macd_signal']):
                signal_type = "BUY_MACD_GOLDEN_CROSS"
                signal_strength = 0.6
                signal_confidence = 0.75
            elif (current_data['macd'] < current_data['macd_signal'] and 
                  prev_data['macd'] >= prev_data['macd_signal']):
                signal_type = "SELL_MACD_DEATH_CROSS"
                signal_strength = 0.6
                signal_confidence = 0.75
            
            # EMA趨勢信號
            elif (current_data['ema_20'] > current_data['ema_50'] and 
                  current_data['close'] > current_data['ema_20'] and
                  current_data['volume_ratio'] > 1.5):
                signal_type = "BUY_EMA_TREND"
                signal_strength = 0.5
                signal_confidence = 0.65
            elif (current_data['ema_20'] < current_data['ema_50'] and 
                  current_data['close'] < current_data['ema_20'] and
                  current_data['volume_ratio'] > 1.5):
                signal_type = "SELL_EMA_TREND"
                signal_strength = 0.5
                signal_confidence = 0.65
            
            # 如果有信號，記錄
            if signal_type:
                signal = {
                    'timestamp': current_time,
                    'symbol': current_data.get('symbol', 'UNKNOWN'),
                    'signal_type': signal_type,
                    'signal_strength': signal_strength,
                    'confidence': signal_confidence,
                    'entry_price': current_data['close'],
                    'rsi': current_data['rsi'],
                    'macd': current_data['macd'],
                    'volume_ratio': current_data['volume_ratio'],
                    'market_data': {
                        'open': current_data['open'],
                        'high': current_data['high'],
                        'low': current_data['low'],
                        'close': current_data['close'],
                        'volume': current_data['volume']
                    }
                }
                signals.append(signal)
        
        return signals
    
    def calculate_signal_performance(self, signals: List[Dict[str, Any]], df: pd.DataFrame, 
                                   holding_period_minutes: int = 60) -> Dict[str, Any]:
        """
        計算信號績效 (模擬真實交易結果)
        
        Args:
            signals: 生成的信號列表
            df: 價格數據DataFrame
            holding_period_minutes: 持有時間(分鐘)
            
        Returns:
            績效統計
        """
        if not signals:
            return {
                'total_signals': 0,
                'win_rate': 0.0,
                'avg_return': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0
            }
        
        results = []
        df_indexed = df.set_index('timestamp') if 'timestamp' in df.columns else df
        
        for signal in signals:
            signal_time = signal['timestamp']
            entry_price = signal['entry_price']
            
            # 計算退出時間
            exit_time = signal_time + timedelta(minutes=holding_period_minutes)
            
            # 查找退出價格
            exit_data = df_indexed[df_indexed.index >= exit_time]
            if len(exit_data) == 0:
                continue  # 沒有足夠的未來數據
            
            exit_price = exit_data.iloc[0]['close']
            
            # 計算收益
            if 'BUY' in signal['signal_type']:
                return_pct = (exit_price - entry_price) / entry_price
            else:  # SELL信號
                return_pct = (entry_price - exit_price) / entry_price
            
            results.append({
                'signal_time': signal_time,
                'signal_type': signal['signal_type'],
                'entry_price': entry_price,
                'exit_price': exit_price,
                'return_pct': return_pct,
                'profitable': return_pct > 0
            })
        
        if not results:
            return {
                'total_signals': len(signals),
                'executable_signals': 0,
                'win_rate': 0.0,
                'avg_return': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0
            }
        
        # 計算績效指標
        returns = [r['return_pct'] for r in results]
        profitable_trades = [r for r in results if r['profitable']]
        
        win_rate = len(profitable_trades) / len(results) if results else 0
        avg_return = np.mean(returns) if returns else 0
        return_std = np.std(returns) if len(returns) > 1 else 0
        sharpe_ratio = avg_return / return_std if return_std > 0 else 0
        
        # 計算最大回撤
        cumulative_returns = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = cumulative_returns - running_max
        max_drawdown = np.min(drawdowns) if len(drawdowns) > 0 else 0
        
        return {
            'total_signals': len(signals),
            'executable_signals': len(results),
            'win_rate': win_rate,
            'avg_return': avg_return,
            'return_std': return_std,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'best_trade': max(returns) if returns else 0,
            'worst_trade': min(returns) if returns else 0,
            'profit_factor': sum([r for r in returns if r > 0]) / abs(sum([r for r in returns if r < 0])) if any(r < 0 for r in returns) else float('inf')
        }
    
    async def run_single_backtest(self, symbol: str, timeframe: str, days_back: int = 7) -> Dict[str, Any]:
        """運行單一交易對和時間框架的回測"""
        logger.info(f"🔄 開始回測: {symbol} {timeframe} (過去{days_back}天)")
        
        try:
            # 獲取歷史數據
            historical_data = await self.data_extension.fetch_extended_historical_data(
                symbol=symbol,
                interval=timeframe,
                days_back=days_back
            )
            
            if not historical_data:
                logger.warning(f"⚠️ 無法獲取 {symbol} {timeframe} 歷史數據")
                return None
            
            # 轉換為DataFrame
            df = self.data_extension.convert_to_dataframe(historical_data)
            df['symbol'] = symbol  # 添加交易對信息
            
            # 驗證數據品質
            quality_report = await self.data_extension.validate_data_quality(historical_data)
            
            # 生成交易信號
            signals = self.generate_signals_from_indicators(df)
            
            # 計算績效
            performance = self.calculate_signal_performance(signals, df)
            
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'backtest_period': {
                    'start': df.index.min().isoformat(),
                    'end': df.index.max().isoformat(),
                    'days': days_back,
                    'total_candles': len(df)
                },
                'data_quality': quality_report,
                'signals_generated': len(signals),
                'performance': performance,
                'signal_types_breakdown': {},
                'timestamp': datetime.now().isoformat()
            }
            
            # 統計不同信號類型
            signal_types = {}
            for signal in signals:
                signal_type = signal['signal_type']
                if signal_type not in signal_types:
                    signal_types[signal_type] = 0
                signal_types[signal_type] += 1
            result['signal_types_breakdown'] = signal_types
            
            logger.info(f"✅ {symbol} {timeframe} 回測完成: {len(signals)}信號, 勝率{performance['win_rate']:.1%}")
            return result
            
        except Exception as e:
            logger.error(f"❌ {symbol} {timeframe} 回測失敗: {e}")
            return None
    
    async def run_comprehensive_backtest(self, days_back: int = 7) -> Dict[str, Any]:
        """運行全面的多時間框架回測"""
        logger.info(f"🚀 開始全面回測: {len(self.test_symbols)}個交易對 × {len(self.timeframes)}個時間框架")
        
        all_results = {}
        summary_stats = {
            'total_backtests': 0,
            'successful_backtests': 0,
            'failed_backtests': 0,
            'overall_performance': {},
            'best_performers': [],
            'worst_performers': []
        }
        
        # 運行所有組合的回測
        for symbol in self.test_symbols:
            all_results[symbol] = {}
            
            for timeframe in self.timeframes:
                result = await self.run_single_backtest(symbol, timeframe, days_back)
                
                summary_stats['total_backtests'] += 1
                
                if result:
                    all_results[symbol][timeframe] = result
                    summary_stats['successful_backtests'] += 1
                    
                    # 記錄表現最好和最差的
                    performance_score = result['performance']['win_rate'] * result['performance']['avg_return']
                    summary_stats['best_performers'].append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'score': performance_score,
                        'win_rate': result['performance']['win_rate'],
                        'avg_return': result['performance']['avg_return']
                    })
                    
                else:
                    all_results[symbol][timeframe] = None
                    summary_stats['failed_backtests'] += 1
                
                # 避免API限制
                await asyncio.sleep(0.1)
        
        # 排序最佳表現者
        summary_stats['best_performers'].sort(key=lambda x: x['score'], reverse=True)
        summary_stats['worst_performers'] = summary_stats['best_performers'][-5:]
        summary_stats['best_performers'] = summary_stats['best_performers'][:5]
        
        # 計算整體統計
        all_performances = []
        for symbol_results in all_results.values():
            for timeframe_result in symbol_results.values():
                if timeframe_result:
                    all_performances.append(timeframe_result['performance'])
        
        if all_performances:
            summary_stats['overall_performance'] = {
                'avg_win_rate': np.mean([p['win_rate'] for p in all_performances]),
                'avg_return': np.mean([p['avg_return'] for p in all_performances]),
                'avg_sharpe_ratio': np.mean([p['sharpe_ratio'] for p in all_performances]),
                'total_signals': sum([p['total_signals'] for p in all_performances])
            }
        
        # 構建最終結果
        final_result = {
            'backtest_summary': summary_stats,
            'detailed_results': all_results,
            'metadata': {
                'backtest_date': datetime.now().isoformat(),
                'days_back': days_back,
                'symbols_tested': self.test_symbols,
                'timeframes_tested': self.timeframes
            }
        }
        
        logger.info(f"🎉 全面回測完成: {summary_stats['successful_backtests']}/{summary_stats['total_backtests']} 成功")
        return final_result


async def test_multiframe_backtest():
    """測試多時間框架回測引擎"""
    logger.info("🧪 開始測試多時間框架回測引擎")
    
    async with MultiTimeframeBacktestEngine() as backtest_engine:
        # 運行全面回測 (使用較短的測試期間)
        results = await backtest_engine.run_comprehensive_backtest(days_back=3)
        
        # 輸出結果摘要
        summary = results['backtest_summary']
        logger.info(f"📊 回測摘要:")
        logger.info(f"   - 總測試數: {summary['total_backtests']}")
        logger.info(f"   - 成功數: {summary['successful_backtests']}")
        logger.info(f"   - 失敗數: {summary['failed_backtests']}")
        
        if summary['overall_performance']:
            perf = summary['overall_performance']
            logger.info(f"📈 整體表現:")
            logger.info(f"   - 平均勝率: {perf['avg_win_rate']:.1%}")
            logger.info(f"   - 平均收益: {perf['avg_return']:.3%}")
            logger.info(f"   - 總信號數: {perf['total_signals']}")
        
        # 顯示最佳表現者
        logger.info(f"🏆 最佳表現:")
        for i, performer in enumerate(summary['best_performers'][:3]):
            logger.info(f"   {i+1}. {performer['symbol']} {performer['timeframe']}: "
                       f"勝率{performer['win_rate']:.1%}, 收益{performer['avg_return']:.3%}")
        
        # 保存詳細結果到檔案 (臨時)
        output_file = Path(__file__).parent / "backtest_results_temp.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📁 詳細結果已保存到: {output_file}")
        
        # 返回結果以供後續處理
        return results


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 運行測試
    asyncio.run(test_multiframe_backtest())
