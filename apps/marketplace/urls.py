from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Main marketplace pages
    path('', views.marketplace_home, name='marketplace_home'),
    path('home/', views.marketplace_home, name='home'),  # Alias for compatibility
    path('productos/', views.lista_productos, name='lista_productos'),
    
    # Product details and categories
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    
    # Product ratings
    path('producto/<int:producto_id>/calificar/', views.valoracion_crear, name='calificar_producto'),
    
    # Shopping cart
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Orders
    path('mis-pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedido/<int:compra_id>/factura/', views.descargar_factura, name='descargar_factura'),
    
    # Ruta para depuración
    path('debug/checkout/', views.debug_checkout, name='debug_checkout'),
    path('debug/ventas/', views.debug_ventas, name='debug_ventas'),
    
    # Shipping addresses
    path('direcciones/', views.mis_direcciones, name='mis_direcciones'),
    path('direcciones/agregar/', views.agregar_direccion, name='agregar_direccion'),
    path('direcciones/editar/<int:direccion_id>/', views.editar_direccion, name='editar_direccion'),
    path('direcciones/eliminar/<int:direccion_id>/', views.eliminar_direccion, name='eliminar_direccion'),
    
    # Wishlist
    path('lista-deseos/', views.ver_lista_deseos, name='ver_lista_deseos'),
    path('lista-deseos/agregar/<int:producto_id>/', views.agregar_a_lista_deseos, name='agregar_a_lista_deseos'),
    path('lista-deseos/eliminar/<int:producto_id>/', views.eliminar_de_lista_deseos, name='eliminar_de_lista_deseos'),
    
    # Seller routes
    path('mi-tienda/', views.mi_tienda, name='mi_tienda'),
    path('producto/nuevo/', views.nuevo_producto, name='nuevo_producto'),
    path('producto/create/', views.product_create, name='product_create'),
    path('producto/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('producto/<int:producto_id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('seleccionar-producto-inventario/', views.seleccionar_producto_inventario, name='seleccionar_producto_inventario'),
    path('producto/inventario/agregar/', views.agregar_producto_inventario, name='agregar_producto_inventario'),
    
    # API endpoints
    path('api/producto/<int:producto_id>/info/', views.api_info_producto, name='api_info_producto'),
    path('api/carrito/cantidad/', views.api_cantidad_carrito, name='api_cantidad_carrito'),
    path('api/carrito/agregar/', views.api_carrito_agregar, name='api_carrito_agregar'),
    path('api/lista-deseos/toggle/', views.api_lista_deseos_toggle, name='api_lista_deseos_toggle'),
    path('api/valoracion/util/', views.api_valoracion_util, name='api_valoracion_util'),
    path('api/producto-inventario/<int:producto_id>/', views.api_producto_inventario, name='api_producto_inventario'),
] 