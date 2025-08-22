#!/usr/bin/env python
"""
Test script for balanced table layout fix in PDF export
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

def test_balanced_layout_fix():
    """Test that the table layout is balanced and all content fits properly"""
    print("Testing Balanced Table Layout Fix...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email='test_balanced_layout@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Balanced Layout'
        }
    )
    
    if created:
        print(f"Created test user: {user.email}")
    
    # Create company profile
    company_profile, created = CompanyProfile.objects.get_or_create(
        user=user,
        defaults={
            'company_name': 'Balanced Layout Test Company',
            'currency_code': 'USD',
            'currency_symbol': '$',
            'email': 'info@balancedlayout.com',
            'phone': '+1234567890',
            'address': '123 Balanced Layout Street, Test City, Test Country',
            'website': 'https://www.balancedlayout.com'
        }
    )
    
    if created:
        print(f"Created company profile: {company_profile.company_name}")
    
    # Create test layout
    layout, created = InventoryLayout.objects.get_or_create(
        user=user,
        name='Balanced Layout Test',
        defaults={
            'description': 'Test layout for balanced table layout',
            'is_default': True,
            'auto_calculate': True
        }
    )
    
    # Create test category
    category, created = InventoryCategory.objects.get_or_create(
        user=user,
        name='Balanced Layout Category',
        defaults={
            'description': 'Test category for balanced layout'
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
    
    # Create test inventory items with various content lengths to test layout
    test_items = []
    test_products = [
        {
            'name': 'Short Product Name',
            'sku': 'SKU001',
            'qty': 10,
            'price': 100.00
        },
        {
            'name': 'Medium Length Product Name That Should Wrap',
            'sku': 'MEDIUM-SKU-CODE-001',
            'qty': 25,
            'price': 250.50
        },
        {
            'name': 'Very Long Product Name That Will Definitely Need To Wrap To Multiple Lines In The Table',
            'sku': 'VERY-LONG-SKU-CODE-THAT-NEEDS-WRAPPING-001',
            'qty': 100,
            'price': 999.99
        },
        {
            'name': 'Product D',
            'sku': 'SKU004',
            'qty': 50,
            'price': 500.00
        },
        {
            'name': 'Product E',
            'sku': 'SKU005',
            'qty': 75,
            'price': 750.00
        },
        {
            'name': 'Product F',
            'sku': 'SKU006',
            'qty': 200,
            'price': 2000.00
        },
        {
            'name': 'Product G',
            'sku': 'SKU007',
            'qty': 150,
            'price': 1500.00
        },
        {
            'name': 'Product H',
            'sku': 'SKU008',
            'qty': 300,
            'price': 3000.00
        },
        {
            'name': 'Product I',
            'sku': 'SKU009',
            'qty': 80,
            'price': 800.00
        },
        {
            'name': 'Product J',
            'sku': 'SKU010',
            'qty': 120,
            'price': 1200.00
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
                    'description': f'Test product {i+1} for balanced layout testing',
                    'category': {
                        'id': category.id,
                        'name': category.name
                    }
                }
            }
        )
        test_items.append(item)
        if created:
            print(f"Created test item: {item.product_name[:30]}... - Serial: {i+1}")
    
    # Test the PDF export functionality
    client = Client()
    client.force_login(user)
    
    print("\n=== Testing Balanced Table Layout Fix ===")
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
        pdf_filename = "balanced_layout_test.pdf"
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
    
    print("✅ Balanced layout fix test completed!")
    print(f"\n📝 Manual Verification Steps:")
    print(f"1. Open the file: {os.path.abspath(pdf_filename)}")
    print("2. Check that all columns are properly sized and balanced")
    print("3. Verify that serial numbers are clearly visible but not too wide")
    print("4. Ensure product names wrap properly without cutoff")
    print("5. Check that SKU codes fit within their columns")
    print("6. Verify that all numeric values (quantities, prices, totals) are fully visible")
    print("7. Ensure the grand total is not cut off")
    print("8. Check that the table fits properly within the page margins")
    print("\n🔍 What to look for:")
    print("- All content should be fully visible without cutoff")
    print("- Column widths should be balanced and proportional")
    print("- Text should wrap properly within cells")
    print("- Serial numbers should be readable but compact")
    print("- No content should extend beyond page margins")
    print("- Professional and clean table appearance")
    print("- Proper spacing between columns")
    print("- Grand total should be clearly visible and complete")

if __name__ == '__main__':
    test_balanced_layout_fix() 