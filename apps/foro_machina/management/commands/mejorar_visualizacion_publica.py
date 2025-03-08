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
    help = 'Mejora la visualización de los foros en la plantilla pública'

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
        
        # 1. Verificar la estructura principal
        self.stdout.write(self.style.NOTICE('Verificando la estructura principal...'))
        
        # Obtener el foro principal
        try:
            foro_principal = Forum.objects.get(name='Campo Unido')
            self.stdout.write(self.style.SUCCESS(f'Foro principal "Campo Unido" encontrado (ID: {foro_principal.id})'))
        except Forum.DoesNotExist:
            self.stdout.write(self.style.ERROR('No se encontró el foro principal "Campo Unido"'))
            return
        
        # 2. Verificar que las categorías principales estén directamente bajo el foro principal
        self.stdout.write(self.style.NOTICE('Verificando las categorías principales...'))
        
        categorias_principales = ['Hidroponía', 'Cultivos Tradicionales', 'General']
        for nombre in categorias_principales:
            try:
                categoria = Forum.objects.get(name=nombre)
                if categoria.parent != foro_principal:
                    categoria.parent = foro_principal
                    categoria.save()
                    self.stdout.write(self.style.SUCCESS(f'Categoría "{nombre}" movida bajo el foro principal'))
                
                # Asegurarse de que la categoría sea del tipo correcto
                if categoria.type != FORUM_TYPE_CATEGORY:
                    categoria.type = FORUM_TYPE_CATEGORY
                    categoria.save()
                    self.stdout.write(self.style.SUCCESS(f'Categoría "{nombre}" actualizada al tipo correcto'))
            except Forum.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'La categoría "{nombre}" no existe'))
        
        # 3. Verificar que los subforos estén bajo las categorías correctas
        self.stdout.write(self.style.NOTICE('Verificando los subforos...'))
        
        # Estructura de subforos por categoría
        estructura_subforos = {
            'Hidroponía': ['Sistemas NFT', 'Sistemas DWC', 'Aeroponia', 'Soluciones Nutritivas', 'Automatización'],
            'Cultivos Tradicionales': ['Hortalizas', 'Frutales', 'Cultivos Orgánicos', 'Control de Plagas'],
            'General': ['Presentaciones', 'Noticias y Eventos', 'Mercado', 'Ayuda y Soporte']
        }
        
        for categoria_nombre, subforos_nombres in estructura_subforos.items():
            try:
                categoria = Forum.objects.get(name=categoria_nombre)
                for subforo_nombre in subforos_nombres:
                    try:
                        subforo = Forum.objects.get(name=subforo_nombre)
                        if subforo.parent != categoria:
                            subforo.parent = categoria
                            subforo.save()
                            self.stdout.write(self.style.SUCCESS(f'Subforo "{subforo_nombre}" movido bajo la categoría "{categoria_nombre}"'))
                        
                        # Asegurarse de que el subforo sea del tipo correcto
                        if subforo.type != FORUM_TYPE_DEFAULT:
                            subforo.type = FORUM_TYPE_DEFAULT
                            subforo.save()
                            self.stdout.write(self.style.SUCCESS(f'Subforo "{subforo_nombre}" actualizado al tipo correcto'))
                    except Forum.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'El subforo "{subforo_nombre}" no existe'))
            except Forum.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'La categoría "{categoria_nombre}" no existe'))
        
        # 4. Actualizar las descripciones de los foros si están vacías
        self.stdout.write(self.style.NOTICE('Actualizando las descripciones de los foros...'))
        
        descripciones = {
            'Campo Unido': 'Bienvenido al foro de Campo Unido. Aquí encontrarás discusiones sobre hidroponía, cultivos tradicionales y más.',
            'Hidroponía': 'Todo sobre cultivos hidropónicos, técnicas, equipos y soluciones.',
            'Cultivos Tradicionales': 'Discusiones sobre cultivos en tierra, técnicas de siembra y cosecha.',
            'General': 'Temas generales sobre agricultura y jardinería.',
            'Sistemas NFT': 'Discusiones sobre sistemas de cultivo hidropónico de película nutritiva (NFT).',
            'Sistemas DWC': 'Foro dedicado a sistemas de cultivo en agua profunda (Deep Water Culture).',
            'Aeroponia': 'Técnicas y sistemas para el cultivo aeropónico.',
            'Soluciones Nutritivas': 'Preparación y manejo de soluciones nutritivas para hidroponía.',
            'Automatización': 'Sistemas automáticos para el control y monitoreo de cultivos.',
            'Hortalizas': 'Cultivo de hortalizas en diferentes sistemas.',
            'Frutales': 'Todo sobre el cultivo de árboles y plantas frutales.',
            'Cultivos Orgánicos': 'Técnicas y métodos para el cultivo orgánico.',
            'Control de Plagas': 'Identificación y control de plagas y enfermedades.',
            'Presentaciones': 'Preséntate a la comunidad y comparte tus proyectos.',
            'Noticias y Eventos': 'Noticias, eventos y actualizaciones del mundo agrícola.',
            'Mercado': 'Compra, venta e intercambio de productos y servicios.',
            'Ayuda y Soporte': 'Preguntas y respuestas para nuevos usuarios.'
        }
        
        foros = Forum.objects.all()
        for foro in foros:
            if not foro.description and foro.name in descripciones:
                foro.description = descripciones[foro.name]
                foro.save()
                self.stdout.write(self.style.SUCCESS(f'Descripción del foro "{foro.name}" actualizada'))
        
        # 5. Asegurar que el orden de visualización sea correcto
        self.stdout.write(self.style.NOTICE('Actualizando el orden de visualización...'))
        
        # Foro principal
        foro_principal.display_position = 0
        foro_principal.save()
        
        # Categorías principales
        posiciones_categorias = {
            'Hidroponía': 1,
            'Cultivos Tradicionales': 2,
            'General': 3
        }
        
        for nombre, posicion in posiciones_categorias.items():
            try:
                categoria = Forum.objects.get(name=nombre)
                categoria.display_position = posicion
                categoria.save()
                self.stdout.write(self.style.SUCCESS(f'Posición de visualización de "{nombre}" actualizada a {posicion}'))
            except Forum.DoesNotExist:
                pass
        
        # 6. Asegurar que los subforos tengan un nivel de visualización correcto
        self.stdout.write(self.style.NOTICE('Actualizando el nivel de visualización de los subforos...'))
        
        for categoria_nombre, subforos_nombres in estructura_subforos.items():
            try:
                categoria = Forum.objects.get(name=categoria_nombre)
                for i, subforo_nombre in enumerate(subforos_nombres):
                    try:
                        subforo = Forum.objects.get(name=subforo_nombre)
                        subforo.display_position = i + 1  # Posición relativa dentro de la categoría
                        subforo.save()
                        self.stdout.write(self.style.SUCCESS(f'Posición de visualización de "{subforo_nombre}" actualizada a {i + 1}'))
                    except Forum.DoesNotExist:
                        pass
            except Forum.DoesNotExist:
                pass
        
        # 7. Verificar que todos los foros tengan slugs correctos
        self.stdout.write(self.style.NOTICE('Verificando los slugs de los foros...'))
        
        for foro in foros:
            slug_esperado = slugify(foro.name)
            if foro.slug != slug_esperado:
                foro.slug = slug_esperado
                foro.save()
                self.stdout.write(self.style.SUCCESS(f'Slug del foro "{foro.name}" actualizado a "{slug_esperado}"'))
        
        self.stdout.write(self.style.SUCCESS('Mejora de la visualización pública de los foros completada exitosamente')) 