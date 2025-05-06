#!/bin/bash
# Script para desplegar automáticamente el proyecto Campo Unido en PythonAnywhere
# Ejecutar este script desde la consola Bash de PythonAnywhere después de subir tu código

# Configuración - Edita estas variables
USERNAME=$(whoami)  # Se obtiene automáticamente del sistema
PROJECT_NAME="campo_unido"
VENV_NAME="campo_unido_venv"
PYTHON_VERSION="3.10"
DOMAIN="$USERNAME.pythonanywhere.com"

# Colores para mejor legibilidad
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Iniciando despliegue de $PROJECT_NAME en PythonAnywhere ===${NC}"

# 1. Crear y activar el entorno virtual
echo -e "${GREEN}Creando entorno virtual...${NC}"
mkvirtualenv --python=/usr/bin/python$PYTHON_VERSION $VENV_NAME || {
    echo -e "${RED}Error al crear entorno virtual. ¿Ya existe?${NC}"
    echo -e "${GREEN}Intentando activar entorno existente...${NC}"
}

# Activar entorno virtual
echo -e "${GREEN}Activando entorno virtual...${NC}"
source "$HOME/.virtualenvs/$VENV_NAME/bin/activate" || {
    echo -e "${RED}Error al activar entorno virtual.${NC}"
    exit 1
}

# 2. Instalar dependencias
echo -e "${GREEN}Instalando dependencias...${NC}"
cd "$HOME/$PROJECT_NAME" || {
    echo -e "${RED}Error: No se encontró el directorio del proyecto.${NC}"
    echo -e "${RED}Asegúrate de que el código esté en ~/$PROJECT_NAME${NC}"
    exit 1
}

pip install -r requirements.txt

# 3. Configurar ALLOWED_HOSTS en production.py
echo -e "${GREEN}Configurando allowed hosts...${NC}"
SETTINGS_FILE="config/settings/production.py"

if [ -f "$SETTINGS_FILE" ]; then
    # Buscar la línea que contiene ALLOWED_HOSTS y reemplazarla
    sed -i "s/ALLOWED_HOSTS = .*/ALLOWED_HOSTS = ['$DOMAIN']/g" $SETTINGS_FILE
    echo -e "${GREEN}Allowed hosts configurado a: '$DOMAIN'${NC}"
    
    # Verificar si queremos usar SQLite en producción
    echo -e "${GREEN}¿Deseas usar SQLite en producción? (Recomendado para sitios pequeños o cuenta gratuita) (s/n)${NC}"
    read -r use_sqlite
    if [[ "$use_sqlite" =~ ^[Ss]$ ]]; then
        echo -e "${GREEN}Configurando SQLite en producción...${NC}"
        # Reemplazar la configuración de base de datos en production.py
        # Primero, hacemos una copia de seguridad
        cp $SETTINGS_FILE ${SETTINGS_FILE}.bak
        
        # Buscamos la sección DATABASES y la reemplazamos
        awk '
        BEGIN { printing = 1; found = 0; }
        /DATABASES = {/ { 
            printing = 0; 
            found = 1;
            print "DATABASES = {";
            print "    '\''default'\'': {";
            print "        '\''ENGINE'\'': '\''django.db.backends.sqlite3'\'',";
            print "        '\''NAME'\'': BASE_DIR / '\''db.sqlite3'\'',";
            print "    }";
            print "}";
        }
        /^}$/ { 
            if (found == 1) { 
                printing = 1; 
                found = 0; 
            } 
        }
        { if (printing) print; }
        ' ${SETTINGS_FILE}.bak > $SETTINGS_FILE
        
        echo -e "${GREEN}SQLite configurado en producción. Se ha guardado copia de seguridad en ${SETTINGS_FILE}.bak${NC}"
    else
        echo -e "${GREEN}Se usará PostgreSQL en producción. Asegúrate de configurar las variables de entorno adecuadas.${NC}"
    fi
else
    echo -e "${RED}Error: No se encontró el archivo $SETTINGS_FILE${NC}"
fi

# 4. Generar una clave secreta si no existe
if ! grep -q "DJANGO_SECRET_KEY" ~/.bashrc; then
    echo -e "${GREEN}Generando SECRET_KEY...${NC}"
    # Generar clave secreta
    SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
    echo "export DJANGO_SECRET_KEY='$SECRET_KEY'" >> ~/.bashrc
    export DJANGO_SECRET_KEY="$SECRET_KEY"
    echo -e "${GREEN}SECRET_KEY generada y guardada en .bashrc${NC}"
else
    echo -e "${GREEN}SECRET_KEY ya existe en .bashrc${NC}"
fi

# 5. Corregir warning de guardian
echo -e "${GREEN}Corrigiendo advertencia de Guardian...${NC}"
SETTINGS_BASE_FILE="config/settings/base.py"
if [ -f "$SETTINGS_BASE_FILE" ]; then
    # Verificar si ya tiene la configuración correcta
    if ! grep -q "django.contrib.auth.backends.ModelBackend" "$SETTINGS_BASE_FILE" || ! grep -q "guardian.backends.ObjectPermissionBackend" "$SETTINGS_BASE_FILE"; then
        echo -e "${GREEN}Añadiendo backends de autenticación correctos para Guardian...${NC}"
        # Reemplazar la sección AUTHENTICATION_BACKENDS
        sed -i "s/AUTHENTICATION_BACKENDS = (.*)/AUTHENTICATION_BACKENDS = (\n    'django.contrib.auth.backends.ModelBackend',\n    'guardian.backends.ObjectPermissionBackend',\n)/g" $SETTINGS_BASE_FILE
    else
        echo -e "${GREEN}Configuración de Guardian parece estar correcta.${NC}"
    fi
else
    echo -e "${RED}Error: No se encontró el archivo $SETTINGS_BASE_FILE${NC}"
fi

# 6. Migrar la base de datos
echo -e "${GREEN}Migrando base de datos...${NC}"
# Crear directorio de media si no existe
mkdir -p media
mkdir -p staticfiles
python manage.py migrate

# 7. Recolectar archivos estáticos
echo -e "${GREEN}Recolectando archivos estáticos...${NC}"
python manage.py collectstatic --noinput

# 8. Ofrecer crear superusuario
echo -e "${GREEN}¿Deseas crear un superusuario? (s/n)${NC}"
read -r create_superuser
if [[ "$create_superuser" =~ ^[Ss]$ ]]; then
    python manage.py createsuperuser
fi

# 9. Dar instrucciones para configurar la web app
echo -e "${BLUE}=== Configuración completada ===${NC}"
echo -e "${GREEN}Para completar el despliegue:${NC}"
echo -e "1. Ve a la pestaña 'Web' en PythonAnywhere"
echo -e "2. Haz clic en 'Add a new web app'"
echo -e "3. Selecciona 'Manual configuration' y Python $PYTHON_VERSION"
echo -e "4. Configura el virtualenv: $HOME/.virtualenvs/$VENV_NAME"
echo -e "5. Edita el archivo WSGI para que apunte a tu proyecto:"
echo -e "   - Ruta del proyecto: $HOME/$PROJECT_NAME"
echo -e "   - Módulo de settings: config.settings.production"
echo -e "6. Configura archivos estáticos:"
echo -e "   - URL: /static/ -> Directorio: $HOME/$PROJECT_NAME/staticfiles"
echo -e "   - URL: /media/ -> Directorio: $HOME/$PROJECT_NAME/media"
echo -e "7. Haz clic en el botón 'Reload'"
echo -e "${BLUE}¡Despliegue completado!${NC}" 