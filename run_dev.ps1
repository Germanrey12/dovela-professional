# Script para ejecutar el entorno de desarrollo de Dovela Professional Web
# Requiere Python 3.10+ y las dependencias instaladas

# Activar entorno virtual si existe
if (Test-Path .\.venv\Scripts\Activate.ps1) {
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "Creando entorno virtual..."
    python -m venv .venv
    & .\.venv\Scripts\Activate.ps1
    pip install -r api/requirements.txt
}

# Iniciar el servidor API en una nueva ventana de PowerShell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; & .\.venv\Scripts\Activate.ps1; Write-Host 'Iniciando API en http://localhost:8000'; python -m uvicorn api.main:app --reload --port 8000"

# Iniciar el servidor web en otra ventana
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'Iniciando servidor web en http://localhost:3000'; cd web; python -m http.server 3000"

# Abrir el navegador
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"

Write-Host "Entorno de desarrollo iniciado:"
Write-Host "- API: http://localhost:8000"
Write-Host "- Web: http://localhost:3000"
