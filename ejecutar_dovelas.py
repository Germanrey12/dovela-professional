#!/usr/bin/env python3
"""
EJECUTAR APLICACIÓN DE DOVELAS DIAMANTE
======================================

Aplicación profesional para análisis de dovelas diamante v2.0
- Análisis de esfuerzos von Mises
- Cumplimiento con códigos AASHTO
- Interfaz gráfica moderna
- Generación de reportes técnicos

INSTRUCCIONES:
1. Ejecutar: python ejecutar_dovelas.py
2. La aplicación se abrirá en una ventana
3. Usar los menús para todas las funciones

✅ TODAS LAS FUNCIONES ESTÁN IMPLEMENTADAS
✅ NO HAY MENSAJES "EN DESARROLLO"
✅ MENÚS COMPLETAMENTE FUNCIONALES
"""

import sys
import os
from pathlib import Path

# Configurar path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Ejecuta la aplicación principal"""
    
    print("🔧 ANÁLISIS DE DOVELAS DIAMANTE v2.0")
    print("="*50)
    print("🚀 Iniciando aplicación...")
    
    try:
        # Importar y ejecutar
        from src.main import main as run_main_app
        run_main_app()
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("\n💡 Intentando método alternativo...")
        
        try:
            from src.gui.main_window import ProfessionalDovelaApp
            app = ProfessionalDovelaApp()
            print("✅ Aplicación cargada exitosamente")
            app.run()
            
        except Exception as e2:
            print(f"❌ Error al ejecutar aplicación: {e2}")
            print("\n🔍 Información del error:")
            import traceback
            traceback.print_exc()
            input("\nPresione Enter para cerrar...")
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresione Enter para cerrar...")

if __name__ == "__main__":
    main()
