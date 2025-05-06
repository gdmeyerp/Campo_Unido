from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Count, Avg, Q, Sum, F
from django.db.models.functions import TruncDate
from django.contrib import messages
from django.core.paginator import Paginator
from .models import (
    CategoriaProducto, Producto, CarritoItem,
    ListaDeseos, Compra, DetalleCompra, ValoracionProducto, RespuestaValoracion, ProductoImagen, DireccionEnvio, Orden,
    NotificacionMarketplace
)
from .forms import ProductoForm
from django import forms
import json
from django.db import transaction
from django.db.utils import IntegrityError
from io import BytesIO
from django.utils import timezone
import os
import logging
import sys
import traceback
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Importar ReportLab para generar PDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm

# Configurar un logger específico para marketplace
logger = logging.getLogger('marketplace')
logger.setLevel(logging.DEBUG)

# Si no hay handlers configurados, añadir uno que escriba a la consola
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

# Formulario para agregar producto de inventario al marketplace
class ProductoInventarioMarketplaceForm(forms.Form):
    producto_inventario = forms.ChoiceField(
        choices=[], 
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cantidad_a_vender = forms.IntegerField(
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    precio_base = forms.DecimalField(
        min_value=0.01,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        help_text="Precio de venta por unidad"
    )
    descripcion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )
    destacado = forms.BooleanField(
        required=False, 
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    es_organico = forms.BooleanField(
        required=False, 
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    imagen_principal = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    imagen_adicional1 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    imagen_adicional2 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    imagen_adicional3 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Cargar productos del inventario del usuario
            from apps.inventario.models import ProductoInventario
            productos = ProductoInventario.objects.filter(propietario=user)
            self.fields['producto_inventario'].choices = [(p.id, f"{p.nombre_producto} (Stock: {p.cantidad_disponible})") for p in productos]

def index(request):
    return render(request, 'marketplace/index.html')


def marketplace_home(request):
    """
    Vista principal del marketplace que muestra productos destacados,
    categorías y ofertas
    """
    # Filtrar productos destacados con stock > 0
    productos_destacados = Producto.objects.filter(
        activo=True,
        stock__gt=0
    ).order_by('-fecha_creacion')[:8]
    
    # Filtrar productos recientes con stock > 0
    productos_recientes = Producto.objects.filter(
        activo=True,
        stock__gt=0
    ).order_by('-fecha_creacion')[:8]
    
    categorias = CategoriaProducto.objects.filter(activa=True).annotate(
        num_productos=Count('productos')
    ).order_by('-num_productos')[:6]
    
    stats = {
        'total_productos': Producto.objects.filter(activo=True, stock__gt=0).count(),
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
    # Filtrar productos con stock > 0
    productos = Producto.objects.filter(
        activo=True, 
        stock__gt=0
    ).order_by('-fecha_creacion')
    
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
        activo=True,
        stock__gt=0
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
            activo=True,
            stock__gt=0
        ).order_by('-fecha_creacion')
    else:
        productos = Producto.objects.filter(
            activo=True,
            stock__gt=0
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
    
    # Validar que el producto no sea del propio usuario
    if producto.vendedor == request.user:
        logger.warning(f"Usuario {request.user.id} intentó agregar su propio producto {producto_id} al carrito")
        message = "No puedes agregar tus propios productos al carrito"
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': message
            })
        messages.warning(request, message)
        return redirect('marketplace:detalle_producto', producto_id=producto_id)
    
    # Validar que el producto tenga stock
    cantidad = int(request.POST.get('cantidad', 1))
    if producto.stock < cantidad:
        logger.warning(f"Usuario {request.user.id} intentó agregar producto {producto_id} sin stock suficiente: solicitado={cantidad}, disponible={producto.stock}")
        message = f"Stock insuficiente. Solo hay {producto.stock} unidades disponibles."
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': message
            })
        messages.warning(request, message)
        return redirect('marketplace:detalle_producto', producto_id=producto_id)
    
    # Verificar si el producto ya está en el carrito
    try:
        item = CarritoItem.objects.get(usuario=request.user, producto=producto)
        # Validar que la cantidad total no exceda el stock
        if item.cantidad + cantidad > producto.stock:
            logger.warning(f"Usuario {request.user.id} intentó agregar más unidades de las disponibles: actual={item.cantidad}, adicional={cantidad}, stock={producto.stock}")
            message = f"No se puede agregar {cantidad} unidades más. Ya tienes {item.cantidad} en el carrito y solo hay {producto.stock} disponibles."
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': message
                })
            messages.warning(request, message)
            return redirect('marketplace:ver_carrito')
            
        item.cantidad += cantidad
        item.save()
        created = False
        logger.info(f"Usuario {request.user.id} actualizó cantidad de producto {producto_id} en carrito: nuevo total={item.cantidad}")
    except CarritoItem.DoesNotExist:
        item = CarritoItem.objects.create(
            usuario=request.user,
            producto=producto,
            cantidad=cantidad
        )
        created = True
        logger.info(f"Usuario {request.user.id} agregó producto {producto_id} al carrito: cantidad={cantidad}")

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
def notify_vendor_stock(request, producto, remaining_stock=0):
    """
    Notifica al vendedor cuando el stock de un producto llega a cero o está bajo
    """
    vendedor = producto.vendedor
    tipo_notificacion = 'STOCK_AGOTADO' if remaining_stock == 0 else 'STOCK_BAJO'
    
    logger.info(f"Enviando notificación de {tipo_notificacion} al vendedor para producto {producto.id}")
    
    # Primero crear una notificación en la plataforma
    try:
        notificacion = NotificacionMarketplace.crear_notificacion_stock(
            usuario=vendedor,
            producto=producto,
            tipo=tipo_notificacion
        )
        logger.info(f"Notificación de plataforma creada con ID {notificacion.id}")
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error al crear notificación en la plataforma: {str(e)}\n{error_traceback}")
    
    # Luego intentar enviar un email
    try:
        # Verificar si el usuario tiene email
        if not hasattr(vendedor, 'email'):
            logger.warning(f"No se puede enviar email: Vendedor de producto {producto.id} no tiene email")
            return False
            
        # Obtener el dominio actual del sitio
        current_site = get_current_site(request)
        domain = current_site.domain
        
        # Construir URL para editar el producto
        edit_url = f"{request.scheme}://{domain}{reverse('marketplace:editar_producto', args=[producto.id])}"
        
        # Asunto del email
        subject = f'¡Alerta de Stock! Tu producto "{producto.nombre}" {"se ha agotado" if remaining_stock == 0 else "tiene stock bajo"}'
        
        # Cuerpo del mensaje
        html_message = f"""
        <p>Hola {vendedor.email},</p>
        
        <p>Tu producto <strong>{producto.nombre}</strong> {"se ha quedado sin stock" if remaining_stock == 0 else "está con stock bajo"}.</p>
        
        <p>Información del producto:</p>
        <ul>
            <li><strong>ID:</strong> {producto.id}</li>
            <li><strong>Nombre:</strong> {producto.nombre}</li>
            <li><strong>Stock actual:</strong> {remaining_stock}</li>
        </ul>
        
        <p>Te recomendamos actualizar el stock {"lo antes posible para no perder ventas" if remaining_stock == 0 else "cuando sea conveniente"}.</p>
        
        <p><a href="{edit_url}">Haz clic aquí para editar tu producto</a></p>
        
        <p>Atentamente,<br>
        El equipo de Campo Unido</p>
        """
        
        # Versión de texto plano
        plain_message = strip_tags(html_message)
        
        # Enviar email
        send_mail(
            subject,
            plain_message,
            'noreply@campounido.com',  # Remitente
            [vendedor.email],  # Destinatario
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Email de notificación enviado a {vendedor.email} para producto {producto.id}")
        return True
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error al enviar email de notificación: {str(e)}\n{error_traceback}")
        return False


@login_required
def checkout(request):
    """
    Proceso de finalización de compra
    """
    logger.info(f"Usuario {request.user.id} inició proceso de checkout")
    
    # Verificar si hay productos en el carrito
    items = CarritoItem.objects.filter(usuario=request.user).select_related('producto')
    if not items.exists():
        logger.warning(f"Usuario {request.user.id} intentó checkout con carrito vacío")
        messages.warning(request, 'No tienes productos en tu carrito')
        return redirect('marketplace:ver_carrito')
    
    logger.info(f"Usuario {request.user.id} tiene {items.count()} productos en su carrito")
    
    # Calcular total
    total = sum(item.subtotal for item in items)
    logger.info(f"Total del carrito: ${total}")
    
    # Procesar el checkout
    if request.method == 'POST':
        logger.info("Procesando formulario POST de checkout")
        try:
            # Obtener datos del formulario
            nombre_completo = request.POST.get('nombre_completo')
            telefono = request.POST.get('telefono')
            direccion = request.POST.get('direccion')
            ciudad = request.POST.get('ciudad')
            departamento = request.POST.get('departamento')
            codigo_postal = request.POST.get('codigo_postal', '')
            instrucciones_envio = request.POST.get('instrucciones_envio', '')
            metodo_pago = request.POST.get('metodo_pago')
            
            logger.debug(f"Datos de envío: {nombre_completo}, {telefono}, {direccion}, {ciudad}, {departamento}")
            logger.debug(f"Método de pago seleccionado: {metodo_pago}")
            
            # Datos de facturación
            requiere_factura = request.POST.get('requiere_factura') == 'on'
            if requiere_factura:
                razon_social = request.POST.get('razon_social', '')
                rfc = request.POST.get('rfc', '')
                direccion_fiscal = request.POST.get('direccion_fiscal', '')
                logger.debug(f"Requiere factura: Razón Social={razon_social}, RFC={rfc}")
            else:
                razon_social = ''
                rfc = ''
                direccion_fiscal = ''
                logger.debug("No requiere factura")
            
            # Validar datos obligatorios
            if not all([nombre_completo, telefono, direccion, ciudad, departamento]):
                logger.warning("Campos obligatorios de envío incompletos")
                messages.error(request, 'Por favor, completa todos los campos obligatorios de envío')
                return render(request, 'marketplace/checkout.html', {
                    'items': items,
                    'total': total,
                })
            
            # Verificar stock suficiente para todos los productos
            logger.info("Verificando stock disponible")
            productos_sin_stock = []
            for item in items:
                if item.cantidad > item.producto.stock:
                    logger.warning(f"Stock insuficiente para producto {item.producto.id} - {item.producto.nombre}: Solicitado={item.cantidad}, Disponible={item.producto.stock}")
                    productos_sin_stock.append({
                        'nombre': item.producto.nombre,
                        'stock_disponible': item.producto.stock,
                        'cantidad_solicitada': item.cantidad
                    })
            
            if productos_sin_stock:
                for producto in productos_sin_stock:
                    error_msg = f"No hay suficiente stock para '{producto['nombre']}'. Disponible: {producto['stock_disponible']}, Solicitado: {producto['cantidad_solicitada']}"
                    logger.warning(error_msg)
                    messages.error(request, error_msg)
                return render(request, 'marketplace/checkout.html', {
                    'items': items,
                    'total': total,
                })
            
            # Formato de dirección para almacenar
            direccion_completa = f"{nombre_completo}\n{telefono}\n{direccion}\n{ciudad}, {departamento}"
            if codigo_postal:
                direccion_completa += f"\nCP: {codigo_postal}"
            if instrucciones_envio:
                direccion_completa += f"\nInstrucciones: {instrucciones_envio}"
                
            # Agregar datos de facturación si se requiere
            info_facturacion = ""
            if requiere_factura:
                info_facturacion = f"Facturación:\nRazón Social: {razon_social}\nRFC/NIF: {rfc}\nDirección Fiscal: {direccion_fiscal}"
            
            compra = None
            orden = None
            
            logger.info("Iniciando transacción para crear compra")
            # Iniciar transacción para garantizar consistencia
            with transaction.atomic():
                # Crear la compra
                logger.debug("Creando registro de compra")
                compra = Compra.objects.create(
                    usuario=request.user,
                    estado='pagado',  # Simulamos que el pago fue exitoso
                    direccion_envio=direccion_completa,
                    metodo_pago='Simulado' if metodo_pago == 'simulado' else metodo_pago,
                    total=total
                )
                logger.info(f"Compra creada con ID: {compra.id}")
                
                # Productos que quedaron con stock cero y requieren notificación
                productos_sin_stock = []
                
                # Crear detalles de la compra
                logger.debug("Creando detalles de compra")
                for item in items:
                    DetalleCompra.objects.create(
                        compra=compra,
                        producto=item.producto,
                        cantidad=item.cantidad,
                        precio_unitario=item.producto.precio
                    )
                    logger.debug(f"Detalle agregado: {item.cantidad} x {item.producto.nombre} a ${item.producto.precio}")
                    
                    # Actualizar stock del producto
                    producto = item.producto
                    if producto.stock < item.cantidad:
                        # Si llegamos aquí, significa que alguien más redujo el stock mientras procesábamos
                        error_msg = f"Stock insuficiente para {producto.nombre} (reducción concurrente)"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    
                    # Verificar si el producto quedará sin stock después de la compra
                    nuevo_stock = producto.stock - item.cantidad
                    producto.stock = nuevo_stock
                    producto.save()
                    logger.debug(f"Stock actualizado para {producto.nombre}: Nuevo stock={producto.stock}")
                    
                    # Si el producto proviene del inventario, actualizar también el inventario
                    try:
                        from apps.inventario.models import ProductoInventario
                        
                        # Verificar si hay una referencia directa al producto en inventario
                        if producto.producto_inventario_id:
                            try:
                                # Buscar producto en inventario por ID referenciado
                                producto_inventario = ProductoInventario.objects.get(
                                    id=producto.producto_inventario_id,
                                    propietario=producto.vendedor
                                )
                                
                                logger.info(f"Actualizando stock en inventario para producto {producto_inventario.id}: {producto_inventario.nombre_producto}")
                                # Actualizar el stock en el inventario
                                producto_inventario.cantidad_disponible -= item.cantidad
                                producto_inventario.save()
                                logger.info(f"Stock de inventario actualizado: {producto_inventario.cantidad_disponible}")
                            except ProductoInventario.DoesNotExist:
                                logger.warning(f"No se encontró el producto de inventario con ID {producto.producto_inventario_id}")
                                # Si no se encuentra por ID, intentar buscar por nombre como respaldo
                                producto_inventario = ProductoInventario.objects.filter(
                                    nombre_producto=producto.nombre,
                                    propietario=producto.vendedor
                                ).first()
                                
                                if producto_inventario:
                                    logger.info(f"Producto encontrado por nombre: {producto_inventario.id}: {producto_inventario.nombre_producto}")
                                    producto_inventario.cantidad_disponible -= item.cantidad
                                    producto_inventario.save()
                                    logger.info(f"Stock de inventario actualizado: {producto_inventario.cantidad_disponible}")
                        else:
                            # Método alternativo: buscar por nombre
                            producto_inventario = ProductoInventario.objects.filter(
                                nombre_producto=producto.nombre,
                                propietario=producto.vendedor
                            ).first()
                            
                            if producto_inventario:
                                logger.info(f"Actualizando stock en inventario para producto {producto_inventario.id}: {producto_inventario.nombre_producto}")
                                # Actualizar el stock en el inventario
                                producto_inventario.cantidad_disponible -= item.cantidad
                                producto_inventario.save()
                                logger.info(f"Stock de inventario actualizado: {producto_inventario.cantidad_disponible}")
                    except Exception as e:
                        # Si hay un error, registrarlo pero no interrumpir la compra
                        error_traceback = traceback.format_exc()
                        logger.error(f"Error al actualizar stock en inventario: {str(e)}\n{error_traceback}")
                    
                    # Si el stock llega a cero o es muy bajo, lo marcamos para notificación
                    if nuevo_stock == 0:
                        productos_sin_stock.append(producto)
                    elif nuevo_stock <= 5:  # Notificamos también si queda poco stock (umbral configurable)
                        productos_sin_stock.append(producto)
                
                # Crear orden asociada con notas que incluyan la facturación si se solicitó
                notas = info_facturacion if info_facturacion else None
                logger.debug("Creando orden asociada a la compra")
                orden = Orden.objects.create(
                    compra=compra,
                    estado='pagada',  # Simulamos que ya está pagada
                    notas=notas
                )
                logger.info(f"Orden creada: {orden.numero_orden}")
                
                # Vaciar el carrito
                logger.debug("Vaciando el carrito")
                items.delete()
                
            # Si llegamos aquí, la transacción fue exitosa
            logger.info("Transacción completada exitosamente")
            
            # Enviar notificaciones de stock a los vendedores (después de la transacción para no bloquear el checkout)
            for producto in productos_sin_stock:
                logger.info(f"Enviando notificación de stock bajo para {producto.nombre} (stock={producto.stock})")
                notify_vendor_stock(request, producto, producto.stock)
            
            # Enviar mensaje de éxito que se mostrará después
            messages.success(request, f'¡Compra realizada con éxito! Tu número de orden es: {orden.numero_orden}')
            
            # Redirigir al detalle del pedido con mensaje de éxito
            logger.debug("Almacenando información de compra exitosa en sesión")
            request.session['compra_exitosa'] = {
                'numero_orden': orden.numero_orden,
                'compra_id': compra.id,
                'fecha': timezone.localtime(compra.fecha_compra).strftime("%d/%m/%Y %H:%M")
            }
            
            # Renderizar la página de compra completa 
            logger.info(f"Redirigiendo a página de checkout completo para compra {compra.id}")
            return render(request, 'marketplace/checkout_complete.html', {
                'compra': compra,
                'orden': orden
            })
                
        except ValueError as e:
            # Capturar errores específicos de nuestra validación
            logger.error(f"Error de validación en checkout: {str(e)}")
            messages.error(request, str(e))
            return render(request, 'marketplace/checkout.html', {
                'items': items,
                'total': total,
            })
        except IntegrityError as e:
            # Capturar errores de integridad de la base de datos
            logger.error(f"Error de integridad en checkout: {str(e)}")
            messages.error(request, "Error al procesar la compra: no se puede reducir el stock por debajo de cero")
            return render(request, 'marketplace/checkout.html', {
                'items': items,
                'total': total,
            })
        except Exception as e:
            # Capturar cualquier otro error
            error_traceback = traceback.format_exc()
            logger.error(f"Error inesperado en checkout: {str(e)}\n{error_traceback}")
            messages.error(request, f"Error inesperado al procesar la compra: {str(e)}")
            return render(request, 'marketplace/checkout.html', {
                'items': items,
                'total': total,
            })
    
    # Mostrar la página de checkout (método GET)
    logger.info("Mostrando formulario de checkout (GET)")
    context = {
        'items': items,
        'total': total,
    }
    
    return render(request, 'marketplace/checkout.html', context)


@login_required
def lista_pedidos(request):
    """
    Muestra los pedidos del usuario con estadísticas y filtrado
    """
    # Aplicar filtros si existen
    filtro_estado = request.GET.get('estado')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    # Consulta base
    pedidos = Compra.objects.filter(usuario=request.user).order_by('-fecha_compra')
    
    # Aplicar filtros
    if filtro_estado:
        pedidos = pedidos.filter(estado=filtro_estado)
    
    if fecha_desde:
        pedidos = pedidos.filter(fecha_compra__gte=fecha_desde)
    
    if fecha_hasta:
        # Agregar un día al fecha_hasta para incluir el día completo
        from datetime import datetime, timedelta
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            fecha_hasta_obj = fecha_hasta_obj + timedelta(days=1)
            pedidos = pedidos.filter(fecha_compra__lt=fecha_hasta_obj)
        except ValueError:
            # Si hay error al parsear la fecha, ignoramos este filtro
            pass
    
    # Calcular estadísticas
    from django.db.models import Sum, Count
    
    # Total de pedidos por estado
    pedidos_por_estado = Compra.objects.filter(usuario=request.user).values('estado').annotate(
        total=Count('id')
    )
    
    # Contadores específicos
    pedidos_completados = sum(item['total'] for item in pedidos_por_estado if item['estado'] in ['entregado'])
    pedidos_proceso = sum(item['total'] for item in pedidos_por_estado if item['estado'] in ['pagado', 'procesando', 'enviado'])
    
    # Total gastado
    total_gastado = Compra.objects.filter(usuario=request.user).aggregate(
        total=Sum('total')
    )['total'] or 0
    
    context = {
        'pedidos': pedidos,
        'pedidos_completados': pedidos_completados,
        'pedidos_proceso': pedidos_proceso,
        'total_gastado': total_gastado,
        'pedidos_por_estado': pedidos_por_estado
    }
    
    return render(request, 'marketplace/mis_compras.html', context)


@login_required
def detalle_pedido(request, pedido_id):
    """
    Muestra los detalles de un pedido
    """
    pedido = get_object_or_404(Compra, id=pedido_id, usuario=request.user)
    items = pedido.detalles.all().select_related('producto')
    
    # Verificar si hay un mensaje de compra exitosa en la sesión
    compra_exitosa = request.session.pop('compra_exitosa', None)
    if compra_exitosa and str(compra_exitosa['compra_id']) == str(pedido_id):
        messages.success(
            request, 
            f'¡Tu compra se ha realizado con éxito! El número de orden es: {compra_exitosa["numero_orden"]}. '
            f'Fecha: {compra_exitosa["fecha"]}'
        )
    
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
    # Get vendor's products
    productos = Producto.objects.filter(
        vendedor=request.user).order_by('-fecha_creacion')

    # Get product IDs sold by this vendor
    productos_ids = productos.values_list('id', flat=True)
    
    # Try multiple approaches to find sales for this vendor
    # First: Get all sales containing vendor's products using direct filter on vendor with prefetch for optimization
    ventas = Compra.objects.filter(
        detalles__producto__vendedor=request.user  # Direct filter on vendor
    ).distinct().select_related('usuario', 'orden').prefetch_related(
        'detalles__producto'
    ).order_by('-fecha_compra')
    
    # Log the query and number of sales found (for debugging)
    logger.debug(f"Vendedor {request.user.id} - Encontradas {ventas.count()} ventas")
    
    # Get DetalleCompra objects for this vendor to compute products sold
    detalles_vendidos = DetalleCompra.objects.filter(
        producto__vendedor=request.user
    )
    
    # Count total items sold
    productos_vendidos_count = detalles_vendidos.aggregate(
        total=Sum('cantidad')
    )['total'] or 0
    
    # For diagnostic purposes, let's check if we're getting sales data using different approaches
    if not ventas.exists():
        logger.warning(f"No se encontraron ventas para el vendedor {request.user.id} usando el método principal")
        
        # Try alternative approach with product IDs
        alt_ventas = Compra.objects.filter(
            detalles__producto__id__in=productos_ids
        ).distinct().order_by('-fecha_compra')
        
        logger.debug(f"Vendedor {request.user.id} - Método alternativo encontró {alt_ventas.count()} ventas")
        
        if alt_ventas.exists():
            # Use this alternative if it found something
            ventas = alt_ventas.select_related('usuario', 'orden').prefetch_related('detalles__producto')
            logger.info(f"Usando método alternativo para mostrar ventas al vendedor {request.user.id}")
    
    # Preparar datos para gráficas
    import json
    from datetime import datetime, timedelta
    
    # 1. Datos de ventas por fecha (últimos 30 días)
    try:
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        logger.debug(f"Generando datos de gráficos para usuario {request.user.id}, período: {fecha_inicio} a {fecha_fin}")
        
        # Diccionario para almacenar ventas por fecha
        ventas_por_fecha = {}
        # Inicializar todas las fechas con valor 0
        for i in range(31):
            fecha = (fecha_fin - timedelta(days=i)).date()
            ventas_por_fecha[fecha.strftime('%Y-%m-%d')] = 0
        
        # Consulta para ventas por fecha
        ventas_periodo = Compra.objects.filter(
            detalles__producto__vendedor=request.user,
            fecha_compra__gte=fecha_inicio,
            fecha_compra__lte=fecha_fin
        ).annotate(
            fecha_str=TruncDate('fecha_compra')
        ).values('fecha_str').annotate(
            total=Sum(F('detalles__cantidad') * F('detalles__precio_unitario'), 
                      filter=Q(detalles__producto__vendedor=request.user))
        ).order_by('fecha_str')
        
        logger.debug(f"Ventas encontradas en el período: {ventas_periodo.count()}")
        
        # Asignar valores a las fechas correspondientes
        for venta in ventas_periodo:
            fecha_str = venta['fecha_str'].strftime('%Y-%m-%d')
            if fecha_str in ventas_por_fecha:
                ventas_por_fecha[fecha_str] = float(venta['total'])
        
        # Convertir a listas ordenadas
        fechas = sorted(list(ventas_por_fecha.keys()))
        valores = [ventas_por_fecha[fecha] for fecha in fechas]
        
        # Formatear fechas para mejor visualización
        fechas_formato = []
        for fecha in fechas:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
            fechas_formato.append(fecha_obj.strftime('%d/%m'))
        
        logger.debug(f"Datos de gráfica: {len(fechas_formato)} fechas, {len(valores)} valores")
        
        ventas_data = {
            'fechas': json.dumps(fechas_formato),
            'valores': json.dumps(valores)
        }
        
        logger.debug(f"JSON generado para gráficas de ventas: {len(ventas_data['fechas'])} caracteres (fechas), {len(ventas_data['valores'])} caracteres (valores)")
        
    except Exception as e:
        logger.error(f"Error generando datos de ventas por fecha: {str(e)}")
        ventas_data = {
            'fechas': json.dumps([]),
            'valores': json.dumps([])
        }
    
    # 2. Datos para distribución de stock
    try:
        productos_sin_stock = productos.filter(stock=0).count()
        productos_stock_bajo = productos.filter(stock__gt=0, stock__lte=5).count()
        productos_stock_adecuado = productos.filter(stock__gt=5).count()
        
        stock_data = json.dumps([
            productos_sin_stock,
            productos_stock_bajo,
            productos_stock_adecuado
        ])
    except Exception as e:
        logger.error(f"Error generando datos de distribución de stock: {str(e)}")
        stock_data = json.dumps([0, 0, 0])
    
    # 3. Datos para productos más vendidos
    try:
        top_productos_vendidos = DetalleCompra.objects.filter(
            producto__vendedor=request.user
        ).values('producto').annotate(
            total_vendido=Sum('cantidad'),
            nombre=F('producto__nombre')
        ).order_by('-total_vendido')[:5]
        
        top_productos = {
            'nombres': json.dumps([p['nombre'] for p in top_productos_vendidos]),
            'cantidades': json.dumps([p['total_vendido'] for p in top_productos_vendidos])
        }
    except Exception as e:
        logger.error(f"Error generando datos de productos más vendidos: {str(e)}")
        top_productos = {
            'nombres': json.dumps([]),
            'cantidades': json.dumps([])
        }
    
    context = {
        'productos': productos,
        'ventas': ventas,
        'stats': {
            'total_productos': productos.count(),
            'productos_activos': productos.filter(activo=True).count(),
            'productos_vendidos': productos_vendidos_count,
        },
        'ventas_data': ventas_data,
        'stock_data': stock_data,
        'top_productos': top_productos
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
    
    # Obtener todas las categorías activas
    categorias = CategoriaProducto.objects.filter(activa=True)
    
    context = {
        'form': form,
        'producto': producto,
        'titulo': 'Editar Producto',
        'accion': 'Actualizar',
        'categorias': categorias
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
    from .models import Producto, CategoriaProducto, ProductoImagen

    # Inicializar el formulario con los productos del inventario del usuario
    if request.method == 'POST':
        form = ProductoInventarioMarketplaceForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            try:
                # Obtener datos del formulario
                producto_id = form.cleaned_data['producto_inventario']
                cantidad = form.cleaned_data['cantidad_a_vender']
                precio = form.cleaned_data['precio_base']
                descripcion = form.cleaned_data['descripcion']
                destacado = form.cleaned_data['destacado']
                es_organico = form.cleaned_data['es_organico']
                
                # Obtener el producto del inventario
                producto_inv = ProductoInventario.objects.get(
                    id=producto_id, propietario=request.user)
                
                # Verificar si hay suficiente stock
                if producto_inv.cantidad_disponible < cantidad:
                    messages.error(request, f'No hay suficiente stock. Disponible: {producto_inv.cantidad_disponible}, Solicitado: {cantidad}')
                    return render(request, 'marketplace/agregar_producto_inventario.html', {'form': form})
                
                # Crear categoría en el marketplace si no existe
                categoria, created = CategoriaProducto.objects.get_or_create(
                    nombre=producto_inv.categoria_producto.nombre_categoria,
                    defaults={
                        'descripcion': producto_inv.categoria_producto.descripcion,
                        'activa': True
                    }
                )
                
                # Usar descripción personalizada o la del producto
                descripcion_final = descripcion if descripcion else producto_inv.descripcion_producto
                
                # Crear el producto en el marketplace
                producto = Producto(
                    nombre=producto_inv.nombre_producto,
                    descripcion=descripcion_final,
                    precio=precio,
                    stock=cantidad,
                    categoria=categoria,
                    vendedor=request.user,
                    destacado=destacado,
                    estado='disponible',
                    producto_inventario_id=producto_inv.id  # Almacenar referencia al producto del inventario
                )
                
                # Guardar imagen principal si se proporcionó
                if form.cleaned_data['imagen_principal']:
                    producto.imagen = form.cleaned_data['imagen_principal']
                
                producto.save()
                
                # Guardar imágenes adicionales si se proporcionaron
                imagenes_adicionales = []
                for i in range(1, 4):
                    imagen_field = f'imagen_adicional{i}'
                    if form.cleaned_data[imagen_field]:
                        ProductoImagen.objects.create(
                            producto=producto,
                            imagen=form.cleaned_data[imagen_field],
                            orden=i
                        )
                        imagenes_adicionales.append(i)
                
                # Actualizar stock en el inventario (opcional - descomentar si se quiere reducir el stock)
                # producto_inv.cantidad_disponible -= cantidad
                # producto_inv.save()
                
                messages.success(
                    request, f'Producto "{producto.nombre}" agregado al marketplace correctamente.')
                
                if imagenes_adicionales:
                    messages.info(request, f'Se agregaron {len(imagenes_adicionales)} imágenes adicionales.')
                
                return redirect('marketplace:mi_tienda')
                
            except ProductoInventario.DoesNotExist:
                messages.error(request, 'El producto seleccionado no existe o no te pertenece.')
            except Exception as e:
                messages.error(request, f'Error al procesar el formulario: {str(e)}')
    else:
        # GET request - mostrar formulario vacío
        form = ProductoInventarioMarketplaceForm(user=request.user)
    
    # Obtener productos del inventario para debugging
    productos_inventario = ProductoInventario.objects.filter(propietario=request.user)
    
    context = {
        'form': form,
        'productos_inventario': productos_inventario,
        'title': 'Agregar Producto desde Inventario'
    }
    
    return render(request, 'marketplace/agregar_producto_inventario.html', context)


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
    # Modificamos para obtener categorías que nosotros creamos (Riego, Semillas, etc.)
    categorias_inventario = CategoriaInventario.objects.all()

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

# Vistas para gestionar direcciones de envío

@login_required
def mis_direcciones(request):
    """
    Muestra las direcciones de envío del usuario
    """
    direcciones = DireccionEnvio.objects.filter(usuario=request.user)
    return render(request, 'marketplace/mis_direcciones.html', {
        'direcciones': direcciones
    })

@login_required
def agregar_direccion(request):
    """
    Agrega una nueva dirección de envío
    """
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre_completo = request.POST.get('nombre_completo')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')
        departamento = request.POST.get('departamento')
        codigo_postal = request.POST.get('codigo_postal', '')
        notas_adicionales = request.POST.get('notas_adicionales', '')
        predeterminada = request.POST.get('predeterminada') == 'on'
        
        if not all([nombre_completo, telefono, direccion, ciudad, departamento]):
            messages.error(request, 'Por favor, completa todos los campos obligatorios')
            return render(request, 'marketplace/agregar_direccion.html')
        
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
        
        # Si venimos del checkout, volver ahí
        if 'next' in request.GET and request.GET['next'] == 'checkout':
            return redirect('marketplace:checkout')
        
        return redirect('marketplace:mis_direcciones')
    
    return render(request, 'marketplace/agregar_direccion.html')

@login_required
def editar_direccion(request, direccion_id):
    """
    Edita una dirección de envío
    """
    direccion = get_object_or_404(DireccionEnvio, id=direccion_id, usuario=request.user)
    
    if request.method == 'POST':
        # Actualizar datos
        nombre_completo = request.POST.get('nombre_completo')
        telefono = request.POST.get('telefono')
        direccion_texto = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')
        departamento = request.POST.get('departamento')
        codigo_postal = request.POST.get('codigo_postal', '')
        notas_adicionales = request.POST.get('notas_adicionales', '')
        predeterminada = request.POST.get('predeterminada') == 'on'
        
        if not all([nombre_completo, telefono, direccion_texto, ciudad, departamento]):
            messages.error(request, 'Por favor, completa todos los campos obligatorios')
            return render(request, 'marketplace/editar_direccion.html', {'direccion': direccion})
        
        # Si es predeterminada, quitar esta marca de las demás direcciones
        if predeterminada and not direccion.predeterminada:
            DireccionEnvio.objects.filter(usuario=request.user, predeterminada=True).update(predeterminada=False)
        
        # Actualizar dirección
        direccion.nombre_completo = nombre_completo
        direccion.telefono = telefono
        direccion.direccion = direccion_texto
        direccion.ciudad = ciudad
        direccion.departamento = departamento
        direccion.codigo_postal = codigo_postal
        direccion.notas_adicionales = notas_adicionales
        direccion.predeterminada = predeterminada
        direccion.save()
        
        messages.success(request, "Dirección actualizada correctamente.")
        return redirect('marketplace:mis_direcciones')
    
    return render(request, 'marketplace/editar_direccion.html', {
        'direccion': direccion
    })

@login_required
def eliminar_direccion(request, direccion_id):
    """
    Elimina una dirección de envío
    """
    direccion = get_object_or_404(DireccionEnvio, id=direccion_id, usuario=request.user)
    
    if request.method == 'POST':
        direccion.delete()
        messages.success(request, "Dirección eliminada correctamente.")
    else:
        messages.error(request, "Método no permitido para eliminar dirección.")
    
    return redirect('marketplace:mis_direcciones')

# Función para generar PDF de factura
def generar_factura_pdf(compra, orden):
    """
    Genera un PDF con la factura/comprobante de compra
    """
    logger.info(f"Iniciando generación de factura PDF para orden {orden.numero_orden}")
    
    # Crear buffer para el PDF
    buffer = BytesIO()
    logger.debug("Buffer IO creado")
    
    try:
        # Crear el objeto PDF usando ReportLab
        logger.debug("Creando objeto PDF con ReportLab")
        try:
            p = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            logger.debug(f"Tamaño del PDF: {width}x{height}")
        except Exception as e:
            logger.error(f"Error al inicializar canvas: {str(e)}")
            raise
        
        # Configuración de estilos
        logger.debug("Configurando estilos")
        try:
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=16,
                alignment=1,
                spaceAfter=0.3*inch
            )
            logger.debug("Estilos configurados correctamente")
        except Exception as e:
            logger.error(f"Error al configurar estilos: {str(e)}")
            raise
        
        # Título del documento
        try:
            p.setTitle(f"Comprobante de Compra - {orden.numero_orden}")
            logger.debug(f"Título del PDF establecido: Comprobante de Compra - {orden.numero_orden}")
        except Exception as e:
            logger.error(f"Error al establecer título: {str(e)}")
            raise
        
        # Encabezado con logo
        try:
            logger.debug("Dibujando encabezado")
            p.setFont('Helvetica-Bold', 16)
            p.drawString(1*cm, height - 2*cm, "CAMPO UNIDO")
            p.setFont('Helvetica', 12)
            p.drawString(1*cm, height - 2.7*cm, "Marketplace de productos agrícolas")
        except Exception as e:
            logger.error(f"Error al dibujar encabezado: {str(e)}")
            raise
        
        # Información de la compra
        try:
            logger.debug("Dibujando información de la compra")
            p.setFont('Helvetica-Bold', 14)
            p.drawString(1*cm, height - 4*cm, f"COMPROBANTE DE COMPRA #{orden.numero_orden}")
            
            p.setFont('Helvetica', 10)
            fecha = timezone.localtime(compra.fecha_compra).strftime("%d/%m/%Y %H:%M")
            p.drawString(1*cm, height - 5*cm, f"Fecha: {fecha}")
        except Exception as e:
            logger.error(f"Error al dibujar información de compra: {str(e)}")
            raise
        
        # Fix: Usar un enfoque más robusto para obtener información del usuario
        try:
            logger.debug("Obteniendo información del cliente")
            nombre_cliente = "Cliente"  # Valor por defecto
            
            # Intentar obtener cualquier identificador disponible
            if hasattr(compra.usuario, 'get_full_name') and callable(compra.usuario.get_full_name):
                logger.debug("Usuario tiene método get_full_name")
                nombre_completo = compra.usuario.get_full_name()
                if nombre_completo:
                    nombre_cliente = nombre_completo
                    logger.debug(f"Usando nombre completo: {nombre_cliente}")
            elif hasattr(compra.usuario, 'email'):
                logger.debug("Usuario tiene atributo email")
                nombre_cliente = compra.usuario.email
                logger.debug(f"Usando email: {nombre_cliente}")
            elif hasattr(compra.usuario, 'username'):
                logger.debug("Usuario tiene atributo username")
                nombre_cliente = compra.usuario.username
                logger.debug(f"Usando username: {nombre_cliente}")
            elif hasattr(compra.usuario, 'name'):
                logger.debug("Usuario tiene atributo name")
                nombre_cliente = compra.usuario.name
                logger.debug(f"Usando name: {nombre_cliente}")
            elif hasattr(compra.usuario, '__str__'):
                logger.debug("Usando representación string del usuario")
                nombre_cliente = str(compra.usuario)
                logger.debug(f"Usando __str__: {nombre_cliente}")
            
            logger.debug(f"Cliente identificado como: {nombre_cliente}")
            p.drawString(1*cm, height - 5.5*cm, f"Cliente: {nombre_cliente}")
            
            # Usar estado de forma segura
            if hasattr(compra, 'get_estado_display') and callable(compra.get_estado_display):
                estado_display = compra.get_estado_display()
                logger.debug(f"Usando get_estado_display(): {estado_display}")
            else:
                estado_display = compra.estado
                logger.debug(f"Usando estado directo: {estado_display}")
                
            p.drawString(1*cm, height - 6*cm, f"Estado: {estado_display}")
        except Exception as e:
            logger.error(f"Error al procesar información del cliente: {str(e)}")
            # No lanzar excepción, seguir con otros elementos
        
        # Detalles de entrega
        try:
            logger.debug("Dibujando datos de envío")
            p.setFont('Helvetica-Bold', 12)
            p.drawString(1*cm, height - 7*cm, "DATOS DE ENVÍO:")
            p.setFont('Helvetica', 10)
            
            # Dividir la dirección de envío en líneas
            y_pos = height - 7.5*cm
            if compra.direccion_envio:
                lineas_direccion = compra.direccion_envio.split('\n')
                logger.debug(f"Dirección tiene {len(lineas_direccion)} líneas")
                for linea in lineas_direccion:
                    p.drawString(1*cm, y_pos, linea)
                    y_pos -= 0.5*cm
            else:
                logger.warning("La compra no tiene dirección de envío")
                p.drawString(1*cm, y_pos, "No hay datos de envío disponibles")
                y_pos -= 0.5*cm
        except Exception as e:
            logger.error(f"Error al dibujar datos de envío: {str(e)}")
            y_pos = height - 8*cm  # Establecer valor por defecto para seguir
        
        # Detalles de la facturación si existen
        try:
            if orden.notas and "Facturación:" in orden.notas:
                logger.debug("Procesando datos de facturación")
                p.setFont('Helvetica-Bold', 12)
                p.drawString(1*cm, y_pos - 0.5*cm, "DATOS DE FACTURACIÓN:")
                p.setFont('Helvetica', 10)
                lineas_facturacion = orden.notas.split('\n')
                logger.debug(f"Facturación tiene {len(lineas_facturacion)} líneas")
                y_pos -= 1*cm
                for linea in lineas_facturacion:
                    p.drawString(1*cm, y_pos, linea)
                    y_pos -= 0.5*cm
            else:
                logger.debug("No hay datos de facturación")
        except Exception as e:
            logger.error(f"Error al dibujar datos de facturación: {str(e)}")
            # Seguir con el resto del PDF
        
        # Tabla de productos
        try:
            logger.debug("Obteniendo detalles de productos")
            items = DetalleCompra.objects.filter(compra=compra)
            logger.debug(f"La compra tiene {items.count()} ítems")
            
            data = [['Producto', 'Cantidad', 'Precio Unit.', 'Subtotal']]
            
            for item in items:
                logger.debug(f"Procesando ítem: {item.producto.nombre} x {item.cantidad}")
                data.append([
                    item.producto.nombre,
                    str(item.cantidad),
                    f"${item.precio_unitario:.2f}",
                    f"${(item.cantidad * item.precio_unitario):.2f}"
                ])
            
            # Añadir fila de total
            data.append(['', '', 'TOTAL', f"${compra.total:.2f}"])
        except Exception as e:
            logger.error(f"Error al preparar datos de productos: {str(e)}")
            data = [['Producto', 'Cantidad', 'Precio', 'Subtotal'], 
                   ['Error al cargar detalles', '', '', f"${compra.total:.2f}"]]
        
        # Crear la tabla
        try:
            logger.debug("Creando tabla de productos")
            table = Table(data, colWidths=[8*cm, 2*cm, 3*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('TOPPADDING', (0, -1), (-1, -1), 12),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
                ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ]))
            
            # Ubicar la tabla en el PDF
            logger.debug("Dibujando tabla en el PDF")
            table.wrapOn(p, width - 2*cm, height)
            table_height = len(data) * 0.6*cm + 1*cm  # Estimación de altura
            table_y = min(y_pos - 1*cm, height - 14*cm)  # Asegurar que la tabla no se salga
            table.drawOn(p, 1*cm, table_y - table_height)
            logger.debug(f"Tabla dibujada en y={table_y - table_height}")
        except Exception as e:
            # Si hay algún problema con la tabla, simplemente añadimos un mensaje de error
            logger.error(f"Error al crear o dibujar tabla en PDF: {str(e)}")
            p.setFont('Helvetica-Bold', 12)
            p.drawString(1*cm, y_pos - 1*cm, "Error al generar detalle de productos.")
            p.setFont('Helvetica', 10)
            p.drawString(1*cm, y_pos - 1.5*cm, f"Total de la compra: ${compra.total:.2f}")
        
        # Pie de página
        try:
            logger.debug("Dibujando pie de página")
            p.setFont('Helvetica-Oblique', 8)
            p.drawString(1*cm, 1*cm, "Este documento sirve como comprobante de compra.")
            p.drawString(1*cm, 0.7*cm, f"Campo Unido - Generado el {timezone.now().strftime('%d/%m/%Y %H:%M')}")
        except Exception as e:
            logger.error(f"Error al dibujar pie de página: {str(e)}")
        
        # Cerrar PDF
        logger.debug("Finalizando PDF")
        p.showPage()
        p.save()
        
        # Obtener el PDF del buffer
        buffer.seek(0)
        logger.info("PDF generado correctamente")
        pdf_content = buffer.getvalue()
        
        # Crear un nuevo buffer con el contenido para evitar problemas de buffer cerrado
        result_buffer = BytesIO(pdf_content)
        return result_buffer
        
    except Exception as e:
        # Si hay algún error grave, lo capturamos y replanteamos para manejarlo en la vista
        error_traceback = traceback.format_exc()
        logger.error(f"Error grave al generar PDF: {str(e)}\n{error_traceback}")
        raise
    finally:
        # Asegurarnos de que el buffer original se cierre adecuadamente
        buffer.close()


@login_required
def descargar_factura(request, compra_id):
    """
    Vista para descargar la factura/comprobante de una compra
    """
    logger.info(f"Usuario {request.user.id} solicitó factura para compra {compra_id}")
    
    try:
        logger.debug(f"Buscando compra con ID {compra_id}")
        compra = get_object_or_404(Compra, id=compra_id, usuario=request.user)
        logger.info(f"Compra encontrada: {compra.id} (Estado: {compra.estado})")
        
        try:
            logger.debug(f"Buscando orden asociada a la compra {compra.id}")
            orden = Orden.objects.get(compra=compra)
            logger.info(f"Orden encontrada: {orden.numero_orden}")
        except Orden.DoesNotExist:
            error_msg = f"No se encontró orden asociada a la compra {compra.id}"
            logger.error(error_msg)
            messages.error(request, error_msg)
            return redirect('marketplace:detalle_pedido', pedido_id=compra.id)
        
        # Guardar mensaje de confirmación en la sesión que se mostrará después
        logger.debug("Almacenando información de compra en sesión")
        request.session['compra_exitosa'] = {
            'numero_orden': orden.numero_orden,
            'compra_id': compra.id,
            'fecha': timezone.localtime(compra.fecha_compra).strftime("%d/%m/%Y %H:%M")
        }
        
        try:
            # Generar el PDF
            logger.info(f"Iniciando generación de PDF para orden {orden.numero_orden}")
            pdf_buffer = generar_factura_pdf(compra, orden)
            logger.info(f"PDF generado correctamente para orden {orden.numero_orden}")
            
            # Configurar la respuesta para forzar la descarga
            filename = f"comprobante_{orden.numero_orden}.pdf"
            logger.debug(f"Preparando respuesta con archivo {filename}")
            
            try:
                # Configurar la respuesta HTTP con el contenido del PDF
                response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                response['Content-Length'] = len(pdf_buffer.getvalue())
                
                # Deshabilitar el almacenamiento en caché para evitar problemas
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
                
                logger.info(f"Enviando factura PDF al usuario para orden {orden.numero_orden}")
                return response
            finally:
                # Asegurarnos de cerrar el buffer después de usarlo
                pdf_buffer.close()
            
        except Exception as e:
            # Si hay cualquier error generando el PDF, registrarlo y redirigir al detalle del pedido
            error_traceback = traceback.format_exc()
            logger.error(f"Error generando factura PDF: {str(e)}\n{error_traceback}")
            messages.error(request, f"No se pudo generar el comprobante de compra. Error: {str(e)}")
            return redirect('marketplace:detalle_pedido', pedido_id=compra.id)
            
    except Exception as e:
        # Si hay cualquier otro error, redirigir a la lista de pedidos
        error_traceback = traceback.format_exc()
        logger.error(f"Error al intentar descargar factura: {str(e)}\n{error_traceback}")
        messages.error(request, f"Ocurrió un error al intentar descargar la factura: {str(e)}")
        return redirect('marketplace:lista_pedidos')


@login_required
def debug_checkout(request):
    """
    Vista de depuración para identificar problemas en el checkout
    """
    logger.info(f"Usuario {request.user.id} accedió a la vista de depuración del checkout")
    
    # Información general
    user_info = {
        'id': request.user.id,
        'is_authenticated': request.user.is_authenticated,
        'username': getattr(request.user, 'username', 'N/A'),
        'email': getattr(request.user, 'email', 'N/A'),
    }
    
    # Información del carrito
    items = CarritoItem.objects.filter(usuario=request.user).select_related('producto')
    
    cart_items = []
    total = 0
    problemas_stock = []
    
    for item in items:
        subtotal = item.cantidad * item.producto.precio
        total += subtotal
        
        cart_item = {
            'id': item.id,
            'producto_id': item.producto.id,
            'nombre': item.producto.nombre,
            'cantidad': item.cantidad,
            'precio': float(item.producto.precio),
            'subtotal': float(subtotal),
            'stock_disponible': item.producto.stock,
            'stock_suficiente': item.producto.stock >= item.cantidad
        }
        
        # Verificar si hay problemas de stock
        if item.cantidad > item.producto.stock:
            problemas_stock.append({
                'producto': item.producto.nombre,
                'solicitado': item.cantidad,
                'disponible': item.producto.stock,
                'faltante': item.cantidad - item.producto.stock
            })
        
        cart_items.append(cart_item)
    
    # Información de sesión
    session_data = {k: v for k, v in request.session.items() if k != '_auth_user_id'}
    
    # Información de mensajes
    message_list = []
    storage = messages.get_messages(request)
    for message in storage:
        message_list.append({
            'level': message.level_tag,
            'message': message.message
        })
    
    # Historial de compras recientes
    compras_recientes = Compra.objects.filter(
        usuario=request.user
    ).order_by('-fecha_compra')[:5]
    
    compras_info = []
    for compra in compras_recientes:
        # Verificar si tiene orden asociada
        try:
            orden = Orden.objects.get(compra=compra)
            orden_info = {
                'numero_orden': orden.numero_orden,
                'estado': orden.estado,
                'notas': orden.notas[:100] + '...' if orden.notas and len(orden.notas) > 100 else orden.notas
            }
        except Orden.DoesNotExist:
            orden_info = None
        
        compra_info = {
            'id': compra.id,
            'fecha': compra.fecha_compra.strftime('%Y-%m-%d %H:%M:%S'),
            'estado': compra.estado,
            'total': float(compra.total),
            'orden': orden_info
        }
        compras_info.append(compra_info)
    
    context = {
        'user_info': user_info,
        'cart_items': cart_items,
        'cart_total': float(total),
        'cart_count': len(cart_items),
        'problemas_stock': problemas_stock,
        'session_data': session_data,
        'messages': message_list,
        'compras_recientes': compras_info,
        'debug_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    return render(request, 'marketplace/debug_checkout.html', context)

@login_required
def debug_ventas(request):
    """
    Vista de depuración para diagnosticar problemas con las ventas
    """
    logger.info(f"Usuario {request.user.id} accedió a la vista de depuración de ventas")
    
    # Get products of this vendor
    productos = Producto.objects.filter(vendedor=request.user)
    productos_ids = list(productos.values_list('id', flat=True))
    
    # Get all sales in the system
    todas_ventas = Compra.objects.all().order_by('-fecha_compra')[:50]  # Limit to the most recent 50
    
    # Get all sales that contain any products from this vendor
    # Using two different query approaches for comparison
    ventas_por_producto = Compra.objects.filter(
        detalles__producto__id__in=productos_ids
    ).distinct().order_by('-fecha_compra')
    
    ventas_por_vendedor = Compra.objects.filter(
        detalles__producto__vendedor=request.user
    ).distinct().order_by('-fecha_compra')
    
    # Get all sale details for this vendor's products
    detalles_ventas = DetalleCompra.objects.filter(
        producto__vendedor=request.user
    ).select_related('compra', 'producto').order_by('-compra__fecha_compra')
    
    # Count products sold
    productos_vendidos = DetalleCompra.objects.filter(
        producto__vendedor=request.user
    ).values('producto').annotate(
        total_vendidos=Sum('cantidad')
    )
    
    # Context data
    context = {
        'productos': productos,
        'productos_ids': productos_ids,
        'todas_ventas': todas_ventas,
        'todas_ventas_count': todas_ventas.count(),
        'ventas_por_producto': ventas_por_producto,
        'ventas_por_producto_count': ventas_por_producto.count(),
        'ventas_por_vendedor': ventas_por_vendedor,
        'ventas_por_vendedor_count': ventas_por_vendedor.count(),
        'detalles_ventas': detalles_ventas,
        'detalles_ventas_count': detalles_ventas.count(),
        'productos_vendidos': productos_vendidos,
    }
    
    return render(request, 'marketplace/debug_ventas.html', context)

@login_required
def api_producto_inventario(request, producto_id):
    """
    API para obtener información de un producto de inventario por su ID
    """
    from apps.inventario.models import ProductoInventario

    try:
        # Obtener el producto del inventario que pertenece al usuario
        producto = ProductoInventario.objects.get(
            id=producto_id, 
            propietario=request.user
        )
        
        # Devolver datos en formato JSON
        return JsonResponse({
            'success': True,
            'id': producto.id,
            'nombre': producto.nombre_producto,
            'descripcion': producto.descripcion_producto or '',
            'cantidad_disponible': float(producto.cantidad_disponible),
            'precio_venta': float(producto.precio_venta),
            'precio_compra': float(producto.precio_compra),
            'categoria': producto.categoria_producto.nombre_categoria,
            'unidad_medida': str(producto.unidad_medida) if producto.unidad_medida else 'unidades',
        })
    except ProductoInventario.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Producto no encontrado o no tienes permisos para acceder a él'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener información del producto: {str(e)}'
        }, status=500)
