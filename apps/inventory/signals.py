from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import InventoryItem, InventoryCategory

@receiver(post_save, sender=InventoryItem)
def auto_assign_category(sender, instance, created, **kwargs):
    """
    Automatically assign a category to inventory items when they are created
    """
    if created and instance.user:
        # Check if item already has a category
        if 'category' not in instance.data or not instance.data['category']:
            # Get user's categories
            user_categories = InventoryCategory.objects.filter(user=instance.user)
            
            if user_categories.exists():
                # Create a mapping of common product names to categories
                item_category_mapping = {
                    'Motor Spare parts': 'Accessories',
                    'TV set': 'Electronics', 
                    'Smoked Glass': 'Furniture',
                    'TEST ITEM': 'Office Supplies',
                    'Laptop': 'Electronics',
                    'Smartphone': 'Electronics',
                    'T-Shirt': 'Clothing',
                    'Jeans': 'Clothing',
                    'Book': 'Books',
                    'Programming Book': 'Books',
                    'Printer Paper': 'Office Supplies',
                    'Office Chair': 'Furniture'
                }
                
                # Find a suitable category for this item
                suggested_category = item_category_mapping.get(instance.product_name, 'Office Supplies')
                
                # Check if the suggested category exists
                category_exists = user_categories.filter(name=suggested_category).exists()
                if category_exists:
                    # Update the item's data with the category
                    instance.data['category'] = suggested_category
                    instance.save(update_fields=['data'])
                else:
                    # Use the first available category
                    first_category = user_categories.first()
                    if first_category:
                        instance.data['category'] = first_category.name
                        instance.save(update_fields=['data'])

@receiver(post_save, sender=InventoryItem)
def clear_inventory_cache(sender, instance, **kwargs):
    """
    Clear cache when inventory items are updated to ensure fresh data across all views
    """
    try:
        # Clear various cache keys that might be used across different views
        cache_keys_to_clear = [
            f'inventory_item_{instance.id}',
            f'inventory_user_{instance.user.id}',
            f'inventory_layout_{instance.layout.id}',
            f'inventory_status_{instance.status.id}',
            f'inventory_category_{instance.data.get("category", "")}',
            'inventory_list_cache',
            'inventory_dashboard_cache',
            'inventory_export_cache',
        ]
        
        for key in cache_keys_to_clear:
            cache.delete(key)
        
        print(f"🧹 Cleared cache for inventory item {instance.id}: {instance.product_name}")
        
    except Exception as e:
        print(f"⚠️ Error clearing cache for item {instance.id}: {str(e)}")

@receiver(post_delete, sender=InventoryItem)
def clear_cache_on_delete(sender, instance, **kwargs):
    """
    Clear cache when inventory items are deleted
    """
    try:
        # Clear cache for the deleted item
        cache_keys_to_clear = [
            f'inventory_item_{instance.id}',
            f'inventory_user_{instance.user.id}',
            f'inventory_layout_{instance.layout.id}',
            f'inventory_status_{instance.status.id}',
            f'inventory_category_{instance.data.get("category", "")}',
        ]
        
        for key in cache_keys_to_clear:
            cache.delete(key)
        
        print(f"🧹 Cleared cache for deleted inventory item {instance.id}")
        
    except Exception as e:
        print(f"⚠️ Error clearing cache for deleted item {instance.id}: {str(e)}") 