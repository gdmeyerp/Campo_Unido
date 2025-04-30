from django.shortcuts import render
import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import ChatRoom, ChatMessage

User = get_user_model()

@login_required
def get_conversations(request):
    """API para obtener conversaciones del usuario actual"""
    user = request.user
    
    # Obtener todas las salas de chat del usuario
    rooms = ChatRoom.objects.filter(participants=user)
    
    conversations_data = []
    total_unread = 0
    
    for room in rooms:
        # Obtener el otro participante en caso de chat privado
        other_user = None
        if not room.is_group:
            other_user = room.get_other_participant(user)
        
        # Obtener el último mensaje
        last_message = room.messages.order_by('-created_at').first()
        
        # Contar mensajes no leídos
        unread_count = room.messages.filter(is_read=False).exclude(sender=user).count()
        total_unread += unread_count
        
        # Construir datos del otro usuario para chat privado
        other_user_data = None
        if other_user:
            # Obtener nombre para mostrar
            display_name = f"{other_user.first_name} {other_user.last_name}".strip()
            if not display_name:
                display_name = other_user.email
                
            # Obtener foto de perfil
            profile_picture = None
            if hasattr(other_user, 'perfilusuario') and other_user.perfilusuario.foto_perfil:
                profile_picture = other_user.perfilusuario.foto_perfil.url
                
            other_user_data = {
                'id': other_user.id,
                'email': other_user.email,
                'display_name': display_name,
                'profile_picture': profile_picture,
            }
        
        # Construir datos del último mensaje
        last_message_data = None
        if last_message:
            # Obtener nombre para mostrar del remitente
            sender_name = f"{last_message.sender.first_name} {last_message.sender.last_name}".strip()
            if not sender_name:
                sender_name = last_message.sender.email
                
            last_message_data = {
                'id': last_message.id,
                'content': last_message.content,
                'created_at': last_message.created_at.isoformat(),
                'is_mine': last_message.sender == user,
                'sender_name': sender_name,
            }
        
        # Construir objeto de conversación
        conversation = {
            'id': room.id,
            'name': room.name,
            'is_group': room.is_group,
            'other_user': other_user_data,
            'last_message': last_message_data,
            'unread_count': unread_count,
            'updated_at': room.updated_at.isoformat(),
        }
        
        conversations_data.append(conversation)
    
    return JsonResponse({
        'status': 'success',
        'conversations': conversations_data,
        'total_unread': total_unread
    })

@login_required
def get_messages(request, room_id):
    """API para obtener mensajes de una sala específica"""
    user = request.user
    room = get_object_or_404(ChatRoom, id=room_id, participants=user)
    
    # Verificar si hay un ID de último mensaje para paginación
    last_id = request.GET.get('last_id')
    
    # Filtrar mensajes según el último ID
    if last_id:
        messages = room.messages.filter(id__gt=last_id)
    else:
        messages = room.messages.all()[:50]  # Limitar a 50 mensajes
    
    messages_data = []
    unread_messages = []
    
    for message in messages:
        # Marcar mensajes como leídos si no son del usuario actual
        if not message.is_read and message.sender != user:
            message.is_read = True
            message.save(update_fields=['is_read'])
            unread_messages.append(message.id)
        
        # Obtener nombre para mostrar del remitente
        sender_name = f"{message.sender.first_name} {message.sender.last_name}".strip()
        if not sender_name:
            sender_name = message.sender.email
            
        # Obtener foto de perfil del remitente
        profile_pic_url = None
        if hasattr(message.sender, 'perfilusuario') and message.sender.perfilusuario.foto_perfil:
            profile_pic_url = message.sender.perfilusuario.foto_perfil.url
        
        # Construir datos del mensaje
        message_data = {
            'id': message.id,
            'content': message.content,
            'message_type': message.message_type,
            'is_mine': message.sender == user,
            'sender': {
                'id': message.sender.id,
                'email': message.sender.email,
                'name': sender_name,
                'profile_pic_url': profile_pic_url,
            },
            'timestamp': message.created_at.strftime('%d/%m/%Y %H:%M'),
            'created_at': message.created_at.isoformat(),
        }
        
        # Si es un mensaje con imagen, incluir la URL
        if message.message_type == ChatMessage.TYPE_IMAGE and message.image:
            message_data['image_url'] = message.image.url
        
        messages_data.append(message_data)
    
    return JsonResponse({
        'status': 'success',
        'messages': messages_data,
        'unread_messages': unread_messages
    })

