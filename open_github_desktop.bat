@echo off
echo Opening GitHub Desktop...
echo.
echo If GitHub Desktop doesn't open, please:
echo 1. Open GitHub Desktop manually from the Start menu
echo 2. Follow the instructions in GITHUB_SETUP_GUIDE.md
echo.
echo Press any key to continue...
pause > nul

REM Try to open GitHub Desktop
start "" "C:\Users\%USERNAME%\AppData\Local\GitHubDesktop\GitHubDesktop.exe" 2>nul
if errorlevel 1 (
    start "" "C:\Program Files\GitHub Desktop\GitHubDesktop.exe" 2>nul
    if errorlevel 1 (
        start "" "C:\Program Files (x86)\GitHub Desktop\GitHubDesktop.exe" 2>nul
        if errorlevel 1 (
            echo GitHub Desktop not found in common locations.
            echo Please open it manually from the Start menu.
        )
    )
)
