#!/usr/bin/env python3
"""
Setup Verification Script
This script verifies that all components are properly installed and configured.
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python version {version.major}.{version.minor} is too old!")
        print("   Please install Python 3.8 or higher.")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_django_installation():
    """Check if Django is properly installed"""
    try:
        import django
        print(f"✓ Django {django.get_version()} is installed")
        return True
    except ImportError:
        print("❌ Django is not installed!")
        return False

def check_required_packages():
    """Check if all required packages are installed"""
    required_packages = [
        'djangorestframework',
        'corsheaders',
        'crispy_forms',
        'crispy_bootstrap5',
        'django_filters',
        'widget_tweaks',
        'Pillow',
        'python-decouple',
        'reportlab',
        'xhtml2pdf',
        'openpyxl',
        'requests',
        'django_extensions',
        'whitenoise',
        'pandas'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_database():
    """Check if database exists and is accessible"""
    db_path = Path('db.sqlite3')
    if db_path.exists():
        print("✓ Database file exists")
        return True
    else:
        print("⚠ Database file does not exist (will be created on first run)")
        return True

def check_static_files():
    """Check if static files are present"""
    static_dir = Path('static')
    if static_dir.exists():
        print("✓ Static files directory exists")
        return True
    else:
        print("❌ Static files directory is missing")
        return False

def check_templates():
    """Check if templates are present"""
    templates_dir = Path('templates')
    if templates_dir.exists():
        print("✓ Templates directory exists")
        return True
    else:
        print("❌ Templates directory is missing")
        return False

def run_django_check():
    """Run Django's system check"""
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'check'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✓ Django system check passed")
            return True
        else:
            print(f"❌ Django system check failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Django system check timed out")
        return False
    except Exception as e:
        print(f"❌ Django system check error: {e}")
        return False

def main():
    """Main verification function"""
    print("=" * 60)
    print("🔍 Multi-Purpose Business Application - Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Django Installation", check_django_installation),
        ("Required Packages", check_required_packages),
        ("Database", check_database),
        ("Static Files", check_static_files),
        ("Templates", check_templates),
        ("Django System Check", run_django_check),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"Checking {check_name}...")
        if check_func():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Verification Results: {passed}/{total} checks passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All checks passed! Your setup is ready to use.")
        print("You can now run the application using:")
        print("  - Start_Application_Silent.vbs (recommended)")
        print("  - Start_Application.bat")
        print("  - launch_app.py")
    else:
        print("⚠ Some checks failed. Please review the issues above.")
        print("You may need to:")
        print("  1. Install missing packages: pip install -r requirements.txt")
        print("  2. Run database migrations: python manage.py migrate")
        print("  3. Check file permissions and paths")
    
    print()
    input("Press Enter to continue...")

if __name__ == '__main__':
    main()
