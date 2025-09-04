"""
Sistema profesional de conversión de unidades para análisis de dovelas
"""
from dataclasses import dataclass
from typing import Union, Dict, Any
from enum import Enum
import logging
import os
import sys

# Manejo de imports para ejecución independiente
try:
    from ..config.settings import UnitSystem
except ImportError:
    # Si los imports relativos fallan, intentar imports absolutos
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from config.settings import UnitSystem


class UnitCategory(Enum):
    """Categorías de unidades"""
    LENGTH = "length"
    FORCE = "force"
    STRESS = "stress"
    MOMENT = "moment"
    AREA = "area"
    VOLUME = "volume"
    DENSITY = "density"


@dataclass
class UnitDefinition:
    """Definición de unidad con factor de conversión"""
    name: str
    symbol: str
    category: UnitCategory
    to_si_factor: float  # Factor para convertir a unidad SI base
    description: str


class ProfessionalUnitConverter:
    """Convertidor profesional de unidades para ingeniería estructural"""
    
    def __init__(self):
        self.logger = logging.getLogger('dovela.units')
        self._setup_unit_definitions()
    
    def _setup_unit_definitions(self):
        """Configura definiciones de unidades"""
        
        # Definiciones de unidades
        self.units = {
            # LONGITUD (base: metros)
            'mm': UnitDefinition('milímetro', 'mm', UnitCategory.LENGTH, 0.001, 'Milímetro'),
            'cm': UnitDefinition('centímetro', 'cm', UnitCategory.LENGTH, 0.01, 'Centímetro'),
            'm': UnitDefinition('metro', 'm', UnitCategory.LENGTH, 1.0, 'Metro (SI base)'),
            'in': UnitDefinition('pulgada', 'in', UnitCategory.LENGTH, 0.0254, 'Pulgada'),
            'ft': UnitDefinition('pie', 'ft', UnitCategory.LENGTH, 0.3048, 'Pie'),
            
            # FUERZA (base: Newtons)
            'N': UnitDefinition('newton', 'N', UnitCategory.FORCE, 1.0, 'Newton (SI base)'),
            'kN': UnitDefinition('kilonewton', 'kN', UnitCategory.FORCE, 1000.0, 'Kilonewton'),
            'lbf': UnitDefinition('libra-fuerza', 'lbf', UnitCategory.FORCE, 4.44822, 'Libra-fuerza'),
            'kip': UnitDefinition('kip', 'kip', UnitCategory.FORCE, 4448.22, 'Kip (1000 lbf)'),
            'ton': UnitDefinition('tonelada-fuerza', 'ton', UnitCategory.FORCE, 8896.44, 'Tonelada-fuerza métrica'),
            
            # ESFUERZO (base: Pascals)
            'Pa': UnitDefinition('pascal', 'Pa', UnitCategory.STRESS, 1.0, 'Pascal (SI base)'),
            'kPa': UnitDefinition('kilopascal', 'kPa', UnitCategory.STRESS, 1000.0, 'Kilopascal'),
            'MPa': UnitDefinition('megapascal', 'MPa', UnitCategory.STRESS, 1e6, 'Megapascal'),
            'GPa': UnitDefinition('gigapascal', 'GPa', UnitCategory.STRESS, 1e9, 'Gigapascal'),
            'psi': UnitDefinition('libras por pulgada cuadrada', 'psi', UnitCategory.STRESS, 6894.76, 'PSI'),
            'ksi': UnitDefinition('kips por pulgada cuadrada', 'ksi', UnitCategory.STRESS, 6.89476e6, 'KSI'),
            
            # ÁREA (base: metros cuadrados)
            'mm2': UnitDefinition('milímetro cuadrado', 'mm²', UnitCategory.AREA, 1e-6, 'Milímetro cuadrado'),
            'cm2': UnitDefinition('centímetro cuadrado', 'cm²', UnitCategory.AREA, 1e-4, 'Centímetro cuadrado'),
            'm2': UnitDefinition('metro cuadrado', 'm²', UnitCategory.AREA, 1.0, 'Metro cuadrado (SI base)'),
            'in2': UnitDefinition('pulgada cuadrada', 'in²', UnitCategory.AREA, 0.00064516, 'Pulgada cuadrada'),
            'ft2': UnitDefinition('pie cuadrado', 'ft²', UnitCategory.AREA, 0.092903, 'Pie cuadrado'),
            
            # DENSIDAD (base: kg/m³)
            'kg_m3': UnitDefinition('kilogramo por metro cúbico', 'kg/m³', UnitCategory.DENSITY, 1.0, 'Densidad SI'),
            'lb_ft3': UnitDefinition('libra por pie cúbico', 'lb/ft³', UnitCategory.DENSITY, 16.0185, 'Densidad imperial'),
        }
        
        # Sistemas de unidades estándar
        self.unit_systems = {
            UnitSystem.METRIC: {
                UnitCategory.LENGTH: 'mm',
                UnitCategory.FORCE: 'kN',
                UnitCategory.STRESS: 'MPa',
                UnitCategory.AREA: 'mm2',
                UnitCategory.DENSITY: 'kg_m3'
            },
            UnitSystem.IMPERIAL: {
                UnitCategory.LENGTH: 'in',
                UnitCategory.FORCE: 'kip',
                UnitCategory.STRESS: 'ksi',
                UnitCategory.AREA: 'in2',
                UnitCategory.DENSITY: 'lb_ft3'
            }
        }
    
    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        """
        Convierte valor entre unidades
        
        Args:
            value: Valor a convertir
            from_unit: Unidad origen
            to_unit: Unidad destino
            
        Returns:
            Valor convertido
            
        Raises:
            ValueError: Si las unidades no son compatibles
        """
        if from_unit == to_unit:
            return value
        
        if from_unit not in self.units:
            raise ValueError(f"Unidad origen '{from_unit}' no reconocida")
        
        if to_unit not in self.units:
            raise ValueError(f"Unidad destino '{to_unit}' no reconocida")
        
        from_def = self.units[from_unit]
        to_def = self.units[to_unit]
        
        if from_def.category != to_def.category:
            raise ValueError(
                f"Unidades incompatibles: {from_def.category.value} -> {to_def.category.value}"
            )
        
        # Convertir a SI base, luego a unidad destino
        si_value = value * from_def.to_si_factor
        result = si_value / to_def.to_si_factor
        
        self.logger.debug(f"Conversión: {value} {from_unit} = {result:.6f} {to_unit}")
        
        return result
    
    def convert_to_system(self, value: float, from_unit: str, 
                         target_system: UnitSystem) -> tuple[float, str]:
        """
        Convierte valor al sistema de unidades especificado
        
        Args:
            value: Valor a convertir
            from_unit: Unidad origen
            target_system: Sistema de unidades destino
            
        Returns:
            Tupla (valor_convertido, unidad_destino)
        """
        if from_unit not in self.units:
            raise ValueError(f"Unidad '{from_unit}' no reconocida")
        
        from_def = self.units[from_unit]
        category = from_def.category
        
        if category not in self.unit_systems[target_system]:
            raise ValueError(f"Categoría {category.value} no definida para sistema {target_system.value}")
        
        target_unit = self.unit_systems[target_system][category]
        converted_value = self.convert(value, from_unit, target_unit)
        
        return converted_value, target_unit
    
    def get_unit_info(self, unit: str) -> UnitDefinition:
        """Obtiene información de una unidad"""
        if unit not in self.units:
            raise ValueError(f"Unidad '{unit}' no reconocida")
        return self.units[unit]
    
    def list_units_by_category(self, category: UnitCategory) -> Dict[str, UnitDefinition]:
        """Lista todas las unidades de una categoría"""
        return {
            unit_key: unit_def 
            for unit_key, unit_def in self.units.items() 
            if unit_def.category == category
        }
    
    def format_value_with_units(self, value: float, unit: str, 
                               precision: int = 3, scientific: bool = False) -> str:
        """
        Formatea valor con unidades para presentación
        
        Args:
            value: Valor numérico
            unit: Unidad
            precision: Dígitos de precisión
            scientific: Usar notación científica si es necesario
            
        Returns:
            String formateado
        """
        if unit not in self.units:
            return f"{value:.{precision}f} {unit}"
        
        unit_def = self.units[unit]
        
        # Usar notación científica para valores muy grandes o pequeños
        if scientific or abs(value) >= 10**6 or (abs(value) < 10**(-2) and abs(value) > 0):
            formatted_value = f"{value:.{precision}e}"
        else:
            formatted_value = f"{value:.{precision}f}"
        
        return f"{formatted_value} {unit_def.symbol}"


