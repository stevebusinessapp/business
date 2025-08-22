from django.db import models, IntegrityError
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
import re

User = get_user_model()


class InvoiceTemplate(models.Model):
    """User-defined invoice templates with custom styling and colors"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoice_templates')
    name = models.CharField(max_length=200, default='Default Invoice', help_text="Template name (e.g., 'Professional Invoice', 'Service Invoice')")
    description = models.TextField(blank=True, help_text="Description of this template")
    
    # Color customization
    primary_color = models.CharField(max_length=7, default='#FF5900', help_text="Primary color (hex code)")
    secondary_color = models.CharField(max_length=7, default='#f8f9fa', help_text="Secondary color (hex code)")
    text_color = models.CharField(max_length=7, default='#333333', help_text="Text color (hex code)")
    accent_color = models.CharField(max_length=7, default='#e9ecef', help_text="Accent color for borders and highlights (hex code)")
    
    # Display options
    show_company_logo = models.BooleanField(default=True)
    show_company_details = models.BooleanField(default=True)
    show_bank_details = models.BooleanField(default=True)
    show_signature = models.BooleanField(default=True)
    
    # Document settings
    document_title = models.CharField(max_length=100, default='INVOICE', help_text="Document title to display")
    number_prefix = models.CharField(max_length=10, default='INV', help_text="Invoice number prefix")
    
    # Payment terms and notes
    default_payment_terms = models.TextField(blank=True, default='Payment due within 30 days', help_text="Default payment terms for new invoices")
    footer_text = models.TextField(blank=True, help_text="Footer text to display on invoices")
    
    is_default = models.BooleanField(default=False, help_text="Use as default template")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default template per user
        if self.is_default:
            InvoiceTemplate.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('delivered', 'Delivered'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    template = models.ForeignKey(InvoiceTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    
    # Client Information
    client_name = models.CharField(max_length=200)
    client_phone = models.CharField(max_length=20, blank=True)
    client_email = models.EmailField(blank=True)
    client_address = models.TextField(blank=True)
    
    # Financial Fields
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    other_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='unpaid')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['invoice_number']),
            models.Index(fields=['status']),
            models.Index(fields=['invoice_date']),
            models.Index(fields=['due_date']),
        ]
        
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        # Handle potential duplicate invoice numbers with retry mechanism
        max_retries = 3
        for retry in range(max_retries):
            try:
                # Only calculate totals if the invoice already exists (has a primary key)
                # This prevents errors when creating new invoices
                if self.pk:
                    self.calculate_totals()
                
                super().save(*args, **kwargs)
                break  # Success, exit retry loop
                
            except IntegrityError as e:
                if 'UNIQUE constraint failed: invoices_invoice.invoice_number' in str(e) and retry < max_retries - 1:
                    # Generate a new invoice number and try again
                    self.invoice_number = self.generate_invoice_number()
                    continue
                else:
                    # Re-raise the error if it's not a duplicate invoice number or we've exhausted retries
                    raise
    
    def generate_invoice_number(self):
        """Generate unique invoice number with collision handling"""
        from datetime import datetime
        import random
        year = datetime.now().year
        
        # Try multiple attempts to generate a unique number
        for attempt in range(10):
            if attempt == 0:
                # First try: use count-based approach
                count = Invoice.objects.filter(
                    user=self.user,
                    created_at__year=year
                ).count() + 1
                invoice_number = f"INV-{year}-{count:04d}"
            else:
                # Subsequent tries: add random component to avoid collisions
                count = Invoice.objects.filter(
                    user=self.user,
                    created_at__year=year
                ).count() + 1
                random_suffix = random.randint(1000, 9999)
                invoice_number = f"INV-{year}-{count:04d}-{random_suffix}"
            
            # Check if this number already exists
            if not Invoice.objects.filter(invoice_number=invoice_number).exists():
                return invoice_number
        
        # Final fallback: use timestamp
        import time
        timestamp = int(time.time() * 1000) % 100000  # Last 5 digits of timestamp
        return f"INV-{year}-{timestamp}"
    
    def calculate_totals(self):
        """Calculate all totals"""
        self.subtotal = sum(item.line_total for item in self.items.all())
        
        # Handle percentage-based tax calculation
        if hasattr(self, '_tax_rate') and self._tax_rate:
            self.total_tax = self.subtotal * (self._tax_rate / 100)
        
        self.grand_total = self.subtotal + self.total_tax + self.shipping_fee + self.other_charges - self.total_discount
        self.balance_due = self.grand_total - self.amount_paid
        
        # Update status based on payment
        if self.amount_paid == 0:
            self.status = 'unpaid'
        elif self.amount_paid >= self.grand_total:
            self.status = 'paid'
        else:
            self.status = 'partial'
    
    @staticmethod
    def parse_number(value):
        """Parse smart number inputs like ₦3k, 7.5%, -500, '80 nires', '45n', 'N 20'"""
        if not value:
            return Decimal('0')
        
        value = str(value).strip()
        original_value = value
        
        # Remove currency symbols first
        value = re.sub(r'[₦$€£,]', '', value)
        
        # Handle percentage
        if '%' in value:
            # Extract number before %
            numbers = re.findall(r'-?\d+\.?\d*', value.replace('%', ''))
            if numbers:
                return Decimal(numbers[0]) / 100
            return Decimal('0')
        
        # Handle 'k' suffix (thousands) - extract number before k
        if value.lower().endswith('k'):
            numbers = re.findall(r'-?\d+\.?\d*', value[:-1])
            if numbers:
                return Decimal(numbers[0]) * 1000
            return Decimal('0')
        
        # Handle 'm' suffix (millions) - extract number before m
        if value.lower().endswith('m'):
            numbers = re.findall(r'-?\d+\.?\d*', value[:-1])
            if numbers:
                return Decimal(numbers[0]) * 1000000
            return Decimal('0')
        
        # Extract all numbers from the string (handles cases like "80 nires", "45n", "N 20")
        numbers = re.findall(r'-?\d+\.?\d*', value)
        if numbers:
            # Take the first number found
            try:
                return Decimal(numbers[0])
            except:
                return Decimal('0')
        
        # Try parsing the whole string as a number (fallback)
        try:
            return Decimal(value)
        except:
            return Decimal('0')


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product_service = models.CharField(max_length=250, blank=True)
    description = models.CharField(max_length=500, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], blank=True, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], blank=True, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        display_text = self.product_service or self.description or "Item"
        return f"{display_text} - {self.invoice.invoice_number}"
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Don't automatically recalculate here to avoid conflicts during bulk saves
        # Let the view handle the recalculation after all items are processed
