from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F, ProtectedError
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta
import csv
import xlwt
import json

from .models import (
    CategoriaProducto, EstadoProducto, UnidadMedida, ProductoInventario,
    MovimientoInventario, Proveedor, PedidoProveedor, DetallePedidoProveedor,
    Almacen, UbicacionAlmacen, InventarioAlmacen, CaducidadProducto,
    AlertaStock, ReservaInventario, ImagenProducto, Notificacion
)
from .forms import (
    CategoriaProductoForm, EstadoProductoForm, UnidadMedidaForm, ProductoInventarioForm,
    MovimientoInventarioForm, ProveedorForm, PedidoProveedorForm, DetallePedidoProveedorForm,
    AlmacenForm, UbicacionAlmacenForm, InventarioAlmacenForm, CaducidadProductoForm,
    AlertaStockForm, ReservaInventarioForm, ImagenProductoForm, RecepcionPedidoForm
)
from .utils import (
    filtrar_productos_por_usuario, asignar_propietario_producto,
    verificar_productos_sin_propietario, verificar_categorias_sin_propietario,
    reparar_propiedades_inventario, verificar_integridad_stock,
    verificar_y_corregir_productos_usuario
)

# Dashboard de Inventario
@login_required
def dashboard_inventario(request):
    # Estadísticas generales
    total_productos = ProductoInventario.objects.filter(propietario=request.user).count()
    productos_stock_bajo = ProductoInventario.objects.filter(
        propietario=request.user,
        cantidad_disponible__lte=F('stock_minimo')
    ).count()
    
    # Lista de productos con stock bajo para mostrar detalles
    productos_bajo_stock = ProductoInventario.objects.filter(
        propietario=request.user,
        cantidad_disponible__lte=F('stock_minimo')
    ).order_by('cantidad_disponible')[:10]
    
    # Productos más vendidos (últimos 30 días)
    fecha_inicio = timezone.now() - timedelta(days=30)
    movimientos_salida = MovimientoInventario.objects.filter(
        producto_inventario__propietario=request.user,
        tipo_movimiento='SALIDA',
        fecha_movimiento__gte=fecha_inicio
    ).values('producto_inventario').annotate(
        total_vendido=Sum('cantidad_movimiento')
    ).order_by('-total_vendido')[:5]
    
    productos_mas_vendidos = []
    for movimiento in movimientos_salida:
        try:
            producto = ProductoInventario.objects.get(id=movimiento['producto_inventario'], propietario=request.user)
            productos_mas_vendidos.append({
                'producto': producto,
                'total_vendido': movimiento['total_vendido']
            })
        except ProductoInventario.DoesNotExist:
            continue
    
    # Alertas recientes
    alertas_recientes = AlertaStock.objects.filter(
        producto_inventario__propietario=request.user
    ).order_by('-fecha_alerta')[:10]
    
    # Movimientos recientes
    movimientos_recientes = MovimientoInventario.objects.filter(
        producto_inventario__propietario=request.user
    ).order_by('-fecha_movimiento')[:5]
    
    # Pedidos pendientes
    pedidos_pendientes = PedidoProveedor.objects.filter(
        estado_pedido__in=['PENDIENTE', 'EN_TRANSITO'],
        propietario=request.user
    ).order_by('fecha_entrega')[:5]
    
    # Productos por categoría para gráfica
    productos_por_categoria = CategoriaProducto.objects.filter(
        Q(propietario=request.user) | Q(propietario__isnull=True)
    ).annotate(
        cantidad_productos=Count('productoinventario', filter=Q(productoinventario__propietario=request.user))
    ).values('nombre_categoria', 'cantidad_productos').order_by('-cantidad_productos')[:8]
    
    return render(request, 'inventario/dashboard_inventario.html', {
        'total_productos': total_productos,
        'productos_stock_bajo': productos_stock_bajo,
        'productos_bajo_stock': productos_bajo_stock,
        'productos_mas_vendidos': productos_mas_vendidos,
        'alertas_recientes': alertas_recientes,
        'movimientos_recientes': movimientos_recientes,
        'pedidos_pendientes': pedidos_pendientes,
        'productos_por_categoria': productos_por_categoria,
    })

# Listar productos
@login_required
def lista_productos(request):
    # Obtener todas las categorías y estados para los filtros
    categorias = CategoriaProducto.objects.filter(propietario=request.user)
    estados = EstadoProducto.objects.all()
    
    # Aplicar filtros
    queryset = ProductoInventario.objects.filter(propietario=request.user).order_by('nombre_producto')
    
    # Filtro por nombre
    q = request.GET.get('q')
    if q:
        queryset = queryset.filter(nombre_producto__icontains=q)
    
    # Filtro por categoría
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        queryset = queryset.filter(categoria_producto_id=categoria_id)
    
    # Filtro por estado
    estado_id = request.GET.get('estado')
    if estado_id:
        queryset = queryset.filter(estado_producto_id=estado_id)
    
    # Paginación
    paginator = Paginator(queryset, 10)  # 10 productos por página
    page = request.GET.get('page')
    productos = paginator.get_page(page)
    
    return render(request, 'inventario/lista_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'estados': estados,
    })

@login_required
def crear_producto(request):
    if request.method == 'POST':
        # Para depuración, podemos ver los datos del POST
        print("POST data:", request.POST)
        
        # Asegurarnos de que el propietario esté en los datos del formulario
        data = request.POST.copy()
        if 'propietario' not in data or not data['propietario']:
            data['propietario'] = request.user.id
        
        form = ProductoInventarioForm(data, user=request.user)
        if form.is_valid():
            try:
                producto = form.save(commit=False)
                
                # Asegurarnos de que el producto tenga un propietario
                producto.propietario = request.user
                
                # Verificar que la categoría seleccionada existe
                categoria_id = form.cleaned_data.get('categoria_producto')
                if categoria_id:
                    producto.save()
                    messages.success(request, f'Producto "{producto.nombre_producto}" creado exitosamente.')
                    
                    # Redirigir a la página de gestión de imágenes si el usuario quiere agregar imágenes
                    if 'agregar_imagenes' in request.POST:
                        return redirect('inventario:gestionar_imagenes', producto_id=producto.id)
                    
                    return redirect('inventario:detalle_producto', pk=producto.id)
                else:
                    messages.error(request, 'Debe seleccionar una categoría para el producto.')
            except Exception as e:
                messages.error(request, f'Error al crear el producto: {str(e)}')
        else:
            # Si el formulario no es válido, mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en el campo {field}: {error}')
    else:
        form = ProductoInventarioForm(user=request.user)
    
    # Obtener todas las categorías para el modal de creación rápida
    categorias = CategoriaProducto.objects.all().order_by('nombre_categoria')
    estados = EstadoProducto.objects.all()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Producto',
        'categorias': categorias,
        'estados': estados
    }
    
    return render(request, 'inventario/producto_form.html', context)

@login_required
def detalle_producto(request, pk):
    try:
        producto = get_object_or_404(ProductoInventario, pk=pk)
        
        # Verificar que el producto pertenezca al usuario actual
        if producto.propietario and producto.propietario != request.user:
            messages.error(request, "No tienes permisos para ver este producto.")
            return redirect('inventario:lista_productos')
        
        # Si el producto no tiene propietario, asignarlo al usuario actual
        if not producto.propietario:
            producto.propietario = request.user
            producto.save()
            messages.info(request, "Este producto no tenía propietario y se ha asignado a tu cuenta.")
        
        # Obtener historial de movimientos
        movimientos = MovimientoInventario.objects.filter(
            producto_inventario=producto
        ).order_by('-fecha_movimiento')[:20]  # Limitar a los últimos 20 movimientos
        
        return render(request, 'inventario/detalle_producto.html', {
            'producto': producto,
            'movimientos': movimientos,
        })
    except Exception as e:
        messages.error(request, f"Error al acceder al producto: {str(e)}")
        return redirect('inventario:lista_productos')

