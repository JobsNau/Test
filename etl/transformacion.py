import pandas as pd
import numpy as np
import re
from typing import Dict, Any
from datetime import datetime
from utils.logging_config import setup_logger

logger = setup_logger(__name__)

# ============================================================================
# DICCIONARIOS DE NORMALIZACIÓN
# ============================================================================

UBICACIONES_MEDELLIN = {
    # El Poblado y variantes
    'el poblado': 'El Poblado',
    'poblado': 'El Poblado',
    'EL POBLADO': 'El Poblado',
    'POBLADO': 'El Poblado',
    
    # Envigado y variantes
    'envigado': 'Envigado',
    'ENVIGADO': 'Envigado',
    
    # Sabaneta y variantes
    'sabaneta': 'Sabaneta',
    'SABANETA': 'Sabaneta',
    
    # Belén y variantes
    'belen': 'Belén',
    'Belen': 'Belén',
    'BELEN': 'Belén',
    
    # Laureles y variantes
    'laureles': 'Laureles',
    'LAURELES': 'Laureles',
    'laureles - estadio': 'Laureles - Estadio',
    'Laureles - Estadio': 'Laureles - Estadio',
    'LAURELES - ESTADIO': 'Laureles - Estadio',
    
    # Robledo y variantes
    'robledo': 'Robledo',
    'Robledo': 'Robledo',
    'ROBLEDO': 'Robledo',
    
    # Centro y variantes
    'centro': 'Centro',
    'Centro': 'Centro',
    'CENTRO': 'Centro',
    'centro - medellín': 'Centro - Medellín',
    'Centro - Medellín': 'Centro - Medellín',
    'CENTRO - MEDELLÍN': 'Centro - Medellín',
    
    # Itagüí
    'itagui': 'Itagüí',
    'itagüí': 'Itagüí',
    'ITAGUI': 'Itagüí',
    
    # La Estrella
    'la estrella': 'La Estrella',
    'LA ESTRELLA': 'La Estrella',
}

TIPOS_INMUEBLE = {
    'casa': 'Casa',
    'Casa': 'Casa',
    'CASA': 'Casa',
    
    'apartamento': 'Apartamento',
    'Apartamento': 'Apartamento',
    'APARTAMENTO': 'Apartamento',
    
    'apartestudio': 'Apartestudio',
    'Apartestudio': 'Apartestudio',
    'APARTESTUDIO': 'Apartestudio',
    
    'finca': 'Finca',
    'Finca': 'Finca',
    'FINCA': 'Finca',
    
    'local': 'Local',
    'Local': 'Local',
    'LOCAL': 'Local',
    
    'bodega': 'Bodega',
    'Bodega': 'Bodega',
    'BODEGA': 'Bodega',
    
    'lote': 'Lote',
    'Lote': 'Lote',
    'LOTE': 'Lote',
    
    # Valores desconocidos
    '?': 'Desconocido',
    'nan': 'Desconocido',
    'none': 'Desconocido',
    'None': 'Desconocido',
    '': 'Desconocido',
}


# ============================================================================
# FUNCIONES DE LIMPIEZA
# ============================================================================

def limpiar_precio(valor: Any) -> float:
    """
    Limpia valores de precio eliminando símbolos y separadores.
    
    Args:
        valor: Valor de precio (puede ser str, int, float)
    
    Returns:
        float: Precio limpio o None si es inválido
    """
    if pd.isna(valor):
        return None
    
    try:
        valor_str = str(valor).strip()
        valor_str = valor_str.replace('$', '').replace('COP', '').replace('USD', '')
        valor_str = valor_str.replace('.', '').replace(',', '')
        precio = float(valor_str)
        
        # Validar que sea positivo
        if precio <= 0:
            return None
        
        return precio
        
    except (ValueError, TypeError) as e:
        logger.warning("No se pudo convertir precio: %s - Error: %s", valor, str(e))
        return None


def limpiar_metraje(valor: Any) -> float:
    """
    Valida y limpia valores de metraje.
    
    Args:
        valor: Valor de metraje
    
    Returns:
        float: Metraje válido o None
    """
    if pd.isna(valor):
        return None
    
    try:
        metraje = float(valor)
        
        if metraje <= 0:
            return None
        
        if metraje > 100000:
            logger.warning("Metraje muy grande: %.2f m²", metraje)
        
        return metraje
        
    except (ValueError, TypeError):
        return None


