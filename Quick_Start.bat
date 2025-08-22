@echo off
title Multi-Purpose Business Application

echo.
echo ============================================================
echo    Multi-Purpose Business Application
echo ============================================================
echo.
echo Starting application...
echo.

REM Get the current directory
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

REM Change to the application directory
cd /d "%CURRENT_DIR%"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Check if virtual environment exists and activate it
if exist "venv" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo ✓ Virtual environment activated
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing requirements...
    python -m pip install -r requirements.txt --quiet
    echo ✓ Setup complete
)

echo.
echo 🌐 Starting web server...
echo 📱 The application will open in your browser automatically.
echo 🔄 Server is running at: http://127.0.0.1:8000
echo.
echo To stop the server, press Ctrl+C
echo.

REM Start the Django server
python manage.py runserver 127.0.0.1:8000

echo.
echo Application stopped.
pause
