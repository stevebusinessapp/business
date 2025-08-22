import re
from datetime import datetime
from django.db import models
from django.apps import apps


def get_currency_info(currency_code):
    """Get currency information including symbol"""
    currency_map = {
        'USD': {'symbol': '$', 'name': 'US Dollar'},
        'EUR': {'symbol': '€', 'name': 'Euro'},
        'GBP': {'symbol': '£', 'name': 'British Pound'},
        'JPY': {'symbol': '¥', 'name': 'Japanese Yen'},
        'CAD': {'symbol': 'C$', 'name': 'Canadian Dollar'},
        'AUD': {'symbol': 'A$', 'name': 'Australian Dollar'},
        'CHF': {'symbol': 'CHF', 'name': 'Swiss Franc'},
        'CNY': {'symbol': '¥', 'name': 'Chinese Yuan'},
        'INR': {'symbol': '₹', 'name': 'Indian Rupee'},
        'NGN': {'symbol': '₦', 'name': 'Nigerian Naira'},
        'ZAR': {'symbol': 'R', 'name': 'South African Rand'},
        'BRL': {'symbol': 'R$', 'name': 'Brazilian Real'},
        'KRW': {'symbol': '₩', 'name': 'South Korean Won'},
        'SGD': {'symbol': 'S$', 'name': 'Singapore Dollar'},
        'HKD': {'symbol': 'HK$', 'name': 'Hong Kong Dollar'},
        'MXN': {'symbol': '$', 'name': 'Mexican Peso'},
        'RUB': {'symbol': '₽', 'name': 'Russian Ruble'},
        'SEK': {'symbol': 'kr', 'name': 'Swedish Krona'},
        'NOK': {'symbol': 'kr', 'name': 'Norwegian Krone'},
        'DKK': {'symbol': 'kr', 'name': 'Danish Krone'},
    }
    
    return currency_map.get(currency_code.upper())


def get_available_currencies():
    """Get list of all available currencies"""
    currencies = []
    currency_codes = [
        'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'INR', 'NGN',
        'ZAR', 'BRL', 'KRW', 'SGD', 'HKD', 'MXN', 'RUB', 'SEK', 'NOK', 'DKK'
    ]
    
    for code in currency_codes:
        info = get_currency_info(code)
        if info:
            currencies.append({
                'code': code,
                'symbol': info['symbol'],
                'name': info['name']
            })
    
    return currencies


def generate_auto_number(doc_type, company_profile, prefix=None):
    """
    Generate auto number for documents
    
    Args:
        doc_type (str): Type of document (invoice, quotation, receipt, etc.)
        company_profile: CompanyProfile instance
        prefix (str): Optional prefix for the number
    
    Returns:
        str: Generated auto number
    """
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Default prefixes for different document types
    default_prefixes = {
        'invoice': 'INV',
        'quotation': 'QUO',
        'receipt': 'REC',
        'job_order': 'JO',
        'waybill': 'WB',
        'expense': 'EXP',
    }
    
    if not prefix:
        prefix = default_prefixes.get(doc_type.lower(), 'DOC')
    
    # Try to get the model for the document type
    try:
        if doc_type.lower() == 'invoice':
            model = apps.get_model('invoices', 'Invoice')
            filter_field = 'company'
        elif doc_type.lower() == 'quotation':
            model = apps.get_model('quotations', 'Quotation')
            filter_field = 'company'
        elif doc_type.lower() == 'receipt':
            model = apps.get_model('receipts', 'Receipt')
            filter_field = 'company'
        elif doc_type.lower() == 'job_order':
            model = apps.get_model('job_orders', 'JobOrder')
            filter_field = 'company'
        elif doc_type.lower() == 'waybill':
            model = apps.get_model('waybills', 'Waybill')
            filter_field = 'company'
        elif doc_type.lower() == 'expense':
            model = apps.get_model('expenses', 'Expense')
            filter_field = 'company'
        else:
            # Fallback for unknown document types
            model = None
    except LookupError:
        model = None
    
    # Generate the auto number
    if model:
        # Get the last document number for this company and year
        last_doc = model.objects.filter(
            **{filter_field: company_profile},
            created_at__year=current_year
        ).order_by('-id').first()
        
        if last_doc and hasattr(last_doc, 'number'):
            # Extract the sequence number from the last document
            match = re.search(r'(\d+)$', last_doc.number)
            if match:
                last_sequence = int(match.group(1))
                next_sequence = last_sequence + 1
            else:
                next_sequence = 1
        else:
            next_sequence = 1
    else:
        # Fallback: use current timestamp
        next_sequence = int(datetime.now().timestamp()) % 10000
    
    # Format: PREFIX-YYYY-MM-NNNN
    auto_number = f"{prefix}-{current_year}-{current_month:02d}-{next_sequence:04d}"
    
    return auto_number


