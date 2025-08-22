from django.core.management.base import BaseCommand
from apps.inventory.models import InventoryItem


class Command(BaseCommand):
    help = 'Debug inventory data to see what is actually stored in the database'

    def add_arguments(self, parser):
        parser.add_argument('--item-id', type=int, help='Specific item ID to debug')

    def handle(self, *args, **options):
        if options['item_id']:
            items = InventoryItem.objects.filter(id=options['item_id'])
        else:
            items = InventoryItem.objects.all()
        
        for item in items:
            self.stdout.write(f"\n=== INVENTORY ITEM {item.id}: {item.product_name} ===")
            self.stdout.write(f"SKU: {item.sku_code}")
            self.stdout.write(f"Status: {item.status.name}")
            self.stdout.write(f"Raw data: {item.data}")
            
            # Check specific fields
            self.stdout.write(f"\n--- Field Analysis ---")
            self.stdout.write(f"Category: {item.data.get('category')}")
            self.stdout.write(f"Supplier: {item.data.get('supplier')}")
            self.stdout.write(f"Location: {item.data.get('location')}")
            self.stdout.write(f"Minimum threshold: {item.data.get('minimum_threshold')}")
            self.stdout.write(f"Description: {item.data.get('description')}")
            self.stdout.write(f"Notes: {item.data.get('notes')}")
            self.stdout.write(f"Expiry date: {item.data.get('expiry_date')}")
            self.stdout.write(f"Quantity: {item.data.get('quantity')}")
            self.stdout.write(f"Unit price: {item.data.get('unit_price')}")
            
            # Test get_value method
            self.stdout.write(f"\n--- get_value() Results ---")
            self.stdout.write(f"get_value('category'): {item.get_value('category')}")
            self.stdout.write(f"get_value('supplier'): {item.get_value('supplier')}")
            self.stdout.write(f"get_value('location'): {item.get_value('location')}")
            self.stdout.write(f"get_value('minimum_threshold'): {item.get_value('minimum_threshold')}")
            self.stdout.write(f"get_value('description'): {item.get_value('description')}")
            self.stdout.write(f"get_value('notes'): {item.get_value('notes')}")
            self.stdout.write(f"get_value('expiry_date'): {item.get_value('expiry_date')}")
            self.stdout.write(f"get_value('quantity'): {item.get_value('quantity')}")
            self.stdout.write(f"get_value('unit_price'): {item.get_value('unit_price')}")
            
            # Test properties
            self.stdout.write(f"\n--- Properties ---")
            self.stdout.write(f"item.quantity: {item.quantity}")
            self.stdout.write(f"item.unit_price: {item.unit_price}")
            self.stdout.write(f"item.total_value: {item.total_value}")
            
            self.stdout.write(f"\n{'='*50}") 