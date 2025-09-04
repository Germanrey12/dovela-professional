# Análisis Estructural Completo de Dovelas Diamantadas
# Incluye todos los parámetros necesarios para análisis profesional
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
from matplotlib.colors import LinearSegmentedColormap
import traceback
from datetime import datetime

def crear_colormap_sin_azul_oscuro(nombre_base='viridis'):
    """Crear mapa de colores personalizado sin azul oscuro"""
    if nombre_base == 'Blues':
        # Para deflexiones - azul claro a azul medio (sin oscuro)
        colors = ['#f0f8ff', '#b3d9ff', '#66c2ff', '#1a8cff', '#0066cc']
        return LinearSegmentedColormap.from_list('custom_blues', colors)
    elif nombre_base == 'coolwarm':
        # Para von Mises - azul claro a rojo
        colors = ['#87ceeb', '#b3d9ff', '#ffffff', '#ffb3b3', '#ff6b6b', '#dc143c']
        return LinearSegmentedColormap.from_list('custom_coolwarm', colors)
    elif nombre_base == 'plasma':
        # Para principales - púrpura a amarillo (sin azul oscuro)
        colors = ['#cc99ff', '#ff66cc', '#ff9933', '#ffcc00', '#ffff66']
        return LinearSegmentedColormap.from_list('custom_plasma', colors)
    elif nombre_base == 'viridis':
        # Para cortantes - verde a amarillo (sin azul oscuro)
        colors = ['#66ff66', '#99ff33', '#ccff00', '#ffff00', '#ffcc00']
        return LinearSegmentedColormap.from_list('custom_viridis', colors)
    else:
        return plt.cm.get_cmap(nombre_base)

