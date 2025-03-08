from django.db import models
from django.conf import settings

# Create your models here.

class CategoriaProducto(models.Model):
    nombre_categoria = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    categoria_padre = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategorias')

    def __str__(self):
        return self.nombre_categoria

class EstadoProducto(models.Model):
    nombre_estado = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_estado

class UnidadMedida(models.Model):
    nombre_unidad = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_unidad

class ProductoInventario(models.Model):
    nombre_producto = models.CharField(max_length=255)
    descripcion_producto = models.TextField(blank=True, null=True)
    categoria_producto = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)
    cantidad_disponible = models.IntegerField()
    stock_minimo = models.IntegerField()
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    estado_producto = models.ForeignKey(EstadoProducto, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_producto

class MovimientoInventario(models.Model):
    producto_inventario = models.ForeignKey(ProductoInventario, on_delete=models.CASCADE)
    tipo_movimiento = models.CharField(max_length=50)
    cantidad_movimiento = models.IntegerField()
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    descripcion_movimiento = models.TextField(blank=True, null=True)
    referencia_documento = models.CharField(max_length=255, blank=True, null=True)
    tipo_documento = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.producto_inventario.nombre_producto}"

class Proveedor(models.Model):
    nombre_proveedor = models.CharField(max_length=255)
    rif = models.CharField(max_length=20, blank=True, null=True, verbose_name="RIF")
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    contacto = models.CharField(max_length=100, blank=True, null=True, verbose_name="Persona de contacto")
    categoria = models.CharField(max_length=50, blank=True, null=True, verbose_name="Categoría")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas adicionales")

    def __str__(self):
        return self.nombre_proveedor

class PedidoProveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha_pedido = models.DateField()
    fecha_entrega = models.DateField(blank=True, null=True)
    estado_pedido = models.CharField(max_length=50)

    def __str__(self):
        return f"Pedido {self.id} - {self.proveedor.nombre_proveedor}"

    def calcular_total(self):
        """Calcula el total del pedido sumando los subtotales de sus detalles."""
        detalles = self.detallepedidoproveedor_set.all()
        total = sum(detalle.subtotal for detalle in detalles) if detalles else 0
        
        # Si existe un campo para almacenar el total, lo actualizamos
        if hasattr(self, 'total'):
            self.total = total
        
        return total

class DetallePedidoProveedor(models.Model):
    pedido_proveedor = models.ForeignKey(PedidoProveedor, on_delete=models.CASCADE)
    producto_inventario = models.ForeignKey(ProductoInventario, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto_inventario.nombre_producto} - {self.cantidad} unidades"

class Almacen(models.Model):
    nombre_almacen = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_almacen

class UbicacionAlmacen(models.Model):
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    nombre_ubicacion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nombre_ubicacion} - {self.almacen.nombre_almacen}"

class InventarioAlmacen(models.Model):
    producto_inventario = models.ForeignKey(ProductoInventario, on_delete=models.CASCADE, related_name='inventarios')
    ubicacion_almacen = models.ForeignKey(UbicacionAlmacen, on_delete=models.CASCADE, related_name='inventarios')
    cantidad = models.IntegerField(default=0)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Inventario en Almacén"
        verbose_name_plural = "Inventarios en Almacenes"
        unique_together = ('producto_inventario', 'ubicacion_almacen')
    
    def __str__(self):
        return f"{self.producto_inventario.nombre_producto} en {self.ubicacion_almacen.nombre_ubicacion} ({self.cantidad} unidades)"

class CaducidadProducto(models.Model):
    producto_inventario = models.ForeignKey(ProductoInventario, on_delete=models.CASCADE)
    fecha_caducidad = models.DateField()
    cantidad_disponible = models.IntegerField()

    def __str__(self):
        return f"{self.producto_inventario.nombre_producto} - Caduca el {self.fecha_caducidad}"

class AlertaStock(models.Model):
    producto_inventario = models.ForeignKey(ProductoInventario, on_delete=models.CASCADE)
    fecha_alerta = models.DateTimeField(auto_now_add=True)
    cantidad_disponible = models.IntegerField()

    def __str__(self):
        return f"Alerta de stock - {self.producto_inventario.nombre_producto}"

class ReservaInventario(models.Model):
    producto_inventario = models.ForeignKey(ProductoInventario, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(blank=True, null=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reserva de {self.producto_inventario.nombre_producto} - {self.cantidad} unidades"
