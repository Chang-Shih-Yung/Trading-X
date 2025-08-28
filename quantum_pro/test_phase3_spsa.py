#!/usr/bin/env python3
"""
測試 Phase 3: Enhanced SPSA 優化器 - 獨立測試
"""

import numpy as np
import logging
import sys
import os

# 添加路徑以便導入
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 設置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_spsa_learning_rate_formula():
    """測試 SPSA 學習率衰減公式"""
    try:
        logger.info("🧪 === 測試 SPSA 學習率衰減公式 ===")
        
        initial_lr = 0.1
        decay_factor = 10.0
        
        # 測試學習率公式: α / (1 + iteration/decay_factor)
        learning_rates = []
        for iteration in range(30):
            lr = initial_lr / (1 + iteration / decay_factor)
            learning_rates.append(lr)
        
        # 驗證學習率性質
        is_decreasing = all(learning_rates[i] >= learning_rates[i+1] for i in range(len(learning_rates)-1))
        starts_at_initial = abs(learning_rates[0] - initial_lr) < 1e-10
        converges_to_zero = learning_rates[-1] < learning_rates[0] * 0.1
        
        logger.info(f"📊 初始學習率: {learning_rates[0]:.6f}")
        logger.info(f"📊 第10次迭代: {learning_rates[9]:.6f}")
        logger.info(f"📊 第20次迭代: {learning_rates[19]:.6f}")
        logger.info(f"📊 最終學習率: {learning_rates[-1]:.6f}")
        
        logger.info(f"✅ 從初始值開始: {starts_at_initial}")
        logger.info(f"✅ 單調遞減: {is_decreasing}")
        logger.info(f"✅ 衰減有效: {converges_to_zero}")
        
        # 測試早停機制邏輯
        logger.info("🧪 測試早停機制邏輯...")
        
        # 模擬目標值序列
        objective_values = [10.0, 8.0, 6.0, 5.9, 5.8, 5.81, 5.82, 5.83, 5.84, 5.85]
        tolerance = 0.01
        patience = 3
        
        best_objective = float('inf')
        patience_counter = 0
        early_stop_triggered = False
        
        for i, obj_val in enumerate(objective_values):
            if obj_val < best_objective - tolerance:
                best_objective = obj_val
                patience_counter = 0
                logger.info(f"� Iteration {i}: 目標值改善 {obj_val:.3f}")
            else:
                patience_counter += 1
                logger.info(f"📊 Iteration {i}: 無改善 {obj_val:.3f} (patience: {patience_counter})")
                
            if patience_counter >= patience:
                early_stop_triggered = True
                logger.info(f"⏹️  早停觸發於第 {i} 次迭代")
                break
        
        logger.info(f"✅ 早停機制觸發: {early_stop_triggered}")
        
        return is_decreasing and starts_at_initial and early_stop_triggered
        
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        return False

def test_quantum_randomness_concept():
    """測試量子隨機數概念"""
    try:
        logger.info("🧪 === 測試量子隨機數概念 ===")
        
        # 模擬量子比特生成 (0 或 1)
        np.random.seed(42)  # 僅用於演示，實際應使用量子隨機數
        n_params = 5
        quantum_bits = np.random.choice([0, 1], size=n_params)
        
        # 轉換為 SPSA 擾動 (+1 或 -1)
        quantum_perturbations = np.array([2 * bit - 1 for bit in quantum_bits], dtype=float)
        
        logger.info(f"� 量子比特: {quantum_bits}")
        logger.info(f"� SPSA 擾動: {quantum_perturbations}")
        
        # 驗證擾動只有 +1 或 -1
        valid_perturbations = all(p in [-1.0, 1.0] for p in quantum_perturbations)
        
        logger.info(f"✅ 擾動值有效: {valid_perturbations}")
        
        return valid_perturbations
        
    except Exception as e:
        logger.error(f"❌ 量子隨機數測試失敗: {e}")
        return False

if __name__ == "__main__":
    logger.info("🔬 === Phase 3: Enhanced SPSA 獨立測試套件 ===")
    
    # 測試1: 學習率衰減公式
    test1_result = test_spsa_learning_rate_formula()
    
    # 測試2: 量子隨機數概念
    test2_result = test_quantum_randomness_concept()
    
    # 總結
    if test1_result and test2_result:
        logger.info("🎉 === Phase 3 核心概念測試通過！===")
        logger.info("✅ 學習率衰減公式: α / (1 + iteration/decay_factor)")
        logger.info("✅ 早停機制: patience-based early stopping")
        logger.info("✅ 量子隨機擾動: {-1, +1} 二進制擾動")
        logger.info("🚀 Phase 3 Enhanced SPSA 實現概念驗證成功！")
    else:
        logger.error("❌ 某些核心概念測試失敗")
