from django.core.management.base import BaseCommand
from apps.marketplace.models import MarketplaceProducto

class Command(BaseCommand):
    help = 'Lists all products in the database'

    def handle(self, *args, **options):
        productos = MarketplaceProducto.objects.all()
        
        self.stdout.write(f'Total products: {productos.count()}')
        
        for p in productos:
            self.stdout.write(f'ID: {p.producto_id} - {p.nombre_producto}')
            self.stdout.write(f'  Category: {p.categoria_producto_id_id.nombre_categoria}')
            self.stdout.write(f'  Price: ${p.precio_base}')
            self.stdout.write(f'  Stock: {p.stock_actual}')
            self.stdout.write(f'  Description: {p.descripcion}')
            self.stdout.write('-' * 50) 