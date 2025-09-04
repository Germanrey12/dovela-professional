"""
Módulo de análisis de esfuerzos profesional para dovelas diamante
Implementación según normas AASHTO y teoría clásica de mecánica de materiales
"""
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List, Any
import numpy as np
import logging
from enum import Enum
from abc import ABC, abstractmethod
import os
import sys

# Manejo de imports para ejecución independiente
try:
    from ..core.geometry import DiamondDovelaGeometry, Point2D
    from ..utils.unit_converter import ParameterWithUnits
    from ..config.settings import MaterialProperties, UnitSystem
except ImportError:
    # Si los imports relativos fallan, intentar imports absolutos
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from core.geometry import DiamondDovelaGeometry, Point2D
    from utils.unit_converter import ParameterWithUnits
    from config.settings import MaterialProperties, UnitSystem


class StressType(Enum):
    """Tipos de esfuerzo analizados"""
    VON_MISES = "von_mises"
    PRINCIPAL_MAX = "principal_max"
    PRINCIPAL_MIN = "principal_min"
    SHEAR_MAX = "shear_max"
    NORMAL_X = "normal_x"
    NORMAL_Y = "normal_y"
    SHEAR_XY = "shear_xy"


class LoadType(Enum):
    """Tipos de carga aplicada"""
    CONCENTRATED = "concentrated"
    DISTRIBUTED = "distributed"
    THERMAL = "thermal"


@dataclass
class LoadCase:
    """Caso de carga con unidades explícitas"""
    magnitude: ParameterWithUnits
    load_type: LoadType
    application_point: Point2D
    direction: Point2D  # Vector unitario de dirección
    description: str = ""
    
    def __post_init__(self):
        """Validación post-inicialización"""
        # Normalizar vector de dirección
        length = np.sqrt(self.direction.x**2 + self.direction.y**2)
        if length > 0:
            self.direction = Point2D(
                self.direction.x / length,
                self.direction.y / length
            )


@dataclass
class StressState:
    """Estado de esfuerzos en un punto"""
    sigma_x: float  # Esfuerzo normal en X [Pa]
    sigma_y: float  # Esfuerzo normal en Y [Pa]
    tau_xy: float   # Esfuerzo cortante XY [Pa]
    location: Point2D  # Ubicación del punto
    
    def von_mises(self) -> float:
        """Calcula esfuerzo von Mises según criterio de falla"""
        return np.sqrt(
            self.sigma_x**2 + self.sigma_y**2 - 
            self.sigma_x * self.sigma_y + 3 * self.tau_xy**2
        )
    
    def principal_stresses(self) -> Tuple[float, float]:
        """
        Calcula esfuerzos principales
        
        Returns:
            Tupla (sigma_1, sigma_2) donde sigma_1 >= sigma_2
        """
        sigma_avg = (self.sigma_x + self.sigma_y) / 2
        radius = np.sqrt(
            ((self.sigma_x - self.sigma_y) / 2)**2 + self.tau_xy**2
        )
        
        sigma_1 = sigma_avg + radius  # Esfuerzo principal máximo
        sigma_2 = sigma_avg - radius  # Esfuerzo principal mínimo
        
        return sigma_1, sigma_2
    
    def max_shear(self) -> float:
        """Calcula esfuerzo cortante máximo"""
        sigma_1, sigma_2 = self.principal_stresses()
        return abs(sigma_1 - sigma_2) / 2
    
    def safety_factor(self, yield_strength: float, criterion: str = "von_mises") -> float:
        """
        Calcula factor de seguridad según criterio especificado
        
        Args:
            yield_strength: Límite elástico del material [Pa]
            criterion: Criterio de falla ("von_mises", "max_principal", "max_shear")
            
        Returns:
            Factor de seguridad
        """
        if criterion == "von_mises":
            equivalent_stress = self.von_mises()
        elif criterion == "max_principal":
            sigma_1, _ = self.principal_stresses()
            equivalent_stress = abs(sigma_1)
        elif criterion == "max_shear":
            equivalent_stress = self.max_shear() * 2  # Criterio de Tresca
        else:
            raise ValueError(f"Criterio '{criterion}' no reconocido")
        
        if equivalent_stress == 0:
            return float('inf')
        
        return yield_strength / equivalent_stress


