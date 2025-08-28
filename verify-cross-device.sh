#!/bin/bash

# Trading X 跨設備環境驗證腳本
# 檢查 Pylance 設定是否正確應用

echo "🔍 Trading X 跨設備環境驗證"
echo "=============================="

# 檢查 Python 命令
echo "🐍 Python 環境檢查："
if command -v python3 &> /dev/null; then
    echo "  ✅ python3: $(python3 --version)"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    version=$(python --version 2>&1 | grep -o "Python [0-9]" | grep -o "[0-9]")
    if [[ "$version" == "3" ]]; then
        echo "  ✅ python: $(python --version)"
        PYTHON_CMD="python"
    else
        echo "  ❌ python: Python 2 不支援"
        exit 1
    fi
else
    echo "  ❌ 未找到 Python"
    exit 1
fi

# 檢查虛擬環境
echo ""
echo "🔧 虛擬環境檢查："
if [ -d "venv" ]; then
    echo "  ✅ 虛擬環境存在"
    if [ -f "venv/bin/python" ]; then
        echo "  ✅ Python 執行檔: $(./venv/bin/python --version)"
    else
        echo "  ❌ 虛擬環境 Python 執行檔不存在"
    fi
else
    echo "  ❌ 虛擬環境不存在"
fi

# 檢查 VS Code 設定
echo ""
echo "⚙️ VS Code 設定檢查："
if [ -f ".vscode/settings.json" ]; then
    echo "  ✅ settings.json 存在"
    
    # 檢查關鍵設定
    if grep -q '"python.analysis.typeCheckingMode": "off"' .vscode/settings.json; then
        echo "  ✅ Pylance 類型檢查已關閉"
    else
        echo "  ❌ Pylance 類型檢查未正確關閉"
    fi
    
    if grep -q '"python.linting.enabled": false' .vscode/settings.json; then
        echo "  ✅ Python Linting 已關閉"
    else
        echo "  ❌ Python Linting 未關閉"
    fi
    
    if grep -q './venv/bin/python' .vscode/settings.json; then
        echo "  ✅ Python 解譯器路徑正確"
    else
        echo "  ❌ Python 解譯器路徑設定有問題"
    fi
else
    echo "  ❌ VS Code 設定檔不存在"
fi

# 檢查專案檔案
echo ""
echo "📁 專案檔案檢查："
files_to_check=("requirements.txt" "pyproject.toml" ".pylintrc" ".env")
for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file 存在"
    else
        echo "  ⚠️  $file 不存在"
    fi
done

# 測試模組導入
echo ""
echo "📦 關鍵模組測試："
if [ -d "venv" ]; then
    source venv/bin/activate
    
    modules=("pandas" "numpy" "aiosqlite" "fastapi" "talib" "pandas_ta" "qiskit" "scipy" "ccxt" "websockets" "pydantic")
    for module in "${modules[@]}"; do
        if python -c "import $module" 2>/dev/null; then
            echo "  ✅ $module 可正常導入"
        else
            echo "  ❌ $module 導入失敗"
        fi
    done
    
    # 🌌 量子計算模組專項檢查
    echo ""
    echo "🚀 量子計算環境檢查："
    python -c "
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

