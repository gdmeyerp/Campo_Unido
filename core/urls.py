# core/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from core import views as core_views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('register/', views.register, name='register'),  # URL para el registro de usuarios
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('accounts/profile/', views.profile_view, name='profile'),

]
