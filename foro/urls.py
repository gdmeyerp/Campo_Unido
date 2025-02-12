from django.urls import path
from . import views

app_name = 'foro'

urlpatterns = [
    path('', views.foro_general, name='foro_general'),
    path('foro/<int:pk>/', views.DetalleForoView.as_view(), name='detalle_foro'),
    path('foro/nuevo/', views.CrearForoView.as_view(), name='crear_foro'),
    path('foro/<int:pk>/editar/', views.EditarForoView.as_view(), name='editar_foro'),
    path('foro/<int:pk>/eliminar/', views.EliminarForoView.as_view(), name='eliminar_foro'),

    path('foro/<int:foro_id>/publicacion/nueva/', views.CrearPublicacionView.as_view(), name='crear_publicacion'),
    path('publicacion/<int:pk>/', views.DetallePublicacionView.as_view(), name='detalle_publicacion'),
    path('publicacion/<int:pk>/editar/', views.EditarPublicacionView.as_view(), name='editar_publicacion'),
    path('publicacion/<int:pk>/eliminar/', views.EliminarPublicacionView.as_view(), name='eliminar_publicacion'),

    path('publicacion/<int:publicacion_id>/comentario/nuevo/', views.CrearComentarioView.as_view(), name='crear_comentario'),
    path('comentario/<int:pk>/editar/', views.EditarComentarioView.as_view(), name='editar_comentario'),
    path('comentario/<int:pk>/eliminar/', views.EliminarComentarioView.as_view(), name='eliminar_comentario'),
]
