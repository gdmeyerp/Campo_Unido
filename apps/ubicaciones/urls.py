from django.urls import path
from . import views

app_name = 'ubicaciones'

urlpatterns = [
    path('', views.lista_paises, name='lista_paises'),
    path('mis-ubicaciones/', views.mis_ubicaciones, name='mis_ubicaciones'),
    path('crear/', views.crear_ubicacion, name='crear_ubicacion'),
    path('editar/<int:ubicacion_id>/', views.editar_ubicacion, name='editar_ubicacion'),
    path('eliminar/<int:ubicacion_id>/', views.eliminar_ubicacion, name='eliminar_ubicacion'),
    path('principal/<int:ubicacion_id>/', views.establecer_principal, name='establecer_principal'),
    path('buscar-cercanos/', views.buscar_cercanos, name='buscar_cercanos'),
    
    # APIs para AJAX
    path('api/estados/<int:pais_id>/', views.api_estados, name='api_estados'),
    path('api/ciudades/<int:estado_id>/', views.api_ciudades, name='api_ciudades'),
] 