@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(ProductoInventario, pk=pk)
    
    # Verificar que el producto pertenezca al usuario
    if producto.propietario and producto.propietario != request.user:
        messages.error(request, "No tienes permisos para editar este producto.")
        return redirect('inventario:lista_productos')
    
    # Si el producto no tiene propietario, asignar el usuario actual
    if not producto.propietario:
        producto.propietario = request.user
        producto.save()
        messages.info(request, "Este producto no tenía propietario y se ha asignado a tu cuenta.")
    
    if request.method == 'POST':
        # Asegurarnos de que el propietario esté en los datos del formulario
        data = request.POST.copy()
        if 'propietario' not in data or not data['propietario']:
            data['propietario'] = request.user.id
            
        form = ProductoInventarioForm(data, instance=producto, user=request.user)
        if form.is_valid():
            try:
                producto_actualizado = form.save(commit=False)
                producto_actualizado.propietario = request.user  # Asegurar que el propietario siga siendo el usuario actual
                producto_actualizado.save()
                messages.success(request, f'Producto "{producto_actualizado.nombre_producto}" actualizado exitosamente.')
                return redirect('inventario:detalle_producto', pk=producto_actualizado.id)
            except Exception as e:
                messages.error(request, f'Error al actualizar el producto: {str(e)}')
        else:
            # Si el formulario no es válido, mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en el campo {field}: {error}')
    else:
        form = ProductoInventarioForm(instance=producto, user=request.user)
    
    # Obtener categorías para el modal de creación rápida
    categorias = CategoriaProducto.objects.all().order_by('nombre_categoria')
    
    context = {
        'form': form,
        'producto': producto,
        'titulo': 'Editar Producto',
        'categorias': categorias
    }
    
    return render(request, 'inventario/producto_form.html', context)

@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(ProductoInventario, pk=pk)
    
    # Verificar que el producto pertenezca al usuario
    if producto.propietario and producto.propietario != request.user:
        messages.error(request, "No tienes permisos para eliminar este producto.")
        return redirect('inventario:lista_productos')
    
    if request.method == 'POST':
        nombre = producto.nombre_producto
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado con éxito.')
        return redirect('inventario:lista_productos')
    
    context = {
        'producto': producto,
    }
    
    return render(request, 'inventario/producto_confirm_delete.html', context)

# Vistas para Movimientos de Inventario
@login_required
def lista_movimientos(request):
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    
    # Filtrar movimientos para mostrar solo los que corresponden a productos del usuario actual
    movimientos = MovimientoInventario.objects.filter(producto_inventario__propietario=request.user)
    
    if query:
        movimientos = movimientos.filter(
            Q(producto_inventario__nombre_producto__icontains=query) |
            Q(descripcion_movimiento__icontains=query) |
            Q(referencia_documento__icontains=query)
        )
    
    if tipo:
        movimientos = movimientos.filter(tipo_movimiento=tipo)
    
    if fecha_inicio:
        movimientos = movimientos.filter(fecha_movimiento__gte=fecha_inicio)
    
    if fecha_fin:
        movimientos = movimientos.filter(fecha_movimiento__lte=fecha_fin)
    
    # Ordenar por fecha (más reciente primero)
    movimientos = movimientos.order_by('-fecha_movimiento')
    
    # Paginación
    paginator = Paginator(movimientos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Datos para filtros
    tipos_movimiento = MovimientoInventario.objects.filter(
        producto_inventario__propietario=request.user
    ).values_list('tipo_movimiento', flat=True).distinct()
    
    # Obtener todos los productos para el filtro
    productos = ProductoInventario.objects.filter(propietario=request.user).order_by('nombre_producto')
    
    # Lista de usuarios (solo el usuario actual en este caso)
    usuarios = [request.user]
    
    context = {
        'page_obj': page_obj,
        'movimientos': page_obj.object_list,  # Añadir la lista de movimientos de la página actual
        'query': query,
        'tipos_movimiento': tipos_movimiento,
        'tipo_seleccionado': tipo,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'productos': productos,
        'usuarios': usuarios
    }
    return render(request, 'inventario/movimiento_list.html', context)

@login_required
def registrar_movimiento(request):
    # Si se especifica un producto en la URL
    producto_id = request.GET.get('producto_id')
    producto_seleccionado = None
    
    if producto_id:
        try:
            producto_seleccionado = ProductoInventario.objects.get(id=producto_id, propietario=request.user)
        except ProductoInventario.DoesNotExist:
            messages.error(request, "El producto especificado no existe o no tienes permiso para acceder a él.")
            return redirect('inventario:lista_movimientos')
    
    if request.method == 'POST':
        form = MovimientoInventarioForm(request.POST, user=request.user)
        if form.is_valid():
            movimiento = form.save(commit=False)
            
            # Esta verificación es redundante ahora que filtramos en el formulario,
            # pero la mantenemos como medida de seguridad adicional
            if movimiento.producto_inventario.propietario != request.user:
                messages.error(request, "No tienes permisos para registrar movimientos para este producto.")
                return redirect('inventario:lista_movimientos')
            
            movimiento.usuario = request.user
            movimiento.save()
            
            messages.success(request, 'Movimiento de inventario registrado con éxito.')
            return redirect('inventario:lista_movimientos')
        else:
            # Mostrar mensajes específicos para los errores
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en el campo {field}: {error}")
    else:
        initial_data = {}
        if producto_seleccionado:
            initial_data['producto_inventario'] = producto_seleccionado
            
        form = MovimientoInventarioForm(initial=initial_data, user=request.user)
    
    context = {
        'form': form,
        'titulo': 'Registrar Movimiento de Inventario',
        'producto': form['producto_inventario'] if 'producto_inventario' in form.fields else None,
        'tipo': form['tipo_movimiento'] if 'tipo_movimiento' in form.fields else None,
        'cantidad': form['cantidad_movimiento'] if 'cantidad_movimiento' in form.fields else None,
        'fecha': None  # Este campo no parece estar en el formulario, pero se usa en la plantilla
    }
    return render(request, 'inventario/movimiento_form.html', context)

# Vistas para Proveedores
@login_required
def lista_proveedores(request):
    search = request.GET.get('search', '')
    estado = request.GET.get('estado', '')
    
    # Filtrar proveedores para mostrar solo los del usuario actual
    proveedores = Proveedor.objects.filter(propietario=request.user)
    
    if search:
        proveedores = proveedores.filter(
            Q(nombre_proveedor__icontains=search) |
            Q(email__icontains=search) |
            Q(telefono__icontains=search)
        )
    
    # Ordenar por nombre
    proveedores = proveedores.order_by('nombre_proveedor')
    
    # Paginación
    paginator = Paginator(proveedores, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'proveedores': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'inventario/proveedor_list.html', context)

@login_required
def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save(commit=False)
            proveedor.propietario = request.user  # Asignar el usuario actual como propietario
            proveedor.save()
            messages.success(request, f'Proveedor "{proveedor.nombre_proveedor}" creado con éxito.')
            return redirect('inventario:detalle_proveedor', pk=proveedor.pk)
    else:
        form = ProveedorForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Proveedor'
    }
    return render(request, 'inventario/proveedor_form.html', context)

@login_required
def detalle_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    # Verificar que el proveedor pertenezca al usuario
    if proveedor.propietario and proveedor.propietario != request.user:
        messages.error(request, "No tienes permisos para ver este proveedor.")
        return redirect('inventario:lista_proveedores')
    
    # Si el proveedor no tiene propietario, asignar el usuario actual
    if not proveedor.propietario:
        proveedor.propietario = request.user
        proveedor.save()
        messages.info(request, "Este proveedor no tenía propietario y se ha asignado a tu cuenta.")
    
    # Pedidos del proveedor
    pedidos = PedidoProveedor.objects.filter(
        proveedor=proveedor,
        propietario=request.user
    ).order_by('-fecha_pedido')
    
    context = {
        'proveedor': proveedor,
        'pedidos': pedidos
    }
    return render(request, 'inventario/proveedor_detail.html', context)

@login_required
def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    # Verificar que el proveedor pertenezca al usuario
    if proveedor.propietario and proveedor.propietario != request.user:
        messages.error(request, "No tienes permisos para editar este proveedor.")
        return redirect('inventario:lista_proveedores')
    
    # Si el proveedor no tiene propietario, asignar el usuario actual
    if not proveedor.propietario:
        proveedor.propietario = request.user
        proveedor.save()
        messages.info(request, "Este proveedor no tenía propietario y se ha asignado a tu cuenta.")
    
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            proveedor_actualizado = form.save(commit=False)
            proveedor_actualizado.propietario = request.user  # Asegurar que el propietario siga siendo el usuario actual
            proveedor_actualizado.save()
            messages.success(request, f'Proveedor "{proveedor_actualizado.nombre_proveedor}" actualizado con éxito.')
            return redirect('inventario:detalle_proveedor', pk=proveedor.pk)
    else:
        form = ProveedorForm(instance=proveedor)
    
    context = {
        'form': form,
        'proveedor': proveedor
    }
    return render(request, 'inventario/proveedor_form.html', context)

