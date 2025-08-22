from django.contrib import admin
from django.utils.html import format_html
from .models import CompanyProfile, BankAccount


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = [
        'company_name', 'user', 'email', 'phone', 'currency_display',
        'has_logo', 'has_signature', 'created_at'
    ]
    list_filter = ['currency_code', 'created_at', 'updated_at']
    search_fields = ['company_name', 'user__username', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'logo_preview', 'signature_preview']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'company_name', 'email', 'phone', 'address', 'website')
        }),
        ('Visual Assets', {
            'fields': ('logo', 'logo_preview', 'signature', 'signature_preview'),
            'classes': ('collapse',)
        }),
        ('Financial Defaults', {
            'fields': ('default_tax', 'default_discount', 'default_shipping_fee', 'custom_charges'),
            'classes': ('collapse',)
        }),
        ('Currency Settings', {
            'fields': ('currency_code', 'currency_symbol')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def currency_display(self, obj):
        return f"{obj.currency_code} ({obj.currency_symbol})"
    currency_display.short_description = 'Currency'

    def has_logo(self, obj):
        if obj.logo:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_logo.short_description = 'Logo'
    has_logo.boolean = True

    def has_signature(self, obj):
        if obj.signature:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_signature.short_description = 'Signature'
    has_signature.boolean = True

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 100px;" />',
                obj.logo.url
            )
        return "No logo uploaded"
    logo_preview.short_description = 'Logo Preview'

    def signature_preview(self, obj):
        if obj.signature:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 100px;" />',
                obj.signature.url
            )
        return "No signature uploaded"
    signature_preview.short_description = 'Signature Preview'


class BankAccountInline(admin.TabularInline):
    model = BankAccount
    extra = 1
    fields = ['bank_name', 'account_name', 'account_number', 'is_default']


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = [
        'company', 'bank_name', 'account_name', 'account_number_masked',
        'is_default', 'created_at'
    ]
    list_filter = ['bank_name', 'is_default', 'created_at', 'updated_at']
    search_fields = [
        'company__company_name', 'bank_name', 'account_name', 'account_number'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Bank Information', {
            'fields': ('company', 'bank_name', 'account_name', 'account_number', 'is_default')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def account_number_masked(self, obj):
        """Display masked account number for security"""
        if len(obj.account_number) > 4:
            return f"****{obj.account_number[-4:]}"
        return obj.account_number
    account_number_masked.short_description = 'Account Number'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company', 'company__user')


# Update CompanyProfile admin to include bank accounts inline
CompanyProfileAdmin.inlines = [BankAccountInline]


# Custom admin site configuration
admin.site.site_header = "Multi-Purpose App Administration"
admin.site.site_title = "Multi-Purpose App Admin"
admin.site.index_title = "Welcome to Multi-Purpose App Administration"
