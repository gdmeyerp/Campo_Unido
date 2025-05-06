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
# Campo_Unido/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),  # URLs de la aplicación core
    path('accounts/', include('django.contrib.auth.urls')),  # URLs de autenticación
    path('login/', core_views.login_view, name='login'),  # URL directa para login
    path('register/', core_views.register, name='register'),  # URL directa para registro
    # Marketplace URLs habilitadas de nuevo con archivo limpio
    path('marketplace/', include('apps.marketplace.urls')),  # URLs del marketplace
    path('foro/', include('apps.foro_machina.urls')),  # URLs del foro
    path('social/', include('apps.social_feed.urls')),  # URLs del feed social
    path('inventario/', include('apps.inventario.urls')),  # URLs del inventario
    path('db_explorer/', include('apps.db_explorer.urls')),  # URLs del explorador de BD
    path('ubicaciones/', include('apps.ubicaciones.urls')),  # URLs de ubicaciones
    path('chat/', include('apps.chat_flotante.urls')),  # URLs del chat flotante
    # Las siguientes URLs están comentadas porque las aplicaciones aún no existen o no están completas
    # path('eventos/', include('apps.eventos.urls')),
    # path('control-remoto/', include('apps.control_remoto.urls')),
    # path('soporte/', include('apps.soporte.urls')),
    # path('suscripciones/', include('apps.suscripciones.urls')),
    # path('monitoreo/', include('apps.monitoreo.urls')),
]

# Configuración para servir archivos estáticos y de medios en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
