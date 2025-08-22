from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.inventory.models import InventoryCategory, InventoryItem
from apps.core.models import CompanyProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up default categories and fix category associations for users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email of specific user to process (optional)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Process all users',
        )

    def handle(self, *args, **options):
        if options['email']:
            try:
                user = User.objects.get(email=options['email'])
                self.process_user(user)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with email {options["email"]} does not exist.')
                )
        elif options['all']:
            users = User.objects.all()
            for user in users:
                self.stdout.write(f'\nProcessing user: {user.email}')
                self.process_user(user)
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --email or --all')
            )

    def process_user(self, user):
        """Process a single user"""
        self.stdout.write(f'Processing user: {user.email}')
        
        # Get or create company profile
        company_profile, created = CompanyProfile.objects.get_or_create(
            user=user,
            defaults={
                'company_name': f'{user.first_name}\'s Company',
                'email': user.email,
                'currency_code': 'NGN',
                'currency_symbol': '₦'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created company profile for {user.email}')
            )
        
        # Create default categories if user doesn't have any
        categories = InventoryCategory.objects.filter(user=user)
        if not categories.exists():
            default_categories = [
                {'name': 'Electronics', 'description': 'Electronic devices and accessories', 'color': '#007bff'},
                {'name': 'Clothing', 'description': 'Apparel and fashion items', 'color': '#28a745'},
                {'name': 'Books', 'description': 'Books and publications', 'color': '#ffc107'},
                {'name': 'Office Supplies', 'description': 'Office equipment and supplies', 'color': '#6f42c1'},
                {'name': 'Furniture', 'description': 'Furniture and home items', 'color': '#fd7e14'},
                {'name': 'Accessories', 'description': 'Various accessories and parts', 'color': '#e83e8c'},
            ]
            
            for cat_data in default_categories:
                category, created = InventoryCategory.objects.get_or_create(
                    user=user,
                    name=cat_data['name'],
                    defaults=cat_data
                )
                if created:
                    self.stdout.write(f'Created category: {category.name}')
                else:
                    self.stdout.write(f'Category already exists: {category.name}')
        
        # Fix category associations for existing items
        items = InventoryItem.objects.filter(user=user)
        if items.exists():
            self.stdout.write(f'Found {items.count()} inventory items')
            
            # Create a mapping of items to categories
            item_category_mapping = {
                'Motor Spare parts': 'Accessories',
                'TV set': 'Electronics', 
                'Smoked Glass': 'Furniture',
                'TEST ITEM': 'Office Supplies',
                'Laptop': 'Electronics',
                'Smartphone': 'Electronics',
                'T-Shirt': 'Clothing',
                'Jeans': 'Clothing',
                'Book': 'Books',
                'Programming Book': 'Books',
                'Printer Paper': 'Office Supplies',
                'Office Chair': 'Furniture'
            }
            
            items_fixed = 0
            for item in items:
                if 'category' not in item.data or not item.data['category']:
                    # Find a suitable category for this item
                    suggested_category = item_category_mapping.get(item.product_name, 'Office Supplies')
                    
                    # Check if the suggested category exists
                    category_exists = categories.filter(name=suggested_category).exists()
                    if category_exists:
                        # Update the item's data with the category
                        item.data['category'] = suggested_category
                        item.save()
                        self.stdout.write(f'✓ Assigned "{suggested_category}" to "{item.product_name}"')
                        items_fixed += 1
                    else:
                        # Use the first available category
                        first_category = categories.first()
                        if first_category:
                            item.data['category'] = first_category.name
                            item.save()
                            self.stdout.write(f'✓ Assigned "{first_category.name}" to "{item.product_name}" (fallback)')
                            items_fixed += 1
            
            if items_fixed > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Fixed category associations for {items_fixed} items')
                )
            else:
                self.stdout.write('All items already have proper category associations')
        
        # Show summary
        categories = InventoryCategory.objects.filter(user=user)
        items = InventoryItem.objects.filter(user=user)
        
        self.stdout.write(f'\nSummary for {user.email}:')
        self.stdout.write(f'  Categories: {categories.count()}')
        self.stdout.write(f'  Inventory Items: {items.count()}')
        
        for category in categories:
            category_items = InventoryItem.objects.filter(
                user=user,
                data__category=category.name
            )
            product_count = category_items.count()
            total_value = sum(item.total_value for item in category_items)
            
            self.stdout.write(f'  - {category.name}: {product_count} products, {company_profile.currency_symbol}{total_value:,.2f}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Completed processing for {user.email}')
        ) 