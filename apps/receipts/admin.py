from django.contrib import admin
from .models import Receipt

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = (
        'receipt_no', 'client_name', 'amount_received', 'payment_method', 'date_received', 'invoice', 'received_by', 'balance_after_payment',
    )
    search_fields = ('receipt_no', 'client_name', 'invoice__invoice_number', 'transaction_id')
    list_filter = ('payment_method', 'date_received', 'received_by')
    readonly_fields = ('created_at', 'updated_at')
