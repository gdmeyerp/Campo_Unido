from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Pais, Estado, Ciudad, Ubicacion, AreaServicio, PreferenciaUbicacion, UbicacionProducto, UsuariosPorCategoria
from .forms import UbicacionForm
from apps.marketplace.models import Producto, CategoriaProducto
import logging
from .utils import RutaOptima
import json

logger = logging.getLogger(__name__)


@login_required
def lista_paises(request):
    """Vista para listar todos los países disponibles."""
    paises = Pais.objects.all().order_by('nombre')
    return render(request, 'ubicaciones/lista_paises.html', {'paises': paises})


@login_required
def estados_por_pais(request, pais_id):
    """Vista para obtener los estados de un país (para AJAX)."""
    pais = get_object_or_404(Pais, id=pais_id)
    estados = Estado.objects.filter(pais=pais)
    return JsonResponse({
        'estados': list(estados.values('id', 'nombre'))
    })


@login_required
def ciudades_por_estado(request, estado_id):
    """Vista para obtener las ciudades de un estado (para AJAX)."""
    estado = get_object_or_404(Estado, id=estado_id)
    ciudades = Ciudad.objects.filter(estado=estado)
    return JsonResponse({
        'ciudades': list(ciudades.values('id', 'nombre'))
    })


@login_required
def mis_ubicaciones(request):
    """Vista para mostrar las ubicaciones del usuario."""
    ubicaciones = Ubicacion.objects.filter(usuario=request.user).select_related('ciudad', 'ciudad__estado', 'ciudad__estado__pais')
    return render(request, 'ubicaciones/mis_ubicaciones.html', {'ubicaciones': ubicaciones})


@login_required
def crear_ubicacion(request):
    """Vista para crear una nueva ubicación."""
    if request.method == 'POST':
        form = UbicacionForm(data=request.POST)
        if form.is_valid():
            ubicacion = form.save(commit=False)
            ubicacion.usuario = request.user
            
            # Si la ubicación se marca como principal, actualizar las demás
            if ubicacion.es_principal:
                Ubicacion.objects.filter(usuario=request.user, es_principal=True).update(es_principal=False)
                
            ubicacion.save()
            messages.success(request, 'Ubicación creada correctamente.')
            return redirect('ubicaciones:mis_ubicaciones')
        else:
            # Manejar errores específicamente
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en el campo {field}: {error}")
    else:
        form = UbicacionForm()

    # Obtener todos los países ordenados alfabéticamente
    paises = Pais.objects.all().order_by('nombre')
    
    return render(request, 'ubicaciones/crear_ubicacion.html', {
        'form': form,
        'paises': paises
    })


@login_required
def editar_ubicacion(request, ubicacion_id):
    """Vista para editar una ubicación existente."""
    ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id, usuario=request.user)
    
    if request.method == 'POST':
        form = UbicacionForm(data=request.POST, instance=ubicacion)
        if form.is_valid():
            # Si se marca como principal, actualizar las demás
            if form.cleaned_data.get('es_principal'):
                Ubicacion.objects.filter(usuario=request.user, es_principal=True).exclude(id=ubicacion.id).update(es_principal=False)
                
            form.save()
            messages.success(request, 'Ubicación actualizada correctamente.')
            return redirect('ubicaciones:mis_ubicaciones')
        else:
            # Manejar errores específicamente
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en el campo {field}: {error}")
    else:
        form = UbicacionForm(instance=ubicacion)
    
    # Obtener todos los países ordenados alfabéticamente
    paises = Pais.objects.all().order_by('nombre')
    
    return render(request, 'ubicaciones/editar_ubicacion.html', {
        'form': form,
        'ubicacion': ubicacion,
        'paises': paises
    })


