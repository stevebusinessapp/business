from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import CompanyProfile
from apps.accounting.models import Ledger, Transaction
from decimal import Decimal
from datetime import datetime, date

User = get_user_model()

class Command(BaseCommand):
    help = 'Test ledger display with serial numbers and currency'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Ledger Display with Serial Numbers and Currency'))
        
        # Get or create a test user and company
        user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            self.stdout.write(f'Created test user: {user.username}')
        
        company, created = CompanyProfile.objects.get_or_create(
            user=user,
            defaults={
                'company_name': 'Test Company Ltd',
                'email': 'company@example.com',
                'phone': '+1234567890',
                'address': '123 Test Street, Test City',
                'currency_symbol': '₦',
                'currency_code': 'NGN'
            }
        )
        
        if created:
            self.stdout.write(f'Created test company: {company.company_name}')
        
        # Create some test transactions for the current year
        current_year = datetime.now().year
        
        # Create transactions for different months
        test_transactions = [
            # January
            {'month': 1, 'type': 'income', 'title': 'Sales Revenue', 'amount': 50000},
            {'month': 1, 'type': 'expense', 'title': 'Office Rent', 'amount': 15000},
            {'month': 1, 'type': 'expense', 'title': 'Utilities', 'amount': 5000},
            
            # February
            {'month': 2, 'type': 'income', 'title': 'Consulting Fees', 'amount': 75000},
            {'month': 2, 'type': 'expense', 'title': 'Salaries', 'amount': 30000},
            {'month': 2, 'type': 'expense', 'title': 'Marketing', 'amount': 10000},
            
            # March
            {'month': 3, 'type': 'income', 'title': 'Product Sales', 'amount': 120000},
            {'month': 3, 'type': 'expense', 'title': 'Inventory', 'amount': 60000},
            {'month': 3, 'type': 'expense', 'title': 'Shipping', 'amount': 8000},
        ]
        
        for trans_data in test_transactions:
            transaction_date = date(current_year, trans_data['month'], 15)
            
            transaction, created = Transaction.objects.get_or_create(
                user=user,
                company=company,
                title=trans_data['title'],
                type=trans_data['type'],
                amount=Decimal(trans_data['amount']),
                transaction_date=transaction_date,
                defaults={
                    'currency': '₦',
                    'net_amount': Decimal(trans_data['amount']),
                    'source_app': 'manual'
                }
            )
            
            if created:
                self.stdout.write(f'Created transaction: {transaction.title} - {transaction.currency} {transaction.amount}')
        
        # Sync ledgers from transactions
        from apps.accounting.views import sync_ledgers_from_transactions
        sync_ledgers_from_transactions(company)
        
        # Display ledger information
        ledgers = Ledger.objects.filter(company=company, year=current_year).order_by('month')
        
        # Add currency information to ledgers
        for ledger in ledgers:
            ledger.currency_symbol = company.currency_symbol
        
        self.stdout.write(self.style.SUCCESS(f'\nLedger Summary for {current_year}:'))
        self.stdout.write('=' * 80)
        self.stdout.write(f"{'S/N':<4} {'Month':<12} {'Income':<15} {'Expense':<15} {'Net Profit':<15} {'Currency'}")
        self.stdout.write('-' * 80)
        
        # Get currency code for display
        from apps.accounting.views import get_currency_display
        currency_code = get_currency_display(company.currency_symbol)
        
        for index, ledger in enumerate(ledgers, 1):
            self.stdout.write(
                f"{index:<4} {ledger.month_name:<12} "
                f"{currency_code} {ledger.total_income:<12} "
                f"{currency_code} {ledger.total_expense:<12} "
                f"{currency_code} {ledger.net_profit:<12} "
                f"{currency_code}"
            )
        
        # Calculate yearly totals
        yearly_income = sum(ledger.total_income for ledger in ledgers)
        yearly_expense = sum(ledger.total_expense for ledger in ledgers)
        yearly_profit = sum(ledger.net_profit for ledger in ledgers)
        
        self.stdout.write('-' * 80)
        self.stdout.write(
            f"{'TOTAL':<4} {'YEAR':<12} "
            f"{currency_code} {yearly_income:<12} "
            f"{currency_code} {yearly_expense:<12} "
            f"{currency_code} {yearly_profit:<12} "
            f"{currency_code}"
        )
        
        self.stdout.write(self.style.SUCCESS('\nTest completed successfully!'))
        self.stdout.write(f'You can now visit http://127.0.0.1:8000/accounting/ledger/ to see the updated table with serial numbers and currency.') 