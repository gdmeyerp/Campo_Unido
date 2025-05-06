from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count, Avg, Q, Sum
from django.contrib import messages
from django.core.paginator import Paginator
from .models import (
    CategoriaProducto, Producto, CarritoItem,
    ListaDeseos, Compra, DetalleCompra, ValoracionProducto, RespuestaValoracion, ProductoImagen
)
from .forms import ProductoForm
import json


def index(request):
    return render(request, 'marketplace/index.html')


def marketplace_home(request):
    """
    Vista principal del marketplace que muestra productos destacados,
    categorías y ofertas
    """
    productos_destacados = Producto.objects.filter(
        activo=True
    ).order_by('-fecha_creacion')[:8]
    
    productos_recientes = Producto.objects.filter(
        activo=True
    ).order_by('-fecha_creacion')[:8]
    
    categorias = CategoriaProducto.objects.filter(activa=True).annotate(
        num_productos=Count('productos')
    ).order_by('-num_productos')[:6]
    
    stats = {
        'total_productos': Producto.objects.filter(activo=True).count(),
        'total_vendedores': Producto.objects.values('vendedor').distinct().count(),
        'total_categorias': CategoriaProducto.objects.filter(activa=True).count(),
    }
    
    context = {
        'productos_destacados': productos_destacados,
        'productos_recientes': productos_recientes,
        'categorias': categorias,
        'stats': stats,
    }
    
    return render(request, 'marketplace/home.html', context)


def lista_productos(request):
    """
    Vista que muestra todos los productos disponibles con opciones de filtrado
    """
    productos = Producto.objects.filter(
        activo=True).order_by('-fecha_creacion')
    
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
    categorias = CategoriaProducto.objects.filter(activa=True)
    
    context = {
        'page_obj': page_obj,
        'productos': page_obj,
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
    
    # Cargar imágenes adicionales - Temporal hasta que se cree la tabla
    try:
        imagenes_adicionales = ProductoImagen.objects.filter(
            producto=producto).order_by('orden')
    except BaseException:
        # Si la tabla no existe, devolvemos una lista vacía
        imagenes_adicionales = []
    
    # Productos relacionados
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria, 
        activo=True
    ).exclude(id=producto_id).order_by('?')[:4]
    
    # Para evitar errores, inicializamos valoraciones con una lista vacía
    valoraciones = []

    # Calcular estadísticas de valoraciones (con valores por defecto)
    estadisticas_valoraciones = {
        'distribución': {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0},
        'distribución_porcentaje': {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0},
        'promedio': 0
    }
    
    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
        'valoraciones': valoraciones,
        'estadisticas_valoraciones': estadisticas_valoraciones,
        'ha_comprado': False,
        'ha_valorado': False,
        'imagenes_adicionales': imagenes_adicionales
    }

    return render(request, 'marketplace/producto_detalle.html', context)


def productos_por_categoria(request, categoria_id):
    """
    Muestra productos filtrados por categoría
    """
    categoria = get_object_or_404(
        CategoriaProducto,
        id=categoria_id,
        activa=True)
    
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
            activo=True
        ).order_by('-fecha_creacion')
    else:
        productos = Producto.objects.filter(
            activo=True
        ).order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(productos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'termino': termino,
    }
    
    return render(request, 'marketplace/lista_productos.html', context)


@login_required
def ver_carrito(request):
    """
    Muestra el carrito de compras del usuario
    """
    items = CarritoItem.objects.filter(
        usuario=request.user).select_related('producto')

    subtotal = sum(item.subtotal for item in items)
    
    context = {
        'items': items,
        'subtotal': subtotal,
        'costo_envio': 0,  # Temporalmente establecido a 0
        'total': subtotal,  # Por ahora, el total es igual al subtotal
    }
    
    return render(request, 'marketplace/carrito_detalle.html', context)


