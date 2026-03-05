#!/usr/bin/env python3
"""
Scheduler inteligente para ejecutar scripts según horarios configurados
- POST e INSUMOS: cada 6 horas (00:00, 06:00, 12:00, 18:00)
- TRANSVERSAL y OPERACION: cada 72 horas (Lunes 02:00), SECUENCIAL
- Evita ejecuciones paralelas de OPERACION con otros scripts
- Sistema de bloqueo para prevenir múltiples instancias
"""

import os
import sys
import time
import subprocess
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import psutil
import json
import threading
import schedule

# Importar utilidades comunes
sys.path.insert(0, str(Path(__file__).parent))
from utils.common import Config, TelegramNotifier, Logger


class ScriptScheduler:
    """Programador de scripts inteligente"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = Config(config_path)
        self.notifier = TelegramNotifier(self.config)
        self.logger = Logger.setup_logger('scheduler', self.config)

        self.scripts_dir = Path(self.config.get('paths', 'scripts_dir'))
        self.base_dir = Path(self.config.get('paths', 'base_dir'))
        self.lock_file = self.base_dir / 'scheduler.lock'

        # Estado de ejecución
        self.running_scripts: Dict[str, subprocess.Popen] = {}
        self.script_start_times: Dict[str, datetime] = {}
        self.last_execution: Dict[str, datetime] = {}

        # Cargar configuración de scripts
        self.post_insumos_config = self.config.get('scheduler', 'post_insumos')
        self.transversal_operacion_config = self.config.get('scheduler', 'transversal_operacion')

    def _create_lock(self) -> bool:
        """Crea archivo de bloqueo para evitar múltiples instancias"""
        if self.lock_file.exists():
            # Verificar si el proceso está realmente corriendo
            try:
                with open(self.lock_file, 'r') as f:
                    old_pid = int(f.read().strip())
                if psutil.pid_exists(old_pid):
                    self.logger.warning(f"Scheduler ya está corriendo (PID: {old_pid})")
                    return False
            except:
                pass

        # Crear nuevo lock
        with open(self.lock_file, 'w') as f:
            f.write(str(os.getpid()))
        return True

    def _remove_lock(self):
        """Elimina archivo de bloqueo"""
        if self.lock_file.exists():
            self.lock_file.unlink()

    def _is_script_running(self, script_name: str) -> bool:
        """Verifica si un script está corriendo"""
        # Verificar en nuestro diccionario
        if script_name in self.running_scripts:
            proc = self.running_scripts[script_name]
            if proc.poll() is None:  # Aún corriendo
                return True
            else:
                # Script terminó, limpiamos
                del self.running_scripts[script_name]
                if script_name in self.script_start_times:
                    duration = (datetime.now() - self.script_start_times[script_name]).total_seconds() / 60
                    self.notifier.send_script_end(script_name, int(duration), success=proc.returncode == 0)
                    del self.script_start_times[script_name]
                return False

        # Verificar en procesos del sistema
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and script_name in ' '.join(cmdline):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return False

    def _can_run_script(self, script_name: str) -> bool:
        """Verifica si un script puede ejecutarse"""
        # Si el mismo script ya está corriendo, no ejecutar
        if self._is_script_running(script_name):
            self.logger.info(f"{script_name} ya está en ejecución, saltando...")
            return False

        # Si es OPERACION, verificar que ningún otro script esté corriendo
        if 'OPERACION' in script_name:
            for running_script in self.running_scripts.keys():
                if self._is_script_running(running_script):
                    self.logger.info(f"OPERACION no puede iniciar: {running_script} está corriendo")
                    return False

        # Si OPERACION está corriendo, no permitir otros scripts
        if self._is_script_running('Script_OPERACION_Linux.py'):
            self.logger.info(f"{script_name} no puede iniciar: OPERACION está corriendo")
            return False

        return True

    def _run_script(self, script_name: str, wait: bool = False) -> bool:
        """Ejecuta un script"""
        if not self._can_run_script(script_name):
            return False

        script_path = self.scripts_dir / script_name

        if not script_path.exists():
            self.logger.error(f"Script no encontrado: {script_path}")
            return False

        try:
            self.logger.info(f"Iniciando {script_name}...")
            self.notifier.send_script_start(script_name)

            # Preparar variables de entorno - FIX: Pasar explícitamente al subprocess
            env_vars = os.environ.copy()
            env_vars.update({
                'DB_HOST': self.config.get('database', 'host'),
                'DB_NAME': self.config.get('database', 'database'),
                'DB_USER': self.config.get('database', 'user'),
                'DB_PASSWORD': self.config.get('database', 'password'),
                'DB_PORT': str(self.config.get('database', 'port')),
            })

            # Ejecutar script con variables de entorno y directorio de trabajo
            proc = subprocess.Popen(
                ['python3', str(script_path), '--verbose'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                env=env_vars,  # Pasar variables de entorno explícitamente
                cwd=str(script_path.parent)  # Establecer directorio de trabajo
            )

            self.running_scripts[script_name] = proc
            self.script_start_times[script_name] = datetime.now()
            self.last_execution[script_name] = datetime.now()

            if wait:
                # Esperar a que termine
                stdout, stderr = proc.communicate()

                duration = (datetime.now() - self.script_start_times[script_name]).total_seconds() / 60
                success = proc.returncode == 0

                # Loggear stdout y stderr (MEJORADO)
                if stdout:
                    stdout_text = stdout.decode('utf-8', errors='replace')
                    self.logger.info(f"{script_name} STDOUT:\n{stdout_text[:2000]}")

                if stderr:
                    stderr_text = stderr.decode('utf-8', errors='replace')
                    self.logger.error(f"{script_name} STDERR:\n{stderr_text[:2000]}")

                if not success:
                    self.logger.error(f"{script_name} falló con código de retorno: {proc.returncode}")
                    error_msg = stderr.decode('utf-8', errors='replace')[:500] if stderr else "Sin información de error"
                    self.notifier.send_error(script_name, error_msg)

                self.notifier.send_script_end(script_name, int(duration), success)

                # Limpiar
                del self.running_scripts[script_name]
                del self.script_start_times[script_name]

                return success
            else:
                # Monitorear en background
                threading.Thread(target=self._monitor_script, args=(script_name,), daemon=True).start()
                return True

        except Exception as e:
            self.logger.error(f"Error al ejecutar {script_name}: {e}")
            self.notifier.send_error(script_name, str(e))
            return False

    def _monitor_script(self, script_name: str):
        """Monitorea un script en ejecución"""
        if script_name not in self.running_scripts:
            return

        proc = self.running_scripts[script_name]

        try:
            # Esperar a que termine y capturar salidas
            stdout, stderr = proc.communicate()

            # Calcular duración
            duration = (datetime.now() - self.script_start_times[script_name]).total_seconds() / 60
            success = proc.returncode == 0

            # Loggear stdout y stderr (MEJORADO - siempre capturar)
            if stdout:
                stdout_text = stdout.decode('utf-8', errors='replace')
                self.logger.info(f"{script_name} STDOUT:\n{stdout_text[:2000]}")

            if stderr:
                stderr_text = stderr.decode('utf-8', errors='replace')
                self.logger.error(f"{script_name} STDERR:\n{stderr_text[:2000]}")

            # Notificar fin
            self.notifier.send_script_end(script_name, int(duration), success)

            if not success:
                self.logger.error(f"{script_name} falló con código de retorno: {proc.returncode}")
                error_msg = stderr.decode('utf-8', errors='replace')[:500] if stderr else "Sin información de error"
                self.notifier.send_error(script_name, error_msg)

        except Exception as e:
            self.logger.error(f"Error monitoreando {script_name}: {e}")
        finally:
            # Limpiar
            if script_name in self.running_scripts:
                del self.running_scripts[script_name]
            if script_name in self.script_start_times:
                del self.script_start_times[script_name]

    def _run_post_insumos(self):
        """Ejecuta POST e INSUMOS (pueden correr en paralelo)"""
        self.logger.info("=== Ejecutando POST e INSUMOS ===")

        scripts = self.post_insumos_config['scripts']

        for script in scripts:
            self._run_script(script, wait=False)

    def _run_transversal_operacion(self):
        """Ejecuta TRANSVERSAL y OPERACION (SECUENCIAL)"""
        self.logger.info("=== Ejecutando TRANSVERSAL y OPERACION (SECUENCIAL) ===")

        scripts = self.transversal_operacion_config['scripts']

        # Ejecutar secuencialmente
        for script in scripts:
            if self._run_script(script, wait=True):
                self.logger.info(f"{script} completado exitosamente")
            else:
                self.logger.error(f"{script} falló, abortando secuencia")
                break

    def _schedule_jobs(self):
        """Configura los horarios de ejecución"""
        # POST e INSUMOS cada 6 horas
        for time_str in self.post_insumos_config['schedule']:
            schedule.every().day.at(time_str).do(self._run_post_insumos)
            self.logger.info(f"Programado: POST e INSUMOS a las {time_str}")

        # TRANSVERSAL y OPERACION cada Lunes a las 02:00
        schedule.every().monday.at("02:00").do(self._run_transversal_operacion)
        self.logger.info("Programado: TRANSVERSAL y OPERACION cada Lunes 02:00")

    def _send_daily_summary(self):
        """Envía resumen diario"""
        message = "📊 *Resumen Diario*\n\n"

        for script_name, last_run in self.last_execution.items():
            script_short = script_name.replace('Script_', '').replace('_Linux.py', '')
            time_ago = datetime.now() - last_run
            hours_ago = int(time_ago.total_seconds() / 3600)
            message += f"• {script_short}: hace {hours_ago}h\n"

        self.notifier.send_message(message)

    def run(self):
        """Inicia el scheduler"""
        if not self._create_lock():
            self.logger.error("No se pudo crear lock, otra instancia está corriendo")
            sys.exit(1)

        self.logger.info("Scheduler iniciado correctamente")
        self.notifier.send_message("🚀 *Scheduler iniciado*\n\nScripts programados correctamente.")

        # Configurar trabajos
        self._schedule_jobs()

        # Resumen diario a las 23:00
        schedule.every().day.at("23:00").do(self._send_daily_summary)

        # Manejador de señales para limpieza
        def signal_handler(signum, frame):
            self.logger.info("Señal de terminación recibida, limpiando...")
            self._remove_lock()

            # Terminar scripts en ejecución
            for script_name, proc in self.running_scripts.items():
                self.logger.info(f"Terminando {script_name}...")
                proc.terminate()

            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Loop principal
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto

        except Exception as e:
            self.logger.error(f"Error en scheduler: {e}")
            self.notifier.send_error("Scheduler", str(e))
        finally:
            self._remove_lock()


if __name__ == '__main__':
    try:
        scheduler = ScriptScheduler()
        scheduler.run()
    except KeyboardInterrupt:
        print("\n👋 Scheduler detenido por el usuario")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)
