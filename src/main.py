"""
Aplicación principal - Punto de entrada para el análisis de dovelas diamante
Integra todos los módulos profesionales
"""
import sys
import os
import logging
import traceback
from pathlib import Path
from typing import Optional

# Agregar src al path para imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

# Configurar logging antes de otros imports
from utils.logging_config import setup_professional_logging

def configure_application():
    """Configura la aplicación antes del inicio"""
    
    # Configurar logging
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    setup_professional_logging(
        log_dir=str(log_dir),
        app_name="dovela_professional"
    )
    
    logger = logging.getLogger('dovela.main')
    logger.info("="*60)
    logger.info("INICIANDO APLICACIÓN DE ANÁLISIS DE DOVELAS DIAMANTE")
    logger.info("="*60)
    
    # Verificar dependencias críticas
    missing_deps = check_dependencies()
    if missing_deps:
        logger.error(f"Dependencias faltantes: {missing_deps}")
        return False
    
    logger.info("Todas las dependencias están disponibles")
    return True

def check_dependencies() -> list:
    """Verifica dependencias críticas de la aplicación"""
    
    missing = []
    
    # Dependencias requeridas
    required_modules = [
        ('numpy', 'np'),
        ('matplotlib', 'plt'), 
        ('tkinter', 'tk'),
        ('scipy', 'scipy'),
        ('pathlib', 'Path')
    ]
    
    for module_name, import_as in required_modules:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(module_name)
    
    # Dependencias opcionales (para FEA)
    optional_modules = [
        'skfem'
    ]
    
    logger = logging.getLogger('dovela.dependencies')
    
    for module_name in optional_modules:
        try:
            __import__(module_name)
            logger.info(f"Módulo opcional '{module_name}' disponible")
        except ImportError:
            logger.warning(f"Módulo opcional '{module_name}' no disponible - funcionalidad FEA limitada")
    
    return missing

def main():
    """Función principal de la aplicación"""
    
    # Configurar aplicación
    if not configure_application():
        print("ERROR: No se pudo configurar la aplicación correctamente")
        input("Presione Enter para salir...")
        sys.exit(1)
    
    logger = logging.getLogger('dovela.main')
    
    try:
        # Importar y ejecutar aplicación principal
        logger.info("Cargando interfaz gráfica...")
        
        from gui.main_window import ProfessionalDovelaApp
        
        logger.info("Inicializando aplicación...")
        app = ProfessionalDovelaApp()
        
        logger.info("Ejecutando aplicación...")
        app.run()
        
        logger.info("Aplicación cerrada correctamente")
        
    except ImportError as e:
        error_msg = f"Error al importar módulos: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        print(f"ERROR: {error_msg}")
        print("\nVerifique que todos los módulos estén correctamente instalados.")
        print("\nTraceback completo:")
        traceback.print_exc()
        
        input("\nPresione Enter para salir...")
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Error fatal en aplicación: {str(e)}"
        logger.critical(error_msg, exc_info=True)
        
        print(f"ERROR FATAL: {error_msg}")
        print("\nConsulte el archivo de log para más detalles.")
        print("\nTraceback completo:")
        traceback.print_exc()
        
        input("\nPresione Enter para salir...")
        sys.exit(1)

