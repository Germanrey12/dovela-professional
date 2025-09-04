"""
Paquete principal para el análisis profesional de dovelas diamante

Este paquete contiene todos los módulos para el análisis de esfuerzos,
validación de diseño y visualización de resultados según normas AASHTO.

Módulos principales:
- config: Configuración y constantes de materiales
- core: Funcionalidades centrales (geometría, análisis de esfuerzos, FEA)
- gui: Interfaz gráfica de usuario
- utils: Utilidades (logging, validación, conversión de unidades)

Versión: 2.0
Autor: Ingeniería Estructural Avanzada
"""

__version__ = "2.0.0"
__author__ = "Ingeniería Estructural Avanzada"
__email__ = "soporte@dovela-diamante.com"

# Imports principales para facilitar uso del paquete
from .config.settings import (
    DEFAULT_SETTINGS,
    STEEL_A36,
    STEEL_A572_50,
    UnitSystem,
    MaterialGrade
)

from .core.geometry import (
    DiamondDovelaGeometry,
    Point2D,
    GeometryFactory
)

from .core.stress_analysis import (
    ClassicalStressAnalyzer,
    AASHTOStressAnalyzer,
    LoadCase,
    LoadType,
    StressResults
)

from .utils.unit_converter import (
    ProfessionalUnitConverter,
    ParameterWithUnits,
    StandardParameters
)

from .utils.validators import (
    DovelaValidator,
    ValidationResult,
    ValidationSeverity
)

# Información del paquete
__all__ = [
    # Configuración
    'DEFAULT_SETTINGS',
    'STEEL_A36',
    'STEEL_A572_50',
    'UnitSystem',
    'MaterialGrade',
    
    # Geometría
    'DiamondDovelaGeometry',
    'Point2D',
    'GeometryFactory',
    
    # Análisis de esfuerzos
    'ClassicalStressAnalyzer',
    'AASHTOStressAnalyzer',
    'LoadCase',
    'LoadType',
    'StressResults',
    
    # Utilidades
    'ProfessionalUnitConverter',
    'ParameterWithUnits',
    'StandardParameters',
    'DovelaValidator',
    'ValidationResult',
    'ValidationSeverity'
]
