from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
from django.forms import inlineformset_factory
from django.utils.safestring import mark_safe
from .models import (
    InventoryLayout, InventoryItem, InventoryStatus, InventoryCustomField,
    InventoryTransaction, InventoryLog, ImportedInventoryFile, InventoryExport,
    InventoryTemplate,
    # Legacy models
    InventoryProduct, InventoryCategory
)
from apps.accounts.models import User
import json
import re
from decimal import Decimal


class InventoryLayoutForm(forms.ModelForm):
    """Form for creating and editing inventory layouts"""
    
    class Meta:
        model = InventoryLayout
        fields = [
            'name', 'description', 'is_default', 'auto_calculate', 'show_totals', 
            'show_grand_total', 'allow_inline_editing', 'allow_bulk_operations',
            'enable_sorting', 'enable_filtering', 'company_name', 'company_address',
            'company_phone', 'company_email', 'primary_color', 'secondary_color'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter layout name (e.g., Product Inventory)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe this layout...'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Company Name'
            }),
            'company_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Company Address'
            }),
            'company_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'company_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'primary_color': forms.TextInput(attrs={
                'class': 'form-control color-picker',
                'type': 'color'
            }),
            'secondary_color': forms.TextInput(attrs={
                'class': 'form-control color-picker',
                'type': 'color'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Set user-specific choices
            pass
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if self.user:
            existing = InventoryLayout.objects.filter(user=self.user, name=name)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError('A layout with this name already exists.')
        return name


class InventoryItemForm(forms.ModelForm):
    """Comprehensive form for inventory items with all standard fields"""
    
    class Meta:
        model = InventoryItem
        fields = ['product_name', 'sku_code', 'status', 'is_active']
        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product Name'
            }),
            'sku_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SKU Code'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    # Dynamic fields that will be stored in the data JSONField
    category = forms.ModelChoiceField(
        queryset=InventoryCategory.objects.none(),
        required=False,
        empty_label="Select a category or leave blank",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Select a category'
        })
    )
    supplier = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name of the supplier'
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Detailed description of the product'
        })
    )
    quantity_in_stock = forms.DecimalField(
        required=True,  # Changed from False to True
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Current available quantity'
        })
    )
    minimum_threshold = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Alert when stock falls below this level'
        })
    )
    unit_price = forms.DecimalField(
        required=True,  # Changed from False to True
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Cost per unit'
        })
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Where the product is stored'
        })
    )
    expiry_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Expiration date (if applicable)'
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional notes or comments'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.layout = kwargs.pop('layout', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Set user-specific choices
            self.fields['status'].queryset = InventoryStatus.objects.filter(is_active=True)
            self.fields['category'].queryset = InventoryCategory.objects.filter(user=self.user, is_active=True)
        
        # Set initial values for existing instance
        if self.instance and self.instance.pk:
            # Load data from the dynamic data field
            if hasattr(self.instance, 'data') and self.instance.data:
                for field_name, value in self.instance.data.items():
                    # Map layout field names back to form field names
                    form_field_name = field_name
                    if field_name == 'quantity':
                        form_field_name = 'quantity_in_stock'
                    
                    if form_field_name in self.fields:
                        # Handle stored model instance data
                        if isinstance(value, dict) and 'id' in value and 'name' in value:
                            # This is a stored model instance, try to get the actual model instance
                            try:
                                if form_field_name == 'category':
                                    model_instance = InventoryCategory.objects.get(pk=value['id'])
                                    self.fields[form_field_name].initial = model_instance
                                else:
                                    # For other model fields, just use the name for display
                                    self.fields[form_field_name].initial = value['name']
                            except:
                                # If model instance not found, use the name
                                self.fields[form_field_name].initial = value['name']
                        elif isinstance(value, str) and form_field_name in ['expiry_date']:
                            # Handle stored date strings
                            try:
                                from datetime import datetime
                                date_obj = datetime.fromisoformat(value).date()
                                self.fields[form_field_name].initial = date_obj
                            except (ValueError, TypeError):
                                # If parsing fails, use as string
                                self.fields[form_field_name].initial = value
                        else:
                            self.fields[form_field_name].initial = value
    
    def clean_sku_code(self):
        sku_code = self.cleaned_data.get('sku_code')
        if self.user:
            existing = InventoryItem.objects.filter(user=self.user, sku_code=sku_code)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError('An item with this SKU code already exists.')
        return sku_code

    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure quantity and unit_price are present
        quantity = cleaned_data.get('quantity_in_stock')
        unit_price = cleaned_data.get('unit_price')
        
        if quantity is None or quantity == '':
            raise ValidationError('Quantity is required.')
        if unit_price is None or unit_price == '':
            raise ValidationError('Unit price is required.')
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.layout:
            instance.layout = self.layout
        
        if self.user:
            instance.user = self.user
        
        # Extract dynamic field data and handle serialization
        dynamic_data = {}
        
        # Define all possible dynamic fields with their mappings
        field_mappings = {
            'quantity_in_stock': 'quantity',
            'unit_price': 'unit_price',
            'supplier': 'supplier',
            'location': 'location',
            'description': 'description',
            'notes': 'notes',
            'category': 'category',
            'minimum_threshold': 'minimum_threshold',
            'expiry_date': 'expiry_date',
        }
        
        # Process all dynamic fields, including empty ones
        for form_field, layout_field in field_mappings.items():
            value = self.cleaned_data.get(form_field)
            
            # Handle different types of values for JSON serialization
            if value is None or value == '':
                # Set appropriate default values for empty fields
                if layout_field in ['quantity', 'unit_price', 'minimum_threshold']:
                    dynamic_data[layout_field] = 0.0
                else:
                    dynamic_data[layout_field] = ''
            elif hasattr(value, 'as_tuple'):  # Check if it's a Decimal
                dynamic_data[layout_field] = float(value)
            elif hasattr(value, 'pk'):  # Check if it's a model instance
                # Store model instance as a dictionary with id and name
                dynamic_data[layout_field] = {
                    'id': value.pk,
                    'name': str(value)
                }
            elif hasattr(value, 'isoformat'):  # Check if it's a date/datetime
                # Convert date/datetime to ISO format string
                dynamic_data[layout_field] = value.isoformat()
            else:
                dynamic_data[layout_field] = value
        
        # Set the dynamic data
        instance.data = dynamic_data
        
        if commit:
            # Save the instance
            instance.save()
            
            # Calculate totals if the model supports it
            if hasattr(instance, 'calculate_totals'):
                instance.calculate_totals()
            
            # Trigger updates across all documents and templates
            if hasattr(instance, 'update_all_documents'):
                instance.update_all_documents()
        
        return instance