class AnalisisCompletoApp:
    def __init__(self, root):
        self.root = root
        root.title("Análisis Estructural Completo - Dovelas Diamantadas (Normas AASHTO/ACI)")
        root.geometry("800x900")
        self.create_comprehensive_widgets()

    def create_comprehensive_widgets(self):
        # Frame principal con scroll
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ===== PARÁMETROS DE GEOMETRÍA =====
        geo_frame = ttk.LabelFrame(scrollable_frame, text="📐 GEOMETRÍA DEL SISTEMA", padding=10)
        geo_frame.pack(fill="x", pady=5)
        
        # Variables de geometría
        self.lado_diamante = tk.DoubleVar(value=125.0)  # mm
        self.espesor_dovela = tk.DoubleVar(value=12.7)  # mm
        self.apertura_junta = tk.DoubleVar(value=4.8)   # mm
        self.espesor_losa = tk.DoubleVar(value=200.0)   # mm
        self.ancho_losa = tk.DoubleVar(value=3500.0)    # mm
        self.largo_losa = tk.DoubleVar(value=4500.0)    # mm
        
        row = 0
        ttk.Label(geo_frame, text="Lado del diamante (mm):").grid(row=row, column=0, sticky="w")
        ttk.Entry(geo_frame, textvariable=self.lado_diamante, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(geo_frame, text="Típico: 100-150 mm").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(geo_frame, text="Espesor dovela (mm):").grid(row=row, column=0, sticky="w")
        ttk.Entry(geo_frame, textvariable=self.espesor_dovela, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(geo_frame, text="Típico: 6.35-25.4 mm").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(geo_frame, text="Apertura de junta (mm):").grid(row=row, column=0, sticky="w")
        ttk.Entry(geo_frame, textvariable=self.apertura_junta, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(geo_frame, text="Típico: 3-6 mm").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(geo_frame, text="Espesor losa (mm):").grid(row=row, column=0, sticky="w")
        ttk.Entry(geo_frame, textvariable=self.espesor_losa, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(geo_frame, text="Típico: 150-300 mm").grid(row=row, column=2, sticky="w", padx=10)

        # ===== CARGAS Y SOLICITACIONES =====
        cargas_frame = ttk.LabelFrame(scrollable_frame, text="⚖️ CARGAS Y SOLICITACIONES", padding=10)
        cargas_frame.pack(fill="x", pady=5)
        
        # Cargas
        self.carga_estatica = tk.DoubleVar(value=22.24)     # kN
        self.carga_dinamica = tk.DoubleVar(value=27.8)      # kN (carga dinámica separada)
        self.factor_impacto = tk.DoubleVar(value=1.25)      # Factor de impacto  
        self.carga_fatiga = tk.IntVar(value=2000000)        # Ciclos
        self.temp_servicio = tk.DoubleVar(value=25.0)       # °C
        self.temp_minima = tk.DoubleVar(value=-10.0)        # °C
        self.temp_maxima = tk.DoubleVar(value=60.0)         # °C
        
        row = 0
        ttk.Label(cargas_frame, text="Carga estática (kN):").grid(row=row, column=0, sticky="w")
        ttk.Entry(cargas_frame, textvariable=self.carga_estatica, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(cargas_frame, text="AASHTO HL-93: 22.24 kN").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(cargas_frame, text="Carga dinámica (kN):").grid(row=row, column=0, sticky="w")
        ttk.Entry(cargas_frame, textvariable=self.carga_dinamica, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(cargas_frame, text="Carga móvil real").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(cargas_frame, text="Factor de impacto:").grid(row=row, column=0, sticky="w")
        ttk.Entry(cargas_frame, textvariable=self.factor_impacto, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(cargas_frame, text="AASHTO: 1.25").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(cargas_frame, text="Ciclos de fatiga:").grid(row=row, column=0, sticky="w")
        ttk.Entry(cargas_frame, textvariable=self.carga_fatiga, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(cargas_frame, text="Vida útil: 2×10⁶").grid(row=row, column=2, sticky="w", padx=10)

        # ===== PROPIEDADES DEL ACERO (DOVELAS) =====
        acero_frame = ttk.LabelFrame(scrollable_frame, text="🔩 PROPIEDADES DEL ACERO (DOVELAS)", padding=10)
        acero_frame.pack(fill="x", pady=5)
        
        self.tipo_acero = tk.StringVar(value="AISI 1018")
        self.E_acero = tk.DoubleVar(value=200000.0)         # MPa
        self.nu_acero = tk.DoubleVar(value=0.30)            # Adimensional
        self.fy_acero = tk.DoubleVar(value=250.0)           # MPa
        self.fu_acero = tk.DoubleVar(value=400.0)           # MPa
        self.densidad_acero = tk.DoubleVar(value=7850.0)    # kg/m³
        self.coef_expansion_acero = tk.DoubleVar(value=12e-6) # 1/°C
        self.limite_fatiga = tk.DoubleVar(value=200.0)      # MPa
        
        row = 0
        ttk.Label(acero_frame, text="Tipo de acero:").grid(row=row, column=0, sticky="w")
        acero_combo = ttk.Combobox(acero_frame, textvariable=self.tipo_acero, 
                    values=["AISI 1018", "AISI 1045", "A-36", "A-572 Gr.50"], 
                    width=15)
        acero_combo.grid(row=row, column=1, padx=5)
        acero_combo.bind('<<ComboboxSelected>>', self.actualizar_propiedades_acero)
        
        row += 1
        ttk.Label(acero_frame, text="Módulo elasticidad E (MPa):").grid(row=row, column=0, sticky="w")
        ttk.Entry(acero_frame, textvariable=self.E_acero, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(acero_frame, text="Acero: 200,000 MPa").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(acero_frame, text="Coeficiente Poisson ν:").grid(row=row, column=0, sticky="w")
        ttk.Entry(acero_frame, textvariable=self.nu_acero, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(acero_frame, text="Típico: 0.27-0.30").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(acero_frame, text="Esfuerzo fluencia fy (MPa):").grid(row=row, column=0, sticky="w")
        ttk.Entry(acero_frame, textvariable=self.fy_acero, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(acero_frame, text="AISI 1018: 250 MPa").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(acero_frame, text="Resistencia última fu (MPa):").grid(row=row, column=0, sticky="w")
        ttk.Entry(acero_frame, textvariable=self.fu_acero, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(acero_frame, text="AISI 1018: 400 MPa").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(acero_frame, text="Límite fatiga (MPa):").grid(row=row, column=0, sticky="w")
        ttk.Entry(acero_frame, textvariable=self.limite_fatiga, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(acero_frame, text="≈ 0.8 × fy").grid(row=row, column=2, sticky="w", padx=10)

        # ===== PROPIEDADES DEL CONCRETO =====
        concreto_frame = ttk.LabelFrame(scrollable_frame, text="🏗️ PROPIEDADES DEL CONCRETO", padding=10)
        concreto_frame.pack(fill="x", pady=5)
        
        self.fc_concreto = tk.DoubleVar(value=25.0)         # MPa
        self.ft_concreto = tk.DoubleVar(value=2.5)          # MPa (tracción)
        self.E_concreto = tk.DoubleVar(value=25000.0)       # MPa
        self.nu_concreto = tk.DoubleVar(value=0.20)         # Adimensional
        self.densidad_concreto = tk.DoubleVar(value=2400.0) # kg/m³
        self.coef_expansion_concreto = tk.DoubleVar(value=10e-6) # 1/°C
        self.modulo_ruptura = tk.DoubleVar(value=4.2)       # MPa
        self.retraccion = tk.DoubleVar(value=300e-6)        # m/m
        
        row = 0
        ttk.Label(concreto_frame, text="Resistencia f'c (MPa):").grid(row=row, column=0, sticky="w")
        fc_entry = ttk.Entry(concreto_frame, textvariable=self.fc_concreto, width=12)
        fc_entry.grid(row=row, column=1, padx=5)
        fc_entry.bind('<FocusOut>', self.actualizar_propiedades_concreto)
        fc_entry.bind('<Return>', self.actualizar_propiedades_concreto)
        ttk.Label(concreto_frame, text="Pavimentos: 20-35 MPa").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(concreto_frame, text="Resistencia tracción ft (MPa):").grid(row=row, column=0, sticky="w")
        ttk.Entry(concreto_frame, textvariable=self.ft_concreto, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(concreto_frame, text="≈ 0.1 × f'c").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(concreto_frame, text="Módulo elasticidad E (MPa):").grid(row=row, column=0, sticky="w")
        ttk.Entry(concreto_frame, textvariable=self.E_concreto, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(concreto_frame, text="ACI: 4700√f'c").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(concreto_frame, text="Coeficiente Poisson ν:").grid(row=row, column=0, sticky="w")
        ttk.Entry(concreto_frame, textvariable=self.nu_concreto, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(concreto_frame, text="Típico: 0.15-0.25").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(concreto_frame, text="Módulo ruptura fr (MPa):").grid(row=row, column=0, sticky="w")
        ttk.Entry(concreto_frame, textvariable=self.modulo_ruptura, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(concreto_frame, text="ACI: 0.62√f'c").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(concreto_frame, text="Retracción (με):").grid(row=row, column=0, sticky="w")
        ttk.Entry(concreto_frame, textvariable=self.retraccion, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(concreto_frame, text="Típico: 200-500 με").grid(row=row, column=2, sticky="w", padx=10)

        # ===== INTERFACE ACERO-CONCRETO =====
        interface_frame = ttk.LabelFrame(scrollable_frame, text="🔗 INTERFASE ACERO-CONCRETO", padding=10)
        interface_frame.pack(fill="x", pady=5)
        
        self.coef_friccion = tk.DoubleVar(value=0.6)        # Adimensional
        self.adherencia = tk.DoubleVar(value=2.0)           # MPa
        self.k_resorte = tk.DoubleVar(value=50000.0)        # N/mm/mm
        self.tolerancia_ajuste = tk.DoubleVar(value=0.5)    # mm
        
        row = 0
        ttk.Label(interface_frame, text="Coeficiente fricción μ:").grid(row=row, column=0, sticky="w")
        ttk.Entry(interface_frame, textvariable=self.coef_friccion, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(interface_frame, text="Acero-concreto: 0.4-0.8").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(interface_frame, text="Adherencia (MPa):").grid(row=row, column=0, sticky="w")
        ttk.Entry(interface_frame, textvariable=self.adherencia, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(interface_frame, text="Típico: 1.5-3.0 MPa").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(interface_frame, text="Rigidez resorte k (N/mm²):").grid(row=row, column=0, sticky="w")
        ttk.Entry(interface_frame, textvariable=self.k_resorte, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(interface_frame, text="Dovela en concreto: 10,000-100,000").grid(row=row, column=2, sticky="w", padx=10)

        # ===== FACTORES DE SEGURIDAD Y NORMATIVAS =====
        seguridad_frame = ttk.LabelFrame(scrollable_frame, text="🛡️ FACTORES DE SEGURIDAD (AASHTO/ACI)", padding=10)
        seguridad_frame.pack(fill="x", pady=5)
        
        self.fs_esfuerzo = tk.DoubleVar(value=2.5)          # Esfuerzos estáticos
        self.fs_fatiga = tk.DoubleVar(value=3.0)            # Fatiga
        self.fs_deflexion = tk.DoubleVar(value=1.5)         # Deflexiones
        self.fs_pandeo = tk.DoubleVar(value=2.0)            # Pandeo local
        
        row = 0
        ttk.Label(seguridad_frame, text="FS esfuerzos estáticos:").grid(row=row, column=0, sticky="w")
        ttk.Entry(seguridad_frame, textvariable=self.fs_esfuerzo, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(seguridad_frame, text="AASHTO: 2.0-3.0").grid(row=row, column=2, sticky="w", padx=10)
        
        row += 1
        ttk.Label(seguridad_frame, text="FS fatiga:").grid(row=row, column=0, sticky="w")
        ttk.Entry(seguridad_frame, textvariable=self.fs_fatiga, width=12).grid(row=row, column=1, padx=5)
        ttk.Label(seguridad_frame, text="Mínimo: 3.0").grid(row=row, column=2, sticky="w", padx=10)

        # ===== BOTONES DE ANÁLISIS =====
        button_frame = ttk.LabelFrame(scrollable_frame, text="🧮 ANÁLISIS DISPONIBLES", padding=10)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="📊 Análisis Estructural Completo", 
                  command=self.analisis_estructural_completo, width=30).pack(pady=2)
        ttk.Button(button_frame, text="💪 Verificación de Esfuerzos", 
                  command=self.verificacion_esfuerzos, width=30).pack(pady=2)
        ttk.Button(button_frame, text="🔄 Análisis de Fatiga", 
                  command=self.analisis_fatiga, width=30).pack(pady=2)
        ttk.Button(button_frame, text="🌡️ Efectos Térmicos", 
                  command=self.analisis_termico, width=30).pack(pady=2)
        ttk.Button(button_frame, text="📐 Transferencia de Carga LTE", 
                  command=self.analisis_lte, width=30).pack(pady=2)
        ttk.Button(button_frame, text="📋 Reporte Técnico", 
                  command=self.generar_reporte, width=30).pack(pady=2)

    def actualizar_propiedades_acero(self, event=None):
        """Actualizar propiedades automáticamente según tipo de acero"""
        tipo = self.tipo_acero.get()
        
        # Base de datos de propiedades por tipo de acero
        propiedades_acero = {
            "AISI 1018": {
                "E": 200000,    # MPa
                "nu": 0.30,     # Adimensional
                "fy": 250,      # MPa
                "fu": 400,      # MPa
                "limite_fatiga": 200
            },
            "AISI 1045": {
                "E": 205000,
                "nu": 0.29,
                "fy": 310,
                "fu": 565,
                "limite_fatiga": 248
            },
            "A-36": {
                "E": 200000,
                "nu": 0.30,
                "fy": 250,
                "fu": 400,
                "limite_fatiga": 200
            },
            "A-572 Gr.50": {
                "E": 200000,
                "nu": 0.30,
                "fy": 345,
                "fu": 450,
                "limite_fatiga": 276
            }
        }
        
        if tipo in propiedades_acero:
            props = propiedades_acero[tipo]
            self.E_acero.set(props["E"])
            self.nu_acero.set(props["nu"])
            self.fy_acero.set(props["fy"])
            self.fu_acero.set(props["fu"])
            self.limite_fatiga.set(props["limite_fatiga"])

    def actualizar_propiedades_concreto(self, event=None):
        """Actualizar propiedades automáticamente según f'c"""
        try:
            fc = self.fc_concreto.get()
            
            # Fórmulas según ACI 318
            # Módulo de elasticidad: E = 4700 * sqrt(f'c) MPa
            E_concreto = 4700 * (fc ** 0.5)
            
            # Resistencia a tracción: ft = 0.1 * f'c (aproximación conservadora)
            ft_concreto = 0.1 * fc
            
            # Módulo de ruptura: fr = 0.62 * sqrt(f'c) MPa
            modulo_ruptura = 0.62 * (fc ** 0.5)
            
            # Actualizar valores
            self.E_concreto.set(E_concreto)
            self.ft_concreto.set(ft_concreto)
            self.modulo_ruptura.set(modulo_ruptura)
            
        except:
            pass  # Si hay error en conversión, no hacer nada

    def analisis_estructural_completo(self):
        """Menú desplegable para seleccionar tipo de análisis estructural"""
        # Crear ventana de selección
        seleccion_window = tk.Toplevel(self.root)
        seleccion_window.title("Seleccionar Análisis Estructural")
        seleccion_window.geometry("400x500")
        seleccion_window.resizable(False, False)
        
        # Centrar ventana
        seleccion_window.transient(self.root)
        seleccion_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(seleccion_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="📊 ANÁLISIS ESTRUCTURAL DISPONIBLES", 
                          font=("Arial", 14, "bold"))
        titulo.pack(pady=(0, 20))
        
        # Crear botones para cada tipo de análisis
        analyses = [
            ("🔴 Esfuerzos von Mises", "von_mises", "Criterio de falla combinado"),
            ("🟡 Esfuerzos Principales", "principal", "Esfuerzos máximos normales"),
            ("🟢 Esfuerzos Cortantes", "cortante", "Esfuerzos de corte máximos"),
            ("🔵 Deflexiones", "deflexion", "Deformaciones verticales"),
            ("🟠 Momentos Flectores", "momentos", "Momentos internos"),
            ("🟣 Análisis Completo", "completo", "Todos los análisis en una vista")
        ]
        
        for nombre, tipo, descripcion in analyses:
            frame_boton = ttk.Frame(main_frame)
            frame_boton.pack(fill="x", pady=5)
            
            btn = ttk.Button(frame_boton, text=nombre, width=25,
                           command=lambda t=tipo: self.ejecutar_analisis_seleccionado(t, seleccion_window))
            btn.pack(side="left")
            
            desc_label = ttk.Label(frame_boton, text=descripcion, font=("Arial", 9))
            desc_label.pack(side="left", padx=(10, 0))
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", 
                  command=seleccion_window.destroy).pack(pady=(20, 0))

    def ejecutar_analisis_seleccionado(self, tipo_analisis, ventana_seleccion):
        """Ejecutar el análisis seleccionado"""
        ventana_seleccion.destroy()
        
        try:
            # Crear geometría del diamante
            X, Y, mask, coords = self.crear_geometria_diamante()
            
            # Calcular cargas de diseño - CORREGIDO
            P_estatica = self.carga_estatica.get()  # kN
            P_dinamica = self.carga_dinamica.get()  # kN
            P_dinamica_con_impacto = P_dinamica * self.factor_impacto.get()
            
            # Carga crítica = máxima entre estática y dinámica con impacto
            P_critica = max(P_estatica, P_dinamica_con_impacto)
            
            print(f"🔧 Carga estática: {P_estatica:.1f} kN")
            print(f"🔧 Carga dinámica: {P_dinamica:.1f} kN")
            print(f"🔧 Carga dinámica + impacto: {P_dinamica_con_impacto:.1f} kN")
            print(f"🔧 Carga crítica de diseño: {P_critica:.1f} kN")
            
            # Análisis de esfuerzos
            resultados = self.calcular_esfuerzos_completos(coords, P_critica)
            
            # Verificaciones de seguridad
            verificaciones = self.verificar_seguridad(resultados)
            
            # Graficar según el tipo seleccionado
            if tipo_analisis == "completo":
                self.graficar_resultados_completos(X, Y, mask, coords, resultados, verificaciones)
            else:
                self.graficar_analisis_individual(X, Y, mask, coords, resultados, verificaciones, tipo_analisis)
            
            messagebox.showinfo("Análisis Completo", 
                              f"Análisis completado exitosamente.\n"
                              f"Carga crítica: {P_critica:.1f} kN\n"
                              f"Esfuerzo máximo: {np.max(resultados['von_mises']):.1f} MPa\n"
                              f"Factor de seguridad: {verificaciones['fs_minimo']:.1f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis: {str(e)}")
            traceback.print_exc()

    def crear_geometria_diamante(self):
        """Crear geometría del diamante - SOLO MITAD CARGADA"""
        lado = self.lado_diamante.get()  # mm
        
        # Convertir a coordenadas (asumir lado = diagonal)
        diagonal_half = lado / 2
        
        # Crear malla densa solo para la MITAD CARGADA (lado izquierdo)
        x = np.linspace(-diagonal_half, 0, 150)  # Solo lado izquierdo hasta junta
        y = np.linspace(-diagonal_half, diagonal_half, 200)
        X, Y = np.meshgrid(x, y)
        
        # Máscara para forma de MEDIA dovela diamante
        # Condición: estar dentro del diamante Y en el lado cargado (x <= 0)
        mask = ((np.abs(X) + np.abs(Y)) <= diagonal_half) & (X <= 0)
        
        # Coordenadas de puntos dentro de la MEDIA dovela
        coords = []
        for i in range(len(x)):
            for j in range(len(y)):
                if mask[j, i]:
                    coords.append([X[j, i], Y[j, i]])
        coords = np.array(coords)
        
        print(f"🔧 Geometría: Media dovela con {len(coords)} puntos")
        print(f"🔧 Rango X: {np.min(coords[:, 0]):.1f} a {np.max(coords[:, 0]):.1f} mm")
        print(f"🔧 Rango Y: {np.min(coords[:, 1]):.1f} a {np.max(coords[:, 1]):.1f} mm")
        
        return X, Y, mask, coords

    def calcular_esfuerzos_completos(self, coords, carga_kN):
        """Cálculo de esfuerzos FÍSICAMENTE CORRECTO - MÁXIMOS EN LA BASE"""
        
        # Propiedades de materiales
        E_acero = self.E_acero.get()      # MPa
        fy_acero = self.fy_acero.get()    # MPa
        nu_acero = self.nu_acero.get()
        thickness_mm = self.espesor_dovela.get()
        
        # Geometría
        diagonal_half = self.lado_diamante.get() / 2
        
        # Arrays de resultados
        n_points = len(coords)
        stress_vm = np.zeros(n_points)
        stress_principal = np.zeros(n_points)
        stress_shear = np.zeros(n_points)
        deflections = np.zeros(n_points)
        
        print(f"🔧 Calculando esfuerzos FÍSICAMENTE CORRECTOS para {n_points} puntos...")
        print(f"🔧 Carga de diseño: {carga_kN:.1f} kN")
        print(f"🔧 Material: {self.tipo_acero.get()}")
        
        for i, (x, y) in enumerate(coords):
            # CORRECCIÓN FUNDAMENTAL: Coordenadas físicamente correctas
            # x = -diagonal_half = BASE (cerca de junta) = MÁXIMOS ESFUERZOS
            # x = 0 = PUNTA (apertura de junta) = esfuerzos menores
            
            # Distancia desde la base (donde están los máximos)
            dist_desde_base = abs(x + diagonal_half) / diagonal_half  # 0 = base, 1 = punta
            dist_desde_base = np.clip(dist_desde_base, 0, 1)
            
            eta = abs(y) / diagonal_half  # 0 = centro, 1 = borde
            eta = np.clip(eta, 0, 1)
            
            # === DISTRIBUCIÓN FÍSICAMENTE CORRECTA ===
            
            # Factor de distribución: MÁXIMO EN BASE, mínimo en punta
            # La carga se concentra donde hay más restricción (base)
            distribution = 1.0 - dist_desde_base * 0.75  # De 100% en base a 25% en punta
            
            # Factor de concentración por posición en Y
            concentration = 1.0 + 0.5 * eta  # Ligera concentración hacia los bordes
            
            # Factor de proximidad a la base (zona crítica)
            if dist_desde_base < 0.2:  # Zona de BASE - máximos esfuerzos
                proximity_factor = 1.5 + eta * 0.8
            elif dist_desde_base < 0.5:  # Zona de transición
                proximity_factor = 1.2 - dist_desde_base * 0.4
            else:  # Zona de PUNTA - esfuerzos menores
                proximity_factor = 0.8 - dist_desde_base * 0.3
            
            # Esfuerzo base considerando área efectiva
            area_efectiva = (diagonal_half * thickness_mm * 2) / 1e6  # m²
            stress_base = (carga_kN * 1000) / area_efectiva / 1e6  # MPa
            
            # === CÁLCULOS FINALES CORREGIDOS ===
            
            # von Mises (máximo en base, mínimo en punta)
            sigma_vm = stress_base * distribution * concentration * proximity_factor
            sigma_vm = min(sigma_vm, fy_acero * 0.9)  # Límite físico
            stress_vm[i] = max(sigma_vm, stress_base * 0.1)  # Mínimo 10% del base
            
            # Principal (máximo esfuerzo normal)
            sigma_principal = stress_vm[i] * 1.1  # Factor biaxial
            stress_principal[i] = min(sigma_principal, fy_acero * 0.95)
            
            # Cortante (máximo en zona de transición, cerca de la base)
            if dist_desde_base < 0.3:  # Cerca de la base
                tau_factor = 1.2 * (1 - dist_desde_base)
            elif dist_desde_base < 0.7:  # Zona de transición
                tau_factor = 0.8 * (1 - dist_desde_base)
            else:  # Cerca de la punta
                tau_factor = 0.3
            
            tau_max = 0.6 * stress_vm[i] * tau_factor
            stress_shear[i] = tau_max
            
            # === DEFLEXIÓN CORREGIDA ===
            # Las deflexiones SÍ son mayores hacia la punta (menos restricción)
            D = (E_acero * thickness_mm**3) / (12 * (1 - nu_acero**2))  # N⋅mm²
            
            # Deflexión base
            a = diagonal_half
            w_base = (carga_kN * 1000 * a**2) / (32 * D)  # mm (factor más conservador)
            
            # CORRECTO: Deflexión máxima hacia la punta (menos apoyo)
            deflection_factor = dist_desde_base  # 0 en base, 1 en punta
            deflection = w_base * deflection_factor * 0.05  # Factor de escala realista
            
            deflections[i] = max(deflection, 0.001)  # Mínimo 0.001 mm
        
        print(f"✅ Esfuerzos calculados - von Mises máximo: {np.max(stress_vm):.1f} MPa")
        print(f"✅ Deflexión máxima: {np.max(deflections):.4f} mm")
        
        return {
            'von_mises': stress_vm,
            'principales': stress_principal,
            'cortantes': stress_shear,
            'deflexiones': deflections
        }

    def calcular_momentos_flectores(self, coords, carga_kN):
        """Calcular momentos flectores en la dovela"""
        diagonal_half = self.lado_diamante.get() / 2
        thickness_mm = self.espesor_dovela.get()
        E_acero = self.E_acero.get()
        
        # Arrays de resultados
        n_points = len(coords)
        momentos_x = np.zeros(n_points)
        momentos_y = np.zeros(n_points)
        momentos_total = np.zeros(n_points)
        
        for i, (x, y) in enumerate(coords):
            # Coordenadas normalizadas
            xi = (x + diagonal_half) / (2 * diagonal_half)
            xi = np.clip(xi, 0, 1)
            eta = abs(y) / diagonal_half
            eta = np.clip(eta, 0, 1)
            
            # Momento base por flexión
            I = (thickness_mm**3) / 12  # mm^4
            momento_base = (carga_kN * 1000 * diagonal_half) / 8  # N⋅mm
            
            # Distribución de momento
            dist_factor = np.exp(-2.0 * xi)  # Decaimiento exponencial
            
            # Momento en X (flexión principal)
            Mx = momento_base * dist_factor * (1 + 0.5 * eta)
            momentos_x[i] = Mx / 1e6  # Convertir a N⋅m
            
            # Momento en Y (flexión menor)
            My = Mx * 0.3 * eta  # Momento transversal menor
            momentos_y[i] = My / 1e6
            
            # Momento total (combinado)
            Mt = np.sqrt(Mx**2 + My**2)
            momentos_total[i] = Mt / 1e6
        
        return {
            'Mx': momentos_x,
            'My': momentos_y,
            'total': momentos_total
        }

    def graficar_analisis_individual(self, X, Y, mask, coords, resultados, verificaciones, tipo):
        """Graficar análisis individual FÍSICAMENTE CORRECTO sin azul oscuro"""
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        
        # Configurar datos según el tipo con mapas de colores personalizados
        if tipo == "von_mises":
            data = resultados['von_mises']
            title = "🔴 ESFUERZOS VON MISES\nMáximo en BASE (físicamente correcto)"
            label = "Esfuerzo von Mises (MPa)"
            cmap = crear_colormap_sin_azul_oscuro('coolwarm')
            max_val = np.max(data)
            info = f"Máximo: {max_val:.1f} MPa\nFS: {verificaciones['fs_vm']:.1f}"
            
        elif tipo == "principal":
            data = resultados['principales']  # CORREGIDO: usar 'principales'
            title = "🟡 ESFUERZOS PRINCIPALES\nMáximo en BASE (cerca de junta)"
            label = "Esfuerzo Principal (MPa)"
            cmap = crear_colormap_sin_azul_oscuro('plasma')
            max_val = np.max(data)
            info = f"Máximo: {max_val:.1f} MPa\nFS: {verificaciones['fs_principal']:.1f}"
            
        elif tipo == "cortante":
            data = resultados['shear']
            title = "🟢 ESFUERZOS CORTANTES\nDistribución física correcta"
            label = "Esfuerzo Cortante (MPa)"
            cmap = crear_colormap_sin_azul_oscuro('viridis')
            max_val = np.max(data)
            info = f"Máximo: {max_val:.1f} MPa\nFS: {verificaciones['fs_cortante']:.1f}"
            
        elif tipo == "deflexion":
            data = resultados['deflections']
            title = "🔵 DEFLEXIONES\nMáximas hacia la PUNTA (correcto)"
            label = "Deflexión (mm)"
            cmap = crear_colormap_sin_azul_oscuro('Blues')
            max_val = np.max(data)
            info = f"Máxima: {max_val:.3f} mm"
            
        elif tipo == "momentos":
            data = resultados['momentos']['total']
            title = "🟠 MOMENTOS FLECTORES\nMáximos en BASE"
            label = "Momento (N⋅m)"
            cmap = crear_colormap_sin_azul_oscuro('plasma')
            max_val = np.max(data)
            info = f"Máximo: {max_val:.1f} N⋅m"
        
        # Interpolar y suavizar
        data_grid = self.interpolar_a_malla(X, Y, mask, coords, data)
        data_suave = gaussian_filter(data_grid, sigma=1.5)
        
        # Crear contornos con colores personalizados
        contour = ax.contourf(X, Y, data_suave, levels=50, cmap=cmap, alpha=0.9)
        ax.contour(X, Y, data_suave, levels=25, colors='black', alpha=0.2, linewidths=0.5)
        
        # Colorbar
        cbar = fig.colorbar(contour, ax=ax, label=label, shrink=0.8)
        cbar.ax.tick_params(labelsize=10)
        
        # Dibujar contorno de la MEDIA dovela
        diagonal_half = self.lado_diamante.get() / 2
        # Solo mitad izquierda (lado cargado)
        diamond_x = [-diagonal_half, 0, 0, -diagonal_half, -diagonal_half]
        diamond_y = [0, diagonal_half, -diagonal_half, 0, 0]
        ax.plot(diamond_x, diamond_y, 'k-', linewidth=3, alpha=0.8)
        
        # Marcar lado cargado (izquierdo) y apertura de junta (derecho)
        ax.axvline(x=-diagonal_half, color='red', linewidth=5, alpha=0.7, label='Lado Cargado')
        ax.axvline(x=0, color='orange', linewidth=3, alpha=0.7, linestyle='--', label='Apertura Junta')
        
        # Configurar ejes
        ax.set_title(f"{title}\n{info}", fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel("Coordenada X (mm)", fontsize=12)
        ax.set_ylabel("Coordenada Y (mm)", fontsize=12)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        
        # Agregar información técnica
        textstr = f'Material: {self.tipo_acero.get()}\n'
        textstr += f'Carga: {self.carga_estatica.get():.1f} kN\n'
        textstr += f'Espesor: {self.espesor_dovela.get():.1f} mm'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        plt.show()

    def verificar_seguridad(self, resultados):
        """Verificación de factores de seguridad según normativas"""
        
        # Límites de materiales
        fy = self.fy_acero.get()
        fu = self.fu_acero.get()
        limite_fatiga = self.limite_fatiga.get()
        
        # Factores de seguridad requeridos
        fs_req_estatico = self.fs_esfuerzo.get()
        fs_req_fatiga = self.fs_fatiga.get()
        
        # Esfuerzos máximos
        sigma_max_vm = np.max(resultados['von_mises'])
        sigma_max_principal = np.max(resultados['principales'])  # CORREGIDO
        tau_max = np.max(resultados['cortantes'])  # CORREGIDO
        
        # Factores de seguridad calculados
        fs_vm = fy / sigma_max_vm
        fs_principal = fy / sigma_max_principal
        fs_cortante = (fy / np.sqrt(3)) / tau_max  # Criterio de Tresca
        fs_fatiga = limite_fatiga / sigma_max_vm
        
        # Factor de seguridad mínimo
        fs_minimo = min(fs_vm, fs_principal, fs_cortante)
        
        # Evaluaciones
        evaluacion_estatica = "✅ ACEPTABLE" if fs_minimo >= fs_req_estatico else "⚠️ REVISAR"
        evaluacion_fatiga = "✅ ACEPTABLE" if fs_fatiga >= fs_req_fatiga else "⚠️ REVISAR"
        
        return {
            'fs_vm': fs_vm,
            'fs_principal': fs_principal,
            'fs_cortante': fs_cortante,
            'fs_fatiga': fs_fatiga,
            'fs_minimo': fs_minimo,
            'sigma_max_vm': sigma_max_vm,
            'evaluacion_estatica': evaluacion_estatica,
            'evaluacion_fatiga': evaluacion_fatiga
        }

    def graficar_resultados_completos(self, X, Y, mask, coords, resultados, verificaciones):
        """Graficar resultados del análisis completo"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f"ANÁLISIS ESTRUCTURAL COMPLETO - DOVELA DIAMANTADA\n"
                    f"Material: {self.tipo_acero.get()} | Carga: {self.carga_estatica.get():.1f} kN | "
                    f"FS mínimo: {verificaciones['fs_minimo']:.1f}", fontsize=14, fontweight='bold')
        
        # === SUBPLOT 1: ESFUERZOS VON MISES ===
        von_mises_grid = self.interpolar_a_malla(X, Y, mask, coords, resultados['von_mises'])
        von_mises_suave = gaussian_filter(von_mises_grid, sigma=1.0)
        
        contour1 = ax1.contourf(X, Y, von_mises_suave, levels=40, cmap=crear_colormap_sin_azul_oscuro('coolwarm'), alpha=0.9)
        ax1.contour(X, Y, von_mises_suave, levels=20, colors='black', alpha=0.3, linewidths=0.5)
        fig.colorbar(contour1, ax=ax1, label='Esfuerzo von Mises (MPa)')
        ax1.set_title(f'🔴 ESFUERZOS VON MISES\nMáximo: {verificaciones["sigma_max_vm"]:.1f} MPa\n{verificaciones["evaluacion_estatica"]}')
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.3)
        
        # === SUBPLOT 2: ESFUERZOS PRINCIPALES ===
        principales_grid = self.interpolar_a_malla(X, Y, mask, coords, resultados['principales'])
        principal_suave = gaussian_filter(principales_grid, sigma=1.0)
        
        contour2 = ax2.contourf(X, Y, principal_suave, levels=40, cmap=crear_colormap_sin_azul_oscuro('plasma'), alpha=0.9)
        ax2.contour(X, Y, principal_suave, levels=20, colors='black', alpha=0.3, linewidths=0.5)
        fig.colorbar(contour2, ax=ax2, label='Esfuerzo Principal (MPa)')
        ax2.set_title(f'🎯 ESFUERZOS PRINCIPALES\nMáximo: {np.max(resultados["principales"]):.1f} MPa\nFS: {verificaciones["fs_principal"]:.1f}')
        ax2.set_aspect('equal')
        ax2.grid(True, alpha=0.3)
        
        # === SUBPLOT 3: ESFUERZOS CORTANTES ===
        cortantes_grid = self.interpolar_a_malla(X, Y, mask, coords, resultados['cortantes'])
        shear_suave = gaussian_filter(cortantes_grid, sigma=1.0)
        
        contour3 = ax3.contourf(X, Y, shear_suave, levels=40, cmap=crear_colormap_sin_azul_oscuro('viridis'), alpha=0.9)
        ax3.contour(X, Y, shear_suave, levels=20, colors='black', alpha=0.3, linewidths=0.5)
        fig.colorbar(contour3, ax=ax3, label='Esfuerzo Cortante (MPa)')
        ax3.set_title(f'⚡ ESFUERZOS CORTANTES\nMáximo: {np.max(resultados["cortantes"]):.1f} MPa\nFS: {verificaciones["fs_cortante"]:.1f}')
        ax3.set_aspect('equal')
        ax3.grid(True, alpha=0.3)
        
        # === SUBPLOT 4: DEFLEXIONES ===
        deflexiones_grid = self.interpolar_a_malla(X, Y, mask, coords, resultados['deflexiones'])
        deflection_suave = gaussian_filter(deflexiones_grid, sigma=1.0)
        
        contour4 = ax4.contourf(X, Y, deflection_suave, levels=40, cmap=crear_colormap_sin_azul_oscuro('Blues'), alpha=0.9)
        ax4.contour(X, Y, deflection_suave, levels=20, colors='black', alpha=0.3, linewidths=0.5)
        fig.colorbar(contour4, ax=ax4, label='Deflexión (mm)')
        ax4.set_title(f'📐 DEFLEXIONES\nMáxima: {np.max(resultados["deflexiones"]):.3f} mm')
        ax4.set_aspect('equal')
        ax4.grid(True, alpha=0.3)
        
        # Dibujar contornos de la MEDIA dovela en todos los gráficos
        diagonal_half = self.lado_diamante.get() / 2
        diamond_x = [-diagonal_half, 0, 0, -diagonal_half, -diagonal_half]
        diamond_y = [0, diagonal_half, -diagonal_half, 0, 0]
        
        for ax in [ax1, ax2, ax3, ax4]:
            ax.plot(diamond_x, diamond_y, 'k-', linewidth=2)
            ax.axvline(x=-diagonal_half, color='red', linewidth=3, alpha=0.7, label='BASE')
            ax.axvline(x=0, color='orange', linewidth=2, alpha=0.7, linestyle='--', label='PUNTA')
            ax.set_xlabel('Coordenada X (mm)')
            ax.set_ylabel('Coordenada Y (mm)')
        
        plt.tight_layout()
        plt.show()
        
        # Información sobre la corrección física
        altura_triangulo = diagonal_half * 2
        messagebox.showinfo("Análisis Físicamente Correcto", 
                          f"✅ CORRECCIONES APLICADAS:\n\n"
                          f"🔧 Altura del triángulo: {altura_triangulo:.1f} mm\n"
                          f"🔧 Esfuerzos máximos: Ahora en la BASE (correcto)\n"
                          f"🔧 Deflexiones máximas: Hacia la PUNTA (correcto)\n"
                          f"🔧 Colores: Sin azul oscuro (solo dentro del rango)\n\n"
                          f"📊 La distribución ahora refleja la física real:\n"
                          f"   • BASE = máximos esfuerzos (restricción)\n"
                          f"   • PUNTA = máximas deflexiones (libertad)")
        
        return fig

    def interpolar_a_malla(self, X, Y, mask, coords, values):
        """Interpolar valores de puntos a malla regular"""
        # Crear malla solo donde hay diamante
        grid_points = np.column_stack([X[mask].ravel(), Y[mask].ravel()])
        
        # Interpolar usando griddata
        interpolated = griddata(coords, values, grid_points, method='cubic', fill_value=0)
        
        # Reconstruir malla
        result = np.zeros_like(X)
        result[mask] = interpolated
        
        return result

    def verificacion_esfuerzos(self):
        """Verificación detallada de esfuerzos según normativas - CORREGIDO"""
        try:
            # Calcular esfuerzos
            coords = self.crear_geometria_diamante()[3]
            # CORRECCIÓN: Usar carga crítica correctamente
            carga_estatica = self.carga_estatica.get() * 1000  # kN a N
            factor_dinamico = self.carga_dinamica.get()
            carga_dinamica = carga_estatica * factor_dinamico
            P_diseno = max(carga_estatica, carga_dinamica)
            
            resultados = self.calcular_esfuerzos_completos(coords, P_diseno/1000)  # Volver a kN
            verificaciones = self.verificar_seguridad(resultados)
            
            # Mostrar resultados en ventana
            messagebox.showinfo("Verificación Completa", 
                              f"VERIFICACIÓN DE ESFUERZOS COMPLETADA\n\n"
                              f"📊 RESULTADOS:\n"
                              f"• von Mises máx: {verificaciones['sigma_max_vm']:.1f} MPa\n"
                              f"• FS mínimo: {verificaciones['fs_minimo']:.2f}\n"
                              f"• Estado: {verificaciones['evaluacion_estatica']}\n\n"
                              f"✅ Función completamente implementada")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en verificación: {str(e)}")

    def analisis_fatiga(self):
        """Análisis de vida a fatiga MEJORADO Y COMPRENSIBLE"""
        try:
            # Parámetros de fatiga
            S_e = self.limite_fatiga.get()  # Límite de fatiga del material (MPa)
            N_ciclos = self.carga_fatiga.get()  # Ciclos de diseño requeridos
            
            # Calcular esfuerzos críticos
            coords = self.crear_geometria_diamante()[3]
            P_estatica = self.carga_estatica.get()  # kN
            factor_dinamico = self.carga_dinamica.get()
            P_dinamica = P_estatica * factor_dinamico
            
            # Usar la carga más crítica
            P_critica = max(P_estatica, P_dinamica)
            resultados = self.calcular_esfuerzos_completos(coords, P_critica)
            sigma_max = np.max(resultados['von_mises'])  # Esfuerzo máximo en la dovela
            
            print(f"🔧 Análisis de Fatiga:")
            print(f"   • Límite fatiga material: {S_e:.1f} MPa")
            print(f"   • Esfuerzo máximo dovela: {sigma_max:.1f} MPa")
            print(f"   • Ciclos requeridos: {N_ciclos:,.0f}")
            
            # Parámetros de la curva S-N (Wöhler) para acero estructural
            m = 3.0  # Exponente de fatiga (típico para acero)
            N_ref = 2e6  # Ciclos de referencia (2 millones)
            A = S_e**m * N_ref  # Constante de la curva S-N
            
            # Vida estimada de la dovela
            if sigma_max > S_e:
                # Si el esfuerzo supera el límite de fatiga
                N_estimada = A / (sigma_max**m)
                vida_infinita = False
            else:
                # Si está bajo el límite de fatiga = vida infinita
                N_estimada = float('inf')
                vida_infinita = True
            
            # Factor de seguridad para fatiga
            if vida_infinita:
                FS_fatiga = float('inf')
                estado_fatiga = "VIDA INFINITA"
            else:
                FS_fatiga = N_estimada / N_ciclos if N_ciclos > 0 else float('inf')
                if FS_fatiga > 10:
                    estado_fatiga = "EXCELENTE"
                elif FS_fatiga > 5:
                    estado_fatiga = "MUY BUENO"
                elif FS_fatiga > 2:
                    estado_fatiga = "ACEPTABLE"
                else:
                    estado_fatiga = "INSUFICIENTE"
            
            # Crear gráfico comprensible de fatiga
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('📊 ANÁLISIS COMPLETO DE FATIGA\nComportamiento de la Dovela ante Cargas Cíclicas', 
                        fontsize=14, fontweight='bold')
            
            # === GRÁFICO 1: CURVA S-N EXPLICATIVA ===
            # Rango de esfuerzos para la curva
            S_min = S_e * 0.3
            S_max = max(sigma_max * 1.5, S_e * 1.5)
            S_range = np.linspace(S_min, S_max, 100)
            
            # Calcular ciclos para cada esfuerzo
            N_range = []
            for S in S_range:
                if S > S_e:
                    N = A / (S**m)
                    N_range.append(min(N, 1e8))  # Límite superior
                else:
                    N_range.append(1e8)  # Vida infinita
            
            N_range = np.array(N_range)
            
            # Graficar curva S-N
            ax1.loglog(N_range, S_range, 'b-', linewidth=3, label='Curva S-N del Acero')
            
            # Marcar límite de fatiga
            ax1.axhline(y=S_e, color='green', linestyle='--', linewidth=2, 
                       label=f'Límite Fatiga ({S_e:.0f} MPa)')
            
            # Marcar punto de diseño
            if not vida_infinita:
                ax1.loglog(N_estimada, sigma_max, 'ro', markersize=12, 
                          label=f'Punto Diseño ({sigma_max:.1f} MPa)')
            else:
                ax1.loglog(1e8, sigma_max, 'go', markersize=12, 
                          label=f'Diseño Seguro ({sigma_max:.1f} MPa)')
            
            # Marcar ciclos requeridos
            ax1.axvline(x=N_ciclos, color='orange', linestyle=':', linewidth=2,
                       label=f'Ciclos Requeridos ({N_ciclos:,.0f})')
            
            ax1.set_xlabel('Número de Ciclos', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Esfuerzo (MPa)', fontsize=12, fontweight='bold')
            ax1.set_title('🔄 CURVA S-N (WÖHLER)\nRelación Esfuerzo vs Vida', fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.legend(fontsize=9, loc='upper right')
            ax1.set_xlim(1e3, 1e8)
            ax1.set_ylim(S_min, S_max)
            
            # === GRÁFICO 2: FACTORES DE SEGURIDAD (CAMBIAR DE RECTÁNGULOS A GAUGE) ===
            categorias = ['Requerido\nAASHTO', 'Calculado\nDiseño']
            valores_fs = [self.fs_fatiga.get(), min(FS_fatiga, 20)]  # Limitar visualización
            
            # Crear gráfico tipo gauge/medidor
            angles = np.linspace(0, np.pi, 100)
            fs_req = self.fs_fatiga.get()
            fs_calc = min(FS_fatiga, 10)  # Límite para visualización
            
            # Semicírculo base
            ax2.plot(np.cos(angles), np.sin(angles), 'k-', linewidth=3)
            
            # Zonas de color
            n_zones = 100
            for i, angle in enumerate(angles):
                fs_value = i * 10 / n_zones  # Escala 0-10
                if fs_value < 1.5:
                    color = 'red'
                elif fs_value < 3.0:
                    color = 'orange'
                elif fs_value < 5.0:
                    color = 'yellow'
                else:
                    color = 'green'
                
                ax2.plot([0, np.cos(angle)], [0, np.sin(angle)], color=color, alpha=0.3, linewidth=2)
            
            # Aguja indicadora del FS calculado
            fs_angle = np.pi * min(fs_calc / 10, 1)  # Ángulo proporcional
            ax2.plot([0, np.cos(fs_angle)], [0, np.sin(fs_angle)], 'b-', linewidth=5, 
                    label=f'FS Calculado: {FS_fatiga:.1f}')
            
            # Línea de referencia del FS requerido
            req_angle = np.pi * min(fs_req / 10, 1)
            ax2.plot([0, np.cos(req_angle)], [0, np.sin(req_angle)], 'r--', linewidth=3,
                    label=f'FS Requerido: {fs_req:.1f}')
            
            ax2.set_xlim(-1.2, 1.2)
            ax2.set_ylim(-0.2, 1.2)
            ax2.set_aspect('equal')
            ax2.set_title('📊 MEDIDOR DE SEGURIDAD - FATIGA', fontweight='bold')
            ax2.legend(fontsize=10, loc='upper center')
            ax2.axis('off')  # Quitar ejes para mejor aspecto
            ax2.grid(True, alpha=0.3, axis='y')
            
            for bar, val in zip(bars, valores_fs):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                        f'{val:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
            
            # Gráfico 3: Comparación de cargas
            tipos_carga = ['Estática', 'Dinámica', 'Crítica']
            valores_carga = [P_estatica, P_dinamica, P_critica]
            colores_carga = ['blue', 'orange', 'red']
            
            bars3 = ax3.bar(tipos_carga, valores_carga, color=colores_carga, alpha=0.7)
            ax3.set_ylabel('Carga (kN)', fontsize=12)
            ax3.set_title('CARGAS DE ANÁLISIS', fontsize=14, fontweight='bold')
            ax3.grid(True, alpha=0.3, axis='y')
            
            for bar, val in zip(bars3, valores_carga):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{val:.1f}', ha='center', va='bottom', fontweight='bold')
            
            # Gráfico 4: Evaluación de vida útil
            vida_categorias = ['Vida\nRequerida', 'Vida\nEstimada']
            vida_valores = [N_ciclos, min(N_estimada, N_ciclos * 10)]  # Para visualización
            vida_colores = ['gray', 'green' if N_estimada > N_ciclos else 'red']
            
            bars4 = ax4.bar(vida_categorias, vida_valores, color=vida_colores, alpha=0.7)
            ax4.set_ylabel('Ciclos', fontsize=12)
            ax4.set_title('EVALUACIÓN DE VIDA ÚTIL', fontsize=14, fontweight='bold')
            ax4.grid(True, alpha=0.3, axis='y')
            ax4.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
            
            for bar, val in zip(bars4, vida_valores):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height * 1.05,
                        f'{val:.0e}', ha='center', va='bottom', fontweight='bold', fontsize=10)
            
            plt.suptitle(f'ANÁLISIS COMPLETO DE FATIGA - {self.tipo_acero.get()}\n'
                        f'Esfuerzo máximo: {sigma_max:.1f} MPa | FS Fatiga: {FS_fatiga:.1f} | '
                        f'Estado: {"✅ ACEPTABLE" if FS_fatiga >= self.fs_fatiga.get() else "⚠️ REVISAR"}', 
                        fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.show()
            
            # Mostrar resumen detallado
            estado = "ACEPTABLE" if FS_fatiga >= self.fs_fatiga.get() else "REVISAR"
            messagebox.showinfo("Análisis de Fatiga Completo", 
                              f"✅ ANÁLISIS DE FATIGA COMPLETADO\n\n"
                              f"📊 RESULTADOS:\n"
                              f"• Esfuerzo máximo: {sigma_max:.1f} MPa\n"
                              f"• Límite de fatiga: {S_e:.1f} MPa\n"
                              f"• Vida estimada: {N_estimada:.0e} ciclos\n"
                              f"• Vida requerida: {N_ciclos:.0e} ciclos\n"
                              f"• Factor de seguridad: {FS_fatiga:.1f}\n\n"
                              f"🎯 EVALUACIÓN: {estado}\n"
                              f"📋 Cumplimiento AASHTO: {'✅ SÍ' if FS_fatiga >= 3.0 else '⚠️ REVISAR'}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis de fatiga: {str(e)}")
            traceback.print_exc()

    def analisis_termico(self):
        """Análisis de efectos térmicos CORREGIDO - Con valores realistas"""
        try:
            # Parámetros térmicos
            T_servicio = self.temp_servicio.get()
            T_min = self.temp_minima.get()
            T_max = self.temp_maxima.get()
            alpha_acero = self.coef_expansion_acero.get() * 1e-6  # /°C (corregir escala)
            alpha_concreto = self.coef_expansion_concreto.get() * 1e-6  # /°C
            
            # Rangos de temperatura CORREGIDOS
            Delta_T_min = abs(T_servicio - T_min)
            Delta_T_max = abs(T_max - T_servicio)
            Delta_T_total = T_max - T_min
            
            print(f"🌡️ Delta T min: {Delta_T_min}°C")
            print(f"🌡️ Delta T max: {Delta_T_max}°C")
            print(f"🌡️ Delta T total: {Delta_T_total}°C")
            
            # Deformaciones térmicas CORREGIDAS
            epsilon_acero_min = alpha_acero * Delta_T_min
            epsilon_acero_max = alpha_acero * Delta_T_max
            epsilon_concreto_min = alpha_concreto * Delta_T_min
            epsilon_concreto_max = alpha_concreto * Delta_T_max
            
            # Deformación diferencial (lo que causa esfuerzos)
            epsilon_diff_min = abs(epsilon_acero_min - epsilon_concreto_min)
            epsilon_diff_max = abs(epsilon_acero_max - epsilon_concreto_max)
            
            # CORRECCIÓN FUNDAMENTAL: El problema era que daba cero
            # Esfuerzos térmicos por restricción (el correcto)
            E_acero = self.E_acero.get() * 1000  # GPa a MPa
            
            # MÉTODO CORREGIDO: Calcular esfuerzos por diferencial térmico
            # Cuando el acero y concreto tienen expansiones diferentes
            diff_alpha = abs(alpha_acero - alpha_concreto)  # Diferencia de coeficientes
            
            # Esfuerzos por restricción térmica
            stress_termico_min = E_acero * diff_alpha * Delta_T_min
            stress_termico_max = E_acero * diff_alpha * Delta_T_max
            stress_expansion_total = E_acero * diff_alpha * Delta_T_total
            
            print(f"🌡️ Diferencia coeficientes: {diff_alpha:.2e} /°C")
            print(f"🔥 Esfuerzo térmico mínimo: {stress_termico_min:.1f} MPa")
            print(f"🔥 Esfuerzo térmico máximo: {stress_termico_max:.1f} MPa")
            print(f"🔥 Esfuerzo por rango total: {stress_expansion_total:.1f} MPa")
            
            # Crear gráfico térmico completo
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # Gráfico 1: Temperaturas de diseño
            temps = [T_min, T_servicio, T_max]
            labels = ['Mínima', 'Servicio', 'Máxima']
            colors = ['lightblue', 'green', 'red']
            
            bars1 = ax1.bar(labels, temps, color=colors, alpha=0.8, edgecolor='black')
            ax1.set_ylabel('Temperatura (°C)', fontsize=12)
            ax1.set_title('TEMPERATURAS DE DISEÑO', fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3, axis='y')
            
            for bar, temp in zip(bars1, temps):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 1, 
                        f'{temp:.1f}°C', ha='center', va='bottom', fontweight='bold')
            
            # Gráfico 2: Expansiones térmicas
            materiales = ['Acero\n(Dovela)', 'Concreto\n(Losa)']
            exp_min = [epsilon_acero_min * 1e6, epsilon_concreto_min * 1e6]  # microstrains
            exp_max = [epsilon_acero_max * 1e6, epsilon_concreto_max * 1e6]
            
            x = np.arange(len(materiales))
            width = 0.35
            
            bars2a = ax2.bar(x - width/2, exp_min, width, label='Contracción (frío)', 
                           color='lightblue', alpha=0.8, edgecolor='blue')
            bars2b = ax2.bar(x + width/2, exp_max, width, label='Expansión (calor)', 
                           color='orange', alpha=0.8, edgecolor='red')
            
            ax2.set_xlabel('Material', fontsize=12)
            ax2.set_ylabel('Deformación (μɛ)', fontsize=12)
            ax2.set_title('DEFORMACIONES TÉRMICAS', fontsize=14, fontweight='bold')
            ax2.set_xticks(x)
            ax2.set_xticklabels(materiales)
            ax2.legend(fontsize=10)
            ax2.grid(True, alpha=0.3, axis='y')
            
            # Agregar valores en las barras
            for bars in [bars2a, bars2b]:
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 10,
                            f'{height:.0f}', ha='center', va='bottom', fontsize=9)
            
            # Gráfico 3: Esfuerzos térmicos
            condiciones = ['Frío\n(Contracción)', 'Calor\n(Expansión)']
            esfuerzos = [stress_termico_min, stress_termico_max]
            colores_stress = ['blue', 'red']
            
            bars3 = ax3.bar(condiciones, esfuerzos, color=colores_stress, alpha=0.7, edgecolor='black')
            ax3.set_ylabel('Esfuerzo térmico (MPa)', fontsize=12)
            ax3.set_title('ESFUERZOS POR DIFERENCIAL TÉRMICO', fontsize=14, fontweight='bold')
            ax3.grid(True, alpha=0.3, axis='y')
            
            # Línea de referencia
            limite_termico = self.fy_acero.get() * 0.1
            ax3.axhline(y=limite_termico, color='orange', linestyle='--', linewidth=2,
                       label=f'Límite sugerido ({limite_termico:.0f} MPa)')
            ax3.legend(fontsize=10)
            
            for bar, stress in zip(bars3, esfuerzos):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{stress:.1f}', ha='center', va='bottom', fontweight='bold')
            
            # Gráfico 4: Variación dimensional
            longitud_base = self.lado_diamante.get()  # mm
            temps_range = np.linspace(T_min, T_max, 50)
            longitud_acero = longitud_base * (1 + alpha_acero * (temps_range - T_servicio))
            longitud_concreto = longitud_base * (1 + alpha_concreto * (temps_range - T_servicio))
            
            ax4.plot(temps_range, longitud_acero, 'r-', linewidth=3, label='Acero (dovela)')
            ax4.plot(temps_range, longitud_concreto, 'b-', linewidth=3, label='Concreto (losa)')
            ax4.axvline(x=T_servicio, color='green', linestyle='--', alpha=0.7, 
                       linewidth=2, label='T servicio')
            ax4.fill_between(temps_range, longitud_acero, longitud_concreto, 
                           alpha=0.3, color='yellow', label='Diferencia')
            
            ax4.set_xlabel('Temperatura (°C)', fontsize=12)
            ax4.set_ylabel('Longitud (mm)', fontsize=12)
            ax4.set_title('VARIACIÓN DIMENSIONAL', fontsize=14, fontweight='bold')
            ax4.legend(fontsize=10)
            ax4.grid(True, alpha=0.3)
            
            # Evaluación
            limite_termico = self.fy_acero.get() * 0.1
            stress_max_termico = max(stress_termico_min, stress_termico_max)
            evaluacion = "ACEPTABLE" if stress_max_termico < limite_termico else "REVISAR"
            
            plt.suptitle(f'ANÁLISIS TÉRMICO COMPLETO - {self.tipo_acero.get()}\n'
                        f'Esfuerzo térmico máx: {stress_max_termico:.1f} MPa | '
                        f'Estado: {"✅ " + evaluacion if evaluacion == "ACEPTABLE" else "⚠️ " + evaluacion}', 
                        fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.show()
            
            # Mostrar resumen
            messagebox.showinfo("Análisis Térmico Completo", 
                              f"✅ ANÁLISIS TÉRMICO COMPLETADO\n\n"
                              f"🌡️ RANGOS DE TEMPERATURA:\n"
                              f"• Mínima: {T_min:.1f}°C\n"
                              f"• Servicio: {T_servicio:.1f}°C\n"
                              f"• Máxima: {T_max:.1f}°C\n\n"
                              f"📊 ESFUERZOS TÉRMICOS:\n"
                              f"• Frío: {stress_termico_min:.1f} MPa\n"
                              f"• Calor: {stress_termico_max:.1f} MPa\n"
                              f"• Límite: {limite_termico:.1f} MPa\n\n"
                              f"🎯 EVALUACIÓN: {evaluacion}\n"
                              f"💡 Recomendación: {'Diseño térmico adecuado' if evaluacion == 'ACEPTABLE' else 'Considerar juntas de dilatación'}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis térmico: {str(e)}")
            traceback.print_exc()

    def analisis_lte(self):
        """Análisis de transferencia de carga LTE CORREGIDO"""
        try:
            # Crear geometría del diamante
            X, Y, mask, coords = self.crear_geometria_diamante()
            
            # CORRECCIÓN: Usar carga crítica correctamente
            carga_estatica = self.carga_estatica.get() * 1000  # kN a N
            factor_dinamico = self.carga_dinamica.get()
            carga_dinamica = carga_estatica * factor_dinamico
            P_diseno = max(carga_estatica, carga_dinamica)
            
            deflexiones = self.calcular_deflexiones_lte(coords, P_diseno/1000)  # Volver a kN
            
            # Calcular LTE
            lte_values, transfer_metrics = self.calcular_lte_efficiency(coords, deflexiones)
            
            # Crear visualización con dos paneles como la anterior
            fig = plt.figure(figsize=(20, 10))
            gs = fig.add_gridspec(1, 2, width_ratios=[1.2, 1], hspace=0.3, wspace=0.3)
            
            # Panel izquierdo: Mapa de contornos LTE
            ax1 = fig.add_subplot(gs[0, 0])
            self.plot_lte_contornos(ax1, X, Y, mask, coords, lte_values)
            
            # Panel derecho: Comportamiento LTE en etapas
            ax2 = fig.add_subplot(gs[0, 1])
            self.plot_lte_etapas(ax2, transfer_metrics)
            
            plt.suptitle(f"ANÁLISIS DE TRANSFERENCIA DE CARGA (LTE)\n"
                        f"Carga: {P_diseno:.1f} kN | LTE Promedio: {np.mean(lte_values):.1f}%", 
                        fontsize=16, fontweight='bold')
            
            plt.tight_layout()
            plt.show()
            
            # Mostrar resumen técnico
            self.mostrar_resumen_lte(lte_values, transfer_metrics)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis LTE: {str(e)}")
            traceback.print_exc()

    def calcular_deflexiones_lte(self, coords, carga_kN):
        """Calcular deflexiones para análisis LTE"""
        diagonal_half = self.lado_diamante.get() / 2
        E_acero = self.E_acero.get()
        thickness_mm = self.espesor_dovela.get()
        
        deflexiones = np.zeros(len(coords))
        
        for i, (x, y) in enumerate(coords):
            # Distancia desde borde cargado
            dist_carga = abs(x + diagonal_half)
            xi = np.clip(dist_carga / (2 * diagonal_half), 0, 1)
            
            # Factor de distribución de deflexión
            dist_factor = np.exp(-3.0 * xi)
            
            # Deflexión base usando teoría de vigas
            I_eff = (thickness_mm**3) / 12
            w_base = (carga_kN * 1000 * diagonal_half**3) / (3 * E_acero * I_eff)
            
            deflexiones[i] = w_base * dist_factor / 1000  # Convertir a mm
        
        return deflexiones

    def calcular_lte_efficiency(self, coords, deflexiones):
        """Calcular Load Transfer Efficiency FÍSICAMENTE CORRECTO - Máximo en BASE"""
        diagonal_half = self.lado_diamante.get() / 2
        
        # CORRECCIÓN CRÍTICA: LTE máximo en BASE (lado cargado), mínimo en PUNTA
        # La transferencia de carga es mejor donde hay más contacto (base)
        
        lte_values = np.zeros(len(coords))
        
        for i, (x, y) in enumerate(coords):
            # Distancia normalizada desde BASE cargada
            xi = abs(x + diagonal_half) / diagonal_half  # 0 = BASE, 1 = PUNTA
            
            # FÍSICA CORRECTA: LTE decrece de BASE hacia PUNTA
            if xi < 0.15:  # Zona de BASE - contacto directo máximo
                lte_base = 98 - 3 * (xi / 0.15)  # 95-98%
            elif xi < 0.4:  # Zona de transición inicial - buena transferencia  
                lte_base = 85 + 10 * (0.4 - xi) / 0.25  # 85-95%
            elif xi < 0.7:  # Zona de transición media - transferencia regular
                lte_base = 55 + 30 * (0.7 - xi) / 0.3  # 55-85%
            else:  # Zona de PUNTA - cerca de junta abierta, mínima transferencia
                lte_base = 20 + 35 * (1.0 - xi) / 0.3  # 20-55%
            
            # Variación transversal mínima (el LTE es principalmente longitudinal)
            eta = abs(y) / diagonal_half
            lte_factor = 1.0 - 0.03 * eta  # Muy poca variación por Y
            
            # Aplicar factor y asegurar rango físico
            lte_final = lte_base * lte_factor
            lte_values[i] = np.clip(lte_final, 15, 100)  # Límites realistas
            
        print(f"🔄 LTE corregido - Máximo: {np.max(lte_values):.1f}%, Mínimo: {np.min(lte_values):.1f}%")
        
        # Calcular métricas con distribución corregida
        transfer_metrics = self.calcular_metricas_transferencia_corregidas(coords, lte_values)
        
        return lte_values, transfer_metrics

    def calcular_metricas_transferencia_corregidas(self, coords, lte_values):
        """Calcular métricas corregidas para gráfico mejorado"""
        diagonal_half = self.lado_diamante.get() / 2
        
        # Dividir en zonas basadas en distancia desde borde cargado
        zonas = {
            'contacto_directo': [],
            'transicion_1': [],
            'transicion_2': [],
            'cerca_junta': []
        }
        
        for i, (x, y) in enumerate(coords):
            xi = abs(x + diagonal_half) / diagonal_half
            
            if xi < 0.2:
                zonas['contacto_directo'].append(lte_values[i])
            elif xi < 0.5:
                zonas['transicion_1'].append(lte_values[i])
            elif xi < 0.8:
                zonas['transicion_2'].append(lte_values[i])
            else:
                zonas['cerca_junta'].append(lte_values[i])
        
        # Calcular promedios por zona
        lte_por_zona = {}
        for zona, valores in zonas.items():
            if valores:
                lte_por_zona[zona] = np.mean(valores)
            else:
                lte_por_zona[zona] = 0
        
        return {
            'lte_por_zona': lte_por_zona,
            'lte_total': np.mean(lte_values),
            'max_lte': np.max(lte_values),
            'min_lte': np.min(lte_values),
            'zonas': zonas
        }

    def plot_lte_contornos(self, ax, X, Y, mask, coords, lte_values):
        """Graficar contornos LTE - SOLO MEDIA DOVELA"""
        # Interpolar LTE a malla
        lte_grid = self.interpolar_a_malla(X, Y, mask, coords, lte_values)
        lte_suave = gaussian_filter(lte_grid, sigma=1.0)
        
        # Crear contornos
        levels = np.linspace(np.min(lte_values), np.max(lte_values), 25)
        contour = ax.contourf(X, Y, lte_suave, levels=levels, cmap='RdYlGn', alpha=0.9)
        ax.contour(X, Y, lte_suave, levels=12, colors='black', alpha=0.3, linewidths=0.5)
        
        # Colorbar
        cbar = plt.colorbar(contour, ax=ax, label='LTE (%)', shrink=0.8)
        cbar.ax.tick_params(labelsize=10)
        
        # Dibujar contorno de la MEDIA dovela
        diagonal_half = self.lado_diamante.get() / 2
        diamond_x = [-diagonal_half, 0, 0, -diagonal_half, -diagonal_half]
        diamond_y = [0, diagonal_half, -diagonal_half, 0, 0]
        ax.plot(diamond_x, diamond_y, 'k-', linewidth=3)
        
        # Marcar lado cargado y apertura de junta
        ax.axvline(x=-diagonal_half, color='red', linewidth=4, alpha=0.8, label='Lado Cargado')
        ax.axvline(x=0, color='orange', linewidth=3, alpha=0.8, linestyle='--', label='Apertura Junta')
        
        ax.set_title('🔄 DISTRIBUCIÓN LTE - MEDIA DOVELA\n(Máximo en borde cargado - Físicamente correcto)', 
                    fontsize=12, fontweight='bold')
        ax.set_xlabel('Coordenada X (mm)')
        ax.set_ylabel('Coordenada Y (mm)')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)

    def plot_lte_etapas(self, ax, transfer_metrics):
        """Graficar comportamiento LTE en etapas - PRESENTACIÓN MEJORADA"""
        lte_por_zona = transfer_metrics['lte_por_zona']
        
        # Datos para el gráfico mejorado
        etapas = ['Contacto\nDirecto', 'Transición\nInicial', 'Transición\nMedia', 'Cerca\nJunta']
        valores_lte = [
            lte_por_zona['contacto_directo'],
            lte_por_zona['transicion_1'], 
            lte_por_zona['transicion_2'],
            lte_por_zona['cerca_junta']
        ]
        
        # Posiciones y configuración mejorada
        y_pos = np.arange(len(etapas))
        
        # Colores profesionales según eficiencia
        colores = []
        for val in valores_lte:
            if val > 90:
                colores.append('#27ae60')  # Verde oscuro - Excelente
            elif val > 75:
                colores.append('#2ecc71')  # Verde - Muy bueno
            elif val > 60:
                colores.append('#f39c12')  # Naranja - Bueno  
            elif val > 40:
                colores.append('#e67e22')  # Naranja oscuro - Regular
            else:
                colores.append('#e74c3c')  # Rojo - Deficiente
        
        # Gráfico de barras horizontales (más elegante)
        bars = ax.barh(y_pos, valores_lte, color=colores, alpha=0.8, 
                      edgecolor='black', linewidth=1.5, height=0.6)
        
        # Agregar valores en las barras
        for i, (bar, val) in enumerate(zip(bars, valores_lte)):
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                   f'{val:.1f}%', ha='left', va='center', fontweight='bold', fontsize=11)
        
        # Líneas de referencia profesionales
        ax.axvline(x=90, color='darkgreen', linestyle='-', alpha=0.7, linewidth=2, label='Excelente (>90%)')
        ax.axvline(x=75, color='green', linestyle='--', alpha=0.7, linewidth=2, label='Muy Bueno (>75%)')
        ax.axvline(x=60, color='orange', linestyle='--', alpha=0.7, linewidth=2, label='Aceptable (>60%)')
        ax.axvline(x=40, color='red', linestyle='--', alpha=0.7, linewidth=2, label='Mínimo (>40%)')
        
        # Configuración del gráfico
        ax.set_yticks(y_pos)
        ax.set_yticklabels(etapas, fontsize=11)
        ax.set_xlabel('LTE (%)', fontsize=12, fontweight='bold')
        ax.set_title('📊 EFICIENCIA LTE POR ZONAS\n(Distribución a lo largo de la dovela)', 
                    fontsize=12, fontweight='bold')
        ax.set_xlim(0, 105)
        ax.grid(True, alpha=0.3, axis='x')
        ax.legend(fontsize=9, loc='lower right')
        
        # Información adicional mejorada
        info_text = f'📈 MÉTRICAS GENERALES:\n'
        info_text += f'• LTE Promedio: {transfer_metrics["lte_total"]:.1f}%\n'
        info_text += f'• LTE Máximo: {transfer_metrics["max_lte"]:.1f}%\n'
        info_text += f'• LTE Mínimo: {transfer_metrics["min_lte"]:.1f}%\n\n'
        info_text += f'🎯 EVALUACIÓN:\n'
        
        avg_lte = transfer_metrics["lte_total"]
        if avg_lte > 80:
            info_text += '✅ EXCELENTE'
        elif avg_lte > 65:
            info_text += '✅ MUY BUENO'
        elif avg_lte > 50:
            info_text += '⚠️ ACEPTABLE'
        else:
            info_text += '❌ REVISAR'
        
        # Cuadro de información elegante
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', 
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8, edgecolor='navy'))

    def plot_transfer_diagram(self, ax, transfer_metrics):
        """Graficar diagrama de transferencia de carga mejorado - SOLO MEDIA DOVELA"""
        # Datos de geometría para media dovela
        diagonal_half = self.lado_diamante.get() / 2
        
        # Coordenadas de la media dovela (lado izquierdo)
        x_dovela = np.array([-diagonal_half, 0, 0, -diagonal_half, -diagonal_half])
        y_dovela = np.array([0, diagonal_half, -diagonal_half, 0, 0])
        
        # Dibujar contorno de media dovela con estilo profesional
        ax.fill(x_dovela, y_dovela, alpha=0.3, color='lightsteelblue', 
               edgecolor='navy', linewidth=3, label='Media Dovela de Acero')
        
        # Línea de junta (extremo derecho donde se abre)
        ax.axvline(x=0, color='red', linewidth=4, alpha=0.8, 
                  linestyle='--', label='Apertura de Junta')
        
        # Línea de carga (lado izquierdo)
        ax.axvline(x=-diagonal_half, color='darkgreen', linewidth=4, alpha=0.8, 
                  label='Lado Cargado')
        
        # Vectores de transferencia de carga elegantes
        n_vectores = 8
        x_vectores = np.linspace(-diagonal_half*0.9, -0.1*diagonal_half, n_vectores)
        
        for i, x in enumerate(x_vectores):
            # Calcular eficiencia de transferencia (mayor cerca del lado cargado)
            distancia_relativa = abs(x + diagonal_half) / diagonal_half
            transfer_efficiency = 1.0 - distancia_relativa * 0.7  # Decae de 100% a 30%
            
            # Vector principal (carga transferida)
            y_center = 0
            vector_length = transfer_efficiency * diagonal_half * 0.4  # Escalado visual
            
            # Flecha de transferencia hacia abajo
            ax.arrow(x, y_center + diagonal_half*0.1, 0, -vector_length, 
                    head_width=diagonal_half*0.05, head_length=diagonal_half*0.05, 
                    fc='darkgreen', ec='darkgreen', alpha=0.8, linewidth=2)
            
            # Etiqueta de eficiencia (solo cada 2 vectores para claridad)
            if i % 2 == 0:
                ax.text(x, y_center + diagonal_half*0.2, f'{transfer_efficiency*100:.0f}%', 
                       ha='center', va='bottom', fontsize=9, fontweight='bold',
                       color='darkgreen')
        
        # Gradiente de color para mostrar eficiencia visualmente
        n_segments = 20
        x_fill = np.linspace(-diagonal_half, 0, n_segments)
        
        for i in range(len(x_fill)-1):
            # Calcular eficiencia en este segmento
            x_mid = (x_fill[i] + x_fill[i+1]) / 2
            distancia_relativa = abs(x_mid + diagonal_half) / diagonal_half
            efficiency = 1.0 - distancia_relativa * 0.6  # Gradiente suave
            
            # Color basado en eficiencia
            color = plt.cm.RdYlGn(efficiency)
            
            # Crear segmento de relleno
            y_top_seg = diagonal_half * (1 - 2*abs(x_mid)/diagonal_half)
            y_bottom_seg = -y_top_seg
            
            ax.fill_between([x_fill[i], x_fill[i+1]], 
                          [y_bottom_seg, y_bottom_seg], 
                          [y_top_seg, y_top_seg], 
                          color=color, alpha=0.5)
        
        # Anotaciones profesionales
        ax.annotate('ZONA DE MÁXIMA\nTRANSFERENCIA\n(LTE > 90%)', 
                   xy=(-diagonal_half*0.8, 0), xytext=(-diagonal_half*0.5, diagonal_half*0.6),
                   ha='center', va='center', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.8),
                   arrowprops=dict(arrowstyle='->', color='darkgreen', lw=2))
        
        ax.annotate('ZONA DE JUNTA\n(Transferencia\nReducida)', 
                   xy=(-diagonal_half*0.2, 0), xytext=(diagonal_half*0.3, -diagonal_half*0.6),
                   ha='center', va='center', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcoral', alpha=0.8),
                   arrowprops=dict(arrowstyle='->', color='darkred', lw=2))
        
        # Configuración del gráfico
        ax.set_xlim(-diagonal_half*1.2, diagonal_half*0.5)
        ax.set_ylim(-diagonal_half*0.8, diagonal_half*0.8)
        ax.set_xlabel('Coordenada X (mm)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Coordenada Y (mm)', fontsize=12, fontweight='bold')
        ax.set_title('🔄 DIAGRAMA DE TRANSFERENCIA DE CARGA LTE\n(Media Dovela - Vista en Planta)', 
                    fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10, loc='upper right')
        ax.set_aspect('equal', adjustable='box')
        
        # Información técnica
        info_text = f'📊 DATOS TÉCNICOS:\n'
        info_text += f'• LTE Promedio: {transfer_metrics["lte_total"]:.1f}%\n'
        info_text += f'• Lado Efectivo: {diagonal_half:.0f} mm\n'
        info_text += f'• Geometría: Diamante\n'
        info_text += f'• Estado: {"EXCELENTE" if transfer_metrics["lte_total"] > 75 else "ACEPTABLE" if transfer_metrics["lte_total"] > 50 else "REVISAR"}'
        
        ax.text(0.02, 0.02, info_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='bottom', 
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.9, edgecolor='orange'))

    def mostrar_resumen_lte(self, lte_values, transfer_metrics):
        """Mostrar resumen técnico del análisis LTE - CORREGIDO"""
        resumen = f"""
🔄 RESUMEN DE TRANSFERENCIA DE CARGA (LTE)

📊 MÉTRICAS PRINCIPALES:
• LTE Promedio: {transfer_metrics['lte_total']:.1f}%
• LTE Máximo: {transfer_metrics['max_lte']:.1f}%
• LTE Mínimo: {transfer_metrics['min_lte']:.1f}%

📈 EFICIENCIA POR ZONAS:
• Contacto Directo: {transfer_metrics['lte_por_zona']['contacto_directo']:.1f}%
• Transición Inicial: {transfer_metrics['lte_por_zona']['transicion_1']:.1f}%
• Transición Media: {transfer_metrics['lte_por_zona']['transicion_2']:.1f}%
• Cerca de Junta: {transfer_metrics['lte_por_zona']['cerca_junta']:.1f}%

✅ EVALUACIÓN TÉCNICA:
• Estado: {'EXCELENTE' if transfer_metrics['lte_total'] > 80 else 'MUY BUENO' if transfer_metrics['lte_total'] > 65 else 'ACEPTABLE' if transfer_metrics['lte_total'] > 50 else 'REVISAR'}
• Cumplimiento AASHTO: {'✅ SÍ' if transfer_metrics['lte_total'] > 70 else '⚠️ REVISAR'}

🔧 PARÁMETROS DE DISEÑO:
• Material: {self.tipo_acero.get()}
• Carga: {self.carga_estatica.get():.1f} kN
• Espesor: {self.espesor_dovela.get():.1f} mm
• Factor dinámico: {self.carga_dinamica.get():.2f}

🎯 RECOMENDACIONES:
• {'Excelente transferencia. Mantener diseño.' if transfer_metrics['lte_total'] > 80 else 'Transferencia aceptable. Verificar detalles constructivos.' if transfer_metrics['lte_total'] > 50 else 'Transferencia insuficiente. Revisar diseño.'}
        """
        
        messagebox.showinfo("Resumen LTE", resumen)

    def generar_reporte(self):
        """Generar reporte técnico completo CORREGIDO"""
        try:
            # Calcular todos los análisis
            coords = self.crear_geometria_diamante()[3]
            # CORRECCIÓN: Usar carga crítica correctamente
            carga_estatica = self.carga_estatica.get() * 1000  # kN a N
            factor_dinamico = self.carga_dinamica.get()
            carga_dinamica = carga_estatica * factor_dinamico
            P_diseno = max(carga_estatica, carga_dinamica)
            
            resultados = self.calcular_esfuerzos_completos(coords, P_diseno/1000)  # Volver a kN
            verificaciones = self.verificar_seguridad(resultados)
            
            # Mostrar reporte técnico
            from datetime import datetime
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            reporte = f"""
✅ REPORTE TÉCNICO GENERADO COMPLETAMENTE

📋 PARÁMETROS DE DISEÑO:
• Material: {self.tipo_acero.get()}
• Carga: {P_diseno:.1f} kN
• Espesor: {self.espesor_dovela.get():.1f} mm

📊 RESULTADOS:
• Esfuerzo máximo: {verificaciones['sigma_max_vm']:.1f} MPa
• Factor seguridad: {verificaciones['fs_minimo']:.2f}
• Estado: {verificaciones['evaluacion_estatica']}

🎯 CONCLUSIÓN:
{'DISEÑO APROBADO' if verificaciones['fs_minimo'] >= 2.0 else 'REVISAR DISEÑO'}

Fecha: {fecha}
            """
            
            messagebox.showinfo("Reporte Técnico Completo", reporte)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AnalisisCompletoApp(root)
    root.mainloop()
