from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_inventario, name='dashboard'),
    
    # Herramienta de diagnóstico
    path('diagnostico/', views.diagnostico_inventario, name='diagnostico_inventario'),
    
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
    path('proveedores/asignar-propietario/', views.asignar_propietario_proveedores, name='asignar_propietario_proveedores'),
    
    # Pedidos a Proveedores
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('pedidos/crear/', views.crear_pedido, name='crear_pedido'),
    path('pedidos/<int:pk>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedidos/<int:pk>/editar/', views.editar_pedido, name='editar_pedido'),
    path('pedidos/detalle/<int:pk>/eliminar/', views.eliminar_detalle_pedido, name='eliminar_detalle_pedido'),
    path('pedidos/<int:pedido_id>/editar-producto/', views.editar_producto_pedido, name='editar_producto_pedido'),
    path('pedidos/<int:pedido_id>/agregar-producto/', views.agregar_producto_pedido, name='agregar_producto_pedido'),
    path('pedidos/<int:pk>/recibir/', views.recibir_pedido, name='recibir_pedido'),
    path('pedidos/<int:pk>/cancelar/', views.cancelar_pedido, name='cancelar_pedido'),
    path('pedidos/asignar-propietario/', views.asignar_propietario_pedidos, name='asignar_propietario_pedidos'),
    
    # Almacenes
    path('almacenes/', views.lista_almacenes, name='lista_almacenes'),
    path('almacenes/crear/', views.crear_almacen, name='crear_almacen'),
    path('almacenes/<int:pk>/', views.detalle_almacen, name='detalle_almacen'),
    path('almacenes/asignar-propietario/', views.asignar_propietario_almacenes, name='asignar_propietario_almacenes'),
    
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
    
    # Imágenes de Productos
    path('productos/<int:producto_id>/imagenes/', views.gestionar_imagenes, name='gestionar_imagenes'),
    path('productos/<int:producto_id>/imagenes/subir/', views.subir_imagen, name='subir_imagen'),
    path('productos/<int:producto_id>/imagenes/subir-multiples/', views.subir_imagenes_multiples, name='subir_imagenes_multiples'),
    path('productos/imagenes/<int:imagen_id>/eliminar/', views.eliminar_imagen, name='eliminar_imagen'),
    path('productos/imagenes/<int:imagen_id>/principal/', views.marcar_como_principal, name='marcar_como_principal'),

    # URLs para Notificaciones
    path('notificaciones/', views.lista_notificaciones, name='lista_notificaciones'),
    path('notificaciones/<int:pk>/', views.detalle_notificacion, name='detalle_notificacion'),
    path('notificaciones/<int:pk>/marcar-leida/', views.marcar_como_leida, name='marcar_notificacion_leida'),
    path('notificaciones/marcar-todas-leidas/', views.marcar_todas_como_leidas, name='marcar_todas_leidas'),
    path('notificaciones/<int:pk>/eliminar/', views.eliminar_notificacion, name='eliminar_notificacion'),
    path('notificaciones/eliminar-todas/', views.eliminar_todas, name='eliminar_todas_notificaciones'),
    path('api/notificaciones/contador/', views.obtener_contador_notificaciones, name='api_contador_notificaciones'),
    path('api/notificaciones/recientes/', views.obtener_notificaciones_recientes, name='api_notificaciones_recientes'),
    path('notificaciones/<int:notificacion_id>/marcar-leida/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('notificaciones/generar-prueba/', views.generar_notificacion_prueba, name='generar_notificacion_prueba'),
] 