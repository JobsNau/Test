# 📋 Reglas de Limpieza - ETL Propiedades Medellín

Documentación completa de todas las reglas de limpieza y validación implementadas en los módulos de extracción y transformación.

## 📥 Módulo de Extracción (`extraccion.py`)

### Validaciones Implementadas

#### 1. Validación de Archivo
- ✅ Verifica que el archivo existe
- ✅ Verifica que es un archivo (no directorio)
- ✅ Valida extensión (.csv o .txt)
- ✅ Reporta tamaño del archivo

#### 2. Manejo de Encoding
Intenta leer con múltiples encodings automáticamente:
1. UTF-8 (predeterminado)
2. Latin1
3. ISO-8859-1
4. CP1252 (Windows)

#### 3. Validación de Estructura
- ✅ Verifica que el archivo no está vacío
- ✅ Valida que existan todas las columnas requeridas:
  - `id_propiedad`
  - `nombre_anuncio`
  - `precio_venta`
  - `metraje_m2`
  - `estrato_socioeconomico`
  - `ubicacion`
  - `tipo_inmueble`
  - `fecha_publicacion`

#### 4. Detección de Problemas
- ⚠️ Detecta duplicados por `id_propiedad`
- ⚠️ Identifica valores nulos en cada columna
- ⚠️ Reporta porcentaje de nulos
- ⚠️ Cuenta valores únicos en columnas categóricas

#### 5. Reportes Generados
- 📊 Total de registros extraídos
- 📊 Total de columnas
- 📊 Uso de memoria
- 📊 Duplicados encontrados
- 📊 Valores nulos por columna
- 📊 Valores únicos (ubicaciones, tipos, estratos)
- 📊 Rangos de precios y metrajes

---

## 🔧 Módulo de Transformación (`transformacion.py`)

### Transformaciones en Orden de Ejecución

#### 1. Eliminación de Duplicados
```python
df.drop_duplicates(subset=["id_propiedad"], keep='first')
```
- Elimina registros con `id_propiedad` duplicado
- Mantiene la primera ocurrencia

#### 2. Limpieza de Nombres de Anuncios

**Función:** `limpiar_nombre_anuncio()`

**Problemas detectados en el CSV:**
```
"None en Robledo"      → "Propiedad en Robledo"
"None en Laureles"     → "Propiedad en Laureles"
```

**Reglas aplicadas:**
- Reemplaza "None en ..." por "Propiedad en ..."
- Normaliza espacios múltiples
- Maneja valores nulos → "Propiedad sin nombre"

#### 3. Limpieza de Precios

**Función:** `limpiar_precio()`

**Problemas detectados en el CSV:**
```
"$ 2.441.000.000"      → 2441000000.0
"$ 580.000.000"        → 580000000.0
"1,500,000"            → 1500000.0
"1989000000"           → 1989000000.0
```

**Reglas aplicadas:**
- ✅ Elimina símbolo de precio: `$`, `COP`, `USD`
- ✅ Elimina separadores de miles: `.` y `,`
- ✅ Convierte a float
- ✅ Valida que sea > 0
- ✅ Valida rango razonable (10M - 100,000M COP)
- ❌ Rechaza precios negativos o cero
- ⚠️ Advierte sobre precios fuera de rango

#### 4. Limpieza de Metrajes

**Función:** `limpiar_metraje()`

**Problemas detectados en el CSV:**
```
0        → None (rechazado)
-50      → None (rechazado)
1        → None (rechazado, muy pequeño)
```

**Reglas aplicadas:**
- ❌ Rechaza valores ≤ 0
- ❌ Rechaza valores < 10 m² (demasiado pequeños para ser realistas)
- ⚠️ Advierte sobre valores > 10,000 m² (muy grandes)
- ✅ Acepta valores entre 10 - 10,000 m²

#### 5. Validación de Estratos

**Función:** `limpiar_estrato()`

**Problemas detectados en el CSV:**
```
""       → None (rechazado)
2.0      → 2 (convertido a entero)
7        → None (rechazado, fuera de rango)
```

