#!/bin/bash

# Trading X 一鍵環境配置腳本
# 跨電腦開發專用 - 自動檢測並配置所有依賴
# 2025-08-28 Version

set -e

echo "🚀 Trading X 一鍵環境配置"
echo "========================="
echo "🔧 自動檢測並安裝：量子計算 + 機器學習 + 交易系統"
echo ""

# 取得腳本路徑
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 檢查作業系統
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 檢測到 macOS"
    OS_TYPE="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 檢測到 Linux"
    OS_TYPE="linux"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "🪟 檢測到 Windows"
    OS_TYPE="windows"
else
    echo "❌ 不支援的作業系統: $OSTYPE"
    exit 1
fi

# 智能檢測 Python
detect_python() {
    local python_cmd=""
    
    if command -v python3 &> /dev/null; then
        python_cmd="python3"
    elif command -v python &> /dev/null; then
        local version=$(python --version 2>&1 | grep -o "Python [0-9]" | grep -o "[0-9]")
        if [[ "$version" == "3" ]]; then
            python_cmd="python"
        fi
    fi
    
    if [[ -z "$python_cmd" ]]; then
        echo "❌ 找不到 Python 3"
        exit 1
    fi
    
    echo "$python_cmd"
}

# 檢測環境類型
detect_environment() {
    if [[ -n "$CONDA_DEFAULT_ENV" ]]; then
        echo "conda"
    elif [[ -n "$VIRTUAL_ENV" ]]; then
        echo "venv"
    else
        echo "system"
    fi
}

# 檢查是否為外部管理環境
check_externally_managed() {
    # 嘗試安裝一個測試包來檢查是否為外部管理
    if $PYTHON_CMD -m pip install --dry-run pip 2>&1 | grep -q "externally-managed-environment"; then
        echo "true"
    else
        echo "false"
    fi
}

PYTHON_CMD=$(detect_python)
ENV_TYPE=$(detect_environment)
EXTERNALLY_MANAGED=$(check_externally_managed)

echo "🐍 Python 命令: $PYTHON_CMD"
echo "🏠 環境類型: $ENV_TYPE"
echo "🔒 外部管理: $EXTERNALLY_MANAGED"

# Python 版本檢查
python_version=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo "📝 Python 版本: $python_version"

# 處理外部管理環境
if [[ "$EXTERNALLY_MANAGED" == "true" && "$ENV_TYPE" == "system" ]]; then
    echo ""
    echo "⚠️ 檢測到外部管理的 Python 環境"
    echo "🔧 需要創建虛擬環境以避免系統包衝突"
    echo ""
    echo "❓ 是否要創建虛擬環境？[Y/n]"
    read -r create_venv
    if [[ ! "$create_venv" =~ ^[Nn]$ ]]; then
        echo "🔨 創建虛擬環境..."
        $PYTHON_CMD -m venv trading-x-env
        source trading-x-env/bin/activate
        PYTHON_CMD="trading-x-env/bin/python"
        echo "✅ 虛擬環境已創建並激活"
        EXTERNALLY_MANAGED="false"
    else
        echo "⚠️ 將使用 --break-system-packages 標記安裝"
    fi
fi

# 檢查是否需要創建虛擬環境
if [[ "$ENV_TYPE" == "system" && "$EXTERNALLY_MANAGED" == "false" ]]; then
    echo ""
    echo "❓ 是否要創建虛擬環境？[Y/n]"
    read -r create_venv
    if [[ ! "$create_venv" =~ ^[Nn]$ ]]; then
        echo "🔨 創建虛擬環境..."
        $PYTHON_CMD -m venv trading-x-env
        source trading-x-env/bin/activate
        PYTHON_CMD="trading-x-env/bin/python"
        echo "✅ 虛擬環境已創建並激活"
    fi
fi

# 函式：安裝系統依賴
install_system_dependencies() {
    echo "🔧 安裝系統依賴..."
    
    case "$OS_TYPE" in
        "macos")
            # 檢查並安裝 Homebrew
            if ! command -v brew &> /dev/null; then
                echo "📦 安裝 Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                
                # 添加 Homebrew 到 PATH
                echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
                eval "$(/opt/homebrew/bin/brew shellenv)"
            fi
            
            # 安裝 OpenMP (XGBoost 依賴)
            echo "🔧 安裝 OpenMP (XGBoost 需要)..."
            brew install libomp || echo "⚠️ OpenMP 安裝失敗，XGBoost 可能無法運行"
            
            # 安裝其他系統依賴
            echo "🔧 安裝其他系統依賴..."
            brew install ta-lib || echo "⚠️ TA-Lib 安裝失敗"
            ;;
            
        "linux")
            # Ubuntu/Debian 系統
            if command -v apt-get &> /dev/null; then
                echo "🔧 更新套件管理器..."
                sudo apt-get update
                
                echo "🔧 安裝 OpenMP 和編譯工具..."
                sudo apt-get install -y libomp-dev gcc g++ make
                
                echo "🔧 安裝 TA-Lib 依賴..."
                sudo apt-get install -y libta-lib-dev
                
            # RedHat/CentOS 系統
            elif command -v yum &> /dev/null; then
                echo "🔧 安裝 OpenMP 和編譯工具..."
                sudo yum install -y libomp-devel gcc gcc-c++ make
                
                echo "🔧 安裝 TA-Lib 依賴..."
                sudo yum install -y ta-lib-devel
            else
                echo "⚠️ 不支援的 Linux 發行版，請手動安裝 OpenMP 和 TA-Lib"
            fi
            ;;
            
        "windows")
            echo "🪟 Windows 系統檢測到"
            echo "💡 Windows 用戶請確保："
            echo "   1. 已安裝 Microsoft Visual C++ Redistributable"
            echo "   2. 已安裝 Microsoft Build Tools 或 Visual Studio"
            echo "   3. OpenMP 通常包含在 Visual Studio 中"
            echo "   4. 如果 XGBoost 安裝失敗，請安裝 Intel MKL 或 OpenMP"
            ;;
    esac
}

