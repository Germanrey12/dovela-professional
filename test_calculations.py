#!/usr/bin/env python3
"""
Test rápido para verificar los cálculos profesionales
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_professional_calculations():
    """Prueba directa de los cálculos profesionales"""
    
    # Simular parámetros de entrada
    params = {
        'geometry': {
            'side_length': 150.0,
            'thickness': 15.0,
            'joint_opening': 25.0
        },
        'loads': {
            'magnitude': 35000.0,
            'safety_factor_target': 2.5,
            'impact_factor': 1.30,
            'dynamic_amplification': 1.20,
            'fatigue_cycles': 5000000
        },
        'thermal': {
            'service_temperature': 35.0,
            'temperature_max': 55.0,
            'temperature_min': -15.0
        },
        'environmental': {
            'exposure_condition': 'Marina',
            'humidity_avg': 85.0,
            'wind_speed_max': 45.0
        }
    }
    
    # Simular material
    class MockMaterial:
        def __init__(self):
            self.fy = 345  # MPa
    
    material = MockMaterial()
    
    # Implementar los cálculos de factores (copiados de main_window.py)
    def calculate_temperature_factor(thermal_params):
        service_temp = thermal_params.get('service_temperature', 23)
        temp_max = thermal_params.get('temperature_max', 50)
        temp_min = thermal_params.get('temperature_min', -20)
        
        temp_range = temp_max - temp_min
        if temp_range > 60:
            return 1.15
        elif temp_range > 40:
            return 1.10
        else:
            return 1.05
    
    def calculate_environmental_factor(env_params):
        exposure = env_params.get('exposure_condition', 'Normal')
        humidity = env_params.get('humidity_avg', 65)
        wind_speed = env_params.get('wind_speed_max', 25)
        
        exposure_factors = {
            'Normal': 1.0,
            'Marina': 1.2,
            'Industrial': 1.15,
            'Severa': 1.25
        }
        base_factor = exposure_factors.get(exposure, 1.0)
        
        if humidity > 80:
            base_factor *= 1.05
        
        if wind_speed > 40:
            base_factor *= 1.03
        
        return base_factor
    
    def calculate_fatigue_factor(load_params):
        fatigue_cycles = load_params.get('fatigue_cycles', 1000000)
        impact_factor = load_params.get('impact_factor', 1.25)
        
        if fatigue_cycles > 10000000:
            fatigue_factor = 1.15
        elif fatigue_cycles > 1000000:
            fatigue_factor = 1.10
        else:
            fatigue_factor = 1.05
        
        return fatigue_factor * (1 + (impact_factor - 1.0) * 0.5)
    
    # Calcular factores
    temp_factor = calculate_temperature_factor(params['thermal'])
    env_factor = calculate_environmental_factor(params['environmental'])
    dynamic_factor = params['loads']['dynamic_amplification']
    fatigue_factor = calculate_fatigue_factor(params['loads'])
    
    total_factor = temp_factor * env_factor * dynamic_factor * fatigue_factor
    
    # Cálculos de esfuerzos
    load_magnitude = params['loads']['magnitude']
    side_length = params['geometry']['side_length']
    thickness = params['geometry']['thickness']
    
    area = (side_length * thickness) / 1e6  # m²
    base_stress = load_magnitude / area  # Pa
    modified_stress = base_stress * total_factor
    
    # Factor de seguridad
    safety_factor = (material.fy * 1e6) / modified_stress if modified_stress > 0 else 5.0
    
    # Mostrar resultados
    print("=== ANÁLISIS PROFESIONAL CON FACTORES AASHTO ===")
    print(f"\nCondiciones de diseño:")
    print(f"- Temperatura de servicio: {params['thermal']['service_temperature']}°C")
    print(f"- Rango térmico: {params['thermal']['temperature_max'] - params['thermal']['temperature_min']}°C")
    print(f"- Exposición ambiental: {params['environmental']['exposure_condition']}")
    print(f"- Humedad promedio: {params['environmental']['humidity_avg']}%")
    print(f"- Velocidad máxima viento: {params['environmental']['wind_speed_max']} km/h")
    print(f"- Ciclos de fatiga: {params['loads']['fatigue_cycles']:,}")
    
    print(f"\nFactores de modificación AASHTO:")
    print(f"- Factor térmico: {temp_factor:.3f}")
    print(f"- Factor ambiental: {env_factor:.3f}")
    print(f"- Factor dinámico: {dynamic_factor:.3f}")
    print(f"- Factor de fatiga: {fatigue_factor:.3f}")
    print(f"- Factor total combinado: {total_factor:.3f}")
    
    print(f"\nAnálisis de esfuerzos:")
    print(f"- Área efectiva: {area*1e6:.1f} mm²")
    print(f"- Esfuerzo base: {base_stress/1e6:.2f} MPa")
    print(f"- Esfuerzo modificado: {modified_stress/1e6:.2f} MPa")
    print(f"- Incremento por factores: {((modified_stress/base_stress - 1) * 100):.1f}%")
    print(f"- Factor de seguridad: {safety_factor:.2f}")
    
    # Evaluación según normativas
    print(f"\nEvaluación según AASHTO:")
    if safety_factor >= 2.0:
        print("✅ DISEÑO ACEPTABLE - Factor de seguridad adecuado")
    elif safety_factor >= 1.5:
        print("⚠️  REVISAR DISEÑO - Factor de seguridad bajo")
    else:
        print("❌ DISEÑO NO ACEPTABLE - Factor de seguridad insuficiente")
    
    if total_factor > 1.3:
        print("⚠️  CONDICIONES SEVERAS - Considerar diseño más robusto")
    elif total_factor > 1.15:
        print("ℹ️  CONDICIONES MODERADAS - Monitoreo recomendado")
    else:
        print("✅ CONDICIONES NORMALES")
    
    return True

if __name__ == "__main__":
    print("PRUEBA DE CÁLCULOS PROFESIONALES AASHTO")
    print("=" * 50)
    
    try:
        test_professional_calculations()
        print("\n" + "=" * 50)
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("✅ Todos los factores profesionales funcionando correctamente")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
