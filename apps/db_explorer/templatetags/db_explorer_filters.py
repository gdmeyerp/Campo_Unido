from django import template

register = template.Library()

@register.filter(name='getattr_filter')
def getattr_filter(obj, attr_name):
    """
    Filtro personalizado que actúa como la función getattr de Python.
    Permite acceder a atributos de un objeto por su nombre como string.
    
    Uso: {{ object|getattr_filter:'attribute_name' }}
    """
    try:
        return getattr(obj, attr_name)
    except (AttributeError, TypeError):
        return None 