@login_required
def eliminar_ubicacion(request, ubicacion_id):
    """Vista para eliminar una ubicación."""
    ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id, usuario=request.user)
    
    if request.method == 'POST':
        # Si es la ubicación principal, buscar otra para marcar como principal
        if ubicacion.es_principal:
            otra_ubicacion = Ubicacion.objects.filter(usuario=request.user).exclude(id=ubicacion.id).first()
            if otra_ubicacion:
                otra_ubicacion.es_principal = True
                otra_ubicacion.save()
                
        ubicacion.delete()
        messages.success(request, 'Ubicación eliminada correctamente.')
        return redirect('ubicaciones:mis_ubicaciones')
    
    return render(request, 'ubicaciones/eliminar_ubicacion.html', {'ubicacion': ubicacion})


@login_required
def establecer_principal(request, ubicacion_id):
    """Vista para establecer una ubicación como principal."""
    ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id, usuario=request.user)
    
    # Desmarcar todas las ubicaciones del usuario como no principales
    Ubicacion.objects.filter(usuario=request.user).update(es_principal=False)
    
    # Marcar la ubicación seleccionada como principal
    ubicacion.es_principal = True
    ubicacion.save()
    
    messages.success(request, 'Ubicación establecida como principal.')
    return redirect('ubicaciones:mis_ubicaciones')


@login_required
def buscar_cercanos(request):
    """Vista para buscar personas cercanas a la ubicación del usuario."""
    # Obtener la ubicación principal del usuario
    ubicacion_principal = Ubicacion.objects.filter(usuario=request.user, es_principal=True).first()
    
    # Obtener todas las ubicaciones del usuario actual (excepto la principal)
    mis_ubicaciones = Ubicacion.objects.filter(usuario=request.user).exclude(
        id=ubicacion_principal.id if ubicacion_principal else 0
    ).select_related('ciudad', 'ciudad__estado', 'ciudad__estado__pais')
    
    # Parámetros de búsqueda
    distancia = float(request.GET.get('distancia', 25))  # Valor predeterminado: 25 km
    categoria_id = request.GET.get('categoria')

    logger.info(f"Iniciando búsqueda con parámetros - distancia: {distancia}, categoria_id: {categoria_id}")

    # Obtener productos activos
    productos_query = Producto.objects.filter(
        activo=True, 
        stock__gt=0
    ).select_related('categoria', 'vendedor')
    
    # Si hay una categoría seleccionada, filtrar por ella
    if categoria_id:
        productos_query = productos_query.filter(categoria_id=categoria_id)
        logger.info(f"Filtrando por categoría ID: {categoria_id}")
    
    # Obtener ubicaciones de usuarios (excluyendo al usuario actual)
    # Nota: No filtramos por productos aquí para obtener todas las ubicaciones primero
    ubicaciones_query = Ubicacion.objects.exclude(
        usuario=request.user
    ).filter(
        latitud__isnull=False,
        longitud__isnull=False
    ).select_related(
        'usuario',
        'ciudad',
        'ciudad__estado',
        'ciudad__estado__pais'
    )
    
    logger.info(f"Total ubicaciones encontradas de otros usuarios: {ubicaciones_query.count()}")

    # Diccionario para almacenar ubicaciones con sus productos
    ubicaciones_con_productos = {}
    
    # Procesar cada ubicación y calcular distancias
    for ubicacion in ubicaciones_query:
        # Calcular distancia si hay ubicación principal
        distancia_km = None
        if ubicacion_principal and ubicacion_principal.latitud and ubicacion_principal.longitud:
            if ubicacion.latitud and ubicacion.longitud:
                distancia_km = AreaServicio.calcular_distancia(
                    float(ubicacion_principal.latitud),
                    float(ubicacion_principal.longitud),
                    float(ubicacion.latitud),
                    float(ubicacion.longitud)
                )
                # Filtrar por distancia si está configurada
                if distancia_km is not None and distancia_km > distancia:
                    logger.info(f"Ubicación {ubicacion.id} descartada por distancia: {distancia_km} > {distancia}")
                    continue
                
                logger.info(f"Ubicación {ubicacion.id} a distancia: {distancia_km} km")
        
        # Incluir la ubicación con un listado vacío de productos (se llenará después)
        ubicaciones_con_productos[ubicacion.id] = {
            'ubicacion': ubicacion,
            'distancia': distancia_km,
            'productos': []
        }
    
    # Ahora obtener los productos y asociarlos a las ubicaciones
    for producto in productos_query:
        # Si el producto no es del usuario actual y su vendedor tiene alguna ubicación
        if producto.vendedor.id != request.user.id:
            # Obtener las ubicaciones del vendedor del producto
            ubicaciones_vendedor = [ub.id for ub in ubicaciones_query if ub.usuario_id == producto.vendedor.id]
            
            # Asociar el producto a las ubicaciones del vendedor que están en nuestro diccionario
            for ubicacion_id in ubicaciones_vendedor:
                if ubicacion_id in ubicaciones_con_productos:
                    ubicaciones_con_productos[ubicacion_id]['productos'].append({
                        'id': producto.id,
                        'nombre': producto.nombre,
                        'precio': float(producto.precio),
                        'stock': producto.stock,
                        'imagen_url': producto.imagen.url if producto.imagen else None,
                        'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría'
                    })
                    logger.info(f"Producto {producto.id} ({producto.nombre}) asociado a ubicación {ubicacion_id}")
    
    # Convertir diccionario a lista y eliminar ubicaciones sin productos
    ubicaciones_cercanas = [
        ub_data for ub_id, ub_data in ubicaciones_con_productos.items() 
        if ub_data['productos']  # Solo incluir ubicaciones con productos
    ]
    
    # Ordenar por distancia si hay ubicación principal
    if ubicacion_principal:
        ubicaciones_cercanas.sort(key=lambda x: x['distancia'] if x['distancia'] is not None else float('inf'))
    
    # Obtener categorías para el filtro
    categorias = CategoriaProducto.objects.filter(activa=True).order_by('nombre')

    context = {
        'ubicacion_principal': ubicacion_principal,
        'mis_ubicaciones': mis_ubicaciones,
        'ubicaciones': ubicaciones_cercanas,
        'distancia': distancia,
        'categorias': categorias,
        'categoria_seleccionada': categoria_id
    }
    
    logger.info(f"Total de ubicaciones enviadas al template: {len(ubicaciones_cercanas)}")
    return render(request, 'ubicaciones/buscar_cercanos.html', context)


