from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiplica el valor por el argumento"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0 

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Obtiene un elemento de un diccionario usando una variable como clave"""
    return dictionary.get(str(key), 0) 

@register.simple_tag
def get_cart_count():
    """
    Devuelve el número de elementos en el carrito.
    Esta es una versión simplificada que siempre devuelve 0
    """
    return """<span class="badge bg-primary rounded-pill">0</span>""" 