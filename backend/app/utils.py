# 🔧 PARCHE PARA utils.py - Corregir rutas de backup
# Reemplazar la clase ScriptRunner completa con esta versión corregida:

import os
import sys
import subprocess
import shutil
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class ScriptRunner:
    def __init__(self, base_scripts_dir=None):
        # 🔧 CORECCIÓN: Directorio donde están los scripts 
        if base_scripts_dir is None:
            # Los scripts están en el directorio padre de backend, no dentro
            self.scripts_dir = Path(settings.BASE_DIR) / "scripts"
            
            # También el backup_dir debe estar en backend/backups
            self.backup_dir = Path(settings.BASE_DIR) / "scripts" / "backups"
            self.backup_dir.mkdir(exist_ok=True)
        else:
            self.scripts_dir = Path(base_scripts_dir)
        
        # 🔧 CORECCIÓN: Directorio para backups (donde realmente se crean)
        # El script copia_Seguridad_db.py crea los backups en database_backups dentro del directorio de scripts
        self.backup_dir = self.scripts_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # También crear el directorio alternativo para compatibilidad
        self.backup_dir_alt = Path(settings.BASE_DIR) / "backups"
        self.backup_dir_alt.mkdir(exist_ok=True)
    
    def clean_backup_directory(self):
        """Limpia AMBOS directorios de backups"""
        try:
            directories_cleaned = 0
            
            # Limpiar directorio principal (donde se crean realmente)
            if self.backup_dir.exists():
                for file_path in self.backup_dir.iterdir():
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                directories_cleaned += 1
                logger.info(f"Directorio principal de backups limpiado: {self.backup_dir}")
            
            # Limpiar directorio alternativo
            if self.backup_dir_alt.exists():
                for file_path in self.backup_dir_alt.iterdir():
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                directories_cleaned += 1
                logger.info(f"Directorio alternativo de backups limpiado: {self.backup_dir_alt}")
            
            return directories_cleaned > 0
        except Exception as e:
            logger.error(f"Error limpiando directorios de backups: {str(e)}")
            return False
    
    def limite_maximos_backups(self, max_backups=5):
        """Limita el número de backups a MAX_BACKUPS, eliminando los más antiguos.
        También limpia ZIPs y logs huérfanos que se acumulan."""
        try:
            backup_files = []

            # Recolectar todos los archivos .sql de ambos directorios
            if self.backup_dir.exists():
                for f in self.backup_dir.glob("*.sql"):
                    backup_files.append(f)

            if self.backup_dir_alt.exists():
                for f in self.backup_dir_alt.glob("*.sql"):
                    backup_files.append(f)

            # Ordenar por fecha de modificación (más reciente primero)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Eliminar los backups que excedan el límite
            if len(backup_files) > max_backups:
                archivos_a_eliminar = backup_files[max_backups:]
                for archivo in archivos_a_eliminar:
                    try:
                        archivo.unlink()
                        logger.info(f"Backup antiguo eliminado: {archivo.name}")
                    except Exception as e:
                        logger.error(f"Error al eliminar {archivo.name}: {str(e)}")

                logger.info(f"Se mantienen {max_backups} backups más recientes, {len(archivos_a_eliminar)} eliminados")
            else:
                logger.info(f"Total de backups: {len(backup_files)}, dentro del límite de {max_backups}")

            # Limpiar ZIPs huérfanos de descargas anteriores
            self._limpiar_archivos_temporales()

            return True
        except Exception as e:
            logger.error(f"Error limitando backups: {str(e)}")
            return False

    def _limpiar_archivos_temporales(self):
        """Elimina ZIPs de descargas anteriores y logs viejos de ambos directorios"""
        eliminados = 0
        for directorio in [self.backup_dir, self.backup_dir_alt, self.scripts_dir]:
            if not directorio.exists():
                continue
            # Eliminar todos los .zip (se regeneran en cada descarga)
            for f in directorio.glob("*.zip"):
                try:
                    f.unlink()
                    eliminados += 1
                except Exception as e:
                    logger.error(f"Error al eliminar ZIP {f.name}: {str(e)}")
            # Eliminar logs de ejecución de backup (solo los .log)
            for f in directorio.glob("backup_execution_*.log"):
                try:
                    f.unlink()
                    eliminados += 1
                except Exception as e:
                    logger.error(f"Error al eliminar log {f.name}: {str(e)}")
        if eliminados > 0:
            logger.info(f"Limpieza: {eliminados} archivos temporales (ZIPs/logs) eliminados")

    def execute_backup_script(self):
        """Ejecuta el script de copia de seguridad con rutas corregidas"""
        logger.info("=" * 80)
        logger.info("🎬 INICIANDO execute_backup_script()")
        logger.info("=" * 80)
        try:
            logger.info("⏳ Paso 1: Limitando backups antiguos...")
            # NO limpiar directorios antes de ejecutar - solo limitar backups antiguos
            # Limitar a máximo 5 backups (elimina los más viejos automáticamente)
            self.limite_maximos_backups(max_backups=5)
            logger.info("✅ Paso 1: Límite de backups completado")

            logger.info("⏳ Paso 2: Verificando existencia del script...")
            script_path = self.scripts_dir / "copia_Seguridad_db.py"
            logger.info(f"📂 Ruta del script: {script_path}")
            logger.info(f"📂 ¿Script existe?: {script_path.exists()}")
            if not script_path.exists():
                logger.error(f"❌ Script no encontrado: {script_path}")
                raise FileNotFoundError(f"Script no encontrado: {script_path}")
            logger.info("✅ Paso 2: Script encontrado")
            
            # Configurar el entorno
            env = os.environ.copy()
            env['PYTHONPATH'] = str(settings.BASE_DIR)
            
            # Ejecutar el script y guardar logs en archivo
            cmd = [sys.executable, str(script_path)]
            log_file = self.scripts_dir / f"backup_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

            logger.info(f"🚀 Ejecutando comando: {' '.join(cmd)}")
            logger.info(f"📁 Directorio de trabajo: {self.scripts_dir}")
            logger.info(f"🔧 Variables de entorno DB_HOST: {env.get('DB_HOST', 'NO DEFINIDO')}")
            logger.info(f"📝 Log guardándose en: {log_file}")

            # Ejecutar y guardar output en archivo
            with open(log_file, 'w') as f:
                result = subprocess.run(
                    cmd,
                    cwd=str(self.scripts_dir),
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env,
                    timeout=300
                )

            # Leer el log para mostrarlo
            with open(log_file, 'r') as f:
                log_content = f.read()

            logger.info(f"✅ Código de salida: {result.returncode}")
            logger.info(f"📄 OUTPUT COMPLETO:\n{log_content}")

            # También guardarlo en el resultado
            result.stdout = log_content
            result.stderr = "" if result.returncode == 0 else log_content

            # 🔧 CORECCIÓN: Buscar archivos en AMBOS directorios
            backup_files = []
            logger.info(f"🔍 Buscando backups en: {self.backup_dir}")
            logger.info(f"🔍 ¿Directorio existe?: {self.backup_dir.exists()}")
            # Buscar en directorio principal
            if self.backup_dir.exists():
                archivos = list(self.backup_dir.iterdir())
                print(f"🔍 Archivos encontrados: {archivos}")

                for file_path in self.backup_dir.iterdir():
                    if file_path.is_file():
                        backup_files.append({
                            'filename': file_path.name,
                            'filepath': str(file_path),
                            'size': file_path.stat().st_size,
                            'location': 'principal'
                        })
            
            # Buscar en directorio alternativo
            if self.backup_dir_alt.exists():
                for file_path in self.backup_dir_alt.iterdir():
                    if file_path.is_file():
                        backup_files.append({
                            'filename': file_path.name,
                            'filepath': str(file_path),
                            'size': file_path.stat().st_size,
                            'location': 'alternativo'
                        })
            
            logger.info(f"Backup completado. Archivos encontrados: {len(backup_files)}")
            for bf in backup_files:
                logger.info(f"  - {bf['filename']} ({bf['size']} bytes) en {bf['location']}")
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'backup_files': backup_files,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired as e:
            logger.error(f"⏱️ TIMEOUT: El script excedió el tiempo límite de ejecución (5 minutos)")
            logger.error(f"⏱️ Detalles: {str(e)}")
            return {
                'success': False,
                'output': '',
                'error': 'El script excedió el tiempo límite de ejecución (5 minutos)',
                'backup_files': [],
                'return_code': -1
            }
        except Exception as e:
            logger.error("=" * 80)
            logger.error("💥 EXCEPCIÓN CAPTURADA EN execute_backup_script()")
            logger.error("=" * 80)
            logger.error(f"❌ Tipo de error: {type(e).__name__}")
            logger.error(f"❌ Mensaje: {str(e)}")
            logger.error(f"❌ Traceback completo:", exc_info=True)
            logger.error("=" * 80)
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'backup_files': [],
                'return_code': -1
            }
    
    def execute_data_script(self):
        """Ejecuta el script de llenado de datos con ruta corregida"""
        try:
            script_path = self.scripts_dir / "llenar_datos_dir_pre_&_post.py"
            if not script_path.exists():
                raise FileNotFoundError(f"Script no encontrado: {script_path}")
            
            # Configurar el entorno
            env = os.environ.copy()
            env['PYTHONPATH'] = str(settings.BASE_DIR)
            
            # Ejecutar el script
            cmd = [sys.executable, str(script_path)]
            result = subprocess.run(
                cmd,
                cwd=str(self.scripts_dir),  # 🔧 Ejecutar desde el directorio correcto
                capture_output=True,
                text=True,
                env=env,
                timeout=600  # 10 minutos de timeout
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'El script excedió el tiempo límite de ejecución (10 minutos)',
                'return_code': -1
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'return_code': -1
            }
    
    def create_zip_from_backups(self):
        """Crea un archivo ZIP con todos los backups de AMBOS directorios"""
        try:
            # Limpiar ZIPs anteriores antes de crear uno nuevo
            self._limpiar_archivos_temporales()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"backup_{timestamp}.zip"

            # Crear el ZIP en el directorio principal
            zip_path = self.backup_dir / zip_filename
            
            files_added = 0
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Agregar archivos del directorio principal
                if self.backup_dir.exists():
                    for file_path in self.backup_dir.iterdir():
                        if file_path.is_file() and not file_path.name.endswith('.zip'):
                            zipf.write(file_path, f"principal_{file_path.name}")
                            files_added += 1
                
                # Agregar archivos del directorio alternativo
                if self.backup_dir_alt.exists():
                    for file_path in self.backup_dir_alt.iterdir():
                        if file_path.is_file() and not file_path.name.endswith('.zip'):
                            zipf.write(file_path, f"alternativo_{file_path.name}")
                            files_added += 1
            
            if zip_path.exists() and zip_path.stat().st_size > 0 and files_added > 0:
                logger.info(f"ZIP creado con {files_added} archivos: {zip_path}")
                return {
                    'success': True,
                    'zip_path': str(zip_path),
                    'zip_filename': zip_filename,
                    'zip_size': zip_path.stat().st_size,
                    'files_included': files_added
                }
            else:
                return {
                    'success': False,
                    'error': f'No se pudo crear el archivo ZIP o está vacío (archivos encontrados: {files_added})'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error creando ZIP: {str(e)}'
            }
    
    def get_backup_files(self):
        """Obtiene la lista de archivos de backup de AMBOS directorios"""
        try:
            files = []
            
            # Archivos del directorio principal
            if self.backup_dir.exists():
                for file_path in self.backup_dir.iterdir():
                    if file_path.is_file():
                        files.append({
                            'filename': file_path.name,
                            'filepath': str(file_path),
                            'size': file_path.stat().st_size,
                            'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                            'location': 'principal'
                        })
            
            # Archivos del directorio alternativo
            if self.backup_dir_alt.exists():
                for file_path in self.backup_dir_alt.iterdir():
                    if file_path.is_file():
                        files.append({
                            'filename': file_path.name,
                            'filepath': str(file_path),
                            'size': file_path.stat().st_size,
                            'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                            'location': 'alternativo'
                        })
            
            logger.info(f"Archivos de backup encontrados: {len(files)}")
            return sorted(files, key=lambda x: x['modified'], reverse=True)
        except Exception as e:
            logger.error(f"Error obteniendo archivos de backup: {str(e)}")
            return []

