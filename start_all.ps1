# Trading X 一鍵啟動腳本
# PowerShell 版本

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "          Trading X 一鍵啟動器" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot

Write-Host "[INFO] 正在啟動 Trading X 服務..." -ForegroundColor Green
Write-Host "[INFO] 後端服務: http://localhost:8000" -ForegroundColor Yellow
Write-Host "[INFO] 前端服務: http://localhost:3000" -ForegroundColor Yellow
Write-Host "[INFO] API 文檔: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""

# 檢查環境
Write-Host "[INFO] 檢查環境依賴..." -ForegroundColor Blue

try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] Python 未安裝" -ForegroundColor Red
    exit 1
}

try {
    $nodeVersion = node --version 2>&1
    Write-Host "[✓] Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] Node.js 未安裝" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 啟動後端服務
Write-Host "[INFO] 啟動後端服務..." -ForegroundColor Blue
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:projectRoot
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
}

# 等待後端啟動
Start-Sleep -Seconds 3

# 啟動前端服務
Write-Host "[INFO] 啟動前端服務..." -ForegroundColor Blue
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "$using:projectRoot\frontend"
    npm run dev
}

# 等待服務啟動
Write-Host "[INFO] 等待服務啟動..." -ForegroundColor Blue
Start-Sleep -Seconds 5

# 檢查服務狀態
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 5
    Write-Host "[✓] 後端服務啟動成功" -ForegroundColor Green
} catch {
    Write-Host "[!] 後端服務可能需要更多時間啟動" -ForegroundColor Yellow
}

# 打開瀏覽器
Write-Host "[INFO] 正在打開瀏覽器..." -ForegroundColor Blue
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "              服務運行中" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "前端: http://localhost:3000" -ForegroundColor Yellow
Write-Host "後端: http://localhost:8000" -ForegroundColor Yellow
Write-Host "文檔: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "按 Ctrl+C 停止服務..." -ForegroundColor Red

# 等待用戶中斷
try {
    while ($true) {
        Start-Sleep -Seconds 1
        if ($backendJob.State -eq "Failed" -or $frontendJob.State -eq "Failed") {
            throw "服務運行失敗"
        }
    }
} catch {
    Write-Host ""
    Write-Host "[INFO] 正在停止服務..." -ForegroundColor Blue
    
    # 停止任務
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $frontendJob -ErrorAction SilentlyContinue
    
    Write-Host "[INFO] 服務已停止" -ForegroundColor Green
}
