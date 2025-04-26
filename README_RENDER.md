# Despliegue de Campo Unido en Render

Este documento describe el proceso completo para desplegar la aplicación Campo Unido en Render.

## Contenido
1. [Preparación del entorno](#preparación-del-entorno)
2. [Configuración del repositorio Git](#configuración-del-repositorio-git)
3. [Despliegue en Render](#despliegue-en-render)
4. [Monitoreo y mantenimiento](#monitoreo-y-mantenimiento)
5. [Solución de problemas](#solución-de-problemas)

## Preparación del entorno

### Requisitos previos
- Git instalado en tu sistema local
- Cuenta en GitHub
- Cuenta en Render (puedes registrarte con tu cuenta de GitHub)

### Archivos clave para el despliegue
Los siguientes archivos son necesarios para el despliegue:

- **render.yaml**: Contiene la configuración del servicio para Render
- **requirements.txt**: Lista de dependencias Python
- **build.sh**: Script ejecutado durante la construcción del servicio
- **Procfile**: Especifica el comando para iniciar la aplicación
- **config/settings/production.py**: Configuración de Django para producción

## Configuración del repositorio Git

1. Inicializa Git en tu proyecto (si aún no está inicializado):
   ```
   git init
   ```

2. Crea un repositorio en GitHub:
   - Visita [https://github.com/new](https://github.com/new)
   - Nombra tu repositorio (por ejemplo, "campo-unido")
   - **NO** inicialices el repositorio con README, .gitignore o licencia
   - Crea el repositorio

3. Añade todos los archivos al staging:
   ```
   git add .
   ```

4. Crea el commit inicial:
   ```
   git commit -m "Configuración inicial para despliegue en Render"
   ```

5. Conecta tu repositorio local con GitHub:
   ```
   git remote add origin https://github.com/tu-usuario/campo-unido.git
   git branch -M main
   git push -u origin main
   ```

## Despliegue en Render

1. Inicia sesión en tu cuenta de [Render](https://dashboard.render.com/).

2. Haz clic en "New +" y selecciona "Web Service".

3. Conecta tu repositorio de GitHub.

4. Configura el servicio:
   - **Nombre**: campo-unido (o el nombre que prefieras)
   - **Región**: Selecciona la más cercana a tus usuarios
   - **Rama**: main
   - **Runtime**: Python
   - **Build Command**: ./build.sh
   - **Start Command**: gunicorn config.wsgi:application

5. En "Advanced" añade las siguientes variables de entorno:
   - **DJANGO_SETTINGS_MODULE**: config.settings.production
   - **DJANGO_SECRET_KEY**: (Usa una clave secreta generada aleatoriamente)
   - **PYTHON_VERSION**: 3.10

6. Haz clic en "Create Web Service".

7. Render comenzará a construir tu aplicación. Puedes seguir el progreso en los logs.

## Monitoreo y mantenimiento

### Logs y monitoreo
- Accede a los logs desde el dashboard de Render para diagnosticar problemas
- Configura alertas para monitorear el estado de tu aplicación

### Actualizaciones
Para actualizar tu aplicación:
1. Realiza cambios en tu código local
2. Haz commit y push a GitHub
3. Render detectará los cambios y volverá a desplegar automáticamente

## Solución de problemas

### Problemas comunes
- **Error 500**: Verifica los logs en Render para diagnosticar el problema
- **Problemas con las migraciones**: Puedes conectarte al shell de Render para ejecutar comandos manualmente
- **Errores de dependencias**: Asegúrate de que todas las dependencias están correctamente listadas en requirements.txt

### Comandos útiles
Para ejecutar comandos manualmente en el shell de Render:
1. Ve a tu servicio en el dashboard de Render
2. Haz clic en "Shell"
3. Ejecuta los comandos necesarios, por ejemplo:
   ```
   python manage.py migrate
   python manage.py createsuperuser
   ```

---

Para una implementación más rápida, utiliza el script `deploy_to_render.ps1` incluido en este proyecto, que te guiará por todo el proceso de despliegue. 