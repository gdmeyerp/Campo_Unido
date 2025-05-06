from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.db.models import Q
from machina.core.db.models import get_model
from machina.core.loading import get_class
from django.conf import settings
import os

Forum = get_model('forum', 'Forum')
ForumPermission = get_model('forum_permission', 'ForumPermission')
GroupForumPermission = get_model('forum_permission', 'GroupForumPermission')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')
PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')

class Command(BaseCommand):
    help = 'Corrige los permisos del foro y la configuración de adjuntos'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando corrección de permisos y configuración...')

        # 1. Crear grupos necesarios
        self.crear_grupos()

        # 2. Asignar permisos a los grupos
        self.asignar_permisos_grupos()

        # 3. Configurar directorio de adjuntos
        self.configurar_adjuntos()

        self.stdout.write(self.style.SUCCESS('Correcciones aplicadas exitosamente'))

    def crear_grupos(self):
        """Crear grupos necesarios para el foro"""
        grupos = ['Administrators', 'Registered users', 'Moderators']
        for nombre_grupo in grupos:
            grupo, creado = Group.objects.get_or_create(name=nombre_grupo)
            if creado:
                self.stdout.write(f'Grupo {nombre_grupo} creado')
            else:
                self.stdout.write(f'Grupo {nombre_grupo} ya existe')

    def asignar_permisos_grupos(self):
        """Asignar permisos a los grupos en todos los foros"""
        # Obtener grupos
        try:
            admin_group = Group.objects.get(name='Administrators')
            users_group = Group.objects.get(name='Registered users')
            mods_group = Group.objects.get(name='Moderators')
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR('Error: Grupos no encontrados'))
            return

        # Obtener todos los permisos disponibles
        all_perms = ForumPermission.objects.all()

        # Permisos para usuarios registrados
        registered_perms = [
            'can_see_forum',
            'can_read_forum',
            'can_start_new_topics',
            'can_reply_to_topics',
            'can_edit_own_posts',
            'can_delete_own_posts',
            'can_upload_attachments',
            'can_download_attachments',
        ]

        # Permisos para moderadores
        mod_perms = registered_perms + [
            'can_move_topics',
            'can_edit_posts',
            'can_delete_posts',
            'can_lock_topics',
            'can_approve_posts',
        ]

        # Limpiar permisos existentes
        GroupForumPermission.objects.all().delete()

        # Para cada foro
        for forum in Forum.objects.all():
            self.stdout.write(f'Configurando permisos para foro: {forum.name}')

            # Asignar todos los permisos a administradores
            for perm in all_perms:
                GroupForumPermission.objects.create(
                    forum=forum,
                    group=admin_group,
                    permission=perm,
                    has_perm=True
                )

            # Asignar permisos a usuarios registrados
            for perm in all_perms.filter(codename__in=registered_perms):
                GroupForumPermission.objects.create(
                    forum=forum,
                    group=users_group,
                    permission=perm,
                    has_perm=True
                )

            # Asignar permisos a moderadores
            for perm in all_perms.filter(codename__in=mod_perms):
                GroupForumPermission.objects.create(
                    forum=forum,
                    group=mods_group,
                    permission=perm,
                    has_perm=True
                )

    def configurar_adjuntos(self):
        """Configurar directorio de adjuntos y permisos"""
        # Crear directorio para adjuntos si no existe
        media_root = settings.MEDIA_ROOT
        attachments_dir = os.path.join(media_root, 'forum_attachments')
        if not os.path.exists(attachments_dir):
            os.makedirs(attachments_dir)
            self.stdout.write(f'Directorio de adjuntos creado en: {attachments_dir}') 