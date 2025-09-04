"""
Módulo de geometría profesional para dovelas diamante
"""
from dataclasses import dataclass
from typing import Tuple, List, Optional
import numpy as np
import logging
from abc import ABC, abstractmethod
import os
import sys

# Manejo de imports para ejecución independiente
try:
    from ..utils.unit_converter import ParameterWithUnits, unit_converter
    from ..config.settings import UnitSystem
except ImportError:
    # Si los imports relativos fallan, intentar imports absolutos
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from utils.unit_converter import ParameterWithUnits, unit_converter
    from config.settings import UnitSystem


@dataclass
class Point2D:
    """Punto en 2D con validación"""
    x: float
    y: float
    
    def distance_to(self, other: 'Point2D') -> float:
        """Calcula distancia a otro punto"""
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def __add__(self, other: 'Point2D') -> 'Point2D':
        return Point2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Point2D') -> 'Point2D':
        return Point2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Point2D':
        return Point2D(self.x * scalar, self.y * scalar)


class GeometryBase(ABC):
    """Clase base para geometrías"""
    
    @abstractmethod
    def get_boundary_points(self, num_points: int = 100) -> List[Point2D]:
        """Obtiene puntos del contorno"""
        pass
    
    @abstractmethod
    def is_inside(self, point: Point2D) -> bool:
        """Verifica si un punto está dentro de la geometría"""
        pass
    
    @abstractmethod
    def get_area(self) -> float:
        """Calcula área de la geometría"""
        pass


