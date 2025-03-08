from django.core.management.base import BaseCommand
from apps.marketplace.models import CategoriaProducto

class Command(BaseCommand):
    help = 'Creates test categories for the marketplace'

    def handle(self, *args, **options):
        # Check existing categories count
        categories_count = CategoriaProducto.objects.count()
        self.stdout.write(f"Current categories count: {categories_count}")
        
        if categories_count == 0:
            # Categories to create
            categories = [
                {'nombre': 'Frutas', 'descripcion': 'Todo tipo de frutas frescas de temporada'},
                {'nombre': 'Verduras', 'descripcion': 'Verduras frescas y organicas'},
                {'nombre': 'Lacteos', 'descripcion': 'Productos lacteos frescos'},
                {'nombre': 'Granos', 'descripcion': 'Granos y cereales de alta calidad'},
                {'nombre': 'Carnes', 'descripcion': 'Carnes frescas de primera calidad'}
            ]
            
            for cat_data in categories:
                category = CategoriaProducto.objects.create(
                    nombre_categoria=cat_data['nombre'],
                    descripcion=cat_data['descripcion']
                )
                
                # Create subcategories for Frutas
                if cat_data['nombre'] == 'Frutas':
                    subcategories = [
                        {'nombre': 'Frutas tropicales', 'descripcion': 'Frutas de clima tropical'},
                        {'nombre': 'Citricos', 'descripcion': 'Limones, naranjas y otros citricos'}
                    ]
                    
                    for subcat_data in subcategories:
                        CategoriaProducto.objects.create(
                            nombre_categoria=subcat_data['nombre'],
                            descripcion=subcat_data['descripcion'],
                            categoria_padre_id=category
                        )
            
            # Report how many were created
            new_count = CategoriaProducto.objects.count()
            self.stdout.write(self.style.SUCCESS(f"Successfully created {new_count - categories_count} categories"))
        else:
            self.stdout.write(self.style.WARNING(f"Categories already exist ({categories_count} found). No new categories created.")) 