@login_required
def agregar_al_carrito(request, producto_id):
    """
    Agrega un producto al carrito del usuario
    """
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    
    cantidad = int(request.POST.get('cantidad', 1))
    
    # Verificar si el producto ya está en el carrito
    try:
        item = CarritoItem.objects.get(usuario=request.user, producto=producto)
        item.cantidad += cantidad
        item.save()
        created = False
    except CarritoItem.DoesNotExist:
        item = CarritoItem.objects.create(
            usuario=request.user,
            producto=producto,
            cantidad=cantidad
        )
        created = True

    # Si es una solicitud AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{producto.nombre} {"agregado al" if created else "actualizado en el"} carrito',
            'cart_count': CarritoItem.objects.filter(usuario=request.user).count()
        })
    
    messages.success(request, f'{producto.nombre} agregado al carrito')
    return redirect('marketplace:ver_carrito')


@login_required
def actualizar_carrito(request, item_id):
    """
    Actualiza la cantidad de un producto en el carrito
    """
    item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
    cantidad = int(request.POST.get('cantidad', 1))
    
    if cantidad <= 0:
        item.delete()
        messages.success(
            request, f'{
                item.producto.nombre} eliminado del carrito')
    else:
        item.cantidad = cantidad
        item.save()
        messages.success(
            request, f'Cantidad actualizada para {
                item.producto.nombre}')
    
    return redirect('marketplace:ver_carrito')


@login_required
def eliminar_del_carrito(request, item_id):
    """
    Elimina un producto del carrito
    """
    item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
    producto_nombre = item.producto.nombre
    item.delete()
    
    messages.success(request, f'{producto_nombre} eliminado del carrito')
    
    return redirect('marketplace:ver_carrito')


@login_required
def checkout(request):
    """
    Procesa el checkout del carrito
    """
    items = CarritoItem.objects.filter(usuario=request.user).select_related('producto')
    
    if not items:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('marketplace:ver_carrito')
    
    total = sum(item.subtotal for item in items)
    
    if request.method == 'POST':
        # Crear la compra
        compra = Compra.objects.create(
            usuario=request.user,
            total=total
        )

        # Crear los detalles de la compra
        for item in items:
            DetalleCompra.objects.create(
                compra=compra,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio,
                subtotal=item.subtotal
            )
            
        # Limpiar el carrito
        items.delete()
            
        messages.success(request, '¡Compra realizada con éxito!')
        return redirect('marketplace:lista_pedidos')
    
    context = {
        'items': items,
        'total': total,
    }
    
    return render(request, 'marketplace/checkout.html', context)


@login_required
def lista_pedidos(request):
    """
    Muestra los pedidos del usuario
    """
    pedidos = Compra.objects.filter(
        usuario=request.user).order_by('-fecha_compra')

    return render(request, 'marketplace/mis_compras.html',
                  {'pedidos': pedidos})


@login_required
def detalle_pedido(request, pedido_id):
    """
    Muestra los detalles de un pedido
    """
    pedido = get_object_or_404(Compra, id=pedido_id, usuario=request.user)
    items = pedido.detalles.all().select_related('producto')
    
    return render(request, 'marketplace/detalle_pedido.html', {
        'pedido': pedido,
        'items': items
    })


@login_required
def ver_lista_deseos(request):
    """
    Muestra la lista de deseos del usuario
    """
    items = ListaDeseos.objects.filter(
        usuario=request.user).select_related('producto')

    return render(request, 'marketplace/lista_deseos.html', {'items': items})


@login_required
def agregar_a_lista_deseos(request, producto_id):
    """
    Agrega un producto a la lista de deseos
    """
    producto = get_object_or_404(Producto, id=producto_id, activo=True)

    # Verificar si ya está en la lista de deseos
    if ListaDeseos.objects.filter(
            usuario=request.user, producto=producto).exists():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'El producto ya está en tu lista de deseos'
            })
        messages.info(request, 'El producto ya está en tu lista de deseos')
    else:
        ListaDeseos.objects.create(usuario=request.user, producto=producto)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Producto agregado a tu lista de deseos'
            })
        messages.success(request, 'Producto agregado a tu lista de deseos')

    # Redirigir según el tipo de solicitud
    referer = request.META.get('HTTP_REFERER')
    if referer and not request.headers.get(
            'X-Requested-With') == 'XMLHttpRequest':
        return redirect(referer)
    return redirect('marketplace:ver_lista_deseos')


