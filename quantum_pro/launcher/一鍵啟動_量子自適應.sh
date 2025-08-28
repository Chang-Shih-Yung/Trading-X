#!/bin/bash
# -*- coding: utf-8 -*-
"""
🔮 Trading X 量子自適應交易系統一鍵啟動 v2.0
═══════════════════════════════════════════════

🚀 跨設備智能啟動：
- ✅ 自動檢測虛擬環境
- ✅ 智能安裝量子依賴
- ✅ 跨平台 Python 命令兼容
- ✅ 環境問題自動修復

突破性改進：
- ❌ 告別固定30秒週期
- ✅ 擁抱量子狀態驅動
- ⚡ 純物理定律觸發信號
- 🌌 自適應間隔調整
"""

echo "🔮 Trading X 量子自適應交易系統啟動 v2.0"
echo "=" * 80
echo "🚀 跨設備智能啟動：自動環境檢測與修復"
echo "⚡ 突破性升級：量子狀態驅動，告別固定週期！"
echo "🌌 純物理定律觸發，零人為限制"
echo "=" * 80

# 🔧 函式：智能檢測 Python 命令
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
    elif command -v python3.12 &> /dev/null; then
        python_cmd="python3.12"
    else
        echo "❌ 未找到 Python 3 安裝"
        echo "💡 請安裝 Python 3.9+ : https://www.python.org/downloads/"
        exit 1
    fi
    
    echo "$python_cmd"
}

# 🔧 函式：檢測虛擬環境
check_virtual_environment() {
    local python_cmd="$1"
    
    # 檢查是否在虛擬環境中
    if $python_cmd -c "import sys; exit(0 if (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)) else 1)" 2>/dev/null; then
        return 0  # 在虛擬環境中
    else
        return 1  # 不在虛擬環境中
    fi
}

# 🔧 函式：自動創建並啟動虛擬環境
setup_virtual_environment() {
    local python_cmd="$1"
    local project_root="$2"
    
    echo "🔨 設置虛擬環境..."
    
    # 進入專案根目錄
    cd "$project_root"
    
    # 創建虛擬環境（如果不存在）
    if [ ! -d "venv" ]; then
        echo "🆕 創建新的虛擬環境..."
        $python_cmd -m venv venv
        if [ $? -ne 0 ]; then
            echo "❌ 虛擬環境創建失敗"
            echo "💡 請確保已安裝 python3-venv: sudo apt install python3-venv (Ubuntu) 或 brew install python (macOS)"
            exit 1
        fi
    else
        echo "✅ 虛擬環境已存在"
    fi
    
    # 啟動虛擬環境
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "✅ 虛擬環境已啟動: $(which python)"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate  # Windows
        echo "✅ 虛擬環境已啟動: $(which python)"
    else
        echo "❌ 無法找到虛擬環境啟動腳本"
        exit 1
    fi
}

# 進入量子系統目錄
cd "$(dirname "$0")"
cd ../

# 獲取專案根目錄
PROJECT_ROOT="$(pwd)/.."

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

# 🔍 檢查虛擬環境狀態
echo "🔍 檢查虛擬環境狀態..."
if check_virtual_environment "$PYTHON_CMD"; then
    echo "✅ 已在虛擬環境中運行"
    VENV_PYTHON="python"  # 在虛擬環境中，使用 python 即可
else
    echo "⚠️ 未檢測到虛擬環境，建立並啟動虛擬環境..."
    setup_virtual_environment "$PYTHON_CMD" "$PROJECT_ROOT"
    VENV_PYTHON="python"  # 啟動虛擬環境後使用 python
fi

# 🔮 執行量子環境檢測器
echo "🔮 執行量子環境完整檢測..."
$VENV_PYTHON check_quantum_environment.py

if [ $? -ne 0 ]; then
    echo "❌ 量子環境檢測發現問題"
    read -p "是否嘗試自動修復環境？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔧 執行自動環境修復..."
        $VENV_PYTHON -c "
from check_quantum_environment import QuantumEnvironmentChecker
checker = QuantumEnvironmentChecker()
checker.auto_fix_environment()
"
        echo "🔄 重新檢測環境..."
        $VENV_PYTHON check_quantum_environment.py
        if [ $? -ne 0 ]; then
            echo "❌ 自動修復失敗，請手動解決環境問題"
            exit 1
        fi
    else
        echo "❌ 環境問題未解決，無法啟動量子系統"
        exit 1
    fi
fi

echo ""
echo "🔍 檢查量子模型狀態..."

# 檢查模型目錄
MODEL_DIR="data/models"
if [ ! -d "$MODEL_DIR" ]; then
    echo "📁 創建模型目錄..."
    mkdir -p "$MODEL_DIR"
fi

# 檢查已訓練的模型數量
TRAINED_MODELS=$(find "$MODEL_DIR" -name "quantum_model_*.pkl" 2>/dev/null | wc -l)

echo "📊 已訓練模型數量: $TRAINED_MODELS/7"

if [ "$TRAINED_MODELS" -eq 0 ]; then
    echo ""
    echo "🎯 發現未訓練的量子模型，開始自動訓練..."
    echo "⏱️ 預計耗時: 20-40分鐘 (7個幣種)"
    echo ""
    
    # 自動訓練所有模型
    cd launcher
    $VENV_PYTHON quantum_model_trainer.py << EOF
2
EOF
    
    if [ $? -eq 0 ]; then
        echo "✅ 量子模型訓練完成！"
    else
        echo "❌ 量子模型訓練失敗，請檢查錯誤訊息"
        exit 1
    fi
    
    cd ..
elif [ "$TRAINED_MODELS" -lt 7 ]; then
    echo "⚠️ 檢測到部分模型缺失 ($TRAINED_MODELS/7)"
    echo "🔄 建議重新訓練所有模型以確保一致性"
    
    read -p "是否重新訓練所有模型？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd launcher
        $VENV_PYTHON quantum_model_trainer.py << EOF
2
EOF
        cd ..
    fi
else
    echo "✅ 所有量子模型已就緒！"
fi

echo ""
echo "🚀 啟動量子自適應交易引擎..."
echo "🌌 系統特色："
echo "   ⚡ 量子狀態觸發 (非固定週期)"
echo "   🔮 疊加態坍縮檢測"
echo "   🌀 量子糾纏監控"
echo "   ⚛️  海森堡不確定性管理"
echo "   🕐 自適應間隔調整 (0.1-3600秒)"
echo "   💻 跨設備環境兼容"
echo ""

# 啟動量子自適應引擎
cd launcher
exec $VENV_PYTHON quantum_adaptive_trading_launcher.py
