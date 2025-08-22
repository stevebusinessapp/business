from django.core.management.base import BaseCommand
from apps.inventory.models import InventoryItem, InventoryStatus

class Command(BaseCommand):
    help = 'Check the status of a specific inventory item'

    def add_arguments(self, parser):
        parser.add_argument('item_id', type=int, help='ID of the inventory item to check')

    def handle(self, *args, **options):
        item_id = options['item_id']
        
        try:
            item = InventoryItem.objects.get(pk=item_id)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Item {item_id}: {item.product_name}\n'
                    f'Status: {item.status.name} ({item.status.display_name})\n'
                    f'Last Updated: {item.updated_at}\n'
                    f'Is Active: {item.is_active}'
                )
            )
        except InventoryItem.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Item with ID {item_id} does not exist')
            ) 