**Reglas aplicadas:**
- ✅ Convierte a entero (de float 2.0 → 2)
- ✅ Valida rango válido: 1 - 6 (estratos de Colombia)
- ❌ Rechaza valores fuera del rango 1-6
- ❌ Rechaza valores nulos

#### 6. Normalización de Ubicaciones

**Función:** `normalizar_ubicacion()`

**Problemas detectados en el CSV:**

| Variantes Encontradas | Normalizado a |
|-----------------------|---------------|
| `El Poblado`, `EL POBLADO`, `POBLADO`, `poblado` | `El Poblado` |
| `Envigado`, `ENVIGADO`, `envigado` | `Envigado` |
| `Sabaneta`, `SABANETA`, `sabaneta` | `Sabaneta` |
| `Belen`, `Belén`, `BELEN` | `Belén` |
| `Laureles`, `LAURELES`, `laureles` | `Laureles` |
| `Laureles - Estadio`, `LAURELES - ESTADIO` | `Laureles - Estadio` |
| `Robledo`, `ROBLEDO`, `robledo` | `Robledo` |
| `Centro`, `CENTRO`, `centro` | `Centro` |
| `Centro - Medellín`, `CENTRO - MEDELLÍN` | `Centro - Medellín` |
| `Itagui`, `Itagüí`, `ITAGUI` | `Itagüí` |
| `La Estrella`, `LA ESTRELLA` | `La Estrella` |

**Reglas aplicadas:**
- ✅ Usa diccionario de normalización con 40+ variantes
- ✅ Consolida variaciones de mayúsculas/minúsculas
- ✅ Preserva acentos correctos (Belén, Itagüí)
- ✅ Si no está en el diccionario, aplica Title Case
- ✅ Valores nulos → "Desconocida"

**Resultado:**
- Reduce de ~15 ubicaciones únicas a ~10 (consolidación)

#### 7. Normalización de Tipos de Inmueble

**Función:** `normalizar_tipo_inmueble()`

**Problemas detectados en el CSV:**

| Variantes Encontradas | Normalizado a |
|-----------------------|---------------|
| `Casa`, `CASA`, `casa` | `Casa` |
| `Apartamento`, `APARTAMENTO` | `Apartamento` |
| `Apartestudio`, `APARTESTUDIO` | `Apartestudio` |
| `Finca`, `FINCA`, `finca` | `Finca` |
| `?`, ``, `None`, `nan` | `Desconocido` |

**Reglas aplicadas:**
- ✅ Normaliza capitalización
- ✅ Convierte valores desconocidos (`?`, vacío, None) → "Desconocido"
- ✅ Soporta: Casa, Apartamento, Apartestudio, Finca, Local, Bodega, Lote
- ✅ Valores nulos → "Desconocido"

**Resultado:**
- Reduce tipos inconsistentes a categorías estándar

#### 8. Normalización de Fechas

**Función:** `normalizar_fecha()`

**Problemas detectados en el CSV:**

| Formato Original | Normalizado a |
|------------------|---------------|
| `"Oct 15, 2023"` | `2023-10-15` |
| `15/10/2023` | `2023-10-15` |
| `2023.10.15` | `2023-10-15` |
| `2023-10-15` | `2023-10-15` |

**Reglas aplicadas:**
- ✅ Soporta 4+ formatos diferentes de fecha
- ✅ Usa `pd.to_datetime()` con manejo de errores
- ✅ Convierte todo a formato estándar: `YYYY-MM-DD`
- ❌ Rechaza fechas inválidas (devuelve None)

#### 9. Cálculo de Precio por m²

**Función:** `calcular_precio_m2()`

**Cálculo:**
```python
precio_m2 = precio_venta / metraje_m2
```

**Reglas aplicadas:**
- ✅ Calcula solo si precio y metraje son válidos
- ✅ Evita división por cero
- ✅ Crea nueva columna `precio_m2`

#### 10. Filtrado Final de Registros Inválidos

**Condiciones para ACEPTAR un registro:**
```python
(precio_venta IS NOT NULL) AND
(precio_venta > 0) AND
(metraje_m2 IS NOT NULL) AND
(metraje_m2 > 0) AND
(estrato_socioeconomico IS NOT NULL) AND
(estrato_socioeconomico BETWEEN 1 AND 6) AND
(fecha_publicacion IS NOT NULL)
```

