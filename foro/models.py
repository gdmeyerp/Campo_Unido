from django.db import models
from django.conf import settings

class CategoriaForo(models.Model):
    nombre_categoria = models.CharField(max_length=255)
    descripcion_categoria = models.TextField()

    def __str__(self):
        return self.nombre_categoria

class EstadoForo(models.Model):
    nombre_estado = models.CharField(max_length=50)
    descripcion_estado = models.TextField()

    def __str__(self):
        return self.nombre_estado

class Foro(models.Model):
    categoria = models.ForeignKey(CategoriaForo, on_delete=models.CASCADE)
    titulo_foro = models.CharField(max_length=255)
    descripcion_foro = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado_foro = models.ForeignKey(EstadoForo, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.titulo_foro

class EstadoPublicacion(models.Model):
    nombre_estado = models.CharField(max_length=50)  # Ejemplos: "Visible", "Oculto"
    descripcion_estado = models.TextField()

    def __str__(self):
        return self.nombre_estado

class PublicacionForo(models.Model):
    foro = models.ForeignKey(Foro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    titulo_publicacion = models.CharField(max_length=255)
    contenido_publicacion = models.TextField()
    fecha_hora_publicacion = models.DateTimeField(auto_now_add=True)
    estado_publicacion = models.ForeignKey(EstadoPublicacion, on_delete=models.SET_NULL, null=True)
    votos_positivos = models.IntegerField(default=0)
    votos_negativos = models.IntegerField(default=0)

    def __str__(self):
        return self.titulo_publicacion

class EstadoComentario(models.Model):
    nombre_estado = models.CharField(max_length=50)  # Ejemplos: "Visible", "Oculto"
    descripcion_estado = models.TextField()

    def __str__(self):
        return self.nombre_estado

class ComentarioPublicacion(models.Model):
    publicacion = models.ForeignKey(PublicacionForo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenido_comentario = models.TextField()
    fecha_hora_comentario = models.DateTimeField(auto_now_add=True)
    estado_comentario = models.ForeignKey(EstadoComentario, on_delete=models.SET_NULL, null=True)
    votos_positivos = models.IntegerField(default=0)
    votos_negativos = models.IntegerField(default=0)

class EstadoReporte(models.Model):
    nombre_estado = models.CharField(max_length=50)  # Ejemplos: "Pendiente", "Resuelto"
    descripcion_estado = models.TextField()

    def __str__(self):
        return self.nombre_estado

class ReportePublicacion(models.Model):
    publicacion = models.ForeignKey(PublicacionForo, on_delete=models.CASCADE)
    usuario_reportador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    motivo_reporte = models.TextField()
    fecha_hora_reporte = models.DateTimeField(auto_now_add=True)
    estado_reporte = models.ForeignKey(EstadoReporte, on_delete=models.SET_NULL, null=True)

class ReporteComentario(models.Model):
    comentario = models.ForeignKey(ComentarioPublicacion, on_delete=models.CASCADE)
    usuario_reportador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    motivo_reporte = models.TextField()
    fecha_hora_reporte = models.DateTimeField(auto_now_add=True)
    estado_reporte = models.ForeignKey(EstadoReporte, on_delete=models.SET_NULL, null=True)

class RolForo(models.Model):
    nombre_rol = models.CharField(max_length=50)  # Ejemplos: "Moderador", "Administrador"
    descripcion_rol = models.TextField()

    def __str__(self):
        return self.nombre_rol

class UsuarioRolForo(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rol_foro = models.ForeignKey(RolForo, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

class TipoReaccion(models.Model):
    nombre_reaccion = models.CharField(max_length=50)  # Ejemplos: "Me gusta", "Divertido"

    def __str__(self):
        return self.nombre_reaccion

class VotacionPublicacion(models.Model):
    publicacion = models.ForeignKey(PublicacionForo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo_voto = models.CharField(max_length=10)  # Valores: "Positivo", "Negativo"
    fecha_hora_voto = models.DateTimeField(auto_now_add=True)

class VotacionComentario(models.Model):
    comentario = models.ForeignKey(ComentarioPublicacion, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo_voto = models.CharField(max_length=10)  # Valores: "Positivo", "Negativo"
    fecha_hora_voto = models.DateTimeField(auto_now_add=True)

class ReaccionPublicacion(models.Model):
    publicacion = models.ForeignKey(PublicacionForo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo_reaccion = models.ForeignKey(TipoReaccion, on_delete=models.SET_NULL, null=True)
    fecha_hora_reaccion = models.DateTimeField(auto_now_add=True)

class ReaccionComentario(models.Model):
    comentario = models.ForeignKey(ComentarioPublicacion, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo_reaccion = models.ForeignKey(TipoReaccion, on_delete=models.SET_NULL, null=True)
    fecha_hora_reaccion = models.DateTimeField(auto_now_add=True)

class PuntuacionUsuarioForo(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puntaje = models.IntegerField(default=0)
    nivel = models.CharField(max_length=50)  # Ejemplos: "Principiante", "Intermedio", "Experto"

class HistorialPuntuacionForo(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    accion = models.CharField(max_length=100)  # Ejemplos: "Publicación creada", "Comentario votado"
    puntos_obtenidos = models.IntegerField()
    fecha_hora_accion = models.DateTimeField(auto_now_add=True)
    