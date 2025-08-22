from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, InvoiceItem, InvoiceTemplate
from decimal import Decimal


class InvoiceForm(forms.ModelForm):
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
    amount_paid = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control money-input',
        'placeholder': '0.00'
    }))
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter templates by user and add an empty option
            self.fields['template'].queryset = InvoiceTemplate.objects.filter(user=user)
            self.fields['template'].empty_label = "Choose a template (optional)"
            
            # Set default template if user has one
            if not self.instance.pk:  # Only for new invoices
                default_template = InvoiceTemplate.objects.filter(user=user, is_default=True).first()
                if default_template:
                    self.fields['template'].initial = default_template
    
    class Meta:
        model = Invoice
        fields = [
            'template', 'due_date', 'client_name', 'client_phone', 'client_email', 
            'client_address', 'total_tax', 'total_discount', 
            'shipping_fee', 'other_charges', 'amount_paid', 'notes'
        ]
        widgets = {
            'template': forms.Select(attrs={
                'class': 'form-control',
                'data-toggle': 'tooltip',
                'title': 'Choose a template for colors and styling'
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter client name'
            }),
            'client_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'client_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'client_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter client address'
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
            'amount_paid': forms.TextInput(attrs={
                'class': 'form-control money-input',
                'placeholder': '0.00'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes...'
            })
        }
    
    def clean_total_tax(self):
        value = self.cleaned_data.get('total_tax')
        if value == '' or value is None:
            return Decimal('0')
        return Invoice.parse_number(value)
    
    def clean_total_discount(self):
        value = self.cleaned_data.get('total_discount')
        if value == '' or value is None:
            return Decimal('0')
        return Invoice.parse_number(value)
    
    def clean_shipping_fee(self):
        value = self.cleaned_data.get('shipping_fee')
        if value == '' or value is None:
            return Decimal('0')
        return Invoice.parse_number(value)
    
    def clean_other_charges(self):
        value = self.cleaned_data.get('other_charges')
        if value == '' or value is None:
            return Decimal('0')
        return Invoice.parse_number(value)
    
    def clean_amount_paid(self):
        value = self.cleaned_data.get('amount_paid')
        if value == '' or value is None:
            return Decimal('0')
        return Invoice.parse_number(value)


class InvoiceItemForm(forms.ModelForm):
    product_service = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': ' '
    }))
    description = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': ' '
    }))
    quantity = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': ' '
    }))
    unit_price = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control money-input',
        'placeholder': ' '
    }))
    
    class Meta:
        model = InvoiceItem
        fields = ['product_service', 'description', 'quantity', 'unit_price']
    
    def clean_quantity(self):
        value = self.cleaned_data.get('quantity')
        if value == '' or value is None:
            return Decimal('0')
        return Invoice.parse_number(value)
    
    def clean_unit_price(self):
        value = self.cleaned_data.get('unit_price')
        if value == '' or value is None:
            return Decimal('0')
        return Invoice.parse_number(value)


# Custom formset class to handle empty forms better
class BaseInvoiceItemFormSet(forms.BaseInlineFormSet):
    def clean(self):
        """Custom validation to allow empty forms"""
        super().clean()
        
        # Don't validate if there are already errors
        if any(self.errors):
            return
        
        valid_forms = 0
        for form in self.forms:
            # Skip deleted forms
            if self.can_delete and self._should_delete_form(form):
                continue
                
            # Check if form has meaningful data
            if hasattr(form, 'cleaned_data') and form.cleaned_data:
                product = form.cleaned_data.get('product_service', '').strip()
                description = form.cleaned_data.get('description', '').strip()
                quantity = form.cleaned_data.get('quantity', 0)
                unit_price = form.cleaned_data.get('unit_price', 0)
                
                # If form has any meaningful data, it should be valid
                if product or description or quantity or unit_price:
                    valid_forms += 1
        
        # We need at least one valid form for an invoice
        if valid_forms == 0:
            raise forms.ValidationError("Please add at least one item to the invoice.")
    
    def _should_delete_form(self, form):
        """Check if form should be deleted"""
        try:
            return form.cleaned_data.get('DELETE', False)
        except AttributeError:
            return False

# Formset for invoice items
InvoiceItemFormSet = inlineformset_factory(
    Invoice, 
    InvoiceItem,
    form=InvoiceItemForm,
    formset=BaseInvoiceItemFormSet,
    extra=1,  # Always provide one extra form for new items
    min_num=0,  # Allow invoices with no items temporarily
    validate_min=False,  # Don't enforce minimum during save
    can_delete=True,
    max_num=None,  # Allow unlimited items
    exclude=()  # Don't exclude any fields
)


class InvoiceFilterForm(forms.Form):
    # Custom status choices for search filter with user-friendly labels
    STATUS_CHOICES = [
        ('', 'All Status'),
        ('unpaid', 'Not Paid'),
        ('partial', 'Pending'),
        ('paid', 'Paid'),
        ('delivered', 'Delivered'),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search invoices...'
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


class InvoiceTemplateForm(forms.ModelForm):
    """Form for creating and editing invoice templates"""
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if self.user and name:
            # Check if another template with this name exists for this user
            existing = InvoiceTemplate.objects.filter(user=self.user, name=name)
            # Exclude current instance if editing
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(f'You already have a template named "{name}". Please choose a different name.')
        
        return name
    
    class Meta:
        model = InvoiceTemplate
        fields = [
            'name', 'description', 'primary_color', 'secondary_color', 
            'text_color', 'accent_color', 'show_company_logo', 'show_company_details',
            'show_bank_details', 'show_signature', 'document_title', 'number_prefix',
            'default_payment_terms', 'footer_text', 'is_default'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter template name (e.g., Professional Invoice)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description of this template'
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
            'accent_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'title': 'Choose accent color'
            }),
            'show_company_logo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_company_details': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_bank_details': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_signature': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'document_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'INVOICE'
            }),
            'number_prefix': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'INV',
                'maxlength': 10
            }),
            'default_payment_terms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Payment due within 30 days'
            }),
            'footer_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Thank you for your business!'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
