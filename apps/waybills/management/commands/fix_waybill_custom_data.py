from django.core.management.base import BaseCommand
from apps.waybills.models import Waybill
from django.db import transaction

class Command(BaseCommand):
    help = 'Fix old waybill custom_data to use nested sender_info and receiver_info structure.'

    def handle(self, *args, **options):
        updated = 0
        with transaction.atomic():
            for waybill in Waybill.objects.all():
                data = waybill.custom_data or {}
                changed = False

                # Migrate sender fields
                sender_fields = ['sender_name', 'sender_phone', 'sender_address']
                if any(f in data for f in sender_fields):
                    sender_info = data.get('sender_info', {})
                    for f in sender_fields:
                        if f in data:
                            key = f.replace('sender_', '')
                            sender_info[f'{key}'] = data.pop(f)
                            changed = True
                    data['sender_info'] = sender_info

                # Migrate recipient fields (sometimes called recipient, sometimes receiver)
                receiver_fields = ['recipient_name', 'recipient_phone', 'recipient_address', 'receiver_name', 'receiver_phone', 'receiver_address']
                if any(f in data for f in receiver_fields):
                    receiver_info = data.get('receiver_info', {})
                    for f in receiver_fields:
                        if f in data:
                            # Normalize to receiver_*
                            key = f.replace('recipient_', '').replace('receiver_', '')
                            receiver_info[f'{key}'] = data.pop(f)
                            changed = True
                    data['receiver_info'] = receiver_info

                if changed:
                    waybill.custom_data = data
                    waybill.save(update_fields=['custom_data'])
                    updated += 1
        self.stdout.write(self.style.SUCCESS(f'Updated {updated} waybills.')) 