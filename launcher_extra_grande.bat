@echo off
chcp 65001 > nul
title Dovela Diamante - Interfaz EXTRA GRANDE

echo ===============================================
echo    DOVELA DIAMANTE - INTERFAZ EXTRA GRANDE
echo ===============================================
echo.
echo 🔍 MEJORAS APLICADAS:
echo ✅ Ventana: 2000x1400 pixels (MAXIMA)
echo ✅ Fuentes: 24pt titulos, 18pt encabezados, 14pt texto
echo ✅ Botones: Doble padding (20x15)
echo ✅ Espaciado: Triple padding (30px)
echo ✅ Escalado DPI: 150%% automatico
echo ✅ Filas tablas: 30px altura
echo.
echo ⚡ Iniciando interfaz MAXIMIZADA...

if exist "src\main.py" (
    python src\main.py
) else (
    echo ❌ Error: No se encontro src\main.py
    pause
    exit /b 1
)

echo.
echo 📋 Si aun es pequeña, ajuste la resolucion de pantalla
echo 💡 O modifique config_interfaz.ini para valores personalizados
pause
