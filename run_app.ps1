# ============================================================================
# DOVELA DIAMANTE - PROFESSIONAL APPLICATION LAUNCHER
# ============================================================================
# Script de lanzamiento profesional para la aplicación de análisis de dovelas
# Autor: Sistema de Desarrollo Automatizado
# Fecha: Septiembre 3, 2025
# Versión: 2.0 Professional
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("gui", "console", "test", "legacy", "help")]
    [string]$Mode = "menu",
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose,
    
    [Parameter(Mandatory=$false)]
    [switch]$NoVenv
)

# Configuración de colores para output profesional
$Host.UI.RawUI.WindowTitle = "Dovela Diamante - Professional Analysis Tool"

# Funciones de utilidad para output con colores
function Write-Header {
    param([string]$Text)
    Write-Host "`n" -NoNewline
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Yellow -BackgroundColor DarkBlue
    Write-Host "=" * 80 -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Text)
    Write-Host "✅ $Text" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Text)
    Write-Host "⚠️  $Text" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Text)
    Write-Host "❌ $Text" -ForegroundColor Red
}

function Write-Info {
    param([string]$Text)
    Write-Host "ℹ️  $Text" -ForegroundColor Cyan
}

function Write-Progress {
    param([string]$Text)
    Write-Host "⚡ $Text" -ForegroundColor Magenta
}

# Función para verificar dependencias
function Test-Dependencies {
    Write-Progress "Verificando dependencias del sistema..."
    
    # Verificar Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python encontrado: $pythonVersion"
        } else {
            throw "Python no encontrado"
        }
    } catch {
        Write-Error "Python no está instalado o no está en el PATH"
        Write-Info "Instale Python desde https://python.org"
        return $false
    }
    
    # Verificar estructura del proyecto
    $requiredPaths = @(
        "src\main.py",
        "src\config\settings.py",
        "src\core\geometry.py",
        "src\gui\main_window.py"
    )
    
    foreach ($path in $requiredPaths) {
        if (-not (Test-Path $path)) {
            Write-Error "Archivo requerido no encontrado: $path"
            return $false
        }
    }
    
    Write-Success "Estructura del proyecto verificada"
    return $true
}

# Función para configurar entorno virtual
function Initialize-VirtualEnvironment {
    if ($NoVenv) {
        Write-Info "Saltando configuración de entorno virtual (--NoVenv especificado)"
        return $true
    }
    
    Write-Progress "Configurando entorno virtual..."
    
    # Verificar si existe el entorno virtual
    if (-not (Test-Path ".venv")) {
        Write-Info "Creando entorno virtual..."
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Error al crear entorno virtual"
            return $false
        }
        Write-Success "Entorno virtual creado"
    }
    
    # Activar entorno virtual
    $activateScript = ".venv\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        Write-Info "Activando entorno virtual..."
        & $activateScript
        Write-Success "Entorno virtual activado"
    } else {
        Write-Warning "Script de activación no encontrado, usando Python del sistema"
    }
    
    # Instalar dependencias si es necesario
    if (Test-Path "requirements.txt") {
        Write-Info "Verificando dependencias de Python..."
        pip install -r requirements.txt --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Dependencias verificadas/instaladas"
        } else {
            Write-Warning "Algunas dependencias podrían no haberse instalado correctamente"
        }
    }
    
    return $true
}

# Función para mostrar menú interactivo
function Show-InteractiveMenu {
    Write-Header "DOVELA DIAMANTE - ANÁLISIS PROFESIONAL DE ESTRUCTURAS"
    
    Write-Host "`n🏗️  OPCIONES DISPONIBLES:" -ForegroundColor Yellow
    Write-Host "   1. 🖥️  Interfaz Gráfica (GUI) - Recomendado" -ForegroundColor Green
    Write-Host "   2. 💻 Modo Consola (Testing)" -ForegroundColor Cyan  
    Write-Host "   3. 🧪 Pruebas de Validación" -ForegroundColor Magenta
    Write-Host "   4. 📜 Aplicación Legacy (Original)" -ForegroundColor Yellow
    Write-Host "   5. 📖 Información del Sistema" -ForegroundColor Blue
    Write-Host "   6. 🚪 Salir" -ForegroundColor Red
    
    Write-Host "`n" -NoNewline
    $choice = Read-Host "Seleccione una opción (1-6)"
    
    switch ($choice) {
        "1" { return "gui" }
        "2" { return "console" }
        "3" { return "test" }
        "4" { return "legacy" }
        "5" { return "info" }
        "6" { return "exit" }
        default { 
            Write-Warning "Opción inválida. Seleccionando interfaz gráfica por defecto."
            return "gui" 
        }
    }
}

# Función para ejecutar la aplicación
function Start-Application {
    param([string]$ExecutionMode)
    
    switch ($ExecutionMode) {
        "gui" {
            Write-Header "INICIANDO INTERFAZ GRÁFICA"
            Write-Progress "Cargando aplicación moderna..."
            python src\main.py
        }
        
        "console" {
            Write-Header "INICIANDO MODO CONSOLA"
            Write-Progress "Ejecutando análisis en consola..."
            python src\main.py console
        }
        
        "test" {
            Write-Header "EJECUTANDO PRUEBAS DE VALIDACIÓN"
            Write-Progress "Corriendo tests automáticos..."
            python src\main.py test
        }
        
        "legacy" {
            Write-Header "INICIANDO APLICACIÓN LEGACY"
            Write-Progress "Cargando versión original..."
            if (Test-Path "deflexion_gui_complete.py") {
                python deflexion_gui_complete.py
            } else {
                Write-Error "Archivo legacy no encontrado: deflexion_gui_complete.py"
                return $false
            }
        }
        
        "info" {
            Show-SystemInfo
            return $true
        }
        
        "exit" {
            Write-Info "Saliendo de la aplicación..."
            return $true
        }
        
        default {
            Write-Error "Modo de ejecución desconocido: $ExecutionMode"
            return $false
        }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Aplicación ejecutada exitosamente"
        return $true
    } else {
        Write-Error "Error durante la ejecución (Código: $LASTEXITCODE)"
        return $false
    }
}

