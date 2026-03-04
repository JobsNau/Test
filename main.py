import sys
import os
from db.repository import PropiedadesRepository
from etl.extraccion import extract, obtener_estadisticas_extraccion
from etl.transformacion import transform, obtener_estadisticas_transformacion
from utils.logging_config import setup_logger

logger = setup_logger(__name__)

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))




def main():
    """
    Proceso completo de inicialización:
    1. Obtener archivo CSV
    2. Ejecutar ETL para limpiar y transformar datos
    3. Cargar dimensiones (ubicaciones y tipos de inmueble)
    4. Cargar propiedades desde CSV
    """
    logger.info("="*60)
    logger.info("PROPIEDADES MEDELLÍN")
    logger.info("="*60)
    
    # Ruta al archivo CSV
    csv_path = "data/propiedades_medellin_raw.csv"
    
    try:
        # Usar context manager para manejo automático de recursos

        # 1. Extraer datos
        df = extract(csv_path)
        estadisticas = obtener_estadisticas_extraccion(df)
        logger.info(f"📊 Estadísticas de extracción: {estadisticas}")

        # 2. Transformar datos
        df_transformado = transform(df)
        estadisticas = obtener_estadisticas_transformacion(df_transformado)
        logger.info(f"📊 Estadísticas de transformación: {estadisticas}")

        # 3. Inicializar repository (crea conexión y tablas)
        repo = PropiedadesRepository()

        # 4. Cargar data desde DataFrame transformado
        repo.cargar_propiedades(df_transformado)

        
        
    except FileNotFoundError:
        logger.error(f"\n✗ Error: Archivo CSV no encontrado: {csv_path}")
    except Exception as e:
        logger.error(f"\n✗ Error durante la inicialización: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
