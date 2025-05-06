from django.urls import path
from . import views
from . import payment_views

app_name = 'marketplaceV1'

urlpatterns = [
    # Rutas principales
    path('', views.inicio_marketplace, name='inicio'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categoria/<slug:slug>/', views.productos_por_categoria, name='productos_por_categoria'),
    
    # Rutas de productos
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('producto/nuevo/', views.crear_producto, name='crear_producto'),
    path('producto/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('producto/<int:producto_id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('mis-productos/', views.mis_productos, name='mis_productos'),
    
    # Rutas del carrito
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    
    # Rutas de compras
    path('checkout/', payment_views.checkout, name='checkout'),
    path('compra/<int:compra_id>/', views.detalle_compra, name='detalle_compra'),
    path('mis-compras/', views.mis_compras, name='mis_compras'),
    
    # Lista de deseos
    path('deseos/', views.lista_deseos, name='lista_deseos'),
    path('deseos/agregar/<int:producto_id>/', views.agregar_a_deseos, name='agregar_a_deseos'),
    path('deseos/eliminar/<int:lista_id>/', views.eliminar_de_deseos, name='eliminar_de_deseos'),
    
    # Valoraciones
    path('valoracion/<int:producto_id>/agregar/', views.agregar_valoracion, name='agregar_valoracion'),
    path('valoracion/<int:valoracion_id>/editar/', views.editar_valoracion, name='editar_valoracion'),
    path('valoracion/<int:valoracion_id>/eliminar/', views.eliminar_valoracion, name='eliminar_valoracion'),
    
    # Nuevas rutas para pagos y órdenes
    path('direcciones/', payment_views.mis_direcciones, name='mis_direcciones'),
    path('direcciones/agregar/', payment_views.agregar_direccion, name='agregar_direccion'),
    path('direcciones/editar/<int:direccion_id>/', payment_views.editar_direccion, name='editar_direccion'),
    path('direcciones/eliminar/<int:direccion_id>/', payment_views.eliminar_direccion, name='eliminar_direccion'),
    
    path('ordenes/', payment_views.mis_ordenes, name='mis_ordenes'),
    path('orden/<int:orden_id>/', payment_views.detalle_orden, name='detalle_orden'),
    path('orden/<int:orden_id>/cancelar/', payment_views.cancelar_orden, name='cancelar_orden'),
    
    path('pago/<int:pago_id>/comprobante/', payment_views.subir_comprobante, name='subir_comprobante'),
] 