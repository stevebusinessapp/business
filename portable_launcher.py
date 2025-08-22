#!/usr/bin/env python3
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
        print("\n🛑 Server stopped by user.")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()
