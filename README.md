# Test

# Diagrama Entidad-Relación (DER)
## Base de Datos: Propiedades Medellín

---

## 📋 Modelo Normalizado (3FN)

### Estructura del Modelo

El modelo consta de **3 tablas** en Tercera Forma Normal (3FN):
- 2 **Tablas Maestras** (Dimensiones)
- 1 **Tabla de Hechos** (Propiedades)

---

## 🗃️ Definición de Tablas

### 1️⃣ Tabla Maestra: `dim_ubicaciones`

**Propósito:** Catálogo normalizado de ubicaciones geográficas

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| **id_ubicacion** | INT | PK, AUTO_INCREMENT | Identificador único |
| nombre_ubicacion | VARCHAR(100) | UNIQUE, NOT NULL | Nombre de la ubicación |
| ciudad | VARCHAR(50) | DEFAULT 'Medellín' | Ciudad |
| departamento | VARCHAR(50) | DEFAULT 'Antioquia' | Departamento |


---

### 2️⃣ Tabla Maestra: `dim_tipos_inmueble`

**Propósito:** Catálogo de clasificación de tipos de inmuebles

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| **id_tipo_inmueble** | INT | PK, AUTO_INCREMENT | Identificador único |
| nombre_tipo | VARCHAR(50) | UNIQUE, NOT NULL | Nombre del tipo |

---

### 3️⃣ Tabla de Hechos: `propiedades`

**Propósito:** Almacena la información detallada de cada propiedad

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| **id_propiedad** | INT | PK | Identificador único de la propiedad |
| nombre_anuncio | VARCHAR(200) | NULL | Título del anuncio |
| precio_venta | DECIMAL(15,2) | NULL, CHECK(>0) | Precio en pesos colombianos |
| metraje_m2 | DECIMAL(10,2) | NULL, CHECK(>=0) | Área en metros cuadrados |
| estrato_socioeconomico | TINYINT | NULL, CHECK(1-6) | Estrato socioeconómico |
| **id_ubicacion** | INT | FK, NOT NULL | Referencia a dim_ubicaciones |
| **id_tipo_inmueble** | INT | FK, NOT NULL | Referencia a dim_tipos_inmueble |
| fecha_publicacion | DATE | NULL | Fecha de publicación |

---

## 🔗 Relaciones

### Relación 1: `dim_ubicaciones` → `propiedades`
- **Cardinalidad:** 1:N (Uno a Muchos)
- **Descripción:** Una ubicación puede tener muchas propiedades
- **Llave Foránea:** `propiedades.id_ubicacion` → `dim_ubicaciones.id_ubicacion`
- **Restricciones:** ON DELETE RESTRICT, ON UPDATE CASCADE

### Relación 2: `dim_tipos_inmueble` → `propiedades`
- **Cardinalidad:** 1:N (Uno a Muchos)
- **Descripción:** Un tipo de inmueble puede clasificar muchas propiedades
- **Llave Foránea:** `propiedades.id_tipo_inmueble` → `dim_tipos_inmueble.id_tipo_inmueble`
- **Restricciones:** ON DELETE RESTRICT, ON UPDATE CASCADE

---

## 📊 Diagrama Entidad-Relación

```
┌─────────────────────────────┐
│   dim_ubicaciones           │
│   (Tabla Maestra)           │
├─────────────────────────────┤
│ PK  id_ubicacion            │
│     nombre_ubicacion (UK)   │
│     ciudad                  │
│     departamento            │
└──────────────┬──────────────┘
               │
               │ 1
               │
               │
               │ N
               │
┌──────────────┴──────────────────────────────┐
│           propiedades                       │
│           (Tabla de Hechos)                 │
├─────────────────────────────────────────────┤
│ PK  id_propiedad                            │
│     nombre_anuncio                          │
│     precio_venta                            │
│     metraje_m2                              │
│     estrato_socioeconomico                  │
│ FK  id_ubicacion            ────────────────┤
│ FK  id_tipo_inmueble        ──────────┐     │
│     fecha_publicacion                 │     │
└───────────────────────────────────────┼─────┘
                                        │
                                        │ N
                                        │
                                        │
                                        │ 1
                                        │
               ┌────────────────────────┴─────┐
               │   dim_tipos_inmueble         │
               │   (Tabla Maestra)            │
               ├──────────────────────────────┤
               │ PK  id_tipo_inmueble         │
               │     nombre_tipo (UK)         │
               │     categoria                │
               └──────────────────────────────┘
```

---

## 🔑 Llaves e Índices

### Llaves Primarias (PK)
- `dim_ubicaciones.id_ubicacion`
- `dim_tipos_inmueble.id_tipo_inmueble`
- `propiedades.id_propiedad`

### Llaves Foráneas (FK)
- `propiedades.id_ubicacion` → `dim_ubicaciones.id_ubicacion`
- `propiedades.id_tipo_inmueble` → `dim_tipos_inmueble.id_tipo_inmueble`

### Llaves Únicas (UK)
- `dim_ubicaciones.nombre_ubicacion`
- `dim_tipos_inmueble.nombre_tipo`

---

## 🎯 Integridad Referencial

### Restricciones de Integridad

1. **Integridad de Entidad**
   - Cada tabla tiene una llave primaria única y no nula
   - No se permiten duplicados en llaves primarias

2. **Integridad Referencial**
   - Las llaves foráneas garantizan que cada propiedad esté asociada a una ubicación válida
   - Las llaves foráneas garantizan que cada propiedad esté asociada a un tipo válido
   - ON DELETE RESTRICT: No se puede eliminar una ubicación o tipo si tiene propiedades asociadas
   - ON UPDATE CASCADE: Los cambios en IDs se propagan automáticamente

3. **Integridad de Dominio**
   - `precio_venta` debe ser mayor que 0
   - `metraje_m2` debe ser mayor o igual a 0
   - `estrato_socioeconomico` debe estar entre 1 y 6
   - Campos obligatorios: id_propiedad, id_ubicacion, id_tipo_inmueble

---


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
