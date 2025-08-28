#!/bin/bash

# Trading X 統一開發環境配置腳本 v2.0
# 支援跨設備一致性開發，自動虛擬環境管理
# 完整量子交易系統依賴安裝 (2025-08-28)
# 兼容不同 Python 命令環境 (python vs python3)

set -e  # 發生錯誤時立即退出

echo "🚀 Trading X 統一開發環境配置 v2.0"
echo "===================================="
echo "🔧 自動檢測並配置：虛擬環境 + 量子依賴 + ML套件"

# 取得腳本絕對路徑
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "📁 專案根目錄: $PROJECT_ROOT"

# 全局變量
VENV_NAME="trading-x-env"
VENV_PATH="$PROJECT_ROOT/$VENV_NAME"
USE_VENV=true

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

# 函式：檢查是否需要虛擬環境
check_venv_needed() {
    echo "🔍 檢查虛擬環境需求..."
    
    # 檢查是否在 conda 環境中
    if [[ -n "$CONDA_DEFAULT_ENV" ]]; then
        echo "✅ 檢測到 Conda 環境: $CONDA_DEFAULT_ENV"
        echo "❓ 是否要使用現有 Conda 環境而非創建虛擬環境？[y/N]"
        read -r use_conda
        if [[ "$use_conda" =~ ^[Yy]$ ]]; then
            USE_VENV=false
            echo "🐍 將使用 Conda 環境進行安裝"
        fi
    fi
    
    # 檢查是否已有虛擬環境
    if [[ "$USE_VENV" == true ]] && [[ -d "$VENV_PATH" ]]; then
        echo "✅ 發現現有虛擬環境: $VENV_PATH"
        echo "❓ 是否要重新創建虛擬環境？[y/N]"
        read -r recreate_venv
        if [[ "$recreate_venv" =~ ^[Yy]$ ]]; then
            echo "🗑️ 刪除現有虛擬環境..."
            rm -rf "$VENV_PATH"
        fi
    fi
}

# 函式：設置虛擬環境
setup_virtual_environment() {
    if [[ "$USE_VENV" == true ]]; then
        if [[ ! -d "$VENV_PATH" ]]; then
            echo "🔨 創建 Python 虛擬環境..."
            $PYTHON_CMD -m venv "$VENV_PATH"
        fi
        
        echo "🔌 激活虛擬環境..."
        source "$VENV_PATH/bin/activate"
        PYTHON_CMD="$VENV_PATH/bin/python"
        PIP_CMD="$VENV_PATH/bin/pip"
    else
        echo "🐍 使用系統/Conda Python 環境"
        PIP_CMD="pip"
    fi
}

# 函式：安裝量子依賴
install_quantum_dependencies() {
    echo "⚛️ 安裝量子計算依賴..."
    
    # 升級 pip
    $PIP_CMD install --upgrade pip
    
    # 安裝核心量子依賴 (固定版本以確保相容性)
    echo "📦 安裝 Qiskit 1.2.4 (相容版本)..."
    $PIP_CMD install qiskit==1.2.4 qiskit-algorithms==0.3.1
    
    # 檢查是否需要重新安裝 rustworkx
    if ! $PYTHON_CMD -c "import rustworkx" 2>/dev/null; then
        echo "🦀 安裝 rustworkx..."
        $PIP_CMD install rustworkx
    fi
}

