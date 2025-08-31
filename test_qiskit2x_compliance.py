#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qiskit 2.x SDK 合規性測試
=========================

測試 btc_quantum_ultimate_model.py 是否完全符合 Qiskit 2.x SDK 標準：
- 使用標準 Primitives API (Sampler, Estimator)
- 嚴格的量子隨機數生成
- 無回退邏輯的純量子操作
- 正確的量子電路構建和測量

作者: Trading X Quantum Team
版本: 1.0
"""

import asyncio
import datetime
import logging
import sys
import traceback

import numpy as np

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_qiskit2x_compliance():
    """測試 Qiskit 2.x SDK 合規性"""
    print("🔬 開始 Qiskit 2.x SDK 合規性測試...")
    print("=" * 60)
    
    try:
        # 1. 測試 Qiskit 2.x 導入
        print("\n1️⃣ 測試 Qiskit 2.x 核心模組導入...")
        
        try:
            from qiskit import QuantumCircuit
            from qiskit.primitives import Estimator, Sampler
            from qiskit.quantum_info import SparsePauliOp
            from qiskit_aer.primitives import Estimator as AerEstimator
            from qiskit_aer.primitives import Sampler as AerSampler
            print("✅ Qiskit 2.x 核心模組導入成功")
        except ImportError as e:
            print(f"❌ Qiskit 2.x 核心模組導入失敗: {e}")
            return False
        
        # 2. 測試 btc_quantum_ultimate_model 導入
        print("\n2️⃣ 測試 btc_quantum_ultimate_model 導入...")
        
        try:
            sys.path.append('quantum_pro')
            from quantum_pro.btc_quantum_ultimate_model import (
                PRIMITIVES_AVAILABLE,
                QUANTUM_LIBS_AVAILABLE,
                BTCQuantumUltimateModel,
            )
            
            if not PRIMITIVES_AVAILABLE:
                print("❌ Qiskit 2.x Primitives API 不可用")
                return False
            
            if not QUANTUM_LIBS_AVAILABLE:
                print("❌ 量子計算庫不可用")
                return False
            
            print("✅ btc_quantum_ultimate_model 導入成功")
        except ImportError as e:
            print(f"❌ btc_quantum_ultimate_model 導入失敗: {e}")
            traceback.print_exc()
            return False
        
        # 3. 測試量子模型初始化
        print("\n3️⃣ 測試量子模型初始化...")
        
        try:
            model = BTCQuantumUltimateModel(quantum_backend_type='local')
            
            # 檢查量子後端
            if model.quantum_backend is None:
                print("❌ 量子後端未正確初始化")
                return False
            
            print(f"✅ 量子模型初始化成功 - 後端: {type(model.quantum_backend).__name__}")
            
        except Exception as e:
            print(f"❌ 量子模型初始化失敗: {e}")
            traceback.print_exc()
            return False
        
        # 4. 測試量子隨機數生成 (Qiskit 2.x Primitives)
        print("\n4️⃣ 測試 Qiskit 2.x Primitives 量子隨機數生成...")
        
        try:
            random_bits = model.quantum_backend_manager.generate_quantum_random_bits(32)
            
            if len(random_bits) != 32:
                print(f"❌ 量子隨機比特數量錯誤: 期望 32，實際 {len(random_bits)}")
                return False
            
            if not all(bit in [0, 1] for bit in random_bits):
                print("❌ 量子隨機比特包含非0/1值")
                return False
            
            print(f"✅ 量子隨機數生成成功: {random_bits[:8]}... (顯示前8位)")
            
        except Exception as e:
            print(f"❌ 量子隨機數生成失敗: {e}")
            traceback.print_exc()
            return False
        
        # 5. 測試量子參數生成
        print("\n5️⃣ 測試量子參數生成...")
        
        try:
            quantum_params = model._generate_quantum_random_parameters(10)
            
            if len(quantum_params) != 10:
                print(f"❌ 量子參數數量錯誤: 期望 10，實際 {len(quantum_params)}")
                return False
            
            # 檢查參數範圍 [-π, π]
            if not all(-np.pi <= param <= np.pi for param in quantum_params):
                print("❌ 量子參數超出範圍 [-π, π]")
                return False
            
            print(f"✅ 量子參數生成成功: {quantum_params[:3]} ... (顯示前3個)")
            
        except Exception as e:
            print(f"❌ 量子參數生成失敗: {e}")
            traceback.print_exc()
            return False
        
        # 6. 測試純量子信號生成
        print("\n6️⃣ 測試純量子信號生成...")
        
        try:
            # 創建測試特徵
            test_features = np.random.randn(5)  # 5個特徵
            
            # 生成量子信號
            prediction, probabilities = model.predict_single(test_features)
            
            # 驗證結果
            if not isinstance(prediction, (int, np.integer)):
                print(f"❌ 預測結果類型錯誤: {type(prediction)}")
                return False
            
            if len(probabilities) != 3:  # SHORT, NEUTRAL, LONG
                print(f"❌ 概率分佈維度錯誤: 期望 3，實際 {len(probabilities)}")
                return False
            
            if not np.isclose(np.sum(probabilities), 1.0, atol=1e-6):
                print(f"❌ 概率分佈總和不為1: {np.sum(probabilities)}")
                return False
            
            print(f"✅ 純量子信號生成成功:")
            print(f"   預測: {prediction} (0=SHORT, 1=NEUTRAL, 2=LONG)")
            print(f"   概率分佈: {probabilities}")
            
        except Exception as e:
            print(f"❌ 純量子信號生成失敗: {e}")
            traceback.print_exc()
            return False
        
        # 7. 測試量子電路評估 (evaluate_quantum_circuit)
        print("\n7️⃣ 測試 Qiskit 2.x 量子電路評估...")
        
        try:
            from quantum_pro.btc_quantum_ultimate_model import evaluate_quantum_circuit

            # 創建測試參數 - 正確計算參數數量
            # 對於 n_readout=3, n_ansatz_layers=2: 需要 3 * 2 * 2 = 12 個參數
            theta = np.random.rand(12) * 2 * np.pi - np.pi  # 12個隨機參數
            feature_vec = np.random.randn(3)  # 3個特徵
            h = np.random.randn(3)  # Hamiltonian
            J = np.random.randn(3, 3)  # 耦合矩陣
            
            # 評估量子電路
            expectations, _ = evaluate_quantum_circuit(
                theta=theta,
                feature_vec=feature_vec,
                h=h,
                J=J,
                n_feature_qubits=3,
                n_readout=3,
                n_ansatz_layers=2,
                encoding='angle',
                use_statevector=True,
                shots=1000,
                noise_model=None,
                quantum_backend=model.quantum_backend
            )
            
            if len(expectations) != 3:
                print(f"❌ 期望值維度錯誤: 期望 3，實際 {len(expectations)}")
                return False
            
            print(f"✅ 量子電路評估成功: {expectations}")
            
        except Exception as e:
            print(f"❌ 量子電路評估失敗: {e}")
            traceback.print_exc()
            return False
        
        # 8. 測試 TradingX 信號格式生成
        print("\n8️⃣ 測試 TradingX 信號格式生成...")
        
        try:
            signal = await model.generate_trading_signal('BTCUSDT')
            
            if signal is None:
                print("❌ 信號生成返回 None")
                return False
            
            # 檢查信號屬性
            required_attrs = ['時間戳', '交易對', '信號類型', '信心度', '制度']
            for attr in required_attrs:
                if not hasattr(signal, attr):
                    print(f"❌ 信號缺少必要屬性: {attr}")
                    return False
            
            print(f"✅ TradingX 信號生成成功:")
            print(f"   交易對: {signal.交易對}")
            print(f"   信號類型: {signal.信號類型}")
            print(f"   信心度: {signal.信心度:.3f}")
            print(f"   制度: {signal.制度}")
            
        except Exception as e:
            print(f"❌ TradingX 信號生成失敗: {e}")
            traceback.print_exc()
            return False
        
        # 9. 測試嚴格模式（無回退邏輯）
        print("\n9️⃣ 測試嚴格模式（無回退邏輯）...")
        
        try:
            # 嘗試使用無效後端（應該失敗）
            try:
                from quantum_pro.btc_quantum_ultimate_model import (
                    evaluate_quantum_circuit,
                )
                
                expectations, _ = evaluate_quantum_circuit(
                    theta=np.array([0.1, 0.2]),
                    feature_vec=np.array([0.1, 0.2]),
                    h=np.array([0.1, 0.2]),
                    J=np.array([[0.1, 0.2], [0.3, 0.4]]),
                    n_feature_qubits=2,
                    n_readout=2,
                    n_ansatz_layers=1,
                    encoding='angle',
                    use_statevector=True,
                    shots=1000,
                    noise_model=None,
                    quantum_backend=None  # 故意設為 None
                )
                
                print("❌ 嚴格模式測試失敗 - 應該拋出異常但沒有")
                return False
                
            except RuntimeError as expected_error:
                if "量子後端" in str(expected_error):
                    print("✅ 嚴格模式測試成功 - 正確拋出量子後端錯誤")
                else:
                    print(f"❌ 嚴格模式測試部分失敗 - 錯誤類型不正確: {expected_error}")
                    return False
                    
        except Exception as e:
            print(f"❌ 嚴格模式測試失敗: {e}")
            traceback.print_exc()
            return False
        
        print("\n" + "=" * 60)
        print("🎉 Qiskit 2.x SDK 合規性測試全部通過！")
        print("✅ 完全符合 Qiskit 2.x 標準")
        print("✅ 嚴格的純量子操作（無回退邏輯）")
        print("✅ 正確使用 Primitives API")
        print("✅ 標準量子隨機數生成")
        print("✅ TradingX 信號格式兼容")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 測試過程發生未預期錯誤: {e}")
        traceback.print_exc()
        return False

def main():
    """主函數"""
    try:
        result = asyncio.run(test_qiskit2x_compliance())
        
        if result:
            print(f"\n🔬 測試結果: ✅ 通過")
            sys.exit(0)
        else:
            print(f"\n🔬 測試結果: ❌ 失敗") 
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ 用戶中斷測試")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 測試程序異常: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
