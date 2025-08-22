from django import template
from django.conf import settings
from apps.core.utils import format_currency

register = template.Library()

def get_currency_display(currency_symbol):
    """Convert currency symbol to display text for better compatibility"""
    if not currency_symbol:
        return 'NGN'
    currency_symbol = currency_symbol.strip()
    currency_mapping = {
        '₦': 'NGN',
        '$': 'USD',
        '€': 'EUR',
        '£': 'GBP',
        '¥': 'JPY',
        '₹': 'INR',
        '₽': 'RUB',
        '₩': 'KRW',
        '₪': 'ILS',
        '₨': 'PKR',
        '₴': 'UAH',
        '₸': 'KZT',
        '₺': 'TRY',
        '₼': 'AZN',
        '₾': 'GEL',
        '₿': 'BTC',
    }
    return currency_mapping.get(currency_symbol, currency_symbol)

@register.filter
def currency_display(currency_symbol):
    """Template filter to convert currency symbol to display text"""
    return get_currency_display(currency_symbol)

@register.filter
def currency_format(value, currency_symbol=None):
    """
    Format a value as currency using the provided symbol or default from settings
    
    Usage:
    {{ amount|currency_format }}
    {{ amount|currency_format:"$" }}
    """
    if value is None:
        value = 0
    
    # Use provided symbol or default from settings
    symbol = currency_symbol or getattr(settings, 'DEFAULT_CURRENCY_SYMBOL', '$')
    
    return format_currency(value, symbol)

@register.filter
def currency_format_with_symbol(value, company_profile=None):
    """
    Format a value as currency using the company profile's currency symbol
    
    Usage:
    {{ amount|currency_format_with_symbol:company_profile }}
    """
    if value is None:
        value = 0
    
    if company_profile and hasattr(company_profile, 'currency_symbol'):
        symbol = company_profile.currency_symbol
    else:
        symbol = getattr(settings, 'DEFAULT_CURRENCY_SYMBOL', '$')
    
    return format_currency(value, symbol)

@register.filter
def currency_format_pdf_safe(value, company_profile=None):
    """
    Format a value as currency for PDF generation, with fallback for problematic Unicode symbols
    
    Usage:
    {{ amount|currency_format_pdf_safe:company_profile }}
    """
    if value is None:
        value = 0
    
    if company_profile and hasattr(company_profile, 'currency_symbol'):
        symbol = company_profile.currency_symbol
    else:
        symbol = getattr(settings, 'DEFAULT_CURRENCY_SYMBOL', '$')
    
    return format_currency(value, symbol, pdf_safe=True)

@register.simple_tag(takes_context=True)
def get_currency_symbol(context):
    """
    Get the current currency symbol from context
    
    Usage:
    {% get_currency_symbol as currency_symbol %}
    """
    # Try to get from company profile in context
    company_profile = context.get('company_profile')
    if company_profile and hasattr(company_profile, 'currency_symbol'):
        return company_profile.currency_symbol
    
    # Try to get from user_currency_symbol in context
    user_currency_symbol = context.get('user_currency_symbol')
    if user_currency_symbol:
        return user_currency_symbol
    
    # Fallback to default
    return getattr(settings, 'DEFAULT_CURRENCY_SYMBOL', '$')

@register.simple_tag(takes_context=True)
def get_currency_code(context):
    """
    Get the current currency code from context
    
    Usage:
    {% get_currency_code as currency_code %}
    """
    # Try to get from company profile in context
    company_profile = context.get('company_profile')
    if company_profile and hasattr(company_profile, 'currency_code'):
        return company_profile.currency_code
    
    # Try to get from user_currency_code in context
    user_currency_code = context.get('user_currency_code')
    if user_currency_code:
        return user_currency_code
    
    # Fallback to default
    return getattr(settings, 'DEFAULT_CURRENCY_CODE', 'USD') 