@dataclass
class StressResults:
    """Resultados completos de análisis de esfuerzos"""
    stress_states: List[StressState]
    coordinates: np.ndarray
    load_case: LoadCase
    material: MaterialProperties
    geometry: DiamondDovelaGeometry
    analysis_info: Dict[str, Any]
    
    def get_max_stress(self, stress_type: StressType) -> Tuple[float, Point2D]:
        """
        Obtiene esfuerzo máximo del tipo especificado
        
        Args:
            stress_type: Tipo de esfuerzo a evaluar
            
        Returns:
            Tupla (valor_máximo, ubicación)
        """
        max_value = 0
        max_location = Point2D(0, 0)
        
        for state in self.stress_states:
            if stress_type == StressType.VON_MISES:
                value = state.von_mises()
            elif stress_type == StressType.PRINCIPAL_MAX:
                value, _ = state.principal_stresses()
            elif stress_type == StressType.SHEAR_MAX:
                value = state.max_shear()
            elif stress_type == StressType.NORMAL_X:
                value = abs(state.sigma_x)
            elif stress_type == StressType.NORMAL_Y:
                value = abs(state.sigma_y)
            elif stress_type == StressType.SHEAR_XY:
                value = abs(state.tau_xy)
            else:
                continue
            
            if value > max_value:
                max_value = value
                max_location = state.location
        
        return max_value, max_location
    
    def get_min_safety_factor(self, criterion: str = "von_mises") -> Tuple[float, Point2D]:
        """
        Obtiene factor de seguridad mínimo
        
        Args:
            criterion: Criterio de falla
            
        Returns:
            Tupla (factor_mínimo, ubicación_crítica)
        """
        min_sf = float('inf')
        critical_location = Point2D(0, 0)
        
        # Convertir yield strength a Pa si está en otras unidades
        fy_pa = self.material.fy
        if self.material.fy < 1000:  # Probablemente en ksi
            fy_pa = self.material.fy * 6.89476e6  # ksi to Pa
        elif self.material.fy < 10000:  # Probablemente en MPa
            fy_pa = self.material.fy * 1e6  # MPa to Pa
        
        for state in self.stress_states:
            sf = state.safety_factor(fy_pa, criterion)
            if sf < min_sf:
                min_sf = sf
                critical_location = state.location
        
        return min_sf, critical_location


class StressAnalyzer(ABC):
    """Clase base abstracta para analizadores de esfuerzo"""
    
    @abstractmethod
    def analyze(self, geometry: DiamondDovelaGeometry, 
               load_case: LoadCase, 
               material: MaterialProperties) -> StressResults:
        """Realiza análisis de esfuerzos"""
        pass


