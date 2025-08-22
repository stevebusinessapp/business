from django.core.management.base import BaseCommand
from apps.inventory.models import InventoryItem


class Command(BaseCommand):
    help = 'Update all inventory items with latest calculations and ensure all documents are up to date'

    def handle(self, *args, **options):
        self.stdout.write('Starting to update all inventory calculations...')
        
        updated_count = 0
        total_count = InventoryItem.objects.count()
        
        for item in InventoryItem.objects.all():
            try:
                # Force recalculation
                item.calculate_totals()
                item.save()
                
                # Update all documents
                item.update_all_documents()
                
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated item {item.id}: {item.product_name} - '
                        f'Qty: {item.get_value("quantity")}, '
                        f'Price: ₦{item.get_value("unit_price")}, '
                        f'Total: ₦{item.total_value}'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error updating item {item.id}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} out of {total_count} inventory items'
            )
        ) 