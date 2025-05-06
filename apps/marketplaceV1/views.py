from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils import timezone
from django.urls import reverse
from django.core.paginator import Paginator
from decimal import Decimal
import uuid

from .models import (
    Producto, CategoriaProducto, CarritoItem, ListaDeseos, 
    Compra, DetalleCompra, MetodoPago, Pago, Orden, DireccionEnvio
)

def inicio_marketplace(request):
    """Vista principal del marketplace V1."""
    productos = Producto.objects.filter(activo=True, destacado=True)[:8]
    categorias = CategoriaProducto.objects.filter(activa=True)
    return render(request, 'marketplaceV1/inicio.html', {
        'productos': productos,
        'categorias': categorias
    })

def buscar_productos(request):
    """Vista para buscar productos."""
    query = request.GET.get('q', '')
    productos = Producto.objects.filter(
        Q(nombre__icontains=query) | Q(descripcion__icontains=query),
        activo=True
    )
    return render(request, 'marketplaceV1/buscar_productos.html', {
        'productos': productos,
        'query': query
    })

def lista_categorias(request):
    """Vista para listar todas las categorías."""
    categorias = CategoriaProducto.objects.filter(activa=True)
    return render(request, 'marketplaceV1/lista_categorias.html', {
        'categorias': categorias
    })

def productos_por_categoria(request, slug):
    """Vista para mostrar productos por categoría."""
    categoria = get_object_or_404(CategoriaProducto, slug=slug, activa=True)
    productos = Producto.objects.filter(categoria=categoria, activo=True)
    return render(request, 'marketplaceV1/productos_por_categoria.html', {
        'categoria': categoria,
        'productos': productos
    })

def detalle_producto(request, producto_id):
    """Vista para mostrar detalles de un producto."""
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    return render(request, 'marketplaceV1/detalle_producto.html', {
        'producto': producto
    })

@login_required
def crear_producto(request):
    """Vista para crear un nuevo producto."""
    return render(request, 'marketplaceV1/crear_producto.html')

@login_required
def editar_producto(request, producto_id):
    """Vista para editar un producto existente."""
    producto = get_object_or_404(Producto, id=producto_id, vendedor=request.user)
    return render(request, 'marketplaceV1/editar_producto.html', {
        'producto': producto
    })

@login_required
def eliminar_producto(request, producto_id):
    """Vista para eliminar un producto."""
    producto = get_object_or_404(Producto, id=producto_id, vendedor=request.user)
    return render(request, 'marketplaceV1/eliminar_producto.html', {
        'producto': producto
    })

@login_required
def mis_productos(request):
    """Vista para mostrar los productos del usuario."""
    productos = Producto.objects.filter(vendedor=request.user)
    return render(request, 'marketplaceV1/mis_productos.html', {
        'productos': productos
    })

@login_required
def ver_carrito(request):
    """Vista para ver el carrito de compras."""
    items = CarritoItem.objects.filter(usuario=request.user)
    total = sum(item.subtotal for item in items)
    
    return render(request, 'marketplaceV1/ver_carrito.html', {
        'items': items,
        'total': total
    })

@login_required
def agregar_al_carrito(request, producto_id):
    """Vista para agregar un producto al carrito."""
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    cantidad = int(request.POST.get('cantidad', 1))
    
    # Verificar si hay suficiente stock
    if cantidad > producto.stock:
        messages.error(request, f"No hay suficiente stock. Stock disponible: {producto.stock}")
        return JsonResponse({'status': 'error', 'message': f"No hay suficiente stock. Disponible: {producto.stock}"})
    
    # Verificar si ya existe este producto en el carrito
    item, created = CarritoItem.objects.get_or_create(
        usuario=request.user,
        producto=producto,
        defaults={'cantidad': cantidad}
    )
    
    # Si no es nuevo, actualizar la cantidad
    if not created:
        item.cantidad += cantidad
        if item.cantidad > producto.stock:
            item.cantidad = producto.stock
        item.save()
    
    messages.success(request, f"Producto '{producto.nombre}' agregado al carrito.")
    return JsonResponse({'status': 'success'})

