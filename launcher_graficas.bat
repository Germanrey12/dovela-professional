@echo off
chcp 65001 > nul
title Dovela Diamante - Con Graficas Mejoradas

echo ===============================================
echo    DOVELA DIAMANTE - GRAFICAS FUNCIONALES
echo ===============================================
echo.
echo 🎨 MEJORAS IMPLEMENTADAS:
echo ✅ Graficas de ejemplo visibles al iniciar
echo ✅ Contornos de esfuerzos realistas
echo ✅ Patron de dovela diamante
echo ✅ Colormaps profesionales
echo ✅ Resultados simulados cuando analisis falla
echo ✅ Factor de seguridad calculado
echo ✅ Informacion detallada del analisis
echo.
echo 🔧 FUNCIONALIDAD DEL ANALISIS:
echo ✅ Boton "Ejecutar Analisis Completo" (F5)
echo ✅ Boton "Analisis Rapido" (F6)
echo ✅ Fallback a resultados simulados
echo ✅ Cambio automatico a pestana de resultados
echo.
echo ⚡ Iniciando aplicacion...

if exist "src\main.py" (
    python src\main.py
) else (
    echo ❌ Error: No se encontro src\main.py
    pause
    exit /b 1
)

echo.
echo 📋 Pruebe los botones de analisis en la barra de herramientas
echo 💡 Las graficas ahora muestran patrones realistas
pause
