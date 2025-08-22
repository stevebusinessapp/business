from django.core.management.base import BaseCommand
from apps.inventory.models import (
    InventoryTable, InventoryRow, InventoryProduct, InventoryCategory,
    InventoryTransaction, InventoryLog, InventoryImport, InventoryExport,
    # Legacy models
    CustomInventoryForm, CustomInventoryItem, InventoryTemplate, TemplateBasedInventory
)
from apps.invoices.models import Invoice, InvoiceItem
from apps.receipts.models import Receipt
from apps.waybills.models import Waybill
from apps.job_orders.models import JobOrder
from apps.quotations.models import Quotation, QuotationItem
from apps.clients.models import Client
from apps.core.models import CompanyProfile, BankAccount
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Clear all data from the database across various apps'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to clear all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL data from the database. Use --confirm to proceed.'
                )
            )
            return

        self.stdout.write('🗑️  Clearing all data...')

        # Count records before deletion
        inventory_products = InventoryProduct.objects.all().count()
        inventory_categories = InventoryCategory.objects.all().count()
        inventory_tables = InventoryTable.objects.all().count()
        inventory_rows = InventoryRow.objects.all().count()
        inventory_transactions = InventoryTransaction.objects.all().count()
        inventory_logs = InventoryLog.objects.all().count()
        inventory_imports = InventoryImport.objects.all().count()
        inventory_exports = InventoryExport.objects.all().count()
        
        # Legacy inventory models
        custom_forms = CustomInventoryForm.objects.all().count()
        custom_items = CustomInventoryItem.objects.all().count()
        inventory_templates = InventoryTemplate.objects.all().count()
        template_inventory = TemplateBasedInventory.objects.all().count()
        
        # Other apps
        invoices = Invoice.objects.all().count()
        invoice_items = InvoiceItem.objects.all().count()
        receipts = Receipt.objects.all().count()
        waybills = Waybill.objects.all().count()
        job_orders = JobOrder.objects.all().count()
        quotations = Quotation.objects.all().count()
        quotation_items = QuotationItem.objects.all().count()
        clients = Client.objects.all().count()
        company_profiles = CompanyProfile.objects.all().count()
        bank_accounts = BankAccount.objects.all().count()
        
        # Count non-superuser users
        users = User.objects.filter(is_superuser=False).count()

        # Delete all data
        # Inventory
        InventoryProduct.objects.all().delete()
        InventoryCategory.objects.all().delete()
        InventoryTable.objects.all().delete()
        InventoryRow.objects.all().delete()
        InventoryTransaction.objects.all().delete()
        InventoryLog.objects.all().delete()
        InventoryImport.objects.all().delete()
        InventoryExport.objects.all().delete()
        
        # Legacy inventory
        CustomInventoryForm.objects.all().delete()
        CustomInventoryItem.objects.all().delete()
        InventoryTemplate.objects.all().delete()
        TemplateBasedInventory.objects.all().delete()
        
        # Other apps
        InvoiceItem.objects.all().delete()
        Invoice.objects.all().delete()
        Receipt.objects.all().delete()
        Waybill.objects.all().delete()
        JobOrder.objects.all().delete()
        QuotationItem.objects.all().delete()
        Quotation.objects.all().delete()
        Client.objects.all().delete()
        CompanyProfile.objects.all().delete()
        BankAccount.objects.all().delete()
        
        # Delete non-superuser users
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(
            self.style.SUCCESS('✅ All data cleared successfully!')
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
        self.stdout.write(f'  - {invoices} invoices')
        self.stdout.write(f'  - {invoice_items} invoice items')
        self.stdout.write(f'  - {receipts} receipts')
        self.stdout.write(f'  - {waybills} waybills')
        self.stdout.write(f'  - {job_orders} job orders')
        self.stdout.write(f'  - {quotations} quotations')
        self.stdout.write(f'  - {quotation_items} quotation items')
        self.stdout.write(f'  - {clients} clients')
        self.stdout.write(f'  - {company_profiles} company profiles')
        self.stdout.write(f'  - {bank_accounts} bank accounts')
        self.stdout.write(f'  - {users} non-superuser users')

        self.stdout.write('\nYou can now start fresh with your data.') 