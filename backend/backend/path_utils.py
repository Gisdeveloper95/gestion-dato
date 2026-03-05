"""
Utilidades para conversión de rutas entre formatos Linux y Windows.

Este módulo proporciona funciones para convertir rutas entre el formato Linux
usado en el servidor y el formato Windows UNC necesario para que los usuarios
puedan acceder a los archivos desde Excel.
"""


def linux_to_windows_path(linux_path):
    """
    Convierte una ruta de Linux a formato Windows UNC.

    Conversión:
        FROM: /mnt/repositorio/2510SP/...
        TO:   \\repositorio\DirGesCat\2510SP\...

    Args:
        linux_path (str): Ruta en formato Linux (ej: /mnt/repositorio/2510SP/...)

    Returns:
        str: Ruta en formato Windows UNC o el valor original si no se puede convertir

    Examples:
        >>> linux_to_windows_path('/mnt/repositorio/2510SP/H_Informacion_Consulta')
        '\\\\repositorio\\DirGesCat\\2510SP\\H_Informacion_Consulta'

        >>> linux_to_windows_path('Sin ruta')
        'Sin ruta'

        >>> linux_to_windows_path(None)
        None
    """
    # Si es None o vacío, retornar tal cual
    if not linux_path:
        return linux_path

    # Si no es una ruta válida, retornar tal cual
    if not isinstance(linux_path, str):
        return linux_path

    # Normalizar la ruta para procesar
    ruta_normalizada = linux_path.strip()

    # Caso 1: Ruta Linux estándar: /mnt/repositorio/...
    if ruta_normalizada.startswith('/mnt/repositorio'):
        windows_path = ruta_normalizada.replace('/mnt/repositorio', r'\\repositorio\DirGesCat')
        windows_path = windows_path.replace('/', '\\')
        return windows_path

    # Caso 2: Ruta que ya tiene formato Windows parcial con / : //repositorio/DirGesCat/...
    if '//repositorio' in ruta_normalizada.lower() or '/repositorio/dirgescat' in ruta_normalizada.lower():
        # Normalizar dobles barras al inicio
        windows_path = ruta_normalizada.replace('//', '\\\\', 1)
        # Convertir el resto de / a \
        windows_path = windows_path.replace('/', '\\')
        return windows_path

    # Caso 3: Ruta que ya está en formato Windows correcto: \\repositorio\DirGesCat\...
    if ruta_normalizada.startswith('\\\\repositorio') or ruta_normalizada.startswith(r'\\repositorio'):
        # Ya está correcta, solo asegurar barras invertidas
        return ruta_normalizada.replace('/', '\\')

    # Caso 4: Mensajes especiales o rutas no reconocidas
    # (podría ser "Sin ruta", "Sin directorio", etc.)
    return linux_path


def windows_to_linux_path(windows_path):
    """
    Convierte una ruta de Windows UNC a formato Linux.

    Conversión:
        FROM: \\repositorio\DirGesCat\2510SP\...
        TO:   /mnt/repositorio/2510SP/...

    Args:
        windows_path (str): Ruta en formato Windows UNC

    Returns:
        str: Ruta en formato Linux o el valor original si no se puede convertir

    Examples:
        >>> windows_to_linux_path('\\\\repositorio\\DirGesCat\\2510SP\\H_Informacion_Consulta')
        '/mnt/repositorio/2510SP/H_Informacion_Consulta'
    """
    # Si es None o vacío, retornar tal cual
    if not windows_path:
        return windows_path

    # Si no es una ruta válida, retornar tal cual
    if not isinstance(windows_path, str):
        return windows_path

    # Si ya es una ruta Linux válida, retornarla tal cual
    if windows_path.startswith('/mnt/repositorio'):
        return windows_path

    # Normalizar la ruta: convertir todas las barras invertidas a barras normales
    normalized_path = windows_path.replace('\\', '/')

    # Si no contiene el patrón de repositorio, retornar tal cual
    if 'repositorio' not in normalized_path.lower():
        return windows_path

    # Eliminar barras iniciales extras para normalizar
    # "//repositorio/..." o "/repositorio/..." -> "repositorio/..."
    while normalized_path.startswith('/'):
        normalized_path = normalized_path[1:]

    # Ahora la ruta debería ser: repositorio/DirGesCat/2510SP/...
    # Convertir a formato Linux: /mnt/repositorio/2510SP/...

    # Caso 1: Ruta con DirGesCat (formato estándar de red Windows)
    if normalized_path.lower().startswith('repositorio/dirgescat/'):
        # Quitar "repositorio/DirGesCat/" y agregar "/mnt/repositorio/"
        resto = normalized_path[len('repositorio/DirGesCat/'):]
        linux_path = '/mnt/repositorio/' + resto
        return linux_path

    # Caso 2: Ruta sin DirGesCat (por si ya viene parcialmente convertida)
    if normalized_path.lower().startswith('repositorio/'):
        resto = normalized_path[len('repositorio/'):]
        linux_path = '/mnt/repositorio/' + resto
        return linux_path

    # Si no coincide con ningún patrón conocido, retornar original
    return windows_path


def convert_paths_for_excel_export(data_dict):
    """
    Convierte todas las rutas en un diccionario de datos para exportación a Excel.

    Busca campos comunes de rutas y los convierte de Linux a Windows.

    Args:
        data_dict (dict): Diccionario con datos que pueden contener rutas

    Returns:
        dict: Diccionario con rutas convertidas a formato Windows

    Examples:
        >>> data = {'path_file': '/mnt/repositorio/2510SP/file.pdf', 'nombre': 'Test'}
        >>> convert_paths_for_excel_export(data)
        {'path_file': '\\\\repositorio\\DirGesCat\\2510SP\\file.pdf', 'nombre': 'Test'}
    """
    if not isinstance(data_dict, dict):
        return data_dict

    # Campos comunes que contienen rutas
    path_fields = [
        'path', 'path_file', 'path_directorio', 'ruta', 'ruta_completa',
        'directorio', 'ruta_directorio', 'ruta_archivo'
    ]

    result = data_dict.copy()

    for field in path_fields:
        if field in result and result[field]:
            result[field] = linux_to_windows_path(result[field])

    return result
