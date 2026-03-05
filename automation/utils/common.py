#!/usr/bin/env python3
"""
Utilidades comunes para el sistema de automatización
"""

import os
import json
import psycopg2
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv


class Config:
    """Gestor de configuración centralizado"""

    def __init__(self, config_path: str = None):
        base_dir = Path(__file__).parent.parent
        env_path = base_dir / ".env"

        if not env_path.exists():
            raise FileNotFoundError(f"❌ Archivo .env no encontrado en {env_path}")

        # override=False: no sobreescribir variables ya definidas (Docker)
        load_dotenv(env_path, override=False)
        self.base_dir = base_dir

        # Cargar config.example.json para scheduler (sin credenciales)
        if config_path is None:
            config_path = base_dir / "config" / "config.example.json"

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Carga configuración NO sensible desde JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            # Si no hay config, crear estructura vacía
            return {}

    def get(self, *keys, default=None) -> Any:
        """
        Obtiene un valor de configuración.
        Prioridad: 1) .env, 2) config.example.json
        """
        # 1. Intentar obtener desde variables de entorno (.env)
        env_value = self._get_from_env(*keys)
        if env_value is not None:
            return env_value

        # 2. Fallback a config.example.json (solo scheduler, cleanup)
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def _get_from_env(self, *keys) -> Any:
        """Obtiene valor desde variables de entorno"""
        # Mapeo de rutas de config.json a variables de entorno
        env_map = {
            ('database', 'host'): 'DB_HOST',
            ('database', 'database'): 'DB_NAME',
            ('database', 'user'): 'DB_USER',
            ('database', 'password'): 'DB_PASSWORD',
            ('database', 'port'): 'DB_PORT',
            ('telegram', 'token'): 'TELEGRAM_TOKEN',
            ('telegram', 'chat_id'): 'TELEGRAM_CHAT_ID',
            ('telegram', 'send_logs'): 'TELEGRAM_SEND_LOGS',
            ('ai', 'groq_api_key'): 'GROQ_API_KEY',
            ('ai', 'model'): 'GROQ_MODEL',
            ('ai', 'max_tokens'): 'GROQ_MAX_TOKENS',
            ('ai', 'temperature'): 'GROQ_TEMPERATURE',
            ('paths', 'base_dir'): 'AUTOMATION_DIR',
            ('paths', 'scripts_dir'): 'SCRIPTS_DIR',
            ('paths', 'config_dir'): 'CONFIG_DIR',
            ('logging', 'log_dir'): 'LOGS_DIR',
            ('logging', 'level'): 'LOG_LEVEL',
            ('logging', 'max_file_size_mb'): 'LOG_MAX_SIZE_MB',
            ('logging', 'backup_count'): 'LOG_BACKUP_COUNT',
            ('cleanup', 'enabled'): 'CLEANUP_ENABLED',
            ('cleanup', 'retention_months'): 'CLEANUP_RETENTION_MONTHS',
        }

        env_var = env_map.get(keys)
        if env_var:
            value = os.getenv(env_var)
            if value is not None:
                # Convertir tipos
                if env_var.endswith('_PORT') or env_var.endswith('_TOKENS') or env_var.endswith('_MB') or env_var.endswith('_COUNT') or env_var.endswith('_MONTHS'):
                    return int(value)
                elif env_var.endswith('_TEMPERATURE'):
                    return float(value)
                elif env_var.endswith('_ENABLED') or env_var.endswith('_LOGS'):
                    return value.lower() in ('true', '1', 'yes')
                return value
        return None

    def reload(self):
        """Recarga la configuración desde el archivo"""
        self.config = self._load_config()


class DatabaseManager:
    """Gestor de conexiones a la base de datos"""

    def __init__(self, config: Config):
        self.config = config
        self.db_config = config.get('database')

    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        try:
            conn = psycopg2.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                port=self.db_config['port']
            )
            return conn
        except Exception as e:
            raise Exception(f"Error al conectar a la base de datos: {e}")

    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Ejecuta una query y retorna los resultados si fetch=True"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)

            if fetch:
                result = cursor.fetchall()
                conn.commit()
                return result
            else:
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def cleanup_old_records(self, table: str, months: int = 4) -> int:
        """Elimina registros antiguos de una tabla"""
        query = f"""
            DELETE FROM {table}
            WHERE fecha_creacion < NOW() - INTERVAL '{months} months'
        """
        try:
            count = self.execute_query(query)
            return count
        except Exception as e:
            raise Exception(f"Error al limpiar tabla {table}: {e}")


