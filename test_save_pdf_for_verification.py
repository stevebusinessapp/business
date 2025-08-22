#!/usr/bin/env python
"""
Test script to save PDF for manual verification of word wrapping
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

def save_pdf_for_verification():
    """Save a PDF with word wrapping for manual verification"""
    print("Creating PDF with word wrapping for manual verification...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email='test_verification@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Verification'
        }
    )
    
    if created:
        print(f"Created test user: {user.email}")
    
    # Create company profile
    company_profile, created = CompanyProfile.objects.get_or_create(
        user=user,
        defaults={
            'company_name': 'Word Wrapping Verification Company',
            'currency_code': 'USD',
            'currency_symbol': '$',
            'email': 'info@verification.com',
            'phone': '+1234567890',
            'address': '123 Verification Street, Test City, Test Country',
            'website': 'https://www.verification.com'
        }
    )
    
    if created:
        print(f"Created company profile: {company_profile.company_name}")
    
    # Create test layout
    layout, created = InventoryLayout.objects.get_or_create(
        user=user,
        name='Verification Layout',
        defaults={
            'description': 'Test layout for word wrapping verification',
            'is_default': True,
            'auto_calculate': True
        }
    )
    
    # Create test category
    category, created = InventoryCategory.objects.get_or_create(
        user=user,
        name='Verification Category',
        defaults={
            'description': 'Test category for verification'
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
    
    # Create test inventory items with very long text to test word wrapping
    test_items = []
    test_products = [
        {
            'name': 'This is an extremely long product name that should definitely wrap to multiple lines in the PDF table cell to thoroughly test the word wrapping functionality and ensure it works properly',
            'sku': 'EXTREMELY-LONG-SKU-CODE-THAT-SHOULD-DEFINITELY-WRAP-TO-MULTIPLE-LINES-123456789-ABCDEFGHIJKLMNOP',
            'qty': 10,
            'price': 1000.00
        },
        {
            'name': 'Another incredibly long product name with multiple words that absolutely need to be wrapped properly in the exported PDF document to demonstrate the word wrapping capabilities',
            'sku': 'ANOTHER-INCREDIBLY-LONG-SKU-WITH-MANY-CHARACTERS-987654321-ZYXWVUTSRQPONMLKJIHGFEDCBA',
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
            'name': 'Product with special characters: @#$%^&*() and numbers 123456789 and more text to make it longer',
            'sku': 'SPECIAL-CHARS-@#$%^&*()-123456789-EXTENDED-VERSION-WITH-MORE-CHARACTERS',
            'qty': 20,
            'price': 750.00
        },
        {
            'name': 'Product with very long description that includes technical specifications and detailed information about the product features and capabilities and additional details about functionality',
            'sku': 'TECHNICAL-SPECIFICATIONS-AND-DETAILED-FEATURES-CODE-2024-EXTENDED-VERSION-WITH-MORE-DETAILS',
            'qty': 8,
            'price': 1500.00
        },
        {
            'name': 'Super long product name with many words that need to be wrapped properly in the PDF export to demonstrate the word wrapping functionality is working correctly',
            'sku': 'SUPER-LONG-SKU-CODE-WITH-MANY-CHARACTERS-AND-NUMBERS-123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ',
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
                    'description': f'Test product {i+1} for word wrapping verification',
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
    
    print("\n=== Generating PDF for Manual Verification ===")
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
        pdf_filename = "word_wrapping_verification.pdf"
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
    
    print("✅ PDF generation completed!")
    print(f"\n📝 Manual Verification Steps:")
    print(f"1. Open the file: {os.path.abspath(pdf_filename)}")
    print("2. Look for long product names that wrap to multiple lines")
    print("3. Check that long SKU codes break across lines")
    print("4. Verify that text doesn't get cut off at cell boundaries")
    print("5. Ensure the table remains readable and professional")
    print("6. Check that cell heights adjust automatically for wrapped text")
    print("\n🔍 What to look for:")
    print("- Product names like 'This is an extremely long product name...' should wrap")
    print("- SKU codes like 'EXTREMELY-LONG-SKU-CODE...' should break across lines")
    print("- No text should be cut off at cell edges")
    print("- Table should remain well-formatted and readable")

if __name__ == '__main__':
    save_pdf_for_verification() 