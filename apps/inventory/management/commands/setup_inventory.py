from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.inventory.models import (
    InventoryStatus, InventoryLayout, InventoryItem,
    InventoryCustomField
)
from decimal import Decimal
import json

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up inventory system with default data and configurations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Email to set up inventory for (default: first user)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of existing data',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up Inventory System...'))
        
        # Get or create user
        if options['user']:
            try:
                user = User.objects.get(email=options['user'])
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with email "{options["user"]}" not found')
                )
                return
        else:
            user = User.objects.first()
            if not user:
                self.stdout.write(
                    self.style.ERROR('No users found. Please create a user first.')
                )
                return
        
        self.stdout.write(f'Setting up inventory for user: {user.email}')
        
        # Create default statuses
        self.create_default_statuses()
        
        # Create default layout
        layout = self.create_default_layout(user, options['force'])
        
        # Create sample inventory items
        self.create_sample_items(user, layout)
        
        # Create custom fields example
        self.create_custom_fields(user, layout)
        
        self.stdout.write(
            self.style.SUCCESS('Inventory system setup completed successfully!')
        )
        
        # Print summary
        self.print_summary(user)

    def create_default_statuses(self):
        """Create default inventory statuses"""
        self.stdout.write('Creating default inventory statuses...')
        
        statuses_data = [
            ('in_stock', 'In Stock', '#28a745', 1),
            ('low_stock', 'Low Stock', '#ffc107', 2),
            ('out_of_stock', 'Out of Stock', '#dc3545', 3),
            ('reserved', 'Reserved', '#17a2b8', 4),
            ('damaged', 'Damaged', '#fd7e14', 5),
            ('returned', 'Returned', '#6f42c1', 6),
            ('disposed', 'Disposed', '#6c757d', 7),
            ('removed', 'Removed', '#343a40', 8),
            ('backordered', 'Backordered', '#e83e8c', 9),
            ('discontinued', 'Discontinued', '#6c757d', 10),
        ]
        
        for status_code, display_name, color, order in statuses_data:
            status, created = InventoryStatus.objects.get_or_create(
                name=status_code,
                defaults={
                    'display_name': display_name,
                    'color': color,
                    'sort_order': order,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created status: {display_name}')
            else:
                self.stdout.write(f'  - Status already exists: {display_name}')

    def create_default_layout(self, user, force=False):
        """Create default inventory layout"""
        self.stdout.write('Creating default inventory layout...')
        
        if force:
            InventoryLayout.objects.filter(user=user, is_default=True).delete()
        
        layout, created = InventoryLayout.objects.get_or_create(
            user=user,
            is_default=True,
            defaults={
                'name': 'Default Layout',
                'description': 'Standard inventory layout with all essential fields',
                'columns': InventoryLayout().get_default_columns(),
                'auto_calculate': True,
                'show_totals': True,
                'show_grand_total': True,
                'allow_inline_editing': True,
                'allow_bulk_operations': True,
                'enable_sorting': True,
                'enable_filtering': True,
                'primary_color': '#007bff',
                'secondary_color': '#6c757d',
                'company_name': f'{user.get_full_name()}\'s Company',
            }
        )
        
        if created:
            self.stdout.write(f'  ✓ Created default layout: {layout.name}')
        else:
            self.stdout.write(f'  - Default layout already exists: {layout.name}')
        
        return layout

    def create_sample_items(self, user, layout):
        """Create sample inventory items"""
        self.stdout.write('Creating sample inventory items...')
        
        # Get default status
        in_stock_status = InventoryStatus.objects.get(name='in_stock')
        low_stock_status = InventoryStatus.objects.get(name='low_stock')
        
        sample_items = [
            {
                'product_name': 'Laptop Computer',
                'sku_code': 'LAP001',
                'status': in_stock_status,
                'data': {
                    'quantity': 25,
                    'unit_price': 150000.00,
                    'description': 'High-performance laptop for business use',
                    'category': 'Electronics',
                    'supplier': 'TechCorp Inc.'
                }
            },
            {
                'product_name': 'Wireless Mouse',
                'sku_code': 'MOU002',
                'status': in_stock_status,
                'data': {
                    'quantity': 150,
                    'unit_price': 2500.00,
                    'description': 'Ergonomic wireless mouse',
                    'category': 'Accessories',
                    'supplier': 'AccessTech Ltd.'
                }
            },
            {
                'product_name': 'Office Chair',
                'sku_code': 'CHA003',
                'status': low_stock_status,
                'data': {
                    'quantity': 8,
                    'unit_price': 45000.00,
                    'description': 'Ergonomic office chair with lumbar support',
                    'category': 'Furniture',
                    'supplier': 'OfficeFurn Co.'
                }
            },
            {
                'product_name': 'Printer Paper',
                'sku_code': 'PAP004',
                'status': in_stock_status,
                'data': {
                    'quantity': 500,
                    'unit_price': 1500.00,
                    'description': 'A4 printer paper, 80gsm, 500 sheets per ream',
                    'category': 'Office Supplies',
                    'supplier': 'PaperMart Ltd.'
                }
            },
            {
                'product_name': 'USB Flash Drive',
                'sku_code': 'USB005',
                'status': in_stock_status,
                'data': {
                    'quantity': 75,
                    'unit_price': 3500.00,
                    'description': '32GB USB 3.0 flash drive',
                    'category': 'Electronics',
                    'supplier': 'DataTech Solutions'
                }
            }
        ]
        
        created_count = 0
        for item_data in sample_items:
            # Check if item already exists
            if InventoryItem.objects.filter(user=user, sku_code=item_data['sku_code']).exists():
                self.stdout.write(f'  - Item already exists: {item_data["product_name"]}')
                continue
            
            # Create item
            item = InventoryItem.objects.create(
                user=user,
                layout=layout,
                product_name=item_data['product_name'],
                sku_code=item_data['sku_code'],
                status=item_data['status'],
                data=item_data['data']
            )
            
            # Calculate totals
            item.calculate_totals()
            created_count += 1
            self.stdout.write(f'  ✓ Created item: {item.product_name}')
        
        self.stdout.write(f'  Created {created_count} sample items')

    def create_custom_fields(self, user, layout):
        """Create example custom fields"""
        self.stdout.write('Creating example custom fields...')
        
        custom_fields = [
            {
                'name': 'supplier',
                'display_name': 'Supplier',
                'field_type': 'text',
                'is_required': False,
                'help_text': 'Product supplier or vendor',
                'width': '150px',
                'sort_order': 1
            },
            {
                'name': 'category',
                'display_name': 'Category',
                'field_type': 'select',
                'is_required': False,
                'help_text': 'Product category',
                'choices': ['Electronics', 'Furniture', 'Office Supplies', 'Accessories'],
                'width': '120px',
                'sort_order': 2
            },
            {
                'name': 'warranty_months',
                'display_name': 'Warranty (Months)',
                'field_type': 'number',
                'is_required': False,
                'help_text': 'Warranty period in months',
                'width': '100px',
                'sort_order': 3
            },
            {
                'name': 'reorder_level',
                'display_name': 'Reorder Level',
                'field_type': 'number',
                'is_required': False,
                'help_text': 'Minimum stock level before reordering',
                'width': '120px',
                'sort_order': 4,
                'is_calculation_field': True
            }
        ]
        
        created_count = 0
        for field_data in custom_fields:
            # Check if field already exists
            if InventoryCustomField.objects.filter(user=user, name=field_data['name']).exists():
                self.stdout.write(f'  - Custom field already exists: {field_data["display_name"]}')
                continue
            
            # Create custom field
            field = InventoryCustomField.objects.create(
                user=user,
                layout=layout,
                name=field_data['name'],
                display_name=field_data['display_name'],
                field_type=field_data['field_type'],
                is_required=field_data['is_required'],
                help_text=field_data['help_text'],
                width=field_data['width'],
                sort_order=field_data['sort_order'],
                is_calculation_field=field_data.get('is_calculation_field', False),
                choices=field_data.get('choices', [])
            )
            
            created_count += 1
            self.stdout.write(f'  ✓ Created custom field: {field.display_name}')
        
        self.stdout.write(f'  Created {created_count} custom fields')

    def print_summary(self, user):
        """Print setup summary"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('INVENTORY SYSTEM SETUP SUMMARY'))
        self.stdout.write('='*50)
        
        # Count statistics
        status_count = InventoryStatus.objects.count()
        layout_count = InventoryLayout.objects.filter(user=user).count()
        item_count = InventoryItem.objects.filter(user=user).count()
        custom_field_count = InventoryCustomField.objects.filter(user=user).count()
        
        self.stdout.write(f'User: {user.email}')
        self.stdout.write(f'Inventory Statuses: {status_count}')
        self.stdout.write(f'Layouts: {layout_count}')
        self.stdout.write(f'Inventory Items: {item_count}')
        self.stdout.write(f'Custom Fields: {custom_field_count}')
        
        # Calculate total value
        total_value = 0
        items = InventoryItem.objects.filter(user=user)
        for item in items:
            total_value += item.total_value
        
        self.stdout.write(f'Total Inventory Value: ₦{total_value:,.2f}')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('SETUP COMPLETED SUCCESSFULLY!'))
        self.stdout.write('='*50)
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Visit /inventory/ to view your inventory')
        self.stdout.write('2. Go to /inventory/layouts/ to customize your layout')
        self.stdout.write('3. Use /inventory/import/ to import more data')
        self.stdout.write('4. Check /inventory/export/ to export your data')
        self.stdout.write('\nFor debugging, add ?debug=true to any inventory URL') 