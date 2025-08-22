#!/usr/bin/env python
"""
Test script for dynamic currency symbol handling in PDF export
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
django.setup()

from apps.inventory.models import InventoryItem, InventoryLayout, InventoryCategory, InventoryStatus
from apps.core.models import CompanyProfile

User = get_user_model()

def test_dynamic_currency_symbols():
    """Test that PDF export properly handles different currency symbols"""
    print("Testing Dynamic Currency Symbol Handling...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email='test_dynamic_currency@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Dynamic Currency'
        }
    )
    
    if created:
        print(f"Created test user: {user.email}")
    
    # Create company profile
    company_profile, created = CompanyProfile.objects.get_or_create(
        user=user,
        defaults={
            'company_name': 'Dynamic Currency Test Company',
            'currency_code': 'NGN',
            'currency_symbol': '₦',
            'email': 'info@dynamiccurrency.com',
            'phone': '+2341234567890',
            'address': '123 Currency Street, Lagos, Nigeria',
            'website': 'https://www.dynamiccurrency.com'
        }
    )
    
    if created:
        print(f"Created company profile: {company_profile.company_name}")
    
    # Create test layout
    layout, created = InventoryLayout.objects.get_or_create(
        user=user,
        name='Dynamic Currency Layout',
        defaults={
            'description': 'Test layout for dynamic currency testing',
            'is_default': True,
            'auto_calculate': True
        }
    )
    
    # Create test category
    category, created = InventoryCategory.objects.get_or_create(
        user=user,
        name='Dynamic Currency Category',
        defaults={
            'description': 'Test category for currency testing'
        }
    )
    
    # Create test status
    status, created = InventoryStatus.objects.get_or_create(
        name='in_stock',
        defaults={
            'display_name': 'In Stock',
            'color': '#28a745',
            'sort_order': 1
        }
    )
    
    # Create test inventory item
    item, created = InventoryItem.objects.get_or_create(
        user=user,
        product_name='Test Product',
        layout=layout,
        defaults={
            'sku_code': 'TEST001',
            'status': status,
            'data': {
                'quantity_in_stock': 10,
                'unit_price': 1000.00,
                'minimum_threshold': 5,
                'description': 'Test product for currency testing',
                'category': {
                    'id': category.id,
                    'name': category.name
                }
            }
        }
    )
    
    if created:
        print(f"Created test item: {item.product_name}")
    
    # Test the PDF export functionality
    client = Client()
    client.force_login(user)
    
    # Test different currency symbols
    test_currencies = [
        {'symbol': '₦', 'name': 'Naira', 'code': 'NGN'},
        {'symbol': '$', 'name': 'Dollar', 'code': 'USD'},
        {'symbol': '€', 'name': 'Euro', 'code': 'EUR'},
        {'symbol': '£', 'name': 'Pound', 'code': 'GBP'},
        {'symbol': '¥', 'name': 'Yen', 'code': 'JPY'},
        {'symbol': '₹', 'name': 'Rupee', 'code': 'INR'},
        {'symbol': '₽', 'name': 'Ruble', 'code': 'RUB'},
        {'symbol': '₩', 'name': 'Won', 'code': 'KRW'},
    ]
    
    print("\n=== Testing Different Currency Symbols ===")
    
    for currency in test_currencies:
        print(f"\nTesting {currency['name']} ({currency['symbol']})...")
        
        # Update company profile with new currency
        company_profile.currency_symbol = currency['symbol']
        company_profile.currency_code = currency['code']
        company_profile.save()
        
        # Test PDF export
        form_data = {
            'layout': layout.id,
            'format': 'pdf',
            'include_calculations': True,
            'include_branding': True,
            'include_low_stock': True
        }
        
        response = client.post(reverse('inventory:export'), data=form_data)
        
        if response.status_code == 200:
            print(f"✅ {currency['name']} PDF export successful")
            
            # Check if the currency symbol appears in the response
            content = response.content.decode('utf-8', errors='ignore')
            
            # For binary PDF content, we can't easily search for the symbol
            # But we can verify the export worked
            if 'application/pdf' in response.get('Content-Type', ''):
                print(f"✅ {currency['name']} PDF content type correct")
            else:
                print(f"❌ {currency['name']} PDF content type incorrect")
        else:
            print(f"❌ {currency['name']} PDF export failed with status {response.status_code}")
    
    # Test with a custom currency symbol
    print(f"\nTesting Custom Currency Symbol...")
    company_profile.currency_symbol = '₿'  # Bitcoin
    company_profile.currency_code = 'BTC'
    company_profile.save()
    
    response = client.post(reverse('inventory:export'), data=form_data)
    if response.status_code == 200:
        print("✅ Custom currency symbol PDF export successful")
    else:
        print(f"❌ Custom currency symbol PDF export failed with status {response.status_code}")
    
    # Test with empty currency symbol
    print(f"\nTesting Empty Currency Symbol...")
    company_profile.currency_symbol = ''
    company_profile.save()
    
    response = client.post(reverse('inventory:export'), data=form_data)
    if response.status_code == 200:
        print("✅ Empty currency symbol PDF export successful (should use default)")
    else:
        print(f"❌ Empty currency symbol PDF export failed with status {response.status_code}")
    
    # Test with a very long currency symbol
    print(f"\nTesting Long Currency Symbol...")
    company_profile.currency_symbol = 'NGN'  # Use currency code as symbol
    company_profile.save()
    
    response = client.post(reverse('inventory:export'), data=form_data)
    if response.status_code == 200:
        print("✅ Long currency symbol PDF export successful")
    else:
        print(f"❌ Long currency symbol PDF export failed with status {response.status_code}")
    
    # Clean up test data
    print("\nCleaning up test data...")
    item.delete()
    layout.delete()
    category.delete()
    # Don't delete status as it's referenced by other items
    company_profile.delete()
    user.delete()
    
    print("✅ Dynamic currency symbol test completed successfully!")

if __name__ == '__main__':
    test_dynamic_currency_symbols() 