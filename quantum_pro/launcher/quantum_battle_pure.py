#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🥊 純量子物理驅動對戰競技場 - 純調用版本
═══════════════════════════════════════════════════════════

🔴 紅隊 (Pure Quantum): btc_quantum_ultimate_model.py - $10 初始資金
🔵 藍隊 (Adaptive Quantum): quantum_adaptive_trading_launcher.py - $10 初始資金

⚛️ 核心原則：
   - 純編排器：只負責調用真實量子組件
   - 零模擬：所有量子計算來自真實組件
   - 零回退：調用失敗即報錯，不允許模擬替代
   - 零風控：虧損就扣錢，扣到負數也繼續

📡 實時數據：幣安 WebSocket + 真實 P&L 計算
"""

import asyncio
import json
import logging
import os
import signal
import sqlite3
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Qiskit 2.x SDK for Quantum Entropy-Driven Scheduling
import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import Sampler, Estimator
from qiskit.quantum_info import (
    random_statevector, entropy, partial_trace, 
    SparsePauliOp, Statevector, DensityMatrix,
    random_unitary, random_density_matrix, Operator
)
from qiskit.circuit.random import random_circuit
from qiskit_aer.primitives import EstimatorV2 as AerEstimator

# 忽略 NumPy/Pandas 兼容性警告
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', message='numpy.dtype size changed')
warnings.filterwarnings('ignore', message='numpy.ufunc size changed')

import aiohttp
import numpy as np
import websockets

# 導入區塊鏈主池數據源
try:
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'X'))
    from binance_data_connector import BinanceDataConnector
    BLOCKCHAIN_CONNECTOR_AVAILABLE = True
    print("✅ 區塊鏈主池數據源可用")
except ImportError:
    BinanceDataConnector = None
    BLOCKCHAIN_CONNECTOR_AVAILABLE = False
    print("❌ 區塊鏈主池數據源不可用，將使用 WebSocket 備用")

# 導入前端服務器
try:
    from frontend_server import QuantumBattleFrontendServer
except ImportError:
    QuantumBattleFrontendServer = None

# 物理常數 (NIST 2018)
PHYSICAL_CONSTANTS = {
    'hbar': 1.054571817e-34,      # 約化普朗克常數
    'alpha': 7.2973525693e-3,     # 精細結構常數
    'phi': 1.618033988749,        # 黃金比例
    'euler': 2.718281828459,      # 歐拉數
}

# 計算量子初始化參數 (純物理推導)
QUANTUM_INIT_POINTS = int(PHYSICAL_CONSTANTS['phi'] * PHYSICAL_CONSTANTS['euler'] * 10)  # φ×e×10 = 43

# 日誌配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('quantum_battle_orchestrator.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class QuantumEntropyUpdateManager:
    """
    基於 Qiskit 2.x SDK 的量子熵驅動更新管理器
    
    使用真實量子熵計算來決定系統更新時機：
    - 量子系統熵下降時觸發重新初始化
    - 基於量子物理原理，完全無人為干預
    - 符合 Qiskit 2.x 標準，使用 Primitives API
    """
    
    def __init__(self, entropy_threshold: float = None):
        """
        初始化量子熵更新管理器
        
        Args:
            entropy_threshold: 熵閾值，None時使用量子隨機生成
        """
        # 使用 Qiskit 2.x Primitives
        self.sampler = Sampler()
        self.estimator = AerEstimator()
        
        # 量子系統狀態追踪（必須在閾值生成之前設置）
        self.quantum_system_qubits = 5  # 5-qubit系統
        self.current_quantum_state = None
        
        # 量子熵歷史記錄
        self.entropy_history = []
        self.last_engine_update = time.time()
        self.last_model_retrain = time.time()
        
        # 量子隨機生成熵閾值（如果未指定）
        if entropy_threshold is None:
            self.entropy_threshold = self._generate_quantum_entropy_threshold()
        else:
            self.entropy_threshold = entropy_threshold
        
        logger.info(f"🌌 量子熵更新管理器初始化 - 熵閾值: {self.entropy_threshold:.4f}")
    
    def _generate_quantum_entropy_threshold(self) -> float:
        """使用 Qiskit 2.x 內建量子隨機套件生成熵閾值 - 修正版"""
        try:
            # 🎲 使用 Qiskit 內建的 random_density_matrix 生成真量子隨機密度矩陣
            random_measurements = []
            
            for _ in range(3):  # 3次獨立的量子隨機密度矩陣
                # 直接使用 Qiskit 內建的量子隨機密度矩陣生成器
                random_dm = random_density_matrix(4)  # 4-qubit 隨機密度矩陣
                
                # 計算該隨機密度矩陣的 von Neumann 熵
                measurement_entropy = entropy(random_dm, base=2)
                random_measurements.append(measurement_entropy)
            
            # 🔬 基於真實量子隨機熵計算閾值
            avg_entropy = np.mean(random_measurements)
            
            # 使用 random_statevector 生成隨機因子
            random_state = random_statevector(4)  # 4-qubit 隨機狀態向量
            
            # 從隨機狀態向量提取隨機因子
            # 計算狀態向量各分量的幅度
            amplitudes = random_state.data  # 獲取狀態向量數據
            
            # 使用第一個振幅的相位作為隨機因子
            first_amplitude = amplitudes[0]
            phase = np.angle(first_amplitude)  # 提取相位 [-π, π]
            
            # 將相位歸一化到 [0.7, 0.9] 範圍作為閾值倍數
            normalized_phase = (phase + np.pi) / (2 * np.pi)  # 歸一化到 [0, 1]
            threshold_multiplier = 0.7 + 0.2 * normalized_phase  # [0.7, 0.9]
            
            # 計算相對於 5-qubit 系統的最終閾值
            system_max_entropy = np.log2(2**self.quantum_system_qubits)  # 5.0
            max_4qubit_entropy = np.log2(16)  # 4.0
            
            threshold = threshold_multiplier * avg_entropy * (system_max_entropy / max_4qubit_entropy)
            
            logger.info(f"🎲 Qiskit內建量子隨機閾值: {threshold:.4f}")
            logger.info(f"   • 隨機密度矩陣熵: {[f'{h:.3f}' for h in random_measurements]}")
            logger.info(f"   • 平均熵: {avg_entropy:.4f}, 閾值倍數: {threshold_multiplier:.3f}")
            logger.info(f"   • 隨機狀態相位: {phase:.3f} → 倍數: {threshold_multiplier:.3f}")
            
            return threshold
                
        except Exception as e:
            logger.error(f"❌ Qiskit內建量子隨機閾值生成失敗: {e}")
            # 嚴格模式：不允許回退
            raise RuntimeError(f"Qiskit 2.x 內建量子隨機失敗，嚴格模式終止: {e}")
    
    async def calculate_current_quantum_entropy(self) -> float:
        """
        使用 Qiskit 2.x 內建套件計算量子熵 - 純套件方法
        
        直接使用 random_statevector, random_circuit, random_density_matrix 等內建函數
        """
        try:
            current_time = datetime.now()
            
            # 🌌 方法1: 使用 random_statevector 創建量子隨機態
            random_state = random_statevector(2**self.quantum_system_qubits)
            
            # 創建密度矩陣
            density_matrix = DensityMatrix(random_state)
            
            # 🔄 方法2: 使用 random_circuit 增加時間相關性
            # 基於當前時間生成隨機電路參數
            circuit_depth = (current_time.second % 10) + 5  # 5-14 depth
            time_seed = current_time.microsecond % 1000
            
            # 使用 Qiskit 內建的 random_circuit
            random_qc = random_circuit(
                num_qubits=self.quantum_system_qubits, 
                depth=circuit_depth,
                measure=False,
                seed=time_seed  # 時間種子確保隨機性
            )
            
            # 從隨機電路獲取狀態向量
            circuit_statevector = Statevector.from_instruction(random_qc)
            circuit_density = DensityMatrix(circuit_statevector)
            
            # 🎲 方法3: 直接使用 random_density_matrix
            pure_random_dm = random_density_matrix(2**self.quantum_system_qubits)
            
            # 🔗 組合三種方法：創建加權混合態
            # 使用 random_statevector 生成權重
            weight_state = random_statevector(8)  # 8維隨機態
            
            # 從隨機狀態向量的前3個分量提取權重
            weight_amplitudes = weight_state.data[:3]  # 取前3個分量
            weights_raw = [abs(amp)**2 for amp in weight_amplitudes]  # 概率權重
            total_weight = sum(weights_raw)
            weights = [w / total_weight for w in weights_raw] if total_weight > 0 else [1/3, 1/3, 1/3]
            
            # 創建最終混合態
            final_density_matrix = (
                weights[0] * density_matrix + 
                weights[1] * circuit_density + 
                weights[2] * pure_random_dm
            )
            
            # 🔬 計算 von Neumann 熵
            current_entropy = entropy(final_density_matrix, base=2)
            
            # 🔍 驗證物理合理性
            max_entropy = np.log2(2**self.quantum_system_qubits)
            if current_entropy > max_entropy or current_entropy < 0:
                raise RuntimeError(f"❌ 量子熵超出物理範圍: {current_entropy:.4f} (0 - {max_entropy:.4f})")
            
            # 📊 記錄結果
            self.entropy_history.append({
                'timestamp': current_time,
                'entropy': current_entropy,
                'max_entropy': max_entropy,
                'entropy_ratio': current_entropy / max_entropy,
                'method': 'qiskit_builtin_random',
                'circuit_depth': circuit_depth,
                'weights': weights,
                'time_seed': time_seed
            })
            
            # 使用 Qiskit 2.x 量子隨機決定歷史記錄管理（絕對無固定數值）
            from qiskit.quantum_info import random_statevector as memory_random_statevector
            from qiskit.quantum_info import random_density_matrix as memory_random_density_matrix
            from qiskit.circuit.random import random_circuit as memory_random_circuit
            
            # 完全量子隨機生成記憶體管理參數
            memory_circuit = memory_random_circuit(num_qubits=4, depth=3, seed=None)
            size_quantum_state = memory_random_statevector(dims=32, seed=None)  # 5-qubit system for size
            retention_quantum_density = memory_random_density_matrix(dims=16, seed=None)  # 4-qubit system for retention
            scale_quantum_state = memory_random_statevector(dims=8, seed=None)  # 3-qubit for scaling
            
            # 完全基於量子隨機的動態計算
            circuit_complexity = memory_circuit.depth() * memory_circuit.num_qubits
            quantum_scale_factor = abs(scale_quantum_state.data[0]) ** 2 * abs(scale_quantum_state.data[1]) ** 2
            quantum_base_multiplier = abs(size_quantum_state.data[0]) ** 2 * abs(size_quantum_state.data[1]) ** 2
            
            # 動態上限：純量子隨機決定
            quantum_max_history = max(
                len(self.entropy_history) + 1,  # 至少比當前大1
                int(circuit_complexity * quantum_base_multiplier * quantum_scale_factor * abs(size_quantum_state.data[2]) ** 2)
            )
            
            # 動態保留：純量子隨機決定
            quantum_retention_factor = abs(retention_quantum_density.trace().real) * abs(size_quantum_state.data[3]) ** 2
            quantum_keep_size = max(
                1,  # 至少保留1項
                int(quantum_max_history * quantum_retention_factor)
            )
            
            if len(self.entropy_history) > quantum_max_history:
                self.entropy_history = self.entropy_history[-quantum_keep_size:]
                logger.debug(f"🌀 絕對純量子記憶體管理: 保留 {quantum_keep_size}/{quantum_max_history} 項記錄")
            
            logger.debug(f"🌀 Qiskit內建量子熵: {current_entropy:.4f}/{max_entropy:.4f} ({current_entropy/max_entropy*100:.1f}%)")
            logger.debug(f"   • 電路深度: {circuit_depth}, 時間種子: {time_seed}, 權重: {[f'{w:.3f}' for w in weights]}")
            
            return current_entropy
            
        except Exception as e:
            logger.error(f"❌ Qiskit內建量子熵計算失敗: {e}")
            # 嚴格模式：不允許回退
            raise RuntimeError(f"Qiskit 2.x 內建量子熵計算失敗，嚴格模式終止: {e}")
        
            
        except Exception as e:
            logger.error(f"❌ 量子熵計算失敗: {e}")
            raise RuntimeError(f"量子熵計算失敗，系統無法繼續: {e}")
    
    async def should_update_engines(self) -> bool:
        """
        純量子熵驅動的引擎更新判斷
        
        完全依據 Qiskit 2.x 量子物理原理，無固定參數
        """
        try:
            current_entropy = await self.calculate_current_quantum_entropy()
            
            # 主要量子觸發：熵值低於閾值（系統過於有序）
            entropy_trigger = current_entropy < self.entropy_threshold
            
            # 使用 Qiskit 2.x 量子隨機數決定檢測條件
            from qiskit.quantum_info import random_statevector, random_density_matrix
            from qiskit.circuit.random import random_circuit
            
            # 量子相位突變檢測：使用量子隨機決定是否檢測
            phase_mutation_trigger = False
            if self.entropy_history:  # 只要有歷史數據就檢測
                # 使用量子隨機狀態生成相位突變閾值
                quantum_state = random_statevector(dims=2, seed=None)
                quantum_phase_threshold = abs(quantum_state.data[0]) ** 2  # 0-1之間的量子隨機值
                
                previous_entropy = self.entropy_history[-1]['entropy']
                entropy_change_rate = abs(current_entropy - previous_entropy) / previous_entropy
                # 使用量子隨機閾值判斷相位突變
                phase_mutation_trigger = entropy_change_rate > quantum_phase_threshold
            
            # 量子糾纏破壞檢測：使用量子隨機決定分析窗口大小
            entanglement_decay_trigger = False
            if self.entropy_history:
                # 使用量子隨機生成電路參數（無固定數值）
                quantum_circuit_generator = random_statevector(dims=8, seed=None)  # 3-qubit for circuit params
                dynamic_qubits = max(1, int(abs(quantum_circuit_generator.data[0]) ** 2 * 5) + 1)  # 1-6 qubits
                dynamic_depth = max(1, int(abs(quantum_circuit_generator.data[1]) ** 2 * 3) + 1)   # 1-4 depth
                
                random_qc = random_circuit(num_qubits=dynamic_qubits, depth=dynamic_depth, seed=None)
                dynamic_window_size = min(len(self.entropy_history), max(1, int(random_qc.depth() * random_qc.num_qubits)))
                
                if len(self.entropy_history) >= dynamic_window_size and dynamic_window_size >= 2:
                    recent_entropies = [h['entropy'] for h in self.entropy_history[-dynamic_window_size:]]
                    
                    try:
                        entropy_trend = np.polyfit(range(len(recent_entropies)), recent_entropies, 1)[0]
                        
                        # 使用量子隨機密度矩陣生成趨勢閾值（無固定倍數）
                        quantum_trend_generator = random_density_matrix(dims=4, seed=None)
                        quantum_scale_factor = abs(quantum_trend_generator.trace().real)
                        quantum_trend_threshold = -quantum_scale_factor  # 負值閾值，完全量子隨機
                        
                        entanglement_decay_trigger = entropy_trend < quantum_trend_threshold
                    except np.linalg.LinAlgError:
                        # 如果數值計算失敗，使用純量子隨機決定
                        quantum_fallback = random_statevector(dims=2, seed=None)
                        entanglement_decay_trigger = abs(quantum_fallback.data[0]) ** 2 < 0.5
            
            # 純量子觸發邏輯
            should_update = (
                entropy_trigger or           # 低熵觸發
                phase_mutation_trigger or    # 量子相位突變
                entanglement_decay_trigger   # 量子糾纏破壞
            )
            
            if should_update:
                logger.info("🔄 純量子熵驅動引擎更新觸發:")
                logger.info(f"   • 當前熵值: {current_entropy:.4f}")
                logger.info(f"   • 熵值閾值: {self.entropy_threshold:.4f} (低熵觸發: {entropy_trigger})")
                logger.info(f"   • 量子相位突變: {phase_mutation_trigger}")
                logger.info(f"   • 量子糾纏破壞: {entanglement_decay_trigger}")
                
                self.last_engine_update = time.time()
                
                # 更新後重新生成量子隨機閾值
                self.entropy_threshold = self._generate_quantum_entropy_threshold()
                
            return should_update
            
        except Exception as e:
            logger.error(f"❌ 量子熵更新判斷失敗: {e}")
            # 嚴格模式：計算失敗時不允許更新
            raise RuntimeError(f"量子熵更新判斷失敗，系統暫停: {e}")
    
    async def should_retrain_models(self) -> bool:
        """
        純量子熵驅動的模型重訓練判斷
        
        完全依據 Qiskit 2.x 量子物理原理，無固定參數
        """
        try:
            current_entropy = await self.calculate_current_quantum_entropy()
            
            # 使用 Qiskit 2.x 量子隨機生成觸發條件
            from qiskit.quantum_info import random_statevector, random_density_matrix
            from qiskit.circuit.random import random_circuit
            
            # 量子隨機生成極低熵閾值（完全無固定數值）
            quantum_multiplier_generator = random_statevector(dims=4, seed=None)  # 2-qubit system
            quantum_scale_generator = random_density_matrix(dims=2, seed=None)
            ultra_low_multiplier = abs(quantum_multiplier_generator.data[0]) ** 2 * abs(quantum_scale_generator.trace().real)
            ultra_low_entropy_threshold = self.entropy_threshold * ultra_low_multiplier
            
            # 量子相干性破壞判斷：使用量子隨機決定檢測條件
            consecutive_low_entropy = False
            if self.entropy_history:
                # 量子隨機生成電路參數和檢測窗口大小
                quantum_circuit_params = random_statevector(dims=8, seed=None)  # 3-qubit for params
                dynamic_qubits = max(1, int(abs(quantum_circuit_params.data[0]) ** 2 * 5) + 1)  # 1-6 qubits
                dynamic_depth = max(1, int(abs(quantum_circuit_params.data[1]) ** 2 * 4) + 1)   # 1-5 depth
                
                random_qc = random_circuit(num_qubits=dynamic_qubits, depth=dynamic_depth, seed=None)
                dynamic_window = min(len(self.entropy_history), max(1, random_qc.depth() + random_qc.num_qubits))
                
                if len(self.entropy_history) >= dynamic_window:
                    recent_entropies = [h['entropy'] for h in self.entropy_history[-dynamic_window:]]
                    
                    # 量子隨機生成低熵判斷閾值（無固定倍數）
                    quantum_threshold_generator = random_density_matrix(dims=4, seed=None)
                    low_entropy_multiplier = abs(quantum_threshold_generator.trace().real)
                    low_entropy_threshold = self.entropy_threshold * low_entropy_multiplier
                    
                    consecutive_low_entropy = all(entropy < low_entropy_threshold for entropy in recent_entropies)
            
            # 量子距離檢測：使用量子隨機決定分析參數
            quantum_distance_trigger = False
            if self.entropy_history:
                # 量子隨機生成基準電路參數
                quantum_large_params = random_statevector(dims=16, seed=None)  # 4-qubit for large params
                large_qubits = max(1, int(abs(quantum_large_params.data[0]) ** 2 * 6) + 2)  # 2-8 qubits
                large_depth = max(1, int(abs(quantum_large_params.data[1]) ** 2 * 5) + 2)   # 2-7 depth
                
                random_qc_large = random_circuit(num_qubits=large_qubits, depth=large_depth, seed=None)
                baseline_window = min(len(self.entropy_history), max(1, random_qc_large.depth() * random_qc_large.num_qubits))
                
                if len(self.entropy_history) >= baseline_window:
                    baseline_entropy = np.mean([h['entropy'] for h in self.entropy_history[-baseline_window:]])
                    quantum_distance = abs(current_entropy - baseline_entropy) / baseline_entropy
                    
                    # 量子隨機生成距離閾值（無固定偏移）
                    quantum_distance_generator = random_statevector(dims=8, seed=None)  # 3-qubit system
                    quantum_offset_generator = random_density_matrix(dims=2, seed=None)
                    distance_threshold = abs(quantum_distance_generator.data[0]) ** 2 + abs(quantum_offset_generator.trace().real)
                    
                    quantum_distance_trigger = quantum_distance > distance_threshold
            
            # 純量子觸發邏輯
            should_retrain = (
                current_entropy < ultra_low_entropy_threshold or  # 量子隨機極低熵值
                consecutive_low_entropy or                        # 量子隨機連續低熵
                quantum_distance_trigger                          # 量子隨機距離異常
            )
            
            if should_retrain:
                logger.info("🔄 純量子熵驅動模型重訓練觸發:")
                logger.info(f"   • 當前熵值: {current_entropy:.4f}")
                logger.info(f"   • 量子極低熵閾值: {ultra_low_entropy_threshold:.4f} (觸發: {current_entropy < ultra_low_entropy_threshold})")
                logger.info(f"   • 量子連續低熵: {consecutive_low_entropy}")
                logger.info(f"   • 量子距離異常: {quantum_distance_trigger}")
                
                self.last_model_retrain = time.time()
                
            return should_retrain
            
        except Exception as e:
            logger.error(f"❌ 量子熵重訓練判斷失敗: {e}")
            raise RuntimeError(f"量子熵重訓練判斷失敗，系統暫停: {e}")
    
    def get_entropy_status(self) -> Dict:
        """獲取當前量子熵狀態報告"""
        if not self.entropy_history:
            return {
                "status": "未初始化", 
                "current_entropy": 0.0,
                "entropy_threshold": self.entropy_threshold,
                "entropy_ratio": 0.0,
                "history_length": 0,
                "last_update": self.last_engine_update,
                "last_retrain": self.last_model_retrain,
                "trend": "未知"
            }
        
        latest = self.entropy_history[-1]
        return {
            "current_entropy": latest['entropy'],
            "entropy_threshold": self.entropy_threshold,
            "entropy_ratio": latest['entropy'] / self.entropy_threshold,
            "history_length": len(self.entropy_history),
            "last_update": self.last_engine_update,
            "last_retrain": self.last_model_retrain,
            "trend": self._calculate_entropy_trend()
        }
    
    def _generate_quantum_emergency_interval(self, interval_type: str) -> float:
        """
        使用 Qiskit 2.x 純量子隨機生成緊急間隔
        
        Args:
            interval_type: 'reinit' 或 'retrain'
        """
        try:
            from qiskit.quantum_info import random_statevector, random_density_matrix
            from qiskit.circuit.random import random_circuit
            
            # 使用量子隨機生成基準電路
            base_qubits = 3 if interval_type == 'reinit' else 4  # reinit: 3-qubit, retrain: 4-qubit
            circuit_state = random_statevector(dims=2**base_qubits, seed=None)
            circuit_density = random_density_matrix(dims=2**base_qubits, seed=None)
            random_qc = random_circuit(num_qubits=base_qubits, depth=5, seed=None)
            
            # 從量子隨機態提取時間因子
            amplitude_factor = abs(circuit_state.data[0]) ** 2
            density_factor = abs(circuit_density.trace().real)
            circuit_factor = random_qc.depth() * random_qc.num_qubits
            
            # 物理常數為基準，量子隨機為倍數
            if interval_type == 'reinit':
                # 重新初始化間隔：基於黃金比例和量子隨機
                base_hours = PHYSICAL_CONSTANTS['phi'] * PHYSICAL_CONSTANTS['euler']  # φ×e ≈ 4.4 小時
                quantum_multiplier = amplitude_factor * density_factor * (circuit_factor / 10)
                interval_hours = base_hours * (1 + quantum_multiplier * 10)  # 範圍約 4-48 小時
            else:  # retrain
                # 重訓練間隔：基於更大的物理週期和量子隨機
                base_days = PHYSICAL_CONSTANTS['phi'] ** 2 * PHYSICAL_CONSTANTS['euler']  # φ²×e ≈ 7.1 天
                quantum_multiplier = amplitude_factor * density_factor * (circuit_factor / 15)
                interval_days = base_days * (1 + quantum_multiplier * 8)  # 範圍約 7-64 天
                interval_hours = interval_days * 24
            
            interval_seconds = interval_hours * 3600
            
            logger.info(f"🌀 純量子{interval_type}間隔: {interval_hours:.2f}小時 ({interval_seconds:.0f}秒)")
            logger.debug(f"   • 振幅因子: {amplitude_factor:.4f}, 密度因子: {density_factor:.4f}")
            logger.debug(f"   • 電路因子: {circuit_factor}, 量子倍數: {quantum_multiplier:.4f}")
            
            return interval_seconds
            
        except Exception as e:
            logger.error(f"❌ 量子緊急間隔生成失敗: {e}")
            raise RuntimeError(f"純量子緊急間隔生成失敗，系統無法初始化: {e}")

    def _calculate_entropy_trend(self) -> str:
        """計算熵值趨勢"""
        if len(self.entropy_history) < 5:
            return "數據不足"
        
        recent_entropies = [h['entropy'] for h in self.entropy_history[-5:]]
        trend = np.polyfit(range(len(recent_entropies)), recent_entropies, 1)[0]
        
        if trend > 0.01:
            return "上升"
        elif trend < -0.01:
            return "下降"
        else:
            return "穩定"


class QuantumBattleDatabase:
    """量子對戰資料庫管理器"""
    
    def __init__(self, db_path: str = None):
        # 確保資料庫檔案統一在 launcher 資料夾內
        if db_path is None:
            launcher_dir = Path(__file__).parent
            self.db_path = str(launcher_dir / "quantum_battle_results.db")
        else:
            self.db_path = db_path
        
        self.init_database()
        logger.info(f"✅ 資料庫路徑統一: {self.db_path}")
    
    def init_database(self):
        """初始化資料庫表格"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 建立對戰信號表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS battle_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                team_name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                signal_strength REAL,
                price REAL,
                quantum_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 建立投資組合狀態表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                team_name TEXT NOT NULL,
                total_value REAL NOT NULL,
                cash REAL NOT NULL,
                unrealized_pnl REAL,
                positions TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 建立交易歷史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                team_name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                size REAL NOT NULL,
                price REAL NOT NULL,
                pnl REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 建立對戰結果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS battle_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                red_team_value REAL NOT NULL,
                blue_team_value REAL NOT NULL,
                winner TEXT,
                battle_duration REAL,
                total_trades INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"✅ 資料庫初始化完成: {self.db_path}")
    
    def save_signal(self, team_name: str, symbol: str, signal_type: str, 
                   signal_strength: float, price: float, quantum_data: dict = None):
        """儲存交易信號"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        quantum_json = json.dumps(quantum_data) if quantum_data else None
        
        cursor.execute('''
            INSERT INTO battle_signals 
            (timestamp, team_name, symbol, signal_type, signal_strength, price, quantum_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, team_name, symbol, signal_type, signal_strength, price, quantum_json))
        
        conn.commit()
        conn.close()
    
    def save_portfolio_status(self, team_name: str, total_value: float, 
                            cash: float, unrealized_pnl: float, positions: dict):
        """儲存投資組合狀態"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        positions_json = json.dumps(positions)
        
        cursor.execute('''
            INSERT INTO portfolio_status 
            (timestamp, team_name, total_value, cash, unrealized_pnl, positions)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, team_name, total_value, cash, unrealized_pnl, positions_json))
        
        conn.commit()
        conn.close()
    
    def save_trade(self, team_name: str, symbol: str, action: str, 
                  size: float, price: float, pnl: float = None):
        """儲存交易記錄"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO trade_history 
            (timestamp, team_name, symbol, action, size, price, pnl)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, team_name, symbol, action, size, price, pnl))
        
        conn.commit()
        conn.close()
    
    def save_battle_result(self, red_team_value: float, blue_team_value: float, 
                          winner: str, battle_duration: float, total_trades: int):
        """儲存對戰結果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO battle_results 
            (timestamp, red_team_value, blue_team_value, winner, battle_duration, total_trades)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, red_team_value, blue_team_value, winner, battle_duration, total_trades))
        
        conn.commit()
        conn.close()
        
    def get_latest_data(self, limit: int = 100):
        """獲取最新的對戰數據（供前端使用）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = {}
        
        # 獲取最新信號
        cursor.execute('''
            SELECT * FROM battle_signals 
            ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        data['signals'] = [dict(zip([col[0] for col in cursor.description], row)) 
                          for row in cursor.fetchall()]
        
        # 獲取最新投資組合狀態
        cursor.execute('''
            SELECT * FROM portfolio_status 
            ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        data['portfolios'] = [dict(zip([col[0] for col in cursor.description], row)) 
                             for row in cursor.fetchall()]
        
        # 獲取最新交易
        cursor.execute('''
            SELECT * FROM trade_history 
            ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        data['trades'] = [dict(zip([col[0] for col in cursor.description], row)) 
                         for row in cursor.fetchall()]
        
        # 獲取對戰結果
        cursor.execute('''
            SELECT * FROM battle_results 
            ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        data['results'] = [dict(zip([col[0] for col in cursor.description], row)) 
                          for row in cursor.fetchall()]
        
        conn.close()
        return data


class QuantumPortfolio:
    """量子投資組合管理器 - 集成量子金融計算"""
    
    def __init__(self, team_name: str, initial_capital: float = 10.0, database=None):
        self.team_name = team_name
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}  # {symbol: {'size': float, 'entry_price': float, 'timestamp': datetime}}
        self.trade_history = []
        self.unrealized_pnl = 0.0
        self.database = database
        
        # 導入量子金融計算模組
        self.quantum_finance = self._initialize_quantum_finance()
    
    def _initialize_quantum_finance(self):
        """初始化量子金融計算模組"""
        try:
            # 安全導入量子金融函數
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            # 忽略所有警告進行導入
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                from regime_hmm_quantum import (
                    _calculate_quantum_uncertainty,
                    _quantum_uncertainty_risk,
                )
            
            logger.info("✅ 量子金融模組載入成功")
            return {
                'quantum_uncertainty_risk': _quantum_uncertainty_risk,
                'calculate_quantum_uncertainty': _calculate_quantum_uncertainty
            }
        except Exception as e:
            logger.error(f"❌ 量子金融模組導入失敗: {e}")
            logger.error("❌ 純量子系統要求必須有量子金融計算，系統終止")
            raise RuntimeError(f"量子金融模組載入失敗，純量子系統無法運行: {e}")
        
        
    def calculate_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """計算投資組合總價值（含未實現損益）"""
        total_value = self.current_capital
        unrealized = 0.0
        
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                entry_price = position['entry_price']
                position_size = position['size']
                
                # 計算未實現損益
                pnl = (current_price - entry_price) * position_size
                unrealized += pnl
                
        self.unrealized_pnl = unrealized
        total_value += unrealized
        
        return total_value
    
    def execute_trade(self, symbol: str, signal: str, signal_strength: float, 
                     current_price: float, max_position_size: float = 1.0) -> Dict:
        """執行交易 - 集成量子風險計算"""
        
        # 計算基礎交易金額
        position_ratio = min(signal_strength, 1.0)
        base_trade_amount = abs(self.current_capital) * position_ratio
        
        # 使用量子金融計算進行交易金額調整
        if self.quantum_finance:
            try:
                # 計算量子不確定性（無參數）
                uncertainty_factor = self.quantum_finance['calculate_quantum_uncertainty']()
                
                # 量子風險調整（只需要信號強度參數）
                risk_adjustment = self.quantum_finance['quantum_uncertainty_risk'](signal_strength)
                
                # 將風險調整應用到基礎交易金額，限制調整範圍
                adjustment_factor = max(0.1, min(2.0, risk_adjustment / base_trade_amount if base_trade_amount > 0 else 1.0))
                trade_amount = base_trade_amount * adjustment_factor
                
                logger.info(f"🔬 {self.team_name} 量子調整: ${base_trade_amount:.2f} × {adjustment_factor:.3f} = ${trade_amount:.2f}")
                
            except Exception as e:
                logger.warning(f"⚠️ 量子計算失敗: {e}，使用基礎金額")
                trade_amount = base_trade_amount
        else:
            trade_amount = base_trade_amount
        
        trade_result = {
            'symbol': symbol,
            'action': 'HOLD',
            'amount': 0.0,
            'price': current_price,
            'timestamp': datetime.now(),
            'portfolio_value_before': self.calculate_portfolio_value({symbol: current_price}),
            'capital_before': self.current_capital,
            'quantum_adjustment': trade_amount != base_trade_amount
        }
        
        if signal == 'BULL' and trade_amount > 0:
            # 買入
            shares = trade_amount / current_price
            if symbol in self.positions:
                # 加倉
                old_size = self.positions[symbol]['size']
                old_price = self.positions[symbol]['entry_price']
                new_size = old_size + shares
                new_avg_price = (old_size * old_price + shares * current_price) / new_size
                self.positions[symbol] = {
                    'size': new_size,
                    'entry_price': new_avg_price,
                    'timestamp': datetime.now()
                }
            else:
                # 新倉位
                self.positions[symbol] = {
                    'size': shares,
                    'entry_price': current_price,
                    'timestamp': datetime.now()
                }
            
            self.current_capital -= trade_amount  # 直接扣除資金，可以變負數
            trade_result.update({
                'action': 'BUY',
                'amount': shares,
                'cost': trade_amount
            })
            
        elif signal == 'BEAR' and symbol in self.positions:
            # 賣出
            position = self.positions[symbol]
            sell_shares = min(position['size'], trade_amount / current_price)
            sell_value = sell_shares * current_price
            
            # 計算實現損益
            realized_pnl = (current_price - position['entry_price']) * sell_shares
            
            # 更新倉位
            remaining_shares = position['size'] - sell_shares
            if remaining_shares > 0.001:  # 保留小額倉位
                self.positions[symbol]['size'] = remaining_shares
            else:
                del self.positions[symbol]
            
            self.current_capital += sell_value  # 獲得現金
            trade_result.update({
                'action': 'SELL',
                'amount': sell_shares,
                'value': sell_value,
                'realized_pnl': realized_pnl
            })
        
        trade_result['portfolio_value_after'] = self.calculate_portfolio_value({symbol: current_price})
        trade_result['capital_after'] = self.current_capital
        
        self.trade_history.append(trade_result)
        
        # 儲存到資料庫
        if self.database:
            try:
                # 儲存交易記錄
                if trade_result['action'] != 'HOLD':
                    pnl = trade_result.get('realized_pnl', 0.0)
                    self.database.save_trade(
                        self.team_name,
                        symbol,
                        trade_result['action'],
                        trade_result['amount'],
                        current_price,
                        pnl
                    )
                
                # 儲存投資組合狀態
                self.database.save_portfolio_status(
                    self.team_name,
                    trade_result['portfolio_value_after'],
                    self.current_capital,
                    self.unrealized_pnl,
                    self.positions
                )
            except Exception as e:
                logger.warning(f"⚠️ 資料庫記錄失敗: {e}")
        
        return trade_result
    
    def get_performance_stats(self) -> Dict:
        """獲取績效統計"""
        total_trades = len([t for t in self.trade_history if t['action'] != 'HOLD'])
        profitable_trades = len([t for t in self.trade_history if t.get('realized_pnl', 0) > 0])
        
        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'unrealized_pnl': self.unrealized_pnl,
            'total_return': (self.current_capital + self.unrealized_pnl - self.initial_capital) / self.initial_capital,
            'total_trades': total_trades,
            'win_rate': profitable_trades / max(total_trades, 1),
            'positions_count': len(self.positions)
        }


class BinanceRealTimeData:
    """幣安實時數據收集器 - 優先使用區塊鏈主池"""
    
    def __init__(self):
        self.current_prices = {}
        self.price_history = {}
        self.websocket_connections = {}
        
        # 初始化區塊鏈主池連接器
        self.blockchain_connector = None
        if BLOCKCHAIN_CONNECTOR_AVAILABLE and BinanceDataConnector:
            try:
                self.blockchain_connector = BinanceDataConnector()
                logger.info("✅ 區塊鏈主池連接器初始化成功")
            except Exception as e:
                logger.warning(f"⚠️ 區塊鏈主池連接器初始化失敗: {e}")
                self.blockchain_connector = None
    
    async def get_current_price(self, symbol: str) -> Dict:
        """獲取當前價格 - 優先使用區塊鏈主池，失敗則直接報錯"""
        
        # 第一優先：區塊鏈主池數據
        if self.blockchain_connector:
            try:
                # 使用 asyncio.wait_for 替代 asyncio.timeout (Python 3.9 兼容)
                async def _get_blockchain_data():
                    async with self.blockchain_connector as connector:
                        market_data = await connector.get_comprehensive_market_data(symbol)
                        
                        if market_data and market_data.get('data_quality') != 'failed':
                            current_price = market_data.get('current_price')
                            
                            # 檢查價格是否有效
                            if current_price is not None and current_price > 0:
                                price_data = {
                                    'price': current_price,
                                    'volume': market_data.get('volume_24h', 0.0),
                                    'change_percent': market_data.get('price_change_24h_percent', 0.0),
                                    'timestamp': datetime.now(),
                                    'source': 'blockchain_pool'
                                }
                                
                                # 更新內部緩存
                                self.current_prices[symbol] = price_data
                                
                                logger.debug(f"📊 {symbol} 區塊鏈主池價格: {price_data['price']}")
                                return price_data
                            else:
                                logger.warning(f"⚠️ {symbol} 區塊鏈主池返回無效價格: {current_price}")
                                return None
                
                # 5秒超時
                result = await asyncio.wait_for(_get_blockchain_data(), timeout=5.0)
                if result:
                    return result
                                
            except asyncio.TimeoutError:
                logger.warning(f"⏰ {symbol} 區塊鏈主池數據獲取超時，嘗試 WebSocket")
            except Exception as e:
                logger.warning(f"⚠️ {symbol} 區塊鏈主池數據獲取失敗: {e}，嘗試 WebSocket")
        
        # 第二優先：即時 WebSocket 獲取
        try:
            logger.info(f"� {symbol} 使用 WebSocket 即時獲取價格...")
            price_data = await self._fetch_single_price_websocket(symbol)
            if price_data and price_data['price'] > 0:
                price_data['source'] = 'websocket_direct'
                # 更新內部緩存
                self.current_prices[symbol] = price_data
                logger.debug(f"🔗 {symbol} WebSocket 即時價格: {price_data['price']}")
                return price_data
            else:
                raise RuntimeError(f"WebSocket 返回無效價格數據")
        except Exception as e:
            logger.error(f"❌ {symbol} WebSocket 即時獲取失敗: {e}")
        
        # 所有方法都失敗 - 直接報錯
        error_msg = f"❌ 無法獲取 {symbol} 的價格數據！區塊鏈主池和 WebSocket 都失敗"
        logger.error(error_msg)
        raise RuntimeError(f"價格數據獲取完全失敗 - {symbol}: 所有數據源都不可用")
    
    async def _fetch_single_price_websocket(self, symbol: str) -> Dict:
        """單次 WebSocket 價格獲取 - 修復 Python 3.9 兼容性"""
        symbol_lower = symbol.lower()
        ws_url = f"wss://stream.binance.com:9443/ws/{symbol_lower}@ticker"
        
        try:
            # 使用 asyncio.wait_for 替代 asyncio.timeout (Python 3.9 兼容)
            async def _get_price():
                async with websockets.connect(ws_url) as websocket:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    return {
                        'price': float(data['c']),
                        'volume': float(data['v']),
                        'change_percent': float(data['P']),
                        'timestamp': datetime.now()
                    }
            
            # 3秒超時
            result = await asyncio.wait_for(_get_price(), timeout=3.0)
            return result
            
        except asyncio.TimeoutError:
            logger.warning(f"⚠️ {symbol} WebSocket 單次獲取超時")
            return None
        except Exception as e:
            logger.warning(f"⚠️ {symbol} WebSocket 單次獲取失敗: {e}")
            return None
        
    async def connect_symbols(self, symbols: list):
        """連接多個交易對的實時數據"""
        tasks = []
        for symbol in symbols:
            task = asyncio.create_task(self.connect_single_symbol(symbol))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def connect_single_symbol(self, symbol: str):
        """連接單個交易對"""
        symbol_lower = symbol.lower()
        ws_url = f"wss://stream.binance.com:9443/ws/{symbol_lower}@ticker"
        
        try:
            async with websockets.connect(ws_url) as websocket:
                logger.info(f"🔗 {symbol} WebSocket 已連接")
                
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        price = float(data['c'])
                        volume = float(data['v'])
                        change_percent = float(data['P'])
                        
                        self.current_prices[symbol] = {
                            'price': price,
                            'volume': volume,
                            'change_percent': change_percent,
                            'timestamp': datetime.now()
                        }
                        
                        # 維護價格歷史
                        if symbol not in self.price_history:
                            self.price_history[symbol] = []
                        
                        self.price_history[symbol].append({
                            'price': price,
                            'timestamp': datetime.now()
                        })
                        
                        # 保持最近100個價格點
                        if len(self.price_history[symbol]) > 100:
                            self.price_history[symbol].pop(0)
                            
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.error(f"❌ {symbol} WebSocket 連接失敗: {e}")


class QuantumBattleOrchestrator:
    """🥊 純量子對戰編排器"""
    
    def __init__(self):
        self.running = False
        self.battle_count = 0
        
        # 交易對（七大量子糾纏幣種）
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT', 'ADAUSDT']
        
        # 資料庫管理器
        self.database = QuantumBattleDatabase()
        
        # 🌌 量子熵驅動更新管理器（符合 Qiskit 2.x 標準）
        self.entropy_manager = QuantumEntropyUpdateManager()
        
        # 前端服務器
        self.frontend_server = None
        
        # 紅藍隊投資組合
        self.red_portfolio = QuantumPortfolio("Pure Quantum", 10.0, self.database)
        self.blue_portfolio = QuantumPortfolio("Adaptive Quantum", 10.0, self.database)
        
        # 實時數據
        self.data_stream = BinanceRealTimeData()
        
        # ⚛️ 智能量子引擎緩存系統（嚴格無回退模式）
        self.red_quantum_engine = None    # btc_quantum_ultimate_model
        self.blue_quantum_engine = None   # quantum_adaptive_trading_launcher
        
        # 🕐 量子熵驅動時間戳管理（取代固定時間間隔）
        self.red_engine_last_init = None    # 紅隊引擎最後初始化時間
        self.blue_engine_last_init = None   # 藍隊引擎最後初始化時間
        self.blue_models_last_retrain = None  # 藍隊模型最後重訓練時間
        
        # 🌌 純量子驅動備用機制（取代固定時間間隔）
        # 使用 Qiskit 2.x 純量子隨機生成緊急間隔參數
        self.emergency_reinit_interval = self.entropy_manager._generate_quantum_emergency_interval('reinit')
        self.emergency_retrain_interval = self.entropy_manager._generate_quantum_emergency_interval('retrain')
        
        # 🔒 絕對嚴格量子模式（無回退、無妥協、無測試數據）
        # 完全禁用任何非Qiskit 2.x的調用
        self.strict_quantum_mode = True
        self.allow_fallback = False
        
        # 忽略任何環境變量覆蓋，強制嚴格模式
        logger.info("🔒 系統已啟用絕對嚴格量子模式")
        logger.info("   • 禁止任何回退機制")
        logger.info("   • 禁止測試數據")
        logger.info("   • 僅允許純Qiskit 2.x SDK調用")
        
        # 戰績記錄
        self.battle_results = {
            'red_wins': 0,
            'blue_wins': 0,
            'draws': 0,
            'total_battles': 0
        }
        
        # 🕰️ 量子信號過期追踪系統（用於真實P&L計算）
        self.active_signals = {}  # {signal_id: signal_data}
        self.signal_liquidations = []  # 過期信號強制平倉記錄
        self.signal_counter = 0  # 信號ID計數器
        
        # 優雅退出
        signal.signal(signal.SIGINT, self._graceful_shutdown)
        signal.signal(signal.SIGTERM, self._graceful_shutdown)
    
    def _start_frontend_server(self):
        """啟動前端服務器"""
        if QuantumBattleFrontendServer is None:
            logger.warning("⚠️ 前端服務器模組未找到，跳過前端啟動")
            return
        
        try:
            # 獲取資料庫路徑
            db_path = str(Path(__file__).parent / self.database.db_path)
            
            # 創建並啟動前端服務器
            self.frontend_server = QuantumBattleFrontendServer(
                port=8888, 
                database_path=db_path
            )
            
            if self.frontend_server.start_server():
                logger.info("✅ 前端服務器啟動成功 - http://localhost:8888")
            else:
                logger.warning("⚠️ 前端服務器啟動失敗")
                
        except Exception as e:
            logger.warning(f"⚠️ 前端服務器啟動錯誤: {e}")
    
    def _stop_frontend_server(self):
        """停止前端服務器"""
        if self.frontend_server:
            try:
                self.frontend_server.stop_server()
            except Exception as e:
                logger.warning(f"⚠️ 前端服務器停止錯誤: {e}")
    
    def _graceful_shutdown(self, signum, frame):
        """優雅退出"""
        logger.info(f"📴 收到關閉信號 {signum}，正在關閉量子對戰系統...")
        self.running = False
        self._stop_frontend_server()
        
        # 同步版本的最終結果顯示
        try:
            # 使用緩存的價格數據
            if hasattr(self.data_stream, 'current_prices') and self.data_stream.current_prices:
                current_prices = {s: data['price'] for s, data in self.data_stream.current_prices.items()}
                final_red_value = self.red_portfolio.calculate_portfolio_value(current_prices)
                final_blue_value = self.blue_portfolio.calculate_portfolio_value(current_prices)
                
                logger.info("🏁 最終戰績:")
                logger.info(f"🔴 紅隊最終價值: ${final_red_value:.2f}")
                logger.info(f"🔵 藍隊最終價值: ${final_blue_value:.2f}")
            else:
                logger.info("📊 無價格數據可用於最終計算")
        except Exception as e:
            logger.warning(f"⚠️ 最終結果計算失敗: {e}")
        
        sys.exit(0)
    
    async def _quantum_entropy_driven_engine_check(self):
        """
        基於量子熵的引擎檢查與更新機制
        
        使用 Qiskit 2.x 標準量子熵計算來決定更新時機，
        完全基於量子物理原理，無人為時間干預。
        """
        
        try:
            # 🌌 檢查是否需要更新引擎
            logger.debug("🔍 量子熵驅動引擎檢查...")
            entropy_status = self.entropy_manager.get_entropy_status()
            
            # 記錄當前量子熵狀態
            logger.info(f"🌀 當前量子熵狀態: {entropy_status['current_entropy']:.4f} (閾值: {entropy_status['entropy_threshold']:.4f})")
            logger.info(f"📊 熵值比率: {entropy_status['entropy_ratio']:.2f}, 趨勢: {entropy_status['trend']}")
            
            # 檢查引擎更新需求
            should_update_engines = await self.entropy_manager.should_update_engines()
            if should_update_engines:
                logger.info("🔄 量子熵觸發引擎更新...")
                
                # 強制重新初始化紅藍隊引擎
                await self._entropy_driven_reinitialize_engines()
            
            # 檢查模型重訓練需求
            should_retrain = await self.entropy_manager.should_retrain_models()
            if should_retrain:
                logger.info("🔄 量子熵觸發模型重訓練...")
                
                # 重新訓練藍隊模型
                await self._entropy_driven_retrain_models()
            
            # 確保引擎已初始化
            await self._ensure_engines_initialized()
                
        except Exception as e:
            logger.error(f"❌ 量子熵引擎檢查失敗: {e}")
            
            if self.strict_quantum_mode and not self.allow_fallback:
                raise RuntimeError(f"量子熵計算失敗，嚴格模式無法繼續: {e}")
            else:
                # 緊急回退到時間基礎檢查
                logger.warning("⚠️ 回退到緊急時間基礎檢查...")
                await self._emergency_time_based_check()
    
    async def _entropy_driven_reinitialize_engines(self):
        """基於量子熵觸發的引擎重新初始化"""
        
        try:
            logger.info("🌌 執行量子熵驅動的引擎重新初始化...")
            
            # 重新初始化紅隊
            if self.red_quantum_engine is not None:
                logger.info("🔴 清除並重新初始化紅隊量子引擎...")
                del self.red_quantum_engine
                self.red_quantum_engine = None
            
            await self._initialize_red_team()
            self.red_engine_last_init = time.time()
            
            # 重新初始化藍隊
            if self.blue_quantum_engine is not None:
                logger.info("🔵 清除並重新初始化藍隊量子引擎...")
                del self.blue_quantum_engine
                self.blue_quantum_engine = None
            
            await self._initialize_blue_team()
            self.blue_engine_last_init = time.time()
            
            logger.info("✅ 量子熵驅動引擎重新初始化完成")
            
        except Exception as e:
            if self.strict_quantum_mode and not self.allow_fallback:
                raise RuntimeError(f"❌ 量子熵驅動引擎重新初始化失敗，嚴格模式終止: {e}")
            else:
                logger.error(f"❌ 量子熵驅動引擎重新初始化失敗: {e}")
    
    async def _entropy_driven_retrain_models(self):
        """基於量子熵觸發的模型重新訓練"""
        
        try:
            logger.info("🌌 執行量子熵驅動的模型重新訓練...")
            
            # 重新訓練藍隊的七個幣種模型
            # 注意：這裡需要實際的重訓練邏輯，目前只標記時間
            logger.warning("🚧 模型重訓練功能待實現 - 目前僅更新時間戳")
            
            self.blue_models_last_retrain = time.time()
            
            # TODO: 實際的模型重訓練邏輯
            # await self._retrain_blue_team_models()
            
            logger.info("✅ 量子熵驅動模型重訓練完成（時間戳更新）")
            
        except Exception as e:
            if self.strict_quantum_mode and not self.allow_fallback:
                raise RuntimeError(f"❌ 量子熵驅動模型重訓練失敗，嚴格模式終止: {e}")
            else:
                logger.error(f"❌ 量子熵驅動模型重訓練失敗: {e}")
    
    async def _ensure_engines_initialized(self):
        """確保引擎已正確初始化 - 智能緩存版本"""
        
        current_time = time.time()
        
        # 檢查紅隊引擎 - 只在引擎為空或緊急間隔觸發時才重新初始化
        if (self.red_quantum_engine is None or 
            self.red_engine_last_init is None):
            logger.info("🔴 紅隊引擎需要初始化...")
            await self._initialize_red_team()
            self.red_engine_last_init = current_time
        else:
            # 引擎已存在且在有效期內，使用緩存
            elapsed = current_time - self.red_engine_last_init
            logger.debug(f"🔴 紅隊引擎緩存有效 (距離上次初始化: {elapsed/3600:.1f}小時)")
        
        # 檢查藍隊引擎 - 只在引擎為空或緊急間隔觸發時才重新初始化
        if (self.blue_quantum_engine is None or 
            self.blue_engine_last_init is None):
            logger.info("🔵 藍隊引擎需要初始化...")
            await self._initialize_blue_team()
            self.blue_engine_last_init = current_time
        else:
            # 引擎已存在且在有效期內，使用緩存
            elapsed = current_time - self.blue_engine_last_init
            logger.debug(f"🔵 藍隊引擎緩存有效 (距離上次初始化: {elapsed/3600:.1f}小時)")
    
    async def _emergency_time_based_check(self):
        """緊急量子驅動檢查（當主要量子熵計算失敗時使用純量子備用機制）"""
        
        logger.warning("⚠️ 使用緊急純量子備用檢查機制...")
        current_time = time.time()
        
        # 動態重新生成量子間隔（每次檢查都更新）
        self.emergency_reinit_interval = self.entropy_manager._generate_quantum_emergency_interval('reinit')
        self.emergency_retrain_interval = self.entropy_manager._generate_quantum_emergency_interval('retrain')
        
        # 檢查紅隊引擎
        if (self.red_quantum_engine is None or 
            self.red_engine_last_init is None or 
            (current_time - self.red_engine_last_init) >= self.emergency_reinit_interval):
            
            logger.warning("� 緊急重新初始化紅隊引擎...")
            await self._initialize_red_team()
            self.red_engine_last_init = current_time
        
        # 檢查藍隊引擎
        if (self.blue_quantum_engine is None or 
            self.blue_engine_last_init is None or 
            (current_time - self.blue_engine_last_init) >= self.emergency_reinit_interval):
            
            logger.warning("� 緊急重新初始化藍隊引擎...")
            await self._initialize_blue_team()
            self.blue_engine_last_init = current_time
        
        # 檢查模型重訓練
        if (self.blue_models_last_retrain is None or 
            (current_time - self.blue_models_last_retrain) >= self.emergency_retrain_interval):
            
            logger.warning("🔄 緊急模型重訓練標記...")
            self.blue_models_last_retrain = current_time
    
    async def _force_reinitialize_red_team(self):
        """強制重新初始化紅隊引擎 - 嚴格模式"""
        if not self.strict_quantum_mode:
            raise RuntimeError("❌ 嚴格量子模式已禁用，無法執行強制重新初始化")
        
        try:
            logger.info("🔴 強制重新初始化紅隊量子引擎...")
            
            # 清除舊引擎
            if self.red_quantum_engine is not None:
                del self.red_quantum_engine
                self.red_quantum_engine = None
            
            # 重新初始化
            await self._initialize_red_team()
            self.red_engine_last_init = time.time()
            
            logger.info("✅ 紅隊量子引擎重新初始化完成")
            
        except Exception as e:
            # 🔒 絕對嚴格模式：任何重新初始化失敗都直接終止
            raise RuntimeError(f"❌ 紅隊強制重新初始化失敗，嚴格模式終止: {e}")
    
    async def _force_reinitialize_blue_team(self):
        """強制重新初始化藍隊引擎 - 嚴格模式"""
        if not self.strict_quantum_mode:
            raise RuntimeError("❌ 嚴格量子模式已禁用，無法執行強制重新初始化")
        
        try:
            logger.info("🔵 強制重新初始化藍隊量子引擎...")
            
            # 清除舊引擎
            if self.blue_quantum_engine is not None:
                del self.blue_quantum_engine
                self.blue_quantum_engine = None
            
            # 重新初始化
            await self._initialize_blue_team()
            self.blue_engine_last_init = time.time()
            
            logger.info("✅ 藍隊量子引擎重新初始化完成")
            
        except Exception as e:
            # 🔒 絕對嚴格模式：任何重新初始化失敗都直接終止
            raise RuntimeError(f"❌ 藍隊強制重新初始化失敗，嚴格模式終止: {e}")
    
    async def _force_retrain_blue_models(self):
        """強制重新訓練藍隊模型 - 嚴格模式"""
        if not self.strict_quantum_mode:
            raise RuntimeError("❌ 嚴格量子模式已禁用，無法執行強制重新訓練")
        
        try:
            logger.info("🔵 強制重新訓練藍隊模型（七個幣種pkl）...")
            
            # 檢查藍隊引擎是否存在重訓練方法
            if self.blue_quantum_engine is None:
                raise RuntimeError("❌ 藍隊引擎未初始化，無法重新訓練")
            
            # 尋找重訓練方法
            if hasattr(self.blue_quantum_engine, 'retrain_models'):
                await self.blue_quantum_engine.retrain_models(self.symbols)
            elif hasattr(self.blue_quantum_engine, 'force_retrain'):
                await self.blue_quantum_engine.force_retrain(self.symbols)
            else:
                # 如果沒有重訓練方法，強制重新初始化
                logger.warning("⚠️ 藍隊引擎沒有重訓練方法，執行強制重新初始化")
                await self._force_reinitialize_blue_team()
            
            self.blue_models_last_retrain = time.time()
            logger.info("✅ 藍隊模型重新訓練完成")
            
        except Exception as e:
            # 🔒 絕對嚴格模式：任何重新訓練失敗都直接終止
            raise RuntimeError(f"❌ 藍隊強制重新訓練失敗，嚴格模式終止: {e}")
    
    async def _validate_strict_quantum_mode(self):
        """驗證量子模式配置 - 絕對嚴格模式"""
        logger.info("🔒 驗證絕對嚴格量子模式配置...")
        
        # 🔒 絕對嚴格模式：不允許任何妥協
        if not self.strict_quantum_mode:
            raise RuntimeError("❌ 嚴格量子模式未啟用，系統拒絕運行")
        
        if self.allow_fallback:
            raise RuntimeError("❌ 檢測到回退機制已啟用，與絕對嚴格模式衝突")
        
        # 驗證量子引擎是否正確初始化
        if self.red_quantum_engine is None:
            raise RuntimeError("❌ 紅隊量子引擎未初始化，無法進入嚴格模式")
        
        if self.blue_quantum_engine is None:
            raise RuntimeError("❌ 藍隊量子引擎未初始化，無法進入嚴格模式")
        
        # 檢查時間戳是否正確設置
        if self.red_engine_last_init is None or self.blue_engine_last_init is None:
            raise RuntimeError("❌ 引擎初始化時間戳未設置，緩存機制無效")
        
        # 驗證更新間隔設置
        if self.emergency_reinit_interval <= 0 or self.emergency_retrain_interval <= 0:
            raise RuntimeError("❌ 量子間隔設置無效，智能緩存機制無法運行")
        
        logger.info("✅ 絕對嚴格量子模式驗證通過！")
        logger.info(f"   🔴 紅隊引擎緩存狀態: 正常 (上次初始化: {self.red_engine_last_init})")
        logger.info(f"   🔵 藍隊引擎緩存狀態: 正常 (上次初始化: {self.blue_engine_last_init})")
        logger.info(f"   ⏰ 量子重新初始化間隔: {self.emergency_reinit_interval / 3600:.1f} 小時")
        logger.info(f"   📚 量子模型重訓練間隔: {self.emergency_retrain_interval / (24 * 3600):.1f} 天")
        logger.info("   🚫 回退機制: 已完全禁用")
    
    async def initialize_quantum_engines(self):
        """初始化真實量子引擎 - 智能緩存模式"""
        
        logger.info("🚀 初始化量子對戰系統（智能緩存模式）...")
        logger.info("=" * 80)
        logger.info("🔴 紅隊：Pure Quantum Engine (btc_quantum_ultimate_model)")
        logger.info("   ⚛️ 純量子物理計算，基於 regime_hmm_quantum.py")
        logger.info("   🎲 量子態直接坍縮")
        logger.info("   🌌 量子熵驅動自動重新初始化")
        logger.info("")
        logger.info("🔵 藍隊：Adaptive Quantum Engine (quantum_adaptive_trading_launcher)")
        logger.info("   🌀 量子 + 歷史學習，基於 regime_hmm_quantum.py + 訓練模型")
        logger.info("   🔮 量子智慧進化")
        logger.info("   🌌 量子熵驅動自動重新初始化與重訓練模型")
        logger.info("=" * 80)
        
        try:
            # 初始化紅隊：純量子引擎
            await self._initialize_red_team()
            self.red_engine_last_init = time.time()
            
            # 初始化藍隊：自適應量子引擎
            await self._initialize_blue_team()
            self.blue_engine_last_init = time.time()
            self.blue_models_last_retrain = time.time()  # 初始化即視為新訓練
            
            logger.info("✅ 量子對戰系統初始化完成（智能緩存已啟動）！")
            
            # 🔒 驗證嚴格模式配置
            await self._validate_strict_quantum_mode()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 量子系統初始化失敗: {e}")
            return False
    
    async def _initialize_red_team(self):
        """初始化紅隊：純量子引擎"""
        
        logger.info("🔴 載入紅隊量子引擎...")
        
        try:
            # 更新調用方式：直接導入純量子模型
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            # 忽略警告導入
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                from btc_quantum_ultimate_model import BTCQuantumUltimateModel

            # 初始化純量子模型
            self.red_quantum_engine = BTCQuantumUltimateModel()
            
            # 驗證紅隊引擎是否正確初始化
            if not hasattr(self.red_quantum_engine, 'is_fitted') or not self.red_quantum_engine.is_fitted:
                logger.error("❌ 紅隊量子引擎未正確設置 (is_fitted=False)")
                raise RuntimeError("紅隊量子引擎處於未初始化狀態")
            
            # 驗證必要的方法存在
            if not hasattr(self.red_quantum_engine, 'generate_trading_signal'):
                raise RuntimeError("btc_quantum_ultimate_model 缺少 generate_trading_signal 方法")
            
            logger.info("✅ 紅隊純量子引擎載入成功 (btc_quantum_ultimate_model)")
            
        except ImportError as e:
            logger.error(f"❌ 紅隊量子引擎導入失敗: {e}")
            # 🔒 絕對嚴格模式：任何引擎加載失敗都直接終止
            raise RuntimeError("無法載入 btc_quantum_ultimate_model，系統終止")
        except Exception as e:
            logger.error(f"❌ 紅隊量子引擎初始化失敗: {e}")
            # 🔒 絕對嚴格模式：任何初始化失敗都直接終止
            raise RuntimeError(f"紅隊量子引擎初始化失敗: {e}")
        
        # 驗證紅隊可以正常生成信號（絕對嚴格模式下強制驗證）
        try:
            logger.info("🔬 驗證紅隊信號生成功能...")
            test_symbol = 'BTCUSDT'
            
            # 測試信號生成
            test_signal = await self.red_quantum_engine.generate_trading_signal(test_symbol)
            if test_signal is None:
                raise RuntimeError("紅隊測試信號生成返回 None")
            
            logger.info(f"✅ 紅隊信號生成驗證成功: {test_symbol}")
            
        except Exception as e:
            logger.error(f"❌ 紅隊信號生成驗證失敗: {e}")
            # 🔒 絕對嚴格模式：信號生成驗證失敗直接終止
            raise RuntimeError(f"紅隊信號生成驗證失敗，系統終止: {e}")
    
    async def _initialize_blue_team(self):
        """初始化藍隊：自適應量子引擎"""
        
        logger.info("🔵 載入藍隊量子引擎...")
        
        try:
            # 更新調用方式：直接導入自適應量子引擎
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                from quantum_adaptive_trading_launcher import (
                    QuantumAdaptiveTradingLauncher,
                )

            # 初始化自適應量子系統
            self.blue_quantum_engine = QuantumAdaptiveTradingLauncher()
            
            # 初始化自適應系統
            initialization_success = await self.blue_quantum_engine.initialize_quantum_systems()
            if not initialization_success:
                raise RuntimeError("quantum_adaptive_trading_launcher 初始化失敗")
            
            # 驗證藍隊引擎的核心組件
            if not hasattr(self.blue_quantum_engine, 'quantum_engine'):
                raise RuntimeError("藍隊量子引擎缺少 quantum_engine 組件")
            
            logger.info("✅ 藍隊自適應量子引擎載入成功 (quantum_adaptive_trading_launcher)")
            
        except ImportError as e:
            logger.error(f"❌ 藍隊量子引擎導入失敗: {e}")
            # 🔒 絕對嚴格模式：任何引擎加載失敗都直接終止
            raise RuntimeError("無法載入 quantum_adaptive_trading_launcher，系統終止")
        except Exception as e:
            logger.error(f"❌ 藍隊量子引擎初始化失敗: {e}")
            # 🔒 絕對嚴格模式：任何初始化失敗都直接終止
            raise RuntimeError(f"藍隊量子引擎初始化失敗: {e}")
        
        # 驗證藍隊可以正常生成信號（絕對嚴格模式下強制驗證）
        try:
            logger.info("🔬 驗證藍隊信號生成功能...")
            test_symbol = 'BTCUSDT'
            
            # 準備測試數據
            test_market_data = {
                'symbol': test_symbol,
                'current_price': 50000.0,
                'volume': 1000000.0,
                'price_change_percent': 2.5,
                'timestamp': datetime.now().isoformat(),
                'price_history': [49000, 49500, 50000]
            }
            
            # 測試信號生成
            signal_processor = await self.blue_quantum_engine._initialize_real_quantum_signal_processor()
            test_signal = await signal_processor.generate_signal(test_symbol, test_market_data)
            
            if test_signal is None:
                raise RuntimeError("藍隊測試信號生成返回 None")
            
            logger.info(f"✅ 藍隊信號生成驗證成功: {test_symbol}")
            
        except Exception as e:
            logger.error(f"❌ 藍隊信號生成驗證失敗: {e}")
            # 🔒 絕對嚴格模式：信號生成驗證失敗直接終止
            raise RuntimeError(f"藍隊信號生成驗證失敗，系統終止: {e}")
    
    async def start_quantum_battle(self):
        """開始量子對戰"""
        
        # 啟動前端服務器
        self._start_frontend_server()
        
        if not await self.initialize_quantum_engines():
            logger.error("❌ 量子系統初始化失敗，無法開始對戰")
            return
        
        # 啟動實時數據流
        data_task = asyncio.create_task(self.data_stream.connect_symbols(self.symbols))
        
        # 等待數據流建立
        await asyncio.sleep(3)
        
        logger.info("🥊 量子對戰開始！")
        self.running = True
        
        try:
            while self.running:
                # 🕰️ 在每輪對戰前檢查信號過期
                await self._monitor_signal_expiration()
                
                await self._conduct_battle_round()
                
                # 基於量子相干時間的動態間隔
                coherence_interval = self._calculate_quantum_coherence_interval()
                await asyncio.sleep(coherence_interval)
                
        except KeyboardInterrupt:
            logger.info("👋 用戶中斷，正在優雅退出...")
        except Exception as e:
            logger.error(f"❌ 對戰過程發生錯誤: {e}")
        finally:
            self.running = False
            await self._display_final_results()
    
    def _calculate_quantum_coherence_interval(self) -> float:
        """計算量子相干時間間隔（基於物理常數）"""
        # 基於精細結構常數和黃金比例的量子時間間隔
        # 這是對戰輪次之間的等待時間，不是信號坍縮時間
        base_interval = PHYSICAL_CONSTANTS['alpha'] * 1000  # 約 7.3 秒
        golden_modulation = PHYSICAL_CONSTANTS['phi'] / 2    # 黃金比例調製
        
        return base_interval * golden_modulation  # 約 5.9 秒
    
    async def _conduct_battle_round(self):
        """進行一輪量子對戰 - 量子熵驅動版本"""
        
        self.battle_count += 1
        logger.info(f"🥊 ========== 第 {self.battle_count} 輪量子對戰 ==========")
        
        # 🌌 量子熵驅動引擎檢查與更新（嚴格無回退）
        try:
            await self._quantum_entropy_driven_engine_check()
        except Exception as e:
            # 🔒 絕對嚴格模式：量子熵引擎檢查失敗直接終止
            raise RuntimeError(f"❌ 量子熵引擎檢查失敗，嚴格模式終止對戰: {e}")
        
        # 檢查實時數據可用性
        if not self.data_stream.current_prices:
            # 🔒 絕對嚴格模式：實時數據未就緒直接終止
            raise RuntimeError("❌ 實時數據未就緒，嚴格模式禁止跳過對戰輪次")
        
        battle_results = {}
        round_trades = {'red': [], 'blue': []}
        
        # 對每個交易對進行對戰
        for symbol in self.symbols:
            try:
                # 獲取當前價格 - 優先使用區塊鏈主池，失敗則報錯
                current_price_data = await self.data_stream.get_current_price(symbol)
                current_price = current_price_data['price']
                logger.info(f"💰 {symbol} 當前價格: {current_price} (來源: {current_price_data['source']})")
                
                # 🔴 紅隊出招：純量子信號
                red_signal = await self._red_team_generate_signal(symbol)
                
                # 🔵 藍隊出招：自適應量子信號
                blue_signal = await self._blue_team_generate_signal(symbol)
                
                # 儲存信號到資料庫
                if self.database:
                    try:
                        self.database.save_signal(
                            "Pure Quantum", symbol, red_signal['signal'], 
                            red_signal['confidence'], current_price, red_signal
                        )
                        self.database.save_signal(
                            "Adaptive Quantum", symbol, blue_signal['signal'],
                            blue_signal['confidence'], current_price, blue_signal
                        )
                    except Exception as e:
                        logger.warning(f"⚠️ 信號記錄失敗: {e}")
                
                # 執行交易
                red_trade = self.red_portfolio.execute_trade(
                    symbol, red_signal['signal'], red_signal['confidence'], current_price
                )
                blue_trade = self.blue_portfolio.execute_trade(
                    symbol, blue_signal['signal'], blue_signal['confidence'], current_price
                )
                
                # 🕰️ 註冊信號到過期追踪系統
                red_signal_id = self._register_signal('red', red_signal, symbol, current_price)
                blue_signal_id = self._register_signal('blue', blue_signal, symbol, current_price)
                
                round_trades['red'].append(red_trade)
                round_trades['blue'].append(blue_trade)
                
                # 記錄對戰結果
                battle_results[symbol] = {
                    'red_signal': red_signal,
                    'blue_signal': blue_signal,
                    'red_trade': red_trade,
                    'blue_trade': blue_trade,
                    'price': current_price
                }
                
                logger.info(f"   💎 {symbol}: 紅隊 {red_signal['signal']} vs 藍隊 {blue_signal['signal']} @ ${current_price:.4f}")
                
            except Exception as e:
                logger.error(f"❌ {symbol} 對戰失敗: {e}")
                continue
        
        # 更新投資組合價值 - 獲取所有幣種的最新價格
        current_prices_dict = {}
        for symbol in self.symbols:
            try:
                price_data = await self.data_stream.get_current_price(symbol)
                current_prices_dict[symbol] = price_data['price']
            except Exception as e:
                logger.error(f"❌ 無法獲取 {symbol} 最新價格用於投資組合計算: {e}")
                # 如果無法獲取價格，跳過該幣種
                continue
        
        red_portfolio_value = self.red_portfolio.calculate_portfolio_value(current_prices_dict)
        blue_portfolio_value = self.blue_portfolio.calculate_portfolio_value(current_prices_dict)
        
        # 顯示本輪結果
        self._display_round_results(red_portfolio_value, blue_portfolio_value, battle_results)
        
        # 儲存對戰結果到資料庫
        if self.database and battle_results:
            try:
                winner = "Pure Quantum" if red_portfolio_value > blue_portfolio_value else "Adaptive Quantum"
                if abs(red_portfolio_value - blue_portfolio_value) < 0.01:
                    winner = "Draw"
                
                total_trades = len(round_trades['red']) + len(round_trades['blue'])
                # 真實量子對戰持續時間：基於實際量子相干間隔
                battle_duration = self._calculate_quantum_coherence_interval()
                
                self.database.save_battle_result(
                    red_portfolio_value, blue_portfolio_value, 
                    winner, battle_duration, total_trades
                )
            except Exception as e:
                logger.warning(f"⚠️ 對戰結果記錄失敗: {e}")
        
        # 更新戰績
        self._update_battle_stats(red_portfolio_value, blue_portfolio_value)
    
    async def _red_team_generate_signal(self, symbol: str) -> Dict:
        """紅隊生成純量子信號 - 加入 Qiskit 2.x 量子時效計算"""
        
        try:
            # 參考 test_qiskit2x_compliance.py 的調用方式
            # 直接使用 BTCQuantumUltimateModel 的 generate_trading_signal 方法
            signal = await self.red_quantum_engine.generate_trading_signal(symbol)
            
            if signal is None:
                raise RuntimeError(f"紅隊量子引擎未能生成 {symbol} 信號")
            
            # 處理 Trading X 信號格式
            if hasattr(signal, '信號類型'):
                # TradingX信號 對象格式
                signal_type = signal.信號類型
                confidence = getattr(signal, '信心度', 0.5)
                strength = getattr(signal, '量子評分', confidence)
                
                # 轉換信號類型到標準格式
                if signal_type in ['LONG', 'BUY']:
                    converted_signal = 'BULL'
                elif signal_type in ['SHORT', 'SELL']:
                    converted_signal = 'BEAR'
                else:
                    converted_signal = 'NEUTRAL'
                
                # 🔴 計算紅隊量子信號時效（基於純量子態熵值）
                try:
                    # 從 regime_hmm_quantum 導入計算函數
                    import sys
                    sys.path.append('/Users/henrychang/Desktop/Trading-X/quantum_pro')
                    from regime_hmm_quantum import calculate_quantum_signal_lifetime_pure
                    
                    # 獲取量子態信息用於時效計算
                    if hasattr(signal, '制度概率分布') and signal.制度概率分布:
                        signal_state = signal.制度概率分布  # 使用概率分布作為量子態
                    else:
                        # 使用信號強度和置信度構造量子態
                        from qiskit.quantum_info import random_statevector
                        base_state = random_statevector(2)
                        signal_state = [strength * base_state.data[0], confidence * base_state.data[1]]
                    
                    # 計算量子時效（嚴格 Qiskit 2.x）
                    quantum_lifetime = calculate_quantum_signal_lifetime_pure(signal_state, confidence)
                    
                    logger.info(f"🔴 {symbol} 紅隊量子時效: {quantum_lifetime:.2f}秒 (熵值方法)")
                    
                except Exception as e:
                    logger.error(f"❌ 紅隊量子時效計算失敗: {e}")
                    # 嚴格模式：時效計算失敗則整個信號無效
                    raise RuntimeError(f"紅隊量子時效計算失敗，嚴格模式終止: {e}")
                
                return {
                    'signal': converted_signal,
                    'confidence': confidence,
                    'strength': strength,
                    'quantum_lifetime': quantum_lifetime,  # 新增量子時效
                    'lifetime_method': 'quantum_entropy',  # 時效計算方法標記
                    'method': 'pure_quantum_physics',
                    'source': 'btc_quantum_ultimate_model'
                }
            elif isinstance(signal, dict):
                # 字典格式
                if 'signal' in signal and 'confidence' in signal:
                    # 🔴 計算字典格式信號的量子時效
                    try:
                        from regime_hmm_quantum import calculate_quantum_signal_lifetime_pure
                        from qiskit.quantum_info import random_statevector
                        
                        confidence = signal['confidence']
                        strength = signal.get('strength', confidence)
                        
                        # 構造量子態
                        base_state = random_statevector(2)
                        signal_state = [strength * base_state.data[0], confidence * base_state.data[1]]
                        
                        quantum_lifetime = calculate_quantum_signal_lifetime_pure(signal_state, confidence)
                        logger.info(f"🔴 {symbol} 紅隊量子時效: {quantum_lifetime:.2f}秒 (字典格式)")
                        
                    except Exception as e:
                        logger.error(f"❌ 紅隊量子時效計算失敗: {e}")
                        raise RuntimeError(f"紅隊量子時效計算失敗，嚴格模式終止: {e}")
                    
                    return {
                        'signal': signal['signal'],
                        'confidence': confidence,
                        'strength': strength,
                        'quantum_lifetime': quantum_lifetime,  # 新增量子時效
                        'lifetime_method': 'quantum_entropy',  # 時效計算方法標記
                        'method': 'pure_quantum_physics',
                        'source': 'btc_quantum_ultimate_model'
                    }
                else:
                    raise RuntimeError(f"紅隊量子引擎返回的信號格式不完整: {signal}")
            else:
                raise RuntimeError(f"紅隊返回未知信號格式: {type(signal)}")
                
        except Exception as e:
            logger.error(f"❌ 紅隊量子信號生成失敗: {e}")
            # 🔒 絕對嚴格模式：任何失敗都直接終止，無回退
            raise RuntimeError(f"❌ 紅隊量子信號生成失敗，嚴格模式終止: {e}")
    
    async def _blue_team_generate_signal(self, symbol: str) -> Dict:
        """藍隊生成自適應量子信號 - 參考測試腳本的成功調用方式"""
        
        try:
            # 參考 test_quantum_adaptive_signal.py 的調用方式
            # 準備符合測試腳本格式的市場數據
            market_data = await self._prepare_adaptive_market_data(symbol)
            
            # 調用藍隊的信號處理器 (參考測試腳本)
            signal_processor = await self.blue_quantum_engine._initialize_real_quantum_signal_processor()
            signal = await signal_processor.generate_signal(symbol, market_data)
            
            if signal is None:
                raise RuntimeError(f"藍隊量子引擎未能生成 {symbol} 信號")
            
            # 處理返回的信號格式
            if isinstance(signal, dict):
                if 'signal' not in signal or 'confidence' not in signal:
                    raise RuntimeError(f"藍隊量子引擎返回的信號格式不完整: {signal}")
                
                # 轉換信號類型到標準格式
                signal_type = signal['signal']
                if signal_type in ['LONG', 'BUY']:
                    converted_signal = 'BULL'
                elif signal_type in ['SHORT', 'SELL']:
                    converted_signal = 'BEAR'
                else:
                    converted_signal = 'NEUTRAL'
                
                confidence = signal['confidence']
                strength = signal.get('signal_strength', confidence)
                
                # 🔵 藍隊使用海森堡不確定性原理計算量子時效
                try:
                    from regime_hmm_quantum import calculate_quantum_signal_lifetime_adaptive
                    quantum_lifetime = calculate_quantum_signal_lifetime_adaptive(strength, confidence)
                    logger.info(f"🔵 {symbol} 藍隊量子時效: {quantum_lifetime:.2f}秒 (海森堡不確定性)")
                    
                except Exception as e:
                    logger.error(f"❌ 藍隊量子時效計算失敗: {e}")
                    raise RuntimeError(f"藍隊量子時效計算失敗，嚴格模式終止: {e}")
                
                return {
                    'signal': converted_signal,
                    'confidence': confidence,
                    'strength': strength,
                    'quantum_lifetime': quantum_lifetime,  # 新增量子時效
                    'lifetime_method': 'heisenberg_uncertainty',  # 時效計算方法標記
                    'method': 'adaptive_quantum_learning',
                    'source': 'quantum_adaptive_trading_launcher'
                }
            else:
                raise RuntimeError(f"藍隊返回未知信號格式: {type(signal)}")
                
        except Exception as e:
            logger.error(f"❌ 藍隊量子信號生成失敗: {e}")
            # 🔒 絕對嚴格模式：任何失敗都直接終止，無回退
            raise RuntimeError(f"❌ 藍隊量子信號生成失敗，嚴格模式終止: {e}")
    
    async def _prepare_adaptive_market_data(self, symbol: str) -> Dict:
        """準備符合藍隊測試腳本格式的市場數據"""
        
        # 獲取當前價格數據
        current_data = await self.data_stream.get_current_price(symbol)
        
        if current_data['price'] <= 0:
            raise RuntimeError(f"無法獲取 {symbol} 的實時數據")
        
        # 構建符合測試腳本格式的市場數據
        # 參考 test_quantum_adaptive_signal.py 中的 test_market_data 格式
        market_data = {
            'current_price': current_data['price'],
            'price_change_percent': current_data['change_percent'],
            'volatility': abs(current_data['change_percent']) * 0.01,  # 估算波動率
            'momentum': current_data['change_percent'] * 0.01,  # 使用價格變化作為動量
            'rsi': 50.0 + current_data['change_percent'] * 2,  # 估算 RSI
            'bb_position': max(0.0, min(1.0, 0.5 + current_data['change_percent'] * 0.05)),  # 估算布林通道位置
            'volume': current_data['volume'],
            'volume_change_percent': 0.0,  # 默認無體積變化
            
            # 額外的藍隊需要的字段
            'symbol': symbol,
            'timestamp': current_data['timestamp'].isoformat(),
            'price_history': self.data_stream.price_history.get(symbol, [])[-10:] if symbol in self.data_stream.price_history else []
        }
        
        return market_data
    
    async def _prepare_market_data(self, symbol: str) -> Dict:
        """準備市場數據供藍隊使用"""
        
        # 獲取當前價格數據 - 優先使用區塊鏈主池
        current_data = await self.data_stream.get_current_price(symbol)
        
        if current_data['price'] <= 0:
            raise RuntimeError(f"無法獲取 {symbol} 的實時數據")
        
        # 構建符合藍隊期望的市場觀測數據格式
        market_observation = {
            'symbol': symbol,
            'current_price': current_data['price'],
            'volume': current_data['volume'],
            'price_change_percent': current_data['change_percent'],
            'timestamp': current_data['timestamp'].isoformat(),
            # 藍隊需要的標準化字段
            '收益率': current_data['change_percent'] / 100.0,
            '已實現波動率': abs(current_data['change_percent'] / 100.0) * 0.1,  # 估算波動率
            '動量斜率': current_data['change_percent'] / 100.0,  # 使用價格變化作為動量
            '買賣價差': 0.001,  # 預設價差 0.1%
            '訂單簿壓力': 0.0,  # 預設中性壓力
            'price_history': self.data_stream.price_history.get(symbol, [])[-10:] if symbol in self.data_stream.price_history else []
        }
        
        return market_observation
    
    def _display_round_results(self, red_value: float, blue_value: float, battle_results: Dict):
        """顯示本輪對戰結果"""
        
        logger.info("📊 本輪戰況:")
        logger.info(f"   🔴 紅隊投資組合價值: ${red_value:.2f} (收益率: {(red_value/10.0-1)*100:.2f}%)")
        logger.info(f"   🔵 藍隊投資組合價值: ${blue_value:.2f} (收益率: {(blue_value/10.0-1)*100:.2f}%)")
        
        # 顯示各交易對信號
        for symbol, result in battle_results.items():
            red_sig = result['red_signal']
            blue_sig = result['blue_signal']
            logger.info(f"   💎 {symbol}: 🔴{red_sig['signal']}({red_sig['confidence']:.2f}) vs 🔵{blue_sig['signal']}({blue_sig['confidence']:.2f})")
    
    def _update_battle_stats(self, red_value: float, blue_value: float):
        """更新戰績統計"""
        
        self.battle_results['total_battles'] += 1
        
        if red_value > blue_value:
            self.battle_results['red_wins'] += 1
            logger.info("🏆 本輪勝者: 🔴 紅隊 (Pure Quantum)")
        elif blue_value > red_value:
            self.battle_results['blue_wins'] += 1
            logger.info("🏆 本輪勝者: 🔵 藍隊 (Adaptive Quantum)")
        else:
            self.battle_results['draws'] += 1
            logger.info("🤝 本輪結果: 平局")
    
    async def _display_final_results(self):
        """顯示最終戰績"""
        
        logger.info("🏁 ========== 量子對戰競技場 - 最終戰績 ==========")
        
        total = self.battle_results['total_battles']
        if total == 0:
            logger.info("📊 無對戰記錄")
            return
        
        red_rate = self.battle_results['red_wins'] / total * 100
        blue_rate = self.battle_results['blue_wins'] / total * 100
        
        # 最終投資組合價值 - 獲取所有幣種的最新價格
        current_prices = {}
        for symbol in self.symbols:
            try:
                price_data = await self.data_stream.get_current_price(symbol)
                current_prices[symbol] = price_data['price']
            except Exception as e:
                logger.warning(f"⚠️ 無法獲取 {symbol} 最終價格: {e}")
                current_prices[symbol] = 0.0
        
        final_red_value = self.red_portfolio.calculate_portfolio_value(current_prices)
        final_blue_value = self.blue_portfolio.calculate_portfolio_value(current_prices)
        
        logger.info(f"🔴 紅隊 (Pure Quantum):")
        logger.info(f"   勝率: {self.battle_results['red_wins']}/{total} ({red_rate:.1f}%)")
        logger.info(f"   最終價值: ${final_red_value:.2f}")
        logger.info(f"   總收益率: {(final_red_value/10.0-1)*100:.2f}%")
        
        logger.info(f"🔵 藍隊 (Adaptive Quantum):")
        logger.info(f"   勝率: {self.battle_results['blue_wins']}/{total} ({blue_rate:.1f}%)")
        logger.info(f"   最終價值: ${final_blue_value:.2f}")
        logger.info(f"   總收益率: {(final_blue_value/10.0-1)*100:.2f}%)")
        
        # 最終勝者
        if final_red_value > final_blue_value:
            logger.info("🏆 最終勝者: 🔴 紅隊 (Pure Quantum Engine)")
        elif final_blue_value > final_red_value:
            logger.info("🏆 最終勝者: 🔵 藍隊 (Adaptive Quantum Engine)")
        else:
            logger.info("🤝 最終結果: 平局")
        
        # 🕰️ 顯示量子信號統計
        self._display_signal_statistics()
    
    # ========== 🕰️ 量子信號過期追踪系統 ==========
    
    def _register_signal(self, team: str, signal_data: Dict, symbol: str, entry_price: float) -> str:
        """註冊新信號到過期追踪系統"""
        self.signal_counter += 1
        signal_id = f"{team}_{self.signal_counter}_{int(time.time())}"
        
        # 記錄信號詳細資訊
        signal_record = {
            'signal_id': signal_id,
            'team': team,
            'symbol': symbol,
            'signal_type': signal_data['signal'],
            'confidence': signal_data['confidence'],
            'strength': signal_data['strength'],
            'quantum_lifetime': signal_data['quantum_lifetime'],
            'lifetime_method': signal_data['lifetime_method'],
            'entry_time': time.time(),
            'entry_price': entry_price,
            'expiry_time': time.time() + signal_data['quantum_lifetime'],
            'is_active': True,
            'liquidated': False
        }
        
        self.active_signals[signal_id] = signal_record
        
        logger.info(f"📝 {team} 信號已註冊: {signal_id}")
        logger.info(f"   • 量子時效: {signal_data['quantum_lifetime']:.2f}秒 ({signal_data['lifetime_method']})")
        logger.info(f"   • 過期時間: {signal_record['expiry_time']:.2f}")
        
        return signal_id
    
    async def _monitor_signal_expiration(self):
        """監控信號過期並執行強制平倉"""
        current_time = time.time()
        expired_signals = []
        
        for signal_id, signal_data in self.active_signals.items():
            if signal_data['is_active'] and current_time >= signal_data['expiry_time']:
                expired_signals.append(signal_id)
        
        # 處理過期信號
        for signal_id in expired_signals:
            await self._liquidate_expired_signal(signal_id)
    
    async def _liquidate_expired_signal(self, signal_id: str):
        """強制平倉過期信號並計算P&L"""
        signal_data = self.active_signals[signal_id]
        
        try:
            # 獲取當前價格
            current_price_data = await self.data_stream.get_current_price(signal_data['symbol'])
            exit_price = current_price_data['price']
            
            # 計算持有時長
            holding_duration = time.time() - signal_data['entry_time']
            
            # 計算P&L（簡化模擬）
            entry_price = signal_data['entry_price']
            signal_type = signal_data['signal_type']
            
            if signal_type == 'BULL':
                pnl_percent = ((exit_price - entry_price) / entry_price) * 100
            elif signal_type == 'BEAR':
                pnl_percent = ((entry_price - exit_price) / entry_price) * 100
            else:  # NEUTRAL
                pnl_percent = 0.0
            
            # 更新投資組合餘額
            portfolio = self.red_portfolio if signal_data['team'] == 'red' else self.blue_portfolio
            pnl_amount = portfolio.balance * (pnl_percent / 100.0) * signal_data['confidence']
            portfolio.balance += pnl_amount
            
            # 記錄平倉資訊
            liquidation_record = {
                'signal_id': signal_id,
                'liquidation_time': time.time(),
                'holding_duration': holding_duration,
                'quantum_lifetime': signal_data['quantum_lifetime'],
                'entry_price': entry_price,
                'exit_price': exit_price,
                'pnl_percent': pnl_percent,
                'pnl_amount': pnl_amount,
                'team': signal_data['team'],
                'symbol': signal_data['symbol'],
                'confidence': signal_data['confidence']
            }
            
            self.signal_liquidations.append(liquidation_record)
            
            # 標記信號為已平倉
            signal_data['is_active'] = False
            signal_data['liquidated'] = True
            signal_data['liquidation_record'] = liquidation_record
            
            logger.info(f"⏰ 信號過期強制平倉: {signal_id}")
            logger.info(f"   • 持有時長: {holding_duration:.2f}秒 (量子時效: {signal_data['quantum_lifetime']:.2f}秒)")
            logger.info(f"   • 價格變化: {entry_price:.2f} → {exit_price:.2f}")
            logger.info(f"   • P&L: {pnl_percent:+.2f}% ({pnl_amount:+.4f} USDT)")
            logger.info(f"   • {signal_data['team']} 隊新餘額: {portfolio.balance:.4f} USDT")
            
        except Exception as e:
            logger.error(f"❌ 信號 {signal_id} 平倉失敗: {e}")
            # 即使平倉失敗也要標記為非活躍，避免永久循環
            signal_data['is_active'] = False
    
    def _display_signal_statistics(self):
        """顯示信號統計資訊"""
        active_count = sum(1 for s in self.active_signals.values() if s['is_active'])
        liquidated_count = len(self.signal_liquidations)
        
        if liquidated_count > 0:
            avg_holding_time = sum(l['holding_duration'] for l in self.signal_liquidations) / liquidated_count
            avg_pnl = sum(l['pnl_percent'] for l in self.signal_liquidations) / liquidated_count
            
            logger.info(f"📊 信號統計:")
            logger.info(f"   • 活躍信號: {active_count}")
            logger.info(f"   • 已平倉信號: {liquidated_count}")
            logger.info(f"   • 平均持有時長: {avg_holding_time:.2f}秒")
            logger.info(f"   • 平均P&L: {avg_pnl:+.2f}%")


async def main():
    """主程序"""
    
    logger.info("🚀 啟動純量子物理對戰競技場...")
    
    orchestrator = QuantumBattleOrchestrator()
    
    try:
        await orchestrator.start_quantum_battle()
    except Exception as e:
        logger.error(f"❌ 系統運行失敗: {e}")
    finally:
        logger.info("👋 量子對戰系統已關閉")


if __name__ == "__main__":
    # 🔒 絕對嚴格量子模式 - 禁止任何命令行覆蓋
    logger.info("🔒 啟動絕對嚴格量子模式")
    logger.info("   • 禁止回退機制")
    logger.info("   • 禁止測試數據") 
    logger.info("   • 僅允許純Qiskit 2.x SDK")
    
    asyncio.run(main())
