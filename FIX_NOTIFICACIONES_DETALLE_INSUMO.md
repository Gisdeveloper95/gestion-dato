# FIX: Notificaciones de Detalle de Insumo no visibles en el frontend

## Contexto del problema

Los usuarios autorizados crean registros de "Detalle de Insumo" desde el panel administrativo (`src/pages/gestion/detalles/DetalleForm.vue`). El trigger de PostgreSQL `trg_nuevo_detalle` genera correctamente las notificaciones en la tabla `notificaciones`, pero estas **nunca aparecen visibles** en la pagina de Notificaciones (`src/pages/Notificaciones.vue`).

Esto impide generar el reporte de seguimiento de los usuarios que suben informacion.

## Diagnostico (3 problemas encontrados)

### Problema 1: Las notificaciones de detalle son el 0.1% del total

La tabla `notificaciones` tiene **122,959 registros**:

| tipo_entidad | accion | cantidad | porcentaje |
|---|---|---:|---:|
| archivo | crear | 56,495 | 45.95% |
| archivo_insumo | actualizar | 50,463 | 41.04% |
| archivo_insumo | crear | 15,203 | 12.36% |
| sistema | sincronizar_insumos | 365 | 0.30% |
| clasificacion_insumo | crear | 292 | 0.24% |
| **detalle** | **INSERT** | **96** | **0.08%** |
| **detalle** | **UPDATE** | **20** | **0.02%** |
| municipio | UPDATE | 19 | 0.02% |
| insumo | crear | 6 | 0.00% |

La funcion `cargarDatos()` en `Notificaciones.vue` (linea ~1789) pide `page_size: 10000` ordenado por `-fecha_cambio`. Las 116 notificaciones de detalle quedan completamente sepultadas entre las 122K+ de archivos.

### Problema 2: No existe filtro por "Tipo Entidad" en el frontend

**Archivo:** `frontend/src/pages/Notificaciones.vue`

Los filtros disponibles en el template (lineas 45-160) son:
- Tipo sistema (preoperacion/postoperacion)
- Departamento
- Municipio
- Accion
- Rango de fechas
- Usuario

**NO hay un dropdown para `tipo_entidad`** (detalle, archivo, archivo_insumo, etc.).

El backend SI lo soporta en `backend/preoperacion/views.py` linea 1208:
```python
filterset_fields = ['tipo_entidad', 'accion', 'leido']
```

Pero el frontend nunca envia el parametro `tipo_entidad` en la peticion.

### Problema 3: Incompatibilidad en nombres de acciones

El trigger de PostgreSQL `fn_notificar_nuevo_detalle()` usa acciones en INGLES:
- `INSERT` para creacion
- `UPDATE` para actualizacion

Pero el resto del sistema (archivos, insumos, clasificaciones) usa acciones en ESPANOL:
- `crear`
- `actualizar`
- `eliminar`

En el dropdown de acciones (`Notificaciones.vue` linea 723-734):
```javascript
const acciones = [
  { value: 'crear', label: 'Crear' },
  { value: 'actualizar', label: 'Actualizar' },
  { value: 'eliminar', label: 'Eliminar' },
  { value: 'aprobar', label: 'Aprobar' },
  { value: 'rechazar', label: 'Rechazar' },
  { value: 'disponer', label: 'Disponer' },
  { value: 'evaluar', label: 'Evaluar' },
  { value: 'INSERT', label: 'Crear (Detalles Insumo)' },
  { value: 'UPDATE', label: 'Actualizar' }
];
```

Si un usuario filtra por "Crear" (`crear`), **no le salen los detalles** porque esos usan `INSERT`.

---

## Solucion a implementar

### Cambio 1: Agregar filtro "Tipo Entidad" en el frontend

**Archivo:** `frontend/src/pages/Notificaciones.vue`

#### 1a. Agregar la variable de tipos de entidad (despues de `const acciones` ~linea 734):

```javascript
const tiposEntidad = [
  { value: 'detalle', label: 'Detalle de Insumo' },
  { value: 'archivo', label: 'Archivo' },
  { value: 'archivo_insumo', label: 'Archivo Insumo' },
  { value: 'clasificacion_insumo', label: 'Clasificacion Insumo' },
  { value: 'insumo', label: 'Insumo' },
  { value: 'municipio', label: 'Municipio' },
  { value: 'sistema', label: 'Sistema' },
];
```

#### 1b. Agregar `tipoEntidad` al objeto `filtros` (buscar `const filtros = ref({` ~linea 658):

Agregar esta propiedad al objeto:
```javascript
tipoEntidad: '',
```

#### 1c. Agregar el dropdown en el template (despues del filtro de "Accion" ~linea 91):

```html
<div class="filter-group">
  <label for="tipoEntidad">Tipo Entidad</label>
  <select id="tipoEntidad" v-model="filtros.tipoEntidad" @change="aplicarFiltros">
    <option value="">Todos los tipos de entidad</option>
    <option v-for="(te, index) in tiposEntidad" :key="te.value || index" :value="te.value">
      {{ te.label }}
    </option>
  </select>
</div>
```

#### 1d. Enviar el parametro al backend en `cargarDatos()` (~linea 1789):

Despues de los filtros existentes (antes de `const tipos = [];` ~linea 1827), agregar:

```javascript
if (filtros.value.tipoEntidad) {
  params.tipo_entidad = filtros.value.tipoEntidad;
}
```

#### 1e. Limpiar el filtro en `limpiarFiltros()` (~linea 962):

Agregar al objeto de reset:
```javascript
tipoEntidad: '',
```

#### 1f. Exponer en el return (buscar la seccion de return ~linea 2250):

Agregar `tiposEntidad` al objeto de return junto con las demas variables expuestas.

