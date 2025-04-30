from .models import ChatMessage, ChatRoom

def chat_flotante_processor(request):
    """
    Context processor para agregar información del chat flotante a todas las páginas.
    """
    context = {
        'chat_flotante_enabled': False,
        'chat_flotante_unread': 0,
    }
    
    # Solo agregar datos de chat si el usuario está autenticado
    if request.user.is_authenticated:
        try:
            # Obtener salas de chat del usuario
            rooms = ChatRoom.objects.filter(participants=request.user)
            
            # Contar mensajes no leídos
            unread_count = ChatMessage.objects.filter(
                room__in=rooms,
                is_read=False
            ).exclude(sender=request.user).count()
            
            context.update({
                'chat_flotante_enabled': True,
                'chat_flotante_unread': unread_count,
            })
        except Exception:
            # En caso de error, simplemente no mostramos datos de chat
            pass
    
    return context 