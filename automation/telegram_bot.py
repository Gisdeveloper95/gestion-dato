#!/usr/bin/env python3
"""
Bot de Telegram para control del servidor de automatización
Comandos disponibles:
- /status - Estado del servidor y scripts
- /scripts - Ver scripts en ejecución (detallado con CPU/RAM/tiempo)
- /proximos - Ver próximas ejecuciones programadas con cuenta regresiva
- /logs [script] - Ver últimos logs
- /iniciar - Ejecutar POST e INSUMOS completos
- /urgente [script] [municipio] - Script específico para municipio
- /detener [script] - Detener script específico
- /restart [script] - Reiniciar script
- /cleanup - Forzar limpieza de BD
- /server [restart|status] - Control del servidor
- /docker - Estado de contenedores Docker
- /ayuda - Ayuda (también puedes usar /comandos)
"""

import os
import sys
import logging
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import time
import psutil
import signal

# Importar utilidades comunes
sys.path.insert(0, str(Path(__file__).parent))
from utils.common import Config, DatabaseManager, TelegramNotifier, Logger, get_system_status, format_duration
from utils.ai_query import AIQuerySystem
from utils.voice_synthesis_simple import get_synthesizer

# Importar biblioteca de Telegram
try:
    from telegram import Update, Bot
    from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
except ImportError:
    print("ERROR: Instala python-telegram-bot: pip3 install python-telegram-bot")
    sys.exit(1)


class ServerBot:
    """Bot de Telegram para control del servidor"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = Config(config_path)
        self.db = DatabaseManager(self.config)
        self.notifier = TelegramNotifier(self.config)
        self.logger = Logger.setup_logger('telegram_bot', self.config)
        self.ai_system = AIQuerySystem(config_path)
        self.voice_synth = get_synthesizer()  # Sintetizador de voz VEGA

        self.scripts_dir = Path(self.config.get('paths', 'scripts_dir'))
        self.authorized_users = self.config.get('telegram', 'authorized_users', default=[])

        # Cargar roles
        self.roles = self._cargar_roles()

        # Mapeo de nombres cortos de scripts
        self.script_map = {
            'post': 'Script_POST_Linux.py',
            'insumos': 'Script_INSUMOS_Linux.py',
            'transversal': 'Script_TRANSVERSAL_Linux.py',
            'operacion': 'Script_OPERACION_Linux.py'
        }

    def _cargar_roles(self) -> Dict:
        """Carga configuración de roles desde JSON"""
        roles_file = Path(self.config.get('paths', 'base_dir')) / 'config' / 'roles.json'
        try:
            with open(roles_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"No se pudieron cargar roles: {e}")
            return {'roles': {}, 'default_role': 'usuario'}

    def _get_user_role(self, user_id: int) -> str:
        """Obtiene el rol de un usuario"""
        for role_name, role_data in self.roles.get('roles', {}).items():
            if user_id in role_data.get('user_ids', []):
                return role_name
        return self.roles.get('default_role', 'usuario')

    def _puede_ejecutar_comando(self, user_id: int, comando: str) -> bool:
        """Verifica si un usuario puede ejecutar un comando según su rol"""
        rol = self._get_user_role(user_id)
        comandos_permitidos = self.roles.get('roles', {}).get(rol, {}).get('comandos_permitidos', [])
        return comando in comandos_permitidos

    def _is_authorized(self, user_id: int) -> bool:
        """Verifica si el usuario está autorizado (mantener compatibilidad)"""
        if not self.authorized_users:
            return True  # Si no hay lista, todos autorizados
        return user_id in self.authorized_users

    async def cmd_start_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start del bot"""
        await update.message.reply_text(
            "🤖 *Bot de Control del Servidor*\n\n"
            "Usa /ayuda o /comandos para ver los comandos disponibles.",
            parse_mode='Markdown'
        )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help - Muestra ayuda"""
        help_text = """
🤖 *Comandos Disponibles*

*📊 Monitoreo*
/status - Estado del servidor y scripts activos
/scripts - Ver scripts en ejecución (detallado)
/proximos - Ver próximas ejecuciones programadas
/logs [script] - Ver últimos logs (ej: /logs post)
/logs\\_live [script] - 🔴 Ver logs EN TIEMPO REAL

*🤖 Consultas IA*
/pregunta [consulta] - Pregunta inteligente con IA
/buscar [keywords] - Buscar archivos por palabras clave
/municipio [nombre] - Info completa de un municipio

*🎮 Control de Scripts*
/iniciar - Ejecutar POST e INSUMOS completos
/ejecutar [script] - Ejecutar CUALQUIER script completo
  Ejemplos:
  • /ejecutar transversal - TRANSVERSAL completo
  • /ejecutar operacion - OPERACION completo
/detener [script] - Detener script
/restart [script] - Reiniciar script

*🚨 Urgencias*
/urgente [script] [municipio] - Script específico para municipio
  Ejemplos:
  • /urgente post Ibagué - POST para Ibagué
  • /urgente insumos La Dorada - INSUMOS para La Dorada

*🧹 Mantenimiento*
/cleanup - Forzar limpieza de BD (>4 meses)

