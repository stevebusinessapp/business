from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class Transaction(models.Model):
    """Main transaction model for all financial entries"""
    TRANSACTION_TYPE = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    SOURCE_APP_CHOICES = [
        ('manual', 'Manual Entry'),
        ('invoice', 'Invoice'),
        ('receipt', 'Receipt'),
        ('job_order', 'Job Order'),
        ('waybill', 'Waybill'),
        ('inventory', 'Inventory'),
        ('expense', 'Expense Tracker'),
    ]
    
    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounting_transactions')
    company = models.ForeignKey('core.CompanyProfile', on_delete=models.CASCADE, related_name='transactions')
    
    # Transaction details
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="₦")
    
    # Financial details
    tax = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    discount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Source tracking
    source_app = models.CharField(max_length=20, choices=SOURCE_APP_CHOICES, default='manual')
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    reference_model = models.CharField(max_length=50, blank=True, null=True)
    
    # Metadata
    transaction_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    
    # Status
    is_reconciled = models.BooleanField(default=False)
    is_void = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'type']),
            models.Index(fields=['company', 'transaction_date']),
            models.Index(fields=['source_app', 'reference_id']),
            models.Index(fields=['type', 'transaction_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.type}) - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        # Calculate net amount
        self.net_amount = self.amount
        if self.tax:
            self.net_amount += self.tax
        if self.discount:
            self.net_amount -= self.discount
        
        super().save(*args, **kwargs)
        
        # Update ledger
        self.update_ledger()
    
    def update_ledger(self):
        """Update the ledger for this transaction's month/year"""
        if not self.is_void:
            ledger, created = Ledger.objects.get_or_create(
                company=self.company,
                year=self.transaction_date.year,
                month=self.transaction_date.month,
                defaults={
                    'total_income': 0,
                    'total_expense': 0,
                    'net_profit': 0
                }
            )
            
            # Recalculate totals for this month
            transactions = Transaction.objects.filter(
                company=self.company,
                transaction_date__year=self.transaction_date.year,
                transaction_date__month=self.transaction_date.month,
                is_void=False
            )
            
            ledger.total_income = transactions.filter(type='income').aggregate(
                total=Sum('net_amount')
            )['total'] or 0
            
            ledger.total_expense = transactions.filter(type='expense').aggregate(
                total=Sum('net_amount')
            )['total'] or 0
            
            ledger.net_profit = ledger.total_income - ledger.total_expense
            ledger.save()


class Ledger(models.Model):
    """Monthly ledger summary for financial reporting"""
    company = models.ForeignKey('core.CompanyProfile', on_delete=models.CASCADE, related_name='ledgers')
    year = models.IntegerField()
    month = models.IntegerField()
    
    # Financial totals
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expense = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Additional metrics
    outstanding_invoices = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_receipts = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['company', 'year', 'month']
        ordering = ['-year', '-month']
        indexes = [
            models.Index(fields=['company', 'year', 'month']),
        ]
    
    def __str__(self):
        return f"{self.company.company_name} - {self.year}/{self.month:02d}"
    
    @property
    def month_name(self):
        """Get month name"""
        from datetime import datetime
        return datetime(self.year, self.month, 1).strftime('%B')
    
    def update_outstanding_amounts(self):
        """Update outstanding invoices and pending receipts"""
        from apps.invoices.models import Invoice
        from apps.receipts.models import Receipt
        
        # Outstanding invoices
        outstanding = Invoice.objects.filter(
            user=self.company.user,
            status__in=['unpaid', 'partial']
        ).aggregate(total=Sum('balance_due'))['total'] or 0
        self.outstanding_invoices = outstanding
        
        # Pending receipts (if any logic needed)
        self.pending_receipts = 0
        
        self.save()


class Account(models.Model):
    """Chart of accounts for better financial organization"""
    ACCOUNT_TYPE_CHOICES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    ]
    
    company = models.ForeignKey('core.CompanyProfile', on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Balance tracking
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['account_number']
        indexes = [
            models.Index(fields=['company', 'account_type']),
            models.Index(fields=['account_number']),
        ]
    
    def __str__(self):
        return f"{self.account_number} - {self.name}"
    
    def update_balance(self):
        """Update current balance based on transactions"""
        transactions = Transaction.objects.filter(
            company=self.company,
            is_void=False
        )
        
        # This is a simplified balance calculation
        # In a real system, you'd have proper double-entry bookkeeping
        self.current_balance = self.opening_balance
        self.save()


class FinancialReport(models.Model):
    """Generated financial reports"""
    REPORT_TYPE_CHOICES = [
        ('income_statement', 'Income Statement'),
        ('balance_sheet', 'Balance Sheet'),
        ('cash_flow', 'Cash Flow Statement'),
        ('trial_balance', 'Trial Balance'),
        ('custom', 'Custom Report'),
    ]
    
    company = models.ForeignKey('core.CompanyProfile', on_delete=models.CASCADE, related_name='financial_reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    
    # Date range
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Report data (stored as JSON)
    report_data = models.JSONField(default=dict)
    
    # File attachments
    pdf_file = models.FileField(upload_to='reports/pdf/', blank=True, null=True)
    excel_file = models.FileField(upload_to='reports/excel/', blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'report_type']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.start_date} to {self.end_date}"
