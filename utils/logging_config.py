import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = __name__, level: str = "DEBUG") -> logging.Logger:
    """
    Configura y retorna un logger con formato consistente.
    
    Args:
        name: Nombre del logger (usualmente __name__ del módulo)
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers si ya está configurado
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, level.upper()))
    
    # Formato
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler consola con UTF-8
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    # Forzar UTF-8 en Windows
    if hasattr(console_handler.stream, 'reconfigure'):
        console_handler.stream.reconfigure(encoding='utf-8')
    logger.addHandler(console_handler)
    
    # Handler archivo (opcional, si existe carpeta logs/)
    log_dir = "logs"
    if os.path.exists(log_dir) or os.makedirs(log_dir, exist_ok=True):
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "test_AA.log"),
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'  # UTF-8 para archivos
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
