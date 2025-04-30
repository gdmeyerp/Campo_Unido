from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def getattribute(obj, attr):
    """
    Obtiene un atributo de un objeto de forma segura.
    Si el atributo no existe, devuelve None.
    """
    try:
        # Primero intentamos acceder directamente
        if hasattr(obj, attr):
            value = getattr(obj, attr)
            # Si es un método, lo llamamos
            if callable(value) and not attr.startswith('_'):
                return value()
            return value
        
        # Si no funciona, intentamos acceder como diccionario
        elif hasattr(obj, '__getitem__'):
            try:
                return obj[attr]
            except (KeyError, TypeError):
                pass
        
        return None
    except Exception:
        return None

@register.filter
def to_json(value):
    """
    Convierte un valor a JSON para mostrar en la interfaz.
    """
    try:
        return mark_safe(json.dumps(value, indent=2, default=str))
    except Exception:
        return '{}'

@register.filter
def get_item(dictionary, key):
    """
    Obtiene un elemento de un diccionario de forma segura.
    """
    return dictionary.get(key)

@register.filter
def format_value(value):
    """
    Formatea un valor para mostrar en la interfaz.
    """
    if value is None:
        return mark_safe('<span class="text-muted">Ninguno</span>')
    elif value == '':
        return mark_safe('<span class="text-muted">Vacío</span>')
    elif value is True:
        return mark_safe('<span class="badge badge-success">Sí</span>')
    elif value is False:
        return mark_safe('<span class="badge badge-danger">No</span>')
    else:
        return value 