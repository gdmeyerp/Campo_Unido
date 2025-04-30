from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def sub(value, arg):
    """Resta el argumento del valor"""
    return value - arg 