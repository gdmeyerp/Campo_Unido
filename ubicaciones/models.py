from django.db import models
from core.models import User  # Asumiendo que User está en la app core

class Pais(models.Model):
    nombre_pais = models.CharField(max_length=100)
    codigo_iso = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.nombre_pais

class Estado(models.Model):
    nombre_estado = models.CharField(max_length=100)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nombre_estado}, {self.pais.nombre_pais}'

class Ciudad(models.Model):
    nombre_ciudad = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    tipo_zona = models.CharField(max_length=50, choices=[('Urbana', 'Urbana'), ('Rural', 'Rural'), ('Suburbana', 'Suburbana')], default='Urbana')

    def __str__(self):
        return f'{self.nombre_ciudad}, {self.estado.nombre_estado}'

class Ubicacion(models.Model):
    direccion = models.CharField(max_length=255)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE)
    codigo_postal = models.CharField(max_length=20)
    latitud = models.FloatField()
    longitud = models.FloatField()
    altitud = models.FloatField(null=True, blank=True)
    zona_horaria = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.direccion}, {self.ciudad.nombre_ciudad}'

class HistorialUbicacion(models.Model):
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_cambio = models.CharField(max_length=50, choices=[('Creación', 'Creación'), ('Actualización', 'Actualización'), ('Eliminación', 'Eliminación')])
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    detalles_cambio = models.TextField()

    def __str__(self):
        return f'Historial de {self.ubicacion.direccion} por {self.usuario.email}'
