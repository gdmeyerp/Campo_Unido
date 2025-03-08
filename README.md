# Campo Unido

Plataforma integral para la gestión y conexión de campos agrícolas.

## Estructura del Proyecto

```
Campo_Unido/
│
├── apps/                    # Todas las aplicaciones Django
│   ├── core/               # Funcionalidad central y autenticación
│   ├── marketplace/        # Mercado de productos agrícolas
│   ├── logistica/         # Gestión de logística y transporte
│   ├── inventario/        # Control de inventario
│   ├── hidroponia/        # Gestión de sistemas hidropónicos
│   ├── foro/              # Foro de discusión
│   ├── eventos/           # Gestión de eventos
│   ├── control_remoto/    # Control remoto de sistemas
│   ├── soporte/          # Sistema de soporte y tickets
│   ├── suscripciones/    # Gestión de suscripciones
│   ├── ubicaciones/      # Gestión de ubicaciones
│   └── monitoreo/        # Sistema de monitoreo
│
├── config/                 # Configuración del proyecto
│   ├── settings/          # Configuraciones separadas por ambiente
│   │   ├── base.py       # Configuración base
│   │   ├── local.py      # Configuración de desarrollo
│   │   └── production.py # Configuración de producción
│   ├── urls.py           # URLs principales
│   ├── wsgi.py           # Configuración WSGI
│   └── asgi.py           # Configuración ASGI
│
├── static/                # Archivos estáticos
│   └── base/             # Archivos estáticos base
│
├── media/                 # Archivos subidos por usuarios
│   └── uploads/          # Carpeta de subidas
│
├── templates/             # Plantillas HTML
│   └── base/             # Plantillas base
│
├── docs/                  # Documentación
├── manage.py             # Script de administración de Django
├── requirements.txt      # Dependencias del proyecto
└── README.md            # Este archivo
```

## Configuración del Entorno de Desarrollo

1. Crear un entorno virtual:
```bash
python -m venv venv
```

2. Activar el entorno virtual:
- Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar la base de datos:
```bash
python manage.py migrate
```

5. Crear un superusuario:
```bash
python manage.py createsuperuser
```

6. Ejecutar el servidor de desarrollo:
```bash
python manage.py runserver
```

## Configuración de Producción

Para el entorno de producción, asegúrese de:

1. Configurar las variables de entorno necesarias (ver config/settings/production.py)
2. Usar un servidor web como Nginx
3. Configurar un servidor de aplicaciones como Gunicorn
4. Usar una base de datos PostgreSQL
5. Configurar SSL/TLS para HTTPS

## Contribuir

1. Crear una rama para la nueva funcionalidad
2. Realizar los cambios
3. Enviar un pull request

## Licencia

[Especificar la licencia del proyecto]