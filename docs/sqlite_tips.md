# Consejos para Usar SQLite en PythonAnywhere

Si has decidido usar SQLite para tu despliegue en PythonAnywhere (especialmente en el plan gratuito), aquí hay algunos consejos importantes para optimizar su rendimiento y evitar problemas.

## Ventajas de SQLite en PythonAnywhere

- **Plan Gratuito Compatible**: No requiere servicios de base de datos adicionales.
- **Facilidad de Uso**: No necesitas configurar credenciales ni servicios adicionales.
- **Portabilidad**: Puedes transferir tu base de datos desde desarrollo con un simple archivo.

## Consideraciones Importantes

### 1. Ubicación del Archivo

El archivo de base de datos debe estar en una ubicación donde tu aplicación pueda acceder y modificar:

```
/home/tuusuario/campo_unido/db.sqlite3
```

### 2. Permisos

Asegúrate de que el archivo tenga los permisos correctos:

```bash
chmod 664 db.sqlite3
```

### 3. Concurrencia

SQLite tiene limitaciones de concurrencia. Si esperas tráfico alto, considera:

- Configurar un tiempo de timeout más alto:
```python
# En production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 30,  # 30 segundos
        }
    }
}
```

- Usar el modo WAL (Write-Ahead Logging) para mejor concurrencia:
```python
from django.db.backends.sqlite3.base import DatabaseWrapper
DatabaseWrapper.settings_dict['OPTIONS']['isolation_level'] = None
```

### 4. Respaldos

SQLite es un único archivo, así que los respaldos son simples pero críticos:

```bash
# Crear un respaldo
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)

# Comprimir el respaldo
gzip db.sqlite3.backup_20250426_120000
```

Configura un script de respaldo periódico usando el programador de tareas de PythonAnywhere.

### 5. Optimización

Para mantener buen rendimiento:

- **Índices**: Asegúrate de tener índices adecuados en los campos frecuentemente usados para búsquedas.

- **Vacuum**: Compacta la base de datos periódicamente:
```python
from django.db import connection
cursor = connection.cursor()
cursor.execute('VACUUM;')
```

- **Limita el número de consultas** por vista. Usa el Debug Toolbar en desarrollo para identificar problemas.

### 6. Migración desde Desarrollo

Para transferir tu base de datos local a PythonAnywhere:

1. Sube el archivo `db.sqlite3` directamente.

2. Alternativamente, usa dumpdata/loaddata:
```bash
# En local
python manage.py dumpdata > data.json

# En PythonAnywhere
python manage.py loaddata data.json
```

### 7. Señales de Advertencia

Es momento de considerar migrar a PostgreSQL cuando notes:

- Tiempos de respuesta lentos
- Errores de "database is locked"
- Crecimiento significativo de datos (>100MB)
- Número creciente de usuarios concurrentes

### Configuración de WSGI para SQLite

Asegúrate de que tu configuración WSGI especifique correctamente la ruta de la base de datos:

```python
import os
import sys

path = '/home/tuusuario/campo_unido'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'

# Si tienes variables de entorno específicas
# os.environ['SQLITE_TIMEOUT'] = '30'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## Conclusión

SQLite es perfectamente adecuado para sitios de tráfico bajo a medio, especialmente en el plan gratuito de PythonAnywhere. Con las configuraciones y precauciones correctas, puede ofrecer un rendimiento satisfactorio para tu aplicación Campo Unido. 