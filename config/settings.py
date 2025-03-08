# Añadir 'apps.social_feed' a INSTALLED_APPS si no está ya
if 'apps.social_feed' not in INSTALLED_APPS:
    INSTALLED_APPS.append('apps.social_feed') 