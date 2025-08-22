from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """
    Template filter to look up a value in a dictionary by key.
    Usage: {{ dict|lookup:key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.filter
def get_item(dictionary, key):
    """
    Alternative filter for dictionary lookup.
    Usage: {{ dict|get_item:key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.filter
def pluralize_custom(value, arg="s"):
    """
    Custom pluralize filter.
    Usage: {{ count|pluralize_custom:"item,items" }}
    """
    if "," in arg:
        singular, plural = arg.split(",")
        return singular if value == 1 else plural
    else:
        return "" if value == 1 else arg
