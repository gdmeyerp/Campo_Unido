from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Producto, Compra, DetalleCompra

@receiver(post_save, sender=DetalleCompra)
def actualizar_stock_producto(sender, instance, created, **kwargs):
    """
    Señal que actualiza el stock del producto cuando se crea una compra.
    """
    if created:
        producto = instance.producto
        # Restar la cantidad comprada del stock del producto
        producto.stock -= instance.cantidad
        if producto.stock < 0:
            producto.stock = 0  # Evitar stock negativo
        producto.save()

@receiver(post_delete, sender=DetalleCompra)
def restaurar_stock_producto(sender, instance, **kwargs):
    """
    Señal que restaura el stock del producto cuando se elimina un detalle de compra.
    """
    producto = instance.producto
    # Devolver la cantidad al stock
    producto.stock += instance.cantidad
    producto.save()

@receiver(post_save, sender=Compra)
def on_compra_save(sender, instance, created, **kwargs):
    """
    Señal que se ejecuta cuando se crea o modifica una compra.
    """
    # Acciones adicionales cuando se crea una compra
    if created:
        pass
        # Aquí podría ir lógica adicional como enviar confirmaciones por email, etc. 