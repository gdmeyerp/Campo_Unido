#!/bin/bash
# Script de construcción para Render

set -e  # Detener ejecución si hay algún error

# Instalar dependencias
echo "===== Instalando dependencias ====="
pip install --upgrade pip
pip install -r requirements.txt

# Configurar la base de datos
echo "===== Configurando la base de datos ====="
python manage.py migrate

# Recolectar archivos estáticos
echo "===== Recolectando archivos estáticos ====="
python manage.py collectstatic --no-input

# Crear superusuario (solo si no existe)
echo "===== Configurando superusuario ====="
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'campo_unido_2024');
    print('Superusuario creado con éxito.');
else:
    print('El superusuario ya existe.')
"

# Verificar archivos estáticos y directorios
echo "===== Verificando directorios ====="
if [ ! -d "staticfiles" ]; then
    mkdir -p staticfiles
    echo "Directorio 'staticfiles' creado."
fi

if [ ! -d "media" ]; then
    mkdir -p media
    echo "Directorio 'media' creado."
fi

# Verificar permisos
chmod -R 755 staticfiles
chmod -R 755 media

echo "===== Construcción completada con éxito ====="
echo "Información del entorno:"
echo "Python: $(python --version)"
echo "Django: $(python -c 'import django; print(django.__version__)')"
echo "Directorio actual: $(pwd)"
echo "Archivos estáticos: $(ls -la staticfiles | wc -l) archivos" 