#!/usr/bin/env python
"""
Script to merge migrations with automatic yes responses
"""
import subprocess
import sys
import os

def run_merge_migrations():
    """Run makemigrations --merge with automatic yes responses"""
    # Set environment to handle prompts
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'business_app.settings'
    
    # Run the merge command
    process = subprocess.Popen(
        ['venv\\Scripts\\python.exe', 'manage.py', 'makemigrations', '--merge'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    # Send 'y' responses to all prompts
    stdout, stderr = process.communicate(input='y\ny\ny\ny\n')
    
    print("STDOUT:")
    print(stdout)
    if stderr:
        print("\nSTDERR:")
        print(stderr)
    
    return process.returncode

if __name__ == "__main__":
    exit_code = run_merge_migrations()
    sys.exit(exit_code)
