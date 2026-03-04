database_url = "sqlite:///./datos_clima.db"
from sqlalchemy import DateTime, create_engine, Column, Integer, Float, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
class Clima(Base):
    __tablename__ = "clima"

    id = Column(Integer, primary_key=True, index=True)
    municipio = Column(String, index=True)
    temperatura = Column(Float)
    weather_code = Column(Integer)
    weather_description = Column(String)
    latitud = Column(Float)
    longitud = Column(Float)
    fecha = Column(DateTime(timezone=True))
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

engine = create_engine(database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def upsert_or_update_clima(municipio, temperatura, weather_code, latitud=None, longitud=None, fecha=None):
    session = SessionLocal()
    clima = session.query(Clima).filter(Clima.municipio == municipio).first()

    if clima:
        clima.temperatura = temperatura
        clima.weather_code = weather_code
        clima.latitud = latitud
        clima.longitud = longitud
        clima.fecha = fecha
    else:
        clima = Clima(
            municipio=municipio,
            temperatura=temperatura,
            weather_code=weather_code,
            latitud=latitud,
            longitud=longitud,
            fecha=fecha
        )
        session.add(clima)

    session.commit()
    session.close()