#!/usr/bin/env python3
"""
🎯 Trading X - 每週自動參數優化器
自動調整 Phase1A 參數以達到 70% 勝率目標
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import numpy as np
from dataclasses import dataclass
import itertools

@dataclass
class OptimizationTarget:
    """優化目標"""
    win_rate: float = 0.70      # 70% 勝率目標
    profit_loss_ratio: float = 1.5   # 1.5 盈虧比目標
    sharpe_ratio: float = 1.0   # 1.0 夏普比率目標

@dataclass
class ParameterSet:
    """參數組合"""
    confidence_threshold: float
    price_change_threshold: float
    volume_change_threshold: float
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'confidence_threshold': self.confidence_threshold,
            'price_change_threshold': self.price_change_threshold,
            'volume_change_threshold': self.volume_change_threshold
        }

class WeeklyParameterOptimizer:
    """每週參數自動優化器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.optimization_target = OptimizationTarget()
        self.current_best_params = None
        self.optimization_history = []
        
        # 參數搜尋空間
        self.parameter_space = {
            'confidence_threshold': np.arange(0.65, 0.86, 0.02),
            'price_change_threshold': np.arange(0.0005, 0.0021, 0.0001),
            'volume_change_threshold': np.arange(1.0, 2.6, 0.1)
        }
    
    async def run_weekly_optimization(self) -> Dict[str, Any]:
        """執行每週參數優化"""
        self.logger.info("🚀 開始每週參數優化...")
        
        start_time = datetime.now()
        
        try:
            # 1. 獲取當前性能基準
            current_performance = await self._get_current_performance()
            
            # 2. 判斷是否需要優化
            if self._meets_targets(current_performance):
                self.logger.info("✅ 當前參數已達標，跳過優化")
                return {
                    'status': 'skip',
                    'reason': '已達到目標性能',
                    'current_performance': current_performance
                }
            
            # 3. 執行智能參數搜尋
            best_params, best_performance = await self._intelligent_parameter_search()
            
            # 4. 驗證最佳參數
            validated_performance = await self._test_parameter_set(best_params)
            
            # 5. 更新 Phase1A 參數
            if self._should_update_parameters(validated_performance, current_performance):
                await self._update_phase1a_parameters(best_params)
                
                optimization_result = {
                    'status': 'success',
                    'optimization_time': (datetime.now() - start_time).total_seconds(),
                    'old_parameters': self.current_best_params.to_dict() if self.current_best_params else None,
                    'new_parameters': best_params.to_dict(),
                    'old_performance': current_performance,
                    'new_performance': validated_performance,
                    'improvement': self._calculate_improvement(current_performance, validated_performance)
                }
                
                self.current_best_params = best_params
                self.optimization_history.append(optimization_result)
                
                self.logger.info(f"✅ 參數優化完成！勝率提升至 {validated_performance['win_rate']:.2%}")
                return optimization_result
            
            else:
                return {
                    'status': 'no_improvement',
                    'reason': '新參數未能顯著改善性能',
                    'tested_performance': validated_performance
                }
                
        except Exception as e:
            self.logger.error(f"❌ 參數優化失敗: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _intelligent_parameter_search(self) -> Tuple[ParameterSet, Dict[str, float]]:
        """智能參數搜尋算法"""
        self.logger.info("🔍 開始智能參數搜尋...")
        
        # 使用改進的網格搜尋 + 貝葉斯優化
        best_score = -float('inf')
        best_params = None
        best_performance = None
        
        # 第一階段：粗糙網格搜尋
        coarse_grid = self._generate_coarse_grid()
        self.logger.info(f"📊 粗糙搜尋: {len(coarse_grid)} 個參數組合")
        
        for i, params in enumerate(coarse_grid):
            if i % 10 == 0:
                self.logger.info(f"   進度: {i}/{len(coarse_grid)} ({i/len(coarse_grid)*100:.1f}%)")
            
            performance = await self._test_parameter_set(params)
            score = self._calculate_composite_score(performance)
            
            if score > best_score:
                best_score = score
                best_params = params
                best_performance = performance
        
        # 第二階段：在最佳區域精細搜尋
        if best_params:
            self.logger.info("🎯 在最佳區域進行精細搜尋...")
            fine_tuned_params, fine_tuned_performance = await self._fine_tune_parameters(best_params)
            
            if self._calculate_composite_score(fine_tuned_performance) > best_score:
                best_params = fine_tuned_params
                best_performance = fine_tuned_performance
        
        return best_params, best_performance
    
    def _generate_coarse_grid(self) -> List[ParameterSet]:
        """生成粗糙網格"""
        # 每個參數選擇 5 個代表性值
        conf_values = np.linspace(0.65, 0.85, 5)
        price_values = np.linspace(0.0005, 0.002, 5)
        volume_values = np.linspace(1.0, 2.5, 5)
        
        grid = []
        for conf, price, volume in itertools.product(conf_values, price_values, volume_values):
            grid.append(ParameterSet(
                confidence_threshold=float(conf),
                price_change_threshold=float(price),
                volume_change_threshold=float(volume)
            ))
        
        return grid
    
    async def _fine_tune_parameters(self, base_params: ParameterSet) -> Tuple[ParameterSet, Dict[str, float]]:
        """在最佳參數附近精細調整"""
        best_params = base_params
        best_performance = await self._test_parameter_set(base_params)
        best_score = self._calculate_composite_score(best_performance)
        
        # 在最佳參數周圍 ±10% 範圍內搜尋
        adjustments = [-0.1, -0.05, 0, 0.05, 0.1]
        
        for conf_adj in adjustments:
            for price_adj in adjustments:
                for volume_adj in adjustments:
                    new_params = ParameterSet(
                        confidence_threshold=max(0.65, min(0.85, base_params.confidence_threshold * (1 + conf_adj))),
                        price_change_threshold=max(0.0005, min(0.002, base_params.price_change_threshold * (1 + price_adj))),
                        volume_change_threshold=max(1.0, min(2.5, base_params.volume_change_threshold * (1 + volume_adj)))
                    )
                    
                    performance = await self._test_parameter_set(new_params)
                    score = self._calculate_composite_score(performance)
                    
                    if score > best_score:
                        best_score = score
                        best_params = new_params
                        best_performance = performance
        
        return best_params, best_performance
    
    async def _test_parameter_set(self, params: ParameterSet) -> Dict[str, float]:
        """測試特定參數組合的性能"""
        try:
            self.logger.info(f"🧪 測試參數組合: {params.to_dict()}")
            
            # 這裡會調用 Phase5 回測系統來測試參數
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent / "auto_backtest_validator"))
            from auto_backtest_validator import AutoBacktestValidator  # type: ignore
            
            validator = AutoBacktestValidator()
            
            # 臨時更新 Phase1A 參數
            await self._temporarily_update_phase1a_parameters(params)
            
            # 運行 7 天回測
            result = await validator.run_phase1a_validation_cycle()
            
            if result is None:
                self.logger.error("❌ 參數測試返回 None")
                return {'win_rate': 0, 'avg_pnl_ratio': 0, 'total_signals': 0, 'sharpe_ratio': 0}
            
            if 'error' in result:
                self.logger.error(f"❌ 參數測試失敗: {result['error']}")
                return {'win_rate': 0, 'avg_pnl_ratio': 0, 'total_signals': 0, 'sharpe_ratio': 0}
            
            # 提取性能指標
            overall_perf = result.get('overall_performance', {})
            performance = {
                'win_rate': overall_perf.get('overall_win_rate', 0),
                'avg_pnl_ratio': overall_perf.get('avg_pnl_ratio', 0),
                'total_signals': overall_perf.get('total_signals', 0),
                'sharpe_ratio': self._calculate_sharpe_ratio(result)
            }
            
            self.logger.info(f"📊 參數測試結果: 勝率 {performance['win_rate']:.2%}")
            return performance
            
        except Exception as e:
            self.logger.error(f"❌ 參數測試異常: {e}")
            import traceback
            traceback.print_exc()
            return {'win_rate': 0, 'avg_pnl_ratio': 0, 'total_signals': 0, 'sharpe_ratio': 0}
    
    def _calculate_composite_score(self, performance: Dict[str, float]) -> float:
        """計算綜合評分"""
        win_rate = performance.get('win_rate', 0)
        pnl_ratio = performance.get('avg_pnl_ratio', 0)
        sharpe_ratio = performance.get('sharpe_ratio', 0)
        
        # 加權綜合評分
        score = (
            win_rate * 50 +           # 勝率權重 50%
            min(pnl_ratio / 1.5, 1) * 30 +  # 盈虧比權重 30%
            min(sharpe_ratio, 1) * 20        # 夏普比率權重 20%
        )
        
        # 如果達到所有目標，給予額外獎勵
        if win_rate >= 0.70 and pnl_ratio >= 1.5 and sharpe_ratio >= 1.0:
            score += 10
        
        return score
    
    def _meets_targets(self, performance: Dict[str, float]) -> bool:
        """檢查是否達到目標"""
        return (
            performance.get('win_rate', 0) >= self.optimization_target.win_rate and
            performance.get('avg_pnl_ratio', 0) >= self.optimization_target.profit_loss_ratio and
            performance.get('sharpe_ratio', 0) >= self.optimization_target.sharpe_ratio
        )
    
    async def _get_current_performance(self) -> Dict[str, float]:
        """獲取當前參數的性能表現"""
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent / "auto_backtest_validator"))
        from auto_backtest_validator import AutoBacktestValidator  # type: ignore
        
        try:
            validator = AutoBacktestValidator()
            self.logger.info("🔄 開始執行 Phase1A 驗證循環...")
            result = await validator.run_phase1a_validation_cycle()
            
            self.logger.info(f"📊 驗證循環執行完成")
            self.logger.info(f"📊 結果類型: {type(result)}")
            
            if result is None:
                self.logger.error("❌ 驗證結果為 None")
                return {'win_rate': 0, 'avg_pnl_ratio': 0, 'total_signals': 0, 'sharpe_ratio': 0}
            
            self.logger.info(f"📊 結果內容摘要: {str(result)[:200]}...")
            
            if 'error' in result:
                self.logger.error(f"❌ 驗證失敗: {result['error']}")
                return {'win_rate': 0, 'avg_pnl_ratio': 0, 'total_signals': 0, 'sharpe_ratio': 0}
            
            # 提取性能指標
            overall_perf = result.get('overall_performance', {})
            performance = {
                'win_rate': overall_perf.get('overall_win_rate', 0),
                'avg_pnl_ratio': overall_perf.get('avg_pnl_ratio', 0),
                'total_signals': overall_perf.get('total_signals', 0),
                'sharpe_ratio': self._calculate_sharpe_ratio(result)
            }
            
            self.logger.info(f"📊 當前性能: 勝率 {performance['win_rate']:.2%}, 盈虧比 {performance['avg_pnl_ratio']:.2f}")
            return performance
            
        except Exception as e:
            self.logger.error(f"❌ 性能獲取失敗: {e}")
            import traceback
            traceback.print_exc()
            return {'win_rate': 0, 'avg_pnl_ratio': 0, 'total_signals': 0, 'sharpe_ratio': 0}
    
    
    async def _update_phase1a_parameters(self, params: ParameterSet):
        """更新 Phase1A 參數"""
        # 更新 JSON 配置文件
        from pathlib import Path
        config_path = Path(__file__).parent.parent.parent.parent / "backend" / "phase1_signal_generation" / "phase1a_basic_signal_generation" / "phase1a_basic_signal_generation.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 更新基礎模式參數
        config['phase1a_basic_signal_generation_dependency']['configuration']['signal_generation_params']['basic_mode']['confidence_threshold']['base_value'] = params.confidence_threshold
        config['phase1a_basic_signal_generation_dependency']['configuration']['signal_generation_params']['basic_mode']['price_change_threshold']['base_value'] = params.price_change_threshold
        config['phase1a_basic_signal_generation_dependency']['configuration']['signal_generation_params']['basic_mode']['volume_change_threshold']['base_value'] = params.volume_change_threshold
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"✅ Phase1A 參數已更新: {params.to_dict()}")
    
    async def _temporarily_update_phase1a_parameters(self, params: ParameterSet):
        """臨時更新 Phase1A 參數進行測試"""
        await self._update_phase1a_parameters(params)
    
    def _calculate_sharpe_ratio(self, result: Dict) -> float:
        """計算夏普比率"""
        # 從回測結果計算夏普比率
        performance_data = result.get('overall_performance', {})
        win_rate = performance_data.get('overall_win_rate', 0)
        avg_pnl = performance_data.get('avg_pnl_ratio', 0)
        
        # 簡化的夏普比率計算（實際應該使用收益的標準差）
        if win_rate > 0:
            return min(avg_pnl * win_rate * 0.5, 2.0)  # 最大限制為 2.0
        return 0
    
    def _calculate_improvement(self, old_performance: Dict[str, float], new_performance: Dict[str, float]) -> Dict[str, float]:
        """計算性能改善幅度"""
        improvement = {}
        for key in ['win_rate', 'avg_pnl_ratio', 'sharpe_ratio']:
            old_val = old_performance.get(key, 0)
            new_val = new_performance.get(key, 0)
            if old_val > 0:
                improvement[f'{key}_improvement'] = (new_val - old_val) / old_val
            else:
                improvement[f'{key}_improvement'] = float('inf') if new_val > 0 else 0
        return improvement
    
    def _should_update_parameters(self, new_performance: Dict[str, float], current_performance: Dict[str, float]) -> bool:
        """判斷是否應該更新參數"""
        new_score = self._calculate_composite_score(new_performance)
        current_score = self._calculate_composite_score(current_performance)
        
        # 需要至少 5% 的改善才更新
        improvement_threshold = 0.05
        return (new_score - current_score) / max(current_score, 1) > improvement_threshold
    
    def _generate_coarse_grid(self) -> List[ParameterSet]:
        """生成粗糙網格搜尋參數"""
        param_sets = []
        
        # 5x5x5 = 125 種組合
        confidence_values = [0.65, 0.70, 0.75, 0.80, 0.85]
        price_change_values = [0.0005, 0.001, 0.0015, 0.002, 0.0025]
        volume_change_values = [1.0, 1.25, 1.5, 1.75, 2.0]
        
        for conf in confidence_values:
            for price in price_change_values:
                for volume in volume_change_values:
                    param_sets.append(ParameterSet(
                        confidence_threshold=conf,
                        price_change_threshold=price,
                        volume_change_threshold=volume
                    ))
        
        return param_sets
    
    def _generate_fine_grid(self, best_params: ParameterSet) -> List[ParameterSet]:
        """在最佳參數周圍生成細緻網格"""
        param_sets = []
        
        # 在最佳參數的 ±10% 範圍內生成 3x3x3 = 27 種組合
        for conf_factor in [0.9, 1.0, 1.1]:
            for price_factor in [0.9, 1.0, 1.1]:
                for volume_factor in [0.9, 1.0, 1.1]:
                    new_conf = max(0.5, min(0.95, best_params.confidence_threshold * conf_factor))
                    new_price = max(0.0001, min(0.005, best_params.price_change_threshold * price_factor))
                    new_volume = max(0.5, min(3.0, best_params.volume_change_threshold * volume_factor))
                    
                    param_sets.append(ParameterSet(
                        confidence_threshold=new_conf,
                        price_change_threshold=new_price,
                        volume_change_threshold=new_volume
                    ))
        
        return param_sets
    
    def _validate_parameters(self, new_performance: Dict[str, float], current_performance: Dict[str, float]) -> bool:
        """驗證新參數是否比當前參數更好"""
        new_score = self._calculate_composite_score(new_performance)
        current_score = self._calculate_composite_score(current_performance)
        
        # 需要至少 2% 的改善才採用新參數
        improvement_threshold = 0.02
        improvement = (new_score - current_score) / max(current_score, 1)
        
        self.logger.info(f"📊 參數驗證: 新分數 {new_score:.2f}, 當前分數 {current_score:.2f}, 改善 {improvement:.2%}")
        return improvement > improvement_threshold

# 全局優化器實例
weekly_optimizer = WeeklyParameterOptimizer()

async def run_weekly_optimization():
    """執行每週優化（全局函數）"""
    # 設定詳細日誌
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info("🚀 開始每週參數優化...")
    
    result = await weekly_optimizer.run_weekly_optimization()
    logger.info(f"📊 優化結果: {result}")
    return result

if __name__ == "__main__":
    # 測試運行
    result = asyncio.run(run_weekly_optimization())
    print(json.dumps(result, indent=2, ensure_ascii=False))
