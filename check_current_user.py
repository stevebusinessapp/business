import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
django.setup()

from apps.inventory.models import InventoryCategory, InventoryItem
from apps.core.models import CompanyProfile
from django.contrib.auth import get_user_model

User = get_user_model()

try:
    # Get all users
    users = User.objects.all()
    print(f"Total users in system: {users.count()}")
    
    for user in users:
        print(f"\nUser: {user.email}")
        print(f"  First Name: {user.first_name}")
        print(f"  Last Name: {user.last_name}")
        print(f"  Is Staff: {user.is_staff}")
        print(f"  Is Superuser: {user.is_superuser}")
        
        # Check if user has company profile
        try:
            company_profile = user.company_profile
            print(f"  Company Profile: {company_profile.company_name}")
            print(f"  Currency: {company_profile.currency_code} ({company_profile.currency_symbol})")
        except:
            print(f"  Company Profile: None")
        
        # Check categories
        categories = InventoryCategory.objects.filter(user=user)
        print(f"  Categories: {categories.count()}")
        for cat in categories:
            print(f"    - {cat.name}")
        
        # Check inventory items
        items = InventoryItem.objects.filter(user=user)
        print(f"  Inventory Items: {items.count()}")
        for item in items:
            print(f"    - {item.product_name}")
        
        print("-" * 50)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 