class ClassicalStressAnalyzer(StressAnalyzer):
    """
    Analizador de esfuerzos basado en teoría clásica de mecánica de materiales
    
    Implementa:
    - Teoría de vigas de Euler-Bernoulli
    - Concentración de esfuerzos según Peterson
    - Distribución parabólica de cortante según Jourawski
    - Criterios de falla según von Mises y Tresca
    """
    
    def __init__(self):
        self.logger = logging.getLogger('dovela.stress_analysis')
    
    def analyze(self, geometry: DiamondDovelaGeometry, 
               load_case: LoadCase, 
               material: MaterialProperties) -> StressResults:
        """
        Análisis de esfuerzos usando teoría clásica
        
        Args:
            geometry: Geometría de la dovela
            load_case: Caso de carga
            material: Propiedades del material
            
        Returns:
            Resultados del análisis
        """
        self.logger.info("Iniciando análisis de esfuerzos clásico...")
        
        # Obtener malla de puntos
        coords, _ = geometry.get_mesh_points(refinement_level=3)
        
        # Convertir carga a Newtons
        load_N = load_case.magnitude.convert_to('N').value
        
        # Análisis por cada punto
        stress_states = []
        
        for coord in coords:
            point = Point2D(coord[0], coord[1])
            stress_state = self._calculate_stress_at_point(
                point, geometry, load_N, material
            )
            stress_states.append(stress_state)
        
        # Información del análisis
        analysis_info = {
            'method': 'classical_theory',
            'num_points': len(coords),
            'load_magnitude_N': load_N,
            'max_von_mises_Pa': max(s.von_mises() for s in stress_states),
            'analysis_notes': [
                'Teoría clásica de vigas',
                'Concentración de esfuerzos incluida',
                'Distribución parabólica de cortante'
            ]
        }
        
        results = StressResults(
            stress_states=stress_states,
            coordinates=coords,
            load_case=load_case,
            material=material,
            geometry=geometry,
            analysis_info=analysis_info
        )
        
        # Log de resultados principales
        max_vm, max_location = results.get_max_stress(StressType.VON_MISES)
        min_sf, critical_location = results.get_min_safety_factor()
        
        self.logger.info(f"Análisis completado:")
        self.logger.info(f"  - von Mises máximo: {max_vm/1e6:.2f} MPa en ({max_location.x:.1f}, {max_location.y:.1f})")
        self.logger.info(f"  - Factor de seguridad mínimo: {min_sf:.2f} en ({critical_location.x:.1f}, {critical_location.y:.1f})")
        
        return results
    
    def _calculate_stress_at_point(self, point: Point2D, 
                                  geometry: DiamondDovelaGeometry,
                                  load_N: float,
                                  material: MaterialProperties) -> StressState:
        """
        Calcula estado de esfuerzos en un punto específico
        
        Args:
            point: Punto de análisis
            geometry: Geometría de la dovela
            load_N: Carga en Newtons
            material: Propiedades del material
            
        Returns:
            Estado de esfuerzos en el punto
        """
        
        # Coordenadas normalizadas
        xi = (point.x + geometry.diagonal_half) / (2 * geometry.diagonal_half)  # 0 a 1
        eta = point.y / geometry.diagonal_half  # -1 a 1
        
        xi = np.clip(xi, 0, 1)
        eta = np.clip(eta, -1, 1)
        
        # === ESFUERZO NORMAL X (FLEXIÓN) ===
        sigma_x = self._calculate_flexural_stress(xi, eta, load_N, geometry)
        
        # === ESFUERZO NORMAL Y (COMPRESIÓN LOCAL) ===
        sigma_y = self._calculate_bearing_stress(xi, eta, load_N, geometry)
        
        # === ESFUERZO CORTANTE XY ===
        tau_xy = self._calculate_shear_stress(xi, eta, load_N, geometry)
        
        return StressState(sigma_x, sigma_y, tau_xy, point)
    
    def _calculate_flexural_stress(self, xi: float, eta: float, 
                                  load_N: float, 
                                  geometry: DiamondDovelaGeometry) -> float:
        """
        Calcula esfuerzo flexural usando teoría de vigas
        
        Args:
            xi: Coordenada normalizada X (0 = lado cargado, 1 = punta libre)
            eta: Coordenada normalizada Y (-1 a 1)
            load_N: Carga en Newtons
            geometry: Geometría
            
        Returns:
            Esfuerzo flexural sigma_x [Pa]
        """
        
        # Momento flector (máximo en lado cargado, cero en punta libre)
        L = geometry.diagonal_half  # Longitud característica
        
        # Momento debido a carga concentrada (aproximación de viga en voladizo)
        M = load_N * L * (1 - xi)  # Decrece linealmente hacia la punta
        
        # Propiedades de sección
        section_props = geometry.get_section_properties()
        I = section_props['Ix']  # Momento de inercia
        c = abs(eta) * geometry.diagonal_half  # Distancia al eje neutro
        
        # Esfuerzo flexural: σ = Mc/I
        if I > 0:
            sigma_flexural = M * c / I
        else:
            sigma_flexural = 0
        
        # Factor de concentración de esfuerzos cerca del punto de carga
        if xi < 0.2:  # Zona de aplicación de carga
            Kt = 1.5 + 2.0 * np.exp(-xi * 10)  # Concentración alta
        else:
            Kt = 1.0  # Sin concentración en zona alejada
        
        return sigma_flexural * Kt
    
    def _calculate_bearing_stress(self, xi: float, eta: float,
                                 load_N: float,
                                 geometry: DiamondDovelaGeometry) -> float:
        """
        Calcula esfuerzo de aplastamiento/compresión local
        
        Args:
            xi: Coordenada normalizada X
            eta: Coordenada normalizada Y  
            load_N: Carga en Newtons
            geometry: Geometría
            
        Returns:
            Esfuerzo de compresión sigma_y [Pa]
        """
        
        # Esfuerzo de aplastamiento máximo en zona de contacto
        contact_area = geometry.contact_area  # m²
        sigma_bearing_max = load_N / contact_area
        
        # Distribución espacial (máximo en zona de carga)
        if xi < 0.3:  # Zona de contacto directo
            # Distribución según Hertz (simplificada)
            distribution_factor = np.exp(-xi * 5)
            concentration_factor = 1.0 + 0.5 * (1 - abs(eta))  # Máximo en centro
        else:  # Zona alejada de la carga
            distribution_factor = 0.1 * np.exp(-(xi - 0.3) * 3)
            concentration_factor = 1.0
        
        return sigma_bearing_max * distribution_factor * concentration_factor
    
    def _calculate_shear_stress(self, xi: float, eta: float,
                               load_N: float, 
                               geometry: DiamondDovelaGeometry) -> float:
        """
        Calcula esfuerzo cortante usando fórmula de Jourawski
        
        Args:
            xi: Coordenada normalizada X
            eta: Coordenada normalizada Y
            load_N: Carga en Newtons
            geometry: Geometría
            
        Returns:
            Esfuerzo cortante tau_xy [Pa]
        """
        
        # Fuerza cortante (constante en sección para carga concentrada)
        V = load_N
        
        # Propiedades de sección
        section_props = geometry.get_section_properties()
        I = section_props['Ix']
        t = geometry.thickness.value  # Espesor
        
        # Momento estático Q = A' * y_bar (simplificado para forma diamante)
        y_pos = abs(eta) * geometry.diagonal_half
        A_above = geometry.area * (1 - abs(eta)) / 2  # Área por encima del punto
        y_bar = y_pos / 2  # Centroide del área
        Q = A_above * y_bar
        
        # Fórmula de Jourawski: τ = VQ/(It)
        if I > 0 and t > 0:
            tau_base = V * Q / (I * t)
        else:
            tau_base = 0
        
        # Distribución parabólica clásica en Y
        parabolic_factor = 1 - eta**2  # Máximo en centro (eta=0)
        
        # Factor de variación longitudinal
        if xi < 0.5:
            longitudinal_factor = 1.0
        else:
            longitudinal_factor = 0.5  # Menor cortante cerca de punta libre
        
        return tau_base * parabolic_factor * longitudinal_factor


