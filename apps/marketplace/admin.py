from django.contrib import admin
from .models import (
    Producto, CategoriaProducto, CarritoItem, ListaDeseos, 
    Compra, DetalleCompra, NotificacionMarketplace, Orden, 
    ProductoImagen, DireccionEnvio, ValoracionProducto, RespuestaValoracion
)

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'vendedor', 'activo')
    list_filter = ('activo', 'categoria')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'cantidad', 'fecha_agregado')
    list_filter = ('fecha_agregado',)
    search_fields = ('usuario__email', 'producto__nombre')

@admin.register(ListaDeseos)
class ListaDeseosAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'fecha_agregado')
    list_filter = ('fecha_agregado',)
    search_fields = ('usuario__email', 'producto__nombre')

class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario')

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_compra', 'estado', 'total')
    list_filter = ('estado', 'fecha_compra')
    search_fields = ('usuario__email', 'id')
    readonly_fields = ('fecha_compra', 'total')
    inlines = [DetalleCompraInline]

@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = ('compra', 'producto', 'cantidad', 'precio_unitario')
    list_filter = ('compra__fecha_compra',)
    search_fields = ('compra__id', 'producto__nombre')

@admin.register(NotificacionMarketplace)
class NotificacionMarketplaceAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'tipo', 'nivel', 'producto', 'fecha_creacion', 'leida')
    list_filter = ('tipo', 'nivel', 'leida', 'fecha_creacion')
    search_fields = ('titulo', 'mensaje', 'usuario__email', 'producto__nombre')
    readonly_fields = ('fecha_creacion',)
    actions = ['marcar_como_leidas']
    
    def marcar_como_leidas(self, request, queryset):
        queryset.update(leida=True)
        self.message_user(request, f"{queryset.count()} notificaciones marcadas como leídas.")
    marcar_como_leidas.short_description = "Marcar notificaciones seleccionadas como leídas"

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('numero_orden', 'compra', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('numero_orden', 'compra__usuario__email')
    readonly_fields = ('numero_orden', 'fecha_creacion', 'fecha_actualizacion')