# 函式：安裝機器學習依賴
install_ml_dependencies() {
    echo "🤖 安裝機器學習依賴..."
    
    # 安裝 XGBoost
    $PIP_CMD install xgboost
    
    # 安裝相容版本的 LightGBM 和 Dask
    $PIP_CMD install "lightgbm>=4.4.0,<4.5.0"
    $PIP_CMD install "dask>=2023.1.0"
    
    echo "✅ 機器學習套件安裝完成"
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

# 檢查虛擬環境需求
check_venv_needed

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

# 安裝 OpenMP (XGBoost 需要)
echo "🔧 安裝 OpenMP (XGBoost 依賴)..."
brew install libomp

# 設置虛擬環境
setup_virtual_environment

# 安裝量子依賴
install_quantum_dependencies

# 安裝機器學習依賴
install_ml_dependencies
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

# 🌌 安裝量子計算依賴 (quantum_pro) - 多階段穩健安裝
echo "🚀 安裝 quantum_pro 量子計算依賴..."

# 第一階段：核心科學計算依賴
echo "📊 階段1: 安裝核心科學計算套件..."
$VENV_PYTHON -m pip install --upgrade pip setuptools wheel
$VENV_PYTHON -m pip install numpy scipy pandas scikit-learn

# 第二階段：網路和API依賴
echo "🌐 階段2: 安裝網路通訊套件..."
$VENV_PYTHON -m pip install ccxt websockets asyncio-mqtt requests aiohttp aiofiles

# 第三階段：Web框架依賴
echo "🚀 階段3: 安裝Web框架..."
$VENV_PYTHON -m pip install fastapi uvicorn pydantic python-multipart

# 第四階段：量子計算依賴 (關鍵優化)
echo "� 階段4: 安裝量子計算框架..."
echo "   🎯 正在安裝 Qiskit 2.x + Aer 模擬器..."

# 強制安裝最新穩定版 Qiskit
$VENV_PYTHON -m pip install --upgrade qiskit qiskit-aer qiskit-ibm-runtime

# 🔧 解決常見的 Qiskit 安裝問題
echo "   🔧 修復可能的依賴衝突..."
$VENV_PYTHON -m pip install --upgrade rustworkx qiskit-terra

# 驗證量子計算套件 (增強版檢測)
echo "🔬 驗證量子計算套件..."
$VENV_PYTHON -c "
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

print('🔍 量子計算環境檢測:')

# 基礎檢測
try:
    import qiskit
    print(f'  ✅ Qiskit 核心: {qiskit.__version__}')
    
    # 測試量子電路
    from qiskit import QuantumCircuit, transpile
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    print('  ✅ 量子電路構建: 成功')
    
except ImportError as e:
    print(f'  ❌ Qiskit 核心安裝失敗: {e}')
    exit(1)

# Aer 模擬器檢測 (多重檢測機制)
aer_detected = False

# 方法1: 檢測 qiskit_aer
try:
    from qiskit_aer import AerSimulator
    import qiskit_aer
    simulator = AerSimulator()
    print(f'  ✅ Aer 模擬器 (qiskit_aer): {qiskit_aer.__version__}')
    aer_detected = True
except ImportError:
    print('  ⚠️ qiskit_aer 模組未安裝')

# 方法2: 檢測內建 Aer (舊版本)
if not aer_detected:
    try:
        from qiskit import Aer
        backend = Aer.get_backend('qasm_simulator') 
        print('  ✅ Aer 模擬器 (內建版本): 可用')
        aer_detected = True
    except ImportError:
        print('  ⚠️ 內建 Aer 模組未找到')

# 方法3: 嘗試基礎模擬器
if not aer_detected:
    try:
        from qiskit.providers.basic_provider import BasicSimulator
        basic_sim = BasicSimulator()
        print('  ⚠️ 使用基礎模擬器 (性能較低)')
        aer_detected = True
    except ImportError:
        print('  ⚠️ 基礎模擬器也無法使用')

# 最終檢測結果
if aer_detected:
    print('  🎯 量子模擬器: 可用 (quantum_pro 可運行)')
    
    # 執行完整量子測試
    try:
        if 'AerSimulator' in locals():
            job = simulator.run(transpile(qc, simulator), shots=100)
            result = job.result()
            counts = result.get_counts(qc)
            print(f'  🌌 量子電路執行測試: 成功 {len(counts)} 種結果')
        else:
            print('  🌌 量子電路執行測試: 跳過 (基礎模擬器)')
    except Exception as e:
        print(f'  ⚠️ 量子電路執行警告: {e}')
        
else:
    print('  ❌ 嚴重警告: 無可用的量子模擬器!')
    print('  💡 建議執行: pip install qiskit-aer')
    print('  🚨 quantum_pro 模組可能無法正常運行')

print('  🔮 量子環境檢測完成')
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
    from pathlib import Path
    sys.path.append('.')
    
    # 檢查目錄結構
    quantum_pro_dir = Path('quantum_pro')
    if quantum_pro_dir.exists():
        print('  ✅ quantum_pro 目錄: 存在')
        
        # 檢查關鍵檔案
        key_files = [
            'regime_hmm_quantum.py',
            'launcher/quantum_adaptive_trading_launcher.py',
            'launcher/一鍵啟動_量子自適應.sh',
            'check_quantum_environment.py'
        ]
        
        missing_files = []
        for file_path in key_files:
            if (quantum_pro_dir / file_path).exists():
                print(f'  ✅ {file_path}: 存在')
            else:
                print(f'  ❌ {file_path}: 缺失')
                missing_files.append(file_path)
        
        if missing_files:
            print(f'  ⚠️ 缺少 {len(missing_files)} 個關鍵檔案')
        
        # 檢查模組導入
        try:
            from quantum_pro.regime_hmm_quantum import QUANTUM_ENTANGLED_COINS, ENTANGLEMENT_PAIRS
            print(f'  ✅ 核心模組導入: 成功')
            print(f'  📊 量子糾纏幣種: {len(QUANTUM_ENTANGLED_COINS)} 種')
            print(f'  🔗 糾纏關係: {len(ENTANGLEMENT_PAIRS)} 對')
        except ImportError as e:
            print(f'  ⚠️ 核心模組導入: 失敗 ({e})')
        
        # 檢查模型目錄
        models_dir = quantum_pro_dir / 'data' / 'models'
        if models_dir.exists():
            model_files = list(models_dir.glob('quantum_model_*.pkl'))
            print(f'  📈 已訓練模型: {len(model_files)}/7')
            if len(model_files) == 0:
                print('  💡 首次使用請執行: make train-quantum')
            elif len(model_files) < 7:
                print('  💡 模型不完整，建議重新訓練: make train-quantum')
        else:
            print('  📁 模型目錄: 不存在 (將自動創建)')
            models_dir.mkdir(parents=True, exist_ok=True)
            print(f'  ✅ 已創建模型目錄: {models_dir}')
    else:
        print('  ❌ quantum_pro 目錄: 不存在')
        
except Exception as e:
    print(f'  ❌ quantum_pro 模組檢查異常: {e}')
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
echo "   🌌 量子環境: 已配置"
echo ""
echo "🚀 下一步操作："
echo "   1. 重新啟動 VS Code"
echo "   2. 確認 Python 解譯器指向: ./venv/bin/python"
echo "   3. make verify       # 驗證完整環境"
echo "   4. make check-quantum # 檢查量子環境"
echo "   5. make run-quantum   # 啟動量子交易系統"
echo ""
echo "⚡ 量子系統快速啟動："
echo "   make run-quantum  # 自動檢測模型狀態並啟動"
echo ""
echo "🔧 跨設備兼容性："
echo "   ✅ 自動檢測 python vs python3 命令"
echo "   ✅ 統一虛擬環境 Python 路徑: ./venv/bin/python"
echo "   ✅ 智能量子依賴安裝與驗證"
echo "   ✅ 量子模型自動檢測與訓練提示"
echo "   ✅ 所有設備行為完全一致"
