from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Transaction, Ledger, Account, FinancialReport


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'type', 'amount_display', 'currency', 'company', 
        'transaction_date', 'source_app', 'is_reconciled', 'created_at'
    ]
    list_filter = [
        'type', 'source_app', 'is_reconciled', 'is_void', 
        'transaction_date', 'created_at', 'company'
    ]
    search_fields = ['title', 'description', 'notes', 'company__company_name']
    readonly_fields = ['id', 'net_amount', 'created_at', 'updated_at']
    date_hierarchy = 'transaction_date'
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'company', 'type', 'title', 'description')
        }),
        ('Financial Details', {
            'fields': ('amount', 'currency', 'tax', 'discount', 'net_amount')
        }),
        ('Source Information', {
            'fields': ('source_app', 'reference_id', 'reference_model')
        }),
        ('Additional Information', {
            'fields': ('transaction_date', 'notes', 'is_reconciled', 'is_void')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def amount_display(self, obj):
        """Display amount with color coding"""
        color = 'green' if obj.type == 'income' else 'red'
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            f"{obj.currency}{obj.amount:,.2f}"
        )
    amount_display.short_description = 'Amount'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company', 'user')


@admin.register(Ledger)
class LedgerAdmin(admin.ModelAdmin):
    list_display = [
        'company', 'year', 'month', 'month_name', 'total_income', 
        'total_expense', 'net_profit', 'outstanding_invoices'
    ]
    list_filter = ['year', 'month', 'company']
    search_fields = ['company__company_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-year', '-month']
    
    fieldsets = (
        ('Company Information', {
            'fields': ('company', 'year', 'month')
        }),
        ('Financial Totals', {
            'fields': ('total_income', 'total_expense', 'net_profit')
        }),
        ('Outstanding Amounts', {
            'fields': ('outstanding_invoices', 'pending_receipts')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = [
        'account_number', 'name', 'account_type', 'company', 
        'current_balance', 'is_active'
    ]
    list_filter = ['account_type', 'is_active', 'company']
    search_fields = ['name', 'account_number', 'company__company_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['account_number']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('company', 'name', 'account_number', 'account_type')
        }),
        ('Balance Information', {
            'fields': ('opening_balance', 'current_balance')
        }),
        ('Additional Information', {
            'fields': ('description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company')


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'report_type', 'company', 'start_date', 'end_date', 
        'created_by', 'created_at'
    ]
    list_filter = ['report_type', 'start_date', 'end_date', 'company']
    search_fields = ['title', 'company__company_name', 'created_by__username']
    readonly_fields = ['created_at', 'report_data_display']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Report Information', {
            'fields': ('company', 'report_type', 'title')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date')
        }),
        ('Report Data', {
            'fields': ('report_data_display', 'pdf_file', 'excel_file')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def report_data_display(self, obj):
        """Display report data in a readable format"""
        if obj.report_data:
            html = '<div style="max-height: 200px; overflow-y: auto;">'
            html += '<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px;">'
            html += str(obj.report_data)
            html += '</pre></div>'
            return mark_safe(html)
        return 'No data'
    report_data_display.short_description = 'Report Data'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company', 'created_by')


# Custom admin site configuration
admin.site.site_header = "Business App Administration"
admin.site.site_title = "Business App Admin"
admin.site.index_title = "Welcome to Business App Administration"