class TelegramNotifier:
    """Gestor de notificaciones por Telegram"""

    def __init__(self, config: Config):
        self.config = config
        self.token = config.get('telegram', 'token')
        self.chat_id = config.get('telegram', 'chat_id')
        self.send_logs = config.get('telegram', 'send_logs', default=True)
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, message: str, parse_mode: str = 'Markdown') -> bool:
        """Envía un mensaje a Telegram"""
        if not self.send_logs:
            return False

        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Error al enviar mensaje a Telegram: {e}")
            return False

    def send_script_start(self, script_name: str):
        """Notifica el inicio de un script"""
        message = f"🚀 *Iniciando:* `{script_name}`\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.send_message(message)

    def send_script_end(self, script_name: str, duration: int, success: bool = True):
        """Notifica el fin de un script"""
        status = "✅ Completado" if success else "❌ Error"
        message = f"{status}: `{script_name}`\n⏱️ Duración: {duration} min\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.send_message(message)

    def send_error(self, script_name: str, error: str):
        """Notifica un error"""
        message = f"⚠️ *ERROR en* `{script_name}`\n\n```\n{error[:500]}\n```\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.send_message(message)

    def send_cleanup_report(self, deleted_counts: Dict[str, int]):
        """Notifica el resultado de la limpieza de BD"""
        message = "🧹 *Limpieza de Base de Datos*\n\n"
        for table, count in deleted_counts.items():
            message += f"• {table}: {count:,} registros eliminados\n"
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.send_message(message)

    def send_status(self, status_info: Dict[str, Any]):
        """Envía estado del sistema"""
        message = "📊 *Estado del Servidor*\n\n"
        for key, value in status_info.items():
            message += f"• {key}: `{value}`\n"
        self.send_message(message)


class Logger:
    """Gestor de logging centralizado"""

    @staticmethod
    def setup_logger(name: str, config: Config) -> logging.Logger:
        """Configura un logger con rotación de archivos"""
        logger = logging.getLogger(name)

        # Evitar duplicar handlers
        if logger.handlers:
            return logger

        log_dir = Path(config.get('logging', 'log_dir'))
        log_dir.mkdir(parents=True, exist_ok=True)

        level_str = config.get('logging', 'level', default='INFO')
        level = getattr(logging, level_str)
        logger.setLevel(level)

        # Handler para archivo con rotación
        log_file = log_dir / f"{name}.log"
        max_bytes = config.get('logging', 'max_file_size_mb', default=100) * 1024 * 1024
        backup_count = config.get('logging', 'backup_count', default=5)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)

        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger


