// app.js - Cliente para Dovela Professional Web

document.addEventListener('DOMContentLoaded', () => {
  // Referencias a elementos del DOM
  const loadInput = document.getElementById('load');
  const thicknessInput = document.getElementById('thickness');
  const analysisTypeSelect = document.getElementById('analysis-type');
  const analyzeBtn = document.getElementById('analyze-btn');
  const loadingElement = document.getElementById('loading');
  const resultsContent = document.getElementById('results-content');
  const errorMessage = document.getElementById('error-message');
  const plotImage = document.getElementById('plot-image');
  const stressMaxElement = document.getElementById('stress-max');
  const stressMinElement = document.getElementById('stress-min');
  const displacementElement = document.getElementById('displacement');
  const safetyFactorElement = document.getElementById('safety-factor');
  const analysisSummaryElement = document.getElementById('analysis-summary');

  // Función para validar los parámetros de entrada
  const validateInputs = () => {
    const load = parseFloat(loadInput.value);
    const thickness = parseFloat(thicknessInput.value);
    
    if (isNaN(load) || load <= 0) {
      alert('La carga debe ser un número positivo.');
      return false;
    }
    
    if (isNaN(thickness) || thickness <= 0) {
      alert('El espesor debe ser un número positivo.');
      return false;
    }
    
    return true;
  };

  // Función para mostrar resultados
  const displayResults = (data) => {
    // Ocultar carga y mostrar resultados
    loadingElement.classList.add('hidden');
    resultsContent.classList.remove('hidden');
    errorMessage.classList.add('hidden');
    
    // Mostrar imagen de análisis
    plotImage.src = data.plot_image;
    
    // Actualizar métricas
    stressMaxElement.textContent = `${data.stress_max.toFixed(2)} MPa`;
    stressMinElement.textContent = `${data.stress_min.toFixed(2)} MPa`;
    displacementElement.textContent = `${data.displacement_mm.toFixed(4)} mm`;
    
    // Formatear factor de seguridad con color según valor
    const safetyFactor = data.safety_factor;
    safetyFactorElement.textContent = safetyFactor.toFixed(2);
    
    if (safetyFactor < 1.0) {
      safetyFactorElement.style.color = 'var(--danger-color)';
    } else if (safetyFactor < 1.5) {
      safetyFactorElement.style.color = 'var(--warning-color)';
    } else {
      safetyFactorElement.style.color = 'var(--success-color)';
    }
    
    // Mostrar resumen
    analysisSummaryElement.textContent = data.analysis_summary;
  };

  // Función para mostrar errores
  const displayError = (message) => {
    loadingElement.classList.add('hidden');
    resultsContent.classList.add('hidden');
    errorMessage.classList.remove('hidden');
    errorMessage.querySelector('p').textContent = message || 'Error al realizar el análisis. Por favor intente de nuevo.';
  };

  // Manejador de eventos para el botón de análisis
  analyzeBtn.addEventListener('click', async () => {
    if (!validateInputs()) return;
    
    // Mostrar pantalla de carga
    loadingElement.classList.remove('hidden');
    resultsContent.classList.add('hidden');
    errorMessage.classList.add('hidden');
    
    // Preparar datos para la API
    const analysisData = {
      load_kN: parseFloat(loadInput.value),
      thickness_mm: parseFloat(thicknessInput.value),
      analysis_type: analysisTypeSelect.value
    };

    try {
      // Determinar URL del API basado en entorno
      // En desarrollo usaremos localhost, en producción la URL de Vercel
      const isProduction = window.location.hostname !== 'localhost';
      const apiBaseUrl = isProduction 
        ? 'https://dovela-professional-api.vercel.app' 
        : 'http://localhost:8000';
      
      // Llamada a la API
      const response = await fetch(`${apiBaseUrl}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(analysisData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al comunicar con el servidor');
      }
      
      const data = await response.json();
      displayResults(data);
    } catch (error) {
      console.error('Error:', error);
      displayError(error.message);
    }
  });

  // Realizar un análisis inicial al cargar la página (opcional)
  // analyzeBtn.click();
});
