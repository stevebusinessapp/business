from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.filter
def format_currency(value, symbol='$'):
    import re
    try:
        # Remove all non-numeric and non-decimal characters
        cleaned = re.sub(r'[^\d.]', '', str(value))
        # Only keep the first decimal point
        if cleaned.count('.') > 1:
            parts = cleaned.split('.')
            cleaned = parts[0] + '.' + ''.join(parts[1:])
        value = float(cleaned) if cleaned else 0
        formatted = f"{value:,.2f}"
        return f"{symbol}{formatted}"
    except (ValueError, TypeError):
        return f"{symbol}0.00" 