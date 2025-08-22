from django.core.management.base import BaseCommand
from apps.job_orders.models import JobOrder

class Command(BaseCommand):
    help = 'Assign tracking IDs to all JobOrders without one.'

    def handle(self, *args, **options):
        joborders = JobOrder.objects.filter(tracking_id__isnull=True).order_by('id')
        last_num = 0
        # Find the highest existing tracking number
        for jo in JobOrder.objects.exclude(tracking_id__isnull=True):
            if jo.tracking_id and jo.tracking_id.startswith('JOB-'):
                try:
                    num = int(jo.tracking_id.split('-')[-1])
                    if num > last_num:
                        last_num = num
                except Exception:
                    pass
        count = 0
        for jo in joborders:
            last_num += 1
            jo.tracking_id = f"JOB-{last_num:04d}"
            jo.save()
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Assigned tracking IDs to {count} job orders.')) 