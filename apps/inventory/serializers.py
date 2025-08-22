from rest_framework import serializers
from .models import (
    InventoryLayout, InventoryItem, InventoryStatus, InventoryCustomField,
    InventoryTransaction, InventoryLog, ImportedInventoryFile, InventoryExport,
    # Legacy models
    InventoryProduct, InventoryCategory
)


class InventoryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryStatus
        fields = '__all__'


class InventoryLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryLayout
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class InventoryItemSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='status.display_name', read_only=True)
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class InventoryCustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCustomField
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class InventoryTransactionSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.product_name', read_only=True)
    status_before_display = serializers.CharField(source='status_before.display_name', read_only=True)
    status_after_display = serializers.CharField(source='status_after.display_name', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = '__all__'
        read_only_fields = ('user', 'transaction_date')


class InventoryLogSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.product_name', read_only=True)
    layout_name = serializers.CharField(source='layout.name', read_only=True)
    
    class Meta:
        model = InventoryLog
        fields = '__all__'
        read_only_fields = ('user', 'created_at')


class ImportedInventoryFileSerializer(serializers.ModelSerializer):
    layout_name = serializers.CharField(source='layout.name', read_only=True)
    
    class Meta:
        model = ImportedInventoryFile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'completed_at')


class InventoryExportSerializer(serializers.ModelSerializer):
    layout_name = serializers.CharField(source='layout.name', read_only=True)
    
    class Meta:
        model = InventoryExport
        fields = '__all__'
        read_only_fields = ('user', 'created_at')


# Legacy serializers for backward compatibility
class InventoryProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryProduct
        fields = '__all__'
        read_only_fields = ('user', 'total_value', 'created_at', 'updated_at')


class InventoryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCategory
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')
