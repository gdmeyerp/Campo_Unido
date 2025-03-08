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
    AlertaStock, ReservaInventario
)
from .forms import (
    CategoriaProductoForm, EstadoProductoForm, UnidadMedidaForm, ProductoInventarioForm,
    MovimientoInventarioForm, ProveedorForm, PedidoProveedorForm, DetallePedidoProveedorForm,
    AlmacenForm, UbicacionAlmacenForm, InventarioAlmacenForm, CaducidadProductoForm,
    AlertaStockForm, ReservaInventarioForm
)

# Dashboard de Inventario
@login_required
def dashboard_inventario(request):
    # Estadísticas generales
    total_productos = ProductoInventario.objects.count()
    productos_stock_bajo = ProductoInventario.objects.filter(
        cantidad_disponible__lte=F('stock_minimo')
    ).count()
    
    # Lista de productos con stock bajo para mostrar detalles
    productos_bajo_stock = ProductoInventario.objects.filter(
        cantidad_disponible__lte=F('stock_minimo')
    ).order_by('cantidad_disponible')[:10]
    
    # Productos más vendidos (últimos 30 días)
    fecha_inicio = timezone.now() - timedelta(days=30)
    movimientos_salida = MovimientoInventario.objects.filter(
        tipo_movimiento='SALIDA',
        fecha_movimiento__gte=fecha_inicio
    ).values('producto_inventario').annotate(
        total_vendido=Sum('cantidad_movimiento')
    ).order_by('-total_vendido')[:5]
    
    productos_mas_vendidos = []
    for movimiento in movimientos_salida:
        producto = ProductoInventario.objects.get(id=movimiento['producto_inventario'])
        productos_mas_vendidos.append({
            'producto': producto,
            'total_vendido': movimiento['total_vendido']
        })
    
    # Alertas recientes
    alertas_recientes = AlertaStock.objects.all().order_by('-fecha_alerta')[:10]
    
    # Movimientos recientes
    movimientos_recientes = MovimientoInventario.objects.all().order_by('-fecha_movimiento')[:5]
    
    # Pedidos pendientes
    pedidos_pendientes = PedidoProveedor.objects.filter(
        estado_pedido__in=['PENDIENTE', 'EN_TRANSITO']
    ).order_by('fecha_entrega')[:5]
    
    # Productos por categoría para gráfica
    productos_por_categoria = CategoriaProducto.objects.annotate(
        cantidad_productos=Count('productoinventario')
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
    categorias = CategoriaProducto.objects.all()
    estados = EstadoProducto.objects.all()
    
    # Aplicar filtros
    queryset = ProductoInventario.objects.all().order_by('nombre_producto')
    
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
        form = ProductoInventarioForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre_producto}" creado exitosamente.')
            return redirect('inventario:detalle_producto', pk=producto.id)
    else:
        form = ProductoInventarioForm()
    
    # Obtener categorías para el modal de creación rápida
    categorias = CategoriaProducto.objects.all().order_by('nombre_categoria')
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Producto',
        'categorias': categorias
    }
    
    return render(request, 'inventario/producto_form.html', context)

@login_required
def detalle_producto(request, pk):
    producto = get_object_or_404(ProductoInventario, pk=pk)
    
    # Obtener historial de movimientos
    movimientos = MovimientoInventario.objects.filter(
        producto_inventario=producto
    ).order_by('-fecha_movimiento')[:20]  # Limitar a los últimos 20 movimientos
    
    return render(request, 'inventario/detalle_producto.html', {
        'producto': producto,
        'movimientos': movimientos,
    })

@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(ProductoInventario, pk=pk)
    
    if request.method == 'POST':
        form = ProductoInventarioForm(request.POST, instance=producto)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre_producto}" actualizado exitosamente.')
            return redirect('inventario:detalle_producto', pk=producto.id)
    else:
        form = ProductoInventarioForm(instance=producto)
    
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
    
    if request.method == 'POST':
        nombre = producto.nombre_producto
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado con éxito.')
        return redirect('inventario:lista_productos')
    
    context = {
        'producto': producto,
    }
    
    return render(request, 'inventario/productos/confirmar_eliminar.html', context)

# Vistas para Movimientos de Inventario
@login_required
def lista_movimientos(request):
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    
    movimientos = MovimientoInventario.objects.all()
    
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
    tipos_movimiento = MovimientoInventario.objects.values_list(
        'tipo_movimiento', flat=True
    ).distinct()
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'tipos_movimiento': tipos_movimiento,
        'tipo_seleccionado': tipo,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    }
    return render(request, 'inventario/movimiento_list.html', context)

@login_required
def registrar_movimiento(request):
    if request.method == 'POST':
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user
            movimiento.save()
            
            messages.success(request, 'Movimiento de inventario registrado con éxito.')
            return redirect('inventario:lista_movimientos')
    else:
        form = MovimientoInventarioForm()
    
    context = {
        'form': form,
        'titulo': 'Registrar Movimiento de Inventario',
        # Asegurarse de que todos los campos se pasen correctamente al contexto
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
    
    proveedores = Proveedor.objects.all()
    
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
            proveedor = form.save()
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
    
    # Pedidos del proveedor
    pedidos = PedidoProveedor.objects.filter(
        proveedor=proveedor
    ).order_by('-fecha_pedido')
    
    context = {
        'proveedor': proveedor,
        'pedidos': pedidos
    }
    return render(request, 'inventario/proveedor_detail.html', context)

@login_required
def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            proveedor = form.save()
            messages.success(request, f'Proveedor "{proveedor.nombre_proveedor}" actualizado con éxito.')
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
    
    pedidos = PedidoProveedor.objects.all()
    
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
    estados_pedido = PedidoProveedor.objects.values_list(
        'estado_pedido', flat=True
    ).distinct()
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'estados_pedido': estados_pedido,
        'estado_seleccionado': estado
    }
    return render(request, 'inventario/pedido_list.html', context)

