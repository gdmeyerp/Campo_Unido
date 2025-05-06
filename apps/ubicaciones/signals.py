from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UbicacionProducto, UsuariosPorCategoria

@receiver(post_save, sender=UbicacionProducto)
def actualizar_usuario_categoria_al_guardar(sender, instance, created, **kwargs):
    """Actualiza el registro de usuarios por categoría cuando se guarda un producto"""
    if instance.producto.activo and instance.stock_disponible > 0:
        UsuariosPorCategoria.actualizar_usuario_categoria(
            instance.ubicacion.usuario,
            instance.producto
        )
    else:
        # Si el producto no está activo o no tiene stock, verificar si hay que eliminar el registro
        UsuariosPorCategoria.eliminar_usuario_categoria(
            instance.ubicacion.usuario,
            instance.producto.categoria
        )

@receiver(post_delete, sender=UbicacionProducto)
def actualizar_usuario_categoria_al_eliminar(sender, instance, **kwargs):
    """Actualiza el registro de usuarios por categoría cuando se elimina un producto"""
    UsuariosPorCategoria.eliminar_usuario_categoria(
        instance.ubicacion.usuario,
        instance.producto.categoria
    ) 