@login_required
def actualizar_carrito(request, item_id):
    """Vista para actualizar la cantidad de un producto en el carrito."""
    item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
    cantidad = int(request.POST.get('cantidad', 1))
    
    # Verificar si hay suficiente stock
    if cantidad > item.producto.stock:
        cantidad = item.producto.stock
        messages.warning(request, f"Cantidad ajustada al stock disponible: {item.producto.stock}")
    
    item.cantidad = cantidad
    item.save()
    
    # Obtener nuevo subtotal y total del carrito
    subtotal = item.subtotal
    total = sum(i.subtotal for i in CarritoItem.objects.filter(usuario=request.user))
    
    return JsonResponse({
        'status': 'success', 
        'subtotal': subtotal, 
        'total': total
    })

@login_required
def eliminar_del_carrito(request, item_id):
    """Vista para eliminar un producto del carrito."""
    item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
    producto_nombre = item.producto.nombre
    item.delete()
    
    messages.success(request, f"Producto '{producto_nombre}' eliminado del carrito.")
    return JsonResponse({'status': 'success'})

@login_required
def vaciar_carrito(request):
    """Vista para vaciar el carrito de compras."""
    CarritoItem.objects.filter(usuario=request.user).delete()
    messages.success(request, "Carrito vaciado correctamente.")
    return JsonResponse({'status': 'success'})

@login_required
def checkout(request):
    """Vista para finalizar la compra."""
    # Verificar si hay productos en el carrito
    items = CarritoItem.objects.filter(usuario=request.user)
    if not items.exists():
        messages.error(request, "No tienes productos en el carrito.")
        return redirect('marketplaceV1:ver_carrito')
    
    # Calcular total
    total = sum(item.subtotal for item in items)
    
    # Obtener direcciones de envío y métodos de pago
    direcciones = DireccionEnvio.objects.filter(usuario=request.user)
    metodos_pago = MetodoPago.objects.filter(activo=True)
    
    # Si no hay direcciones, redirigir para agregar una
    if not direcciones.exists():
        messages.info(request, "Necesitas agregar una dirección de envío para continuar.")
        return redirect('marketplaceV1:agregar_direccion')
    
    # Procesar el checkout
    if request.method == 'POST':
        # Obtener datos del formulario
        direccion_id = request.POST.get('direccion')
        metodo_pago_id = request.POST.get('metodo_pago')
        
        # Validar datos
        if not direccion_id or not metodo_pago_id:
            messages.error(request, "Por favor, selecciona una dirección de envío y un método de pago.")
            return render(request, 'marketplaceV1/checkout.html', {
                'items': items,
                'total': total,
                'direcciones': direcciones,
                'metodos_pago': metodos_pago
            })
        
        try:
            direccion = DireccionEnvio.objects.get(id=direccion_id, usuario=request.user)
            metodo_pago = MetodoPago.objects.get(id=metodo_pago_id, activo=True)
        except (DireccionEnvio.DoesNotExist, MetodoPago.DoesNotExist):
            messages.error(request, "Error en la selección de dirección o método de pago.")
            return redirect('marketplaceV1:checkout')
        
        # Crear la compra
        compra = Compra.objects.create(
            usuario=request.user,
            estado='pendiente',
            direccion_envio=f"{direccion.nombre_completo}\n{direccion.telefono}\n{direccion.direccion}\n{direccion.ciudad}, {direccion.departamento}",
            metodo_pago=metodo_pago.nombre,
            total=total
        )
        
        # Crear detalles de la compra
        for item in items:
            DetalleCompra.objects.create(
                compra=compra,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio
            )
            
            # Actualizar stock del producto
            producto = item.producto
            producto.stock -= item.cantidad
            producto.save()
            
        # Crear orden asociada a la compra
        orden = Orden.objects.create(
            compra=compra,
            estado='pendiente_pago'
        )
        
        # Crear registro de pago pendiente
        Pago.objects.create(
            compra=compra,
            metodo_pago=metodo_pago,
            monto=total,
            estado='pendiente'
        )
        
        # Vaciar el carrito
        items.delete()
        
        messages.success(request, f"¡Orden creada correctamente! Tu número de orden es: {orden.numero_orden}")
        return redirect('marketplaceV1:detalle_orden', orden_id=orden.id)
    
    # Renderizar página de checkout
    return render(request, 'marketplaceV1/checkout.html', {
        'items': items,
        'total': total,
        'direcciones': direcciones,
        'metodos_pago': metodos_pago
    })

