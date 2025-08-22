from django import template

register = template.Library()

@register.filter
def currency(value):
    """Format currency with commas"""
    try:
        # Convert to float and format with commas
        amount = float(value)
        return f"{amount:,.2f}"
    except (ValueError, TypeError):
        return value
