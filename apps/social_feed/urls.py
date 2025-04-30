from django.urls import path
from . import views

app_name = 'social_feed'

urlpatterns = [
    # Vista principal del feed
    path('', views.feed, name='feed'),
    
    # Perfil de usuario
    path('perfil/<str:username>/', views.perfil, name='perfil'),
    
    # Operaciones con posts
    path('post/crear/', views.crear_post, name='crear_post'),
    path('post/<int:post_id>/', views.detalle_post, name='detalle_post'),
    path('post/<int:post_id>/editar/', views.editar_post, name='editar_post'),
    path('post/<int:post_id>/eliminar/', views.eliminar_post, name='eliminar_post'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comentar/', views.comentar_post, name='comentar_post'),
    
    # Operaciones con comentarios
    path('comentario/<int:comentario_id>/eliminar/', views.eliminar_comentario, name='eliminar_comentario'),
] 