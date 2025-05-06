# Campo Unido

Plataforma integral para la gestión y conexión de campos agrícolas desarrollada por GA10-220501097.

## Descripción del Proyecto

Campo Unido es una solución tecnológica avanzada diseñada para optimizar la gestión agrícola mediante el uso de tecnologías de información. La plataforma conecta a agricultores con herramientas digitales para monitoreo de cultivos, comercialización directa de productos, gestión logística y soporte técnico especializado.

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

## Requisitos mínimos para la instalación

### Requisitos de Hardware
- **Procesador**: Intel Core i3 (8ª generación) o AMD Ryzen 3 o superior
- **RAM**: 4 GB mínimo (8 GB recomendado para entornos de producción)
- **Almacenamiento**: 10 GB de espacio libre en SSD (preferible para mejor rendimiento)
- **Pantalla**: Resolución mínima de 1366x768 para interfaz administrativa
- **Conectividad**: Conexión a Internet de banda ancha (10 Mbps mínimo)

### Requisitos de Software
- **Sistema Operativo**: 
  - Windows 10/11 (64 bits)
  - macOS 11.0 (Big Sur) o superior
  - Ubuntu 20.04 LTS, Debian 11 o distribuciones equivalentes
- **Entorno de Ejecución**: Python 3.8 o superior
- **Base de datos**: 
  - SQLite 3.34+ (desarrollo local)
  - PostgreSQL 13+ (entorno de producción)
- **Navegadores compatibles**: Ver sección "Características de los navegadores"
- **Software adicional**: Git 2.30+, Node.js 14+ (para algunas funcionalidades frontend)

## Paso a paso de la instalación

1. **Preparación del entorno**:
   - Asegúrese de tener instalados Git y Python según los requisitos.
   - Para Windows, se recomienda instalar [Git for Windows](https://gitforwindows.org/) y [Python](https://www.python.org/downloads/windows/).

2. **Clonar el repositorio desde GitHub**:
```bash
git clone https://github.com/GA10-220501097/Campo_Unido.git
cd Campo_Unido
```

3. **Crear y activar un entorno virtual**:
- Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
- Windows (CMD):
```cmd
python -m venv venv
.\venv\Scripts\activate.bat
```
- Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

4. **Instalar dependencias**:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

5. **Configurar variables de entorno** (opcional):
   - Cree un archivo `.env` en la raíz del proyecto con las siguientes variables:
   ```
   DEBUG=True
   SECRET_KEY=your_secret_key_here
   DATABASE_URL=sqlite:///db.sqlite3
   ```

6. **Configurar la base de datos**:
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Crear un superusuario (administrador)**:
```bash
python manage.py createsuperuser
```

8. **Cargar datos iniciales** (opcional):
```bash
python manage.py loaddata initial_data.json
```

9. **Recolectar archivos estáticos**:
```bash
python manage.py collectstatic
```

10. **Ejecutar el servidor de desarrollo**:
```bash
python manage.py runserver
```

11. **Acceder a la aplicación en el navegador**:
```
http://localhost:8000
```

12. **Acceder al panel de administración**:
```
http://localhost:8000/admin
```

## Planeación de implantación

Para implantar Campo Unido en un entorno de producción, considere las siguientes recomendaciones:

1. **Servidor Recomendado**:
   - CPU: 2+ núcleos, 2.0+ GHz
   - RAM: 4+ GB
   - Almacenamiento: 20+ GB SSD
   - Sistema Operativo: Ubuntu Server 20.04 LTS

2. **Servicios de Despliegue**:
   - Gunicorn o uWSGI como servidor WSGI
   - Nginx como servidor proxy
   - Base de datos PostgreSQL en servidor dedicado
   - Redis para caché y colas

3. **Opciones de Implantación en la Nube**:
   - AWS Elastic Beanstalk
   - Google App Engine
   - DigitalOcean App Platform
   - Heroku

## Protocolo de transmisión de datos

Campo Unido implementa los siguientes protocolos para garantizar la seguridad y eficiencia en la transmisión de datos:

- **HTTPS/TLS 1.3**: Para todas las comunicaciones entre cliente y servidor
- **WebSockets (WSS)**: Comunicación bidireccional en tiempo real para módulos de monitoreo
- **REST API**: Interfaz de programación para integraciones externas
- **JWT (JSON Web Tokens)**: Autenticación segura para API
- **CORS (Cross-Origin Resource Sharing)**: Configurado para permitir solo dominios autorizados

### Seguridad de Datos
- Cifrado AES-256 para datos sensibles almacenados
- Hashing de contraseñas con algoritmo PBKDF2
- Protección contra ataques CSRF, XSS y SQL Injection
- Auditoría de acceso y registro de actividades críticas

## Características de los navegadores

La plataforma ha sido probada y optimizada para funcionar correctamente en los siguientes navegadores:

| Navegador | Versión mínima | Recomendada | Observaciones |
|-----------|----------------|-------------|---------------|
| Google Chrome | 88+ | 105+ | Experiencia óptima, todas las funcionalidades disponibles |
| Mozilla Firefox | 85+ | 102+ | Compatible con todas las funciones principales |
| Microsoft Edge | 88+ | 105+ | Basado en Chromium, rendimiento similar a Chrome |
| Safari | 14+ | 15.4+ | Algunas animaciones pueden variar |
| Opera | 74+ | 90+ | Compatible con todas las funcionalidades |

**Nota**: La interfaz es responsive y se adapta a dispositivos móviles con los siguientes navegadores:
- Chrome para Android 105+
- Safari para iOS 15+

## Tipo de licencia

**© 2024 GA10-220501097. Todos los derechos reservados.**

Este software es propiedad intelectual de su autor y está protegido por la siguiente licencia personalizada:

### Licencia de Uso Propietario - Campo Unido

1. **Prohibición de Distribución**: Este software no puede ser distribuido, compartido, copiado o transferido sin autorización expresa y escrita del propietario del copyright.

2. **Prohibición de Modificación**: No se permite modificar, adaptar, transformar o crear obras derivadas basadas en este software o cualquier parte del mismo.

3. **Uso Limitado**: El uso de este software está limitado exclusivamente a fines académicos, de evaluación o bajo términos específicos acordados con el propietario del copyright.

4. **Sin Concesión de Derechos de Propiedad Intelectual**: Esta licencia no otorga derechos de propiedad intelectual sobre el software o cualquier componente del mismo.

5. **Ingeniería Inversa**: Queda estrictamente prohibida la ingeniería inversa, descompilación o desmontaje del software.

6. **Garantía y Responsabilidad**: El software se proporciona "tal cual", sin garantía de ningún tipo. El propietario del copyright no será responsable por daños derivados del uso del software.

7. **Terminación**: Cualquier incumplimiento de los términos de esta licencia resultará en la terminación automática de los derechos otorgados.

Para solicitar permisos adicionales o licencias comerciales, contacte a:
german_meyer@soy.sena.edu.co

**Aviso Legal**: El uso no autorizado de este software puede resultar en acciones legales por infracción de derechos de autor.