@login_required
def eliminar_de_lista_deseos(request, producto_id):
    """
    Elimina un producto de la lista de deseos
    """
    ListaDeseos.objects.filter(
        usuario=request.user,
        producto_id=producto_id).delete()
    messages.success(request, 'Producto eliminado de tu lista de deseos')
    
    return redirect('marketplace:ver_lista_deseos')


@login_required
def mi_tienda(request):
    """
    Muestra los productos del vendedor y estadísticas básicas
    """
    productos = Producto.objects.filter(
        vendedor=request.user).order_by('-fecha_creacion')

    # Cálculo de estadísticas básicas
    productos_vendidos = DetalleCompra.objects.filter(
        producto__vendedor=request.user
    ).values('producto').annotate(total=Sum('cantidad')).count()
    
    context = {
        'productos': productos,
        'stats': {
            'total_productos': productos.count(),
            'productos_activos': productos.filter(activo=True).count(),
            'productos_vendidos': productos_vendidos,
        }
    }
    
    return render(request, 'marketplace/mi_tienda.html', context)


@login_required
def nuevo_producto(request):
    """
    Crea un nuevo producto
    """
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.vendedor = request.user
            producto.save()
            
            messages.success(request, '¡Producto creado con éxito!')
            return redirect('marketplace:mi_tienda')
    else:
        form = ProductoForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Producto',
        'accion': 'Crear',
    }
    
    return render(request, 'marketplace/form_producto.html', context)


@login_required
def editar_producto(request, producto_id):
    """
    Edita un producto existente
    """
    producto = get_object_or_404(
        Producto,
        id=producto_id,
        vendedor=request.user)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Producto actualizado con éxito!')
            return redirect('marketplace:mi_tienda')
    else:
        form = ProductoForm(instance=producto)
    
    context = {
        'form': form,
        'producto': producto,
        'titulo': 'Editar Producto',
        'accion': 'Actualizar',
    }
    
    return render(request, 'marketplace/form_producto.html', context)


@login_required
def eliminar_producto(request, producto_id):
    """
    Elimina un producto
    """
    producto = get_object_or_404(
        Producto,
        id=producto_id,
        vendedor=request.user)
    
    if request.method == 'POST':
        producto.delete()
        messages.success(request, '¡Producto eliminado con éxito!')
        return redirect('marketplace:mi_tienda')
    
    context = {
        'producto': producto,
    }

    return render(
        request, 'marketplace/confirmar_eliminar_producto.html', context)


def api_info_producto(request, producto_id):
    """
    API que devuelve información del producto en formato JSON
    """
    try:
        producto = Producto.objects.get(id=producto_id, activo=True)
        data = {
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'stock': producto.stock,
            'imagen': producto.imagen.url if producto.imagen else '',
            'disponible': producto.stock > 0 and producto.activo,
        }
        return JsonResponse(data)
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)


