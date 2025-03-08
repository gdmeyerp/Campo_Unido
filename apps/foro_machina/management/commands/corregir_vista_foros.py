from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from machina.core.db.models import get_model
from django.utils.text import slugify

User = get_user_model()
Forum = get_model('forum', 'Forum')

# Constantes para los tipos de foro
FORUM_TYPE_DEFAULT = 0
FORUM_TYPE_CATEGORY = 1
FORUM_TYPE_LINK = 2

class Command(BaseCommand):
    help = 'Corrige la visualización de los foros en la vista pública'

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
        
        # 1. Verificar la estructura jerárquica
        self.stdout.write(self.style.NOTICE('Verificando la estructura jerárquica...'))
        
        # Obtener el foro principal
        try:
            foro_principal = Forum.objects.get(name='Campo Unido')
        except Forum.DoesNotExist:
            self.stdout.write(self.style.ERROR('No se encontró el foro principal "Campo Unido"'))
            return
        
        # Asegurarse de que el foro principal tenga el tipo correcto
        if foro_principal.type != FORUM_TYPE_DEFAULT:
            foro_principal.type = FORUM_TYPE_DEFAULT
            self.stdout.write(self.style.SUCCESS('Foro principal actualizado al tipo correcto'))
        foro_principal.save()
        
        # 2. Verificar las categorías principales
        categorias_principales = ['Hidroponía', 'Cultivos Tradicionales', 'General']
        for nombre in categorias_principales:
            try:
                categoria = Forum.objects.get(name=nombre)
                # Verificar que la categoría tenga el tipo correcto
                if categoria.type != FORUM_TYPE_CATEGORY:
                    categoria.type = FORUM_TYPE_CATEGORY
                    categoria.save()
                    self.stdout.write(self.style.SUCCESS(f'Categoría "{nombre}" actualizada al tipo correcto'))
                
                # Verificar que la categoría tenga el padre correcto
                if categoria.parent != foro_principal:
                    categoria.parent = foro_principal
                    categoria.save()
                    self.stdout.write(self.style.SUCCESS(f'Categoría "{nombre}" movida bajo el foro principal'))
            except Forum.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'La categoría "{nombre}" no existe'))
        
        # 3. Contar cuántos foros hay en total
        total_foros = Forum.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f'Total de foros: {total_foros}'))
        
        # 4. Verificar que todos los subforos tengan el tipo correcto
        subforos = Forum.objects.exclude(name='Campo Unido').exclude(name__in=categorias_principales)
        for subforo in subforos:
            if subforo.type != FORUM_TYPE_DEFAULT:
                subforo.type = FORUM_TYPE_DEFAULT
                subforo.save()
                self.stdout.write(self.style.SUCCESS(f'Subforo "{subforo.name}" actualizado al tipo correcto'))
        
        self.stdout.write(self.style.SUCCESS('Corrección de la vista de foros completada exitosamente')) 