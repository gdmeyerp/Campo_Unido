from django import template
from apps.inventario.models import Notificacion
import logging

# Configura el logging
logger = logging.getLogger(__name__)

register = template.Library()

@register.simple_tag
def notificaciones_no_leidas(user):
    """
    Devuelve el número de notificaciones no leídas para el usuario
    """
    if user.is_authenticated:
        count = Notificacion.objects.filter(usuario=user, leida=False).count()
        try:
            # Intentar obtener un identificador seguro del usuario
            user_ident = getattr(user, 'email', getattr(user, 'id', 'desconocido'))
            logger.info(f"Usuario ID:{user_ident} tiene {count} notificaciones no leídas")
        except Exception:
            logger.info(f"Usuario tiene {count} notificaciones no leídas")
        return count
    return 0

@register.inclusion_tag('inventario/notificaciones/menu_notificaciones.html')
def mostrar_menu_notificaciones(user):
    """
    Renderiza el menú de notificaciones con el contador
    """
    notificaciones_count = 0
    if hasattr(user, 'is_authenticated') and user.is_authenticated:
        try:
            notificaciones_count = Notificacion.objects.filter(usuario=user, leida=False).count()
            # Intentar obtener un identificador seguro del usuario
            user_ident = getattr(user, 'email', getattr(user, 'id', 'desconocido'))
            logger.info(f"Mostrando menú de notificaciones para usuario ID:{user_ident}. Tiene {notificaciones_count} no leídas")
        except Exception as e:
            logger.error(f"Error al obtener notificaciones: {str(e)}")
    
    return {
        'notificaciones_count': notificaciones_count,
        'user': user
    }

@register.simple_tag
def get_notificaciones_count():
    """
    Devuelve el número de notificaciones no leídas.
    Esta es una versión simplificada que siempre devuelve 0
    """
    return """<span class="badge bg-primary rounded-pill">0</span>"""

@register.simple_tag
def get_notificaciones():
    """
    Devuelve las notificaciones recientes.
    Esta es una versión simplificada que muestra un mensaje
    """
    return """<div class="p-2 text-center">
                <p class="small text-muted">No tienes notificaciones nuevas</p>
            </div>""" 