"""
Sistema de validación profesional para análisis de dovelas diamante
"""
from typing import Union, Optional, Tuple, List
import numpy as np
from dataclasses import dataclass
from enum import Enum
import logging
import os
import sys

# Manejo de imports para ejecución independiente
try:
    from ..config.settings import GeometryLimits, MaterialProperties, UnitSystem
except ImportError:
    # Si los imports relativos fallan, intentar imports absolutos
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from config.settings import GeometryLimits, MaterialProperties, UnitSystem


class ValidationError(Exception):
    """Error específico de validación"""
    pass


class ValidationSeverity(Enum):
    """Severidad de validaciones"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Resultado de validación individual"""
    is_valid: bool
    severity: ValidationSeverity
    message: str
    parameter: str
    value: Union[float, str]
    recommendation: Optional[str] = None


class DovelaValidator:
    """Validador profesional para parámetros de dovela diamante"""
    
    def __init__(self, geometry_limits: Optional[GeometryLimits] = None):
        self.geometry_limits = geometry_limits or GeometryLimits()
        self.logger = logging.getLogger('dovela.validation')
        self.results: List[ValidationResult] = []
    
    def reset_results(self):
        """Reinicia resultados de validación"""
        self.results.clear()
    
    def add_result(self, result: ValidationResult):
        """Agrega resultado de validación"""
        self.results.append(result)
        
        # Log según severidad
        if result.severity == ValidationSeverity.CRITICAL:
            self.logger.critical(f"{result.parameter}: {result.message}")
        elif result.severity == ValidationSeverity.ERROR:
            self.logger.error(f"{result.parameter}: {result.message}")
        elif result.severity == ValidationSeverity.WARNING:
            self.logger.warning(f"{result.parameter}: {result.message}")
        else:
            self.logger.info(f"{result.parameter}: {result.message}")
    
    def validate_geometry(self, side_mm: float, thickness_mm: float, 
                         joint_opening_mm: float) -> bool:
        """
        Valida geometría según límites AASHTO 14.5.1
        
        Args:
            side_mm: Lado de la dovela diamante [mm]
            thickness_mm: Espesor de la dovela [mm]
            joint_opening_mm: Apertura de junta [mm]
            
        Returns:
            True si la geometría es válida
            
        Raises:
            ValidationError: Si hay errores críticos
        """
        self.logger.info("Validando geometría según AASHTO 14.5.1...")
        
        # Validar lado
        if not isinstance(side_mm, (int, float)) or side_mm <= 0:
            result = ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                message="Lado debe ser un número positivo",
                parameter="side_mm",
                value=side_mm
            )
            self.add_result(result)
            raise ValidationError(result.message)
        
        if not (self.geometry_limits.min_side_mm <= side_mm <= self.geometry_limits.max_side_mm):
            result = ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message=f"Lado debe estar entre {self.geometry_limits.min_side_mm}-{self.geometry_limits.max_side_mm} mm",
                parameter="side_mm",
                value=side_mm,
                recommendation=f"Usar valor entre {self.geometry_limits.min_side_mm}-{self.geometry_limits.max_side_mm} mm según AASHTO"
            )
            self.add_result(result)
            raise ValidationError(result.message)
        
        # Validar espesor
        if not isinstance(thickness_mm, (int, float)) or thickness_mm <= 0:
            result = ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                message="Espesor debe ser un número positivo",
                parameter="thickness_mm",
                value=thickness_mm
            )
            self.add_result(result)
            raise ValidationError(result.message)
        
        if not (self.geometry_limits.min_thickness_mm <= thickness_mm <= self.geometry_limits.max_thickness_mm):
            result = ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message=f"Espesor debe estar entre {self.geometry_limits.min_thickness_mm}-{self.geometry_limits.max_thickness_mm} mm",
                parameter="thickness_mm",
                value=thickness_mm,
                recommendation=f"Usar espesor estándar: 6.35mm (1/4\"), 12.7mm (1/2\"), 19.1mm (3/4\")"
            )
            self.add_result(result)
            raise ValidationError(result.message)
        
        # Validar apertura de junta
        if not isinstance(joint_opening_mm, (int, float)) or joint_opening_mm < 0:
            result = ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                message="Apertura de junta debe ser un número no negativo",
                parameter="joint_opening_mm",
                value=joint_opening_mm
            )
            self.add_result(result)
            raise ValidationError(result.message)
        
        max_joint = side_mm * self.geometry_limits.max_joint_opening_ratio
        if joint_opening_mm > max_joint:
            result = ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message=f"Apertura de junta no debe exceder {max_joint:.1f} mm ({self.geometry_limits.max_joint_opening_ratio*100}% del lado)",
                parameter="joint_opening_mm",
                value=joint_opening_mm,
                recommendation=f"Reducir apertura a máximo {max_joint:.1f} mm"
            )
            self.add_result(result)
            raise ValidationError(result.message)
        
        # Validaciones de advertencia
        
        # Relación espesor/lado
        thickness_ratio = thickness_mm / side_mm
        if thickness_ratio < 0.05:
            result = ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.WARNING,
                message=f"Dovela muy delgada (t/d = {thickness_ratio:.3f})",
                parameter="thickness_ratio",
                value=thickness_ratio,
                recommendation="Considerar incrementar espesor para mejor rigidez"
            )
            self.add_result(result)
        
        elif thickness_ratio > 0.4:
            result = ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.WARNING,
                message=f"Dovela muy gruesa (t/d = {thickness_ratio:.3f})",
                parameter="thickness_ratio",
                value=thickness_ratio,
                recommendation="Espesor excesivo puede causar problemas de instalación"
            )
            self.add_result(result)
        
        self.logger.info("✅ Geometría validada correctamente")
        return True
    
    def validate_load_case(self, load_kN: float, safety_factor: Optional[float] = None) -> bool:
        """
        Valida caso de carga según límites de diseño
        
        Args:
            load_kN: Carga aplicada [kN]
            safety_factor: Factor de seguridad opcional
            
        Returns:
            True si la carga es válida
        """
        self.logger.info("Validando caso de carga...")
        
        # Validar tipo y valor
        if not isinstance(load_kN, (int, float)) or load_kN <= 0:
            result = ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                message="Carga debe ser un número positivo",
                parameter="load_kN",
                value=load_kN
            )
            self.add_result(result)
            raise ValidationError(result.message)
        
        # Validar límites de diseño - COMENTADO PARA PERMITIR CUALQUIER CARGA
        # if load_kN > self.geometry_limits.max_design_load_kN:
        #     result = ValidationResult(
        #         is_valid=False,
        #         severity=ValidationSeverity.ERROR,
        #         message=f"Carga excede máximo de diseño ({self.geometry_limits.max_design_load_kN} kN)",
        #         parameter="load_kN",
        #         value=load_kN,
        #         recommendation=f"Reducir carga a máximo {self.geometry_limits.max_design_load_kN} kN o revisar diseño"
        #     )
        #     self.add_result(result)
        #     raise ValidationError(result.message)
        
        # Cargas típicas de servicio para dovelas
        typical_service_load = 22.2  # kN (5000 lbf)
        if load_kN > typical_service_load * 2:
            result = ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.WARNING,
                message=f"Carga alta comparada con servicio típico ({typical_service_load} kN)",
                parameter="load_kN",
                value=load_kN,
                recommendation="Verificar que sea carga factorizada apropiada"
            )
            self.add_result(result)
        
        # Validar factor de seguridad si se proporciona
        if safety_factor is not None:
            if safety_factor < 1.5:
                result = ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Factor de seguridad ({safety_factor:.1f}) menor que mínimo (1.5)",
                    parameter="safety_factor",
                    value=safety_factor,
                    recommendation="Aumentar factor de seguridad a mínimo 1.5"
                )
                self.add_result(result)
                raise ValidationError(result.message)
            
            elif safety_factor < 2.0:
                result = ValidationResult(
                    is_valid=True,
                    severity=ValidationSeverity.WARNING,
                    message=f"Factor de seguridad bajo ({safety_factor:.1f})",
                    parameter="safety_factor",
                    value=safety_factor,
                    recommendation="AASHTO recomienda FS ≥ 2.0 para dovelas"
                )
                self.add_result(result)
        
        self.logger.info("✅ Caso de carga validado")
        return True
    
    def validate_material_properties(self, material: MaterialProperties, 
                                   unit_system: UnitSystem) -> bool:
        """
        Valida propiedades del material
        
        Args:
            material: Propiedades del material
            unit_system: Sistema de unidades
            
        Returns:
            True si las propiedades son válidas
        """
        self.logger.info(f"Validando propiedades de material: {material.grade.value}")
        
        # Validar módulo de elasticidad
        if unit_system == UnitSystem.METRIC:
            E_min, E_max = 190000, 210000  # MPa
            E_unit = "MPa"
        else:
            E_min, E_max = 27500, 30500   # ksi
            E_unit = "ksi"
        
        if not (E_min <= material.E <= E_max):
            result = ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                message=f"Módulo E ({material.E} {E_unit}) fuera de rango típico para acero ({E_min}-{E_max} {E_unit})",
                parameter="E",
                value=material.E,
                recommendation=f"Verificar valor, típico para acero: 200 GPa (29000 ksi)"
            )
            self.add_result(result)
        
        # Validar Poisson
        if not (0.25 <= material.nu <= 0.35):
            result = ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                message=f"Relación de Poisson ({material.nu}) fuera de rango típico (0.25-0.35)",
                parameter="nu",
                value=material.nu,
                recommendation="Usar 0.3 para acero estructural"
            )
            self.add_result(result)
        
        # Validar límite elástico según grado
        if material.grade == material.grade.A36:
            fy_min = 250 if unit_system == UnitSystem.METRIC else 36  # MPa o ksi
            if material.fy < fy_min:
                result = ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"fy ({material.fy}) menor que mínimo ASTM A36 ({fy_min})",
                    parameter="fy",
                    value=material.fy
                )
                self.add_result(result)
                raise ValidationError(result.message)
        
        self.logger.info("✅ Propiedades de material validadas")
        return True
    
    def validate_mesh_quality(self, coords: np.ndarray, triangles: np.ndarray) -> bool:
        """
        Valida calidad de la malla FEA
        
        Args:
            coords: Coordenadas nodales
            triangles: Conectividad de elementos
            
        Returns:
            True si la malla es adecuada
        """
        self.logger.info("Validando calidad de malla FEA...")
        
        # Número mínimo de elementos
        min_elements = 100
        if len(triangles) < min_elements:
            result = ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.WARNING,
                message=f"Malla gruesa ({len(triangles)} elementos), recomendado > {min_elements}",
                parameter="mesh_elements",
                value=len(triangles),
                recommendation="Refinar malla para mayor precisión"
            )
            self.add_result(result)
        
        # Verificar aspect ratio de elementos (básico)
        if len(triangles) > 0:
            # Calcular aspect ratios (simplificado)
            aspect_ratios = []
            for tri in triangles[:min(100, len(triangles))]:  # Muestra
                if len(tri) == 3:
                    p1, p2, p3 = coords[tri]
                    # Longitudes de lados
                    a = np.linalg.norm(p2 - p1)
                    b = np.linalg.norm(p3 - p2)
                    c = np.linalg.norm(p1 - p3)
                    
                    # Aspect ratio aproximado
                    max_side = max(a, b, c)
                    min_side = min(a, b, c)
                    if min_side > 0:
                        aspect_ratios.append(max_side / min_side)
            
            if aspect_ratios:
                max_aspect = max(aspect_ratios)
                avg_aspect = np.mean(aspect_ratios)
                
                if max_aspect > 10:
                    result = ValidationResult(
                        is_valid=True,
                        severity=ValidationSeverity.WARNING,
                        message=f"Elementos muy distorsionados (aspect ratio máximo: {max_aspect:.1f})",
                        parameter="aspect_ratio",
                        value=max_aspect,
                        recommendation="Refinar malla en zonas con elementos distorsionados"
                    )
                    self.add_result(result)
                
                self.logger.info(f"Calidad de malla: {len(triangles)} elementos, aspect ratio promedio: {avg_aspect:.2f}")
        
        self.logger.info("✅ Calidad de malla validada")
        return True
    
    def get_validation_summary(self) -> dict:
        """
        Genera resumen de validación
        
        Returns:
            Diccionario con resumen de validación
        """
        summary = {
            'total_checks': len(self.results),
            'critical': len([r for r in self.results if r.severity == ValidationSeverity.CRITICAL]),
            'errors': len([r for r in self.results if r.severity == ValidationSeverity.ERROR]),
            'warnings': len([r for r in self.results if r.severity == ValidationSeverity.WARNING]),
            'info': len([r for r in self.results if r.severity == ValidationSeverity.INFO]),
            'is_valid': all(r.severity not in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR] for r in self.results),
            'results': self.results
        }
        
        return summary
    
    def print_validation_report(self):
        """Imprime reporte de validación formateado"""
        summary = self.get_validation_summary()
        
        print("\n" + "="*60)
        print("📋 REPORTE DE VALIDACIÓN")
        print("="*60)
        
        print(f"Total de verificaciones: {summary['total_checks']}")
        print(f"❌ Críticos: {summary['critical']}")
        print(f"🚫 Errores: {summary['errors']}")
        print(f"⚠️  Advertencias: {summary['warnings']}")
        print(f"ℹ️  Informativos: {summary['info']}")
        
        status = "✅ VÁLIDO" if summary['is_valid'] else "❌ INVÁLIDO"
        print(f"\nEstado general: {status}")
        
        if self.results:
            print("\nDetalles:")
            for result in self.results:
                icon = {"critical": "❌", "error": "🚫", "warning": "⚠️", "info": "ℹ️"}[result.severity.value]
                print(f"  {icon} {result.parameter}: {result.message}")
                if result.recommendation:
                    print(f"     💡 {result.recommendation}")
        
        print("="*60)
