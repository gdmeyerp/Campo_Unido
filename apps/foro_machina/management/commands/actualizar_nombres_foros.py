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
    help = 'Actualiza los nombres de los foros para mejorar la visualización en las plantillas'

    def handle(self, *args, **options):
        # Obtener todos los foros
        foros = Forum.objects.all()
        
        for foro in foros:
            nombre_original = foro.name
            nombre_nuevo = nombre_original
            
            # Eliminar prefijos "Categoría" y "Foro" si existen
            if nombre_original.startswith('Categoría '):
                nombre_nuevo = nombre_original.replace('Categoría ', '')
            elif nombre_original.startswith('Foro '):
                nombre_nuevo = nombre_original.replace('Foro ', '')
                
            # Actualizar el nombre si ha cambiado
            if nombre_nuevo != nombre_original:
                foro.name = nombre_nuevo
                foro.slug = slugify(nombre_nuevo)
                foro.save()
                self.stdout.write(self.style.SUCCESS(f'Foro "{nombre_original}" renombrado a "{nombre_nuevo}"'))
            
        self.stdout.write(self.style.SUCCESS('Actualización de nombres de foros completada'))
        
        # Actualizar la visualización de los foros en la plantilla principal
        self.stdout.write(self.style.NOTICE('Actualizando la visualización de los foros...'))
        
        # Obtener el foro principal
        try:
            foro_principal = Forum.objects.get(name='Foro Campo Unido')
            # Cambiar el nombre a algo más adecuado para la visualización
            foro_principal.name = 'Campo Unido'
            foro_principal.slug = slugify('Campo Unido')
            foro_principal.save()
            self.stdout.write(self.style.SUCCESS('Foro principal renombrado a "Campo Unido"'))
        except Forum.DoesNotExist:
            self.stdout.write(self.style.WARNING('No se encontró el foro principal "Foro Campo Unido"'))
        
        self.stdout.write(self.style.SUCCESS('Actualización de la visualización de los foros completada')) 