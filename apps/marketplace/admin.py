from django.contrib import admin
from .models import Producto, CategoriaProducto, CarritoItem, ListaDeseos, Compra, DetalleCompra

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
