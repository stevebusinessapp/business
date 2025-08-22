#!/usr/bin/env python3
"""
Improved Django Application Launcher
This script launches the Django application and opens it in the default browser.
"""

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

# Add the current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Set environment variables for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
os.environ.setdefault('SECRET_KEY', 'django-insecure-portable-app-secret-key-2024')
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('DEBUG_INVENTORY', 'True')

def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def wait_for_server(port, timeout=60):
    """Wait for the server to be ready"""
    print(f"Waiting for server to start on port {port}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                if s.connect_ex(('localhost', port)) == 0:
                    print("✓ Server is ready!")
                    return True
        except:
            pass
        time.sleep(1)
    
    return False

def open_browser():
    """Open the application in the default browser after server is ready"""
    if wait_for_server(8000):
        try:
            webbrowser.open('http://127.0.0.1:8000')
            print("✓ Application opened in your default browser!")
            print("✓ You can now register and start using the application.")
            print("✓ To stop the server, press Ctrl+C")
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print("Please manually open: http://127.0.0.1:8000")
    else:
        print("❌ Server did not start within the expected time.")
        print("Please check the console for error messages.")

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = ['django', 'rest_framework', 'corsheaders']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("Please run the setup script first.")
        return False
    
    return True

def main():
    """Main function to launch the Django application"""
    print("=" * 60)
    print("🚀 Starting Multi-Purpose Business Application")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path('business_app').exists():
        print("❌ Error: business_app directory not found!")
        print("Please make sure this script is in the project root directory.")
        input("Press Enter to exit...")
        return
    
    # Check if port 8000 is already in use
    if is_port_in_use(8000):
        print("❌ Error: Port 8000 is already in use!")
        print("Please close other applications using port 8000 or restart your computer.")
        input("Press Enter to exit...")
        return
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        return
    
    # Check if database exists, if not run migrations
    db_path = Path('db.sqlite3')
    if not db_path.exists():
        print("📊 Setting up database...")
        try:
            result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                                  check=True, capture_output=True, text=True)
            print("✓ Database setup complete!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Database setup failed: {e}")
            print(f"Error output: {e.stderr}")
            input("Press Enter to exit...")
            return
    
    # Start browser opening in a separate thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    print("🌐 Starting web server...")
    print("📱 The application will open in your browser automatically.")
    print("🔄 Server is running at: http://127.0.0.1:8000")
    print("-" * 60)
    
    try:
        # Start Django development server
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', '127.0.0.1:8000'
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user.")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()
