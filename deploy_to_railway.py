#!/usr/bin/env python3
"""
Railway Deployment Helper Script
This script helps prepare and verify your Django project for Railway deployment.
"""

import os
import sys
import subprocess
import secrets
import string
from pathlib import Path

def generate_secret_key(length=50):
    """Generate a secure secret key for Django"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def check_railway_files():
    """Check if all required Railway files exist"""
    required_files = ['Procfile', 'requirements.txt', 'runtime.txt']
    missing_files = []
    
    print("🔍 Checking Railway deployment files...")
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} - Found")
        else:
            print(f"❌ {file} - Missing")
            missing_files.append(file)
    
    return missing_files

def check_django_config():
    """Check Django configuration for production readiness"""
    print("\n🔍 Checking Django configuration...")
    
    # Check if settings.py exists
    settings_file = Path('business_app/settings.py')
    if not settings_file.exists():
        print("❌ business_app/settings.py not found")
        return False
    
    # Read settings file
    with open(settings_file, 'r') as f:
        settings_content = f.read()
    
    # Check for important configurations
    checks = [
        ('DATABASE_URL', 'Database URL configuration'),
        ('whitenoise', 'WhiteNoise middleware'),
        ('ALLOWED_HOSTS', 'Allowed hosts configuration'),
        ('STATIC_ROOT', 'Static files configuration'),
    ]
    
    all_good = True
    for check, description in checks:
        if check in settings_content:
            print(f"✅ {description} - Found")
        else:
            print(f"❌ {description} - Missing")
            all_good = False
    
    return all_good

def generate_env_template():
    """Generate a .env template for Railway"""
    print("\n📝 Generating Railway environment variables template...")
    
    env_template = f"""# Railway Deployment Environment Variables
# Copy these to your Railway project variables

# Django Settings
SECRET_KEY={generate_secret_key()}
DEBUG=False
DEBUG_INVENTORY=False

# Database (Railway will set this automatically)
# DATABASE_URL=postgresql://...

# Email Settings (Optional)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password

# Custom Domain (Optional)
# RAILWAY_STATIC_URL=https://your-domain.com
"""
    
    with open('railway_env_template.txt', 'w') as f:
        f.write(env_template)
    
    print("✅ Created railway_env_template.txt")
    print("📋 Copy the variables from this file to your Railway project settings")

def check_dependencies():
    """Check if all dependencies are properly listed"""
    print("\n🔍 Checking dependencies...")
    
    if not Path('requirements.txt').exists():
        print("❌ requirements.txt not found")
        return False
    
    # Check for essential dependencies
    essential_deps = [
        'Django',
        'gunicorn',
        'whitenoise',
        'psycopg2-binary',
        'dj-database-url',
    ]
    
    with open('requirements.txt', 'r') as f:
        requirements = f.read()
    
    missing_deps = []
    for dep in essential_deps:
        if dep.lower() in requirements.lower():
            print(f"✅ {dep} - Found")
        else:
            print(f"❌ {dep} - Missing")
            missing_deps.append(dep)
    
    return len(missing_deps) == 0

def create_deployment_checklist():
    """Create a deployment checklist"""
    print("\n📋 Creating deployment checklist...")
    
    checklist = """# Railway Deployment Checklist

## Pre-Deployment
- [ ] All Railway files are present (Procfile, requirements.txt, runtime.txt)
- [ ] Django settings are configured for production
- [ ] All dependencies are listed in requirements.txt
- [ ] Database migrations are ready
- [ ] Static files are configured with WhiteNoise

## Railway Setup
- [ ] Create Railway account at https://railway.app
- [ ] Connect GitHub repository
- [ ] Create new project from GitHub repo
- [ ] Add PostgreSQL database service
- [ ] Set environment variables:
  - [ ] SECRET_KEY
  - [ ] DEBUG=False
  - [ ] DEBUG_INVENTORY=False
  - [ ] DATABASE_URL (auto-set by Railway)

## Post-Deployment
- [ ] Run database migrations
- [ ] Create superuser account
- [ ] Test application functionality
- [ ] Configure custom domain (optional)
- [ ] Set up email settings (optional)
- [ ] Test all business features

## Verification
- [ ] Application loads correctly
- [ ] User registration works
- [ ] Login/logout works
- [ ] All business modules work
- [ ] Static files load properly
- [ ] Database operations work

## Monitoring
- [ ] Check Railway logs for errors
- [ ] Monitor application performance
- [ ] Set up error tracking (optional)
- [ ] Configure backups

Your app will be available at: https://your-app-name.railway.app
"""
    
    with open('railway_deployment_checklist.md', 'w') as f:
        f.write(checklist)
    
    print("✅ Created railway_deployment_checklist.md")

def main():
    """Main function"""
    print("🚀 Railway Deployment Helper")
    print("=" * 50)
    
    # Check current directory
    if not Path('business_app').exists():
        print("❌ Error: Please run this script from your project root directory")
        print("   (where business_app/ folder is located)")
        return
    
    # Run all checks
    missing_files = check_railway_files()
    django_ok = check_django_config()
    deps_ok = check_dependencies()
    
    # Generate helpful files
    generate_env_template()
    create_deployment_checklist()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT READINESS SUMMARY")
    print("=" * 50)
    
    if not missing_files and django_ok and deps_ok:
        print("🎉 Your project is ready for Railway deployment!")
        print("\n📋 Next steps:")
        print("1. Go to https://railway.app")
        print("2. Sign in with your GitHub account")
        print("3. Create new project from GitHub repo")
        print("4. Follow the checklist in railway_deployment_checklist.md")
        print("5. Use the environment variables from railway_env_template.txt")
    else:
        print("⚠️  Some issues need to be fixed before deployment:")
        if missing_files:
            print(f"   - Missing files: {', '.join(missing_files)}")
        if not django_ok:
            print("   - Django configuration needs updates")
        if not deps_ok:
            print("   - Dependencies need to be added to requirements.txt")
    
    print("\n📚 For detailed instructions, see RAILWAY_DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    main()
