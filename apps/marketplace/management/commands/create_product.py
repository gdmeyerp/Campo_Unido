from django.core.management.base import BaseCommand
from apps.marketplace.models import MarketplaceProducto, CategoriaProducto, EstadoProducto, UnidadMedida
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a sample product in the database'

    def handle(self, *args, **options):
        User = get_user_model()
        admin_user = User.objects.first()
        
        if not admin_user:
            self.stdout.write(self.style.ERROR('No users found in the database'))
            return
            
        self.stdout.write(f'Using user: {admin_user.email}')
        
        categoria = CategoriaProducto.objects.first()
        if not categoria:
            self.stdout.write(self.style.ERROR('No categories found in the database'))
            return
        self.stdout.write(f'Using category: {categoria.nombre_categoria}')
        
        estado = EstadoProducto.objects.first()
        if not estado:
            self.stdout.write(self.style.ERROR('No product states found in the database'))
            return
        self.stdout.write(f'Using product state: {estado.nombre_estado}')
        
        unidad = UnidadMedida.objects.first()
        if not unidad:
            self.stdout.write(self.style.ERROR('No measurement units found in the database'))
            return
        self.stdout.write(f'Using measurement unit: {unidad.nombre_unidad}')
        
        try:
            producto = MarketplaceProducto(
                vendedor_id_id=admin_user,
                nombre_producto='Manzanas Rojas',
                descripcion='Manzanas rojas frescas de temporada',
                categoria_producto_id_id=categoria,
                estado_producto_id_id=estado,
                unidad_medida_id_id=unidad,
                precio_base=2.50,
                stock_actual=100,
                disponibilidad=True
            )
            producto.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully created product with ID: {producto.producto_id}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating product: {str(e)}')) 