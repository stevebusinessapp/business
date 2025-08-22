from django import forms
from django.forms import inlineformset_factory
from .models import Waybill, WaybillItem, WaybillTemplate, WaybillFieldTemplate
from decimal import Decimal
import json


class WaybillTemplateForm(forms.ModelForm):
    """Form for creating and editing waybill templates"""
    
    class Meta:
        model = WaybillTemplate
        fields = [
            'name', 'description', 'primary_color', 'secondary_color', 'text_color',
            'document_title', 'number_prefix', 'show_company_logo', 'show_company_details',
            'show_bank_details', 'show_signature', 'is_default'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Shipping Waybill, Delivery Note'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe when to use this template...'
            }),
            'primary_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'title': 'Choose primary color'
            }),
            'secondary_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'title': 'Choose secondary color'
            }),
            'text_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'title': 'Choose text color'
            }),
            'document_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'WAYBILL'
            }),
            'number_prefix': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'WB',
                'maxlength': '10'
            }),
            'show_company_logo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_company_details': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_bank_details': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_signature': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DynamicWaybillForm(forms.ModelForm):
    """Dynamic form for creating waybills based on template"""
    
    def __init__(self, *args, **kwargs):
        self.template = kwargs.pop('template', None)
        super().__init__(*args, **kwargs)
        
        if self.template:
            self._add_custom_fields()
    
    def _add_custom_fields(self):
        """Add custom fields based on template configuration"""
        custom_fields = self.template.get_default_custom_fields()
        
        for section_key, section_config in custom_fields.items():
            if section_config.get('type') == 'section':
                # Add section fields
                for field_key, field_config in section_config.get('fields', {}).items():
                    field_name = f"custom_{section_key}_{field_key}"
                    
                    # Create form field based on type
                    if field_config.get('type') == 'textarea':
                        field = forms.CharField(
                            required=field_config.get('required', False),
                            widget=forms.Textarea(attrs={
                                'class': 'form-control',
                                'rows': 3,
                                'placeholder': field_config.get('placeholder', ''),
                                'data-section': section_key,
                                'data-field': field_key,
                            }),
                            label=field_config.get('label', field_key.title()),
                            help_text=field_config.get('help_text', ''),
                        )
                    elif field_config.get('type') == 'number':
                        field = forms.CharField(
                            required=field_config.get('required', False),
                            widget=forms.TextInput(attrs={
                                'class': 'form-control',
                                'placeholder': field_config.get('placeholder', ''),
                                'data-section': section_key,
                                'data-field': field_key,
                            }),
                            label=field_config.get('label', field_key.title()),
                            help_text=field_config.get('help_text', ''),
                        )
                    elif field_config.get('type') == 'date':
                        field = forms.DateField(
                            required=field_config.get('required', False),
                            widget=forms.DateInput(attrs={
                                'type': 'date',
                                'class': 'form-control',
                                'data-section': section_key,
                                'data-field': field_key,
                            }),
                            label=field_config.get('label', field_key.title()),
                            help_text=field_config.get('help_text', ''),
                        )
                    else:  # Default to text
                        field = forms.CharField(
                            required=field_config.get('required', False),
                            widget=forms.TextInput(attrs={
                                'class': 'form-control',
                                'placeholder': field_config.get('placeholder', ''),
                                'data-section': section_key,
                                'data-field': field_key,
                            }),
                            label=field_config.get('label', field_key.title()),
                            help_text=field_config.get('help_text', ''),
                        )
                    
                    self.fields[field_name] = field
    
    def clean(self):
        """Process custom field data"""
        cleaned_data = super().clean()
        
        if self.template:
            custom_data = {}
            custom_fields = self.template.get_default_custom_fields()
            
            for section_key, section_config in custom_fields.items():
                if section_config.get('type') == 'section':
                    custom_data[section_key] = {}
                    for field_key, field_config in section_config.get('fields', {}).items():
                        field_name = f"custom_{section_key}_{field_key}"
                        if field_name in cleaned_data:
                            custom_data[section_key][field_key] = cleaned_data[field_name]
            
            cleaned_data['custom_data'] = custom_data
        
        return cleaned_data
    
    class Meta:
        model = Waybill
        fields = ['delivery_date', 'status', 'notes']
        widgets = {
            'delivery_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes...'
            })
        }


class WaybillFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All Status')] + Waybill.STATUS_CHOICES
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search waybills...'
        })
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    template = forms.ModelChoiceField(
        queryset=WaybillTemplate.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Templates"
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['template'].queryset = WaybillTemplate.objects.filter(user=user)


class WaybillFieldTemplateForm(forms.ModelForm):
    """Form for creating reusable field templates"""
    
    class Meta:
        model = WaybillFieldTemplate
        fields = ['name', 'label', 'field_type', 'is_required', 'placeholder', 'help_text', 'options']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'field_name (no spaces, use underscores)'
            }),
            'label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Field Label'
            }),
            'field_type': forms.Select(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'placeholder': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Placeholder text...'
            }),
            'help_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Help text for users...'
            }),
            'options': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'For select fields: {"option1": "Label 1", "option2": "Label 2"}'
            }),
        }
    
    def clean_options(self):
        options = self.cleaned_data.get('options')
        if options:
            try:
                # Try to parse as JSON
                parsed_options = json.loads(options)
                return parsed_options
            except json.JSONDecodeError:
                # If not JSON, treat as simple text
                return options
        return {}


# Dynamic Item Form Creator
def create_dynamic_item_form(template):
    """Create a dynamic form class for waybill items based on template"""
    
    columns = template.get_default_table_columns()
    
    class DynamicWaybillItemForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            for column in columns:
                field_name = column['name']
                field_type = column.get('type', 'text')
                
                if field_type == 'number':
                    field = forms.CharField(
                        required=False,
                        widget=forms.TextInput(attrs={
                            'class': 'form-control item-field',
                            'placeholder': column.get('placeholder', ''),
                            'data-column': field_name,
                        }),
                        label=column.get('label', field_name.title()),
                    )
                elif field_type == 'textarea':
                    field = forms.CharField(
                        required=False,
                        widget=forms.Textarea(attrs={
                            'class': 'form-control item-field',
                            'rows': 2,
                            'placeholder': column.get('placeholder', ''),
                            'data-column': field_name,
                        }),
                        label=column.get('label', field_name.title()),
                    )
                else:  # Default to text
                    field = forms.CharField(
                        required=False,
                        widget=forms.TextInput(attrs={
                            'class': 'form-control item-field',
                            'placeholder': column.get('placeholder', ''),
                            'data-column': field_name,
                        }),
                        label=column.get('label', field_name.title()),
                    )
                
                self.fields[field_name] = field
    
    return DynamicWaybillItemForm


# Custom formset for items (similar to invoice items)
class BaseWaybillItemFormSet(forms.BaseFormSet):
    def clean(self):
        """Custom validation to allow empty forms"""
        super().clean()
        
        # Don't validate if there are already errors
        if any(self.errors):
            return
        
        valid_forms = 0
        for form in self.forms:
            if hasattr(form, 'cleaned_data') and form.cleaned_data:
                # Check if form has any meaningful data
                has_data = any(value and str(value).strip() for value in form.cleaned_data.values())
                if has_data:
                    valid_forms += 1
        
        # We need at least one valid form for a waybill
        if valid_forms == 0:
            raise forms.ValidationError("Please add at least one item to the waybill.")
