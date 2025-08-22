@echo off
title Django App Railway Deployment Helper
color 0A

echo ========================================
echo    Django Railway Deployment Helper
echo ========================================
echo.

echo Step 1: Checking Git repository status...
git status
echo.

echo Step 2: Checking if remote repository is connected...
git remote -v
echo.

echo Step 3: Current branch...
git branch
echo.

echo ========================================
echo    NEXT STEPS TO COMPLETE:
echo ========================================
echo.
echo 1. CREATE GITHUB REPOSITORY:
echo    - Open GitHub Desktop (run open_github_desktop.bat)
echo    - OR go to https://github.com and create a new repository
echo    - Repository name: multi-purpose-business-app
echo.
echo 2. PUSH TO GITHUB:
echo    - If using GitHub Desktop: Publish repository
echo    - If using command line: 
echo      git remote add origin https://github.com/YOUR_USERNAME/multi-purpose-business-app.git
echo      git push -u origin main
echo.
echo 3. DEPLOY TO RAILWAY:
echo    - Go to https://railway.app
echo    - Sign in with GitHub
echo    - Create new project from GitHub repo
echo    - Select your multi-purpose-business-app repository
echo.
echo 4. SET ENVIRONMENT VARIABLES IN RAILWAY:
echo    - SECRET_KEY: (generate a secure key)
echo    - DEBUG: False
echo.
echo 5. RUN MIGRATIONS:
echo    - In Railway dashboard, open terminal
echo    - Run: python manage.py migrate
echo    - Run: python manage.py createsuperuser
echo.
echo ========================================
echo    HELPFUL FILES:
echo ========================================
echo - GITHUB_SETUP_GUIDE.md (detailed instructions)
echo - README.md (project documentation)
echo - open_github_desktop.bat (opens GitHub Desktop)
echo.
echo ========================================
echo    QUICK COMMANDS:
echo ========================================
echo To open GitHub Desktop: open_github_desktop.bat
echo To view setup guide: notepad GITHUB_SETUP_GUIDE.md
echo To view README: notepad README.md
echo.
echo Press any key to open GitHub Desktop...
pause > nul

call open_github_desktop.bat
