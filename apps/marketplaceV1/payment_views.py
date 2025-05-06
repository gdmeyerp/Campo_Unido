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