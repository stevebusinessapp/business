#!/usr/bin/env python
"""
Test script to verify email configuration
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
django.setup()

from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from apps.accounts.models import User

def test_email_configuration():
    """Test basic email sending"""
    print("Testing email configuration...")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        print("\n[WARNING] Using console backend - emails will only be printed to console")
        print("Configure your email settings in .env file to send real emails")
    else:
        print("\n[OK] Using SMTP backend - emails will be sent")
        
    return True

def test_password_reset_email(email_address):
    """Test password reset email for a specific user"""
    try:
        user = User.objects.get(email=email_address)
        print(f"\nTesting password reset email for: {email_address}")
        
        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Create reset URL
        reset_url = f"http://127.0.0.1:8000/auth/password_reset/confirm/{uid}/{token}/"
        
        # Send email
        subject = "Password Reset Request"
        message = f"""
        Hi {user.get_full_name() or user.email},
        
        You have requested to reset your password. Click the link below to reset it:
        
        {reset_url}
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        Your App Team
        """
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email_address]
        
        send_mail(subject, message, from_email, recipient_list)
        print(f"[OK] Password reset email sent successfully to {email_address}")
        print(f"Reset URL: {reset_url}")
        
    except User.DoesNotExist:
        print(f"[ERROR] User with email {email_address} not found")
    except Exception as e:
        print(f"[ERROR] Error sending email: {str(e)}")

if __name__ == "__main__":
    print("=== Email Configuration Test ===")
    test_email_configuration()
    
    print("\n=== Password Reset Email Test ===")
    email = input("Enter your email address to test password reset: ").strip()
    if email:
        test_password_reset_email(email)
    else:
        print("No email provided - skipping password reset test")
