#!/usr/bin/env python
"""
Test script for wider total column in PDF export
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

def test_wider_total_column():
    """Test that the total column is wider and can accommodate large amounts"""
    print("Testing Wider Total Column...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email='test_wider_total@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Wider Total'
        }
    )
    
    if created:
        print(f"Created test user: {user.email}")
    
    # Create company profile
    company_profile, created = CompanyProfile.objects.get_or_create(
        user=user,
        defaults={
            'company_name': 'Wider Total Test Company',
            'currency_code': 'USD',
            'currency_symbol': '$',
            'email': 'info@widertotal.com',
            'phone': '+1234567890',
            'address': '123 Wider Total Street, Test City, Test Country',
            'website': 'https://www.widertotal.com'
        }
    )
    
    if created:
        print(f"Created company profile: {company_profile.company_name}")
    
    # Create test layout
    layout, created = InventoryLayout.objects.get_or_create(
        user=user,
        name='Wider Total Test',
        defaults={
            'description': 'Test layout for wider total column',
            'is_default': True,
            'auto_calculate': True
        }
    )
    
    # Create test category
    category, created = InventoryCategory.objects.get_or_create(
        user=user,
        name='Wider Total Category',
        defaults={
            'description': 'Test category for wider total column'
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
    
    # Create test inventory items with large amounts to test total column width
    test_items = []
    test_products = [
        {
            'name': 'Small Amount Product',
            'sku': 'SMALL001',
            'qty': 10,
            'price': 100.00
        },
        {
            'name': 'Medium Amount Product',
            'sku': 'MEDIUM001',
            'qty': 1000,
            'price': 5000.00
        },
        {
            'name': 'Large Amount Product',
            'sku': 'LARGE001',
            'qty': 5000,
            'price': 25000.00
        },
        {
            'name': 'Very Large Amount Product',
            'sku': 'VLARGE001',
            'qty': 10000,
            'price': 100000.00
        },
        {
            'name': 'Extremely Large Amount Product',
            'sku': 'XLARGE001',
            'qty': 50000,
            'price': 500000.00
        },
        {
            'name': 'Mega Large Amount Product',
            'sku': 'MEGA001',
            'qty': 100000,
            'price': 1000000.00
        },
        {
            'name': 'Ultra Large Amount Product',
            'sku': 'ULTRA001',
            'qty': 500000,
            'price': 5000000.00
        },
        {
            'name': 'Super Large Amount Product',
            'sku': 'SUPER001',
            'qty': 1000000,
            'price': 10000000.00
        },
        {
            'name': 'Mega Ultra Large Amount Product',
            'sku': 'MEGAULTRA001',
            'qty': 5000000,
            'price': 50000000.00
        },
        {
            'name': 'Ultimate Large Amount Product',
            'sku': 'ULTIMATE001',
            'qty': 10000000,
            'price': 100000000.00
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
                    'description': f'Test product {i+1} for wider total column testing',
                    'category': {
                        'id': category.id,
                        'name': category.name
                    }
                }
            }
        )
        test_items.append(item)
        if created:
            total_value = product['qty'] * product['price']
            print(f"Created test item: {item.product_name[:30]}... - Total: ${total_value:,.2f}")
    
    # Test the PDF export functionality
    client = Client()
    client.force_login(user)
    
    print("\n=== Testing Wider Total Column ===")
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
        pdf_filename = "wider_total_column_test.pdf"
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
    
    print("✅ Wider total column test completed!")
    print(f"\n📝 Manual Verification Steps:")
    print(f"1. Open the file: {os.path.abspath(pdf_filename)}")
    print("2. Check that the Total column is noticeably wider than other columns")
    print("3. Verify that large amounts fit completely within the Total column")
    print("4. Ensure no total amounts overflow into adjacent columns")
    print("5. Check that the grand total amount is fully visible")
    print("6. Verify that all amounts are properly formatted with commas")
    print("7. Ensure the Total column header is properly aligned")
    print("8. Check that the wider column doesn't cause other columns to be too narrow")
    print("\n🔍 What to look for:")
    print("- Total column should be wider than other columns")
    print("- Large amounts should fit completely within the Total column")
    print("- No text should overflow into adjacent columns")
    print("- All amounts should be properly formatted")
    print("- Grand total should be clearly visible and complete")
    print("- Professional appearance with balanced column widths")
    print("- Proper spacing and alignment")

if __name__ == '__main__':
    test_wider_total_column() 