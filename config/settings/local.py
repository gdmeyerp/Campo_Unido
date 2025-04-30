"""
Local development settings for Campo Unido project.
"""

from .base import *  # noqa

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-development-key-change-this-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Aplicaciones adicionales para desarrollo
INSTALLED_APPS += [
    # 'apps.db_explorer.apps.DbExplorerConfig',  # Ya está registrada en base.py
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configuración de autenticación
AUTHENTICATION_BACKENDS = [
    'apps.core.backends.EmailBackend',  # Backend personalizado para email
    'django.contrib.auth.backends.ModelBackend',  # Backend predeterminado de Django
] 