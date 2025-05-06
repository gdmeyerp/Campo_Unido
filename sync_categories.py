import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.inventario.views import sincronizar_categorias
from django.http import HttpRequest

def sync_categories():
    request = HttpRequest()
    request.user = User.objects.filter(is_staff=True).first()
    
    # El request necesita _messages para que funcione correctamente
    setattr(request, '_messages', [])
    
    # Sincronizar categorías
    result = sincronizar_categorias(request)
    print("Sincronización completada correctamente.")
    return result

if __name__ == "__main__":
    sync_categories() 