**Registros RECHAZADOS:**
- ❌ Sin precio o precio ≤ 0
- ❌ Sin metraje o metraje ≤ 0
- ❌ Sin estrato o estrato fuera de 1-6
- ❌ Sin fecha válida

---

## 📊 Reportes de Calidad

### Reporte de Extracción

Muestra:
- Total de registros y columnas
- Uso de memoria
- Duplicados detectados
- Valores nulos por columna
- Valores únicos
- Rangos de precios y metrajes

### Reporte de Transformación

Muestra:
- **Resumen:**
  - Registros iniciales vs finales
  - Pérdida (cantidad y %)
  
- **Precios:**
  - Mínimo, Máximo, Promedio, Mediana
  
- **Metrajes:**
  - Mínimo, Máximo, Promedio
  
- **Precio por m²:**
  - Mínimo, Máximo, Promedio
  
- **Top 5 Ubicaciones:**
  - Cantidad y porcentaje
  
- **Tipos de Inmueble:**
  - Distribución completa
  
- **Estratos:**
  - Distribución por estrato (1-6)

---

## 🎯 Resumen de Reglas Implementadas

### ✅ Reglas de Limpieza (10 totales)

1. **Duplicados:** Elimina registros con ID duplicado
2. **Nombres:** Corrige "None en..." → "Propiedad en..."
3. **Precios:** Elimina $, puntos, comas; valida > 0
4. **Metrajes:** Rechaza ≤ 0 y < 10 m²
5. **Estratos:** Valida rango 1-6
6. **Ubicaciones:** Normaliza 40+ variantes de Medellín
7. **Tipos:** Normaliza categorías de inmuebles
8. **Fechas:** Unifica 4 formatos diferentes
9. **Precio/m²:** Calcula automáticamente
10. **Filtrado:** Elimina registros con datos faltantes críticos

### 📈 Resultados Esperados

Con el archivo de 1,242 registros originales:

| Métrica | Valor Esperado |
|---------|----------------|
| Registros extraídos | ~1,242 |
| Duplicados eliminados | 0-5 |
| Registros con precios inválidos | ~10-20 |
| Registros con metrajes inválidos | ~5-15 |
| Registros con estratos inválidos | ~5-10 |
| Registros con fechas inválidas | 0 |
| **Registros finales válidos** | **~1,200-1,220 (97-98%)** |
| Tasa de rechazo | **2-3%** |

### 🔄 Consolidación de Datos

| Campo | Antes | Después | Consolidación |
|-------|-------|---------|---------------|
| Ubicaciones únicas | ~15 | ~10 | 33% reducción |
| Tipos de inmueble | ~8 | ~6 | 25% reducción |
| Formatos de fecha | 4 | 1 | 100% unificado |

---

## 🧪 Cómo Probar

### Opción 1: Script de Prueba

```bash
python probar_etl.py
```

Este script ejecuta el pipeline completo y muestra todos los reportes de calidad.

### Opción 2: Uso Manual

```python
from etl.extraccion import extract
from etl.transformacion import transform

# Extraer
df_raw = extract('data/propiedades_medellin_raw.csv')
print(f"Extraídos: {len(df_raw)} registros")

# Transformar
df_clean = transform(df_raw)
print(f"Transformados: {len(df_clean)} registros")
```

---

## 📝 Notas Importantes

### Configuración de Logging

Para ver todos los reportes detallados, configura logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Valores Rechazados

Los valores rechazados durante la limpieza se registran en los logs con nivel `WARNING` o `DEBUG`.

### Personalización

Puedes modificar los diccionarios de normalización en `transformacion.py`:
- `UBICACIONES_MEDELLIN`: Agregar más variantes de ubicaciones
- `TIPOS_INMUEBLE`: Agregar más tipos de propiedades

### Performance

- Extracción: ~0.5 segundos (1,242 registros)
- Transformación: ~2 segundos (1,242 registros)
- **Total:** ~2.5 segundos

---

**Última actualización:** Marzo 2026  
**Versión:** 2.0 (Mejorado con análisis del CSV real)
