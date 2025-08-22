from django.contrib import admin
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    readonly_fields = ('line_total',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client_name', 'invoice_date', 'due_date', 'grand_total', 'status', 'user']
    list_filter = ['status', 'invoice_date', 'user']
    search_fields = ['invoice_number', 'client_name', 'client_email']
    readonly_fields = ['invoice_number', 'subtotal', 'grand_total', 'balance_due', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'invoice_date', 'due_date', 'user')
        }),
        ('Client Information', {
            'fields': ('client_name', 'client_phone', 'client_email', 'client_address')
        }),
        ('Financial Information', {
            'fields': ('subtotal', 'total_tax', 'total_discount', 'shipping_fee', 'other_charges', 'grand_total')
        }),
        ('Payment Information', {
            'fields': ('amount_paid', 'balance_due', 'status')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at')
        })
    )


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'quantity', 'unit_price', 'line_total']
    list_filter = ['invoice__user']
    search_fields = ['description', 'invoice__invoice_number']
    readonly_fields = ['line_total']