# API endpoints para AJAX
def api_estados(request, pais_id):
    """API para obtener los estados de un país mediante AJAX."""
    estados = Estado.objects.filter(pais_id=pais_id).order_by('nombre')
    data = {
        'estados': [{'id': estado.id, 'nombre': estado.nombre} for estado in estados]
    }
    return JsonResponse(data)

def api_ciudades(request, estado_id):
    """API para obtener las ciudades de un estado mediante AJAX."""
    ciudades = Ciudad.objects.filter(estado_id=estado_id).order_by('nombre')
    data = {
        'ciudades': [{'id': ciudad.id, 'nombre': ciudad.nombre} for ciudad in ciudades]
    }
    return JsonResponse(data)

@login_required
def configurar_area_servicio(request):
    """Vista para que los productores configuren su área de servicio"""
    if request.method == 'POST':
        ubicacion_id = request.POST.get('ubicacion')
        radio_km = request.POST.get('radio_km')
        
        ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id, usuario=request.user)
        
        area_servicio, created = AreaServicio.objects.update_or_create(
            productor=request.user,
            ubicacion_centro=ubicacion,
            defaults={'radio_km': radio_km}
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Área de servicio actualizada correctamente'
        })
    
    ubicaciones = Ubicacion.objects.filter(usuario=request.user)
    areas_servicio = AreaServicio.objects.filter(productor=request.user)
    
    return render(request, 'ubicaciones/configurar_area_servicio.html', {
        'ubicaciones': ubicaciones,
        'areas_servicio': areas_servicio
    })

