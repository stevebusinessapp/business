import re
from decimal import Decimal, InvalidOperation
from typing import Optional, Union


def parse_number(value: Union[str, int, float, Decimal]) -> Optional[Decimal]:
    """
    Parse a value into a Decimal number, handling various input formats.
    
    Args:
        value: The value to parse (string, int, float, or Decimal)
    
    Returns:
        Decimal if successful, None if parsing fails
    """
    if value is None:
        return None
    
    # If already a Decimal, return it
    if isinstance(value, Decimal):
        return value
    
    # Convert to string for processing
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    
    if not isinstance(value, str):
        return None
    
    # Remove whitespace
    value = value.strip()
    
    if not value:
        return None
    
    # Handle common currency symbols and formatting
    # Remove currency symbols, commas, and other formatting
    value = re.sub(r'[^\d.-]', '', value)
    
    # Handle multiple decimal points (take the last one)
    if value.count('.') > 1:
        parts = value.split('.')
        value = ''.join(parts[:-1]) + '.' + parts[-1]
    
    # Handle multiple minus signs
    if value.count('-') > 1:
        value = value.replace('-', '')
        value = '-' + value
    
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def format_currency(amount: Union[Decimal, float, int], currency: str = 'USD') -> str:
    """
    Format a number as currency.
    
    Args:
        amount: The amount to format
        currency: The currency code (default: USD)
    
    Returns:
        Formatted currency string
    """
    if amount is None:
        return f"$0.00"
    
    amount_decimal = parse_number(amount)
    if amount_decimal is None:
        return f"$0.00"
    
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'NGN': '₦',
    }
    
    symbol = currency_symbols.get(currency, '$')
    return f"{symbol}{amount_decimal:,.2f}"


def format_number(value: Union[Decimal, float, int]) -> str:
    """
    Format a number with appropriate decimal places.
    
    Args:
        value: The number to format
    
    Returns:
        Formatted number string
    """
    if value is None:
        return "0"
    
    value_decimal = parse_number(value)
    if value_decimal is None:
        return "0"
    
    # If it's a whole number, don't show decimal places
    if value_decimal == value_decimal.to_integral():
        return f"{value_decimal:,.0f}"
    else:
        return f"{value_decimal:,.2f}"


def sanitize_sku(sku: str) -> str:
    """
    Sanitize SKU code by removing special characters and normalizing.
    
    Args:
        sku: The SKU code to sanitize
    
    Returns:
        Sanitized SKU code
    """
    if not sku:
        return ""
    
    # Remove special characters except alphanumeric, hyphens, and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '', str(sku))
    
    # Convert to uppercase
    return sanitized.upper()


def generate_sku_code(prefix: str = "SKU", length: int = 8) -> str:
    """
    Generate a unique SKU code.
    
    Args:
        prefix: Prefix for the SKU code
        length: Length of the random part
    
    Returns:
        Generated SKU code
    """
    import random
    import string
    
    # Generate random alphanumeric string
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    return f"{prefix}-{random_part}"


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not url:
        return False
    
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return bool(re.match(pattern, url))


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def safe_int(value: Union[str, int, float, Decimal], default: int = 0) -> int:
    """
    Safely convert a value to integer.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
    
    Returns:
        Integer value
    """
    try:
        if isinstance(value, (int, float, Decimal)):
            return int(value)
        if isinstance(value, str):
            return int(float(value))
        return default
    except (ValueError, TypeError):
        return default


def safe_float(value: Union[str, int, float, Decimal], default: float = 0.0) -> float:
    """
    Safely convert a value to float.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
    
    Returns:
        Float value
    """
    try:
        if isinstance(value, (int, float, Decimal)):
            return float(value)
        if isinstance(value, str):
            return float(value)
        return default
    except (ValueError, TypeError):
        return default 