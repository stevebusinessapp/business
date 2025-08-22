from rest_framework import serializers
from .models import Invoice, InvoiceItem


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'line_total']
        read_only_fields = ['line_total']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_date', 'due_date',
            'client_name', 'client_phone', 'client_email', 'client_address',
            'subtotal', 'total_tax', 'total_discount', 'shipping_fee', 'other_charges',
            'grand_total', 'amount_paid', 'balance_due', 'status', 'notes',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['invoice_number', 'subtotal', 'grand_total', 'balance_due', 'created_at', 'updated_at']


class InvoiceCreateSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, write_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'due_date', 'client_name', 'client_phone', 'client_email', 'client_address',
            'total_tax', 'total_discount', 'shipping_fee', 'other_charges',
            'amount_paid', 'notes', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        invoice = Invoice.objects.create(**validated_data)
        
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        
        return invoice
