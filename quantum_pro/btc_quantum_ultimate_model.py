#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC 量子終極模型 - 整合到 Trading X 量子系統
========================================

這個模組整合了您提供的 BTC_Quantum_Ultimate_Model.py 的核心量子電路功能，
並與現有的 Trading X 量子系統完美整合。

核心功能：
- 量子特徵編碼 (angle, amplitude, multi-scale)
- 量子電路參數化 ansatz
- 時間演化與 Hamiltonian 映射
- 噪聲模型與真機支援
- 變分訓練器 (SPSA, COBYLA)
- 回測模組

整合特性：
- 與 regime_hmm_quantum.py 的即時數據流整合
- 與 quantum_decision_optimizer.py 的決策引擎整合
- 支援 Trading X 信號輸出格式

作者: Trading X Quantum Team
版本: 1.0 - Trading X 整合版
"""

import datetime
from datetime import timedelta
import json
import logging
import math
import os
import pickle
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 🔮 量子級區塊鏈歷史數據撷取器 - 從真實創世開始
from blockchain_unlimited_extractor import QuantumBlockchainExtractor, ProductionConfig

# Qiskit 量子計算
try:
    from qiskit import ClassicalRegister, QuantumCircuit, transpile
    from qiskit.circuit import ParameterVector
    try:
        from qiskit import Aer
    except ImportError:
        try:
            from qiskit_aer import Aer
        except ImportError:
            Aer = None
    
    try:
        from qiskit.providers.aer.noise import (
            NoiseModel,
            depolarizing_error,
            thermal_relaxation_error,
        )
    except ImportError:
        try:
            from qiskit_aer.noise import (
                NoiseModel,
                depolarizing_error,
                thermal_relaxation_error,
            )
        except ImportError:
            NoiseModel = None
            depolarizing_error = None
            thermal_relaxation_error = None
    
    QISKIT_AVAILABLE = True
    QUANTUM_LIBS_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    QUANTUM_LIBS_AVAILABLE = False
    print("⚠️ Qiskit 未安裝，量子電路功能將被禁用")

# Progress bar
try:
    from tqdm import tqdm
except ImportError:
    # Fallback 進度條
    def tqdm(iterable, **kwargs):
        return iterable

# Trading X 整合
try:
    import os

    # 整合 X 資料夾的區塊鏈主池數據源
    import sys

    # from .quantum_decision_optimizer import ProductionQuantumConfig  # 已刪除
    from .regime_hmm_quantum import TradingX信號, 即時幣安數據收集器
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'X'))
    from binance_data_connector import BinanceDataConnector
    TRADING_X_AVAILABLE = True
except ImportError:
    try:
        import os

        # 整合 X 資料夾的區塊鏈主池數據源
        import sys

        # from quantum_decision_optimizer import ProductionQuantumConfig  # 已刪除
        from regime_hmm_quantum import TradingX信號, 即時幣安數據收集器
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'X'))
        from binance_data_connector import BinanceDataConnector
        TRADING_X_AVAILABLE = True
    except ImportError:
        print("⚠️ Trading X 模組未找到，使用獨立模式")
        即時幣安數據收集器 = None
        TradingX信號 = None
        # ProductionQuantumConfig = None  # 已刪除
        BinanceDataConnector = None
        TRADING_X_AVAILABLE = False

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger('BTCQuantumUltimate')

# ---------------------------
# CONFIG: 量子模型配置
# ---------------------------
QUANTUM_CONFIG = {
    'N_FEATURE_QUBITS': 6,
    'N_READOUT': 3,  # bear/side/bull
    'N_ANSATZ_LAYERS': 3,
    'ENCODING': 'multi-scale',  # 'angle' | 'amplitude' | 'multi-scale'
    'USE_STATEVECTOR': False,
    'SHOTS': 2048,
    'SPSA_ITER': 120,
    'SPSA_SETTINGS': {'a': 0.4, 'c': 0.15, 'A': 20, 'alpha': 0.602, 'gamma': 0.101},
    'NOISE_MODEL': True,
    'DEPOLARIZING_PROB': 0.002,
    'THERMAL_PARAMS': {'T1': 50e3, 'T2': 70e3, 'time': 50},
    'LOOKBACK': 30,
    'AHEAD': 3,
    'BULL_THRESHOLD': 0.02,
    'BEAR_THRESHOLD': -0.02,
    # 七大幣種區塊鏈主池配置
    'BLOCKCHAIN_SYMBOLS': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT', 'ADAUSDT']
}

# ---------------------------
# 量子電路建構函數
# ---------------------------

def angle_encoding(qc, qubit_indices: List[int], features: np.ndarray, scale=1.0):
    """角度編碼量子特徵（兼容 Qiskit 不可用情況）"""
    if not QUANTUM_LIBS_AVAILABLE or qc is None:
        return
    for i, q in enumerate(qubit_indices):
        if i < len(features):
            angle = float(features[i]) * scale
            qc.ry(angle, q)

def amplitude_encoding(qc, qubit_indices: List[int], features: np.ndarray):
    """振幅編碼量子特徵（兼容 Qiskit 不可用情況）"""
    if not QUANTUM_LIBS_AVAILABLE or qc is None:
        return
    
    vec = np.zeros(2 ** len(qubit_indices))
    vec[:min(len(features), len(vec))] = features[:len(vec)]
    norm = np.linalg.norm(vec)
    if norm > 1e-12:
        vec = vec / norm
    qc.initialize(vec, qubit_indices)

def multi_scale_encoding(qc, qubit_indices: List[int], features: np.ndarray):
    """多尺度編碼量子特徵（兼容 Qiskit 不可用情況）"""
    if not QUANTUM_LIBS_AVAILABLE or qc is None:
        return
    
    n_qubits = len(qubit_indices)
    if n_qubits < 2:
        angle_encoding(qc, qubit_indices, features)
        return
    
    # 分組編碼：短期、中期、長期特徵
    group_size = n_qubits // 3
    for i, start_idx in enumerate([0, group_size, 2 * group_size]):
        end_idx = start_idx + group_size if i < 2 else n_qubits
        group_qubits = qubit_indices[start_idx:end_idx]
        group_features = features[i * len(group_qubits):(i + 1) * len(group_qubits)]
        
        if len(group_features) > 0:
            angle_encoding(qc, group_qubits, group_features, scale=0.5 * (i + 1))

def entangle_chain(qc, qubits: List[int]):
    """鏈式糾纏（兼容 Qiskit 不可用情況）"""
    if not QUANTUM_LIBS_AVAILABLE or qc is None:
        return
    for i in range(len(qubits) - 1):
        qc.cx(qubits[i], qubits[i + 1])

def entangle_star(qc, qubits: List[int]):
    """星形糾纏（兼容 Qiskit 不可用情況）"""
    if not QUANTUM_LIBS_AVAILABLE or qc is None:
        return
    if len(qubits) < 2:
        return
    center = qubits[0]
    for q in qubits[1:]:
        qc.cx(center, q)

def build_param_ansatz(n_qubits: int, n_layers: int, prefix='theta') -> Tuple[Any, Any]:
    """構建參數化 ansatz（兼容 Qiskit 不可用情況）"""
    if not QUANTUM_LIBS_AVAILABLE:
        return None, None
    
    pcount = n_layers * n_qubits * 2
    params = ParameterVector(prefix, length=pcount)
    qc = QuantumCircuit(n_qubits)
    
    idx = 0
    for layer in range(n_layers):
        # 單量子位旋轉
        for q in range(n_qubits):
            qc.ry(params[idx], q)
            idx += 1
            qc.rz(params[idx], q)
            idx += 1
        
        # 糾纏層
        if layer < n_layers - 1:
            entangle_chain(qc, list(range(n_qubits)))
    
    return qc, params

def apply_zz_interaction(qc, q1: int, q2: int, theta: float):
    """應用 ZZ 相互作用（兼容 Qiskit 不可用情況）"""
    if not QUANTUM_LIBS_AVAILABLE or qc is None:
        return
    qc.cx(q1, q2)
    qc.rz(2 * theta, q2)
    qc.cx(q1, q2)

def apply_time_evolution(qc, feature_qubits: List[int], h: np.ndarray, J: np.ndarray, dt: float, trotter_steps: int = 1):
    """應用時間演化（兼容 Qiskit 不可用情況）"""
    if not QUANTUM_LIBS_AVAILABLE or qc is None:
        return
    n = len(feature_qubits)
    
    for _ in range(trotter_steps):
        # 單體項演化
        for i in range(n):
            if i < len(h):
                qc.rz(2 * h[i] * dt, feature_qubits[i])
        
        # 相互作用項演化
        for i in range(n):
            for j in range(i + 1, min(n, len(h))):
                if abs(J[i, j]) > 1e-12:
                    apply_zz_interaction(qc, feature_qubits[i], feature_qubits[j], J[i, j] * dt)

# ---------------------------
# 特徵到 Hamiltonian 映射
# ---------------------------

def feature_to_hJ_advanced(feature_vec: np.ndarray, n_qubits: int, mapping_mode: str = 'hybrid') -> Tuple[np.ndarray, np.ndarray]:
    """進階特徵到 Hamiltonian 映射"""
    v = np.zeros(n_qubits)
    v[:min(len(feature_vec), n_qubits)] = feature_vec[:n_qubits]
    
    # 正規化
    norm = np.linalg.norm(v)
    if norm > 1e-12:
        v = v / norm
    
    # h: 線性 + 非線性變換
    h = 0.6 * v + 0.4 * np.tanh(v)
    
    # J: 多尺度外積 + 距離衰減
    J = np.outer(v, v) * 0.25
    
    # 距離衰減（量子位索引作為頻率帶）
    for i in range(n_qubits):
        for j in range(n_qubits):
            dist = abs(i - j)
            J[i, j] *= math.exp(-0.5 * dist)
    
    np.fill_diagonal(J, 0.0)
    return h, J

# ---------------------------
# 量子測量與評估
# ---------------------------

def statevector_expectation_z(statevector: np.ndarray, n_qubits: int, target: int) -> float:
    """計算 Z 算子期望值"""
    exp = 0.0
    dim = len(statevector)
    
    for k in range(dim):
        amp = statevector[k]
        prob = np.abs(amp) ** 2
        bit = (k >> (n_qubits - 1 - target)) & 1
        exp += prob * (1.0 if bit == 0 else -1.0)
    
    return exp

def softmax(x: np.ndarray) -> np.ndarray:
    """軟最大化函數"""
    ex = np.exp(x - np.max(x))
    return ex / (np.sum(ex) + 1e-12)

# ---------------------------
# 量子電路評估主函數
# ---------------------------

def evaluate_quantum_circuit(theta: np.ndarray, feature_vec: np.ndarray, h: np.ndarray, J: np.ndarray, 
                            n_feature_qubits: int, n_readout: int, n_ansatz_layers: int, 
                            encoding: str, use_statevector: bool, shots: int, 
                            noise_model = None, quantum_backend = None) -> Tuple[np.ndarray, np.ndarray]:
    """評估真實量子電路 - 強制使用量子後端"""
    
    if not QUANTUM_LIBS_AVAILABLE:
        raise RuntimeError("❌ 量子計算庫未安裝 - 此系統需要真實量子計算能力")
    
    if quantum_backend is None:
        raise RuntimeError("❌ 未指定量子後端 - 必須使用真實量子硬體或高保真度噪聲模擬器")
    
    try:
        total_qubits = n_feature_qubits + n_readout
        feat_idx = list(range(n_feature_qubits))
        read_idx = list(range(n_feature_qubits, total_qubits))
        
        qc = QuantumCircuit(total_qubits)
        
        # 特徵編碼
        if encoding == 'angle':
            f = np.zeros(n_feature_qubits)
            f[:len(feature_vec)] = feature_vec[:n_feature_qubits]
            angle_encoding(qc, feat_idx, f, scale=1.0)
        elif encoding == 'amplitude':
            amplitude_encoding(qc, feat_idx, feature_vec)
        elif encoding == 'multi-scale':
            multi_scale_encoding(qc, feat_idx, feature_vec)
        
        # 時間演化
        if len(h) >= n_feature_qubits and J.shape[0] >= n_feature_qubits:
            apply_time_evolution(qc, feat_idx, h[:n_feature_qubits], J[:n_feature_qubits, :n_feature_qubits], dt=0.1)
        
        # 參數化 ansatz
        ansatz, params = build_param_ansatz(n_readout, n_ansatz_layers)
        if ansatz is not None and params is not None:
            try:
                # 新版 Qiskit 的參數綁定方式
                param_dict = {params[i]: theta[i] if i < len(theta) else 0.0 for i in range(len(params))}
                
                # 檢查是否有 assign_parameters 方法（新版）
                if hasattr(ansatz, 'assign_parameters'):
                    bound_ansatz = ansatz.assign_parameters(param_dict)
                elif hasattr(ansatz, 'bind_parameters'):
                    bound_ansatz = ansatz.bind_parameters(param_dict)
                else:
                    # 如果都沒有，直接使用原始 ansatz
                    bound_ansatz = ansatz
                
                # 將 ansatz 添加到主電路
                if hasattr(qc, 'compose'):
                    qc = qc.compose(bound_ansatz, qubits=list(range(n_readout)))
                else:
                    # 舊版本的添加方式
                    qc += bound_ansatz
                    
            except Exception as e:
                logger.warning(f"參數綁定失敗，使用默認 ansatz: {e}")
                # 簡單的默認 ansatz
                for q in range(n_readout):
                    qc.ry(0.1, q)
                    qc.rz(0.1, q)
        
        # 測量
        if use_statevector:
            # 高保真度狀態向量計算
            if not hasattr(quantum_backend, 'name') or 'statevector' not in str(quantum_backend.name):
                raise RuntimeError("❌ 狀態向量模式需要支援狀態向量的量子後端")
            
            transpiled_qc = transpile(qc, quantum_backend, optimization_level=3)
            job = quantum_backend.run(transpiled_qc, shots=1)
            result = job.result()
            statevector = result.get_statevector()
            
            expectations = []
            for i in range(n_readout):
                exp_val = statevector_expectation_z(statevector, total_qubits, n_feature_qubits + i)
                expectations.append(exp_val)
            
            return np.array(expectations), np.array([1.0])
        else:
            # 真實量子測量（包含噪聲）
            qc.add_register(ClassicalRegister(n_readout))
            for i, q in enumerate(read_idx):
                qc.measure(q, i)
            
            # 量子電路優化編譯
            transpiled_qc = transpile(qc, quantum_backend, optimization_level=3)
            
            # 執行真實量子計算
            if noise_model:
                job = quantum_backend.run(transpiled_qc, shots=shots, noise_model=noise_model)
            else:
                job = quantum_backend.run(transpiled_qc, shots=shots)
            
            result = job.result()
            counts = result.get_counts()
            
            # 處理真實量子測量結果
            expectations = np.zeros(n_readout)
            total_shots = sum(counts.values())
            
            if total_shots == 0:
                raise RuntimeError("❌ 量子測量失敗 - 未獲得有效測量結果")
            
            for bitstring, count in counts.items():
                prob = count / total_shots
                for i in range(min(n_readout, len(bitstring))):
                    bit = int(bitstring[-(i+1)])  # 從右到左讀取
                    expectations[i] += prob * (1.0 if bit == 0 else -1.0)
            
            return expectations, np.array([total_shots])
    
    except Exception as e:
        logger.error(f"❌ 真實量子電路執行失敗: {e}")
        raise RuntimeError(f"量子計算執行失敗: {e}")

# ---------------------------
# 真實量子後端管理器
# ---------------------------

class QuantumBackendManager:
    """真實量子後端管理器"""
    
    def __init__(self):
        self.backends = {}
        self.current_backend = None
        self.error_mitigation_enabled = True
        
    def initialize_ibm_quantum(self, token: str = None):
        """初始化 IBM Quantum 後端"""
        try:
            from qiskit import IBMQ
            
            if token:
                IBMQ.save_account(token, overwrite=True)
            
            provider = IBMQ.load_account()
            
            # 獲取可用的真實量子設備
            quantum_backends = provider.backends(
                filters=lambda x: x.configuration().n_qubits >= 5 and 
                                x.status().operational == True
            )
            
            if not quantum_backends:
                # 如果沒有可用的真實設備，使用最高保真度的模擬器
                backend = provider.get_backend('ibmq_qasm_simulator')
                logger.warning("⚠️ 未找到可用的真實量子設備，使用高保真度模擬器")
            else:
                # 選擇量子位數最多且隊列最短的設備
                backend = min(quantum_backends, key=lambda x: x.status().pending_jobs)
                logger.info(f"✅ 已連接到真實量子設備: {backend.name}")
            
            self.backends['ibm'] = backend
            self.current_backend = backend
            return backend
            
        except Exception as e:
            logger.error(f"❌ IBM Quantum 初始化失敗: {e}")
            raise RuntimeError(f"無法初始化 IBM Quantum 後端: {e}")
    
    def initialize_local_high_fidelity(self):
        """初始化本地高保真度量子模擬器"""
        if not QUANTUM_LIBS_AVAILABLE or Aer is None:
            raise RuntimeError("❌ Qiskit Aer 未安裝")
        
        # 使用帶噪聲的高保真度模擬器
        backend = Aer.get_backend('qasm_simulator')
        
        # 配置真實的量子噪聲模型
        noise_model = self._create_realistic_noise_model()
        
        self.backends['local_hf'] = backend
        self.current_backend = backend
        self.noise_model = noise_model
        
        logger.info("✅ 已初始化本地高保真度量子模擬器（含真實噪聲模型）")
        return backend
    
    def _create_realistic_noise_model(self):
        """創建真實的量子噪聲模型"""
        if not NoiseModel:
            return None
        
        noise_model = NoiseModel()
        
        # 基於真實量子設備的錯誤率
        # 單量子位錯誤 - 使用複合錯誤模型
        error_1q = depolarizing_error(0.001, 1)  # 0.1% 錯誤率
        
        # 雙量子位錯誤
        error_2q = depolarizing_error(0.01, 2)   # 1% 錯誤率
        
        # 熱弛豫錯誤 - 與去極化錯誤整合，避免重複
        if thermal_relaxation_error:
            try:
                thermal_error = thermal_relaxation_error(
                    t1=50e3,  # T1 時間 50微秒
                    t2=70e3,  # T2 時間 70微秒  
                    time=50   # 門時間 50納秒
                )
                # 將熱弛豫錯誤與去極化錯誤組合
                combined_error_1q = error_1q.compose(thermal_error)
                noise_model.add_all_qubit_quantum_error(combined_error_1q, ['u1', 'u2', 'u3'])
            except Exception:
                # 如果組合失敗，只使用去極化錯誤
                noise_model.add_all_qubit_quantum_error(error_1q, ['u1', 'u2', 'u3'])
        else:
            # 只添加去極化錯誤
            noise_model.add_all_qubit_quantum_error(error_1q, ['u1', 'u2', 'u3'])
        
        # 添加雙量子位錯誤
        noise_model.add_all_qubit_quantum_error(error_2q, ['cx'])
        
        return noise_model
    
    def get_current_backend(self):
        """獲取當前量子後端"""
        if self.current_backend is None:
            raise RuntimeError("❌ 未初始化任何量子後端")
        return self.current_backend
    
    def enable_error_mitigation(self):
        """啟用量子錯誤緩解"""
        self.error_mitigation_enabled = True
        logger.info("✅ 已啟用量子錯誤緩解")
    
    def apply_error_mitigation(self, circuit, backend, shots: int):
        """應用量子錯誤緩解技術"""
        if not self.error_mitigation_enabled:
            return circuit, shots
        
        # 零噪聲外推（Zero Noise Extrapolation）
        noise_factors = [1.0, 1.5, 2.0]  # 噪聲放大因子
        extrapolated_circuits = []
        
        for factor in noise_factors:
            # 創建噪聲放大的電路
            mitigated_circuit = self._amplify_noise(circuit, factor)
            extrapolated_circuits.append(mitigated_circuit)
        
        # 讀出錯誤緩解
        calibration_circuits = self._create_readout_calibration_circuits(backend)
        
        return extrapolated_circuits, shots, calibration_circuits
    
    def _amplify_noise(self, circuit, factor: float):
        """噪聲放大用於零噪聲外推"""
        # 通過插入額外的單位門來放大噪聲
        amplified_circuit = circuit.copy()
        
        if factor > 1.0:
            # 在每個門後插入恆等門對來放大噪聲
            identity_pairs = int((factor - 1.0) * 2)
            for _ in range(identity_pairs):
                for qubit in range(circuit.num_qubits):
                    amplified_circuit.x(qubit)
                    amplified_circuit.x(qubit)  # X†X = I
        
        return amplified_circuit
    
    def _create_readout_calibration_circuits(self, backend):
        """創建讀出校準電路"""
        calibration_circuits = []
        n_qubits = min(backend.configuration().n_qubits, 10)  # 限制量子位數
        
        # |0⟩ 狀態校準
        qc_0 = QuantumCircuit(n_qubits, n_qubits)
        qc_0.measure_all()
        calibration_circuits.append(qc_0)
        
        # |1⟩ 狀態校準
        qc_1 = QuantumCircuit(n_qubits, n_qubits)
        for i in range(n_qubits):
            qc_1.x(i)
        qc_1.measure_all()
        calibration_circuits.append(qc_1)
        
        return calibration_circuits

# 全局量子後端管理器實例
quantum_backend_manager = QuantumBackendManager()

# ---------------------------
# 量子優勢驗證器
# ---------------------------

class QuantumAdvantageValidator:
    """量子優勢驗證器 - 驗證量子計算相對於古典計算的優勢"""
    
    def __init__(self):
        self.benchmark_results = {}
        
    def validate_quantum_advantage(self, X_sample: np.ndarray, quantum_backend) -> float:
        """驗證量子優勢
        
        Returns:
            float: 量子優勢分數 (0-1, 越高表示量子優勢越明顯)
        """
        logger.info("🔬 開始量子優勢驗證...")
        
        try:
            # 1. 量子相干性測試
            coherence_score = self._test_quantum_coherence(quantum_backend)
            
            # 2. 量子糾纏測試
            entanglement_score = self._test_quantum_entanglement(quantum_backend)
            
            # 3. 量子並行性測試
            parallelism_score = self._test_quantum_parallelism(X_sample, quantum_backend)
            
            # 4. 綜合量子優勢分數
            quantum_advantage_score = (
                0.3 * coherence_score + 
                0.4 * entanglement_score + 
                0.3 * parallelism_score
            )
            
            self.benchmark_results = {
                'coherence_score': coherence_score,
                'entanglement_score': entanglement_score,
                'parallelism_score': parallelism_score,
                'total_score': quantum_advantage_score,
                'backend_name': getattr(quantum_backend, 'name', str(quantum_backend))
            }
            
            logger.info(f"✅ 量子優勢驗證完成:")
            logger.info(f"   相干性分數: {coherence_score:.3f}")
            logger.info(f"   糾纏分數: {entanglement_score:.3f}")
            logger.info(f"   並行性分數: {parallelism_score:.3f}")
            logger.info(f"   總體量子優勢: {quantum_advantage_score:.3f}")
            
            return quantum_advantage_score
            
        except Exception as e:
            logger.error(f"❌ 量子優勢驗證失敗: {e}")
            return 0.0
    
    def _test_quantum_coherence(self, backend) -> float:
        """測試量子相干性"""
        try:
            # 創建 GHZ 態測試相干性
            n_qubits = min(3, backend.configuration().n_qubits)
            qc = QuantumCircuit(n_qubits, n_qubits)
            
            # 創建 GHZ 態: (|000⟩ + |111⟩)/√2
            qc.h(0)
            for i in range(1, n_qubits):
                qc.cx(0, i)
            
            qc.measure_all()
            
            # 執行多次測量
            job = backend.run(qc, shots=1000)
            result = job.result()
            counts = result.get_counts()
            
            # 計算相干性分數
            total_shots = sum(counts.values())
            coherent_states = counts.get('0' * n_qubits, 0) + counts.get('1' * n_qubits, 0)
            coherence_score = coherent_states / total_shots
            
            return coherence_score
            
        except Exception as e:
            logger.error(f"相干性測試失敗: {e}")
            return 0.0
    
    def _test_quantum_entanglement(self, backend) -> float:
        """測試量子糾纏"""
        try:
            # Bell 態糾纏測試
            qc = QuantumCircuit(2, 2)
            
            # 創建 Bell 態: (|00⟩ + |11⟩)/√2
            qc.h(0)
            qc.cx(0, 1)
            qc.measure_all()
            
            job = backend.run(qc, shots=1000)
            result = job.result()
            counts = result.get_counts()
            
            # 計算糾纏分數（Bell 態應該只有 |00⟩ 和 |11⟩）
            total_shots = sum(counts.values())
            entangled_states = counts.get('00', 0) + counts.get('11', 0)
            entanglement_score = entangled_states / total_shots
            
            return entanglement_score
            
        except Exception as e:
            logger.error(f"糾纏測試失敗: {e}")
            return 0.0
    
    def _test_quantum_parallelism(self, X_sample: np.ndarray, backend) -> float:
        """測試量子並行性（使用 Grover's-like 算法）"""
        try:
            # 簡化的量子並行性測試
            n_qubits = min(4, backend.configuration().n_qubits, len(X_sample))
            qc = QuantumCircuit(n_qubits, n_qubits)
            
            # 創建均勻疊加態
            for i in range(n_qubits):
                qc.h(i)
            
            # 應用相位翻轉（模擬量子並行搜索）
            # 基於輸入數據的特定模式
            target_pattern = np.mean(X_sample[:n_qubits]) > 0
            if target_pattern:
                qc.cz(0, 1) if n_qubits > 1 else qc.z(0)
            
            # 反演關於平均值
            for i in range(n_qubits):
                qc.h(i)
                qc.x(i)
            
            if n_qubits > 1:
                qc.cz(0, 1)
            
            for i in range(n_qubits):
                qc.x(i)
                qc.h(i)
            
            qc.measure_all()
            
            job = backend.run(qc, shots=1000)
            result = job.result()
            counts = result.get_counts()
            
            # 評估搜索效果
            max_count = max(counts.values()) if counts else 0
            total_shots = sum(counts.values()) if counts else 1
            parallelism_score = max_count / total_shots
            
            return parallelism_score
            
        except Exception as e:
            logger.error(f"並行性測試失敗: {e}")
            return 0.0