def format_currency(amount, currency_symbol='$', decimal_places=2, pdf_safe=False):
    """
    Format amount as currency
    
    Args:
        amount (float/Decimal): Amount to format
        currency_symbol (str): Currency symbol
        decimal_places (int): Number of decimal places
        pdf_safe (bool): Whether to use PDF-safe formatting
    
    Returns:
        str: Formatted currency string
    """
    if amount is None:
        amount = 0
    
    # Handle problematic Unicode symbols for PDF generation
    if pdf_safe:
        symbol_fallbacks = {
            '₦': 'NGN',  # Nigerian Naira
            '₹': 'INR',  # Indian Rupee
            '₽': 'RUB',  # Russian Ruble
            '₩': 'KRW',  # South Korean Won
            '¥': 'JPY',  # Japanese Yen
        }
        
        # Use fallback if symbol is problematic for PDF
        if currency_symbol in symbol_fallbacks:
            currency_symbol = symbol_fallbacks[currency_symbol]
    
    # Format with commas and specified decimal places
    formatted_amount = f"{float(amount):,.{decimal_places}f}"
    
    return f"{currency_symbol}{formatted_amount}"


def validate_image_file(image_file, max_size_mb=5):
    """
    Validate uploaded image file
    
    Args:
        image_file: Uploaded file object
        max_size_mb (int): Maximum file size in MB
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not image_file:
        return True, None
    
    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if image_file.size > max_size_bytes:
        return False, f"File size cannot exceed {max_size_mb}MB"
    
    # Check file extension
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    file_extension = image_file.name.lower().split('.')[-1]
    if f'.{file_extension}' not in valid_extensions:
        return False, "File must be a JPG, PNG, GIF, or WebP image"
    
    # Check MIME type
    valid_mime_types = [
        'image/jpeg', 'image/png', 'image/gif', 'image/webp'
    ]
    if hasattr(image_file, 'content_type') and image_file.content_type not in valid_mime_types:
        return False, "Invalid image file type"
    
    return True, None


def clean_phone_number(phone_number):
    """
    Clean and format phone number
    
    Args:
        phone_number (str): Raw phone number
    
    Returns:
        str: Cleaned phone number
    """
    if not phone_number:
        return phone_number
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone_number)
    
    # Ensure it starts with + if it doesn't have country code
    if not cleaned.startswith('+'):
        cleaned = f'+{cleaned}'
    
    return cleaned


def get_company_context(user):
    """
    Get company context for templates
    
    Args:
        user: User instance
    
    Returns:
        dict: Company context data
    """
    try:
        company_profile = user.company_profile
        return {
            'company_profile': company_profile,
            'company_logo': company_profile.logo.url if company_profile.logo else None,
            'company_signature': company_profile.signature.url if company_profile.signature else None,
            'currency_symbol': company_profile.currency_symbol,
            'currency_code': company_profile.currency_code,
        }
    except Exception:
        return {
            'company_profile': None,
            'company_logo': None,
            'company_signature': None,
            'currency_symbol': '$',
            'currency_code': 'USD',
        }


def calculate_percentage(amount, percentage):
    """
    Calculate percentage of an amount
    
    Args:
        amount (float/Decimal): Base amount
        percentage (float/Decimal): Percentage to calculate
    
    Returns:
        float: Calculated percentage amount
    """
    if not amount or not percentage:
        return 0
    
    return float(amount) * (float(percentage) / 100)


def apply_custom_charges(base_amount, custom_charges):
    """
    Apply custom charges to base amount
    
    Args:
        base_amount (float/Decimal): Base amount
        custom_charges (dict): Custom charges dictionary
    
    Returns:
        dict: Applied charges with totals
    """
    applied_charges = {}
    total_charges = 0
    
    if custom_charges and isinstance(custom_charges, dict):
        for charge_name, charge_value in custom_charges.items():
            try:
                charge_amount = float(charge_value)
                applied_charges[charge_name] = charge_amount
                total_charges += charge_amount
            except (ValueError, TypeError):
                # Skip invalid charge values
                continue
    
    return {
        'charges': applied_charges,
        'total_charges': total_charges,
        'final_amount': float(base_amount) + total_charges
    }
