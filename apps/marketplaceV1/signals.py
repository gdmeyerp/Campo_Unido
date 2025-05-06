from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Producto, DetalleCompra

@receiver(post_save, sender=DetalleCompra)
def actualizar_stock_compra(sender, instance, created, **kwargs):
    """
    Actualiza el stock del producto cuando se crea o modifica un detalle de compra
    """
    if created:
        # Si es un detalle nuevo, reducir el stock
        producto = instance.producto
        producto.stock -= instance.cantidad
        producto.save()
    else:
        # Si se modifica, manejar diferencia
        pass

@receiver(post_delete, sender=DetalleCompra)
def restaurar_stock_compra(sender, instance, **kwargs):
    """
    Restaura el stock cuando se elimina un detalle de compra
    """
    producto = instance.producto
    producto.stock += instance.cantidad
    producto.save()

@receiver(post_save, sender=Producto)
def actualizar_estado_producto(sender, instance, **kwargs):
    """
    Actualiza el estado del producto basado en el stock
    """
    if instance.stock <= 0 and instance.estado == 'disponible':
        instance.estado = 'agotado'
        instance.save(update_fields=['estado'])
    elif instance.stock > 0 and instance.estado == 'agotado':
        instance.estado = 'disponible'
        instance.save(update_fields=['estado']) 