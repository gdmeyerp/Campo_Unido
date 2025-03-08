from django.core.management.base import BaseCommand
from apps.inventario.models import CategoriaProducto, EstadoProducto

class Command(BaseCommand):
    help = 'Crea datos iniciales para el sistema de inventario (categorías y estados)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando carga de datos...'))
        
        # Crear categorías predeterminadas
        categorias = [
            {'nombre': 'Insumos Agrícolas', 'descripcion': 'Semillas, fertilizantes, pesticidas y otros insumos para agricultura'},
            {'nombre': 'Herramientas', 'descripcion': 'Herramientas manuales y eléctricas para el campo'},
            {'nombre': 'Maquinaria', 'descripcion': 'Equipos y maquinaria agrícola'},
            {'nombre': 'Alimentos para Animales', 'descripcion': 'Concentrados, forrajes y suplementos para ganado'},
            {'nombre': 'Productos Veterinarios', 'descripcion': 'Medicamentos, vacunas y suplementos para animales'},
            {'nombre': 'Productos Procesados', 'descripcion': 'Alimentos y productos procesados listos para venta'},
        ]
        
        for cat_data in categorias:
            categoria, created = CategoriaProducto.objects.get_or_create(
                nombre_categoria=cat_data['nombre'],
                defaults={'descripcion': cat_data['descripcion']}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Categoría creada: {categoria.nombre_categoria}'))
            else:
                self.stdout.write(self.style.WARNING(f'La categoría {categoria.nombre_categoria} ya existe'))
        
        # Crear subcategorías para Insumos Agrícolas
        cat_insumos = CategoriaProducto.objects.filter(nombre_categoria='Insumos Agrícolas').first()
        if cat_insumos:
            subcategorias_insumos = [
                {'nombre': 'Semillas', 'descripcion': 'Todo tipo de semillas para cultivos'},
                {'nombre': 'Fertilizantes', 'descripcion': 'Abonos orgánicos e inorgánicos'},
                {'nombre': 'Pesticidas', 'descripcion': 'Productos para control de plagas'},
                {'nombre': 'Herbicidas', 'descripcion': 'Productos para control de malezas'},
            ]
            
            for subcat_data in subcategorias_insumos:
                subcategoria, created = CategoriaProducto.objects.get_or_create(
                    nombre_categoria=subcat_data['nombre'],
                    defaults={
                        'descripcion': subcat_data['descripcion'],
                        'categoria_padre': cat_insumos
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Subcategoría creada: {subcategoria.nombre_categoria}'))
                else:
                    self.stdout.write(self.style.WARNING(f'La subcategoría {subcategoria.nombre_categoria} ya existe'))
        
        # Crear estados predeterminados
        estados = [
            'Disponible',
            'Agotado',
            'Próximo a vencer',
            'En oferta',
            'Reservado',
            'Inactivo'
        ]
        
        for nombre_estado in estados:
            estado, created = EstadoProducto.objects.get_or_create(nombre_estado=nombre_estado)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Estado creado: {estado.nombre_estado}'))
            else:
                self.stdout.write(self.style.WARNING(f'El estado {estado.nombre_estado} ya existe'))
        
        self.stdout.write(self.style.SUCCESS('Carga de datos completada correctamente')) 