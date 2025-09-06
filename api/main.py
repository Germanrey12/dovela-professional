from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from typing import List, Dict, Optional, Any
import traceback
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.tri as mtri
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter

app = FastAPI(title="Dovela Professional API",
              description="API para análisis de dovelas diamante",
              version="2.0.0")

# Configuración de CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, limitar a tu dominio específico
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de datos
class DovelaProfesionalRequest(BaseModel):
    load_kN: float = 22.2
    thickness_mm: float = 12.7
    analysis_type: str = "von_mises"

class DovelaProfesionalResponse(BaseModel):
    stress_max: float
    stress_min: float
    plot_image: str  # Base64 de la imagen
    displacement_mm: float
    safety_factor: float
    analysis_summary: str

# Implementación del análisis de dovela (adaptada de tu implementación con Tkinter)
def analyze_dowel(load_kN: float, thickness_mm: float, analysis_type: str) -> Dict[str, Any]:
    try:
        # Geometría de la dovela diamante
        width_mm = 70
        length_mm = 70
        
        # Propiedades del material
        E = 200000  # Módulo de Young para el acero (MPa)
        poisson = 0.3  # Coeficiente de Poisson
        yield_stress = 350  # Límite elástico para acero estructural típico (MPa)
        
        # Generar malla para el análisis
        x = np.linspace(-width_mm/2, width_mm/2, 100)
        y = np.linspace(-length_mm/2, length_mm/2, 100)
        X, Y = np.meshgrid(x, y)
        
        # Máscara para forma de diamante
        diamond_mask = (abs(X) + abs(Y) <= width_mm/2)
        
        # Calcular esfuerzos (simplificación del modelo de elementos finitos)
        load_N = load_kN * 1000
        area_mm2 = width_mm * length_mm * 0.5  # Área del diamante
        pressure = load_N / area_mm2
        
        # Modelo simplificado para esfuerzos
        if analysis_type == "von_mises":
            # Esfuerzo de Von Mises
            stress = pressure * (1 - (X**2 + Y**2) / ((width_mm/2)**2))
            stress = np.abs(stress) * diamond_mask
            title = "Esfuerzos de Von Mises (MPa)"
            
        elif analysis_type == "principal":
            # Esfuerzos principales
            stress = pressure * (1 - (X**2 / (width_mm/2)**2 + Y**2 / (length_mm/2)**2))
            stress = stress * diamond_mask
            title = "Esfuerzos Principales (MPa)"
            
        elif analysis_type == "cortante":
            # Esfuerzos cortantes
            stress = pressure * 0.5 * (X**2 - Y**2) / ((width_mm/2)**2) * diamond_mask
            title = "Esfuerzos Cortantes (MPa)"
            
        elif analysis_type == "lte_fisico":
            # Modelo LTE (Load Transfer Efficiency)
            k = 0.75  # Factor de eficiencia de transferencia de carga
            stress = pressure * k * np.exp(-((X**2 + Y**2) / (width_mm/3)**2)) * diamond_mask
            title = "Modelo LTE - Transferencia de Carga (MPa)"
            
        else:  # Análisis completo
            # Combinación de esfuerzos
            stress_vm = pressure * (1 - (X**2 + Y**2) / ((width_mm/2)**2))
            stress_p = pressure * (1 - (X**2 / (width_mm/2)**2 + Y**2 / (length_mm/2)**2))
            stress = np.sqrt(stress_vm**2 + 3 * stress_p**2) * diamond_mask
            title = "Análisis Completo - Esfuerzos Combinados (MPa)"
        
        # Suavizado para resultados más realistas
        stress = gaussian_filter(stress, sigma=1) * diamond_mask
        
        # Calcular deformación
        t = thickness_mm
        # Simplificación de la fórmula de deformación para una placa
        displacement = pressure * (width_mm**4) / (32 * E * t**3)
        
        # Calcular factor de seguridad
        stress_max = np.max(stress)
        safety_factor = yield_stress / stress_max if stress_max > 0 else float('inf')
        
        # Generar gráfico
        fig = Figure(figsize=(10, 8))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Usar solo los puntos dentro del diamante para el gráfico de contorno
        mask = diamond_mask.flatten()
        x_valid = X.flatten()[mask]
        y_valid = Y.flatten()[mask]
        z_valid = stress.flatten()[mask]
        
        # Generar una malla triangular para el contorno
        triang = mtri.Triangulation(x_valid, y_valid)
        
        # Graficar contorno
        contour = ax.tricontourf(triang, z_valid, cmap='jet', levels=20)
        ax.set_title(title)
        ax.set_xlabel('Ancho (mm)')
        ax.set_ylabel('Largo (mm)')
        ax.axis('equal')
        fig.colorbar(contour, ax=ax, label='Esfuerzo (MPa)')
        
        # Añadir detalles adicionales
        ax.set_xlim(-width_mm/2, width_mm/2)
        ax.set_ylim(-length_mm/2, length_mm/2)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Convertir el gráfico a Base64 para enviarlo en la respuesta JSON
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        # Texto de resumen
        if safety_factor < 1.0:
            summary = "¡ADVERTENCIA! La dovela podría fallar bajo esta carga."
        elif safety_factor < 1.5:
            summary = "Diseño crítico. Se recomienda aumentar el espesor o reducir la carga."
        elif safety_factor < 3.0:
            summary = "Diseño aceptable. Factor de seguridad moderado."
        else:
            summary = "Diseño seguro. Alto factor de seguridad."
            
        summary += f"\nEsfuerzo máximo: {stress_max:.2f} MPa"
        summary += f"\nDeformación máxima: {displacement:.4f} mm"
        
        return {
            "stress_max": float(stress_max),
            "stress_min": float(np.min(stress[stress > 0])) if np.any(stress > 0) else 0.0,
            "plot_image": f"data:image/png;base64,{img_base64}",
            "displacement_mm": float(displacement),
            "safety_factor": float(safety_factor),
            "analysis_summary": summary
        }
        
    except Exception as e:
        # Log error para debugging
        error_trace = traceback.format_exc()
        print(f"Error en análisis: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error en el análisis: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Dovela Professional API v2.0", "status": "active"}

@app.post("/analyze", response_model=DovelaProfesionalResponse)
def analyze_dowel_endpoint(request: DovelaProfesionalRequest):
    result = analyze_dowel(
        load_kN=request.load_kN,
        thickness_mm=request.thickness_mm,
        analysis_type=request.analysis_type
    )
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
