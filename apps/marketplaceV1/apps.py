from django.apps import AppConfig


class MarketplaceV1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.marketplaceV1'
    verbose_name = 'Marketplace V1'
    
    def ready(self):
        import apps.marketplaceV1.signals 