# 設置 pip 安裝參數
PIP_ARGS=""
if [[ "$EXTERNALLY_MANAGED" == "true" ]]; then
    PIP_ARGS="--break-system-packages"
    echo "⚠️ 使用 --break-system-packages 標記"
fi

# 安裝系統依賴
install_system_dependencies

# 升級 pip
echo "⬆️ 升級 pip..."
$PYTHON_CMD -m pip install --upgrade pip $PIP_ARGS

# 安裝核心依賴
echo ""
echo "📦 安裝核心依賴..."
$PYTHON_CMD -m pip install -r requirements.txt $PIP_ARGS

# 特殊處理相容性問題
echo ""
echo "🔧 處理相容性問題..."

# 檢查並修復 Qiskit 版本
echo "⚛️ 檢查 Qiskit 版本..."
if ! $PYTHON_CMD -c "import qiskit; print(f'Qiskit: {qiskit.__version__}')" 2>/dev/null; then
    echo "🔄 清理舊版 Qiskit 並安裝相容版本..."
    $PYTHON_CMD -m pip uninstall qiskit qiskit-terra qiskit-aer qiskit-ibmq-provider qiskit-algorithms -y 2>/dev/null || true
    $PYTHON_CMD -m pip install qiskit==1.2.4 qiskit-algorithms==0.3.1 $PIP_ARGS
fi

# 檢查並修復機器學習套件
echo "🤖 檢查機器學習套件..."
if ! $PYTHON_CMD -c "import xgboost, lightgbm" 2>/dev/null; then
    echo "🔄 安裝機器學習套件..."
    
    # 特殊處理 XGBoost（需要 OpenMP）
    echo "📦 安裝 XGBoost..."
    if [[ "$OS_TYPE" == "macos" ]]; then
        # macOS 需要特殊處理 OpenMP 路徑
        export LDFLAGS="-L/opt/homebrew/lib"
        export CPPFLAGS="-I/opt/homebrew/include"
    fi
    
    $PYTHON_CMD -m pip install xgboost $PIP_ARGS
    
    # 測試 XGBoost 是否正常運行
    if ! $PYTHON_CMD -c "import xgboost; print('XGBoost 測試成功')" 2>/dev/null; then
        echo "⚠️ XGBoost 安裝後仍有問題，可能需要手動安裝 OpenMP"
        case "$OS_TYPE" in
            "macos")
                echo "💡 macOS 解決方案：brew install libomp"
                ;;
            "linux")
                echo "💡 Linux 解決方案：sudo apt-get install libomp-dev (Ubuntu) 或 sudo yum install libomp-devel (CentOS)"
                ;;
            "windows")
                echo "💡 Windows 解決方案：安裝 Visual Studio Build Tools 或 Intel MKL"
                ;;
        esac
    fi
    
    # 安裝其他 ML 套件
    $PYTHON_CMD -m pip install "lightgbm>=4.4.0,<4.5.0" "dask>=2023.1.0" $PIP_ARGS
fi

# 系統驗證
echo ""
echo "🧪 系統驗證..."
verification_result=$($PYTHON_CMD -c "
try:
    import qiskit
    import xgboost
    import lightgbm
    import pandas
    import numpy
    import ccxt
    print('✅ 所有核心依賴正常')
    success = True
except ImportError as e:
    print(f'❌ 依賴問題: {e}')
    success = False

# 測試量子模組
try:
    import sys
    import os
    sys.path.append('quantum_pro')
    from btc_quantum_ultimate_model import BTCQuantumUltimateModel
    print('✅ 量子交易模型可用')
except Exception as e:
    print(f'⚠️ 量子模型問題: {e}')

print('success' if success else 'failed')
" 2>&1)

echo "$verification_result"

if [[ "$verification_result" == *"success"* ]]; then
    echo ""
    echo "🎉 環境配置完成！"
    echo "📝 使用說明："
    echo "   cd quantum_pro"
    echo "   python btc_quantum_ultimate_model.py --help"
    echo ""
    echo "💡 如果使用了虛擬環境，下次請先激活："
    echo "   source trading-x-env/bin/activate"
else
    echo ""
    echo "❌ 環境配置有問題，請檢查錯誤訊息"
    exit 1
fi
