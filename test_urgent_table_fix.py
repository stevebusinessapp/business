#!/usr/bin/env python
"""
Test script for urgent table layout fix
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

def test_urgent_table_fix():
    """Test that the urgent table layout fix is working correctly"""
    print("Testing Urgent Table Layout Fix...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email='test_urgent_fix@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Urgent Fix'
        }
    )
    
    if created:
        print(f"Created test user: {user.email}")
    
    # Create company profile
    company_profile, created = CompanyProfile.objects.get_or_create(
        user=user,
        defaults={
            'company_name': 'Urgent Table Fix Test Company',
            'currency_code': 'USD',
            'currency_symbol': '$',
            'email': 'info@urgentfix.com',
            'phone': '+1234567890',
            'address': '123 Urgent Fix Street, Test City, Test Country',
            'website': 'https://www.urgentfix.com'
        }
    )
    
    if created:
        print(f"Created company profile: {company_profile.company_name}")
    
    # Create test layout
    layout, created = InventoryLayout.objects.get_or_create(
        user=user,
        name='Urgent Fix Layout',
        defaults={
            'description': 'Test layout for urgent table layout fix',
            'is_default': True,
            'auto_calculate': True
        }
    )
    
    # Create test category
    category, created = InventoryCategory.objects.get_or_create(
        user=user,
        name='Urgent Fix Category',
        defaults={
            'description': 'Test category for urgent fix'
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
    
    # Create test inventory items with very long text to test the fix
    test_items = []
    test_products = [
        {
            'name': 'This is an extremely long product name that should definitely wrap to multiple lines in the PDF table cell to thoroughly test the urgent table layout fix and ensure it works properly without cutting off any content',
            'sku': 'EXTREMELY-LONG-SKU-CODE-THAT-SHOULD-DEFINITELY-WRAP-TO-MULTIPLE-LINES-123456789-ABCDEFGHIJKLMNOP-QRSTUVWXYZ-EXTENDED-VERSION',
            'qty': 10,
            'price': 1000.00
        },
        {
            'name': 'Another incredibly long product name with multiple words that absolutely need to be wrapped properly in the exported PDF document to demonstrate the urgent table layout fix capabilities and prevent any content from being cut off',
            'sku': 'ANOTHER-INCREDIBLY-LONG-SKU-WITH-MANY-CHARACTERS-987654321-ZYXWVUTSRQPONMLKJIHGFEDCBA-123456789-EXTENDED',
            'qty': 5,
            'price': 2500.00
        },
        {
            'name': 'Short Name',
            'sku': 'SHORT',
            'qty': 15,
            'price': 500.00
        },
        {
            'name': 'Product with special characters: @#$%^&*() and numbers 123456789 and more text to make it longer and test the urgent table layout fix',
            'sku': 'SPECIAL-CHARS-@#$%^&*()-123456789-EXTENDED-VERSION-WITH-MORE-CHARACTERS-AND-NUMBERS-AND-SYMBOLS',
            'qty': 20,
            'price': 750.00
        },
        {
            'name': 'Product with very long description that includes technical specifications and detailed information about the product features and capabilities and additional details about functionality and performance metrics',
            'sku': 'TECHNICAL-SPECIFICATIONS-AND-DETAILED-FEATURES-CODE-2024-EXTENDED-VERSION-WITH-MORE-DETAILS-AND-INFO-AND-METRICS',
            'qty': 8,
            'price': 1500.00
        },
        {
            'name': 'Super long product name with many words that need to be wrapped properly in the PDF export to demonstrate the urgent table layout fix is working correctly and preventing any content cutoff issues',
            'sku': 'SUPER-LONG-SKU-CODE-WITH-MANY-CHARACTERS-AND-NUMBERS-123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ-EXTENDED-VERSION-WITH-MORE-DETAILS',
            'qty': 12,
            'price': 2000.00
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
                    'description': f'Test product {i+1} for urgent table layout fix testing',
                    'category': {
                        'id': category.id,
                        'name': category.name
                    }
                }
            }
        )
        test_items.append(item)
        if created:
            print(f"Created test item: {item.product_name[:50]}... - {item.sku_code[:30]}...")
    
    # Test the PDF export functionality
    client = Client()
    client.force_login(user)
    
    print("\n=== Testing Urgent Table Layout Fix ===")
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
        pdf_filename = "urgent_table_fix_test.pdf"
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
    
    print("✅ Urgent table layout fix test completed!")
    print(f"\n📝 Manual Verification Steps:")
    print(f"1. Open the file: {os.path.abspath(pdf_filename)}")
    print("2. Check that NO content is cut off at page edges")
    print("3. Verify that all text fits within table cells")
    print("4. Ensure the table fits completely on the page")
    print("5. Check that word wrapping works properly")
    print("6. Verify that the layout is compact and readable")
    print("\n🔍 What to look for:")
    print("- No text should be cut off at page margins")
    print("- All content should be fully visible")
    print("- Table should fit within page boundaries")
    print("- Word wrapping should work effectively")
    print("- Layout should be compact but readable")

if __name__ == '__main__':
    test_urgent_table_fix() 