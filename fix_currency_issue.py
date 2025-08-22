#!/usr/bin/env python
"""
Script to fix currency display issues in accounting transactions.
This script will update all transactions to use the current company profile currency.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
django.setup()

from apps.core.models import CompanyProfile
from apps.accounting.models import Transaction
from django.db import models

def fix_currency_issues():
    """Fix currency display issues for all companies"""
    print("🔧 Fixing Currency Display Issues...")
    print("=" * 50)
    
    companies = CompanyProfile.objects.all()
    
    for company in companies:
        print(f"\n📊 Processing: {company.company_name}")
        print(f"   Current Currency: {company.currency_code} ({company.currency_symbol})")
        
        # Get all transactions for this company
        transactions = Transaction.objects.filter(company=company)
        
        if not transactions.exists():
            print("   ✅ No transactions found")
            continue
        
        # Check current currency distribution
        currency_distribution = transactions.values('currency').annotate(
            count=models.Count('id')
        ).order_by('-count')
        
        print("   📈 Current Currency Distribution:")
        for item in currency_distribution:
            print(f"      {item['currency']}: {item['count']} transactions")
        
        # Update all transactions to use the company's current currency
        updated_count = transactions.update(currency=company.currency_symbol)
        
        print(f"   ✅ Updated {updated_count} transactions to use {company.currency_symbol}")
        
        # Verify the update
        remaining_currencies = transactions.values('currency').distinct()
        if len(remaining_currencies) == 1 and remaining_currencies[0]['currency'] == company.currency_symbol:
            print(f"   ✅ All transactions now use {company.currency_symbol}")
        else:
            print(f"   ⚠️  Some transactions still have different currencies")
            # Show remaining currencies
            for item in remaining_currencies:
                count = transactions.filter(currency=item['currency']).count()
                print(f"      {item['currency']}: {count} transactions")
    
    print("\n" + "=" * 50)
    print("🎉 Currency fix completed!")
    print("\nNext steps:")
    print("1. Refresh your transactions page")
    print("2. All currencies should now display correctly")
    print("3. Use the 'Update Currencies' button if needed")

if __name__ == "__main__":
    try:
        fix_currency_issues()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1) 