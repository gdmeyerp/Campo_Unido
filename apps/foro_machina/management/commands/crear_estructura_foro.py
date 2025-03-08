import logging
from django.core.management.base import BaseCommand
from machina.apps.forum.models import Forum
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from machina.core.db.models import get_model
from machina.core.loading import get_class

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')
ForumPermission = get_model('forum_permission', 'ForumPermission')
GroupForumPermission = get_model('forum_permission', 'GroupForumPermission')

FORUM_TYPES = {
    'FORUM_CAT': 0,  # Categoría
    'FORUM_POST': 1,  # Foro normal para posts
    'FORUM_LINK': 2,  # Enlace
}

class Command(BaseCommand):
    help = 'Crea la estructura básica de foros para Campo Unido'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando creación de estructura de foro'))
        
        # Eliminar foros existentes si se desea iniciar de cero
        Forum.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Foros existentes eliminados'))
        
        # Crear la estructura base
        with transaction.atomic():
            # 1. Foro principal "Campo Unido"
            foro_principal = Forum.objects.create(
                name='Campo Unido',
                slug='campo-unido',
                type=FORUM_TYPES['FORUM_CAT'],
                description='Foro principal de la comunidad Campo Unido'
            )
            self.stdout.write(self.style.SUCCESS(f'Foro principal creado: {foro_principal.name}'))
            
            # 2. Categorías principales
            cat_agricultura = Forum.objects.create(
                name='Agricultura',
                slug='agricultura',
                type=FORUM_TYPES['FORUM_CAT'],
                description='Discusiones sobre técnicas agrícolas, cultivos y consejos',
                parent=foro_principal
            )
            
            cat_ganaderia = Forum.objects.create(
                name='Ganadería',
                slug='ganaderia',
                type=FORUM_TYPES['FORUM_CAT'],
                description='Información sobre cría, manejo y cuidado de ganado',
                parent=foro_principal
            )
            
            cat_tecnologia = Forum.objects.create(
                name='Tecnología agrícola',
                slug='tecnologia-agricola',
                type=FORUM_TYPES['FORUM_CAT'],
                description='Avances tecnológicos para el campo',
                parent=foro_principal
            )
            
            cat_compraventa = Forum.objects.create(
                name='Compra-Venta',
                slug='compra-venta',
                type=FORUM_TYPES['FORUM_CAT'],
                description='Espacio para ofertar y buscar productos del campo',
                parent=foro_principal
            )
            
            cat_comunidad = Forum.objects.create(
                name='Comunidad',
                slug='comunidad',
                type=FORUM_TYPES['FORUM_CAT'],
                description='Discusiones generales de la comunidad',
                parent=foro_principal
            )
            
            # 3. Subforos de Agricultura
            Forum.objects.create(
                name='Cultivos tradicionales',
                slug='cultivos-tradicionales',
                type=FORUM_TYPES['FORUM_POST'],
                description='Maíz, frijol, trigo y otros cultivos tradicionales',
                parent=cat_agricultura
            )
            
            Forum.objects.create(
                name='Cultivos orgánicos',
                slug='cultivos-organicos',
                type=FORUM_TYPES['FORUM_POST'],
                description='Producción y certificación orgánica',
                parent=cat_agricultura
            )
            
            Forum.objects.create(
                name='Hidroponia',
                slug='hidroponia',
                type=FORUM_TYPES['FORUM_POST'],
                description='Sistemas hidropónicos, técnicas y cultivos',
                parent=cat_agricultura
            )
            
            # 4. Subforos de Ganadería
            Forum.objects.create(
                name='Ganado bovino',
                slug='ganado-bovino',
                type=FORUM_TYPES['FORUM_POST'],
                description='Vacas, toros y producción de leche',
                parent=cat_ganaderia
            )
            
            Forum.objects.create(
                name='Ganado porcino',
                slug='ganado-porcino',
                type=FORUM_TYPES['FORUM_POST'],
                description='Cría y manejo de cerdos',
                parent=cat_ganaderia
            )
            
            Forum.objects.create(
                name='Aves',
                slug='aves',
                type=FORUM_TYPES['FORUM_POST'],
                description='Gallinas, pollos y otras aves de corral',
                parent=cat_ganaderia
            )
            
            # 5. Subforos de Tecnología agrícola
            Forum.objects.create(
                name='Maquinaria agrícola',
                slug='maquinaria-agricola',
                type=FORUM_TYPES['FORUM_POST'],
                description='Tractores, cosechadoras y equipos',
                parent=cat_tecnologia
            )
            
            Forum.objects.create(
                name='Sistemas de riego',
                slug='sistemas-riego',
                type=FORUM_TYPES['FORUM_POST'],
                description='Tecnologías y métodos de riego eficiente',
                parent=cat_tecnologia
            )
            
            Forum.objects.create(
                name='Aplicaciones y software',
                slug='apps-software',
                type=FORUM_TYPES['FORUM_POST'],
                description='Herramientas digitales para el campo',
                parent=cat_tecnologia
            )
            
            # 6. Subforos de Compra-venta
            Forum.objects.create(
                name='Productos agrícolas',
                slug='productos-agricolas',
                type=FORUM_TYPES['FORUM_POST'],
                description='Venta de granos, frutas y verduras',
                parent=cat_compraventa
            )
            
            Forum.objects.create(
                name='Ganado y derivados',
                slug='ganado-derivados',
                type=FORUM_TYPES['FORUM_POST'],
                description='Compra y venta de ganado y productos derivados',
                parent=cat_compraventa
            )
            
            Forum.objects.create(
                name='Equipos e insumos',
                slug='equipos-insumos',
                type=FORUM_TYPES['FORUM_POST'],
                description='Herramientas, semillas, fertilizantes y más',
                parent=cat_compraventa
            )
            
            # 7. Subforos de Comunidad
            Forum.objects.create(
                name='Anuncios oficiales',
                slug='anuncios-oficiales',
                type=FORUM_TYPES['FORUM_POST'],
                description='Comunicados y noticias importantes',
                parent=cat_comunidad
            )
            
            Forum.objects.create(
                name='Ayuda y soporte',
                slug='ayuda-soporte',
                type=FORUM_TYPES['FORUM_POST'],
                description='Preguntas y respuestas sobre el funcionamiento del foro',
                parent=cat_comunidad
            )
            
            Forum.objects.create(
                name='Charla general',
                slug='charla-general',
                type=FORUM_TYPES['FORUM_POST'],
                description='Conversaciones diversas entre miembros',
                parent=cat_comunidad
            )
            
            self.stdout.write(self.style.SUCCESS('Estructura de foro creada exitosamente!'))

    def asignar_permisos_foros(self):
        """Asigna permisos a todos los foros para usuarios registrados"""
        permission_handler = PermissionHandler()
        
        # Obtener todos los permisos
        forum_permissions = ForumPermission.objects.all()
        
        # Para cada foro, establecer permisos para usuarios anónimos y registrados
        for forum in Forum.objects.all():
            # Permisos para usuarios anónimos (solo lectura)
            for perm in forum_permissions.filter(codename__in=['can_see_forum', 'can_read_forum']):
                permission_handler.assign_forum_permission(perm, None, forum)  # None = usuario anónimo
            
            # Permisos completos para usuarios registrados
            for perm in forum_permissions:
                # Asignar todos los permisos a los usuarios registrados
                # Esto usa grupos en lugar de usuarios individuales
                try:
                    registered_group, created = Group.objects.get_or_create(name='Registered users')
                    permission_handler.assign_forum_permission(perm, registered_group, forum)
                except Exception as e:
                    logging.error(f"Error asignando permisos para {forum.name}: {e}")
        
        self.stdout.write(self.style.SUCCESS('Permisos asignados correctamente')) 