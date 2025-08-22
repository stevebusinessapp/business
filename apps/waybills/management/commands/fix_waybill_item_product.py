from django.core.management.base import BaseCommand
from apps.waybills.models import WaybillItem
from django.db import transaction

class Command(BaseCommand):
    help = 'Fix all waybill items to use product_service key for product field.'

    def handle(self, *args, **options):
        updated = 0
        with transaction.atomic():
            for item in WaybillItem.objects.all():
                data = item.item_data or {}
                if 'product' in data:
                    data['product_service'] = data['product']
                    item.item_data = data
                    item.save(update_fields=['item_data'])
                    updated += 1
        self.stdout.write(self.style.SUCCESS(f'Updated {updated} waybill items.')) 