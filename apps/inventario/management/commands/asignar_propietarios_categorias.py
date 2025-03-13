from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.inventario.models import CategoriaProducto, ProductoInventario

class Command(BaseCommand):
    help = 'Asigna propietarios a todas las categorías y productos que no tengan uno'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Obtener el primer usuario como propietario por defecto
        default_user = User.objects.first()
        
        if not default_user:
            self.stdout.write(self.style.ERROR('No hay usuarios en el sistema para asignar como propietarios.'))
            return
        
        # Contar categorías sin propietario
        categorias_sin_propietario = CategoriaProducto.objects.filter(propietario__isnull=True)
        productos_sin_propietario = ProductoInventario.objects.filter(propietario__isnull=True)
        
        self.stdout.write(f"Se encontraron {categorias_sin_propietario.count()} categorías sin propietario.")
        self.stdout.write(f"Se encontraron {productos_sin_propietario.count()} productos sin propietario.")
        
        # Asignar el propietario por defecto a todas las categorías sin propietario
        num_categorias_actualizadas = categorias_sin_propietario.update(propietario=default_user)
        self.stdout.write(self.style.SUCCESS(f"Se asignó propietario a {num_categorias_actualizadas} categorías."))
        
        # Asignar el propietario por defecto a todos los productos sin propietario
        num_productos_actualizados = productos_sin_propietario.update(propietario=default_user)
        self.stdout.write(self.style.SUCCESS(f"Se asignó propietario a {num_productos_actualizados} productos."))
        
        # Mostrar estadísticas finales
        self.stdout.write("\nEstadísticas finales:")
        self.stdout.write(f"Categorías sin propietario: {CategoriaProducto.objects.filter(propietario__isnull=True).count()}")
        self.stdout.write(f"Productos sin propietario: {ProductoInventario.objects.filter(propietario__isnull=True).count()}")
        
        # Contar categorías y productos por usuario
        for usuario in User.objects.all():
            num_categorias = CategoriaProducto.objects.filter(propietario=usuario).count()
            num_productos = ProductoInventario.objects.filter(propietario=usuario).count()
            self.stdout.write(f"Usuario {usuario.id}: {num_categorias} categorías, {num_productos} productos") 