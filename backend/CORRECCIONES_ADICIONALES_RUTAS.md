# Correcciones Adicionales - Conversión de Rutas

## Problema Detectado
Después del primer intento, se encontraron dos problemas:
1. **Rutas sin convertir** en registros "Sin datos" de postoperación
2. **Rutas duplicadas** (Windows + Linux en la misma celda) por conversión doble

---

## Solución Aplicada

### 1. **postoperacion/views.py - Función `extraer_ruta_hasta_directorio_padre()`**

**Ubicación:** Líneas 1466-1504

**Problema:** Esta función solo estaba convirtiendo `/` a `\` pero NO aplicaba la conversión completa de Linux a Windows (`/mnt/repositorio` → `\\repositorio\DirGesCat`).

**Solución:** Modificada para aplicar `linux_to_windows_path()` antes de retornar:

```python
def extraer_ruta_hasta_directorio_padre(ruta_completa):
    """
    Extrae ruta hasta el directorio padre (sin archivo)
    CONVIERTE de formato Linux a formato Windows para usuarios
    """
    if not ruta_completa:
        return "SIN_RUTA"

    try:
        ruta_str = str(ruta_completa)

        # Si termina en archivo (contiene extensión), remover el archivo
        if '/' in ruta_str or '\\' in ruta_str:
            # Normalizar a / para procesar
            ruta_normalizada = ruta_str.replace('\\', '/')
            partes = ruta_normalizada.split('/')

            if partes and partes[-1] and '.' in partes[-1]:
                # Última parte es archivo, removerla
                partes = partes[:-1]
                resultado = '/'.join(partes)
            else:
                # Ya es un directorio
                resultado = ruta_normalizada.rstrip('/')
        else:
            resultado = ruta_str

        # 🔄 Convertir de Linux a Windows para que los usuarios puedan acceder
        resultado = linux_to_windows_path(resultado)

        # Agregar \ al final si no la tiene (formato directorio Windows)
        if resultado and not resultado.endswith('\\'):
            resultado += '\\'

        return resultado

    except Exception as e:
        print(f"⚠️ Error extrayendo ruta directorio: {e}")
        return "ERROR_RUTA"
```

**Impacto:**
- Esta función es usada en líneas 2721 y 2731 para crear `dato['ruta_directorio']`
- Ahora todos los registros (incluyendo "Sin datos") tendrán rutas Windows correctas

---

### 2. **postoperacion/views.py - Eliminar Conversión Duplicada**

**Ubicación:** Línea 3026 (Inventario de Archivos)

**Problema:** Se estaba aplicando `linux_to_windows_path()` sobre `dato['ruta_directorio']` que YA había sido convertido por `extraer_ruta_hasta_directorio_padre()`. Esto causaba rutas duplicadas o malformadas.

**Antes:**
```python
# Columna K: RUTA DIRECTORIO PADRE (SIN archivo final) - convertir a Windows
ruta_directorio = linux_to_windows_path(dato['ruta_directorio'])
ws.cell(row=row, column=11, value=ruta_directorio).alignment = left_align
```

**Después:**
```python
# Columna K: RUTA DIRECTORIO PADRE (SIN archivo final) - ya convertido por extraer_ruta_hasta_directorio_padre()
ruta_directorio = dato['ruta_directorio']
ws.cell(row=row, column=11, value=ruta_directorio).alignment = left_align
```

**Impacto:** Eliminada conversión duplicada que causaba rutas mal formadas

---

### 3. **preoperacion/views.py - Bloque FALLBACK de `extraer_directorio_desde_ruta()`**

**Ubicación:** Líneas 2750-2778

**Problema:** El bloque FALLBACK (en caso de error) NO estaba aplicando conversión a Windows.

**Solución:** Agregado `linux_to_windows_path()` en tres puntos del fallback:
- Línea 2772: Cuando se extrae directorio padre de archivo
- Línea 2775: Cuando la ruta ya es directorio
- Línea 2778: Como último recurso en caso de error

---

## Resumen de Cambios

| Archivo | Función | Cambio | Impacto |
|---------|---------|--------|---------|
| postoperacion/views.py | `extraer_ruta_hasta_directorio_padre()` | Agregada conversión completa Linux → Windows | Corrige registros "Sin datos" |
| postoperacion/views.py | Inventario de Archivos (línea 3026) | Eliminada conversión duplicada | Elimina rutas duplicadas/malformadas |
| preoperacion/views.py | `extraer_directorio_desde_ruta()` FALLBACK | Agregada conversión en 3 puntos del fallback | Garantiza conversión incluso en errores |

---

## Para Aplicar los Cambios

**IMPORTANTE:** Debes reiniciar el contenedor del backend:

```bash
sudo docker restart igac_backend
```

---

## Verificación Final

Ejecutado comando de búsqueda exhaustiva:
```bash
grep -n "\.path_file\|\.path_directorio\|\.ruta_completa\|\['ruta" *.py | \
  grep -E "(ws\.cell|cell.*value|cell.*hyperlink)" | \
  grep -v "linux_to_windows_path\|extraer_directorio_desde_ruta\|extraer_ruta_hasta_directorio_padre"
```

**Resultado:** ✅ No se encontraron más rutas sin convertir

---

Fecha: 2025-11-11
Segunda ronda de correcciones completada
