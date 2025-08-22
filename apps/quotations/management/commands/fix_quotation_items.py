from django.core.management.base import BaseCommand
from apps.quotations.models import Quotation, QuotationItem
from decimal import Decimal


class Command(BaseCommand):
    help = 'Fix existing quotations with missing or incorrect line items'

    def handle(self, *args, **options):
        self.stdout.write('Starting quotation fix process...')
        
        # Get all quotations
        quotations = Quotation.objects.all()
        
        for quotation in quotations:
            self.stdout.write(f'Processing quotation {quotation.quotation_number}...')
            
            # Check if quotation has line items
            items = quotation.items.all()
            
            if items.exists():
                self.stdout.write(f'  - Found {items.count()} line items')
                
                # Recalculate line totals
                for item in items:
                    old_total = item.line_total
                    item.line_total = item.quantity * item.unit_price
                    
                    if old_total != item.line_total:
                        self.stdout.write(f'    - Fixed line total for {item.product_service}: {old_total} -> {item.line_total}')
                        item.save(update_fields=['line_total'])
                
                # Recalculate quotation totals
                old_subtotal = quotation.subtotal
                old_grand_total = quotation.grand_total
                
                quotation.calculate_totals()
                quotation.refresh_from_db()
                
                if old_subtotal != quotation.subtotal or old_grand_total != quotation.grand_total:
                    self.stdout.write(f'  - Fixed totals: Subtotal {old_subtotal} -> {quotation.subtotal}, Grand Total {old_grand_total} -> {quotation.grand_total}')
            else:
                self.stdout.write(f'  - No line items found')
        
        self.stdout.write(self.style.SUCCESS('Quotation fix process completed!')) 