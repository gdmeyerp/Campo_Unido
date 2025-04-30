from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CustomUserCreationForm(forms.ModelForm):
    """
    Formulario para crear un nuevo usuario, con campos adicionales.
    Sobreescribe completamente UserCreationForm para evitar dependencias de 'username'.
    """
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
        required=True, 
        help_text=_('Requerido. Ingrese una dirección de email válida.')
    )
    first_name = forms.CharField(
        label=_("First name"),
        max_length=30, 
        required=False, 
        help_text=_('Opcional.')
    )
    last_name = forms.CharField(
        label=_("Last name"),
        max_length=30, 
        required=False, 
        help_text=_('Opcional.')
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_('La contraseña debe tener al menos 8 caracteres y no puede ser demasiado común.'),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_("Ingrese la misma contraseña que antes, para verificación."),
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Las contraseñas no coinciden."))
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
