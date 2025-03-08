from django import template
from django.forms.widgets import Widget

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """Agrega una clase CSS a un campo de formulario"""
    if hasattr(field, 'field') and hasattr(field.field, 'widget'):
        widget = field.field.widget
        if hasattr(widget, 'attrs'):
            existing_classes = widget.attrs.get('class', '')
            if existing_classes:
                css_class = f"{existing_classes} {css_class}"
            widget.attrs['class'] = css_class
    return field 