from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import json
import uuid
import re
from typing import Dict, Any, List, Optional
from django.db.models import JSONField

User = get_user_model()

class InventoryStatus(models.Model):
    """Predefined inventory status options with color coding"""
    STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('reserved', 'Reserved'),
        ('damaged', 'Damaged'),
        ('returned', 'Returned'),
        ('disposed', 'Disposed'),
        ('removed', 'Removed'),
        ('backordered', 'Backordered'),
        ('discontinued', 'Discontinued'),
    ]
    
    name = models.CharField(max_length=20, choices=STATUS_CHOICES, unique=True)
    display_name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#007bff")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Inventory Status'
        verbose_name_plural = 'Inventory Statuses'
    
    def __str__(self):
        return self.display_name
    
    @classmethod
    def get_default_statuses(cls):
        """Create default statuses if they don't exist"""
        defaults = [
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
        
        for status_code, display_name, color, order in defaults:
            cls.objects.get_or_create(
                name=status_code,
                defaults={
                    'display_name': display_name,
                    'color': color,
                    'sort_order': order
                }
            )


class InventoryLayout(models.Model):
    """User's custom inventory table layout and preferences"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_layouts')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    
    # Layout configuration
    columns = JSONField(default=list, help_text="Column definitions and order")
    column_visibility = JSONField(default=dict, help_text="Column visibility settings")
    column_widths = JSONField(default=dict, help_text="Column width settings")
    column_order = JSONField(default=list, help_text="Column order preferences")
    
    # Calculation settings
    auto_calculate = models.BooleanField(default=True)
    calculation_fields = JSONField(default=list, help_text="Fields that trigger calculations")
    calculation_rules = JSONField(default=dict, help_text="Custom calculation rules")
    
    # Branding and styling
    company_logo = models.ImageField(upload_to='inventory/logos/', null=True, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    company_address = models.TextField(blank=True)
    company_phone = models.CharField(max_length=50, blank=True)
    company_email = models.EmailField(blank=True)
    primary_color = models.CharField(max_length=7, default="#007bff")
    secondary_color = models.CharField(max_length=7, default="#6c757d")
    
    # Table settings
    show_totals = models.BooleanField(default=True)
    show_grand_total = models.BooleanField(default=True)
    allow_inline_editing = models.BooleanField(default=True)
    allow_bulk_operations = models.BooleanField(default=True)
    enable_sorting = models.BooleanField(default=True)
    enable_filtering = models.BooleanField(default=True)
    
    # Export settings
    export_settings = JSONField(default=dict, help_text="Export configuration")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
        unique_together = ['user', 'name']
        verbose_name = 'Inventory Layout'
        verbose_name_plural = 'Inventory Layouts'
    
    def __str__(self):
        # Handle different User model field names
        user_identifier = getattr(self.user, 'username', None)
        if not user_identifier:
            user_identifier = getattr(self.user, 'email', None)
        if not user_identifier:
            user_identifier = str(self.user.id)
        return f"{user_identifier} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default layout per user
        if self.is_default:
            InventoryLayout.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
    def get_visible_columns(self):
        """Get list of visible columns in order"""
        if not self.columns:
            return self.get_default_columns()
        
        visible_columns = []
        for col in self.columns:
            if self.column_visibility.get(col.get('name', ''), True):
                visible_columns.append(col)
        return visible_columns
    
    def supports_calculations(self):
        """Check if layout supports calculations (has quantity and price fields)"""
        if not self.auto_calculate:
            return False
        
        column_names = [col.get('name', '').lower() for col in self.columns]
        has_quantity = any('quantity' in name for name in column_names)
        has_price = any('price' in name or 'cost' in name for name in column_names)
        return has_quantity and has_price
    
    def get_calculation_fields(self):
        """Get fields that should trigger calculations"""
        if not self.calculation_fields:
            # Auto-detect calculation fields
            calculation_fields = []
            for col in self.columns:
                col_name = col.get('name', '').lower()
                if any(keyword in col_name for keyword in ['quantity', 'price', 'cost', 'amount']):
                    calculation_fields.append(col.get('name', ''))
            return calculation_fields
        return self.calculation_fields
    
    def get_default_columns(self):
        """Get the default standard table columns"""
        return [
            {
                'name': 'serial_number',
                'display_name': 'S/N',
                'field_type': 'serial',
                'is_required': False,
                'is_editable': False,
                'width': '60px',
                'sortable': False,
                'searchable': False,
                'is_auto_numbered': True
            },
            {
                'name': 'product_name',
                'display_name': 'Product Name',
                'field_type': 'text',
                'is_required': True,
                'is_editable': True,
                'width': '200px',
                'sortable': True,
                'searchable': True
            },
            {
                'name': 'sku_code',
                'display_name': 'Product Code/SKU',
                'field_type': 'text',
                'is_required': True,
                'is_editable': True,
                'width': '150px',
                'sortable': True,
                'searchable': True
            },
            {
                'name': 'quantity',
                'display_name': 'Quantity',
                'field_type': 'number',
                'is_required': True,
                'is_editable': True,
                'width': '100px',
                'sortable': True,
                'searchable': True,
                'is_calculation_field': True
            },
            {
                'name': 'unit_price',
                'display_name': 'Unit Price',
                'field_type': 'decimal',
                'is_required': True,
                'is_editable': True,
                'width': '120px',
                'sortable': True,
                'searchable': True,
                'is_calculation_field': True
            },
            {
                'name': 'total',
                'display_name': 'Total',
                'field_type': 'calculated',
                'is_required': False,
                'is_editable': False,
                'width': '120px',
                'sortable': True,
                'searchable': False,
                'formula': 'quantity * unit_price'
            },
            {
                'name': 'status',
                'display_name': 'Status',
                'field_type': 'select',
                'is_required': True,
                'is_editable': True,
                'width': '120px',
                'sortable': True,
                'searchable': True,
                'choices': 'status_choices'
            },
            {
                'name': 'actions',
                'display_name': 'Actions',
                'field_type': 'actions',
                'is_required': False,
                'is_editable': False,
                'width': '150px',
                'sortable': False,
                'searchable': False
            }
        ]


class InventoryCustomField(models.Model):
    """Custom fields that users can add to their inventory"""
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('decimal', 'Decimal'),
        ('date', 'Date'),
        ('datetime', 'Date & Time'),
        ('select', 'Dropdown'),
        ('multiselect', 'Multiple Choice'),
        ('boolean', 'Yes/No'),
        ('url', 'URL'),
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('textarea', 'Long Text'),
        ('file', 'File Upload'),
        ('image', 'Image'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_custom_fields')
    layout = models.ForeignKey(InventoryLayout, on_delete=models.CASCADE, related_name='custom_fields', null=True, blank=True)
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    
    # Field configuration
    is_required = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)
    default_value = models.TextField(blank=True)
    help_text = models.CharField(max_length=200, blank=True)
    
    # For select/multiselect fields
    choices = JSONField(default=list, blank=True)
    
    # Validation
    min_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    max_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    min_length = models.PositiveIntegerField(null=True, blank=True)
    max_length = models.PositiveIntegerField(null=True, blank=True)
    
    # Display settings
    is_visible = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    width = models.CharField(max_length=10, default='auto', help_text="Column width (e.g., '100px', '20%')")
    
    # Calculation settings
    is_calculation_field = models.BooleanField(default=False, help_text="Include in calculations")
    calculation_formula = models.CharField(max_length=500, blank=True, help_text="Custom calculation formula")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
        unique_together = ['user', 'name']
        verbose_name = 'Inventory Custom Field'
        verbose_name_plural = 'Inventory Custom Fields'
    
    def __str__(self):
        return f"{self.display_name} ({self.user.email})"
    
    def clean(self):
        """Validate field configuration"""
        if self.field_type in ['select', 'multiselect'] and not self.choices:
            raise ValidationError("Select fields must have choices defined.")
        
        if self.field_type in ['number', 'decimal']:
            if self.min_value and self.max_value and self.min_value > self.max_value:
                raise ValidationError("Minimum value cannot be greater than maximum value.")
        
        # Validate field name format
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.name):
            raise ValidationError('Field name must start with a letter or underscore and contain only letters, numbers, and underscores.')


class InventoryItem(models.Model):
    """Main inventory item with dynamic fields and real-time calculations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_items')
    layout = models.ForeignKey(InventoryLayout, on_delete=models.CASCADE, related_name='items')
    
    # Core fields (always present)
    product_name = models.CharField(max_length=200)
    sku_code = models.CharField(max_length=100)
    status = models.ForeignKey(InventoryStatus, on_delete=models.PROTECT, related_name='items')
    
    # Dynamic data storage
    data = JSONField(default=dict, help_text="Dynamic field values")
    calculated_data = JSONField(default=dict, help_text="Auto-calculated values")
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['sku_code']),
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
        ]
        unique_together = ['user', 'sku_code']
        verbose_name = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'
    
    def __str__(self):
        return f"{self.product_name} ({self.sku_code})"
    
    def get_value(self, field_name: str) -> Any:
        """Get value for a specific field"""
        # Check core fields first
        if hasattr(self, field_name):
            return getattr(self, field_name)
        
        # Check dynamic data
        value = self.data.get(field_name, '')
        
        # Handle stored model instance data
        if isinstance(value, dict) and 'id' in value and 'name' in value:
            # This is a stored model instance, return the name for display
            return value['name']
        
        # Handle stored date strings - convert back to date objects if needed
        if isinstance(value, str) and field_name in ['expiry_date', 'created_date', 'updated_date']:
            try:
                from datetime import datetime
                # Try to parse as date
                return datetime.fromisoformat(value).date()
            except (ValueError, TypeError):
                # If parsing fails, return as string
                return value
        
        return value
    
    def get_all_data(self) -> Dict[str, Any]:
        """Get all data (core fields + dynamic data) as a dictionary"""
        data = {}
        
        # Add core fields
        data['product_name'] = self.product_name
        data['sku_code'] = self.sku_code
        data['status'] = self.status
        data['is_active'] = self.is_active
        data['created_at'] = self.created_at
        data['updated_at'] = self.updated_at
        
        # Add dynamic data
        for field_name, value in self.data.items():
            data[field_name] = self.get_value(field_name)
        
        return data
    
    def set_value(self, field_name: str, value: Any) -> None:
        """Set value for a specific field and trigger calculations"""
        # Handle core fields (but not properties)
        if hasattr(self, field_name) and not hasattr(type(self), field_name):
            setattr(self, field_name, value)
        else:
            # Handle dynamic fields - handle different types for JSON serialization
            if hasattr(value, 'as_tuple'):  # Check if it's a Decimal
                self.data[field_name] = float(value)
            elif hasattr(value, 'pk'):  # Check if it's a model instance
                # Store model instance as a dictionary with id and name
                self.data[field_name] = {
                    'id': value.pk,
                    'name': str(value)
                }
            elif hasattr(value, 'isoformat'):  # Check if it's a date/datetime
                # Convert date/datetime to ISO format string
                self.data[field_name] = value.isoformat()
            else:
                self.data[field_name] = value
        
        self.save()
        self.calculate_totals()
        
        # Trigger updates across all inventory documents and templates
        self.update_all_documents()

    def update_all_documents(self, skip_status_update=False):
        """Update all inventory documents and templates when data changes"""
        try:
            # Force recalculation of totals
            calculated_data = self.calculate_totals()
            
            # Update calculated data in the model
            self.calculated_data = calculated_data
            
            # Update status based on quantity (only if not explicitly setting status)
            if not skip_status_update:
                self._update_status_based_on_quantity()
            
            # Save the model to persist changes
            self.save(update_fields=['calculated_data', 'status', 'updated_at'])
            
            # Update any cached data
            self.refresh_from_db()
            
            # Update related documents and templates
            self._update_related_documents()
            
            # Clear Django's cache for this item
            from django.core.cache import cache
            cache_keys_to_clear = [
                f'inventory_item_{self.id}',
                f'inventory_user_{self.user.id}',
                f'inventory_layout_{self.layout.id}',
                f'inventory_status_{self.status.id}',
            ]
            for key in cache_keys_to_clear:
                cache.delete(key)
            
            # Log the update for tracking
            from .models import InventoryLog
            InventoryLog.objects.create(
                user=self.user,
                item=self,
                log_type='field_update',
                description=f'Updated item data - Quantity: {self.get_value("quantity")}, Unit Price: ₦{self.get_value("unit_price")}, Total: ₦{self.total_value}',
                details={
                    'quantity': self.get_value("quantity"),
                    'unit_price': self.get_value("unit_price"),
                    'total_value': self.total_value,
                    'status': self.status.name,
                    'status_display': self.status.display_name,
                    'updated_at': self.updated_at.isoformat()
                }
            )
            
            print(f"✅ Updated all documents for item {self.id}: {self.product_name}")
            print(f"   Quantity: {self.get_value('quantity')}")
            print(f"   Unit Price: ₦{self.get_value('unit_price')}")
            print(f"   Total: ₦{self.total_value}")
            print(f"   Status: {self.status.display_name}")
            
        except Exception as e:
            print(f"❌ Error updating documents for item {self.id}: {str(e)}")
    
    def _update_status_based_on_quantity(self):
        """Update item status based on current quantity"""
        try:
            quantity = self.quantity
            minimum_threshold = self.get_value('minimum_threshold') or 0
            
            # Get status objects
            from .models import InventoryStatus
            in_stock_status = InventoryStatus.objects.get(name='in_stock')
            low_stock_status = InventoryStatus.objects.get(name='low_stock')
            out_of_stock_status = InventoryStatus.objects.get(name='out_of_stock')
            
            # Update status based on quantity
            if quantity <= 0:
                self.status = out_of_stock_status
            elif minimum_threshold > 0 and quantity <= minimum_threshold:
                self.status = low_stock_status
            else:
                self.status = in_stock_status
                
        except Exception as e:
            print(f"⚠️ Warning: Error updating status for item {self.id}: {str(e)}")
    
    def _update_related_documents(self):
        """Update related documents, templates, and exports"""
        try:
            # Update any cached exports that include this item
            from .models import InventoryExport
            exports = InventoryExport.objects.filter(
                user=self.user,
                layout=self.layout
            )
            
            for export in exports:
                # Mark export as needing refresh
                export.export_settings['needs_refresh'] = True
                export.save(update_fields=['export_settings'])
            
            # Update any templates that reference this item
            from .models import InventoryTemplate
            templates = InventoryTemplate.objects.filter(
                user=self.user
            )
            
            for template in templates:
                # Update template if it contains this item's data
                if 'items' in template.field_config:
                    template.updated_at = self.updated_at
                    template.save(update_fields=['updated_at'])
            
            # Clear any cached data for this item
            self._clear_cached_data()
            
        except Exception as e:
            print(f"⚠️ Warning: Error updating related documents: {str(e)}")
    
    def _clear_cached_data(self):
        """Clear any cached data for this item"""
        try:
            # Clear any Django cache entries for this item
            from django.core.cache import cache
            cache_keys = [
                f'inventory_item_{self.id}',
                f'inventory_detail_{self.id}',
                f'inventory_export_{self.user.id}_{self.layout.id}',
                f'inventory_print_{self.id}',
            ]
            
            for key in cache_keys:
                cache.delete(key)
                
        except Exception as e:
            print(f"⚠️ Warning: Error clearing cache: {str(e)}")
    
    def calculate_totals(self) -> Dict[str, Any]:
        """Calculate totals based on layout configuration"""
        if not self.layout.supports_calculations():
            return {}
        
        calculated = {}
        
        # Extract numeric values from data
        quantity = self._extract_number(self.get_value('quantity') or self.get_value('Quantity'))
        unit_price = self._extract_number(self.get_value('unit_price') or self.get_value('Unit Price'))
        
        if quantity is not None and unit_price is not None:
            total = quantity * unit_price
            # Convert Decimal to float for JSON serialization
            if hasattr(total, 'as_tuple'):  # Check if it's a Decimal
                total = float(total)
            calculated['total'] = total
            calculated['Total'] = total
        
        # Apply custom calculation rules
        for rule in self.layout.calculation_rules.get('rules', []):
            if rule.get('enabled', False):
                result = self._apply_calculation_rule(rule)
                if result is not None:
                    calculated[rule['output_field']] = result
        
        self.calculated_data = calculated
        self.save()
        return calculated
    
    def _extract_number(self, value) -> Optional[float]:
        """Extract numeric value from mixed input with enhanced sanitization"""
        if value is None or value == '':
            return None
        
        if isinstance(value, (int, float, Decimal)):
            return float(value)
        
        # Convert to string and clean
        value_str = str(value).strip()
        
        # Remove common currency symbols
        value_str = re.sub(r'[₦$€£¥₹₿₤₩₪₫₭₮₯₰₱₲₳₴₵₶₷₸₹₺₻₼₽₾₿]', '', value_str)
        
        # Remove common text patterns like "each", "pcs", "units", etc.
        value_str = re.sub(r'\b(each|pcs|pieces|units|items|nos|qty|quantity)\b', '', value_str, flags=re.IGNORECASE)
        
        # Remove other common text patterns
        value_str = re.sub(r'\b(price|cost|amount|value|total)\b', '', value_str, flags=re.IGNORECASE)
        
        # Remove parentheses and their contents
        value_str = re.sub(r'\([^)]*\)', '', value_str)
        
        # Remove extra spaces and keep only numbers, decimals, and minus signs
        value_str = re.sub(r'[^\d.-]', '', value_str)
        
        # Handle multiple decimal points (keep only the first one)
        parts = value_str.split('.')
        if len(parts) > 2:
            value_str = parts[0] + '.' + ''.join(parts[1:])
        
        try:
            result = float(value_str) if value_str else None
            # Validate reasonable range
            if result is not None and (result < -999999999 or result > 999999999):
                return None
            return result
        except ValueError:
            return None
    
    def _apply_calculation_rule(self, rule: Dict) -> Optional[float]:
        """Apply a custom calculation rule"""
        try:
            formula = rule.get('formula', '')
            if not formula:
                return None
            
            # Replace field names with actual values
            for field_name in rule.get('input_fields', []):
                field_value = self._extract_number(self.get_value(field_name)) or 0
                formula = formula.replace(f'{{{field_name}}}', str(field_value))
            
            # Safe evaluation (only basic math operations)
            allowed_chars = set('0123456789+-*/(). ')
            if all(c in allowed_chars for c in formula):
                return eval(formula)
            
        except Exception:
            pass
        
        return None
    
    @property
    def total_value(self) -> float:
        """Get total value for this item"""
        return self.calculated_data.get('total', 0)
    
    @property
    def quantity(self) -> float:
        """Get quantity value"""
        return self._extract_number(self.data.get('quantity') or self.data.get('Quantity')) or 0
    
    @property
    def unit_price(self) -> float:
        """Get unit price value"""
        return self._extract_number(self.data.get('unit_price') or self.data.get('Unit Price')) or 0
    
    def format_value(self, value, field_type):
        """Format a value based on field type"""
        if field_type == 'number' or field_type == 'decimal':
            num = self._extract_number(value)
            if num is not None:
                if field_type == 'decimal':
                    return f"₦{num:,.2f}"
                else:
                    return f"{num:,.0f}"
        return str(value) if value is not None else ''


