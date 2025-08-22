import os
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.urls import reverse
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
try:
    from num2words import num2words
except ImportError:
    num2words = None


def company_logo_upload_path(instance, filename):
    """Generate upload path for company logos"""
    return f'company/logos/{instance.user.id}/{filename}'


def company_signature_upload_path(instance, filename):
    """Generate upload path for company signatures"""
    return f'company/signatures/{instance.user.id}/{filename}'


User = get_user_model()


class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    address = models.TextField()
    website = models.URLField(blank=True, null=True)
    
    # File uploads
    logo = models.ImageField(upload_to=company_logo_upload_path, blank=True, null=True)
    signature = models.ImageField(upload_to=company_signature_upload_path, blank=True, null=True)
    
    # Financial defaults
    default_tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    default_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    default_shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Custom charges stored as JSON
    custom_charges = models.JSONField(default=dict, blank=True)
    
    # Currency settings
    currency_code = models.CharField(max_length=3, default='USD')
    currency_symbol = models.CharField(max_length=5, default='$')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company Profile'
        verbose_name_plural = 'Company Profiles'

    def __str__(self):
        return self.company_name

    def get_absolute_url(self):
        return reverse('core:company_profile')

    def delete_old_logo(self):
        """Delete old logo file when uploading new one"""
        if self.logo and os.path.isfile(self.logo.path):
            os.remove(self.logo.path)

    def delete_old_signature(self):
        """Delete old signature file when uploading new one"""
        if self.signature and os.path.isfile(self.signature.path):
            os.remove(self.signature.path)

    def save(self, *args, **kwargs):
        # Track if a new logo is being uploaded
        new_logo = False
        if self.pk:
            old = CompanyProfile.objects.filter(pk=self.pk).first()
            if old and old.logo != self.logo:
                new_logo = True
        elif self.logo:
            new_logo = True
        super().save(*args, **kwargs)
        # Auto-convert logo to PNG if needed
        if self.logo and new_logo:
            logo_path = self.logo.path
            ext = os.path.splitext(logo_path)[1].lower()
            if ext != '.png':
                try:
                    img = Image.open(logo_path)
                    if img.mode in ("RGBA", "P"):  # Convert to RGB if needed
                        img = img.convert("RGBA")
                    else:
                        img = img.convert("RGB")
                    png_io = BytesIO()
                    img.save(png_io, format='PNG')
                    png_name = os.path.splitext(self.logo.name)[0] + '.png'
                    self.logo.save(png_name, ContentFile(png_io.getvalue()), save=False)
                    super().save(update_fields=['logo'])
                    # Remove the old file if it exists and is not PNG
                    if ext != '.png' and os.path.exists(logo_path):
                        os.remove(logo_path)
                except Exception as e:
                    # Optionally log the error
                    pass


def format_currency(value, currency_symbol=None):
    try:
        value = float(value)
    except Exception:
        value = 0.0
    symbol = currency_symbol or getattr(settings, 'DEFAULT_CURRENCY_SYMBOL', '₦')
    return f"{symbol}{value:,.2f}"


def number_to_words(value, currency_name='Naira'):
    """Convert number to words with proper currency handling"""
    if num2words:
        try:
            # Convert to float first to handle Decimal objects
            float_value = float(value)
            # Use num2words to convert to currency words
            if currency_name.lower() == 'naira':
                # For Naira, use the Nigerian format
                words = num2words(float_value, to='currency', currency='NGN')
            else:
                # For other currencies, try the currency name
                words = num2words(float_value, to='currency', currency=currency_name)
            return words
        except Exception as e:
            # Fallback: convert to basic number words with currency suffix
            try:
                float_value = float(value)
                cardinal_words = num2words(float_value, to='cardinal')
                return f"{cardinal_words} {currency_name}"
            except Exception:
                return str(value)
    else:
        # Fallback when num2words is not available
        try:
            float_value = float(value)
            return f"{float_value:,.2f} {currency_name}"
        except Exception:
            return str(value)


class BankAccount(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='bank_accounts')
    bank_name = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bank Account'
        verbose_name_plural = 'Bank Accounts'
        unique_together = ['company', 'account_number']

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"

    def save(self, *args, **kwargs):
        # Ensure only one default bank account per company
        if self.is_default:
            BankAccount.objects.filter(company=self.company, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
