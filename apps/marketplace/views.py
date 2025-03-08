from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.urls import reverse
from .models import Producto, CategoriaProducto, CarritoItem, ListaDeseos, Compra, DetalleCompra

def product_list(request):
    """Vista para listar todos los productos"""
    productos = Producto.objects.filter(activo=True)
    categoria_id = request.GET.get('categoria')
    
    # Filtrar por categoría si se proporciona
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        productos = productos.filter(nombre__icontains=query)
    
    # Paginación
    paginator = Paginator(productos, 12)  # 12 productos por página
    page_number = request.GET.get('page')
    productos_paginados = paginator.get_page(page_number)
    
    # Obtener todas las categorías para filtros
    categorias = CategoriaProducto.objects.filter(activa=True)
    
    return render(request, 'marketplace/product_list.html', {
        'productos': productos_paginados,
        'categorias': categorias,
        'categoria_actual': categoria_id,
        'query': query
    })

def product_detail(request, product_id):
    """Vista para ver el detalle de un producto"""
    producto = get_object_or_404(Producto, id=product_id, activo=True)
    
    # Productos relacionados (misma categoría)
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria, 
        activo=True
    ).exclude(id=producto.id)[:4]
    
    return render(request, 'marketplace/product_detail.html', {
        'producto': producto,
        'productos_relacionados': productos_relacionados
    })

@login_required
def product_create(request):
    """Vista para crear un nuevo producto"""
    # Obtener todas las categorías para el formulario
    categorias = CategoriaProducto.objects.all()
    
    if request.method == 'POST':
        # Procesar el formulario
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        categoria_id = request.POST.get('categoria')
        imagen = request.FILES.get('imagen')
        
        # Validación básica
        if not nombre or not precio:
            messages.error(request, 'El nombre y el precio son obligatorios')
            return render(request, 'marketplace/product_create.html', {
                'categorias': categorias,
                'values': request.POST  # Para mantener los valores ingresados
            })
        
        try:
            # Crear el producto
            categoria = CategoriaProducto.objects.get(id=categoria_id) if categoria_id else None
            
            producto = Producto.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                precio=float(precio),
                stock=int(stock) if stock else 0,
                categoria=categoria,
                imagen=imagen,
                vendedor=request.user
            )
            
            messages.success(request, f'Producto "{nombre}" creado exitosamente')
            return redirect('marketplace:product_detail', product_id=producto.id)
            
        except Exception as e:
            messages.error(request, f'Error al crear el producto: {str(e)}')
    
    # GET request - mostrar formulario
    return render(request, 'marketplace/product_create.html', {
        'categorias': categorias
    })

@login_required
def cart(request):
    """Vista para mostrar el carrito de compras"""
    carrito_items = CarritoItem.objects.filter(usuario=request.user)
    total = sum(item.subtotal for item in carrito_items)
    
    return render(request, 'marketplace/cart.html', {
        'items': carrito_items,
        'total': total
    })

@login_required
def add_to_cart(request, product_id):
    """Vista para añadir productos al carrito"""
    producto = get_object_or_404(Producto, id=product_id, activo=True)
    
    # Verificar si el producto ya está en el carrito
    carrito_item, created = CarritoItem.objects.get_or_create(
        usuario=request.user,
        producto=producto
    )
    
    # Si ya existía, incrementar la cantidad
    if not created:
        carrito_item.cantidad += 1
        carrito_item.save()
    
    # Respuesta AJAX o normal
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'"{producto.nombre}" añadido al carrito',
            'cart_count': CarritoItem.objects.filter(usuario=request.user).count()
        })
    else:
        messages.success(request, f'"{producto.nombre}" añadido al carrito')
        return redirect('marketplace:product_list')

@login_required
def wishlist(request):
    """Vista para mostrar la lista de deseos"""
    deseos = ListaDeseos.objects.filter(usuario=request.user)
    
    return render(request, 'marketplace/wishlist.html', {
        'deseos': deseos
    })

@login_required
def add_to_wishlist(request, product_id):
    """Vista para añadir productos a la lista de deseos"""
    producto = get_object_or_404(Producto, id=product_id, activo=True)
    
    # Verificar si el producto ya está en la lista de deseos
    _, created = ListaDeseos.objects.get_or_create(
        usuario=request.user,
        producto=producto
    )
    
    # Respuesta AJAX o normal
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    return JsonResponse({
        'success': True,
            'message': f'"{producto.nombre}" añadido a tu lista de deseos',
            'created': created
    })
    else:
        messages.success(request, f'"{producto.nombre}" añadido a tu lista de deseos')
        return redirect('marketplace:product_list')

@login_required
def checkout(request):
    """Vista para el proceso de checkout"""
    carrito_items = CarritoItem.objects.filter(usuario=request.user)
    
    if not carrito_items.exists():
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('marketplace:cart')
    
    total = sum(item.subtotal for item in carrito_items)
    
    if request.method == 'POST':
        # Procesar la compra
        direccion = request.POST.get('direccion')
        metodo_pago = request.POST.get('metodo_pago')
        
        # Crear la compra
        compra = Compra.objects.create(
            usuario=request.user,
            direccion_envio=direccion,
            metodo_pago=metodo_pago,
            total=total
        )
        
        # Crear los detalles de la compra
        for item in carrito_items:
            DetalleCompra.objects.create(
                compra=compra,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio
            )
            
            # Actualizar stock
            item.producto.stock -= item.cantidad
            item.producto.save()
        
        # Limpiar el carrito
        carrito_items.delete()
        
        messages.success(request, '¡Compra realizada con éxito!')
        return redirect('marketplace:product_list')
    
    return render(request, 'marketplace/checkout.html', {
        'items': carrito_items,
        'total': total
    }) 