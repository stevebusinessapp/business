#!/usr/bin/env python3
"""
Portable Executable Creator for Multi-Purpose Business Application
This script creates a self-contained executable that includes Python and all dependencies.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not"""
    try:
        import PyInstaller
        print("✓ PyInstaller is already installed")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✓ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install PyInstaller: {e}")
            return False

def create_portable_launcher():
    """Create a portable launcher script"""
    launcher_content = '''#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import webbrowser
import threading
from pathlib import Path
import signal
import atexit
import socket

def setup_environment():
    """Setup the environment for the portable application"""
    if getattr(sys, 'frozen', False):
        app_path = Path(sys._MEIPASS)
    else:
        app_path = Path(__file__).parent
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
    os.environ.setdefault('SECRET_KEY', 'django-insecure-portable-app-secret-key-2024')
    os.environ.setdefault('DEBUG', 'True')
    os.environ.setdefault('DEBUG_INVENTORY', 'True')
    
    sys.path.insert(0, str(app_path))
    return app_path

def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def open_browser():
    """Open the application in the default browser after a short delay"""
    time.sleep(3)
    try:
        webbrowser.open('http://127.0.0.1:8000')
        print("✓ Application opened in your default browser!")
    except Exception as e:
        print(f"Please manually open: http://127.0.0.1:8000")

def main():
    """Main function to launch the portable Django application"""
    print("=" * 60)
    print("🚀 Starting Multi-Purpose Business Application (Portable)")
    print("=" * 60)
    
    app_path = setup_environment()
    
    if is_port_in_use(8000):
        print("❌ Error: Port 8000 is already in use!")
        input("Press Enter to exit...")
        return
    
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    print("🌐 Starting web server...")
    print("📱 The application will open in your browser automatically.")
    print("🔄 Server is running at: http://127.0.0.1:8000")
    print("-" * 60)
    
    try:
        os.chdir(app_path)
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'business_app.settings'
        env['SECRET_KEY'] = 'django-insecure-portable-app-secret-key-2024'
        env['DEBUG'] = 'True'
        env['DEBUG_INVENTORY'] = 'True'
        
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', '127.0.0.1:8000'
        ], env=env)
    except KeyboardInterrupt:
        print("\\n🛑 Server stopped by user.")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()
'''
    
    with open('portable_launcher.py', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("✓ Created portable launcher script")

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['portable_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('business_app', 'business_app'),
        ('apps', 'apps'),
        ('templates', 'templates'),
        ('static', 'static'),
        ('manage.py', '.'),
        ('requirements.txt', '.'),
        ('db.sqlite3', '.'),
    ],
    hiddenimports=[
        'django',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.humanize',
        'rest_framework',
        'corsheaders',
        'crispy_forms',
        'crispy_bootstrap5',
        'django_filters',
        'widget_tweaks',
        'apps.accounts',
        'apps.core',
        'apps.invoices',
        'apps.receipts',
        'apps.waybills',
        'apps.job_orders',
        'apps.quotations',
        'apps.expenses',
        'apps.inventory',
        'apps.clients',
        'apps.accounting',
        'PIL',
        'reportlab',
        'xhtml2pdf',
        'openpyxl',
        'requests',
        'pandas',
        'whitenoise',
        'gunicorn',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Multi-Purpose_Business_App',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('portable_app.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ Created PyInstaller spec file")

def build_executable():
    """Build the portable executable"""
    print("🔨 Building portable executable...")
    print("This may take 5-10 minutes...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "portable_app.spec"
        ], check=True)
        
        print("✓ Portable executable built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build executable: {e}")
        return False

def create_portable_package():
    """Create the final portable package"""
    print("📦 Creating portable package...")
    
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    portable_dir = dist_dir / "Multi-Purpose_Business_App_Portable"
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir()
    
    exe_path = dist_dir / "Multi-Purpose_Business_App.exe"
    if exe_path.exists():
        shutil.copy2(exe_path, portable_dir / "Multi-Purpose_Business_App.exe")
    
    launcher_bat = '''@echo off
title Multi-Purpose Business Application

echo.
echo ============================================================
echo    Multi-Purpose Business Application (Portable)
echo ============================================================
echo.
echo Starting application...
echo This may take a moment on first run...
echo.

set "APP_DIR=%~dp0"
cd /d "%APP_DIR%"
start "" "Multi-Purpose_Business_App.exe"

echo.
echo Application is starting...
echo It will open in your browser automatically.
echo.
echo To stop the application, close the console window.
echo.
pause
'''
    
    with open(portable_dir / "Start_Application.bat", 'w', encoding='utf-8') as f:
        f.write(launcher_bat)
    
    readme_content = '''# Multi-Purpose Business Application (Portable)

## 🚀 Quick Start

1. **Double-click** `Start_Application.bat` to start the application
2. The application will open in your browser automatically
3. Register a new account and start using the application

## 📋 System Requirements

- Windows 7 or later
- At least 500MB free disk space
- No Python installation required!

## 🎯 Usage

1. Copy this entire folder to any Windows computer
2. Double-click `Start_Application.bat`
3. Wait for the application to start (first run may take longer)
4. The application will open in your default browser
5. Register and start using immediately

## 🔒 Security

- **Local Only**: Application runs on your computer only
- **No External Servers**: Your data stays on your computer
- **No Internet Required**: Works completely offline after first run

## 🆘 Troubleshooting

### If the application doesn't start:
1. Make sure you have at least 500MB free disk space
2. Try running as Administrator
3. Check if antivirus is blocking the application

### If browser doesn't open automatically:
1. Manually open: http://127.0.0.1:8000

## 🎉 Success!

Once everything is working:
- The application will open in your browser
- You can register a new account
- Start managing your business immediately
- All data is saved locally on your computer
- No internet required for daily use

---

**Happy Business Management! 🚀**
'''
    
    with open(portable_dir / "README.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✓ Portable package created successfully!")
    print(f"📁 Location: {portable_dir}")
    
    return portable_dir

def main():
    """Main function to create the portable application"""
    print("=" * 70)
    print("🚀 Creating Portable Multi-Purpose Business Application")
    print("=" * 70)
    print()
    
    if not check_pyinstaller():
        print("❌ Cannot proceed without PyInstaller")
        return
    
    create_portable_launcher()
    create_spec_file()
    
    if not build_executable():
        print("❌ Failed to build executable")
        return
    
    portable_dir = create_portable_package()
    
    print()
    print("=" * 70)
    print("🎉 PORTABLE APPLICATION CREATED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print(f"📁 Portable package location: {portable_dir}")
    print()
    print("📋 Next Steps:")
    print("1. Copy the entire 'Multi-Purpose_Business_App_Portable' folder")
    print("2. Paste it on any Windows computer")
    print("3. Double-click 'Start_Application.bat' to run")
    print("4. No Python installation required!")
    print()
    print("🔒 The application is now truly portable and will work on any")
    print("   Windows computer without requiring Python or any dependencies.")
    print()

if __name__ == '__main__':
    main()
