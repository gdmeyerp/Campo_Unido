from django.contrib import admin
from .models import (
    CategoriaProducto, Producto, ProductoImagen, ValoracionProducto, 
    RespuestaValoracion, TarifaEnvio, CarritoItem, ListaDeseos, 
    Compra, DetalleCompra, MetodoPago, Pago, Orden, DireccionEnvio
)

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'activa', 'categoria_padre')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('activa',)
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'vendedor', 'activo', 'destacado')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('activo', 'destacado', 'categoria', 'vendedor')
    date_hierarchy = 'fecha_creacion'

@admin.register(ProductoImagen)
class ProductoImagenAdmin(admin.ModelAdmin):
    list_display = ('producto', 'orden')
    search_fields = ('producto__nombre',)

@admin.register(ValoracionProducto)
class ValoracionProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'usuario', 'calificacion', 'fecha_valoracion')
    search_fields = ('producto__nombre', 'comentario')
    list_filter = ('calificacion',)

@admin.register(RespuestaValoracion)
class RespuestaValoracionAdmin(admin.ModelAdmin):
    list_display = ('valoracion', 'fecha_respuesta')
    search_fields = ('respuesta',)

@admin.register(TarifaEnvio)
class TarifaEnvioAdmin(admin.ModelAdmin):
    list_display = ('distancia_min', 'distancia_max', 'costo')

@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'cantidad', 'fecha_agregado')
    search_fields = ('usuario__email', 'producto__nombre')

@admin.register(ListaDeseos)
class ListaDeseosAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'fecha_agregado')
    search_fields = ('usuario__email', 'producto__nombre')

# Registrar módulos existentes de compra
@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_compra', 'estado', 'total')
    search_fields = ('usuario__email',)
    list_filter = ('estado',)
    date_hierarchy = 'fecha_compra'

class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 0

@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = ('compra', 'producto', 'cantidad', 'precio_unitario')
    search_fields = ('compra__id', 'producto__nombre')

# Registrar nuevos modelos de pago y órdenes
@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'activo')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('tipo', 'activo')

class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'compra', 'metodo_pago', 'monto', 'fecha_pago', 'estado')
    search_fields = ('compra__id', 'referencia')
    list_filter = ('estado', 'metodo_pago')
    date_hierarchy = 'fecha_pago'

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('numero_orden', 'compra', 'fecha_creacion', 'estado')
    search_fields = ('numero_orden', 'compra__usuario__email')
    list_filter = ('estado',)
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('numero_orden',)
    inlines = [PagoInline]

@admin.register(DireccionEnvio)
class DireccionEnvioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nombre_completo', 'ciudad', 'departamento', 'predeterminada')
    search_fields = ('usuario__email', 'nombre_completo', 'direccion', 'ciudad')
    list_filter = ('departamento', 'predeterminada') 