from django.core.management.base import BaseCommand
from django.db import connection
from apps.waybills.models import Waybill


class Command(BaseCommand):
    help = 'Check and fix waybill status values'

    def handle(self, *args, **options):
        self.stdout.write("Checking waybill status values...")
        
        # Check current status values in database
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT status FROM waybills_waybill")
            statuses = [row[0] for row in cursor.fetchall()]
            
        self.stdout.write(f"Current status values in database: {statuses}")
        
        # Check if we can update to new values
        try:
            # Try to update one waybill to test
            waybill = Waybill.objects.first()
            if waybill:
                old_status = waybill.status
                self.stdout.write(f"Testing status update on waybill {waybill.id}")
                
                # Try each status
                for test_status in ['delivered', 'pending', 'processing', 'dispatched', 'not_delivered', 'returned', 'cancelled', 'on_hold', 'awaiting_pickup']:
                    waybill.status = test_status
                    waybill.save()
                    waybill.refresh_from_db()
                    
                    if waybill.status == test_status:
                        self.stdout.write(f"✓ Status '{test_status}' works")
                    else:
                        self.stdout.write(f"✗ Status '{test_status}' failed - got '{waybill.status}'")
                
                # Restore original status
                waybill.status = old_status
                waybill.save()
                
        except Exception as e:
            self.stdout.write(f"Error testing status update: {e}")
        
        self.stdout.write("Status check completed.")
