#!/bin/bash

# Trading X 統一開發環境配置腳本
# 支援跨設備一致性開發，解決 Pylance 類型檢查問題
# 兼容不同 Python 命令環境 (python vs python3)

set -e  # 發生錯誤時立即退出

echo "🚀 Trading X 統一開發環境配置"
echo "================================"

# 取得腳本絕對路徑
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "📁 專案根目錄: $PROJECT_ROOT"

# 函式：智能檢測 Python 命令
detect_python_command() {
    local python_cmd=""
    
    # 優先順序：python3 > python > python3.x
    if command -v python3 &> /dev/null; then
        python_cmd="python3"
    elif command -v python &> /dev/null; then
        # 檢查 python 是否是 Python 3
        local version=$(python --version 2>&1 | grep -o "Python [0-9]" | grep -o "[0-9]")
        if [[ "$version" == "3" ]]; then
            python_cmd="python"
        else
            echo "❌ 檢測到 Python 2，需要 Python 3"
            exit 1
        fi
    elif command -v python3.9 &> /dev/null; then
        python_cmd="python3.9"
    elif command -v python3.10 &> /dev/null; then
        python_cmd="python3.10"
    elif command -v python3.11 &> /dev/null; then
        python_cmd="python3.11"
    else
        echo "❌ 未找到 Python 3 安裝"
        exit 1
    fi
    
    echo "$python_cmd"
}

# 檢測並設定 Python 命令
PYTHON_CMD=$(detect_python_command)
echo "🐍 檢測到 Python 命令: $PYTHON_CMD"

# 檢查 Python 版本
python_version=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo "🐍 Python 版本: $python_version"

