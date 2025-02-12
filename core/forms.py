from django import forms
from django.contrib.auth.forms import UserCreationForm
from core.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User  # Usamos el modelo de usuario personalizado
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')  # Campos que se solicitan en el formulario
