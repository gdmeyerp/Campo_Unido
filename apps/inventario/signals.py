from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import (
    ProductoInventario, MovimientoInventario, 
    AlertaStock, ReservaInventario, CaducidadProducto,
    EstadoProducto, CategoriaProducto, PedidoProveedor,
    Notificacion
)
from apps.marketplace.models import Compra

# Las señales se configurarán cuando tengamos los modelos definidos
# Aquí se manejarán eventos como:
# - Actualización automática de stock cuando se realiza una venta
# - Generación de alertas cuando el stock baje del mínimo
# - Registro de movimientos de inventario 

User = get_user_model()

@receiver(post_save, sender=MovimientoInventario)
def actualizar_stock_producto(sender, instance, created, **kwargs):
    """
    Actualiza el stock del producto cuando se registra un movimiento de inventario.
    """
    if created:
        with transaction.atomic():
            producto = instance.producto_inventario
            
            if instance.tipo_movimiento == 'ENTRADA':
                # Para entradas, simplemente aumentamos el stock
                ProductoInventario.objects.filter(
                    id=producto.id
                ).update(
                    cantidad_disponible=F('cantidad_disponible') + instance.cantidad_movimiento
                )
            elif instance.tipo_movimiento == 'SALIDA':
                # Para salidas, aseguramos que no quede stock negativo
                ProductoInventario.objects.filter(
                    id=producto.id, 
                    cantidad_disponible__gte=instance.cantidad_movimiento
                ).update(
                    cantidad_disponible=F('cantidad_disponible') - instance.cantidad_movimiento
                )
            elif instance.tipo_movimiento == 'AJUSTE':
                # Para ajustes, asignamos el valor directamente
                ProductoInventario.objects.filter(
                    id=producto.id
                ).update(
                    cantidad_disponible=instance.cantidad_movimiento
                )
                
            # Recargamos el producto para tener los valores actualizados
            producto.refresh_from_db()

@receiver(post_save, sender=ProductoInventario)
def verificar_stock_minimo(sender, instance, **kwargs):
    """
    Verifica si el stock del producto está por debajo del mínimo y genera una alerta.
    """
    if instance.cantidad_disponible <= instance.stock_minimo:
        ultima_alerta = AlertaStock.objects.filter(
            producto_inventario=instance,
            fecha_alerta__gte=timezone.now() - timezone.timedelta(hours=24)
        ).first()
        
        if not ultima_alerta:
            AlertaStock.objects.create(
                producto_inventario=instance,
                cantidad_disponible=instance.cantidad_disponible
            )

@receiver(post_save, sender=Compra)
def registrar_salida_inventario(sender, instance, created, **kwargs):
    """
    Registra una salida de inventario cuando se realiza una compra.
    """
    if created:
        try:
            producto_inventario = ProductoInventario.objects.get(id=instance.producto.id)
            
            MovimientoInventario.objects.create(
                producto_inventario=producto_inventario,
                tipo_movimiento='SALIDA',
                cantidad_movimiento=instance.cantidad,
                usuario=instance.comprador,
                descripcion_movimiento=f'Venta: Compra #{instance.id}',
                referencia_documento=str(instance.id),
                tipo_documento='COMPRA'
            )
        except ProductoInventario.DoesNotExist:
            pass

@receiver(post_delete, sender=ReservaInventario)
def liberar_reserva_inventario(sender, instance, **kwargs):
    """
    Libera la reserva de inventario cuando se elimina una reserva.
    """
    pass

@receiver(post_save, sender=CaducidadProducto)
def verificar_caducidad_productos(sender, instance, created, **kwargs):
    """
    Verifica si hay productos próximos a caducar y genera alertas.
    """
    if created:
        dias_para_caducidad = (instance.fecha_caducidad - timezone.now().date()).days
        
        if dias_para_caducidad <= 30:
            MovimientoInventario.objects.create(
                producto_inventario=instance.producto_inventario,
                tipo_movimiento='ALERTA',
                cantidad_movimiento=instance.cantidad_disponible,
                usuario=instance.producto_inventario.usuario if hasattr(instance.producto_inventario, 'usuario') else None,
                descripcion_movimiento=f'Alerta: Producto próximo a caducar en {dias_para_caducidad} días',
                tipo_documento='CADUCIDAD'
            )

@receiver(post_save, sender=User)
def configurar_inventario_nuevo_usuario(sender, instance, created, **kwargs):
    """
    Configura el inventario inicial para un nuevo usuario.
    Crea categorías y estados básicos para que el usuario pueda empezar a trabajar.
    """
    if created:
        try:
            with transaction.atomic():
                # Crear categorías básicas para el nuevo usuario
                categorias_base = [
                    {"nombre": "General", "descripcion": "Categoría general para productos diversos"},
                    {"nombre": "Materias Primas", "descripcion": "Materiales utilizados en la producción"},
                    {"nombre": "Productos Terminados", "descripcion": "Productos listos para venta"}
                ]
                
                for cat in categorias_base:
                    CategoriaProducto.objects.get_or_create(
                        nombre_categoria=cat["nombre"],
                        propietario=instance,
                        defaults={"descripcion": cat["descripcion"]}
                    )
                
                # Asegurarse de que existan estados básicos
                estados_base = ["Activo", "Inactivo", "Agotado", "Descontinuado"]
                for estado in estados_base:
                    EstadoProducto.objects.get_or_create(nombre_estado=estado)
        except Exception as e:
            print(f"Error configurando inventario para nuevo usuario: {str(e)}")

