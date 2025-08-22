import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
django.setup()

from apps.inventory.models import InventoryCategory, InventoryItem, InventoryLayout, InventoryStatus
from apps.core.models import CompanyProfile
from django.contrib.auth import get_user_model

User = get_user_model()

try:
    # Get steve's user (using the correct email)
    user = User.objects.get(email='steve@gmail.com')
    print(f"Working with user: {user.email}")
    
    # Get steve's categories
    categories = InventoryCategory.objects.filter(user=user)
    print(f"\nSteve's categories ({categories.count()}):")
    for cat in categories:
        print(f"  - {cat.name}")
    
    # Get steve's inventory items
    items = InventoryItem.objects.filter(user=user)
    print(f"\nSteve's inventory items ({items.count()}):")
    for item in items:
        print(f"  - {item.product_name}: data={item.data}")
    
    # Check which items have category data
    print(f"\n=== CHECKING CATEGORY ASSOCIATIONS ===")
    for item in items:
        if 'category' in item.data:
            print(f"✓ {item.product_name} has category: {item.data['category']}")
        else:
            print(f"✗ {item.product_name} has NO category")
    
    # Get or create default layout and status for steve
    layout, created = InventoryLayout.objects.get_or_create(
        user=user,
        is_default=True,
        defaults={
            'name': 'Default Layout',
            'columns': InventoryLayout().get_default_columns()
        }
    )
    
    status, created = InventoryStatus.objects.get_or_create(
        name='in_stock',
        defaults={
            'display_name': 'In Stock',
            'color': '#28a745'
        }
    )
    
    # Assign categories to items that don't have them
    print(f"\n=== ASSIGNING CATEGORIES TO ITEMS ===")
    
    # Create a mapping of items to categories based on the actual data
    item_category_mapping = {
        'Motor Spare parts': 'Accessories',
        'TV set': 'Electronics', 
        'Smoked Glass': 'Furniture',
        'TEST ITEM': 'Office Supplies'
    }
    
    for item in items:
        if 'category' not in item.data or not item.data['category']:
            # Find a suitable category for this item
            suggested_category = item_category_mapping.get(item.product_name, 'Office Supplies')
            
            # Check if the suggested category exists
            category_exists = categories.filter(name=suggested_category).exists()
            if category_exists:
                # Update the item's data with the category
                item.data['category'] = suggested_category
                item.save()
                print(f"✓ Assigned '{suggested_category}' to '{item.product_name}'")
            else:
                # Use the first available category
                first_category = categories.first()
                if first_category:
                    item.data['category'] = first_category.name
                    item.save()
                    print(f"✓ Assigned '{first_category.name}' to '{item.product_name}' (fallback)")
    
    # Now test the category calculations
    print(f"\n=== TESTING CATEGORY CALCULATIONS ===")
    for category in categories:
        category_items = InventoryItem.objects.filter(
            user=user,
            data__category=category.name
        )
        
        product_count = category_items.count()
        total_value = sum(item.total_value for item in category_items)
        
        print(f"\nCategory: {category.name}")
        print(f"  Products: {product_count}")
        print(f"  Total Value: ₦{total_value:,.2f}")
        
        for item in category_items:
            print(f"    - {item.product_name}: ₦{item.total_value:,.2f}")
    
    print(f"\n=== FIX COMPLETED ===")
    print("Now refresh your categories page to see the correct data!")
    
except User.DoesNotExist:
    print("User steve@gmail.com not found")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 