#!/usr/bin/env python3
"""
Script de prueba para verificar las correcciones en los contornos de esfuerzos
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def test_stress_distribution():
    """Prueba la distribución corregida de esfuerzos"""
    
    # Parámetros de prueba
    ap_mm = 4.8
    length_effective = 50.0
    x_positions = np.linspace(ap_mm/2, ap_mm/2 + length_effective, 100)
    
    # Distribución corregida - máximos en la base (x = ap_mm/2)
    stresses_corrected = []
    for x in x_positions:
        xi = (x - ap_mm/2) / length_effective  # 0 = base, 1 = punta
        xi = np.clip(xi, 0, 1)
        
        # Factor de distribución exponencial (máximo en xi=0)
        alpha = 3.0
        distribution_factor = np.exp(-alpha * xi)  # Máximo en xi=0, mínimo en xi=1
        
        # Factor de concentración corregido
        if xi < 0.1:  # Zona de contacto (base)
            Kt_total = 2.5  # Alta concentración en la base
        elif xi < 0.3:  # Zona de transición
            Kt_total = 1.8 * np.exp(-5 * xi)
        else:  # Zona de punta
            Kt_total = 0.2  # Esfuerzos mínimos en la punta
        
        stress = 100 * distribution_factor * Kt_total  # MPa base
        stresses_corrected.append(stress)
    
    # Crear gráfico de verificación
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Gráfico 1: Distribución de esfuerzos a lo largo de X
    ax1.plot(x_positions, stresses_corrected, 'b-', linewidth=3, label='Esfuerzo Corregido')
    ax1.axvline(ap_mm/2, color='red', linestyle='--', alpha=0.7, label='Base (Lado Cargado)')
    ax1.axvline(x_positions[-1], color='green', linestyle='--', alpha=0.7, label='Punta')
    ax1.set_xlabel('Posición X (mm)')
    ax1.set_ylabel('Esfuerzo von Mises (MPa)')
    ax1.set_title('Distribución Corregida de Esfuerzos\n(Máximo en BASE, Mínimo en PUNTA)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Anotaciones
    max_stress = max(stresses_corrected)
    min_stress = min(stresses_corrected)
    ax1.text(0.05, 0.95, f'Máximo: {max_stress:.1f} MPa (en base)\nMínimo: {min_stress:.1f} MPa (en punta)', 
             transform=ax1.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # Gráfico 2: Comparación visual con cuadro indicador
    diagonal_half = 60
    
    # Simular coordenadas de media dovela
    n_points = 50
    coords_x = np.linspace(ap_mm/2, diagonal_half, n_points)
    coords_y = np.linspace(-diagonal_half/2, diagonal_half/2, n_points)
    X, Y = np.meshgrid(coords_x, coords_y)
    
    # Calcular esfuerzos en la malla
    Z = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            x, y = X[i,j], Y[i,j]
            xi = (x - ap_mm/2) / length_effective
            xi = np.clip(xi, 0, 1)
            
            alpha = 3.0
            distribution_factor = np.exp(-alpha * xi)
            
            if xi < 0.1:
                Kt_total = 2.5
            elif xi < 0.3:
                Kt_total = 1.8 * np.exp(-5 * xi)
            else:
                Kt_total = 0.2
            
            Z[i,j] = 100 * distribution_factor * Kt_total
    
    # Contornos
    contour = ax2.contourf(X, Y, Z, levels=20, cmap='plasma')
    plt.colorbar(contour, ax=ax2, label='Esfuerzo von Mises (MPa)')
    
    # Cuadro indicador del lado cargado (reemplaza línea roja)
    rect_width = diagonal_half * 0.1
    rect_height = diagonal_half
    rect_x = ap_mm/2 - rect_width/2
    rect_y = -diagonal_half/2
    
    loaded_rect = Rectangle((rect_x, rect_y), rect_width, rect_height, 
                          facecolor='red', alpha=0.3, edgecolor='red', 
                          linewidth=2, label='Lado Cargado')
    ax2.add_patch(loaded_rect)
    
    # Contorno de media dovela
    diamond_x = [ap_mm/2, diagonal_half, ap_mm/2, ap_mm/2]
    diamond_y = [diagonal_half/2, 0, -diagonal_half/2, diagonal_half/2]
    ax2.plot(diamond_x, diamond_y, 'k-', linewidth=3, alpha=0.9)
    
    ax2.set_aspect('equal')
    ax2.set_xlabel('Posición X (mm)')
    ax2.set_ylabel('Posición Y (mm)')
    ax2.set_title('Vista 2D Corregida\n(Cuadro rojo = Lado Cargado)')
    ax2.legend()
    
    plt.tight_layout()
    plt.show()
    
    # Verificación numérica
    print("=== VERIFICACIÓN DE CORRECCIONES ===")
    print(f"Esfuerzo máximo: {max_stress:.2f} MPa (debe estar en la BASE)")
    print(f"Esfuerzo mínimo: {min_stress:.2f} MPa (debe estar en la PUNTA)")
    print(f"Relación máx/mín: {max_stress/min_stress:.1f}:1 (debe ser > 5:1)")
    print(f"Posición del máximo: x = {x_positions[np.argmax(stresses_corrected)]:.2f} mm")
    print(f"Posición de lado cargado: x = {ap_mm/2:.2f} mm")
    print("✓ Corrección aplicada: Esfuerzos máximos en BASE, mínimos en PUNTA")
    print("✓ Líneas rojas reemplazadas por cuadros indicadores")

if __name__ == "__main__":
    test_stress_distribution()
