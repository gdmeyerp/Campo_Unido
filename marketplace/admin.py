from django.contrib import admin
from .models import (
    CategoriaProducto, EstadoProducto, UnidadMedida, MarketplaceProducto, 
    HistorialPrecioProducto, PromocionProducto, Compra, DetalleCompra, 
    EstadoCompra, MetodoPago, ValoracionProducto, RespuestaValoracion
)

admin.site.register(CategoriaProducto)
admin.site.register(EstadoProducto)
admin.site.register(UnidadMedida)
admin.site.register(MarketplaceProducto)
admin.site.register(HistorialPrecioProducto)
admin.site.register(PromocionProducto)
admin.site.register(Compra)
admin.site.register(DetalleCompra)
admin.site.register(EstadoCompra)
admin.site.register(MetodoPago)
admin.site.register(ValoracionProducto)
admin.site.register(RespuestaValoracion)
