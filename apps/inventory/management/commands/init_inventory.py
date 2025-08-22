from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.inventory.models import InventoryStatus, InventoryLayout

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize the new inventory system with default statuses and layouts'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Initializing new inventory system...')
        
        # Create default statuses
        self.stdout.write('Creating default inventory statuses...')
        InventoryStatus.get_default_statuses()
        
        # Get all users and create default layouts
        users = User.objects.all()
        for user in users:
            # Check if user already has a default layout
            if not InventoryLayout.objects.filter(user=user, is_default=True).exists():
                layout = InventoryLayout.objects.create(
                    user=user,
                    name="Default Inventory",
                    is_default=True,
                    columns=[
                        {'name': 'Product Name', 'type': 'text', 'required': True, 'visible': True},
                        {'name': 'SKU Code', 'type': 'text', 'required': True, 'visible': True},
                        {'name': 'Quantity', 'type': 'number', 'required': False, 'visible': True},
                        {'name': 'Unit Price', 'type': 'decimal', 'required': False, 'visible': True},
                        {'name': 'Total', 'type': 'calculated', 'required': False, 'visible': True},
                        {'name': 'Status', 'type': 'status', 'required': True, 'visible': True},
                    ],
                    auto_calculate=True,
                    show_totals=True,
                    show_grand_total=True,
                    allow_inline_editing=True,
                    allow_bulk_operations=True
                )
                self.stdout.write(f'  Created default layout for user: {user.email}')
        
        self.stdout.write(
            self.style.SUCCESS('✅ Inventory system initialized successfully!')
        )
        self.stdout.write(f'  - Created default statuses')
        self.stdout.write(f'  - Created default layouts for {users.count()} users') 