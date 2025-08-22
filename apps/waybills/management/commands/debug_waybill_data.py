from django.core.management.base import BaseCommand
from apps.waybills.models import Waybill

class Command(BaseCommand):
    help = 'Print all data for waybill 26, including custom_data and all item_data.'

    def handle(self, *args, **options):
        try:
            waybill = Waybill.objects.get(pk=26)
            self.stdout.write(self.style.SUCCESS(f'Waybill #{waybill.pk} - {waybill.waybill_number}'))
            self.stdout.write('custom_data:')
            self.stdout.write(str(waybill.custom_data))
            self.stdout.write('Items:')
            for item in waybill.items.all():
                self.stdout.write(f'  Item #{item.pk}: {item.item_data}')
        except Waybill.DoesNotExist:
            self.stdout.write(self.style.ERROR('Waybill with pk=26 does not exist.')) 