def format_duration(seconds: int) -> str:
    """Formatea una duración en segundos a formato legible"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def get_system_status() -> Dict[str, str]:
    """Obtiene información del estado del sistema"""
    import subprocess
    import psutil

    status = {}

    # Uso de disco
    disk = psutil.disk_usage('/')
    status['Disco /'] = f"{disk.percent}% usado"

    # Uso de NFS si está montado
    try:
        nfs = psutil.disk_usage('/mnt/repositorio')
        status['NFS /mnt/repositorio'] = f"{nfs.percent}% usado"
    except:
        status['NFS /mnt/repositorio'] = "No montado"

    # Memoria
    mem = psutil.virtual_memory()
    status['Memoria'] = f"{mem.percent}% usada"

    # CPU
    cpu = psutil.cpu_percent(interval=1)
    status['CPU'] = f"{cpu}%"

    # Uptime
    try:
        result = subprocess.run(['uptime', '-p'], capture_output=True, text=True)
        status['Uptime'] = result.stdout.strip().replace('up ', '')
    except:
        status['Uptime'] = "N/A"

    return status


class HealthCheck:
    """Sistema de healthcheck para sincronización entre servicios"""

    def __init__(self, service_name: str, health_file: str = None):
        self.service_name = service_name
        self.health_file = Path(health_file or os.getenv('HEALTHCHECK_FILE', '/tmp/automation_health.json'))
        self.lock_file = Path(f"/tmp/automation_{service_name}.lock")

    def update_status(self, status: str, extra: Dict[str, Any] = None):
        """Actualiza el estado del servicio en el archivo de health"""
        try:
            # Leer estado actual
            data = {}
            if self.health_file.exists():
                with open(self.health_file, 'r') as f:
                    data = json.load(f)

            # Actualizar
            data[self.service_name] = {
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'pid': os.getpid()
            }
            if extra:
                data[self.service_name].update(extra)

            # Escribir
            with open(self.health_file, 'w') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            logging.error(f"Error actualizando healthcheck: {e}")
            return False

    def get_status(self, service_name: str = None) -> Optional[Dict]:
        """Obtiene el estado de un servicio"""
        try:
            if not self.health_file.exists():
                return None

            with open(self.health_file, 'r') as f:
                data = json.load(f)

            target = service_name or self.service_name
            return data.get(target)
        except:
            return None

    def is_service_healthy(self, service_name: str, max_age_seconds: int = 120) -> bool:
        """Verifica si un servicio está saludable (actualizado recientemente)"""
        status = self.get_status(service_name)
        if not status:
            return False

        try:
            last_update = datetime.fromisoformat(status['timestamp'])
            age = (datetime.now() - last_update).total_seconds()
            return age < max_age_seconds and status.get('status') == 'running'
        except:
            return False

    def acquire_lock(self) -> bool:
        """Intenta adquirir un lock exclusivo"""
        import psutil

        if self.lock_file.exists():
            try:
                with open(self.lock_file, 'r') as f:
                    old_pid = int(f.read().strip())
                if psutil.pid_exists(old_pid):
                    return False  # Proceso aún corriendo
            except:
                pass

        # Crear lock
        with open(self.lock_file, 'w') as f:
            f.write(str(os.getpid()))
        return True

    def release_lock(self):
        """Libera el lock"""
        if self.lock_file.exists():
            try:
                with open(self.lock_file, 'r') as f:
                    pid = int(f.read().strip())
                if pid == os.getpid():
                    self.lock_file.unlink()
            except:
                pass


class ServiceCoordinator:
    """Coordinador de sincronización entre scheduler y bot"""

    def __init__(self):
        self.scheduler_health = HealthCheck('scheduler')
        self.bot_health = HealthCheck('bot')
        self.script_status_file = Path('/tmp/automation_scripts.json')

    def notify_script_start(self, script_name: str):
        """Notifica que un script está iniciando"""
        try:
            data = {}
            if self.script_status_file.exists():
                with open(self.script_status_file, 'r') as f:
                    data = json.load(f)

            data[script_name] = {
                'status': 'running',
                'started': datetime.now().isoformat(),
                'pid': os.getpid()
            }

            with open(self.script_status_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.error(f"Error notificando inicio de script: {e}")

    def notify_script_end(self, script_name: str, success: bool, duration_seconds: int = 0):
        """Notifica que un script terminó"""
        try:
            data = {}
            if self.script_status_file.exists():
                with open(self.script_status_file, 'r') as f:
                    data = json.load(f)

            data[script_name] = {
                'status': 'completed' if success else 'failed',
                'finished': datetime.now().isoformat(),
                'duration_seconds': duration_seconds,
                'success': success
            }

            with open(self.script_status_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.error(f"Error notificando fin de script: {e}")

    def get_running_scripts(self) -> Dict[str, Any]:
        """Obtiene lista de scripts en ejecución"""
        try:
            if not self.script_status_file.exists():
                return {}

            with open(self.script_status_file, 'r') as f:
                data = json.load(f)

            # Filtrar solo los que están corriendo
            return {k: v for k, v in data.items() if v.get('status') == 'running'}
        except:
            return {}

    def is_scheduler_ready(self) -> bool:
        """Verifica si el scheduler está listo"""
        return self.scheduler_health.is_service_healthy('scheduler')

    def is_bot_ready(self) -> bool:
        """Verifica si el bot está listo"""
        return self.bot_health.is_service_healthy('bot')