@dataclass
class ParameterWithUnits:
    """Parámetro con unidades explícitas"""
    value: float
    unit: str
    description: str = ""
    
    def __post_init__(self):
        """Validación post-inicialización"""
        self.converter = ProfessionalUnitConverter()
        if self.unit not in self.converter.units:
            raise ValueError(f"Unidad '{self.unit}' no reconocida")
    
    def convert_to(self, target_unit: str) -> 'ParameterWithUnits':
        """Convierte a otra unidad"""
        new_value = self.converter.convert(self.value, self.unit, target_unit)
        return ParameterWithUnits(new_value, target_unit, self.description)
    
    def to_system(self, target_system: UnitSystem) -> 'ParameterWithUnits':
        """Convierte al sistema de unidades especificado"""
        new_value, new_unit = self.converter.convert_to_system(
            self.value, self.unit, target_system
        )
        return ParameterWithUnits(new_value, new_unit, self.description)
    
    def format(self, precision: int = 3) -> str:
        """Formatea para presentación"""
        return self.converter.format_value_with_units(
            self.value, self.unit, precision
        )
    
    def __str__(self) -> str:
        return self.format()


class StandardParameters:
    """Parámetros estándar con unidades para dovelas diamante"""
    
    @staticmethod
    def create_load_parameter(value: float, system: UnitSystem) -> ParameterWithUnits:
        """Crea parámetro de carga en el sistema especificado"""
        unit = 'kN' if system == UnitSystem.METRIC else 'kip'
        return ParameterWithUnits(value, unit, "Carga aplicada")
    
    @staticmethod
    def create_dimension_parameter(value: float, system: UnitSystem, 
                                 description: str = "Dimensión") -> ParameterWithUnits:
        """Crea parámetro dimensional en el sistema especificado"""
        unit = 'mm' if system == UnitSystem.METRIC else 'in'
        return ParameterWithUnits(value, unit, description)
    
    @staticmethod
    def create_stress_parameter(value: float, system: UnitSystem) -> ParameterWithUnits:
        """Crea parámetro de esfuerzo en el sistema especificado"""
        unit = 'MPa' if system == UnitSystem.METRIC else 'ksi'
        return ParameterWithUnits(value, unit, "Esfuerzo")
    
    @staticmethod
    def create_elastic_modulus(material_grade: str, system: UnitSystem) -> ParameterWithUnits:
        """Crea módulo elástico estándar según grado de material"""
        if system == UnitSystem.METRIC:
            value, unit = 200000, 'MPa'  # Típico para acero
        else:
            value, unit = 29000, 'ksi'   # Típico para acero
        
        return ParameterWithUnits(value, unit, f"Módulo elástico - {material_grade}")


# Instancia global del convertidor
unit_converter = ProfessionalUnitConverter()
