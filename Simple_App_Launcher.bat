@echo off
title Multi-Purpose Business Application Launcher

echo.
echo ============================================================
echo    Multi-Purpose Business Application
echo ============================================================
echo.
echo Starting application...
echo Please wait while the application loads...
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
    echo Make sure to check 'Add Python to PATH' during installation.
    echo.
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment exists
)

REM Activate virtual environment and install requirements
echo Installing/checking requirements...
call venv\Scripts\activate.bat
python -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ❌ Failed to install requirements!
    pause
    exit /b 1
)
echo ✓ Requirements installed

REM Run database migrations if needed
echo Checking database...
python manage.py migrate --run-syncdb --noinput
if %errorlevel% neq 0 (
    echo ❌ Database setup failed!
    pause
    exit /b 1
)
echo ✓ Database ready

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
