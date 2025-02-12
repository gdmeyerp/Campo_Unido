from django.db import models
from core.models import User
from ubicaciones.models import Ubicacion

# Categoría de productos con soporte para subcategorías
class CategoriaProducto(models.Model):
    categoria_producto_id = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria_padre_id = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_categoria

# Estado del producto
class EstadoProducto(models.Model):
    estado_producto_id = models.AutoField(primary_key=True)
    nombre_estado = models.CharField(max_length=50)  # Ejemplos: "Nuevo", "Usado", "Reacondicionado"

    def __str__(self):
        return self.nombre_estado

# Unidad de medida del producto
class UnidadMedida(models.Model):
    unidad_medida_id = models.AutoField(primary_key=True)
    nombre_unidad = models.CharField(max_length=50)  # Ejemplos: "Kilogramo", "Litro", "Unidad"

    def __str__(self):
        return self.nombre_unidad

# Información sobre productos en el marketplace
class MarketplaceProducto(models.Model):
    producto_id = models.AutoField(primary_key=True)
    vendedor_id = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre_producto = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria_producto_id = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)
    estado_producto_id = models.ForeignKey(EstadoProducto, on_delete=models.CASCADE)
    unidad_medida_id = models.ForeignKey(UnidadMedida, on_delete=models.CASCADE)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.IntegerField()
    ubicacion_id = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    disponibilidad = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_producto

# Historial de cambios en el precio de productos
class HistorialPrecioProducto(models.Model):
    historial_precio_id = models.AutoField(primary_key=True)
    producto_id = models.ForeignKey(MarketplaceProducto, on_delete=models.CASCADE)
    precio_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    precio_nuevo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    motivo_cambio = models.TextField(blank=True)

# Promociones y descuentos aplicados a productos
class PromocionProducto(models.Model):
    promocion_id = models.AutoField(primary_key=True)
    producto_id = models.ForeignKey(MarketplaceProducto, on_delete=models.CASCADE)
    descripcion_promocion = models.TextField()
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()

# Detalles de la compra realizada por un usuario
class Compra(models.Model):
    compra_id = models.AutoField(primary_key=True)
    comprador_id = models.ForeignKey(User, on_delete=models.CASCADE)
    total_compra = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    estado_compra_id = models.ForeignKey('EstadoCompra', on_delete=models.SET_NULL, null=True)
    metodo_pago_id = models.ForeignKey('MetodoPago', on_delete=models.SET_NULL, null=True)
    direccion_envio_id = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True)

# Detalle de productos dentro de una compra específica
class DetalleCompra(models.Model):
    detalle_compra_id = models.AutoField(primary_key=True)
    compra_id = models.ForeignKey(Compra, on_delete=models.CASCADE)
    producto_id = models.ForeignKey(MarketplaceProducto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

# Estado de la compra para controlar el ciclo de vida de una compra
class EstadoCompra(models.Model):
    estado_compra_id = models.AutoField(primary_key=True)
    nombre_estado = models.CharField(max_length=50)  # Ejemplos: "Pendiente", "Enviado", "Completado", "Cancelado"

    def __str__(self):
        return self.nombre_estado

# Métodos de pago disponibles en la plataforma
class MetodoPago(models.Model):
    metodo_pago_id = models.AutoField(primary_key=True)
    nombre_metodo_pago = models.CharField(max_length=100)  # Ejemplos: "Tarjeta de Crédito", "PayPal", "Transferencia Bancaria"

    def __str__(self):
        return self.nombre_metodo_pago

# Valoraciones y comentarios de productos
class ValoracionProducto(models.Model):
    valoracion_id = models.AutoField(primary_key=True)
    producto_id = models.ForeignKey(MarketplaceProducto, on_delete=models.CASCADE)
    usuario_id = models.ForeignKey(User, on_delete=models.CASCADE)
    puntuacion = models.IntegerField()  # Rango de 1 a 5
    comentario = models.TextField()
    fecha_valoracion = models.DateTimeField(auto_now_add=True)

# Respuesta a las valoraciones realizadas por los usuarios
class RespuestaValoracion(models.Model):
    respuesta_valoracion_id = models.AutoField(primary_key=True)
    valoracion_id = models.ForeignKey(ValoracionProducto, on_delete=models.CASCADE)
    usuario_respuesta_id = models.ForeignKey(User, on_delete=models.CASCADE)
    respuesta = models.TextField()
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
