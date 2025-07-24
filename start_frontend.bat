@echo off
chcp 65001 >nul
title Trading X - 前端服務

echo ============================================
echo          Trading X 前端服務啟動器
echo ============================================
echo.

echo [INFO] 正在啟動前端服務...
echo [INFO] 前端地址: http://localhost:3000
echo.

cd /d "%~dp0\frontend"

echo [INFO] 檢查 Node.js 環境...
node --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js 未安裝或未添加到 PATH
    echo [HELP] 請安裝 Node.js 16+ 
    pause
    exit /b 1
)

echo [INFO] 檢查依賴安裝...
if not exist "node_modules" (
    echo [WARN] 依賴未安裝，正在安裝...
    npm install
)

echo [INFO] 啟動開發服務器...
npm run dev

echo.
echo [INFO] 服務已停止
pause
