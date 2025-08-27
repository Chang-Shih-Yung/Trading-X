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
    echo "🚀 量子計算模組檢查："
    python -c "
try:
    import qiskit
    from qiskit import QuantumCircuit
    print('  ✅ Qiskit: 量子計算框架運作正常')
    print(f'  📦 Qiskit 版本: {qiskit.__version__}')
    
    # 測試量子電路
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    print('  🌌 量子電路創建: 成功')
    
    # 檢查 Aer 模擬器（quantum_pro 必需）
    aer_available = False
    try:
        from qiskit_aer import Aer
        import qiskit_aer
        backend = Aer.get_backend('qasm_simulator')
        print('  ✅ Aer 模擬器: 可用 (qiskit_aer)')
        print(f'  📦 Aer 版本: {qiskit_aer.__version__}')
        aer_available = True
    except ImportError:
        try:
            from qiskit import Aer
            backend = Aer.get_backend('qasm_simulator')
            print('  ✅ Aer 模擬器: 可用 (qiskit 內建)')
            aer_available = True
        except ImportError:
            print('  ❌ Aer 模擬器: 未安裝 (quantum_pro 必需)')
            aer_available = False
    
    if not aer_available:
        print('  ⚠️  警告: quantum_pro 模組需要 Aer 模擬器才能正常運作')
        print('  💡 安裝指令: pip install qiskit[aer] 或 pip install qiskit-aer')
    
except ImportError as e:
    print(f'  ❌ Qiskit 未安裝或有問題: {e}')
except Exception as e:
    print(f'  ⚠️  Qiskit 功能測試失敗: {e}')
"
    
    # quantum_pro 模組檢查
    echo ""
    echo "🌌 quantum_pro 模組檢查："
    python -c "
try:
    import sys
    sys.path.append('.')
    from quantum_pro.regime_hmm_quantum import QUANTUM_ENTANGLED_COINS, ENTANGLEMENT_PAIRS
    print(f'  ✅ 七幣種糾纏池: {len(QUANTUM_ENTANGLED_COINS)} 幣種')
    print(f'  ✅ 量子糾纏對: {len(ENTANGLEMENT_PAIRS)} 對')
    print('  ✅ 量子糾纏系統: 運作正常')
except ImportError as e:
    print(f'  ❌ quantum_pro 模組導入失敗: {e}')
except Exception as e:
    print(f'  ⚠️  quantum_pro 模組功能測試失敗: {e}')
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
echo "  🌌 量子模組狀態: $([ -d "venv" ] && source venv/bin/activate && python -c "import qiskit; print('正常')" 2>/dev/null || echo "需要安裝")"

echo ""
echo "💡 如果有任何 ❌ 項目，請執行："
echo "   ./setup-dev-environment.sh"
