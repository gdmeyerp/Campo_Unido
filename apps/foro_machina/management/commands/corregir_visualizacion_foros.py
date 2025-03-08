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
    help = 'Corrige la visualización de los foros en la plantilla principal y en la vista de administración'

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
        
        # 1. Corregir nombres de foros (eliminar prefijos)
        self.stdout.write(self.style.NOTICE('Corrigiendo nombres de foros...'))
        
        foros = Forum.objects.all()
        for foro in foros:
            nombre_original = foro.name
            nombre_nuevo = nombre_original
            
            # Eliminar prefijos "Categoría" y "Foro" si existen
            if nombre_original.startswith('Categoría '):
                nombre_nuevo = nombre_original.replace('Categoría ', '')
                foro.name = nombre_nuevo
                foro.slug = slugify(nombre_nuevo)
                foro.save()
                self.stdout.write(self.style.SUCCESS(f'Foro "{nombre_original}" renombrado a "{nombre_nuevo}"'))
            elif nombre_original.startswith('Foro '):
                nombre_nuevo = nombre_original.replace('Foro ', '')
                foro.name = nombre_nuevo
                foro.slug = slugify(nombre_nuevo)
                foro.save()
                self.stdout.write(self.style.SUCCESS(f'Foro "{nombre_original}" renombrado a "{nombre_nuevo}"'))
        
        # 2. Verificar la estructura jerárquica
        self.stdout.write(self.style.NOTICE('Verificando la estructura jerárquica...'))
        
        # Obtener el foro principal
        try:
            foro_principal = Forum.objects.get(name='Campo Unido')
        except Forum.DoesNotExist:
            self.stdout.write(self.style.ERROR('No se encontró el foro principal "Campo Unido"'))
            return
        
        # Asegurarse de que el foro principal sea visible
        foro_principal.display_on_index = True
        foro_principal.save()
        
        # 3. Verificar las categorías principales
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
                
                # Asegurarse de que la categoría sea visible
                categoria.display_on_index = True
                categoria.save()
            except Forum.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'La categoría "{nombre}" no existe'))
        
        # 4. Verificar los subforos
        self.stdout.write(self.style.NOTICE('Verificando los subforos...'))
        
        # Subforos de Hidroponía
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
                    
                    # Asegurarse de que el subforo sea visible
                    subforo.display_on_index = True
                    subforo.save()
                except Forum.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'El subforo "{nombre}" no existe'))
        except Forum.DoesNotExist:
            self.stdout.write(self.style.WARNING('La categoría "Hidroponía" no existe'))
        
        # Subforos de Cultivos Tradicionales
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
                    
                    # Asegurarse de que el subforo sea visible
                    subforo.display_on_index = True
                    subforo.save()
                except Forum.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'El subforo "{nombre}" no existe'))
        except Forum.DoesNotExist:
            self.stdout.write(self.style.WARNING('La categoría "Cultivos Tradicionales" no existe'))
        
        # Subforos de General
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
                    
                    # Asegurarse de que el subforo sea visible
                    subforo.display_on_index = True
                    subforo.save()
                except Forum.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'El subforo "{nombre}" no existe'))
        except Forum.DoesNotExist:
            self.stdout.write(self.style.WARNING('La categoría "General" no existe'))
        
        # 5. Actualizar el orden de visualización
        self.stdout.write(self.style.NOTICE('Actualizando el orden de visualización...'))
        
        # Establecer el orden de las categorías principales
        foro_principal.display_position = 0
        foro_principal.save()
        
        try:
            hidroponía = Forum.objects.get(name='Hidroponía')
            hidroponía.display_position = 1
            hidroponía.save()
        except Forum.DoesNotExist:
            pass
        
        try:
            cultivos = Forum.objects.get(name='Cultivos Tradicionales')
            cultivos.display_position = 2
            cultivos.save()
        except Forum.DoesNotExist:
            pass
        
        try:
            general = Forum.objects.get(name='General')
            general.display_position = 3
            general.save()
        except Forum.DoesNotExist:
            pass
        
        # 6. Verificar y actualizar las descripciones
        self.stdout.write(self.style.NOTICE('Verificando y actualizando las descripciones...'))
        
        # Actualizar la descripción del foro principal si está vacía
        if not foro_principal.description:
            foro_principal.description = 'Bienvenido al foro de Campo Unido. Aquí encontrarás discusiones sobre hidroponía, cultivos tradicionales y más.'
            foro_principal.save()
            self.stdout.write(self.style.SUCCESS('Descripción del foro principal actualizada'))
        
        # Actualizar las descripciones de las categorías principales si están vacías
        descripciones = {
            'Hidroponía': 'Todo sobre cultivos hidropónicos, técnicas, equipos y soluciones.',
            'Cultivos Tradicionales': 'Discusiones sobre cultivos en tierra, técnicas de siembra y cosecha.',
            'General': 'Temas generales sobre agricultura y jardinería.'
        }
        
        for nombre, descripcion in descripciones.items():
            try:
                categoria = Forum.objects.get(name=nombre)
                if not categoria.description:
                    categoria.description = descripcion
                    categoria.save()
                    self.stdout.write(self.style.SUCCESS(f'Descripción de la categoría "{nombre}" actualizada'))
            except Forum.DoesNotExist:
                pass
        
        # 7. Verificar y actualizar los permisos
        self.stdout.write(self.style.NOTICE('Verificando y actualizando los permisos...'))
        
        # Asegurarse de que todos los foros sean visibles para todos los usuarios
        for foro in Forum.objects.all():
            foro.display_on_index = True
            foro.save()
        
        self.stdout.write(self.style.SUCCESS('Corrección de la visualización de los foros completada exitosamente')) 