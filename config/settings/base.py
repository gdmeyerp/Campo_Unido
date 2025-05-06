"""
Base settings for Campo Unido project.
"""

import os
from pathlib import Path
from machina import MACHINA_MAIN_TEMPLATE_DIR, MACHINA_MAIN_STATIC_DIR

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Add the apps directory to the Python path
import sys
sys.path.append(str(BASE_DIR))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# Permitir localhost y 127.0.0.1 para desarrollo local
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Custom user model
AUTH_USER_MODEL = 'core.User'

# Authentication backends
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

PROJECT_APPS = [
    'apps.core.apps.CoreConfig',
    'apps.marketplace.apps.MarketplaceConfig',
    'apps.logistica.apps.LogisticaConfig',
    'apps.inventario.apps.InventarioConfig',
    'apps.hidroponia.apps.HidroponiaConfig',
    'apps.foro_machina.apps.ForoMachinaConfig',
    'apps.eventos.apps.EventosConfig',
    'apps.control_remoto.apps.ControlRemotoConfig',
    'apps.soporte.apps.SoporteConfig',
    'apps.suscripciones.apps.SuscripcionesConfig',
    'apps.monitoreo.apps.MonitoreoConfig',
    'apps.social_feed.apps.SocialFeedConfig',
    'apps.db_explorer.apps.DbExplorerConfig',
    'apps.ubicaciones.apps.UbicacionesConfig',
    'apps.chat_flotante.apps.ChatFlotanteConfig',
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + [
    'mptt',
    'haystack',
    'widget_tweaks',
    'guardian',
    'machina',
    'machina.apps.forum',
    'machina.apps.forum_conversation',
    'machina.apps.forum_conversation.forum_attachments',
    'machina.apps.forum_conversation.forum_polls',
    'machina.apps.forum_feeds',
    'machina.apps.forum_moderation',
    'machina.apps.forum_search',
    'machina.apps.forum_tracking',
    'machina.apps.forum_member',
    'machina.apps.forum_permission',
    'crispy_forms',
    'crispy_bootstrap4',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'machina.apps.forum_permission.middleware.ForumPermissionMiddleware',
    'apps.inventario.middleware.ProductoAccesoMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            MACHINA_MAIN_TEMPLATE_DIR,
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'machina.core.context_processors.metadata',
                'apps.chat_flotante.context_processors.chat_flotante_processor',
                # Desactivado temporalmente debido a problemas
                # 'apps.marketplace.context_processors.cart_processor',
                # 'apps.marketplace.context_processors.marketplace_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    MACHINA_MAIN_STATIC_DIR,
]

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

# Configuración de caché para adjuntos
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'machina_attachments': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'tmp'),
    },
}

# Configuración de machina
MACHINA_FORUM_NAME = 'Campo Unido Forum'
MACHINA_ATTACHMENT_CACHE_NAME = 'machina_attachments'
MACHINA_FORUM_ATTACHMENTS_UPLOAD_TO = 'forum_attachments'

# Configuración de django-guardian
GUARDIAN_RAISE_403 = True
ANONYMOUS_USER_NAME = 'anonymous@example.com'

# Configuración de crispy-forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap4'

# Se eliminó la configuración de Channels 