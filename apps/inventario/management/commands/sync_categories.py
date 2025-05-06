from django.core.management.base import BaseCommand
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from apps.inventario.views import sincronizar_categorias
from django.contrib.messages.storage.fallback import FallbackStorage

class Command(BaseCommand):
    help = 'Sincroniza las categorías entre inventario y marketplace'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando sincronización de categorías...'))
        
        # Crear un request falso
        request = HttpRequest()
        
        # Usar el modelo de usuario personalizado
        User = get_user_model()
        
        # Asignar un usuario administrador
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No se encontró ningún usuario administrador. Abortando.'))
            return
        
        request.user = admin_user
        
        # Configurar almacenamiento de mensajes
        setattr(request, 'session', 'dummy')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # Llamar a la función de sincronización
        try:
            sincronizar_categorias(request)
            self.stdout.write(self.style.SUCCESS('Sincronización de categorías completada exitosamente.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error durante la sincronización: {str(e)}')) 