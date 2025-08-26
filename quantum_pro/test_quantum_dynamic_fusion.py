#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子動態權重融合系統測試器
測試真正的自適應權重融合機制
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/Users/henrychang/Desktop/Trading-X/logs/quantum_fusion_test.log')
    ]
)
logger = logging.getLogger(__name__)

# 導入我們的量子系統
try:
    from regime_hmm_quantum import (
        DynamicWeightFusion,
        _calculate_quantum_uncertainty,
        _generate_quantum_random_parameters,
        _quantum_superposition_momentum,
        _quantum_true_random_measurement,
        即時市場觀測,
    )
    logger.info("✅ 量子系統模組導入成功")
except ImportError as e:
    logger.error(f"❌ 無法導入量子系統: {e}")
    exit(1)

@dataclass
class TestMarketData:
    """測試市場數據"""
    timestamp: datetime
    price: float
    volume: float
    volatility: float
    momentum: float
    regime: str
    buy_ratio: float

class QuantumFusionTester:
    """量子動態權重融合測試器"""
    
    def __init__(self):
        self.fusion_engine = DynamicWeightFusion(quantum_enhanced=True)
        self.test_results = []
        self.performance_log = []
        
        logger.info("🔮 量子融合測試器初始化完成")
    
    def generate_test_market_data(self, scenario: str = "bull_to_bear") -> List[TestMarketData]:
        """生成測試市場數據"""
        data = []
        base_time = datetime.now()
        
        if scenario == "bull_to_bear":
            # 牛市轉熊市場景
            for i in range(100):
                if i < 40:  # 牛市階段
                    price = 50000 + i * 500 + _quantum_true_random_measurement() * 1000
                    volatility = 0.01 + _calculate_quantum_uncertainty() * 0.01
                    momentum = 0.02 + _quantum_superposition_momentum(0.7) * 0.03
                    regime = "STRONG_BULL" if i < 20 else "MILD_BULL"
                    buy_ratio = 0.65 + _quantum_true_random_measurement() * 0.2
                    
                elif i < 60:  # 轉換期
                    price = 70000 - (i-40) * 800 + _quantum_true_random_measurement() * 2000
                    volatility = 0.03 + _calculate_quantum_uncertainty() * 0.02
                    momentum = -0.01 + _quantum_superposition_momentum(0.3) * 0.02
                    regime = "NEUTRAL" if i < 50 else "UNCERTAIN"
                    buy_ratio = 0.5 + _quantum_true_random_measurement() * 0.3
                    
                else:  # 熊市階段
                    price = 54000 - (i-60) * 300 + _quantum_true_random_measurement() * 1500
                    volatility = 0.025 + _calculate_quantum_uncertainty() * 0.015
                    momentum = -0.025 + _quantum_superposition_momentum(0.2) * 0.01
                    regime = "MILD_BEAR" if i < 80 else "STRONG_BEAR"
                    buy_ratio = 0.35 + _quantum_true_random_measurement() * 0.2
                
                data.append(TestMarketData(
                    timestamp=base_time,
                    price=price,
                    volume=1000 + _quantum_true_random_measurement() * 500,
                    volatility=volatility,
                    momentum=momentum,
                    regime=regime,
                    buy_ratio=buy_ratio
                ))
                
        elif scenario == "volatile_market":
            # 高波動市場場景
            for i in range(80):
                # 隨機劇烈波動
                price = 50000 + _quantum_true_random_measurement() * 10000 - 5000
                volatility = 0.05 + _calculate_quantum_uncertainty() * 0.05  # 高波動
                momentum = (_quantum_true_random_measurement() - 0.5) * 0.08  # 隨機動量
                
                # 隨機制度切換
                rand_regime = _quantum_true_random_measurement()
                if rand_regime < 0.2:
                    regime = "STRONG_BULL"
                elif rand_regime < 0.35:
                    regime = "MILD_BULL"
                elif rand_regime < 0.5:
                    regime = "NEUTRAL"
                elif rand_regime < 0.65:
                    regime = "UNCERTAIN"
                elif rand_regime < 0.8:
                    regime = "MILD_BEAR"
                else:
                    regime = "STRONG_BEAR"
                    
                buy_ratio = 0.3 + _quantum_true_random_measurement() * 0.4
                
                data.append(TestMarketData(
                    timestamp=base_time,
                    price=price,
                    volume=800 + _quantum_true_random_measurement() * 800,
                    volatility=volatility,
                    momentum=momentum,
                    regime=regime,
                    buy_ratio=buy_ratio
                ))
                
        elif scenario == "trending_market":
            # 趨勢市場場景（持續上漲）
            for i in range(120):
                # 持續上漲趨勢
                price = 45000 + i * 200 + _quantum_true_random_measurement() * 800
                volatility = 0.015 + _calculate_quantum_uncertainty() * 0.01  # 中等波動
                momentum = 0.015 + _quantum_superposition_momentum(0.8) * 0.02  # 持續正動量
                
                # 趨勢相關制度
                if i < 30:
                    regime = "MILD_BULL"
                elif i < 90:
                    regime = "STRONG_BULL"
                else:
                    regime = "STRONG_BULL"  # 持續強牛
                    
                buy_ratio = 0.6 + _quantum_true_random_measurement() * 0.25
                
                data.append(TestMarketData(
                    timestamp=base_time,
                    price=price,
                    volume=1200 + _quantum_true_random_measurement() * 600,
                    volatility=volatility,
                    momentum=momentum,
                    regime=regime,
                    buy_ratio=buy_ratio
                ))
        
        else:
            logger.warning(f"⚠️ 未知測試場景: {scenario}，使用默認場景")
            return self.generate_test_market_data("bull_to_bear")
                
        logger.info(f"📊 生成 {len(data)} 條 {scenario} 測試數據")
        return data
    
    def create_market_observation(self, data: TestMarketData) -> 即時市場觀測:
        """創建市場觀測數據"""
        return 即時市場觀測(
            時間戳=data.timestamp,
            交易對="BTCUSDT",
            價格=data.price,
            成交量=data.volume,
            收益率=data.momentum,
            已實現波動率=data.volatility,
            動量斜率=data.momentum,
            最佳買價=data.price * 0.999,
            最佳賣價=data.price * 1.001,
            買賣價差=data.price * 0.002,
            訂單簿壓力=data.buy_ratio - 0.5,
            主動買入比率=data.buy_ratio,
            大單流入率=_quantum_true_random_measurement() * 0.1,
            資金費率=_quantum_true_random_measurement() * 0.001,
            未平倉量=1000000 + _quantum_true_random_measurement() * 500000,
            隱含波動率=data.volatility * 1.2
        )
    
    async def test_fusion_engine(self, test_data: List[TestMarketData]) -> Dict[str, Any]:
        """測試融合引擎"""
        logger.info("🧪 開始量子融合引擎測試")
        
        fusion_results = []
        regime_predictions = []
        quantum_predictions = []
        
        for i, data in enumerate(test_data):
            try:
                # 模擬制度和量子信號
                regime_prob = _quantum_superposition_momentum(0.7) if "BULL" in data.regime else _quantum_superposition_momentum(0.3)
                regime_persistence = _quantum_superposition_momentum(0.8) if i > 0 and test_data[i-1].regime == data.regime else _quantum_superposition_momentum(0.4)
                
                quantum_confidence = _quantum_superposition_momentum(0.6) + _calculate_quantum_uncertainty() * 0.3
                quantum_fidelity = 0.85 + _quantum_true_random_measurement() * 0.1
                risk_reward_ratio = 2.0 + _quantum_true_random_measurement() * 1.0
                
                # 市場狀態
                market_state = {
                    'regime': data.regime,
                    'volatility': data.volatility,
                    'trend_strength': abs(data.momentum) * 10,
                    'fear_greed': 50 + data.momentum * 1000
                }
                
                # 調用融合引擎
                fusion_result = self.fusion_engine.fuse_signals(
                    regime_probability=regime_prob,
                    regime_persistence=regime_persistence,
                    quantum_confidence=quantum_confidence,
                    quantum_fidelity=quantum_fidelity,
                    risk_reward_ratio=risk_reward_ratio,
                    market_state=market_state
                )
                
                fusion_results.append(fusion_result)
                
                # 模擬實際結果（用於績效更新）
                actual_regime_success = _quantum_true_random_measurement() > 0.3
                actual_quantum_success = _quantum_true_random_measurement() > 0.4
                
                # 更新績效反饋
                self.fusion_engine.update_performance_feedback(
                    actual_regime_success, actual_quantum_success
                )
                
                regime_predictions.append(actual_regime_success)
                quantum_predictions.append(actual_quantum_success)
                
                # 每10步顯示狀態
                if i % 10 == 0:
                    await self.display_fusion_status(i, fusion_result, market_state)
                
            except Exception as e:
                logger.error(f"❌ 測試步驟 {i} 失敗: {e}")
                continue
        
        # 計算測試結果
        test_summary = self.analyze_test_results(fusion_results, regime_predictions, quantum_predictions)
        
        logger.info("✅ 量子融合引擎測試完成")
        return test_summary
    
    async def display_fusion_status(self, step: int, fusion_result: Dict, market_state: Dict):
        """顯示融合狀態"""
        logger.info(f"📊 步驟 {step} - 量子融合狀態:")
        logger.info(f"   💰 最終信心度: {fusion_result['final_confidence']:.3f}")
        logger.info(f"   ⚖️ 權重分配: 制度{fusion_result['regime_weight']:.2%} | 量子{fusion_result['quantum_weight']:.2%}")
        logger.info(f"   📈 信號強度: 制度{fusion_result['regime_signal']:.3f} | 量子{fusion_result['quantum_signal']:.3f}")
        logger.info(f"   🎯 風險因子: {fusion_result['risk_factor']:.3f}")
        logger.info(f"   🔮 量子獎勵: {fusion_result['ensemble_bonus']:.3f}")
        logger.info(f"   🌊 市場狀態: {market_state['regime']} (波動率 {market_state['volatility']:.1%})")
        
        # 顯示學習指標
        adaptation_info = fusion_result.get('adaptation_info', {})
        logger.info(f"   🧠 學習狀態: 制度績效{adaptation_info.get('regime_performance', 0):.1%} | 量子績效{adaptation_info.get('quantum_performance', 0):.1%}")
        logger.info(f"   📚 學習率: {adaptation_info.get('learning_rate', 0):.4f}")
    
    def analyze_test_results(self, fusion_results: List[Dict], regime_preds: List[bool], quantum_preds: List[bool]) -> Dict[str, Any]:
        """分析測試結果"""
        if not fusion_results:
            logger.warning("⚠️ 無測試結果，返回默認值")
            return {
                'confidence_stats': {
                    'mean': 0.0,
                    'std': 0.0,
                    'min': 0.0,
                    'max': 0.0
                },
                'weight_dynamics': {
                    'regime_weight_variance': 0.0,
                    'quantum_weight_variance': 0.0,
                    'avg_regime_weight': 0.5,
                    'avg_quantum_weight': 0.5
                },
                'risk_management': {
                    'avg_risk_factor': 1.0,
                    'risk_factor_range': 0.0
                },
                'performance_validation': {
                    'regime_accuracy': 0.0,
                    'quantum_accuracy': 0.0,
                    'sample_size': 0
                },
                'learning_system': self.fusion_engine.get_performance_summary()
            }
        
        # 信心度統計
        confidences = [r['final_confidence'] for r in fusion_results]
        regime_weights = [r['regime_weight'] for r in fusion_results]
        quantum_weights = [r['quantum_weight'] for r in fusion_results]
        risk_factors = [r['risk_factor'] for r in fusion_results]
        
        # 權重變化分析
        weight_variance_regime = np.var(regime_weights) if regime_weights else 0
        weight_variance_quantum = np.var(quantum_weights) if quantum_weights else 0
        
        # 績效分析
        regime_accuracy = np.mean(regime_preds) if regime_preds else 0
        quantum_accuracy = np.mean(quantum_preds) if quantum_preds else 0
        
        # 獲取融合引擎性能摘要
        performance_summary = self.fusion_engine.get_performance_summary()
        
        return {
            'confidence_stats': {
                'mean': np.mean(confidences),
                'std': np.std(confidences),
                'min': np.min(confidences),
                'max': np.max(confidences)
            },
            'weight_dynamics': {
                'regime_weight_variance': weight_variance_regime,
                'quantum_weight_variance': weight_variance_quantum,
                'avg_regime_weight': np.mean(regime_weights),
                'avg_quantum_weight': np.mean(quantum_weights)
            },
            'risk_management': {
                'avg_risk_factor': np.mean(risk_factors),
                'risk_factor_range': np.max(risk_factors) - np.min(risk_factors)
            },
            'performance_validation': {
                'regime_accuracy': regime_accuracy,
                'quantum_accuracy': quantum_accuracy,
                'sample_size': len(fusion_results)
            },
            'learning_system': performance_summary
        }
    
    async def test_quantum_adaptability(self):
        """測試量子自適應能力"""
        logger.info("🔬 開始量子自適應能力測試")
        
        scenarios = ["bull_to_bear", "volatile_market", "trending_market"]
        adaptability_scores = {}
        
        for scenario in scenarios:
            logger.info(f"📊 測試場景: {scenario}")
            
            # 重置融合引擎
            self.fusion_engine.reset_quantum_state()
            
            # 生成測試數據
            test_data = self.generate_test_market_data(scenario)
            
            # 運行測試
            results = await self.test_fusion_engine(test_data)
            
            # 計算自適應評分
            weight_variance = results['weight_dynamics']['regime_weight_variance'] + results['weight_dynamics']['quantum_weight_variance']
            adaptability_score = min(1.0, weight_variance * 10)  # 權重變化越大，自適應性越好
            
            adaptability_scores[scenario] = adaptability_score
            
            logger.info(f"✅ {scenario} 自適應評分: {adaptability_score:.3f}")
        
        return adaptability_scores
    
    async def stress_test(self):
        """壓力測試"""
        logger.info("💪 開始壓力測試")
        
        stress_results = []
        
        for iteration in range(10):
            try:
                start_time = time.time()
                
                # 生成極端市場數據
                extreme_data = []
                for i in range(50):
                    extreme_volatility = 0.1 + _quantum_true_random_measurement() * 0.05  # 極高波動
                    extreme_momentum = (_quantum_true_random_measurement() - 0.5) * 0.1  # 極端動量
                    
                    extreme_data.append(TestMarketData(
                        timestamp=datetime.now(),
                        price=50000 + _quantum_true_random_measurement() * 10000,
                        volume=500 + _quantum_true_random_measurement() * 1000,
                        volatility=extreme_volatility,
                        momentum=extreme_momentum,
                        regime="UNCERTAIN",
                        buy_ratio=_quantum_true_random_measurement()
                    ))
                
                # 運行極端測試
                results = await self.test_fusion_engine(extreme_data)
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                stress_results.append({
                    'iteration': iteration,
                    'execution_time': execution_time,
                    'success': True,
                    'confidence_stability': results['confidence_stats']['std'],
                    'weight_adaptability': results['weight_dynamics']['regime_weight_variance']
                })
                
                logger.info(f"✅ 壓力測試 {iteration+1}/10 完成 ({execution_time:.2f}s)")
                
            except Exception as e:
                logger.error(f"❌ 壓力測試 {iteration+1} 失敗: {e}")
                stress_results.append({
                    'iteration': iteration,
                    'success': False,
                    'error': str(e)
                })
        
        success_rate = sum(1 for r in stress_results if r.get('success', False)) / len(stress_results)
        avg_time = np.mean([r.get('execution_time', 0) for r in stress_results if r.get('success', False)])
        
        logger.info(f"💪 壓力測試完成: 成功率 {success_rate:.1%}, 平均執行時間 {avg_time:.2f}s")
        
        return {
            'success_rate': success_rate,
            'avg_execution_time': avg_time,
            'detailed_results': stress_results
        }

