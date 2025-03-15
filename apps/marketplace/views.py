from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count, Avg, Q
from django.contrib import messages
from django.core.paginator import Paginator
from .models import (
    Categoria, Producto, ImagenProducto, Carrito, 
    ItemCarrito, Pedido, ItemPedido, Resena, ListaDeseos
)
from .forms import ProductoForm, CheckoutForm, ResenaForm


def marketplace_home(request):
    """
    Vista principal del marketplace que muestra productos destacados,
    categorías y ofertas
    """
    productos_destacados = Producto.objects.filter(
        destacado=True, 
        estado='disponible'
    ).order_by('-fecha_creacion')[:8]
    
    productos_recientes = Producto.objects.filter(
        estado='disponible'
    ).order_by('-fecha_creacion')[:8]
    
    productos_oferta = Producto.objects.filter(
        estado='disponible', 
        precio_oferta__isnull=False
    ).order_by('-fecha_creacion')[:8]
    
    categorias = Categoria.objects.filter(activa=True).annotate(
        num_productos=Count('productos')
    ).order_by('-num_productos')[:6]
    
    stats = {
        'total_productos': Producto.objects.filter(estado='disponible').count(),
        'total_vendedores': Producto.objects.values('vendedor').distinct().count(),
        'total_categorias': Categoria.objects.filter(activa=True).count(),
    }
    
    context = {
        'productos_destacados': productos_destacados,
        'productos_recientes': productos_recientes,
        'productos_oferta': productos_oferta,
        'categorias': categorias,
        'stats': stats,
    }
    
    return render(request, 'marketplace/home.html', context)


def lista_productos(request):
    """
    Vista que muestra todos los productos disponibles con opciones de filtrado
    """
    productos = Producto.objects.filter(estado='disponible').order_by('-fecha_creacion')
    
    # Filtros
    categoria = request.GET.get('categoria')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    orden = request.GET.get('orden')
    
    if categoria:
        productos = productos.filter(categoria_id=categoria)
    
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)
    
    if orden:
        if orden == 'precio_asc':
            productos = productos.order_by('precio')
        elif orden == 'precio_desc':
            productos = productos.order_by('-precio')
        elif orden == 'nombre':
            productos = productos.order_by('nombre')
        elif orden == 'recientes':
            productos = productos.order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(productos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Categorías para el filtro
    categorias = Categoria.objects.filter(activa=True)
    
    context = {
        'page_obj': page_obj,
        'categorias': categorias,
        'filtros': {
            'categoria': categoria,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'orden': orden,
        }
    }
    
    return render(request, 'marketplace/lista_productos.html', context)


def detalle_producto(request, producto_id):
    """
    Vista detallada de un producto con sus imágenes, información y reseñas
    """
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Productos relacionados
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria, 
        estado='disponible'
    ).exclude(id=producto_id).order_by('?')[:4]
    
    # Reseñas
    resenas = producto.resenas.all().order_by('-fecha_creacion')
    
    # Formulario de reseña
    form_resena = None
    if request.user.is_authenticated:
        # Verificar si el usuario ya tiene una reseña para este producto
        resena_existente = None
        try:
            resena_existente = Resena.objects.get(producto=producto, usuario=request.user)
        except Resena.DoesNotExist:
            pass
        
        if request.method == 'POST' and 'submit_resena' in request.POST:
            form_resena = ResenaForm(request.POST, instance=resena_existente)
            if form_resena.is_valid():
                resena = form_resena.save(commit=False)
                resena.producto = producto
                resena.usuario = request.user
                resena.save()
                if resena_existente:
                    messages.success(request, '¡Tu reseña ha sido actualizada correctamente!')
                else:
                    messages.success(request, '¡Gracias por tu reseña!')
                return redirect('marketplace:detalle_producto', producto_id=producto_id)
        else:
            # Si el usuario ya tiene una reseña, inicializar el formulario con sus datos
            if resena_existente:
                form_resena = ResenaForm(instance=resena_existente)
            else:
                form_resena = ResenaForm()
    
    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
        'resenas': resenas,
        'form_resena': form_resena,
    }
    
    return render(request, 'marketplace/detalle_producto.html', context)


def productos_por_categoria(request, categoria_id):
    """
    Muestra productos filtrados por categoría
    """
    categoria = get_object_or_404(Categoria, id=categoria_id, activa=True)
    
    # Reutilizamos la lógica de lista_productos
    request.GET._mutable = True
    request.GET['categoria'] = categoria_id
    
    return lista_productos(request)


