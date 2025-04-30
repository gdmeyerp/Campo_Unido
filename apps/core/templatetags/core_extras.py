from django import template

register = template.Library()

@register.filter
def get_username_display(user):
    """
    Retorna el nombre de usuario para mostrar en la interfaz.
    Prioridad: username > email (solo la parte antes de @) > 'Usuario'
    """
    if not user:
        return 'Usuario'
    
    if hasattr(user, 'username') and user.username:
        return user.username
    
    if hasattr(user, 'email') and user.email:
        if '@' in user.email:
            return user.email.split('@')[0]
        return user.email
    
    return 'Usuario' 