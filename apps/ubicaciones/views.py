from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Pais, Estado, Ciudad, Ubicacion
from .forms import UbicacionForm


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
    mis_ubicaciones = Ubicacion.objects.filter(usuario=request.user).exclude(id=ubicacion_principal.id if ubicacion_principal else 0).select_related(
        'ciudad', 'ciudad__estado', 'ciudad__estado__pais'
    )
    
    # Obtener todas las ubicaciones de otros usuarios
    ubicaciones_otros = Ubicacion.objects.exclude(usuario=request.user).select_related(
        'usuario', 'ciudad', 'ciudad__estado', 'ciudad__estado__pais'
    )
    
    # Filtrar por distancia si se proporciona
    distancia = request.GET.get('distancia', 25)  # Valor predeterminado: 25 km
    tipo_usuario = request.GET.get('tipo', '')
    
    # Si hay filtro de tipo de usuario
    if tipo_usuario:
        # Aquí podrías implementar un filtro basado en el tipo de usuario 
        # (asumiendo que hay un perfil con ese campo)
        # Por ejemplo: ubicaciones_otros = ubicaciones_otros.filter(usuario__perfil__tipo=tipo_usuario)
        pass
    
    # Pasar los datos al contexto
    context = {
        'ubicacion_principal': ubicacion_principal,
        'mis_ubicaciones': mis_ubicaciones,
        'ubicaciones': ubicaciones_otros,
        'distancia': distancia,
        'tipo_usuario': tipo_usuario
    }
    
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