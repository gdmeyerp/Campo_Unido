from django import forms
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from .models import CategoriaProducto, Producto

class ProductoForm(forms.ModelForm):
    """
    Formulario para crear y editar productos en el marketplace
    """
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'descripcion',
            'precio',
            'stock',
            'imagen',
            'categoria',
            'activo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción',
            'precio': 'Precio',
            'stock': 'Stock disponible',
            'imagen': 'Imagen del producto',
            'categoria': 'Categoría',
            'activo': 'Producto activo'
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if len(nombre) < 3:
            raise ValidationError('El nombre del producto debe tener al menos 3 caracteres')
        return nombre

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio <= 0:
            raise ValidationError('El precio debe ser mayor que cero')
        return precio

class CategoriaProductoForm(forms.ModelForm):
    """
    Formulario para crear y editar categorías de productos
    """
    class Meta:
        model = CategoriaProducto
        fields = ['nombre', 'descripcion', 'imagen', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        # Convertir el nombre a slug para validar unicidad
        slug = slugify(nombre)
        
        # Verificar si ya existe una categoría con el mismo slug
        if CategoriaProducto.objects.filter(slug=slug).exists():
            if self.instance and self.instance.slug == slug:
                # Si estamos editando y el slug no cambió, está bien
                return nombre
            raise ValidationError('Ya existe una categoría con un nombre similar')
        
        return nombre 