def buscar_productos(request):
    """
    Busca productos por término de búsqueda
    """
    termino = request.GET.get('q', '')
    
    if termino:
        productos = Producto.objects.filter(
            Q(nombre__icontains=termino) | 
            Q(descripcion__icontains=termino),
            estado='disponible'
        ).order_by('-fecha_creacion')
    else:
        productos = Producto.objects.filter(
            estado='disponible'
        ).order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(productos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'termino': termino,
    }
    
    return render(request, 'marketplace/buscar_productos.html', context)


@login_required
def ver_carrito(request):
    """
    Muestra el carrito de compras del usuario
    """
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all().select_related('producto')
    
    context = {
        'carrito': carrito,
        'items': items,
    }
    
    return render(request, 'marketplace/carrito.html', context)


@login_required
def agregar_al_carrito(request, producto_id):
    """
    Agrega un producto al carrito del usuario
    """
    producto = get_object_or_404(Producto, id=producto_id, estado='disponible')
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    
    cantidad = int(request.POST.get('cantidad', 1))
    
    # Verificar si el producto ya está en el carrito
    item, created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        defaults={'cantidad': cantidad}
    )
    
    if not created:
        item.cantidad += cantidad
        item.save()
    
    messages.success(request, f'{producto.nombre} agregado al carrito')
    
    # Redirigir según el parámetro next
    next_url = request.POST.get('next', '')
    if next_url:
        return HttpResponseRedirect(next_url)
    
    return redirect('marketplace:ver_carrito')


@login_required
def actualizar_carrito(request, item_id):
    """
    Actualiza la cantidad de un producto en el carrito
    """
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    
    cantidad = int(request.POST.get('cantidad', 1))
    
    if cantidad > 0:
        item.cantidad = cantidad
        item.save()
    else:
        item.delete()
    
    return redirect('marketplace:ver_carrito')


@login_required
def eliminar_del_carrito(request, item_id):
    """
    Elimina un producto del carrito
    """
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    producto_nombre = item.producto.nombre
    item.delete()
    
    messages.success(request, f'{producto_nombre} eliminado del carrito')
    
    return redirect('marketplace:ver_carrito')


@login_required
def checkout(request):
    """
    Proceso de finalización de compra
    """
    carrito = get_object_or_404(Carrito, usuario=request.user)
    items = carrito.items.all().select_related('producto')
    
    if not items:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('marketplace:ver_carrito')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Crear un nuevo pedido
            pedido = Pedido.objects.create(
                comprador=request.user,
                direccion_envio=form.cleaned_data['direccion'],
                contacto_telefono=form.cleaned_data['telefono'],
                notas=form.cleaned_data['notas'],
                total=carrito.get_total()
            )
            
            # Crear items del pedido
            for item in items:
                ItemPedido.objects.create(
                    pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                    precio_unitario=item.producto.precio_oferta or item.producto.precio,
                    subtotal=item.get_subtotal()
                )
            
            # Vaciar el carrito
            items.delete()
            
            messages.success(request, f'Pedido #{pedido.id} creado correctamente')
            return redirect('marketplace:detalle_pedido', pedido_id=pedido.id)
    else:
        form = CheckoutForm()
    
    context = {
        'carrito': carrito,
        'items': items,
        'form': form,
    }
    
    return render(request, 'marketplace/checkout.html', context)


@login_required
def lista_pedidos(request):
    """
    Muestra la lista de pedidos del usuario
    """
    pedidos = Pedido.objects.filter(comprador=request.user).order_by('-fecha_pedido')
    
    context = {
        'pedidos': pedidos,
    }
    
    return render(request, 'marketplace/lista_pedidos.html', context)


