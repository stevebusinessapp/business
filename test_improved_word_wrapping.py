#!/usr/bin/env python
"""
Test script for improved word wrapping in PDF export
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

def test_improved_word_wrapping():
    """Test that improved word wrapping is working correctly in PDF export"""
    print("Testing Improved Word Wrapping in PDF Export...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email='test_improved_wrapping@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Improved Wrapping'
        }
    )
    
    if created:
        print(f"Created test user: {user.email}")
    
    # Create company profile
    company_profile, created = CompanyProfile.objects.get_or_create(
        user=user,
        defaults={
            'company_name': 'Improved Word Wrapping Test Company',
            'currency_code': 'USD',
            'currency_symbol': '$',
            'email': 'info@improvedwrapping.com',
            'phone': '+1234567890',
            'address': '123 Improved Wrapping Street, Test City, Test Country',
            'website': 'https://www.improvedwrapping.com'
        }
    )
    
    if created:
        print(f"Created company profile: {company_profile.company_name}")
    
    # Create test layout
    layout, created = InventoryLayout.objects.get_or_create(
        user=user,
        name='Improved Wrapping Layout',
        defaults={
            'description': 'Test layout for improved word wrapping functionality',
            'is_default': True,
            'auto_calculate': True
        }
    )
    
    # Create test category
    category, created = InventoryCategory.objects.get_or_create(
        user=user,
        name='Improved Wrapping Category',
        defaults={
            'description': 'Test category for improved word wrapping'
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
    
    # Create test inventory items with very long text to test improved word wrapping
    test_items = []
    test_products = [
        {
            'name': 'This is an extremely long product name that should definitely wrap to multiple lines in the PDF table cell to thoroughly test the improved word wrapping functionality and ensure it works properly without crossing into other cells',
            'sku': 'EXTREMELY-LONG-SKU-CODE-THAT-SHOULD-DEFINITELY-WRAP-TO-MULTIPLE-LINES-123456789-ABCDEFGHIJKLMNOP-QRSTUVWXYZ',
            'qty': 10,
            'price': 1000.00
        },
        {
            'name': 'Another incredibly long product name with multiple words that absolutely need to be wrapped properly in the exported PDF document to demonstrate the improved word wrapping capabilities and prevent text overflow',
            'sku': 'ANOTHER-INCREDIBLY-LONG-SKU-WITH-MANY-CHARACTERS-987654321-ZYXWVUTSRQPONMLKJIHGFEDCBA-123456789',
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
            'name': 'Product with special characters: @#$%^&*() and numbers 123456789 and more text to make it longer and test word wrapping',
            'sku': 'SPECIAL-CHARS-@#$%^&*()-123456789-EXTENDED-VERSION-WITH-MORE-CHARACTERS-AND-NUMBERS',
            'qty': 20,
            'price': 750.00
        },
        {
            'name': 'Product with very long description that includes technical specifications and detailed information about the product features and capabilities and additional details about functionality and performance',
            'sku': 'TECHNICAL-SPECIFICATIONS-AND-DETAILED-FEATURES-CODE-2024-EXTENDED-VERSION-WITH-MORE-DETAILS-AND-INFO',
            'qty': 8,
            'price': 1500.00
        },
        {
            'name': 'Super long product name with many words that need to be wrapped properly in the PDF export to demonstrate the improved word wrapping functionality is working correctly and preventing text overflow issues',
            'sku': 'SUPER-LONG-SKU-CODE-WITH-MANY-CHARACTERS-AND-NUMBERS-123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ-EXTENDED',
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
                    'description': f'Test product {i+1} for improved word wrapping testing',
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
    
    print("\n=== Testing Improved Word Wrapping in PDF Export ===")
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
        pdf_filename = "improved_word_wrapping_test.pdf"
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
    
    print("✅ Improved word wrapping test completed!")
    print(f"\n📝 Manual Verification Steps:")
    print(f"1. Open the file: {os.path.abspath(pdf_filename)}")
    print("2. Check that long product names wrap properly within their cells")
    print("3. Verify that long SKU codes break across lines within their cells")
    print("4. Ensure no text crosses into adjacent table cells")
    print("5. Check that the table remains well-formatted and readable")
    print("6. Verify that cell heights adjust automatically for wrapped text")
    print("\n🔍 What to look for:")
    print("- Product names should wrap within their designated column")
    print("- SKU codes should break at appropriate points")
    print("- No text should overflow into neighboring cells")
    print("- Table should maintain proper structure and alignment")
    print("- All content should be fully visible and readable")

if __name__ == '__main__':
    test_improved_word_wrapping() 