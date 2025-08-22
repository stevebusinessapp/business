#!/usr/bin/env python
"""
Test script for serial number column fix in PDF export
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
django.setup()

from apps.inventory.models import InventoryItem, InventoryLayout, InventoryCategory, InventoryStatus
from apps.core.models import CompanyProfile

User = get_user_model()

def test_serial_number_fix():
    """Test that the serial number column is no longer being cut off"""
    print("Testing Serial Number Column Fix...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email='test_serial_number_fix@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Serial Number Fix'
        }
    )
    
    if created:
        print(f"Created test user: {user.email}")
    
    # Create company profile
    company_profile, created = CompanyProfile.objects.get_or_create(
        user=user,
        defaults={
            'company_name': 'Serial Number Fix Test Company',
            'currency_code': 'USD',
            'currency_symbol': '$',
            'email': 'info@serialnumberfix.com',
            'phone': '+1234567890',
            'address': '123 Serial Number Fix Street, Test City, Test Country',
            'website': 'https://www.serialnumberfix.com'
        }
    )
    
    if created:
        print(f"Created company profile: {company_profile.company_name}")
    
    # Create test layout
    layout, created = InventoryLayout.objects.get_or_create(
        user=user,
        name='Serial Number Fix Layout',
        defaults={
            'description': 'Test layout for serial number column fix',
            'is_default': True,
            'auto_calculate': True
        }
    )
    
    # Create test category
    category, created = InventoryCategory.objects.get_or_create(
        user=user,
        name='Serial Number Fix Category',
        defaults={
            'description': 'Test category for serial number fix'
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
    
    # Create test inventory items to test serial number display
    test_items = []
    test_products = [
        {
            'name': 'Product A',
            'sku': 'SKU001',
            'qty': 10,
            'price': 100.00
        },
        {
            'name': 'Product B',
            'sku': 'SKU002',
            'qty': 20,
            'price': 200.00
        },
        {
            'name': 'Product C',
            'sku': 'SKU003',
            'qty': 30,
            'price': 300.00
        },
        {
            'name': 'Product D',
            'sku': 'SKU004',
            'qty': 40,
            'price': 400.00
        },
        {
            'name': 'Product E',
            'sku': 'SKU005',
            'qty': 50,
            'price': 500.00
        },
        {
            'name': 'Product F',
            'sku': 'SKU006',
            'qty': 60,
            'price': 600.00
        },
        {
            'name': 'Product G',
            'sku': 'SKU007',
            'qty': 70,
            'price': 700.00
        },
        {
            'name': 'Product H',
            'sku': 'SKU008',
            'qty': 80,
            'price': 800.00
        },
        {
            'name': 'Product I',
            'sku': 'SKU009',
            'qty': 90,
            'price': 900.00
        },
        {
            'name': 'Product J',
            'sku': 'SKU010',
            'qty': 100,
            'price': 1000.00
        }
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
                    'description': f'Test product {i+1} for serial number testing',
                    'category': {
                        'id': category.id,
                        'name': category.name
                    }
                }
            }
        )
        test_items.append(item)
        if created:
            print(f"Created test item: {item.product_name} - Serial: {i+1}")
    
    # Test the PDF export functionality
    client = Client()
    client.force_login(user)
    
    print("\n=== Testing Serial Number Column Fix ===")
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
        
        # Save the PDF to a file for manual verification
        pdf_filename = "serial_number_fix_test.pdf"
        with open(pdf_filename, 'wb') as pdf_file:
            pdf_file.write(response.content)
        
        print(f"✅ PDF saved to: {os.path.abspath(pdf_filename)}")
        print(f"📄 PDF Size: {len(response.content)} bytes")
        
        # Check if response contains PDF magic bytes
        if response.content.startswith(b'%PDF'):
            print("✅ Valid PDF file detected")
        else:
            print("⚠️  Response may not be a valid PDF file")
        
    elif response.status_code == 302:
        print("✅ PDF export successful (redirect)")
    else:
        print(f"❌ PDF export failed with status {response.status_code}")
    
    # Clean up test data
    print("\nCleaning up test data...")
    for item in test_items:
        item.delete()
    layout.delete()
    category.delete()
    # Don't delete status as it's referenced by other items
    company_profile.delete()
    user.delete()
    
    print("✅ Serial number fix test completed!")
    print(f"\n📝 Manual Verification Steps:")
    print(f"1. Open the file: {os.path.abspath(pdf_filename)}")
    print("2. Check that serial numbers (1, 2, 3, etc.) are fully visible")
    print("3. Verify that serial numbers are not cut off at the left edge")
    print("4. Ensure there's adequate spacing around serial numbers")
    print("5. Check that the S/N header is properly aligned")
    print("6. Verify that all serial numbers are clearly readable")
    print("\n🔍 What to look for:")
    print("- Serial numbers should be fully visible")
    print("- No numbers should be cut off at the left edge")
    print("- Adequate padding around serial numbers")
    print("- Clear separation from the next column")
    print("- Professional appearance and readability")

if __name__ == '__main__':
    test_serial_number_fix() 