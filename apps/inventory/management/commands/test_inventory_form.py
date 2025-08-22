from django.core.management.base import BaseCommand
from apps.inventory.models import InventoryItem, InventoryLayout, InventoryStatus, InventoryCategory
from apps.inventory.forms import InventoryItemForm
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Test the inventory form to see if all fields are being saved correctly'

    def handle(self, *args, **options):
        # Get the first user
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
            return
        
        # Get or create a layout
        layout, created = InventoryLayout.objects.get_or_create(
            user=user,
            is_default=True,
            defaults={
                'name': 'Default Layout',
                'description': 'Default inventory layout'
            }
        )
        
        # Get a status
        status = InventoryStatus.objects.filter(is_active=True).first()
        if not status:
            self.stdout.write(self.style.ERROR('No status found. Please create statuses first.'))
            return
        
        # Get a category
        category = InventoryCategory.objects.filter(user=user, is_active=True).first()
        
        # Test data
        import uuid
        unique_sku = f"TEST{uuid.uuid4().hex[:8].upper()}"
        
        test_data = {
            'product_name': 'Test Product',
            'sku_code': unique_sku,
            'status': status.id,
            'is_active': True,
            'category': category.id if category else None,
            'supplier': 'Test Supplier',
            'description': 'This is a test product description',
            'quantity_in_stock': 100.0,
            'minimum_threshold': 10.0,
            'unit_price': 25.50,
            'location': 'Warehouse A',
            'expiry_date': '2025-12-31',
            'notes': 'Test notes for this product'
        }
        
        self.stdout.write(f"Testing form with data: {test_data}")
        
        # Create form
        form = InventoryItemForm(data=test_data, user=user, layout=layout)
        
        if form.is_valid():
            self.stdout.write(self.style.SUCCESS('Form is valid!'))
            
            # Save the item
            item = form.save()
            
            self.stdout.write(f"Item saved with ID: {item.id}")
            self.stdout.write(f"Item data: {item.data}")
            
            # Check each field
            self.stdout.write("\n--- Field Check ---")
            self.stdout.write(f"Category: {item.data.get('category')}")
            self.stdout.write(f"Supplier: {item.data.get('supplier')}")
            self.stdout.write(f"Description: {item.data.get('description')}")
            self.stdout.write(f"Quantity: {item.data.get('quantity')}")
            self.stdout.write(f"Minimum threshold: {item.data.get('minimum_threshold')}")
            self.stdout.write(f"Unit price: {item.data.get('unit_price')}")
            self.stdout.write(f"Location: {item.data.get('location')}")
            self.stdout.write(f"Expiry date: {item.data.get('expiry_date')}")
            self.stdout.write(f"Notes: {item.data.get('notes')}")
            
            # Test get_value method
            self.stdout.write("\n--- get_value() Test ---")
            self.stdout.write(f"get_value('category'): {item.get_value('category')}")
            self.stdout.write(f"get_value('supplier'): {item.get_value('supplier')}")
            self.stdout.write(f"get_value('description'): {item.get_value('description')}")
            self.stdout.write(f"get_value('quantity'): {item.get_value('quantity')}")
            self.stdout.write(f"get_value('minimum_threshold'): {item.get_value('minimum_threshold')}")
            self.stdout.write(f"get_value('unit_price'): {item.get_value('unit_price')}")
            self.stdout.write(f"get_value('location'): {item.get_value('location')}")
            self.stdout.write(f"get_value('expiry_date'): {item.get_value('expiry_date')}")
            self.stdout.write(f"get_value('notes'): {item.get_value('notes')}")
            
            # Clean up
            item.delete()
            self.stdout.write(self.style.SUCCESS('Test completed successfully!'))
            
        else:
            self.stdout.write(self.style.ERROR('Form is not valid!'))
            self.stdout.write(f"Form errors: {form.errors}") 