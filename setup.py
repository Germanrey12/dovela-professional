#!/usr/bin/env python3
"""
Script de instalación y configuración para la aplicación de dovelas diamante
"""
import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    if sys.version_info < (3, 8):
        print("❌ ERROR: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - Compatible")
    return True

def install_dependencies():
    """Instala las dependencias requeridas"""
    print("\n📦 Instalando dependencias...")
    
    try:
        # Actualizar pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Instalar dependencias del requirements.txt
        requirements_file = Path("requirements.txt")
        if requirements_file.exists():
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencias instaladas correctamente")
        else:
            print("⚠️ Archivo requirements.txt no encontrado")
            
            # Instalar dependencias mínimas
            basic_deps = ["numpy", "scipy", "matplotlib"]
            for dep in basic_deps:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def create_directories():
    """Crea directorios necesarios"""
    print("\n📁 Creando directorios...")
    
    directories = [
        "logs",
        "output",
        "projects",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ {directory}/")

def test_installation():
    """Prueba que la instalación funcione correctamente"""
    print("\n🧪 Probando instalación...")
    
    try:
        # Cambiar al directorio src para imports
        sys.path.insert(0, str(Path("src")))
        
        # Probar imports básicos
        import numpy as np
        import matplotlib.pyplot as plt
        import scipy
        print("   ✅ Dependencias científicas")
        
        # Probar módulos propios
        from config.settings import DEFAULT_SETTINGS
        from utils.validators import DovelaValidator
        print("   ✅ Módulos de configuración")
        
        from core.geometry import DiamondDovelaGeometry
        from core.stress_analysis import ClassicalStressAnalyzer
        print("   ✅ Módulos de análisis")
        
        print("✅ Instalación verificada correctamente")
        return True
        
    except ImportError as e:
        print(f"❌ Error en verificación: {e}")
        return False

def create_launcher_script():
    """Crea script de lanzamiento"""
    print("\n🚀 Creando script de lanzamiento...")
    
    if os.name == 'nt':  # Windows
        launcher_content = f'''@echo off
cd /d "{Path.cwd()}"
python src\\main.py
pause
'''
        launcher_file = "ejecutar_dovela.bat"
    else:  # Unix/Linux/Mac
        launcher_content = f'''#!/bin/bash
cd "{Path.cwd()}"
python3 src/main.py
'''
        launcher_file = "ejecutar_dovela.sh"
    
    Path(launcher_file).write_text(launcher_content)
    
    if os.name != 'nt':
        # Hacer ejecutable en Unix
        os.chmod(launcher_file, 0o755)
    
    print(f"   ✅ {launcher_file}")

def main():
    """Función principal de configuración"""
    print("="*60)
    print("CONFIGURACIÓN DE DOVELA DIAMANTE PROFESSIONAL v2.0")
    print("="*60)
    
    # Verificar Python
    if not check_python_version():
        input("\nPresione Enter para salir...")
        sys.exit(1)
    
    # Instalar dependencias
    if not install_dependencies():
        print("\n❌ Error en instalación de dependencias")
        input("Presione Enter para salir...")
        sys.exit(1)
    
    # Crear directorios
    create_directories()
    
    # Probar instalación
    if not test_installation():
        print("\n❌ Error en verificación")
        input("Presione Enter para salir...")
        sys.exit(1)
    
    # Crear launcher
    create_launcher_script()
    
    print("\n" + "="*60)
    print("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
    print("="*60)
    print("\nPara ejecutar la aplicación:")
    print("  Opción 1: python src/main.py")
    if os.name == 'nt':
        print("  Opción 2: Doble clic en ejecutar_dovela.bat")
    else:
        print("  Opción 2: ./ejecutar_dovela.sh")
    
    print("\nModos adicionales:")
    print("  Consola: python src/main.py console")
    print("  Tests:   python src/main.py test")
    
    input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()
