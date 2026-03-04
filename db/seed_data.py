from db.models import DimUbicacion, DimTipoInmueble
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def seed_ubicaciones(db):
    """Carga ubicaciones iniciales basadas en el dataset."""
    ubicaciones = [
        {"nombre_ubicacion": "El Poblado", "ciudad": "Medellín", "departamento": "Antioquia"},
        {"nombre_ubicacion": "Envigado", "ciudad": "Envigado", "departamento": "Antioquia"},
        {"nombre_ubicacion": "Sabaneta", "ciudad": "Sabaneta", "departamento": "Antioquia"},
        {"nombre_ubicacion": "Robledo", "ciudad": "Medellín", "departamento": "Antioquia"},
        {"nombre_ubicacion": "Belén", "ciudad": "Medellín", "departamento": "Antioquia"},
        {"nombre_ubicacion": "Laureles", "ciudad": "Medellín", "departamento": "Antioquia"},
        {"nombre_ubicacion": "Laureles - Estadio", "ciudad": "Medellín", "departamento": "Antioquia"},
        {"nombre_ubicacion": "Centro", "ciudad": "Medellín", "departamento": "Antioquia"},
        {"nombre_ubicacion": "Centro - Medellín", "ciudad": "Medellín", "departamento": "Antioquia"},
        {"nombre_ubicacion": "Desconocida", "ciudad": "Medellín", "departamento": "Antioquia"},
    ]
    
    try:
        logger.info("\nCargando ubicaciones...")
        count = 0
        for ub_data in ubicaciones:
            # Verificar si ya existe
            existing = db.query(DimUbicacion).filter_by(
                nombre_ubicacion=ub_data["nombre_ubicacion"]
            ).first()
            
            if not existing:
                ubicacion = DimUbicacion(**ub_data)
                db.add(ubicacion)
                count += 1
        
        db.commit()
        logger.info(f"  ✓ {count} ubicaciones insertadas")
        
    except Exception as e:
        logger.error(f"  ✗ Error: {e}")
        db.rollback()
    finally:
        db.close()


def seed_tipos_inmueble(db):
    """Carga tipos de inmueble iniciales."""
    tipos = [
        {"nombre_tipo": "Casa"},
        {"nombre_tipo": "Apartamento"},
        {"nombre_tipo": "Apartestudio"},
        {"nombre_tipo": "Finca"},
        {"nombre_tipo": "Desconocido"},
    ]
    
    try:
        logger.info("Cargando tipos de inmueble...")
        count = 0
        for tipo_data in tipos:
            # Verificar si ya existe
            existing = db.query(DimTipoInmueble).filter_by(
                nombre_tipo=tipo_data["nombre_tipo"]
            ).first()
            
            if not existing:
                tipo = DimTipoInmueble(**tipo_data)
                db.add(tipo)
                count += 1
        
        db.commit()
        logger.info(f"  ✓ {count} tipos de inmueble insertados")
        
    except Exception as e:
        logger.error(f"  ✗ Error: {e}")
        db.rollback()
    finally:
        db.close()


def verificar_datos(db):
    """Verifica los datos cargados."""
    try:
        logger.info("\n" + "="*60)
        logger.info("VERIFICACIÓN DE DATOS MAESTROS")
        logger.info("="*60)
        
        # Contar ubicaciones
        ubicaciones_count = db.query(DimUbicacion).count()
        logger.info(f"\n📍 Ubicaciones en la base de datos: {ubicaciones_count}")
        
        ubicaciones = db.query(DimUbicacion).all()
        for ub in ubicaciones:
            logger.info(f"   {ub.id_ubicacion}. {ub.nombre_ubicacion}, {ub.ciudad}")
        
        # Contar tipos
        tipos_count = db.query(DimTipoInmueble).count()
        logger.info(f"\n🏠 Tipos de inmueble en la base de datos: {tipos_count}")
        
        tipos = db.query(DimTipoInmueble).all()
        for tipo in tipos:
            logger.info(f"   {tipo.id_tipo_inmueble}. {tipo.nombre_tipo}")
        
        logger.info("\n" + "="*60)
        
    finally:
        db.close()


def main(db):
    """Ejecuta la carga de datos maestros."""
    logger.info("="*60)
    logger.info("CARGA DE DATOS MAESTROS")
    logger.info("="*60)
    
    try:
        seed_ubicaciones(db)
        seed_tipos_inmueble(db)
        verificar_datos(db)
        
        logger.info("\n✓ Datos maestros cargados exitosamente!")
        
    except Exception as e:
        logger.error(f"\n✗ Error en la carga de datos: {e}")
        raise


if __name__ == "__main__":
    main()
