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
    help = 'Mejora la visualización de los foros en la plantilla principal'

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
        self.stdout.write(self.style.NOTICE('Mejorando la visualización de los foros...'))
        
        # 2. Actualizar propiedades de visualización para todos los foros
        foros = Forum.objects.all()
        for foro in foros:
            # Todos los foros deben ser visibles en el índice
            foro.display_on_index = True
            
            # Actualizar la descripción si está vacía
            if not foro.description:
                if foro.name == 'Campo Unido':
                    foro.description = 'Bienvenido al foro de Campo Unido. Aquí encontrarás discusiones sobre hidroponía, cultivos tradicionales y más.'
                elif foro.name == 'Hidroponía':
                    foro.description = 'Todo sobre cultivos hidropónicos, técnicas, equipos y soluciones.'
                elif foro.name == 'Cultivos Tradicionales':
                    foro.description = 'Discusiones sobre cultivos en tierra, técnicas de siembra y cosecha.'
                elif foro.name == 'General':
                    foro.description = 'Temas generales sobre agricultura y jardinería.'
                elif foro.name == 'Sistemas NFT':
                    foro.description = 'Discusiones sobre sistemas de cultivo NFT (Nutrient Film Technique).'
                elif foro.name == 'Sistemas DWC':
                    foro.description = 'Discusiones sobre sistemas de cultivo DWC (Deep Water Culture).'
                elif foro.name == 'Aeroponia':
                    foro.description = 'Discusiones sobre sistemas de cultivo aeropónicos.'
                elif foro.name == 'Soluciones Nutritivas':
                    foro.description = 'Discusiones sobre soluciones nutritivas para cultivos hidropónicos.'
                elif foro.name == 'Automatización':
                    foro.description = 'Discusiones sobre automatización de sistemas hidropónicos.'
                elif foro.name == 'Hortalizas':
                    foro.description = 'Discusiones sobre cultivo de hortalizas.'
                elif foro.name == 'Frutales':
                    foro.description = 'Discusiones sobre cultivo de frutales.'
                elif foro.name == 'Cultivos Orgánicos':
                    foro.description = 'Discusiones sobre cultivos orgánicos.'
                elif foro.name == 'Control de Plagas':
                    foro.description = 'Discusiones sobre control de plagas en cultivos.'
                elif foro.name == 'Presentaciones':
                    foro.description = 'Preséntate a la comunidad y comparte tus proyectos.'
                elif foro.name == 'Noticias y Eventos':
                    foro.description = 'Noticias y eventos relacionados con la agricultura y la hidroponía.'
                elif foro.name == 'Mercado':
                    foro.description = 'Compra, venta e intercambio de productos relacionados con la agricultura y la hidroponía.'
                elif foro.name == 'Ayuda y Soporte':
                    foro.description = 'Solicita ayuda y soporte para tus proyectos de agricultura e hidroponía.'
            
            # Guardar cambios
            foro.save()
            self.stdout.write(self.style.SUCCESS(f'Foro "{foro.name}" actualizado para mejorar su visualización'))
        
        # 3. Actualizar el orden de visualización
        self.stdout.write(self.style.NOTICE('Actualizando el orden de visualización...'))
        
        # Establecer el orden de las categorías principales
        try:
            foro_principal = Forum.objects.get(name='Campo Unido')
            foro_principal.display_position = 0
            foro_principal.save()
            
            hidroponía = Forum.objects.get(name='Hidroponía')
            hidroponía.display_position = 1
            hidroponía.save()
            
            cultivos = Forum.objects.get(name='Cultivos Tradicionales')
            cultivos.display_position = 2
            cultivos.save()
            
            general = Forum.objects.get(name='General')
            general.display_position = 3
            general.save()
            
            self.stdout.write(self.style.SUCCESS('Orden de categorías principales actualizado'))
        except Forum.DoesNotExist:
            self.stdout.write(self.style.WARNING('No se encontraron todas las categorías principales'))
        
        # 4. Asegurar que los subforos tengan el nivel de visualización correcto
        subforos = Forum.objects.exclude(parent=None)
        for subforo in subforos:
            # Los subforos deben tener un nivel de visualización más bajo que sus padres
            if subforo.parent:
                subforo.display_position = subforo.id  # Usar el ID como posición para mantener un orden consistente
                subforo.save()
        
        self.stdout.write(self.style.SUCCESS('Mejora de la visualización de los foros completada exitosamente')) 