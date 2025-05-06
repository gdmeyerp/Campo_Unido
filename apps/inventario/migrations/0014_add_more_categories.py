from django.db import migrations
from django.utils.text import slugify

def crear_mas_categorias(apps, schema_editor):
    CategoriaProducto = apps.get_model('inventario', 'CategoriaProducto')
    
    # Obtener categorías principales existentes
    try:
        agricultura = CategoriaProducto.objects.get(nombre_categoria="Agricultura")
    except CategoriaProducto.DoesNotExist:
        agricultura = CategoriaProducto.objects.create(
            nombre_categoria="Agricultura",
            descripcion="Productos y servicios relacionados con la agricultura"
        )
    
    # Nuevas subcategorías de Agricultura
    nuevas_subcategorias_agricultura = [
        {
            "nombre": "Agroquímicos",
            "descripcion": "Productos químicos utilizados en la agricultura para mejorar el rendimiento y proteger los cultivos"
        },
        {
            "nombre": "Protección de cultivos",
            "descripcion": "Productos y sistemas para proteger cultivos de plagas, enfermedades y condiciones ambientales adversas"
        },
        {
            "nombre": "Agricultura Vertical",
            "descripcion": "Sistemas y equipos para cultivo en vertical, aprovechando el espacio en altura"
        },
        {
            "nombre": "Cultivos Hidropónicos",
            "descripcion": "Cultivos específicos adaptados a sistemas hidropónicos, técnicas y nutrientes especializados"
        },
        {
            "nombre": "Cultivos Acuapónicos",
            "descripcion": "Plantas adaptadas a sistemas acuapónicos y componentes biológicos complementarios"
        },
        {
            "nombre": "Cultivos Urbanos",
            "descripcion": "Equipos, semillas y accesorios para cultivos en espacios urbanos y huertos urbanos"
        },
        {
            "nombre": "Invernaderos",
            "descripcion": "Estructuras, cubiertas, sistemas de control climático y accesorios para invernaderos"
        },
        {
            "nombre": "Agricultura Orgánica",
            "descripcion": "Insumos certificados, herramientas especializadas y productos para agricultura orgánica"
        },
        {
            "nombre": "Automatización Agrícola",
            "descripcion": "Sistemas de control, sensores, autómatas y equipos para automatización de cultivos"
        },
        {
            "nombre": "Equipos para Análisis",
            "descripcion": "Instrumentos y kits para análisis de suelo, agua, nutrientes y parámetros de cultivo"
        },
        {
            "nombre": "Sustratos Especializados",
            "descripcion": "Medios de cultivo específicos para diferentes técnicas de cultivo sin suelo"
        },
        {
            "nombre": "Cultivos Tradicionales",
            "descripcion": "Insumos y técnicas para cultivos tradicionales y ancestrales"
        }
    ]
    
    # Crear las nuevas subcategorías
    for subcat in nuevas_subcategorias_agricultura:
        # Verificar si ya existe la categoría
        if not CategoriaProducto.objects.filter(nombre_categoria=subcat["nombre"]).exists():
            CategoriaProducto.objects.create(
                nombre_categoria=subcat["nombre"],
                descripcion=subcat["descripcion"],
                categoria_padre=agricultura
            )

def revertir_categorias(apps, schema_editor):
    CategoriaProducto = apps.get_model('inventario', 'CategoriaProducto')
    # Nombres de categorías a eliminar
    nombres_categorias = [
        "Agroquímicos", "Protección de cultivos", "Agricultura Vertical",
        "Cultivos Hidropónicos", "Cultivos Acuapónicos", "Cultivos Urbanos",
        "Invernaderos", "Agricultura Orgánica", "Automatización Agrícola",
        "Equipos para Análisis", "Sustratos Especializados", "Cultivos Tradicionales"
    ]
    CategoriaProducto.objects.filter(nombre_categoria__in=nombres_categorias).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('inventario', '0013_merge_20250428_2014'),
    ]

    operations = [
        migrations.RunPython(crear_mas_categorias, revertir_categorias),
    ] 