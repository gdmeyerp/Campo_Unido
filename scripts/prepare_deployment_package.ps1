# Script para preparar un paquete de despliegue para PythonAnywhere
# Ejecutar en PowerShell desde la raíz del proyecto

# Configuración
$ProjectName = "campo_unido"
$DeploymentFilesDir = "deployment_files"
$TempDir = ".\temp_deploy"
$ZipFile = "${ProjectName}_deploy.zip"

# Crear directorio temporal si no existe
Write-Host "Creando directorio temporal..." -ForegroundColor Green
if (-not (Test-Path $TempDir)) {
    New-Item -ItemType Directory -Path $TempDir | Out-Null
}

# Copiar archivos de despliegue a directorio temporal
Write-Host "Copiando archivos de despliegue..." -ForegroundColor Green
Copy-Item "requirements.txt" -Destination $TempDir
Copy-Item "pythonanywhere_deploy.sh" -Destination $TempDir
Copy-Item "example_wsgi_pythonanywhere.py" -Destination $TempDir
Copy-Item "example_wsgi_pythonanywhere_sqlite.py" -Destination $TempDir
Copy-Item "pythonAnywhere_setup.md" -Destination $TempDir
Copy-Item "README_DEPLOYMENT.md" -Destination $TempDir
Copy-Item "sqlite_tips.md" -Destination $TempDir
Copy-Item "deploy_checklist.md" -Destination $TempDir
Copy-Item "deploy_quick_start.md" -Destination $TempDir
Copy-Item "deploy_guardian_fix.md" -Destination $TempDir

# Copiar código fuente
Write-Host "Copiando código fuente..." -ForegroundColor Green
Copy-Item -Recurse ".\apps" -Destination $TempDir

if (Test-Path ".\config") {
    Copy-Item -Recurse ".\config" -Destination $TempDir
} else {
    Write-Host "No se encontró el directorio 'config'" -ForegroundColor Yellow
}

if (Test-Path ".\templates") {
    Copy-Item -Recurse ".\templates" -Destination $TempDir
} else {
    Write-Host "No se encontró el directorio 'templates'" -ForegroundColor Yellow
}

if (Test-Path ".\static") {
    Copy-Item -Recurse ".\static" -Destination $TempDir
} else {
    Write-Host "No se encontró el directorio 'static'" -ForegroundColor Yellow
}

Copy-Item "manage.py" -Destination $TempDir

# Preguntar si se debe incluir la base de datos
$IncludeDB = Read-Host "¿Incluir base de datos (db.sqlite3)? (s/n)"
if ($IncludeDB -eq "s") {
    Write-Host "Copiando base de datos..." -ForegroundColor Green
    if (Test-Path "db.sqlite3") {
        Copy-Item "db.sqlite3" -Destination $TempDir
    } else {
        Write-Host "No se encontró el archivo 'db.sqlite3'" -ForegroundColor Yellow
    }
}

# Preguntar si se deben incluir los archivos de media
$IncludeMedia = Read-Host "¿Incluir archivos de media? (s/n)"
if ($IncludeMedia -eq "s") {
    Write-Host "Copiando archivos de media..." -ForegroundColor Green
    if (Test-Path ".\media") {
        Copy-Item -Recurse ".\media" -Destination $TempDir
    } else {
        Write-Host "No se encontró el directorio 'media'" -ForegroundColor Yellow
        # Crear directorio media vacío
        New-Item -ItemType Directory -Path "$TempDir\media" | Out-Null
    }
}

# Verificar si hay archivos estáticos recolectados
if (Test-Path ".\staticfiles") {
    $IncludeStatic = Read-Host "¿Incluir archivos estáticos recolectados? (s/n)"
    if ($IncludeStatic -eq "s") {
        Write-Host "Copiando archivos estáticos..." -ForegroundColor Green
        Copy-Item -Recurse ".\staticfiles" -Destination $TempDir
    }
} else {
    Write-Host "No se encontró el directorio 'staticfiles', se creará al desplegar" -ForegroundColor Yellow
    # Crear directorio staticfiles vacío para mantener la estructura
    New-Item -ItemType Directory -Path "$TempDir\staticfiles" | Out-Null
}

# Comprimir archivos
Write-Host "Comprimiendo archivos..." -ForegroundColor Green
if (Test-Path $ZipFile) {
    Remove-Item $ZipFile
}
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($TempDir, $ZipFile)

# Limpiar directorio temporal
Write-Host "Limpiando directorio temporal..." -ForegroundColor Green
Remove-Item -Recurse -Force $TempDir

Write-Host "Paquete de despliegue creado: $ZipFile" -ForegroundColor Green
Write-Host "Tamaño: $([Math]::Round((Get-Item $ZipFile).Length / 1MB, 2)) MB" -ForegroundColor Green
Write-Host "Listo para subir a PythonAnywhere!" -ForegroundColor Green 