def run_console_mode():
    """Ejecuta aplicación en modo consola (para testing/debugging)"""
    
    if not configure_application():
        print("ERROR: No se pudo configurar la aplicación")
        return
    
    logger = logging.getLogger('dovela.console')
    
    try:
        print("\n" + "="*60)
        print("ANÁLISIS DE DOVELAS DIAMANTE - MODO CONSOLA")
        print("="*60)
        
        # Importar módulos necesarios
        from config.settings import DEFAULT_SETTINGS, STEEL_A36, UnitSystem
        from core.geometry import DiamondDovelaGeometry, Point2D
        from core.stress_analysis import LoadCase, LoadType, ClassicalStressAnalyzer, StressType
        from utils.unit_converter import ParameterWithUnits
        from utils.validators import DovelaValidator
        
        print("\n✅ Módulos cargados correctamente")
        
        # Crear geometría de prueba
        print("\n📐 Creando geometría de prueba...")
        side_length = ParameterWithUnits(125.0, "mm", "Lado del diamante")
        thickness = ParameterWithUnits(12.7, "mm", "Espesor")
        joint_opening = ParameterWithUnits(4.8, "mm", "Apertura de junta")
        
        geometry = DiamondDovelaGeometry(
            side_length, thickness, joint_opening, UnitSystem.METRIC
        )
        
        print(f"   Geometría: Lado={side_length.format()}, Espesor={thickness.format()}")
        
        # Validar geometría
        print("\n✅ Validando geometría...")
        validator = DovelaValidator()
        validator.validate_geometry(
            side_length.value, thickness.value, joint_opening.value
        )
        
        if validator.get_validation_summary()['is_valid']:
            print("   ✅ Geometría válida")
        else:
            print("   ❌ Geometría inválida")
            validator.print_validation_report()
            return
        
        # Crear caso de carga
        print("\n⚡ Creando caso de carga...")
        load_magnitude = ParameterWithUnits(22.2, "kN", "Carga aplicada")
        load_case = LoadCase(
            magnitude=load_magnitude,
            load_type=LoadType.CONCENTRATED,
            application_point=Point2D(-50, 0),
            direction=Point2D(0, -1),
            description="Carga de prueba"
        )
        
        print(f"   Carga: {load_case.description} - {load_magnitude.format()}")
        
        # Ejecutar análisis básico
        print("\n🔧 Ejecutando análisis clásico...")
        analyzer = ClassicalStressAnalyzer()
        
        results = analyzer.analyze(geometry, load_case, STEEL_A36)
        
        print("\n📊 RESULTADOS DEL ANÁLISIS:")
        print("-" * 40)
        max_von_mises, _ = results.get_max_stress(StressType.VON_MISES)
        max_principal, _ = results.get_max_stress(StressType.PRINCIPAL_MAX)
        min_safety_factor, _ = results.get_min_safety_factor()
        print(f"von Mises máximo: {max_von_mises/1e6:.2f} MPa")
        print(f"Principal máximo: {max_principal/1e6:.2f} MPa")
        print(f"Factor de seguridad: {min_safety_factor:.2f}")
        print(f"Método usado: {results.analysis_info['method']}")
        
        # Verificar cumplimiento
        if min_safety_factor >= 2.0:
            print("\n✅ DISEÑO APROBADO - Factor de seguridad adecuado")
        else:
            print("\n❌ DISEÑO RECHAZADO - Factor de seguridad insuficiente")
        
        print("\n✅ Análisis completado exitosamente")
        
    except Exception as e:
        logger.error(f"Error en modo consola: {str(e)}", exc_info=True)
        print(f"\nERROR: {str(e)}")
        traceback.print_exc()

