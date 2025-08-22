from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    InventoryLayout, InventoryItem, InventoryStatus, InventoryCustomField,
    InventoryTransaction, InventoryLog, ImportedInventoryFile, InventoryExport,
    InventoryTemplate,
    # Legacy models
    InventoryProduct, InventoryCategory
)


@admin.register(InventoryStatus)
class InventoryStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'color_display', 'is_active', 'sort_order']
    list_filter = ['is_active']
    search_fields = ['name', 'display_name']
    ordering = ['sort_order', 'name']
    
    def color_display(self, obj):
        """Display color as a colored square"""
        return format_html(
            '<div style="background-color: {}; width: 20px; height: 20px; border-radius: 3px;"></div>',
            obj.color
        )
    color_display.short_description = 'Color'
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(InventoryLayout)
class InventoryLayoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_default', 'auto_calculate', 'show_totals', 'created_at']
    list_filter = ['is_default', 'auto_calculate', 'show_totals', 'created_at']
    search_fields = ['name', 'user__email', 'company_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-is_default', '-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description', 'is_default')
        }),
        ('Table Configuration', {
            'fields': ('auto_calculate', 'show_totals', 'show_grand_total', 'allow_inline_editing', 'allow_bulk_operations', 'enable_sorting', 'enable_filtering')
        }),
        ('Branding', {
            'fields': ('company_name', 'company_address', 'company_phone', 'company_email', 'company_logo', 'primary_color', 'secondary_color')
        }),
        ('Advanced', {
            'fields': ('columns', 'column_visibility', 'column_widths', 'column_order', 'calculation_fields', 'calculation_rules', 'export_settings'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'sku_code', 'status', 'quantity_display', 'unit_price_display', 'total_value_display', 'user', 'layout', 'created_at']
    list_filter = ['status', 'is_active', 'created_at', 'layout']
    search_fields = ['product_name', 'sku_code', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'total_value_display']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'layout', 'product_name', 'sku_code', 'status', 'is_active')
        }),
        ('Dynamic Data', {
            'fields': ('data', 'calculated_data'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def quantity_display(self, obj):
        """Display quantity with formatting"""
        quantity = obj.quantity
        if quantity == 0:
            return format_html('<span style="color: red;">{}</span>', quantity)
        elif quantity <= 5:
            return format_html('<span style="color: orange;">{}</span>', quantity)
        else:
            return quantity
    quantity_display.short_description = 'Quantity'
    
    def unit_price_display(self, obj):
        """Display unit price with formatting"""
        price = obj.unit_price
        if price > 0:
            return f"${price:.2f}"
        return "-"
    unit_price_display.short_description = 'Unit Price'
    
    def total_value_display(self, obj):
        """Display total value with formatting"""
        total = obj.total_value
        if total > 0:
            return f"${total:.2f}"
        return "-"
    total_value_display.short_description = 'Total Value'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'layout', 'status')


@admin.register(InventoryCustomField)
class InventoryCustomFieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'field_type', 'user', 'layout', 'is_required', 'is_visible', 'sort_order']
    list_filter = ['field_type', 'is_required', 'is_unique', 'is_visible', 'is_calculation_field', 'created_at']
    search_fields = ['name', 'display_name', 'user__email']
    ordering = ['user', 'sort_order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'layout', 'name', 'display_name', 'field_type')
        }),
        ('Configuration', {
            'fields': ('is_required', 'is_unique', 'default_value', 'help_text', 'width')
        }),
        ('Validation', {
            'fields': ('min_value', 'max_value', 'min_length', 'max_length'),
            'classes': ('collapse',)
        }),
        ('Display', {
            'fields': ('is_visible', 'sort_order', 'choices')
        }),
        ('Calculation', {
            'fields': ('is_calculation_field', 'calculation_formula'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'layout')


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ['item', 'transaction_type', 'quantity_change', 'quantity_before', 'quantity_after', 'user', 'transaction_date']
    list_filter = ['transaction_type', 'transaction_date', 'item__layout']
    search_fields = ['item__product_name', 'item__sku_code', 'user__email', 'reference']
    readonly_fields = ['transaction_date']
    ordering = ['-transaction_date']
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('user', 'item', 'transaction_type', 'quantity_change', 'unit_price', 'total_value')
        }),
        ('Before/After', {
            'fields': ('quantity_before', 'quantity_after', 'status_before', 'status_after')
        }),
        ('Field Changes', {
            'fields': ('field_changes',),
            'classes': ('collapse',)
        }),
        ('Additional Info', {
            'fields': ('reference', 'notes', 'transaction_date')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'item', 'status_before', 'status_after')


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ['log_type', 'description', 'user', 'item', 'layout', 'created_at']
    list_filter = ['log_type', 'created_at', 'item__layout']
    search_fields = ['description', 'user__email', 'item__product_name']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Log Information', {
            'fields': ('user', 'log_type', 'description')
        }),
        ('Related Objects', {
            'fields': ('item', 'layout')
        }),
        ('Details', {
            'fields': ('details', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'item', 'layout')


@admin.register(ImportedInventoryFile)
class ImportedInventoryFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'user', 'layout', 'file_type', 'status', 'total_rows', 'imported_rows', 'failed_rows', 'created_at']
    list_filter = ['status', 'file_type', 'created_at', 'layout']
    search_fields = ['file_name', 'user__email']
    readonly_fields = ['created_at', 'completed_at', 'file_size']
    ordering = ['-created_at']
    
    fieldsets = (
        ('File Information', {
            'fields': ('user', 'layout', 'file_name', 'file_path', 'file_size', 'file_type')
        }),
        ('Import Configuration', {
            'fields': ('column_mapping', 'import_settings'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_rows', 'imported_rows', 'failed_rows', 'error_log')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'completed_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'layout')


@admin.register(InventoryExport)
class InventoryExportAdmin(admin.ModelAdmin):
    list_display = ['layout', 'format', 'user', 'total_items', 'file_size', 'include_calculations', 'include_branding', 'created_at']
    list_filter = ['format', 'include_calculations', 'include_branding', 'created_at']
    search_fields = ['layout__name', 'user__email']
    readonly_fields = ['created_at', 'file_size']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Export Information', {
            'fields': ('user', 'layout', 'format', 'file_path', 'file_size')
        }),
        ('Configuration', {
            'fields': ('include_calculations', 'include_branding', 'filters', 'export_settings')
        }),
        ('Statistics', {
            'fields': ('total_items', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'layout')


@admin.register(InventoryTemplate)
class InventoryTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'category', 'is_public', 'created_at']
    list_filter = ['is_public', 'category', 'created_at']
    search_fields = ['name', 'description', 'user__email']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description')
        }),
        ('Configuration', {
            'fields': ('layout_config', 'field_config', 'branding_config'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_public', 'category', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Legacy models for backward compatibility
@admin.register(InventoryProduct)
class InventoryProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'sku_code', 'quantity_in_stock', 'unit_price', 'total_value', 'user', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['product_name', 'sku_code', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(InventoryCategory)
class InventoryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color_display', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    def color_display(self, obj):
        """Display color as a colored square"""
        return format_html(
            '<div style="background-color: {}; width: 20px; height: 20px; border-radius: 3px;"></div>',
            obj.color
        )
    color_display.short_description = 'Color'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Admin site customization
admin.site.site_header = "Inventory Management System"
admin.site.site_title = "Inventory Admin"
admin.site.index_title = "Welcome to Inventory Management"
