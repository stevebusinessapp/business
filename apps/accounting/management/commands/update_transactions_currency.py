from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounting.models import Transaction
from apps.core.models import CompanyProfile
from django.db import models

User = get_user_model()


class Command(BaseCommand):
    help = 'Update all existing transactions to use the current company profile currency'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Update transactions for a specific user ID',
        )
        parser.add_argument(
            '--company-id',
            type=int,
            help='Update transactions for a specific company ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        company_id = options.get('company_id')
        dry_run = options.get('dry_run')

        if user_id:
            try:
                user = User.objects.get(id=user_id)
                company = user.company_profile
                self.stdout.write(f"Processing transactions for user: {user.username}")
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User with ID {user_id} not found"))
                return
        elif company_id:
            try:
                company = CompanyProfile.objects.get(id=company_id)
                self.stdout.write(f"Processing transactions for company: {company.company_name}")
            except CompanyProfile.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Company with ID {company_id} not found"))
                return
        else:
            # Process all companies
            companies = CompanyProfile.objects.all()
            self.stdout.write(f"Processing transactions for {companies.count()} companies")
            
            for company in companies:
                self.process_company_transactions(company, dry_run)
            return

        # Process single company
        self.process_company_transactions(company, dry_run)

    def process_company_transactions(self, company, dry_run=False):
        """Process transactions for a specific company"""
        current_currency = company.currency_symbol
        
        # Get transactions that don't match the current currency
        transactions = Transaction.objects.filter(
            company=company,
            currency__iexact=current_currency
        ).exclude(currency=current_currency)
        
        if not transactions.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"All transactions for {company.company_name} already use the current currency ({current_currency})"
                )
            )
            return

        self.stdout.write(
            f"Found {transactions.count()} transactions for {company.company_name} "
            f"that need currency update to {current_currency}"
        )

        if dry_run:
            # Show what would be updated
            for transaction in transactions[:5]:  # Show first 5 as examples
                self.stdout.write(
                    f"  Would update: {transaction.title} - "
                    f"Currency: {transaction.currency} -> {current_currency}"
                )
            if transactions.count() > 5:
                self.stdout.write(f"  ... and {transactions.count() - 5} more transactions")
        else:
            # Actually update the transactions
            updated_count = transactions.update(currency=current_currency)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully updated {updated_count} transactions for {company.company_name} "
                    f"to use currency {current_currency}"
                )
            )

        # Show summary by currency
        currency_summary = Transaction.objects.filter(company=company).values('currency').annotate(
            count=models.Count('id')
        ).order_by('-count')
        
        self.stdout.write(f"\nCurrency distribution for {company.company_name}:")
        for item in currency_summary:
            self.stdout.write(f"  {item['currency']}: {item['count']} transactions") 