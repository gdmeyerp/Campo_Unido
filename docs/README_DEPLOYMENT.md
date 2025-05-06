# Guía de Despliegue de Campo Unido en PythonAnywhere

Este documento proporciona instrucciones detalladas para desplegar el proyecto Campo Unido en PythonAnywhere, una plataforma de hosting para aplicaciones Python/Django.

## Preparando el Proyecto para Producción

Antes de desplegar, asegúrate de que tu proyecto esté listo para producción:

1. El proyecto ya tiene la estructura de configuración adecuada con settings separados para desarrollo y producción.
2. El archivo `requirements.txt` ha sido actualizado con todas las dependencias requeridas.
3. Se actualizó `config/wsgi.py` para usar la configuración de producción.

## Opciones de Despliegue

Tienes tres opciones para desplegar el proyecto:

### Opción 1: Despliegue Automático (Recomendado)

1. Sube tu código a PythonAnywhere (vía Git o carga de archivos).
2. Sube el script `pythonanywhere_deploy.sh` a tu directorio principal.
3. Dale permisos de ejecución: `chmod +x pythonanywhere_deploy.sh`
4. Ejecuta el script: `./pythonanywhere_deploy.sh`
5. Sigue las instrucciones que te da el script para completar la configuración web.

### Opción 2: Despliegue Manual Siguiendo la Guía

Sigue las instrucciones detalladas en el archivo `pythonAnywhere_setup.md`.

### Opción 3: Despliegue Manual Paso a Paso

Si prefieres entender cada paso, aquí están todas las acciones necesarias:

#### 1. Configurar Entorno en PythonAnywhere

```bash
# Crear entorno virtual
mkvirtualenv --python=/usr/bin/python3.10 campo_unido_venv

# Clonar el repositorio (si usas Git)
git clone https://github.com/tu-usuario/campo-unido.git campo_unido

# O descomprime el archivo que subiste
# unzip tu-archivo.zip -d campo_unido

# Instalar dependencias
cd campo_unido
pip install -r requirements.txt
```

#### 2. Configurar Base de Datos

El proyecto está configurado para usar PostgreSQL en producción, pero también puedes usar SQLite:

Para PostgreSQL (servicio de pago en PythonAnywhere):
1. Crea una base de datos PostgreSQL desde la pestaña Databases.
2. Configura las variables de entorno o ajusta `production.py`:
   ```bash
   export DB_NAME="tuusuario$campo_unido"
   export DB_USER="tuusuario"
   export DB_PASSWORD="tu_contraseña"
   export DB_HOST="tuusuario.postgres.pythonanywhere-services.com"
   export DB_PORT="10432"  # Puerto estándar de PostgreSQL en PythonAnywhere
   ```

Para SQLite (gratuito, opción más simple):
1. Modifica `settings/production.py` para usar SQLite:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }
   ```

2. Ejecuta las migraciones:
   ```bash
   python manage.py migrate
   ```

#### 3. Archivos Estáticos y Media

```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Crear directorio de media si no existe
mkdir -p media
```

#### 4. Configurar Web App

1. Ve a la pestaña Web → Add a new web app → Manual configuration → Python 3.10
2. Configurar virtualenv: `/home/tuusuario/.virtualenvs/campo_unido_venv`
3. Editar el archivo WSGI (usa el contenido de `example_wsgi_pythonanywhere.py` como base)
4. Configura archivos estáticos:
   - URL: `/static/` → Directorio: `/home/tuusuario/campo_unido/staticfiles`
   - URL: `/media/` → Directorio: `/home/tuusuario/campo_unido/media`

## Características Específicas del Proyecto

Este proyecto tiene varias aplicaciones y características que requieren atención especial:

### Foro (django-machina)

El proyecto usa django-machina para el foro. Asegúrate de que los archivos estáticos de machina se recolecten correctamente con `collectstatic`.

### Imágenes y Archivos Multimedia

La aplicación `social_feed` permite subir imágenes y videos. Asegúrate de que el directorio `media` tenga permisos adecuados y de que esté configurado en la sección de archivos estáticos.

### Base de Datos

Si usas SQLite, puedes mantener la misma base de datos de desarrollo o empezar con una nueva. Si usas PostgreSQL, deberás migrar tus datos.

Para transferir datos entre bases de datos:
```bash
# En tu entorno de desarrollo
python manage.py dumpdata > database_dump.json

# Sube database_dump.json a PythonAnywhere
# Luego en PythonAnywhere:
python manage.py loaddata database_dump.json
```

## Solución de Problemas

### Error 500 (Internal Server Error)

1. Revisa los logs de error: Pestaña Web → Error log
2. Comprueba que todas las dependencias estén instaladas correctamente
3. Verifica que la configuración de ALLOWED_HOSTS incluya tu dominio

### Problemas con Archivos Estáticos

1. Verifica que `collectstatic` se ejecutó correctamente
2. Comprueba las rutas en la configuración de archivos estáticos
3. Asegúrate de que `STATIC_ROOT` y `MEDIA_ROOT` están configurados correctamente

### Problemas de Base de Datos

1. Verifica que todas las migraciones se ejecutaron correctamente
2. Comprueba las credenciales de la base de datos (para PostgreSQL)
3. Verifica los permisos del archivo de base de datos (para SQLite)

## Actualización del Sitio

Para actualizar el sitio después de hacer cambios:

```bash
# Si usas Git:
cd ~/campo_unido
git pull

# Actualizar dependencias (si es necesario)
pip install -r requirements.txt

# Aplicar migraciones (si hay cambios en los modelos)
python manage.py migrate

# Actualizar archivos estáticos
python manage.py collectstatic --noinput

# Reiniciar la aplicación web
# (Haz clic en el botón "Reload" en la pestaña Web)
```

## Recursos Adicionales

- [Documentación oficial de PythonAnywhere](https://help.pythonanywhere.com/)
- [Guía de Django en PythonAnywhere](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)
- [Documentación de django-machina](https://django-machina.readthedocs.io/) 