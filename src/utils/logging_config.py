"""
Sistema de logging profesional para análisis de dovelas
"""
import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Formatter con colores para consola"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
        return super().format(record)


def setup_professional_logging(log_dir: str = "logs", app_name: str = "dovela_analysis"):
    """
    Configura sistema de logging profesional
    
    Args:
        log_dir: Directorio para archivos de log
        app_name: Nombre de la aplicación
    """
    
    # Crear directorio de logs
    Path(log_dir).mkdir(exist_ok=True)
    
    # Timestamp para archivos únicos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Configurar formato detallado para archivo
    file_formatter = logging.Formatter(
        '%(asctime)s | %(name)-20s | %(levelname)-8s | '
        '%(funcName)-15s:%(lineno)-3d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configurar formato simple para consola
    console_formatter = ColoredFormatter(
        '%(levelname)s: %(message)s'
    )
    
    # Handler para archivo principal (toda la sesión)
    main_log_file = os.path.join(log_dir, f"{app_name}_{timestamp}.log")
    file_handler = logging.FileHandler(main_log_file, encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Handler rotativo para archivo de errores
    error_log_file = os.path.join(log_dir, f"{app_name}_errors.log")
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file, 
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setFormatter(file_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Agregar handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # Logger específico para análisis FEA
    fea_logger = logging.getLogger('dovela.fea')
    fea_logger.setLevel(logging.DEBUG)
    
    # Logger específico para GUI
    gui_logger = logging.getLogger('dovela.gui')
    gui_logger.setLevel(logging.INFO)
    
    # Logger específico para validación
    validation_logger = logging.getLogger('dovela.validation')
    validation_logger.setLevel(logging.WARNING)
    
    # Mensaje inicial
    root_logger.info("="*60)
    root_logger.info(f"SISTEMA DE LOGGING INICIALIZADO - {app_name.upper()}")
    root_logger.info(f"Archivo principal: {main_log_file}")
    root_logger.info(f"Archivo de errores: {error_log_file}")
    root_logger.info("="*60)
    
    return {
        'main_log_file': main_log_file,
        'error_log_file': error_log_file,
        'fea_logger': fea_logger,
        'gui_logger': gui_logger,
        'validation_logger': validation_logger
    }


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene logger específico para módulo
    
    Args:
        name: Nombre del módulo (ej: 'dovela.stress_analysis')
    
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


class AnalysisProgressLogger:
    """Logger especializado para progreso de análisis"""
    
    def __init__(self, name: str = "dovela.analysis"):
        self.logger = logging.getLogger(name)
        self.start_time = None
        self.step_count = 0
    
    def start_analysis(self, analysis_type: str, total_steps: int = None):
        """Inicia logging de análisis"""
        self.start_time = datetime.now()
        self.step_count = 0
        
        self.logger.info("🚀 " + "="*50)
        self.logger.info(f"🚀 INICIANDO ANÁLISIS: {analysis_type.upper()}")
        if total_steps:
            self.logger.info(f"🚀 Pasos estimados: {total_steps}")
        self.logger.info("🚀 " + "="*50)
    
    def log_step(self, step_description: str, detail: str = None):
        """Log de paso individual"""
        self.step_count += 1
        elapsed = datetime.now() - self.start_time if self.start_time else None
        
        if elapsed:
            elapsed_str = f"[{elapsed.total_seconds():.1f}s]"
        else:
            elapsed_str = ""
        
        msg = f"✓ Paso {self.step_count}: {step_description} {elapsed_str}"
        self.logger.info(msg)
        
        if detail:
            self.logger.debug(f"   └─ {detail}")
    
    def log_error(self, error_description: str, exception: Exception = None):
        """Log de error en análisis"""
        self.logger.error(f"❌ ERROR: {error_description}")
        if exception:
            self.logger.error(f"   └─ Excepción: {str(exception)}")
            self.logger.debug(f"   └─ Traceback completo:", exc_info=True)
    
    def finish_analysis(self, success: bool = True, summary: str = None):
        """Finaliza logging de análisis"""
        elapsed = datetime.now() - self.start_time if self.start_time else None
        
        if success:
            self.logger.info("🎉 " + "="*50)
            self.logger.info("🎉 ANÁLISIS COMPLETADO EXITOSAMENTE")
        else:
            self.logger.error("💥 " + "="*50)
            self.logger.error("💥 ANÁLISIS TERMINADO CON ERRORES")
        
        if elapsed:
            self.logger.info(f"⏱️  Tiempo total: {elapsed.total_seconds():.1f} segundos")
        
        self.logger.info(f"📊 Pasos ejecutados: {self.step_count}")
        
        if summary:
            self.logger.info(f"📋 Resumen: {summary}")
        
        if success:
            self.logger.info("🎉 " + "="*50)
        else:
            self.logger.error("💥 " + "="*50)
