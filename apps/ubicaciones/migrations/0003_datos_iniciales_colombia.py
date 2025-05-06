from django.db import migrations

def crear_datos_colombia(apps, schema_editor):
    Pais = apps.get_model('ubicaciones', 'Pais')
    Estado = apps.get_model('ubicaciones', 'Estado')
    Ciudad = apps.get_model('ubicaciones', 'Ciudad')
    
    # Crear Colombia si no existe
    colombia, _ = Pais.objects.get_or_create(
        nombre='Colombia',
        codigo='COL'
    )
    
    # Diccionario de departamentos y sus ciudades principales
    departamentos = {
        'Antioquia': ['Medellín', 'Bello', 'Envigado', 'Itagüí', 'Rionegro'],
        'Atlántico': ['Barranquilla', 'Soledad', 'Malambo', 'Puerto Colombia'],
        'Bogotá D.C.': ['Bogotá'],
        'Bolívar': ['Cartagena', 'Magangué', 'Turbaco', 'Arjona'],
        'Boyacá': ['Tunja', 'Duitama', 'Sogamoso', 'Paipa'],
        'Caldas': ['Manizales', 'La Dorada', 'Chinchiná', 'Villamaría'],
        'Caquetá': ['Florencia', 'San Vicente del Caguán', 'Puerto Rico'],
        'Cauca': ['Popayán', 'Santander de Quilichao', 'Puerto Tejada'],
        'Cesar': ['Valledupar', 'Aguachica', 'Bosconia', 'La Jagua de Ibirico'],
        'Córdoba': ['Montería', 'Lorica', 'Cereté', 'Sahagún'],
        'Cundinamarca': ['Soacha', 'Facatativá', 'Zipaquirá', 'Chía', 'Mosquera'],
        'Huila': ['Neiva', 'Pitalito', 'Garzón', 'La Plata'],
        'La Guajira': ['Riohacha', 'Maicao', 'Uribia', 'Fonseca'],
        'Magdalena': ['Santa Marta', 'Ciénaga', 'Fundación', 'Plato'],
        'Meta': ['Villavicencio', 'Acacías', 'Granada', 'Puerto López'],
        'Nariño': ['Pasto', 'Ipiales', 'Tumaco', 'Túquerres'],
        'Norte de Santander': ['Cúcuta', 'Ocaña', 'Pamplona', 'Los Patios'],
        'Quindío': ['Armenia', 'Calarcá', 'Montenegro', 'La Tebaida'],
        'Risaralda': ['Pereira', 'Dosquebradas', 'Santa Rosa de Cabal', 'La Virginia'],
        'Santander': ['Bucaramanga', 'Floridablanca', 'Girón', 'Piedecuesta', 'Barrancabermeja'],
        'Sucre': ['Sincelejo', 'Corozal', 'Santiago de Tolú', 'San Marcos'],
        'Tolima': ['Ibagué', 'Espinal', 'Melgar', 'Chaparral'],
        'Valle del Cauca': ['Cali', 'Buenaventura', 'Palmira', 'Tuluá', 'Yumbo']
    }
    
    # Crear departamentos y ciudades
    for dep_nombre, ciudades in departamentos.items():
        departamento, _ = Estado.objects.get_or_create(
            nombre=dep_nombre,
            pais=colombia
        )
        
        # Crear ciudades para cada departamento
        for ciudad_nombre in ciudades:
            Ciudad.objects.get_or_create(
                nombre=ciudad_nombre,
                estado=departamento
            )

def revertir_datos_colombia(apps, schema_editor):
    Pais = apps.get_model('ubicaciones', 'Pais')
    Pais.objects.filter(codigo='COL').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('ubicaciones', '0002_areaservicio_preferenciaubicacion_ubicacionproducto'),
    ]

    operations = [
        migrations.RunPython(crear_datos_colombia, revertir_datos_colombia),
    ] 