try:
    import qiskit
    from qiskit import QuantumCircuit
    print('  ✅ Qiskit 核心: 量子計算框架運作正常')
    print(f'  📦 Qiskit 版本: {qiskit.__version__}')
    
    # 檢查版本是否為 1.x+ (推薦) 或 0.x (可用)
    try:
        major_version = int(qiskit.__version__.split('.')[0])
        if major_version >= 1:
            print(f'     🎯 Qiskit 版本狀態: 最新 v{major_version}.x (推薦)')
        else:
            print(f'     ⚠️ Qiskit 版本狀態: 舊版 v{major_version}.x (可用，建議升級)')
    except:
        print(f'     ⚠️ Qiskit 版本解析: 無法確定 ({qiskit.__version__})')
    
    # 測試量子電路創建
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    print('  🌌 量子電路創建: 成功')
    
    # 檢查 Aer 模擬器（多重檢測機制）
    aer_available = False
    aer_method = None
    
    # 方法1: 檢測 qiskit_aer (推薦)
    try:
        from qiskit_aer import AerSimulator
        import qiskit_aer
        simulator = AerSimulator()
        print(f'  ✅ Aer 模擬器 (qiskit_aer): {qiskit_aer.__version__}')
        aer_available = True
        aer_method = 'qiskit_aer'
    except ImportError:
        print('  ⚠️ qiskit_aer: 未安裝')
    
    # 方法2: 檢測內建 Aer (舊版本)
    if not aer_available:
        try:
            from qiskit import Aer
            backend = Aer.get_backend('qasm_simulator')
            print('  ✅ Aer 模擬器 (內建): 可用')
            aer_available = True
            aer_method = 'builtin'
        except ImportError:
            print('  ⚠️ 內建 Aer: 不可用')
    
    # 方法3: 基礎模擬器
    if not aer_available:
        try:
            from qiskit.providers.basic_provider import BasicSimulator
            basic_sim = BasicSimulator()
            print('  ✅ 基礎模擬器: 可用 (性能較低)')
            aer_available = True
            aer_method = 'basic'
        except ImportError:
            print('  ❌ 基礎模擬器: 不可用')
    
    if not aer_available:
        print('  ❌ 嚴重問題: 無可用的量子模擬器!')
        print('  💡 修復建議: pip install qiskit-aer')
        print('  🚨 quantum_pro 模組將無法正常運作')
    else:
        print(f'  🎯 量子模擬器狀態: 可用 (使用 {aer_method})')
        
        # 執行量子電路測試
        try:
            from qiskit import transpile
            if aer_method == 'qiskit_aer':
                job = simulator.run(transpile(qc, simulator), shots=100)
                result = job.result()
                counts = result.get_counts(qc)
                print(f'       ✅ 量子電路執行測試: 成功 ({len(counts)} 種結果)')
            elif aer_method == 'builtin':
                job = backend.run(transpile(qc, backend), shots=100)
                result = job.result()
                counts = result.get_counts(qc)
                print(f'       ✅ 量子電路執行測試: 成功 ({len(counts)} 種結果)')
            else:
                print('       ⚠️ 基礎模擬器測試跳過 (功能有限)')
        except Exception as e:
            print(f'       ⚠️ 量子電路執行警告: {e}')
    
except ImportError as e:
    print(f'  ❌ Qiskit 未安裝: {e}')
    print('  💡 安裝指令: pip install qiskit qiskit-aer')
except Exception as e:
    print(f'  ⚠️ Qiskit 功能測試異常: {e}')
"
    
    # quantum_pro 模組檢查
    echo ""
    echo "🌌 quantum_pro 模組結構檢查："
    python -c "
