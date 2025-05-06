# Lista de Verificación para Despliegue en PythonAnywhere

## Antes de Desplegar
- [ ] Código actualizado y funcionando localmente
- [ ] Base de datos migrada y con datos básicos configurados
- [ ] Se han resuelto errores y warnings críticos
- [ ] Se ha actualizado `requirements.txt` con todas las dependencias
- [ ] Configurado `config/wsgi.py` para producción

## Preparación de Archivos
- [ ] Comprimir el proyecto en un archivo ZIP (o preparar repositorio Git)
- [ ] Asegurarse de que los siguientes archivos están incluidos:
  - [ ] `requirements.txt`
  - [ ] `pythonanywhere_deploy.sh`
  - [ ] `example_wsgi_pythonanywhere.py`
  - [ ] `pythonAnywhere_setup.md`
  - [ ] `db.sqlite3` (si vas a transferir la base de datos)

## SQLite vs PostgreSQL
- [ ] Decidir qué base de datos usar en producción:
  - SQLite (gratis): Más simple, bueno para proyectos pequeños o personales
  - PostgreSQL (pago): Más escalable, mejor para aplicaciones en producción

## Plan de PythonAnywhere
- [ ] Revisar plan de PythonAnywhere:
  - Plan Gratuito: 
    - Dominio: `tuusuario.pythonanywhere.com`
    - Limitado a 512MB de CPU
    - 512MB de RAM
  - Planes de pago: Mejores recursos, dominio personalizado

## Pasos de Despliegue
1. [ ] Subir código a PythonAnywhere
2. [ ] Configurar entorno virtual
3. [ ] Instalar dependencias
4. [ ] Configurar producción
5. [ ] Migrar base de datos
6. [ ] Configurar web app
7. [ ] Comprobar funcionamiento

## Detección de Problemas
- [ ] Revisar logs de acceso en caso de error
- [ ] Revisar logs de error
- [ ] Verificar archivos estáticos
- [ ] Comprobar permisos de la base de datos
- [ ] Verificar configuración WSGI

## Post-Despliegue
- [ ] Probar funcionalidades críticas:
  - [ ] Registro/Login de usuarios
  - [ ] Funcionalidades del Social Feed
  - [ ] Foro (machina)
  - [ ] Todas las apps críticas
- [ ] Verificar apariencia visual (CSS, imágenes, etc.)
- [ ] Probar carga de archivos multimedia 