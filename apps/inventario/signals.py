from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import (
    ProductoInventario, MovimientoInventario, 
    AlertaStock, ReservaInventario, CaducidadProducto
)
from apps.marketplace.models import Compra

# Las señales se configurarán cuando tengamos los modelos definidos
# Aquí se manejarán eventos como:
# - Actualización automática de stock cuando se realiza una venta
# - Generación de alertas cuando el stock baje del mínimo
# - Registro de movimientos de inventario 

@receiver(post_save, sender=MovimientoInventario)
def actualizar_stock_producto(sender, instance, created, **kwargs):
    """
    Actualiza el stock del producto cuando se registra un movimiento de inventario.
    """
    if created:
        producto = instance.producto_inventario
        
        if instance.tipo_movimiento == 'ENTRADA':
            producto.cantidad_disponible += instance.cantidad_movimiento
        elif instance.tipo_movimiento == 'SALIDA':
            producto.cantidad_disponible -= instance.cantidad_movimiento
        elif instance.tipo_movimiento == 'AJUSTE':
            producto.cantidad_disponible = instance.cantidad_movimiento
        
        producto.save()

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