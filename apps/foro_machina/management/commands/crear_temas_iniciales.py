from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from machina.core.db.models import get_model
from django.utils.text import slugify
from django.utils import timezone
import random

User = get_user_model()
Forum = get_model('forum', 'Forum')
Topic = get_model('forum_conversation', 'Topic')
Post = get_model('forum_conversation', 'Post')

class Command(BaseCommand):
    help = 'Crea temas iniciales para los foros existentes'

    def handle(self, *args, **options):
        # Obtener o crear usuario administrador
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                self.stdout.write(self.style.ERROR('No se encontró un usuario administrador. Por favor, crea uno primero.'))
                return
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('No se encontró un usuario administrador. Por favor, crea uno primero.'))
            return
        
        # Definir temas para cada foro
        temas_por_foro = {
            'Sistemas NFT': [
                {
                    'titulo': 'Guía para principiantes: Cómo construir tu primer sistema NFT',
                    'contenido': 'En esta guía, te mostraré paso a paso cómo construir un sistema NFT básico con materiales accesibles. Los sistemas NFT (Nutrient Film Technique) son ideales para cultivar lechugas, hierbas y vegetales de hoja verde.\n\nMateriales necesarios:\n- Tubos de PVC de 4 pulgadas\n- Bomba de agua sumergible\n- Depósito para solución nutritiva\n- Mangueras\n- Temporizador\n\nPasos para la construcción...'
                },
                {
                    'titulo': 'Problemas comunes en sistemas NFT y cómo solucionarlos',
                    'contenido': 'Después de varios años utilizando sistemas NFT, he identificado los problemas más comunes y sus soluciones:\n\n1. Obstrucción de canales: Limpiar regularmente los canales y utilizar filtros adecuados.\n2. Raíces demasiado largas: Podar las raíces periódicamente para evitar bloqueos.\n3. Temperatura de la solución: Mantener la solución entre 18-22°C para óptima absorción de nutrientes.\n4. Fallas en la bomba: Tener siempre una bomba de respaldo y un sistema de alerta.'
                },
                {
                    'titulo': 'Comparativa de diferentes diseños de sistemas NFT',
                    'contenido': 'He experimentado con varios diseños de sistemas NFT y quiero compartir mis resultados:\n\n- Sistema vertical: Ahorra espacio pero tiene problemas de distribución uniforme de nutrientes.\n- Sistema horizontal tradicional: El más confiable y fácil de mantener.\n- Sistema NFT en zigzag: Maximiza el espacio pero complica la limpieza.\n\nCada diseño tiene sus ventajas dependiendo del espacio disponible y los cultivos que planeas sembrar.'
                }
            ],
            'Sistemas DWC': [
                {
                    'titulo': 'Mi experiencia con DWC para cultivo de tomates',
                    'contenido': 'Llevo 2 años cultivando tomates en sistemas DWC (Deep Water Culture) y quiero compartir mi experiencia. Los tomates cherry han sido particularmente exitosos, produciendo cosechas abundantes durante todo el año.\n\nPuntos clave para el éxito:\n- Oxigenación constante con piedras difusoras de alta calidad\n- Monitoreo diario de EC y pH\n- Cambio parcial de solución cada 7-10 días\n- Soporte adecuado para las plantas a medida que crecen'
                },
                {
                    'titulo': 'Sistemas RDWC: Ventajas sobre DWC tradicional',
                    'contenido': 'Los sistemas RDWC (Recirculating Deep Water Culture) ofrecen varias ventajas sobre los sistemas DWC tradicionales:\n\n1. Distribución uniforme de nutrientes entre todas las plantas\n2. Facilidad para ajustar pH y EC en un solo depósito\n3. Menor riesgo de fluctuaciones de temperatura\n4. Mantenimiento simplificado\n\nEn mi experiencia, el costo inicial es mayor pero se compensa con los resultados y la facilidad de manejo.'
                }
            ],
            'Aeroponia': [
                {
                    'titulo': 'Sistema aeropónico casero con nebulizadores',
                    'contenido': 'Construí un sistema aeropónico utilizando nebulizadores de jardín y quiero compartir el proceso. La aeroponia ofrece un crecimiento más rápido que otros métodos hidropónicos debido a la alta oxigenación de las raíces.\n\nComponentes principales:\n- Nebulizadores de 0.5mm\n- Bomba de presión de 60 PSI\n- Temporizador digital (ciclos de 1 minuto on, 4 minutos off)\n- Contenedor hermético a la luz\n\nEl sistema ha funcionado perfectamente para lechugas y hierbas aromáticas.'
                },
                {
                    'titulo': 'Aeroponia de alta presión vs. baja presión',
                    'contenido': 'Después de experimentar con ambos sistemas, puedo comparar la aeroponia de alta presión (true aeroponic) con la de baja presión:\n\nAlta presión (>80 PSI):\n- Gotas más finas (5-50 micrones)\n- Mejor oxigenación\n- Crecimiento más rápido\n- Mayor costo y complejidad\n\nBaja presión (<60 PSI):\n- Más económico y fácil de implementar\n- Menos problemas de obstrucción\n- Resultados buenos aunque no óptimos\n- Ideal para principiantes'
                }
            ],
            'Soluciones Nutritivas': [
                {
                    'titulo': 'Fórmulas nutritivas para cultivos de hoja',
                    'contenido': 'Después de varios años de experimentación, he desarrollado estas fórmulas nutritivas optimizadas para cultivos de hoja como lechuga, espinaca y rúcula:\n\nFórmula básica (por litro de agua):\n- 1.0g Nitrato de Calcio\n- 0.5g Nitrato de Potasio\n- 0.3g Sulfato de Magnesio\n- 0.2g Fosfato Monopotásico\n- 2ml Micronutrientes\n\nEC objetivo: 1.0-1.2 mS/cm\npH: 5.8-6.2'
                },
                {
                    'titulo': 'Cómo preparar soluciones madre concentradas',
                    'contenido': 'Las soluciones madre concentradas facilitan el manejo de nutrientes en sistemas hidropónicos. Aquí explico cómo prepararlas correctamente:\n\nSolución A (Calcio y parte del Nitrógeno):\n- 950g Nitrato de Calcio en 5L de agua\n\nSolución B (resto de macronutrientes):\n- 540g Nitrato de Potasio\n- 120g Fosfato Monopotásico\n- 490g Sulfato de Magnesio\nDisolver en 5L de agua\n\nSolución C (micronutrientes):\n- 50g de mezcla comercial de micronutrientes en 5L de agua\n\nDosificación: 5ml de cada solución por litro de agua final.'
                },
                {
                    'titulo': 'Ajuste de pH: Métodos naturales vs. químicos',
                    'contenido': 'El ajuste de pH es crucial en hidroponía. Comparo métodos naturales y químicos:\n\nMétodos químicos:\n- Ácido fosfórico o nítrico para bajar pH\n- Hidróxido de potasio para subir pH\n- Precisos y rápidos\n\nMétodos naturales:\n- Vinagre de manzana para bajar pH (orgánico)\n- Bicarbonato de sodio para subir pH\n- Menos precisos pero más seguros de manejar\n\nMi recomendación: usar métodos químicos para sistemas comerciales y naturales para pequeños sistemas hogareños.'
                }
            ],
            'Automatización': [
                {
                    'titulo': 'Sistema de monitoreo con Arduino para hidroponía',
                    'contenido': 'He desarrollado un sistema de monitoreo basado en Arduino que supervisa parámetros críticos en mi sistema hidropónico:\n\n- Sensor de pH Atlas Scientific\n- Sensor de EC DFRobot\n- Sensor de temperatura DS18B20\n- Sensor de nivel de agua ultrasónico HC-SR04\n\nEl sistema envía alertas a mi teléfono cuando algún parámetro sale de los rangos establecidos y registra datos históricos en una tarjeta SD para análisis posterior.\n\nComparto el código y esquema de conexiones en este post.'
                },
                {
                    'titulo': 'Control automático de riego con Raspberry Pi',
                    'contenido': 'Mi sistema de control automático basado en Raspberry Pi ha revolucionado mi cultivo hidropónico:\n\n- Programación de ciclos de riego basados en humedad del sustrato\n- Ajuste automático según temperatura ambiente\n- Interfaz web para monitoreo remoto\n- Registro de datos y gráficas de tendencias\n\nEl sistema utiliza relés para controlar bombas y válvulas, y sensores DHT22 para temperatura y humedad. La inversión inicial se recupera rápidamente con el ahorro de agua y nutrientes.'
                }
            ],
            'Hortalizas': [
                {
                    'titulo': 'Calendario de siembra para hortalizas en clima templado',
                    'contenido': 'Comparto mi calendario de siembra para clima templado, basado en 10 años de experiencia:\n\nPrimavera (Sep-Nov):\n- Tomates, pimientos, berenjenas (en semillero protegido)\n- Zanahorias, rábanos, lechugas (siembra directa)\n\nVerano (Dic-Feb):\n- Calabacines, pepinos, melones\n- Maíz dulce, judías verdes\n\nOtoño (Mar-May):\n- Brócoli, coliflor, repollo\n- Espinacas, acelgas, remolachas\n\nInvierno (Jun-Ago):\n- Ajos, cebollas, habas\n- Guisantes, nabos, puerros'
                },
                {
                    'titulo': 'Técnicas de rotación de cultivos para huertos familiares',
                    'contenido': 'La rotación de cultivos es esencial para mantener la salud del suelo. Mi sistema de rotación de 4 años:\n\nAño 1: Leguminosas (frijoles, arvejas, habas) - Fijan nitrógeno\nAño 2: Hojas (lechugas, espinacas, coles) - Consumen mucho nitrógeno\nAño 3: Frutos (tomates, pimientos, berenjenas) - Necesitan fósforo\nAño 4: Raíces (zanahorias, cebollas, ajos) - Airean el suelo\n\nEste sistema ha reducido significativamente las plagas y enfermedades en mi huerto.'
                }
            ],
            'Frutales': [
                {
                    'titulo': 'Guía de poda para árboles frutales jóvenes',
                    'contenido': 'La poda correcta en los primeros años determina la productividad futura del árbol. Mis principios básicos:\n\n1. Primer año: Poda de formación para establecer estructura básica (3-5 ramas principales)\n2. Segundo año: Selección de ramas secundarias y eliminación de chupones\n3. Tercer año: Aclareo para permitir entrada de luz y aire\n\nRecuerda: cada especie tiene sus particularidades. Los cítricos requieren menos poda que los frutales de carozo o pepita.'
                },
                {
                    'titulo': 'Cultivo de fresas en sistemas verticales',
                    'contenido': 'Las fresas son ideales para cultivos verticales, maximizando el espacio y facilitando la cosecha. Mi sistema utiliza tubos de PVC de 4" con orificios de 3" de diámetro, espaciados cada 20cm en disposición escalonada.\n\nPuntos clave:\n- Sustrato: 70% fibra de coco, 30% perlita\n- Riego por goteo con emisores de 2L/h\n- Fertilización semanal con fórmula rica en potasio\n- Renovación de plantas cada 2 años\n\nCon este sistema he logrado producir 5kg de fresas por metro lineal de tubo.'
                }
            ],
            'Cultivos Orgánicos': [
                {
                    'titulo': 'Preparación de compost acelerado en 30 días',
                    'contenido': 'Mi método de compostaje acelerado produce compost de alta calidad en solo 30 días:\n\n1. Mezcla inicial: 2 partes de material marrón (hojas secas, cartón) por 1 parte de material verde (restos de cocina, césped)\n2. Activador: 1 taza de compost maduro o mantillo de bosque por cada 30cm de altura\n3. Volteo: Cada 3 días durante las primeras 2 semanas\n4. Humedad: Como una esponja exprimida (40-60%)\n\nLa temperatura debe alcanzar 65-70°C en la primera semana, lo que elimina patógenos y semillas de malezas.'
                },
                {
                    'titulo': 'Biopreparados caseros para control de plagas',
                    'contenido': 'Estos biopreparados han demostrado ser efectivos en mi huerto orgánico:\n\n1. Purín de ortiga (contra pulgones):\n   - 1kg de ortigas frescas en 10L de agua\n   - Fermentar 7-10 días, remover diariamente\n   - Diluir 1:10 antes de aplicar\n\n2. Macerado de ajo y chile (contra ácaros e insectos masticadores):\n   - 100g de ajo\n   - 50g de chile picante\n   - 10L de agua\n   - 50ml de alcohol\n   - Reposar 48h, filtrar y aplicar diluido 1:5\n\n3. Caldo bordelés (contra hongos):\n   - 100g de sulfato de cobre\n   - 100g de cal viva\n   - 10L de agua'
                }
            ],
            'Control de Plagas': [
                {
                    'titulo': 'Control biológico: Insectos beneficiosos para tu huerto',
                    'contenido': 'El control biológico ha transformado mi huerto. Estos son los insectos beneficiosos que introduje y sus resultados:\n\n1. Mariquitas (Coccinellidae): Controlaron eficazmente los pulgones en mis pimientos y rosas\n2. Crisopas (Chrysoperla carnea): Excelentes para controlar trips, mosca blanca y ácaros\n3. Avispas parasitoides (Trichogramma): Redujeron en un 80% las orugas de polillas\n4. Ácaros depredadores (Phytoseiulus persimilis): Eliminaron la araña roja de mis tomates\n\nLa clave es crear un hábitat adecuado con plantas nectaríferas como hinojo, eneldo y caléndula para atraer y mantener estos aliados.'
                },
                {
                    'titulo': 'Identificación y tratamiento de enfermedades fúngicas comunes',
                    'contenido': 'Guía para identificar y tratar las enfermedades fúngicas más comunes:\n\n1. Oídio (polvo blanco en hojas):\n   - Tratamiento: Bicarbonato de sodio (5g/L) con aceite de neem (5ml/L)\n   - Prevención: Espaciado adecuado, riego por la mañana\n\n2. Mildiu (manchas amarillas en el haz, moho grisáceo en el envés):\n   - Tratamiento: Caldo bordelés o productos a base de cobre\n   - Prevención: Evitar mojar el follaje, mejorar ventilación\n\n3. Botrytis (moho gris en frutos y tallos):\n   - Tratamiento: Eliminar partes afectadas, aplicar Trichoderma\n   - Prevención: Control de humedad, poda para airear\n\nRecuerda: la identificación temprana es clave para un control efectivo.'
                }
            ],
            'Presentaciones': [
                {
                    'titulo': 'Hola desde Bogotá: Mi proyecto de hidroponía urbana',
                    'contenido': 'Hola a todos, soy Carlos desde Bogotá. Quiero presentarme y compartir mi proyecto de hidroponía urbana que inicié hace 6 meses en la terraza de mi apartamento.\n\nActualmente tengo un sistema NFT con 48 sitios donde cultivo principalmente lechugas, albahaca y cilantro. También estoy experimentando con un pequeño sistema DWC para tomates cherry.\n\nMi objetivo es demostrar que es posible producir alimentos frescos y saludables en espacios urbanos reducidos. Espero aprender mucho de esta comunidad y compartir mis avances.'
                },
                {
                    'titulo': 'Presentación: Proyecto educativo de hidroponía en escuelas rurales',
                    'contenido': 'Saludos desde Medellín. Soy María, profesora de ciencias naturales, y estoy implementando sistemas hidropónicos en escuelas rurales como herramienta educativa.\n\nEl proyecto busca enseñar principios de biología, química y física de forma práctica, mientras los estudiantes producen alimentos para el comedor escolar.\n\nHasta ahora hemos instalado sistemas en 5 escuelas, beneficiando a más de 300 estudiantes. Los resultados han sido sorprendentes, no solo en términos educativos sino también en el impacto en la nutrición de los niños.\n\nMe uno a este foro para compartir experiencias y buscar ideas para mejorar nuestros sistemas con materiales económicos y accesibles.'
                }
            ],
            'Noticias y Eventos': [
                {
                    'titulo': 'Feria de Agricultura Urbana 2025 - Bogotá',
                    'contenido': 'Me complace anunciar la Feria de Agricultura Urbana 2025 que se realizará en Bogotá del 15 al 17 de marzo en el Jardín Botánico.\n\nActividades principales:\n- Exposición de sistemas hidropónicos y acuapónicos\n- Talleres prácticos de construcción de sistemas caseros\n- Conferencias sobre tecnologías de cultivo urbano\n- Intercambio de semillas y plántulas\n- Concurso de innovación en agricultura urbana\n\nLa entrada es gratuita previa inscripción en el sitio web del Jardín Botánico. ¡Espero verlos allí!'
                },
                {
                    'titulo': 'Nueva normativa para agricultura urbana en Colombia',
                    'contenido': 'El Ministerio de Agricultura acaba de publicar la nueva normativa que regula y promueve la agricultura urbana en Colombia. Puntos destacados:\n\n1. Incentivos fiscales para proyectos productivos en zonas urbanas\n2. Simplificación de trámites para comercialización de productos\n3. Programas de capacitación y asistencia técnica gratuitos\n4. Líneas de crédito especiales para emprendimientos de agricultura urbana\n\nEsta normativa representa un gran avance para quienes nos dedicamos a la producción de alimentos en entornos urbanos. El documento completo está disponible en la página del ministerio.'
                }
            ],
            'Mercado': [
                {
                    'titulo': 'Vendo: Sistema NFT completo 48 sitios',
                    'contenido': 'Vendo sistema NFT completo para 48 plantas, usado solo durante 3 meses (me mudo de ciudad).\n\nIncluye:\n- 4 canales de PVC de 3 metros con 12 sitios cada uno\n- Depósito de 120 litros con tapa\n- Bomba sumergible de 800L/h\n- Temporizador digital programable\n- Kit completo de nutrientes para 3 meses\n- Manual de operación y mantenimiento\n\nPrecio: $450.000 COP (negociable)\nUbicación: Medellín, sector El Poblado\nContacto: Por mensaje privado'
                },
                {
                    'titulo': 'Busco: Semillas de variedades raras de tomate',
                    'contenido': 'Estoy buscando semillas de variedades poco comunes de tomate para mi colección y cultivo experimental. Especialmente interesado en:\n\n- Black Krim\n- Green Zebra\n- Brandywine\n- San Marzano original\n- Cherokee Purple\n\nOfrezco intercambio por semillas de variedades locales colombianas que he venido preservando, o compra directa.\n\nTambién tengo experiencia en cultivo hidropónico de tomates y puedo ofrecer asesoría como parte del intercambio.'
                }
            ],
            'Ayuda y Soporte': [
                {
                    'titulo': 'Problema con pH inestable en sistema NFT',
                    'contenido': 'Estoy teniendo problemas con fluctuaciones de pH en mi sistema NFT. Comienza en 5.8 por la mañana pero para el final del día sube hasta 7.2, lo que está afectando mis plantas de fresa.\n\nDetalles del sistema:\n- 24 plantas de fresa\n- Depósito de 50 litros\n- Solución nutritiva comercial para frutos\n- Temperatura ambiente: 18-25°C\n\n¿Alguien ha experimentado algo similar? ¿Qué podría estar causando estas fluctuaciones y cómo puedo estabilizar el pH?'
                },
                {
                    'titulo': 'Guía para principiantes: ¿Por dónde empezar?',
                    'contenido': 'Hola a todos, soy nuevo en el mundo de la hidroponía y me siento un poco abrumado con tanta información. Tengo un pequeño balcón de 2x3 metros y me gustaría comenzar a cultivar algunas hierbas y tal vez lechugas.\n\n¿Podrían recomendarme un sistema sencillo para principiantes? ¿Qué cultivos son más fáciles para empezar? ¿Existe alguna guía paso a paso que pueda seguir?\n\nMi presupuesto es limitado (aproximadamente $200.000 COP), así que idealmente busco algo que pueda construir yo mismo. Agradezco cualquier consejo para no cometer errores comunes de principiante.'
                }
            ]
        }
        
        # Crear temas para cada foro
        for nombre_foro, temas in temas_por_foro.items():
            try:
                # Buscar el foro por nombre
                foro = Forum.objects.get(name=nombre_foro)
                self.stdout.write(self.style.SUCCESS(f'Creando temas para el foro: {nombre_foro}'))
                
                # Crear temas para este foro
                for tema in temas:
                    # Verificar si ya existe un tema con este título en este foro
                    if Topic.objects.filter(subject=tema['titulo'], forum=foro).exists():
                        self.stdout.write(self.style.WARNING(f'El tema "{tema["titulo"]}" ya existe en este foro. Omitiendo...'))
                        continue
                    
                    # Crear el tema
                    nuevo_tema = Topic.objects.create(
                        forum=foro,
                        subject=tema['titulo'],
                        poster=admin_user,
                        status=Topic.TOPIC_UNLOCKED,
                        type=Topic.TOPIC_POST,
                        approved=True
                    )
                    
                    # Crear el primer post del tema
                    primer_post = Post.objects.create(
                        topic=nuevo_tema,
                        poster=admin_user,
                        content=tema['contenido'],
                        approved=True
                    )
                    
                    # Actualizar el tema con el primer post
                    nuevo_tema.first_post = primer_post
                    nuevo_tema.last_post = primer_post
                    nuevo_tema.last_post_on = timezone.now()
                    nuevo_tema.save()
                    
                    self.stdout.write(self.style.SUCCESS(f'Tema creado: {tema["titulo"]}'))
            
            except Forum.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'No se encontró el foro: {nombre_foro}'))
                continue
        
        self.stdout.write(self.style.SUCCESS('Temas iniciales creados exitosamente')) 