# Vistas para Pedidos a Proveedores
@login_required
def lista_pedidos(request):
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    
    # Obtener todos los pedidos para verificar cuántos hay en total
    total_pedidos = PedidoProveedor.objects.all().count()
    
    # Filtrar pedidos para mostrar solo los del usuario actual o sin propietario
    pedidos = PedidoProveedor.objects.filter(
        Q(propietario=request.user) | Q(propietario__isnull=True)
    )
    
    # Contar cuántos pedidos puede ver el usuario actual
    pedidos_visibles = pedidos.count()
    
    # Si hay pedidos no visibles, mostrar un mensaje
    if pedidos_visibles < total_pedidos:
        messages.info(
            request, 
            f"Se encontraron {total_pedidos} pedidos en total, pero solo puedes ver {pedidos_visibles} porque los demás pertenecen a otros usuarios."
        )
    
    if query:
        pedidos = pedidos.filter(
            Q(proveedor__nombre_proveedor__icontains=query)
        )
    
    if estado:
        pedidos = pedidos.filter(estado_pedido=estado)
    
    # Ordenar por fecha (más reciente primero)
    pedidos = pedidos.order_by('-fecha_pedido')
    
    # Paginación
    paginator = Paginator(pedidos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Datos para filtros
    estados_pedido = PedidoProveedor.objects.filter(
        Q(propietario=request.user) | Q(propietario__isnull=True)
    ).values_list(
        'estado_pedido', flat=True
    ).distinct()
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'estados_pedido': estados_pedido,
        'estado_seleccionado': estado,
        'total_pedidos': total_pedidos,
        'pedidos_visibles': pedidos_visibles
    }
    return render(request, 'inventario/pedido_list.html', context)

@login_required
def crear_pedido(request):
    if request.method == 'POST':
        # Copiar los datos POST para asegurarnos de que el propietario esté presente
        data = request.POST.copy()
        if 'propietario' not in data or not data['propietario']:
            data['propietario'] = request.user.id
            
        form = PedidoProveedorForm(data, user=request.user)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.propietario = request.user  # Asegurar que el propietario sea el usuario actual
            pedido.save()
            messages.success(request, f'Pedido #{pedido.id} creado con éxito.')
            return redirect('inventario:detalle_pedido', pk=pedido.pk)
        else:
            # Si el formulario no es válido, mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en el campo {field}: {error}')
    else:
        form = PedidoProveedorForm(user=request.user)
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Pedido'
    }
    return render(request, 'inventario/pedido_form.html', context)

@login_required
def detalle_pedido(request, pk):
    pedido = get_object_or_404(PedidoProveedor, pk=pk)
    
    # Verificar que el pedido pertenezca al usuario
    if pedido.propietario and pedido.propietario != request.user:
        messages.error(request, "No tienes permisos para ver este pedido.")
        return redirect('inventario:lista_pedidos')
    
    # Si el pedido no tiene propietario, asignar el usuario actual
    if not pedido.propietario:
        pedido.propietario = request.user
        pedido.save()
        messages.info(request, "Este pedido no tenía propietario y se ha asignado a tu cuenta.")
    
    # Detalles del pedido
    detalles = DetallePedidoProveedor.objects.filter(
        pedido_proveedor=pedido
    )
    
    # Calcular el total del pedido
    total = sum(detalle.subtotal for detalle in detalles)
    
    # Obtener lista de productos para el modal de agregar producto
    productos = ProductoInventario.objects.filter(propietario=request.user).order_by('nombre_producto')
    
    # Formulario para agregar productos al pedido
    if request.method == 'POST':
        detalle_form = DetallePedidoProveedorForm(request.POST)
        if detalle_form.is_valid():
            detalle = detalle_form.save(commit=False)
            detalle.pedido_proveedor = pedido
            detalle.subtotal = detalle.cantidad * detalle.precio_unitario
            detalle.save()
            messages.success(request, 'Producto agregado al pedido con éxito.')
            return redirect('inventario:detalle_pedido', pk=pedido.pk)
    else:
        detalle_form = DetallePedidoProveedorForm()
    
    context = {
        'pedido': pedido,
        'detalles': detalles,
        'detalle_form': detalle_form,
        'total': total,
        'productos': productos,
    }
    return render(request, 'inventario/pedido_detail.html', context)

@login_required
def editar_pedido(request, pk):
    pedido = get_object_or_404(PedidoProveedor, pk=pk)
    
    # Verificar que el pedido pertenezca al usuario
    if pedido.propietario and pedido.propietario != request.user:
        messages.error(request, "No tienes permisos para editar este pedido.")
        return redirect('inventario:lista_pedidos')
    
    # Si el pedido no tiene propietario, asignar el usuario actual
    if not pedido.propietario:
        pedido.propietario = request.user
        pedido.save()
        messages.info(request, "Este pedido no tenía propietario y se ha asignado a tu cuenta.")
    
    if request.method == 'POST':
        # Asegurarnos de que el propietario esté en los datos del formulario
        data = request.POST.copy()
        if 'propietario' not in data or not data['propietario']:
            data['propietario'] = request.user.id
            
        form = PedidoProveedorForm(data, instance=pedido, user=request.user)
        if form.is_valid():
            pedido_actualizado = form.save(commit=False)
            pedido_actualizado.propietario = request.user  # Asegurar que el propietario siga siendo el usuario actual
            pedido_actualizado.save()
            messages.success(request, f'Pedido #{pedido.id} actualizado con éxito.')
            return redirect('inventario:detalle_pedido', pk=pedido.pk)
        else:
            # Si el formulario no es válido, mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en el campo {field}: {error}')
    else:
        form = PedidoProveedorForm(instance=pedido, user=request.user)
    
    # Obtener lista de productos para el modal de agregar producto
    productos = ProductoInventario.objects.filter(propietario=request.user).order_by('nombre_producto')
    
    # Obtener los detalles del pedido
    detalles = DetallePedidoProveedor.objects.filter(pedido_proveedor=pedido)
    
    # Calcular el total del pedido
    total = sum(detalle.subtotal for detalle in detalles)
    
    context = {
        'form': form,
        'titulo': f'Editar Pedido #{pedido.id}',
        'pedido': pedido,
        'productos': productos,
        'detalles': detalles,
        'total': total
    }
    return render(request, 'inventario/pedido_form.html', context)

@login_required
def eliminar_detalle_pedido(request, pk):
    detalle = get_object_or_404(DetallePedidoProveedor, pk=pk)
    pedido = detalle.pedido_proveedor
    pedido_id = pedido.id
    
    # Verificar que el pedido pertenezca al usuario
    if pedido.propietario and pedido.propietario != request.user:
        messages.error(request, "No tienes permisos para modificar este pedido.")
        return redirect('inventario:lista_pedidos')
    
    # Si el pedido no tiene propietario, asignar el usuario actual
    if not pedido.propietario:
        pedido.propietario = request.user
        pedido.save()
        messages.info(request, "Este pedido no tenía propietario y se ha asignado a tu cuenta.")
    
    # Eliminar el detalle (aceptamos tanto GET como POST para mayor flexibilidad)
    detalle.delete()
    messages.success(request, 'Producto eliminado del pedido con éxito.')
    
    # Redirigir a la página de detalle del pedido
    return redirect('inventario:detalle_pedido', pk=pedido_id)

# Vistas para Almacenes
@login_required
def lista_almacenes(request):
    # Filtrar almacenes para mostrar solo los del usuario actual
    almacenes = Almacen.objects.filter(propietario=request.user).order_by('nombre_almacen')
    
    context = {
        'almacenes': almacenes,
    }
    
    return render(request, 'inventario/almacenes/lista.html', context)

@login_required
def crear_almacen(request):
    if request.method == 'POST':
        form = AlmacenForm(request.POST)
        if form.is_valid():
            almacen = form.save(commit=False)
            almacen.propietario = request.user  # Asignar el usuario actual como propietario
            almacen.save()
            messages.success(request, f'Almacén "{almacen.nombre_almacen}" creado con éxito.')
            return redirect('inventario:detalle_almacen', pk=almacen.pk)
    else:
        form = AlmacenForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Almacén',
    }
    
    return render(request, 'inventario/almacenes/form.html', context)