@receiver(post_save, sender=AlertaStock)
def crear_notificacion_stock_bajo(sender, instance, created, **kwargs):
    """
    Crea una notificación cuando se genera una alerta de stock bajo.
    """
    if created and hasattr(instance.producto_inventario, 'usuario'):
        usuario = instance.producto_inventario.usuario
        producto = instance.producto_inventario
        
        Notificacion.objects.create(
            usuario=usuario,
            tipo='STOCK_BAJO',
            nivel='WARNING',
            titulo=f'Stock bajo: {producto.nombre_producto}',
            mensaje=f'El producto "{producto.nombre_producto}" tiene un stock de {producto.cantidad_disponible} unidades, por debajo del mínimo recomendado ({producto.stock_minimo}).',
            enlace=reverse('inventario:detalle_producto', args=[producto.id])
        )

@receiver(post_save, sender=PedidoProveedor)
def notificar_cambios_pedido(sender, instance, created, **kwargs):
    """
    Crea notificaciones cuando se crea o actualiza un pedido.
    """
    if not hasattr(instance, 'propietario'):
        return
        
    usuario = instance.propietario
    
    if created:
        # Notificación de pedido creado
        Notificacion.objects.create(
            usuario=usuario,
            tipo='PEDIDO_CREADO',
            nivel='INFO',
            titulo=f'Nuevo pedido #{instance.id} creado',
            mensaje=f'Se ha creado un nuevo pedido al proveedor {instance.proveedor.nombre_proveedor}.',
            enlace=reverse('inventario:detalle_pedido', args=[instance.id])
        )
    else:
        # Notificación de cambio de estado
        if instance.estado_pedido == 'RECIBIDO':
            Notificacion.objects.create(
                usuario=usuario,
                tipo='PEDIDO_RECIBIDO',
                nivel='SUCCESS',
                titulo=f'Pedido #{instance.id} recibido',
                mensaje=f'El pedido al proveedor {instance.proveedor.nombre_proveedor} ha sido marcado como recibido.',
                enlace=reverse('inventario:detalle_pedido', args=[instance.id])
            )
        elif instance.estado_pedido == 'CANCELADO':
            Notificacion.objects.create(
                usuario=usuario,
                tipo='PEDIDO_CANCELADO',
                nivel='ERROR',
                titulo=f'Pedido #{instance.id} cancelado',
                mensaje=f'El pedido al proveedor {instance.proveedor.nombre_proveedor} ha sido cancelado.',
                enlace=reverse('inventario:detalle_pedido', args=[instance.id])
            )
        elif instance.estado_pedido == 'EN_TRANSITO':
            Notificacion.objects.create(
                usuario=usuario,
                tipo='PEDIDO_CREADO',
                nivel='INFO',
                titulo=f'Pedido #{instance.id} en tránsito',
                mensaje=f'El pedido al proveedor {instance.proveedor.nombre_proveedor} está en tránsito.',
                enlace=reverse('inventario:detalle_pedido', args=[instance.id])
            )

@receiver(post_save, sender=CaducidadProducto)
def notificar_caducidad_proxima(sender, instance, created, **kwargs):
    """
    Crea una notificación cuando un producto está próximo a caducar.
    """
    if not created:
        return
        
    producto = instance.producto_inventario
    if not hasattr(producto, 'usuario'):
        return
        
    usuario = producto.usuario
    dias_para_caducidad = (instance.fecha_caducidad - timezone.now().date()).days
    
    if dias_para_caducidad <= 30:
        nivel = 'WARNING'
        if dias_para_caducidad <= 7:
            nivel = 'ERROR'
            
        Notificacion.objects.create(
            usuario=usuario,
            tipo='CADUCIDAD_PROXIMA',
            nivel=nivel,
            titulo=f'Producto próximo a caducar: {producto.nombre_producto}',
            mensaje=f'El producto "{producto.nombre_producto}" caducará en {dias_para_caducidad} días ({instance.fecha_caducidad}). Cantidad afectada: {instance.cantidad_disponible} unidades.',
            enlace=reverse('inventario:detalle_producto', args=[producto.id])
        )

@receiver(post_save, sender=MovimientoInventario)
def notificar_movimiento_inventario(sender, instance, created, **kwargs):
    """
    Crea una notificación cuando hay un movimiento significativo en el inventario.
    """
    if not created or not instance.usuario:
        return
        
    producto = instance.producto_inventario
    
    # Solo notificar para movimientos grandes (más del 20% del stock)
    if instance.tipo_movimiento in ['ENTRADA', 'SALIDA', 'AJUSTE']:
        stock_total = producto.cantidad_disponible + (instance.cantidad_movimiento if instance.tipo_movimiento == 'SALIDA' else 0)
        if stock_total > 0 and (instance.cantidad_movimiento / stock_total) >= 0.2:
            tipo_texto = {
                'ENTRADA': 'entrada',
                'SALIDA': 'salida',
                'AJUSTE': 'ajuste'
            }.get(instance.tipo_movimiento, 'movimiento')
            
            Notificacion.objects.create(
                usuario=instance.usuario,
                tipo='MOVIMIENTO',
                nivel='INFO',
                titulo=f'Movimiento importante de {tipo_texto}',
                mensaje=f'Se ha registrado un {tipo_texto} de {instance.cantidad_movimiento} unidades para el producto "{producto.nombre_producto}".',
                enlace=reverse('inventario:detalle_producto', args=[producto.id])
            ) 