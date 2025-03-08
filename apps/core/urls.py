# core/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'  # Esto define el namespace 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/profile/', views.profile_view, name='profile'),
    path('accounts/profile/edit/', views.editar_perfil, name='editar_perfil'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),  # URL para el registro de usuarios
]
