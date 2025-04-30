from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from machina.core.db.models import get_model
from django.utils.text import slugify
from apps.foro_machina.views import assign_basic_permissions

User = get_user_model()
Forum = get_model('forum', 'Forum')

# Constantes para los tipos de foro
FORUM_TYPE_DEFAULT = 0
FORUM_TYPE_CATEGORY = 1
FORUM_TYPE_LINK = 2

class Command(BaseCommand):
    help = 'Crea un foro principal como punto de entrada para todos los foros'

    def handle(self, *args, **options):
        # Obtener usuario administrador
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                self.stdout.write(self.style.ERROR('No se encontró un usuario administrador. Por favor, crea uno primero.'))
                return
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('No se encontró un usuario administrador. Por favor, crea uno primero.'))
            return
        
        # Crear foro principal "Foro Campo Unido"
        foro_principal_nombre = "Foro Campo Unido"
        
        # Verificar si ya existe
        if Forum.objects.filter(name=foro_principal_nombre).exists():
            self.stdout.write(self.style.WARNING(f'El foro "{foro_principal_nombre}" ya existe'))
            foro_principal = Forum.objects.get(name=foro_principal_nombre)
        else:
            # Crear el foro principal
            foro_principal = Forum.objects.create(
                name=foro_principal_nombre,
                slug=slugify(foro_principal_nombre),
                type=FORUM_TYPE_CATEGORY,
                description="Bienvenido al foro de Campo Unido. Aquí encontrarás discusiones sobre hidroponía, cultivos tradicionales y más.",
                created_by=admin_user
            )
            self.stdout.write(self.style.SUCCESS(f'Foro principal "{foro_principal_nombre}" creado correctamente'))
            
            # Asignar permisos básicos
            assign_basic_permissions(foro_principal)
        
        # Mover las categorías principales bajo el foro principal
        categorias_principales = ['Hidroponía', 'Cultivos Tradicionales', 'General']
        for nombre in categorias_principales:
            try:
                categoria = Forum.objects.get(name=nombre)
                if categoria.parent != foro_principal:
                    categoria.parent = foro_principal
                    categoria.save()
                    self.stdout.write(self.style.SUCCESS(f'Categoría "{nombre}" movida bajo el foro principal'))
            except Forum.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'La categoría "{nombre}" no existe'))
        
        self.stdout.write(self.style.SUCCESS('Creación y reorganización del foro principal completada exitosamente')) 