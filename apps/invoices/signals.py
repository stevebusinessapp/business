from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import InvoiceItem


@receiver(post_save, sender=InvoiceItem)
def update_invoice_totals_on_save(sender, instance, **kwargs):
    """Update invoice totals when an item is saved"""
    instance.invoice.calculate_totals()
    instance.invoice.save(update_fields=['subtotal', 'grand_total', 'balance_due', 'status'])


@receiver(post_delete, sender=InvoiceItem)
def update_invoice_totals_on_delete(sender, instance, **kwargs):
    """Update invoice totals when an item is deleted"""
    instance.invoice.calculate_totals()
    instance.invoice.save(update_fields=['subtotal', 'grand_total', 'balance_due', 'status'])