try:
    import sys
    import os
    from pathlib import Path
    
    # 檢查 quantum_pro 目錄結構
    quantum_pro_dir = Path('quantum_pro')
    if not quantum_pro_dir.exists():
        print('  ❌ quantum_pro 目錄不存在')
        exit(1)
    
    required_files = [
        'regime_hmm_quantum.py',
        'btc_quantum_ultimate_model.py', 
        '__init__.py',
        'launcher/quantum_adaptive_trading_launcher.py',
        'launcher/quantum_adaptive_signal_engine.py',
        'launcher/quantum_model_trainer.py',
        'launcher/一鍵啟動_量子自適應.sh',
        'config/model_paths.py',
        'check_quantum_environment.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = quantum_pro_dir / file_path
        if full_path.exists():
            print(f'  ✅ {file_path}')
        else:
            print(f'  ❌ {file_path}: 缺失')
            missing_files.append(file_path)
    
    # 檢查模型目錄
    models_dir = quantum_pro_dir / 'data' / 'models'
    if models_dir.exists():
        model_files = list(models_dir.glob('quantum_model_*.pkl'))
        print(f'  📊 已訓練量子模型: {len(model_files)}/7')
        
        expected_coins = ['btc', 'eth', 'ada', 'sol', 'xrp', 'doge', 'bnb']
        trained_coins = []
        
        for model_file in model_files:
            coin = model_file.stem.replace('quantum_model_', '').lower()
            trained_coins.append(coin)
            print(f'     ✅ {coin.upper()} 模型已訓練')
        
        missing_coins = set(expected_coins) - set(trained_coins)
        if missing_coins:
            print(f'  ⚠️ 缺少模型: {list(missing_coins)}')
            print('  💡 執行訓練: make train-quantum 或 cd quantum_pro/launcher && python quantum_model_trainer.py')
        else:
            print('  🎯 所有幣種模型完整')
    else:
        print(f'  ❌ 模型目錄不存在: {models_dir}')
        print('  💡 首次使用需要執行: make train-quantum')
    
    # 測試核心模組導入
    sys.path.append('.')
    try:
        from quantum_pro.regime_hmm_quantum import QUANTUM_ENTANGLED_COINS, ENTANGLEMENT_PAIRS
        print(f'  ✅ 核心模組: {len(QUANTUM_ENTANGLED_COINS)} 幣種糾纏池')
        print(f'  ✅ 糾纏關係: {len(ENTANGLEMENT_PAIRS)} 對糾纏')
        print('  ✅ 量子糾纏系統: 運作正常')
    except ImportError as e:
        print(f'  ❌ 核心模組導入失敗: {e}')
    except Exception as e:
        print(f'  ⚠️ 核心模組測試異常: {e}')
    
    if missing_files:
        print(f'  🚨 結構完整性: 缺少 {len(missing_files)} 個必要檔案')
    else:
        print('  ✅ 結構完整性: 所有必要檔案齊全')
        
except Exception as e:
    print(f'  ❌ quantum_pro 結構檢查失敗: {e}')
"
else
    echo "  ⚠️  無法測試（虛擬環境不存在）"
fi

# 輸出結果摘要
echo ""
echo "📊 環境驗證摘要："
echo "  🖥️  設備: $(hostname)"
echo "  🐍 Python 命令: $PYTHON_CMD"
echo "  📂 專案路徑: $(pwd)"
echo "  🔧 Pylance 狀態: $(grep -q '"python.analysis.typeCheckingMode": "off"' .vscode/settings.json 2>/dev/null && echo "已關閉" || echo "需要配置")"

# 量子環境狀態檢查
if [ -d "venv" ]; then
    source venv/bin/activate
    quantum_status=$(python -c "
try:
    import qiskit
    try:
        from qiskit_aer import AerSimulator
        print('完整')
    except ImportError:
        try:
            from qiskit import Aer
            print('基礎')
        except ImportError:
            print('缺失模擬器')
    except Exception:
        print('異常')
except ImportError:
    print('未安裝')
except Exception:
    print('錯誤')
" 2>/dev/null)
    
    model_count=$(find quantum_pro/data/models -name "quantum_model_*.pkl" 2>/dev/null | wc -l)
    
    echo "  🌌 量子環境: $quantum_status"
    echo "  🎯 量子模型: $model_count/7 個已訓練"
else
    echo "  🌌 量子環境: 無法檢測 (虛擬環境未啟用)"
    echo "  🎯 量子模型: 無法檢測"
fi

echo ""
echo "💡 修復建議："
if [ ! -d "venv" ] || ! grep -q '"python.analysis.typeCheckingMode": "off"' .vscode/settings.json 2>/dev/null; then
    echo "   🔧 基礎環境: ./setup-dev-environment.sh"
fi

if [ -d "venv" ]; then
    source venv/bin/activate
    if ! python -c "import qiskit" 2>/dev/null; then
        echo "   🔮 量子依賴: make setup (會自動安裝 Qiskit)"
    fi
    
    model_count=$(find quantum_pro/data/models -name "quantum_model_*.pkl" 2>/dev/null | wc -l)
    if [ "$model_count" -lt 7 ]; then
        echo "   🎯 量子模型: make train-quantum (訓練量子模型)"
    fi
fi

echo ""
echo "🚀 快速啟動指令："
echo "   make setup         # 完整環境設置"
echo "   make verify        # 重新驗證環境"
echo "   make check-quantum # 詳細量子環境檢查"
echo "   make run-quantum   # 啟動量子交易系統"
