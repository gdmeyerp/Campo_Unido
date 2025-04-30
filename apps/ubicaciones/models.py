from django.db import models
from django.conf import settings
import math


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
    productor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='areas_servicio')
    ubicacion_centro = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='areas_servicio')
    radio_km = models.DecimalField(max_digits=5, decimal_places=2, help_text='Radio de cobertura en kilómetros')
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Área de Servicio'
        verbose_name_plural = 'Áreas de Servicio'
    
    def __str__(self):
        return f"Área de {self.productor.username} - {self.ubicacion_centro.nombre} ({self.radio_km} km)"
        
    @staticmethod
    def calcular_distancia(lat1, lon1, lat2, lon2):
        """
        Calcula la distancia en kilómetros entre dos puntos geográficos
        utilizando la fórmula de Haversine.
        """
        # Radio de la Tierra en kilómetros
        R = 6371.0
        
        # Convertir grados a radianes
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Diferencias en radianes
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Fórmula de Haversine
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distancia = R * c
        
        return distancia


class PreferenciaUbicacion(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferencia_ubicacion')
    ubicacion_preferida = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, related_name='preferencias_usuarios', 
                                          blank=True, null=True)
    radio_busqueda_km = models.DecimalField(max_digits=5, decimal_places=2, default=10.0,
                                         help_text='Radio de búsqueda preferido en kilómetros')

    class Meta:
        verbose_name = 'Preferencia de Ubicación'
        verbose_name_plural = 'Preferencias de Ubicación'

    def __str__(self):
        return f"Preferencias de {self.usuario.username}"


class UbicacionProducto(models.Model):
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='productos')
    producto = models.ForeignKey('marketplace.Producto', on_delete=models.CASCADE, related_name='ubicaciones')
    stock_disponible = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Ubicación de Producto'
        verbose_name_plural = 'Ubicaciones de Productos'
        unique_together = ('producto', 'ubicacion')
        
    def __str__(self):
        return f"{self.producto.nombre} en {self.ubicacion.nombre}"
    
    @classmethod
    def encontrar_productos_cercanos(cls, ubicacion, radio_km=10.0, categoria=None):
        """
        Encuentra productos cercanos a una ubicación dentro de un radio específico.
        
        Args:
            ubicacion: Objeto Ubicacion desde donde buscar
            radio_km: Radio de búsqueda en kilómetros
            categoria: Objeto CategoriaProducto opcional para filtrar por categoría
            
        Returns:
            Lista de productos cercanos con información de distancia
        """
        from apps.marketplace.models import Producto
        
        productos_cercanos = []
        
        # Verificar que la ubicación tenga coordenadas
        if not ubicacion or not ubicacion.latitud or not ubicacion.longitud:
            return []
            
        lat1 = float(ubicacion.latitud)
        lon1 = float(ubicacion.longitud)
        
        # Obtener todas las ubicaciones de productos (excepto las del usuario de la ubicación proporcionada)
        ubicaciones_productos = cls.objects.filter(
            activo=True,
            stock_disponible__gt=0,
            producto__activo=True
        ).exclude(
            ubicacion__usuario=ubicacion.usuario
        ).select_related(
            'ubicacion',
            'producto',
            'producto__categoria',
            'ubicacion__ciudad',
            'ubicacion__ciudad__estado',
            'ubicacion__ciudad__estado__pais'
        )
        
        # Filtrar por categoría si se especifica
        if categoria:
            ubicaciones_productos = ubicaciones_productos.filter(producto__categoria=categoria)
            
        # Para cada ubicación de producto, calcular la distancia
        for up in ubicaciones_productos:
            if not up.ubicacion.latitud or not up.ubicacion.longitud:
                continue
                
            lat2 = float(up.ubicacion.latitud)
            lon2 = float(up.ubicacion.longitud)
            
            distancia = AreaServicio.calcular_distancia(lat1, lon1, lat2, lon2)
            
            # Si está dentro del radio de búsqueda, añadir a los resultados
            if distancia <= float(radio_km):
                productos_cercanos.append({
                    'producto': up.producto,
                    'ubicacion': up.ubicacion,
                    'stock': up.stock_disponible,
                    'distancia': distancia
                })
        
        # Ordenar por distancia
        productos_cercanos.sort(key=lambda x: x['distancia'])
        
        return productos_cercanos


class UsuariosPorCategoria(models.Model):
    """Modelo para guardar estadísticas de cuántos usuarios hay por cada categoría de producto"""
    categoria = models.ForeignKey('marketplace.CategoriaProducto', on_delete=models.CASCADE)
    total_usuarios = models.PositiveIntegerField(default=0)
    usuarios_activos = models.PositiveIntegerField(default=0)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Estadística por Categoría'
        verbose_name_plural = 'Estadísticas por Categorías'
        
    def __str__(self):
        return f"Estadísticas de {self.categoria.nombre}" 