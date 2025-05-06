from django.db import migrations

def fix_duplicate_categories(apps, schema_editor):
    CategoriaProducto = apps.get_model('inventario', 'CategoriaProducto')
    ProductoInventario = apps.get_model('inventario', 'ProductoInventario')
    
    # Dictionary to track which categories to merge
    categories_to_merge = {}
    
    # Step 1: Find categories with the same name or similar concepts
    # First, get all categories
    all_categories = list(CategoriaProducto.objects.all().order_by('id'))
    
    # Categories to analyze for duplication
    duplicate_pairs = [
        # Format: [newer_category_name, older_category_name_to_keep]
        ["Fertilizantes", "Fertilizantes"],  # From Agricultura vs initial categories
        ["Alimentación Animal", "Alimentación Animal"],  # From Ganadería vs initial categories
        ["Hidroponía", "Cultivos Hidropónicos"],  # Possible duplicates with different names
        ["Acuaponía", "Cultivos Acuapónicos"],  # Possible duplicates with different names
    ]
    
    # Process each pair of potential duplicates
    for newer_name, older_name in duplicate_pairs:
        newer_cats = list(CategoriaProducto.objects.filter(nombre_categoria=newer_name))
        older_cats = list(CategoriaProducto.objects.filter(nombre_categoria=older_name))
        
        # Skip if there's only one category with this name
        if len(newer_cats) <= 1 and len(older_cats) <= 1 and newer_name == older_name:
            continue
            
        # For categories with the same name, keep the one that's used in products
        if newer_name == older_name and len(newer_cats) > 1:
            categories = sorted(newer_cats, key=lambda x: x.id)
            # Keep the oldest category (lowest ID) as that's likely the one used in statistics
            keeper = categories[0]
            
            # Mark all others for merging
            for category in categories[1:]:
                categories_to_merge[category.id] = keeper.id
        
        # For categories with different names but similar concept
        elif newer_name != older_name:
            newer_matches = CategoriaProducto.objects.filter(nombre_categoria=newer_name)
            older_matches = CategoriaProducto.objects.filter(nombre_categoria=older_name)
            
            # If both exist, keep the older one with products
            if newer_matches.exists() and older_matches.exists():
                newer_cat = newer_matches.first()
                older_cat = older_matches.first()
                
                # Check which one has products
                newer_product_count = ProductoInventario.objects.filter(categoria_producto=newer_cat).count()
                older_product_count = ProductoInventario.objects.filter(categoria_producto=older_cat).count()
                
                # Keep the one with more products, or the older one if equal
                if newer_product_count > older_product_count:
                    categories_to_merge[older_cat.id] = newer_cat.id
                else:
                    categories_to_merge[newer_cat.id] = older_cat.id
    
    # Step 2: Merge the categories
    for category_to_remove_id, keeper_id in categories_to_merge.items():
        try:
            category_to_remove = CategoriaProducto.objects.get(id=category_to_remove_id)
            keeper = CategoriaProducto.objects.get(id=keeper_id)
            
            # Update all products using the category to be removed
            ProductoInventario.objects.filter(categoria_producto=category_to_remove).update(
                categoria_producto=keeper
            )
            
            # Update all subcategories to point to the keeper
            CategoriaProducto.objects.filter(categoria_padre=category_to_remove).update(
                categoria_padre=keeper
            )
            
            # Delete the duplicate category
            category_to_remove.delete()
        except CategoriaProducto.DoesNotExist:
            # Skip if the category doesn't exist (already deleted)
            pass

def reverse_migration(apps, schema_editor):
    # This migration cannot be reversed precisely since we're deleting data
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('inventario', '0014_add_more_categories'),
    ]

    operations = [
        migrations.RunPython(fix_duplicate_categories, reverse_migration),
    ] 