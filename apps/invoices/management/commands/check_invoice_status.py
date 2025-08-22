from django.core.management.base import BaseCommand
from django.db import connection
from apps.invoices.models import Invoice


class Command(BaseCommand):
    help = 'Check and fix invoice status values'

    def handle(self, *args, **options):
        self.stdout.write("Checking invoice status values...")
        
        # Check current status values in database
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT status FROM invoices_invoice")
            statuses = [row[0] for row in cursor.fetchall()]
            
        self.stdout.write(f"Current status values in database: {statuses}")
        
        # Check if we can update to new values
        try:
            # Try to update one invoice to test
            invoice = Invoice.objects.first()
            if invoice:
                old_status = invoice.status
                self.stdout.write(f"Testing status update on invoice {invoice.id}")
                
                # Try each status
                for test_status in ['unpaid', 'partial', 'paid', 'delivered']:
                    invoice.status = test_status
                    invoice.save()
                    invoice.refresh_from_db()
                    
                    if invoice.status == test_status:
                        self.stdout.write(f"✓ Status '{test_status}' works")
                    else:
                        self.stdout.write(f"✗ Status '{test_status}' failed - got '{invoice.status}'")
                
                # Restore original status
                invoice.status = old_status
                invoice.save()
                
        except Exception as e:
            self.stdout.write(f"Error testing status update: {e}")
        
        self.stdout.write("Status check completed.")
