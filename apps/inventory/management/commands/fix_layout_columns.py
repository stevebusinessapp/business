from django.core.management.base import BaseCommand
from apps.inventory.models import InventoryLayout

class Command(BaseCommand):
    help = 'Fix InventoryLayout columns: rename field key to name if needed.'

    def handle(self, *args, **options):
        layouts = InventoryLayout.objects.all()
        fixed_count = 0
        for layout in layouts:
            changed = False
            columns = layout.columns
            if isinstance(columns, list):
                for col in columns:
                    if isinstance(col, dict) and 'field' in col and 'name' not in col:
                        col['name'] = col['field']
                        del col['field']
                        changed = True
            if changed:
                layout.columns = columns
                layout.save()
                fixed_count += 1
        self.stdout.write(self.style.SUCCESS(f'Fixed {fixed_count} layouts.')) 