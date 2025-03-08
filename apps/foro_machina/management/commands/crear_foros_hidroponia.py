from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from machina.core.db.models import get_model
from django.db.models import Q
from django.contrib.auth.models import Group
from machina.apps.forum_permission.models import GroupForumPermission, UserForumPermission
from guardian.utils import get_anonymous_user

User = get_user_model()
Forum = get_model('forum', 'Forum')
ForumPermission = get_model('forum_permission', 'ForumPermission')

# Constantes para los tipos de foro
FORUM_TYPE_DEFAULT = 0
FORUM_TYPE_CATEGORY = 1
FORUM_TYPE_LINK = 2

class Command(BaseCommand):
    help = 'Crea foros relacionados con hidroponía y cultivos en general'

    def handle(self, *args, **options):
        # Obtener o crear usuario administrador
        try:
            admin_user = User.objects.get(is_superuser=True)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('No se encontró un usuario administrador. Por favor, crea uno primero.'))
            return
        
        # Crear categorías principales
        hidroponía_cat = self._crear_foro(
            name='Hidroponía',
            description='Todo sobre cultivos hidropónicos, técnicas, equipos y soluciones.',
            parent=None,
            type=FORUM_TYPE_CATEGORY,
            created_by=admin_user
        )
        
        cultivos_cat = self._crear_foro(
            name='Cultivos Tradicionales',
            description='Discusiones sobre cultivos en tierra, técnicas de siembra y cosecha.',
            parent=None,
            type=FORUM_TYPE_CATEGORY,
            created_by=admin_user
        )
        
        general_cat = self._crear_foro(
            name='General',
            description='Temas generales sobre agricultura y jardinería.',
            parent=None,
            type=FORUM_TYPE_CATEGORY,
            created_by=admin_user
        )
        
        # Crear subforos de Hidroponía
        self._crear_foro(
            name='Sistemas NFT',
            description='Discusiones sobre sistemas de cultivo de película nutritiva (NFT).',
            parent=hidroponía_cat,
            type=FORUM_TYPE_DEFAULT,
            created_by=admin_user
        )
        
        self._crear_foro(
            name='Sistemas DWC',
            description='Cultivo en agua profunda (Deep Water Culture) y sus variantes.',
            parent=hidroponía_cat,
            type=FORUM_TYPE_DEFAULT,
            created_by=admin_user
        )
        
        self._crear_foro(
            name='Aeroponia',
            description='Sistemas de cultivo aeropónico y técnicas relacionadas.',
            parent=hidroponía_cat,
            type=FORUM_TYPE_DEFAULT,
            created_by=admin_user
        )
        
        self._crear_foro(
            name='Soluciones Nutritivas',
            description='Preparación y manejo de soluciones nutritivas para cultivos hidropónicos.',
            parent=hidroponía_cat,
            type=FORUM_TYPE_DEFAULT,
            created_by=admin_user
        )
        
        self._crear_foro(
            name='Automatización',
            description='Sistemas de automatización y control para cultivos hidropónicos.',
            parent=hidroponía_cat,
            type=FORUM_TYPE_DEFAULT,
            created_by=admin_user
        )
        
        # Crear subforos de Cultivos Tradicionales
        self._crear_foro(
            name='Hortalizas',
            description='Cultivo de hortalizas en tierra y técnicas relacionadas.',
            parent=cultivos_cat,
            type=FORUM_TYPE_DEFAULT,
            created_by=admin_user
        )
        
        self._crear_foro(
            name='Frutales',
            description='Cultivo de árboles frutales y arbustos.',
            parent=cultivos_cat,
            type=FORUM_TYPE_DEFAULT,
            created_by=admin_user
        )
        
        self._crear_foro(
            name='Cultivos Orgánicos',
            description='Técnicas de cultivo orgánico y permacultura.',
            parent=cultivos_cat,
            type=FORUM_TYPE_DEFAULT,
            created_by=admin_user
        )
        
        self._crear_foro(
            name='Control de Plagas',
            description='Métodos de control de plagas y enfermedades en cultivos tradicionales.',
            parent=cultivos_cat,
            type=FORUM_TYPE_DEFAULT,
            created_by=admin_user
        )
        
        # Crear subforos de General
        self._crear_foro(
            name='Presentaciones',
            description='Preséntate a la comunidad y comparte tus proyectos.',
            parent=general_cat,
            type=FORUM_TYPE_DEFAULT,
            created_by=admin_user
        )
        
        self._crear_foro(
            name='Noticias y Eventos',
            description='Noticias, eventos y ferias relacionadas con la agricultura.',
            parent=general_cat,
            type=FORUM_TYPE_DEFAULT,
            created_by=admin_user
        )
        
        self._crear_foro(
            name='Mercado',
            description='Compra, venta e intercambio de productos y equipos.',
            parent=general_cat,
            type=FORUM_TYPE_DEFAULT,
            created_by=admin_user
        )
        
        self._crear_foro(
            name='Ayuda y Soporte',
            description='Preguntas generales sobre el uso del foro y la plataforma.',
            parent=general_cat,
            type=FORUM_TYPE_DEFAULT,
            created_by=admin_user
        )
        
        self.stdout.write(self.style.SUCCESS('Foros creados exitosamente'))
    
    def _crear_foro(self, name, description, parent, type, created_by):
        """
        Crea un foro y asigna los permisos básicos
        """
        # Verificar si ya existe un foro con el mismo nombre y padre
        existing_forum = Forum.objects.filter(name=name)
        if parent:
            existing_forum = existing_forum.filter(parent=parent)
        else:
            existing_forum = existing_forum.filter(parent__isnull=True)
        
        if existing_forum.exists():
            self.stdout.write(self.style.WARNING(f'El foro "{name}" ya existe. Omitiendo...'))
            return existing_forum.first()
        
        # Crear el foro
        forum = Forum.objects.create(
            name=name,
            description=description,
            parent=parent,
            type=type,
            created_by=created_by
        )
        
        self.stdout.write(self.style.SUCCESS(f'Foro "{name}" creado correctamente'))
        
        # Asignar permisos básicos
        self._assign_basic_permissions(forum)
        
        return forum
    
    def _assign_basic_permissions(self, forum):
        """
        Asigna permisos básicos a un foro
        """
        # Obtener todos los permisos disponibles
        all_perms = ForumPermission.objects.all()
        
        # Asignar permisos para usuarios anónimos (solo lectura)
        for perm in all_perms.filter(Q(codename__contains='read') | Q(codename='can_see_forum')):
            UserForumPermission.objects.create(
                forum=forum,
                permission=perm,
                user=get_anonymous_user(),
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