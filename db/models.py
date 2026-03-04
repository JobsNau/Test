from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, CheckConstraint, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DimUbicacion(Base):
    """
    Tabla maestra de ubicaciones geográficas.
    
    Propósito: Catálogo normalizado de ubicaciones para garantizar
    integridad referencial y evitar redundancias.
    
    Relaciones:
        - Tiene muchas propiedades (1:N)
    """
    __tablename__ = "dim_ubicaciones"
    
    # Columnas
    id_ubicacion = Column(
        Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="Identificador único de la ubicación"
    )
    
    nombre_ubicacion = Column(
        String(100), 
        unique=True, 
        nullable=False,
        index=True,
        comment="Nombre normalizado de la ubicación"
    )
    
    ciudad = Column(
        String(50), 
        nullable=False,
        default="Medellín",
        comment="Ciudad donde se ubica"
    )
    
    departamento = Column(
        String(50), 
        nullable=False,
        default="Antioquia",
        comment="Departamento"
    )
    
    # Timestamps
    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Fecha de creación del registro"
    )
    
    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Fecha de última actualización"
    )
    
    # Relaciones
    propiedades = relationship(
        "Propiedad",
        back_populates="ubicacion",
        cascade="all, delete",  # Si se elimina ubicación, se eliminan propiedades
        passive_deletes=True
    )
    
    def __repr__(self):
        return f"<DimUbicacion(id={self.id_ubicacion}, nombre='{self.nombre_ubicacion}')>"
    
    def __str__(self):
        return f"{self.nombre_ubicacion}, {self.ciudad}"


class DimTipoInmueble(Base):
    """
    Tabla maestra de tipos de inmuebles.
    
    Propósito: Catálogo de clasificación de tipos de propiedades
    para garantizar integridad referencial.
    
    Relaciones:
        - Clasifica muchas propiedades (1:N)
    """
    __tablename__ = "dim_tipos_inmueble"
    
    # Columnas
    id_tipo_inmueble = Column(
        Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="Identificador único del tipo de inmueble"
    )
    
    nombre_tipo = Column(
        String(50), 
        unique=True, 
        nullable=False,
        index=True,
        comment="Nombre del tipo de inmueble (Casa, Apartamento, etc.)"
    )
    
    # Timestamps
    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Fecha de creación del registro"
    )
    
    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Fecha de última actualización"
    )
    
    # Relaciones
    propiedades = relationship(
        "Propiedad",
        back_populates="tipo_inmueble",
        cascade="all, delete",
        passive_deletes=True
    )
    
    def __repr__(self):
        return f"<DimTipoInmueble(id={self.id_tipo_inmueble}, tipo='{self.nombre_tipo}')>"
    
    def __str__(self):
        return f"{self.nombre_tipo}"


class Propiedad(Base):
    """
    Tabla de hechos con información detallada de propiedades.
    
    Propósito: Almacenar datos específicos de cada propiedad inmobiliaria,
    relacionados con tablas maestras mediante llaves foráneas.
    
    Relaciones:
        - Pertenece a una ubicación (N:1)
        - Pertenece a un tipo de inmueble (N:1)
    """
    __tablename__ = "propiedades"
    
    # Columna primaria
    id_propiedad = Column(
        Integer, 
        primary_key=True,
        comment="Identificador único de la propiedad"
    )
    
    # Información básica
    nombre_anuncio = Column(
        String(200),
        nullable=True,
        comment="Título del anuncio de la propiedad"
    )
    
    # Información financiera
    precio_venta = Column(
        Numeric(15, 2),
        nullable=True,
        comment="Precio de venta en pesos colombianos (COP)"
    )
    
    # Información física
    metraje_m2 = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Área total en metros cuadrados"
    )
    
    # Información socioeconómica
    estrato_socioeconomico = Column(
        Integer,
        nullable=True,
        comment="Estrato socioeconómico (1-6)"
    )
    
    # Llaves foráneas
    id_ubicacion = Column(
        Integer,
        ForeignKey(
            "dim_ubicaciones.id_ubicacion",
            ondelete="RESTRICT",  # No permite eliminar ubicación si tiene propiedades
            onupdate="CASCADE"    # Actualiza en cascada si cambia el ID
        ),
        nullable=False,
        # index=True,
        comment="Referencia a la tabla de ubicaciones"
    )
    
    id_tipo_inmueble = Column(
        Integer,
        ForeignKey(
            "dim_tipos_inmueble.id_tipo_inmueble",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        ),
        nullable=False,
        # index=True,
        comment="Referencia a la tabla de tipos de inmueble"
    )
    
    # Información temporal
    fecha_publicacion = Column(
        Date,
        nullable=True,
        comment="Fecha de publicación del anuncio"
    )
    
    # Timestamps de auditoría
    fecha_carga = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Fecha de carga en el sistema"
    )
    
    # Constraints de validación
    __table_args__ = (
        CheckConstraint(
            'precio_venta IS NULL OR precio_venta > 0',
            name='chk_precio_positivo'
        ),
        CheckConstraint(
            'metraje_m2 IS NULL OR metraje_m2 >= 0',
            name='chk_metraje_positivo'
        ),
        CheckConstraint(
            'estrato_socioeconomico IS NULL OR (estrato_socioeconomico BETWEEN 1 AND 6)',
            name='chk_estrato_rango'
        ),
    )
    
    # Relaciones
    ubicacion = relationship(
        "DimUbicacion",
        back_populates="propiedades"
    )
    
    tipo_inmueble = relationship(
        "DimTipoInmueble",
        back_populates="propiedades"
    )
    
    def __repr__(self):
        return f"<Propiedad(id={self.id_propiedad}, tipo='{self.tipo_inmueble.nombre_tipo if self.tipo_inmueble else 'N/A'}')>"
    
    def __str__(self):
        return f"{self.nombre_anuncio or 'Propiedad'} - ${self.precio_venta:,.0f}" if self.precio_venta else self.nombre_anuncio or f"Propiedad #{self.id_propiedad}"
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_propiedad': self.id_propiedad,
            'nombre_anuncio': self.nombre_anuncio,
            'precio_venta': float(self.precio_venta) if self.precio_venta else None,
            'metraje_m2': float(self.metraje_m2) if self.metraje_m2 else None,
            # 'precio_m2': self.precio_m2 if self.precio_m2 is not None else None,
            'estrato_socioeconomico': self.estrato_socioeconomico,
            'ubicacion': {
                'id': self.id_ubicacion,
                'nombre': self.ubicacion.nombre_ubicacion if self.ubicacion else None,
                'ciudad': self.ubicacion.ciudad if self.ubicacion else None
            },
            'tipo_inmueble': {
                'id': self.id_tipo_inmueble,
                'nombre': self.tipo_inmueble.nombre_tipo if self.tipo_inmueble else None,
                'categoria': self.tipo_inmueble.categoria if self.tipo_inmueble else None
            },
            'fecha_publicacion': self.fecha_publicacion.isoformat() if self.fecha_publicacion else None,
            'fecha_carga': self.fecha_carga.isoformat() if self.fecha_carga else None
        }
