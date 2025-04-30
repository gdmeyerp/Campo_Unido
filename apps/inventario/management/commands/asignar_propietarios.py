from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.inventario.models import ProductoInventario

User = get_user_model()

class Command(BaseCommand):
    help = 'Asigna propietarios a productos existentes que no tengan propietario'
    
    def add_arguments(self, parser):
        parser.add_argument('--usuario', type=str, help='Email del usuario a asignar como propietario. Si no se especifica, se usará el primer usuario del sistema.')
        parser.add_argument('--clear', action='store_true', help='Limpiar propietarios existentes antes de asignar.')
    
    def handle(self, *args, **options):
        email_usuario = options.get('usuario')
        clear = options.get('clear')
        
        if email_usuario:
            try:
                usuario = User.objects.get(email=email_usuario)
                self.stdout.write(f'Usando usuario: {usuario.email}')
            except User.DoesNotExist:
                raise CommandError(f'No se encontró ningún usuario con email: {email_usuario}')
        else:
            try:
                usuario = User.objects.first()
                self.stdout.write(f'Usando el primer usuario: {usuario.email}')
            except User.DoesNotExist:
                raise CommandError('No se encontraron usuarios en el sistema.')
        
        # Limpiar propietarios existentes si se indica
        if clear:
            self.stdout.write('Limpiando propietarios existentes...')
            ProductoInventario.objects.all().update(propietario=None)
            self.stdout.write(self.style.SUCCESS('Propietarios limpiados.'))
        
        # Consultar productos sin propietario
        productos_sin_propietario = ProductoInventario.objects.filter(propietario__isnull=True)
        count = productos_sin_propietario.count()
        
        if count == 0:
            self.stdout.write('No hay productos sin propietario.')
            return
        
        self.stdout.write(f'Asignando {count} productos al usuario {usuario.email}...')
        
        # Asignar el usuario a todos los productos sin propietario
        for producto in productos_sin_propietario:
            producto.propietario = usuario
            producto.save()
            self.stdout.write(f'Asignado propietario a: {producto.nombre_producto}')
        
        self.stdout.write(self.style.SUCCESS(f'Se asignaron {count} productos al usuario {usuario.email}.')) 