# Guía Rápida de Despliegue en PythonAnywhere

## Pasos Esenciales

1. **Preparar el Proyecto**
   - Verificar que tu proyecto funciona localmente
   - Asegurarte de tener todos los archivos de despliegue:
     - `requirements.txt`
     - `pythonanywhere_deploy.sh`
     - `example_wsgi_pythonanywhere.py`

2. **Comprimir el Proyecto**
   - Usar `zip -r campo_unido.zip .` (Linux/Mac)
   - O usar software de compresión (Windows)
   - Verificar que incluye el archivo db.sqlite3 si vas a usar la misma base de datos

3. **Subir a PythonAnywhere**
   - Crear cuenta en PythonAnywhere.com
   - Ir a la pestaña Files
   - Subir el zip y descomprimirlo:
     ```
     unzip campo_unido.zip -d campo_unido
     ```

4. **Despliegue Automático**
   ```bash
   cd ~
   chmod +x campo_unido/pythonanywhere_deploy.sh
   ./campo_unido/pythonanywhere_deploy.sh
   ```

5. **Configurar Web App**
   - Ir a la pestaña Web
   - Add a new web app → Manual configuration → Python 3.10
   - Virtualenv: `/home/tuusuario/.virtualenvs/campo_unido_venv`
   - Editar archivo WSGI
   - Configurar archivos estáticos:
     - `/static/` → `/home/tuusuario/campo_unido/staticfiles`
     - `/media/` → `/home/tuusuario/campo_unido/media`

6. **Reiniciar y Probar**
   - Hacer clic en "Reload"
   - Verificar tu sitio en tuusuario.pythonanywhere.com

## Solución de Problemas

- **Error 500**: Revisar Web → Error log
- **Archivos estáticos no se cargan**: Verificar carpeta staticfiles y configuración
- **Problema de bases de datos**: Verificar permisos en db.sqlite3
- **Guardian warning**: El script de despliegue debería corregirlo automáticamente 