#!/bin/bash

# Script de instalación para Dovela Professional v2.0
# Autor: Germán Andrés Rey Carrillo

echo "🔧 INSTALANDO DOVELA PROFESSIONAL v2.0"
echo "========================================"
echo "Autor: Germán Andrés Rey Carrillo"
echo "PROPISOS S.A."
echo ""

# Verificar Python
python --version
if [ $? -ne 0 ]; then
    echo "❌ Python no encontrado. Instale Python 3.12+"
    exit 1
fi

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python -m venv .venv

# Activar entorno virtual (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
echo "⬇️ Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Instalación completada"
echo ""
echo "🚀 Para ejecutar la aplicación:"
echo "   source .venv/bin/activate"
echo "   python ejecutar_dovelas.py"