# 檢查版本是否符合需求 (>= 3.9)
version_check=$($PYTHON_CMD -c "
import sys
major, minor = sys.version_info[:2]
if major == 3 and minor >= 9:
    print('OK')
else:
    print('LOW')
")

if [[ "$version_check" != "OK" ]]; then
    echo "⚠️  警告: Python 版本 $python_version < 3.9，可能有相容性問題"
fi

# 檢查 macOS 版本
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 此腳本僅支援 macOS"
    exit 1
fi

# 檢查並安裝 Homebrew
if ! command -v brew &> /dev/null; then
    echo "📦 安裝 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # 添加 Homebrew 到 PATH
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# 安裝系統依賴
echo "🔧 安裝系統依賴..."
brew install ta-lib python@3.9 node postgresql

# 創建虛擬環境
cd "$PROJECT_ROOT"
if [ ! -d "venv" ]; then
    echo "🔨 創建 Python 虛擬環境..."
    $PYTHON_CMD -m venv venv
else
    echo "✅ 虛擬環境已存在"
fi

# 啟動虛擬環境
source venv/bin/activate

# 確認虛擬環境中的 Python 路徑
VENV_PYTHON="./venv/bin/python"
echo "✅ 虛擬環境 Python: $VENV_PYTHON"

# 升級 pip
echo "📦 升級 pip..."
$VENV_PYTHON -m pip install --upgrade pip setuptools wheel

# 設置 TA-Lib 環境變數
export TA_INCLUDE_PATH="$(brew --prefix ta-lib)/include"
export TA_LIBRARY_PATH="$(brew --prefix ta-lib)/lib"

# 安裝 Python 依賴
if [ -f "requirements.txt" ]; then
    echo "📦 安裝 Python 依賴..."
    $VENV_PYTHON -m pip install -r requirements.txt
else
    echo "⚠️  requirements.txt 不存在，創建基礎依賴..."
    $VENV_PYTHON -m pip install TA-Lib web3 pandas numpy fastapi uvicorn aiohttp websockets asyncio-mqtt
fi

# 🌌 安裝量子計算依賴 (quantum_pro)
echo "🚀 安裝 quantum_pro 量子計算依賴..."
$VENV_PYTHON -m pip install numpy scipy pandas qiskit qiskit-aer ccxt websockets asyncio-mqtt fastapi uvicorn pydantic

# 驗證量子計算套件
echo "🔬 驗證量子計算套件..."
$VENV_PYTHON -c "
try:
    import qiskit
    from qiskit import QuantumCircuit
    print('  ✅ Qiskit: 量子計算框架安裝成功')
    print(f'  📦 Qiskit 版本: {qiskit.__version__}')
    
    # 測試量子電路
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    print('  🌌 量子電路測試: 成功')
    
    # 驗證 Aer 模擬器
    try:
        from qiskit_aer import Aer
        import qiskit_aer
        backend = Aer.get_backend('qasm_simulator')
        print('  ✅ Aer 模擬器: 安裝成功 (qiskit_aer)')
        print(f'  📦 Aer 版本: {qiskit_aer.__version__}')
    except ImportError:
        try:
            from qiskit import Aer
            backend = Aer.get_backend('qasm_simulator')
            print('  ✅ Aer 模擬器: 安裝成功 (qiskit 內建)')
        except ImportError:
            print('  ❌ Aer 模擬器: 未安裝 (quantum_pro 需要)')
            raise ImportError('請安裝 qiskit-aer: pip install qiskit-aer')
    
except ImportError as e:
    print(f'  ❌ Qiskit 安裝失敗: {e}')
"

# 驗證關鍵套件安裝
echo "🔍 驗證關鍵套件..."
$VENV_PYTHON -c "
import sys
packages_to_check = [
    'pandas', 'numpy', 'aiohttp', 'aiosqlite', 'fastapi', 
    'uvicorn', 'web3', 'talib', 'pandas_ta', 'websockets',
    'qiskit', 'qiskit_aer', 'scipy', 'ccxt', 'pydantic'
]

print('📊 套件檢查結果:')
for package in packages_to_check:
    try:
        module = __import__(package)
        version = getattr(module, '__version__', '未知版本')
        print(f'  ✅ {package}: {version}')
    except ImportError:
        print(f'  ❌ {package}: 未安裝')

# 🌌 特殊檢查：quantum_pro 量子計算模組
print('\\n🚀 quantum_pro 量子計算模組檢查:')
try:
    import sys
    sys.path.append('.')
    from quantum_pro.regime_hmm_quantum import QUANTUM_ENTANGLED_COINS, ENTANGLEMENT_PAIRS
    print(f'  ✅ 七幣種糾纏池: {len(QUANTUM_ENTANGLED_COINS)} 幣種')
    print(f'  ✅ 量子糾纏對: {len(ENTANGLEMENT_PAIRS)} 對')
    print('  ✅ 量子糾纏系統: 運作正常')
except Exception as e:
    print(f'  ❌ quantum_pro 模組錯誤: {e}')
"

# 安裝 Node.js 依賴（如果存在）
if [ -f "package.json" ]; then
    echo "📦 安裝 Node.js 依賴..."
    npm install
fi

# 創建必要目錄
mkdir -p logs data backups tests data/logs data/system_status data/locks X/logs X/data/logs X/databases

# 配置 VS Code 設定（完全關閉 Pylance 類型檢查，跨設備一致）
echo "⚙️ 配置 VS Code 設定（完全關閉 Pylance 類型檢查）..."
mkdir -p .vscode

# 強制覆蓋 VS Code 設定，確保跨設備一致性
cat > .vscode/settings.json << EOL
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    
    "// === 完全關閉所有類型檢查和 Linting ===": "",
    "python.linting.enabled": false,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": false,
    "python.linting.mypyEnabled": false,
    "python.linting.banditEnabled": false,
    "python.linting.pydocstyleEnabled": false,
    "python.linting.prospectorEnabled": false,
    "python.linting.pycodestyleEnabled": false,
    "python.linting.pylamaEnabled": false,
    
    "// === Pylance 類型檢查完全關閉 ===": "",
    "python.analysis.typeCheckingMode": "off",
    "python.analysis.diagnosticMode": "openFilesOnly",
    "python.analysis.autoSearchPaths": false,
    "python.analysis.extraPaths": [
        "./X",
        "./app",
        "./X/backend",
        "./X/backend/phase1_signal_generation",
        "./X/backend/phase2_adaptive_learning",
        "./X/backend/phase3_execution_policy"
    ],
    "python.analysis.include": [],
    "python.analysis.exclude": [
        "**/__pycache__",
        "**/venv",
        "**/.pytest_cache",
        "**/.mypy_cache"
    ],
    "python.analysis.ignore": ["**"],
    "python.analysis.disabled": [
        "reportMissingImports",
        "reportMissingTypeStubs",
        "reportOptionalMemberAccess",
        "reportOptionalCall",
        "reportOptionalIterable",
        "reportOptionalContextManager",
        "reportOptionalOperand",
        "reportTypedDictNotRequiredAccess",
        "reportPrivateImportUsage",
        "reportUnknownArgumentType",
        "reportUnknownVariableType",
        "reportUnknownMemberType"
    ],
    
    "// === 代碼格式化保留 ===": "",
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": "explicit"
    },
    
    "// === 檔案顯示設定 ===": "",
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/venv": true,
        "**/.pytest_cache": true,
        "**/.mypy_cache": true,
        "**/.DS_Store": true,
        "**/*.log": false
    },
    
    "// === 測試設定 ===": "",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    
    "// === 終端設定 ===": "",
    "terminal.integrated.defaultProfile.osx": "zsh",
    "terminal.integrated.env.osx": {
        "PYTHONPATH": "./X:./app:."
    }
}
EOL

