from django.db import models
from django.conf import settings


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