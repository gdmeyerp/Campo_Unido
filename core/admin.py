from django.contrib import admin
from .models import User, PerfilUsuario, RolUsuario, UsuarioRol, Permiso, RolPermiso

admin.site.register(User)
admin.site.register(PerfilUsuario)
admin.site.register(RolUsuario)
admin.site.register(UsuarioRol)
admin.site.register(Permiso)
admin.site.register(RolPermiso)
