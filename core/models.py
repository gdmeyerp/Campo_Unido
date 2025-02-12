from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    account_locked = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_perfil = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    descripcion = models.TextField(blank=True)
    intereses = models.TextField(blank=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'Perfil de {self.user.email}'

class RolUsuario(models.Model):
    nombre_rol = models.CharField(max_length=50)
    descripcion_rol = models.TextField()

    def __str__(self):
        return self.nombre_rol

class UsuarioRol(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(RolUsuario, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

class Permiso(models.Model):
    nombre_permiso = models.CharField(max_length=50)
    descripcion_permiso = models.TextField()

class RolPermiso(models.Model):
    rol = models.ForeignKey(RolUsuario, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)
