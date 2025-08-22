from django import forms
from .models import Receipt, PAYMENT_CHOICES
from apps.invoices.models import Invoice

class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = [
            'invoice', 'client_name', 'client_phone', 'client_address', 'amount_received', 'amount_in_words', 'payment_method',
            'transaction_id', 'received_by', 'notes', 'custom_color'
        ]
        widgets = {
            'invoice': forms.Select(attrs={'class': 'form-control border', 'data-invoice-select': '1'}),
            'client_name': forms.TextInput(attrs={'class': 'form-control border', 'placeholder': 'Client Name'}),
            'client_phone': forms.TextInput(attrs={'class': 'form-control border', 'placeholder': 'Client Phone'}),
            'client_address': forms.TextInput(attrs={'class': 'form-control border', 'placeholder': 'Client Address'}),
            'amount_received': forms.NumberInput(attrs={'class': 'form-control border', 'step': '0.01', 'placeholder': 'Amount Received', 'readonly': 'readonly'}),
            'amount_in_words': forms.TextInput(attrs={'class': 'form-control border', 'placeholder': 'Amount in Words', 'readonly': 'readonly'}),
            'payment_method': forms.Select(choices=PAYMENT_CHOICES, attrs={'class': 'form-control border', 'placeholder': 'Payment Method'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control border', 'placeholder': 'Transaction ID (optional)'}),
            'received_by': forms.TextInput(attrs={'class': 'form-control border', 'placeholder': 'Received By', 'required': 'required'}),
            'notes': forms.Textarea(attrs={'class': 'form-control border', 'rows': 3, 'placeholder': 'Notes (optional)'}),
            'custom_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color border', 'placeholder': 'Pick a color'}),
        }

    def __init__(self, *args, **kwargs):
        invoice = kwargs.pop('invoice', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if invoice:
            self.fields['invoice'].initial = invoice.pk
            self.fields['client_name'].initial = invoice.client_name
            self.fields['client_phone'].initial = invoice.client_phone
            self.fields['client_address'].initial = invoice.client_address
        # Allow multiple receipts per invoice: show all invoices for the user
        if user is not None:
            self.fields['invoice'].queryset = Invoice.objects.filter(user=user)
        else:
            self.fields['invoice'].queryset = Invoice.objects.none()
        self.fields['invoice'].empty_label = 'Select Invoice'
        # Add data attributes for JS
        for inv in self.fields['invoice'].queryset:
            self.fields['invoice'].widget.choices.queryset = self.fields['invoice'].queryset
        # Ensure custom_color always has a valid default
        if not self.initial.get('custom_color'):
            self.initial['custom_color'] = '#000000'

    def clean_amount_received(self):
        amount = self.cleaned_data['amount_received']
        if amount <= 0:
            raise forms.ValidationError('Amount received must be greater than zero.')
        return amount

    def clean(self):
        cleaned = super().clean()
        invoice = cleaned.get('invoice')
        if invoice:
            if not cleaned.get('client_name'):
                cleaned['client_name'] = invoice.client_name
            if not cleaned.get('client_phone'):
                cleaned['client_phone'] = invoice.client_phone
            if not cleaned.get('client_address'):
                cleaned['client_address'] = invoice.client_address
        return cleaned
