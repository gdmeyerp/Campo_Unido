from django import template
from apps.inventario.models import Notificacion

register = template.Library()

@register.simple_tag
def notificaciones_no_leidas(user):
    """
    Devuelve el número de notificaciones no leídas para el usuario
    """
    if user.is_authenticated:
        return Notificacion.objects.filter(usuario=user, leida=False).count()
    return 0

@register.inclusion_tag('inventario/notificaciones/menu_notificaciones.html')
def mostrar_menu_notificaciones(user):
    """
    Renderiza el menú de notificaciones con el contador
    """
    notificaciones_count = 0
    if user.is_authenticated:
        notificaciones_count = Notificacion.objects.filter(usuario=user, leida=False).count()
    
    return {
        'notificaciones_count': notificaciones_count,
        'user': user
    } 