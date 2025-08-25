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
    
    modules=("pandas" "numpy" "aiosqlite" "fastapi" "talib" "pandas_ta")
    for module in "${modules[@]}"; do
        if python -c "import $module" 2>/dev/null; then
            echo "  ✅ $module 可正常導入"
        else
            echo "  ❌ $module 導入失敗"
        fi
    done
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

echo ""
echo "💡 如果有任何 ❌ 項目，請執行："
echo "   ./setup-dev-environment.sh"
