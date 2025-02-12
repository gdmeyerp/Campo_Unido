from django.contrib import admin
from .models import (
    CategoriaForo, Foro, EstadoForo, PublicacionForo, EstadoPublicacion,
    ComentarioPublicacion, EstadoComentario, ReaccionPublicacion,
    ReaccionComentario, TipoReaccion, RolForo, UsuarioRolForo
)

admin.site.register(CategoriaForo)
admin.site.register(Foro)
admin.site.register(EstadoForo)
admin.site.register(PublicacionForo)
admin.site.register(EstadoPublicacion)
admin.site.register(ComentarioPublicacion)
admin.site.register(EstadoComentario)
admin.site.register(ReaccionPublicacion)
admin.site.register(ReaccionComentario)
admin.site.register(TipoReaccion)
admin.site.register(RolForo)
admin.site.register(UsuarioRolForo)
