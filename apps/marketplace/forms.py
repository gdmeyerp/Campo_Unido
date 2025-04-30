from django import forms
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from apps.inventario.models import ProductoInventario
from .models import MarketplaceProducto, CategoriaProducto, EstadoProducto, UnidadMedida, ImagenProducto

class InventarioToMarketplaceForm(forms.Form):
    """
    Form para convertir productos de inventario a productos de marketplace
    """
    producto_inventario = forms.ModelChoiceField(
        queryset=ProductoInventario.objects.filter(cantidad_disponible__gt=0),
        label="Producto de Inventario",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    cantidad_a_vender = forms.IntegerField(
        min_value=1,
        label="Cantidad para venta",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    precio_base = forms.DecimalField(
        max_digits=10, 
        decimal_places=5,
        label="Precio base",
        help_text="El precio sugerido se carga automáticamente, pero puede modificarlo",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    descripcion = forms.CharField(
        required=True,
        label="Descripción del producto",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    categoria_producto_id_id = forms.ModelChoiceField(
        queryset=CategoriaProducto.objects.all(),
        label="Categoría",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    estado_producto_id_id = forms.ModelChoiceField(
        queryset=EstadoProducto.objects.all(),
        label="Estado del producto",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    unidad_medida_id_id = forms.ModelChoiceField(
        queryset=UnidadMedida.objects.all(),
        label="Unidad de medida",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Campos para imágenes
    imagen_principal = forms.ImageField(
        label="Imagen Principal",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    imagen_adicional1 = forms.ImageField(
        label="Imagen Adicional 1",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    imagen_adicional2 = forms.ImageField(
        label="Imagen Adicional 2",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    imagen_adicional3 = forms.ImageField(
        label="Imagen Adicional 3",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    # Campos adicionales
    destacado = forms.BooleanField(
        required=False,
        label="Destacar producto",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    es_organico = forms.BooleanField(
        required=False,
        label="Producto orgánico",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si hay un producto seleccionado, cargar su precio como sugerencia
        if 'producto_inventario' in self.data:
            try:
                producto_id = int(self.data.get('producto_inventario'))
                producto = ProductoInventario.objects.get(id=producto_id)
                self.fields['precio_base'].initial = producto.precio_venta
                self.fields['cantidad_a_vender'].max_value = producto.cantidad_disponible
            except (ValueError, ProductoInventario.DoesNotExist):
                pass

class ProductoMarketplaceForm(forms.ModelForm):
    """
    Form para editar los detalles de un producto en el marketplace
    """
    imagen_1 = forms.ImageField(
        label="Imagen 1",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    imagen_2 = forms.ImageField(
        label="Imagen 2",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    imagen_3 = forms.ImageField(
        label="Imagen 3", 
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = MarketplaceProducto
        fields = [
            'nombre_producto',
            'descripcion',
            'categoria_producto_id_id',
            'estado_producto_id_id',
            'unidad_medida_id_id',
            'precio_base',
            'stock_actual',
            'disponibilidad',
            'ubicacion_id_id'
        ]
        widgets = {
            'nombre_producto': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria_producto_id_id': forms.Select(attrs={'class': 'form-select'}),
            'estado_producto_id_id': forms.Select(attrs={'class': 'form-select'}),
            'unidad_medida_id_id': forms.Select(attrs={'class': 'form-select'}),
            'precio_base': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'disponibilidad': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ubicacion_id_id': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'nombre_producto': 'Nombre del Producto',
            'descripcion': 'Descripción',
            'categoria_producto_id_id': 'Categoría',
            'estado_producto_id_id': 'Estado',
            'unidad_medida_id_id': 'Unidad de Medida',
            'precio_base': 'Precio Base',
            'stock_actual': 'Stock Actual',
            'disponibilidad': 'Disponible',
            'ubicacion_id_id': 'Ubicación'
        }

class ProductoExternoForm(forms.Form):
    """
    Formulario para añadir un producto al marketplace a partir de una fuente externa
    (reemplaza la dependencia directa con ProductoInventario)
    """
    id_producto_externo = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    sistema_origen = forms.CharField(
        max_length=50,
        widget=forms.HiddenInput(),
        initial="inventario"
    )
    
    nombre_producto = forms.CharField(
        max_length=255,
        label="Nombre del Producto",
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    
    cantidad_disponible = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    
    cantidad_a_vender = forms.IntegerField(
        min_value=1,
        label="Cantidad para venta",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    precio_base = forms.DecimalField(
        max_digits=10,
        decimal_places=5,
        label="Precio base",
        help_text="El precio sugerido se carga automáticamente, pero puede modificarlo",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    descripcion = forms.CharField(
        required=True,
        label="Descripción del producto",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    categoria_producto_id_id = forms.ModelChoiceField(
        queryset=CategoriaProducto.objects.all(),
        label="Categoría",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    estado_producto_id_id = forms.ModelChoiceField(
        queryset=EstadoProducto.objects.all(),
        label="Estado del producto",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    unidad_medida_id_id = forms.ModelChoiceField(
        queryset=UnidadMedida.objects.all(),
        label="Unidad de medida",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Campos para imágenes
    imagen_principal = forms.ImageField(
        label="Imagen Principal",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    imagen_adicional1 = forms.ImageField(
        label="Imagen Adicional 1",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    imagen_adicional2 = forms.ImageField(
        label="Imagen Adicional 2",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    imagen_adicional3 = forms.ImageField(
        label="Imagen Adicional 3",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    # Campos adicionales
    destacado = forms.BooleanField(
        required=False,
        label="Destacar producto",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    es_organico = forms.BooleanField(
        required=False,
        label="Producto orgánico",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        cleaned_data = super().clean()
        # Esta validación se traslada a la vista que utilizará la API
        return cleaned_data 