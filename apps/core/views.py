from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
import os

from .forms import CustomUserCreationForm
from .models import User, PerfilUsuario
from django.contrib.auth.forms import AuthenticationForm

@login_required
def profile_view(request):
    # Asegurarse de que el usuario tenga un perfil
    perfil, created = PerfilUsuario.objects.get_or_create(user=request.user)
    return render(request, 'core/profile.html')

@login_required
def editar_perfil(request):
    # Asegurarse de que el usuario tenga un perfil
    perfil, created = PerfilUsuario.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Actualizar datos del usuario
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        
        # Actualizar datos del perfil
        perfil.descripcion = request.POST.get('descripcion', '')
        perfil.intereses = request.POST.get('intereses', '')
        
        # Procesar fecha de nacimiento
        fecha_nacimiento = request.POST.get('fecha_nacimiento', '')
        if fecha_nacimiento:
            perfil.fecha_nacimiento = fecha_nacimiento
        else:
            perfil.fecha_nacimiento = None
            
        # Procesar género
        perfil.genero = request.POST.get('genero', '')
        
        # Procesar foto de perfil
        if 'eliminar_foto' in request.POST and perfil.foto_perfil:
            # Eliminar la foto anterior del sistema de archivos
            if os.path.isfile(perfil.foto_perfil.path):
                os.remove(perfil.foto_perfil.path)
            perfil.foto_perfil = None
        
        if 'foto_perfil' in request.FILES:
            # Si ya existe una foto, eliminarla primero
            if perfil.foto_perfil:
                if os.path.isfile(perfil.foto_perfil.path):
                    os.remove(perfil.foto_perfil.path)
            
            # Guardar la nueva foto
            perfil.foto_perfil = request.FILES['foto_perfil']
        
        perfil.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('profile')
    
    return render(request, 'core/editar_perfil.html')

def custom_logout(request):
    logout(request)
    return redirect('login')  # Redirige a la página de inicio de sesión u otra página deseada

def configuracion(request):
    return render(request, 'core/configuracion.html')

def register(request):
    """Vista para el registro de usuarios usando email como identificador principal"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        # Verificar si es una solicitud AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        print(f"Intento de registro - Email: {request.POST.get('email')}")
        
        if form.is_valid():
            user = form.save()
            # Autenticar al usuario directamente tras el registro
            # Importante: usar el email como username para la autenticación
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=email, password=password)
            
            print(f"Registro exitoso para {email}")
            
            if user is not None:
                login(request, user)
                
                if is_ajax:
                    return JsonResponse({
                        'success': True, 
                        'redirect_url': '/'
                    })
                return redirect('core:dashboard')
            else:
                print(f"Registro exitoso pero login fallido para {email}")
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': 'Registro exitoso pero error al iniciar sesión. Por favor inicie sesión manualmente.'
                    })
                messages.success(request, 'Registro exitoso. Por favor inicie sesión.')
                return redirect('core:login')
        else:
            print(f"Errores en el formulario de registro: {form.errors}")
            if is_ajax:
                # Formatear errores para AJAX
                errors = dict([(k, [str(e) for e in v]) for k, v in form.errors.items()])
                return JsonResponse({
                    'success': False, 
                    'errors': errors,
                    'message': 'Por favor corrija los errores en el formulario.'
                })
    else:
        form = CustomUserCreationForm()
    
    # Si es una solicitud AJAX GET, responder con JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'GET':
        return JsonResponse({
            'success': False,
            'message': 'Por favor use POST para registrarse'
        })
    
    # Si llegamos aquí es porque es GET o POST con errores (no AJAX)
    return render(request, 'registration/register.html', {'form': form})

def index(request):
    """Vista de la página principal"""
    return render(request, 'core/index.html')

@login_required
def dashboard(request):
    """Vista del dashboard del usuario"""
    return render(request, 'core/dashboard.html')

def login_view(request):
    """Vista para el inicio de sesión de usuarios con email"""
    if request.method == 'POST':
        username = request.POST.get('username')  # Este campo contiene el email
        password = request.POST.get('password')
        
        # Añadir logs para depuración
        print(f"Intento de login - Email: {username}")
        
        # Autenticar usando el email como 'username'
        user = authenticate(request, username=username, password=password)
        
        # Verificar si es una solicitud AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if user is not None:
            login(request, user)
            
            print(f"Login exitoso para {username}")
            
            # Manejar respuestas AJAX
            if is_ajax:
                return JsonResponse({
                    'success': True, 
                    'redirect_url': request.POST.get('next', '/')
                })
            else:
                next_url = request.POST.get('next', '')
                if next_url:
                    return redirect(next_url)
                return redirect('core:dashboard')
        else:
            print(f"Login fallido para {username}")
            
            # Autenticación fallida
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Email o contraseña incorrectos. Por favor intente nuevamente.'
                })
            else:
                messages.error(request, 'Email o contraseña incorrectos. Por favor intente nuevamente.')
                return render(request, 'registration/login.html', {
                    'form': AuthenticationForm(request, data=request.POST)
                })
    
    # Si es GET, mostrar el formulario de login
    # Si es una solicitud AJAX GET, responder con JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'GET':
        return JsonResponse({
            'success': False,
            'message': 'Por favor use POST para iniciar sesión'
        })
    
    return render(request, 'registration/login.html', {
        'form': AuthenticationForm()
    })

def logout_view(request):
    """Vista de logout"""
    logout(request)
    return redirect('core:index')

@login_required
def profile(request):
    """Vista del perfil del usuario"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('core:profile')
    else:
        form = CustomUserCreationForm(instance=request.user)
    return render(request, 'core/profile.html', {'form': form})
