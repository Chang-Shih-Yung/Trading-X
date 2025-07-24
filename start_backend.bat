@echo off
chcp 65001 >nul
title Trading X - 後端服務

echo ============================================
echo          Trading X 後端服務啟動器
echo ============================================
echo.

echo [INFO] 正在啟動後端服務...
echo [INFO] API 地址: http://localhost:8000
echo [INFO] API 文檔: http://localhost:8000/docs
echo.

cd /d "%~dp0"

echo [INFO] 檢查 Python 環境...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python 未安裝或未添加到 PATH
    echo [HELP] 請安裝 Python 3.9+ 並添加到環境變數
    pause
    exit /b 1
)

echo [INFO] 檢查依賴安裝...
python -c "import fastapi" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] 依賴未安裝，正在安裝...
    pip install -r requirements.txt
)

echo [INFO] 啟動服務中...
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

echo.
echo [INFO] 服務已停止
pause
