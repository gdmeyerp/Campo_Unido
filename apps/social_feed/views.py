from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

from .models import Post, Multimedia, Comentario, Like
from .forms import PostForm, ComentarioForm, MultimediaFormSet

# Obtener el modelo de usuario configurado en el proyecto
User = get_user_model()


@login_required
def feed(request):
    """
    Vista principal del feed social que muestra las publicaciones de todos los usuarios.
    """
    # Obtener todos los posts ordenados por fecha de creación (más recientes primero)
    posts = Post.objects.filter(es_publico=True).select_related('usuario').prefetch_related(
        'multimedia', 'comentarios', 'likes'
    ).order_by('-fecha_creacion')
    
    # Formulario para crear un nuevo post
    form = PostForm()
    
    # Paginación
    paginator = Paginator(posts, 10)  # 10 posts por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Formulario para comentarios
    comentario_form = ComentarioForm()
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'comentario_form': comentario_form,
    }
    
    return render(request, 'social_feed/dashboard_feed.html', context)


@login_required
def perfil(request, username):
    """
    Vista del perfil de un usuario que muestra sus publicaciones.
    """
    # Obtener el usuario por su nombre de usuario
    usuario = get_object_or_404(User, username=username)
    
    # Obtener los posts del usuario
    if request.user == usuario:
        # Si es el propio usuario, mostrar todos sus posts (públicos y privados)
        posts = Post.objects.filter(usuario=usuario)
    else:
        # Si es otro usuario, mostrar solo los posts públicos
        posts = Post.objects.filter(usuario=usuario, es_publico=True)
    
    # Ordenar por fecha de creación y hacer prefetch de relaciones
    posts = posts.select_related('usuario').prefetch_related(
        'multimedia', 'comentarios', 'likes'
    ).order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(posts, 10)  # 10 posts por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Formulario para comentarios
    comentario_form = ComentarioForm()
    
    context = {
        'usuario_perfil': usuario,
        'page_obj': page_obj,
        'comentario_form': comentario_form,
    }
    
    return render(request, 'social_feed/perfil.html', context)


@login_required
def crear_post(request):
    """
    Vista para crear un nuevo post con archivos multimedia.
    """
    if request.method == 'POST':
        form = PostForm(request.POST)
        formset = MultimediaFormSet(request.POST, request.FILES, prefix='multimedia')
        
        if form.is_valid() and formset.is_valid():
            # Guardar el post
            post = form.save(commit=False)
            post.usuario = request.user
            post.save()
            
            # Guardar los archivos multimedia
            instancias = formset.save(commit=False)
            for instancia in instancias:
                if instancia.archivo:  # Solo guardar si hay un archivo
                    instancia.post = post
                    # Determinar automáticamente el tipo basado en el archivo
                    if instancia.archivo.name.lower().endswith(('jpg', 'jpeg', 'png', 'gif')):
                        instancia.tipo = 'imagen'
                    elif instancia.archivo.name.lower().endswith(('mp4', 'avi', 'mov', 'wmv')):
                        instancia.tipo = 'video'
                    instancia.save()
            
            messages.success(request, _('Publicación creada con éxito.'))
            return redirect('social_feed:feed')
        else:
            messages.error(request, _('Por favor corrige los errores en el formulario.'))
    else:
        form = PostForm()
        formset = MultimediaFormSet(prefix='multimedia')
    
    context = {
        'form': form,
        'formset': formset,
    }
    
    return render(request, 'social_feed/crear_post.html', context)


@login_required
def detalle_post(request, post_id):
    """
    Vista para ver el detalle de un post específico.
    """
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar si el post es privado y el usuario no es el propietario
    if not post.es_publico and request.user != post.usuario:
        messages.error(request, _('No tienes permiso para ver esta publicación.'))
        return redirect('social_feed:feed')
    
    # Obtener comentarios ordenados por fecha
    comentarios = post.comentarios.filter(comentario_padre=None).select_related('usuario').prefetch_related('respuestas')
    
    # Formulario para comentarios
    comentario_form = ComentarioForm()
    
    context = {
        'post': post,
        'comentarios': comentarios,
        'comentario_form': comentario_form,
    }
    
    return render(request, 'social_feed/detalle_post.html', context)


