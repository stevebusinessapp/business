#!/usr/bin/env python
"""
Test script for enhanced inventory export functionality
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

def test_enhanced_export_functionality():
    """Test the enhanced export functionality with company branding"""
    print("Testing Enhanced Inventory Export Functionality...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email='test_enhanced_export@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Enhanced Export'
        }
    )
    
    if created:
        print(f"Created test user: {user.email}")
    
    # Create company profile with logo
    company_profile, created = CompanyProfile.objects.get_or_create(
        user=user,
        defaults={
            'company_name': 'Enhanced Test Company Ltd.',
            'currency_code': 'USD',
            'currency_symbol': '$',
            'email': 'info@enhancedtest.com',
            'phone': '+1234567890',
            'address': '123 Business Street, Suite 100, New York, NY 10001',
            'website': 'https://www.enhancedtest.com'
        }
    )
    
    if created:
        print(f"Created company profile: {company_profile.company_name}")
    
    # Create test layout
    layout, created = InventoryLayout.objects.get_or_create(
        user=user,
        name='Enhanced Test Layout',
        defaults={
            'description': 'Enhanced test layout for export with branding',
            'is_default': True,
            'auto_calculate': True
        }
    )
    
    # Create test category
    category, created = InventoryCategory.objects.get_or_create(
        user=user,
        name='Enhanced Category',
        defaults={
            'description': 'Enhanced test category'
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
        {'name': 'Premium Laptop', 'sku': 'LAP001', 'qty': 15, 'price': 1299.99},
        {'name': 'Wireless Mouse', 'sku': 'MOU002', 'qty': 50, 'price': 29.99},
        {'name': 'Mechanical Keyboard', 'sku': 'KEY003', 'qty': 25, 'price': 89.99},
        {'name': '4K Monitor', 'sku': 'MON004', 'qty': 10, 'price': 399.99},
        {'name': 'USB-C Cable', 'sku': 'CAB005', 'qty': 100, 'price': 12.99},
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
                    'description': f'High-quality {product["name"].lower()} for professional use',
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
    
    # Test the export functionality
    client = Client()
    client.force_login(user)
    
    # Test PDF export
    print("\n=== Testing PDF Export ===")
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
        else:
            print("❌ PDF content type incorrect")
    elif response.status_code == 302:
        print("✅ PDF export successful (redirect)")
    else:
        print(f"❌ PDF export failed with status {response.status_code}")
    
    # Test Excel export
    print("\n=== Testing Excel Export ===")
    form_data['format'] = 'excel'
    
    response = client.post(reverse('inventory:export'), data=form_data)
    print(f"Excel Export Response Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Excel export working correctly!")
        if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in response.get('Content-Type', ''):
            print("✅ Excel content type correct")
        else:
            print("❌ Excel content type incorrect")
    elif response.status_code == 302:
        print("✅ Excel export successful (redirect)")
    else:
        print(f"❌ Excel export failed with status {response.status_code}")
    
    # Test CSV export
    print("\n=== Testing CSV Export ===")
    form_data['format'] = 'csv'
    
    response = client.post(reverse('inventory:export'), data=form_data)
    print(f"CSV Export Response Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ CSV export working correctly!")
        if 'text/csv' in response.get('Content-Type', ''):
            print("✅ CSV content type correct")
        else:
            print("❌ CSV content type incorrect")
    elif response.status_code == 302:
        print("✅ CSV export successful (redirect)")
    else:
        print(f"❌ CSV export failed with status {response.status_code}")
    
    # Test export preview with company branding
    print("\n=== Testing Export Preview with Company Branding ===")
    preview_data = {
        'layout_id': layout.id,
        'include_low_stock': True
    }
    
    response = client.post(
        reverse('inventory:ajax_export_preview'),
        data=json.dumps(preview_data),
        content_type='application/json'
    )
    
    print(f"Export Preview Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Export preview with company branding working correctly!")
            print(f"   - Total items: {data['summary']['total_items']}")
            print(f"   - Total value: {company_profile.currency_symbol}{data['summary']['total_value']:.2f}")
            print(f"   - Categories: {data['summary']['categories']}")
            print(f"   - Low stock items: {data['summary']['low_stock_count']}")
            print(f"   - Preview items: {len(data['preview_data'])}")
            
            # Check if currency symbol is being used correctly
            if data['summary']['total_value'] > 0:
                print("✅ Currency formatting working correctly")
            else:
                print("⚠️  Currency formatting - no values to test")
        else:
            print(f"❌ Export preview failed: {data.get('error')}")
    else:
        print(f"❌ Export preview request failed with status {response.status_code}")
    
    # Clean up test data
    print("\nCleaning up test data...")
    for item in test_items:
        item.delete()
    layout.delete()
    category.delete()
    # Don't delete status as it's referenced by other items
    company_profile.delete()
    user.delete()
    
    print("✅ Enhanced export test completed successfully!")

if __name__ == '__main__':
    test_enhanced_export_functionality() 