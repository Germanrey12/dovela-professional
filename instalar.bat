@echo off
echo ========================================
echo    DOVELA PROFESSIONAL v2.0
echo    Instalador Automatico
echo ========================================
echo.
echo Desarrollado por: German Andres Rey Carrillo
echo Ingeniero Civil, M. Eng.
echo Director de Diseno PROPISOS S.A.
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado.
    echo Por favor instale Python 3.12+ desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Python detectado correctamente
echo.

REM Crear entorno virtual
echo [2/4] Creando entorno virtual...
python -m venv .venv
if %errorlevel% neq 0 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

REM Activar entorno virtual
echo [3/4] Activando entorno virtual...
call .venv\Scripts\activate.bat

REM Instalar dependencias
echo [4/4] Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo.
echo ========================================
echo    INSTALACION COMPLETADA
echo ========================================
echo.
echo Para ejecutar la aplicacion:
echo 1. Abra una terminal en esta carpeta
echo 2. Active el entorno: .venv\Scripts\activate
echo 3. Ejecute: python ejecutar_dovelas.py
echo.
echo O simplemente ejecute: ejecutar_aplicacion.bat
echo.
pause
