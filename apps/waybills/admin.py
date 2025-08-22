from django.contrib import admin
from .models import Waybill, WaybillItem, WaybillTemplate, WaybillFieldTemplate


class WaybillItemInline(admin.TabularInline):
    model = WaybillItem
    extra = 1
    fields = ['item_data', 'row_order']
    readonly_fields = ['row_order']


@admin.register(Waybill)
class WaybillAdmin(admin.ModelAdmin):
    list_display = ['waybill_number', 'user', 'template', 'status', 'waybill_date', 'delivery_date']
    list_filter = ['status', 'waybill_date', 'template', 'user']
    search_fields = ['waybill_number', 'user__email', 'custom_data']
    readonly_fields = ['waybill_number', 'created_at', 'updated_at']
    inlines = [WaybillItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('waybill_number', 'user', 'template', 'waybill_date', 'delivery_date', 'status')
        }),
        ('Custom Data', {
            'fields': ('custom_data', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WaybillTemplate)
class WaybillTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'document_title', 'number_prefix', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at', 'user']
    search_fields = ['name', 'description', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'user', 'is_default')
        }),
        ('Document Settings', {
            'fields': ('document_title', 'number_prefix')
        }),
        ('Color Customization', {
            'fields': ('primary_color', 'secondary_color', 'text_color')
        }),
        ('Display Options', {
            'fields': ('show_company_logo', 'show_company_details', 'show_bank_details', 'show_signature')
        }),
        ('Custom Configuration', {
            'fields': ('custom_fields', 'table_columns'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WaybillItem)
class WaybillItemAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'waybill', 'row_order']
    list_filter = ['waybill__template', 'waybill__user']
    search_fields = ['item_data', 'waybill__waybill_number']
    readonly_fields = ['row_order']


@admin.register(WaybillFieldTemplate)
class WaybillFieldTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'label', 'field_type', 'is_required', 'created_at']
    list_filter = ['field_type', 'is_required', 'created_at']
    search_fields = ['name', 'label', 'help_text']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'label', 'field_type', 'is_required')
        }),
        ('Field Configuration', {
            'fields': ('placeholder', 'help_text', 'options')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
