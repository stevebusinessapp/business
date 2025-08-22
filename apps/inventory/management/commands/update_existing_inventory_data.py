from django.core.management.base import BaseCommand
from apps.inventory.models import InventoryItem


class Command(BaseCommand):
    help = 'Update existing inventory items with default values for missing fields'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        items = InventoryItem.objects.all()
        updated_count = 0
        
        for item in items:
            data_updated = False
            current_data = item.data.copy()
            
            # Check and add missing fields with default values
            if 'category' not in current_data:
                current_data['category'] = None
                data_updated = True
                self.stdout.write(f'Would add category field for item {item.id}: {item.product_name}')
            
            if 'supplier' not in current_data:
                current_data['supplier'] = None
                data_updated = True
                self.stdout.write(f'Would add supplier field for item {item.id}: {item.product_name}')
            
            if 'description' not in current_data:
                current_data['description'] = None
                data_updated = True
                self.stdout.write(f'Would add description field for item {item.id}: {item.product_name}')
            
            if 'location' not in current_data:
                current_data['location'] = None
                data_updated = True
                self.stdout.write(f'Would add location field for item {item.id}: {item.product_name}')
            
            if 'minimum_threshold' not in current_data:
                current_data['minimum_threshold'] = None
                data_updated = True
                self.stdout.write(f'Would add minimum_threshold field for item {item.id}: {item.product_name}')
            
            if 'expiry_date' not in current_data:
                current_data['expiry_date'] = None
                data_updated = True
                self.stdout.write(f'Would add expiry_date field for item {item.id}: {item.product_name}')
            
            if 'notes' not in current_data:
                current_data['notes'] = None
                data_updated = True
                self.stdout.write(f'Would add notes field for item {item.id}: {item.product_name}')
            
            # Update the item if changes were made
            if data_updated and not dry_run:
                item.data = current_data
                item.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated item {item.id}: {item.product_name}'
                    )
                )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would update {updated_count} items'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} items'
                )
            ) 