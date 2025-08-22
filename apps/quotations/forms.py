from django import forms
from django.forms import inlineformset_factory
from .models import Quotation, QuotationItem, QuotationTemplate
from apps.clients.models import Client
from decimal import Decimal


class QuotationForm(forms.ModelForm):
    total_tax = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control money-input',
        'placeholder': '0.00 or 5%'
    }))
    total_discount = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control money-input',
        'placeholder': '0.00 or 10%'
    }))
    shipping_fee = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control money-input',
        'placeholder': '0.00'
    }))
    other_charges = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control money-input',
        'placeholder': '0.00'
    }))
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter templates by user and add an empty option
            self.fields['template'].queryset = QuotationTemplate.objects.filter(user=user)
            self.fields['template'].empty_label = "Choose a template (optional)"
            
            # Set default template if user has one
            if not self.instance.pk:  # Only for new quotations
                default_template = QuotationTemplate.objects.filter(user=user, is_default=True).first()
                if default_template:
                    self.fields['template'].initial = default_template
            
            # Make client field optional and handle client filtering
            self.fields['client'].required = False
            self.fields['client'].empty_label = "Select a client (optional)"
            
            # Filter clients by user's company
            try:
                company_profile = user.company_profile
                if company_profile:
                    clients = Client.objects.filter(company=company_profile)
                    if clients.exists():
                        self.fields['client'].queryset = clients
                    else:
                        # If no clients exist, show a message
                        self.fields['client'].queryset = Client.objects.none()
                        self.fields['client'].empty_label = "No clients available - Create clients first"
                else:
                    self.fields['client'].queryset = Client.objects.none()
                    self.fields['client'].empty_label = "No company profile - Create company profile first"
            except Exception as e:
                self.fields['client'].queryset = Client.objects.none()
                self.fields['client'].empty_label = "Error loading clients"
    
    class Meta:
        model = Quotation
        fields = [
            'template', 'valid_until', 'client', 'total_tax', 'total_discount', 
            'shipping_fee', 'other_charges', 'terms', 'notes'
        ]
        widgets = {
            'template': forms.Select(attrs={
                'class': 'form-control',
                'data-toggle': 'tooltip',
                'title': 'Choose a template for colors and styling'
            }),
            'valid_until': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'client': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select client (optional)',
                'data-toggle': 'tooltip',
                'title': 'Choose a client or leave empty for general quotation'
            }),
            'total_tax': forms.TextInput(attrs={
                'class': 'form-control money-input',
                'placeholder': '0.00 or 5%'
            }),
            'total_discount': forms.TextInput(attrs={
                'class': 'form-control money-input',
                'placeholder': '0.00 or 10%'
            }),
            'shipping_fee': forms.TextInput(attrs={
                'class': 'form-control money-input',
                'placeholder': '0.00'
            }),
            'other_charges': forms.TextInput(attrs={
                'class': 'form-control money-input',
                'placeholder': '0.00'
            }),
            'terms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter terms and conditions'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter additional notes'
            }),
        }
    
    def clean_total_tax(self):
        value = self.cleaned_data.get('total_tax')
        return Quotation.parse_number(value)
    
    def clean_total_discount(self):
        value = self.cleaned_data.get('total_discount')
        return Quotation.parse_number(value)
    
    def clean_shipping_fee(self):
        value = self.cleaned_data.get('shipping_fee')
        return Quotation.parse_number(value)
    
    def clean_other_charges(self):
        value = self.cleaned_data.get('other_charges')
        return Quotation.parse_number(value)