@login_required
def actualizar_preferencias_ubicacion(request):
    """Vista para actualizar las preferencias de ubicación del usuario"""
    if request.method == 'POST':
        ubicacion_id = request.POST.get('ubicacion')
        radio_km = request.POST.get('radio_km', 10.0)
        
        ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id, usuario=request.user)
        
        preferencia, created = PreferenciaUbicacion.objects.update_or_create(
            usuario=request.user,
            defaults={
                'ubicacion_preferida': ubicacion,
                'radio_busqueda_km': radio_km
            }
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Preferencias actualizadas correctamente'
        })
    
    ubicaciones = Ubicacion.objects.filter(usuario=request.user)
    preferencia = PreferenciaUbicacion.objects.filter(usuario=request.user).first()
    
    return render(request, 'ubicaciones/preferencias_ubicacion.html', {
        'ubicaciones': ubicaciones,
        'preferencia': preferencia
    })

@login_required
def productos_cercanos(request):
    """Vista para mostrar productos cercanos a la ubicación del usuario"""
    # Obtener parámetros
    categoria_id = request.GET.get('categoria')
    radio_km = request.GET.get('radio_km')
    ubicacion_id = request.GET.get('ubicacion')
    
    # Obtener ubicación del usuario
    if ubicacion_id:
        ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id, usuario=request.user)
    else:
        # Usar ubicación preferida o principal
        preferencia = PreferenciaUbicacion.objects.filter(usuario=request.user).first()
        if preferencia and preferencia.ubicacion_preferida:
            ubicacion = preferencia.ubicacion_preferida
        else:
            ubicacion = Ubicacion.objects.filter(usuario=request.user, es_principal=True).first()
    
    if not ubicacion:
        return render(request, 'ubicaciones/productos_cercanos.html', {
            'error': 'No se ha configurado una ubicación'
        })
    
    # Configurar radio de búsqueda
    if not radio_km:
        preferencia = PreferenciaUbicacion.objects.filter(usuario=request.user).first()
        radio_km = float(preferencia.radio_busqueda_km if preferencia else 10.0)
    else:
        radio_km = float(radio_km)
    
    # Buscar productos cercanos
    categoria = None
    if categoria_id:
        categoria = get_object_or_404(CategoriaProducto, id=categoria_id)
    
    productos_cercanos = UbicacionProducto.encontrar_productos_cercanos(
        ubicacion,
        radio_km=radio_km,
        categoria=categoria
    )
    
    # Obtener categorías para el filtro
    categorias = CategoriaProducto.objects.filter(activa=True)
    
    return render(request, 'ubicaciones/productos_cercanos.html', {
        'productos': productos_cercanos,
        'ubicacion': ubicacion,
        'radio_km': radio_km,
        'categoria_actual': categoria,
        'categorias': categorias
    })

@login_required
def actualizar_ubicacion_producto(request, producto_id):
    """Vista para actualizar la ubicación de un producto"""
    producto = get_object_or_404(Producto, id=producto_id, vendedor=request.user)
    
    if request.method == 'POST':
        ubicacion_id = request.POST.get('ubicacion')
        stock = request.POST.get('stock', 0)
        
        ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id, usuario=request.user)
        
        ubicacion_producto, created = UbicacionProducto.objects.update_or_create(
            producto=producto,
            ubicacion=ubicacion,
            defaults={'stock_disponible': stock}
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Ubicación del producto actualizada correctamente'
        })
    
    ubicaciones = Ubicacion.objects.filter(usuario=request.user)
    ubicaciones_producto = UbicacionProducto.objects.filter(producto=producto)
    
    return render(request, 'ubicaciones/ubicacion_producto.html', {
        'producto': producto,
        'ubicaciones': ubicaciones,
        'ubicaciones_producto': ubicaciones_producto
    })