### Cambio 2 (OPCIONAL pero recomendado): Normalizar acciones en el trigger de PostgreSQL

**Esto es en la base de datos de produccion**, ejecutar en PostgreSQL:

```sql
-- Opcion A: Modificar el trigger para usar acciones en espanol (RECOMENDADO)
CREATE OR REPLACE FUNCTION fn_notificar_nuevo_detalle()
RETURNS TRIGGER AS $$
DECLARE
    clasificacion_info RECORD;
    usuario_nombre VARCHAR;
BEGIN
    SELECT c.nombre, i.cod_categoria, i.cod_municipio, m.nom_municipio
    INTO clasificacion_info
    FROM clasificacion_insumo c
    JOIN insumos i ON c.cod_insumo = i.cod_insumo
    JOIN municipios m ON i.cod_municipio = m.cod_municipio
    WHERE c.cod_clasificacion = NEW.cod_clasificacion;

    SELECT nombre INTO usuario_nombre
    FROM usuarios WHERE cod_usuario = NEW.cod_usuario;

    INSERT INTO notificaciones (
        tipo_entidad, id_entidad, accion, descripcion, datos_contexto
    )
    VALUES (
        'detalle',
        NEW.cod_detalle,
        'crear',  -- CAMBIADO: de 'INSERT' a 'crear'
        'Nuevo detalle de insumo creado para la clasificacion "' || clasificacion_info.nombre || '"',
        jsonb_build_object(
            'detalle_id', NEW.cod_detalle,
            'estado', NEW.estado,
            'escala', NEW.escala,
            'zona', NEW.zona,
            'categoria_id', clasificacion_info.cod_categoria,
            'entidad_id', NEW.cod_entidad,
            'usuario_id', NEW.cod_usuario,
            'usuario_nombre', usuario_nombre,
            'clasificacion_id', NEW.cod_clasificacion,
            'clasificacion_nombre', clasificacion_info.nombre,
            'municipio_id', clasificacion_info.cod_municipio,
            'municipio_nombre', clasificacion_info.nom_municipio
        )
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

Y tambien actualizar `fn_notificar_detalle()` (el trigger de UPDATE):

```sql
-- Verificar y actualizar el trigger de UPDATE de forma similar
-- Buscar la funcion con: SELECT prosrc FROM pg_proc WHERE proname = 'fn_notificar_detalle';
-- Y cambiar 'UPDATE' por 'actualizar' en el INSERT a notificaciones
```

**Opcion B (alternativa sin tocar triggers):** Actualizar las notificaciones existentes en la BD:

```sql
UPDATE notificaciones SET accion = 'crear' WHERE tipo_entidad = 'detalle' AND accion = 'INSERT';
UPDATE notificaciones SET accion = 'actualizar' WHERE tipo_entidad = 'detalle' AND accion = 'UPDATE';
```

### Cambio 3 (OPCIONAL): Simplificar el dropdown de acciones

Si se aplica el Cambio 2, se puede eliminar la duplicacion de acciones en el frontend.

**Archivo:** `frontend/src/pages/Notificaciones.vue` (~linea 723)

Quitar las entradas duplicadas:
```javascript
const acciones = [
  { value: 'crear', label: 'Crear' },
  { value: 'actualizar', label: 'Actualizar' },
  { value: 'eliminar', label: 'Eliminar' },
  { value: 'aprobar', label: 'Aprobar' },
  { value: 'rechazar', label: 'Rechazar' },
  { value: 'disponer', label: 'Disponer' },
  { value: 'evaluar', label: 'Evaluar' },
];
```

---

## Archivos a modificar (resumen)

| Archivo | Cambio |
|---|---|
| `frontend/src/pages/Notificaciones.vue` | Agregar filtro tipo_entidad (template + script + cargarDatos) |
| BD PostgreSQL: `fn_notificar_nuevo_detalle()` | Cambiar 'INSERT' -> 'crear' (opcional) |
| BD PostgreSQL: `fn_notificar_detalle()` | Cambiar 'UPDATE' -> 'actualizar' (opcional) |
| BD PostgreSQL: tabla `notificaciones` | UPDATE masivo para normalizar acciones existentes (opcional) |

## Prioridad de implementacion

1. **CRITICO:** Cambio 1 (filtro tipo_entidad) - Esto desbloquea inmediatamente a los usuarios
2. **IMPORTANTE:** Cambio 2 Opcion B (UPDATE masivo) - Normaliza datos existentes
3. **DESEABLE:** Cambio 2 Opcion A (triggers) - Previene inconsistencias futuras
4. **MENOR:** Cambio 3 (limpiar dropdown) - Solo cosmetico

## Datos de referencia

Usuarios con registros en detalle_insumo creados desde el frontend:

| Usuario | Correo | Total registros |
|---|---|---:|
| ELIZABETH ROSAS CRISTANCHO | elizabeth.rosas@igac.gov.co | 48 |
| Carolina Del Socorro Guerrero Ordoñez | carolina.guerrero@igac.gov.co | 25 |
| (sin nombre) | felipe.vargas@igac.gov.co | 7 |
| Sonia Elizabeth Eraso Hanrryr | elizabeth.eraso@igac.gov.co | 2 |
| AIDA MARCELA BELALCAZAR LARA | aida.belalcazar@igac.gov.co | 2 |
| SERGIO DANIEL LOPEZ PINZON | sergio.lopez@igac.gov.co | 1 |
| ANGIE SHIRLEY MENDOZA CAÑON | angie.mendoza@igac.gov.co | 1 |

Los 4,772 registros de ANDRES FELIPE OSORIO BASTIDAS fueron carga masiva SQL, no desde frontend. No tienen ni notificacion ni auditoria.
