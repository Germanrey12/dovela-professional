@echo off
chcp 65001 > nul
title Dovela Diamante - Launcher Simple

echo ===============================================
echo    DOVELA DIAMANTE - LAUNCHER SIMPLE
echo ===============================================
echo.

echo Opciones disponibles:
echo 1. Interfaz Grafica (GUI)
echo 2. Modo Consola  
echo 3. Pruebas de Validacion
echo 4. Aplicacion Original
echo 5. Salir
echo.

set /p opcion="Seleccione una opcion (1-5): "

if "%opcion%"=="1" (
    echo Iniciando interfaz grafica...
    if exist "src\main.py" (
        python src\main.py
    ) else (
        echo Error: No se encontro src\main.py
        pause
    )
) else if "%opcion%"=="2" (
    echo Iniciando modo consola...
    if exist "src\main.py" (
        python src\main.py console
    ) else (
        echo Error: No se encontro src\main.py
        pause
    )
) else if "%opcion%"=="3" (
    echo Ejecutando pruebas...
    if exist "src\main.py" (
        python src\main.py test
    ) else (
        echo Error: No se encontro src\main.py
        pause
    )
) else if "%opcion%"=="4" (
    echo Iniciando aplicacion original...
    if exist "deflexion_gui_complete.py" (
        python deflexion_gui_complete.py
    ) else (
        echo Error: No se encontro deflexion_gui_complete.py
        pause
    )
) else if "%opcion%"=="5" (
    echo Saliendo...
    exit /b
) else (
    echo Opcion invalida. Iniciando GUI por defecto...
    if exist "src\main.py" (
        python src\main.py
    ) else (
        echo Error: No se encontro src\main.py
        pause
    )
)

echo.
pause
