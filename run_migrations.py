#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
django.setup()

from django.core.management import execute_from_command_line

def run_migrations():
    """Run migrations with automatic answers"""
    print("Running makemigrations...")
    try:
        # Create a fake stdin that answers 'y' to all prompts
        import io
        import sys
        
        # Backup original stdin
        original_stdin = sys.stdin
        
        # Create a fake stdin that returns 'y' for all inputs
        class FakeStdin:
            def readline(self):
                return 'y\n'
        
        sys.stdin = FakeStdin()
        
        # Run makemigrations
        execute_from_command_line(['manage.py', 'makemigrations', 'inventory'])
        
        # Restore original stdin
        sys.stdin = original_stdin
        
        print("Running migrate...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("Migrations completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations() 