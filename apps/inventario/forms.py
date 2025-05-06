from django import forms
from .models import (
    CategoriaProducto, EstadoProducto, UnidadMedida, ProductoInventario,
    MovimientoInventario, Proveedor, PedidoProveedor, DetallePedidoProveedor,
    Almacen, UbicacionAlmacen, InventarioAlmacen, CaducidadProducto,
    AlertaStock, ReservaInventario, ImagenProducto
)
from django.db.models import Q

class CategoriaProductoForm(forms.ModelForm):
    class Meta:
        model = CategoriaProducto
        fields = ['nombre_categoria', 'descripcion', 'categoria_padre', 'propietario']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'propietario': forms.HiddenInput(),  # Campo oculto
        }
    
    def __init__(self, *args, **kwargs):
        # Extraer el usuario de los kwargs antes de pasar al constructor padre
        user = kwargs.pop('user', None)
        super(CategoriaProductoForm, self).__init__(*args, **kwargs)
        
        # Si se proporcionó un usuario, pre-seleccionar el propietario
        if user:
            self.initial['propietario'] = user
            
            # Mostrar solo categorías padres del usuario y categorías sin propietario
            self.fields['categoria_padre'].queryset = CategoriaProducto.objects.filter(
                Q(propietario=user) | Q(propietario__isnull=True)
            ).order_by('nombre_categoria')

class EstadoProductoForm(forms.ModelForm):
    class Meta:
        model = EstadoProducto
        fields = ['nombre_estado']

class UnidadMedidaForm(forms.ModelForm):
    class Meta:
        model = UnidadMedida
        fields = ['nombre_unidad']

class ProductoInventarioForm(forms.ModelForm):
    class Meta:
        model = ProductoInventario
        fields = [
            'nombre_producto', 'descripcion_producto', 'categoria_producto',
            'cantidad_disponible', 'stock_minimo', 'precio_compra',
            'precio_venta', 'estado_producto', 'propietario'
        ]
        widgets = {
            'descripcion_producto': forms.Textarea(attrs={'rows': 3}),
            'propietario': forms.HiddenInput(),  # Campo oculto
        }

    def __init__(self, *args, **kwargs):
        # Extraer el usuario de los kwargs antes de pasar al constructor padre
        user = kwargs.pop('user', None)
        super(ProductoInventarioForm, self).__init__(*args, **kwargs)
        
        # Modificación: Mostrar todas las categorías disponibles en el sistema
        # para resolver el problema de categorías no accesibles
        self.fields['categoria_producto'].queryset = CategoriaProducto.objects.all()
        
        # Pre-seleccionar el propietario si se proporciona un usuario
        if user:
            # Asignar el usuario como valor inicial Y también como valor POST si es un formulario POST
            self.initial['propietario'] = user.id
            
            # Esto es crítico: Si estamos en un POST y no viene el propietario, lo añadimos a los datos
            if args and isinstance(args[0], dict) and 'propietario' not in args[0]:
                args[0]['propietario'] = user.id
                
            self.fields['propietario'].widget = forms.HiddenInput()
            # Hacemos que el campo no sea requerido para la validación, ya que lo asignaremos manualmente
            self.fields['propietario'].required = False