@login_required
def detalle_orden(request, orden_id):
    """Vista para ver los detalles de una orden."""
    orden = get_object_or_404(Orden, id=orden_id, compra__usuario=request.user)
    compra = orden.compra
    detalles = compra.detalles.all()
    pagos = compra.pagos.all()
    
    return render(request, 'marketplaceV1/detalle_orden.html', {
        'orden': orden,
        'compra': compra,
        'detalles': detalles,
        'pagos': pagos
    })

@login_required
def mis_ordenes(request):
    """Vista para ver las órdenes del usuario."""
    ordenes = Orden.objects.filter(compra__usuario=request.user).order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(ordenes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'marketplaceV1/mis_ordenes.html', {
        'page_obj': page_obj
    })

@login_required
def subir_comprobante(request, pago_id):
    """Vista para subir comprobante de pago."""
    pago = get_object_or_404(Pago, id=pago_id, compra__usuario=request.user)
    
    if request.method == 'POST':
        comprobante = request.FILES.get('comprobante')
        referencia = request.POST.get('referencia')
        comentarios = request.POST.get('comentarios')
        
        if not comprobante:
            messages.error(request, "Debes adjuntar un comprobante.")
            return redirect('marketplaceV1:detalle_orden', orden_id=pago.compra.orden.id)
        
        # Actualizar pago
        pago.comprobante = comprobante
        pago.referencia = referencia
        pago.comentarios = comentarios
        pago.save()
        
        # Actualizar estado de la orden
        orden = pago.compra.orden
        orden.estado = 'pendiente_pago'
        orden.save()
        
        messages.success(request, "Comprobante subido correctamente. Tu pago está en proceso de verificación.")
        return redirect('marketplaceV1:detalle_orden', orden_id=orden.id)
    
    return render(request, 'marketplaceV1/subir_comprobante.html', {
        'pago': pago
    })

@login_required
def cancelar_orden(request, orden_id):
    """Vista para cancelar una orden."""
    orden = get_object_or_404(Orden, id=orden_id, compra__usuario=request.user)
    
    # Solo se pueden cancelar órdenes en ciertos estados
    estados_cancelables = ['creada', 'pendiente_pago']
    if orden.estado not in estados_cancelables:
        messages.error(request, "No se puede cancelar esta orden en su estado actual.")
        return redirect('marketplaceV1:detalle_orden', orden_id=orden.id)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        
        # Actualizar estados
        orden.estado = 'cancelada'
        orden.notas = f"Cancelada por el usuario. Motivo: {motivo}"
        orden.save()
        
        compra = orden.compra
        compra.estado = 'cancelado'
        compra.save()
        
        # Devolver stock a los productos
        for detalle in compra.detalles.all():
            producto = detalle.producto
            producto.stock += detalle.cantidad
            producto.save()
        
        messages.success(request, "Orden cancelada correctamente.")
        return redirect('marketplaceV1:mis_ordenes')
    
    return render(request, 'marketplaceV1/cancelar_orden.html', {
        'orden': orden
    })

@login_required
def mis_direcciones(request):
    """Vista para gestionar las direcciones de envío del usuario."""
    direcciones = DireccionEnvio.objects.filter(usuario=request.user)
    return render(request, 'marketplaceV1/mis_direcciones.html', {
        'direcciones': direcciones
    })

