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
    help = 'Corrige la estructura de visualización de los foros'

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
        
        # 1. Verificar la estructura actual
        self.stdout.write(self.style.NOTICE('Verificando la estructura actual de los foros...'))
        
        # Obtener el foro principal
        try:
            foro_principal = Forum.objects.get(name='Campo Unido')
        except Forum.DoesNotExist:
            self.stdout.write(self.style.ERROR('No se encontró el foro principal "Campo Unido"'))
            return
        
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
        
        # 3. Verificar los subforos de Hidroponía
        try:
            hidroponía = Forum.objects.get(name='Hidroponía')
            subforos_hidroponía = ['Sistemas NFT', 'Sistemas DWC', 'Aeroponia', 'Soluciones Nutritivas', 'Automatización']
            for nombre in subforos_hidroponía:
                try:
                    subforo = Forum.objects.get(name=nombre)
                    # Verificar que el subforo tenga el tipo correcto
                    if subforo.type != FORUM_TYPE_DEFAULT:
                        subforo.type = FORUM_TYPE_DEFAULT
                        subforo.save()
                        self.stdout.write(self.style.SUCCESS(f'Subforo "{nombre}" actualizado al tipo correcto'))
                    
                    # Verificar que el subforo tenga el padre correcto
                    if subforo.parent != hidroponía:
                        subforo.parent = hidroponía
                        subforo.save()
                        self.stdout.write(self.style.SUCCESS(f'Subforo "{nombre}" movido bajo la categoría "Hidroponía"'))
                except Forum.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'El subforo "{nombre}" no existe'))
        except Forum.DoesNotExist:
            self.stdout.write(self.style.WARNING('La categoría "Hidroponía" no existe'))
        
        # 4. Verificar los subforos de Cultivos Tradicionales
        try:
            cultivos = Forum.objects.get(name='Cultivos Tradicionales')
            subforos_cultivos = ['Hortalizas', 'Frutales', 'Cultivos Orgánicos', 'Control de Plagas']
            for nombre in subforos_cultivos:
                try:
                    subforo = Forum.objects.get(name=nombre)
                    # Verificar que el subforo tenga el tipo correcto
                    if subforo.type != FORUM_TYPE_DEFAULT:
                        subforo.type = FORUM_TYPE_DEFAULT
                        subforo.save()
                        self.stdout.write(self.style.SUCCESS(f'Subforo "{nombre}" actualizado al tipo correcto'))
                    
                    # Verificar que el subforo tenga el padre correcto
                    if subforo.parent != cultivos:
                        subforo.parent = cultivos
                        subforo.save()
                        self.stdout.write(self.style.SUCCESS(f'Subforo "{nombre}" movido bajo la categoría "Cultivos Tradicionales"'))
                except Forum.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'El subforo "{nombre}" no existe'))
        except Forum.DoesNotExist:
            self.stdout.write(self.style.WARNING('La categoría "Cultivos Tradicionales" no existe'))
        
        # 5. Verificar los subforos de General
        try:
            general = Forum.objects.get(name='General')
            subforos_general = ['Presentaciones', 'Noticias y Eventos', 'Mercado', 'Ayuda y Soporte']
            for nombre in subforos_general:
                try:
                    subforo = Forum.objects.get(name=nombre)
                    # Verificar que el subforo tenga el tipo correcto
                    if subforo.type != FORUM_TYPE_DEFAULT:
                        subforo.type = FORUM_TYPE_DEFAULT
                        subforo.save()
                        self.stdout.write(self.style.SUCCESS(f'Subforo "{nombre}" actualizado al tipo correcto'))
                    
                    # Verificar que el subforo tenga el padre correcto
                    if subforo.parent != general:
                        subforo.parent = general
                        subforo.save()
                        self.stdout.write(self.style.SUCCESS(f'Subforo "{nombre}" movido bajo la categoría "General"'))
                except Forum.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'El subforo "{nombre}" no existe'))
        except Forum.DoesNotExist:
            self.stdout.write(self.style.WARNING('La categoría "General" no existe'))
        
        # 6. Actualizar el orden de visualización (display_on_index)
        self.stdout.write(self.style.NOTICE('Actualizando el orden de visualización...'))
        
        # Foro principal siempre visible
        foro_principal.display_on_index = True
        foro_principal.save()
        
        # Categorías principales siempre visibles
        for nombre in categorias_principales:
            try:
                categoria = Forum.objects.get(name=nombre)
                categoria.display_on_index = True
                categoria.save()
                self.stdout.write(self.style.SUCCESS(f'Categoría "{nombre}" configurada para mostrar en el índice'))
            except Forum.DoesNotExist:
                pass
        
        self.stdout.write(self.style.SUCCESS('Corrección de la estructura de foros completada exitosamente')) 