from django.core.management.base import BaseCommand
from apps.inventory.models import InventoryItem


class Command(BaseCommand):
    help = 'Fix inventory items that are missing data fields'

    def add_arguments(self, parser):
        parser.add_argument('--item-id', type=int, help='Fix specific item ID')
        parser.add_argument('--all', action='store_true', help='Fix all items')

    def handle(self, *args, **options):
        item_id = options.get('item_id')
        fix_all = options.get('all')
        
        if item_id:
            items = InventoryItem.objects.filter(pk=item_id)
            self.stdout.write(f'Fixing item {item_id}...')
        elif fix_all:
            items = InventoryItem.objects.all()
            self.stdout.write('Fixing all items...')
        else:
            self.stdout.write('Please specify --item-id or --all')
            return
        
        fixed_count = 0
        
        for item in items:
            try:
                # Check if item is missing essential fields
                data_updated = False
                current_data = item.data.copy()
                
                # Ensure all required fields are present
                required_fields = {
                    'quantity': 0.0,
                    'unit_price': 0.0,
                    'supplier': '',
                    'location': '',
                    'description': '',
                    'notes': '',
                    'minimum_threshold': 0.0,
                }
                
                for field, default_value in required_fields.items():
                    if field not in current_data or current_data[field] is None:
                        current_data[field] = default_value
                        data_updated = True
                        self.stdout.write(f'  Added missing field {field} to item {item.id}')
                
                # Update the item if data was changed
                if data_updated:
                    item.data = current_data
                    item.save()
                    
                    # Trigger calculations and document updates
                    if hasattr(item, 'calculate_totals'):
                        item.calculate_totals()
                    
                    if hasattr(item, 'update_all_documents'):
                        item.update_all_documents()
                    
                    fixed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Fixed item {item.id}: {item.product_name}'
                        )
                    )
                else:
                    self.stdout.write(
                        f'ℹ️ Item {item.id}: {item.product_name} - No fixes needed'
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error fixing item {item.id}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Successfully fixed {fixed_count} items!'
            )
        ) 