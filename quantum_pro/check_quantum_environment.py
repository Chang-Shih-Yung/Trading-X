#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔮 Trading X 量子環境檢測器
===========================

跨設備量子環境一致性檢測工具
自動檢測並修復常見的量子計算環境問題
"""

import os
import sys
import subprocess
import importlib.util
import warnings
from pathlib import Path

# 抑制警告
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

class QuantumEnvironmentChecker:
    """量子環境檢測器"""
    
    def __init__(self):
        self.python_executable = sys.executable
        self.issues = []
        self.recommendations = []
        
    def print_header(self):
        """打印檢測標題"""
        print("🔮 Trading X 量子環境檢測器")
        print("=" * 60)
        print(f"🐍 Python 版本: {sys.version}")
        print(f"📍 Python 路徑: {self.python_executable}")
        print(f"💻 作業系統: {os.name}")
        print("=" * 60)
        
    def check_python_version(self):
        """檢查 Python 版本"""
        print("\n🔍 檢查 Python 版本...")
        
        major, minor = sys.version_info[:2]
        if major == 3 and minor >= 9:
            print(f"  ✅ Python {major}.{minor}: 版本符合需求 (>= 3.9)")
            return True
        else:
            print(f"  ❌ Python {major}.{minor}: 版本過低，需要 >= 3.9")
            self.issues.append("Python 版本過低")
            self.recommendations.append("升級到 Python 3.9 或更高版本")
            return False
    
    def check_virtual_environment(self):
        """檢查虛擬環境"""
        print("\n🔍 檢查虛擬環境...")
        
        # 檢查是否在虛擬環境中
        in_venv = (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
            'venv' in self.python_executable.lower()
        )
        
        if in_venv:
            print("  ✅ 虛擬環境: 已啟用")
            print(f"     📁 環境路徑: {sys.prefix}")
            return True
        else:
            print("  ⚠️ 虛擬環境: 未啟用 (建議使用虛擬環境)")
            self.recommendations.append("使用虛擬環境: python -m venv venv && source venv/bin/activate")
            return False
    
    def check_package_installation(self, package_name, import_name=None):
        """檢查套件安裝狀態"""
        if import_name is None:
            import_name = package_name
            
        try:
            module = importlib.import_module(import_name)
            version = getattr(module, '__version__', '未知版本')
            print(f"  ✅ {package_name}: {version}")
            return True, version
        except ImportError:
            print(f"  ❌ {package_name}: 未安裝")
            return False, None
    
    def check_core_dependencies(self):
        """檢查核心依賴"""
        print("\n🔍 檢查核心依賴...")
        
        core_packages = [
            ('numpy', 'numpy'),
            ('scipy', 'scipy'), 
            ('pandas', 'pandas'),
            ('scikit-learn', 'sklearn'),
            ('requests', 'requests'),
            ('aiohttp', 'aiohttp'),
            ('websockets', 'websockets'),
            ('ccxt', 'ccxt'),
            ('fastapi', 'fastapi'),
            ('uvicorn', 'uvicorn'),
            ('pydantic', 'pydantic')
        ]
        
        missing_packages = []
        
        for package_name, import_name in core_packages:
            installed, version = self.check_package_installation(package_name, import_name)
            if not installed:
                missing_packages.append(package_name)
        
        if missing_packages:
            self.issues.append(f"缺少核心依賴: {', '.join(missing_packages)}")
            self.recommendations.append(f"安裝: pip install {' '.join(missing_packages)}")
            
        return len(missing_packages) == 0
    
    def check_quantum_computing(self):
        """檢查量子計算環境"""
        print("\n🔮 檢查量子計算環境...")
        
        # 檢查 Qiskit 核心
        qiskit_installed, qiskit_version = self.check_package_installation('qiskit', 'qiskit')
        
        if not qiskit_installed:
            self.issues.append("Qiskit 核心未安裝")
            self.recommendations.append("安裝 Qiskit: pip install qiskit")
            return False
        
        # 檢查 Qiskit 版本
        try:
            major_version = int(qiskit_version.split('.')[0])
            if major_version >= 1:
                print(f"     🎯 Qiskit 版本: {qiskit_version} (v{major_version}.x)")
            else:
                print(f"     ⚠️ Qiskit 版本: {qiskit_version} (建議升級到 1.x+)")
        except:
            print(f"     ⚠️ Qiskit 版本: {qiskit_version} (無法解析)")
        
        # 檢查 Aer 模擬器 (多重檢測)
        aer_available = False
        aer_method = None
        
        # 方法1: qiskit_aer
        try:
            from qiskit_aer import AerSimulator
            import qiskit_aer
            aer_version = qiskit_aer.__version__
            print(f"  ✅ Aer 模擬器 (qiskit_aer): {aer_version}")
            aer_available = True
            aer_method = "qiskit_aer"
        except ImportError:
            print("  ⚠️ qiskit_aer: 未安裝")
        
        # 方法2: 內建 Aer (舊版本)
        if not aer_available:
            try:
                from qiskit import Aer
                backend = Aer.get_backend('qasm_simulator')
                print("  ✅ Aer 模擬器 (內建): 可用")
                aer_available = True
                aer_method = "builtin"
            except ImportError:
                print("  ⚠️ 內建 Aer: 不可用")
        
        # 方法3: 基礎模擬器
        if not aer_available:
            try:
                from qiskit.providers.basic_provider import BasicSimulator
                basic_sim = BasicSimulator()
                print("  ✅ 基礎模擬器: 可用 (性能較低)")
                aer_available = True
                aer_method = "basic"
            except ImportError:
                print("  ❌ 基礎模擬器: 不可用")
        
        if not aer_available:
            self.issues.append("無可用的量子模擬器")
            self.recommendations.append("安裝 Aer: pip install qiskit-aer")
            return False
        
        # 測試量子電路執行
        try:
            print("     🌌 測試量子電路執行...")
            from qiskit import QuantumCircuit, transpile
            
            qc = QuantumCircuit(2, 2)
            qc.h(0)
            qc.cx(0, 1)
            qc.measure_all()
            
            if aer_method == "qiskit_aer":
                simulator = AerSimulator()
                job = simulator.run(transpile(qc, simulator), shots=100)
                result = job.result()
                counts = result.get_counts(qc)
                print(f"       ✅ 量子電路執行成功: {len(counts)} 種結果")
            elif aer_method == "builtin":
                backend = Aer.get_backend('qasm_simulator')
                job = backend.run(transpile(qc, backend), shots=100)
                result = job.result()
                counts = result.get_counts(qc)
                print(f"       ✅ 量子電路執行成功: {len(counts)} 種結果")
            else:
                print("       ⚠️ 基礎模擬器測試跳過")
                
        except Exception as e:
            print(f"       ❌ 量子電路執行失敗: {e}")
            self.issues.append("量子電路執行失敗")
            self.recommendations.append("重新安裝 qiskit 和 qiskit-aer")
            return False
        
        return True
    
    def check_quantum_pro_structure(self):
        """檢查 quantum_pro 目錄結構"""
        print("\n🔍 檢查 quantum_pro 目錄結構...")
        
        # 定位 quantum_pro 目錄
        current_dir = Path(__file__).parent
        quantum_pro_dir = current_dir
        
        required_files = [
            'regime_hmm_quantum.py',
            'btc_quantum_ultimate_model.py',
            '__init__.py',
            'launcher/quantum_adaptive_trading_launcher.py',
            'launcher/quantum_adaptive_signal_engine.py',
            'launcher/quantum_model_trainer.py',
            'config/model_paths.py'
        ]
        
        missing_files = []
        
        for file_path in required_files:
            full_path = quantum_pro_dir / file_path
            if full_path.exists():
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path}: 缺失")
                missing_files.append(file_path)
        
        # 檢查模型目錄
        models_dir = quantum_pro_dir / "data" / "models"
        if models_dir.exists():
            model_files = list(models_dir.glob("quantum_model_*.pkl"))
            print(f"  📊 已訓練模型: {len(model_files)}/7")
            
            for model_file in model_files:
                coin = model_file.stem.replace("quantum_model_", "").upper()
                print(f"     ✅ {coin}")
                
            if len(model_files) == 0:
                self.recommendations.append("運行模型訓練: python quantum_pro/launcher/quantum_model_trainer.py")
            elif len(model_files) < 7:
                self.recommendations.append("補充訓練缺失的模型")
        else:
            print(f"  ❌ 模型目錄不存在: {models_dir}")
            models_dir.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ 已創建模型目錄: {models_dir}")
        
        if missing_files:
            self.issues.append(f"缺少必要檔案: {', '.join(missing_files)}")
            
        return len(missing_files) == 0
    
    def run_full_check(self):
        """執行完整檢測"""
        self.print_header()
        
        results = {
            'python_version': self.check_python_version(),
            'virtual_environment': self.check_virtual_environment(),
            'core_dependencies': self.check_core_dependencies(),
            'quantum_computing': self.check_quantum_computing(),
            'quantum_pro_structure': self.check_quantum_pro_structure()
        }
        
        self.print_summary(results)
        return results
    
    def print_summary(self, results):
        """打印檢測總結"""
        print("\n" + "=" * 60)
        print("📊 檢測總結")
        print("=" * 60)
        
        total_checks = len(results)
        passed_checks = sum(results.values())
        
        print(f"🎯 通過檢測: {passed_checks}/{total_checks}")
        
        if passed_checks == total_checks:
            print("🎉 恭喜！量子環境配置完美！")
            print("🚀 可以直接運行 quantum_pro 系統")
        else:
            print("⚠️ 發現環境問題，需要修復")
        
        if self.issues:
            print("\n❌ 發現的問題:")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        
        if self.recommendations:
            print("\n💡 建議修復步驟:")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "=" * 60)
    
    def auto_fix_environment(self):
        """自動修復環境問題"""
        print("\n🔧 自動修復環境問題...")
        
        if not self.check_core_dependencies():
            print("📦 自動安裝缺失的核心依賴...")
            try:
                subprocess.run([
                    self.python_executable, "-m", "pip", "install", "--upgrade",
                    "numpy", "scipy", "pandas", "scikit-learn", "requests", 
                    "aiohttp", "websockets", "ccxt", "fastapi", "uvicorn", "pydantic"
                ], check=True, capture_output=True, text=True)
                print("  ✅ 核心依賴安裝完成")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ 安裝失敗: {e}")
        
        if not self.check_quantum_computing():
            print("🔮 自動安裝量子計算依賴...")
            try:
                subprocess.run([
                    self.python_executable, "-m", "pip", "install", "--upgrade",
                    "qiskit", "qiskit-aer", "qiskit-ibm-runtime"
                ], check=True, capture_output=True, text=True)
                print("  ✅ 量子計算依賴安裝完成")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ 安裝失敗: {e}")
        
        print("🔄 重新檢測環境...")
        return self.run_full_check()


def main():
    """主函數"""
    checker = QuantumEnvironmentChecker()
    
    # 執行檢測
    results = checker.run_full_check()
    
    # 如果有問題，詢問是否自動修復
    if not all(results.values()) and checker.recommendations:
        response = input("\n❓ 是否嘗試自動修復環境問題？(y/N): ").strip().lower()
        if response in ['y', 'yes']:
            checker.auto_fix_environment()
    
    return results


if __name__ == "__main__":
    main()