def get_ciudades_por_estado(request, estado_id):
    try:
        ciudades = Ciudad.objects.filter(estado_id=estado_id).values('id', 'nombre')
        return JsonResponse(list(ciudades), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def calcular_ruta(request):
    """Vista para calcular y mostrar la ruta óptima entre ubicaciones seleccionadas."""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            origen_id = int(request.POST.get('origen_id'))
            destinos_ids = json.loads(request.POST.get('destinos_ids', '[]'))
            
            # Validar que hay al menos un destino
            if not destinos_ids:
                return JsonResponse({
                    'error': 'Debe seleccionar al menos un destino.'
                }, status=400)
            
            # Calcular la ruta óptima
            distancia_total, ruta = RutaOptima.encontrar_ruta_optima(origen_id, destinos_ids)
            
            # Si no se pudo encontrar una ruta
            if distancia_total == float('infinity') or not ruta:
                return JsonResponse({
                    'error': 'No fue posible encontrar una ruta entre las ubicaciones seleccionadas.'
                }, status=400)
            
            # Generar instrucciones para la ruta
            instrucciones = RutaOptima.obtener_instrucciones_ruta(ruta)
            
            # Preparar datos para el mapa
            puntos_ruta = []
            for ubicacion in ruta:
                puntos_ruta.append({
                    'id': ubicacion.id,
                    'nombre': ubicacion.nombre,
                    'latitud': float(ubicacion.latitud),
                    'longitud': float(ubicacion.longitud),
                    'direccion': ubicacion.direccion,
                    'usuario': ubicacion.usuario.email
                })
            
            return JsonResponse({
                'success': True,
                'distancia_total': round(distancia_total, 2),
                'ruta': puntos_ruta,
                'instrucciones': instrucciones
            })
            
        except Exception as e:
            return JsonResponse({
                'error': f'Error al calcular la ruta: {str(e)}'
            }, status=500)
    
    # Si es una petición GET, mostrar la página para seleccionar ubicaciones
    else:
        # Obtener todas las ubicaciones del usuario
        mis_ubicaciones = Ubicacion.objects.filter(
            usuario=request.user
        ).select_related('ciudad', 'ciudad__estado', 'ciudad__estado__pais')
        
        # Obtener la ubicación principal (si existe)
        ubicacion_principal = Ubicacion.objects.filter(
            usuario=request.user, 
            es_principal=True
        ).first()
        
        # Obtener otras ubicaciones con productos (para visitar)
        ubicaciones_con_productos = []
        
        # Primero verificamos si hay una ubicación principal
        if ubicacion_principal and ubicacion_principal.latitud and ubicacion_principal.longitud:
            # Obtener ubicaciones cercanas con productos disponibles
            ubicaciones_query = Ubicacion.objects.exclude(
                usuario=request.user
            ).filter(
                latitud__isnull=False,
                longitud__isnull=False
            ).select_related(
                'usuario',
                'ciudad',
                'ciudad__estado',
                'ciudad__estado__pais'
            )
            
            # Para cada ubicación, verificar si tiene productos
            for ubicacion in ubicaciones_query:
                productos = UbicacionProducto.objects.filter(
                    ubicacion=ubicacion,
                    producto__activo=True,
                    stock_disponible__gt=0
                ).select_related('producto')
                
                if productos.exists():
                    # Calcular distancia desde la ubicación principal
                    distancia = AreaServicio.calcular_distancia(
                        float(ubicacion_principal.latitud),
                        float(ubicacion_principal.longitud),
                        float(ubicacion.latitud),
                        float(ubicacion.longitud)
                    )
                    
                    # Agregar a la lista
                    ubicaciones_con_productos.append({
                        'ubicacion': ubicacion,
                        'distancia': distancia,
                        'productos_count': productos.count()
                    })
            
            # Ordenar por distancia
            ubicaciones_con_productos.sort(key=lambda x: x['distancia'])
        
        context = {
            'mis_ubicaciones': mis_ubicaciones,
            'ubicacion_principal': ubicacion_principal,
            'ubicaciones_con_productos': ubicaciones_con_productos
        }
        
        return render(request, 'ubicaciones/calcular_ruta.html', context) 