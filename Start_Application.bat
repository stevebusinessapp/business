@echo off
title Multi-Purpose Business Application
color 0A

echo.
echo ============================================================
echo    Multi-Purpose Business Application Launcher
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements if not already installed
if not exist "venv\Lib\site-packages\django" (
    echo Installing required packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install requirements!
        pause
        exit /b 1
    )
)

REM Run the launcher script
echo Starting application...
python launch_app.py

REM Keep window open if there was an error
if %errorlevel% neq 0 (
    echo.
    echo Application stopped with an error.
    pause
)
