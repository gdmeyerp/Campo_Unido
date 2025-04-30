from django import forms
from .models import Ubicacion, Ciudad, Estado, Pais


class UbicacionForm(forms.ModelForm):
    pais = forms.ModelChoiceField(
        queryset=Pais.objects.all().order_by('nombre'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_pais'})
    )
    
    estado = forms.ModelChoiceField(
        queryset=Estado.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_estado'})
    )
    
    class Meta:
        model = Ubicacion
        fields = ['nombre', 'direccion', 'codigo_postal', 'ciudad', 'latitud', 'longitud', 'es_principal']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.Select(attrs={'class': 'form-control'}),
            'latitud': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0000001'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0000001'}),
            'es_principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer que la ciudad sea requerida
        self.fields['ciudad'].required = True
        
        # Configurar el queryset inicial para la ciudad (vacío al principio)
        self.fields['ciudad'].queryset = Ciudad.objects.none()
        
        # Si estamos editando una ubicación existente
        if 'instance' in kwargs and kwargs['instance']:
            ubicacion = kwargs['instance']
            if ubicacion.ciudad and ubicacion.ciudad.estado:
                estado = ubicacion.ciudad.estado
                pais = estado.pais
                
                # Configurar los campos iniciales
                self.fields['pais'].initial = pais
                self.fields['estado'].queryset = Estado.objects.filter(pais=pais)
                self.fields['estado'].initial = estado
                self.fields['ciudad'].queryset = Ciudad.objects.filter(estado=estado)
        
        # Si hay datos POST
        if 'data' in kwargs:
            data = kwargs['data']
            if data.get('pais'):
                try:
                    pais_id = int(data.get('pais'))
                    self.fields['estado'].queryset = Estado.objects.filter(pais_id=pais_id)
                    
                    if data.get('estado'):
                        try:
                            estado_id = int(data.get('estado'))
                            self.fields['ciudad'].queryset = Ciudad.objects.filter(estado_id=estado_id)
                        except (ValueError, TypeError):
                            pass
                except (ValueError, TypeError):
                    pass
        
        # Agregar clases adicionales para los campos específicos
        self.fields['latitud'].widget.attrs.update({'placeholder': 'Ej: 4.7110'})
        self.fields['longitud'].widget.attrs.update({'placeholder': 'Ej: -74.0721'})
        
    def clean(self):
        cleaned_data = super().clean()
        pais = cleaned_data.get('pais')
        estado = cleaned_data.get('estado')
        ciudad = cleaned_data.get('ciudad')
        latitud = cleaned_data.get('latitud')
        longitud = cleaned_data.get('longitud')
        
        # Validar que la ciudad pertenezca al estado seleccionado
        if estado and ciudad and ciudad.estado != estado:
            self.add_error('ciudad', 'La ciudad seleccionada no pertenece al estado/departamento seleccionado.')
        
        # Validar que el estado pertenezca al país seleccionado
        if pais and estado and estado.pais != pais:
            self.add_error('estado', 'El estado/departamento seleccionado no pertenece al país seleccionado.')
        
        # Validar que ambos campos de coordenadas estén presentes o ambos ausentes
        if (latitud is None and longitud is not None) or (latitud is not None and longitud is None):
            raise forms.ValidationError(
                "Debe proporcionar tanto latitud como longitud, o dejar ambos campos en blanco."
            )
            
        # Validar el rango de latitud y longitud
        if latitud is not None:
            if latitud < -90 or latitud > 90:
                self.add_error('latitud', 'La latitud debe estar entre -90 y 90.')
                
        if longitud is not None:
            if longitud < -180 or longitud > 180:
                self.add_error('longitud', 'La longitud debe estar entre -180 y 180.')
        
        return cleaned_data 