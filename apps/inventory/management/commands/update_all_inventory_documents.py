from django.core.management.base import BaseCommand
from apps.inventory.models import InventoryItem, InventoryExport, InventoryTemplate
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Update all inventory documents, templates, and exports with latest data'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Force update even if not needed')
        parser.add_argument('--user', type=int, help='Update only for specific user ID')

    def handle(self, *args, **options):
        force = options['force']
        user_id = options['user']
        
        self.stdout.write('🔄 Starting inventory document update process...')
        
        # Get items to update
        if user_id:
            items = InventoryItem.objects.filter(user_id=user_id)
            self.stdout.write(f'Updating documents for user {user_id}...')
        else:
            items = InventoryItem.objects.all()
            self.stdout.write('Updating documents for all users...')
        
        total_items = items.count()
        updated_count = 0
        
        for item in items:
            try:
                # Force recalculation
                item.calculate_totals()
                
                # Update all documents
                item.update_all_documents()
                
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Updated item {item.id}: {item.product_name} - '
                        f'Qty: {item.get_value("quantity")}, '
                        f'Price: ₦{item.get_value("unit_price")}, '
                        f'Total: ₦{item.total_value}, '
                        f'Status: {item.status.display_name}'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error updating item {item.id}: {str(e)}'
                    )
                )
        
        # Update exports
        self.stdout.write('🔄 Updating inventory exports...')
        exports = InventoryExport.objects.all()
        for export in exports:
            try:
                export.export_settings['needs_refresh'] = True
                export.save(update_fields=['export_settings'])
                self.stdout.write(f'✅ Marked export {export.id} for refresh')
            except Exception as e:
                self.stdout.write(f'❌ Error updating export {export.id}: {str(e)}')
        
        # Update templates
        self.stdout.write('🔄 Updating inventory templates...')
        templates = InventoryTemplate.objects.all()
        for template in templates:
            try:
                template.save(update_fields=['updated_at'])
                self.stdout.write(f'✅ Updated template {template.id}: {template.name}')
            except Exception as e:
                self.stdout.write(f'❌ Error updating template {template.id}: {str(e)}')
        
        # Clear cache
        self.stdout.write('🔄 Clearing cache...')
        try:
            cache.clear()
            self.stdout.write('✅ Cache cleared successfully')
        except Exception as e:
            self.stdout.write(f'⚠️ Warning: Error clearing cache: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Successfully updated {updated_count} out of {total_items} inventory items'
            )
        )
        self.stdout.write('✅ All inventory documents, templates, and exports have been updated!') 