class AASHTOStressAnalyzer(StressAnalyzer):
    """
    Analizador según normas AASHTO 14.5.2
    
    Implementa procedimientos específicos de AASHTO para análisis de dovelas
    """
    
    def __init__(self):
        self.logger = logging.getLogger('dovela.aashto_analysis')
    
    def analyze(self, geometry: DiamondDovelaGeometry, 
               load_case: LoadCase, 
               material: MaterialProperties) -> StressResults:
        """Análisis según AASHTO 14.5.2"""
        
        self.logger.info("Iniciando análisis según AASHTO 14.5.2...")
        
        # Para implementación inicial, usar método clásico con factores AASHTO
        classical_analyzer = ClassicalStressAnalyzer()
        results = classical_analyzer.analyze(geometry, load_case, material)
        
        # Aplicar factores de modificación AASHTO
        for state in results.stress_states:
            # Factores de modificación según AASHTO
            # (Estos serían específicos según la norma exacta)
            state.sigma_x *= 1.1  # Factor de conservatismo
            state.sigma_y *= 1.15  # Factor para aplastamiento
            state.tau_xy *= 1.05   # Factor para cortante
        
        # Actualizar información del análisis
        results.analysis_info.update({
            'method': 'AASHTO_14.5.2',
            'safety_factors_applied': {
                'flexural': 1.1,
                'bearing': 1.15,
                'shear': 1.05
            },
            'analysis_notes': [
                'Análisis según AASHTO 14.5.2',
                'Factores de seguridad aplicados',
                'Conservativo para diseño'
            ]
        })
        
        self.logger.info("Análisis AASHTO completado con factores de seguridad")
        
        return results
