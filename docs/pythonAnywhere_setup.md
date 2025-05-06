# Guía de Despliegue en PythonAnywhere para Campo Unido

Esta guía te proporcionará los pasos necesarios para desplegar tu aplicación Django "Campo Unido" en PythonAnywhere.

## 1. Crear una cuenta en PythonAnywhere

1. Regístrate en [PythonAnywhere](https://www.pythonanywhere.com)
2. Inicia sesión en tu cuenta

## 2. Subir el Código

### Opción A: Git (Recomendada)
```bash
# En la consola de PythonAnywhere
git clone <URL_DE_TU_REPOSITORIO> campo_unido
```

### Opción B: Subir archivos manualmente
1. Comprimir todo tu proyecto en un archivo .zip
2. Subir este archivo en la sección "Files" de PythonAnywhere
3. Descomprimir usando la consola:
```bash
unzip tu_proyecto.zip -d campo_unido
```

## 3. Configurar el Entorno Virtual

```bash
# Crear entorno virtual
mkvirtualenv --python=/usr/bin/python3.10 campo_unido_venv

# Activar el entorno virtual (si no está activado)
workon campo_unido_venv

# Instalar dependencias
cd campo_unido
pip install -r requirements.txt

# Instalar machina y otras dependencias que falten en el requirements.txt
pip install django-machina django-haystack django-crispy-forms crispy-bootstrap4 django-guardian django-mptt django-widget-tweaks
```

## 4. Configurar la Base de Datos

```bash
# Migrar la base de datos
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

## 5. Configurar los Archivos Estáticos

```bash
# Recolectar archivos estáticos
python manage.py collectstatic
```

## 6. Configurar la Web App en PythonAnywhere

1. Ir a la pestaña "Web" en PythonAnywhere
2. Hacer clic en "Add a new web app"
3. Elegir "Manual configuration"
4. Seleccionar Python 3.10
5. Configurar el Virtualenv:
   - Ruta: `/home/<tu_usuario>/.virtualenvs/campo_unido_venv`

## 7. Configurar WSGI

1. Hacer clic en el enlace WSGI (generalmente `/var/www/<tu_usuario>_pythonanywhere_com_wsgi.py`)
2. Borrar todo el contenido y reemplazarlo por:

```python
import os
import sys

# Ruta al directorio del proyecto
path = '/home/<tu_usuario>/campo_unido'
if path not in sys.path:
    sys.path.append(path)

# Configuración del módulo de settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'

# Reparar problema de WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 8. Crear un archivo de settings para producción

1. Verifica que el archivo `config/settings/production.py` contenga las configuraciones correctas
2. Configura ALLOWED_HOSTS para incluir tu dominio de PythonAnywhere:

```python
ALLOWED_HOSTS = ['<tu_usuario>.pythonanywhere.com']
```

3. Configura la SECRET_KEY para producción:
   - Ve a la pestaña "Consoles" en PythonAnywhere
   - Abre una consola Bash
   - Configura la variable de entorno (o crea un archivo .env):
```bash
export DJANGO_SECRET_KEY='tu_clave_secreta_segura'
```

## 9. Configurar URLs Estáticas en PythonAnywhere

1. Ve a la pestaña "Web"
2. En la sección "Static files" añade:
   - URL: `/static/`
   - Directorio: `/home/<tu_usuario>/campo_unido/staticfiles`
   
   - URL: `/media/`
   - Directorio: `/home/<tu_usuario>/campo_unido/media`

## 10. Actualizar el archivo config/wsgi.py

Es necesario actualizar el archivo WSGI de tu proyecto para que use la configuración de producción:

```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_wsgi_application()
```

## 11. Reiniciar la aplicación web

1. Ve a la pestaña "Web" en PythonAnywhere
2. Haz clic en el botón "Reload"

## 12. Solución de problemas comunes

### Archivos estáticos no se cargan
- Verifica que `STATIC_ROOT` esté configurado correctamente en settings
- Asegúrate de haber ejecutado `collectstatic`
- Verifica la configuración de archivos estáticos en PythonAnywhere

### Errores de importación
- Verifica que el virtualenv esté configurado correctamente
- Asegúrate de que todas las dependencias estén instaladas

### Errores 500
- Revisa los logs de error en la pestaña "Web" -> "Error log"
- Activa DEBUG temporalmente para obtener más información

### Problemas con la base de datos
- Asegúrate de haber ejecutado todas las migraciones
- Verifica las credenciales de la base de datos en settings/production.py

## Actualización Continua

Para actualizar tu aplicación después de cambios:

```bash
# En la consola de PythonAnywhere
cd ~/campo_unido
git pull  # Si usas git

# Actualizar dependencias si es necesario
workon campo_unido_venv
pip install -r requirements.txt

# Migraciones si cambiaste modelos
python manage.py migrate

# Actualizar archivos estáticos
python manage.py collectstatic --noinput

# Reiniciar la web app desde la interfaz web
```

¡Felicidades! Tu aplicación Campo Unido debería estar ahora funcionando en PythonAnywhere. 