def limpiar_estrato(valor: Any) -> int:
    """
    Valida estratos socioeconómicos (deben estar entre 1 y 6).
    
    Args:
        valor: Valor de estrato
    
    Returns:
        int: Estrato válido (1-6) o None
    """
    if pd.isna(valor):
        return None
    
    try:
        estrato = int(float(valor))
        if 1 <= estrato <= 6:
            return estrato
        else:
            logger.warning("Estrato fuera de rango: %s", estrato)
            return None
            
    except (ValueError, TypeError):
        return None


def normalizar_ubicacion(ubicacion: Any) -> str:
    """
    Normaliza nombres de ubicaciones de Medellín.
    
    Args:
        ubicacion: Nombre de ubicación (puede tener variaciones)
    
    Returns:
        str: Nombre normalizado o 'Desconocida'
    """
    if pd.isna(ubicacion):
        return 'Desconocida'
    
    ubicacion_str = str(ubicacion).strip()
    
    # Buscar en diccionario de ubicaciones
    if ubicacion_str in UBICACIONES_MEDELLIN:
        return UBICACIONES_MEDELLIN[ubicacion_str]
    
    # Si no está en el diccionario, aplicar normalización básica
    # Primera letra mayúscula
    ubicacion_normalizada = ubicacion_str.title()
    
    return ubicacion_normalizada


def normalizar_tipo_inmueble(tipo: Any) -> str:
    """
    Normaliza tipos de inmueble.
    
    Args:
        tipo: Tipo de inmueble
    
    Returns:
        str: Tipo normalizado o 'Desconocido'
    """
    if pd.isna(tipo):
        return 'Desconocido'
    
    tipo_str = str(tipo).strip().lower()
    
    if tipo_str in TIPOS_INMUEBLE:
        return TIPOS_INMUEBLE[tipo_str]
    
    if tipo_str in ['', 'nan', 'none', '?', 'n/a', 'na']:
        return 'Desconocido'
    
    return tipo_str.capitalize()


def normalizar_fecha(fecha: Any) -> str:
    """
    Normaliza fechas a formato YYYY-MM-DD.
    
    Args:
        fecha: Valor de fecha en cualquier formato
    
    Returns:
        str: Fecha en formato YYYY-MM-DD o None
    """
    if pd.isna(fecha):
        return None
    
    try:
        fecha_obj = pd.to_datetime(fecha, errors='coerce')
        
        if pd.isna(fecha_obj):
            return None
        
        return fecha_obj.strftime('%Y-%m-%d')
        
    except Exception as e:
        logger.warning("No se pudo convertir fecha: %s - Error: %s", fecha, str(e))
        return None


