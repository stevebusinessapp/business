from django.core.management.base import BaseCommand
from apps.inventory.models import InventoryLayout


class Command(BaseCommand):
    help = 'Add serial number column to existing inventory layouts'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        updated_count = 0
        
        for layout in InventoryLayout.objects.all():
            current_columns = layout.columns
            
            # Check if serial number column already exists
            has_serial = any(col.get('name') == 'serial_number' for col in current_columns)
            
            if not has_serial:
                # Add serial number column at the beginning
                serial_column = {
                    'name': 'serial_number',
                    'display_name': 'S/N',
                    'field_type': 'serial',
                    'is_required': False,
                    'is_editable': False,
                    'width': '60px',
                    'sortable': False,
                    'searchable': False,
                    'is_auto_numbered': True
                }
                
                new_columns = [serial_column] + current_columns
                
                if dry_run:
                    self.stdout.write(f'Would update layout "{layout.name}" (ID: {layout.id})')
                    self.stdout.write(f'  Current columns: {len(current_columns)}')
                    self.stdout.write(f'  New columns: {len(new_columns)}')
                else:
                    layout.columns = new_columns
                    layout.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated layout "{layout.name}" (ID: {layout.id})'
                        )
                    )
            else:
                if dry_run:
                    self.stdout.write(f'Layout "{layout.name}" (ID: {layout.id}) already has serial number column')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would update {updated_count} layouts with serial number columns'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} layouts with serial number columns'
                )
            ) 