# Launcher Simple para Dovela Diamante
# Versión simplificada que funciona en cualquier sistema

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "    DOVELA DIAMANTE - LAUNCHER SIMPLE" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Opciones disponibles:" -ForegroundColor Green
Write-Host "1. Interfaz Grafica (GUI)" -ForegroundColor White
Write-Host "2. Modo Consola" -ForegroundColor White  
Write-Host "3. Pruebas de Validacion" -ForegroundColor White
Write-Host "4. Aplicacion Original" -ForegroundColor White
Write-Host "5. Salir" -ForegroundColor White
Write-Host ""

$opcion = Read-Host "Seleccione una opcion (1-5)"

switch ($opcion) {
    "1" {
        Write-Host "Iniciando interfaz grafica..." -ForegroundColor Green
        if (Test-Path "src\main.py") {
            python src\main.py
        } else {
            Write-Host "Error: No se encontro src\main.py" -ForegroundColor Red
        }
    }
    "2" {
        Write-Host "Iniciando modo consola..." -ForegroundColor Green
        if (Test-Path "src\main.py") {
            python src\main.py console
        } else {
            Write-Host "Error: No se encontro src\main.py" -ForegroundColor Red
        }
    }
    "3" {
        Write-Host "Ejecutando pruebas..." -ForegroundColor Green
        if (Test-Path "src\main.py") {
            python src\main.py test
        } else {
            Write-Host "Error: No se encontro src\main.py" -ForegroundColor Red
        }
    }
    "4" {
        Write-Host "Iniciando aplicacion original..." -ForegroundColor Green
        if (Test-Path "deflexion_gui_complete.py") {
            python deflexion_gui_complete.py
        } else {
            Write-Host "Error: No se encontro deflexion_gui_complete.py" -ForegroundColor Red
        }
    }
    "5" {
        Write-Host "Saliendo..." -ForegroundColor Yellow
        exit
    }
    default {
        Write-Host "Opcion invalida. Iniciando GUI por defecto..." -ForegroundColor Yellow
        if (Test-Path "src\main.py") {
            python src\main.py
        } else {
            Write-Host "Error: No se encontro src\main.py" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "Presione cualquier tecla para continuar..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
