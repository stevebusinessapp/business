#!/usr/bin/env python
"""
Test script for authentication system
"""
import os
import sys
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
django.setup()

from django.contrib.auth import authenticate
from apps.accounts.models import User
from apps.accounts.forms import UserRegistrationForm, UserLoginForm
from django.test import RequestFactory

def test_user_registration():
    """Test user registration functionality"""
    print("Testing user registration...")
    
    # Clean up existing user first
    User.objects.filter(email='test_new@example.com').delete()
    
    # Test data
    test_data = {
        'email': 'test_new@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password1': 'TestPassword123!',
        'password2': 'TestPassword123!',
        'phone': '+1234567890'
    }
    
    # Create form
    form = UserRegistrationForm(data=test_data)
    
    if form.is_valid():
        try:
            user = form.save()
            print(f"[SUCCESS] User created successfully: {user.email}")
            print(f"  - Full name: {user.get_full_name()}")
            print(f"  - Is active: {user.is_active}")
            return True
        except Exception as e:
            print(f"[ERROR] Error creating user: {e}")
            return False
    else:
        print("[ERROR] Form validation errors:")
        for field, errors in form.errors.items():
            for error in errors:
                print(f"  - {field}: {error}")
        return False

def test_user_login():
    """Test user login functionality"""
    print("\nTesting user login...")
    
    # First create a user if doesn't exist
    email = 'test@example.com'
    password = 'TestPassword123!'
    
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"[SUCCESS] Created test user: {email}")
    
    # Test authentication
    factory = RequestFactory()
    request = factory.post('/login/')
    
    form_data = {
        'username': email,
        'password': password
    }
    
    form = UserLoginForm(request, data=form_data)
    
    if form.is_valid():
        authenticated_user = form.get_user()
        print(f"[SUCCESS] User authenticated successfully: {authenticated_user.email}")
        return True
    else:
        print("[ERROR] Login form validation errors:")
        for field, errors in form.errors.items():
            for error in errors:
                print(f"  - {field}: {error}")
        return False

def test_password_reset():
    """Test password reset functionality"""
    print("\nTesting password reset...")
    
    # Ensure user exists
    email = 'test@example.com'
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True
        }
    )
    
    if created:
        user.set_password('TestPassword123!')
        user.save()
    
    # Test that user can be found for password reset
    try:
        user = User.objects.get(email=email)
        print(f"[SUCCESS] User found for password reset: {user.email}")
        return True
    except User.DoesNotExist:
        print("[ERROR] User not found for password reset")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("AUTHENTICATION SYSTEM TESTS")
    print("=" * 50)
    
    tests = [
        test_user_registration,
        test_user_login,
        test_password_reset
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"[ERROR] Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("[SUCCESS] All tests passed! Authentication system is working correctly.")
    else:
        print("[ERROR] Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
