from django import forms
from .models import (
    CategoriaProducto, EstadoProducto, UnidadMedida, ProductoInventario,
    MovimientoInventario, Proveedor, PedidoProveedor, DetallePedidoProveedor,
    Almacen, UbicacionAlmacen, InventarioAlmacen, CaducidadProducto,
    AlertaStock, ReservaInventario
)

class CategoriaProductoForm(forms.ModelForm):
    class Meta:
        model = CategoriaProducto
        fields = ['nombre_categoria', 'descripcion', 'categoria_padre']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

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
            'precio_venta', 'estado_producto'
        ]
        widgets = {
            'descripcion_producto': forms.Textarea(attrs={'rows': 3}),
        }

class MovimientoInventarioForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = [
            'producto_inventario', 'tipo_movimiento', 'cantidad_movimiento',
            'descripcion_movimiento', 'referencia_documento', 'tipo_documento'
        ]
        widgets = {
            'descripcion_movimiento': forms.Textarea(attrs={'rows': 3}),
        }

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre_proveedor', 'direccion', 'telefono', 'email']

class PedidoProveedorForm(forms.ModelForm):
    class Meta:
        model = PedidoProveedor
        fields = ['proveedor', 'fecha_pedido', 'fecha_entrega', 'estado_pedido']
        widgets = {
            'fecha_pedido': forms.DateInput(attrs={'type': 'date'}),
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
        }

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