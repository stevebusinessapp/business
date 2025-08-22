from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import CompanyProfile
from apps.inventory.models import InventoryCategory, InventoryItem, InventoryLayout, InventoryStatus
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Test currency functionality for inventory categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email to test with',
            default='admin@example.com'
        )

    def handle(self, *args, **options):
        email = options['email']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with email {email} does not exist. Please create the user first.')
            )
            return

        self.stdout.write(f'Testing currency functionality for user: {email}')
        
        # Get or create company profile
        company_profile, created = CompanyProfile.objects.get_or_create(
            user=user,
            defaults={
                'company_name': 'Test Company',
                'email': 'test@example.com',
                'phone': '+1234567890',
                'address': '123 Test Street',
                'currency_code': 'USD',
                'currency_symbol': '$'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created company profile with currency: {company_profile.currency_code} ({company_profile.currency_symbol})')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Using existing company profile with currency: {company_profile.currency_code} ({company_profile.currency_symbol})')
            )

        # Get or create default layout
        layout, created = InventoryLayout.objects.get_or_create(
            user=user,
            is_default=True,
            defaults={
                'name': 'Default Layout',
                'columns': InventoryLayout().get_default_columns()
            }
        )

        # Get or create status
        status, created = InventoryStatus.objects.get_or_create(
            name='in_stock',
            defaults={
                'display_name': 'In Stock',
                'color': '#28a745'
            }
        )

        # Create test categories
        categories_data = [
            {
                'name': 'Electronics',
                'description': 'Electronic devices and accessories',
                'color': '#007bff'
            },
            {
                'name': 'Clothing',
                'description': 'Apparel and fashion items',
                'color': '#28a745'
            },
            {
                'name': 'Books',
                'description': 'Books and publications',
                'color': '#ffc107'
            }
        ]

        created_categories = []
        for cat_data in categories_data:
            category, created = InventoryCategory.objects.get_or_create(
                user=user,
                name=cat_data['name'],
                defaults=cat_data
            )
            created_categories.append(category)
            
            if created:
                self.stdout.write(f'Created category: {category.name}')
            else:
                self.stdout.write(f'Using existing category: {category.name}')

        # Create test inventory items
        items_data = [
            {
                'product_name': 'Laptop',
                'sku_code': 'LAP001',
                'category': 'Electronics',
                'quantity': 10,
                'unit_price': 1200.00
            },
            {
                'product_name': 'Smartphone',
                'sku_code': 'PHN001',
                'category': 'Electronics',
                'quantity': 25,
                'unit_price': 800.00
            },
            {
                'product_name': 'T-Shirt',
                'sku_code': 'TSH001',
                'category': 'Clothing',
                'quantity': 50,
                'unit_price': 25.00
            },
            {
                'product_name': 'Jeans',
                'sku_code': 'JNS001',
                'category': 'Clothing',
                'quantity': 30,
                'unit_price': 75.00
            },
            {
                'product_name': 'Programming Book',
                'sku_code': 'BK001',
                'category': 'Books',
                'quantity': 15,
                'unit_price': 45.00
            }
        ]

        created_items = []
        for item_data in items_data:
            # Check if item already exists
            existing_item = InventoryItem.objects.filter(
                user=user,
                sku_code=item_data['sku_code']
            ).first()
            
            if existing_item:
                self.stdout.write(f'Using existing item: {existing_item.product_name}')
                created_items.append(existing_item)
                continue

            # Create new item
            item = InventoryItem.objects.create(
                user=user,
                layout=layout,
                product_name=item_data['product_name'],
                sku_code=item_data['sku_code'],
                status=status,
                data={
                    'category': item_data['category'],
                    'quantity': item_data['quantity'],
                    'unit_price': item_data['unit_price']
                }
            )
            
            # Calculate totals
            item.calculate_totals()
            created_items.append(item)
            
            self.stdout.write(f'Created item: {item.product_name} - Total Value: {item.total_value}')

        # Test category calculations
        self.stdout.write('\n' + '='*50)
        self.stdout.write('CATEGORY SUMMARY')
        self.stdout.write('='*50)
        
        for category in created_categories:
            # Get items in this category
            category_items = InventoryItem.objects.filter(
                user=user,
                data__category=category.name
            )
            
            # Calculate totals
            product_count = category_items.count()
            total_value = sum(item.total_value for item in category_items)
            
            self.stdout.write(f'\nCategory: {category.name}')
            self.stdout.write(f'  Products: {product_count}')
            self.stdout.write(f'  Total Value: {company_profile.currency_symbol}{total_value:,.2f}')
            
            # List items in category
            for item in category_items:
                self.stdout.write(f'    - {item.product_name}: {company_profile.currency_symbol}{item.total_value:,.2f}')

        # Test currency change
        self.stdout.write('\n' + '='*50)
        self.stdout.write('TESTING CURRENCY CHANGE')
        self.stdout.write('='*50)
        
        # Change to NGN
        old_currency = company_profile.currency_symbol
        company_profile.currency_code = 'NGN'
        company_profile.currency_symbol = '₦'
        company_profile.save()
        
        self.stdout.write(f'Changed currency from {old_currency} to {company_profile.currency_symbol}')
        
        # Recalculate category totals
        for category in created_categories:
            category_items = InventoryItem.objects.filter(
                user=user,
                data__category=category.name
            )
            
            product_count = category_items.count()
            total_value = sum(item.total_value for item in category_items)
            
            self.stdout.write(f'\nCategory: {category.name}')
            self.stdout.write(f'  Products: {product_count}')
            self.stdout.write(f'  Total Value: {company_profile.currency_symbol}{total_value:,.2f}')

        self.stdout.write('\n' + '='*50)
        self.stdout.write('TEST COMPLETED SUCCESSFULLY')
        self.stdout.write('='*50)
        self.stdout.write('\nYou can now visit http://127.0.0.1:8000/inventory/categories/')
        self.stdout.write('to see the currency functionality in action.')
        self.stdout.write('\nTo test currency changes:')
        self.stdout.write('1. Go to Company Profile')
        self.stdout.write('2. Change the currency')
        self.stdout.write('3. Return to Categories page to see the updates') 