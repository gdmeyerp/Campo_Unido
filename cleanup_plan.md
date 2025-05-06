# Plan de limpieza del proyecto Campo Unido

## Archivos que pueden ser eliminados

### Archivos de respaldo de base de datos
- `db.sqlite3.backup_20250303_000449`
- `db.sqlite3.backup_20250303_001326`
- `db.sqlite3.backup_20250303_001618`

### Archivos duplicados de despliegue en PythonAnywhere (ya que ahora se usa Render)
- `pythonanywhere_deploy.sh`
- `example_wsgi_pythonanywhere.py`
- `example_wsgi_pythonanywhere_sqlite.py`
- `pythonAnywhere_setup.md`
- `README_DEPLOYMENT.md` (específico para PythonAnywhere)

### Archivos temporales y de corrección
- `views_temp.py`
- `correcciones.py`
- `inventario_fix.py`
- `inventario_patch.txt`
- `add_usuario_nombre_fields.sql` (si ya fue aplicado)
- `models_db.txt` (archivo vacío)

### Documentación redundante o desactualizada
- `deploy_quick_start.md` (reemplazado por `README_RENDER.md`)
- `deploy_guardian_fix.md` (si el fix ya fue aplicado)

### Archivos de despliegue redundantes
- Si ya se completó el despliegue en Render, considerar eliminar:
  - `prepare_deployment_package.ps1`
  - `campo_unido_deploy.zip`

## Archivos a conservar
- `README.md`, `README_v3.0.md`, `README_RENDER.md` (documentación principal)
- `render.yaml` (configuración de Render)
- `build.sh` (script de construcción para Render)
- `requirements.txt` (dependencias)
- `db.sqlite3` (base de datos actual)
- `.gitignore`
- `deploy_to_render.ps1` (útil para futuros despliegues)
- `setup_git.ps1` (útil para configuración de Git)

## Recomendaciones de organización
1. Mover todos los archivos de documentación (*.md) a una carpeta `docs/`
2. Mover los scripts de despliegue (*.ps1, *.sh) a una carpeta `scripts/`
3. Mantener solo los archivos esenciales en la raíz del proyecto 