# Función para mostrar información del sistema
function Show-SystemInfo {
    Write-Header "INFORMACIÓN DEL SISTEMA"
    
    Write-Host "`n📊 ESTADO DEL PROYECTO:" -ForegroundColor Yellow
    
    # Información de Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python: $pythonVersion"
    } catch {
        Write-Error "Python: No disponible"
    }
    
    # Información del entorno virtual
    if (Test-Path ".venv") {
        Write-Success "Entorno Virtual: Configurado"
    } else {
        Write-Warning "Entorno Virtual: No configurado"
    }
    
    # Módulos del proyecto
    $modules = @(
        "src\config\settings.py",
        "src\core\geometry.py", 
        "src\core\stress_analysis.py",
        "src\core\fea_solver.py",
        "src\gui\main_window.py",
        "src\utils\logging_config.py",
        "src\utils\validators.py",
        "src\utils\unit_converter.py"
    )
    
    Write-Host "`n🔧 MÓDULOS PROFESIONALES:" -ForegroundColor Yellow
    foreach ($module in $modules) {
        if (Test-Path $module) {
            $size = (Get-Item $module).Length
            Write-Success "$(Split-Path $module -Leaf): $('{0:N0}' -f $size) bytes"
        } else {
            Write-Error "$(Split-Path $module -Leaf): No encontrado"
        }
    }
    
    # Información de dependencias
    if (Test-Path "requirements.txt") {
        $requirements = Get-Content "requirements.txt" | Where-Object { $_ -notmatch "^#" -and $_ -ne "" }
        Write-Host "`n📦 DEPENDENCIAS REQUERIDAS:" -ForegroundColor Yellow
        foreach ($req in $requirements) {
            Write-Info $req
        }
    }
    
    Write-Host "`n🎯 CARACTERÍSTICAS:" -ForegroundColor Yellow
    Write-Success "✅ Arquitectura modular profesional"
    Write-Success "✅ Análisis según normas AASHTO"
    Write-Success "✅ Engine FEA con scikit-fem"
    Write-Success "✅ Interfaz gráfica moderna"
    Write-Success "✅ Sistema de logging avanzado"
    Write-Success "✅ Validación automática"
    Write-Success "✅ Conversión de unidades"
    Write-Success "✅ Testing framework integrado"
}

# Función para mostrar ayuda
function Show-Help {
    Write-Header "AYUDA - DOVELA DIAMANTE LAUNCHER"
    
    Write-Host @"

📖 USO:
   .\run_app.ps1 [MODO] [OPCIONES]

🎯 MODOS DISPONIBLES:
   gui      - Interfaz gráfica (por defecto)
   console  - Modo consola para testing
   test     - Ejecutar pruebas de validación
   legacy   - Aplicación original
   help     - Mostrar esta ayuda

⚙️  OPCIONES:
   -Verbose - Mostrar información detallada
   -NoVenv  - No usar entorno virtual

📝 EJEMPLOS:
   .\run_app.ps1                    # Menú interactivo
   .\run_app.ps1 gui                # Interfaz gráfica directa
   .\run_app.ps1 console -Verbose   # Consola con detalles
   .\run_app.ps1 test               # Ejecutar pruebas

🔧 RESOLUCIÓN DE PROBLEMAS:
   - Asegúrese de que Python esté instalado
   - Verifique que las dependencias estén instaladas
   - Use -Verbose para información detallada
   - Ejecute como administrador si hay problemas de permisos

"@ -ForegroundColor Cyan
}

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

function Main {
    try {
        # Configurar política de ejecución si es necesario
        if ((Get-ExecutionPolicy) -eq "Restricted") {
            Write-Warning "Política de ejecución restrictiva detectada"
            Write-Info "Ejecute: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
        }
        
        # Mostrar ayuda si se solicita
        if ($Mode -eq "help") {
            Show-Help
            return
        }
        
        # Verificar dependencias
        if (-not (Test-Dependencies)) {
            Write-Error "Verificación de dependencias falló"
            return
        }
        
        # Configurar entorno
        if (-not (Initialize-VirtualEnvironment)) {
            Write-Error "Error al configurar entorno virtual"
            return
        }
        
        # Determinar modo de ejecución
        $executionMode = $Mode
        if ($Mode -eq "menu") {
            $executionMode = Show-InteractiveMenu
        }
        
        # Ejecutar aplicación
        if ($executionMode -ne "exit") {
            $success = Start-Application -ExecutionMode $executionMode
            
            if ($success) {
                Write-Host "`n" -NoNewline
                Write-Success "Operación completada exitosamente"
            } else {
                Write-Host "`n" -NoNewline
                Write-Error "La operación falló"
            }
        }
        
        # Mensaje final
        Write-Host "`n📋 Para más información, ejecute: .\run_app.ps1 help" -ForegroundColor Gray
        
    } catch {
        Write-Error "Error inesperado: $($_.Exception.Message)"
        Write-Info "Stack trace: $($_.ScriptStackTrace)"
    }
}

# Ejecutar función principal
Main
