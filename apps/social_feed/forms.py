from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, Comentario, Multimedia


class PostForm(forms.ModelForm):
    """
    Formulario para crear y editar publicaciones.
    """
    class Meta:
        model = Post
        fields = ['contenido', 'es_publico']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('¿Qué estás pensando?')
            }),
            'es_publico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class MultimediaForm(forms.ModelForm):
    """
    Formulario para subir archivos multimedia (imágenes y videos).
    """
    class Meta:
        model = Multimedia
        fields = ['archivo', 'tipo', 'titulo', 'descripcion']
        widgets = {
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,video/*'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Título (opcional)')
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('Descripción (opcional)')
            })
        }


class ComentarioForm(forms.ModelForm):
    """
    Formulario para crear comentarios.
    """
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('Escribe un comentario...')
            })
        }


class MultimediaFormSet(forms.BaseModelFormSet):
    """
    FormSet para manejar múltiples archivos multimedia en un solo post.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Multimedia.objects.none()


MultimediaFormSet = forms.modelformset_factory(
    Multimedia,
    form=MultimediaForm,
    formset=MultimediaFormSet,
    extra=3,
    max_num=10,
    can_delete=True
) 