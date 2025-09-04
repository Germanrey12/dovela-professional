@echo off
chcp 65001 > nul
title Dovela Diamante - Interfaz Maximizada

echo ===============================================
echo    DOVELA DIAMANTE - INTERFAZ GRANDE
echo ===============================================
echo.
echo ⚡ Iniciando aplicacion con interfaz maximizada...
echo ℹ️  Ventana: 1800x1200 pixels (pantalla completa)
echo ℹ️  Fuentes: Aumentadas para mejor legibilidad
echo ℹ️  Espaciado: Mejorado para facilitar uso
echo.

if exist "src\main.py" (
    python src\main.py
) else (
    echo ❌ Error: No se encontro src\main.py
    echo.
    echo Alternativas disponibles:
    if exist "deflexion_gui_complete.py" (
        echo 🔄 Ejecutando version original...
        python deflexion_gui_complete.py
    ) else (
        echo ❌ No se encontraron archivos de aplicacion
    )
)

echo.
echo 📋 Interfaz optimizada para mejor visibilidad
pause
