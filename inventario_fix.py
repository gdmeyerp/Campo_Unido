"""
Modificaciones necesarias para asegurar que los productos y movimientos 
se asocien correctamente al usuario actual.

PASO 1: Actualizar ProductoInventarioForm para incluir propietario como campo oculto

Archivo: apps/inventario/forms.py
Clase: ProductoInventarioForm

class ProductoInventarioForm(forms.ModelForm):
    class Meta:
        model = ProductoInventario
        fields = [
            'nombre_producto', 'descripcion_producto', 'categoria_producto',
            'cantidad_disponible', 'stock_minimo', 'precio_compra',
            'precio_venta', 'estado_producto', 'propietario'
        ]
        widgets = {
            'descripcion_producto': forms.Textarea(attrs={'rows': 3}),
            'propietario': forms.HiddenInput(),  # Campo oculto
        }

PASO 2: Modificar crear_producto para asignar el usuario actual

Archivo: apps/inventario/views.py
Función: crear_producto

@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoInventarioForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.propietario = request.user  # Asignar el usuario actual como propietario
            producto.save()
            messages.success(request, f'Producto "{producto.nombre_producto}" creado exitosamente.')
            return redirect('inventario:detalle_producto', pk=producto.id)
    else:
        form = ProductoInventarioForm(initial={'propietario': request.user})  # Preseleccionar el usuario actual
    
    # Obtener categorías para el modal de creación rápida
    categorias = CategoriaProducto.objects.all().order_by('nombre_categoria')
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Producto',
        'categorias': categorias
    }
    
    return render(request, 'inventario/producto_form.html', context)

PASO 3: Modificar editar_producto para verificar y preservar propietario

@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(ProductoInventario, pk=pk)
    
    # Verificar que el propietario coincide con el usuario actual o asignar propietario si no tiene
    if not producto.propietario:
        producto.propietario = request.user
        producto.save()
    elif producto.propietario != request.user:
        messages.error(request, "No tienes permisos para editar este producto.")
        return redirect('inventario:lista_productos')
    
    if request.method == 'POST':
        form = ProductoInventarioForm(request.POST, instance=producto)
        if form.is_valid():
            producto_actualizado = form.save(commit=False)
            # Asegurar que no se cambie el propietario
            producto_actualizado.propietario = request.user
            producto_actualizado.save()
            messages.success(request, f'Producto "{producto_actualizado.nombre_producto}" actualizado exitosamente.')
            return redirect('inventario:detalle_producto', pk=producto_actualizado.id)
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

PASO 4: Modificar lista_movimientos para filtrar por propietario

@login_required
def lista_movimientos(request):
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    
    # Filtrar por productos que pertenecen al usuario actual
    movimientos = MovimientoInventario.objects.filter(
        producto_inventario__propietario=request.user
    )
    
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

PASO 5: Modificar registrar_movimiento para verificar propietario y limitar productos

@login_required
def registrar_movimiento(request):
    if request.method == 'POST':
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            
            # Verificar que el producto pertenece al usuario actual
            if movimiento.producto_inventario.propietario != request.user:
                messages.error(request, "No puedes realizar movimientos en productos que no te pertenecen.")
                return redirect('inventario:lista_movimientos')
                
            movimiento.usuario = request.user
            movimiento.save()
            
            messages.success(request, 'Movimiento de inventario registrado con éxito.')
            return redirect('inventario:lista_movimientos')
    else:
        # Prellenar el formulario si se pasan parámetros en la URL
        initial_data = {}
        if request.GET.get('producto'):
            try:
                producto = ProductoInventario.objects.get(id=request.GET.get('producto'))
                # Verificar que el producto pertenezca al usuario actual
                if producto.propietario == request.user:
                    initial_data['producto_inventario'] = producto
            except ProductoInventario.DoesNotExist:
                pass
                
        if request.GET.get('tipo'):
            initial_data['tipo_movimiento'] = request.GET.get('tipo')
            
        # Limitar las opciones de productos a solo los del usuario actual
        form = MovimientoInventarioForm(initial=initial_data)
        form.fields['producto_inventario'].queryset = ProductoInventario.objects.filter(propietario=request.user)
    
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

"""
Script para filtrar productos por propietario en varias vistas.
Ejecutar con: python manage.py shell < inventario_fix.py
"""

from django.db.models import Q, F, Sum, Count
from apps.inventario.models import ProductoInventario, CategoriaProducto
from apps.inventario.views import lista_productos, dashboard_inventario, detalle_producto, editar_producto, eliminar_producto, registrar_movimiento

# Función personalizada para aplicar parches a las vistas
def apply_patches():
    # 1. Modificar dashboard_inventario
    def patched_dashboard_inventario(request):
        from django.contrib.auth.decorators import login_required
        from django.shortcuts import render
        from django.db.models import Sum, Count, Q, F
        from django.utils import timezone
        from datetime import timedelta
        from apps.inventario.models import ProductoInventario, MovimientoInventario, AlertaStock, PedidoProveedor, CategoriaProducto
        
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
            estado_pedido__in=['PENDIENTE', 'EN_TRANSITO']
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
    
    # 2. Modificar detalle_producto, editar_producto y eliminar_producto
    from apps.inventario.views import detalle_producto, editar_producto, eliminar_producto, registrar_movimiento
    from django.contrib import messages
    from django.shortcuts import redirect, get_object_or_404
    
    # Aplicar los parches
    # Esta parte se ejecutaría manualmente en el shell
    print("Parches generados. Copiar las funciones a views.py")

if __name__ == "__main__":
    apply_patches() 