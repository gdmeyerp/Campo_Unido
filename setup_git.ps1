# Script para inicializar Git y preparar el repositorio
# Ejecutar en PowerShell desde la raíz del proyecto

# Inicializar repositorio Git (si no existe)
if (-not (Test-Path ".git")) {
    Write-Host "Inicializando repositorio Git..." -ForegroundColor Green
    git init
}

# Añadir todos los archivos
Write-Host "Añadiendo archivos al staging..." -ForegroundColor Green
git add .

# Verificar si hay un commit inicial
$hasCommits = git log --oneline 2>&1
if ($hasCommits -match "fatal" -or $hasCommits -eq $null) {
    # Realizar commit inicial
    Write-Host "Realizando commit inicial..." -ForegroundColor Green
    git commit -m "Configuración inicial para despliegue en Render"
} else {
    # Realizar commit de los cambios
    Write-Host "Realizando commit de los cambios..." -ForegroundColor Green
    git commit -m "Actualización para despliegue en Render"
}

# Instrucciones para vincular con GitHub y hacer push
Write-Host "`nPara subir a GitHub, ejecuta los siguientes comandos:" -ForegroundColor Yellow
Write-Host "1. Crea un repositorio en GitHub (sin README ni .gitignore)" -ForegroundColor Yellow
Write-Host "2. Ejecuta:" -ForegroundColor Yellow
Write-Host "   git remote add origin https://github.com/tu-usuario/campo-unido.git" -ForegroundColor Cyan
Write-Host "   git branch -M main" -ForegroundColor Cyan
Write-Host "   git push -u origin main" -ForegroundColor Cyan

Write-Host "`nLuego sigue las instrucciones en RENDER_DEPLOY.md para desplegar en Render" -ForegroundColor Green 