from django.urls import path
from . import views

app_name = 'chat_flotante'

urlpatterns = [
    # API para conversaciones
    path('api/conversaciones/', views.get_conversations, name='get_conversations'),
    path('api/mensajes/<int:room_id>/', views.get_messages, name='get_messages'),
    path('api/enviar/<int:room_id>/', views.send_message, name='send_message'),
    path('api/sala-info/', views.get_room_info, name='get_room_info'),
    path('api/crear-chat/', views.create_chat, name='create_chat'),
    path('api/buscar-usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
    path('api/usuarios-sugeridos/', views.obtener_usuarios_sugeridos, name='usuarios_sugeridos'),
    
    # Vista para el dashboard chat
    path('dashboard/', views.dashboard_chat, name='dashboard_chat'),
] 