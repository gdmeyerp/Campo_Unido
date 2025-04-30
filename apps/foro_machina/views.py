from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from machina.core.db.models import get_model
from machina.core.loading import get_class
from django.http import HttpResponseRedirect
from django.db.models import Count, Max, Q
from django import forms
from mptt.forms import TreeNodeChoiceField
from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm
from guardian.utils import get_anonymous_user
from django.template.response import TemplateResponse
from django.db import connection
from django.utils import timezone
from machina.apps.forum.models import Forum
from machina.apps.forum_conversation.models import Topic, Post
from machina.apps.forum_permission.viewmixins import PermissionRequiredMixin
from .forms import ForumForm
from .models import TopicAttachment
from django.utils.text import slugify

# Importar modelos de machina
Forum = get_model('forum', 'Forum')
Topic = get_model('forum_conversation', 'Topic')
Post = get_model('forum_conversation', 'Post')

# Importar formularios
TopicForm = get_class('forum_conversation.forms', 'TopicForm')
PostForm = get_class('forum_conversation.forms', 'PostForm')
# ForumForm = get_class('forum.forms', 'ForumForm')  # Esta clase no existe en machina

# Crear un formulario personalizado para Forum
class ForumForm(forms.ModelForm):
    parent = TreeNodeChoiceField(
        queryset=Forum.objects.all(),
        required=False,
        label=_('Foro padre'),
        empty_label=_('Sin foro padre (foro raíz)'),
    )

    class Meta:
        model = Forum
        fields = ['name', 'description', 'parent', 'type', 'image', 'display_sub_forum_list']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        forum_instance = kwargs.pop('forum_instance', None)
        super(ForumForm, self).__init__(*args, **kwargs)
        
        # Si estamos editando un foro existente, excluirlo a sí mismo y sus descendientes
        # de las opciones de foro padre para evitar ciclos
        if forum_instance:
            descendants = forum_instance.get_descendants(include_self=True)
            self.fields['parent'].queryset = Forum.objects.exclude(
                pk__in=[descendant.pk for descendant in descendants]
            )

# Importar permisos
PermissionRequiredMixin = get_class('forum_permission.viewmixins', 'PermissionRequiredMixin')

# Función para verificar si un usuario es administrador
def es_admin(user):
    return user.is_authenticated and user.is_staff

# Middleware para agregar foros a todas las plantillas
class ForumMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Si la respuesta es una TemplateResponse y usa una plantilla de foro_machina
        if isinstance(response, TemplateResponse) and hasattr(response, 'template_name'):
            template_name = response.template_name
            if isinstance(template_name, (list, tuple)):
                template_name = template_name[0] if template_name else ''
            
            if 'foro_machina' in template_name:
                # Obtener todos los foros y agregarlos al contexto
                if 'forums' not in response.context_data:
                    response.context_data['forums'] = Forum.objects.all()
        
        return response

def foro_dashboard(request):
    """
    Vista principal del foro que muestra los foros principales y los temas/posts recientes.
    """
    # Obtener el foro principal "Campo Unido"
    try:
        foro_principal = Forum.objects.get(name='Campo Unido')
        # Obtener todos los foros, incluyendo el principal
        forums = Forum.objects.all()
    except Forum.DoesNotExist:
        # Si no existe el foro principal, mostrar todos los foros de nivel superior
        forums = Forum.objects.filter(parent=None)
    
    recent_topics = Topic.objects.order_by('-last_post_on')[:5]
    recent_posts = Post.objects.order_by('-created')[:5]
    
    return render(request, 'foro_machina/dashboard.html', {
        'forums': forums,
        'recent_topics': recent_topics,
        'recent_posts': recent_posts,
    })

