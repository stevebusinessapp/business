from django import forms
from django.contrib.auth import get_user_model
from .models import Transaction, Account, FinancialReport
from decimal import Decimal
import re

User = get_user_model()


class TransactionForm(forms.ModelForm):
    """Form for creating and editing transactions"""
    
    class Meta:
        model = Transaction
        fields = [
            'type', 'title', 'description', 'amount', 'currency', 
            'tax', 'discount', 'transaction_date', 'notes'
        ]
        widgets = {
            'transaction_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'tax': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'discount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set default currency from user's company
        if self.user and hasattr(self.user, 'company_profile'):
            self.fields['currency'].initial = self.user.company_profile.currency_symbol
    
    def clean_amount(self):
        """Clean and validate amount field"""
        amount = self.cleaned_data.get('amount')
        if amount is not None:
            # Handle currency symbols and formatting
            if isinstance(amount, str):
                # Remove currency symbols and commas
                amount = re.sub(r'[₦$€£¥,\s]', '', amount)
                try:
                    amount = Decimal(amount)
                except (ValueError, TypeError):
                    raise forms.ValidationError("Please enter a valid amount.")
            
            if amount <= 0:
                raise forms.ValidationError("Amount must be greater than zero.")
        
        return amount
    
    def clean_tax(self):
        """Clean tax field"""
        tax = self.cleaned_data.get('tax')
        if tax is not None and isinstance(tax, str):
            tax = re.sub(r'[₦$€£¥,\s]', '', tax)
            try:
                tax = Decimal(tax)
            except (ValueError, TypeError):
                raise forms.ValidationError("Please enter a valid tax amount.")
        return tax or 0
    
    def clean_discount(self):
        """Clean discount field"""
        discount = self.cleaned_data.get('discount')
        if discount is not None and isinstance(discount, str):
            discount = re.sub(r'[₦$€£¥,\s]', '', discount)
            try:
                discount = Decimal(discount)
            except (ValueError, TypeError):
                raise forms.ValidationError("Please enter a valid discount amount.")
        return discount or 0


class TransactionFilterForm(forms.Form):
    """Form for filtering transactions"""
    
    # Date range
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    # Transaction type
    transaction_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Transaction.TRANSACTION_TYPE,
        required=False
    )
    
    # Source app
    source_app = forms.ChoiceField(
        choices=[('', 'All Sources')] + Transaction.SOURCE_APP_CHOICES,
        required=False
    )
    
    # Amount range
    min_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': 'Min Amount'})
    )
    max_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': 'Max Amount'})
    )
    
    # Search
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search transactions...'})
    )
    
    # Status
    is_reconciled = forms.ChoiceField(
        choices=[('', 'All'), ('true', 'Reconciled'), ('false', 'Not Reconciled')],
        required=False
    )


class AccountForm(forms.ModelForm):
    """Form for creating and editing accounts"""
    
    class Meta:
        model = Account
        fields = ['name', 'account_number', 'account_type', 'description', 'opening_balance']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'opening_balance': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def clean_account_number(self):
        """Ensure account number is unique"""
        account_number = self.cleaned_data.get('account_number')
        if Account.objects.filter(account_number=account_number).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError("This account number is already in use.")
        return account_number


class FinancialReportForm(forms.ModelForm):
    """Form for generating financial reports"""
    
    class Meta:
        model = FinancialReport
        fields = ['report_type', 'title', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        """Validate date range"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be after end date.")
        
        return cleaned_data


class BulkTransactionForm(forms.Form):
    """Form for bulk transaction operations"""
    
    transaction_ids = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    action = forms.ChoiceField(
        choices=[
            ('reconcile', 'Mark as Reconciled'),
            ('unreconcile', 'Mark as Not Reconciled'),
            ('void', 'Void Transactions'),
            ('export', 'Export Selected'),
        ]
    )


class ReconciliationForm(forms.Form):
    """Form for bank reconciliation"""
    
    bank_statement_balance = forms.DecimalField(
        label="Bank Statement Balance",
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )
    
    reconciliation_date = forms.DateField(
        label="Reconciliation Date",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )


class ImportTransactionForm(forms.Form):
    """Form for importing transactions from CSV/Excel"""
    
    file = forms.FileField(
        label="Transaction File",
        help_text="Upload CSV or Excel file with transaction data"
    )
    
    has_header = forms.BooleanField(
        initial=True,
        required=False,
        label="File has header row"
    )
    
    date_format = forms.ChoiceField(
        choices=[
            ('%Y-%m-%d', 'YYYY-MM-DD'),
            ('%d/%m/%Y', 'DD/MM/YYYY'),
            ('%m/%d/%Y', 'MM/DD/YYYY'),
        ],
        initial='%Y-%m-%d'
    )
    
    def clean_file(self):
        """Validate uploaded file"""
        file = self.cleaned_data.get('file')
        if file:
            # Check file extension
            allowed_extensions = ['.csv', '.xlsx', '.xls']
            file_extension = file.name.lower()
            
            if not any(file_extension.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError(
                    "Please upload a valid CSV or Excel file."
                )
            
            # Check file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "File size must be less than 5MB."
                )
        
        return file
