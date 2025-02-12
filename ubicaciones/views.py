from django.shortcuts import render, get_object_or_404, redirect
from .models import Pais, Estado, Ciudad, Ubicacion
from .forms import PaisForm, EstadoForm, CiudadForm, UbicacionForm

def lista_paises(request):
    paises = Pais.objects.all()
    return render(request, 'ubicaciones/lista_paises.html', {'paises': paises})

def crear_pais(request):
    if request.method == 'POST':
        form = PaisForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_paises')
    else:
        form = PaisForm()
    return render(request, 'ubicaciones/crear_pais.html', {'form': form})
