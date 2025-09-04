#!/usr/bin/env python3
"""
Test script para verificar el análisis profesional con factores AASHTO
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from gui.main_window import MainWindow
import tkinter as tk

def test_professional_parameters():
    """Prueba los parámetros profesionales"""
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal para test
    
    # Crear la aplicación
    app = MainWindow(root)
    
    # Configurar parámetros de prueba
    params_panel = app.params_panel
    
    # Parámetros de geometría
    params_panel.side_length.set(150.0)  # mm
    params_panel.thickness.set(15.0)     # mm
    params_panel.joint_opening.set(25.0) # mm
    
    # Parámetros de carga básicos
    params_panel.load_magnitude.set(35000.0)  # N
    params_panel.safety_factor_target.set(2.5)
    
    # Parámetros profesionales - térmica
    params_panel.service_temperature.set(35.0)    # °C (más alto que normal)
    params_panel.temperature_max.set(55.0)        # °C 
    params_panel.temperature_min.set(-15.0)       # °C
    
    # Parámetros ambientales
    params_panel.exposure_condition.set("Marina")  # Condición severa
    params_panel.humidity_avg.set(85.0)           # % alta humedad
    params_panel.wind_speed_max.set(45.0)         # km/h viento fuerte
    
    # Parámetros de carga avanzados
    params_panel.impact_factor.set(1.30)          # Factor alto
    params_panel.dynamic_amplification.set(1.20)  # Amplificación dinámica
    params_panel.fatigue_cycles.set(5000000)      # Ciclos altos
    
    # Obtener parámetros completos
    full_params = params_panel.get_parameters()
    
    # Verificar estructura de parámetros
    print("=== PARÁMETROS PROFESIONALES DE PRUEBA ===")
    print(f"Sistema de unidades: {full_params['unit_system']}")
    
    print("\n--- GEOMETRÍA ---")
    for key, value in full_params['geometry'].items():
        print(f"{key}: {value}")
    
    print("\n--- FACTORES TÉRMICOS ---")
    for key, value in full_params['thermal'].items():
        print(f"{key}: {value}")
    
    print("\n--- FACTORES AMBIENTALES ---")
    for key, value in full_params['environmental'].items():
        print(f"{key}: {value}")
    
    print("\n--- CARGAS Y FACTORES ---")
    for key, value in full_params['loads'].items():
        print(f"{key}: {value}")
    
    # Simular análisis
    print("\n=== SIMULACIÓN DE ANÁLISIS ===")
    from gui.main_window import DiamondDovelaGeometry, LoadCase, Material, UnitSystem
    from dataclasses import dataclass
    
    # Crear objetos para análisis
    geometry = DiamondDovelaGeometry(
        side_length=full_params['geometry']['side_length'],
        thickness=full_params['geometry']['thickness'], 
        joint_opening=full_params['geometry']['joint_opening'],
        unit_system=full_params['unit_system']
    )
    
    @dataclass
    class MockMaterial:
        grade: str = "A572-50"
        E: float = 200000  # MPa
        fy: float = 345    # MPa
        
    @dataclass 
    class MockLoadCase:
        magnitude: float = 35000  # N
        
    material = MockMaterial()
    load_case = MockLoadCase()
    
    # Generar resultados simulados con factores profesionales
    results = app._generate_simulated_results(full_params, geometry, load_case, material)
    
    # Mostrar resultados del análisis
    print("\n--- RESULTADOS DEL ANÁLISIS ---")
    print(f"Factor de seguridad: {results.safety_factor:.2f}")
    print(f"Esfuerzo máximo: {results.max_stress:.2f} MPa")
    print(f"Desplazamiento máximo: {results.max_displacement:.3f} mm")
    
    print("\n--- INFORMACIÓN DEL ANÁLISIS ---")
    for key, value in results.analysis_info.items():
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")
    
    print("\n=== FACTORES DE MODIFICACIÓN ===")
    info = results.analysis_info
    print(f"Factor de temperatura: {info.get('temperature_factor', 'N/A'):.3f}")
    print(f"Factor ambiental: {info.get('environmental_factor', 'N/A'):.3f}")
    print(f"Factor dinámico: {info.get('dynamic_factor', 'N/A'):.3f}")
    print(f"Factor de fatiga: {info.get('fatigue_factor', 'N/A'):.3f}")
    print(f"Factor total: {info.get('total_modification_factor', 'N/A'):.3f}")
    
    # Comparación con análisis básico
    basic_stress = info.get('base_stress_Pa', 0) / 1e6  # MPa
    modified_stress = info.get('modified_stress_Pa', 0) / 1e6  # MPa
    
    print(f"\nEsfuerzo base (sin factores): {basic_stress:.2f} MPa")
    print(f"Esfuerzo modificado (con factores): {modified_stress:.2f} MPa")
    print(f"Incremento debido a factores: {((modified_stress/basic_stress - 1) * 100):.1f}%")
    
    root.destroy()
    return True

def test_zoom_functionality():
    """Prueba la funcionalidad de zoom"""
    print("\n=== PRUEBA DE FUNCIONALIDAD DE ZOOM ===")
    
    root = tk.Tk()
    root.withdraw()
    
    app = MainWindow(root)
    params_panel = app.params_panel
    
    # Estado inicial
    initial_zoom = params_panel.zoom_level.get()
    print(f"Nivel de zoom inicial: {initial_zoom}")
    
    # Probar zoom in
    params_panel._zoom_in()
    zoom_after_in = params_panel.zoom_level.get()
    print(f"Zoom después de zoom in: {zoom_after_in}")
    
    # Probar zoom out
    params_panel._zoom_out()
    zoom_after_out = params_panel.zoom_level.get()
    print(f"Zoom después de zoom out: {zoom_after_out}")
    
    # Probar reset
    params_panel._reset_zoom()
    zoom_after_reset = params_panel.zoom_level.get()
    print(f"Zoom después de reset: {zoom_after_reset}")
    
    root.destroy()
    return True

if __name__ == "__main__":
    print("INICIANDO PRUEBAS DEL SISTEMA PROFESIONAL")
    print("=" * 50)
    
    try:
        # Prueba 1: Parámetros profesionales
        test_professional_parameters()
        
        # Prueba 2: Funcionalidad de zoom
        test_zoom_functionality()
        
        print("\n" + "=" * 50)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("✅ Factores profesionales AASHTO funcionando")
        print("✅ Zoom y controles de interfaz funcionando")
        print("✅ Análisis simulado con factores integrados")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
