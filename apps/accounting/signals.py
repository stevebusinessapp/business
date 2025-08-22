from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Transaction
from apps.invoices.models import Invoice
from apps.receipts.models import Receipt
from apps.job_orders.models import JobOrder
from apps.waybills.models import Waybill
# from apps.expenses.models import Expense  # Commented out until Expense model is created
from decimal import Decimal

User = get_user_model()


@receiver(post_save, sender=Invoice)
def sync_invoice_to_accounting(sender, instance, created, **kwargs):
    """Sync invoice payments to accounting transactions"""
    if instance.status == 'paid' and instance.grand_total > 0:
        # Check if transaction already exists
        existing_transaction = Transaction.objects.filter(
            source_app='invoice',
            reference_id=str(instance.id)
        ).first()
        
        if not existing_transaction:
            # Create income transaction for paid invoice
            Transaction.objects.create(
                user=instance.user,
                company=instance.user.company_profile,
                type='income',
                title=f"Invoice Payment - {instance.invoice_number}",
                description=f"Payment for invoice {instance.invoice_number} from {instance.client_name}",
                amount=instance.grand_total,
                currency=instance.user.company_profile.currency_symbol,
                tax=instance.total_tax,
                discount=instance.total_discount,
                source_app='invoice',
                reference_id=str(instance.id),
                reference_model='Invoice',
                transaction_date=instance.updated_at.date(),
                notes=f"Auto-synced from paid invoice {instance.invoice_number}"
            )


@receiver(post_save, sender=Receipt)
def sync_receipt_to_accounting(sender, instance, created, **kwargs):
    """Sync receipt payments to accounting transactions"""
    if created and instance.amount_received > 0:
        # Check if transaction already exists
        existing_transaction = Transaction.objects.filter(
            source_app='receipt',
            reference_id=str(instance.id)
        ).first()
        
        if not existing_transaction:
            # Create income transaction for receipt
            Transaction.objects.create(
                user=instance.created_by,
                company=instance.created_by.company_profile,
                type='income',
                title=f"Receipt Payment - {instance.receipt_no}",
                description=f"Payment receipt {instance.receipt_no} from {instance.client_name}",
                amount=instance.amount_received,
                currency=instance.created_by.company_profile.currency_symbol,
                source_app='receipt',
                reference_id=str(instance.id),
                reference_model='Receipt',
                transaction_date=instance.date_received,
                notes=f"Auto-synced from receipt {instance.receipt_no}"
            )


@receiver(post_save, sender=JobOrder)
def sync_job_order_to_accounting(sender, instance, created, **kwargs):
    """Sync job order costs to accounting transactions"""
    if instance.status == 'completed' and instance.total_cost > 0:
        # Check if transaction already exists
        existing_transaction = Transaction.objects.filter(
            source_app='job_order',
            reference_id=str(instance.id)
        ).first()
        
        if not existing_transaction:
            # Create expense transaction for job order costs
            Transaction.objects.create(
                user=instance.created_by,
                company=instance.created_by.company_profile,
                type='expense',
                title=f"Job Order Cost - {instance.job_number}",
                description=f"Cost for completed job order {instance.job_number}",
                amount=instance.total_cost,
                currency=instance.created_by.company_profile.currency_symbol,
                source_app='job_order',
                reference_id=str(instance.id),
                reference_model='JobOrder',
                transaction_date=instance.completed_date or instance.created_at.date(),
                notes=f"Auto-synced from completed job order {instance.job_number}"
            )


@receiver(post_save, sender=Waybill)
def sync_waybill_to_accounting(sender, instance, created, **kwargs):
    """Sync waybill charges to accounting transactions"""
    if instance.status == 'delivered' and instance.total_amount > 0:
        # Check if transaction already exists
        existing_transaction = Transaction.objects.filter(
            source_app='waybill',
            reference_id=str(instance.id)
        ).first()
        
        if not existing_transaction:
            # Create income transaction for waybill charges
            Transaction.objects.create(
                user=instance.created_by,
                company=instance.created_by.company_profile,
                type='income',
                title=f"Waybill Charges - {instance.waybill_number}",
                description=f"Charges for delivered waybill {instance.waybill_number}",
                amount=instance.total_amount,
                currency=instance.created_by.company_profile.currency_symbol,
                source_app='waybill',
                reference_id=str(instance.id),
                reference_model='Waybill',
                transaction_date=instance.delivery_date or instance.created_at.date(),
                notes=f"Auto-synced from delivered waybill {instance.waybill_number}"
            )


# @receiver(post_save, sender=Expense)
# def sync_expense_to_accounting(sender, instance, created, **kwargs):
#     """Sync manual expenses to accounting transactions"""
#     if created and instance.amount > 0:
#         # Check if transaction already exists
#         existing_transaction = Transaction.objects.filter(
#             source_app='expense',
#             reference_id=str(instance.id)
#         ).first()
#         
#         if not existing_transaction:
#             # Create expense transaction
#             Transaction.objects.create(
#                 user=instance.created_by,
#                 company=instance.created_by.company_profile,
#                 type='expense',
#                 title=f"Expense - {instance.title}",
#                 description=instance.description,
#                 amount=instance.amount,
#                 currency=instance.created_by.company_profile.currency_symbol,
#                 source_app='expense',
#                 reference_id=str(instance.id),
#                 reference_model='Expense',
#                 transaction_date=instance.expense_date,
#                 notes=f"Auto-synced from expense entry"
#             )


@receiver(post_delete, sender=Transaction)
def handle_transaction_deletion(sender, instance, **kwargs):
    """Handle transaction deletion by updating ledgers"""
    if not instance.is_void:
        # Update the ledger for the deleted transaction's month/year
        from .models import Ledger
        
        ledger = Ledger.objects.filter(
            company=instance.company,
            year=instance.transaction_date.year,
            month=instance.transaction_date.month
        ).first()
        
        if ledger:
            # Recalculate totals for this month
            transactions = Transaction.objects.filter(
                company=instance.company,
                transaction_date__year=instance.transaction_date.year,
                transaction_date__month=instance.transaction_date.month,
                is_void=False
            )
            
            from django.db.models import Sum
            
            ledger.total_income = transactions.filter(type='income').aggregate(
                total=Sum('net_amount')
            )['total'] or 0
            
            ledger.total_expense = transactions.filter(type='expense').aggregate(
                total=Sum('net_amount')
            )['total'] or 0
            
            ledger.net_profit = ledger.total_income - ledger.total_expense
            ledger.save()


# Import signals when the app is ready
def ready():
    import apps.accounting.signals 