def limpiar_nombre_anuncio(nombre: Any) -> str:
    """
    Limpia nombres de anuncios.
    
    Args:
        nombre: Nombre del anuncio
    
    Returns:
        str: Nombre limpio
    """
    if pd.isna(nombre):
        return 'Propiedad sin nombre'
    
    nombre_str = str(nombre).strip()
    
    if nombre_str.startswith('None en '):
        nombre_str = nombre_str.replace('None en ', 'Propiedad en ', 1)
    
    # Normalizar espacios múltiples
    nombre_str = re.sub(r'\s+', ' ', nombre_str)
    
    return nombre_str


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y normaliza el DataFrame completo de propiedades.

    Transformaciones aplicadas:
    1. Elimina duplicados
    2. Limpia precios (elimina $, puntos, comas)
    3. Normaliza ubicaciones (Medellín)
    4. Normaliza tipos de inmueble
    5. Valida metrajes (> 10 m²)
    6. Valida estratos (1-6)
    7. Normaliza fechas (múltiples formatos)
    8. Limpia nombres de anuncios
    9. Filtra registros inválidos

    Args:
        df (pd.DataFrame): DataFrame crudo extraído

    Returns:
        pd.DataFrame: DataFrame limpio y validado
    """

    logger.info("="*60)
    logger.info("INICIANDO TRANSFORMACIÓN DE DATOS")
    logger.info("="*60)

    inicial_count = len(df)
    logger.info("Registros iniciales: %s", inicial_count)

    # Crear copia para no modificar original
    df = df.copy()

    # ===== 1. ELIMINAR DUPLICADOS =====
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["id_propiedad"], keep='first')
    duplicados_removidos = before_dedup - len(df)
    if duplicados_removidos > 0:
        logger.info("✓ Duplicados eliminados: %s", duplicados_removidos)

    # ===== 2. LIMPIEZA DE NOMBRES DE ANUNCIOS =====
    logger.info("🔧 Limpiando nombres de anuncios...")
    df["nombre_anuncio"] = df["nombre_anuncio"].apply(limpiar_nombre_anuncio)

    # ===== 3. LIMPIEZA DE PRECIOS =====
    logger.info("🔧 Limpiando precios (eliminando $, puntos, comas)...")
    df["precio_venta"] = df["precio_venta"].apply(limpiar_precio)
    precios_nulos = df["precio_venta"].isna().sum()
    logger.info("  • Precios válidos: %s / %s", len(df) - precios_nulos, len(df))

    # ===== 4. LIMPIEZA DE METRAJES =====
    logger.info("🔧 Validando metrajes (eliminando <= 0 m²)...")
    df["metraje_m2"] = df["metraje_m2"].apply(limpiar_metraje)
    metrajes_nulos = df["metraje_m2"].isna().sum()
    logger.info("  • Metrajes válidos: %s / %s", len(df) - metrajes_nulos, len(df))

    # ===== 5. VALIDACIÓN DE ESTRATOS =====
    logger.info("🔧 Validando estratos (1-6)...")
    df["estrato_socioeconomico"] = df["estrato_socioeconomico"].apply(limpiar_estrato)
    estratos_nulos = df["estrato_socioeconomico"].isna().sum()
    logger.info("  • Estratos válidos: %s / %s", len(df) - estratos_nulos, len(df))

    # ===== 6. NORMALIZACIÓN DE UBICACIONES =====
    logger.info("🔧 Normalizando ubicaciones...")
    before_ubicacion = df['ubicacion'].nunique()
    df["ubicacion"] = df["ubicacion"].apply(normalizar_ubicacion)
    after_ubicacion = df['ubicacion'].nunique()
    logger.info("  • Ubicaciones únicas: %s → %s (consolidadas: %s)", 
                before_ubicacion, after_ubicacion, before_ubicacion - after_ubicacion)

    # ===== 7. NORMALIZACIÓN DE TIPOS DE INMUEBLE =====
    logger.info("🔧 Normalizando tipos de inmueble...")
    before_tipos = df['tipo_inmueble'].nunique()
    df["tipo_inmueble"] = df["tipo_inmueble"].apply(normalizar_tipo_inmueble)
    after_tipos = df['tipo_inmueble'].nunique()
    logger.info("  • Tipos únicos: %s → %s (consolidados: %s)", 
                before_tipos, after_tipos, before_tipos - after_tipos)

    # ===== 8. NORMALIZACIÓN DE FECHAS =====
    logger.info("🔧 Normalizando fechas (múltiples formatos)...")
    df["fecha_publicacion"] = df["fecha_publicacion"].apply(normalizar_fecha)
    fechas_nulas = df["fecha_publicacion"].isna().sum()
    logger.info("  • Fechas válidas: %s / %s", len(df) - fechas_nulas, len(df))

    # ===== 10. FILTRAR REGISTROS INVÁLIDOS =====
    logger.info("🔍 Filtrando registros inválidos...")
    before_filter = len(df)
    
    df = df[
        (df["precio_venta"].notna()) &
        (df["precio_venta"] > 0) &
        (df["metraje_m2"].notna()) &
        (df["metraje_m2"] > 0) &
        (df["estrato_socioeconomico"].notna()) &
        (df["estrato_socioeconomico"].between(1, 6)) &
        (df["fecha_publicacion"].notna())
    ]
    
    registros_filtrados = before_filter - len(df)
    logger.info("• Registros eliminados: %s", registros_filtrados)
    logger.info("• Registros válidos: %s", len(df))

    # Reset index
    df = df.reset_index(drop=True)
    
    logger.info("="*60)
    logger.info("✓ TRANSFORMACIÓN COMPLETADA")
    logger.info("="*60)
    logger.info("Registros finales: %s (%.1f%% del total)", len(df), (len(df) / inicial_count) * 100)

    return df


def obtener_estadisticas_transformacion(df: pd.DataFrame) -> Dict:
    """
    Obtiene estadísticas detalladas de los datos transformados.
    
    Args:
        df: DataFrame transformado
    
    Returns:
        Dict con estadísticas
    """
    return {
        'total_registros': len(df),
        'precio_min': float(df['precio_venta'].min()),
        'precio_max': float(df['precio_venta'].max()),
        'precio_promedio': float(df['precio_venta'].mean()),
        'metraje_min': float(df['metraje_m2'].min()),
        'metraje_max': float(df['metraje_m2'].max()),
        'metraje_promedio': float(df['metraje_m2'].mean()),
        'ubicaciones_unicas': int(df['ubicacion'].nunique()),
        'tipos_inmueble_unicos': int(df['tipo_inmueble'].nunique()),
        'top_ubicaciones': df['ubicacion'].value_counts().head(5).to_dict(),
        'distribucion_tipos': df['tipo_inmueble'].value_counts().to_dict(),
        'distribucion_estratos': df['estrato_socioeconomico'].value_counts().to_dict(),
    }
