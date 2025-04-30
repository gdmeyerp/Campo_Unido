from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class EmailBackend(ModelBackend):
    """
    Backend de autenticación que permite iniciar sesión con email
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # En Django, el parámetro se llama 'username' por convención,
        # pero en nuestro caso lo tratamos como email
        UserModel = get_user_model()
        email = username  # El campo username contiene el email
        
        try:
            # Buscar al usuario por email
            user = UserModel.objects.get(email=email)
            
            # Verificar la contraseña
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            # Si el usuario no existe, continuar con el siguiente backend
            return None
            
        return None 