@login_required
def tema_detalle(request, pk):
    """
    Vista que muestra un tema específico y sus posts.
    """
    try:
        topic = Topic.objects.get(pk=pk)
    except Topic.DoesNotExist:
        raise Http404(_("El tema solicitado no existe"))
    
    # Incrementar contador de vistas
    topic.views_count += 1
    topic.save()
    
    # Obtener foro y posts
    forum = topic.forum
    posts = topic.posts.all().order_by('created')
    
    # Procesar formulario de respuesta
    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES, user=request.user)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.topic = topic
            post.poster = request.user
            post.save()
            
            # Manejar archivos adjuntos
            if 'attachment' in request.FILES:
                attachment = TopicAttachment(
                    topic=topic,
                    post=post,  # Asociar el archivo adjunto con el post específico
                    file=request.FILES['attachment'],
                    filename=request.FILES['attachment'].name,
                    mimetype=request.FILES['attachment'].content_type
                )
                attachment.save()
            
            return redirect('foro_machina:tema_detalle', pk=topic.pk)
    else:
        post_form = PostForm(user=request.user)
    
    context = {
        'topic': topic,
        'forum': forum,
        'posts': posts,
        'post_form': post_form,
    }
    
    return render(request, 'foro_machina/tema_detalle.html', context)

@login_required
def foro_detalle(request, pk):
    """
    Vista que muestra un foro específico y sus temas.
    """
    forum = get_object_or_404(Forum, pk=pk)
    topics = forum.topics.order_by('-last_post_on')
    
    # Obtener todos los foros para la plantilla base
    forums = Forum.objects.all()
    
    return render(request, 'foro_machina/foro_detalle.html', {
        'forum': forum,
        'topics': topics,
        'forums': forums,
    })

@login_required
def crear_tema(request, forum_id):
    """
    Vista para crear un nuevo tema en un foro.
    """
    forum = get_object_or_404(Forum, pk=forum_id)
    
    if request.method == 'POST':
        # Creamos un tema directamente con los datos básicos
        topic = Topic(
            forum=forum,
            poster=request.user,
            subject=request.POST.get('subject', ''),
            type=Topic.TOPIC_POST,  # Tema normal
            status=Topic.TOPIC_UNLOCKED,  # Desbloqueado por defecto
            approved=True,
        )
        topic.slug = slugify(topic.subject)
        topic.save()
        
        # Ahora creamos el post utilizando los datos del formulario
        post = Post(
            topic=topic,
            poster=request.user, 
            subject=request.POST.get('subject', ''),
            content=request.POST.get('content', ''),
            approved=True,
        )
        post.save()
        
        # Procesamos las etiquetas
        tags_text = request.POST.get('tags', '')
        if tags_text:
            tags = tags_text.split(',')
            for tag_name in tags:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, created = TopicTag.objects.get_or_create(
                        name=tag_name,
                        defaults={'slug': slugify(tag_name)}
                    )
                    topic.tags.add(tag)
        
        # Procesamos archivos adjuntos
        if 'attachment' in request.FILES:
            attachment = request.FILES['attachment']
            TopicAttachment.objects.create(
                topic=topic,
                post=post,
                file=attachment,
                filename=attachment.name,
                mimetype=attachment.content_type
            )
        
        messages.success(request, _("Tema creado correctamente."))
        return redirect('foro_machina:tema_detalle', pk=topic.pk)
    else:
        return render(request, 'foro_machina/crear_tema.html', {
            'forum': forum,
        })

def buscar(request):
    """
    Vista para buscar en el foro.
    """
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Buscar en temas
        topic_results = Topic.objects.filter(
            Q(subject__icontains=query) | Q(posts__content__icontains=query)
        ).distinct()
        
        # Buscar en posts
        post_results = Post.objects.filter(content__icontains=query)
        
        results = {
            'topics': topic_results,
            'posts': post_results,
        }
    
    # Obtener todos los foros para la plantilla base
    forums = Forum.objects.all()
    
    return render(request, 'foro_machina/buscar.html', {
        'query': query,
        'results': results,
        'forums': forums,
    })

# Funciones de administración de foros
def is_forum_admin(user):
    """
    Verifica si un usuario puede administrar foros.
    Ahora cualquier usuario autenticado puede administrar foros.
    """
    return user.is_authenticated

@login_required
def admin_foros(request):
    """
    Vista para listar todos los foros disponibles para administración.
    """
    forums = Forum.objects.all()
    return render(request, 'foro_machina/admin/admin_foros.html', {'forums': forums})

