"""
URL configuration for Campo_Unido project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from machina import urls as machina_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),  # Incluye las URLs de la app core
    path('accounts/', include('django.contrib.auth.urls')),  # URLs de autenticación
    path('machina/', include((machina_urls, 'machina'), namespace='foro')),  # URLs de machina con namespace 'foro'
    path('foro/', include('apps.foro_machina.urls')),  # Incluye las URLs de la app foro_machina
    path('social/', include('apps.social_feed.urls')),
    path('inventario/', include('apps.inventario.urls')),  # Incluye las URLs de la app inventario
    path('db-explorer/', include('apps.db_explorer.urls')),  # Incluye las URLs del explorador de base de datos
]

# Configuración para servir archivos estáticos y de medios en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 