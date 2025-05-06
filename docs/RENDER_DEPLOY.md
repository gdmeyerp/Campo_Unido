# Despliegue en Render

Este documento contiene las instrucciones para desplegar Campo Unido en Render.com.

## Pasos para el despliegue

1. Crea una cuenta en [Render](https://render.com)

2. Ve a tu dashboard de Render y haz clic en "New" y selecciona "Web Service"

3. Conecta tu repositorio de GitHub o GitLab donde has subido este proyecto

4. Configura el servicio web:
   - **Name**: campo-unido (o el nombre que prefieras)
   - **Region**: Elige la más cercana a tus usuarios
   - **Branch**: main (o la rama que uses para producción)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

5. En la sección "Environment", añade las siguientes variables de entorno:
   - `DJANGO_SETTINGS_MODULE` = `config.settings.production`
   - `SECRET_KEY` = (genera una clave secreta segura o deja que Render la genere)
   - `PYTHON_VERSION` = `3.10.5`

6. Haz clic en "Create Web Service"

## Supervisión y mantenimiento

Una vez desplegado:

1. Puedes acceder a los logs desde el dashboard de Render
2. Si necesitas ejecutar comandos de Django (como migraciones), puedes usar el shell de Render
3. Los archivos estáticos se sirven automáticamente con whitenoise

## Solución de problemas

Si encuentras errores durante el despliegue:

1. Revisa los logs en la sección "Logs" del panel de Render
2. Asegúrate de que todas las dependencias estén correctamente listadas en requirements.txt
3. Si tienes problemas con importaciones, puede ser necesario deshabilitar temporalmente algunas apps en config/urls.py

## Actualización del sitio

Para actualizar tu aplicación después de hacer cambios:

1. Haz push a tu repositorio
2. Render automáticamente desplegará los cambios

Render también soporta despliegues manuales desde el dashboard. 