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
    help = 'Crea temas de ejemplo para cada subcategoría del foro'

    def handle(self, *args, **options):
        try:
            admin_user = User.objects.get(email='gdmeyerpSuperUser@unal.edu.co')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('No se encontró el usuario administrador'))
            return

        # Temas para Hidroponía
        temas_hidroponia = {
            'Sistemas NFT': [
                {
                    'titulo': 'Guía básica para construir un sistema NFT',
                    'contenido': 'En esta guía aprenderemos los pasos básicos para construir un sistema NFT casero...'
                },
                {
                    'titulo': 'Cultivos ideales para NFT',
                    'contenido': 'Los mejores cultivos para sistemas NFT incluyen lechuga, albahaca, espinaca...'
                },
                {
                    'titulo': 'Solución de problemas comunes en NFT',
                    'contenido': 'Problemas frecuentes en sistemas NFT y cómo solucionarlos...'
                }
            ],
            'Sistemas DWC': [
                {
                    'titulo': 'Construcción de raíz flotante DWC',
                    'contenido': 'Guía paso a paso para construir tu sistema de raíz flotante...'
                },
                {
                    'titulo': 'Oxigenación en sistemas DWC',
                    'contenido': 'La importancia de la oxigenación y diferentes métodos para lograrla...'
                }
            ],
            'Aeroponia': [
                {
                    'titulo': 'Introducción a la Aeroponía',
                    'contenido': 'Conceptos básicos y ventajas de los sistemas aeropónicos...'
                },
                {
                    'titulo': 'Nebulizadores para Aeroponía',
                    'contenido': 'Tipos de nebulizadores y su mantenimiento...'
                }
            ],
            'Soluciones Nutritivas': [
                {
                    'titulo': 'Fórmulas básicas de nutrientes',
                    'contenido': 'Recetas básicas para preparar soluciones nutritivas...'
                },
                {
                    'titulo': 'Control de pH y EC',
                    'contenido': 'Guía para mantener el pH y EC óptimos...'
                },
                {
                    'titulo': 'Nutrientes orgánicos en hidroponía',
                    'contenido': 'Alternativas orgánicas para nutrición hidropónica...'
                }
            ],
            'Automatización': [
                {
                    'titulo': 'Control automático de pH',
                    'contenido': 'Sistemas de control automático de pH con Arduino...'
                },
                {
                    'titulo': 'Temporizadores y bombas',
                    'contenido': 'Configuración de ciclos de riego automáticos...'
                }
            ]
        }

        # Temas para Cultivos Tradicionales
        temas_tradicionales = {
            'Hortalizas': [
                {
                    'titulo': 'Calendario de siembra',
                    'contenido': 'Guía mensual para la siembra de hortalizas...'
                },
                {
                    'titulo': 'Rotación de cultivos',
                    'contenido': 'Importancia y planificación de la rotación...'
                }
            ],
            'Frutales': [
                {
                    'titulo': 'Poda de árboles frutales',
                    'contenido': 'Técnicas de poda para diferentes especies...'
                },
                {
                    'titulo': 'Injertos en cítricos',
                    'contenido': 'Guía paso a paso para injertar cítricos...'
                }
            ],
            'Cultivos Orgánicos': [
                {
                    'titulo': 'Compostaje casero',
                    'contenido': 'Cómo hacer compost de calidad en casa...'
                },
                {
                    'titulo': 'Control biológico de plagas',
                    'contenido': 'Métodos naturales para controlar plagas...'
                }
            ],
            'Control de Plagas': [
                {
                    'titulo': 'Identificación de plagas comunes',
                    'contenido': 'Guía visual de plagas frecuentes...'
                },
                {
                    'titulo': 'Preparados naturales repelentes',
                    'contenido': 'Recetas de insecticidas naturales...'
                }
            ]
        }

        # Temas para sección General
        temas_general = {
            'Presentaciones': [
                {
                    'titulo': '¡Nuevo proyecto hidropónico!',
                    'contenido': 'Hola a todos, quiero compartir mi nuevo proyecto...'
                },
                {
                    'titulo': 'Granja familiar en desarrollo',
                    'contenido': 'Presentando nuestra granja familiar...'
                }
            ],
            'Noticias y Eventos': [
                {
                    'titulo': 'Feria Agrícola 2024',
                    'contenido': 'Próxima feria agrícola en la región...'
                },
                {
                    'titulo': 'Nuevo curso de hidroponía',
                    'contenido': 'Anuncio de curso presencial de hidroponía...'
                }
            ],
            'Mercado': [
                {
                    'titulo': 'Vendo sistema NFT completo',
                    'contenido': 'Sistema NFT de 4 metros, incluye bomba...'
                },
                {
                    'titulo': 'Compro semillas orgánicas',
                    'contenido': 'Busco semillas certificadas orgánicas...'
                }
            ],
            'Ayuda y Soporte': [
                {
                    'titulo': 'Guía de uso del foro',
                    'contenido': 'Cómo publicar, responder y usar el foro...'
                },
                {
                    'titulo': 'Reglas de la comunidad',
                    'contenido': 'Normas básicas de convivencia en el foro...'
                }
            ]
        }

        # Función para crear temas en un foro
        def crear_temas_en_foro(nombre_foro, temas):
            try:
                foro = Forum.objects.get(name=nombre_foro)
                for tema in temas:
                    # Crear el tema
                    nuevo_tema = Topic.objects.create(
                        forum=foro,
                        subject=tema['titulo'],
                        poster=admin_user,
                        type=Topic.TOPIC_POST,
                        status=Topic.TOPIC_UNLOCKED
                    )
                    
                    # Crear el primer post del tema
                    Post.objects.create(
                        topic=nuevo_tema,
                        poster=admin_user,
                        content=tema['contenido'],
                        updated=timezone.now()
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f'Tema creado: {tema["titulo"]} en {nombre_foro}'))
            except Forum.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'No se encontró el foro: {nombre_foro}'))

        # Crear temas para cada categoría
        for foro, temas in temas_hidroponia.items():
            crear_temas_en_foro(foro, temas)

        for foro, temas in temas_tradicionales.items():
            crear_temas_en_foro(foro, temas)

        for foro, temas in temas_general.items():
            crear_temas_en_foro(foro, temas)

        self.stdout.write(self.style.SUCCESS('Temas de ejemplo creados exitosamente')) 