@login_required
def detalle_almacen(request, pk):
    almacen = get_object_or_404(Almacen, pk=pk)
    
    # Verificar que el almacén pertenezca al usuario
    if almacen.propietario and almacen.propietario != request.user:
        messages.error(request, "No tienes permisos para ver este almacén.")
        return redirect('inventario:lista_almacenes')
    
    # Si el almacén no tiene propietario, asignar el usuario actual
    if not almacen.propietario:
        almacen.propietario = request.user
        almacen.save()
        messages.info(request, "Este almacén no tenía propietario y se ha asignado a tu cuenta.")
    
    # Ubicaciones del almacén
    ubicaciones = UbicacionAlmacen.objects.filter(
        almacen=almacen
    ).order_by('nombre_ubicacion')
    
    # Productos en el almacén
    inventario = InventarioAlmacen.objects.filter(
        ubicacion_almacen__almacen=almacen
    ).select_related('producto_inventario', 'ubicacion_almacen')
    
    context = {
        'almacen': almacen,
        'ubicaciones': ubicaciones,
        'inventario': inventario,
    }
    
    return render(request, 'inventario/almacenes/detalle.html', context)

# Vistas para Ubicaciones de Almacén
@login_required
def crear_ubicacion(request, almacen_id):
    almacen = get_object_or_404(Almacen, pk=almacen_id)
    
    if request.method == 'POST':
        form = UbicacionAlmacenForm(request.POST)
        if form.is_valid():
            ubicacion = form.save(commit=False)
            ubicacion.almacen = almacen
            ubicacion.save()
            messages.success(request, f'Ubicación "{ubicacion.nombre_ubicacion}" creada con éxito.')
            return redirect('inventario:detalle_almacen', pk=almacen.pk)
    else:
        form = UbicacionAlmacenForm(initial={'almacen': almacen})
    
    context = {
        'form': form,
        'titulo': f'Crear Nueva Ubicación en {almacen.nombre_almacen}',
        'almacen': almacen,
    }
    
    return render(request, 'inventario/almacenes/ubicacion_form.html', context)

# Vistas para Inventario en Almacenes
@login_required
def asignar_producto_ubicacion(request, ubicacion_id):
    ubicacion = get_object_or_404(UbicacionAlmacen, pk=ubicacion_id)
    
    if request.method == 'POST':
        form = InventarioAlmacenForm(request.POST, user=request.user)
        if form.is_valid():
            inventario = form.save(commit=False)
            inventario.ubicacion_almacen = ubicacion
            
            # Verificar que el producto pertenezca al usuario actual
            if inventario.producto_inventario.propietario != request.user:
                messages.error(request, "No tienes permisos para asignar este producto.")
                return redirect('inventario:detalle_almacen', pk=ubicacion.almacen.pk)
            
            # Verificar si ya existe el producto en esta ubicación
            existente = InventarioAlmacen.objects.filter(
                producto_inventario=inventario.producto_inventario,
                ubicacion_almacen=ubicacion
            ).first()
            
            if existente:
                existente.cantidad += inventario.cantidad
                existente.save()
                messages.success(request, f'Cantidad actualizada para {inventario.producto_inventario.nombre_producto}.')
            else:
                inventario.save()
                messages.success(request, f'Producto {inventario.producto_inventario.nombre_producto} asignado a la ubicación.')
            
            return redirect('inventario:detalle_almacen', pk=ubicacion.almacen.pk)
        else:
            # Mostrar mensajes específicos para los errores
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en el campo {field}: {error}")
    else:
        form = InventarioAlmacenForm(initial={'ubicacion_almacen': ubicacion}, user=request.user)
    
    context = {
        'form': form,
        'titulo': f'Asignar Producto a {ubicacion.nombre_ubicacion}',
        'ubicacion': ubicacion,
    }
    
    return render(request, 'inventario/inventario_almacen/form.html', context)

# Vistas para Caducidad de Productos
@login_required
def registrar_caducidad(request, producto_id):
    producto = get_object_or_404(ProductoInventario, pk=producto_id)
    
    if request.method == 'POST':
        form = CaducidadProductoForm(request.POST)
        if form.is_valid():
            caducidad = form.save(commit=False)
            caducidad.producto_inventario = producto
            caducidad.save()
            messages.success(request, f'Fecha de caducidad registrada para {producto.nombre_producto}.')
            return redirect('inventario:detalle_producto', pk=producto.pk)
    else:
        form = CaducidadProductoForm(initial={'producto_inventario': producto})
    
    context = {
        'form': form,
        'titulo': f'Registrar Caducidad para {producto.nombre_producto}',
        'producto': producto,
    }
    
    return render(request, 'inventario/caducidad/form.html', context)

@login_required
def crear_alerta_stock(request, producto_id):
    producto = get_object_or_404(ProductoInventario, id=producto_id)
    
    # Verificar si ya existe una alerta reciente (últimas 24 horas)
    alerta_reciente = AlertaStock.objects.filter(
        producto_inventario=producto,
        fecha_alerta__gte=timezone.now() - timedelta(hours=24)
    ).exists()
    
    if alerta_reciente:
        messages.warning(request, f"Ya existe una alerta reciente para {producto.nombre_producto}.")
        return redirect('inventario:detalle_producto', pk=producto_id)
    
    # Crear nueva alerta
    alerta = AlertaStock.objects.create(
        producto_inventario=producto,
        cantidad_disponible=producto.cantidad_disponible
    )
    
    messages.success(request, f"Alerta de stock creada para {producto.nombre_producto}.")
    return redirect('inventario:detalle_producto', pk=producto_id)

# Función para verificar y crear alertas de stock automáticas
@login_required
def verificar_stock_bajo(request):
    productos_stock_bajo = ProductoInventario.objects.filter(
        cantidad_disponible__lte=F('stock_minimo')
    )
    
    contador = 0
    for producto in productos_stock_bajo:
        # Verificar si ya existe una alerta reciente (últimas 24 horas)
        alerta_reciente = AlertaStock.objects.filter(
            producto_inventario=producto,
            fecha_alerta__gte=timezone.now() - timedelta(hours=24)
        ).exists()
        
        if not alerta_reciente:
            # Crear nueva alerta
            AlertaStock.objects.create(
                producto_inventario=producto,
                cantidad_disponible=producto.cantidad_disponible
            )
            contador += 1
    
    messages.success(request, f"Se han creado {contador} alertas de stock bajo.")
    return redirect('inventario:dashboard')

@login_required
def exportar_informe_inventario(request, formato='excel'):
    """
    Exporta un informe de inventario en diferentes formatos (Excel, CSV, PDF)
    """
    from django.http import HttpResponse
    import csv
    import xlwt
    from datetime import datetime
    
    # Obtener datos para el informe - FILTRAR POR USUARIO ACTUAL
    productos = ProductoInventario.objects.filter(propietario=request.user).select_related(
        'categoria_producto', 'estado_producto'
    ).order_by('categoria_producto__nombre_categoria', 'nombre_producto')
    
    if formato == 'excel':
        # Crear libro de Excel
        response = HttpResponse(
            content_type='application/ms-excel'
        )
        response['Content-Disposition'] = f'attachment; filename="inventario_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xls"'
        
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Inventario')
        
        # Estilos
        header_style = xlwt.easyxf('font: bold on; align: wrap on, vert centre, horiz center')
        date_style = xlwt.easyxf(num_format_str='DD/MM/YYYY')
        
        # Encabezados
        row_num = 0
        columns = [
            'ID', 'Nombre', 'Categoría', 'Stock Actual', 'Stock Mínimo', 
            'Precio Compra', 'Precio Venta', 'Estado'
        ]
        
        for col_num, column_title in enumerate(columns):
            ws.write(row_num, col_num, column_title, header_style)
        
        # Datos
        for producto in productos:
            row_num += 1
            
            row = [
                producto.id,
                producto.nombre_producto,
                producto.categoria_producto.nombre_categoria,
                producto.cantidad_disponible,
                producto.stock_minimo,
                producto.precio_compra,
                producto.precio_venta,
                producto.estado_producto.nombre_estado
            ]
            
            for col_num, cell_value in enumerate(row):
                ws.write(row_num, col_num, cell_value)
        
        wb.save(response)
        return response
    
    elif formato == 'csv':
        # Crear archivo CSV
        response = HttpResponse(
            content_type='text/csv'
        )
        response['Content-Disposition'] = f'attachment; filename="inventario_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        
        # Encabezados
        writer.writerow([
            'ID', 'Nombre', 'Categoría', 'Stock Actual', 'Stock Mínimo', 
            'Precio Compra', 'Precio Venta', 'Estado'
        ])
        
        # Datos
        for producto in productos:
            writer.writerow([
                producto.id,
                producto.nombre_producto,
                producto.categoria_producto.nombre_categoria,
                producto.cantidad_disponible,
                producto.stock_minimo,
                producto.precio_compra,
                producto.precio_venta,
                producto.estado_producto.nombre_estado
            ])
        
        return response
    
    # Si el formato no es compatible
    messages.warning(request, f'El formato {formato} no está soportado.')
    return redirect('inventario:dashboard')