class InventoryTransaction(models.Model):
    """Track all inventory movements and changes"""
    TRANSACTION_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Stock Adjustment'),
        ('transfer', 'Transfer'),
        ('return', 'Return'),
        ('status_change', 'Status Change'),
        ('price_change', 'Price Change'),
        ('field_update', 'Field Update'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_transactions')
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='transactions')
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity_change = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Before and after values
    quantity_before = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity_after = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status_before = models.ForeignKey(InventoryStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions_before')
    status_after = models.ForeignKey(InventoryStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions_after')
    
    # Field changes
    field_changes = JSONField(default=dict, help_text="Track field value changes")
    
    # Transaction details
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-transaction_date']
        verbose_name = 'Inventory Transaction'
        verbose_name_plural = 'Inventory Transactions'
    
    def __str__(self):
        return f"{self.transaction_type} - {self.item.product_name}"


class InventoryLog(models.Model):
    """Activity log for inventory operations"""
    LOG_TYPES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('stock_adjustment', 'Stock Adjustment'),
        ('status_change', 'Status Change'),
        ('import', 'Import'),
        ('export', 'Export'),
        ('layout_change', 'Layout Change'),
        ('field_update', 'Field Update'),
        ('calculation', 'Calculation'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_logs')
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, null=True, blank=True, related_name='logs')
    layout = models.ForeignKey(InventoryLayout, on_delete=models.CASCADE, null=True, blank=True, related_name='logs')
    
    description = models.CharField(max_length=500)
    details = JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Inventory Log'
        verbose_name_plural = 'Inventory Logs'
    
    def __str__(self):
        return f"{self.log_type} - {self.description}"


class ImportedInventoryFile(models.Model):
    """Track imported inventory data files"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='imported_inventory_files')
    layout = models.ForeignKey(InventoryLayout, on_delete=models.CASCADE, related_name='imports')
    
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.PositiveIntegerField(default=0)
    file_type = models.CharField(max_length=10, choices=[
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ])
    
    # Import configuration
    column_mapping = JSONField(default=dict, help_text="Column mapping from file to layout")
    import_settings = JSONField(default=dict, help_text="Import configuration")
    
    # Import statistics
    total_rows = models.PositiveIntegerField(default=0)
    imported_rows = models.PositiveIntegerField(default=0)
    failed_rows = models.PositiveIntegerField(default=0)
    error_log = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Imported Inventory File'
        verbose_name_plural = 'Imported Inventory Files'
    
    def __str__(self):
        return f"Import {self.file_name} - {self.status}"


class InventoryExport(models.Model):
    """Track exported inventory data"""
    EXPORT_FORMATS = [
        ('excel', 'Excel (.xlsx)'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('json', 'JSON'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_exports')
    layout = models.ForeignKey(InventoryLayout, on_delete=models.CASCADE, related_name='exports')
    format = models.CharField(max_length=10, choices=EXPORT_FORMATS)
    
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    
    # Export configuration
    filters = JSONField(default=dict, blank=True)
    include_calculations = models.BooleanField(default=True)
    include_branding = models.BooleanField(default=True)
    export_settings = JSONField(default=dict, help_text="Export-specific settings")
    
    total_items = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Inventory Export'
        verbose_name_plural = 'Inventory Exports'
    
    def __str__(self):
        return f"Export {self.layout.name} - {self.format}"


class InventoryTemplate(models.Model):
    """Saved inventory templates for quick setup"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_templates')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Template configuration
    layout_config = JSONField(default=dict, help_text="Layout configuration")
    field_config = JSONField(default=dict, help_text="Field configuration")
    branding_config = JSONField(default=dict, help_text="Branding configuration")
    
    # Template metadata
    is_public = models.BooleanField(default=False, help_text="Available to all users")
    category = models.CharField(max_length=100, blank=True)
    tags = JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name']
        verbose_name = 'Inventory Template'
        verbose_name_plural = 'Inventory Templates'
    
    def __str__(self):
        return f"{self.name} ({self.user.email})"


# Legacy models for backward compatibility (simplified)
class InventoryProduct(models.Model):
    """Legacy model - kept for backward compatibility"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='legacy_inventory_products')
    product_name = models.CharField(max_length=200)
    sku_code = models.CharField(max_length=100)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Legacy Inventory Product'
        verbose_name_plural = 'Legacy Inventory Products'
    
    def __str__(self):
        return f"{self.product_name} ({self.sku_code})"


class InventoryCategory(models.Model):
    """Legacy model - kept for backward compatibility"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#007bff")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='legacy_inventory_categories')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Legacy Inventory Category'
        verbose_name_plural = 'Legacy Inventory Categories'
    
    def __str__(self):
        return self.name
