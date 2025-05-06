from django.db import migrations
from django.utils.text import slugify

def crear_categorias_agro(apps, schema_editor):
    CategoriaProducto = apps.get_model('inventario', 'CategoriaProducto')
    
    # Crear categoría principal de Agricultura
    agricultura = CategoriaProducto.objects.create(
        nombre_categoria="Agricultura",
        descripcion="Productos y servicios relacionados con la agricultura"
    )
    
    # Subcategorías de Agricultura
    subcategorias_agricultura = [
        {
            "nombre": "Semillas y Plantines",
            "descripcion": "Semillas, plantines y material de propagación"
        },
        {
            "nombre": "Fertilizantes",
            "descripcion": "Fertilizantes, abonos y mejoradores de suelo"
        },
        {
            "nombre": "Maquinaria Agrícola",
            "descripcion": "Maquinaria y equipos para agricultura"
        },
        {
            "nombre": "Herramientas",
            "descripcion": "Herramientas manuales y equipos menores"
        },
        {
            "nombre": "Riego",
            "descripcion": "Sistemas y equipos de riego"
        },
        {
            "nombre": "Hidroponía",
            "descripcion": "Sistemas, equipos y suministros para cultivos hidropónicos, incluyendo sistemas NFT, sustratos, nutrientes y monitoreo"
        },
        {
            "nombre": "Acuaponía",
            "descripcion": "Equipamiento y suministros para sistemas acuapónicos, combinando acuicultura e hidroponía, incluyendo tanques, bombas y sistemas de filtración"
        }
    ]
    
    for subcat in subcategorias_agricultura:
        CategoriaProducto.objects.create(
            nombre_categoria=subcat["nombre"],
            descripcion=subcat["descripcion"],
            categoria_padre=agricultura
        )
    
    # Crear categoría principal de Ganadería
    ganaderia = CategoriaProducto.objects.create(
        nombre_categoria="Ganadería",
        descripcion="Productos y servicios relacionados con la ganadería"
    )
    
    # Subcategorías de Ganadería
    subcategorias_ganaderia = [
        {
            "nombre": "Alimentación Animal",
            "descripcion": "Alimentos balanceados y suplementos"
        },
        {
            "nombre": "Sanidad Animal",
            "descripcion": "Productos veterinarios y de sanidad animal"
        },
        {
            "nombre": "Equipamiento Ganadero",
            "descripcion": "Equipos y materiales para ganadería"
        },
        {
            "nombre": "Genética y Reproducción",
            "descripcion": "Productos y servicios de mejoramiento genético"
        },
        {
            "nombre": "Cercado y Corrales",
            "descripcion": "Materiales para cercado y construcción de corrales"
        }
    ]
    
    for subcat in subcategorias_ganaderia:
        CategoriaProducto.objects.create(
            nombre_categoria=subcat["nombre"],
            descripcion=subcat["descripcion"],
            categoria_padre=ganaderia
        )

def revertir_categorias(apps, schema_editor):
    CategoriaProducto = apps.get_model('inventario', 'CategoriaProducto')
    CategoriaProducto.objects.filter(
        nombre_categoria__in=[
            "Agricultura", "Ganadería",
            "Semillas y Plantines", "Fertilizantes", "Maquinaria Agrícola",
            "Herramientas", "Riego", "Hidroponía", "Acuaponía",
            "Alimentación Animal", "Sanidad Animal", "Equipamiento Ganadero",
            "Genética y Reproducción", "Cercado y Corrales"
        ]
    ).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('inventario', '0003_alter_inventarioalmacen_options_and_more'),
    ]

    operations = [
        migrations.RunPython(crear_categorias_agro, revertir_categorias),
    ] 