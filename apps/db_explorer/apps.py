from django.apps import AppConfig


class DbExplorerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.db_explorer'
    verbose_name = 'Explorador de Base de Datos'
    
    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista.
        """
        pass
