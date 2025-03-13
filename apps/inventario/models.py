from django.db import models
from django.conf import settings

# Create your models here.

class CategoriaProducto(models.Model):
    nombre_categoria = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    categoria_padre = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategorias')
    propietario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='categorias_producto')

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
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=2)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    estado_producto = models.ForeignKey(EstadoProducto, on_delete=models.CASCADE)
    propietario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='productos_inventario')
    
    # Campos adicionales
    codigo_barras = models.CharField(max_length=100, blank=True, null=True)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.SET_NULL, blank=True, null=True)
    peso = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dimensiones = models.CharField(max_length=100, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.nombre_producto
        
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre_producto']

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
    propietario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='proveedores')

    def __str__(self):
        return self.nombre_proveedor

class PedidoProveedor(models.Model):
    ESTADO_PEDIDO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_TRANSITO', 'En Tránsito'),
        ('PARCIAL', 'Recibido Parcialmente'),
        ('RECIBIDO', 'Recibido Completamente'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha_pedido = models.DateField()
    fecha_entrega = models.DateField(blank=True, null=True)
    estado_pedido = models.CharField(max_length=50, choices=ESTADO_PEDIDO_CHOICES, default='PENDIENTE')
    propietario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='pedidos_proveedor')

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
    propietario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='almacenes')

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

# Modelo para las imágenes de productos
class ImagenProducto(models.Model):
    producto = models.ForeignKey(ProductoInventario, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/')
    es_principal = models.BooleanField(default=False)
    titulo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Imagen de Producto"
        verbose_name_plural = "Imágenes de Productos"
        ordering = ['-es_principal', '-fecha_creacion']
    
    def __str__(self):
        return f"Imagen de {self.producto.nombre_producto}"
    
    def save(self, *args, **kwargs):
        # Si esta imagen se marca como principal, quitar la marca de principal de otras imágenes
        if self.es_principal:
            ImagenProducto.objects.filter(
                producto=self.producto, 
                es_principal=True
            ).exclude(id=self.id).update(es_principal=False)
        super().save(*args, **kwargs)

# Modelo para notificaciones del sistema de inventario
class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('STOCK_BAJO', 'Stock Bajo'),
        ('PEDIDO_CREADO', 'Pedido Creado'),
        ('PEDIDO_RECIBIDO', 'Pedido Recibido'),
        ('PEDIDO_CANCELADO', 'Pedido Cancelado'),
        ('CADUCIDAD_PROXIMA', 'Caducidad Próxima'),
        ('MOVIMIENTO', 'Movimiento de Inventario'),
        ('SISTEMA', 'Sistema'),
    ]
    
    NIVEL_CHOICES = [
        ('INFO', 'Información'),
        ('WARNING', 'Advertencia'),
        ('ERROR', 'Error'),
        ('SUCCESS', 'Éxito'),
    ]
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones_inventario')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    nivel = models.CharField(max_length=10, choices=NIVEL_CHOICES, default='INFO')
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    enlace = models.CharField(max_length=255, blank=True, null=True)  # URL relativa a la que redirigir cuando se hace clic
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.get_tipo_display()}: {self.titulo}"
    
    def marcar_como_leida(self):
        self.leida = True
        self.save(update_fields=['leida'])
    
    @classmethod
    def crear_notificacion_stock_bajo(cls, usuario, producto):
        """Crea una notificación de stock bajo para un producto"""
        return cls.objects.create(
            usuario=usuario,
            tipo='STOCK_BAJO',
            nivel='WARNING',
            titulo=f'Stock bajo de {producto.nombre_producto}',
            mensaje=f'El producto {producto.nombre_producto} ha alcanzado un nivel de stock crítico. Cantidad actual: {producto.cantidad_disponible}',
            enlace=f'/inventario/productos/{producto.id}/'
        )
    
    @classmethod
    def crear_notificacion_pedido(cls, usuario, pedido, tipo_notificacion):
        """Crea una notificación relacionada con un pedido"""
        if tipo_notificacion == 'PEDIDO_CREADO':
            nivel = 'INFO'
            titulo = f'Nuevo pedido #{pedido.id} creado'
            mensaje = f'Se ha creado un nuevo pedido al proveedor {pedido.proveedor.nombre_proveedor}'
        elif tipo_notificacion == 'PEDIDO_RECIBIDO':
            nivel = 'SUCCESS'
            titulo = f'Pedido #{pedido.id} recibido'
            mensaje = f'El pedido al proveedor {pedido.proveedor.nombre_proveedor} ha sido recibido'
        elif tipo_notificacion == 'PEDIDO_CANCELADO':
            nivel = 'ERROR'
            titulo = f'Pedido #{pedido.id} cancelado'
            mensaje = f'El pedido al proveedor {pedido.proveedor.nombre_proveedor} ha sido cancelado'
        else:
            nivel = 'INFO'
            titulo = f'Actualización del pedido #{pedido.id}'
            mensaje = f'El pedido al proveedor {pedido.proveedor.nombre_proveedor} ha sido actualizado'
        
        return cls.objects.create(
            usuario=usuario,
            tipo=tipo_notificacion,
            nivel=nivel,
            titulo=titulo,
            mensaje=mensaje,
            enlace=f'/inventario/pedidos/{pedido.id}/'
        )
