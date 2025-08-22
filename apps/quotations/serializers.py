from rest_framework import serializers
from .models import Quotation, QuotationItem, QuotationTemplate

class QuotationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'total', 'custom_fields']

class QuotationSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True, read_only=True)
    class Meta:
        model = Quotation
        fields = [
            'id', 'number', 'client', 'company', 'date', 'status', 'subtotal', 'tax', 'discount',
            'shipping', 'other_charges', 'total', 'terms', 'notes', 'template', 'color_scheme',
            'custom_fields', 'created_by', 'created_at', 'updated_at', 'items'
        ]

class QuotationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationTemplate
        fields = ['id', 'name', 'company', 'layout_config', 'branding', 'default_terms', 'created_by', 'created_at', 'updated_at']
