from django import forms
from django.utils.translation import gettext_lazy as _
from machina.apps.forum.models import Forum
from machina.core.db.models import get_model
from machina.core.loading import get_class
from mptt.forms import TreeNodeChoiceField
from machina.apps.forum_conversation.forms import TopicForm as BaseTopicForm
from machina.apps.forum_conversation.forms import PostForm as BasePostForm
from .models import TopicTag, TopicAttachment

ForumVisibilityContentTree = get_class('forum.visibility', 'ForumVisibilityContentTree')

class ForumForm(forms.ModelForm):
    """
    Formulario para crear y editar foros.
    """
    parent = TreeNodeChoiceField(
        queryset=Forum.objects.all(),
        required=False,
        label=_('Foro padre'),
        empty_label=_('Ninguno (foro raíz)'),
    )

    class Meta:
        model = Forum
        fields = ['name', 'description', 'parent', 'type', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        self.forum_instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        
        # Configurar el campo parent para excluir el foro actual y sus descendientes
        if self.forum_instance and self.forum_instance.pk:
            descendants = self.forum_instance.get_descendants()
            self.fields['parent'].queryset = Forum.objects.exclude(
                pk__in=[self.forum_instance.pk] + [d.pk for d in descendants]
            )
        
        # Añadir clases de Bootstrap a los campos
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        
        # Añadir textos de ayuda
        self.fields['type'].help_text = _('Un foro puede ser una categoría que contiene otros foros o un foro estándar donde se pueden crear temas.')
        self.fields['parent'].help_text = _('Selecciona un foro padre para crear una jerarquía. Deja en blanco para crear un foro de nivel superior.')
        self.fields['image'].help_text = _('Imagen opcional para el foro. Tamaño recomendado: 100x100px.')

class TopicForm(BaseTopicForm):
    """
    Formulario extendido para la creación de temas.
    """
    tags = forms.CharField(
        label=_('Etiquetas'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Separadas por comas (ej: ayuda, pregunta, importante)'),
            'data-role': 'tagsinput'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.forum = kwargs.pop('forum', None)
        super(TopicForm, self).__init__(*args, **kwargs)

    class Meta(BaseTopicForm.Meta):
        fields = BaseTopicForm.Meta.fields + ['tags']

class PostForm(BasePostForm):
    """
    Formulario para crear o editar un post.
    """
    attachment = forms.FileField(
        label=_('Archivo adjunto'),
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        help_text=_('Puedes adjuntar un archivo a tu mensaje.'),
    )
    
    class Meta(BasePostForm.Meta):
        fields = ['subject', 'content', 'attachment']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'class': 'form-control',
            'rows': 8,
        })
        if 'subject' in self.fields:
            self.fields['subject'].widget.attrs.update({
                'class': 'form-control',
            })
    
    def save(self, commit=True):
        post = super(PostForm, self).save(commit=False)
        
        if commit:
            post.save()
        
        return post 