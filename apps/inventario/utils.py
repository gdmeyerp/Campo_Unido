"""
Utilidades para ayudar con el manejo de productos e inventario
"""
from django.db import transaction
from django.db.models import Count, Q, Sum
from .models import ProductoInventario, CategoriaProducto, MovimientoInventario, Notificacion
from django.contrib.auth import get_user_model

User = get_user_model()

def filtrar_productos_por_usuario(queryset, usuario):
    """
    Filtra un queryset de productos para mostrar solo los que pertenecen al usuario especificado.
    
    Args:
        queryset: QuerySet de ProductoInventario
        usuario: Usuario actual
        
    Returns:
        QuerySet filtrado
    """
    return queryset.filter(propietario=usuario)

def asignar_propietario_producto(producto, usuario):
    """
    Asigna un usuario como propietario de un producto.
    
    Args:
        producto: Objeto ProductoInventario
        usuario: Usuario a asignar como propietario
        
    Returns:
        Producto modificado
    """
    producto.propietario = usuario
    return producto

def verificar_productos_sin_propietario():
    """
    Encuentra productos sin propietario asignado.
    
    Returns:
        QuerySet de productos sin propietario
    """
    return ProductoInventario.objects.filter(propietario__isnull=True)

def verificar_categorias_sin_propietario():
    """
    Encuentra categorías sin propietario asignado.
    
    Returns:
        QuerySet de categorías sin propietario
    """
    return CategoriaProducto.objects.filter(propietario__isnull=True)

def reparar_propiedades_inventario(usuario):
    """
    Asigna el usuario especificado como propietario a todos los productos y categorías 
    que no tienen propietario.
    
    Args:
        usuario: Usuario a asignar como propietario
        
    Returns:
        Tuple con el número de productos y categorías reparados
    """
    with transaction.atomic():
        # Productos sin propietario
        productos_sin_propietario = verificar_productos_sin_propietario()
        count_productos = productos_sin_propietario.count()
        
        productos_sin_propietario.update(propietario=usuario)
        
        # Categorías sin propietario
        categorias_sin_propietario = verificar_categorias_sin_propietario()
        count_categorias = categorias_sin_propietario.count()
        
        categorias_sin_propietario.update(propietario=usuario)
        
    return (count_productos, count_categorias)

def verificar_integridad_stock(producto_id):
    """
    Verifica que el stock de un producto coincida con sus movimientos de inventario.
    
    Args:
        producto_id: ID del producto a verificar
        
    Returns:
        Tuple con (stock_actual, stock_calculado, diferencia)
    """
    try:
        producto = ProductoInventario.objects.get(id=producto_id)
        
        # Calcular el stock basado en los movimientos
        entradas = MovimientoInventario.objects.filter(
            producto_inventario_id=producto_id,
            tipo_movimiento='ENTRADA'
        ).aggregate(total=Sum('cantidad_movimiento'))['total'] or 0
        
        salidas = MovimientoInventario.objects.filter(
            producto_inventario_id=producto_id,
            tipo_movimiento='SALIDA'
        ).aggregate(total=Sum('cantidad_movimiento'))['total'] or 0
        
        ajustes = MovimientoInventario.objects.filter(
            producto_inventario_id=producto_id,
            tipo_movimiento='AJUSTE'
        ).order_by('-fecha_movimiento').first()
        
        if ajustes:
            # Si hay ajustes, el stock se calcula desde el último ajuste
            stock_calculado = ajustes.cantidad_movimiento
            
            # Sumar entradas posteriores al último ajuste
            entradas_post_ajuste = MovimientoInventario.objects.filter(
                producto_inventario_id=producto_id,
                tipo_movimiento='ENTRADA',
                fecha_movimiento__gt=ajustes.fecha_movimiento
            ).aggregate(total=Sum('cantidad_movimiento'))['total'] or 0
            
            # Restar salidas posteriores al último ajuste
            salidas_post_ajuste = MovimientoInventario.objects.filter(
                producto_inventario_id=producto_id,
                tipo_movimiento='SALIDA',
                fecha_movimiento__gt=ajustes.fecha_movimiento
            ).aggregate(total=Sum('cantidad_movimiento'))['total'] or 0
            
            stock_calculado = stock_calculado + entradas_post_ajuste - salidas_post_ajuste
        else:
            # Si no hay ajustes, el stock es entradas - salidas
            stock_calculado = entradas - salidas
        
        diferencia = producto.cantidad_disponible - stock_calculado
        
        return (producto.cantidad_disponible, stock_calculado, diferencia)
    except ProductoInventario.DoesNotExist:
        return (None, None, None)

