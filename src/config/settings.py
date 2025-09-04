"""
Configuración profesional para análisis de dovelas diamante
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
import os


class UnitSystem(Enum):
    """Sistema de unidades soportado"""
    METRIC = "metric"
    IMPERIAL = "imperial"


class MaterialGrade(Enum):
    """Grados de acero estándar"""
    A36 = "A36"
    A572_50 = "A572-50"
    A588 = "A588"
    CUSTOM = "CUSTOM"


@dataclass
class AnalysisSettings:
    """Configuración global del análisis FEA"""
    
    # Configuración de malla
    mesh_refinement: int = 3
    convergence_tolerance: float = 1e-6
    max_iterations: int = 1000
    
    # Sistema de unidades
    unit_system: UnitSystem = UnitSystem.METRIC
    
    # Configuración de visualización
    contour_levels: int = 30
    colormap: str = "viridis"
    figure_dpi: int = 300
    figure_size: tuple = (16, 12)
    
    # Límites de seguridad según AASHTO
    max_stress_ratio: float = 0.6  # Fracción de fy
    min_safety_factor: float = 2.0
    
    # Configuración de exportación
    output_format: str = "both"  # "metric", "imperial", "both"
    export_csv: bool = True
    export_pdf_report: bool = True
    
    # Directorios
    output_dir: str = "results"
    log_dir: str = "logs"
    
    def __post_init__(self):
        """Validación post-inicialización"""
        if self.mesh_refinement < 1 or self.mesh_refinement > 5:
            raise ValueError("mesh_refinement debe estar entre 1 y 5")
        
        if self.min_safety_factor < 1.5:
            raise ValueError("Factor de seguridad mínimo debe ser ≥ 1.5")
        
        # Crear directorios si no existen
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)


@dataclass
class MaterialProperties:
    """Propiedades del material con validación según normas"""
    
    # Propiedades mecánicas básicas
    E: float  # Módulo de elasticidad [MPa o ksi]
    nu: float  # Relación de Poisson
    fy: float  # Límite elástico [MPa o psi]
    fu: float  # Resistencia última [MPa o psi]
    
    # Identificación
    grade: MaterialGrade = MaterialGrade.A36
    description: str = "Acero estructural"
    
    # Propiedades adicionales
    density: float = 7850  # kg/m³ para acero
    thermal_expansion: float = 12e-6  # /°C
    
    def __post_init__(self):
        """Validación según normas ASTM/AASHTO"""
        if self.grade == MaterialGrade.A36:
            self._validate_A36()
        elif self.grade == MaterialGrade.A572_50:
            self._validate_A572()
    
    def _validate_A36(self):
        """Valida propiedades para ASTM A36"""
        if not 190000 <= self.E <= 210000:  # MPa
            raise ValueError("Módulo E para A36 debe estar entre 190-210 GPa")
        
        if not 0.25 <= self.nu <= 0.35:
            raise ValueError("Poisson para acero debe estar entre 0.25-0.35")
        
        if self.fy < 250:  # MPa
            raise ValueError("fy para A36 debe ser ≥ 250 MPa")
    
    def _validate_A572(self):
        """Valida propiedades para ASTM A572 Grado 50"""
        if self.fy < 345:  # MPa
            raise ValueError("fy para A572-50 debe ser ≥ 345 MPa")


@dataclass  
class GeometryLimits:
    """Límites geométricos según AASHTO 14.5.1"""
    
    # Límites de dovela diamante [mm]
    min_side_mm: float = 100
    max_side_mm: float = 200
    min_thickness_mm: float = 6
    max_thickness_mm: float = 50
    
    # Límites de apertura de junta
    max_joint_opening_ratio: float = 0.1  # 10% del lado
    
    # Límites de carga [kN]
    max_design_load_kN: float = 1000  # Aumentado para permitir cargas mayores
    
    def validate_geometry(self, side_mm: float, thickness_mm: float, 
                         joint_opening_mm: float) -> None:
        """Valida geometría según AASHTO"""
        
        if not self.min_side_mm <= side_mm <= self.max_side_mm:
            raise ValueError(
                f"Lado debe estar entre {self.min_side_mm}-{self.max_side_mm} mm"
            )
        
        if not self.min_thickness_mm <= thickness_mm <= self.max_thickness_mm:
            raise ValueError(
                f"Espesor debe estar entre {self.min_thickness_mm}-{self.max_thickness_mm} mm"
            )
        
        max_joint = side_mm * self.max_joint_opening_ratio
        if joint_opening_mm > max_joint:
            raise ValueError(
                f"Apertura de junta no debe exceder {max_joint:.1f} mm "
                f"({self.max_joint_opening_ratio*100}% del lado)"
            )


# Configuración por defecto
DEFAULT_SETTINGS = AnalysisSettings()

# Materiales estándar
STEEL_A36 = MaterialProperties(
    E=200000,  # MPa
    nu=0.3,
    fy=250,    # MPa
    fu=400,    # MPa
    grade=MaterialGrade.A36,
    description="ASTM A36 - Acero estructural carbono"
)

STEEL_A572_50 = MaterialProperties(
    E=200000,  # MPa
    nu=0.3,
    fy=345,    # MPa  
    fu=450,    # MPa
    grade=MaterialGrade.A572_50,
    description="ASTM A572 Grado 50 - Acero alta resistencia"
)

# Límites geométricos por defecto
DEFAULT_GEOMETRY_LIMITS = GeometryLimits()
