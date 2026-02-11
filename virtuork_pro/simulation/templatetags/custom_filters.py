# app/templatetags/custom_filters.py
from django import template
register = template.Library()

@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_id(obj):
    return obj.id