@login_required
@require_POST
def like_post(request, post_id):
    """
    Vista para dar/quitar like a un post.
    """
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar si el post es privado y el usuario no es el propietario
    if not post.es_publico and request.user != post.usuario:
        return JsonResponse({'error': _('No tienes permiso para interactuar con esta publicación.')}, status=403)
    
    # Verificar si ya existe un like del usuario en este post
    like, created = Like.objects.get_or_create(post=post, usuario=request.user)
    
    if not created:
        # Si ya existía, eliminar el like
        like.delete()
        return JsonResponse({
            'success': True,
            'action': 'unlike',
            'total_likes': post.total_likes
        })
    
    return JsonResponse({
        'success': True,
        'action': 'like',
        'total_likes': post.total_likes
    })


@login_required
@require_POST
def comentar_post(request, post_id):
    """
    Vista para comentar un post.
    """
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar si el post es privado y el usuario no es el propietario
    if not post.es_publico and request.user != post.usuario:
        messages.error(request, _('No tienes permiso para comentar esta publicación.'))
        return redirect('social_feed:feed')
    
    form = ComentarioForm(request.POST)
    if form.is_valid():
        comentario = form.save(commit=False)
        comentario.post = post
        comentario.usuario = request.user
        
        # Verificar si es una respuesta a otro comentario
        comentario_padre_id = request.POST.get('comentario_padre')
        if comentario_padre_id:
            comentario_padre = get_object_or_404(Comentario, id=comentario_padre_id, post=post)
            comentario.comentario_padre = comentario_padre
        
        comentario.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Si es una solicitud AJAX, devolver JSON
            return JsonResponse({
                'success': True,
                'comentario_id': comentario.id,
                'usuario': comentario.usuario.username,
                'contenido': comentario.contenido,
                'fecha': comentario.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                'total_comentarios': post.total_comentarios
            })
        
        # Redirigir a la página de detalle del post
        return redirect('social_feed:detalle_post', post_id=post.id)
    
    # Si hay errores en el formulario
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    messages.error(request, _('Por favor corrige los errores en el formulario.'))
    return redirect('social_feed:detalle_post', post_id=post.id)


@login_required
def editar_post(request, post_id):
    """
    Vista para editar un post existente.
    """
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar si el usuario es el propietario del post
    if request.user != post.usuario:
        messages.error(request, _('No tienes permiso para editar esta publicación.'))
        return redirect('social_feed:feed')
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        
        if form.is_valid():
            form.save()
            messages.success(request, _('Publicación actualizada con éxito.'))
            return redirect('social_feed:detalle_post', post_id=post.id)
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
    }
    
    return render(request, 'social_feed/editar_post.html', context)


@login_required
def eliminar_post(request, post_id):
    """
    Vista para eliminar un post.
    """
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar si el usuario es el propietario del post
    if request.user != post.usuario:
        messages.error(request, _('No tienes permiso para eliminar esta publicación.'))
        return redirect('social_feed:feed')
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, _('Publicación eliminada con éxito.'))
        return redirect('social_feed:feed')
    
    context = {
        'post': post,
    }
    
    return render(request, 'social_feed/eliminar_post.html', context)


@login_required
def eliminar_comentario(request, comentario_id):
    """
    Vista para eliminar un comentario.
    """
    comentario = get_object_or_404(Comentario, id=comentario_id)
    
    # Verificar si el usuario es el propietario del comentario o del post
    if request.user != comentario.usuario and request.user != comentario.post.usuario:
        messages.error(request, _('No tienes permiso para eliminar este comentario.'))
        return redirect('social_feed:detalle_post', post_id=comentario.post.id)
    
    if request.method == 'POST':
        post_id = comentario.post.id
        comentario.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'total_comentarios': Post.objects.get(id=post_id).total_comentarios
            })
        
        messages.success(request, _('Comentario eliminado con éxito.'))
        return redirect('social_feed:detalle_post', post_id=post_id)
    
    context = {
        'comentario': comentario,
    }
    
    return render(request, 'social_feed/eliminar_comentario.html', context)