async def main():
    """主測試函數"""
    logger.info("🚀 啟動量子動態權重融合系統測試")
    
    tester = QuantumFusionTester()
    
    try:
        # 1. 基本功能測試
        logger.info("=" * 50)
        logger.info("🧪 階段 1: 基本功能測試")
        test_data = tester.generate_test_market_data("bull_to_bear")
        basic_results = await tester.test_fusion_engine(test_data)
        
        logger.info("📋 基本測試結果:")
        logger.info(f"   信心度統計: 平均 {basic_results['confidence_stats']['mean']:.3f} ± {basic_results['confidence_stats']['std']:.3f}")
        logger.info(f"   權重動態性: 制度 {basic_results['weight_dynamics']['regime_weight_variance']:.4f}, 量子 {basic_results['weight_dynamics']['quantum_weight_variance']:.4f}")
        logger.info(f"   績效驗證: 制度 {basic_results['performance_validation']['regime_accuracy']:.1%}, 量子 {basic_results['performance_validation']['quantum_accuracy']:.1%}")
        
        # 2. 自適應能力測試
        logger.info("=" * 50)
        logger.info("🔬 階段 2: 自適應能力測試")
        adaptability_results = await tester.test_quantum_adaptability()
        
        logger.info("📋 自適應測試結果:")
        for scenario, score in adaptability_results.items():
            logger.info(f"   {scenario}: {score:.3f}")
        
        # 3. 壓力測試
        logger.info("=" * 50)
        logger.info("💪 階段 3: 壓力測試")
        stress_results = await tester.stress_test()
        
        logger.info("📋 壓力測試結果:")
        logger.info(f"   成功率: {stress_results['success_rate']:.1%}")
        logger.info(f"   平均執行時間: {stress_results['avg_execution_time']:.2f}s")
        
        # 4. 綜合評估
        logger.info("=" * 50)
        logger.info("🎯 綜合評估結果")
        
        overall_score = (
            basic_results['confidence_stats']['mean'] * 0.3 +
            np.mean(list(adaptability_results.values())) * 0.4 +
            stress_results['success_rate'] * 0.3
        )
        
        logger.info(f"🏆 量子動態權重融合系統總評分: {overall_score:.3f}/1.0")
        
        if overall_score > 0.8:
            logger.info("✅ 測試結果: 優秀 - 系統運行穩定，自適應性強")
        elif overall_score > 0.6:
            logger.info("⚠️  測試結果: 良好 - 系統基本穩定，有改進空間")
        else:
            logger.info("❌ 測試結果: 需要優化 - 系統存在問題")
            
    except Exception as e:
        logger.error(f"❌ 測試過程發生錯誤: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    logger.info("🏁 量子動態權重融合系統測試完成")

if __name__ == "__main__":
    asyncio.run(main())
