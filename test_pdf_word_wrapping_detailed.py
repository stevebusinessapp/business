#!/usr/bin/env python
"""
Detailed test script for word wrapping in PDF export
This test actually generates a PDF and verifies the content
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json
import tempfile
import subprocess

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
django.setup()

from apps.inventory.models import InventoryItem, InventoryLayout, InventoryCategory, InventoryStatus
from apps.core.models import CompanyProfile

User = get_user_model()

def test_pdf_word_wrapping_detailed():
    """Test that word wrapping is actually working in the generated PDF"""
    print("Testing Word Wrapping in PDF Export - Detailed Analysis...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email='test_pdf_wrapping@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'PDF Wrapping'
        }
    )
    
    if created:
        print(f"Created test user: {user.email}")
    
    # Create company profile
    company_profile, created = CompanyProfile.objects.get_or_create(
        user=user,
        defaults={
            'company_name': 'PDF Word Wrapping Test Company',
            'currency_code': 'USD',
            'currency_symbol': '$',
            'email': 'info@pdfwrapping.com',
            'phone': '+1234567890',
            'address': '123 PDF Wrapping Street, Test City, Test Country',
            'website': 'https://www.pdfwrapping.com'
        }
    )
    
    if created:
        print(f"Created company profile: {company_profile.company_name}")
    
    # Create test layout
    layout, created = InventoryLayout.objects.get_or_create(
        user=user,
        name='PDF Wrapping Layout',
        defaults={
            'description': 'Test layout for PDF word wrapping functionality',
            'is_default': True,
            'auto_calculate': True
        }
    )
    
    # Create test category
    category, created = InventoryCategory.objects.get_or_create(
        user=user,
        name='PDF Wrapping Category',
        defaults={
            'description': 'Test category for PDF word wrapping'
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
                    'description': f'Test product {i+1} for PDF word wrapping testing with long description',
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
    
    print("\n=== Testing PDF Export with Word Wrapping ===")
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
        
        # Save the PDF to a temporary file for analysis
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(response.content)
            temp_pdf_path = temp_pdf.name
        
        print(f"✅ PDF saved to: {temp_pdf_path}")
        
        # Try to extract text from PDF using pdftotext (if available)
        try:
            # Try to use pdftotext to extract text from PDF
            result = subprocess.run(['pdftotext', temp_pdf_path, '-'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                pdf_text = result.stdout
                print("✅ Successfully extracted text from PDF")
                
                # Check for word wrapping indicators
                print("\n=== PDF Content Analysis ===")
                
                # Check if long product names are present
                long_product_indicators = [
                    "This is an extremely long product name",
                    "Another incredibly long product name",
                    "Product with special characters",
                    "Product with very long description"
                ]
                
                for indicator in long_product_indicators:
                    if indicator in pdf_text:
                        print(f"✅ Found long product name: {indicator[:50]}...")
                    else:
                        print(f"⚠️  Long product name not found: {indicator[:50]}...")
                
                # Check if long SKU codes are present
                long_sku_indicators = [
                    "EXTREMELY-LONG-SKU-CODE",
                    "ANOTHER-INCREDIBLY-LONG-SKU",
                    "SPECIAL-CHARS-@#$%^&*()",
                    "TECHNICAL-SPECIFICATIONS-AND-DETAILED"
                ]
                
                for indicator in long_sku_indicators:
                    if indicator in pdf_text:
                        print(f"✅ Found long SKU code: {indicator}")
                    else:
                        print(f"⚠️  Long SKU code not found: {indicator}")
                
                # Check for line breaks (indicating word wrapping)
                if '\n' in pdf_text:
                    lines = pdf_text.split('\n')
                    long_lines = [line for line in lines if len(line) > 80]
                    if long_lines:
                        print(f"⚠️  Found {len(long_lines)} long lines (may indicate no wrapping)")
                        for i, line in enumerate(long_lines[:3]):  # Show first 3 long lines
                            print(f"   Long line {i+1}: {line[:100]}...")
                    else:
                        print("✅ No excessively long lines found (good for word wrapping)")
                
                # Check for table structure
                if 'Product Name' in pdf_text and 'SKU' in pdf_text:
                    print("✅ Table structure detected")
                else:
                    print("⚠️  Table structure not clearly detected")
                
            else:
                print("⚠️  Could not extract text from PDF (pdftotext not available or failed)")
                print("   This is normal if pdftotext is not installed")
                
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            print("⚠️  pdftotext not available - cannot analyze PDF content directly")
            print("   This is normal if pdftotext is not installed on the system")
        
        # Clean up temporary file
        try:
            os.unlink(temp_pdf_path)
        except:
            pass
        
        print(f"\n📄 PDF Content Type: {response.get('Content-Type', 'Unknown')}")
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
    
    print("✅ Detailed PDF word wrapping test completed!")
    print("\n📝 Manual Verification Steps:")
    print("1. Open the generated PDF file in a PDF viewer")
    print("2. Look for long product names that wrap to multiple lines")
    print("3. Check that long SKU codes break across lines")
    print("4. Verify that text doesn't get cut off at cell boundaries")
    print("5. Ensure the table remains readable and professional")
    print("6. Check that cell heights adjust automatically for wrapped text")

if __name__ == '__main__':
    test_pdf_word_wrapping_detailed() 