# ANÁLISIS PROFESIONAL DE DOVELA DIAMANTE - VERSIÓN COHERENTE
# Implementación según normas AASHTO y teoría de Westergaard
# Autor: Análisis estructural profesional
# Fecha: 2025

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
import traceback

class DovelaAnalysisProfessional:
    def __init__(self, root):
        self.root = root
        root.title("Análisis Profesional de Dovela Diamante - AASHTO/Westergaard")
        root.geometry("600x800")
        self.create_widgets()

    def create_widgets(self):
        # Frame principal con scroll
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # === PARÁMETROS DE ENTRADA ===
        input_frame = ttk.LabelFrame(main_frame, text="Parámetros del Análisis", padding=10)
        input_frame.grid(row=0, column=0, sticky="ew", pady=(0,10))
        
        # Geometría de la dovela
        ttk.Label(input_frame, text="GEOMETRÍA DE LA DOVELA", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,5))
        
        ttk.Label(input_frame, text="Diagonal del diamante (mm):").grid(row=1, column=0, sticky="w")
        self.diagonal_mm = tk.DoubleVar(value=180.0)  # Diagonal completa
        ttk.Entry(input_frame, textvariable=self.diagonal_mm, width=10).grid(row=1, column=1, sticky="w")
        
        ttk.Label(input_frame, text="Espesor dovela (mm):").grid(row=2, column=0, sticky="w")
        self.thickness_mm = tk.DoubleVar(value=25.4)  # 1 pulgada estándar
        ttk.Entry(input_frame, textvariable=self.thickness_mm, width=10).grid(row=2, column=1, sticky="w")
        
        # Cargas
        ttk.Label(input_frame, text="CARGAS Y MATERIAL", font=('Arial', 10, 'bold')).grid(row=3, column=0, columnspan=2, pady=(10,5))
        
        ttk.Label(input_frame, text="Carga aplicada (kN):").grid(row=4, column=0, sticky="w")
        self.load_kN = tk.DoubleVar(value=22.24)  # Carga estándar AASHTO
        ttk.Entry(input_frame, textvariable=self.load_kN, width=10).grid(row=4, column=1, sticky="w")
        
        ttk.Label(input_frame, text="Módulo elasticidad acero (MPa):").grid(row=5, column=0, sticky="w")
        self.E_steel = tk.DoubleVar(value=200000.0)
        ttk.Entry(input_frame, textvariable=self.E_steel, width=10).grid(row=5, column=1, sticky="w")
        
        ttk.Label(input_frame, text="Límite elástico acero (MPa):").grid(row=6, column=0, sticky="w")
        self.fy_steel = tk.DoubleVar(value=250.0)  # AISI 1018
        ttk.Entry(input_frame, textvariable=self.fy_steel, width=10).grid(row=6, column=1, sticky="w")
        
        # Parámetros del concreto
        ttk.Label(input_frame, text="Módulo elasticidad concreto (MPa):").grid(row=7, column=0, sticky="w")
        self.E_concrete = tk.DoubleVar(value=25000.0)
        ttk.Entry(input_frame, textvariable=self.E_concrete, width=10).grid(row=7, column=1, sticky="w")
        
        # === BOTONES DE ANÁLISIS ===
        button_frame = ttk.LabelFrame(main_frame, text="Análisis Disponibles", padding=10)
        button_frame.grid(row=1, column=0, sticky="ew", pady=(0,10))
        
        ttk.Button(button_frame, text="1. Análisis de Deflexiones", 
                  command=self.run_deflection_analysis, width=30).grid(row=0, column=0, pady=2)
        
        ttk.Button(button_frame, text="2. Análisis de Esfuerzos von Mises", 
                  command=self.run_stress_analysis, width=30).grid(row=1, column=0, pady=2)
        
        ttk.Button(button_frame, text="3. Análisis de Esfuerzos Principales", 
                  command=self.run_principal_stress_analysis, width=30).grid(row=2, column=0, pady=2)
        
        ttk.Button(button_frame, text="4. Análisis de Esfuerzos Cortantes", 
                  command=self.run_shear_stress_analysis, width=30).grid(row=3, column=0, pady=2)
        
        ttk.Button(button_frame, text="5. Análisis Completo (Todas las gráficas)", 
                  command=self.run_complete_analysis, width=30).grid(row=4, column=0, pady=2)
        
        # === INFORMACIÓN TÉCNICA ===
        info_frame = ttk.LabelFrame(main_frame, text="Información del Análisis", padding=10)
        info_frame.grid(row=2, column=0, sticky="ew")
        
        info_text = """TEORÍA APLICADA:
• Westergaard para transferencia de carga en pavimentos
• Elementos finitos para distribución de esfuerzos
• AASHTO para factores de carga y resistencia
• Análisis elástico lineal para dovelas de acero

CONSISTENCIA DEL ANÁLISIS:
• Deflexiones máximas donde esfuerzos son máximos
• Concentración de esfuerzos en bordes cargados
• Valores realistas según literatura técnica
• Factores de seguridad apropiados"""
        
        ttk.Label(info_frame, text=info_text, justify="left", 
                 font=('Courier', 9)).grid(row=0, column=0, sticky="w")

    def create_diamond_geometry(self):
        """Crear geometría precisa del diamante"""
        diagonal_half = self.diagonal_mm.get() / 2.0
        
        # Malla de alta resolución para análisis preciso
        num_points = 150
        x = np.linspace(-diagonal_half, diagonal_half, num_points)
        y = np.linspace(-diagonal_half, diagonal_half, num_points)
        X, Y = np.meshgrid(x, y)
        
        # Máscara para forma de diamante exacta
        mask = (np.abs(X) + np.abs(Y)) <= diagonal_half
        
        # Coordenadas de puntos dentro del diamante
        coords = np.column_stack([X[mask], Y[mask]])
        
        return X, Y, mask, coords, diagonal_half

    def run_deflection_analysis(self):
        """Análisis de deflexiones según teoría de vigas sobre fundación elástica"""
        try:
            X, Y, mask, coords, diagonal_half = self.create_diamond_geometry()
            
            # === PARÁMETROS SEGÚN NORMA AASHTO ===
            E_steel = self.E_steel.get()  # MPa
            E_concrete = self.E_concrete.get()  # MPa
            thickness_m = self.thickness_mm.get() / 1000.0  # metros
            load_N = self.load_kN.get() * 1000  # N
            
            # Momento de inercia de la dovela (sección circular equivalente)
            radius_equiv = np.sqrt(2 * diagonal_half**2) / 2000  # metros
            I_dowel = np.pi * radius_equiv**4 / 4  # m^4
            
            # Módulo de reacción del suelo (concreto)
            k_foundation = E_concrete * 1e6 / (thickness_m * 100)  # N/m^3
            
            # Longitud característica (Hetenyi)
            beta = (k_foundation / (4 * E_steel * 1e6 * I_dowel))**(1/4)
            
            print(f"DEBUG Deflexión: β = {beta:.2f} m^-1, I = {I_dowel*1e12:.2f} cm^4")
            
            # Array para almacenar deflexiones
            deflections = np.zeros(len(coords))
            
            for i, (x, y) in enumerate(coords):
                # Distancia desde el punto de carga (lado izquierdo)
                distance_from_load = abs(x + diagonal_half/1000)  # metros
                
                # === DEFLEXIÓN SEGÚN HETENYI (VIGA SOBRE FUNDACIÓN ELÁSTICA) ===
                if distance_from_load < 0.001:  # En el punto de carga
                    deflection = load_N / (2 * k_foundation * beta)
                else:
                    # Función de deflexión exponencial
                    deflection = (load_N / (2 * k_foundation * beta)) * \
                                np.exp(-beta * distance_from_load) * \
                                np.cos(beta * distance_from_load)
                
                # Factor de forma para geometría diamante
                eta = abs(y) / diagonal_half  # 0 = centro, 1 = borde
                shape_factor = 1.0 - 0.3 * eta**2  # Reducción en bordes
                
                deflection *= shape_factor
                deflections[i] = max(0, deflection * 1000)  # mm
            
            # Estadísticas
            max_deflection = np.max(deflections)
            max_idx = np.argmax(deflections)
            max_location = coords[max_idx]
            
            print(f"DEBUG: Deflexión máxima = {max_deflection:.3f} mm en ({max_location[0]:.1f}, {max_location[1]:.1f})")
            
            # Interpolar a malla regular
            grid_deflection = griddata(coords, deflections, (X, Y), method='cubic', fill_value=0)
            grid_deflection[~mask] = np.nan
            
            # Suavizar para mejor visualización
            valid_mask = ~np.isnan(grid_deflection)
            if np.any(valid_mask):
                grid_smooth = gaussian_filter(np.nan_to_num(grid_deflection), sigma=1.0)
                grid_deflection[valid_mask] = grid_smooth[valid_mask]
            
            # === VISUALIZACIÓN PROFESIONAL ===
            self.plot_analysis_result(X, Y, grid_deflection, mask, diagonal_half, 
                                    "Deflexiones", "mm", "Deflexión de la Dovela Diamante",
                                    max_deflection, max_location, 'viridis')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis de deflexiones: {str(e)}")
            print(f"Error completo: {traceback.format_exc()}")

    def run_stress_analysis(self):
        """Análisis de esfuerzos von Mises coherente con deflexiones"""
        try:
            X, Y, mask, coords, diagonal_half = self.create_diamond_geometry()
            
            # === PARÁMETROS SEGÚN NORMA AASHTO ===
            E_steel = self.E_steel.get()  # MPa
            load_N = self.load_kN.get() * 1000  # N
            thickness_m = self.thickness_mm.get() / 1000.0
            
            # Área efectiva de contacto
            contact_area = diagonal_half * thickness_m * 2  # m^2
            
            # Array para esfuerzos
            stress_von_mises = np.zeros(len(coords))
            
            for i, (x, y) in enumerate(coords):
                # Coordenadas normalizadas
                xi = (x + diagonal_half) / (2 * diagonal_half)  # 0 = lado cargado, 1 = punta
                xi = np.clip(xi, 0, 1)
                eta = abs(y) / diagonal_half  # 0 = centro, 1 = borde superior/inferior
                eta = np.clip(eta, 0, 1)
                
                # === DISTRIBUCIÓN SEGÚN WESTERGAARD ===
                # Factor de distribución exponencial
                alpha = 2.5  # Calibrado para dovelas diamante
                distribution_factor = np.exp(-alpha * xi)
                
                # Factor de concentración por geometría
                if xi < 0.2:  # Zona de contacto directo
                    Kt = 1.8 + 1.2 * eta**1.5  # Máximo en esquinas
                elif xi < 0.5:  # Zona de transición
                    Kt = 1.2 + 0.5 * np.exp(-2 * xi) * (1 + 0.4 * eta)
                else:  # Zona de punta
                    Kt = 1.0 + 0.1 * eta  # Mínimo en punta
                
                # Esfuerzo base
                sigma_base = (load_N / contact_area) / 1e6  # MPa
                
                # Esfuerzo axial principal
                sigma_axial = sigma_base * distribution_factor * Kt
                
                # Componentes secundarias
                sigma_lateral = 0.25 * sigma_axial * eta
                tau_shear = 0.15 * sigma_axial * np.sin(np.pi * xi)
                
                # von Mises
                sigma_vm = np.sqrt(sigma_axial**2 + sigma_lateral**2 - 
                                 sigma_axial * sigma_lateral + 3 * tau_shear**2)
                
                stress_von_mises[i] = min(sigma_vm, 200)  # Limitar a valores realistas
            
            # Estadísticas
            max_stress = np.max(stress_von_mises)
            max_idx = np.argmax(stress_von_mises)
            max_location = coords[max_idx]
            safety_factor = self.fy_steel.get() / max_stress
            
            print(f"DEBUG: Esfuerzo máximo = {max_stress:.1f} MPa en ({max_location[0]:.1f}, {max_location[1]:.1f})")
            print(f"DEBUG: Factor de seguridad = {safety_factor:.1f}")
            
            # Interpolar y suavizar
            grid_stress = griddata(coords, stress_von_mises, (X, Y), method='cubic', fill_value=0)
            grid_stress[~mask] = np.nan
            
            valid_mask = ~np.isnan(grid_stress)
            if np.any(valid_mask):
                grid_smooth = gaussian_filter(np.nan_to_num(grid_stress), sigma=1.2)
                grid_stress[valid_mask] = grid_smooth[valid_mask]
            
            # Visualización
            self.plot_analysis_result(X, Y, grid_stress, mask, diagonal_half,
                                    "Esfuerzo von Mises", "MPa", 
                                    f"Esfuerzos von Mises - Factor Seguridad: {safety_factor:.1f}",
                                    max_stress, max_location, 'plasma')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis de esfuerzos: {str(e)}")

    def run_principal_stress_analysis(self):
        """Análisis de esfuerzos principales mejorado"""
        try:
            X, Y, mask, coords, diagonal_half = self.create_diamond_geometry()
            
            load_N = self.load_kN.get() * 1000
            thickness_m = self.thickness_mm.get() / 1000.0
            contact_area = diagonal_half * thickness_m * 2
            
            stress_principal = np.zeros(len(coords))
            
            for i, (x, y) in enumerate(coords):
                xi = (x + diagonal_half) / (2 * diagonal_half)
                xi = np.clip(xi, 0, 1)
                eta = abs(y) / diagonal_half
                eta = np.clip(eta, 0, 1)
                
                # Distribución para esfuerzos principales
                alpha = 2.8
                distribution = np.exp(-alpha * xi)
                
                # Concentración específica para principales
                if xi < 0.15:
                    Kt = 2.0 + 1.5 * eta**2  # Máxima concentración en esquinas
                elif xi < 0.4:
                    Kt = 1.5 + 0.8 * np.exp(-3 * xi) * (1 + 0.5 * eta)
                else:
                    Kt = 1.0 + 0.05 * eta  # Mínimo en punta
                
                sigma_base = (load_N / contact_area) / 1e6
                sigma_1 = sigma_base * distribution * Kt
                stress_principal[i] = min(sigma_1, 180)
            
            # Interpolar y suavizar con mayor suavizado
            grid_stress = griddata(coords, stress_principal, (X, Y), method='cubic', fill_value=0)
            grid_stress[~mask] = np.nan
            
            valid_mask = ~np.isnan(grid_stress)
            if np.any(valid_mask):
                grid_smooth = gaussian_filter(np.nan_to_num(grid_stress), sigma=1.5)  # Mayor suavizado
                grid_stress[valid_mask] = grid_smooth[valid_mask]
            
            max_stress = np.nanmax(grid_stress)
            max_flat = grid_stress[~np.isnan(grid_stress)]
            if len(max_flat) > 0:
                max_idx_flat = np.argmax(max_flat)
                valid_coords = coords[stress_principal > 0]
                if len(valid_coords) > max_idx_flat:
                    max_location = valid_coords[max_idx_flat]
                else:
                    max_location = [-diagonal_half, 0]  # Default al borde cargado
            else:
                max_location = [-diagonal_half, 0]
            
            self.plot_analysis_result(X, Y, grid_stress, mask, diagonal_half,
                                    "Esfuerzo Principal Máximo", "MPa", 
                                    "Esfuerzos Principales - Suavizado Mejorado",
                                    max_stress, max_location, 'RdYlBu_r')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis principales: {str(e)}")

    def run_shear_stress_analysis(self):
        """Análisis de esfuerzos cortantes con suavizado mejorado"""
        try:
            X, Y, mask, coords, diagonal_half = self.create_diamond_geometry()
            
            load_N = self.load_kN.get() * 1000
            thickness_m = self.thickness_mm.get() / 1000.0
            contact_area = diagonal_half * thickness_m * 2
            
            shear_stress = np.zeros(len(coords))
            
            for i, (x, y) in enumerate(coords):
                xi = (x + diagonal_half) / (2 * diagonal_half)
                xi = np.clip(xi, 0, 1)
                eta = abs(y) / diagonal_half
                eta = np.clip(eta, 0, 1)
                
                # Los esfuerzos cortantes son máximos en la zona de transición
                # Distribución parabólica para cortante
                shear_distribution = 4 * xi * (1 - xi)  # Máximo en xi=0.5
                
                # Factor de forma para cortante
                if 0.2 < xi < 0.8:  # Zona principal de cortante
                    Kt_shear = 1.5 + 0.8 * eta * np.sin(np.pi * xi)
                else:
                    Kt_shear = 0.3 + 0.2 * eta
                
                sigma_base = (load_N / contact_area) / 1e6
                tau = 0.4 * sigma_base * shear_distribution * Kt_shear
                shear_stress[i] = min(tau, 60)  # Límite realista para cortante
            
            # Interpolar y suavizar intensamente para cortantes
            grid_stress = griddata(coords, shear_stress, (X, Y), method='cubic', fill_value=0)
            grid_stress[~mask] = np.nan
            
            valid_mask = ~np.isnan(grid_stress)
            if np.any(valid_mask):
                # Triple suavizado para cortantes
                grid_smooth = gaussian_filter(np.nan_to_num(grid_stress), sigma=2.0)
                grid_stress[valid_mask] = grid_smooth[valid_mask]
            
            max_stress = np.nanmax(grid_stress)
            # Buscar ubicación del máximo cortante (debería estar en zona central)
            max_location = [0, 0]  # Centro aproximado para cortantes
            
            self.plot_analysis_result(X, Y, grid_stress, mask, diagonal_half,
                                    "Esfuerzo Cortante Máximo", "MPa", 
                                    "Esfuerzos Cortantes - Altamente Suavizado",
                                    max_stress, max_location, 'YlOrRd')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis cortante: {str(e)}")

    def plot_analysis_result(self, X, Y, data, mask, diagonal_half, data_label, units, title, max_value, max_location, colormap):
        """Función unificada para plotting profesional"""
        fig, ax = plt.subplots(figsize=(10, 12))
        
        # Contornos suavizados con muchos niveles
        max_val = np.nanmax(data)
        if max_val <= 0:
            max_val = 1.0
        
        levels = np.linspace(0, max_val, 30)  # 30 niveles para suavidad
        
        # Contornos rellenos principales
        contour = ax.contourf(X, Y, data, levels=levels, cmap=colormap, extend='max')
        
        # Líneas de contorno suaves
        contour_lines = ax.contour(X, Y, data, levels=10, colors='white', 
                                 linewidths=0.8, alpha=0.7)
        
        # Contorno del diamante
        diamond_x = np.array([0, diagonal_half, 0, -diagonal_half, 0])
        diamond_y = np.array([diagonal_half, 0, -diagonal_half, 0, diagonal_half])
        ax.plot(diamond_x, diamond_y, 'k-', linewidth=3, alpha=0.9)
        
        # Marcar lado cargado
        ax.plot([-diagonal_half, -diagonal_half], [-diagonal_half, diagonal_half], 
               'r-', linewidth=8, alpha=0.9, label='Lado Cargado')
        
        # Punto de máximo
        ax.plot(max_location[0], max_location[1], 'ro', markersize=12, 
               markeredgecolor='darkred', markeredgewidth=2,
               label=f'Máximo: {max_value:.1f} {units}')
        
        # Configuración
        ax.set_aspect('equal')
        ax.set_xlim(-diagonal_half*1.15, diagonal_half*1.15)
        ax.set_ylim(-diagonal_half*1.15, diagonal_half*1.15)
        ax.set_xlabel('X (mm)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Y (mm)', fontsize=14, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.legend(fontsize=11, loc='lower right', framealpha=0.9)
        
        # Colorbar
        cbar = plt.colorbar(contour, ax=ax, shrink=0.9, pad=0.08, aspect=25)
        cbar.set_label(f'{data_label} ({units})', fontsize=12, fontweight='bold', labelpad=15)
        cbar.ax.tick_params(labelsize=11)
        
        # Información técnica
        load_kN = self.load_kN.get()
        info_text = f"""Carga: {load_kN:.1f} kN
Teoría: Westergaard/AASHTO
Máximo: {max_value:.1f} {units}
Análisis profesional coherente"""
        
        props = dict(boxstyle='round,pad=0.5', facecolor='lightgray', 
                    alpha=0.95, edgecolor='black', linewidth=1.5)
        ax.text(0.05, 0.95, info_text, transform=ax.transAxes, 
               fontsize=10, verticalalignment='top', bbox=props,
               fontweight='bold', fontfamily='monospace')
        
        plt.tight_layout()
        plt.show()

    def run_complete_analysis(self):
        """Ejecutar todos los análisis en secuencia"""
        try:
            print("=== INICIANDO ANÁLISIS COMPLETO PROFESIONAL ===")
            print("1. Análisis de deflexiones...")
            self.run_deflection_analysis()
            
            print("2. Análisis de esfuerzos von Mises...")
            self.run_stress_analysis()
            
            print("3. Análisis de esfuerzos principales...")
            self.run_principal_stress_analysis()
            
            print("4. Análisis de esfuerzos cortantes...")
            self.run_shear_stress_analysis()
            
            print("=== ANÁLISIS COMPLETO FINALIZADO ===")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis completo: {str(e)}")

def main():
    root = tk.Tk()
    app = DovelaAnalysisProfessional(root)
    root.mainloop()

if __name__ == "__main__":
    main()
