@echo off
echo ========================================
echo    DOVELA PROFESSIONAL v2.0
echo    Iniciando Aplicacion...
echo ========================================
echo.

REM Verificar si existe el entorno virtual
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Entorno virtual no encontrado.
    echo Ejecute primero: instalar.bat
    pause
    exit /b 1
)

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Ejecutar aplicacion
echo Iniciando DOVELA PROFESSIONAL...
echo.
python ejecutar_dovelas.py

REM Si hay error, mostrar mensaje
if %errorlevel% neq 0 (
    echo.
    echo ERROR: La aplicacion no pudo iniciarse correctamente.
    echo Verifique que todas las dependencias esten instaladas.
    echo.
    pause
)
