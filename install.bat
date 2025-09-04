@echo off
REM Script de instalación para Dovela Professional v2.0
REM Autor: Germán Andrés Rey Carrillo

echo 🔧 INSTALANDO DOVELA PROFESSIONAL v2.0
echo ========================================
echo Autor: Germán Andrés Rey Carrillo
echo PROPISOS S.A.
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Instale Python 3.12+
    pause
    exit /b 1
)

REM Crear entorno virtual
echo 📦 Creando entorno virtual...
python -m venv .venv

REM Activar entorno virtual (Windows)
call .venv\Scripts\activate.bat

REM Instalar dependencias
echo ⬇️ Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✅ Instalación completada
echo.
echo 🚀 Para ejecutar la aplicación:
echo    .venv\Scripts\activate
echo    python ejecutar_dovelas.py
pause
