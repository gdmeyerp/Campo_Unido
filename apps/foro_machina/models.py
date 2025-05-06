from django.db import models
from django.conf import settings
from machina.core.db.models import get_model
from django.utils.translation import gettext_lazy as _

# Obtener los modelos necesarios
Forum = get_model('forum', 'Forum')
Topic = get_model('forum_conversation', 'Topic')
Post = get_model('forum_conversation', 'Post')

# Añadir el campo created_by al modelo Forum
if not hasattr(Forum, 'created_by'):
    created_by_field = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_forums',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Creado por'
    )
    created_by_field.contribute_to_class(Forum, 'created_by')

class TopicTag(models.Model):
    """
    Modelo para las etiquetas de los temas del foro.
    """
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Nombre'))
    slug = models.SlugField(max_length=50, unique=True, verbose_name=_('Slug'))
    color = models.CharField(max_length=7, default='#007bff', verbose_name=_('Color'))
    topics = models.ManyToManyField(Topic, related_name='tags', verbose_name=_('Temas'))
    
    class Meta:
        verbose_name = _('Etiqueta de tema')
        verbose_name_plural = _('Etiquetas de temas')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class TopicAttachment(models.Model):
    """
    Modelo para almacenar archivos adjuntos a temas del foro.
    """
    topic = models.ForeignKey(
        Topic,
        related_name='attachments',
        on_delete=models.CASCADE,
        verbose_name=_('Tema')
    )
    post = models.ForeignKey(
        Post,
        related_name='custom_attachments',
        on_delete=models.CASCADE,
        verbose_name=_('Post'),
        null=True,
        blank=True
    )
    file = models.FileField(
        upload_to='forum_attachments',
        verbose_name=_('Archivo')
    )
    filename = models.CharField(
        max_length=255,
        verbose_name=_('Nombre del archivo')
    )
    mimetype = models.CharField(
        max_length=100,
        verbose_name=_('Tipo MIME')
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )

    class Meta:
        verbose_name = _('Archivo adjunto')
        verbose_name_plural = _('Archivos adjuntos')
        ordering = ['-created']

    def __str__(self):
        return self.filename
