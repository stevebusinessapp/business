#!/usr/bin/env python3
"""
Deployment verification script for Render
Checks if all required packages are installed and working
"""

import sys
import os

def check_package(package_name, import_name=None):
    """Check if a package is installed and can be imported"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name} - FAILED: {e}")
        return False

def main():
    print("🔍 Checking deployment dependencies...")
    print("=" * 50)
    
    # Core Django packages
    core_packages = [
        ("Django", "django"),
        ("Django REST Framework", "rest_framework"),
        ("Pillow", "PIL"),
        ("psycopg2-binary", "psycopg2"),
        ("python-decouple", "decouple"),
        ("openpyxl", "openpyxl"),
        ("django-crispy-forms", "crispy_forms"),
        ("crispy-bootstrap5", "crispy_bootstrap5"),
        ("requests", "requests"),
        ("django-filter", "django_filters"),
        ("django-extensions", "django_extensions"),
        ("django-widget-tweaks", "widget_tweaks"),
        ("whitenoise", "whitenoise"),
        ("gunicorn", "gunicorn"),
        ("dj-database-url", "dj_database_url"),
    ]
    
    # PDF generation packages
    pdf_packages = [
        ("reportlab", "reportlab"),
        ("xhtml2pdf", "xhtml2pdf"),
    ]
    
    print("📦 Core Packages:")
    core_success = all(check_package(name, import_name) for name, import_name in core_packages)
    
    print("\n📄 PDF Packages:")
    pdf_success = all(check_package(name, import_name) for name, import_name in pdf_packages)
    
    print("\n" + "=" * 50)
    
    if core_success and pdf_success:
        print("🎉 All packages are installed and working!")
        print("✅ Your deployment should work correctly.")
        return 0
    else:
        print("⚠️  Some packages are missing or not working.")
        print("❌ Please check your requirements.txt and deployment configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
