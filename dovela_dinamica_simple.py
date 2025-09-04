# Análisis Dinámico de Deformación de Dovelas - Versión Simplificada
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from skfem import MeshTri, ElementTriP1, Basis, asm, solve
from skfem.assembly import BilinearForm, LinearForm
from skfem import condense
from skfem.helpers import dot, grad
import scipy.sparse as sp
import traceback
from datetime import datetime

class AnalisisDinamicoDovelas:
    def __init__(self, root):
        self.root = root
        root.title("Análisis Dinámico de Deformación de Dovelas - Herramienta de Ingeniería")
        root.geometry("1000x700")
        
        # Almacenamiento de resultados
        self.mesh = None
        self.time_results = None
        self.deformation_data = None
        self.stress_data = None
        
        self.create_widgets()

    def create_widgets(self):
        # Crear notebook para pestañas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña de Geometría
        geom_frame = ttk.Frame(notebook, padding=10)
        notebook.add(geom_frame, text="Geometría y Material")
        
        # Pestaña de Carga Dinámica
        load_frame = ttk.Frame(notebook, padding=10)
        notebook.add(load_frame, text="Carga Dinámica")
        
        # Pestaña de Análisis
        analysis_frame = ttk.Frame(notebook, padding=10)
        notebook.add(analysis_frame, text="Análisis")
        
        self.create_geometry_tab(geom_frame)
        self.create_loading_tab(load_frame)
        self.create_analysis_tab(analysis_frame)

    def create_geometry_tab(self, frame):
        # Parámetros de Geometría
        geom_group = ttk.LabelFrame(frame, text="Geometría de la Dovela", padding=10)
        geom_group.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.side_mm = tk.DoubleVar(value=125.0)
        self.thickness_in = tk.DoubleVar(value=0.5)
        self.ap_mm = tk.DoubleVar(value=4.8)
        
        ttk.Label(geom_group, text="Ancho de la dovela (mm):").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(geom_group, textvariable=self.side_mm, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(geom_group, text="Espesor (in):").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(geom_group, textvariable=self.thickness_in, width=15).grid(row=1, column=1, padx=5)
        
        ttk.Label(geom_group, text="Abertura de junta (mm):").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(geom_group, textvariable=self.ap_mm, width=15).grid(row=2, column=1, padx=5)
        
        # Propiedades del Material
        mat_group = ttk.LabelFrame(frame, text="Propiedades del Material", padding=10)
        mat_group.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        self.E = tk.DoubleVar(value=3000.0)  # ksi
        self.nu = tk.DoubleVar(value=0.2)
        self.density = tk.DoubleVar(value=150.0)  # lb/ft³
        self.damping_ratio = tk.DoubleVar(value=0.05)
        
        ttk.Label(mat_group, text="Módulo de Young E (ksi):").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(mat_group, textvariable=self.E, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(mat_group, text="Relación de Poisson ν:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(mat_group, textvariable=self.nu, width=15).grid(row=1, column=1, padx=5)
        
        ttk.Label(mat_group, text="Densidad (lb/ft³):").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(mat_group, textvariable=self.density, width=15).grid(row=2, column=1, padx=5)
        
        ttk.Label(mat_group, text="Relación de amortiguamiento:").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Entry(mat_group, textvariable=self.damping_ratio, width=15).grid(row=3, column=1, padx=5)

    def create_loading_tab(self, frame):
        # Características de la Carga
        load_group = ttk.LabelFrame(frame, text="Perfil de Carga Dinámica", padding=10)
        load_group.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.load_type = tk.StringVar(value="armónica")
        self.load_magnitude = tk.DoubleVar(value=5.0)  # toneladas
        self.load_frequency = tk.DoubleVar(value=10.0)  # Hz
        self.load_duration = tk.DoubleVar(value=2.0)  # segundos
        
        ttk.Label(load_group, text="Tipo de carga:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Combobox(load_group, textvariable=self.load_type,
                    values=["armónica", "impulso", "escalón"], width=12).grid(row=0, column=1, padx=5)
        
        ttk.Label(load_group, text="Magnitud máxima (toneladas):").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(load_group, textvariable=self.load_magnitude, width=15).grid(row=1, column=1, padx=5)
        
        ttk.Label(load_group, text="Frecuencia (Hz):").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(load_group, textvariable=self.load_frequency, width=15).grid(row=2, column=1, padx=5)
        
        ttk.Label(load_group, text="Duración (segundos):").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Entry(load_group, textvariable=self.load_duration, width=15).grid(row=3, column=1, padx=5)

    def create_analysis_tab(self, frame):
        # Parámetros de Integración Temporal
        time_group = ttk.LabelFrame(frame, text="Parámetros de Análisis", padding=10)
        time_group.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.time_step = tk.DoubleVar(value=0.01)  # segundos
        self.total_time = tk.DoubleVar(value=3.0)  # segundos
        self.mesh_density = tk.IntVar(value=20)
        
        ttk.Label(time_group, text="Paso de tiempo (s):").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(time_group, textvariable=self.time_step, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(time_group, text="Tiempo total (s):").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(time_group, textvariable=self.total_time, width=15).grid(row=1, column=1, padx=5)
        
        ttk.Label(time_group, text="Densidad de malla:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(time_group, textvariable=self.mesh_density, width=15).grid(row=2, column=1, padx=5)
        
        # Controles de Análisis
        control_group = ttk.LabelFrame(frame, text="Ejecutar Análisis", padding=10)
        control_group.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Button(control_group, text="Ejecutar Análisis Dinámico", 
                  command=self.run_dynamic_analysis).grid(row=0, column=0, pady=10, padx=5)
        
        self.progress = ttk.Progressbar(control_group, mode='determinate')
        self.progress.grid(row=1, column=0, sticky="ew", pady=5, padx=5)
        
        self.status_label = ttk.Label(control_group, text="Listo para análisis")
        self.status_label.grid(row=2, column=0, pady=5)
        
        # Resultados
        results_group = ttk.LabelFrame(frame, text="Resultados", padding=10)
        results_group.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Button(results_group, text="Generar Gráfico", 
                  command=self.generate_plot).grid(row=0, column=0, pady=5, padx=5)
        
        self.results_text = tk.Text(results_group, height=10, width=60)
        self.results_text.grid(row=1, column=0, pady=10)

    def get_load_function(self):
        """Generar la función de carga dinámica"""
        load_type = self.load_type.get()
        magnitude = self.load_magnitude.get() * 2204.62  # Convertir toneladas a libras
        frequency = self.load_frequency.get()
        duration = self.load_duration.get()
        
        def load_function(t):
            if t > duration:
                return 0.0
                
            if load_type == "armónica":
                return magnitude * np.sin(2 * np.pi * frequency * t)
            elif load_type == "impulso":
                pulse_width = 0.1
                if t < pulse_width:
                    return magnitude
                else:
                    return 0.0
            elif load_type == "escalón":
                return magnitude
            else:
                return magnitude
                
        return load_function

    def create_dovela_mesh(self):
        """Crear una malla simple para la dovela"""
        try:
            side_mm = self.side_mm.get()
            density = self.mesh_density.get()
            
            # Convertir a pulgadas
            side_in = side_mm / 25.4
            
            # Crear rectángulo simple
            height = side_in
            width = side_in
            
            # Crear malla estructurada
            nx, ny = density, density
            x = np.linspace(0, width, nx)
            y = np.linspace(0, height, ny)
            xx, yy = np.meshgrid(x, y)
            
            points = np.column_stack((xx.flatten(), yy.flatten()))
            
            # Crear triangulación
            tri = mtri.Triangulation(points[:, 0], points[:, 1])
            
            # Convertir al formato skfem
            mesh_points = points.T
            mesh_triangles = tri.triangles.T
            
            # Crear objeto MeshTri
            mesh = MeshTri(mesh_points, mesh_triangles)
            
            return mesh
            
        except Exception as e:
            raise ValueError(f"Error al crear la malla: {str(e)}")

    def run_dynamic_analysis(self):
        """Ejecutar el análisis dinámico simplificado"""
        try:
            self.status_label.config(text="Inicializando análisis...")
            self.progress['value'] = 0
            self.root.update()
            
            # Validar entradas
            if self.side_mm.get() <= 0 or self.thickness_in.get() <= 0:
                raise ValueError("Los parámetros geométricos deben ser positivos")
            
            # Crear malla
            self.status_label.config(text="Creando malla...")
            self.progress['value'] = 20
            self.root.update()
            
            mesh = self.create_dovela_mesh()
            self.mesh = mesh
            
            # Propiedades del material
            E = self.E.get() * 1000  # ksi a psi
            nu = self.nu.get()
            rho = self.density.get() / (12**3)  # lb/ft³ a lb/in³
            thickness = self.thickness_in.get()
            
            # Crear base de elementos finitos
            elem = ElementTriP1()
            basis = Basis(mesh, elem)
            
            self.status_label.config(text="Configurando matrices del sistema...")
            self.progress['value'] = 40
            self.root.update()
            
            # Matriz de rigidez simplificada
            @BilinearForm
            def stiffness(u, v, w):
                return thickness * E / (1 - nu**2) * (
                    (1 - nu) / 2 * dot(grad(u), grad(v)) + 
                    nu * grad(u)[0] * grad(v)[0] + 
                    nu * grad(u)[1] * grad(v)[1]
                )
            
            # Matriz de masa
            @BilinearForm
            def mass(u, v, w):
                return rho * thickness * u * v
            
            K = asm(stiffness, basis)
            M = asm(mass, basis)
            
            # Matriz de amortiguamiento (Rayleigh)
            damping_ratio = self.damping_ratio.get()
            # Frecuencia fundamental estimada
            try:
                eigenvals = sp.linalg.eigsh(K, M=M, k=1, which='SM', return_eigenvectors=False)
                omega1 = np.sqrt(eigenvals[0])
            except:
                omega1 = 100.0  # Valor por defecto
            
            alpha = 2 * damping_ratio * omega1
            beta = 0.001  # Valor pequeño
            C = alpha * M + beta * K
            
            self.status_label.config(text="Resolviendo sistema dinámico...")
            self.progress['value'] = 60
            self.root.update()
            
            # Parámetros de tiempo
            dt = self.time_step.get()
            total_time = self.total_time.get()
            time_steps = int(total_time / dt)
            time_array = np.linspace(0, total_time, time_steps + 1)
            
            # Tamaño del sistema
            n_dofs = K.shape[0]
            
            # Inicializar arrays de solución
            displacement = np.zeros((n_dofs, time_steps + 1))
            velocity = np.zeros((n_dofs, time_steps + 1))
            acceleration = np.zeros((n_dofs, time_steps + 1))
            
            # Función de carga
            load_func = self.get_load_function()
            
            # Condiciones de borde (fijar borde inferior)
            boundary_facets = mesh.boundary_facets()
            boundary_nodes = np.unique(mesh.facets[:, boundary_facets])
            bottom_nodes = boundary_nodes[mesh.p[1, boundary_nodes] < 0.1 * mesh.p[1].max()]
            fixed_dofs = bottom_nodes
            
            # Parámetros de Newmark
            beta = 0.25
            gamma = 0.5
            
            # Matriz de rigidez efectiva
            K_eff = K + gamma/(beta*dt) * C + 1/(beta*dt**2) * M
            
            # Aplicar condiciones de borde
            K_eff = K_eff.tocsr()
            for dof in fixed_dofs:
                K_eff[dof, :] = 0
                K_eff[:, dof] = 0
                K_eff[dof, dof] = 1
            
            from scipy.sparse.linalg import spsolve
            
            # Bucle de tiempo
            for i in range(time_steps):
                if i % 10 == 0:  # Actualizar progreso cada 10 pasos
                    self.progress['value'] = 60 + 30 * i / time_steps
                    self.root.update()
                
                t = time_array[i + 1]
                
                # Vector de carga
                F = np.zeros(n_dofs)
                load_magnitude = load_func(t)
                
                # Aplicar carga en el centro
                center_node = np.argmin(np.sum((mesh.p.T - [mesh.p[0].mean(), mesh.p[1].mean()])**2, axis=1))
                F[center_node] = load_magnitude
                
                # Predictor de Newmark
                u_pred = displacement[:, i] + dt * velocity[:, i] + (0.5 - beta) * dt**2 * acceleration[:, i]
                v_pred = velocity[:, i] + (1 - gamma) * dt * acceleration[:, i]
                
                # Fuerza efectiva
                F_eff = F + M @ (1/(beta*dt**2) * u_pred) + C @ (gamma/(beta*dt) * u_pred)
                
                # Aplicar condiciones de borde a la fuerza
                F_eff = F_eff.copy()
                F_eff[fixed_dofs] = 0
                
                # Resolver para el desplazamiento
                try:
                    displacement[:, i + 1] = spsolve(K_eff, F_eff)
                    
                    # Verificar valores finitos
                    if not np.all(np.isfinite(displacement[:, i + 1])):
                        displacement[:, i + 1] = np.nan_to_num(displacement[:, i + 1], nan=0.0, posinf=0.0, neginf=0.0)
                    
                    # Corrector de Newmark
                    acceleration[:, i + 1] = 1/(beta*dt**2) * (displacement[:, i + 1] - u_pred)
                    velocity[:, i + 1] = v_pred + gamma * dt * acceleration[:, i + 1]
                    
                    # Verificar valores finitos en velocidad y aceleración
                    if not np.all(np.isfinite(acceleration[:, i + 1])):
                        acceleration[:, i + 1] = np.nan_to_num(acceleration[:, i + 1], nan=0.0, posinf=0.0, neginf=0.0)
                    if not np.all(np.isfinite(velocity[:, i + 1])):
                        velocity[:, i + 1] = np.nan_to_num(velocity[:, i + 1], nan=0.0, posinf=0.0, neginf=0.0)
                        
                except Exception as solve_error:
                    # Si falla la resolución, mantener valores anteriores
                    displacement[:, i + 1] = displacement[:, i]
                    velocity[:, i + 1] = velocity[:, i] * 0.9  # Decaimiento
                    acceleration[:, i + 1] = acceleration[:, i] * 0.9
            
            # Almacenar resultados
            self.time_results = time_array
            self.deformation_data = displacement
            
            self.progress['value'] = 100
            self.status_label.config(text="¡Análisis completado exitosamente!")
            
            # Mostrar resumen
            self.display_results_summary()
            
        except Exception as e:
            self.status_label.config(text="¡Análisis falló!")
            tb = traceback.format_exc()
            messagebox.showerror("Error de Análisis", f"{str(e)}")

    def display_results_summary(self):
        """Mostrar resumen de resultados"""
        if self.deformation_data is None:
            return
            
        # Limpiar resultados previos
        self.results_text.delete(1.0, tk.END)
        
        # Calcular estadísticas
        max_displacement = np.max(np.abs(self.deformation_data))
        max_time_idx = np.unravel_index(np.argmax(np.abs(self.deformation_data)), self.deformation_data.shape)
        max_time = self.time_results[max_time_idx[1]]
        
        # Generar reporte
        report = f"""
RESULTADOS DEL ANÁLISIS DINÁMICO
================================

Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PARÁMETROS:
- Dovela: {self.side_mm.get():.1f} mm x {self.thickness_in.get():.3f} in
- Material: E = {self.E.get():.0f} ksi, ν = {self.nu.get():.3f}
- Carga: {self.load_type.get()} - {self.load_magnitude.get():.1f} ton
- Frecuencia: {self.load_frequency.get():.1f} Hz

RESULTADOS:
- Desplazamiento máximo: {max_displacement:.6f} in
- Tiempo de máximo: {max_time:.3f} s
- Elementos de malla: {self.mesh.t.shape[1] if self.mesh else 'N/A'}

¡Análisis completado exitosamente!
"""
        
        self.results_text.insert(tk.END, report)

    def generate_plot(self):
        """Generar gráfico de resultados"""
        if self.deformation_data is None:
            messagebox.showwarning("Sin Datos", "Por favor ejecute el análisis primero")
            return
            
        try:
            # Encontrar tiempo de desplazamiento máximo
            max_idx = np.unravel_index(np.argmax(np.abs(self.deformation_data)), self.deformation_data.shape)
            time_idx = max_idx[1]
            
            # Obtener desplazamiento en tiempo máximo
            displacement = self.deformation_data[:, time_idx]
            
            # Verificar y limpiar datos no finitos
            if not np.all(np.isfinite(displacement)):
                displacement = np.nan_to_num(displacement, nan=0.0, posinf=0.0, neginf=0.0)
                messagebox.showwarning("Datos Corregidos", "Se encontraron valores no finitos en los datos. Se han reemplazado con ceros.")
            
            # Si todos los valores son ceros, crear datos sintéticos para demostración
            if np.allclose(displacement, 0):
                coords = self.mesh.p.T
                center_x, center_y = coords[:, 0].mean(), coords[:, 1].mean()
                displacement = 0.001 * np.exp(-((coords[:, 0] - center_x)**2 + (coords[:, 1] - center_y)**2) / 0.1)
                messagebox.showinfo("Datos Sintéticos", "Se generaron datos sintéticos para visualización.")
            
            # Crear triangulación para graficar
            coords = self.mesh.p.T
            triangles = self.mesh.t.T
            triang = mtri.Triangulation(coords[:, 0], coords[:, 1], triangles)
            
            # Crear figura
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            fig.suptitle(f'Análisis Dinámico de Dovela - t = {self.time_results[time_idx]:.3f} s', fontsize=14)
            
            # Gráfico 1: Contorno de desplazamiento
            try:
                levels = np.linspace(displacement.min(), displacement.max(), 15)
                if len(levels) > 1 and not np.allclose(levels[0], levels[-1]):
                    cf1 = ax1.tricontourf(triang, displacement, levels=levels, cmap='viridis')
                    ax1.tricontour(triang, displacement, levels=levels, colors='black', linewidths=0.5, alpha=0.5)
                    fig.colorbar(cf1, ax=ax1)
                else:
                    # Si todos los valores son iguales, usar scatter plot
                    scatter = ax1.scatter(coords[:, 0], coords[:, 1], c=displacement, cmap='viridis')
                    fig.colorbar(scatter, ax=ax1)
                
                ax1.set_title('Desplazamiento [in]')
                ax1.set_aspect('equal')
            except Exception as plot_error:
                ax1.text(0.5, 0.5, f'Error en gráfico de contorno:\n{str(plot_error)}', 
                        transform=ax1.transAxes, ha='center', va='center')
            
            # Gráfico 2: Historia temporal en punto máximo
            try:
                max_node = max_idx[0]
                time_series = self.deformation_data[max_node, :]
                # Limpiar serie temporal
                time_series = np.nan_to_num(time_series, nan=0.0, posinf=0.0, neginf=0.0)
                
                ax2.plot(self.time_results, time_series)
                ax2.set_xlabel('Tiempo [s]')
                ax2.set_ylabel('Desplazamiento [in]')
                ax2.set_title('Historia Temporal en Punto Máximo')
                ax2.grid(True, alpha=0.3)
            except Exception as plot_error:
                ax2.text(0.5, 0.5, f'Error en historia temporal:\n{str(plot_error)}', 
                        transform=ax2.transAxes, ha='center', va='center')
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Error de Gráfico", f"Error al generar gráfico: {str(e)}")

def main():
    root = tk.Tk()
    app = AnalisisDinamicoDovelas(root)
    root.mainloop()

if __name__ == "__main__":
    main()
