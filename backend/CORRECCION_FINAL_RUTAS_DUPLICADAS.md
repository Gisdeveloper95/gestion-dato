# Corrección Final - Rutas Duplicadas

## Problema Detectado
Después de la segunda corrección, se encontró:
1. **Rutas duplicadas** unidas con ` | ` en la columna "RUTA DE ACCESO"
2. **Rutas con formato mixto** (`//repositorio/...` con `/` en lugar de `\`)

Ejemplo del problema:
```
//repositorio/DirGesCat/2510SP/H_Informacion_Consulta/Sub_Proy/01_actualiz_catas\ | \\repositorio\DirGesCat\2510SP\H_Informacion_Consulta\Sub_Proy\01_actualiz_catas\
```

---

## Causa Raíz

### Problema 1: Concatenación de Rutas
**Ubicación:** postoperacion/views.py línea 2445

La columna "RUTA DE ACCESO" estaba usando `.join()` para mostrar hasta 2 rutas del mismo directorio:
```python
rutas_texto = " | ".join(sorted(rutas_acceso)[:2]) if rutas_acceso else "Sin rutas"
```

Esto causaba que si había múltiples archivos en el mismo directorio (cada uno con su `ruta_directorio`), se mostraran varias rutas juntas.

### Problema 2: Rutas con Formato Mixto
**Ubicación:** backend/path_utils.py línea 44

La función `linux_to_windows_path()` solo manejaba rutas que empezaban con `/mnt/repositorio`, pero NO convertía rutas que ya tenían formato parcial de Windows con barras normales como:
- `//repositorio/DirGesCat/...` (con `/` en lugar de `\`)

---

## Soluciones Aplicadas

### 1. **Eliminar Concatenación de Rutas**

**Archivo:** postoperacion/views.py
**Línea:** 2445

**Antes:**
```python
# Columna G: Rutas de Acceso
rutas_texto = " | ".join(sorted(rutas_acceso)[:2]) if rutas_acceso else "Sin rutas"
ws.cell(row=row, column=7, value=rutas_texto).alignment = left_align
```

**Después:**
```python
# Columna G: Rutas de Acceso (solo mostrar la primera ruta, todas deberían ser iguales)
rutas_texto = sorted(rutas_acceso)[0] if rutas_acceso else "Sin rutas"
ws.cell(row=row, column=7, value=rutas_texto).alignment = left_align
```

**Impacto:** Ahora solo muestra UNA ruta por directorio en lugar de concatenar múltiples.

---

### 2. **Mejorar Función de Conversión de Rutas**

**Archivo:** backend/path_utils.py
**Líneas:** 34-66

**Nueva lógica con 4 casos:**

```python
def linux_to_windows_path(linux_path):
    # Si es None o vacío, retornar tal cual
    if not linux_path:
        return linux_path

    if not isinstance(linux_path, str):
        return linux_path

    ruta_normalizada = linux_path.strip()

    # Caso 1: Ruta Linux estándar: /mnt/repositorio/...
    if ruta_normalizada.startswith('/mnt/repositorio'):
        windows_path = ruta_normalizada.replace('/mnt/repositorio', r'\\repositorio\DirGesCat')
        windows_path = windows_path.replace('/', '\\')
        return windows_path

    # Caso 2: Ruta con formato Windows parcial con /: //repositorio/DirGesCat/...
    if '//repositorio' in ruta_normalizada.lower() or '/repositorio/dirgescat' in ruta_normalizada.lower():
        windows_path = ruta_normalizada.replace('//', '\\\\', 1)
        windows_path = windows_path.replace('/', '\\')
        return windows_path

    # Caso 3: Ruta ya en formato Windows correcto: \\repositorio\DirGesCat\...
    if ruta_normalizada.startswith('\\\\repositorio') or ruta_normalizada.startswith(r'\\repositorio'):
        return ruta_normalizada.replace('/', '\\')

    # Caso 4: Mensajes especiales o rutas no reconocidas
    return linux_path
```

**Mejoras:**
- ✅ Maneja `/mnt/repositorio/...` (rutas Linux)
- ✅ Maneja `//repositorio/DirGesCat/...` (formato parcial con `/`)
- ✅ Maneja `\\repositorio\DirGesCat\...` (ya correctas)
- ✅ Preserva mensajes como "Sin ruta", "Sin directorio"

---

## Resultados de Pruebas

```
✅ Test 1: /mnt/repositorio/2510SP/...
   → \\repositorio\DirGesCat\2510SP\...

✅ Test 2: //repositorio/DirGesCat/2510SP/...
   → \\repositorio\DirGesCat\2510SP\...

✅ Test 3: \\repositorio\DirGesCat\2510SP\...
   → \\repositorio\DirGesCat\2510SP\...

✅ Test 4: Sin ruta → Sin ruta
✅ Test 5: None → None
✅ Test 6: '' → ''
```

---

## Resumen de Cambios

| Archivo | Línea | Cambio | Impacto |
|---------|-------|--------|---------|
| postoperacion/views.py | 2445 | Eliminado `.join()` de múltiples rutas | Solo muestra 1 ruta por directorio |
| backend/path_utils.py | 34-66 | Agregados 4 casos de conversión | Maneja todos los formatos de ruta posibles |

---

## Para Aplicar los Cambios

**IMPORTANTE:** Reiniciar el contenedor del backend:

```bash
sudo docker restart igac_backend
```

**Resultado Esperado:**
- ✅ Solo UNA ruta por celda (sin ` | `)
- ✅ Todas las rutas en formato correcto: `\\repositorio\DirGesCat\2510SP\...`
- ✅ Sin rutas mezcladas con `/` y `\`

---

Fecha: 2025-11-11
Tercera corrección completada
