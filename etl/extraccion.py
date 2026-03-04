import pandas as pd
from pathlib import Path
from typing import Dict
from utils.logging_config import setup_logger

logger = setup_logger(__name__)

# Columnas requeridas en el CSV
REQUIRED_COLUMNS = {
    "id_propiedad",
    "nombre_anuncio",
    "precio_venta",
    "metraje_m2",
    "estrato_socioeconomico",
    "ubicacion",
    "tipo_inmueble",
    "fecha_publicacion",
}


def extract(csv_path: str, encoding: str = 'utf-8') -> pd.DataFrame:
    """
    Extrae datos desde un archivo CSV con validaciones completas.

    Args:
        csv_path (str): Ruta al archivo CSV
        encoding (str): Codificación del archivo (default: utf-8)

    Returns:
        pd.DataFrame: DataFrame con datos crudos extraídos

    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si faltan columnas requeridas o el archivo está vacío
    """

    path = Path(csv_path)

    # Validación 1: Archivo existe
    if not path.exists():
        logger.error("Archivo no encontrado: %s", csv_path)
        raise FileNotFoundError(f"Archivo no encontrado: {csv_path}")

    # Validación 2: Es un archivo (no directorio)
    if not path.is_file():
        logger.error("La ruta no es un archivo: %s", csv_path)
        raise ValueError(f"La ruta no es un archivo: {csv_path}")

    # Validación 3: Extensión correcta
    if path.suffix.lower() not in ['.csv']:
        logger.warning("Extensión de archivo inusual: %s", path.suffix)

    logger.info("="*60)
    logger.info("INICIANDO EXTRACCIÓN DE DATOS")
    logger.info("="*60)
    logger.info("Archivo: %s", csv_path)
    
    # Intentar leer con diferentes encodings si falla
    encodings_to_try = [encoding, 'utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    df = None
    
    for enc in encodings_to_try:
        try:
            logger.info("Intentando leer con encoding: %s", enc)
            df = pd.read_csv(path, encoding=enc)
            logger.info("✓ CSV leído exitosamente con encoding: %s", enc)
            break
        except UnicodeDecodeError:
            logger.warning("Fallo con encoding %s, probando siguiente...", enc)
            continue
        except Exception as e:
            logger.error("Error inesperado al leer CSV: %s", str(e))
            raise
    
    if df is None:
        raise ValueError(f"No se pudo leer el archivo con ningún encoding probado")

    # Validación 4: DataFrame no está vacío
    if df.empty:
        logger.error("El archivo CSV está vacío")
        raise ValueError("El archivo CSV está vacío")

    logger.info("Total de registros leídos: %s", len(df))
    logger.info("Total de columnas: %s", len(df.columns))

    # Validación 5: Columnas requeridas presentes
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        logger.error("Faltan columnas requeridas: %s", missing_columns)
        raise ValueError(f"Faltan columnas requeridas: {missing_columns}")
    
    extra_columns = set(df.columns) - REQUIRED_COLUMNS
    if extra_columns:
        logger.info("Columnas adicionales encontradas: %s", extra_columns)


    logger.info("="*60)
    logger.info("✓ EXTRACCIÓN COMPLETADA EXITOSAMENTE")
    logger.info("="*60)

    return df

def obtener_estadisticas_extraccion(df: pd.DataFrame) -> Dict:
    """
    Obtiene estadísticas detalladas de los datos extraídos.
    
    Args:
        df: DataFrame extraído
    
    Returns:
        Dict con estadísticas de extracción
    """
    return {
        'total_registros': len(df),
        'total_columnas': len(df.columns),
        'duplicados': df['id_propiedad'].duplicated().sum(),
        'memoria_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
        'valores_nulos': df.isnull().sum().to_dict(),
        'ubicaciones_unicas': df['ubicacion'].nunique(),
        'tipos_inmueble_unicos': df['tipo_inmueble'].nunique(),
        'estratos_unicos': df['estrato_socioeconomico'].nunique(),
    }