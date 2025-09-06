# Dovela Professional - Aplicación Web

Este proyecto convierte la aplicación de escritorio "Dovela Professional" en una aplicación web que puede ser desplegada en Vercel.

## Descripción

Dovela Professional es una herramienta para análisis de dovelas diamante, originalmente desarrollada como una aplicación de escritorio con Python y Tkinter. Esta versión web mantiene la misma funcionalidad pero la hace accesible desde cualquier navegador.

## Estructura del Proyecto

```
dovela-professional/
├── api/                  # Backend con FastAPI
│   ├── main.py           # Punto de entrada de la API 
│   └── requirements.txt  # Dependencias de la API
├── web/                  # Frontend
│   ├── index.html        # Página principal
│   ├── styles.css        # Estilos de la aplicación
│   ├── app.js            # Lógica del cliente
│   └── favicon.svg       # Icono de la aplicación
├── vercel.json           # Configuración para Vercel
├── run_dev.ps1           # Script para ejecutar en desarrollo
└── README.md             # Este archivo
```

## Características

- **Backend API con FastAPI**: Expone los cálculos y análisis como servicios web
- **Frontend Web Responsivo**: Interfaz de usuario moderna accesible desde cualquier dispositivo
- **Análisis Completos**: Mismas capacidades que la versión de escritorio
- **Visualizaciones Profesionales**: Gráficos de contorno para resultados de análisis

## Requisitos

- Python 3.10 o superior
- Dependencias listadas en `api/requirements.txt`

## Ejecución Local

Para ejecutar la aplicación en modo desarrollo:

1. Clonar el repositorio
2. Ejecutar el script `run_dev.ps1` (Windows) o los comandos equivalentes en Linux/Mac:

```powershell
# En Windows
.\run_dev.ps1
```

Para Linux/Mac:

```bash
# Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r api/requirements.txt

# Iniciar API en un terminal
uvicorn api.main:app --reload --port 8000

# En otro terminal, iniciar servidor web
cd web
python -m http.server 3000
```

La aplicación estará disponible en `http://localhost:3000` con la API en `http://localhost:8000`.

## Despliegue en Vercel

La aplicación está configurada para despliegue automático en Vercel. Solo necesitas:

1. Conectar tu cuenta de Vercel con el repositorio de GitHub
2. Importar el proyecto
3. Vercel detectará automáticamente la configuración necesaria desde `vercel.json`

## Desarrollo Futuro

- Implementación de más tipos de análisis
- Exportación de resultados en PDF
- Comparación entre diferentes configuraciones de dovelas

## Licencia

Ver archivo LICENSE incluido en el repositorio.

---

Desarrollado por Germán Andrés Rey Carrillo
