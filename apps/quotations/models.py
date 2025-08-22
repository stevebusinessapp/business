from django.db import models, IntegrityError
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.core.models import CompanyProfile
from apps.clients.models import Client
import re

User = get_user_model()


class QuotationTemplate(models.Model):
    """User-defined quotation templates with custom styling and colors"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quotation_templates')
    name = models.CharField(max_length=200, default='Default Quotation', help_text="Template name (e.g., 'Professional Quotation', 'Service Quote')")
    description = models.TextField(blank=True, help_text="Description of this template")
    
    # Color customization
    primary_color = models.CharField(max_length=7, default='#1976d2', help_text="Primary color (hex code)")
    secondary_color = models.CharField(max_length=7, default='#f8f9fa', help_text="Secondary color (hex code)")
    text_color = models.CharField(max_length=7, default='#333333', help_text="Text color (hex code)")
    accent_color = models.CharField(max_length=7, default='#e9ecef', help_text="Accent color for borders and highlights (hex code)")
    
    # Display options
    show_company_logo = models.BooleanField(default=True)
    show_company_details = models.BooleanField(default=True)
    show_bank_details = models.BooleanField(default=True)
    show_signature = models.BooleanField(default=True)
    
    # Document settings
    document_title = models.CharField(max_length=100, default='QUOTATION', help_text="Document title to display")
    number_prefix = models.CharField(max_length=10, default='QT', help_text="Quotation number prefix")
    
    # Terms and notes
    default_terms = models.TextField(blank=True, default='This quotation is valid for 30 days from the date of issue', help_text="Default terms for new quotations")
    footer_text = models.TextField(blank=True, help_text="Footer text to display on quotations")
    
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
            QuotationTemplate.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Quotation(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    quotation_number = models.CharField(max_length=50, editable=False)
    quotation_date = models.DateField(auto_now_add=True)
    valid_until = models.DateField(null=True, blank=True, help_text="Quotation validity period")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quotations')
    template = models.ForeignKey(QuotationTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotations')
    
    # Client Information
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotations')
    
    # Financial Fields
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    other_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    terms = models.TextField(blank=True, help_text="Terms and conditions")
    notes = models.TextField(blank=True, help_text="Additional notes")
    
    # Professional conversion tracking
    converted_invoice = models.ForeignKey('invoices.Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='source_quotation')
    conversion_date = models.DateTimeField(null=True, blank=True, help_text="Date when quotation was converted to invoice")
    
    # Custom fields for flexibility
    custom_fields = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = [['user', 'quotation_number']]
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['quotation_number']),
            models.Index(fields=['status']),
            models.Index(fields=['quotation_date']),
            models.Index(fields=['valid_until']),
            models.Index(fields=['client']),
        ]
    
    def __str__(self):
        client_name = self.client.name if self.client else "No Client"
        return f"Quotation {self.quotation_number} - {client_name}"
    
    def save(self, *args, **kwargs):
        if not self.quotation_number:
            self.quotation_number = self.generate_quotation_number()
        
        # Set default values from company profile if not set
        if not self.pk:  # Only for new quotations
            try:
                company_profile = self.user.company_profile
                if company_profile:
                    if not self.total_tax:
                        self.total_tax = company_profile.default_tax
                    if not self.total_discount:
                        self.total_discount = company_profile.default_discount
                    if not self.shipping_fee:
                        self.shipping_fee = company_profile.default_shipping_fee
            except:
                pass
        
        super().save(*args, **kwargs)
        self.calculate_totals()
    
    def generate_quotation_number(self):
        """Generate unique quotation number based on user and sequence"""
        prefix = "QT"
        if self.template and self.template.number_prefix:
            prefix = self.template.number_prefix
        
        # Get the last quotation number for this user
        last_quotation = Quotation.objects.filter(
            user=self.user,
            quotation_number__startswith=prefix
        ).order_by('-quotation_number').first()
        
        if last_quotation and last_quotation.quotation_number:
            # Extract the number part and increment
            try:
                number_part = last_quotation.quotation_number[len(prefix):]
                if number_part.startswith('-'):
                    number_part = number_part[1:]
                next_number = int(number_part) + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f"{prefix}-{next_number:06d}"
    
    def calculate_totals(self):
        """Calculate all totals based on line items"""
        # Calculate subtotal from line items
        subtotal = sum(item.line_total for item in self.items.all())
        self.subtotal = subtotal
        
        # Calculate grand total
        self.grand_total = (
            self.subtotal +
            self.total_tax +
            self.shipping_fee +
            self.other_charges -
            self.total_discount
        )
        
        # Use update to avoid recursion
        Quotation.objects.filter(pk=self.pk).update(
            subtotal=self.subtotal,
            grand_total=self.grand_total
        )
    
    @staticmethod
    def parse_number(value):
        """Parse number from string, handling percentage and currency formats"""
        if not value:
            return Decimal('0.00')
        
        if isinstance(value, (int, float, Decimal)):
            return Decimal(str(value))
        
        # Convert to string and clean
        value_str = str(value).strip().replace(',', '')
        
        # Handle percentage
        if '%' in value_str:
            try:
                percentage = Decimal(value_str.replace('%', ''))
                return percentage / 100
            except:
                return Decimal('0.00')
        
        # Handle currency symbols
        value_str = re.sub(r'[^\d.-]', '', value_str)
        
        try:
            return Decimal(value_str)
        except:
            return Decimal('0.00')


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    product_service = models.CharField(max_length=250, blank=True, help_text="Product or service name")
    description = models.CharField(max_length=500, blank=True, help_text="Detailed description")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], blank=True, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], blank=True, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Custom fields for flexibility
    custom_fields = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product_service or self.description} - {self.quotation.quotation_number}"
    
    def save(self, *args, **kwargs):
        # Calculate line total
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Recalculate quotation totals without triggering save again
        if self.quotation:
            self.quotation.calculate_totals()
