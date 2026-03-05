# app/settings.py
# Configuraciones específicas para la app de scripts

import os
from pathlib import Path
from django.conf import settings

# Configuraciones por defecto para scripts
SCRIPT_SETTINGS = {
    # Directorio base donde están los scripts
    'SCRIPTS_BASE_DIR': Path(settings.BASE_DIR).parent / "Scripts",
    
    # Directorio donde se guardan los backups
    'BACKUPS_DIR': Path(settings.BASE_DIR) / "backups",
    
    # Timeouts para diferentes tipos de scripts (en segundos)
    'TIMEOUTS': {
        'backup_db': 300,      # 5 minutos
        'llenar_datos': 600,   # 10 minutos
        'default': 300         # 5 minutos por defecto
    },
    
    # Configuración de compresión
    'COMPRESSION': {
        'enabled': True,
        'method': 'zip',       # 'zip' o 'gzip'
        'compression_level': 6  # 1-9, donde 9 es máxima compresión
    },
    
    # Configuración de limpieza automática
    'AUTO_CLEANUP': {
        'enabled': True,
        'backup_db': True,     # Limpiar antes de backup
        'llenar_datos': False  # No limpiar para este script
    },
    
    # Configuración de archivos
    'FILES': {
        'max_backup_files': 10,     # Máximo número de backups a mantener
        'max_total_size_mb': 500,   # Tamaño máximo total en MB
        'auto_delete_old': True     # Eliminar archivos viejos automáticamente
    },
    
    # Configuración de logging
    'LOGGING': {
        'log_output': True,        # Guardar output de scripts
        'log_errors': True,        # Guardar errores detallados
        'max_log_length': 10000    # Máximo caracteres en logs
    },
    
    # Configuración de notificaciones (para futuras implementaciones)
    'NOTIFICATIONS': {
        'enabled': False,
        'email_on_success': False,
        'email_on_failure': True,
        'webhook_url': None
    }
}

# Función para obtener configuraciones con valores por defecto
def get_script_setting(key, default=None):
    """
    Obtiene una configuración específica del script
    
    Args:
        key (str): Clave de configuración (puede usar notación de punto)
        default: Valor por defecto si no se encuentra la configuración
    
    Returns:
        Valor de la configuración o default
    """
    # Permitir override desde Django settings
    django_settings = getattr(settings, 'SCRIPT_SETTINGS', {})
    
    # Combinar configuraciones
    combined_settings = {**SCRIPT_SETTINGS, **django_settings}
    
    # Navegar por claves anidadas (ej: 'TIMEOUTS.backup_db')
    keys = key.split('.')
    value = combined_settings
    
    try:
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        return default

# Funciones helper para configuraciones comunes
def get_timeout_for_script(script_name):
    """Obtiene el timeout para un script específico"""
    timeouts = get_script_setting('TIMEOUTS', {})
    return timeouts.get(script_name, timeouts.get('default', 300))

def should_auto_cleanup(script_name):
    """Determina si debe hacer limpieza automática para un script"""
    auto_cleanup = get_script_setting('AUTO_CLEANUP', {})
    if not auto_cleanup.get('enabled', False):
        return False
    return auto_cleanup.get(script_name, False)

def get_backup_directory():
    """Obtiene el directorio de backups"""
    backup_dir = get_script_setting('BACKUPS_DIR')
    if isinstance(backup_dir, str):
        backup_dir = Path(backup_dir)
    
    # Crear directorio si no existe
    backup_dir.mkdir(exist_ok=True)
    return backup_dir

def get_scripts_directory():
    """Obtiene el directorio de scripts"""
    scripts_dir = get_script_setting('SCRIPTS_BASE_DIR')
    if isinstance(scripts_dir, str):
        scripts_dir = Path(scripts_dir)
    return scripts_dir

# Configuración para usar en Django settings.py
# Agregar esto al final de tu settings.py para personalizar:

"""
# En backend/settings.py, al final del archivo:

# Configuración personalizada para scripts
SCRIPT_SETTINGS = {
    'BACKUPS_DIR': '/custom/path/to/backups',  # Personalizar ruta de backups
    'TIMEOUTS': {
        'backup_db': 600,  # 10 minutos para backups
        'llenar_datos': 900,  # 15 minutos para datos
    },
    'FILES': {
        'max_backup_files': 20,  # Mantener más backups
        'max_total_size_mb': 1000,  # Permitir más espacio
    },
    'NOTIFICATIONS': {
        'enabled': True,
        'email_on_failure': True,
        'webhook_url': 'https://tu-webhook.com/scripts',
    }
}
"""