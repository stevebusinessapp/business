from django.core.management.base import BaseCommand
from apps.inventory.models import InventoryItem


class Command(BaseCommand):
    help = 'Debug the data stored in a specific inventory item'

    def add_arguments(self, parser):
        parser.add_argument('item_id', type=int, help='ID of the inventory item to debug')

    def handle(self, *args, **options):
        item_id = options['item_id']
        
        try:
            item = InventoryItem.objects.get(pk=item_id)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Item {item_id}: {item.product_name}\n'
                    f'Status: {item.status.name} ({item.status.display_name})\n'
                    f'Last Updated: {item.updated_at}\n'
                    f'Is Active: {item.is_active}\n'
                    f'Layout: {item.layout.name}\n'
                    f'User: {item.user.email}\n'
                )
            )
            
            # Show the raw data field
            self.stdout.write('\n📊 Raw Data Field:')
            self.stdout.write(f'Data: {item.data}')
            
            # Show individual field values
            self.stdout.write('\n📋 Individual Field Values:')
            fields_to_check = [
                'quantity', 'unit_price', 'supplier', 'location', 
                'expiry_date', 'notes', 'category', 'description', 
                'minimum_threshold'
            ]
            
            for field in fields_to_check:
                value = item.get_value(field)
                self.stdout.write(f'  {field}: {value}')
            
            # Show calculated values
            self.stdout.write('\n🧮 Calculated Values:')
            self.stdout.write(f'  quantity (property): {item.quantity}')
            self.stdout.write(f'  unit_price (property): {item.unit_price}')
            self.stdout.write(f'  total_value (property): {item.total_value}')
            
            # Show calculated data
            self.stdout.write('\n📈 Calculated Data:')
            self.stdout.write(f'Calculated Data: {item.calculated_data}')
            
        except InventoryItem.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Item with ID {item_id} does not exist')
            ) 