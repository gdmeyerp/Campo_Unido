from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from apps.inventario.models import CategoriaProducto, ProductoInventario
from django.utils import timezone

class Command(BaseCommand):
    help = 'Diagnoses and fixes issues with product categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Apply fixes for duplicate categories',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information',
        )

    def handle(self, *args, **options):
        fix_mode = options['fix']
        verbose = options['verbose']
        
        self.stdout.write(self.style.WARNING('Analizando categorías de productos...'))
        
        # Count total categories
        total_categories = CategoriaProducto.objects.count()
        self.stdout.write(f'Total categorías: {total_categories}')
        
        # Get categories with the same name
        duplicates = CategoriaProducto.objects.values('nombre_categoria') \
                                              .annotate(count=Count('id')) \
                                              .filter(count__gt=1) \
                                              .order_by('-count')
        
        if duplicates:
            self.stdout.write(self.style.ERROR(f'Se encontraron {len(duplicates)} categorías duplicadas:'))
            for dup in duplicates:
                self.stdout.write(f"  - '{dup['nombre_categoria']}' ({dup['count']} ocurrencias)")
                
                if verbose:
                    # Show more details about each duplicate
                    cats = CategoriaProducto.objects.filter(nombre_categoria=dup['nombre_categoria']).order_by('id')
                    for cat in cats:
                        products_count = ProductoInventario.objects.filter(categoria_producto=cat).count()
                        self.stdout.write(f"    * ID: {cat.id}, Desc: {cat.descripcion[:50]}..., Productos: {products_count}")
                
                if fix_mode:
                    self.fix_duplicate_category(dup['nombre_categoria'])
        else:
            self.stdout.write(self.style.SUCCESS('No se encontraron categorías con nombres duplicados.'))
        
        # Check categories that might be similar but with different names
        self.check_similar_categories([
            ('Hidroponía', 'Cultivos Hidropónicos'),
            ('Acuaponía', 'Cultivos Acuapónicos'),
        ], fix_mode, verbose)
        
        # Get statistics on categories
        self.stdout.write("\nEstadísticas de categorías:")
        
        # Categories without products
        unused_categories = CategoriaProducto.objects.annotate(
            num_products=Count('productoinventario')
        ).filter(num_products=0).count()
        self.stdout.write(f"- Categorías sin productos: {unused_categories}")
        
        # Top categories by product count
        top_categories = CategoriaProducto.objects.annotate(
            num_products=Count('productoinventario')
        ).filter(num_products__gt=0).order_by('-num_products')[:10]
        
        self.stdout.write("- Top 10 categorías por número de productos:")
        for cat in top_categories:
            self.stdout.write(f"  * {cat.nombre_categoria}: {cat.num_products} productos")

    def fix_duplicate_category(self, category_name):
        """Fix duplicate categories with the same name"""
        categories = CategoriaProducto.objects.filter(nombre_categoria=category_name).order_by('id')
        if categories.count() <= 1:
            return
            
        # Keep the oldest category (lowest ID) as that's likely the one used in statistics
        keeper = categories[0]
        to_remove = categories[1:]
        
        self.stdout.write(f"  Fusionando categorías para '{category_name}':")
        self.stdout.write(f"    - Manteniendo categoría con ID {keeper.id}")
        
        for category in to_remove:
            # Get products count before moving
            product_count = ProductoInventario.objects.filter(categoria_producto=category).count()
            
            # Update all products using the category to be removed
            ProductoInventario.objects.filter(categoria_producto=category).update(
                categoria_producto=keeper
            )
            
            # Update all subcategories to point to the keeper
            subcats_count = CategoriaProducto.objects.filter(categoria_padre=category).count()
            CategoriaProducto.objects.filter(categoria_padre=category).update(
                categoria_padre=keeper
            )
            
            self.stdout.write(f"    - Eliminando categoría con ID {category.id} (moviendo {product_count} productos y {subcats_count} subcategorías)")
            category.delete()
            
        self.stdout.write(self.style.SUCCESS(f"  ✓ Categorías para '{category_name}' fusionadas exitosamente"))
        
    def check_similar_categories(self, pairs, fix_mode, verbose):
        """Check for categories that might be similar but with different names"""
        self.stdout.write("\nVerificando categorías similares:")
        
        for name1, name2 in pairs:
            cat1 = CategoriaProducto.objects.filter(nombre_categoria=name1)
            cat2 = CategoriaProducto.objects.filter(nombre_categoria=name2)
            
            if cat1.exists() and cat2.exists():
                self.stdout.write(f"- Posibles categorías similares encontradas: '{name1}' y '{name2}'")
                
                if verbose:
                    for c1 in cat1:
                        products_count1 = ProductoInventario.objects.filter(categoria_producto=c1).count()
                        self.stdout.write(f"  * '{name1}' (ID: {c1.id}): {products_count1} productos")
                        
                    for c2 in cat2:
                        products_count2 = ProductoInventario.objects.filter(categoria_producto=c2).count()
                        self.stdout.write(f"  * '{name2}' (ID: {c2.id}): {products_count2} productos")
                
                if fix_mode:
                    self.merge_similar_categories(name1, name2)
    
    def merge_similar_categories(self, name1, name2):
        """Merge two similar categories with different names"""
        cat1 = CategoriaProducto.objects.filter(nombre_categoria=name1).first()
        cat2 = CategoriaProducto.objects.filter(nombre_categoria=name2).first()
        
        if not cat1 or not cat2:
            return
            
        # Count products for each category
        products_count1 = ProductoInventario.objects.filter(categoria_producto=cat1).count()
        products_count2 = ProductoInventario.objects.filter(categoria_producto=cat2).count()
        
        # Keep the category with more products
        if products_count1 >= products_count2:
            keeper, to_remove = cat1, cat2
        else:
            keeper, to_remove = cat2, cat1
            
        self.stdout.write(f"  Fusionando categorías similares:")
        self.stdout.write(f"    - Manteniendo '{keeper.nombre_categoria}' (ID: {keeper.id}) con {max(products_count1, products_count2)} productos")
        self.stdout.write(f"    - Eliminando '{to_remove.nombre_categoria}' (ID: {to_remove.id}) con {min(products_count1, products_count2)} productos")
        
        # Update all products using the category to be removed
        ProductoInventario.objects.filter(categoria_producto=to_remove).update(
            categoria_producto=keeper
        )
        
        # Update all subcategories to point to the keeper
        subcats_count = CategoriaProducto.objects.filter(categoria_padre=to_remove).count()
        CategoriaProducto.objects.filter(categoria_padre=to_remove).update(
            categoria_padre=keeper
        )
        
        # Delete the category to remove
        to_remove.delete()
        
        self.stdout.write(self.style.SUCCESS(f"  ✓ Categorías fusionadas exitosamente")) 