class QuotationItemForm(forms.ModelForm):
    product_service = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Product or service name'
    }))
    description = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Detailed description'
    }))
    quantity = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control quantity-input',
        'placeholder': '1'
    }))
    unit_price = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control price-input',
        'placeholder': '0.00'
    }))
    
    class Meta:
        model = QuotationItem
        fields = ['product_service', 'description', 'quantity', 'unit_price']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert Decimal values to strings for proper display in CharField widgets
        if self.instance and self.instance.pk:
            if self.instance.quantity:
                self.initial['quantity'] = str(self.instance.quantity)
            if self.instance.unit_price:
                self.initial['unit_price'] = str(self.instance.unit_price)
    
    def clean_quantity(self):
        value = self.cleaned_data.get('quantity')
        if not value:
            return Decimal('0.00')
        
        # Handle string input with numbers and text
        if isinstance(value, str):
            # Extract numbers from string
            import re
            numbers = re.findall(r'\d+\.?\d*', value)
            if numbers:
                try:
                    return Decimal(numbers[0])
                except:
                    return Decimal('0.00')
            return Decimal('0.00')
        
        try:
            if isinstance(value, (int, float)):
                return Decimal(str(value))
            return Decimal(str(value).replace(',', ''))
        except:
            return Decimal('0.00')
    
    def clean_unit_price(self):
        value = self.cleaned_data.get('unit_price')
        if not value:
            return Decimal('0.00')
        
        # Handle string input with numbers and text
        if isinstance(value, str):
            # Extract numbers from string
            import re
            numbers = re.findall(r'\d+\.?\d*', value)
            if numbers:
                try:
                    return Decimal(numbers[0])
                except:
                    return Decimal('0.00')
            return Decimal('0.00')
        
        try:
            if isinstance(value, (int, float)):
                return Decimal(str(value))
            return Decimal(str(value).replace(',', ''))
        except:
            return Decimal('0.00')


class BaseQuotationItemFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        
        # Allow any form data to pass through - let the model handle validation
        # This ensures that even partial data gets saved
        pass
    
    def save_new(self, form, commit=True):
        """Override to ensure line items are saved properly"""
        instance = super().save_new(form, commit=False)
        if commit:
            instance.save()
        return instance


QuotationItemFormSet = inlineformset_factory(
    Quotation,
    QuotationItem,
    form=QuotationItemForm,
    formset=BaseQuotationItemFormSet,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False
)


class QuotationFilterForm(forms.Form):
    # Custom status choices for search filter with user-friendly labels
    STATUS_CHOICES = [
        ('', 'All Status'),
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search quotations...'
        })
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
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
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=False,
        empty_label="All Clients",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class QuotationTemplateForm(forms.ModelForm):
    primary_color = forms.CharField(
        label='Primary Color',
        widget=forms.TextInput(attrs={'type': 'color'}),
        required=False
    )
    secondary_color = forms.CharField(
        label='Secondary Color',
        widget=forms.TextInput(attrs={'type': 'color'}),
        required=False
    )
    text_color = forms.CharField(
        label='Text Color',
        widget=forms.TextInput(attrs={'type': 'color'}),
        required=False
    )
    accent_color = forms.CharField(
        label='Accent Color',
        widget=forms.TextInput(attrs={'type': 'color'}),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set help text for better UX
        self.fields['name'].help_text = "Give your template a descriptive name"
        self.fields['description'].help_text = "Optional description of this template"
        self.fields['document_title'].help_text = "Title that appears on the quotation document"
        self.fields['number_prefix'].help_text = "Prefix for quotation numbers (e.g., QT, QUOTE)"
        self.fields['default_terms'].help_text = "Default terms that will appear on new quotations"
        self.fields['footer_text'].help_text = "Text that appears at the bottom of quotations"
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Template name is required.")
        
        # Check for uniqueness per user
        user = getattr(self.instance, 'user', None)
        if user:
            existing = QuotationTemplate.objects.filter(
                user=user, 
                name=name
            ).exclude(pk=getattr(self.instance, 'pk', None))
            if existing.exists():
                raise forms.ValidationError("A template with this name already exists.")
        
        return name
    
    class Meta:
        model = QuotationTemplate
        fields = [
            'name', 'description', 'primary_color', 'secondary_color', 
            'text_color', 'accent_color', 'show_company_logo', 'show_company_details',
            'show_bank_details', 'show_signature', 'document_title', 'number_prefix',
            'default_terms', 'footer_text', 'is_default'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter template name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe this template'
            }),
            'document_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'QUOTATION'
            }),
            'number_prefix': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'QT'
            }),
            'default_terms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter default terms and conditions'
            }),
            'footer_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter footer text'
            }),
            'show_company_logo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_company_details': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_bank_details': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_signature': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