# 🔧 MANTENER EL RESTO DE LA CLASE DatabaseBackupManager SIN CAMBIOS
class DatabaseBackupManager:
    """Manager específico para backups de base de datos usando la configuración de Django"""
    
    @staticmethod
    def get_db_config():
        """Obtiene la configuración de base de datos desde Django settings"""
        db_config = settings.DATABASES['default']
        return {
            'host': db_config.get('HOST', 'localhost'),
            'database': db_config.get('NAME'),
            'user': db_config.get('USER'),
            'password': db_config.get('PASSWORD'),
            'port': db_config.get('PORT', '5432')
        }
    
    @staticmethod
    def create_backup_with_django_config(output_dir=None):
        """Crea un backup usando la configuración de Django"""
        if output_dir is None:
            output_dir = Path(settings.BASE_DIR).parent / "Scripts" / "backups"
        
        # Importar las funciones del script original
        sys.path.append(str(Path(settings.BASE_DIR).parent / "Scripts"))
        
        try:
            import copia_Seguridad_db as backup_module
            
            db_config = DatabaseBackupManager.get_db_config()
            
            # Crear directorio si no existe
            Path(output_dir).mkdir(exist_ok=True)
            
            # Intentar crear backup con diferentes métodos
            result = backup_module.create_postgres_backup(db_config, str(output_dir))
            
            if not result:
                result = backup_module.backup_using_custom_commands(db_config, str(output_dir))
            
            if not result:
                result = backup_module.create_backup_with_psycopg2(db_config, str(output_dir))
            
            return result
            
        except Exception as e:
            logger.error(f"Error en backup con configuración de Django: {str(e)}")
            return None