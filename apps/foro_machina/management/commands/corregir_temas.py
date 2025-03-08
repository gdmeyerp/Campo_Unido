from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from machina.core.db.models import get_model
from django.utils.timezone import now

User = get_user_model()
Forum = get_model('forum', 'Forum')
Topic = get_model('forum_conversation', 'Topic')
Post = get_model('forum_conversation', 'Post')

class Command(BaseCommand):
    help = 'Corrige los temas existentes y asegura que todos los temas tengan sus posts correctamente asociados'

    def handle(self, *args, **options):
        # Obtener usuario administrador
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                self.stdout.write(self.style.ERROR('No se encontró un usuario administrador. Por favor, crea uno primero.'))
                return
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('No se encontró un usuario administrador. Por favor, crea uno primero.'))
            return
        
        # 1. Verificar todos los temas
        self.stdout.write(self.style.NOTICE('Verificando todos los temas...'))
        
        temas = Topic.objects.all()
        self.stdout.write(self.style.SUCCESS(f'Se encontraron {temas.count()} temas para verificar'))
        
        for tema in temas:
            # Verificar si el tema tiene posts
            posts = Post.objects.filter(topic=tema).order_by('created')
            
            if posts.exists():
                primer_post = posts.first()
                ultimo_post = posts.last()
                
                # Verificar si el tema tiene first_post y last_post correctamente asignados
                if tema.first_post != primer_post or tema.last_post != ultimo_post:
                    tema.first_post = primer_post
                    tema.last_post = ultimo_post
                    tema.last_post_on = ultimo_post.created
                    tema.posts_count = posts.count()
                    tema.save()
                    self.stdout.write(self.style.SUCCESS(f'Tema "{tema.subject}" actualizado con los posts correctos'))
            else:
                # Si el tema no tiene posts, crear uno
                self.stdout.write(self.style.WARNING(f'Tema "{tema.subject}" no tiene posts. Creando uno...'))
                
                # Crear un post para el tema
                post = Post.objects.create(
                    topic=tema,
                    poster=admin_user,
                    subject=tema.subject,
                    content='Este post fue creado automáticamente para corregir un tema sin posts.',
                    created=now(),
                    updated=now()
                )
                
                # Actualizar el tema con el post creado
                tema.first_post = post
                tema.last_post = post
                tema.last_post_on = post.created
                tema.posts_count = 1
                tema.save()
                self.stdout.write(self.style.SUCCESS(f'Post creado para el tema "{tema.subject}"'))
        
        # 2. Verificar todos los posts
        self.stdout.write(self.style.NOTICE('Verificando todos los posts...'))
        
        posts = Post.objects.all()
        self.stdout.write(self.style.SUCCESS(f'Se encontraron {posts.count()} posts para verificar'))
        
        for post in posts:
            # Verificar si el post tiene un tema asociado
            if not post.topic:
                self.stdout.write(self.style.WARNING(f'Post "{post.subject}" no tiene un tema asociado. Eliminando...'))
                post.delete()
                continue
            
            # Verificar si el tema del post existe
            try:
                tema = Topic.objects.get(pk=post.topic.pk)
            except Topic.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'El tema del post "{post.subject}" no existe. Eliminando post...'))
                post.delete()
                continue
        
        self.stdout.write(self.style.SUCCESS('Corrección de temas completada exitosamente')) 