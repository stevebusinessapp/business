from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone
from apps.invoices.models import Invoice
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import time
import random
from django.db.utils import IntegrityError

User = get_user_model()

PAYMENT_CHOICES = [
    ("cash", "Cash"),
    ("bank_transfer", "Bank Transfer"),
    ("cheque", "Cheque"),
    ("card", "Card"),
    ("mobile_money", "Mobile Money"),
    ("other", "Other"),
]

class Receipt(models.Model):
    """
    Receipt model linked to Invoice. Tracks payments, supports custom color, and stores audit info.
    """
    receipt_no = models.CharField(max_length=20, unique=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="receipts")
    client_name = models.CharField(max_length=255)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    client_address = models.CharField(max_length=500, blank=True, null=True)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2)
    amount_in_words = models.CharField(max_length=500)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    received_by = models.CharField(max_length=255)
    date_received = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    balance_after_payment = models.DecimalField(max_digits=10, decimal_places=2)
    custom_color = models.CharField(max_length=20, default="#000000")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='receipts_created')

    def save(self, *args, **kwargs):
        if not self.receipt_no:
            for _ in range(5):
                self.receipt_no = self.generate_receipt_no()
                try:
                    super().save(*args, **kwargs)
                    return
                except IntegrityError:
                    continue
            raise IntegrityError("Could not generate a unique receipt number after several attempts.")
        else:
            super().save(*args, **kwargs)

    def generate_receipt_no(self):
        """Generate a unique receipt number (REC-YYYYMMDD-XXXX)"""
        from django.utils import timezone
        date_str = timezone.now().strftime("%Y%m%d")
        for attempt in range(10):
            count = Receipt.objects.filter(date_received=timezone.now().date()).count() + 1
            random_part = random.randint(100, 999)
            receipt_no = f"REC-{date_str}-{count:03d}-{random_part}"
            if not Receipt.objects.filter(receipt_no=receipt_no).exists():
                return receipt_no
        # Fallback: use timestamp
        return f"REC-{date_str}-{int(time.time() * 1000) % 100000}"

    def __str__(self):
        return f"Receipt {self.receipt_no} for {self.client_name}"


@receiver(post_save, sender=Receipt)
def update_invoice_on_receipt_save(sender, instance, created, **kwargs):
    invoice = instance.invoice
    # Recalculate all receipts for this invoice
    total_received = sum(r.amount_received for r in invoice.receipts.all())
    invoice.amount_paid = total_received
    invoice.balance_due = invoice.grand_total - total_received
    # Update status
    if invoice.amount_paid == 0:
        invoice.status = 'unpaid'
    elif invoice.amount_paid >= invoice.grand_total:
        invoice.status = 'paid'
    else:
        invoice.status = 'partial'
    invoice.save()

@receiver(post_delete, sender=Receipt)
def update_invoice_on_receipt_delete(sender, instance, **kwargs):
    invoice = instance.invoice
    total_received = sum(r.amount_received for r in invoice.receipts.all())
    invoice.amount_paid = total_received
    invoice.balance_due = invoice.grand_total - total_received
    # Update status
    if invoice.amount_paid == 0:
        invoice.status = 'unpaid'
    elif invoice.amount_paid >= invoice.grand_total:
        invoice.status = 'paid'
    else:
        invoice.status = 'partial'
    invoice.save()
