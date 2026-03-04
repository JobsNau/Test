from math import log
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from db.models import Base, DimUbicacion, DimTipoInmueble, Propiedad
from utils.logging_config import setup_logger
from db.seed_data import seed_ubicaciones, seed_tipos_inmueble, verificar_datos
import psycopg2.extras
from dotenv import load_dotenv
load_dotenv()

logger = setup_logger(__name__)


class PropiedadesRepository:
    """
    Repository para gestión de propiedades inmobiliarias.
    
    Responsabilidades:
    - Crear conexión a base de datos (PostgreSQL, MySQL, SQLite)
    - Crear tablas si no existen
    - Cargar tablas de dimensiones (dim_ubicaciones, dim_tipos_inmueble)
    - Cargar tabla de hechos (propiedades)
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Inicializa el repository y crea conexión a base de datos.
        
        Args:
            database_url: URL de conexión. Si es None, se lee de variables de entorno
                         o se usa SQLite por defecto.
        
        Ejemplos de URLs:
            - PostgreSQL: "postgresql://user:pass@localhost:5432/propiedades_medellin"
            - MySQL: "mysql+pymysql://user:pass@localhost:3306/propiedades_medellin"
            - SQLite: "sqlite:///./propiedades_medellin.db"
        """
        self.database_url = database_url or self._get_database_url()
        self.engine = None
        self.session = None
        
        # Crear conexión
        self._create_connection()
        
        # Crear tablas si no existen
        self._create_tables_if_not_exist()

        # # Cargar datos maestros
        # seed_ubicaciones(self.session)
        # seed_tipos_inmueble(self.session)
        # verificar_datos(self.session)
        self.close()
    
    def _get_database_url(self) -> str:
        """Obtiene URL de base de datos desde variables de entorno o usa SQLite."""
        # Intentar leer desde variable de entorno
        db_url = os.getenv("DATABASE_URL")
        
        if db_url:
            return db_url
        
        # Si no hay variable de entorno, construir desde componentes
        db_type = os.getenv("DB_TYPE", "sqlite")  # postgresql, mysql, sqlite
        
        if db_type == "postgresql":
            user = os.getenv("DB_USER", "postgres")
            password = os.getenv("DB_PASSWORD", "")
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "5432")
            name = os.getenv("DB_NAME", "propiedades_medellin")
            return f"postgresql://{user}:{password}@{host}:{port}/{name}"
        
        elif db_type == "mysql":
            user = os.getenv("DB_USER", "root")
            password = os.getenv("DB_PASSWORD", "")
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "3306")
            name = os.getenv("DB_NAME", "propiedades_medellin")
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
        
        else:  # SQLite por defecto
            db_path = os.getenv("DB_PATH", "./propiedades_medellin.db")
            return f"sqlite:///{db_path}"
    
    def _create_connection(self):
        """Crea la conexión a la base de datos."""
        
        try:
            # Configuración específica para SQLite
            connect_args = {}
            if self.database_url.startswith("sqlite"):
                connect_args = {"check_same_thread": False}
            
            # Crear engine
            self.engine = create_engine(
                self.database_url,
                connect_args=connect_args,
                echo=False,  # Cambiar a True para ver SQL queries
                pool_pre_ping=True
            )
            
            # Crear sessionmaker
            SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self.session = SessionLocal()
            
            # Verificar conexión
            with self.engine.connect() as conn:
                logger.info("✓ Conexión establecida exitosamente")
                
        except Exception as e:
            logger.error(f"✗ Error al conectar a la base de datos: {e}")
            raise
    
    def _create_tables_if_not_exist(self):
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=self.engine)
        
        logger.info(f"\n✓ Verificación de tablas completada")
    
    def get_or_create_ubicacion(self, nombre_ubicacion: str, 
                                ciudad: str = "Medellín", 
                                departamento: str = "Antioquia") -> DimUbicacion:
        """
        Obtiene una ubicación existente o la crea si no existe.
        
        Args:
            nombre_ubicacion: Nombre de la ubicación
            ciudad: Ciudad (por defecto Medellín)
            departamento: Departamento (por defecto Antioquia)
        
        Returns:
            Objeto DimUbicacion
        """
        # Buscar ubicación existente
        ubicacion = self.session.query(DimUbicacion).filter_by(
            nombre_ubicacion=nombre_ubicacion
        ).first()
        
        if ubicacion:
            return ubicacion
        
        # Crear nueva ubicación
        nueva_ubicacion = DimUbicacion(
            nombre_ubicacion=nombre_ubicacion,
            ciudad=ciudad,
            departamento=departamento
        )
        
        self.session.add(nueva_ubicacion)
        self.session.flush()  # Para obtener el ID sin hacer commit
        
        return nueva_ubicacion
    
    def get_or_create_tipo_inmueble(self, nombre_tipo: str, ) -> DimTipoInmueble:
        """
        Obtiene un tipo de inmueble existente o lo crea si no existe.
        
        Args:
            nombre_tipo: Nombre del tipo (Casa, Apartamento, etc.)
        
        Returns:
            Objeto DimTipoInmueble
        """
        # Buscar tipo existente
        tipo = self.session.query(DimTipoInmueble).filter_by(
            nombre_tipo=nombre_tipo
        ).first()
        
        if tipo:
            return tipo
        
        # Crear nuevo tipo
        nuevo_tipo = DimTipoInmueble(
            nombre_tipo=nombre_tipo
        )
        
        self.session.add(nuevo_tipo)
        self.session.flush()
        
        return nuevo_tipo
    
    def cargar_propiedades(self, df: pd.DataFrame):

        if self.database_url.startswith("postgresql"):
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
            )
            cursor = conn.cursor()

            try:
                tipos = df["tipo_inmueble"].dropna().unique()

                insert_tipos_query = """
                    INSERT INTO dim_tipos_inmueble (nombre_tipo)
                    VALUES (%s)
                    ON CONFLICT (nombre_tipo) DO NOTHING
                """
                logger.info("\nCargando tipos de inmueble...")
                logger.info(insert_tipos_query)

                for tipo in tipos:
                    cursor.execute(insert_tipos_query, (tipo,))

                ubicaciones = df["ubicacion"].dropna().unique()

                insert_ubicaciones_query = """
                    INSERT INTO dim_ubicaciones (nombre_ubicacion, ciudad, departamento)
                    VALUES (%s, 'Medellín', 'Antioquia')
                    ON CONFLICT (nombre_ubicacion) DO NOTHING
                """
                logger.info("\nCargando ubicaciones...")
                logger.info(insert_ubicaciones_query)

                for ubicacion in ubicaciones:
                    cursor.execute(insert_ubicaciones_query, (ubicacion,))


                cursor.execute("SELECT id_tipo_inmueble, nombre_tipo FROM dim_tipos_inmueble")
                tipo_map = dict(cursor.fetchall())
                tipo_map = {v: k for k, v in tipo_map.items()}

                cursor.execute("SELECT id_ubicacion, nombre_ubicacion FROM dim_ubicaciones")
                ubicacion_map = dict(cursor.fetchall())
                ubicacion_map = {v: k for k, v in ubicacion_map.items()}

                df["id_tipo_inmueble"] = df["tipo_inmueble"].map(tipo_map)
                df["id_ubicacion"] = df["ubicacion"].map(ubicacion_map)

                propiedades_records = df[
                    [
                        "id_propiedad",
                        "nombre_anuncio",
                        "precio_venta",
                        "metraje_m2",
                        "estrato_socioeconomico",
                        "id_ubicacion",
                        "id_tipo_inmueble",
                        "fecha_publicacion",
                    ]
                ].values.tolist()

                insert_propiedades_query = """
                    INSERT INTO propiedades (
                        id_propiedad,
                        nombre_anuncio,
                        precio_venta,
                        metraje_m2,
                        estrato_socioeconomico,
                        id_ubicacion,
                        id_tipo_inmueble,
                        fecha_publicacion
                    )
                    VALUES %s
                    ON CONFLICT (id_propiedad) DO NOTHING
                """

                psycopg2.extras.execute_values(
                    cursor,
                    insert_propiedades_query,
                    propiedades_records
                )
                logger.info("\nCargando propiedades...")
                logger.info(insert_propiedades_query)

                conn.commit()

            except Exception as e:
                conn.rollback()
                logger.error("Error during load process: %s", str(e))
                raise

            finally:
                cursor.close()
                conn.close()

        if self.database_url.startswith("sqlite"):
            conn = self.engine.raw_connection()
            cursor = conn.cursor()

            try:
                tipos = df["tipo_inmueble"].dropna().unique()

                insert_tipos_query = """
                    INSERT OR IGNORE INTO dim_tipos_inmueble (nombre_tipo)
                    VALUES (?)
                """
                logger.info("\nCargando tipos de inmueble...")
                logger.info(insert_tipos_query)

                for tipo in tipos:
                    cursor.execute(insert_tipos_query, (tipo,))

                ubicaciones = df["ubicacion"].dropna().unique()

                insert_ubicaciones_query = """
                    INSERT OR IGNORE INTO dim_ubicaciones (nombre_ubicacion, ciudad, departamento)
                    VALUES (?, 'Medellín', 'Antioquia')
                """
                logger.info("\nCargando ubicaciones...")
                logger.info(insert_ubicaciones_query)

                for ubicacion in ubicaciones:
                    cursor.execute(insert_ubicaciones_query, (ubicacion,))

                cursor.execute("SELECT id_tipo_inmueble, nombre_tipo FROM dim_tipos_inmueble")
                tipo_map = dict(cursor.fetchall())
                tipo_map = {v: k for k, v in tipo_map.items()}

                cursor.execute("SELECT id_ubicacion, nombre_ubicacion FROM dim_ubicaciones")
                ubicacion_map = dict(cursor.fetchall())
                ubicacion_map = {v: k for k, v in ubicacion_map.items()}

                df["id_tipo_inmueble"] = df["tipo_inmueble"].map(tipo_map)
                df["id_ubicacion"] = df["ubicacion"].map(ubicacion_map)

                propiedades_records = df[
                    [
                        "id_propiedad",
                        "nombre_anuncio",
                        "precio_venta",
                        "metraje_m2",
                        "estrato_socioeconomico",
                        "id_ubicacion",
                        "id_tipo_inmueble",
                        "fecha_publicacion",
                    ]
                ].values.tolist()

                insert_propiedades_query = """
                    INSERT OR IGNORE INTO propiedades (
                        id_propiedad,
                        nombre_anuncio,
                        precio_venta,
                        metraje_m2,
                        estrato_socioeconomico,
                        id_ubicacion,
                        id_tipo_inmueble,
                        fecha_publicacion
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """

                cursor.executemany(
                    insert_propiedades_query,
                    propiedades_records
                )
                logger.info("\nCargando propiedades...")
                logger.info(insert_propiedades_query)

                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error("Error during SQLite load process: %s", str(e))
                raise

            finally:
                cursor.close()
                conn.close()

    
    def _insert_batch(self, batch: List):
        """Inserta un lote de propiedades usando SQL directo."""
        placeholders = ",".join([
            f"({','.join(['?' if 'sqlite' in self.database_url else '%s'] * 8)})"
            for _ in range(len(batch))
        ])
        
        query = f"""
            INSERT INTO propiedades (
                id_propiedad, nombre_anuncio, precio_venta, metraje_m2,
                estrato_socioeconomico, id_ubicacion, id_tipo_inmueble, fecha_publicacion
            ) VALUES {placeholders} ON CONFLICT (id_propiedad) DO NOTHING
        """
        
        flat_batch = [item for row in batch for item in row]
        self.session.execute_values(query, flat_batch)
        self.session.commit()

    
    def close(self):
        """Cierra la sesión de base de datos."""
        if self.session:
            self.session.close()
            logger.info("\n✓ Sesión cerrada")