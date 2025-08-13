#!/usr/bin/env python3
"""
🎯 Trading X - 智能參數優化引擎
第二階段：基於回測結果的智能參數調整
自動優化RSI、MACD、成交量等技術指標參數
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import itertools
from dataclasses import dataclass, asdict
import sys

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from historical_data_extension import HistoricalDataExtension
from multiframe_backtest_engine import MultiTimeframeBacktestEngine

logger = logging.getLogger(__name__)

@dataclass
class ParameterRange:
    """參數範圍定義"""
    min_value: float
    max_value: float
    step: float
    current_value: float
    
    def get_test_values(self) -> List[float]:
        """獲取測試值列表"""
        return list(np.arange(self.min_value, self.max_value + self.step, self.step))

@dataclass
class OptimizationResult:
    """優化結果"""
    parameter_name: str
    optimal_value: float
    performance_improvement: float
    confidence_score: float
    test_results: Dict[float, Dict[str, float]]

class IntelligentParameterOptimizer:
    """智能參數優化引擎"""
    
    def __init__(self):
        self.data_extension = None
        self.backtest_engine = None
        
        # 默認參數範圍
        self.parameter_ranges = {
            "rsi_oversold": ParameterRange(20, 35, 5, 30),
            "rsi_overbought": ParameterRange(65, 80, 5, 70),
            "macd_fast": ParameterRange(8, 16, 2, 12),
            "macd_slow": ParameterRange(20, 32, 4, 26),
            "macd_signal": ParameterRange(6, 12, 2, 9),
            "ema_short": ParameterRange(10, 30, 5, 20),
            "ema_long": ParameterRange(40, 60, 5, 50),
            "volume_threshold": ParameterRange(1.2, 2.5, 0.3, 1.5),
            "confidence_threshold": ParameterRange(0.6, 0.9, 0.1, 0.7)
        }
        
        self.optimization_results = {}
        
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
    
    def calculate_rsi_with_params(self, prices: pd.Series, period: int = 14, 
                                oversold: float = 30, overbought: float = 70) -> Tuple[pd.Series, List[Dict]]:
        """使用自定義參數計算RSI和信號"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 生成信號
        signals = []
        for i in range(len(rsi)):
            if pd.isna(rsi.iloc[i]):
                continue
                
            current_rsi = rsi.iloc[i]
            prev_rsi = rsi.iloc[i-1] if i > 0 else current_rsi
            
            if current_rsi < oversold and prev_rsi >= oversold:
                signals.append({
                    'index': i,
                    'type': 'BUY_RSI_OVERSOLD',
                    'rsi_value': current_rsi,
                    'strength': 0.8
                })
            elif current_rsi > overbought and prev_rsi <= overbought:
                signals.append({
                    'index': i,
                    'type': 'SELL_RSI_OVERBOUGHT', 
                    'rsi_value': current_rsi,
                    'strength': 0.8
                })
        
        return rsi, signals
    
    def calculate_macd_with_params(self, prices: pd.Series, fast: int = 12, 
                                 slow: int = 26, signal: int = 9) -> Tuple[Dict[str, pd.Series], List[Dict]]:
        """使用自定義參數計算MACD和信號"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        macd_data = {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
        
        # 生成信號
        signals = []
        for i in range(1, len(macd_line)):
            if pd.isna(macd_line.iloc[i]) or pd.isna(signal_line.iloc[i]):
                continue
                
            current_macd = macd_line.iloc[i]
            current_signal = signal_line.iloc[i]
            prev_macd = macd_line.iloc[i-1]
            prev_signal = signal_line.iloc[i-1]
            
            # 金叉信號
            if current_macd > current_signal and prev_macd <= prev_signal:
                signals.append({
                    'index': i,
                    'type': 'BUY_MACD_GOLDEN_CROSS',
                    'macd_value': current_macd,
                    'strength': 0.7
                })
            # 死叉信號
            elif current_macd < current_signal and prev_macd >= prev_signal:
                signals.append({
                    'index': i,
                    'type': 'SELL_MACD_DEATH_CROSS',
                    'macd_value': current_macd,
                    'strength': 0.7
                })
        
        return macd_data, signals
    
    async def test_parameter_combination(self, symbol: str, timeframe: str, 
                                       parameters: Dict[str, float], 
                                       days_back: int = 7) -> Dict[str, float]:
        """測試特定參數組合的表現"""
        try:
            # 獲取歷史數據
            historical_data = await self.data_extension.fetch_extended_historical_data(
                symbol=symbol, interval=timeframe, days_back=days_back
            )
            
            if not historical_data:
                return {"win_rate": 0.0, "avg_return": 0.0, "sharpe_ratio": 0.0, "total_signals": 0}
            
            df = self.data_extension.convert_to_dataframe(historical_data)
            
            # 使用自定義參數計算指標
            rsi, rsi_signals = self.calculate_rsi_with_params(
                df['close'], 
                oversold=parameters.get('rsi_oversold', 30),
                overbought=parameters.get('rsi_overbought', 70)
            )
            
            macd_data, macd_signals = self.calculate_macd_with_params(
                df['close'],
                fast=int(parameters.get('macd_fast', 12)),
                slow=int(parameters.get('macd_slow', 26)),
                signal=int(parameters.get('macd_signal', 9))
            )
            
            # 合併所有信號
            all_signals = []
            
            # 轉換RSI信號
            for signal in rsi_signals:
                if signal['index'] < len(df):
                    all_signals.append({
                        'timestamp': df.index[signal['index']],
                        'symbol': symbol,
                        'signal_type': signal['type'],
                        'signal_strength': signal['strength'],
                        'confidence': 0.8,
                        'entry_price': df.iloc[signal['index']]['close']
                    })
            
            # 轉換MACD信號
            for signal in macd_signals:
                if signal['index'] < len(df):
                    all_signals.append({
                        'timestamp': df.index[signal['index']],
                        'symbol': symbol,
                        'signal_type': signal['type'],
                        'signal_strength': signal['strength'],
                        'confidence': 0.7,
                        'entry_price': df.iloc[signal['index']]['close']
                    })
            
            # 按置信度過濾信號
            confidence_threshold = parameters.get('confidence_threshold', 0.7)
            filtered_signals = [s for s in all_signals if s['confidence'] >= confidence_threshold]
            
            # 計算績效
            if not filtered_signals:
                return {"win_rate": 0.0, "avg_return": 0.0, "sharpe_ratio": 0.0, "total_signals": 0}
            
            # 簡化的績效計算
            df_temp = df.copy()
            df_temp['symbol'] = symbol
            performance = self.backtest_engine.calculate_signal_performance(
                filtered_signals, df_temp, holding_period_minutes=60
            )
            
            return {
                "win_rate": performance.get('win_rate', 0.0),
                "avg_return": performance.get('avg_return', 0.0),
                "sharpe_ratio": performance.get('sharpe_ratio', 0.0),
                "total_signals": performance.get('executable_signals', 0)
            }
            
        except Exception as e:
            logger.error(f"❌ 測試參數組合失敗: {e}")
            return {"win_rate": 0.0, "avg_return": 0.0, "sharpe_ratio": 0.0, "total_signals": 0}
    
    async def optimize_single_parameter(self, parameter_name: str, symbol: str = "BTCUSDT", 
                                      timeframe: str = "1m", days_back: int = 7) -> OptimizationResult:
        """優化單一參數"""
        logger.info(f"🔧 開始優化參數: {parameter_name}")
        
        if parameter_name not in self.parameter_ranges:
            raise ValueError(f"未知參數: {parameter_name}")
        
        param_range = self.parameter_ranges[parameter_name]
        test_values = param_range.get_test_values()
        
        logger.info(f"📊 測試 {len(test_values)} 個值: {test_values}")
        
        # 基準參數（使用當前值）
        base_parameters = {name: range_obj.current_value 
                          for name, range_obj in self.parameter_ranges.items()}
        
        test_results = {}
        best_performance = -999999
        best_value = param_range.current_value
        
        # 測試每個參數值
        for test_value in test_values:
            test_parameters = base_parameters.copy()
            test_parameters[parameter_name] = test_value
            
            logger.info(f"🧪 測試 {parameter_name} = {test_value}")
            
            performance = await self.test_parameter_combination(
                symbol, timeframe, test_parameters, days_back
            )
            
            test_results[test_value] = performance
            
            # 計算綜合分數 (勝率權重0.7，收益率權重0.3)
            score = (performance['win_rate'] * 0.7 + 
                    max(0, performance['avg_return']) * 30 * 0.3)
            
            if score > best_performance:
                best_performance = score
                best_value = test_value
            
            logger.info(f"   勝率: {performance['win_rate']:.1%}, "
                       f"收益: {performance['avg_return']:.3%}, "
                       f"信號數: {performance['total_signals']}")
            
            # 避免API限制
            await asyncio.sleep(0.1)
        
        # 計算改進程度
        base_performance = test_results.get(param_range.current_value, {"win_rate": 0, "avg_return": 0})
        best_result = test_results.get(best_value, {"win_rate": 0, "avg_return": 0})
        
        base_score = (base_performance['win_rate'] * 0.7 + 
                     max(0, base_performance['avg_return']) * 30 * 0.3)
        best_score = (best_result['win_rate'] * 0.7 + 
                     max(0, best_result['avg_return']) * 30 * 0.3)
        
        improvement = best_score - base_score
        
        # 計算置信度（基於測試結果的一致性）
        scores = []
        for value, perf in test_results.items():
            score = (perf['win_rate'] * 0.7 + max(0, perf['avg_return']) * 30 * 0.3)
            scores.append(score)
        
        confidence_score = 1.0 - (np.std(scores) / (np.mean(scores) + 0.001))
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        result = OptimizationResult(
            parameter_name=parameter_name,
            optimal_value=best_value,
            performance_improvement=improvement,
            confidence_score=confidence_score,
            test_results=test_results
        )
        
        logger.info(f"✅ {parameter_name} 優化完成: {param_range.current_value} → {best_value} "
                   f"(改進: {improvement:.3f}, 信心: {confidence_score:.1%})")
        
        return result
    
    async def run_comprehensive_optimization(self, 
                                           target_symbols: List[str] = None,
                                           target_timeframes: List[str] = None,
                                           days_back: int = 7) -> Dict[str, Any]:
        """運行全面的參數優化"""
        logger.info("🚀 開始全面參數優化")
        
        target_symbols = target_symbols or ["BTCUSDT", "ETHUSDT"]
        target_timeframes = target_timeframes or ["1m", "5m"]
        
        optimization_report = {
            "optimization_date": datetime.now().isoformat(),
            "target_symbols": target_symbols,
            "target_timeframes": target_timeframes,
            "parameter_results": {},
            "recommendations": [],
            "summary": {}
        }
        
        # 優化每個參數
        all_improvements = []
        significant_improvements = []
        
        for param_name in self.parameter_ranges.keys():
            logger.info(f"🔧 優化參數: {param_name}")
            
            # 在多個標的和時間框架上測試
            param_results = {}
            total_improvement = 0
            test_count = 0
            
            for symbol in target_symbols:
                for timeframe in target_timeframes:
                    try:
                        result = await self.optimize_single_parameter(
                            param_name, symbol, timeframe, days_back
                        )
                        
                        key = f"{symbol}_{timeframe}"
                        param_results[key] = asdict(result)
                        
                        total_improvement += result.performance_improvement
                        test_count += 1
                        
                    except Exception as e:
                        logger.error(f"❌ 優化 {param_name} 在 {symbol} {timeframe} 失敗: {e}")
                        continue
            
            if test_count > 0:
                avg_improvement = total_improvement / test_count
                all_improvements.append(avg_improvement)
                
                optimization_report["parameter_results"][param_name] = {
                    "average_improvement": avg_improvement,
                    "test_count": test_count,
                    "detailed_results": param_results
                }
                
                # 顯著改進判斷
                if avg_improvement > 0.05:  # 5% 改進
                    significant_improvements.append({
                        "parameter": param_name,
                        "improvement": avg_improvement,
                        "recommended_action": "立即應用"
                    })
                elif avg_improvement > 0.02:  # 2% 改進
                    significant_improvements.append({
                        "parameter": param_name,
                        "improvement": avg_improvement,
                        "recommended_action": "謹慎測試"
                    })
        
        # 生成建議
        if significant_improvements:
            # 按改進程度排序
            significant_improvements.sort(key=lambda x: x["improvement"], reverse=True)
            
            for imp in significant_improvements[:3]:  # 前3個最重要的改進
                optimization_report["recommendations"].append(
                    f"🎯 優先調整 {imp['parameter']}: "
                    f"預期改進 {imp['improvement']:.1%} ({imp['recommended_action']})"
                )
        else:
            optimization_report["recommendations"].append(
                "📊 當前參數已較為優化，建議保持現有設定並持續監控"
            )
        
        # 生成摘要
        optimization_report["summary"] = {
            "total_parameters_tested": len(self.parameter_ranges),
            "average_improvement": np.mean(all_improvements) if all_improvements else 0,
            "significant_improvements_count": len(significant_improvements),
            "optimization_quality": "excellent" if len(significant_improvements) >= 3 else 
                                  "good" if len(significant_improvements) >= 1 else "stable"
        }
        
        logger.info(f"🎉 全面優化完成: {len(significant_improvements)} 個顯著改進")
        return optimization_report
    
    def generate_optimized_config(self, optimization_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成優化後的配置檔案"""
        optimized_config = {
            "config_version": "optimized_v1.0",
            "optimization_date": datetime.now().isoformat(),
            "optimized_parameters": {},
            "performance_expectations": {},
            "implementation_notes": []
        }
        
        # 提取最佳參數值
        for param_name, param_result in optimization_results["parameter_results"].items():
            if param_result["average_improvement"] > 0.01:  # 1%以上改進才考慮
                # 找到最常見的最佳值
                best_values = []
                for detailed_result in param_result["detailed_results"].values():
                    best_values.append(detailed_result["optimal_value"])
                
                if best_values:
                    # 使用中位數作為推薦值
                    recommended_value = np.median(best_values)
                    
                    optimized_config["optimized_parameters"][param_name] = {
                        "recommended_value": float(recommended_value),
                        "current_value": self.parameter_ranges[param_name].current_value,
                        "expected_improvement": param_result["average_improvement"],
                        "confidence": "high" if param_result["average_improvement"] > 0.05 else "medium"
                    }
        
        # 預期績效
        total_improvement = optimization_results["summary"]["average_improvement"]
        optimized_config["performance_expectations"] = {
            "expected_win_rate_improvement": f"+{total_improvement * 70:.1f}%",
            "expected_return_improvement": f"+{total_improvement * 30:.2f}%",
            "confidence_level": optimization_results["summary"]["optimization_quality"]
        }
        
        # 實施建議
        optimized_config["implementation_notes"] = [
            "🔧 建議分階段實施參數調整，每次調整1-2個參數",
            "📊 實施後持續監控7天，確認效果符合預期",
            "⚠️ 如發現性能下降，立即回滾到原始參數",
            "📈 每月重新運行優化，適應市場變化"
        ]
        
        return optimized_config