@login_required
@require_POST
def send_message(request, room_id):
    """API para enviar un mensaje"""
    user = request.user
    room = get_object_or_404(ChatRoom, id=room_id, participants=user)
    
    # Verificar si es una solicitud AJAX o un formulario con imagen
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        if is_ajax:
            # Para mensajes de texto y emoticones (AJAX)
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            message_type = ChatMessage.TYPE_TEXT
            
            if not content:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El mensaje no puede estar vacío'
                })
                
            # Crear mensaje de texto
            message = ChatMessage.objects.create(
                room=room,
                sender=user,
                content=content,
                message_type=message_type
            )
        else:
            # Para mensajes con imagen (form-data)
            content = request.POST.get('content', '').strip()
            image = request.FILES.get('image')
            
            if not image and not content:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Debes enviar una imagen o un mensaje'
                })
                
            # Determinar el tipo de mensaje basado en si hay imagen
            message_type = ChatMessage.TYPE_IMAGE if image else ChatMessage.TYPE_TEXT
            
            # Crear mensaje
            message = ChatMessage.objects.create(
                room=room,
                sender=user,
                content=content,
                message_type=message_type,
                image=image
            )
        
        # Actualizar fecha de última actualización de la sala
        room.updated_at = timezone.now()
        room.save(update_fields=['updated_at'])
        
        # Obtener nombre para mostrar del remitente
        sender_name = f"{user.first_name} {user.last_name}".strip()
        if not sender_name:
            sender_name = user.email
        
        # Construir respuesta
        message_data = {
            'id': message.id,
            'content': message.content,
            'is_mine': True,
            'message_type': message.message_type,
            'sender': {
                'id': user.id,
                'email': user.email,
                'name': sender_name,
            },
            'timestamp': message.created_at.strftime('%d/%m/%Y %H:%M'),
            'created_at': message.created_at.isoformat(),
        }
        
        # Agregar URL de la imagen si existe
        if message.image:
            message_data['image_url'] = message.image.url
        
        return JsonResponse({
            'status': 'success',
            'message': message_data
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Formato JSON inválido'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
def get_room_info(request):
    """API para obtener información de una sala"""
    user = request.user
    room_id = request.GET.get('room_id')
    
    if not room_id:
        return JsonResponse({
            'status': 'error',
            'message': 'ID de sala no proporcionado'
        })
    
    try:
        room = get_object_or_404(ChatRoom, id=room_id, participants=user)
        
        room_data = {
            'id': room.id,
            'name': room.name,
            'is_group': room.is_group,
        }
        
        # Si es chat privado, usar nombre del otro usuario
        if not room.is_group:
            other_user = room.get_other_participant(user)
            if other_user:
                # Obtener nombre para mostrar
                display_name = f"{other_user.first_name} {other_user.last_name}".strip()
                if not display_name:
                    display_name = other_user.email
                    
                room_data['name'] = display_name
                
                # Agregar imagen de perfil si está disponible
                if hasattr(other_user, 'perfilusuario') and other_user.perfilusuario.foto_perfil:
                    room_data['profile_pic_url'] = other_user.perfilusuario.foto_perfil.url
        
        return JsonResponse({
            'status': 'success',
            'room': room_data
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
@require_POST
def create_chat(request):
    """API para crear un nuevo chat privado"""
    user = request.user
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({
                'status': 'error',
                'message': 'ID de usuario no proporcionado'
            })
        
        # Obtener el otro usuario
        other_user = get_object_or_404(User, id=user_id)
        
        # Verificar si ya existe un chat privado entre estos usuarios
        existing_rooms = ChatRoom.objects.filter(
            is_group=False,
            participants=user
        ).filter(
            participants=other_user
        )
        
        if existing_rooms.exists():
            room = existing_rooms.first()
        else:
            # Crear nueva sala de chat
            room = ChatRoom.objects.create(is_group=False)
            room.participants.add(user, other_user)
        
        return JsonResponse({
            'status': 'success',
            'room_id': room.id
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Formato JSON inválido'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
def buscar_usuarios(request):
    """API para buscar usuarios por nombre o email"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({
            'status': 'error',
            'message': 'Consulta de búsqueda demasiado corta'
        })
    
    # Buscar usuarios por email o nombre completo
    users = User.objects.filter(
        Q(email__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id)[:10]  # Limitar a 10 resultados
    
    users_data = []
    for user in users:
        # Obtener URL de la imagen de perfil si está disponible
        profile_picture = None
        if hasattr(user, 'perfilusuario') and user.perfilusuario.foto_perfil:
            profile_picture = user.perfilusuario.foto_perfil.url
        
        # Usar primero nombre/apellido, si no hay, usar email
        display_name = f"{user.first_name} {user.last_name}".strip()
        if not display_name:
            display_name = user.email
        
        users_data.append({
            'id': user.id,
            'email': user.email,
            'full_name': display_name,
            'profile_picture': profile_picture
        })
    
    return JsonResponse({
        'status': 'success',
        'users': users_data
    })

@login_required
def dashboard_chat(request):
    """Vista para el chat en el dashboard estilo Facebook"""
    return render(request, 'chat_flotante/dashboard_chat_page.html', {
        'title': 'Chat',
        'active_section': 'chat',
    })

@login_required
def obtener_usuarios_sugeridos(request):
    """API para obtener una lista de usuarios sugeridos para iniciar conversación"""
    user = request.user
    
    # Obtener usuarios con los que ya ha chateado (participantes de sus salas)
    salas = ChatRoom.objects.filter(participants=user, is_group=False)
    usuarios_recientes = set()
    
    for sala in salas:
        otros_participantes = sala.participants.exclude(id=user.id)
        for otro_usuario in otros_participantes:
            usuarios_recientes.add(otro_usuario.id)
    
    # Primero incluir usuarios con los que ya ha chateado
    usuarios_recientes_queryset = User.objects.filter(id__in=usuarios_recientes)
    
    # Luego incluir otros usuarios (limitado a 20 en total)
    limite_restante = 20 - len(usuarios_recientes)
    otros_usuarios = User.objects.exclude(
        id__in=[user.id] + list(usuarios_recientes)
    ).order_by('-date_joined')[:limite_restante]
    
    # Combinar los resultados
    todos_usuarios = list(usuarios_recientes_queryset) + list(otros_usuarios)
    
    users_data = []
    for user_obj in todos_usuarios:
        # Obtener URL de la imagen de perfil si está disponible
        profile_picture = None
        if hasattr(user_obj, 'perfilusuario') and user_obj.perfilusuario.foto_perfil:
            profile_picture = user_obj.perfilusuario.foto_perfil.url
            
        # Usar primero nombre/apellido, si no hay, usar email
        display_name = f"{user_obj.first_name} {user_obj.last_name}".strip()
        if not display_name:
            display_name = user_obj.email
        
        users_data.append({
            'id': user_obj.id,
            'email': user_obj.email,
            'full_name': display_name,
            'profile_picture': profile_picture
        })
    
    return JsonResponse({
        'status': 'success',
        'users': users_data
    })
