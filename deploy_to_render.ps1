# Script para desplegar en Render
# Ejecutar en PowerShell desde la raíz del proyecto

$projectName = "campo-unido"
$githubRepo = ""

function Show-Title {
    param([string]$Title)
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Cyan
}

function Generate-SecretKey {
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-=_+[]{}|;:,.<>?/"
    $secret = ""
    1..50 | ForEach-Object { $secret += $chars[(Get-Random -Maximum $chars.Length)] }
    return $secret
}

# Verificar requisitos previos
Show-Title "Verificando requisitos previos"
try {
    git --version | Out-Null
    Write-Host "✅ Git instalado" -ForegroundColor Green
} catch {
    Write-Host "❌ Git no está instalado o no está en el PATH. Por favor instala Git: https://git-scm.com/downloads" -ForegroundColor Red
    exit
}

# Inicializar Git y preparar el repositorio
Show-Title "Inicializando repositorio Git"
if (-not (Test-Path ".git")) {
    Write-Host "Inicializando repositorio Git..." -ForegroundColor Yellow
    git init
}

# Chequeando archivos y carpetas necesarias
Show-Title "Verificando archivos necesarios para el despliegue"

$requiredFiles = @(
    "render.yaml", 
    "requirements.txt", 
    "build.sh", 
    "Procfile", 
    "config/settings/production.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file encontrado" -ForegroundColor Green
    } else {
        Write-Host "❌ $file no encontrado" -ForegroundColor Red
    }
}

# Generar una SECRET_KEY para producción
$secretKey = Generate-SecretKey
Write-Host "✅ SECRET_KEY generada para producción" -ForegroundColor Green
Write-Host "   Guarda esta clave en un lugar seguro:" -ForegroundColor Yellow
Write-Host "   $secretKey" -ForegroundColor Cyan

# Solicitar al usuario que cree un repositorio en GitHub
Show-Title "Configurando repositorio en GitHub"
Write-Host "Para continuar con el despliegue en Render, necesitas crear un repositorio en GitHub."
Write-Host "1. Ve a https://github.com/new" -ForegroundColor Yellow
Write-Host "2. Crea un nuevo repositorio (preferiblemente llamado 'campo-unido')" -ForegroundColor Yellow
Write-Host "3. NO inicialices el repositorio con README, .gitignore o licencia" -ForegroundColor Yellow
Write-Host "4. Copia la URL del repositorio (formato: https://github.com/tu-usuario/campo-unido.git)" -ForegroundColor Yellow

$githubRepo = Read-Host "Ingresa la URL del repositorio de GitHub"

if ([string]::IsNullOrWhiteSpace($githubRepo)) {
    Write-Host "❌ No se proporcionó URL de repositorio. No podrás hacer push a GitHub." -ForegroundColor Red
} else {
    Write-Host "✅ Repositorio GitHub configurado: $githubRepo" -ForegroundColor Green
}

# Añadiendo archivos al repositorio
Show-Title "Añadiendo archivos al repositorio Git"
Write-Host "Añadiendo archivos..." -ForegroundColor Yellow
git add .
git status

# Realizando commit
$commitMessage = "Configuración inicial para despliegue en Render"
Write-Host "Realizando commit: $commitMessage" -ForegroundColor Yellow
git commit -m $commitMessage

# Configurando el repositorio remoto
if (-not [string]::IsNullOrWhiteSpace($githubRepo)) {
    Write-Host "Configurando repositorio remoto..." -ForegroundColor Yellow
    git remote add origin $githubRepo
    
    # Creando rama main
    Write-Host "Creando rama main..." -ForegroundColor Yellow
    git branch -M main
    
    # Haciendo push
    Write-Host "Haciendo push al repositorio remoto..." -ForegroundColor Yellow
    git push -u origin main
    
    Write-Host "✅ Código subido a GitHub con éxito" -ForegroundColor Green
}

# Instrucciones para desplegar en Render
Show-Title "Instrucciones para desplegar en Render"
Write-Host "1. Ve a https://dashboard.render.com/" -ForegroundColor Yellow
Write-Host "2. Inicia sesión o crea una cuenta" -ForegroundColor Yellow
Write-Host "3. Haz clic en 'New +' y selecciona 'Web Service'" -ForegroundColor Yellow
Write-Host "4. Conecta tu repositorio de GitHub" -ForegroundColor Yellow
Write-Host "5. Configura el servicio:" -ForegroundColor Yellow
Write-Host "   - Nombre: $projectName (o el que prefieras)" -ForegroundColor Cyan
Write-Host "   - Región: la más cercana a tus usuarios" -ForegroundColor Cyan
Write-Host "   - Rama: main" -ForegroundColor Cyan
Write-Host "   - Runtime: Python" -ForegroundColor Cyan
Write-Host "   - Build Command: ./build.sh" -ForegroundColor Cyan
Write-Host "   - Start Command: gunicorn config.wsgi:application" -ForegroundColor Cyan
Write-Host "6. En 'Advanced' añade las siguientes variables de entorno:" -ForegroundColor Yellow
Write-Host "   - DJANGO_SETTINGS_MODULE: config.settings.production" -ForegroundColor Cyan
Write-Host "   - DJANGO_SECRET_KEY: $secretKey" -ForegroundColor Cyan
Write-Host "   - PYTHON_VERSION: 3.10" -ForegroundColor Cyan
Write-Host "7. Haz clic en 'Create Web Service'" -ForegroundColor Yellow

Write-Host ""
Write-Host "Para más detalles, consulta el archivo RENDER_DEPLOY.md" -ForegroundColor Green
Write-Host ""
Write-Host "¡Todo listo para desplegar en Render!" -ForegroundColor Green 