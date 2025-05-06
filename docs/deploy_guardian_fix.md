# Solución del Warning de Django Guardian

## Problema

Al ejecutar el servidor de desarrollo, aparecía el siguiente warning:

```
WARNINGS:
?: (guardian.W001) Guardian authentication backend is not hooked. You can add this in settings as eg: `AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', 'guardian.backends.ObjectPermissionBackend')`.
```

## Causa

El problema ocurre porque `django-guardian` requiere que su backend de autenticación esté configurado en `AUTHENTICATION_BACKENDS`, pero la configuración en `local.py` estaba sobrescribiendo la configuración correcta que ya existía en `base.py`.

## Solución

1. En `base.py` ya existía la configuración correcta:

```python
# Authentication backends
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)
```

2. Pero en `local.py` se sobrescribía sin incluir el backend de guardian:

```python
# Configuración de autenticación
AUTHENTICATION_BACKENDS = [
    'apps.core.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

3. La solución fue añadir el backend de guardian a la configuración en `local.py`:

```python
# Configuración de autenticación
AUTHENTICATION_BACKENDS = [
    'apps.core.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',  # Guardian backend
]
```

## Implicaciones para el Despliegue

En el despliegue a PythonAnywhere, se debe asegurar que:

1. Si se usa `config.settings.production`, la configuración en `base.py` se mantiene.

2. Si se modifica `production.py` para incluir un `AUTHENTICATION_BACKENDS` propio, debe incluir el backend de guardian.

El script `pythonanywhere_deploy.sh` ya incluye una verificación y corrección automática para este problema.

## Verificación

Para comprobar que el warning ha sido resuelto, ejecuta:

```bash
python manage.py check
```

No debería aparecer ningún warning relacionado con guardian. 