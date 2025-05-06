# Resumen de limpieza del proyecto Campo Unido

## Acciones realizadas

1. **Organización de la estructura del proyecto**:
   - Creada carpeta `docs/` para toda la documentación
   - Creada carpeta `scripts/` para scripts de despliegue y configuración
   - Movidos los archivos correspondientes a sus carpetas

2. **Eliminación de archivos innecesarios**:
   - Eliminados backups antiguos de la base de datos
   - Eliminados archivos temporales y de corrección
   - Eliminados archivos específicos de PythonAnywhere (ya que ahora se usa Render)

3. **Actualización de rutas en archivos clave**:
   - Modificado `build.sh` para funcionar desde su nueva ubicación
   - Actualizado `render.yaml` para apuntar a la nueva ruta del script de compilación
   - Actualizado `README.md` para reflejar la nueva estructura de directorios

## Estado actual

El proyecto ahora tiene una estructura más limpia y organizada:

- **Raíz del proyecto**: Solo contiene los archivos esenciales
- **docs/**: Contiene toda la documentación
- **scripts/**: Contiene scripts de despliegue y configuración
- **apps/**: Contiene las aplicaciones Django (estructura original conservada)

## Beneficios de la limpieza

- **Mayor claridad**: Es más fácil entender la estructura del proyecto
- **Mejor mantenibilidad**: Los archivos relacionados están agrupados lógicamente
- **Reducción de confusión**: Eliminados archivos duplicados o obsoletos
- **Menor tamaño**: Eliminados archivos de backup innecesarios

## Recomendaciones futuras

1. Mantener siempre la estructura organizada cuando se añadan nuevos archivos
2. Documentar adecuadamente cualquier cambio importante en los archivos README
3. Considerar la eliminación de `campo_unido_deploy.zip` cuando ya no sea necesario
4. Actualizar cualquier referencia a los scripts o documentación en otros archivos del proyecto 