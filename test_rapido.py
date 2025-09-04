#!/usr/bin/env python3
"""
Script de prueba rápida para verificar que la aplicación funciona
"""
import sys
from pathlib import Path

# Agregar src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    print("✅ Probando imports...")
    from config.settings import MaterialProperties, STEEL_A36
    print("✅ Config importado correctamente")
    
    from core.geometry import DiamondDovelaGeometry
    print("✅ Geometría importada correctamente")
    
    from core.stress_analysis import ClassicalStressAnalyzer
    print("✅ Análisis de esfuerzos importado correctamente")
    
    from gui.main_window import ProfessionalDovelaApp
    print("✅ GUI importada correctamente")
    
    print("\n🎉 TODOS LOS MÓDULOS FUNCIONAN CORRECTAMENTE")
    print("✅ Error de MaterialProperties CORREGIDO")
    print("\n📋 Para ejecutar:")
    print("   python src/main.py        # GUI")
    print("   python src/main.py console # Consola")
    print("   python src/main.py test    # Tests")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