@login_required
def crear_foro(request):
    """
    Vista para crear un nuevo foro.
    """
    if request.method == 'POST':
        form = ForumForm(request.POST, request.FILES)
        if form.is_valid():
            forum = form.save(commit=False)
            forum.created_by = request.user
            forum.save()
            
            # Asignar permisos básicos usando assign_basic_permissions
            assign_basic_permissions(forum)
            
            messages.success(request, _('Foro creado correctamente.'))
            return redirect('foro_machina:admin_foros')
    else:
        form = ForumForm()
    
    # Obtener todos los foros para la plantilla base
    forums = Forum.objects.all()
    
    return render(request, 'foro_machina/admin/crear_foro.html', {
        'form': form,
        'forums': forums,
    })

@login_required
def editar_foro(request, pk):
    """
    Vista para editar un foro existente.
    """
    forum = get_object_or_404(Forum, pk=pk)
    
    # Verificar si el usuario es el creador del foro o un administrador
    if not (request.user.is_staff or request.user.is_superuser or forum.created_by == request.user):
        messages.error(request, _('No tienes permiso para editar este foro.'))
        return redirect('foro_machina:admin_foros')
    
    if request.method == 'POST':
        form = ForumForm(request.POST, request.FILES, instance=forum)
        if form.is_valid():
            form.save()
            messages.success(request, _('Foro actualizado correctamente.'))
            return redirect('foro_machina:admin_foros')
    else:
        form = ForumForm(instance=forum)
    
    # Obtener todos los foros para la plantilla base
    forums = Forum.objects.all()
    
    return render(request, 'foro_machina/admin/editar_foro.html', {
        'form': form, 
        'forum': forum,
        'forums': forums,
    })

@login_required
def eliminar_foro(request, pk):
    """
    Vista para eliminar un foro.
    """
    forum = get_object_or_404(Forum, pk=pk)
    
    # Verificar si el usuario es el creador del foro o un administrador
    if not (request.user.is_staff or request.user.is_superuser or forum.created_by == request.user):
        messages.error(request, _('No tienes permiso para eliminar este foro.'))
        return redirect('foro_machina:admin_foros')
    
    if request.method == 'POST':
        forum.delete()
        messages.success(request, _('Foro eliminado correctamente.'))
        return redirect('foro_machina:admin_foros')
    
    # Obtener todos los foros para la plantilla base
    forums = Forum.objects.all()
    
    return render(request, 'foro_machina/admin/eliminar_foro.html', {
        'forum': forum,
        'forums': forums,
    })

def assign_basic_permissions(forum):
    """
    Asigna permisos básicos a un foro recién creado.
    """
    from django.contrib.auth.models import Group
    from machina.apps.forum_permission.models import GroupForumPermission, UserForumPermission
    from machina.core.db.models import get_model
    
    # Obtener todos los permisos disponibles
    ForumPermission = get_model('forum_permission', 'ForumPermission')
    all_perms = ForumPermission.objects.all()
    
    # Asignar permisos para usuarios anónimos (solo lectura)
    for perm in all_perms.filter(Q(codename__contains='read') | Q(codename='can_see_forum')):
        UserForumPermission.objects.create(
            forum=forum,
            permission=perm,
            user=get_anonymous_user(),  # Usuario anónimo
            has_perm=True
        )
    
    # Asignar todos los permisos a superusuarios
    try:
        admin_group = Group.objects.get(name='Administrators')
    except Group.DoesNotExist:
        # Crear el grupo si no existe
        admin_group = Group.objects.create(name='Administrators')
    
    for perm in all_perms:
        GroupForumPermission.objects.create(
            forum=forum,
            permission=perm,
            group=admin_group,
            has_perm=True
        )
    
    # Asignar permisos de lectura y escritura a usuarios registrados
    registered_perms = all_perms.filter(
        Q(codename__contains='read') | 
        Q(codename='can_see_forum') |
        Q(codename='can_start_new_topics') |
        Q(codename='can_reply_to_topics')
    )
    
    try:
        users_group = Group.objects.get(name='Registered users')
    except Group.DoesNotExist:
        # Crear el grupo si no existe
        users_group = Group.objects.create(name='Registered users')
    
    for perm in registered_perms:
        GroupForumPermission.objects.create(
            forum=forum,
            permission=perm,
            group=users_group,
            has_perm=True
        )
