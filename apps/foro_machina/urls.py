from django.urls import path
from . import views

app_name = 'foro_machina'

urlpatterns = [
    path('', views.foro_dashboard, name='dashboard'),
    path('tema/<int:pk>/', views.tema_detalle, name='tema_detalle'),
    path('foro/<int:pk>/', views.foro_detalle, name='foro_detalle'),
    path('foro/<int:forum_id>/nuevo-tema/', views.crear_tema, name='crear_tema'),
    path('buscar/', views.buscar, name='buscar'),
    
    # URLs de administración de foros
    path('admin/', views.admin_foros, name='admin_foros'),
    path('admin/crear-foro/', views.crear_foro, name='crear_foro'),
    path('admin/editar-foro/<int:pk>/', views.editar_foro, name='editar_foro'),
    path('admin/eliminar-foro/<int:pk>/', views.eliminar_foro, name='eliminar_foro'),
] 