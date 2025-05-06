from django.apps import AppConfig


class UbicacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ubicaciones'
    verbose_name = 'Ubicaciones'

    def ready(self):
        import apps.ubicaciones.signals  # noqa 