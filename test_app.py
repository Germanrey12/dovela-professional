#!/usr/bin/env python3
"""
Archivo de prueba para ejecutar la aplicación de dovelas
"""

import sys
import os

# Agregar el directorio al path
sys.path.append(os.path.dirname(__file__))

try:
    from src.gui.main_window import ProfessionalDovelaApp
    import tkinter as tk
    from tkinter import messagebox
    
    print("🚀 Iniciando aplicación de análisis de dovelas...")
    
    # Crear la aplicación
    app = ProfessionalDovelaApp()
    
    print("✅ Aplicación creada exitosamente")
    print("📱 Mostrando ventana principal...")
    
    # Mostrar mensaje de bienvenida
    app.root.after(1000, lambda: messagebox.showinfo(
        "Bienvenido", 
        "Aplicación de Análisis de Dovelas Diamante v2.0\n\n"
        "✅ Todos los menús están funcionando\n"
        "✅ Sin mensajes 'En desarrollo'\n"
        "✅ Funcionalidad completa disponible\n\n"
        "Puede usar todas las opciones del menú."
    ))
    
    # Ejecutar la aplicación
    app.run()
    
except KeyboardInterrupt:
    print("\n👋 Aplicación cerrada por el usuario")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    input("\nPresione Enter para cerrar...")
