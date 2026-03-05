#!/usr/bin/env python3
"""
Limpiador automático de base de datos
Elimina registros antiguos (>4 meses) de tablas especificadas
Ejecutar manualmente o programar con cron/systemd
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict

# Importar utilidades comunes
sys.path.insert(0, str(Path(__file__).parent))
from utils.common import Config, DatabaseManager, TelegramNotifier, Logger


class DatabaseCleaner:
    """Limpiador de base de datos"""

    def __init__(self, config_path: str = None):
        self.config = Config(config_path)
        self.db = DatabaseManager(self.config)
        self.notifier = TelegramNotifier(self.config)
        self.logger = Logger.setup_logger('db_cleaner', self.config)

        self.enabled = self.config.get('cleanup', 'enabled', default=True)
        self.retention_months = self.config.get('cleanup', 'retention_months', default=4)
        self.tables = self.config.get('cleanup', 'tables', default=[])

    def clean_table(self, table: str) -> int:
        """Limpia una tabla específica"""
        self.logger.info(f"Limpiando tabla: {table}")

        try:
            # Primero verificar cuántos registros hay antes
            count_query = f"""
                SELECT COUNT(*) FROM {table}
                WHERE fecha_creacion < NOW() - INTERVAL '{self.retention_months} months'
            """
            result = self.db.execute_query(count_query, fetch=True)
            records_to_delete = result[0][0] if result else 0

            if records_to_delete == 0:
                self.logger.info(f"No hay registros para eliminar en {table}")
                return 0

            self.logger.info(f"Se eliminarán {records_to_delete:,} registros de {table}")

            # Eliminar registros
            deleted = self.db.cleanup_old_records(table, self.retention_months)

            self.logger.info(f"✅ Eliminados {deleted:,} registros de {table}")
            return deleted

        except Exception as e:
            self.logger.error(f"Error limpiando tabla {table}: {e}")
            self.notifier.send_error(f"DB Cleaner ({table})", str(e))
            return 0

    def run(self, force: bool = False) -> Dict[str, int]:
        """Ejecuta la limpieza de todas las tablas configuradas"""
        if not self.enabled and not force:
            self.logger.info("Limpieza deshabilitada en configuración")
            return {}

        self.logger.info("=== Iniciando limpieza de base de datos ===")
        self.logger.info(f"Retención: {self.retention_months} meses")
        self.logger.info(f"Tablas: {', '.join(self.tables)}")

        start_time = datetime.now()
        deleted_counts = {}

        for table in self.tables:
            try:
                deleted = self.clean_table(table)
                deleted_counts[table] = deleted
            except Exception as e:
                self.logger.error(f"Error procesando tabla {table}: {e}")
                deleted_counts[table] = 0

        # Calcular duración
        duration = (datetime.now() - start_time).total_seconds()

        # Enviar reporte por Telegram
        self.send_report(deleted_counts, duration)

        self.logger.info(f"=== Limpieza completada en {duration:.1f}s ===")

        return deleted_counts

    def send_report(self, deleted_counts: Dict[str, int], duration: float):
        """Envía reporte de limpieza por Telegram"""
        total_deleted = sum(deleted_counts.values())

        if total_deleted == 0:
            message = "🧹 *Limpieza de Base de Datos*\n\n"
            message += "✅ No había registros para eliminar\n"
            message += f"⏱️ Duración: {duration:.1f}s"
        else:
            message = "🧹 *Limpieza de Base de Datos*\n\n"
            message += f"📊 *Total eliminado:* {total_deleted:,} registros\n\n"

            for table, count in deleted_counts.items():
                if count > 0:
                    message += f"• `{table}`: {count:,}\n"

            message += f"\n⏱️ Duración: {duration:.1f}s"
            message += f"\n📅 Retención: {self.retention_months} meses"

        self.notifier.send_message(message)

    def get_table_stats(self) -> Dict[str, Dict[str, int]]:
        """Obtiene estadísticas de las tablas"""
        stats = {}

        for table in self.tables:
            try:
                # Total de registros
                query_total = f"SELECT COUNT(*) FROM {table}"
                result = self.db.execute_query(query_total, fetch=True)
                total = result[0][0] if result else 0

                # Registros antiguos (>4 meses)
                query_old = f"""
                    SELECT COUNT(*) FROM {table}
                    WHERE fecha_creacion < NOW() - INTERVAL '{self.retention_months} months'
                """
                result = self.db.execute_query(query_old, fetch=True)
                old = result[0][0] if result else 0

                # Registros recientes (<1 mes)
                query_recent = f"""
                    SELECT COUNT(*) FROM {table}
                    WHERE fecha_creacion > NOW() - INTERVAL '1 month'
                """
                result = self.db.execute_query(query_recent, fetch=True)
                recent = result[0][0] if result else 0

                stats[table] = {
                    'total': total,
                    'old': old,
                    'recent': recent
                }

            except Exception as e:
                self.logger.error(f"Error obteniendo stats de {table}: {e}")
                stats[table] = {'total': 0, 'old': 0, 'recent': 0}

        return stats

    def print_stats(self):
        """Imprime estadísticas de las tablas"""
        stats = self.get_table_stats()

        print("\n📊 Estadísticas de Base de Datos")
        print("=" * 60)

        for table, data in stats.items():
            print(f"\n{table}:")
            print(f"  Total:           {data['total']:>10,} registros")
            print(f"  Antiguos (>4m):  {data['old']:>10,} registros")
            print(f"  Recientes (<1m): {data['recent']:>10,} registros")

        print("\n" + "=" * 60)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Limpiador de base de datos')
    parser.add_argument('--stats', action='store_true', help='Mostrar estadísticas sin limpiar')
    parser.add_argument('--force', action='store_true', help='Forzar limpieza aunque esté deshabilitada')
    parser.add_argument('--dry-run', action='store_true', help='Simulación (no elimina nada)')

    args = parser.parse_args()

    try:
        cleaner = DatabaseCleaner()

        if args.stats:
            cleaner.print_stats()
        elif args.dry_run:
            print("🔍 Modo simulación (dry-run)")
            stats = cleaner.get_table_stats()

            total_to_delete = sum(s['old'] for s in stats.values())
            print(f"\n💡 Se eliminarían {total_to_delete:,} registros en total:")

            for table, data in stats.items():
                if data['old'] > 0:
                    print(f"  • {table}: {data['old']:,} registros")
        else:
            deleted_counts = cleaner.run(force=args.force)

            print("\n✅ Limpieza completada:")
            for table, count in deleted_counts.items():
                print(f"  • {table}: {count:,} registros eliminados")

    except KeyboardInterrupt:
        print("\n👋 Limpieza cancelada por el usuario")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)