@login_required
def api_cantidad_carrito(request):
    """
    API para obtener la cantidad de items en el carrito
    """
    try:
        cantidad = CarritoItem.objects.filter(usuario=request.user).count()
        return JsonResponse({'cantidad': cantidad})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def agregar_producto_inventario(request):
    """
    Vista para agregar productos desde el inventario al marketplace
    """
    from apps.inventario.models import ProductoInventario
    from apps.inventario.forms import ProductoInventarioForm
    from .models import Producto, CategoriaProducto

    # Obtener los productos del inventario del usuario
    productos_inventario = ProductoInventario.objects.filter(
        propietario=request.user)

    if request.method == 'POST':
        producto_id = request.POST.get('producto_inventario')

        try:
            # Obtener el producto del inventario
            producto_inv = ProductoInventario.objects.get(
                id=producto_id, propietario=request.user)

            # Crear producto en el marketplace
            categoria, created = CategoriaProducto.objects.get_or_create(
                nombre=producto_inv.categoria_producto.nombre_categoria,
                defaults={
                    'descripcion': producto_inv.categoria_producto.descripcion
                }
            )

            # Crear el producto en el marketplace
            producto = Producto(
                nombre=producto_inv.nombre_producto,
                descripcion=producto_inv.descripcion_producto,
                precio=producto_inv.precio_venta,
                stock=producto_inv.cantidad_disponible,
                categoria=categoria,
                vendedor=request.user,
                destacado=False,
                estado='disponible'
            )
            producto.save()

            messages.success(
                request, f'Producto "{
                    producto.nombre}" agregado al marketplace correctamente.')
            return redirect('marketplace:mi_tienda')

        except ProductoInventario.DoesNotExist:
            messages.error(
                request,
                'El producto seleccionado no existe o no te pertenece.')
            return redirect('marketplace:agregar_producto_inventario')

    context = {
        'productos_inventario': productos_inventario,
        'title': 'Agregar Producto desde Inventario'
    }

    return render(
        request, 'marketplace/agregar_producto_inventario.html', context)


@login_required
def product_create(request):
    """
    Crea un nuevo producto usando la plantilla product_create.html
    """
    from apps.inventario.models import CategoriaProducto as CategoriaInventario

    if request.method == 'POST':
        # Debug para ver contenido de FILES
        print("FILES:", request.FILES)

        # Procesar la categoría de inventario si es seleccionada
        categoria_id = request.POST.get('categoria', '')
        if categoria_id.startswith('inv_'):
            # Es una categoría del inventario, procesar y crear la categoría en
            # marketplace
            inv_id = categoria_id.replace('inv_', '')
            try:
                cat_inventario = CategoriaInventario.objects.get(
                    id=inv_id, propietario=request.user)
                # Crear o buscar la categoría equivalente en marketplace
                cat_marketplace, created = CategoriaProducto.objects.get_or_create(
                    nombre=cat_inventario.nombre_categoria,
                    defaults={
                        'descripcion': cat_inventario.descripcion,
                        'activa': True
                    }
                )
                # Reemplazar la categoría en el POST con la del marketplace
                request.POST = request.POST.copy()
                request.POST['categoria'] = str(cat_marketplace.id)
            except CategoriaInventario.DoesNotExist:
                messages.error(
                    request, "La categoría seleccionada no existe o no te pertenece.")
                return redirect('marketplace:product_create')

        # Continuar con el proceso normal
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.vendedor = request.user
            producto.destacado = request.POST.get('destacado', 'off') == 'on'
            producto.estado = 'disponible'
            producto.activo = True  # Asegurar que el producto esté activo por defecto

            # Manejar la imagen
            if 'imagen' in request.FILES:
                producto.imagen = request.FILES['imagen']
                print("Imagen asignada:", producto.imagen)

            producto.save()
            print(
                "Producto guardado con ID:",
                producto.id,
                "Imagen:",
                producto.imagen)

            # Manejar imágenes adicionales - Temporal hasta que se cree la
            # tabla
            try:
                if 'imagenes_adicionales' in request.FILES:
                    imagenes = request.FILES.getlist('imagenes_adicionales')
                    for i, img in enumerate(imagenes):
                        ProductoImagen.objects.create(
                            producto=producto,
                            imagen=img,
                            orden=i + 1
                        )
                    print(f"Se guardaron {len(imagenes)} imágenes adicionales")
            except Exception as e:
                print(f"No se pudieron guardar las imágenes adicionales: {e}")

            messages.success(request, '¡Producto creado con éxito!')
            return redirect('marketplace:mi_tienda')
        else:
            print("Errores en formulario:", form.errors)
            messages.error(
                request,
                "Hubo errores en el formulario. Por favor revisa los campos.")
    else:
        form = ProductoForm()

    # Obtener categorías del marketplace
    categorias_marketplace = CategoriaProducto.objects.filter(activa=True)

    # Obtener categorías del inventario
    categorias_inventario = CategoriaInventario.objects.filter(
        propietario=request.user)

    context = {
        'form': form,
        'categorias': categorias_marketplace,
        'categorias_inventario': categorias_inventario,
        'values': {},
    }

    return render(request, 'marketplace/product_create.html', context)


