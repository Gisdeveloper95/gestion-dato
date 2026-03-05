# Crear la estructura de directorios:
# app/management/
# app/management/__init__.py
# app/management/commands/
# app/management/commands/__init__.py
# app/management/commands/run_script.py

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from app.models import ScriptExecution
from app.utils import ScriptRunner
from django.utils import timezone

class Command(BaseCommand):
    help = 'Ejecuta un script específico'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'script_name',
            type=str,
            choices=['backup_db', 'llenar_datos'],
            help='Nombre del script a ejecutar'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username del usuario que ejecuta el script (opcional)'
        )
        parser.add_argument(
            '--clean-backup-dir',
            action='store_true',
            help='Limpiar directorio de backups antes de ejecutar'
        )
    
    def handle(self, *args, **options):
        script_name = options['script_name']
        username = options.get('user')
        clean_backup = options.get('clean_backup_dir', False)
        
        # Obtener usuario
        user = None
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Usuario {username} no encontrado. Ejecutando sin usuario.')
                )
        
        # Crear registro de ejecución
        execution = ScriptExecution.objects.create(
            script_name=script_name,
            user=user,
            status='running',
            started_at=timezone.now()
        )
        
        self.stdout.write(f'Iniciando ejecución del script: {script_name}')
        self.stdout.write(f'ID de ejecución: {execution.id}')
        
        try:
            runner = ScriptRunner()
            
            # Limpiar directorio si se solicita
            if clean_backup and script_name == 'backup_db':
                self.stdout.write('Limpiando directorio de backups...')
                if runner.clean_backup_directory():
                    self.stdout.write(self.style.SUCCESS('Directorio limpiado exitosamente'))
                else:
                    self.stdout.write(self.style.WARNING('Error limpiando directorio'))
            
            # Ejecutar script
            if script_name == 'backup_db':
                result = runner.execute_backup_script()
            elif script_name == 'llenar_datos':
                result = runner.execute_data_script()
            else:
                raise CommandError(f'Script no soportado: {script_name}')
            
            # Actualizar ejecución
            execution.status = 'completed' if result['success'] else 'failed'
            execution.completed_at = timezone.now()
            execution.output_log = result.get('output', '')
            execution.error_message = result.get('error', '') if not result['success'] else None
            execution.save()
            
            # Mostrar resultados
            if result['success']:
                self.stdout.write(self.style.SUCCESS(f'Script ejecutado exitosamente'))
                if result.get('output'):
                    self.stdout.write('Salida del script:')
                    self.stdout.write(result['output'])
                
                # Para backups, mostrar archivos creados
                if script_name == 'backup_db' and result.get('backup_files'):
                    self.stdout.write('\nArchivos de backup creados:')
                    for file_info in result['backup_files']:
                        size_mb = file_info['size'] / (1024 * 1024)
                        self.stdout.write(f"  - {file_info['filename']} ({size_mb:.2f} MB)")
            else:
                self.stdout.write(self.style.ERROR(f'Error ejecutando script: {result.get("error", "Error desconocido")}'))
                if result.get('output'):
                    self.stdout.write('Salida del script:')
                    self.stdout.write(result['output'])
            
        except Exception as e:
            execution.status = 'failed'
            execution.completed_at = timezone.now()
            execution.error_message = str(e)
            execution.save()
            
            raise CommandError(f'Error ejecutando script: {str(e)}')
        
        self.stdout.write(f'Ejecución completada. Estado: {execution.status}')