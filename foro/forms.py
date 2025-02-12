from django import forms
from .models import Foro, PublicacionForo, ComentarioPublicacion

class ForoForm(forms.ModelForm):
    class Meta:
        model = Foro
        fields = ['categoria', 'titulo_foro', 'descripcion_foro', 'estado_foro']

class PublicacionForm(forms.ModelForm):
    class Meta:
        model = PublicacionForo
        fields = ['titulo_publicacion', 'contenido_publicacion', 'estado_publicacion']

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = ComentarioPublicacion
        fields = ['contenido_comentario', 'estado_comentario']
