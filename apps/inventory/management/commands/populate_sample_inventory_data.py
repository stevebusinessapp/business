from django.core.management.base import BaseCommand
from apps.inventory.models import InventoryItem, InventoryCategory
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Populate existing inventory items with sample data for demonstration'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Sample data for different items
        sample_data = {
            7: {  # Printer Paper
                'category': 'Office Supplies',
                'supplier': 'PaperCo Supplies',
                'description': 'High-quality A4 printer paper, 80gsm, white, 500 sheets per pack',
                'location': 'Warehouse A - Shelf 3',
                'minimum_threshold': 5.0,
                'expiry_date': '2026-12-31',
                'notes': 'Best seller item. Reorder when stock gets low.',
                'quantity': 8.0,
                'unit_price': 2.0
            },
            8: {  # Banner
                'category': 'Printing Materials',
                'supplier': 'BannerPro Printing',
                'description': 'Vinyl banner material, 510gsm, suitable for outdoor use',
                'location': 'Warehouse B - Roll Storage',
                'minimum_threshold': 2.0,
                'expiry_date': '2027-06-30',
                'notes': 'Used for outdoor advertising banners. Store in dry area.',
                'quantity': 15.0,
                'unit_price': 45.0
            },
            9: {  # Techno Phone
                'category': 'Electronics',
                'supplier': 'TechWorld Electronics',
                'description': 'Smartphone with 128GB storage, 6.7" display, 5G capable',
                'location': 'Warehouse A - Electronics Section',
                'minimum_threshold': 3.0,
                'expiry_date': '2026-03-15',
                'notes': 'Premium electronics item. Handle with care. Includes warranty.',
                'quantity': 12.0,
                'unit_price': 850.0
            },
            10: {  # TEST ITEM
                'category': 'Accessories',
                'supplier': 'Test Supplier Inc.',
                'description': 'This is a test product for demonstration purposes',
                'location': 'Test Storage Area',
                'minimum_threshold': 10.0,
                'expiry_date': '2025-12-31',
                'notes': 'Test item created to verify system functionality.',
                'quantity': 50.0,
                'unit_price': 25.0
            }
        }
        
        updated_count = 0
        
        for item_id, data in sample_data.items():
            try:
                item = InventoryItem.objects.get(id=item_id)
                
                # Get or create category
                category_name = data['category']
                category, created = InventoryCategory.objects.get_or_create(
                    name=category_name,
                    user=item.user,  # Add the user field
                    defaults={
                        'description': f'Category for {category_name}',
                        'color': '#007bff',
                        'is_active': True
                    }
                )
                
                # Update item data
                current_data = item.data.copy()
                current_data.update({
                    'category': {'id': category.id, 'name': category.name},
                    'supplier': data['supplier'],
                    'description': data['description'],
                    'location': data['location'],
                    'minimum_threshold': data['minimum_threshold'],
                    'expiry_date': data['expiry_date'],
                    'notes': data['notes'],
                    'quantity': data['quantity'],
                    'unit_price': data['unit_price']
                })
                
                if dry_run:
                    self.stdout.write(f'Would update item {item.id}: {item.product_name}')
                    self.stdout.write(f'  Category: {data["category"]}')
                    self.stdout.write(f'  Supplier: {data["supplier"]}')
                    self.stdout.write(f'  Location: {data["location"]}')
                else:
                    item.data = current_data
                    item.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated item {item.id}: {item.product_name}'
                        )
                    )
                    
            except InventoryItem.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'Item {item_id} not found, skipping...'
                    )
                )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would update {updated_count} items with sample data'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} items with sample data'
                )
            ) 