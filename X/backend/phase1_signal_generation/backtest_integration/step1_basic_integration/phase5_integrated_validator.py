#!/usr/bin/env python3
"""
🎯 Trading X - Phase5整合回測驗證器
整合現有Phase5系統與多時間框架回測
保持原有架構，純擴展功能
"""

import asyncio
import logging
import json
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

# 設置logger
logger = logging.getLogger(__name__)

# 添加項目路徑 - 使用絕對路徑確保正確導入
current_file = Path(__file__).resolve()
# 從當前檔案位置往上找到backend目錄
backend_root = None
for parent in current_file.parents:
    if parent.name == 'backend':
        backend_root = parent
        break

if backend_root:
    sys.path.insert(0, str(backend_root))
    logger.info(f"✅ Backend路徑添加成功: {backend_root}")
else:
    # 備用：相對路徑計算 (step1 -> backtest_integration -> phase1 -> backend)
    backend_root = current_file.parent.parent.parent.parent
    sys.path.insert(0, str(backend_root))
    logger.warning(f"⚠️ 使用備用路徑: {backend_root}")

from historical_data_extension import HistoricalDataExtension
from multiframe_backtest_engine import MultiTimeframeBacktestEngine

try:
    # 嘗試導入現有的Phase5模組 - 修正導入路徑
    from phase5_backtest_validation.auto_backtest_validator import AutoBacktestValidator
    logger.info("✅ Phase5模組導入成功")
except ImportError as e:
    logger.warning(f"⚠️ Phase5模組導入失敗: {e}")
    logger.warning("將使用簡化版本運行")
    AutoBacktestValidator = None

