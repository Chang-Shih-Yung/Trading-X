# PowerShell Script to setup and run Trading-X backend with venv

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "    Trading-X Backend Setup (venv)" -ForegroundColor Cyan  
Write-Host "=======================================" -ForegroundColor Cyan

Set-Location "c:\Users\User\Desktop\Trading-X"

# 檢查是否已有虛擬環境
if (Test-Path "venv") {
    Write-Host "[INFO] Virtual environment already exists" -ForegroundColor Green
} else {
    Write-Host "[INFO] Creating virtual environment..." -ForegroundColor Blue
    
    # 嘗試不同的 Python 命令
    $pythonCommands = @("python", "python3", "py", "python.exe")
    $venvCreated = $false
    
    foreach ($cmd in $pythonCommands) {
        try {
            Write-Host "[INFO] Trying: $cmd -m venv venv" -ForegroundColor Yellow
            & $cmd -m venv venv 2>$null
            if (Test-Path "venv") {
                Write-Host "[✓] Virtual environment created with $cmd" -ForegroundColor Green
                $venvCreated = $true
                break
            }
        } catch {
            Write-Host "[!] $cmd failed" -ForegroundColor Red
        }
    }
    
    if (-not $venvCreated) {
        Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
        Write-Host "[INFO] Trying to install dependencies directly..." -ForegroundColor Yellow
        
        # 嘗試直接安裝 uvicorn
        try {
            python -m pip install uvicorn fastapi
            Write-Host "[✓] Dependencies installed globally" -ForegroundColor Green
        } catch {
            Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
            exit 1
        }
    }
}

# 激活虛擬環境（如果存在）
if (Test-Path "venv") {
    Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Blue
    & ".\venv\Scripts\Activate.ps1"
    
    # 檢查是否需要安裝依賴
    try {
        uvicorn --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[✓] Dependencies already installed" -ForegroundColor Green
        } else {
            throw "uvicorn not found"
        }
    } catch {
        Write-Host "[INFO] Installing dependencies..." -ForegroundColor Blue
        pip install -r requirements.txt
    }
} else {
    Write-Host "[INFO] Using global Python environment" -ForegroundColor Yellow
}

# 啟動後端服務
Write-Host "[INFO] Starting backend server..." -ForegroundColor Blue
Write-Host "[INFO] Backend will be available at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "[INFO] API docs will be available at: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
