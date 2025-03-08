from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from machina.core.db.models import get_model
from django.utils.text import slugify

User = get_user_model()
Forum = get_model('forum', 'Forum')
Topic = get_model('forum_conversation', 'Topic')
Post = get_model('forum_conversation', 'Post')

# Constantes para los tipos de foro
FORUM_TYPE_DEFAULT = 0
FORUM_TYPE_CATEGORY = 1
FORUM_TYPE_LINK = 2

class Command(BaseCommand):
    help = 'Reorganiza los foros para asegurar una estructura correcta'

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
        
        # 1. Eliminar el foro "daniel meyer" si existe
        try:
            foro_daniel = Forum.objects.get(name='daniel meyer')
            # Verificar si tiene subforos y moverlos a otro foro principal si es necesario
            subforos = Forum.objects.filter(parent=foro_daniel)
            if subforos.exists():
                # Mover subforos a la categoría General
                general = Forum.objects.get(name='General')
                for subforo in subforos:
                    subforo.parent = general
                    subforo.save()
                    self.stdout.write(self.style.SUCCESS(f'Subforo "{subforo.name}" movido a la categoría General'))
            
            # Eliminar el foro
            foro_daniel.delete()
            self.stdout.write(self.style.SUCCESS('Foro "daniel meyer" eliminado correctamente'))
        except Forum.DoesNotExist:
            self.stdout.write(self.style.WARNING('El foro "daniel meyer" no existe'))
        
        # 2. Verificar que las categorías principales tengan el tipo correcto
        categorias_principales = ['Hidroponía', 'Cultivos Tradicionales', 'General']
        for nombre in categorias_principales:
            try:
                categoria = Forum.objects.get(name=nombre)
                if categoria.type != FORUM_TYPE_CATEGORY:
                    categoria.type = FORUM_TYPE_CATEGORY
                    categoria.save()
                    self.stdout.write(self.style.SUCCESS(f'Categoría "{nombre}" actualizada al tipo correcto'))
            except Forum.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'La categoría "{nombre}" no existe'))
        
        # 3. Verificar que los subforos tengan el tipo correcto
        subforos = Forum.objects.exclude(parent=None)
        for subforo in subforos:
            if subforo.type != FORUM_TYPE_DEFAULT:
                subforo.type = FORUM_TYPE_DEFAULT
                subforo.save()
                self.stdout.write(self.style.SUCCESS(f'Subforo "{subforo.name}" actualizado al tipo correcto'))
        
        # 4. Verificar que todos los subforos tengan una categoría padre
        subforos_sin_padre = Forum.objects.filter(parent=None).exclude(name__in=categorias_principales)
        if subforos_sin_padre.exists():
            general = Forum.objects.get(name='General')
            for subforo in subforos_sin_padre:
                if subforo.name not in categorias_principales:
                    subforo.parent = general
                    subforo.type = FORUM_TYPE_DEFAULT
                    subforo.save()
                    self.stdout.write(self.style.SUCCESS(f'Subforo "{subforo.name}" movido a la categoría General'))
        
        # 5. Actualizar descripciones de las categorías principales
        descripciones = {
            'Hidroponía': 'Todo sobre cultivos hidropónicos, técnicas, equipos y soluciones.',
            'Cultivos Tradicionales': 'Discusiones sobre cultivos en tierra, técnicas de siembra y cosecha.',
            'General': 'Temas generales sobre agricultura y jardinería.'
        }
        
        for nombre, descripcion in descripciones.items():
            try:
                categoria = Forum.objects.get(name=nombre)
                categoria.description = descripcion
                categoria.save()
                self.stdout.write(self.style.SUCCESS(f'Descripción de "{nombre}" actualizada'))
            except Forum.DoesNotExist:
                pass
        
        self.stdout.write(self.style.SUCCESS('Reorganización de foros completada exitosamente')) 