*🖥️ Servidor*
/server status - Estado del sistema
/server restart - Reiniciar servidor (requiere confirmación)

*🐳 Docker*
/docker - Estado de contenedores Docker

*Scripts disponibles:*
• `post` - Script\\_POST\\_Linux.py
• `insumos` - Script\\_INSUMOS\\_Linux.py
• `transversal` - Script\\_TRANSVERSAL\\_Linux.py
• `operacion` - Script\\_OPERACION\\_Linux.py
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status - Estado del sistema"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ No autorizado")
            return

        try:
            # Estado del sistema
            system_status = get_system_status()

            # Scripts activos
            active_scripts = self._get_active_scripts()

            # Último horario de ejecución
            last_runs = self._get_last_script_runs()

            message = "📊 *Estado del Servidor*\n\n"
            message += "*Sistema:*\n"
            for key, value in system_status.items():
                message += f"• {key}: `{value}`\n"

            message += "\n*Scripts Activos:*\n"
            if active_scripts:
                for script, pid in active_scripts.items():
                    message += f"• `{script}` (PID: {pid})\n"
            else:
                message += "• Ninguno en ejecución\n"

            message += "\n*Última Ejecución:*\n"
            for script, last_run in last_runs.items():
                message += f"• `{script}`: {last_run}\n"

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            self.logger.error(f"Error en cmd_status: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def cmd_logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /logs [script] - Ver logs"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ No autorizado")
            return

        if not context.args:
            await update.message.reply_text(
                "Uso: /logs [script]\nEjemplo: /logs post"
            )
            return

        script_name = context.args[0].lower()
        script_full = self.script_map.get(script_name, script_name)

        log_file = Path(self.config.get('logging', 'log_dir')) / f"{script_full}.log"

        if not log_file.exists():
            await update.message.reply_text(f"❌ No se encontró log para `{script_name}`", parse_mode='Markdown')
            return

        try:
            # Leer últimas 30 líneas
            result = subprocess.run(['tail', '-n', '30', str(log_file)], capture_output=True, text=True)
            logs = result.stdout

            if len(logs) > 4000:
                logs = logs[-4000:]

            message = f"📄 *Logs de {script_name}:*\n\n```\n{logs}\n```"
            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            self.logger.error(f"Error en cmd_logs: {e}")
            try:
                if update and update.message:
                    await update.message.reply_text(f"❌ Error al leer logs: {str(e)}")
            except:
                pass  # Evitar errores en cascada

    async def cmd_logs_live(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /logs_live [script] - Ver logs en tiempo real del script en ejecución"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ No autorizado")
            return

        if not context.args:
            await update.message.reply_text(
                "Uso: /logs_live [script]\nEjemplo: /logs_live post"
            )
            return

        script_name = context.args[0].lower()
        script_full = self.script_map.get(script_name, script_name)

        # Verificar si el script está corriendo
        if not self._is_script_running(script_full):
            await update.message.reply_text(
                f"⚠️ `{script_name}` no está en ejecución\n"
                f"Usa `/iniciar` (POST+INSUMOS) o `/urgente {script_name} [municipio]`",
                parse_mode='Markdown'
            )
            return

        try:
            # Buscar el log más reciente del script
            base_dir = Path(self.config.get('paths', 'base_dir'))
            log_dir = base_dir / 'logs' / 'scripts'

            if not log_dir.exists():
                await update.message.reply_text("❌ No hay directorio de logs")
                return

            # Buscar archivos de log del script
            log_files = sorted(log_dir.glob(f"{script_name}_*.log"), key=lambda x: x.stat().st_mtime, reverse=True)

            if not log_files:
                await update.message.reply_text(f"❌ No se encontró log activo para `{script_name}`", parse_mode='Markdown')
                return

            log_file = log_files[0]

            # Leer últimas 50 líneas
            result = subprocess.run(['tail', '-n', '50', str(log_file)], capture_output=True, text=True)
            logs = result.stdout

            if len(logs) > 4000:
                logs = logs[-4000:]

            # Calcular tiempo de ejecución
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            running_time = datetime.now() - file_time
            hours = int(running_time.total_seconds() // 3600)
            minutes = int((running_time.total_seconds() % 3600) // 60)

            message = f"🔴 *Log en vivo: {script_name}*\n"
            message += f"⏱️ Ejecutándose: {hours}h {minutes}m\n"
            message += f"📝 Archivo: `{log_file.name}`\n\n"
            message += f"```\n{logs}\n```"

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            self.logger.error(f"Error en cmd_logs_live: {e}")
            try:
                if update and update.message:
                    await update.message.reply_text(f"❌ Error al leer logs: {str(e)}")
            except:
                pass  # Evitar errores en cascada

    async def cmd_start_script(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /iniciar - Ejecuta POST e INSUMOS completos"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ No autorizado")
            return

        # Verificar que no haya argumentos (solo POST+INSUMOS completo)
        if context.args:
            await update.message.reply_text(
                "❌ `/iniciar` ejecuta POST e INSUMOS completos\n\n"
                "💡 Para un municipio específico usa:\n"
                "`/urgente [script] [municipio]`\n\n"
                "Ejemplo: `/urgente post La Dorada`",
                parse_mode='Markdown'
            )
            return

        try:
            # Crear directorio de logs
            base_dir = Path(self.config.get('paths', 'base_dir'))
            log_dir = base_dir / 'logs' / 'scripts'
            log_dir.mkdir(exist_ok=True, parents=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            scripts_iniciados = []

            # Ejecutar POST e INSUMOS en paralelo
            for script_short in ['post', 'insumos']:
                script_full = self.script_map[script_short]
                script_path = self.scripts_dir / script_full

                if not script_path.exists():
                    continue

                # Verificar si ya está corriendo
                if self._is_script_running(script_full):
                    await update.message.reply_text(f"⚠️ `{script_short}` ya está en ejecución", parse_mode='Markdown')
                    return

                # Crear log file
                log_file = log_dir / f"{script_short}_{timestamp}.log"

                # Construir comando
                cmd = ['python3', str(script_path), '--verbose']

                # Preparar variables de entorno - FIX: Pasar explícitamente al subprocess
                env_vars = os.environ.copy()
                env_vars.update({
                    'DB_HOST': self.config.get('database', 'host'),
                    'DB_NAME': self.config.get('database', 'database'),
                    'DB_USER': self.config.get('database', 'user'),
                    'DB_PASSWORD': self.config.get('database', 'password'),
                    'DB_PORT': str(self.config.get('database', 'port')),
                })

                # Iniciar script con variables de entorno
                with open(log_file, 'w') as f:
                    process = subprocess.Popen(
                        cmd,
                        stdout=f,
                        stderr=subprocess.STDOUT,
                        start_new_session=True,
                        env=env_vars,  # Pasar variables de entorno explícitamente
                        cwd=str(script_path.parent)  # Establecer directorio de trabajo
                    )

                scripts_iniciados.append(script_short)
                self.logger.info(f"Script {script_short} iniciado por usuario {update.effective_user.id} "
                               f"(PID: {process.pid}, log: {log_file})")

            if scripts_iniciados:
                message = (
                    f"✅ *POST e INSUMOS iniciados*\n\n"
                    f"⚡ Scripts ejecutándose:\n"
                )
                for script in scripts_iniciados:
                    message += f"• `{script.upper()}`\n"

                message += f"\n💡 Usa `/logs_live post` o `/logs_live insumos` para monitorear"
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ No se pudieron iniciar los scripts")

        except Exception as e:
            await update.message.reply_text(f"❌ Error al iniciar: {str(e)}")

    async def cmd_ejecutar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ejecutar [script] - Ejecuta CUALQUIER script completo"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ No autorizado")
            return

        if not context.args:
            await update.message.reply_text(
                "📝 *Uso:* `/ejecutar [script]`\n\n"
                "*Ejemplos:*\n"
                "• `/ejecutar post` - POST completo\n"
                "• `/ejecutar insumos` - INSUMOS completo\n"
                "• `/ejecutar transversal` - TRANSVERSAL completo\n"
                "• `/ejecutar operacion` - OPERACION completo\n\n"
                "⚠️ *Nota:* OPERACION bloquea otros scripts mientras corre",
                parse_mode='Markdown'
            )
            return

        script_name = context.args[0].lower()

        # Validar que el script existe
        if script_name not in self.script_map:
            await update.message.reply_text(
                f"❌ Script `{script_name}` no válido\n\n"
                f"Scripts disponibles: `post`, `insumos`, `transversal`, `operacion`",
                parse_mode='Markdown'
            )
            return

        script_full = self.script_map[script_name]
        script_path = self.scripts_dir / script_full

        if not script_path.exists():
            await update.message.reply_text(f"❌ Script no encontrado: {script_path}")
            return

        try:
            # Verificar si ya está corriendo
            if self._is_script_running(script_full):
                await update.message.reply_text(
                    f"⚠️ `{script_name.upper()}` ya está en ejecución\n\n"
                    f"Usa `/detener {script_name}` para detenerlo primero",
                    parse_mode='Markdown'
                )
                return

            # Advertencia especial para OPERACION
            if script_name == 'operacion':
                # Verificar si hay otros scripts corriendo
                active_scripts = self._get_active_scripts()
                if active_scripts:
                    scripts_activos = ', '.join([f"`{s}`" for s in active_scripts.keys()])
                    await update.message.reply_text(
                        f"⚠️ *ADVERTENCIA:* Hay scripts activos: {scripts_activos}\n\n"
                        f"OPERACION requiere que no haya otros scripts ejecutándose.\n"
                        f"Detén los scripts activos primero con `/detener [script]`",
                        parse_mode='Markdown'
                    )
                    return

            # Crear directorio de logs
            base_dir = Path(self.config.get('paths', 'base_dir'))
            log_dir = base_dir / 'logs' / 'scripts'
            log_dir.mkdir(exist_ok=True, parents=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = log_dir / f"{script_name}_{timestamp}.log"

            # Construir comando
            cmd = ['python3', str(script_path), '--verbose']

            # Preparar variables de entorno - FIX: Pasar explícitamente al subprocess
            env_vars = os.environ.copy()
            env_vars.update({
                'DB_HOST': self.config.get('database', 'host'),
                'DB_NAME': self.config.get('database', 'database'),
                'DB_USER': self.config.get('database', 'user'),
                'DB_PASSWORD': self.config.get('database', 'password'),
                'DB_PORT': str(self.config.get('database', 'port')),
            })

            # Iniciar script con variables de entorno
            with open(log_file, 'w') as f:
                process = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                    env=env_vars,  # Pasar variables de entorno explícitamente
                    cwd=str(script_path.parent)  # Establecer directorio de trabajo
                )

            self.logger.info(f"Script {script_name} COMPLETO iniciado por usuario {update.effective_user.id} "
                           f"(PID: {process.pid}, log: {log_file})")

            # Mensaje de confirmación
            icon = "🔥" if script_name == 'operacion' else "⚡"
            message = (
                f"{icon} *{script_name.upper()} COMPLETO iniciado*\n\n"
                f"🔧 PID: `{process.pid}`\n"
                f"📝 Log: `{log_file.name}`\n\n"
                f"💡 Usa `/logs_live {script_name}` para monitorear\n"
                f"💡 Usa `/detener {script_name}` para detener"
            )

            if script_name == 'operacion':
                message += "\n\n⚠️ *OPERACION bloqueará otros scripts mientras se ejecuta*"

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            self.logger.error(f"Error ejecutando {script_name}: {e}")
            await update.message.reply_text(f"❌ Error al ejecutar: {str(e)}")

    async def cmd_stop_script(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /stop [script] - Detener script"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ No autorizado")
            return

        if not context.args:
            await update.message.reply_text(
                "Uso: /stop [script]\nEjemplo: /stop post"
            )
            return

        script_name = context.args[0].lower()
        script_full = self.script_map.get(script_name, script_name)

        try:
            pid = self._get_script_pid(script_full)
            if pid:
                os.kill(pid, signal.SIGTERM)
                await update.message.reply_text(f"✅ `{script_name}` detenido (PID: {pid})", parse_mode='Markdown')
                self.logger.info(f"Script {script_name} detenido por usuario {update.effective_user.id}")
            else:
                await update.message.reply_text(f"⚠️ `{script_name}` no está en ejecución", parse_mode='Markdown')

        except Exception as e:
            await update.message.reply_text(f"❌ Error al detener: {str(e)}")

    async def cmd_restart_script(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /restart [script] - Reiniciar script"""
        if not context.args:
            await update.message.reply_text(
                "Uso: /restart [script]\nEjemplo: /restart post"
            )
            return

        # Detener
        await self.cmd_stop_script(update, context)
        time.sleep(2)

        # Iniciar
        await self.cmd_start_script(update, context)

    async def cmd_cleanup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /cleanup - Limpiar BD"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ No autorizado")
            return

        await update.message.reply_text("🧹 Iniciando limpieza de base de datos...")

        try:
            retention_months = self.config.get('cleanup', 'retention_months', default=4)
            tables = self.config.get('cleanup', 'tables', default=[])

            deleted_counts = {}
            for table in tables:
                count = self.db.cleanup_old_records(table, retention_months)
                deleted_counts[table] = count

            # Enviar reporte
            message = f"✅ *Limpieza Completada*\n\n"
            for table, count in deleted_counts.items():
                message += f"• {table}: {count:,} registros eliminados\n"

            await update.message.reply_text(message, parse_mode='Markdown')
            self.logger.info(f"Limpieza manual ejecutada por usuario {update.effective_user.id}")

        except Exception as e:
            await update.message.reply_text(f"❌ Error en limpieza: {str(e)}")

    async def cmd_server(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /server [status|restart] - Control del servidor"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ No autorizado")
            return

        if not context.args:
            await update.message.reply_text(
                "Uso: /server [status|restart]\nEjemplo: /server status"
            )
            return

        action = context.args[0].lower()

        if action == 'status':
            system_status = get_system_status()
            message = "🖥️ *Estado del Sistema*\n\n"
            for key, value in system_status.items():
                message += f"• {key}: `{value}`\n"
            await update.message.reply_text(message, parse_mode='Markdown')

        elif action == 'restart':
            await update.message.reply_text(
                "⚠️ *ADVERTENCIA*: ¿Confirmar reinicio del servidor?\n"
                "Responde 'SI CONFIRMO' para continuar.",
                parse_mode='Markdown'
            )
            # TODO: Implementar sistema de confirmación

        else:
            await update.message.reply_text("❌ Acción no válida. Usa: status o restart")

    async def cmd_docker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /docker - Estado de Docker"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ No autorizado")
            return

        try:
            result = subprocess.run(
                ['sudo', 'docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                output = result.stdout
                message = f"🐳 *Docker Containers*\n\n```\n{output}\n```"
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Error al obtener estado de Docker")

        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def cmd_scripts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /scripts - Ver scripts en ejecución con detalles"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ No autorizado")
            return

        try:
            active_scripts_info = self._get_active_scripts_detailed()

            if not active_scripts_info:
                message = "📋 *Scripts en Ejecución*\n\n"
                message += "✅ No hay scripts ejecutándose actualmente\n\n"
                message += "_Usa /iniciar [script] para ejecutar uno_"
                await update.message.reply_text(message, parse_mode='Markdown')
                return

            message = "📋 *Scripts en Ejecución*\n\n"

            # Contar scripts en paralelo
            total = len(active_scripts_info)
            if total > 1:
                message += f"⚡ *{total} scripts en paralelo*\n\n"

            for script_info in active_scripts_info:
                script_name = script_info['name']
                pid = script_info['pid']
                runtime = script_info['runtime']
                cpu = script_info['cpu']
                memory = script_info['memory']

                message += f"🔹 *{script_name}*\n"
                message += f"   • PID: `{pid}`\n"
                message += f"   • Tiempo: `{runtime}`\n"
                message += f"   • CPU: `{cpu:.1f}%`\n"
                message += f"   • RAM: `{memory:.1f} MB`\n\n"

            # Agregar nota si OPERACION está corriendo
            operacion_running = any(s['name'] == 'operacion' for s in active_scripts_info)
            if operacion_running:
                message += "⚠️ _OPERACION en ejecución - otros scripts bloqueados_\n"

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            self.logger.error(f"Error en cmd_scripts: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def cmd_proximos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /proximos - Ver próximas ejecuciones programadas"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ No autorizado")
            return

        try:
            proximas_ejecuciones = self._get_next_executions()

            message = "⏰ *Próximas Ejecuciones Programadas*\n\n"

            if not proximas_ejecuciones:
                message += "⚠️ No hay ejecuciones programadas\n"
                await update.message.reply_text(message, parse_mode='Markdown')
                return

            for idx, ejecucion in enumerate(proximas_ejecuciones, 1):
                scripts = ejecucion['scripts']
                hora = ejecucion['hora']
                tiempo_restante = ejecucion['tiempo_restante']
                es_proximo = ejecucion['es_proximo']

                # Icono especial para el próximo
                icono = "🔜" if es_proximo else f"{idx}️⃣"

                message += f"{icono} *{', '.join(scripts)}*\n"
                message += f"   📅 {hora}\n"
                message += f"   ⏳ {tiempo_restante}\n\n"

            # Footer con información adicional
            message += "_💡 Los horarios son automáticos según configuración_"

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            self.logger.error(f"Error en cmd_proximos: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def cmd_pregunta(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /pregunta - Consulta con IA"""
        user_id = update.effective_user.id

        if not self._puede_ejecutar_comando(user_id, 'pregunta'):
            rol = self._get_user_role(user_id)
            await update.message.reply_text(
                f"❌ No autorizado\nTu rol: `{rol}`", parse_mode='Markdown'
            )
            return

        if not context.args:
            await update.message.reply_text(
                "💡 *Uso:* `/pregunta [tu consulta]`\n\n*Ejemplos:*\n"
                "• `/pregunta ¿Cuántos archivos tiene Ibagué?`\n"
                "• `/pregunta Busca shapefiles en Neiva`",
                parse_mode='Markdown'
            )
            return

        pregunta = ' '.join(context.args)
        processing_msg = await update.message.reply_text("🤖 Procesando consulta...")

        try:
            resultado = self.ai_system.procesar_consulta_completa(pregunta)

            # Construir mensaje sin Markdown para evitar errores de formato
            message = "🤖 Respuesta IA\n\n"

            if resultado['municipios']:
                mun = resultado['municipios'][0]
                message += f"📍 Municipio: {mun['nombre']} ({mun['cod_dane']})\n\n"

            if resultado['archivos_encontrados']:
                message += f"🗂️ Archivos relevantes: {len(resultado['archivos_encontrados'])}\n\n"

            message += f"💡 {resultado['respuesta_ia']}"

            await processing_msg.delete()
            # Enviar sin parse_mode para evitar conflictos con caracteres especiales
            await update.message.reply_text(message)

            # Generar respuesta por voz con VEGA
            voz_disponible = self.voice_synth.is_available()
            self.logger.info(f"Voz disponible: {voz_disponible}")

            if voz_disponible:
                try:
                    voice_msg = await update.message.reply_text("🎤 Generando respuesta por voz...")

                    # Generar audio (solo la respuesta de IA, sin emojis)
                    texto_voz = resultado['respuesta_ia'].replace('📍', '').replace('🗂️', '').replace('💡', '').strip()
                    self.logger.info(f"Texto para voz ({len(texto_voz)} chars): {texto_voz[:100]}...")

                    audio_bytes = self.voice_synth.text_to_speech_bytes(texto_voz, language='es')
                    self.logger.info(f"Audio bytes generados: {len(audio_bytes) if audio_bytes else 0}")

                    if audio_bytes:
                        await voice_msg.delete()
                        await update.message.reply_voice(
                            voice=audio_bytes,
                            caption="🎤 Respuesta de VEGA"
                        )
                        self.logger.info(f"✅ Respuesta por voz enviada (usuario: {user_id})")
                    else:
                        await voice_msg.edit_text("⚠️ No se pudo generar audio")
                        self.logger.error("audio_bytes es None")

                except Exception as ve:
                    self.logger.error(f"❌ Error generando voz: {ve}")
                    import traceback
                    self.logger.error(traceback.format_exc())
                    try:
                        await voice_msg.edit_text(f"⚠️ Error: {str(ve)[:100]}")
                    except:
                        pass
            else:
                self.logger.warning("Voz NO disponible - no se generará audio")

        except Exception as e:
            self.logger.error(f"Error en /pregunta: {e}")
            await processing_msg.delete()
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def cmd_buscar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /buscar - Busca archivos"""
        user_id = update.effective_user.id

        if not self._puede_ejecutar_comando(user_id, 'buscar'):
            await update.message.reply_text("❌ No autorizado")
            return

        if not context.args:
            await update.message.reply_text(
                "💡 *Uso:* `/buscar [keywords]`\n\n*Ejemplos:*\n"
                "• `/buscar shp cartografia`\n• `/buscar excel poblacion`",
                parse_mode='Markdown'
            )
            return

        keywords = context.args
        processing_msg = await update.message.reply_text("🔍 Buscando archivos...")

        try:
            archivos = self.ai_system.buscar_archivos_por_keywords(keywords)

            if not archivos:
                await processing_msg.delete()
                await update.message.reply_text("❌ No se encontraron archivos")
                return

            message = f"🔍 *Resultados*\n\nEncontrados: *{len(archivos)}*\n\n"

            for idx, archivo in enumerate(archivos[:5], 1):
                nombre = archivo['path'].split('/')[-1]
                message += f"📄 *{idx}. {nombre}*\n"
                message += f"   {archivo['origen']} - {archivo['size_mb']:.2f} MB\n\n"

            if len(archivos) > 5:
                message += f"_... y {len(archivos) - 5} más_"

            await processing_msg.delete()
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            self.logger.error(f"Error en /buscar: {e}")
            await processing_msg.delete()
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def cmd_municipio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /municipio - Info de municipio"""
        user_id = update.effective_user.id

        if not self._puede_ejecutar_comando(user_id, 'municipio'):
            await update.message.reply_text("❌ No autorizado")
            return

        if not context.args:
            await update.message.reply_text(
                "💡 *Uso:* `/municipio [nombre]`\n\n*Ejemplos:*\n"
                "• `/municipio Ibagué`\n• `/municipio Neiva`",
                parse_mode='Markdown'
            )
            return

        nombre = ' '.join(context.args)
        processing_msg = await update.message.reply_text("🔍 Buscando municipio...")

        try:
            municipio = self.ai_system.buscar_municipio(nombre)

            if not municipio:
                await processing_msg.delete()
                await update.message.reply_text(f"❌ No se encontró: *{nombre}*", parse_mode='Markdown')
                return

            if 'multiples' in municipio:
                message = "📍 *Múltiples resultados:*\n\n"
                for idx, m in enumerate(municipio['multiples'], 1):
                    message += f"{idx}. *{m['nombre']}* ({m['cod_dane']}) - {m['nombre_depto']}\n"
                await processing_msg.delete()
                await update.message.reply_text(message, parse_mode='Markdown')
                return

            stats = self.ai_system.obtener_estadisticas_municipio(municipio['cod_dane'])

            message = f"📍 *{municipio['nombre']}*\n\n"
            message += f"🆔 Código: `{municipio['cod_dane']}`\n"
            message += f"🏛️ Depto: {municipio['nombre_depto']}\n\n"

            if stats and stats.get('total_archivos', 0) > 0:
                message += f"📊 *PREOPERACION:*\n"
                message += f"• Archivos: *{stats['total_archivos']:,}*\n"
                message += f"• Peso: *{stats['peso_total_gb']:.2f} GB*\n\n"

                if stats['categorias']:
                    message += "📁 *Top 5:*\n"
                    for idx, cat in enumerate(stats['categorias'][:5], 1):
                        message += f"{idx}. {cat['categoria']}: {cat['archivos']:,}\n"
            else:
                message += "⚠️ Sin datos"

            await processing_msg.delete()
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            self.logger.error(f"Error en /municipio: {e}")
            await processing_msg.delete()
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def cmd_urgente(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /urgente [script] [municipio] - Actualización urgente"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ No autorizado")
            return

        if len(context.args) < 2:
            await update.message.reply_text(
                "🚨 *ACTUALIZACIÓN URGENTE*\n\n"
                "📝 *Uso:* `/urgente [script] [municipio]`\n\n"
                "*Ejemplos:*\n"
                "• `/urgente post Ibagué` - POST para Ibagué\n"
                "• `/urgente insumos La Dorada` - INSUMOS para La Dorada\n"
                "• `/urgente post 23670` - POST para código DANE 23670\n\n"
                "*Scripts disponibles:*\n"
                "• post, insumos, transversal, operacion",
                parse_mode='Markdown'
            )
            return

        # Obtener script
        script_name = context.args[0].lower()
        script_full = self.script_map.get(script_name, script_name)
        script_path = self.scripts_dir / script_full

        if not script_path.exists():
            await update.message.reply_text(f"❌ Script `{script_name}` no encontrado", parse_mode='Markdown')
            return

        # Obtener municipio
        municipio_input = ' '.join(context.args[1:])

        # Buscar municipio
        processing_msg = await update.message.reply_text("🔍 Buscando municipio...")

        try:
            # Buscar municipio por nombre
            municipio = self.ai_system.buscar_municipio(municipio_input)

            if not municipio:
                await processing_msg.delete()
                await update.message.reply_text(f"❌ No se encontró: *{municipio_input}*", parse_mode='Markdown')
                return

            if 'multiples' in municipio:
                await processing_msg.delete()
                message = "⚠️ *Múltiples resultados:*\n\n"
                for idx, m in enumerate(municipio['multiples'], 1):
                    message += f"{idx}. *{m['nombre']}* ({m['cod_dane']}) - {m['nombre_depto']}\n"
                message += f"\n💡 Escribe el nombre completo:\n`/urgente {script_name} [nombre exacto]`"
                await update.message.reply_text(message, parse_mode='Markdown')
                return

            municipio_cod = municipio['cod_dane']
            municipio_nombre = municipio['nombre']

            await processing_msg.edit_text(
                f"🚨 Iniciando *{script_name.upper()}* para *{municipio_nombre}*...",
                parse_mode='Markdown'
            )

            # Crear directorio de logs
            base_dir = Path(self.config.get('paths', 'base_dir'))
            log_dir = base_dir / 'logs' / 'scripts'
            log_dir.mkdir(exist_ok=True, parents=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = log_dir / f"{script_name}_{municipio_cod}_{timestamp}.log"

            # Construir comando
            cmd = ['python3', str(script_path), '--verbose', '--municipio', municipio_cod]

            # Preparar variables de entorno - FIX: Pasar explícitamente al subprocess
            env_vars = os.environ.copy()
            env_vars.update({
                'DB_HOST': self.config.get('database', 'host'),
                'DB_NAME': self.config.get('database', 'database'),
                'DB_USER': self.config.get('database', 'user'),
                'DB_PASSWORD': self.config.get('database', 'password'),
                'DB_PORT': str(self.config.get('database', 'port')),
            })

            # Iniciar script con variables de entorno
            with open(log_file, 'w') as f:
                process = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                    env=env_vars,  # Pasar variables de entorno explícitamente
                    cwd=str(script_path.parent)  # Establecer directorio de trabajo
                )

            self.logger.info(f"[URGENTE] Script {script_name} iniciado para {municipio_cod} "
                           f"(PID: {process.pid}, log: {log_file})")

            await processing_msg.delete()

            message = (
                f"🚨 *URGENTE: {script_name.upper()}*\n\n"
                f"📍 Municipio: *{municipio_nombre}*\n"
                f"🆔 Código DANE: `{municipio_cod}`\n"
                f"🔧 PID: `{process.pid}`\n"
                f"📝 Log: `{log_file.name}`\n\n"
                f"💡 Usa `/logs_live {script_name}` para monitorear"
            )

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            self.logger.error(f"Error en /urgente: {e}")
            await processing_msg.delete()
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # Métodos auxiliares

    def _get_active_scripts(self) -> Dict[str, int]:
        """Obtiene scripts activos con sus PIDs"""
        active = {}
        for short_name, full_name in self.script_map.items():
            pid = self._get_script_pid(full_name)
            if pid:
                active[short_name] = pid
        return active

    def _get_script_pid(self, script_name: str) -> Optional[int]:
        """Obtiene el PID de un script si está corriendo"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and script_name in ' '.join(cmdline):
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return None

    def _is_script_running(self, script_name: str) -> bool:
        """Verifica si un script está corriendo"""
        return self._get_script_pid(script_name) is not None

    def _get_last_script_runs(self) -> Dict[str, str]:
        """Obtiene la última ejecución de cada script desde la BD"""
        last_runs = {}
        try:
            # Intentar obtener desde notificaciones (estructura nueva)
            query = """
                SELECT tipo_entidad, MAX(fecha_cambio) as ultima
                FROM notificaciones
                WHERE tipo_entidad IN ('script_post', 'script_insumos', 'script_transversal', 'script_operacion')
                GROUP BY tipo_entidad
            """
            results = self.db.execute_query(query, fetch=True)

            if results:
                for tipo, fecha in results:
                    script_name = tipo.replace('script_', '')
                    if fecha:
                        last_runs[script_name] = fecha.strftime('%Y-%m-%d %H:%M')
                    else:
                        last_runs[script_name] = "Nunca"
            else:
                # Si no hay resultados, retornar valores por defecto
                for script in ['post', 'insumos', 'transversal', 'operacion']:
                    last_runs[script] = "Sin datos"

        except Exception as e:
            self.logger.warning(f"No se pudieron obtener últimas ejecuciones (tabla puede no existir): {e}")
            # Retornar valores por defecto
            for script in ['post', 'insumos', 'transversal', 'operacion']:
                last_runs[script] = "N/A"

        return last_runs

    def _get_active_scripts_detailed(self) -> list:
        """Obtiene información detallada de scripts en ejecución"""
        active_scripts = []

        for short_name, full_name in self.script_map.items():
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info', 'create_time']):
                try:
                    cmdline = proc.info['cmdline']
                    if not cmdline:
                        continue

                    if full_name in ' '.join(cmdline):
                        # Calcular tiempo de ejecución
                        create_time = proc.info['create_time']
                        runtime_seconds = time.time() - create_time
                        runtime = format_duration(int(runtime_seconds))

                        # Obtener CPU y memoria
                        cpu_percent = proc.cpu_percent(interval=0.1)
                        memory_mb = proc.info['memory_info'].rss / (1024 * 1024)

                        active_scripts.append({
                            'name': short_name,
                            'pid': proc.info['pid'],
                            'runtime': runtime,
                            'cpu': cpu_percent,
                            'memory': memory_mb
                        })
                        break  # Ya encontramos este script

                except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                    continue

        return active_scripts

    def _get_next_executions(self) -> list:
        """Calcula las próximas 5 ejecuciones programadas"""
        from datetime import datetime, timedelta
        import calendar

        now = datetime.now()
        executions = []

        # POST e INSUMOS - cada 6 horas
        post_insumos_times = ["00:00", "06:00", "12:00", "18:00"]
        for time_str in post_insumos_times:
            hour, minute = map(int, time_str.split(':'))
            exec_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Si ya pasó hoy, programar para mañana
            if exec_time <= now:
                exec_time += timedelta(days=1)

            time_left = exec_time - now
            hours_left = int(time_left.total_seconds() / 3600)
            minutes_left = int((time_left.total_seconds() % 3600) / 60)

            if hours_left > 0:
                tiempo_str = f"{hours_left}h {minutes_left}m"
            else:
                tiempo_str = f"{minutes_left}m"

            executions.append({
                'scripts': ['POST', 'INSUMOS'],
                'hora': exec_time.strftime('%a %d/%m %H:%M'),
                'tiempo_restante': tiempo_str,
                'timestamp': exec_time,
                'es_proximo': False
            })

        # TRANSVERSAL y OPERACION - cada Lunes 02:00
        days_until_monday = (7 - now.weekday()) % 7  # 0 = Lunes
        if days_until_monday == 0:  # Hoy es lunes
            next_monday = now.replace(hour=2, minute=0, second=0, microsecond=0)
            if next_monday <= now:
                days_until_monday = 7
                next_monday += timedelta(days=7)
        else:
            next_monday = now + timedelta(days=days_until_monday)
            next_monday = next_monday.replace(hour=2, minute=0, second=0, microsecond=0)

        time_left = next_monday - now
        days_left = time_left.days
        hours_left = int((time_left.total_seconds() % 86400) / 3600)

        if days_left > 0:
            tiempo_str = f"{days_left}d {hours_left}h"
        elif hours_left > 0:
            minutes_left = int((time_left.total_seconds() % 3600) / 60)
            tiempo_str = f"{hours_left}h {minutes_left}m"
        else:
            minutes_left = int(time_left.total_seconds() / 60)
            tiempo_str = f"{minutes_left}m"

        executions.append({
            'scripts': ['TRANSVERSAL', 'OPERACION'],
            'hora': next_monday.strftime('%a %d/%m %H:%M'),
            'tiempo_restante': tiempo_str,
            'timestamp': next_monday,
            'es_proximo': False
        })

        # Ordenar por timestamp
        executions.sort(key=lambda x: x['timestamp'])

        # Marcar el próximo
        if executions:
            executions[0]['es_proximo'] = True

        # Retornar solo las próximas 5
        return executions[:5]

    def run(self):
        """Inicia el bot"""
        token = self.config.get('telegram', 'token')

        # Crear aplicación
        application = Application.builder().token(token).build()

        # Registrar comandos
        application.add_handler(CommandHandler("start", self.cmd_start_bot))
        application.add_handler(CommandHandler("ayuda", self.cmd_help))
        application.add_handler(CommandHandler("comandos", self.cmd_help))  # Alias
        application.add_handler(CommandHandler("help", self.cmd_help))  # Mantener por compatibilidad
        application.add_handler(CommandHandler("status", self.cmd_status))
        application.add_handler(CommandHandler("scripts", self.cmd_scripts))
        application.add_handler(CommandHandler("proximos", self.cmd_proximos))
        application.add_handler(CommandHandler("logs", self.cmd_logs))
        application.add_handler(CommandHandler("logs_live", self.cmd_logs_live))
        application.add_handler(CommandHandler("iniciar", self.cmd_start_script))
        application.add_handler(CommandHandler("ejecutar", self.cmd_ejecutar))
        application.add_handler(CommandHandler("detener", self.cmd_stop_script))
        application.add_handler(CommandHandler("restart", self.cmd_restart_script))
        application.add_handler(CommandHandler("cleanup", self.cmd_cleanup))
        application.add_handler(CommandHandler("server", self.cmd_server))
        application.add_handler(CommandHandler("docker", self.cmd_docker))
        # Comandos IA
        application.add_handler(CommandHandler("pregunta", self.cmd_pregunta))
        application.add_handler(CommandHandler("buscar", self.cmd_buscar))
        application.add_handler(CommandHandler("municipio", self.cmd_municipio))
        application.add_handler(CommandHandler("urgente", self.cmd_urgente))

        self.logger.info("Bot de Telegram iniciado correctamente")
        print("🤖 Bot de Telegram en ejecución...")

        # Iniciar bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    try:
        bot = ServerBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)