# API para obtener información del producto
@login_required
def api_producto_info(request):
    """Vista para obtener información básica de un producto por AJAX"""
    producto_id = request.GET.get('producto_id')
    if not producto_id:
        return JsonResponse({'error': 'Producto no especificado'}, status=400)
    
    try:
        producto = ProductoInventario.objects.get(pk=producto_id)
        data = {
            'cantidad_disponible': producto.cantidad_disponible,
            'stock_minimo': producto.stock_minimo,
            'stock_maximo': 0,  # Este campo no está en el modelo, pero se usa en la plantilla
            'unidad_medida': 'unidades'  # Por defecto, si no hay unidad de medida específica
        }
        return JsonResponse(data)
    except ProductoInventario.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)

# Vistas para Categorías de Productos
@login_required
def lista_categorias(request):
    """Vista para listar todas las categorías de productos"""
    # Modificación: Recuperar todas las categorías inicialmente sin filtrar por propietario
    # Esto garantiza que veamos todas las categorías en el sistema
    categorias = CategoriaProducto.objects.all().order_by('nombre_categoria')
    
    return render(request, 'inventario/categoria_list.html', {
        'categorias': categorias,
        'titulo': 'Categorías de Productos'
    })

@login_required
def crear_categoria(request):
    """Vista para crear una nueva categoría de producto"""
    if request.method == 'POST':
        form = CategoriaProductoForm(request.POST, user=request.user)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.propietario = request.user  # Asegurarse de que el propietario sea el usuario actual
            
            # Verificar si ya existe una categoría con el mismo nombre para este usuario
            categoria_existente = CategoriaProducto.objects.filter(
                nombre_categoria=categoria.nombre_categoria,
                propietario=request.user
            ).first()
            
            if categoria_existente:
                messages.warning(request, f'Ya existe una categoría llamada "{categoria.nombre_categoria}" en tu inventario.')
                return redirect('inventario:lista_categorias')
            
            categoria.save()
            messages.success(request, 'Categoría creada correctamente.')
            return redirect('inventario:lista_categorias')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en el campo {field}: {error}')
    else:
        form = CategoriaProductoForm(user=request.user)
    
    return render(request, 'inventario/categoria_form.html', {
        'form': form,
        'titulo': 'Crear Nueva Categoría de Producto'
    })

@login_required
def editar_categoria(request, pk):
    """Vista para editar una categoría existente"""
    categoria = get_object_or_404(CategoriaProducto, pk=pk)
    
    # Verificar que la categoría pertenezca al usuario actual o no tenga propietario
    if categoria.propietario and categoria.propietario != request.user:
        messages.error(request, "No tienes permisos para editar esta categoría.")
        return redirect('inventario:lista_categorias')
    
    # Si la categoría no tiene propietario, asignarla al usuario actual
    if not categoria.propietario:
        categoria.propietario = request.user
        categoria.save()
        messages.info(request, "Esta categoría no tenía propietario y se ha asignado a tu cuenta.")
    
    if request.method == 'POST':
        form = CategoriaProductoForm(request.POST, instance=categoria, user=request.user)
        if form.is_valid():
            categoria_actualizada = form.save(commit=False)
            categoria_actualizada.propietario = request.user  # Asegurar que el propietario siga siendo el usuario actual
            
            # Verificar si el nuevo nombre ya existe en otra categoría del usuario
            if categoria_actualizada.nombre_categoria != categoria.nombre_categoria:
                categoria_existente = CategoriaProducto.objects.filter(
                    nombre_categoria=categoria_actualizada.nombre_categoria,
                    propietario=request.user
                ).exclude(id=categoria.id).first()
                
                if categoria_existente:
                    messages.warning(request, f'Ya existe una categoría llamada "{categoria_actualizada.nombre_categoria}" en tu inventario.')
                    return redirect('inventario:editar_categoria', pk=categoria.pk)
            
            categoria_actualizada.save()
            messages.success(request, 'Categoría actualizada correctamente.')
            return redirect('inventario:lista_categorias')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en el campo {field}: {error}')
    else:
        form = CategoriaProductoForm(instance=categoria, user=request.user)
    
    return render(request, 'inventario/categoria_form.html', {
        'form': form,
        'titulo': 'Editar Categoría',
        'categoria': categoria
    })

@login_required
def eliminar_categoria(request, pk):
    """Vista para eliminar una categorÃ­a"""
    categoria = get_object_or_404(CategoriaProducto, pk=pk)
    
    if request.method == 'POST':
        try:
            categoria.delete()
            messages.success(request, 'CategorÃ­a eliminada correctamente.')
            return redirect('inventario:lista_categorias')
        except ProtectedError:
            messages.error(request, 'No se puede eliminar esta categorÃ­a porque estÃ¡ en uso.')
            return redirect('inventario:lista_categorias')
    
    return render(request, 'inventario/categoria_confirm_delete.html', {
        'categoria': categoria,
        'titulo': 'Eliminar CategorÃ­a'
    })

# Vistas para Estados de Productos
@login_required
def lista_estados(request):
    """Vista para listar todos los estados de productos"""
    estados = EstadoProducto.objects.all().order_by('nombre_estado')
    return render(request, 'inventario/estado_list.html', {
        'estados': estados,
        'titulo': 'Estados de Productos'
    })

@login_required
def crear_estado(request):
    """Vista para crear un nuevo estado de producto"""
    if request.method == 'POST':
        form = EstadoProductoForm(request.POST)
        if form.is_valid():
            estado = form.save()
            messages.success(request, 'Estado creado correctamente.')
            return redirect('inventario:lista_estados')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = EstadoProductoForm()
    
    return render(request, 'inventario/estado_form.html', {
        'form': form,
        'titulo': 'Crear Nuevo Estado de Producto'
    })