async def test_parameter_optimization():
    """測試參數優化功能"""
    logger.info("🧪 開始測試智能參數優化引擎")
    
    async with IntelligentParameterOptimizer() as optimizer:
        # 運行小規模優化測試
        results = await optimizer.run_comprehensive_optimization(
            target_symbols=["BTCUSDT"],
            target_timeframes=["1m"],
            days_back=3
        )
        
        # 輸出結果摘要
        summary = results["summary"]
        logger.info(f"📊 優化摘要:")
        logger.info(f"   - 測試參數數: {summary['total_parameters_tested']}")
        logger.info(f"   - 平均改進: {summary['average_improvement']:.3%}")
        logger.info(f"   - 顯著改進數: {summary['significant_improvements_count']}")
        logger.info(f"   - 優化品質: {summary['optimization_quality']}")
        
        # 顯示建議
        logger.info(f"💡 優化建議:")
        for i, rec in enumerate(results["recommendations"], 1):
            logger.info(f"   {i}. {rec}")
        
        # 生成優化配置
        optimized_config = optimizer.generate_optimized_config(results)
        logger.info(f"🎯 生成優化配置: {len(optimized_config['optimized_parameters'])} 個參數調整")
        
        # 保存結果到臨時檔案
        output_file = Path(__file__).parent / "parameter_optimization_results_temp.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            final_results = {
                "optimization_results": results,
                "optimized_config": optimized_config
            }
            json.dump(final_results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📁 結果已保存到: {output_file}")
        return final_results


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 運行測試
    asyncio.run(test_parameter_optimization())
