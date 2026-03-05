/**
 * Utilidades para conversión de rutas entre formatos Linux y Windows.
 *
 * Este módulo proporciona funciones para convertir rutas entre el formato Linux
 * usado en el servidor y el formato Windows UNC necesario para que los usuarios
 * puedan acceder a los archivos desde sus equipos Windows.
 *
 * Equivalente al path_utils.py del backend.
 */

/**
 * Convierte una ruta de Linux a formato Windows UNC.
 *
 * Conversión:
 *   FROM: /mnt/repositorio/2510SP/...
 *   TO:   \\repositorio\DirGesCat\2510SP\...
 *
 * @param linuxPath - Ruta en formato Linux (ej: /mnt/repositorio/2510SP/...)
 * @returns Ruta en formato Windows UNC o el valor original si no se puede convertir
 *
 * @example
 * linuxToWindowsPath('/mnt/repositorio/2510SP/H_Informacion_Consulta')
 * // => '\\\\repositorio\\DirGesCat\\2510SP\\H_Informacion_Consulta'
 *
 * linuxToWindowsPath('Sin ruta')
 * // => 'Sin ruta'
 *
 * linuxToWindowsPath(null)
 * // => null
 */
export function linuxToWindowsPath(linuxPath: string | null | undefined): string | null | undefined {
  // Si es null, undefined o vacío, retornar tal cual
  if (!linuxPath) {
    return linuxPath
  }

  // Si no es una cadena válida, retornar tal cual
  if (typeof linuxPath !== 'string') {
    return linuxPath
  }

  // Normalizar la ruta para procesar
  const rutaNormalizada = linuxPath.trim()

  // Caso 1: Ruta Linux estándar: /mnt/repositorio/...
  if (rutaNormalizada.startsWith('/mnt/repositorio')) {
    let windowsPath = rutaNormalizada.replace('/mnt/repositorio', '\\\\repositorio\\DirGesCat')
    windowsPath = windowsPath.replace(/\//g, '\\')
    return windowsPath
  }

  // Caso 2: Ruta que ya tiene formato Windows parcial con / : //repositorio/DirGesCat/...
  if (rutaNormalizada.toLowerCase().includes('//repositorio') ||
      rutaNormalizada.toLowerCase().includes('/repositorio/dirgescat')) {
    // Normalizar dobles barras al inicio
    let windowsPath = rutaNormalizada.replace('//', '\\\\')
    // Convertir el resto de / a \
    windowsPath = windowsPath.replace(/\//g, '\\')
    return windowsPath
  }

  // Caso 3: Ruta que ya está en formato Windows correcto: \\repositorio\DirGesCat\...
  if (rutaNormalizada.startsWith('\\\\repositorio') || rutaNormalizada.startsWith('\\repositorio')) {
    // Ya está correcta, solo asegurar barras invertidas
    return rutaNormalizada.replace(/\//g, '\\')
  }

  // Caso 4: Mensajes especiales o rutas no reconocidas
  // (podría ser "Sin ruta", "Sin directorio", etc.)
  return linuxPath
}

/**
 * Convierte una ruta de Windows UNC a formato Linux.
 *
 * Conversión:
 *   FROM: \\repositorio\DirGesCat\2510SP\...
 *   TO:   /mnt/repositorio/2510SP/...
 *
 * @param windowsPath - Ruta en formato Windows UNC
 * @returns Ruta en formato Linux o el valor original si no se puede convertir
 *
 * @example
 * windowsToLinuxPath('\\\\repositorio\\DirGesCat\\2510SP\\H_Informacion_Consulta')
 * // => '/mnt/repositorio/2510SP/H_Informacion_Consulta'
 */
export function windowsToLinuxPath(windowsPath: string | null | undefined): string | null | undefined {
  // Si es null, undefined o vacío, retornar tal cual
  if (!windowsPath) {
    return windowsPath
  }

  // Si no es una cadena válida, retornar tal cual
  if (typeof windowsPath !== 'string') {
    return windowsPath
  }

  // Normalizar la ruta (puede venir con \ o con \\)
  let normalizedPath = windowsPath.replace(/\\/g, '/')

  // Si no contiene el patrón de repositorio, retornar tal cual
  if (!normalizedPath.toLowerCase().includes('repositorio')) {
    return windowsPath
  }

  // Convertir de Windows UNC a Linux
  // //repositorio/DirGesCat/2510SP/... -> /mnt/repositorio/2510SP/...
  let linuxPath = normalizedPath.replace('//repositorio/DirGesCat/', '/mnt/repositorio/')
  linuxPath = linuxPath.replace('\\\\repositorio\\DirGesCat\\', '/mnt/repositorio/')

  return linuxPath
}

/**
 * Detecta si una ruta es de tipo Linux (comienza con /)
 *
 * @param path - Ruta a verificar
 * @returns true si es una ruta Linux
 */
export function isLinuxPath(path: string | null | undefined): boolean {
  if (!path || typeof path !== 'string') {
    return false
  }
  return path.trim().startsWith('/')
}

/**
 * Detecta si una ruta es de tipo Windows (comienza con \\ o letra de unidad)
 *
 * @param path - Ruta a verificar
 * @returns true si es una ruta Windows
 */
export function isWindowsPath(path: string | null | undefined): boolean {
  if (!path || typeof path !== 'string') {
    return false
  }
  const trimmed = path.trim()
  return trimmed.startsWith('\\\\') || /^[a-zA-Z]:/.test(trimmed)
}

/**
 * Detecta si una cadena parece ser una ruta de archivo/directorio
 *
 * @param value - Valor a verificar
 * @returns true si parece ser una ruta
 */
export function isPathLike(value: string | null | undefined): boolean {
  if (!value || typeof value !== 'string') {
    return false
  }
  const trimmed = value.trim()

  // Verificar patrones comunes de rutas
  return (
    trimmed.startsWith('/mnt/') ||
    trimmed.startsWith('\\\\') ||
    trimmed.startsWith('//') ||
    /^[a-zA-Z]:[\\/]/.test(trimmed) ||
    trimmed.toLowerCase().includes('repositorio')
  )
}

/**
 * Campos comunes que contienen rutas en los datos
 */
export const PATH_FIELDS = [
  'path',
  'path_file',
  'path_directorio',
  'ruta',
  'ruta_completa',
  'directorio',
  'ruta_directorio',
  'ruta_archivo',
  'ruta_acceso'
]

/**
 * Convierte todas las rutas en un objeto de datos para mostrar al usuario.
 *
 * Busca campos comunes de rutas y los convierte de Linux a Windows.
 *
 * @param dataDict - Objeto con datos que pueden contener rutas
 * @returns Objeto con rutas convertidas a formato Windows
 *
 * @example
 * const data = { path_file: '/mnt/repositorio/2510SP/file.pdf', nombre: 'Test' }
 * convertPathsForDisplay(data)
 * // => { path_file: '\\\\repositorio\\DirGesCat\\2510SP\\file.pdf', nombre: 'Test' }
 */
export function convertPathsForDisplay(dataDict: Record<string, any>): Record<string, any> {
  if (!dataDict || typeof dataDict !== 'object') {
    return dataDict
  }

  const result = { ...dataDict }

  for (const field of PATH_FIELDS) {
    if (field in result && result[field]) {
      result[field] = linuxToWindowsPath(result[field])
    }
  }

  return result
}

/**
 * Copia una ruta al portapapeles
 *
 * @param path - Ruta a copiar
 * @returns Promise que se resuelve cuando se copia exitosamente
 */
export async function copyPathToClipboard(path: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(path)
  } catch (err) {
    // Fallback para navegadores antiguos
    const textArea = document.createElement('textarea')
    textArea.value = path
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    document.execCommand('copy')
    textArea.remove()
  }
}

export default {
  linuxToWindowsPath,
  windowsToLinuxPath,
  isLinuxPath,
  isWindowsPath,
  isPathLike,
  convertPathsForDisplay,
  copyPathToClipboard,
  PATH_FIELDS
}
