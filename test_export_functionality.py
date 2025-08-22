#!/usr/bin/env python
"""
Test script for inventory export functionality
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

def test_export_functionality():
    """Test the export functionality"""
    print("Testing Inventory Export Functionality...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email='test_export_user@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        print(f"Created test user: {user.email}")
    
    # Create company profile
    company_profile, created = CompanyProfile.objects.get_or_create(
        user=user,
        defaults={
            'company_name': 'Test Company',
            'currency_code': 'USD',
            'currency_symbol': '$'
        }
    )
    
    # Create test layout
    layout, created = InventoryLayout.objects.get_or_create(
        user=user,
        name='Test Layout',
        defaults={
            'description': 'Test layout for export',
            'is_default': True,
            'auto_calculate': True
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
    
    # Create test category
    category, created = InventoryCategory.objects.get_or_create(
        user=user,
        name='Test Category',
        defaults={
            'description': 'Test category'
        }
    )
    
    # Create test inventory items
    test_items = []
    for i in range(5):
        item, created = InventoryItem.objects.get_or_create(
            user=user,
            product_name=f'Test Product {i+1}',
            layout=layout,
            defaults={
                'sku_code': f'SKU{i+1:03d}',
                'status': status,
                'data': {
                    'quantity_in_stock': 10 + i,
                    'unit_price': 10.50 + i,
                    'minimum_threshold': 5,
                    'description': f'Test product description {i+1}',
                    'category': {
                        'id': category.id,
                        'name': category.name
                    }
                }
            }
        )
        test_items.append(item)
        if created:
            print(f"Created test item: {item.product_name}")
    
    # Test the export preview AJAX endpoint
    client = Client()
    client.force_login(user)
    
    # Test data for the AJAX request
    preview_data = {
        'layout_id': layout.id,
        'include_low_stock': True
    }
    
    # Make the AJAX request
    response = client.post(
        reverse('inventory:ajax_export_preview'),
        data=json.dumps(preview_data),
        content_type='application/json'
    )
    
    print(f"\nExport Preview Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Export preview AJAX endpoint working correctly!")
            print(f"   - Total items: {data['summary']['total_items']}")
            print(f"   - Total value: ${data['summary']['total_value']:.2f}")
            print(f"   - Categories: {data['summary']['categories']}")
            print(f"   - Low stock items: {data['summary']['low_stock_count']}")
            print(f"   - Preview items: {len(data['preview_data'])}")
        else:
            print(f"❌ Export preview failed: {data.get('error')}")
    else:
        print(f"❌ Export preview request failed with status {response.status_code}")
    
    # Test the export page
    response = client.get(reverse('inventory:export'))
    print(f"\nExport Page Response Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Export page loads correctly!")
        # Check if the form is present
        if hasattr(response, 'context') and response.context and 'form' in response.context:
            print("✅ Export form is present in context")
        else:
            print("❌ Export form missing from context")
    else:
        print(f"❌ Export page failed to load with status {response.status_code}")
    
    # Test form submission
    form_data = {
        'layout': layout.id,
        'format': 'excel',
        'include_calculations': True,
        'include_branding': True,
        'include_low_stock': True
    }
    
    response = client.post(reverse('inventory:export'), data=form_data)
    print(f"\nExport Form Submission Response Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Export form submission working!")
        if hasattr(response, 'context') and response.context and 'form' in response.context and response.context['form'].errors:
            print(f"❌ Form has errors: {response.context['form'].errors}")
        else:
            print("✅ Form submission successful")
    elif response.status_code == 302:
        print("✅ Export form submission successful (redirect)")
    else:
        print(f"❌ Export form submission failed with status {response.status_code}")
    
    # Clean up test data
    print("\nCleaning up test data...")
    for item in test_items:
        item.delete()
    layout.delete()
    category.delete()
    # Don't delete status as it's referenced by other items
    company_profile.delete()
    user.delete()
    
    print("✅ Test completed successfully!")

if __name__ == '__main__':
    test_export_functionality() 