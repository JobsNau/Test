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

