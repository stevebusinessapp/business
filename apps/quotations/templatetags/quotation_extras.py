from django import template
import json
register = template.Library()

@register.filter
def get_custom_field(fields, col):
    return fields.get(f'custom_{col}')

@register.filter
def json_loads(value):
    try:
        return json.loads(value)
    except Exception:
        return []

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.filter
def get_form_field(form, field_name):
    """Get a form field by name"""
    if hasattr(form, 'fields') and field_name in form.fields:
        return form[field_name]
    return None 