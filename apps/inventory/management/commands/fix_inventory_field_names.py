from django.core.management.base import BaseCommand
from apps.inventory.models import InventoryItem


class Command(BaseCommand):
    help = 'Fix inventory item field names in data JSONField'

    def handle(self, *args, **options):
        self.stdout.write('Starting to fix inventory field names...')
        
        fixed_count = 0
        total_count = InventoryItem.objects.count()
        
        for item in InventoryItem.objects.all():
            data_updated = False
            data = item.data.copy()
            
            # Fix quantity_in_stock -> quantity
            if 'quantity_in_stock' in data:
                data['quantity'] = data.pop('quantity_in_stock')
                data_updated = True
                self.stdout.write(f'Fixed quantity field for item {item.id}: {item.product_name}')
            
            # Update the data if changes were made
            if data_updated:
                item.data = data
                item.save()
                fixed_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully fixed {fixed_count} out of {total_count} inventory items'
            )
        ) 