# � DOVELA PROFESSIONAL v2.0

**Análisis Profesional de Dovelas Diamante con Elementos Finitos**

Desarrollado por: **Germán Andrés Rey Carrillo** - Ingeniero Civil, M. Eng.  
Director de Diseño PROPISOS S.A.

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Propietario-red.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Producción-green.svg)](https://github.com/germanrey/dovela-professional)

## 👨‍💼 Autor

**Germán Andrés Rey Carrillo**  
Ingeniero Civil, M. Eng.  
Director de Diseño PROPISOS S.A.

## 🏢 Empresa
**PROPISOS S.A.**  
Especialistas en Diseño de Infraestructura  
Bogotá, Colombia

---

## 📋 Descripción

Esta aplicación proporciona herramientas profesionales para el análisis de esfuerzos en dovelas diamante utilizadas en juntas de dilatación de puentes. Implementa métodos clásicos de análisis estructural y cumple con las especificaciones AASHTO.

### ✨ Características Principales

- **🎯 Análisis de Esfuerzos**: Cálculo de esfuerzos von Mises, principales y cortantes
- **📐 Geometría Paramétrica**: Definición flexible de dovelas diamante
- **🔍 Validación AASHTO**: Verificación según normas AASHTO 14.5.1 y 14.5.2  
- **📊 Visualización Avanzada**: Gráficos profesionales de contornos de esfuerzos
- **🌐 Sistemas de Unidades**: Soporte completo para SI e Imperial
- **📈 Reportes Técnicos**: Generación automática de reportes de diseño
- **🔧 Interfaz Moderna**: GUI profesional con validación en tiempo real

---

## 🚀 Instalación Rápida

### Requisitos del Sistema

- **Python**: 3.8 o superior
- **Sistema Operativo**: Windows, macOS, Linux
- **RAM**: Mínimo 4 GB (recomendado 8 GB)
- **Espacio en Disco**: 500 MB

### Instalación Automática

1. **Descargar** o clonar este repositorio
2. **Ejecutar** el configurador automático:

```bash
python setup.py
```

3. **Lanzar** la aplicación:
   - **Windows**: Doble clic en `ejecutar_dovela.bat`
   - **Linux/Mac**: `./ejecutar_dovela.sh`
   - **Manual**: `python src/main.py`

### Instalación Manual

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Crear directorios
mkdir logs output projects temp

# 3. Ejecutar aplicación
python src/main.py
```

---

## 🎮 Modo de Uso

### Interfaz Gráfica (Recomendado)

```bash
python src/main.py
```

La aplicación abrirá con una interfaz moderna que incluye:

1. **📊 Panel de Parámetros**: Configuración de geometría, cargas y materiales
2. **📈 Panel de Resultados**: Visualización de esfuerzos y factores de seguridad  
3. **✅ Panel de Validación**: Verificación automática según normas

### Modo Consola

```bash
python src/main.py console
```

Ejecuta un análisis de demostración con parámetros predefinidos.

### Modo de Pruebas

```bash
python src/main.py test
```

Verifica que todos los módulos funcionen correctamente.

---

## 📐 Ejemplo de Análisis

### Parámetros de Entrada

```python
# Geometría
lado_diamante = 125.0 mm
espesor = 12.7 mm
apertura_junta = 4.8 mm

# Carga
fuerza_aplicada = 22.2 kN (vertical)

# Material
acero = A36 (fy = 250 MPa, E = 200 GPa)
```

### Resultados Típicos

```
📊 RESULTADOS DEL ANÁLISIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
von Mises máximo:     157.3 MPa
Principal máximo:     145.8 MPa  
Factor de seguridad:  1.59
Estado:               ⚠️ REVISAR DISEÑO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🏗️ Arquitectura del Software

```
src/
├── 🔧 config/          # Configuración y constantes
│   ├── settings.py     # Parámetros globales
│   └── __init__.py
├── 🎯 core/            # Funcionalidades centrales  
│   ├── geometry.py     # Geometría de dovelas
│   ├── stress_analysis.py  # Análisis de esfuerzos
│   ├── fea_solver.py   # Solucionador FEA (opcional)
│   └── __init__.py
├── 🖥️ gui/            # Interfaz gráfica
│   ├── main_window.py  # Ventana principal
│   └── __init__.py
├── 🛠️ utils/          # Utilidades
│   ├── logging_config.py   # Sistema de logging
│   ├── validators.py   # Validación de parámetros
│   ├── unit_converter.py   # Conversión de unidades
│   └── __init__.py
├── main.py            # Punto de entrada principal
└── __init__.py
```

---

## 🔬 Fundamentos Técnicos

### Métodos de Análisis

1. **Análisis Clásico**
   - Teoría de vigas de Euler-Bernoulli
   - Concentración de esfuerzos según Peterson
   - Factor de concentración: Kt = 3.0 (geometría de esquina)

2. **Análisis AASHTO** 
   - Cumplimiento AASHTO 14.5.1 (Capacidades)
   - Cumplimiento AASHTO 14.5.2 (Detalles constructivos)
   - Factores de seguridad según especificación

3. **Análisis FEA** (Opcional)
   - Elementos triangulares lineales
   - Malla adaptativa en zonas críticas
   - Biblioteca: scikit-fem

### Criterios de Diseño

- **von Mises**: σ_vm ≤ fy / FS
- **Factor de Seguridad**: FS ≥ 2.0 (servicio), FS ≥ 1.67 (último)
- **Deflexión**: δ_max ≤ L/250 (criterio de servicio)

---

## 📊 Validación y Verificación

### Casos de Prueba

El software incluye validación automática contra:

1. **✅ Soluciones Analíticas**: Vigas simples con concentradores
2. **✅ Benchmarks FEA**: Modelos de referencia internacional  
3. **✅ Normas AASHTO**: Ejemplos de la especificación
4. **✅ Casos Extremos**: Validación de límites físicos

### Ejecutar Validación

```bash
python src/main.py test
```

Ejecuta **26 pruebas** que verifican:
- Módulos de configuración
- Conversión de unidades
- Cálculos de geometría
- Análisis de esfuerzos
- Validación AASHTO

---

## 🤝 Contribución

### Estructura de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Ejecutar tests
pytest tests/ -v --cov=src

# Formatear código
black src/ tests/

# Verificar tipos
mypy src/

# Linting
flake8 src/
```

### Guías de Contribución

1. **🔀 Fork** el repositorio
2. **🌿 Crear** rama feature: `git checkout -b feature/nueva-funcionalidad`
3. **💻 Desarrollar** siguiendo estándares PEP 8
4. **🧪 Agregar** tests para nueva funcionalidad
5. **📝 Documentar** cambios en docstrings
6. **📤 Pull Request** con descripción detallada

---

## 📚 Documentación Técnica

### Referencias Normativas

- **AASHTO LRFD**: Bridge Design Specifications 9th Edition
- **ACI 318**: Building Code Requirements for Structural Concrete
- **AISC 360**: Specification for Structural Steel Buildings

### Bibliografía Técnica

1. Pilkey, W.D. - *Peterson's Stress Concentration Factors*
2. Cook, R.D. - *Concepts and Applications of Finite Element Analysis*
3. Zienkiewicz, O.C. - *The Finite Element Method*

### API y Extensiones

```python
from src import DiamondDovelaGeometry, ClassicalStressAnalyzer

# Crear geometría personalizada
geometry = DiamondDovelaGeometry(
    side_length=ParameterWithUnits(125.0, "mm"),
    thickness=ParameterWithUnits(12.7, "mm"),
    joint_opening=ParameterWithUnits(4.8, "mm")
)

# Ejecutar análisis
analyzer = ClassicalStressAnalyzer()
results = analyzer.analyze(geometry, load_case, material)
```

---

## 🐛 Solución de Problemas

### Problemas Comunes

**❌ Error: "tkinter no encontrado"**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL  
sudo yum install tkinter
```

**❌ Error: "No module named 'numpy'"**
```bash
pip install --upgrade pip
pip install numpy scipy matplotlib
```

**❌ Interface no responde**
- Verificar versión Python ≥ 3.8
- Cerrar otras aplicaciones pesadas
- Revisar logs en `logs/dovela_professional.log`

### Logs y Debugging

```bash
# Ver logs en tiempo real
tail -f logs/dovela_professional.log

# Modo debug
python src/main.py --debug

# Información del sistema
python src/main.py --info
```

---

## 📄 Licencia

**MIT License** - Ver archivo [LICENSE](LICENSE) para detalles completos.

```
Copyright (c) 2025 Ingeniería Estructural Avanzada

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 👥 Créditos

### Equipo de Desarrollo

- **🎯 Arquitectura**: Ingeniería Estructural Avanzada
- **💻 Desarrollo**: Equipo de Software Técnico
- **🔬 Validación**: Consultores Especializados en Puentes
- **📚 Documentación**: Equipo Técnico de Redacción

### Agradecimientos

- **AASHTO** por las especificaciones técnicas
- **Comunidad Python** por las bibliotecas científicas
- **Usuarios Beta** por feedback y validación

---

## 📞 Soporte

### Contacto Técnico

- **📧 Email**: soporte@dovela-diamante.com
- **💬 Soporte**: [Formulario de Contacto](https://dovela-diamante.com/soporte)
- **🐛 Bugs**: [GitHub Issues](https://github.com/tu-usuario/dovela-diamante-professional/issues)
- **📖 Documentación**: [Documentación Completa](https://dovela-diamante-professional.readthedocs.io/)

### Horarios de Soporte

- **🕐 Lunes a Viernes**: 9:00 AM - 6:00 PM (UTC-5)
- **⚡ Respuesta**: < 24 horas días hábiles
- **🆘 Urgencias**: soporte-urgente@dovela-diamante.com

---

**📌 Versión**: 2.0.0 | **📅 Fecha**: Enero 2025 | **🔄 Estado**: Beta

*Software profesional para análisis estructural - Desarrollado con estándares de ingeniería*