class DiamondDovelaGeometry(GeometryBase):
    """
    Geometría profesional de dovela diamante según AASHTO 14.5.1
    
    Especificaciones:
    - Forma diamante simétrica
    - Dimensiones según norma AASHTO
    - Coordenadas en sistema local (centro en origen)
    """
    
    def __init__(self, side_length: ParameterWithUnits, thickness: ParameterWithUnits,
                 joint_opening: ParameterWithUnits, unit_system: UnitSystem):
        """
        Inicializa geometría de dovela diamante
        
        Args:
            side_length: Longitud del lado del diamante
            thickness: Espesor de la dovela
            joint_opening: Apertura de la junta
            unit_system: Sistema de unidades de trabajo
        """
        self.logger = logging.getLogger('dovela.geometry')
        
        # Convertir todo al sistema de trabajo
        self.side_length = side_length.to_system(unit_system)
        self.thickness = thickness.to_system(unit_system)
        self.joint_opening = joint_opening.to_system(unit_system)
        self.unit_system = unit_system
        
        # Calcular propiedades geométricas
        self._calculate_geometry()
        
        self.logger.info(f"Geometría diamante creada: {self.side_length.format()} × {self.thickness.format()}")
    
    def _calculate_geometry(self):
        """Calcula propiedades geométricas derivadas"""
        
        # Radio del diamante (distancia del centro a vértice)
        self.diagonal_half = self.side_length.value * np.sqrt(2) / 2
        
        # Vértices del diamante en coordenadas locales
        self.vertices = [
            Point2D(self.diagonal_half, 0),      # Derecha
            Point2D(0, self.diagonal_half),      # Arriba
            Point2D(-self.diagonal_half, 0),     # Izquierda
            Point2D(0, -self.diagonal_half)      # Abajo
        ]
        
        # Área del diamante
        self.area = 2 * self.side_length.value**2
        
        # Momento de inercia aproximado (para análisis simplificado)
        self.Ixx = self.area * self.diagonal_half**2 / 12  # Aproximación
        self.Iyy = self.Ixx  # Simetría
        
        # Área efectiva de contacto (lado cargado)
        self.contact_area = self.side_length.value * self.thickness.value
        
        # Centroide (en el centro por simetría)
        self.centroid = Point2D(0, 0)
        
        self.logger.debug(f"Área total: {self.area:.2f} {self.side_length.unit}²")
        self.logger.debug(f"Diagonal media: {self.diagonal_half:.2f} {self.side_length.unit}")
    
    def get_boundary_points(self, num_points: int = 100) -> List[Point2D]:
        """
        Genera puntos del contorno del diamante
        
        Args:
            num_points: Número de puntos del contorno
            
        Returns:
            Lista de puntos del contorno
        """
        points = []
        
        # Generar puntos en cada lado del diamante
        points_per_side = num_points // 4
        
        # Lado derecho (arriba → derecha)
        for i in range(points_per_side):
            t = i / points_per_side
            x = t * self.diagonal_half
            y = (1 - t) * self.diagonal_half
            points.append(Point2D(x, y))
        
        # Lado inferior (derecha → abajo)
        for i in range(points_per_side):
            t = i / points_per_side
            x = (1 - t) * self.diagonal_half
            y = -t * self.diagonal_half
            points.append(Point2D(x, y))
        
        # Lado izquierdo (abajo → izquierda)
        for i in range(points_per_side):
            t = i / points_per_side
            x = -t * self.diagonal_half
            y = -(1 - t) * self.diagonal_half
            points.append(Point2D(x, y))
        
        # Lado superior (izquierda → arriba)
        for i in range(points_per_side):
            t = i / points_per_side
            x = -(1 - t) * self.diagonal_half
            y = t * self.diagonal_half
            points.append(Point2D(x, y))
        
        return points
    
    def is_inside(self, point: Point2D) -> bool:
        """
        Verifica si un punto está dentro del diamante
        
        Args:
            point: Punto a verificar
            
        Returns:
            True si el punto está dentro
        """
        # Para un diamante: |x| + |y| <= diagonal_half
        return abs(point.x) + abs(point.y) <= self.diagonal_half
    
    def get_area(self) -> float:
        """Retorna área del diamante"""
        return self.area
    
    def get_loaded_side_geometry(self) -> Tuple[Point2D, Point2D]:
        """
        Obtiene geometría del lado cargado
        
        Returns:
            Tupla (punto_superior, punto_inferior) del lado cargado
        """
        # Asumiendo que el lado cargado está en x = -diagonal_half + joint_opening/2
        load_x = -self.diagonal_half + self.joint_opening.value / 2
        
        # Límites Y para el lado cargado
        y_max = self.diagonal_half - abs(load_x)
        y_min = -y_max
        
        return Point2D(load_x, y_max), Point2D(load_x, y_min)
    
    def get_mesh_points(self, refinement_level: int = 3) -> Tuple[np.ndarray, np.ndarray]:
        """
        Genera puntos para malla FEA
        
        Args:
            refinement_level: Nivel de refinamiento (1-5)
            
        Returns:
            Tupla (coordenadas, máscara_válida)
        """
        # Número de puntos basado en nivel de refinamiento
        base_points = 50
        num_points = base_points * refinement_level
        
        # Crear malla regular
        x_range = np.linspace(-self.diagonal_half, self.diagonal_half, num_points)
        y_range = np.linspace(-self.diagonal_half, self.diagonal_half, num_points)
        X, Y = np.meshgrid(x_range, y_range)
        
        # Máscara para puntos dentro del diamante
        mask = (np.abs(X) + np.abs(Y)) <= self.diagonal_half
        
        # Coordenadas válidas
        coords = np.column_stack([X[mask], Y[mask]])
        
        self.logger.debug(f"Malla generada: {len(coords)} puntos, refinamiento nivel {refinement_level}")
        
        return coords, mask
    
    def get_section_properties(self) -> dict:
        """
        Calcula propiedades de la sección transversal
        
        Returns:
            Diccionario con propiedades de sección
        """
        # Área de la sección transversal
        A = self.area * self.thickness.value
        
        # Momentos de inercia (aproximados para forma diamante)
        # Usando fórmulas para rombo
        a = self.side_length.value  # Lado
        t = self.thickness.value    # Espesor
        
        # Momento de inercia en X (flexión sobre eje Y)
        Ix = (a**4 * t) / 48  # Aproximación
        
        # Momento de inercia en Y (flexión sobre eje X)  
        Iy = Ix  # Simetría
        
        # Momento polar
        J = Ix + Iy
        
        # Módulos de sección
        c = self.diagonal_half  # Distancia al punto más alejado
        Sx = Ix / c
        Sy = Iy / c
        
        # Radio de giro
        rx = np.sqrt(Ix / A)
        ry = np.sqrt(Iy / A)
        
        return {
            'area': A,
            'Ix': Ix,
            'Iy': Iy,
            'J': J,
            'Sx': Sx,
            'Sy': Sy,
            'rx': rx,
            'ry': ry,
            'centroid_x': 0,
            'centroid_y': 0
        }
    
    def export_to_dict(self) -> dict:
        """Exporta geometría a diccionario para serialización"""
        return {
            'type': 'DiamondDovela',
            'side_length': {
                'value': self.side_length.value,
                'unit': self.side_length.unit
            },
            'thickness': {
                'value': self.thickness.value,
                'unit': self.thickness.unit
            },
            'joint_opening': {
                'value': self.joint_opening.value,
                'unit': self.joint_opening.unit
            },
            'unit_system': self.unit_system.value,
            'area': self.area,
            'diagonal_half': self.diagonal_half,
            'contact_area': self.contact_area,
            'vertices': [(v.x, v.y) for v in self.vertices]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DiamondDovelaGeometry':
        """Crea geometría desde diccionario"""
        side_length = ParameterWithUnits(
            data['side_length']['value'],
            data['side_length']['unit'],
            "Lado del diamante"
        )
        
        thickness = ParameterWithUnits(
            data['thickness']['value'],
            data['thickness']['unit'],
            "Espesor"
        )
        
        joint_opening = ParameterWithUnits(
            data['joint_opening']['value'],
            data['joint_opening']['unit'],
            "Apertura de junta"
        )
        
        unit_system = UnitSystem(data['unit_system'])
        
        return cls(side_length, thickness, joint_opening, unit_system)
    
    def __str__(self) -> str:
        return (f"DiamondDovela({self.side_length.format()} × {self.thickness.format()}, "
                f"apertura: {self.joint_opening.format()})")


class GeometryFactory:
    """Factory para crear geometrías estándar"""
    
    @staticmethod
    def create_standard_diamond(size: str, unit_system: UnitSystem) -> DiamondDovelaGeometry:
        """
        Crea geometría diamante estándar
        
        Args:
            size: Tamaño estándar ('small', 'medium', 'large')
            unit_system: Sistema de unidades
            
        Returns:
            Geometría de dovela diamante
        """
        
        if unit_system == UnitSystem.METRIC:
            sizes = {
                'small': (100, 6.35, 3.0),    # mm
                'medium': (125, 12.7, 4.8),   # mm (estándar)
                'large': (150, 19.1, 6.0)     # mm
            }
            unit = 'mm'
        else:
            sizes = {
                'small': (4.0, 0.25, 0.125),   # in
                'medium': (5.0, 0.5, 0.19),    # in (estándar)
                'large': (6.0, 0.75, 0.25)     # in
            }
            unit = 'in'
        
        if size not in sizes:
            raise ValueError(f"Tamaño '{size}' no reconocido. Usar: {list(sizes.keys())}")
        
        side, thickness, joint = sizes[size]
        
        return DiamondDovelaGeometry(
            ParameterWithUnits(side, unit, "Lado del diamante"),
            ParameterWithUnits(thickness, unit, "Espesor"),
            ParameterWithUnits(joint, unit, "Apertura de junta"),
            unit_system
        )