class InventoryCustomFieldForm(forms.ModelForm):
    """Form for creating and editing custom fields"""
    
    class Meta:
        model = InventoryCustomField
        fields = [
            'name', 'display_name', 'field_type', 'is_required', 'is_unique',
            'default_value', 'help_text', 'choices', 'min_value', 'max_value',
            'min_length', 'max_length', 'is_visible', 'sort_order', 'width',
            'is_calculation_field', 'calculation_formula'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'field_name (no spaces)'
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Display Name'
            }),
            'field_type': forms.Select(attrs={'class': 'form-control'}),
            'default_value': forms.TextInput(attrs={'class': 'form-control'}),
            'help_text': forms.TextInput(attrs={'class': 'form-control'}),
            'choices': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'One choice per line'
            }),
            'min_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_length': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_length': forms.NumberInput(attrs={'class': 'form-control'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'width': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 100px, 20%'
            }),
            'calculation_formula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., {quantity} * {unit_price} * 0.1'
            }),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_unique': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_calculation_field': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.layout = kwargs.pop('layout', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Set user-specific choices
            pass
        
        if self.layout:
            self.fields['layout'].initial = self.layout
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if self.user:
            existing = InventoryCustomField.objects.filter(user=self.user, name=name)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError('A field with this name already exists.')
        
        # Validate field name format
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            raise ValidationError('Field name must start with a letter or underscore and contain only letters, numbers, and underscores.')
        
        return name
    
    def clean_choices(self):
        choices = self.cleaned_data.get('choices')
        field_type = self.cleaned_data.get('field_type')
        
        if field_type in ['select', 'multiselect'] and not choices:
            raise ValidationError('Select fields must have choices defined.')
        
        if choices:
            # Convert textarea input to list
            choice_list = [choice.strip() for choice in choices.split('\n') if choice.strip()]
            return choice_list
        
        return []
    
    def clean(self):
        cleaned_data = super().clean()
        field_type = cleaned_data.get('field_type')
        min_value = cleaned_data.get('min_value')
        max_value = cleaned_data.get('max_value')
        min_length = cleaned_data.get('min_length')
        max_length = cleaned_data.get('max_length')
        
        if field_type in ['number', 'decimal']:
            if min_value and max_value and min_value > max_value:
                raise ValidationError("Minimum value cannot be greater than maximum value.")
        
        if min_length and max_length and min_length > max_length:
            raise ValidationError("Minimum length cannot be greater than maximum length.")
        
        return cleaned_data


class InventoryTransactionForm(forms.ModelForm):
    """Form for inventory transactions"""
    
    class Meta:
        model = InventoryTransaction
        fields = ['transaction_type', 'quantity_change', 'unit_price', 'reference', 'notes']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity_change': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Quantity change (positive for in, negative for out)'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Unit price (optional)'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reference (invoice, PO, etc.)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Transaction notes'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.item = kwargs.pop('item', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.item:
            # Pre-fill with item data
            self.fields['unit_price'].initial = self.item.unit_price


class InventorySearchForm(forms.Form):
    """Form for searching and filtering inventory"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products, SKU, description...'
        })
    )
    status = forms.ModelChoiceField(
        queryset=InventoryStatus.objects.filter(is_active=True),
        required=False,
        empty_label="All Statuses",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    layout = forms.ModelChoiceField(
        queryset=InventoryLayout.objects.none(),
        required=False,
        empty_label="All Layouts",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_quantity = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min quantity',
            'step': '0.01'
        })
    )
    max_quantity = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max quantity',
            'step': '0.01'
        })
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min price',
            'step': '0.01'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max price',
            'step': '0.01'
        })
    )
    is_active = forms.ChoiceField(
        choices=[
            ('', 'All Items'),
            ('true', 'Active Only'),
            ('false', 'Inactive Only'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['layout'].queryset = InventoryLayout.objects.filter(user=self.user)


class StockAdjustmentForm(forms.Form):
    """Form for adjusting stock quantities"""
    
    ADJUSTMENT_TYPES = [
        ('add', 'Add Stock'),
        ('subtract', 'Remove Stock'),
        ('set', 'Set Stock Level'),
    ]
    
    adjustment_type = forms.ChoiceField(
        choices=ADJUSTMENT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Quantity'
        })
    )
    unit_price = forms.DecimalField(
        required=False,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Unit price (optional)'
        })
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Reason for adjustment'
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Additional notes (optional)'
        })
    )
    reference = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Reference (invoice, PO, etc.)'
        })
    )


class InventoryImportForm(forms.ModelForm):
    """Form for importing inventory data"""
    
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls,.csv,.json'
        }),
        help_text="Supported formats: Excel (.xlsx, .xls), CSV, JSON"
    )
    
    class Meta:
        model = ImportedInventoryFile
        fields = ['file_name', 'layout', 'file_type']
        widgets = {
            'file_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'File name'
            }),
            'layout': forms.Select(attrs={'class': 'form-control'}),
            'file_type': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['layout'].queryset = InventoryLayout.objects.filter(user=self.user)


class InventoryExportForm(forms.Form):
    """Form for exporting inventory data"""
    
    EXPORT_FORMATS = [
        ('excel', 'Excel (.xlsx)'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('json', 'JSON'),
    ]
    
    format = forms.ChoiceField(
        choices=EXPORT_FORMATS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    layout = forms.ModelChoiceField(
        queryset=InventoryLayout.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    include_calculations = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    include_branding = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Filter fields
    category_filter = forms.ModelChoiceField(
        queryset=InventoryCategory.objects.none(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    include_low_stock = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    # Additional export options
    include_images = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    include_company_info = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    include_totals = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Search filter
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products, SKU, description...'
        })
    )
    
    # Status filter
    status_filter = forms.ModelChoiceField(
        queryset=InventoryStatus.objects.filter(is_active=True),
        required=False,
        empty_label="All Statuses",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Quantity filters
    min_quantity = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min quantity',
            'step': '0.01'
        })
    )
    max_quantity = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max quantity',
            'step': '0.01'
        })
    )
    
    # Price filters
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min price',
            'step': '0.01'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max price',
            'step': '0.01'
        })
    )
    
    filters = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['layout'].queryset = InventoryLayout.objects.filter(user=self.user)
            self.fields['category_filter'].queryset = InventoryCategory.objects.filter(user=self.user)


class StatusChangeForm(forms.Form):
    """Form for changing item status"""
    
    new_status = forms.ModelChoiceField(
        queryset=InventoryStatus.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Reason for status change (optional)'
        })
    )


class InventoryTemplateForm(forms.ModelForm):
    """Form for creating and editing inventory templates"""
    
    class Meta:
        model = InventoryTemplate
        fields = ['name', 'description', 'is_public', 'category', 'tags']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Template Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Template description...'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category (e.g., Retail, Manufacturing)'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tags separated by commas'
            }),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Set user-specific choices
            pass
    
    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if tags:
            # Convert comma-separated string to list
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            return tag_list
        return []


class LayoutColumnForm(forms.Form):
    """Form for configuring layout columns"""
    
    column_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Column Name'
        })
    )
    field_type = forms.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('number', 'Number'),
            ('decimal', 'Decimal'),
            ('date', 'Date'),
            ('datetime', 'Date & Time'),
            ('select', 'Dropdown'),
            ('boolean', 'Yes/No'),
            ('textarea', 'Long Text'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_visible = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    is_required = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    is_editable = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    width = forms.CharField(
        initial='auto',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Width (e.g., 100px, 20%)'
        })
    )


# Legacy forms for backward compatibility
class InventoryProductForm(forms.ModelForm):
    """Legacy form - kept for backward compatibility"""
    
    class Meta:
        model = InventoryProduct
        fields = ['product_name', 'sku_code', 'quantity_in_stock', 'unit_price', 'is_active']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'sku_code': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class InventoryCategoryForm(forms.ModelForm):
    """Legacy form - kept for backward compatibility"""
    
    class Meta:
        model = InventoryCategory
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'color': forms.TextInput(attrs={'class': 'form-control color-picker', 'type': 'color'}),
        }