def verificar_y_corregir_productos_usuario(usuario):
    """
    Verifica si hay productos asociados a un usuario específico y corrige
    automáticamente cualquier inconsistencia.
    
    Args:
        usuario: Usuario cuya propiedad sobre productos debe verificarse
        
    Returns:
        int: Número de productos corregidos
    """
    # Buscar productos sin propietario pero que pertenecen al usuario según
    # sus movimientos, asociaciones, etc.
    productos_corregidos = 0
    
    # 1. Productos sin propietario pero con movimientos del usuario
    movimientos_usuario = MovimientoInventario.objects.filter(
        usuario=usuario,
        producto_inventario__propietario__isnull=True
    ).values_list('producto_inventario_id', flat=True).distinct()
    
    if movimientos_usuario:
        with transaction.atomic():
            productos_afectados = ProductoInventario.objects.filter(
                id__in=movimientos_usuario,
                propietario__isnull=True
            )
            productos_corregidos += productos_afectados.count()
            productos_afectados.update(propietario=usuario)
    
    return productos_corregidos

def enviar_notificacion_sistema(titulo, mensaje, nivel='INFO', usuarios=None, enlace=None):
    """
    Envía una notificación de sistema a todos los usuarios o a usuarios específicos.
    
    Args:
        titulo (str): Título de la notificación
        mensaje (str): Mensaje detallado de la notificación
        nivel (str): Nivel de la notificación ('INFO', 'WARNING', 'ERROR', 'SUCCESS')
        usuarios (list): Lista de usuarios o IDs de usuario a los que enviar la notificación.
                        Si es None, se envía a todos los usuarios.
        enlace (str): URL relativa opcional para incluir en la notificación
    
    Returns:
        int: Número de notificaciones creadas
    """
    notificaciones_creadas = 0
    
    # Determinar los usuarios a los que enviar la notificación
    if usuarios is None:
        usuarios_destino = User.objects.all()
    else:
        # Convertir IDs a objetos de usuario si es necesario
        ids_usuarios = [u.id if hasattr(u, 'id') else u for u in usuarios]
        usuarios_destino = User.objects.filter(id__in=ids_usuarios)
    
    # Crear notificaciones para cada usuario
    for usuario in usuarios_destino:
        Notificacion.objects.create(
            usuario=usuario,
            tipo='SISTEMA',
            nivel=nivel,
            titulo=titulo,
            mensaje=mensaje,
            enlace=enlace
        )
        notificaciones_creadas += 1
    
    return notificaciones_creadas

def enviar_notificacion_usuario(usuario, titulo, mensaje, tipo='SISTEMA', nivel='INFO', enlace=None):
    """
    Envía una notificación a un usuario específico.
    
    Args:
        usuario: Usuario o ID de usuario al que enviar la notificación
        titulo (str): Título de la notificación
        mensaje (str): Mensaje detallado de la notificación
        tipo (str): Tipo de notificación (ver TIPO_CHOICES en el modelo Notificacion)
        nivel (str): Nivel de la notificación ('INFO', 'WARNING', 'ERROR', 'SUCCESS')
        enlace (str): URL relativa opcional para incluir en la notificación
    
    Returns:
        Notificacion: Objeto de notificación creado o None si no se pudo crear
    """
    # Obtener el usuario si se proporcionó un ID
    if not hasattr(usuario, 'id'):
        try:
            usuario = User.objects.get(id=usuario)
        except User.DoesNotExist:
            return None
    
    # Crear y devolver la notificación
    return Notificacion.objects.create(
        usuario=usuario,
        tipo=tipo,
        nivel=nivel,
        titulo=titulo,
        mensaje=mensaje,
        enlace=enlace
    ) 