class Phase5IntegratedBacktestValidator:
    """Phase5整合回測驗證器 - 結合現有Phase5與多時間框架回測"""
    
    def __init__(self):
        self.phase5_validator = None
        self.multiframe_engine = None
        self.validation_results = {}
        
        # 整合配置 (保持與現有Phase5兼容)
        self.config = {
            "validation_window_hours": 48,
            "win_rate_threshold": 0.70,
            "profit_loss_threshold": 1.5,
            "monthly_optimization": True,
            "timeframes": ["1m", "5m", "15m", "1h"],
            "test_symbols": ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        }
    
    async def __aenter__(self):
        """異步初始化"""
        try:
            # 初始化Phase5驗證器 (如果可用)
            if AutoBacktestValidator:
                self.phase5_validator = AutoBacktestValidator()
                logger.info("✅ Phase5驗證器初始化成功")
            else:
                logger.warning("⚠️ Phase5驗證器不可用，使用簡化模式")
            
            # 初始化多時間框架引擎
            self.multiframe_engine = await MultiTimeframeBacktestEngine().__aenter__()
            logger.info("✅ 多時間框架引擎初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 初始化失敗: {e}")
            raise
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """清理資源"""
        if self.multiframe_engine:
            await self.multiframe_engine.__aexit__(exc_type, exc_val, exc_tb)
    
    def simulate_phase5_validation(self, backtest_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        模擬Phase5驗證邏輯 (當Phase5不可用時)
        基於真實的驗證標準
        """
        validation_summary = {
            "validation_status": "completed",
            "validation_timestamp": datetime.now().isoformat(),
            "threshold_analysis": {},
            "performance_classification": {},
            "recommendations": []
        }
        
        # 分析每個時間框架的表現
        for symbol, timeframe_results in backtest_results['detailed_results'].items():
            for timeframe, result in timeframe_results.items():
                if not result:
                    continue
                
                perf = result['performance']
                
                # 應用Phase5驗證標準
                meets_win_rate = perf['win_rate'] >= self.config['win_rate_threshold']
                meets_profit_loss = perf.get('profit_factor', 0) >= self.config['profit_loss_threshold']
                
                # 分類績效
                if meets_win_rate and meets_profit_loss:
                    classification = "excellent"
                elif meets_win_rate or meets_profit_loss:
                    classification = "good"
                elif perf['win_rate'] > 0.5:
                    classification = "marginal"
                else:
                    classification = "poor"
                
                validation_key = f"{symbol}_{timeframe}"
                validation_summary["performance_classification"][validation_key] = {
                    "classification": classification,
                    "win_rate": perf['win_rate'],
                    "profit_factor": perf.get('profit_factor', 0),
                    "meets_threshold": meets_win_rate and meets_profit_loss,
                    "signal_count": perf['total_signals']
                }
                
                # 生成建議
                if classification == "poor":
                    validation_summary["recommendations"].append(
                        f"⚠️ {symbol} {timeframe}: 表現不佳，建議調整參數或暫停此組合"
                    )
                elif classification == "excellent":
                    validation_summary["recommendations"].append(
                        f"🏆 {symbol} {timeframe}: 表現優秀，可增加信號權重"
                    )
        
        return validation_summary
    
    async def run_integrated_validation(self, days_back: int = 7) -> Dict[str, Any]:
        """運行整合式回測驗證"""
        logger.info("🚀 開始整合式回測驗證")
        
        validation_results = {
            "validation_type": "integrated_phase5_multiframe",
            "start_time": datetime.now().isoformat(),
            "config": self.config,
            "results": {}
        }
        
        try:
            # 第一步: 運行多時間框架回測
            logger.info("📊 步驟1: 運行多時間框架回測")
            backtest_results = await self.multiframe_engine.run_comprehensive_backtest(days_back)
            
            validation_results["results"]["multiframe_backtest"] = backtest_results
            
            # 第二步: Phase5風格驗證
            logger.info("🔍 步驟2: 應用Phase5驗證標準")
            
            if self.phase5_validator:
                # 使用真實Phase5驗證器
                try:
                    # 這裡需要根據實際Phase5 API調整
                    phase5_validation = await self._integrate_with_phase5(backtest_results)
                    validation_results["results"]["phase5_validation"] = phase5_validation
                    logger.info("✅ Phase5驗證完成")
                except Exception as e:
                    logger.warning(f"⚠️ Phase5驗證失敗，使用模擬模式: {e}")
                    phase5_validation = self.simulate_phase5_validation(backtest_results)
                    validation_results["results"]["phase5_validation"] = phase5_validation
            else:
                # 模擬Phase5驗證
                phase5_validation = self.simulate_phase5_validation(backtest_results)
                validation_results["results"]["phase5_validation"] = phase5_validation
                logger.info("✅ 模擬Phase5驗證完成")
            
            # 第三步: 生成整合建議
            logger.info("💡 步驟3: 生成整合建議")
            integration_recommendations = self._generate_integration_recommendations(
                backtest_results, phase5_validation
            )
            validation_results["results"]["integration_recommendations"] = integration_recommendations
            
            # 第四步: 參數調整建議
            logger.info("⚙️ 步驟4: 生成參數調整建議")
            parameter_adjustments = self._suggest_parameter_adjustments(backtest_results)
            validation_results["results"]["parameter_adjustments"] = parameter_adjustments
            
            validation_results["end_time"] = datetime.now().isoformat()
            validation_results["status"] = "success"
            
            logger.info("🎉 整合式回測驗證完成")
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ 整合驗證失敗: {e}")
            validation_results["status"] = "failed"
            validation_results["error"] = str(e)
            validation_results["end_time"] = datetime.now().isoformat()
            return validation_results
    
    async def _integrate_with_phase5(self, backtest_results: Dict[str, Any]) -> Dict[str, Any]:
        """與真實Phase5系統整合 (佔位函數)"""
        # 這個函數需要根據實際Phase5 API實現
        # 目前返回模擬結果
        return self.simulate_phase5_validation(backtest_results)
    
    def _generate_integration_recommendations(self, 
                                            backtest_results: Dict[str, Any],
                                            phase5_validation: Dict[str, Any]) -> List[str]:
        """生成整合建議"""
        recommendations = []
        
        # 分析整體表現
        summary = backtest_results['backtest_summary']
        overall_perf = summary.get('overall_performance', {})
        
        if overall_perf.get('avg_win_rate', 0) < 0.6:
            recommendations.append("🔧 整體勝率偏低，建議調整信號生成閾值")
        
        if overall_perf.get('avg_return', 0) < 0.01:
            recommendations.append("📈 平均收益偏低，建議優化止盈止損策略")
        
        # 分析最佳表現者
        best_performers = summary.get('best_performers', [])
        if best_performers:
            best = best_performers[0]
            recommendations.append(
                f"🏆 建議重點關注 {best['symbol']} {best['timeframe']}，表現最佳"
            )
        
        # 分析Phase5驗證結果
        excellent_count = sum(1 for perf in phase5_validation['performance_classification'].values() 
                            if perf['classification'] == 'excellent')
        total_count = len(phase5_validation['performance_classification'])
        
        if excellent_count / total_count > 0.5 if total_count > 0 else False:
            recommendations.append("✨ 多數組合表現優秀，可考慮增加整體信號頻率")
        else:
            recommendations.append("⚠️ 優秀組合比例較低，建議加強參數優化")
        
        return recommendations
    
    def _suggest_parameter_adjustments(self, backtest_results: Dict[str, Any]) -> Dict[str, Any]:
        """建議參數調整"""
        adjustments = {
            "rsi_parameters": {},
            "macd_parameters": {},
            "volume_parameters": {},
            "confidence_thresholds": {}
        }
        
        # 基於回測結果分析最佳參數
        all_results = []
        for symbol_results in backtest_results['detailed_results'].values():
            for timeframe_result in symbol_results.values():
                if timeframe_result:
                    all_results.append(timeframe_result)
        
        if not all_results:
            return adjustments
        
        # 計算平均表現
        avg_win_rate = sum(r['performance']['win_rate'] for r in all_results) / len(all_results)
        avg_return = sum(r['performance']['avg_return'] for r in all_results) / len(all_results)
        
        # RSI參數建議
        if avg_win_rate < 0.6:
            adjustments["rsi_parameters"] = {
                "oversold_threshold": 25,  # 更嚴格
                "overbought_threshold": 75,  # 更嚴格
                "reasoning": "勝率偏低，建議使用更嚴格的RSI閾值"
            }
        else:
            adjustments["rsi_parameters"] = {
                "oversold_threshold": 35,  # 更寬鬆
                "overbought_threshold": 65,  # 更寬鬆
                "reasoning": "勝率良好，可使用稍寬鬆的RSI閾值增加信號頻率"
            }
        
        # MACD參數建議
        if avg_return < 0.005:  # 0.5%
            adjustments["macd_parameters"] = {
                "fast_period": 10,  # 更敏感
                "slow_period": 24,  # 更敏感
                "signal_period": 8,  # 更敏感
                "reasoning": "收益偏低，建議使用更敏感的MACD參數"
            }
        else:
            adjustments["macd_parameters"] = {
                "fast_period": 14,  # 較穩定
                "slow_period": 28,  # 較穩定
                "signal_period": 10,  # 較穩定
                "reasoning": "收益良好，建議使用較穩定的MACD參數"
            }
        
        # 信心閾值建議
        high_conf_signals = 0
        total_signals = 0
        for result in all_results:
            total_signals += result['performance']['total_signals']
            # 這裡需要更詳細的信號分析
        
        if total_signals > 0 and avg_win_rate > 0.7:
            adjustments["confidence_thresholds"] = {
                "minimum_confidence": 0.6,  # 可稍微降低
                "reasoning": "高勝率表現，可適當降低信心閾值增加信號量"
            }
        else:
            adjustments["confidence_thresholds"] = {
                "minimum_confidence": 0.8,  # 提高要求
                "reasoning": "表現需改善，提高信心閾值確保信號品質"
            }
        
        return adjustments
    
    def generate_monthly_optimization_plan(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成月度優化計劃"""
        optimization_plan = {
            "plan_date": datetime.now().isoformat(),
            "next_optimization_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "priority_actions": [],
            "parameter_schedule": {},
            "monitoring_targets": {}
        }
        
        if 'parameter_adjustments' in validation_results.get('results', {}):
            adjustments = validation_results['results']['parameter_adjustments']
            
            # 優先級動作
            optimization_plan["priority_actions"] = [
                "應用新的RSI參數設定",
                "調整MACD敏感度",
                "更新信心閾值",
                "監控調整後的績效表現"
            ]
            
            # 參數調整時程
            optimization_plan["parameter_schedule"] = {
                "week_1": "實施RSI參數調整",
                "week_2": "實施MACD參數調整", 
                "week_3": "實施信心閾值調整",
                "week_4": "評估整體效果並準備下月計劃"
            }
            
            # 監控目標
            current_perf = validation_results.get('results', {}).get('multiframe_backtest', {}).get('backtest_summary', {}).get('overall_performance', {})
            target_win_rate = min(0.85, current_perf.get('avg_win_rate', 0.6) + 0.05)
            target_return = current_perf.get('avg_return', 0.01) + 0.002
            
            optimization_plan["monitoring_targets"] = {
                "target_win_rate": target_win_rate,
                "target_avg_return": target_return,
                "min_signal_count": 50,  # 每月最少信號數
                "max_drawdown_limit": 0.15
            }
        
        return optimization_plan


async def test_phase5_integration():
    """測試Phase5整合回測驗證器"""
    logger.info("🧪 開始測試Phase5整合回測驗證器")
    
    async with Phase5IntegratedBacktestValidator() as validator:
        # 運行整合驗證 (使用較短的測試期間)
        results = await validator.run_integrated_validation(days_back=3)
        
        # 輸出結果摘要
        logger.info(f"📊 驗證狀態: {results['status']}")
        
        if results['status'] == 'success':
            # 多時間框架回測結果
            backtest = results['results']['multiframe_backtest']['backtest_summary']
            logger.info(f"📈 回測結果: {backtest['successful_backtests']}/{backtest['total_backtests']} 成功")
            
            # Phase5驗證結果
            phase5 = results['results']['phase5_validation']
            excellent_count = sum(1 for p in phase5['performance_classification'].values() 
                                if p['classification'] == 'excellent')
            total_count = len(phase5['performance_classification'])
            logger.info(f"🏆 優秀組合: {excellent_count}/{total_count}")
            
            # 建議
            recommendations = results['results']['integration_recommendations']
            logger.info(f"💡 建議數量: {len(recommendations)}")
            for i, rec in enumerate(recommendations[:3]):
                logger.info(f"   {i+1}. {rec}")
            
            # 生成月度優化計劃
            optimization_plan = validator.generate_monthly_optimization_plan(results)
            logger.info(f"📅 月度優化計劃已生成")
            
            # 保存結果到臨時檔案
            output_file = Path(__file__).parent / "phase5_integration_results_temp.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                # 包含優化計劃
                results['monthly_optimization_plan'] = optimization_plan
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"📁 詳細結果已保存到: {output_file}")
        
        else:
            logger.error(f"❌ 驗證失敗: {results.get('error', '未知錯誤')}")
        
        return results


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 運行測試
    asyncio.run(test_phase5_integration())
