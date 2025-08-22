# Django Project Runner for PowerShell
Write-Host "Starting Django Multi-Purpose Business App..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Use virtual environment Python directly
Write-Host "Using virtual environment Python..." -ForegroundColor Cyan
& "venv\Scripts\python.exe" manage.py runserver

Read-Host "Press Enter to exit"
