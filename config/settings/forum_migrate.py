"""
Settings for forum migrations only.
"""

from .temp_migrate import *  # noqa

# Add forum-related apps
INSTALLED_APPS += [
    'mptt',
    'haystack',
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
]

# Add forum middleware
MIDDLEWARE += [
    'machina.apps.forum_permission.middleware.ForumPermissionMiddleware',
]

# Add forum templates directory
from machina import MACHINA_MAIN_TEMPLATE_DIR
TEMPLATES[0]['DIRS'] += [MACHINA_MAIN_TEMPLATE_DIR]

# Add forum static directory
from machina import MACHINA_MAIN_STATIC_DIR
STATICFILES_DIRS += [MACHINA_MAIN_STATIC_DIR]

# Add forum context processor
TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'machina.core.context_processors.metadata',
]

# Forum cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'machina_attachments': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR / 'tmp',
    },
}

# Forum search configuration
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

# Forum settings
MACHINA_FORUM_NAME = 'Campo Unido Forum'
MACHINA_ATTACHMENT_CACHE_NAME = 'machina_attachments'