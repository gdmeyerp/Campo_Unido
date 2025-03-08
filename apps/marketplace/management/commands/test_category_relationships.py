from django.core.management.base import BaseCommand
from apps.marketplace.models import CategoriaProducto, MarketplaceProducto

class Command(BaseCommand):
    help = 'Tests the relationship between products and categories'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing category relationships...'))
        
        # List all categories
        categories = CategoriaProducto.objects.all()
        self.stdout.write(f"Total categories: {categories.count()}")
        
        for cat in categories:
            self.stdout.write(f"\nCategory: {cat.nombre_categoria} (ID: {cat.categoria_producto_id})")
            
            # List products in this category
            products = MarketplaceProducto.objects.filter(categoria_producto_id_id=cat)
            self.stdout.write(f"  - Products in this category: {products.count()}")
            
            for product in products:
                self.stdout.write(f"    - {product.nombre_producto} (ID: {product.producto_id})")
                
                # Verify the relationship works both ways
                category_from_product = product.categoria_producto_id_id
                if category_from_product:
                    self.stdout.write(f"      - Category from product: {category_from_product.nombre_categoria} (ID: {category_from_product.categoria_producto_id})")
                    if category_from_product.categoria_producto_id == cat.categoria_producto_id:
                        self.stdout.write(self.style.SUCCESS("      ✓ Relationship verified"))
                    else:
                        self.stdout.write(self.style.ERROR("      ✗ Relationship mismatch"))
                else:
                    self.stdout.write(self.style.ERROR("      ✗ Product has no category"))
        
        self.stdout.write(self.style.SUCCESS('\nTest completed.')) 