from django.contrib import admin
from .models import Pais, Estado, Ciudad, Ubicacion


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'pais')
    list_filter = ('pais',)
    search_fields = ('nombre', 'codigo')


@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado')
    list_filter = ('estado__pais', 'estado')
    search_fields = ('nombre',)


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'ciudad', 'usuario', 'es_principal')
    list_filter = ('ciudad__estado__pais', 'ciudad__estado', 'es_principal')
    search_fields = ('nombre', 'direccion', 'codigo_postal', 'usuario__username')
    raw_id_fields = ('usuario',) 