from django.contrib import admin
from .models import Pais, Estado, Ciudad, Ubicacion, HistorialUbicacion

admin.site.register(Pais)
admin.site.register(Estado)
admin.site.register(Ciudad)
admin.site.register(Ubicacion)
admin.site.register(HistorialUbicacion)