def run_validation_tests():
    """Ejecuta pruebas de validación de módulos"""
    
    if not configure_application():
        print("ERROR: No se pudo configurar la aplicación")
        return
    
    logger = logging.getLogger('dovela.validation')
    
    print("\n" + "="*60)
    print("PRUEBAS DE VALIDACIÓN DE MÓDULOS")
    print("="*60)
    
    tests = [
        ("Configuración", test_config_module),
        ("Logging", test_logging_module),
        ("Validadores", test_validators_module),
        ("Conversión de unidades", test_unit_converter_module),
        ("Geometría", test_geometry_module),
        ("Análisis de esfuerzos", test_stress_analysis_module)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Probando {test_name}...")
        try:
            test_func()
            print(f"   ✅ {test_name}: APROBADO")
            passed += 1
        except Exception as e:
            print(f"   ❌ {test_name}: FALLIDO - {str(e)}")
            logger.error(f"Test {test_name} falló: {str(e)}", exc_info=True)
    
    print(f"\n📈 RESUMEN: {passed}/{total} pruebas aprobadas")
    
    if passed == total:
        print("✅ TODOS LOS MÓDULOS FUNCIONAN CORRECTAMENTE")
    else:
        print("❌ ALGUNOS MÓDULOS PRESENTAN PROBLEMAS")

def test_config_module():
    """Prueba módulo de configuración"""
    from config.settings import DEFAULT_SETTINGS, STEEL_A36, UnitSystem
    assert DEFAULT_SETTINGS.unit_system == UnitSystem.METRIC
    assert STEEL_A36.E > 0
    assert STEEL_A36.fy > 0

def test_logging_module():
    """Prueba módulo de logging"""
    from utils.logging_config import AnalysisProgressLogger
    logger = AnalysisProgressLogger("test")
    logger.start_analysis("validation_test", total_steps=1)
    logger.log_step("Test step")
    logger.finish_analysis(True)

def test_validators_module():
    """Prueba módulo de validadores"""
    from utils.validators import DovelaValidator
    validator = DovelaValidator()
    validator.validate_geometry(125.0, 12.7, 4.8)
    summary = validator.get_validation_summary()
    assert summary['is_valid']

def test_unit_converter_module():
    """Prueba módulo de conversión de unidades"""
    from utils.unit_converter import ProfessionalUnitConverter, ParameterWithUnits
    converter = ProfessionalUnitConverter()
    
    param = ParameterWithUnits(125.0, "mm", "Test parameter")
    converted = param.convert_to("in")
    assert abs(converted.value - 4.921) < 0.01

def test_geometry_module():
    """Prueba módulo de geometría"""
    from core.geometry import DiamondDovelaGeometry, Point2D
    from utils.unit_converter import ParameterWithUnits
    from config.settings import UnitSystem
    
    side = ParameterWithUnits(125.0, "mm", "Lado")
    thickness = ParameterWithUnits(12.7, "mm", "Espesor")
    opening = ParameterWithUnits(4.8, "mm", "Apertura")
    
    geometry = DiamondDovelaGeometry(side, thickness, opening, UnitSystem.METRIC)
    points = geometry.get_boundary_points()
    assert len(points) > 0

def test_stress_analysis_module():
    """Prueba módulo de análisis de esfuerzos"""
    from core.stress_analysis import ClassicalStressAnalyzer, LoadCase, LoadType, StressType
    from core.geometry import DiamondDovelaGeometry, Point2D
    from utils.unit_converter import ParameterWithUnits
    from config.settings import UnitSystem, STEEL_A36
    
    # Crear geometría básica
    side = ParameterWithUnits(125.0, "mm", "Lado")
    thickness = ParameterWithUnits(12.7, "mm", "Espesor") 
    opening = ParameterWithUnits(4.8, "mm", "Apertura")
    geometry = DiamondDovelaGeometry(side, thickness, opening, UnitSystem.METRIC)
    
    # Crear carga básica
    magnitude = ParameterWithUnits(22.2, "kN", "Carga")
    load_case = LoadCase(
        magnitude=magnitude,
        load_type=LoadType.CONCENTRATED,
        application_point=Point2D(-50, 0),
        direction=Point2D(0, -1),
        description="Test load"
    )
    
    # Ejecutar análisis
    analyzer = ClassicalStressAnalyzer()
    results = analyzer.analyze(geometry, load_case, STEEL_A36)
    
    max_von_mises, _ = results.get_max_stress(StressType.VON_MISES)
    min_sf, _ = results.get_min_safety_factor()
    assert max_von_mises > 0
    assert min_sf > 0

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "console":
            run_console_mode()
        elif command == "test":
            run_validation_tests()
        elif command == "validate":
            run_validation_tests()
        else:
            print(f"Comando desconocido: {command}")
            print("Comandos disponibles:")
            print("  python main.py          - Ejecutar interfaz gráfica")
            print("  python main.py console  - Ejecutar en modo consola")
            print("  python main.py test     - Ejecutar pruebas de validación")
    else:
        # Modo por defecto: interfaz gráfica
        main()
