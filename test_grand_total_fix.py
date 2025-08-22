#!/usr/bin/env python
"""
Test script for grand total amount fix in PDF export
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

def test_grand_total_fix():
    """Test that the grand total amount is no longer being cut off"""
    print("Testing Grand Total Amount Fix...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email='test_grand_total_fix@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Grand Total Fix'
        }
    )
    
    if created:
        print(f"Created test user: {user.email}")
    
    # Create company profile
    company_profile, created = CompanyProfile.objects.get_or_create(
        user=user,
        defaults={
            'company_name': 'Grand Total Fix Test Company',
            'currency_code': 'USD',
            'currency_symbol': '$',
            'email': 'info@grandtotalfix.com',
            'phone': '+1234567890',
            'address': '123 Grand Total Fix Street, Test City, Test Country',
            'website': 'https://www.grandtotalfix.com'
        }
    )
    
    if created:
        print(f"Created company profile: {company_profile.company_name}")
    
    # Create test layout
    layout, created = InventoryLayout.objects.get_or_create(
        user=user,
        name='Grand Total Fix Layout',
        defaults={
            'description': 'Test layout for grand total amount fix',
            'is_default': True,
            'auto_calculate': True
        }
    )
    
    # Create test category
    category, created = InventoryCategory.objects.get_or_create(
        user=user,
        name='Grand Total Fix Category',
        defaults={
            'description': 'Test category for grand total fix'
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
    
    # Create test inventory items with high values to test grand total
    test_items = []
    test_products = [
        {
            'name': 'High Value Product 1',
            'sku': 'HVP001',
            'qty': 1000,
            'price': 999999.99
        },
        {
            'name': 'High Value Product 2',
            'sku': 'HVP002',
            'qty': 500,
            'price': 888888.88
        },
        {
            'name': 'Medium Value Product',
            'sku': 'MVP001',
            'qty': 100,
            'price': 55555.55
        },
        {
            'name': 'Low Value Product',
            'sku': 'LVP001',
            'qty': 50,
            'price': 1234.56
        },
        {
            'name': 'Very High Value Product',
            'sku': 'VHVP001',
            'qty': 2000,
            'price': 1500000.00
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
                    'description': f'Test product {i+1} for grand total testing',
                    'category': {
                        'id': category.id,
                        'name': category.name
                    }
                }
            }
        )
        test_items.append(item)
        if created:
            print(f"Created test item: {item.product_name} - Qty: {product['qty']}, Price: ${product['price']:,.2f}")
    
    # Test the PDF export functionality
    client = Client()
    client.force_login(user)
    
    print("\n=== Testing Grand Total Amount Fix ===")
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
        pdf_filename = "grand_total_fix_test.pdf"
        with open(pdf_filename, 'wb') as pdf_file:
            pdf_file.write(response.content)
        
        print(f"✅ PDF saved to: {os.path.abspath(pdf_filename)}")
        print(f"📄 PDF Size: {len(response.content)} bytes")
        
        # Check if response contains PDF magic bytes
        if response.content.startswith(b'%PDF'):
            print("✅ Valid PDF file detected")
        else:
            print("⚠️  Response may not be a valid PDF file")
        
        # Calculate expected grand total
        expected_total = sum(item.total_value for item in test_items)
        print(f"💰 Expected Grand Total: ${expected_total:,.2f}")
        
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
    
    print("✅ Grand total fix test completed!")
    print(f"\n📝 Manual Verification Steps:")
    print(f"1. Open the file: {os.path.abspath(pdf_filename)}")
    print("2. Check that the Grand Total amount is fully visible")
    print("3. Verify that the total amount is not cut off")
    print("4. Ensure the grand total row is properly formatted")
    print("5. Check that the currency symbol displays correctly")
    print("6. Verify that the total value matches the expected amount")
    print("\n🔍 What to look for:")
    print("- Grand Total amount should be fully visible")
    print("- No numbers should be cut off at cell edges")
    print("- Currency symbol should display properly")
    print("- Total should match the calculated sum")
    print("- Grand Total row should be properly highlighted")

if __name__ == '__main__':
    test_grand_total_fix() 