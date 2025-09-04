@echo off
echo ===============================================
echo ANÁLISIS PROFESIONAL DE DOVELAS DIAMANTE v2.0
echo ===============================================
echo.

cd /d "%~dp0"

echo Verificando entorno virtual...
if exist ".venv\Scripts\python.exe" (
    echo ✅ Entorno virtual encontrado
    set PYTHON_EXE=.venv\Scripts\python.exe
) else (
    echo ⚠️ Usando Python del sistema
    set PYTHON_EXE=python
)

echo.
echo Seleccione el modo de ejecución:
echo [1] Interfaz Gráfica (Recomendado)
echo [2] Modo Consola (Testing)
echo [3] Pruebas de Validación
echo [4] Salir
echo.

set /p choice=Ingrese su elección (1-4): 

if "%choice%"=="1" (
    echo.
    echo 🚀 Iniciando interfaz gráfica...
    "%PYTHON_EXE%" src\main.py
) else if "%choice%"=="2" (
    echo.
    echo 🔧 Ejecutando modo consola...
    "%PYTHON_EXE%" src\main.py console
    pause
) else if "%choice%"=="3" (
    echo.
    echo 🧪 Ejecutando pruebas de validación...
    "%PYTHON_EXE%" src\main.py test
    pause
) else if "%choice%"=="4" (
    exit /b
) else (
    echo.
    echo ❌ Opción inválida
    pause
    goto :eof
)

if errorlevel 1 (
    echo.
    echo ❌ Error durante la ejecución
    echo Ver logs en la carpeta 'logs' para más detalles
    pause
)