@login_required
def agregar_direccion(request):
    """Vista para agregar una nueva dirección de envío."""
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre_completo = request.POST.get('nombre_completo')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')
        departamento = request.POST.get('departamento')
        codigo_postal = request.POST.get('codigo_postal')
        notas_adicionales = request.POST.get('notas_adicionales')
        predeterminada = 'predeterminada' in request.POST
        
        # Si es predeterminada, quitar esta marca de las demás direcciones
        if predeterminada:
            DireccionEnvio.objects.filter(usuario=request.user, predeterminada=True).update(predeterminada=False)
        
        # Crear nueva dirección
        DireccionEnvio.objects.create(
            usuario=request.user,
            nombre_completo=nombre_completo,
            telefono=telefono,
            direccion=direccion,
            ciudad=ciudad,
            departamento=departamento,
            codigo_postal=codigo_postal,
            notas_adicionales=notas_adicionales,
            predeterminada=predeterminada
        )
        
        messages.success(request, "Dirección agregada correctamente.")
        return redirect('marketplaceV1:mis_direcciones')
    
    return render(request, 'marketplaceV1/agregar_direccion.html')

@login_required
def editar_direccion(request, direccion_id):
    """Vista para editar una dirección de envío."""
    direccion = get_object_or_404(DireccionEnvio, id=direccion_id, usuario=request.user)
    
    if request.method == 'POST':
        # Actualizar datos
        direccion.nombre_completo = request.POST.get('nombre_completo')
        direccion.telefono = request.POST.get('telefono')
        direccion.direccion = request.POST.get('direccion')
        direccion.ciudad = request.POST.get('ciudad')
        direccion.departamento = request.POST.get('departamento')
        direccion.codigo_postal = request.POST.get('codigo_postal')
        direccion.notas_adicionales = request.POST.get('notas_adicionales')
        predeterminada = 'predeterminada' in request.POST
        
        # Si es predeterminada, quitar esta marca de las demás direcciones
        if predeterminada and not direccion.predeterminada:
            DireccionEnvio.objects.filter(usuario=request.user, predeterminada=True).update(predeterminada=False)
        
        direccion.predeterminada = predeterminada
        direccion.save()
        
        messages.success(request, "Dirección actualizada correctamente.")
        return redirect('marketplaceV1:mis_direcciones')
    
    return render(request, 'marketplaceV1/editar_direccion.html', {
        'direccion': direccion
    })

@login_required
def eliminar_direccion(request, direccion_id):
    """Vista para eliminar una dirección de envío."""
    direccion = get_object_or_404(DireccionEnvio, id=direccion_id, usuario=request.user)
    direccion.delete()
    
    messages.success(request, "Dirección eliminada correctamente.")
    return redirect('marketplaceV1:mis_direcciones')

@login_required
def detalle_compra(request, compra_id):
    """Vista para ver los detalles de una compra."""
    return render(request, 'marketplaceV1/detalle_compra.html')

@login_required
def mis_compras(request):
    """Vista para ver las compras del usuario."""
    return render(request, 'marketplaceV1/mis_compras.html')

@login_required
def lista_deseos(request):
    """Vista para ver la lista de deseos."""
    return render(request, 'marketplaceV1/lista_deseos.html')

@login_required
def agregar_a_deseos(request, producto_id):
    """Vista para agregar un producto a la lista de deseos."""
    return JsonResponse({'status': 'success'})

@login_required
def eliminar_de_deseos(request, lista_id):
    """Vista para eliminar un producto de la lista de deseos."""
    return JsonResponse({'status': 'success'})

@login_required
def agregar_valoracion(request, producto_id):
    """Vista para agregar una valoración a un producto."""
    return render(request, 'marketplaceV1/agregar_valoracion.html')

@login_required
def editar_valoracion(request, valoracion_id):
    """Vista para editar una valoración."""
    return render(request, 'marketplaceV1/editar_valoracion.html')

@login_required
def eliminar_valoracion(request, valoracion_id):
    """Vista para eliminar una valoración."""
    return JsonResponse({'status': 'success'}) 