class MovimientoInventarioForm(forms.ModelForm):
    # Agregar un campo fecha explícito para usar con datepicker
    fecha_movimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha'
    )
    
    class Meta:
        model = MovimientoInventario
        fields = [
            'producto_inventario', 'tipo_movimiento', 'cantidad_movimiento',
            'descripcion_movimiento', 'referencia_documento', 'tipo_documento'
        ]
        widgets = {
            'descripcion_movimiento': forms.Textarea(attrs={'rows': 3}),
            'tipo_movimiento': forms.Select(choices=[
                ('', '---------'),
                ('ENTRADA', 'Entrada'),
                ('SALIDA', 'Salida'),
                ('AJUSTE', 'Ajuste')
            ]),
            'producto_inventario': forms.Select(attrs={'class': 'select2'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extraer el usuario de los kwargs antes de pasar al constructor padre
        user = kwargs.pop('user', None)
        super(MovimientoInventarioForm, self).__init__(*args, **kwargs)
        
        # Filtrar productos para mostrar solo los del usuario actual
        if user:
            self.fields['producto_inventario'].queryset = ProductoInventario.objects.filter(propietario=user)
            
            # Configurar el widget para product_inventario para usar con select2
            self.fields['producto_inventario'].widget.attrs.update({
                'class': 'select2',
                'data-placeholder': 'Seleccione un producto'
            })
            
            # Asegurar que el campo tipo_movimiento tenga opciones predefinidas
            self.fields['tipo_movimiento'].choices = [
                ('', '---------'),
                ('ENTRADA', 'Entrada'),
                ('SALIDA', 'Salida'),
                ('AJUSTE', 'Ajuste')
            ]
        
        # Agregar clases de bootstrap a los campos
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_movimiento = cleaned_data.get('tipo_movimiento')
        cantidad_movimiento = cleaned_data.get('cantidad_movimiento')
        producto_inventario = cleaned_data.get('producto_inventario')
        
        # Validar stock suficiente para movimientos de salida
        if tipo_movimiento == 'SALIDA' and producto_inventario and cantidad_movimiento:
            if producto_inventario.cantidad_disponible < cantidad_movimiento:
                raise forms.ValidationError(
                    f"No hay suficiente stock disponible. Stock actual: {producto_inventario.cantidad_disponible}"
                )
        
        return cleaned_data

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre_proveedor', 'direccion', 'telefono', 'email']

class PedidoProveedorForm(forms.ModelForm):
    class Meta:
        model = PedidoProveedor
        fields = ['proveedor', 'fecha_pedido', 'fecha_entrega', 'estado_pedido', 'propietario']
        widgets = {
            'fecha_pedido': forms.DateInput(attrs={'type': 'date'}),
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
            'propietario': forms.HiddenInput(),  # Campo oculto
        }
        
    def __init__(self, *args, **kwargs):
        # Extraer el usuario de los kwargs antes de pasar al constructor padre
        user = kwargs.pop('user', None)
        super(PedidoProveedorForm, self).__init__(*args, **kwargs)
        
        # Pre-seleccionar el propietario si se proporciona un usuario
        if user:
            self.initial['propietario'] = user.id
            
            # Esto es crítico: Si estamos en un POST y no viene el propietario, lo añadimos a los datos
            if args and isinstance(args[0], dict) and 'propietario' not in args[0]:
                args[0]['propietario'] = user.id

class DetallePedidoProveedorForm(forms.ModelForm):
    class Meta:
        model = DetallePedidoProveedor
        fields = ['producto_inventario', 'cantidad', 'precio_unitario']

    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get('cantidad')
        precio_unitario = cleaned_data.get('precio_unitario')
        
        if cantidad and precio_unitario:
            cleaned_data['subtotal'] = cantidad * precio_unitario
        
        return cleaned_data

class AlmacenForm(forms.ModelForm):
    class Meta:
        model = Almacen
        fields = ['nombre_almacen', 'direccion', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

class UbicacionAlmacenForm(forms.ModelForm):
    class Meta:
        model = UbicacionAlmacen
        fields = ['nombre_ubicacion']

class InventarioAlmacenForm(forms.ModelForm):
    class Meta:
        model = InventarioAlmacen
        fields = ['producto_inventario', 'cantidad']
        labels = {
            'producto_inventario': 'Producto',
            'cantidad': 'Cantidad'
        }
        widgets = {
            'producto_inventario': forms.Select(attrs={'class': 'form-control select2'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
        }
        
    def __init__(self, *args, **kwargs):
        # Extraer el usuario de los kwargs antes de pasar al constructor padre
        user = kwargs.pop('user', None)
        super(InventarioAlmacenForm, self).__init__(*args, **kwargs)
        
        # Filtrar productos para mostrar solo los del usuario actual
        if user:
            self.fields['producto_inventario'].queryset = ProductoInventario.objects.filter(propietario=user)

class CaducidadProductoForm(forms.ModelForm):
    class Meta:
        model = CaducidadProducto
        fields = ['producto_inventario', 'fecha_caducidad', 'cantidad_disponible']
        widgets = {
            'fecha_caducidad': forms.DateInput(attrs={'type': 'date'}),
        }

class AlertaStockForm(forms.ModelForm):
    class Meta:
        model = AlertaStock
        fields = ['producto_inventario', 'cantidad_disponible']

class ReservaInventarioForm(forms.ModelForm):
    class Meta:
        model = ReservaInventario
        fields = ['producto_inventario', 'cantidad', 'usuario', 'fecha_expiracion']
        widgets = {
            'fecha_expiracion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ImagenProductoForm(forms.ModelForm):
    """Formulario para gestionar imágenes de productos"""
    class Meta:
        model = ImagenProducto
        fields = ['imagen', 'titulo', 'descripcion', 'es_principal']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'es_principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'imagen': 'Seleccionar imagen',
            'titulo': 'Título (opcional)',
            'descripcion': 'Descripción (opcional)',
            'es_principal': 'Establecer como imagen principal'
        }
        help_texts = {
            'es_principal': 'Si marcas esta opción, esta imagen se mostrará como la principal del producto.'
        }

class ImagenesMultiplesForm(forms.Form):
    """Formulario para subir múltiples imágenes a la vez"""
    imagenes = forms.FileField(
        label='Seleccionar imágenes', 
        help_text='Puede seleccionar múltiples imágenes manteniendo presionada la tecla Ctrl.',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    ) 

class RecepcionPedidoForm(forms.Form):
    """Formulario para registrar la recepción de productos de un pedido"""
    notas_recepcion = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        label='Notas de Recepción'
    ) 