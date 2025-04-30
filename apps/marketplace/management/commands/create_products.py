from django.core.management.base import BaseCommand
from apps.marketplace.models import MarketplaceProducto, CategoriaProducto, EstadoProducto, UnidadMedida
from django.contrib.auth import get_user_model
import random

class Command(BaseCommand):
    help = 'Creates multiple sample products in the database'

    def handle(self, *args, **options):
        User = get_user_model()
        admin_user = User.objects.first()
        
        if not admin_user:
            self.stdout.write(self.style.ERROR('No users found in the database'))
            return
            
        self.stdout.write(f'Using user: {admin_user.email}')
        
        categorias = CategoriaProducto.objects.all()
        if not categorias:
            self.stdout.write(self.style.ERROR('No categories found in the database'))
            return
        
        estados = EstadoProducto.objects.all()
        if not estados:
            self.stdout.write(self.style.ERROR('No product states found in the database'))
            return
        
        unidades = UnidadMedida.objects.all()
        if not unidades:
            self.stdout.write(self.style.ERROR('No measurement units found in the database'))
            return
        
        # Sample products data
        productos = [
            {
                'nombre': 'Manzanas Verdes',
                'descripcion': 'Manzanas verdes frescas y crujientes',
                'precio': 2.75,
                'stock': 80,
                'categoria_nombre': 'Frutas'
            },
            {
                'nombre': 'Plátanos Orgánicos',
                'descripcion': 'Plátanos orgánicos cultivados sin pesticidas',
                'precio': 1.99,
                'stock': 120,
                'categoria_nombre': 'Frutas'
            },
            {
                'nombre': 'Zanahorias',
                'descripcion': 'Zanahorias frescas de cultivo local',
                'precio': 1.50,
                'stock': 150,
                'categoria_nombre': 'Verduras'
            },
            {
                'nombre': 'Brócoli',
                'descripcion': 'Brócoli fresco y nutritivo',
                'precio': 2.25,
                'stock': 70,
                'categoria_nombre': 'Verduras'
            },
            {
                'nombre': 'Leche Entera',
                'descripcion': 'Leche fresca de vacas alimentadas con pasto',
                'precio': 3.50,
                'stock': 50,
                'categoria_nombre': 'Lacteos'
            },
            {
                'nombre': 'Queso Fresco',
                'descripcion': 'Queso artesanal recién elaborado',
                'precio': 5.75,
                'stock': 40,
                'categoria_nombre': 'Lacteos'
            },
            {
                'nombre': 'Carne de Res',
                'descripcion': 'Carne de res premium de ganado alimentado con pasto',
                'precio': 12.99,
                'stock': 30,
                'categoria_nombre': 'Carnes'
            },
            {
                'nombre': 'Pollo Entero',
                'descripcion': 'Pollo entero fresco de granja local',
                'precio': 8.50,
                'stock': 25,
                'categoria_nombre': 'Carnes'
            },
            {
                'nombre': 'Arroz Integral',
                'descripcion': 'Arroz integral orgánico de grano largo',
                'precio': 4.25,
                'stock': 100,
                'categoria_nombre': 'Granos'
            },
            {
                'nombre': 'Frijoles Negros',
                'descripcion': 'Frijoles negros orgánicos de alta calidad',
                'precio': 3.75,
                'stock': 90,
                'categoria_nombre': 'Granos'
            }
        ]
        
        created_count = 0
        
        for producto_data in productos:
            try:
                # Find the category by name
                categoria = None
                for cat in categorias:
                    if cat.nombre_categoria == producto_data['categoria_nombre']:
                        categoria = cat
                        break
                
                if not categoria:
                    self.stdout.write(self.style.WARNING(f"Category '{producto_data['categoria_nombre']}' not found, skipping product '{producto_data['nombre']}'"))
                    continue
                
                # Get random estado and unidad
                estado = random.choice(list(estados))
                unidad = random.choice(list(unidades))
                
                producto = MarketplaceProducto(
                    vendedor_id_id=admin_user,
                    nombre_producto=producto_data['nombre'],
                    descripcion=producto_data['descripcion'],
                    categoria_producto_id_id=categoria,
                    estado_producto_id_id=estado,
                    unidad_medida_id_id=unidad,
                    precio_base=producto_data['precio'],
                    stock_actual=producto_data['stock'],
                    disponibilidad=True
                )
                producto.save()
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created product '{producto_data['nombre']}' with ID: {producto.producto_id}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating product '{producto_data['nombre']}': {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} products")) 