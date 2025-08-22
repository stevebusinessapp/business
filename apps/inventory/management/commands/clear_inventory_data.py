from django.core.management.base import BaseCommand
from apps.inventory.models import (
    InventoryTable, InventoryRow, InventoryProduct, InventoryCategory,
    InventoryTransaction, InventoryLog, InventoryImport, InventoryExport,
    # Legacy models
    CustomInventoryForm, CustomInventoryItem, InventoryTemplate, TemplateBasedInventory
)


class Command(BaseCommand):
    help = 'Clear all inventory-related data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to clear all inventory data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL inventory data. Use --confirm to proceed.'
                )
            )
            return

        self.stdout.write('🗑️  Clearing inventory data...')

        # Count records before deletion
        inventory_products = InventoryProduct.objects.all().count()
        inventory_categories = InventoryCategory.objects.all().count()
        inventory_tables = InventoryTable.objects.all().count()
        inventory_rows = InventoryRow.objects.all().count()
        inventory_transactions = InventoryTransaction.objects.all().count()
        inventory_logs = InventoryLog.objects.all().count()
        inventory_imports = InventoryImport.objects.all().count()
        inventory_exports = InventoryExport.objects.all().count()
        
        # Legacy models
        custom_forms = CustomInventoryForm.objects.all().count()
        custom_items = CustomInventoryItem.objects.all().count()
        inventory_templates = InventoryTemplate.objects.all().count()
        template_inventory = TemplateBasedInventory.objects.all().count()

        # Delete all inventory data
        InventoryProduct.objects.all().delete()
        InventoryCategory.objects.all().delete()
        InventoryTable.objects.all().delete()
        InventoryRow.objects.all().delete()
        InventoryTransaction.objects.all().delete()
        InventoryLog.objects.all().delete()
        InventoryImport.objects.all().delete()
        InventoryExport.objects.all().delete()
        
        # Delete legacy data
        CustomInventoryForm.objects.all().delete()
        CustomInventoryItem.objects.all().delete()
        InventoryTemplate.objects.all().delete()
        TemplateBasedInventory.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS('✅ Inventory data cleared successfully!')
        )
        self.stdout.write('Deleted:')
        self.stdout.write(f'  - {inventory_products} inventory products')
        self.stdout.write(f'  - {inventory_categories} inventory categories')
        self.stdout.write(f'  - {inventory_tables} inventory tables')
        self.stdout.write(f'  - {inventory_rows} inventory rows')
        self.stdout.write(f'  - {inventory_transactions} inventory transactions')
        self.stdout.write(f'  - {inventory_logs} inventory logs')
        self.stdout.write(f'  - {inventory_imports} inventory imports')
        self.stdout.write(f'  - {inventory_exports} inventory exports')
        self.stdout.write(f'  - {custom_forms} custom forms')
        self.stdout.write(f'  - {custom_items} custom items')
        self.stdout.write(f'  - {inventory_templates} inventory templates')
        self.stdout.write(f'  - {template_inventory} template-based inventory items')

        self.stdout.write('\nYou can now start fresh with your inventory data.') 