@login_required
def editar_estado(request, pk):
    """Vista para editar un estado existente"""
    estado = get_object_or_404(EstadoProducto, pk=pk)
    
    if request.method == 'POST':
        form = EstadoProductoForm(request.POST, instance=estado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estado actualizado correctamente.')
            return redirect('inventario:lista_estados')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = EstadoProductoForm(instance=estado)
    
    return render(request, 'inventario/estado_form.html', {
        'form': form,
        'titulo': 'Editar Estado',
        'estado': estado
    })

@login_required
def eliminar_estado(request, pk):
    """Vista para eliminar un estado"""
    estado = get_object_or_404(EstadoProducto, pk=pk)
    
    if request.method == 'POST':
        try:
            estado.delete()
            messages.success(request, 'Estado eliminado correctamente.')
            return redirect('inventario:lista_estados')
        except ProtectedError:
            messages.error(request, 'No se puede eliminar este estado porque estÃ¡ en uso.')
            return redirect('inventario:lista_estados')
    
    return render(request, 'inventario/estado_confirm_delete.html', {
        'estado': estado,
        'titulo': 'Eliminar Estado'
    })

# Vistas de API para crear categorías y estados mediante AJAX
@login_required
def api_crear_categoria(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre_categoria')
        descripcion = data.get('descripcion', '')
        categoria_padre_id = data.get('categoria_padre')
        
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'}, status=400)
        
        categoria_padre = None
        if categoria_padre_id:
            try:
                categoria_padre = CategoriaProducto.objects.get(id=categoria_padre_id)
            except CategoriaProducto.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Categoría padre no encontrada'}, status=404)
        
        # Comprobamos primero si ya existe una categoría con el mismo nombre para evitar duplicados
        categoria_existente = CategoriaProducto.objects.filter(nombre_categoria=nombre).first()
        if categoria_existente:
            # Si existe, la devolvemos en lugar de crear una nueva
            return JsonResponse({
                'success': True,
                'mensaje': 'Se utilizó una categoría existente',
                'categoria': {
                    'id': categoria_existente.id,
                    'nombre': categoria_existente.nombre_categoria
                }
            })
        
        # Si no existe, creamos una nueva
        categoria = CategoriaProducto.objects.create(
            nombre_categoria=nombre,
            descripcion=descripcion,
            categoria_padre=categoria_padre,
            propietario=request.user  # Asignar el usuario actual como propietario
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Categoría creada correctamente',
            'categoria': {
                'id': categoria.id,
                'nombre': categoria.nombre_categoria
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def api_crear_estado(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre_estado')
        
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'}, status=400)
        
        estado = EstadoProducto.objects.create(nombre_estado=nombre)
        
        return JsonResponse({
            'success': True,
            'estado': {
                'id': estado.id,
                'nombre': estado.nombre_estado
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def editar_producto_pedido(request, pedido_id):
    """Vista para editar un producto existente en un pedido a proveedor"""
    pedido = get_object_or_404(PedidoProveedor, pk=pedido_id)
    
    # Verificar que el pedido pertenezca al usuario
    if pedido.propietario and pedido.propietario != request.user:
        messages.error(request, "No tienes permisos para modificar este pedido.")
        return redirect('inventario:lista_pedidos')
    
    # Si el pedido no tiene propietario, asignar el usuario actual
    if not pedido.propietario:
        pedido.propietario = request.user
        pedido.save()
        messages.info(request, "Este pedido no tenía propietario y se ha asignado a tu cuenta.")
    
    detalle_id = request.GET.get('detalle_id')
    
    if not detalle_id:
        messages.error(request, "Detalle de pedido no especificado.")
        return redirect('inventario:detalle_pedido', pk=pedido_id)
    
    detalle = get_object_or_404(DetallePedidoProveedor, pk=detalle_id, pedido_proveedor=pedido)
    
    if request.method == 'POST':
        form = DetallePedidoProveedorForm(request.POST, instance=detalle)
        if form.is_valid():
            detalle_actualizado = form.save(commit=False)
            detalle_actualizado.subtotal = detalle_actualizado.cantidad * detalle_actualizado.precio_unitario
            detalle_actualizado.save()
            messages.success(request, 'Producto actualizado en el pedido con éxito.')
            return redirect('inventario:detalle_pedido', pk=pedido_id)
    else:
        form = DetallePedidoProveedorForm(instance=detalle)
    
    context = {
        'form': form,
        'titulo': f'Editar Producto en Pedido #{pedido.id}',
        'pedido': pedido,
        'detalle': detalle,
    }
    
    return render(request, 'inventario/pedidos/editar_producto_form.html', context)

@login_required
def agregar_producto_pedido(request, pedido_id):
    """Vista para agregar un producto a un pedido existente"""
    pedido = get_object_or_404(PedidoProveedor, pk=pedido_id)
    
    # Verificar que el pedido pertenezca al usuario
    if pedido.propietario and pedido.propietario != request.user:
        messages.error(request, "No tienes permisos para modificar este pedido.")
        return redirect('inventario:lista_pedidos')
    
    # Si el pedido no tiene propietario, asignar el usuario actual
    if not pedido.propietario:
        pedido.propietario = request.user
        pedido.save()
        messages.info(request, "Este pedido no tenía propietario y se ha asignado a tu cuenta.")
    
    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        cantidad = request.POST.get('cantidad')
        precio_unitario = request.POST.get('precio_unitario')
        
        if producto_id and cantidad and precio_unitario:
            producto = get_object_or_404(ProductoInventario, pk=producto_id)
            
            # Crear el detalle del pedido
            detalle = DetallePedidoProveedor(
                pedido_proveedor=pedido,
                producto_inventario=producto,
                cantidad=int(cantidad),
                precio_unitario=float(precio_unitario),
                subtotal=int(cantidad) * float(precio_unitario)
            )
            detalle.save()
            
            messages.success(request, 'Producto agregado al pedido con éxito.')
        else:
            messages.error(request, 'Por favor complete todos los campos requeridos.')
            
        return redirect('inventario:editar_pedido', pk=pedido_id)
    
    # Este método solo acepta POST, así que redirigir si es GET
    return redirect('inventario:editar_pedido', pk=pedido_id)

# Vistas para gestión de imágenes de productos
@login_required
def gestionar_imagenes(request, producto_id):
    """Vista para gestionar las imágenes de un producto"""
    producto = get_object_or_404(ProductoInventario, pk=producto_id)
    
    # Verificar que el producto pertenezca al usuario
    if producto.propietario and producto.propietario != request.user:
        messages.error(request, "No tienes permisos para gestionar las imágenes de este producto.")
        return redirect('inventario:lista_productos')
    
    # Obtener todas las imágenes del producto
    imagenes = ImagenProducto.objects.filter(producto=producto).order_by('-es_principal', '-fecha_creacion')
    
    context = {
        'producto': producto,
        'imagenes': imagenes,
        'titulo': f'Gestionar imágenes de {producto.nombre_producto}'
    }
    return render(request, 'inventario/imagenes/gestionar_imagenes.html', context)

@login_required
def subir_imagen(request, producto_id):
    """Vista para subir una nueva imagen para un producto"""
    producto = get_object_or_404(ProductoInventario, pk=producto_id)
    
    # Verificar que el producto pertenezca al usuario
    if producto.propietario and producto.propietario != request.user:
        messages.error(request, "No tienes permisos para añadir imágenes a este producto.")
        return redirect('inventario:lista_productos')
    
    if request.method == 'POST':
        form = ImagenProductoForm(request.POST, request.FILES)
        if form.is_valid():
            imagen = form.save(commit=False)
            imagen.producto = producto
            
            # Si no hay otras imágenes, marcar esta como principal
            if not ImagenProducto.objects.filter(producto=producto).exists():
                imagen.es_principal = True
            
            imagen.save()
            messages.success(request, 'Imagen subida correctamente.')
            return redirect('inventario:gestionar_imagenes', producto_id=producto.id)
    else:
        form = ImagenProductoForm()
    
    context = {
        'form': form,
        'producto': producto,
        'titulo': f'Subir imagen para {producto.nombre_producto}'
    }
    return render(request, 'inventario/imagenes/subir_imagen.html', context)

@login_required
def eliminar_imagen(request, imagen_id):
    """Vista para eliminar una imagen de un producto"""
    imagen = get_object_or_404(ImagenProducto, pk=imagen_id)
    producto = imagen.producto
    
    # Verificar que el producto pertenezca al usuario
    if producto.propietario and producto.propietario != request.user:
        messages.error(request, "No tienes permisos para eliminar imágenes de este producto.")
        return redirect('inventario:lista_productos')
    
    # Verificar si es la imagen principal
    es_principal = imagen.es_principal
    
    if request.method == 'POST':
        # Si es la única imagen, simplemente eliminarla
        otras_imagenes = ImagenProducto.objects.filter(producto=producto).exclude(id=imagen_id).exists()
        
        # Si es la imagen principal y hay otras imágenes, establecer otra como principal
        if es_principal and otras_imagenes:
            # Obtener la siguiente imagen más reciente
            siguiente_imagen = ImagenProducto.objects.filter(
                producto=producto
            ).exclude(id=imagen_id).order_by('-fecha_creacion').first()
            
            if siguiente_imagen:
                siguiente_imagen.es_principal = True
                siguiente_imagen.save()
        
        # Eliminar la imagen
        imagen.delete()
        messages.success(request, 'Imagen eliminada correctamente.')
        return redirect('inventario:gestionar_imagenes', producto_id=producto.id)
    
    context = {
        'imagen': imagen,
        'producto': producto,
        'es_principal': es_principal,
        'titulo': 'Confirmar eliminación de imagen'
    }
    return render(request, 'inventario/imagenes/confirmar_eliminar.html', context)

@login_required
def marcar_como_principal(request, imagen_id):
    """Vista para marcar una imagen como la principal del producto"""
    imagen = get_object_or_404(ImagenProducto, pk=imagen_id)
    producto = imagen.producto
    
    # Verificar que el producto pertenezca al usuario
    if producto.propietario and producto.propietario != request.user:
        messages.error(request, "No tienes permisos para modificar imágenes de este producto.")
        return redirect('inventario:lista_productos')
    
    # Desmarcar todas las imágenes principales del producto
    ImagenProducto.objects.filter(producto=producto, es_principal=True).update(es_principal=False)
    
    # Marcar esta imagen como principal
    imagen.es_principal = True
    imagen.save()
    
    messages.success(request, 'Imagen establecida como principal.')
    return redirect('inventario:gestionar_imagenes', producto_id=producto.id)

@login_required
def subir_imagenes_multiples(request, producto_id):
    """Vista para subir múltiples imágenes de un producto"""
    producto = get_object_or_404(ProductoInventario, pk=producto_id)
    
    # Verificar que el producto pertenezca al usuario
    if producto.propietario and producto.propietario != request.user:
        messages.error(request, "No tienes permisos para añadir imágenes a este producto.")
        return redirect('inventario:lista_productos')
    
    # Comprobar si hay imágenes
    hay_imagenes = ImagenProducto.objects.filter(producto=producto).exists()
    
    if request.method == 'POST':
        if 'imagenes' in request.FILES:
            # Verificar si ya hay imágenes para el producto
            es_primera_imagen = not hay_imagenes
            
            # Procesar el archivo subido
            imagen_file = request.FILES['imagenes']
            nueva_imagen = ImagenProducto(
                producto=producto,
                imagen=imagen_file,
                es_principal=es_primera_imagen
            )
            nueva_imagen.save()
            
            messages.success(request, 'Imagen subida correctamente.')
        else:
            messages.warning(request, 'No se seleccionó ninguna imagen.')
            
        return redirect('inventario:gestionar_imagenes', producto_id=producto.id)
    
    context = {
        'producto': producto,
        'titulo': f'Subir múltiples imágenes para {producto.nombre_producto}'
    }
    return render(request, 'inventario/imagenes/subir_imagenes_multiples.html', context)

# Herramienta de diagnóstico y reparación
@login_required
def diagnostico_inventario(request):
    """
    Vista para diagnosticar y reparar problemas en el módulo de inventario,
    específicamente con los propietarios de productos y categorías.
    """
    productos_sin_propietario = verificar_productos_sin_propietario()
    categorias_sin_propietario = verificar_categorias_sin_propietario()
    
    # También contamos los productos propios del usuario
    productos_propios = ProductoInventario.objects.filter(propietario=request.user).count()
    
    # Información para el diagnóstico
    diagnostico_info = {
        'productos_sin_propietario': productos_sin_propietario.count(),
        'categorias_sin_propietario': categorias_sin_propietario.count(),
        'total_productos': ProductoInventario.objects.count(),
        'total_categorias': CategoriaProducto.objects.count(),
        'productos_propios': productos_propios
    }
    
    # Si se solicita reparación
    if request.method == 'POST' and 'reparar' in request.POST:
        try:
            productos_reparados, categorias_reparadas = reparar_propiedades_inventario(request.user)
            
            # También reparamos productos específicos del usuario
            productos_usuario_corregidos = verificar_y_corregir_productos_usuario(request.user)
            
            total_productos_reparados = productos_reparados + productos_usuario_corregidos
            
            messages.success(
                request, 
                f'Reparación completada: {total_productos_reparados} productos y {categorias_reparadas} categorías asignadas a tu usuario.'
            )
        except Exception as e:
            messages.error(request, f'Error durante la reparación: {str(e)}')
            
        return redirect('inventario:diagnostico_inventario')
    
    return render(request, 'inventario/diagnostico.html', {
        'diagnostico': diagnostico_info,
        'titulo': 'Diagnóstico del Sistema de Inventario'
    })

@login_required
def recibir_pedido(request, pk):
    pedido = get_object_or_404(PedidoProveedor, pk=pk)
    
    # Verificar que el pedido pertenezca al usuario
    if pedido.propietario and pedido.propietario != request.user:
        messages.error(request, "No tienes permisos para recibir este pedido.")
        return redirect('inventario:lista_pedidos')
    
    # Si el pedido no tiene propietario, asignar el usuario actual
    if not pedido.propietario:
        pedido.propietario = request.user
        pedido.save()
        messages.info(request, "Este pedido no tenía propietario y se ha asignado a tu cuenta.")
    
    if pedido.estado_pedido not in ['PENDIENTE', 'PARCIAL']:
        messages.error(request, f"No se puede recibir un pedido en estado {pedido.get_estado_pedido_display()}")
        return redirect('inventario:detalle_pedido', pk=pedido.pk)
    
    # Obtener detalles del pedido
    detalles = DetallePedidoProveedor.objects.filter(pedido_proveedor=pedido)
    
    if request.method == 'POST':
        form = RecepcionPedidoForm(request.POST)
        if form.is_valid():
            # Actualizar estado del pedido
            todos_recibidos = True
            
            for detalle in detalles:
                cantidad_recibida = int(request.POST.get(f'cantidad_recibida_{detalle.id}', 0))
                if cantidad_recibida > 0:
                    if cantidad_recibida > detalle.cantidad - detalle.cantidad_recibida:
                        cantidad_recibida = detalle.cantidad - detalle.cantidad_recibida
                    
                    # Actualizar cantidad recibida
                    detalle.cantidad_recibida += cantidad_recibida
                    detalle.save()
                    
                    # Actualizar inventario
                    if detalle.producto_inventario:
                        detalle.producto_inventario.cantidad_disponible += cantidad_recibida
                        detalle.producto_inventario.save()
                        
                        # Registrar movimiento
                        MovimientoInventario.objects.create(
                            producto_inventario=detalle.producto_inventario,
                            tipo_movimiento='ENTRADA',
                            cantidad=cantidad_recibida,
                            referencia=f'Recepción de pedido #{pedido.id}',
                            usuario=request.user
                        )
                
                # Verificar si todos los productos se recibieron completamente
                if detalle.cantidad_recibida < detalle.cantidad:
                    todos_recibidos = False
            
            # Actualizar estado del pedido
            if todos_recibidos:
                pedido.estado_pedido = 'RECIBIDO'
            else:
                pedido.estado_pedido = 'PARCIAL'
            
            pedido.fecha_recepcion = timezone.now().date()
            pedido.save()
            
            messages.success(request, 'Recepción de productos registrada con éxito.')
            return redirect('inventario:detalle_pedido', pk=pedido.pk)
    else:
        form = RecepcionPedidoForm()
    
    context = {
        'pedido': pedido,
        'detalles': detalles,
        'form': form
    }
    return render(request, 'inventario/recibir_pedido.html', context)

@login_required
def cancelar_pedido(request, pk):
    pedido = get_object_or_404(PedidoProveedor, pk=pk)
    
    # Verificar que el pedido pertenezca al usuario
    if pedido.propietario and pedido.propietario != request.user:
        messages.error(request, "No tienes permisos para cancelar este pedido.")
        return redirect('inventario:lista_pedidos')
    
    # Si el pedido no tiene propietario, asignar el usuario actual
    if not pedido.propietario:
        pedido.propietario = request.user
        pedido.save()
        messages.info(request, "Este pedido no tenía propietario y se ha asignado a tu cuenta.")
    
    if pedido.estado_pedido != 'PENDIENTE':
        messages.error(request, f"No se puede cancelar un pedido en estado {pedido.get_estado_pedido_display()}")
        return redirect('inventario:detalle_pedido', pk=pedido.pk)
    
    # Cancelar el pedido
    pedido.estado_pedido = 'CANCELADO'
    pedido.save()
    
    messages.success(request, f'Pedido #{pedido.id} cancelado con éxito.')
    return redirect('inventario:lista_pedidos')

@login_required
def asignar_propietario_pedidos(request):
    """Asigna el usuario actual como propietario a todos los pedidos sin propietario."""
    if request.method == 'POST':
        # Contar pedidos sin propietario
        pedidos_sin_propietario = PedidoProveedor.objects.filter(propietario__isnull=True)
        cantidad = pedidos_sin_propietario.count()
        
        # Asignar el propietario
        pedidos_sin_propietario.update(propietario=request.user)
        
        messages.success(request, f"Se han asignado {cantidad} pedidos a tu cuenta.")
        return redirect('inventario:lista_pedidos')
    
    # Si es GET, mostrar confirmación
    pedidos_sin_propietario = PedidoProveedor.objects.filter(propietario__isnull=True)
    cantidad = pedidos_sin_propietario.count()
    
    context = {
        'cantidad': cantidad,
        'pedidos': pedidos_sin_propietario
    }
    return render(request, 'inventario/asignar_propietario_pedidos.html', context)

@login_required
def asignar_propietario_proveedores(request):
    """Asigna el usuario actual como propietario a todos los proveedores sin propietario."""
    if request.method == 'POST':
        # Contar proveedores sin propietario
        proveedores_sin_propietario = Proveedor.objects.filter(propietario__isnull=True)
        cantidad = proveedores_sin_propietario.count()
        
        # Asignar el propietario
        proveedores_sin_propietario.update(propietario=request.user)
        
        messages.success(request, f"Se han asignado {cantidad} proveedores a tu cuenta.")
        return redirect('inventario:lista_proveedores')
    
    # Si es GET, mostrar confirmación
    proveedores_sin_propietario = Proveedor.objects.filter(propietario__isnull=True)
    cantidad = proveedores_sin_propietario.count()
    
    context = {
        'cantidad': cantidad,
        'proveedores': proveedores_sin_propietario
    }
    return render(request, 'inventario/asignar_propietario_proveedores.html', context)

@login_required
def asignar_propietario_almacenes(request):
    """Asigna el usuario actual como propietario a todos los almacenes sin propietario."""
    if request.method == 'POST':
        # Contar almacenes sin propietario
        almacenes_sin_propietario = Almacen.objects.filter(propietario__isnull=True)
        cantidad = almacenes_sin_propietario.count()
        
        # Asignar el propietario
        almacenes_sin_propietario.update(propietario=request.user)
        
        messages.success(request, f"Se han asignado {cantidad} almacenes a tu cuenta.")
        return redirect('inventario:lista_almacenes')
    
    # Si es GET, mostrar confirmación
    almacenes_sin_propietario = Almacen.objects.filter(propietario__isnull=True)
    cantidad = almacenes_sin_propietario.count()
    
    context = {
        'cantidad': cantidad,
        'almacenes': almacenes_sin_propietario
    }
    return render(request, 'inventario/asignar_propietario_almacenes.html', context)

# Vistas para Notificaciones
@login_required
def lista_notificaciones(request):
    """Vista para ver todas las notificaciones del usuario"""
    # Obtener notificaciones del usuario actual
    notificaciones = Notificacion.objects.filter(usuario=request.user)
    
    # Filtrado por tipo
    tipo = request.GET.get('tipo', '')
    if tipo:
        notificaciones = notificaciones.filter(tipo=tipo)
    
    # Filtrado por leídas/no leídas
    estado = request.GET.get('estado', '')
    if estado == 'leidas':
        notificaciones = notificaciones.filter(leida=True)
    elif estado == 'no_leidas':
        notificaciones = notificaciones.filter(leida=False)
    
    # Paginación
    paginator = Paginator(notificaciones, 15)  # 15 notificaciones por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Contar notificaciones no leídas
    no_leidas_count = Notificacion.objects.filter(usuario=request.user, leida=False).count()
    
    context = {
        'page_obj': page_obj,
        'tipo_seleccionado': tipo,
        'estado_seleccionado': estado,
        'no_leidas_count': no_leidas_count,
        'tipos_notificacion': Notificacion.TIPO_CHOICES,
    }
    return render(request, 'inventario/notificaciones/lista.html', context)

@login_required
def detalle_notificacion(request, pk):
    """Vista para ver el detalle de una notificación y marcarla como leída"""
    notificacion = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    
    # Marcar como leída si no lo está
    if not notificacion.leida:
        notificacion.marcar_como_leida()
    
    context = {
        'notificacion': notificacion
    }
    return render(request, 'inventario/notificaciones/detalle.html', context)

@login_required
def marcar_como_leida(request, pk):
    """Marca una notificación específica como leída"""
    notificacion = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    notificacion.marcar_como_leida()
    
    # Redirigir a la página de detalle o de regreso a la lista
    next_url = request.GET.get('next', 'inventario:lista_notificaciones')
    if next_url == 'detalle':
        return redirect('inventario:detalle_notificacion', pk=notificacion.pk)
    else:
        return redirect('inventario:lista_notificaciones')

@login_required
def marcar_todas_como_leidas(request):
    """Marca todas las notificaciones del usuario como leídas"""
    Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
    messages.success(request, "Todas las notificaciones han sido marcadas como leídas.")
    return redirect('inventario:lista_notificaciones')

@login_required
def eliminar_notificacion(request, pk):
    """Elimina una notificación específica"""
    notificacion = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        notificacion.delete()
        messages.success(request, "La notificación ha sido eliminada.")
        return redirect('inventario:lista_notificaciones')
    
    context = {
        'notificacion': notificacion
    }
    return render(request, 'inventario/notificaciones/confirmar_eliminar.html', context)

@login_required
def eliminar_todas(request):
    """Elimina todas las notificaciones leídas del usuario"""
    if request.method == 'POST':
        count = Notificacion.objects.filter(usuario=request.user, leida=True).count()
        Notificacion.objects.filter(usuario=request.user, leida=True).delete()
        messages.success(request, f"Se han eliminado {count} notificaciones leídas.")
        return redirect('inventario:lista_notificaciones')
    
    return render(request, 'inventario/notificaciones/confirmar_eliminar_todas.html')

@login_required
def obtener_contador_notificaciones(request):
    """Vista API para obtener el contador de notificaciones no leídas"""
    count = Notificacion.objects.filter(usuario=request.user, leida=False).count()
    return JsonResponse({'count': count})

@login_required
def obtener_notificaciones_recientes(request):
    """Vista API para obtener las notificaciones recientes del usuario"""
    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:10]
    
    data = []
    for notif in notificaciones:
        tipo_display = dict(Notificacion.TIPO_CHOICES).get(notif.tipo, '')
        nivel_display = dict(Notificacion.NIVEL_CHOICES).get(notif.nivel, '')
        
        data.append({
            'id': notif.id,
            'titulo': notif.titulo,
            'mensaje': notif.mensaje,
            'nivel': notif.nivel,
            'nivel_display': nivel_display,
            'tipo': notif.tipo,
            'tipo_display': tipo_display,
            'fecha_creacion': notif.fecha_creacion.isoformat(),
            'leida': notif.leida,
            'enlace': notif.enlace
        })
    
    return JsonResponse(data, safe=False)

@login_required
def marcar_notificacion_leida(request, notificacion_id):
    """Vista para marcar una notificación como leída mediante AJAX"""
    try:
        notificacion = Notificacion.objects.get(id=notificacion_id, usuario=request.user)
        notificacion.leida = True
        notificacion.save()
        return JsonResponse({'success': True})
    except Notificacion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notificación no encontrada'}, status=404)

@login_required
def generar_notificacion_prueba(request):
    """
    Vista para generar notificaciones de prueba para el usuario actual.
    Útil para desarrollo y demostración.
    """
    from .utils import enviar_notificacion_usuario
    from django.utils.crypto import get_random_string
    
    if request.method == 'POST':
        tipo = request.POST.get('tipo', 'SISTEMA')
        nivel = request.POST.get('nivel', 'INFO')
        
        # Generar título y mensaje aleatorios
        titulo = f"Notificación de prueba - {tipo} ({get_random_string(4)})"
        mensaje = f"Esta es una notificación de prueba de nivel {nivel} generada el {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}. Tipo: {tipo}."
        
        # Crear la notificación
        notificacion = enviar_notificacion_usuario(
            usuario=request.user,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            nivel=nivel,
            enlace=request.POST.get('enlace', reverse('inventario:dashboard'))
        )
        
        messages.success(request, f"Notificación de prueba creada: {titulo}")
        
        # Redirigir a la lista de notificaciones o de vuelta a la página de generación
        return redirect('inventario:lista_notificaciones')
    
    # Mostrar el formulario para generar notificaciones
    context = {
        'tipos_notificacion': Notificacion.TIPO_CHOICES,
        'niveles_notificacion': Notificacion.NIVEL_CHOICES,
    }
    return render(request, 'inventario/notificaciones/generar_prueba.html', context)
