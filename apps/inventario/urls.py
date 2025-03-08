from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_inventario, name='dashboard'),
    
    # Categorías de Productos
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:pk>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # Estados de Productos
    path('estados/', views.lista_estados, name='lista_estados'),
    path('estados/crear/', views.crear_estado, name='crear_estado'),
    path('estados/<int:pk>/editar/', views.editar_estado, name='editar_estado'),
    path('estados/<int:pk>/eliminar/', views.eliminar_estado, name='eliminar_estado'),
    
    # Productos
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('productos/<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    
    # Movimientos de Inventario
    path('movimientos/', views.lista_movimientos, name='lista_movimientos'),
    path('movimientos/registrar/', views.registrar_movimiento, name='registrar_movimiento'),
    
    # Proveedores
    path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedores/<int:pk>/', views.detalle_proveedor, name='detalle_proveedor'),
    path('proveedores/<int:pk>/editar/', views.editar_proveedor, name='editar_proveedor'),
    
    # Pedidos a Proveedores
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('pedidos/crear/', views.crear_pedido, name='crear_pedido'),
    path('pedidos/<int:pk>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedidos/<int:pk>/editar/', views.editar_pedido, name='editar_pedido'),
    path('pedidos/detalle/<int:pk>/eliminar/', views.eliminar_detalle_pedido, name='eliminar_detalle_pedido'),
    path('pedidos/<int:pedido_id>/editar-producto/', views.editar_producto_pedido, name='editar_producto_pedido'),
    
    # Almacenes
    path('almacenes/', views.lista_almacenes, name='lista_almacenes'),
    path('almacenes/crear/', views.crear_almacen, name='crear_almacen'),
    path('almacenes/<int:pk>/', views.detalle_almacen, name='detalle_almacen'),
    
    # Ubicaciones de Almacén
    path('almacenes/<int:almacen_id>/ubicaciones/crear/', views.crear_ubicacion, name='crear_ubicacion'),
    
    # Inventario en Almacenes
    path('ubicaciones/<int:ubicacion_id>/asignar-producto/', views.asignar_producto_ubicacion, name='asignar_producto_ubicacion'),
    
    # Caducidad de Productos
    path('productos/<int:producto_id>/caducidad/registrar/', views.registrar_caducidad, name='registrar_caducidad'),
    
    # Alertas de Stock
    path('productos/<int:producto_id>/alerta-stock/crear/', views.crear_alerta_stock, name='crear_alerta_stock'),
    path('verificar-stock-bajo/', views.verificar_stock_bajo, name='verificar_stock_bajo'),
    
    # Exportación de informes
    path('exportar-informe/<str:formato>/', views.exportar_informe_inventario, name='exportar_informe'),
    
    # API
    path('api/producto-info/', views.api_producto_info, name='api_producto_info'),
    path('api/crear-categoria/', views.api_crear_categoria, name='api_crear_categoria'),
    path('api/crear-estado/', views.api_crear_estado, name='api_crear_estado'),
] 