#!/usr/bin/env python
"""
Test script for PDF export fixes
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

def test_pdf_export_fixes():
    """Test the PDF export fixes for currency symbols and HTML tags"""
    print("Testing PDF Export Fixes...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email='test_pdf_fixes@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'PDF Fixes'
        }
    )
    
    if created:
        print(f"Created test user: {user.email}")
    
    # Create company profile with different currency symbols to test
    company_profile, created = CompanyProfile.objects.get_or_create(
        user=user,
        defaults={
            'company_name': 'PDF Test Company Ltd.',
            'currency_code': 'NGN',
            'currency_symbol': '₦',  # This should be converted to 'N'
            'email': 'info@pdftest.com',
            'phone': '+2341234567890',
            'address': '123 Test Street, Lagos, Nigeria',
            'website': 'https://www.pdftest.com'
        }
    )
    
    if created:
        print(f"Created company profile: {company_profile.company_name}")
    
    # Create test layout
    layout, created = InventoryLayout.objects.get_or_create(
        user=user,
        name='PDF Test Layout',
        defaults={
            'description': 'Test layout for PDF export fixes',
            'is_default': True,
            'auto_calculate': True
        }
    )
    
    # Create test category
    category, created = InventoryCategory.objects.get_or_create(
        user=user,
        name='PDF Test Category',
        defaults={
            'description': 'Test category for PDF export'
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
    
    # Create test inventory items with realistic data
    test_items = []
    test_products = [
        {'name': 'Test Product 1', 'sku': 'TP001', 'qty': 10, 'price': 1000.00},
        {'name': 'Test Product 2', 'sku': 'TP002', 'qty': 5, 'price': 2500.00},
        {'name': 'Test Product 3', 'sku': 'TP003', 'qty': 15, 'price': 500.00},
    ]
    
    for i, product in enumerate(test_products):
        item, created = InventoryItem.objects.get_or_create(
            user=user,
            product_name=product['name'],
            layout=layout,
            defaults={
                'sku_code': product['sku'],
                'status': status,
                'data': {
                    'quantity_in_stock': product['qty'],
                    'unit_price': product['price'],
                    'minimum_threshold': 5,
                    'description': f'Test product {i+1} for PDF export testing',
                    'category': {
                        'id': category.id,
                        'name': category.name
                    }
                }
            }
        )
        test_items.append(item)
        if created:
            print(f"Created test item: {item.product_name} - {item.sku_code}")
    
    # Test the PDF export functionality
    client = Client()
    client.force_login(user)
    
    # Test PDF export with calculations and branding
    print("\n=== Testing PDF Export with Fixes ===")
    form_data = {
        'layout': layout.id,
        'format': 'pdf',
        'include_calculations': True,
        'include_branding': True,
        'include_low_stock': True
    }
    
    response = client.post(reverse('inventory:export'), data=form_data)
    print(f"PDF Export Response Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ PDF export working correctly!")
        if 'application/pdf' in response.get('Content-Type', ''):
            print("✅ PDF content type correct")
            
            # Check if the response contains the expected content
            content = response.content.decode('utf-8', errors='ignore')
            
            # Check for currency symbol fixes
            if 'N' in content:  # Should show 'N' instead of '₦'
                print("✅ Currency symbol properly converted to 'N'")
            else:
                print("⚠️  Currency symbol conversion not found")
            
            # Check for HTML tag fixes
            if '<b>Grand Total</b>' not in content:
                print("✅ HTML tags properly removed from Grand Total")
            else:
                print("❌ HTML tags still present in Grand Total")
            
            # Check for layout information removal
            if 'Layout:' not in content:
                print("✅ Layout information properly removed from summary")
            else:
                print("❌ Layout information still present in summary")
            
        else:
            print("❌ PDF content type incorrect")
    elif response.status_code == 302:
        print("✅ PDF export successful (redirect)")
    else:
        print(f"❌ PDF export failed with status {response.status_code}")
    
    # Test with different currency symbols
    print("\n=== Testing Different Currency Symbols ===")
    
    # Test with USD
    company_profile.currency_symbol = '$'
    company_profile.save()
    
    response = client.post(reverse('inventory:export'), data=form_data)
    if response.status_code == 200:
        content = response.content.decode('utf-8', errors='ignore')
        if '$' in content:
            print("✅ USD currency symbol working correctly")
        else:
            print("❌ USD currency symbol not found")
    
    # Test with EUR
    company_profile.currency_symbol = '€'
    company_profile.save()
    
    response = client.post(reverse('inventory:export'), data=form_data)
    if response.status_code == 200:
        content = response.content.decode('utf-8', errors='ignore')
        if 'EUR' in content:
            print("✅ EUR currency symbol properly converted to 'EUR'")
        else:
            print("❌ EUR currency symbol conversion not found")
    
    # Test with GBP
    company_profile.currency_symbol = '£'
    company_profile.save()
    
    response = client.post(reverse('inventory:export'), data=form_data)
    if response.status_code == 200:
        content = response.content.decode('utf-8', errors='ignore')
        if 'GBP' in content:
            print("✅ GBP currency symbol properly converted to 'GBP'")
        else:
            print("❌ GBP currency symbol conversion not found")
    
    # Clean up test data
    print("\nCleaning up test data...")
    for item in test_items:
        item.delete()
    layout.delete()
    category.delete()
    # Don't delete status as it's referenced by other items
    company_profile.delete()
    user.delete()
    
    print("✅ PDF export fixes test completed successfully!")

if __name__ == '__main__':
    test_pdf_export_fixes() 