from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.filter
def split(value, arg):
    """Split a string by a delimiter"""
    if value:
        return value.split(arg)
    return []

@register.filter
def strip(value):
    """Strip whitespace from a string"""
    if value:
        return value.strip()
    return value

@register.filter
def format_currency(value, currency_symbol=None):
    """Format a number as currency with dynamic symbol"""
    if value is not None:
        try:
            # Use provided currency symbol or default to $
            symbol = currency_symbol or '$'
            return f"{symbol}{float(value):,.2f}"
        except (ValueError, TypeError):
            return value
    return value

@register.filter
def format_number(value):
    """Format a number with commas"""
    if value is not None:
        try:
            return f"{float(value):,.2f}"
        except (ValueError, TypeError):
            return value
    return value

@register.filter
def yes_no(value):
    """Convert boolean to Yes/No"""
    if value:
        return "Yes"
    return "No"

@register.filter
def check_mark(value):
    """Convert boolean to checkmark or X"""
    if value:
        return "✓"
    return "✗"

@register.filter
def get_field(form, field_name):
    """Get a form field by name"""
    if hasattr(form, 'fields') and field_name in form.fields:
        return form[field_name]
    return None

@register.filter
def get_field_id(form, field_name):
    """Get a form field ID by name"""
    if hasattr(form, 'fields') and field_name in form.fields:
        return form[field_name].id_for_label
    return field_name

@register.filter
def get_field_errors(form, field_name):
    """Get form field errors by name"""
    if hasattr(form, 'errors') and field_name in form.errors:
        return form.errors[field_name]
    return None

@register.filter
def has_field(form, field_name):
    """Check if form has a specific field"""
    return hasattr(form, 'fields') and field_name in form.fields

@register.filter
def multiply(value, arg):
    """Multiply two numbers"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def get_field_value(item, field_name):
    """Get a field value from an inventory item"""
    return item.get_value(field_name)

@register.filter
def serial_number(item, forloop_counter):
    """Get the serial number for an item based on its position in the list"""
    if forloop_counter is not None:
        return forloop_counter
    return 1


@register.filter
def format_currency_dynamic(value, request=None):
    """Format currency using user's company profile currency"""
    if value is not None:
        try:
            # Get currency symbol from request context
            if request and hasattr(request, 'user') and request.user.is_authenticated:
                try:
                    currency_symbol = request.user.company_profile.currency_symbol
                except:
                    currency_symbol = '$'
            else:
                currency_symbol = '$'
            
            return f"{currency_symbol}{float(value):,.2f}"
        except (ValueError, TypeError):
            return value
    return value


@register.simple_tag(takes_context=True)
def format_currency_with_symbol(context, value):
    """Format currency using context currency symbol"""
    if value is not None:
        try:
            # Get currency symbol from context
            currency_symbol = context.get('user_currency_symbol', '$')
            return f"{currency_symbol}{float(value):,.2f}"
        except (ValueError, TypeError):
            return value
    return value 