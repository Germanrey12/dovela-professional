@echo off
chcp 65001 > nul
title Dovela Diamante - Campos Profesionales Completos

echo ===============================================
echo    DOVELA DIAMANTE - ANALISIS PROFESIONAL
echo ===============================================
echo.
echo 📋 CAMPOS PROFESIONALES AGREGADOS:
echo.
echo 🌡️  PARAMETROS NORMATIVOS:
echo ✅ Temperatura de servicio / maxima / minima
echo ✅ Factor de impacto AASHTO (IM)
echo ✅ Factor de distribucion de carga
echo ✅ Ciclos de fatiga esperados
echo.
echo 🌦️  CONDICIONES AMBIENTALES:
echo ✅ Humedad relativa
echo ✅ Velocidad del viento
echo ✅ Exposicion a corrosion (4 niveles)
echo ✅ Zona sismica (0-4)
echo.
echo 🔍 CONTROLES DE INTERFAZ:
echo ✅ Boton de zoom con slider
echo ✅ Zoom in/out (+/-)
echo ✅ Reset zoom (100%%)
echo ✅ Indicador visual del nivel
echo.
echo 📊 NORMATIVAS CONSIDERADAS:
echo ✅ AASHTO LRFD Bridge Design
echo ✅ Condiciones ambientales
echo ✅ Fatiga y vida util
echo ✅ Efectos termicos
echo.
echo ⚡ Iniciando aplicacion con campos completos...

if exist "src\main.py" (
    python src\main.py
) else (
    echo ❌ Error: No se encontro src\main.py
    pause
    exit /b 1
)

echo.
echo 💡 Use el slider de zoom para ajustar el tamaño
echo 📋 Todos los campos son necesarios para analisis profesional
pause
