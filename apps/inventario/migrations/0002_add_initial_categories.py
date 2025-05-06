from django.db import migrations

def crear_categorias_iniciales(apps, schema_editor):
    CategoriaProducto = apps.get_model('inventario', 'CategoriaProducto')
    
    # Categorías principales
    categorias_principales = [
        {
            'nombre': 'Insumos Agrícolas',
            'descripcion': 'Productos y materiales necesarios para la producción agrícola'
        },
        {
            'nombre': 'Maquinaria y Equipos',
            'descripcion': 'Equipamiento y herramientas para agricultura y ganadería'
        },
        {
            'nombre': 'Productos Ganaderos',
            'descripcion': 'Productos relacionados con la cría y cuidado de ganado'
        },
        {
            'nombre': 'Productos Agrícolas',
            'descripcion': 'Productos cultivados listos para la venta'
        },
        {
            'nombre': 'Sanidad Animal',
            'descripcion': 'Productos veterinarios y de cuidado animal'
        },
        {
            'nombre': 'Alimentación Animal',
            'descripcion': 'Alimentos y suplementos para animales'
        }
    ]
    
    # Crear las categorías principales
    categorias_creadas = {}
    for cat in categorias_principales:
        categoria = CategoriaProducto.objects.create(
            nombre_categoria=cat['nombre'],
            descripcion=cat['descripcion']
        )
        categorias_creadas[cat['nombre']] = categoria
    
    # Subcategorías por categoría principal
    subcategorias = {
        'Insumos Agrícolas': [
            ('Fertilizantes', 'Fertilizantes químicos y orgánicos'),
            ('Semillas', 'Semillas certificadas de diferentes cultivos'),
            ('Agroquímicos', 'Pesticidas, herbicidas y fungicidas'),
            ('Sistemas de Riego', 'Equipos y materiales para riego'),
            ('Sustratos y Tierra', 'Sustratos y mezclas de tierra para cultivo')
        ],
        'Maquinaria y Equipos': [
            ('Tractores', 'Tractores y accesorios'),
            ('Herramientas Manuales', 'Herramientas para trabajo agrícola'),
            ('Equipos de Fumigación', 'Fumigadoras y atomizadores'),
            ('Sistemas de Ordeño', 'Equipos para ordeño mecánico'),
            ('Maquinaria de Cosecha', 'Equipos para cosecha y post-cosecha')
        ],
        'Productos Ganaderos': [
            ('Ganado Bovino', 'Vacas, toros y terneros'),
            ('Ganado Ovino', 'Ovejas y corderos'),
            ('Ganado Porcino', 'Cerdos y lechones'),
            ('Aves de Corral', 'Pollos, gallinas y otras aves'),
            ('Productos Lácteos', 'Leche y derivados')
        ],
        'Productos Agrícolas': [
            ('Cereales', 'Maíz, trigo, arroz y otros cereales'),
            ('Frutas', 'Frutas frescas de temporada'),
            ('Hortalizas', 'Verduras y hortalizas frescas'),
            ('Legumbres', 'Frijoles, lentejas y otras legumbres'),
            ('Cultivos Industriales', 'Café, cacao y otros cultivos industriales')
        ],
        'Sanidad Animal': [
            ('Medicamentos', 'Medicamentos veterinarios'),
            ('Vacunas', 'Vacunas para diferentes especies'),
            ('Desparasitantes', 'Productos para control de parásitos'),
            ('Instrumental Veterinario', 'Equipos y herramientas veterinarias'),
            ('Productos de Higiene', 'Productos para limpieza y desinfección')
        ],
        'Alimentación Animal': [
            ('Alimento Balanceado', 'Alimentos completos balanceados'),
            ('Forrajes', 'Heno, paja y forrajes'),
            ('Suplementos', 'Vitaminas y suplementos alimenticios'),
            ('Concentrados', 'Alimentos concentrados'),
            ('Sales Minerales', 'Sales y complementos minerales')
        ]
    }
    
    # Crear las subcategorías
    for categoria_principal, subs in subcategorias.items():
        categoria_padre = categorias_creadas[categoria_principal]
        for nombre, descripcion in subs:
            CategoriaProducto.objects.create(
                nombre_categoria=nombre,
                descripcion=descripcion,
                categoria_padre=categoria_padre
            )

def revertir_categorias(apps, schema_editor):
    CategoriaProducto = apps.get_model('inventario', 'CategoriaProducto')
    CategoriaProducto.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('inventario', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_categorias_iniciales, revertir_categorias),
    ] 