@login_required
def valoracion_crear(request, producto_id):
    """
    Crea una nueva valoración para un producto
    """
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        comentario = request.POST.get('comentario')
        calificacion = int(request.POST.get('puntuacion'))

        # Verificar si el usuario ya valoró este producto
        if ValoracionProducto.objects.filter(
                producto=producto, usuario=request.user).exists():
            messages.warning(request, 'Ya has valorado este producto')
            return redirect('marketplace:detalle_producto',
                            producto_id=producto_id)

        # Verificar si el usuario ha comprado el producto
        ha_comprado = DetalleCompra.objects.filter(
            compra__usuario=request.user,
            producto=producto
        ).exists()

        if not ha_comprado:
            messages.warning(
                request, 'Debes comprar el producto antes de valorarlo')
            return redirect('marketplace:detalle_producto',
                            producto_id=producto_id)

        # Crear la valoración
        valoracion = ValoracionProducto(
            producto=producto,
            usuario=request.user,
            titulo=titulo,
            comentario=comentario,
            calificacion=calificacion
        )
        valoracion.save()

        messages.success(request, 'Valoración creada correctamente')
        return redirect('marketplace:detalle_producto',
                        producto_id=producto_id)

    return redirect('marketplace:detalle_producto', producto_id=producto_id)


@login_required
def valoracion_editar(request, valoracion_id):
    """
    Edita una valoración existente
    """
    valoracion = get_object_or_404(
        ValoracionProducto,
        id=valoracion_id,
        usuario=request.user)

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        comentario = request.POST.get('comentario')
        calificacion = int(request.POST.get('puntuacion'))

        valoracion.titulo = titulo
        valoracion.comentario = comentario
        valoracion.calificacion = calificacion
        valoracion.save()

        messages.success(request, 'Valoración actualizada correctamente')
        return redirect('marketplace:detalle_producto',
                        producto_id=valoracion.producto.id)

    context = {
        'valoracion': valoracion,
        'producto': valoracion.producto
    }

    return render(request, 'marketplace/valoracion_editar.html', context)


@login_required
def valoracion_responder(request, valoracion_id):
    """
    Responde a una valoración (solo para el vendedor del producto)
    """
    valoracion = get_object_or_404(ValoracionProducto, id=valoracion_id)
    producto = valoracion.producto

    if request.user != producto.vendedor:
        messages.warning(
            request,
            'Solo el vendedor puede responder a esta valoración')
        return redirect('marketplace:detalle_producto',
                        producto_id=producto.id)

    if RespuestaValoracion.objects.filter(valoracion=valoracion).exists():
        messages.warning(request, 'Ya has respondido a esta valoración')
        return redirect('marketplace:detalle_producto',
                        producto_id=producto.id)

    if request.method == 'POST':
        respuesta = request.POST.get('respuesta')

        RespuestaValoracion.objects.create(
            valoracion=valoracion,
            respuesta=respuesta
        )

        messages.success(request, 'Respuesta enviada correctamente')

    return redirect('marketplace:detalle_producto', producto_id=producto.id)


@login_required
def api_valoracion_util(request):
    """
    API para marcar una valoración como útil
    """
    if request.method == 'POST':
        valoracion_id = request.POST.get('valoracion_id')

        try:
            valoracion = ValoracionProducto.objects.get(id=valoracion_id)

            # Incrementar el contador de utilidad
            valoracion.utilidad += 1
            valoracion.save()

            return JsonResponse({
                'status': 'success',
                'utilidad': valoracion.utilidad,
                'added': True
            })
        except ValoracionProducto.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Valoración no encontrada'
            }, status=404)

    return JsonResponse({
        'status': 'error',
        'message': 'Método no permitido'
    }, status=405)


