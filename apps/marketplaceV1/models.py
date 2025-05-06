from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse

User = get_user_model()

class CategoriaProducto(models.Model):
    """Modelo para las categorías de productos"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    imagen = models.ImageField(upload_to='categorias/', blank=True, null=True)
    activa = models.BooleanField(default=True)
    categoria_padre = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategorias')
    
    class Meta:
        verbose_name = "Categoría de Producto"
        verbose_name_plural = "Categorías de Productos"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

class Producto(models.Model):
    """Modelo para los productos del marketplace"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.SET_NULL, blank=True, null=True, related_name='productos')
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productos_v1')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    estado = models.CharField(max_length=50, default='disponible')

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre
    
    def get_absolute_url(self):
        return reverse('marketplaceV1:detalle_producto', args=[self.id])
        
    def obtener_valoracion_promedio(self):
        valoraciones = ValoracionProducto.objects.filter(producto=self)
        if valoraciones.exists():
            return valoraciones.aggregate(models.Avg('calificacion'))['calificacion__avg']
        return 0

class ProductoImagen(models.Model):
    """Modelo para las imágenes adicionales de productos"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/imagenes/', blank=True, null=True)
    orden = models.PositiveSmallIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Imagen de Producto"
        verbose_name_plural = "Imágenes de Productos"
        ordering = ['orden', 'fecha_creacion']
    
    def __str__(self):
        return f"Imagen {self.orden} de {self.producto.nombre}"

class ValoracionProducto(models.Model):
    """Modelo para las valoraciones de productos"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='valoraciones_v1')
    calificacion = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1)])
    titulo = models.CharField(max_length=100)
    comentario = models.TextField()
    fecha_valoracion = models.DateTimeField(auto_now_add=True)
    utilidad = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Valoración de Producto"
        verbose_name_plural = "Valoraciones de Productos"
        unique_together = ['producto', 'usuario']
        ordering = ['-fecha_valoracion']
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.calificacion}/5 - {self.usuario.username}"

class RespuestaValoracion(models.Model):
    """Modelo para las respuestas a valoraciones"""
    valoracion = models.ForeignKey(ValoracionProducto, on_delete=models.CASCADE, related_name='respuestas')
    respuesta = models.TextField()
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Respuesta a Valoración"
        verbose_name_plural = "Respuestas a Valoraciones"
    
    def __str__(self):
        return f"Respuesta a {self.valoracion}"

class TarifaEnvio(models.Model):
    """Modelo para las tarifas de envío basadas en distancia"""
    distancia_min = models.DecimalField(max_digits=5, decimal_places=2, help_text="Distancia mínima en kilómetros")
    distancia_max = models.DecimalField(max_digits=5, decimal_places=2, help_text="Distancia máxima en kilómetros")
    costo = models.DecimalField(max_digits=10, decimal_places=2, help_text="Costo del envío")
    
    class Meta:
        verbose_name = "Tarifa de Envío"
        verbose_name_plural = "Tarifas de Envío"
        ordering = ['distancia_min']
    
    def __str__(self):
        return f"{self.distancia_min}km - {self.distancia_max}km: ${self.costo}"

class CarritoItem(models.Model):
    """Modelo para los items en el carrito de compras"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carrito_items_v1')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Item de Carrito"
        verbose_name_plural = "Items de Carrito"
        unique_together = ['usuario', 'producto']
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
    @property
    def subtotal(self):
        return self.cantidad * self.producto.precio

class ListaDeseos(models.Model):
    """Modelo para la lista de deseos de un usuario"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lista_deseos_v1')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Lista de Deseos"
        verbose_name_plural = "Listas de Deseos"
        unique_together = ['usuario', 'producto']
        db_table = 'marketplaceV1_lista_deseos'
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.usuario.email}"

class Compra(models.Model):
    """Modelo para las compras realizadas"""
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compras_v1')
    productos = models.ManyToManyField(Producto, through='DetalleCompra')
    fecha_compra = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    direccion_envio = models.TextField(blank=True, null=True)
    metodo_pago = models.CharField(max_length=100, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    referencia_pago = models.CharField(max_length=100, blank=True, null=True, help_text="Referencia para trazabilidad del pago")
    
    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ['-fecha_compra']
    
    def __str__(self):
        return f"Compra #{self.id} - {self.usuario.email}"

class DetalleCompra(models.Model):
    """Modelo para los detalles de una compra"""
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Detalle de Compra"
        verbose_name_plural = "Detalles de Compra"
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

# Nuevos modelos para el sistema de pagos

class MetodoPago(models.Model):
    """Modelo para los métodos de pago disponibles"""
    TIPO_CHOICES = (
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
        ('consignacion', 'Consignación'),
        ('contra_entrega', 'Pago Contra Entrega'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('nequi', 'Nequi'),
        ('daviplata', 'Daviplata'),
        ('otro', 'Otro'),
    )
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField(blank=True, null=True)
    instrucciones = models.TextField(blank=True, null=True, help_text="Instrucciones para realizar el pago")
    datos_adicionales = models.JSONField(blank=True, null=True, help_text="Datos adicionales como número de cuenta")
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Pago(models.Model):
    """Modelo para registrar los pagos realizados"""
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente de verificación'),
        ('verificado', 'Verificado'),
        ('rechazado', 'Rechazado'),
        ('reembolsado', 'Reembolsado'),
    )
    
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='pagos')
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    comprobante = models.FileField(upload_to='comprobantes_pago/', blank=True, null=True)
    referencia = models.CharField(max_length=100, blank=True, null=True, help_text="Número de referencia del pago")
    comentarios = models.TextField(blank=True, null=True)
    datos_transaccion = models.JSONField(blank=True, null=True, help_text="Datos adicionales de la transacción")
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha_pago']
    
    def __str__(self):
        return f"Pago {self.id} - Compra #{self.compra.id} - {self.estado}"

class Orden(models.Model):
    """Modelo para las órdenes de compra"""
    ESTADO_CHOICES = (
        ('creada', 'Creada'),
        ('pendiente_pago', 'Pendiente de pago'),
        ('pagada', 'Pagada'),
        ('preparando', 'Preparando'),
        ('enviada', 'Enviada'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
    )
    
    compra = models.OneToOneField(Compra, on_delete=models.CASCADE, related_name='orden')
    numero_orden = models.CharField(max_length=20, unique=True, help_text="Número único de la orden")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='creada')
    notas = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Orden #{self.numero_orden} - {self.estado}"
    
    def save(self, *args, **kwargs):
        # Generar número de orden si es nuevo
        if not self.numero_orden:
            # Formato: ORD-YYYYMMDD-XXXXXX donde XXXXXX es un número incremental
            import datetime
            from django.utils.crypto import get_random_string
            
            fecha = datetime.datetime.now().strftime('%Y%m%d')
            aleatorio = get_random_string(6, '0123456789')
            self.numero_orden = f"ORD-{fecha}-{aleatorio}"
            
        super().save(*args, **kwargs)

class DireccionEnvio(models.Model):
    """Modelo para las direcciones de envío"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direcciones_envio')
    nombre_completo = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    notas_adicionales = models.TextField(blank=True, null=True)
    predeterminada = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Dirección de Envío"
        verbose_name_plural = "Direcciones de Envío"
    
    def __str__(self):
        return f"{self.nombre_completo} - {self.direccion}, {self.ciudad}" 