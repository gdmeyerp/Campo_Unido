from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Post(models.Model):
    """
    Modelo para las publicaciones de los usuarios en el feed social.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='social_feed_posts',
        verbose_name=_('Usuario')
    )
    contenido = models.TextField(
        verbose_name=_('Contenido'),
        blank=True,
        null=True
    )
    fecha_creacion = models.DateTimeField(
        verbose_name=_('Fecha de creación'),
        default=timezone.now
    )
    fecha_actualizacion = models.DateTimeField(
        verbose_name=_('Fecha de actualización'),
        auto_now=True
    )
    es_publico = models.BooleanField(
        verbose_name=_('Es público'),
        default=True,
        help_text=_('Si es falso, solo los amigos pueden ver la publicación')
    )

    class Meta:
        verbose_name = _('Publicación')
        verbose_name_plural = _('Publicaciones')
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Post de {self.usuario.username} - {self.fecha_creacion.strftime("%d/%m/%Y %H:%M")}'
    
    @property
    def total_likes(self):
        return self.likes.count()
    
    @property
    def total_comentarios(self):
        return self.comentarios.count()


class Multimedia(models.Model):
    """
    Modelo para archivos multimedia (imágenes y videos) asociados a un post.
    """
    TIPO_CHOICES = (
        ('imagen', _('Imagen')),
        ('video', _('Video')),
        ('documento', _('Documento')),
        ('otro', _('Otro')),
    )
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='multimedia',
        verbose_name=_('Post')
    )
    archivo = models.FileField(
        upload_to='social_feed/multimedia/%Y/%m/',
        verbose_name=_('Archivo')
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name=_('Tipo')
    )
    titulo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Título')
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Descripción')
    )
    fecha_subida = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de subida')
    )

    class Meta:
        verbose_name = _('Archivo multimedia')
        verbose_name_plural = _('Archivos multimedia')
        ordering = ['fecha_subida']

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.titulo or "Sin título"}'
    
    @property
    def es_imagen(self):
        return self.tipo == 'imagen'
    
    @property
    def es_video(self):
        return self.tipo == 'video'


class Comentario(models.Model):
    """
    Modelo para los comentarios en las publicaciones.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name=_('Post')
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='social_feed_comentarios',
        verbose_name=_('Usuario')
    )
    contenido = models.TextField(
        verbose_name=_('Contenido')
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    comentario_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='respuestas',
        verbose_name=_('Comentario padre')
    )

    class Meta:
        verbose_name = _('Comentario')
        verbose_name_plural = _('Comentarios')
        ordering = ['fecha_creacion']

    def __str__(self):
        return f'Comentario de {self.usuario.username} en {self.post}'


class Like(models.Model):
    """
    Modelo para los likes en las publicaciones.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('Post')
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='social_feed_likes',
        verbose_name=_('Usuario')
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )

    class Meta:
        verbose_name = _('Like')
        verbose_name_plural = _('Likes')
        unique_together = ('post', 'usuario')
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Like de {self.usuario.username} en {self.post}'
