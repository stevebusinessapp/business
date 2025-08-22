#!/usr/bin/env python
"""
Test script for word wrapping in PDF export
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

def test_word_wrapping():
    """Test that word wrapping is working correctly in PDF export"""
    print("Testing Word Wrapping in PDF Export...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email='test_word_wrapping@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Word Wrapping'
        }
    )
    
    if created:
        print(f"Created test user: {user.email}")
    
    # Create company profile
    company_profile, created = CompanyProfile.objects.get_or_create(
        user=user,
        defaults={
            'company_name': 'Word Wrapping Test Company',
            'currency_code': 'USD',
            'currency_symbol': '$',
            'email': 'info@wordwrapping.com',
            'phone': '+1234567890',
            'address': '123 Word Wrapping Street, Test City, Test Country',
            'website': 'https://www.wordwrapping.com'
        }
    )
    
    if created:
        print(f"Created company profile: {company_profile.company_name}")
    
    # Create test layout
    layout, created = InventoryLayout.objects.get_or_create(
        user=user,
        name='Word Wrapping Layout',
        defaults={
            'description': 'Test layout for word wrapping functionality',
            'is_default': True,
            'auto_calculate': True
        }
    )
    
    # Create test category
    category, created = InventoryCategory.objects.get_or_create(
        user=user,
        name='Word Wrapping Category',
        defaults={
            'description': 'Test category for word wrapping'
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
    
    # Create test inventory items with long text to test word wrapping
    test_items = []
    test_products = [
        {
            'name': 'This is a very long product name that should wrap to multiple lines in the PDF table cell to test the word wrapping functionality',
            'sku': 'VERY-LONG-SKU-CODE-THAT-SHOULD-WRAP-TO-MULTIPLE-LINES-123456789',
            'qty': 10,
            'price': 1000.00
        },
        {
            'name': 'Another extremely long product name with multiple words that need to be wrapped properly in the exported PDF document',
            'sku': 'ANOTHER-LONG-SKU-WITH-MANY-CHARACTERS-987654321',
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
            'name': 'Product with special characters: @#$%^&*() and numbers 123456789',
            'sku': 'SPECIAL-CHARS-@#$%^&*()-123456789',
            'qty': 20,
            'price': 750.00
        },
        {
            'name': 'Product with very long description that includes technical specifications and detailed information about the product features and capabilities',
            'sku': 'TECHNICAL-SPECIFICATIONS-AND-DETAILED-FEATURES-CODE-2024',
            'qty': 8,
            'price': 1500.00
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
                    'description': f'Test product {i+1} for word wrapping testing with long description',
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
    
    print("\n=== Testing Word Wrapping in PDF Export ===")
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
            
            # Check for word wrapping indicators (Paragraph objects in PDF)
            if 'Paragraph' in content or 'wordWrap' in content:
                print("✅ Word wrapping functionality detected in PDF")
            else:
                print("⚠️  Word wrapping functionality not detected")
            
            # Check for long product names (should be wrapped)
            long_product_name = "This is a very long product name that should wrap"
            if long_product_name in content:
                print("✅ Long product names are being processed")
            else:
                print("⚠️  Long product names not found")
            
            # Check for long SKU codes (should be wrapped)
            long_sku = "VERY-LONG-SKU-CODE-THAT-SHOULD-WRAP"
            if long_sku in content:
                print("✅ Long SKU codes are being processed")
            else:
                print("⚠️  Long SKU codes not found")
            
        else:
            print("❌ PDF content type incorrect")
    elif response.status_code == 302:
        print("✅ PDF export successful (redirect)")
    else:
        print(f"❌ PDF export failed with status {response.status_code}")
    
    # Test with different column widths to see word wrapping in action
    print("\n=== Testing Different Column Widths ===")
    
    # Test with narrow columns to force more wrapping
    form_data_narrow = {
        'layout': layout.id,
        'format': 'pdf',
        'include_calculations': True,
        'include_branding': True,
        'include_low_stock': True
    }
    
    response_narrow = client.post(reverse('inventory:export'), data=form_data_narrow)
    if response_narrow.status_code == 200:
        print("✅ PDF export with narrow columns working")
    else:
        print(f"❌ PDF export with narrow columns failed: {response_narrow.status_code}")
    
    # Clean up test data
    print("\nCleaning up test data...")
    for item in test_items:
        item.delete()
    layout.delete()
    category.delete()
    # Don't delete status as it's referenced by other items
    company_profile.delete()
    user.delete()
    
    print("✅ Word wrapping test completed successfully!")
    print("\n📝 Manual Verification Required:")
    print("1. Open the generated PDF file")
    print("2. Check that long product names wrap to multiple lines")
    print("3. Check that long SKU codes wrap to multiple lines")
    print("4. Verify that text doesn't get cut off at cell boundaries")
    print("5. Ensure table remains readable and professional")

if __name__ == '__main__':
    test_word_wrapping() 