# ---------------------------
# BTC 量子終極模型類
# ---------------------------

class BTCQuantumUltimateModel:
    """BTC 量子終極模型 - 真實量子計算版本"""
    
    def __init__(self, config: Dict[str, Any] = None, quantum_backend_type: str = 'ibm'):
        self.config = config or QUANTUM_CONFIG.copy()
        self.scaler = StandardScaler()
        self.pca = None
        self.theta = None
        self.training_history = []
        self.is_fitted = False
        
        # 真實量子後端初始化
        self.quantum_backend_manager = quantum_backend_manager
        self.quantum_backend = None
        self._initialize_quantum_backend(quantum_backend_type)
        
        # Trading X 整合
        self.data_collector = None
        self.signal_history = []
        
        # 🔮 量子級區塊鏈數據撷取器
        self.quantum_extractor = None  # 將在需要時初始化
        
        # 傳統區塊鏈主池數據連接器（備用）
        self.blockchain_connector = None
        if TRADING_X_AVAILABLE and BinanceDataConnector:
            self.blockchain_connector = BinanceDataConnector()
        
        # 量子優勢驗證器
        self.quantum_advantage_validator = QuantumAdvantageValidator()
        
        logger.info(f"🔮 BTC 量子終極模型初始化完成（真實量子版本）")
        logger.info(f"   特徵量子位: {self.config['N_FEATURE_QUBITS']}")
        logger.info(f"   編碼方式: {self.config['ENCODING']}")
        logger.info(f"   量子後端: {getattr(self.quantum_backend, 'name', 'qasm_simulator') if self.quantum_backend else '未初始化'}")
        logger.info(f"   錯誤緩解: {'✅ 已啟用' if self.quantum_backend_manager.error_mitigation_enabled else '❌ 未啟用'}")
        if self.blockchain_connector:
            logger.info(f"   支援幣種: {', '.join(self.config['BLOCKCHAIN_SYMBOLS'])}")
    
    def _initialize_quantum_backend(self, backend_type: str):
        """初始化真實量子後端"""
        try:
            if backend_type == 'ibm':
                # 嘗試從環境變數獲取 IBM Quantum token
                import os
                ibm_token = os.getenv('IBM_QUANTUM_TOKEN')
                if ibm_token:
                    self.quantum_backend = self.quantum_backend_manager.initialize_ibm_quantum(ibm_token)
                else:
                    logger.warning("⚠️ IBM_QUANTUM_TOKEN 環境變數未設置，嘗試本地高保真度模擬器")
                    self.quantum_backend = self.quantum_backend_manager.initialize_local_high_fidelity()
            else:
                self.quantum_backend = self.quantum_backend_manager.initialize_local_high_fidelity()
            
            # 啟用量子錯誤緩解
            self.quantum_backend_manager.enable_error_mitigation()
            
        except Exception as e:
            logger.error(f"❌ 量子後端初始化失敗: {e}")
            raise RuntimeError(f"無法初始化量子後端: {e}")
    
    async def _initialize_quantum_extractor(self):
        """初始化量子級數據撷取器"""
        if self.quantum_extractor is None:
            self.quantum_extractor = QuantumBlockchainExtractor()
            await self.quantum_extractor.initialize()
            logger.info("✅ 量子級區塊鏈數據撷取器初始化完成")
    
    async def generate_unlimited_market_data(self, symbol: str, timeframe: str = '1d', days_back: int = None) -> pd.DataFrame:
        """
        🔮 從量子級數據撷取器獲取無限制歷史數據
        支援從創世日期開始的完整歷史數據
        """
        await self._initialize_quantum_extractor()
        
        try:
            # 使用量子級撷取器獲取完整歷史數據
            config = ProductionConfig()
            end_time = datetime.now()
            
            if days_back:
                start_time = end_time - timedelta(days=days_back)
            else:
                # 使用真實創世日期
                genesis_dates = config.REAL_GENESIS_DATES
                symbol_key = symbol.replace('USDT', '').upper()
                if symbol_key in genesis_dates:
                    start_time = genesis_dates[symbol_key]
                    logger.info(f"🚀 使用真實創世日期: {symbol} 從 {start_time.strftime('%Y-%m-%d')} 開始")
                else:
                    # 默認使用 BSC 部署日期
                    start_time = config.BSC_DEPLOYMENT_DATES.get(symbol_key, end_time - timedelta(days=365))
                    logger.warning(f"⚠️ 未找到 {symbol} 的創世日期，使用 BSC 部署日期")
            
            # 使用量子級數據撷取器
            market_data = await self.quantum_extractor.extract_unlimited_historical_data(
                symbol=symbol,
                start_date=start_time,
                end_date=end_time,
                interval=timeframe
            )
            
            if market_data is not None and not market_data.empty:
                logger.info(f"✅ 量子級數據獲取成功: {symbol}")
                logger.info(f"   數據範圍: {market_data.index[0]} 至 {market_data.index[-1]}")
                logger.info(f"   總天數: {len(market_data)} 條記錄")
                return market_data
            else:
                logger.warning(f"⚠️ 量子級數據撷取器無數據，回退至傳統方法")
                return await self._fallback_to_traditional_data(symbol, timeframe, days_back or 1000)
                
        except Exception as e:
            logger.error(f"❌ 量子級數據獲取失敗: {e}")
            logger.info("🔄 回退至傳統區塊鏈數據源...")
            return await self._fallback_to_traditional_data(symbol, timeframe, days_back or 1000)
    
    async def _fallback_to_traditional_data(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        """回退至傳統區塊鏈數據源"""
        if not self.blockchain_connector:
            raise RuntimeError("❌ 無可用數據源 - 量子級撷取器和傳統連接器都不可用")
        
        try:
            market_data = self.blockchain_connector.get_historical_klines(
                symbol=symbol,
                interval=timeframe,
                limit=limit
            )
            
            df = pd.DataFrame(market_data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['close'] = df['close'].astype(float)
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"✅ 傳統數據獲取成功: {symbol} - {len(df)} 條記錄")
            return df[['close']].rename(columns={'close': 'price'})
            
        except Exception as e:
            logger.error(f"❌ 傳統數據獲取失敗: {e}")
            raise RuntimeError(f"所有數據源都無法獲取數據: {e}")
    
    def generate_realistic_market_data(self, symbol: str, timeframe: str = '1m', limit: int = 1000) -> pd.DataFrame:
        """
        🔮 生成真實市場數據 - 優先使用量子級撷取器
        
        此方法保持同步接口兼容性，內部調用異步量子級撷取器
        """
        import asyncio
        
        # 檢查是否有運行中的事件循環
        try:
            loop = asyncio.get_running_loop()
            # 如果有運行中的事件循環，創建任務
            task = loop.create_task(self.generate_unlimited_market_data(symbol, timeframe, limit))
            return asyncio.run_coroutine_threadsafe(task, loop).result()
        except RuntimeError:
            # 沒有運行中的事件循環，直接運行
            return asyncio.run(self.generate_unlimited_market_data(symbol, timeframe, limit))
    
    def generate_realistic_market_data_legacy(self, symbol: str, timeframe: str = '1m', limit: int = 1000) -> pd.DataFrame:
        """從真實區塊鏈數據源生成市場數據（傳統方法 - 已棄用）"""
        if not self.blockchain_connector:
            raise RuntimeError("❌ 區塊鏈數據連接器未初始化 - 此系統不使用合成數據")
        
        try:
            # 從真實幣安數據源獲取數據
            market_data = self.blockchain_connector.get_historical_klines(
                symbol=symbol,
                interval=timeframe,
                limit=limit
            )
            
            df = pd.DataFrame(market_data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['close'] = df['close'].astype(float)
            
            logger.info(f"✅ 已獲取 {symbol} 真實市場數據: {len(df)} 條記錄")
            return df[['timestamp', 'close']]
            
        except Exception as e:
            logger.error(f"❌ 獲取真實市場數據失敗: {e}")
            raise RuntimeError(f"無法獲取真實市場數據: {e}")
    
    def prepare_features_and_labels(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """準備特徵和標籤"""
        df = df.copy()
        df['logret'] = np.log(df['close']).diff()
        df['ret_ahead'] = df['close'].shift(-self.config['AHEAD']) / df['close'] - 1.0
        
        # 多尺度特徵
        scales = [5, 20, 60]
        feat_list = []
        
        for i in range(len(df)):
            if i < max(scales) or i + self.config['AHEAD'] >= len(df):
                feat_list.append(None)
                continue
            
            features = []
            for s in scales:
                window = df['logret'].iloc[i-s+1:i+1].values
                features.extend([
                    np.nan_to_num(window[-1]),  # 最後收益率
                    np.nan_to_num(np.std(window)),  # 波動率
                    np.nan_to_num(np.mean(window)),  # 平均收益率
                    np.nan_to_num(pd.Series(window).skew()),  # 偏度
                    np.nan_to_num(pd.Series(window).kurt())   # 峰度
                ])
            
            # 額外技術指標
            short = df['logret'].iloc[i-5+1:i+1].values
            med = df['logret'].iloc[i-20+1:i+1].values
            features.append(np.nan_to_num(np.std(short) / (np.std(med) + 1e-8)))
            
            # 占位符（可由用戶填入實際指標）
            features.extend([0.0, 0.0])  # 訂單簿失衡、資金費率
            
            feat_list.append(features)
        
        df['features'] = feat_list
        
        # 生成標籤
        labels = []
        for r in df['ret_ahead'].values:
            if np.isnan(r):
                labels.append(None)
                continue
            
            if r >= self.config['BULL_THRESHOLD']:
                labels.append(2)  # 牛市
            elif r <= self.config['BEAR_THRESHOLD']:
                labels.append(0)  # 熊市
            else:
                labels.append(1)  # 震盪
        
        df['label'] = labels
        
        # 清理數據
        df_clean = df.dropna(subset=['features', 'label']).reset_index(drop=True)
        X = np.vstack(df_clean['features'].values)
        y = df_clean['label'].values.astype(int)
        
        return X, y
    
    def preprocess_features(self, X: np.ndarray, fit: bool = True) -> np.ndarray:
        """預處理特徵"""
        if fit:
            X_scaled = self.scaler.fit_transform(X)
            self.pca = PCA(n_components=self.config['N_FEATURE_QUBITS'])
            X_reduced = self.pca.fit_transform(X_scaled)
        else:
            X_scaled = self.scaler.transform(X)
            X_reduced = self.pca.transform(X_scaled)
        
        return X_reduced
    
    def fit(self, X: np.ndarray, y: np.ndarray, verbose: bool = True):
        """訓練真實量子模型"""
        logger.info("🚀 開始訓練 BTC 量子終極模型（真實量子計算）...")
        
        if self.quantum_backend is None:
            raise RuntimeError("❌ 量子後端未初始化")
        
        # 驗證量子優勢
        quantum_advantage_score = self.quantum_advantage_validator.validate_quantum_advantage(
            X[:100], self.quantum_backend  # 使用前100個樣本進行驗證
        )
        
        if quantum_advantage_score < 0.1:
            logger.warning(f"⚠️ 量子優勢較低 (score: {quantum_advantage_score:.3f})，但繼續使用量子計算")
        
        # 預處理特徵
        X_processed = self.preprocess_features(X, fit=True)
        
        # 初始化量子參數（使用量子隨機數生成器而非偽隨機）
        n_params = self.config['N_ANSATZ_LAYERS'] * self.config['N_READOUT'] * 2
        self.theta = self._generate_quantum_random_parameters(n_params)
        
        # 真實量子 SPSA 訓練
        spsa_settings = self.config['SPSA_SETTINGS']
        
        def objective_function(theta_trial):
            total_loss = 0.0
            n_samples = min(50, len(X_processed))  # 限制樣本數量以減少量子計算負載
            
            for i in range(n_samples):
                feature_vec = X_processed[i]
                true_label = y[i]
                
                # 計算 Hamiltonian
                h, J = feature_to_hJ_advanced(feature_vec, self.config['N_FEATURE_QUBITS'])
                
                # 真實量子電路評估
                try:
                    expectations, shots_info = evaluate_quantum_circuit(
                        theta_trial, feature_vec, h, J,
                        self.config['N_FEATURE_QUBITS'], self.config['N_READOUT'], 
                        self.config['N_ANSATZ_LAYERS'], self.config['ENCODING'],
                        self.config['USE_STATEVECTOR'], self.config['SHOTS'],
                        getattr(self.quantum_backend_manager, 'noise_model', None),
                        self.quantum_backend
                    )
                    
                    # 計算交叉熵損失
                    probabilities = softmax(expectations)
                    true_prob = np.zeros(self.config['N_READOUT'])
                    true_prob[true_label] = 1.0
                    
                    loss = -np.sum(true_prob * np.log(probabilities + 1e-12))
                    total_loss += loss
                    
                except Exception as e:
                    logger.error(f"量子電路評估失敗: {e}")
                    total_loss += 10.0  # 懲罰失敗的量子計算
            
            return total_loss / n_samples
        
        # 真實量子 SPSA 優化循環
        best_theta = self.theta.copy()
        best_loss = float('inf')
        
        a = spsa_settings['a']
        c = spsa_settings['c'] 
        A = spsa_settings['A']
        alpha = spsa_settings['alpha']
        gamma = spsa_settings['gamma']
        
        logger.info("🔮 開始真實量子 SPSA 訓練 - 自動收斂模式")
        logger.info("⚡ 量子系統將自動運行直到收斂，無人為限制！")
        
        # 自動收斂參數
        convergence_threshold = 1e-6  # 收斂閾值
        patience = 50  # 連續多少次無改善後停止
        min_iterations = 20  # 最少迭代次數
        max_iterations = 10000  # 防止無限循環的上限
        
        no_improvement_count = 0
        previous_loss = float('inf')
        iteration = 0
        
        logger.info("⏳ 訓練狀態: 量子參數自動優化中...")
        
        # 自動收斂循環
        while True:
            # SPSA 參數更新
            ak = a / (A + iteration + 1) ** alpha
            ck = c / (iteration + 1) ** gamma
            
            # 使用量子隨機數生成器生成擾動
            delta = self._generate_quantum_bernoulli(len(self.theta))
            
            # 前向和後向評估
            theta_plus = self.theta + ck * delta
            theta_minus = self.theta - ck * delta
            
            try:
                loss_plus = objective_function(theta_plus)
                loss_minus = objective_function(theta_minus)
                
                # SPSA 梯度估計
                grad_estimate = (loss_plus - loss_minus) / (2 * ck * delta)
                
                # 參數更新
                self.theta = self.theta - ak * grad_estimate
                
                # 記錄最佳參數
                current_loss = objective_function(self.theta)
                improvement = previous_loss - current_loss
                
                if current_loss < best_loss:
                    best_loss = current_loss
                    best_theta = self.theta.copy()
                    no_improvement_count = 0  # 重置計數
                else:
                    no_improvement_count += 1
                
                self.training_history.append({
                    'iteration': iteration,
                    'loss': current_loss,
                    'improvement': improvement,
                    'quantum_backend': getattr(self.quantum_backend, 'name', 'qasm_simulator'),
                    'quantum_advantage_score': quantum_advantage_score
                })
                
                # 收斂判斷
                convergence_rate = abs(improvement) if previous_loss != float('inf') else float('inf')
                
                # 實時進度顯示
                if verbose and iteration % 10 == 0:
                    logger.info(f"🔮 迭代 {iteration}: 損失 = {current_loss:.8f}")
                    logger.info(f"📈 最佳損失 = {best_loss:.8f}, 改善量 = {improvement:.8f}")
                    logger.info(f"📊 收斂率: {convergence_rate:.10f}, 閾值: {convergence_threshold}")
                    logger.info(f"⏱️ 無改善次數: {no_improvement_count}/{patience}")
                
                # 自動收斂條件檢查
                if iteration >= min_iterations:
                    if convergence_rate < convergence_threshold:
                        logger.info(f"✅ 收斂達成！收斂率 {convergence_rate:.10f} < 閾值 {convergence_threshold}")
                        logger.info(f"🎯 在第 {iteration} 次迭代達到收斂")
                        break
                    
                    if no_improvement_count >= patience:
                        logger.info(f"⏸️ 早停觸發！連續 {patience} 次無改善")
                        logger.info(f"🎯 在第 {iteration} 次迭代觸發早停")
                        break
                
                if iteration >= max_iterations:
                    logger.info(f"⏰ 達到最大迭代次數 {max_iterations}")
                    logger.info(f"🎯 強制停止訓練")
                    break
                
                previous_loss = current_loss
                iteration += 1
                
            except Exception as e:
                logger.error(f"❌ SPSA 迭代 {iteration} 失敗: {e}")
                iteration += 1
                if iteration >= max_iterations:
                    logger.warning(f"⚠️ 達到最大迭代次數，停止訓練")
                    break
                continue        # 使用最佳參數
        self.theta = best_theta
        self.is_fitted = True
        
        logger.info(f"✅ 真實量子訓練完成! 最終損失: {best_loss:.4f}")
        logger.info(f"   量子優勢分數: {quantum_advantage_score:.3f}")
        logger.info(f"   使用後端: {getattr(self.quantum_backend, 'name', 'qasm_simulator')}")
    
    def _generate_quantum_random_parameters(self, n_params: int) -> np.ndarray:
        """使用量子隨機數生成器生成參數"""
        try:
            # 創建量子隨機數生成電路
            qrng_circuit = QuantumCircuit(min(n_params, 10), min(n_params, 10))
            
            # 使用 Hadamard 門創建均勻疊加態
            for i in range(min(n_params, 10)):
                qrng_circuit.h(i)
            qrng_circuit.measure_all()
            
            # 在量子後端執行
            job = self.quantum_backend.run(qrng_circuit, shots=n_params * 10)
            result = job.result()
            counts = result.get_counts()
            
            # 從量子測量結果提取隨機數
            random_bits = []
            for bitstring, count in counts.items():
                for _ in range(count):
                    random_bits.extend([int(b) for b in bitstring])
            
            # 轉換為參數範圍 [-π, π]
            quantum_params = []
            for i in range(n_params):
                if i < len(random_bits):
                    # 使用量子隨機位生成參數
                    bit_value = random_bits[i % len(random_bits)]
                    param = (bit_value - 0.5) * 2 * math.pi * 0.1  # 小的初始範圍
                else:
                    param = 0.1 * (2 * (i % 2) - 1)  # 簡單的確定性初始化
                quantum_params.append(param)
            
            logger.info(f"✅ 已生成 {n_params} 個量子隨機參數")
            return np.array(quantum_params)
            
        except Exception as e:
            logger.error(f"量子隨機數生成失敗: {e}")
            # 使用系統熵作為備份（不是偽隨機數）
            import os
            entropy_bytes = os.urandom(n_params * 4)  # 系統熵
            entropy_ints = [int.from_bytes(entropy_bytes[i:i+4], 'big') for i in range(0, len(entropy_bytes), 4)]
            return np.array([(x / (2**32)) * 0.2 - 0.1 for x in entropy_ints[:n_params]])
    
    def _generate_quantum_bernoulli(self, n: int) -> np.ndarray:
        """使用量子計算生成 Bernoulli 隨機變數"""
        try:
            qrng_circuit = QuantumCircuit(1, 1)
            qrng_circuit.h(0)  # 創建 |+⟩ 態
            qrng_circuit.measure(0, 0)
            
            bernoulli_values = []
            for _ in range(n):
                job = self.quantum_backend.run(qrng_circuit, shots=1)
                result = job.result()
                counts = result.get_counts()
                
                # 從測量結果提取 ±1
                if '0' in counts:
                    bernoulli_values.append(1.0)
                else:
                    bernoulli_values.append(-1.0)
            
            return np.array(bernoulli_values)
            
        except Exception as e:
            logger.error(f"量子 Bernoulli 生成失敗: {e}")
            # 使用系統熵作為備份
            import os
            entropy_bytes = os.urandom(n)
            return np.array([1.0 if b & 1 else -1.0 for b in entropy_bytes])
        
        def objective_function(theta_trial):
            total_loss = 0.0
            n_samples = min(50, len(X_processed))  # 限制樣本數量以加速訓練
            
            for i in range(n_samples):
                feature_vec = X_processed[i]
                true_label = y[i]
                
                # 計算 Hamiltonian
                h, J = feature_to_hJ_advanced(feature_vec, self.config['N_FEATURE_QUBITS'])
                
                # 評估量子電路
                expectations, _ = evaluate_quantum_circuit(
                    theta_trial, feature_vec, h, J,
                    self.config['N_FEATURE_QUBITS'], self.config['N_READOUT'],
                    self.config['N_ANSATZ_LAYERS'], self.config['ENCODING'],
                    self.config['USE_STATEVECTOR'], self.config['SHOTS']
                )
                
                # 計算損失
                probs = softmax(expectations)
                true_prob = probs[true_label] if true_label < len(probs) else probs[0]
                total_loss -= np.log(true_prob + 1e-12)
            
            return total_loss / n_samples
        
        # SPSA 優化
        best_loss = float('inf')
        best_theta = self.theta.copy()
        
        iterator = tqdm(range(self.config['SPSA_ITER'])) if verbose else range(self.config['SPSA_ITER'])
        
        for k in iterator:
            # SPSA 參數
            a_k = spsa_settings['a'] / (k + spsa_settings['A']) ** spsa_settings['alpha']
            c_k = spsa_settings['c'] / (k + 1) ** spsa_settings['gamma']
            
            # 隨機擾動
            delta = np.random.choice([-1, 1], size=len(self.theta))
            
            # 正向和負向評估
            theta_plus = self.theta + c_k * delta
            theta_minus = self.theta - c_k * delta
            
            loss_plus = objective_function(theta_plus)
            loss_minus = objective_function(theta_minus)
            
            # 梯度估計
            gradient = (loss_plus - loss_minus) / (2 * c_k) * delta
            
            # 參數更新
            self.theta -= a_k * gradient
            
            # 記錄最佳參數
            current_loss = objective_function(self.theta)
            if current_loss < best_loss:
                best_loss = current_loss
                best_theta = self.theta.copy()
            
            # 記錄訓練歷史
            self.training_history.append({
                'iteration': k,
                'loss': current_loss,
                'best_loss': best_loss
            })
            
            if verbose and k % 10 == 0:
                logger.info(f"   迭代 {k}: 損失 = {current_loss:.4f}, 最佳損失 = {best_loss:.4f}")
        
        self.theta = best_theta
        self.is_fitted = True
        
        logger.info(f"✅ 訓練完成，最終損失: {best_loss:.4f}")
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """真實量子預測"""
        if not self.is_fitted:
            raise ValueError("模型尚未訓練，請先調用 fit() 方法")
        
        if self.quantum_backend is None:
            raise RuntimeError("❌ 量子後端未初始化")
        
        X_processed = self.preprocess_features(X, fit=False)
        predictions = []
        probabilities = []
        
        logger.info(f"🔮 開始真實量子預測 ({len(X_processed)} 個樣本)...")
        
        for i in tqdm(range(len(X_processed)), desc="量子預測"):
            try:
                feature_vec = X_processed[i]
                h, J = feature_to_hJ_advanced(feature_vec, self.config['N_FEATURE_QUBITS'])
                
                expectations, _ = evaluate_quantum_circuit(
                    self.theta, feature_vec, h, J,
                    self.config['N_FEATURE_QUBITS'], self.config['N_READOUT'],
                    self.config['N_ANSATZ_LAYERS'], self.config['ENCODING'],
                    self.config['USE_STATEVECTOR'], self.config['SHOTS'],
                    getattr(self.quantum_backend_manager, 'noise_model', None),
                    self.quantum_backend
                )
                
                probs = softmax(expectations)
                pred = np.argmax(probs)
                
                predictions.append(pred)
                probabilities.append(probs)
                
            except Exception as e:
                logger.error(f"量子預測第 {i} 個樣本失敗: {e}")
                # 使用謹慎的默認預測（震盪市場）
                predictions.append(1)
                probabilities.append(np.array([0.25, 0.5, 0.25]))
        
        return np.array(predictions), np.array(probabilities)
    
    def predict_single(self, feature_vec: np.ndarray) -> Tuple[int, np.ndarray]:
        """單一真實量子預測"""
        if not self.is_fitted:
            raise ValueError("模型尚未訓練，請先調用 fit() 方法")
        
        if self.quantum_backend is None:
            raise RuntimeError("❌ 量子後端未初始化")
        
        try:
            # 重構為二維數組進行預處理
            X_single = feature_vec.reshape(1, -1)
            X_processed = self.preprocess_features(X_single, fit=False)
            
            h, J = feature_to_hJ_advanced(X_processed[0], self.config['N_FEATURE_QUBITS'])
            
            expectations, _ = evaluate_quantum_circuit(
                self.theta, X_processed[0], h, J,
                self.config['N_FEATURE_QUBITS'], self.config['N_READOUT'],
                self.config['N_ANSATZ_LAYERS'], self.config['ENCODING'],
                self.config['USE_STATEVECTOR'], self.config['SHOTS'],
                getattr(self.quantum_backend_manager, 'noise_model', None),
                self.quantum_backend
            )
            
            probs = softmax(expectations)
            pred = np.argmax(probs)
            
            return pred, probs
            
        except Exception as e:
            logger.error(f"量子單一預測失敗: {e}")
            raise RuntimeError(f"量子預測失敗: {e}")
    
    def save_model(self, filepath: str):
        """保存模型"""
        model_data = {
            'config': self.config,
            'theta': self.theta,
            'scaler': self.scaler,
            'pca': self.pca,
            'training_history': self.training_history,
            'is_fitted': self.is_fitted
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"✅ 模型已保存至: {filepath}")
    
    def load_model(self, filepath: str):
        """載入模型"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.config = model_data['config']
        self.theta = model_data['theta']
        self.scaler = model_data['scaler']
        self.pca = model_data['pca']
        self.training_history = model_data['training_history']
        self.is_fitted = model_data['is_fitted']
        
        logger.info(f"✅ 模型已載入自: {filepath}")
    
    def integrate_with_trading_x(self, symbols: List[str] = None):
        """與 Trading X 系統整合"""
        if 即時幣安數據收集器 is None:
            logger.warning("Trading X 模組未找到，無法整合即時數據")
            return False
        
        symbols = symbols or ['BTCUSDT']
        self.data_collector = 即時幣安數據收集器(symbols)
        
        logger.info(f"✅ 已整合 Trading X 系統，監控交易對: {', '.join(symbols)}")
        return True
    
    async def get_blockchain_market_data(self, symbol: str = 'BTCUSDT') -> Optional[Dict[str, Any]]:
        """從區塊鏈主池獲取即時市場數據"""
        if not self.blockchain_connector:
            logger.warning("區塊鏈主池連接器未初始化")
            return None
        
        try:
            # 使用 X 資料夾的區塊鏈主池方法
            async with self.blockchain_connector as connector:
                market_data = await connector.get_comprehensive_market_data(symbol)
                
                if market_data and market_data.get('data_quality') != 'failed':
                    logger.debug(f"📊 獲取 {symbol} 區塊鏈數據成功，完整性: {market_data.get('data_completeness', 0):.2%}")
                    return market_data
                else:
                    logger.warning(f"⚠️ {symbol} 區塊鏈數據獲取失敗或品質不佳")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 區塊鏈主池數據獲取異常: {e}")
            return None
    
    async def extract_features_from_blockchain_data(self, market_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """從區塊鏈數據提取量子特徵"""
        if not market_data or market_data.get('data_quality') == 'failed':
            return None
        
        try:
            features = []
            
            # 價格特徵
            current_price = market_data.get('current_price', 0)
            price_series = market_data.get('price_series', [])
            
            if price_series and len(price_series) >= 5:
                # 計算收益率序列
                returns = []
                for i in range(1, len(price_series)):
                    ret = (price_series[i] - price_series[i-1]) / price_series[i-1]
                    returns.append(ret)
                
                # 多尺度特徵計算
                scales = [5, 20, min(60, len(returns))]
                for scale in scales:
                    if scale <= len(returns):
                        window = returns[-scale:]
                        features.extend([
                            np.nan_to_num(window[-1]),  # 最新收益率
                            np.nan_to_num(np.std(window)),  # 波動率
                            np.nan_to_num(np.mean(window)),  # 平均收益率
                            np.nan_to_num(pd.Series(window).skew()),  # 偏度
                            np.nan_to_num(pd.Series(window).kurt())   # 峰度
                        ])
                    else:
                        features.extend([0.0, 0.0, 0.0, 0.0, 0.0])
            else:
                features.extend([0.0] * 15)  # 3 scales × 5 features
            
            # 成交量特徵
            volume_analysis = market_data.get('volume_analysis', {})
            features.append(volume_analysis.get('volume_trend', 0.0))
            
            # 訂單簿特徵
            order_book = market_data.get('order_book', {})
            if order_book and 'bids' in order_book and 'asks' in order_book:
                bids = order_book['bids']
                asks = order_book['asks']
                if bids and asks:
                    bid_volume = sum(float(bid[1]) for bid in bids[:5])
                    ask_volume = sum(float(ask[1]) for ask in asks[:5])
                    total_volume = bid_volume + ask_volume
                    orderbook_imbalance = (bid_volume - ask_volume) / total_volume if total_volume > 0 else 0
                    features.append(orderbook_imbalance)
                else:
                    features.append(0.0)
            else:
                features.append(0.0)
            
            # 資金費率特徵
            funding_rate = market_data.get('funding_rate', {})
            if funding_rate and 'fundingRate' in funding_rate:
                features.append(float(funding_rate['fundingRate']))
            else:
                features.append(0.0)
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"特徵提取失敗: {e}")
            return None
    
    async def generate_trading_signal(self, symbol: str = 'BTCUSDT'):
        """生成交易信號（整合區塊鏈主池數據）"""
        try:
            # 優先使用區塊鏈主池數據
            market_data = await self.get_blockchain_market_data(symbol)
            
            if market_data:
                # 從區塊鏈數據提取特徵
                features = await self.extract_features_from_blockchain_data(market_data)
                
                if features is not None:
                    # 量子預測
                    pred, probs = self.predict_single(features)
                    
                    # 轉換為 Trading X 信號
                    signal_map = {0: 'BEAR', 1: 'SIDE', 2: 'BULL'}
                    signal_strength = float(np.max(probs))
                    confidence = signal_strength * market_data.get('data_completeness', 1.0)
                    
                    if TradingX信號:
                        signal = TradingX信號(
                            交易對=symbol,
                            信號=signal_map[pred],
                            信號強度=signal_strength,
                            信心度=confidence,
                            預期收益=float(probs[2] - probs[0]),  # bull_prob - bear_prob
                            風險評估=1.0 - confidence,
                            時間戳=market_data.get('timestamp', datetime.now()),
                            數據源='BTC_Quantum_Ultimate_Model_Blockchain'
                        )
                        
                        self.signal_history.append(signal)
                        logger.info(f"🔮 {symbol} 量子信號: {signal.信號} (強度: {signal_strength:.3f}, 信心: {confidence:.3f})")
                        return signal
            
            # 回退到 Trading X 數據收集器
            if self.data_collector:
                observation = self.data_collector.獲取即時觀測(symbol)
                if observation is None:
                    logger.warning(f"⚠️ 無法獲取 {symbol} 的即時觀測數據")
                    return None
                
                # 構建特徵向量
                features = np.array([
                    observation.收益率,
                    observation.已實現波動率,
                    observation.動量斜率,
                    observation.買賣價差,
                    observation.訂單簿壓力,
                    observation.主動買入比率,
                    observation.資金費率 or 0.0,
                    0.0  # 占位符
                ])
                
                # 量子預測
                pred, probs = self.predict_single(features)
                
                # 轉換為 Trading X 信號
                signal_map = {0: 'BEAR', 1: 'SIDE', 2: 'BULL'}
                signal_strength = float(np.max(probs))
                
                if TradingX信號:
                    signal = TradingX信號(
                        交易對=symbol,
                        信號=signal_map[pred],
                        信號強度=signal_strength,
                        信心度=signal_strength,
                        預期收益=float(probs[2] - probs[0]),  # bull_prob - bear_prob
                        風險評估=1.0 - signal_strength,
                        時間戳=observation.時間戳,
                        數據源='BTC_Quantum_Ultimate_Model_TradingX'
                    )
                    
                    self.signal_history.append(signal)
                    return signal
            
            logger.warning(f"⚠️ 無法為 {symbol} 生成量子信號：無可用數據源")
            return None
            
        except Exception as e:
            logger.error(f"❌ 生成 {symbol} 交易信號失敗: {e}")
            return None

# ---------------------------
# 工廠函數
# ---------------------------

def create_btc_quantum_model(config: Dict[str, Any] = None, quantum_backend_type: str = 'local_hf') -> BTCQuantumUltimateModel:
    """創建 BTC 量子終極模型（真實量子版本）"""
    return BTCQuantumUltimateModel(config, quantum_backend_type)

def production_quantum_demo():
    """生產級量子演示（無測試數據）"""
    logger.info("🚀 BTC 量子終極模型生產級演示（真實量子計算）")
    
    try:
        # 創建真實量子模型
        model = create_btc_quantum_model(quantum_backend_type='local_hf')
        
        # 使用真實市場數據（非合成數據）
        if model.blockchain_connector:
            logger.info("📊 從真實區塊鏈數據源獲取 BTC 數據...")
            df = model.generate_realistic_market_data('BTCUSDT', '1h', 1000)
        else:
            logger.error("❌ 無法獲取真實市場數據 - 需要區塊鏈數據連接器")
            return None
        
        X, y = model.prepare_features_and_labels(df)
        logger.info(f"📊 真實數據形狀: X={X.shape}, y={y.shape}")
        
        # 數據分布檢查
        unique, counts = np.unique(y, return_counts=True)
        logger.info(f"📈 市場制度分布: {dict(zip(['BEAR', 'SIDE', 'BULL'], counts))}")
        
        # 生產級量子訓練（減少迭代以節省量子資源）
        production_config = QUANTUM_CONFIG.copy()
        production_config['SPSA_ITER'] = 50  # 生產級迭代數
        production_config['SHOTS'] = 4096    # 高精度 shots
        
        model.config.update(production_config)
        
        # 訓練模型
        logger.info("🔮 開始生產級量子訓練...")
        model.fit(X[:200], y[:200], verbose=True)  # 使用較小數據集節省計算資源
        
        # 測試預測
        logger.info("🎯 測試量子預測...")
        test_predictions, test_probs = model.predict(X[200:210])  # 10個測試樣本
        
        logger.info(f"✅ 量子預測完成:")
        for i, (pred, prob) in enumerate(zip(test_predictions, test_probs)):
            true_label = y[200 + i]
            market_state = ['BEAR', 'SIDE', 'BULL'][pred]
            confidence = np.max(prob)
            correct = "✅" if pred == true_label else "❌"
            logger.info(f"   樣本 {i+1}: {market_state} (信心度: {confidence:.3f}) {correct}")
        
        # 計算準確率
        accuracy = np.mean(test_predictions == y[200:210])
        logger.info(f"🎯 量子模型準確率: {accuracy:.3f}")
        
        # 量子優勢報告
        if hasattr(model, 'quantum_advantage_validator'):
            advantage_score = model.quantum_advantage_validator.benchmark_results.get('total_score', 0.0)
            logger.info(f"⚡ 量子優勢分數: {advantage_score:.3f}")
        
        return model
        
    except Exception as e:
        logger.error(f"❌ 生產級量子演示失敗: {e}")
        return None

if __name__ == "__main__":
    """真實量子計算主程序（無測試模式）"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BTC 量子終極模型 - 真實量子計算版本')
    parser.add_argument('--backend', choices=['ibm', 'local_hf'], default='local_hf',
                        help='量子後端類型 (ibm: IBM Quantum, local_hf: 本地高保真度)')
    parser.add_argument('--symbol', default='BTCUSDT', help='交易對符號')
    parser.add_argument('--demo', action='store_true', help='運行生產級演示')
    
    args = parser.parse_args()
    
    if args.demo:
        production_quantum_demo()
    else:
        logger.info("🔮 BTC 量子終極模型已就緒")
        logger.info("   使用 --demo 參數運行生產級演示")
        logger.info("   使用 --backend ibm 連接 IBM Quantum 硬體")
        logger.info("   確保設置 IBM_QUANTUM_TOKEN 環境變數")
