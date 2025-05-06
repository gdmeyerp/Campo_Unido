from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import F, ExpressionWrapper, FloatField
from django.db.models.functions import ACos, Cos, Sin, Radians
import math
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from apps.marketplace.models import Producto, CategoriaProducto
from math import radians, sin, cos, sqrt, atan2

User = get_user_model()


class Pais(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=3, unique=True)
    
    class Meta:
        verbose_name = 'País'
        verbose_name_plural = 'Países'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Estado(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, blank=True)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name='estados')
    
    class Meta:
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'
        ordering = ['nombre']
        unique_together = ['nombre', 'pais']
    
    def __str__(self):
        return f"{self.nombre}, {self.pais}"


class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name='ciudades')
    
    class Meta:
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        ordering = ['nombre']
        unique_together = ['nombre', 'estado']
    
    def __str__(self):
        return f"{self.nombre}, {self.estado.nombre}"


class Ubicacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ubicaciones')
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=255)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, related_name='ubicaciones')
    latitud = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    es_principal = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
        ordering = ['-es_principal', 'nombre']
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        # Si esta ubicación se marca como principal, desmarcamos las demás del mismo usuario
        if self.es_principal:
            Ubicacion.objects.filter(usuario=self.usuario, es_principal=True).update(es_principal=False)
        
        # Si es la primera ubicación del usuario, la marcamos como principal
        if not self.pk and not Ubicacion.objects.filter(usuario=self.usuario).exists():
            self.es_principal = True
            
        super().save(*args, **kwargs)


class AreaServicio(models.Model):
    """Área de servicio de un productor"""
    productor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='areas_servicio')
    ubicacion_centro = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='areas_servicio')
    radio_km = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Radio de cobertura en kilómetros"
    )
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Área de Servicio'
        verbose_name_plural = 'Áreas de Servicio'
    
    def __str__(self):
        return f"Área de {self.productor.username} - {self.ubicacion_centro.nombre}"
    
    @staticmethod
    def calcular_distancia(lat1, lon1, lat2, lon2):
        """
        Calcula la distancia en kilómetros entre dos puntos usando la fórmula de Haversine
        """
        R = 6371  # Radio de la Tierra en km
        
        lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def esta_en_rango(self, ubicacion):
        """
        Verifica si una ubicación está dentro del radio de servicio
        """
        if not (self.ubicacion_centro.latitud and self.ubicacion_centro.longitud and 
                ubicacion.latitud and ubicacion.longitud):
            return False
            
        distancia = self.calcular_distancia(
            self.ubicacion_centro.latitud,
            self.ubicacion_centro.longitud,
            ubicacion.latitud,
            ubicacion.longitud
        )
        
        return distancia <= float(self.radio_km)


class PreferenciaUbicacion(models.Model):
    """Preferencias de ubicación de un usuario"""
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferencia_ubicacion')
    radio_busqueda_km = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.0,
        help_text="Radio de búsqueda preferido en kilómetros"
    )
    ubicacion_preferida = models.ForeignKey(
        Ubicacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preferencias_usuarios'
    )
    
    class Meta:
        verbose_name = 'Preferencia de Ubicación'
        verbose_name_plural = 'Preferencias de Ubicación'
    
    def __str__(self):
        return f"Preferencias de {self.usuario.username}"


class UbicacionProducto(models.Model):
    """Ubicación específica de un producto"""
    producto = models.ForeignKey('marketplace.Producto', on_delete=models.CASCADE, related_name='ubicaciones')
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='productos')
    stock_disponible = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Ubicación de Producto'
        verbose_name_plural = 'Ubicaciones de Productos'
        unique_together = ['producto', 'ubicacion']
    
    def __str__(self):
        return f"{self.producto.nombre} en {self.ubicacion.nombre}"

    @staticmethod
    def encontrar_productos_cercanos(ubicacion_usuario, radio_km=10, categoria=None, limite=10):
        """
        Encuentra productos cercanos a una ubicación dada
        """
        if not (ubicacion_usuario.latitud and ubicacion_usuario.longitud):
            return []
            
        # Convertir coordenadas a radianes
        lat = float(ubicacion_usuario.latitud)
        lon = float(ubicacion_usuario.longitud)
        
        # Filtrar productos activos y con stock
        productos = UbicacionProducto.objects.filter(
            activo=True,
            stock_disponible__gt=0,
            ubicacion__latitud__isnull=False,
            ubicacion__longitud__isnull=False
        )
        
        if categoria:
            productos = productos.filter(producto__categoria=categoria)
        
        # Calcular distancia usando la fórmula de Haversine
        productos = productos.annotate(
            distancia=ExpressionWrapper(
                6371 * ACos(
                    Cos(Radians(lat)) * 
                    Cos(Radians(F('ubicacion__latitud'))) * 
                    Cos(Radians(F('ubicacion__longitud')) - Radians(lon)) + 
                    Sin(Radians(lat)) * 
                    Sin(Radians(F('ubicacion__latitud')))
                ),
                output_field=FloatField()
            )
        ).filter(distancia__lte=radio_km)
        
        # Ordenar por distancia y limitar resultados
        return productos.order_by('distancia')[:limite]


class UsuariosPorCategoria(models.Model):
    """Modelo para mantener un registro de usuarios por categoría de producto"""
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('categoria', 'usuario')
        indexes = [
            models.Index(fields=['categoria', 'usuario']),
        ]

    @classmethod
    def actualizar_usuario_categoria(cls, usuario, producto):
        """Actualiza el registro de usuarios por categoría cuando se publica o actualiza un producto"""
        cls.objects.get_or_create(
            categoria=producto.categoria,
            usuario=usuario
        )

    @classmethod
    def eliminar_usuario_categoria(cls, usuario, categoria):
        """Elimina el registro si el usuario ya no tiene productos en esta categoría"""
        # Verificar si el usuario aún tiene productos activos en esta categoría
        productos_activos = UbicacionProducto.objects.filter(
            ubicacion__usuario=usuario,
            producto__categoria=categoria,
            producto__activo=True,
            stock_disponible__gt=0
        ).exists()
        
        if not productos_activos:
            cls.objects.filter(usuario=usuario, categoria=categoria).delete() 