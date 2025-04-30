"""
Aquí están las correcciones que debes aplicar manualmente a tus archivos:

1. Agregar la función editar_producto_pedido a views.py:
"""

@login_required
def editar_producto_pedido(request, pedido_id):
    """Vista para editar un producto existente en un pedido a proveedor"""
    pedido = get_object_or_404(PedidoProveedor, pk=pedido_id)
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


"""
2. Modificar crear_categoria para asignar el propietario:
"""

@login_required
def crear_categoria(request):
    """Vista para crear una nueva categoría de producto"""
    if request.method == 'POST':
        form = CategoriaProductoForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.propietario = request.user  # Asignar el usuario actual como propietario
            categoria.save()
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


"""
3. Modificar api_crear_categoria para asignar el propietario:
"""

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
            categoria_padre=categoria_padre,
            propietario=request.user  # Asignar el usuario actual como propietario
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


"""
4. Modificar crear_producto para usar el formulario con el usuario:
"""

@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoInventarioForm(request.POST, user=request.user)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.propietario = request.user  # Asignar el usuario actual como propietario
            producto.save()
            messages.success(request, f'Producto "{producto.nombre_producto}" creado exitosamente.')
            
            # Redirigir a la página de gestión de imágenes si el usuario quiere agregar imágenes
            if 'agregar_imagenes' in request.POST:
                return redirect('inventario:gestionar_imagenes', producto_id=producto.id)
            
            return redirect('inventario:detalle_producto', pk=producto.id)
    else:
        form = ProductoInventarioForm(user=request.user)  # Pasar el usuario al formulario
    
    # Obtener categorías para el modal de creación rápida
    categorias = CategoriaProducto.objects.filter(propietario=request.user).order_by('nombre_categoria')
    estados = EstadoProducto.objects.all().order_by('nombre_estado')
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Producto',
        'categorias': categorias,
        'estados': estados,
        'mostrar_boton_imagenes': True  # Para mostrar el botón de agregar imágenes
    }
    
    return render(request, 'inventario/producto_form.html', context) 