from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import random

from apps.accounting.models import Transaction
from apps.core.models import CompanyProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample transactions for testing the accounting dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email of user to create transactions for',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of transactions to create (default: 50)',
        )

    def handle(self, *args, **options):
        email = options['email']
        count = options['count']

        if not email:
            self.stdout.write(
                self.style.ERROR('Please provide an email with --email')
            )
            return

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with email "{email}" not found')
            )
            return

        company = getattr(user, 'company_profile', None)
        if not company:
            self.stdout.write(
                self.style.ERROR(f'User with email "{email}" has no company profile')
            )
            return

        # Sample transaction data
        income_sources = [
            ('Sales Revenue', 'invoice'),
            ('Service Income', 'job_order'),
            ('Consulting Fees', 'manual'),
            ('Product Sales', 'inventory'),
            ('Freight Charges', 'waybill'),
        ]

        expense_sources = [
            ('Office Supplies', 'expense'),
            ('Utilities', 'expense'),
            ('Rent', 'expense'),
            ('Salaries', 'expense'),
            ('Marketing', 'expense'),
            ('Inventory Purchase', 'inventory'),
            ('Transportation', 'waybill'),
        ]

        # Create transactions over the last 6 months
        current_date = timezone.now()
        transactions_created = 0

        for i in range(count):
            # Random date within last 6 months
            days_ago = random.randint(0, 180)
            transaction_date = current_date - timedelta(days=days_ago)

            # Random transaction type
            is_income = random.choice([True, False])
            
            if is_income:
                title, source_app = random.choice(income_sources)
                amount = Decimal(random.randint(5000, 50000))
            else:
                title, source_app = random.choice(expense_sources)
                amount = Decimal(random.randint(1000, 25000))

            # Create transaction
            transaction = Transaction.objects.create(
                user=user,
                company=company,
                type='income' if is_income else 'expense',
                title=f"{title} #{i+1}",
                description=f"Sample {transaction.type} transaction for testing",
                amount=amount,
                currency="₦",
                transaction_date=transaction_date,
                source_app=source_app,
                notes="Sample transaction created for dashboard testing"
            )

            transactions_created += 1

            if transactions_created % 10 == 0:
                self.stdout.write(f"Created {transactions_created} transactions...")

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {transactions_created} sample transactions for user "{email}"'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                'You can now visit the accounting dashboard to see the charts with real data'
            )
        ) 