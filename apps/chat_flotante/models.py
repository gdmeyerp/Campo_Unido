from django.db import models
from django.conf import settings

class ChatRoom(models.Model):
    """Modelo para las salas de chat"""
    name = models.CharField(max_length=255, blank=True, verbose_name="Nombre")
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='chat_rooms_flotante',
        verbose_name="Participantes"
    )
    is_group = models.BooleanField(default=False, verbose_name="Es grupo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Sala de Chat"
        verbose_name_plural = "Salas de Chat"
        ordering = ['-updated_at']

    def __str__(self):
        if self.is_group:
            return f"Grupo: {self.name}"
        return self.name or f"Chat {self.id}"

    def get_other_participant(self, user):
        """Obtiene el otro participante en chats privados (1 a 1)"""
        if self.is_group:
            return None
        return self.participants.exclude(id=user.id).first()


class ChatMessage(models.Model):
    """Modelo para los mensajes de chat"""
    # Constantes para tipos de mensaje
    TYPE_TEXT = 'text'
    TYPE_IMAGE = 'image'
    
    MESSAGE_TYPES = (
        (TYPE_TEXT, 'Texto'),
        (TYPE_IMAGE, 'Imagen'),
    )
    
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Sala"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_messages_flotante',
        verbose_name="Remitente"
    )
    content = models.TextField(verbose_name="Contenido")
    message_type = models.CharField(
        max_length=10, 
        choices=MESSAGE_TYPES, 
        default=TYPE_TEXT,
        verbose_name="Tipo de mensaje"
    )
    image = models.ImageField(
        upload_to='chat_images/', 
        blank=True, 
        null=True,
        verbose_name="Imagen"
    )
    is_read = models.BooleanField(default=False, verbose_name="Leído")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de envío")

    class Meta:
        verbose_name = "Mensaje de Chat"
        verbose_name_plural = "Mensajes de Chat"
        ordering = ['created_at']

    def __str__(self):
        return f"Mensaje de {self.sender} en {self.room}"
