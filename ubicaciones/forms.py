from django import forms
from .models import Pais, Estado, Ciudad, Ubicacion

class PaisForm(forms.ModelForm):
    class Meta:
        model = Pais
        fields = ['nombre_pais', 'codigo_iso']

class EstadoForm(forms.ModelForm):
    class Meta:
        model = Estado
        fields = ['nombre_estado', 'pais']

class CiudadForm(forms.ModelForm):
    class Meta:
        model = Ciudad
        fields = ['nombre_ciudad', 'estado', 'tipo_zona']

class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = ['direccion', 'ciudad', 'codigo_postal', 'latitud', 'longitud', 'altitud', 'zona_horaria']
