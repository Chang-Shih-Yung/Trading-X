# Trading-X Windows Cleanup Script
# Clean up temporary files and unnecessary scripts from installation

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Trading-X Installation Cleanup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Set-Location "c:\Users\User\Desktop\Trading-X"

# Files to delete
$filesToDelete = @(
    "setup_windows_environment.ps1",
    "start_backend_venv.ps1", 
    "start_backend_with_venv.bat",
    "WINDOWS_SETUP_GUIDE.md"
)

Write-Host "[INFO] Cleaning up installation scripts..." -ForegroundColor Blue

foreach ($file in $filesToDelete) {
    if (Test-Path $file) {
        try {
            Remove-Item $file -Force
            Write-Host "[OK] Deleted: $file" -ForegroundColor Green
        } catch {
            Write-Host "[!] Could not delete: $file" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[!] File not found: $file" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "        Cleanup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "[INFO] Important scripts preserved:" -ForegroundColor Blue
Write-Host "  - start_windows.bat (recommended)" -ForegroundColor Yellow
Write-Host "  - start_all.ps1 (full startup script)" -ForegroundColor Yellow
Write-Host ""
Write-Host "[INFO] Important files preserved:" -ForegroundColor Blue
Write-Host "  - requirements.txt (dependencies)" -ForegroundColor Yellow
Write-Host "  - venv/ (virtual environment)" -ForegroundColor Yellow
Write-Host "  - main.py (main application)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next time use: .\start_windows.bat" -ForegroundColor Cyan

# Auto-delete this cleanup script
Write-Host ""
Write-Host "[INFO] Removing this cleanup script..." -ForegroundColor Blue
Start-Sleep -Seconds 2
Remove-Item $MyInvocation.MyCommand.Path -Force
Write-Host "[OK] Cleanup script auto-deleted" -ForegroundColor Green