@login_required
def api_carrito_agregar(request):
    """
    API para agregar un producto al carrito
    """
    if request.method == 'POST':
        try:
            # Parse JSON data
            data = json.loads(request.body)
            producto_id = data.get('producto_id')
            cantidad = int(data.get('cantidad', 1))

            producto = Producto.objects.get(id=producto_id, activo=True)

            # Verificar stock
            if producto.stock < cantidad:
                return JsonResponse({
                    'status': 'error',
                    'message': f'No hay suficiente stock disponible. Solo quedan {producto.stock} unidades.'
                })

            # Verificar si el producto ya está en el carrito
            try:
                item = CarritoItem.objects.get(
                    usuario=request.user, producto=producto)
                item.cantidad += cantidad
                item.save()
                created = False
            except CarritoItem.DoesNotExist:
                item = CarritoItem.objects.create(
                    usuario=request.user,
                    producto=producto,
                    cantidad=cantidad
                )
                created = True

            # Obtener el número total de items en el carrito
            cart_count = CarritoItem.objects.filter(
                usuario=request.user).count()

            return JsonResponse({
                'status': 'success',
                'message': f'Producto {"agregado al" if created else "actualizado en el"} carrito',
                'cart_count': cart_count
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Datos JSON inválidos'
            }, status=400)
        except Producto.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Producto no encontrado o no disponible'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Método no permitido'
    }, status=405)


@login_required
def api_lista_deseos_toggle(request):
    """
    API para agregar/quitar un producto de la lista de deseos
    """
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')

        try:
            producto = Producto.objects.get(id=producto_id)

            # Verificar si ya está en la lista de deseos
            lista_deseos_item = ListaDeseos.objects.filter(
                usuario=request.user,
                producto=producto
            )

            if lista_deseos_item.exists():
                # Si existe, eliminarlo
                lista_deseos_item.delete()
                return JsonResponse({
                    'status': 'success',
                    'added': False,
                    'message': 'Producto eliminado de tu lista de deseos'
                })
            else:
                # Si no existe, agregarlo
                ListaDeseos.objects.create(
                    usuario=request.user,
                    producto=producto
                )
                return JsonResponse({
                    'status': 'success',
                    'added': True,
                    'message': 'Producto agregado a tu lista de deseos'
                })
        except Producto.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Producto no encontrado'
            }, status=404)

    return JsonResponse({
        'status': 'error',
        'message': 'Método no permitido'
    }, status=405)


@login_required
def seleccionar_producto_inventario(request):
    """
    Vista para seleccionar un producto del inventario para agregarlo al marketplace
    """
    from apps.inventario.models import ProductoInventario
    from django.db.models import Q

    # Búsqueda por término
    search = request.GET.get('search', '')
    
    # Obtener los productos del inventario del usuario
    query = ProductoInventario.objects.filter(propietario=request.user)
    
    # Aplicar filtro de búsqueda si existe
    if search:
        query = query.filter(
            Q(nombre_producto__icontains=search) | 
            Q(descripcion_producto__icontains=search)
        )
    
    # Ordenar los productos
    productos = query.order_by('nombre_producto')
    
    # Para la selección de producto
    producto_seleccionado = None
    form = None
    
    if 'producto_id' in request.GET:
        try:
            producto_id = request.GET.get('producto_id')
            producto_seleccionado = ProductoInventario.objects.get(
                id=producto_id, propietario=request.user)
            
            # Aquí puedes inicializar un formulario si es necesario
            # form = TuFormulario(initial={
            #    'campo': valor,
            # })
            
        except ProductoInventario.DoesNotExist:
            messages.error(request, 'El producto seleccionado no existe o no te pertenece.')
    
    context = {
        'title': 'Seleccionar Producto de Inventario',
        'productos': productos,
        'producto_seleccionado': producto_seleccionado,
        'form': form,
    }
    
    return render(request, 'marketplace/seleccionar_producto_inventario.html', context)