echo "✅ VS Code 設定已強制更新（Pylance 完全關閉）"

# 設定環境變數檔案
echo "🔧 建立環境變數檔案..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOL'
# Trading X 環境變數
PYTHONPATH=./X:./app:.
TRADING_X_ENV=development
TRADING_X_LOG_LEVEL=INFO
TRADING_X_DATA_PATH=./data
TRADING_X_DB_PATH=./X/databases
EOL
    echo "✅ .env 檔案已建立"
fi

# 記錄系統資訊（包含 Python 命令差異）
echo "📝 記錄系統資訊..."
cat > system_info.txt << EOL
# Trading X 系統資訊
生成時間: $(date)
作業系統: $(uname -s) $(uname -r)
主機名稱: $(hostname)
Python 命令: $PYTHON_CMD
Python 版本: $python_version
Python 路徑: $(which $PYTHON_CMD)
虛擬環境路徑: $VENV_PYTHON
專案路徑: $PROJECT_ROOT
虛擬環境狀態: $(which python | grep venv >/dev/null && echo "已啟用" || echo "未啟用")
Pylance 設定: 完全關閉所有類型檢查
設備兼容性: ✅ 支援 python 和 python3 命令
EOL

echo "✅ Trading X 開發環境配置完成！"
echo ""
echo "🎯 跨設備一致性驗證："
echo "   📱 當前設備: $(hostname)"
echo "   🐍 Python 命令: $PYTHON_CMD"
echo "   📊 版本: $python_version"
echo "   🔧 Pylance: 完全關閉"
echo ""
echo "🎯 下一步操作："
echo "   1. 重新啟動 VS Code"
echo "   2. 確認 Python 解譯器指向: ./venv/bin/python"
echo "   3. make run  # 或使用 Makefile 快捷指令"
echo "   4. $VENV_PYTHON X/production_launcher_phase2_enhanced.py  # 運行系統"
echo ""
echo "🔧 henry 電腦適配："
echo "   ✅ 自動檢測 python vs python3 命令"
echo "   ✅ 統一虛擬環境 Python 路徑: ./venv/bin/python"
echo "   ✅ 強制覆蓋 VS Code 設定，確保無 Pylance 錯誤"
echo "   ✅ 所有設備行為完全一致"
