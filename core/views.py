from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate

from .forms import CustomUserCreationForm  # Importa el formulario de usuario personalizado
from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect

@login_required
def profile_view(request):
    return render(request, 'core/profile.html')

def custom_logout(request):
    logout(request)
    return redirect('login')  # Redirige a la página de inicio de sesión u otra página deseada


def configuracion(request):
    return render(request, 'core/configuracion.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Puedes asignar roles al usuario si es necesario aquí
            return redirect('login')  # Redirige a la página de inicio de sesión después del registro
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def index(request):
    return render(request, 'core/index.html')

@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')
