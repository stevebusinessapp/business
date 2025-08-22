from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounting.models import Transaction
from apps.invoices.models import Invoice
from apps.receipts.models import Receipt
from apps.job_orders.models import JobOrder
from apps.waybills.models import Waybill
# from apps.expenses.models import Expense  # Commented out until Expense model is created
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Sync existing data from other apps to the accounting system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            type=str,
            help='Specific app to sync (invoices, receipts, job_orders, waybills, expenses)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sync even if transactions already exist',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting accounting data sync...')
        )

        app_to_sync = options.get('app')
        force = options.get('force')

        if app_to_sync:
            if app_to_sync == 'invoices':
                self.sync_invoices(force)
            elif app_to_sync == 'receipts':
                self.sync_receipts(force)
            elif app_to_sync == 'job_orders':
                self.sync_job_orders(force)
            elif app_to_sync == 'waybills':
                self.sync_waybills(force)
            elif app_to_sync == 'expenses':
                self.sync_expenses(force)
            else:
                self.stdout.write(
                    self.style.ERROR(f'Unknown app: {app_to_sync}')
                )
        else:
            # Sync all apps
            self.sync_invoices(force)
            self.sync_receipts(force)
            self.sync_job_orders(force)
            self.sync_waybills(force)
            # self.sync_expenses(force)  # Commented out until Expense model is created

        self.stdout.write(
            self.style.SUCCESS('Accounting data sync completed!')
        )

    def sync_invoices(self, force=False):
        """Sync paid invoices to accounting transactions"""
        self.stdout.write('Syncing invoices...')
        
        paid_invoices = Invoice.objects.filter(status='paid')
        synced_count = 0
        
        for invoice in paid_invoices:
            if not force:
                # Check if transaction already exists
                existing = Transaction.objects.filter(
                    source_app='invoice',
                    reference_id=str(invoice.id)
                ).first()
                
                if existing:
                    continue
            
            try:
                Transaction.objects.create(
                    user=invoice.user,
                    company=invoice.user.company_profile,
                    type='income',
                    title=f"Invoice Payment - {invoice.invoice_number}",
                    description=f"Payment for invoice {invoice.invoice_number} from {invoice.client_name}",
                    amount=invoice.grand_total,
                    currency=invoice.user.company_profile.currency_symbol,
                    tax=invoice.total_tax,
                    discount=invoice.total_discount,
                    source_app='invoice',
                    reference_id=str(invoice.id),
                    reference_model='Invoice',
                    transaction_date=invoice.updated_at.date(),
                    notes=f"Auto-synced from paid invoice {invoice.invoice_number}"
                )
                synced_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error syncing invoice {invoice.id}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Synced {synced_count} invoices')
        )

    def sync_receipts(self, force=False):
        """Sync receipts to accounting transactions"""
        self.stdout.write('Syncing receipts...')
        
        receipts = Receipt.objects.all()
        synced_count = 0
        
        for receipt in receipts:
            if not force:
                # Check if transaction already exists
                existing = Transaction.objects.filter(
                    source_app='receipt',
                    reference_id=str(receipt.id)
                ).first()
                
                if existing:
                    continue
            
            try:
                Transaction.objects.create(
                    user=receipt.created_by,
                    company=receipt.created_by.company_profile,
                    type='income',
                    title=f"Receipt Payment - {receipt.receipt_no}",
                    description=f"Payment receipt {receipt.receipt_no} from {receipt.client_name}",
                    amount=receipt.amount_received,
                    currency=receipt.created_by.company_profile.currency_symbol,
                    source_app='receipt',
                    reference_id=str(receipt.id),
                    reference_model='Receipt',
                    transaction_date=receipt.date_received,
                    notes=f"Auto-synced from receipt {receipt.receipt_no}"
                )
                synced_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error syncing receipt {receipt.id}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Synced {synced_count} receipts')
        )

    def sync_job_orders(self, force=False):
        """Sync completed job orders to accounting transactions"""
        self.stdout.write('Syncing job orders...')
        
        completed_jobs = JobOrder.objects.filter(status='completed')
        synced_count = 0
        
        for job in completed_jobs:
            if not force:
                # Check if transaction already exists
                existing = Transaction.objects.filter(
                    source_app='job_order',
                    reference_id=str(job.id)
                ).first()
                
                if existing:
                    continue
            
            try:
                # Get total cost from job order
                total_cost = getattr(job, 'total_cost', 0) or 0
                
                if total_cost > 0:
                    Transaction.objects.create(
                        user=job.created_by,
                        company=job.created_by.company_profile,
                        type='expense',
                        title=f"Job Order Cost - {job.job_number}",
                        description=f"Cost for completed job order {job.job_number}",
                        amount=total_cost,
                        currency=job.created_by.company_profile.currency_symbol,
                        source_app='job_order',
                        reference_id=str(job.id),
                        reference_model='JobOrder',
                        transaction_date=job.completed_date or job.created_at.date(),
                        notes=f"Auto-synced from completed job order {job.job_number}"
                    )
                    synced_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error syncing job order {job.id}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Synced {synced_count} job orders')
        )

    def sync_waybills(self, force=False):
        """Sync delivered waybills to accounting transactions"""
        self.stdout.write('Syncing waybills...')
        
        delivered_waybills = Waybill.objects.filter(status='delivered')
        synced_count = 0
        
        for waybill in delivered_waybills:
            if not force:
                # Check if transaction already exists
                existing = Transaction.objects.filter(
                    source_app='waybill',
                    reference_id=str(waybill.id)
                ).first()
                
                if existing:
                    continue
            
            try:
                # Get total amount from waybill
                total_amount = getattr(waybill, 'total_amount', 0) or 0
                
                if total_amount > 0:
                    Transaction.objects.create(
                        user=waybill.created_by,
                        company=waybill.created_by.company_profile,
                        type='income',
                        title=f"Waybill Charges - {waybill.waybill_number}",
                        description=f"Charges for delivered waybill {waybill.waybill_number}",
                        amount=total_amount,
                        currency=waybill.created_by.company_profile.currency_symbol,
                        source_app='waybill',
                        reference_id=str(waybill.id),
                        reference_model='Waybill',
                        transaction_date=waybill.delivery_date or waybill.created_at.date(),
                        notes=f"Auto-synced from delivered waybill {waybill.waybill_number}"
                    )
                    synced_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error syncing waybill {waybill.id}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Synced {synced_count} waybills')
        )

    # def sync_expenses(self, force=False):
    #     """Sync manual expenses to accounting transactions"""
    #     self.stdout.write('Syncing expenses...')
    #     
    #     expenses = Expense.objects.all()
    #     synced_count = 0
    #     
    #     for expense in expenses:
    #         if not force:
    #             # Check if transaction already exists
    #             existing = Transaction.objects.filter(
    #                 source_app='expense',
    #                 reference_id=str(expense.id)
    #             ).first()
    #             
    #             if existing:
    #                 continue
    #         
    #         try:
    #             Transaction.objects.create(
    #                 user=expense.created_by,
    #                 company=expense.created_by.company_profile,
    #                 type='expense',
    #                 title=f"Expense - {expense.title}",
    #                 description=expense.description,
    #                 amount=expense.amount,
    #                 currency=expense.created_by.company_profile.currency_symbol,
    #                 source_app='expense',
    #                 reference_id=str(expense.id),
    #                 reference_model='Expense',
    #                 transaction_date=expense.expense_date,
    #                 notes=f"Auto-synced from expense entry"
    #             )
    #             synced_count += 1
    #         except Exception as e:
    #             self.stdout.write(
    #                 self.style.WARNING(f'Error syncing expense {expense.id}: {e}')
    #             )
    #     
    #     self.stdout.write(
    #         self.style.SUCCESS(f'Synced {synced_count} expenses')
    #     ) 