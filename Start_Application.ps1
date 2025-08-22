# Multi-Purpose Business Application Launcher (PowerShell)
# This script provides a more robust way to launch the application

param(
    [switch]$Silent
)

# Set console title and colors
$Host.UI.RawUI.WindowTitle = "Multi-Purpose Business Application"
$Host.UI.RawUI.ForegroundColor = "Green"

function Write-Header {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "    Multi-Purpose Business Application Launcher" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Test-Python {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
            return $true
        }
    }
    catch {
        # Python not found
    }
    
    Write-Host "❌ Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.8 or higher from:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    Write-Host ""
    
    if (-not $Silent) {
        Read-Host "Press Enter to exit"
    }
    return $false
}

function Setup-VirtualEnvironment {
    if (-not (Test-Path "venv")) {
        Write-Host "Creating virtual environment..." -ForegroundColor Yellow
        python -m venv venv
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to create virtual environment!" -ForegroundColor Red
            if (-not $Silent) { Read-Host "Press Enter to exit" }
            return $false
        }
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
    }
    return $true
}

function Install-Requirements {
    $djangoPath = "venv\Lib\site-packages\django"
    if (-not (Test-Path $djangoPath)) {
        Write-Host "Installing required packages..." -ForegroundColor Yellow
        & "venv\Scripts\python.exe" -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to install requirements!" -ForegroundColor Red
            if (-not $Silent) { Read-Host "Press Enter to exit" }
            return $false
        }
        Write-Host "✓ Requirements installed" -ForegroundColor Green
    } else {
        Write-Host "✓ Requirements already installed" -ForegroundColor Green
    }
    return $true
}

function Start-Application {
    Write-Host "Starting application..." -ForegroundColor Yellow
    & "venv\Scripts\python.exe" launch_app.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "Application stopped with an error." -ForegroundColor Red
        if (-not $Silent) { Read-Host "Press Enter to exit" }
    }
}

# Main execution
Write-Header

if (-not (Test-Python)) { exit 1 }
if (-not (Setup-VirtualEnvironment)) { exit 1 }
if (-not (Install-Requirements)) { exit 1 }

Start-Application