@login_required
def detalle_pedido(request, pedido_id):
    """
    Muestra el detalle de un pedido específico
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, comprador=request.user)
    items = pedido.items.all().select_related('producto')
    
    context = {
        'pedido': pedido,
        'items': items,
    }
    
    return render(request, 'marketplace/detalle_pedido.html', context)


@login_required
def ver_lista_deseos(request):
    # Obtener los items de la lista de deseos del usuario actual
    lista_deseos = ListaDeseos.objects.filter(usuario=request.user).first()
    
    # Si no existe una lista de deseos, crear una vacía
    if not lista_deseos:
        lista_deseos = ListaDeseos.objects.create(usuario=request.user)
    
    # Obtener los productos de la lista de deseos
    items_lista_deseos = lista_deseos.productos.all()
    
    context = {
        'lista_deseos': items_lista_deseos,
    }
    
    return render(request, 'marketplace/lista_deseos.html', context)


@login_required
def agregar_a_lista_deseos(request, producto_id):
    """
    Agrega un producto a la lista de deseos
    """
    producto = get_object_or_404(Producto, id=producto_id, estado='disponible')
    lista_deseos, created = ListaDeseos.objects.get_or_create(usuario=request.user)
    
    lista_deseos.productos.add(producto)
    
    messages.success(request, f'{producto.nombre} agregado a tu lista de deseos')
    
    # Redirigir según el parámetro next
    next_url = request.GET.get('next', '')
    if next_url:
        return HttpResponseRedirect(next_url)
    
    return redirect('marketplace:ver_lista_deseos')


@login_required
def eliminar_de_lista_deseos(request, producto_id):
    """
    Elimina un producto de la lista de deseos
    """
    producto = get_object_or_404(Producto, id=producto_id)
    lista_deseos = get_object_or_404(ListaDeseos, usuario=request.user)
    
    lista_deseos.productos.remove(producto)
    
    messages.success(request, f'{producto.nombre} eliminado de tu lista de deseos')
    
    return redirect('marketplace:ver_lista_deseos')


@login_required
def mi_tienda(request):
    """
    Muestra los productos que vende el usuario
    """
    productos = Producto.objects.filter(vendedor=request.user).order_by('-fecha_creacion')
    
    # Estadísticas básicas
    productos_vendidos = 0  # Aquí se podría calcular desde los pedidos
    
    context = {
        'productos': productos,
        'stats': {
            'total_productos': productos.count(),
            'productos_activos': productos.filter(estado='disponible').count(),
            'productos_vendidos': productos_vendidos,
        }
    }
    
    return render(request, 'marketplace/mi_tienda.html', context)


@login_required
def nuevo_producto(request):
    """
    Permite al usuario crear un nuevo producto
    """
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.vendedor = request.user
            producto.save()
            
            # Manejar imágenes adicionales
            for imagen in request.FILES.getlist('imagenes_adicionales'):
                ImagenProducto.objects.create(
                    producto=producto,
                    imagen=imagen
                )
            
            messages.success(request, f'Producto {producto.nombre} creado correctamente')
            return redirect('marketplace:mi_tienda')
    else:
        form = ProductoForm()
    
    context = {
        'form': form,
        'accion': 'Crear',
        'habilitar_multiple_imagenes': True,  # Flag para habilitar multiple mediante JS
    }
    
    return render(request, 'marketplace/form_producto.html', context)


@login_required
def editar_producto(request, producto_id):
    """
    Permite al usuario editar un producto existente
    """
    producto = get_object_or_404(Producto, id=producto_id, vendedor=request.user)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            
            # Manejar imágenes adicionales
            for imagen in request.FILES.getlist('imagenes_adicionales'):
                ImagenProducto.objects.create(
                    producto=producto,
                    imagen=imagen
                )
            
            messages.success(request, f'Producto {producto.nombre} actualizado correctamente')
            return redirect('marketplace:mi_tienda')
    else:
        form = ProductoForm(instance=producto)
    
    context = {
        'form': form,
        'producto': producto,
        'accion': 'Editar',
        'habilitar_multiple_imagenes': True,  # Flag para habilitar multiple mediante JS
    }
    
    return render(request, 'marketplace/form_producto.html', context)


@login_required
def eliminar_producto(request, producto_id):
    """
    Permite al usuario eliminar un producto propio
    """
    producto = get_object_or_404(Producto, id=producto_id, vendedor=request.user)
    nombre_producto = producto.nombre
    
    if request.method == 'POST':
        # Eliminar imágenes asociadas
        if producto.imagen_principal:
            producto.imagen_principal.delete(save=False)
        
        for imagen in producto.imagenes.all():
            imagen.imagen.delete(save=False)
        
        # Eliminar el producto
        producto.delete()
        
        messages.success(request, f'Producto "{nombre_producto}" eliminado correctamente')
        return redirect('marketplace:mi_tienda')
    
    # Si no es POST, redirigir a mi_tienda
    return redirect('marketplace:mi_tienda')


def api_info_producto(request, producto_id):
    """
    API para obtener información de un producto en formato JSON
    """
    try:
        producto = Producto.objects.get(id=producto_id, estado='disponible')
        data = {
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'precio_oferta': float(producto.precio_oferta) if producto.precio_oferta else None,
            'stock': producto.stock,
            'en_oferta': producto.esta_en_oferta(),
            'porcentaje_descuento': producto.porcentaje_descuento(),
        }
        return JsonResponse({'status': 'success', 'data': data})
    except Producto.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)


@login_required
def api_cantidad_carrito(request):
    """
    API para obtener la cantidad de items en el carrito
    """
    try:
        carrito = Carrito.objects.get(usuario=request.user)
        cantidad = carrito.get_cantidad_items()
        return JsonResponse({'status': 'success', 'cantidad': cantidad})
    except Carrito.DoesNotExist:
        return JsonResponse({'status': 'success', 'cantidad': 0}) 