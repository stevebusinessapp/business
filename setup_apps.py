#!/usr/bin/env python
"""
Script to create basic Django app files for remaining modules
"""

import os
import sys

# Add the project to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')

import django
django.setup()

apps_to_create = [
    'receipts', 'waybills', 'job_orders', 'quotations', 
    'expenses', 'inventory', 'clients', 'accounting'
]

def create_basic_app_files(app_name):
    """Create basic Django app files"""
    app_path = f"apps/{app_name}"
    
    # Create __init__.py
    with open(f"{app_path}/__init__.py", 'w') as f:
        f.write("")
    
    # Create apps.py
    app_class = ''.join(word.capitalize() for word in app_name.split('_'))
    with open(f"{app_path}/apps.py", 'w') as f:
        f.write(f"""from django.apps import AppConfig


class {app_class}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
    verbose_name = '{app_class}'
""")
    
    # Create models.py
    with open(f"{app_path}/models.py", 'w') as f:
        f.write("""from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

# Models will be added here based on requirements
""")
    
    # Create admin.py
    with open(f"{app_path}/admin.py", 'w') as f:
        f.write("""from django.contrib import admin

# Register your models here.
""")
    
    # Create views.py
    with open(f"{app_path}/views.py", 'w') as f:
        f.write("""from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
""")
    
    # Create urls.py
    with open(f"{app_path}/urls.py", 'w') as f:
        f.write(f"""from django.urls import path
from . import views

app_name = '{app_name}'

urlpatterns = [
    # URLs will be added here
]
""")
    
    # Create api_urls.py
    with open(f"{app_path}/api_urls.py", 'w') as f:
        f.write("""from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# Register viewsets here

urlpatterns = [
    path('', include(router.urls)),
]
""")
    
    # Create serializers.py
    with open(f"{app_path}/serializers.py", 'w') as f:
        f.write("""from rest_framework import serializers

# Serializers will be added here
""")
    
    # Create forms.py
    with open(f"{app_path}/forms.py", 'w') as f:
        f.write("""from django import forms

# Forms will be added here
""")
    
    print(f"✓ Created basic files for {app_name} app")

if __name__ == "__main__":
    print("Setting up remaining Django apps...")
    
    for app_name in apps_to_create:
        if os.path.exists(f"apps/{app_name}"):
            create_basic_app_files(app_name)
        else:
            print(f"! Directory apps/{app_name} does not exist")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Run: python manage.py makemigrations")
    print("2. Run: python manage.py migrate")
    print("3. Run: python manage.py createsuperuser")
    print("4. Run: python manage.py runserver")
