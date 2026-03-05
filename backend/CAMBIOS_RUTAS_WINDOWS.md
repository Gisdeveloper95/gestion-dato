# Conversión de Rutas Linux a Windows en Reportes Excel

## Resumen
Todos los reportes Excel ahora convierten automáticamente las rutas de formato Linux (almacenadas en la base de datos) a formato Windows UNC para que los usuarios de Windows puedan acceder directamente a los archivos desde Excel.

**Conversión aplicada:**
- **Desde:** `/mnt/repositorio/2510SP/...`
- **Hacia:** `\\repositorio\DirGesCat\2510SP\...`

---

## Archivos Modificados

### 1. **backend/path_utils.py** (NUEVO)
Archivo utilitario con funciones de conversión de rutas:
- `linux_to_windows_path()`: Convierte rutas Linux → Windows UNC
- `windows_to_linux_path()`: Convierte rutas Windows → Linux (inverso)
- `convert_paths_for_excel_export()`: Convierte múltiples campos en diccionarios

### 2. **app/views.py**
**Import agregado (línea 40):**
```python
from backend.path_utils import linux_to_windows_path
```

**Ubicaciones corregidas:**

| Línea | Función | Descripción | Campo convertido |
|-------|---------|-------------|------------------|
| 1984 | `generar_inventario_archivos_operacion` | Ruta completa archivo | `path_file` |
| 1992 | `generar_inventario_archivos_operacion` | Ruta directorio | `path_directorio` |
| 2541 | `generar_inventario_archivos_transversal` | Ruta completa archivo | `path_file` |
| 2549 | `generar_inventario_archivos_transversal` | Ruta directorio | `ruta_completa` |
| 2798 | `excel_definitivo` | Ruta path_file (PRE) | `path_file` (sliced 50 chars) |
| 2825 | `excel_definitivo` | Ruta path_file (OP) | `path_file` (sliced 50 chars) |

**Total:** 6 ubicaciones corregidas en reportes de Operación y Transversal

### 3. **preoperacion/views.py**
**Import agregado (línea 41):**
```python
from backend.path_utils import linux_to_windows_path
```

**Función modificada:**
- **`extraer_directorio_desde_ruta()` (línea 2720-2778)**
  - Ahora aplica conversión automática Linux → Windows en el resultado principal (línea 2747)
  - Corregido bloque FALLBACK para también aplicar conversión (líneas 2772, 2775, 2778)

**Impacto:** Esta función es usada en múltiples reportes de pre-operación:
- `generar_pestana_detalles_categorias()` - Líneas 2667, 2676 (valor y hyperlink)
- `generar_pestana_matriz_primarios()` - Líneas 3040, 3046 (valor y hyperlink)
- Reportes con patrones de archivos - Línea 3258, 3270 (valor y hyperlink)

**Total:** Todas las rutas en reportes de pre-operación ahora se convierten automáticamente

### 4. **postoperacion/views.py**
**Import agregado (línea 49):**
```python
from backend.path_utils import linux_to_windows_path
```

**Ubicaciones corregidas:**

| Línea | Función | Descripción | Campo convertido |
|-------|---------|-------------|------------------|
| 2636 | `generar_pestana_resumen_general` | Ruta completa | `ruta_completa` |
| 3011 | `generar_pestana_detalles_componentes` | Ruta directorio padre | `ruta_directorio` |
| 3017 | `generar_pestana_detalles_componentes` | Ruta archivo completa | `ruta_completa` |

**Total:** 3 ubicaciones corregidas en reportes de post-operación

---

## Archivos de Prueba Creados

### test_path_simple.py
Script de prueba unitaria que verifica la conversión correcta:
- ✅ Rutas Linux → Windows UNC
- ✅ Valores especiales (`None`, "Sin ruta") se mantienen
- ✅ Todas las pruebas pasaron exitosamente

---

## Resumen Total de Cambios

| Archivo | Líneas modificadas | Tipos de cambio |
|---------|-------------------|-----------------|
| backend/path_utils.py | 137 (nuevo) | Funciones utilitarias |
| app/views.py | 6 ubicaciones | Conversión directa en celdas |
| preoperacion/views.py | 1 función + fallback | Conversión automática vía función |
| postoperacion/views.py | 3 ubicaciones | Conversión directa en celdas |

**Total: 10+ ubicaciones** donde se generan rutas en Excel ahora aplican conversión Windows

---

## Cómo Funciona

### Antes (Rutas en formato Linux - NO funcionan para usuarios Windows)
```
/mnt/repositorio/2510SP/H_Informacion_Consulta/Sub_Proy/documento.pdf
```

### Después (Rutas en formato Windows UNC - Funcionan para usuarios Windows)
```
\\repositorio\DirGesCat\2510SP\H_Informacion_Consulta\Sub_Proy\documento.pdf
```

Los usuarios de Windows ahora pueden:
- **Hacer clic** en los hipervínculos de Excel para abrir directorios
- **Copiar/pegar** rutas directamente en el Explorador de Windows
- **Acceder** a los archivos desde sus sistemas Windows

---

## Para Aplicar los Cambios

**IMPORTANTE:** Debes reiniciar el contenedor del backend para que los cambios surtan efecto:

```bash
sudo docker restart igac_backend
```

O rebuild completo:
```bash
cd /home/sonia.eraso/server
sudo docker-compose down
sudo docker-compose up -d --build backend
```

---

## Notas Técnicas

1. **La base de datos NO cambia:** Las rutas siguen almacenadas en formato Linux
2. **Conversión en tiempo real:** Se hace solo al generar el Excel
3. **Sin impacto en el servidor:** El backend sigue usando rutas Linux internamente
4. **Retrocompatibilidad:** Si una ruta ya está en formato Windows, no se altera

---

Fecha de implementación: 2025-11-11
Desarrollado por: Claude Code Assistant
