from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from guardian.utils import get_anonymous_user

class Command(BaseCommand):
    help = 'Crea el usuario anónimo necesario para django-guardian'

    def handle(self, *args, **options):
        User = get_user_model()
        
        try:
            anonymous_user = get_anonymous_user()
            self.stdout.write(self.style.SUCCESS(f'El usuario anónimo ya existe: {anonymous_user}'))
        except:
            # Crear el usuario anónimo si no existe
            User.objects.create_user(
                email='anonymous@example.com',
                first_name='Anonymous',
                last_name='User',
                password=None,
                is_active=False
            )
            self.stdout.write(self.style.SUCCESS('Usuario anónimo creado correctamente')) 