@login_required
def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoProveedorForm(request.POST)
        if form.is_valid():
            pedido = form.save()
            messages.success(request, f'Pedido #{pedido.id} creado con éxito.')
            return redirect('inventario:detalle_pedido', pk=pedido.pk)
    else:
        form = PedidoProveedorForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Pedido'
    }
    return render(request, 'inventario/pedido_form.html', context)

@login_required
def detalle_pedido(request, pk):
    pedido = get_object_or_404(PedidoProveedor, pk=pk)
    
    # Detalles del pedido
    detalles = DetallePedidoProveedor.objects.filter(
        pedido_proveedor=pedido
    )
    
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
    }
    return render(request, 'inventario/pedido_detail.html', context)

@login_required
def editar_pedido(request, pk):
    pedido = get_object_or_404(PedidoProveedor, pk=pk)
    
    if request.method == 'POST':
        form = PedidoProveedorForm(request.POST, instance=pedido)
        if form.is_valid():
            pedido = form.save()
            messages.success(request, f'Pedido #{pedido.id} actualizado con éxito.')
            return redirect('inventario:detalle_pedido', pk=pedido.pk)
    else:
        form = PedidoProveedorForm(instance=pedido)
    
    context = {
        'form': form,
        'titulo': f'Editar Pedido #{pedido.id}',
        'pedido': pedido
    }
    return render(request, 'inventario/pedido_form.html', context)

@login_required
def eliminar_detalle_pedido(request, pk):
    detalle = get_object_or_404(DetallePedidoProveedor, pk=pk)
    pedido_id = detalle.pedido_proveedor.id
    
    if request.method == 'POST':
        detalle.delete()
        messages.success(request, 'Producto eliminado del pedido con éxito.')
        return redirect('inventario:detalle_pedido', pk=pedido_id)
    
    context = {
        'detalle': detalle,
        'pedido_id': pedido_id,
    }
    
    return render(request, 'inventario/pedidos/confirmar_eliminar_detalle.html', context)

# Vistas para Almacenes
@login_required
def lista_almacenes(request):
    almacenes = Almacen.objects.all().order_by('nombre_almacen')
    
    context = {
        'almacenes': almacenes,
    }
    
    return render(request, 'inventario/almacenes/lista.html', context)

@login_required
def crear_almacen(request):
    if request.method == 'POST':
        form = AlmacenForm(request.POST)
        if form.is_valid():
            almacen = form.save()
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
        form = InventarioAlmacenForm(request.POST)
        if form.is_valid():
            inventario = form.save(commit=False)
            inventario.ubicacion_almacen = ubicacion
            
            # Verificar si ya existe el producto en esta ubicación
            existente = InventarioAlmacen.objects.filter(
                producto_inventario=inventario.producto_inventario,
                ubicacion_almacen=ubicacion
            ).first()
            
            if existente:
                existente.cantidad_disponible += inventario.cantidad_disponible
                existente.save()
                messages.success(request, f'Cantidad actualizada para {inventario.producto_inventario.nombre_producto}.')
            else:
                inventario.save()
                messages.success(request, f'Producto {inventario.producto_inventario.nombre_producto} asignado a la ubicación.')
            
            return redirect('inventario:detalle_almacen', pk=ubicacion.almacen.pk)
    else:
        form = InventarioAlmacenForm(initial={'ubicacion_almacen': ubicacion})
    
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
    
    # Obtener datos para el informe
    productos = ProductoInventario.objects.all().select_related(
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
    categorias = CategoriaProducto.objects.all().order_by('nombre_categoria')
    return render(request, 'inventario/categoria_list.html', {
        'categorias': categorias,
        'titulo': 'Categorías de Productos'
    })

@login_required
def crear_categoria(request):
    """Vista para crear una nueva categoría de producto"""
    if request.method == 'POST':
        form = CategoriaProductoForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, 'Categoría creada correctamente.')
            return redirect('inventario:lista_categorias')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = CategoriaProductoForm()
    
    return render(request, 'inventario/categoria_form.html', {
        'form': form,
        'titulo': 'Crear Nueva Categoría de Producto'
    })

@login_required
def editar_categoria(request, pk):
    """Vista para editar una categoría existente"""
    categoria = get_object_or_404(CategoriaProducto, pk=pk)
    
    if request.method == 'POST':
        form = CategoriaProductoForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada correctamente.')
            return redirect('inventario:lista_categorias')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = CategoriaProductoForm(instance=categoria)
    
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
        
        categoria = CategoriaProducto.objects.create(
            nombre_categoria=nombre,
            descripcion=descripcion,
            categoria_padre=categoria_padre
        )
        
        return JsonResponse({
            'success': True,
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
