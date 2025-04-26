# Resumen de Despliegue de Campo Unido en Render

Este documento resume los pasos finales para desplegar la aplicación en Render.

## Pasos para el despliegue

1. **Preparación local** (ya completada):
   - Se ha creado `render.yaml` con la configuración del servicio
   - Se ha añadido `gunicorn` y `whitenoise` a `requirements.txt`
   - Se ha configurado `production.py` para entorno de producción
   - Se ha corregido la advertencia de Guardian en `base.py`
   - Se ha optimizado `build.sh` para el proceso de construcción

2. **Crear repositorio en GitHub**:
   - Ejecuta `.\setup_git.ps1` para inicializar el repositorio
   - Crea un repositorio en GitHub sin README ni .gitignore
   - Vincula tu repositorio local al remoto:
     ```
     git remote add origin https://github.com/tu-usuario/campo-unido.git
     git branch -M main
     git push -u origin main
     ```

3. **Desplegar en Render**:
   - Ejecuta `.\deploy_to_render.ps1` para una experiencia guiada
   - Sigue los pasos que te indica el script
   - Alternativamente, puedes seguir las instrucciones en `README_RENDER.md` manualmente

## Credenciales iniciales

Una vez desplegado, podrás acceder con las siguientes credenciales de superusuario:
- **Usuario**: admin
- **Email**: admin@example.com
- **Contraseña**: campo_unido_2024

## Solución de problemas comunes

- **Error al desplegar**: Verifica los logs en el panel de Render
- **Errores con dependencias**: Asegúrate de que `requirements.txt` contiene todas las dependencias necesarias
- **Problemas con archivos estáticos**: Verifica que `whitenoise` está correctamente configurado

## Próximos pasos

1. Cambia la contraseña del superusuario inmediatamente después del despliegue
2. Configura variables de entorno adicionales según sea necesario
3. Configura un dominio personalizado si lo deseas
4. Configura copias de seguridad de la base de datos

---

Para implementaciones más avanzadas, considera usar PostgreSQL en lugar de SQLite añadiendo una base de datos en Render y configurando las variables de entorno correspondientes. 