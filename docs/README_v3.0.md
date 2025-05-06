# Campo Unido - Versión 3.0

Esta versión incluye las configuraciones necesarias para desplegar la aplicación en Render, una plataforma moderna de alojamiento en la nube.

## Novedades en esta versión

### Configuración para despliegue en Render
- Añadida configuración `render.yaml` para despliegue automático
- Creado script `build.sh` para el proceso de construcción
- Optimizado middleware y configuraciones para producción
- Añadido soporte para servir archivos estáticos con Whitenoise

### Mejoras técnicas
- Corregida la advertencia de Guardian en los backends de autenticación
- Optimizada la configuración de producción para un mejor rendimiento
- Añadido soporte de Gunicorn como servidor WSGI
- Configuración de logs mejorada para diagnóstico en producción

### Scripts de utilidad
- `deploy_to_render.ps1`: Script guiado para despliegue en Render
- `setup_git.ps1`: Configuración de Git para despliegue
- Documentación mejorada sobre el proceso de despliegue

## Instrucciones de despliegue

Para desplegar la aplicación en Render:

1. Ejecuta el script guiado:
   ```
   .\deploy_to_render.ps1
   ```

2. Sigue las instrucciones en pantalla para:
   - Crear un repositorio en GitHub
   - Vincular tu repositorio local al remoto
   - Configurar tu servicio en Render

3. Una vez completado, accede a tu aplicación en la URL proporcionada por Render.

## Documentación adicional

- `README_RENDER.md`: Guía detallada sobre el despliegue en Render
- `README_DEPLOY_SUMMARY.md`: Resumen de los pasos para el despliegue

## Credenciales de acceso inicial

Una vez desplegada la aplicación, podrás acceder con las siguientes credenciales:

- **Usuario**: admin
- **Email**: admin@example.com  
- **Contraseña**: campo_unido_2024

*Recuerda cambiar esta contraseña inmediatamente después del primer inicio de sesión por razones de seguridad.* 