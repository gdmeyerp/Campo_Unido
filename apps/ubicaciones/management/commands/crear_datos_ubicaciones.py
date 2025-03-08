from django.core.management.base import BaseCommand
from apps.ubicaciones.models import Pais, Estado, Ciudad


class Command(BaseCommand):
    help = 'Crea datos iniciales para la aplicación de ubicaciones (países, estados y ciudades)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando carga de datos de ubicaciones...'))
        
        # 1. Crear México y sus estados/ciudades
        mexico, creado = Pais.objects.get_or_create(
            nombre='México',
            codigo='MX'
        )
        self.stdout.write(self.style.SUCCESS(f'País {"creado" if creado else "cargado"}: {mexico.nombre}'))
        
        # Estados de México
        jalisco, creado = Estado.objects.get_or_create(
            nombre='Jalisco',
            codigo='JAL',
            pais=mexico
        )
        self.stdout.write(self.style.SUCCESS(f'Estado {"creado" if creado else "cargado"}: {jalisco.nombre}'))
        
        ciudad_mexico, creado = Estado.objects.get_or_create(
            nombre='Ciudad de México',
            codigo='CDMX',
            pais=mexico
        )
        self.stdout.write(self.style.SUCCESS(f'Estado {"creado" if creado else "cargado"}: {ciudad_mexico.nombre}'))
        
        nuevo_leon, creado = Estado.objects.get_or_create(
            nombre='Nuevo León',
            codigo='NL',
            pais=mexico
        )
        self.stdout.write(self.style.SUCCESS(f'Estado {"creado" if creado else "cargado"}: {nuevo_leon.nombre}'))
        
        # Ciudades de Jalisco
        guadalajara, creado = Ciudad.objects.get_or_create(
            nombre='Guadalajara',
            estado=jalisco
        )
        self.stdout.write(self.style.SUCCESS(f'Ciudad {"creada" if creado else "cargada"}: {guadalajara.nombre}'))
        
        zapopan, creado = Ciudad.objects.get_or_create(
            nombre='Zapopan',
            estado=jalisco
        )
        self.stdout.write(self.style.SUCCESS(f'Ciudad {"creada" if creado else "cargada"}: {zapopan.nombre}'))
        
        # Ciudades de CDMX
        cdmx, creado = Ciudad.objects.get_or_create(
            nombre='Ciudad de México',
            estado=ciudad_mexico
        )
        self.stdout.write(self.style.SUCCESS(f'Ciudad {"creada" if creado else "cargada"}: {cdmx.nombre}'))
        
        # Ciudades de Nuevo León
        monterrey, creado = Ciudad.objects.get_or_create(
            nombre='Monterrey',
            estado=nuevo_leon
        )
        self.stdout.write(self.style.SUCCESS(f'Ciudad {"creada" if creado else "cargada"}: {monterrey.nombre}'))
        
        # 2. Crear Estados Unidos y sus estados/ciudades
        usa, creado = Pais.objects.get_or_create(
            nombre='Estados Unidos',
            codigo='US'
        )
        self.stdout.write(self.style.SUCCESS(f'País {"creado" if creado else "cargado"}: {usa.nombre}'))
        
        # Estados de EE.UU.
        california, creado = Estado.objects.get_or_create(
            nombre='California',
            codigo='CA',
            pais=usa
        )
        self.stdout.write(self.style.SUCCESS(f'Estado {"creado" if creado else "cargado"}: {california.nombre}'))
        
        texas, creado = Estado.objects.get_or_create(
            nombre='Texas',
            codigo='TX',
            pais=usa
        )
        self.stdout.write(self.style.SUCCESS(f'Estado {"creado" if creado else "cargado"}: {texas.nombre}'))
        
        florida, creado = Estado.objects.get_or_create(
            nombre='Florida',
            codigo='FL',
            pais=usa
        )
        self.stdout.write(self.style.SUCCESS(f'Estado {"creado" if creado else "cargado"}: {florida.nombre}'))
        
        # Ciudades de California
        los_angeles, creado = Ciudad.objects.get_or_create(
            nombre='Los Angeles',
            estado=california
        )
        self.stdout.write(self.style.SUCCESS(f'Ciudad {"creada" if creado else "cargada"}: {los_angeles.nombre}'))
        
        san_francisco, creado = Ciudad.objects.get_or_create(
            nombre='San Francisco',
            estado=california
        )
        self.stdout.write(self.style.SUCCESS(f'Ciudad {"creada" if creado else "cargada"}: {san_francisco.nombre}'))
        
        # Ciudades de Texas
        houston, creado = Ciudad.objects.get_or_create(
            nombre='Houston',
            estado=texas
        )
        self.stdout.write(self.style.SUCCESS(f'Ciudad {"creada" if creado else "cargada"}: {houston.nombre}'))
        
        dallas, creado = Ciudad.objects.get_or_create(
            nombre='Dallas',
            estado=texas
        )
        self.stdout.write(self.style.SUCCESS(f'Ciudad {"creada" if creado else "cargada"}: {dallas.nombre}'))
        
        # Ciudades de Florida
        miami, creado = Ciudad.objects.get_or_create(
            nombre='Miami',
            estado=florida
        )
        self.stdout.write(self.style.SUCCESS(f'Ciudad {"creada" if creado else "cargada"}: {miami.nombre}'))
        
        # 3. Crear España y sus provincias/ciudades
        espana, creado = Pais.objects.get_or_create(
            nombre='España',
            codigo='ES'
        )
        self.stdout.write(self.style.SUCCESS(f'País {"creado" if creado else "cargado"}: {espana.nombre}'))
        
        # Comunidades de España
        madrid, creado = Estado.objects.get_or_create(
            nombre='Comunidad de Madrid',
            codigo='MAD',
            pais=espana
        )
        self.stdout.write(self.style.SUCCESS(f'Estado {"creado" if creado else "cargado"}: {madrid.nombre}'))
        
        cataluna, creado = Estado.objects.get_or_create(
            nombre='Cataluña',
            codigo='CAT',
            pais=espana
        )
        self.stdout.write(self.style.SUCCESS(f'Estado {"creado" if creado else "cargado"}: {cataluna.nombre}'))
        
        # Ciudades de Madrid
        madrid_ciudad, creado = Ciudad.objects.get_or_create(
            nombre='Madrid',
            estado=madrid
        )
        self.stdout.write(self.style.SUCCESS(f'Ciudad {"creada" if creado else "cargada"}: {madrid_ciudad.nombre}'))
        
        # Ciudades de Cataluña
        barcelona, creado = Ciudad.objects.get_or_create(
            nombre='Barcelona',
            estado=cataluna
        )
        self.stdout.write(self.style.SUCCESS(f'Ciudad {"creada" if creado else "cargada"}: {barcelona.nombre}'))
        
        self.stdout.write(self.style.SUCCESS('Carga de datos de ubicaciones completada correctamente!')) 