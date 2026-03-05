# preoperacion/management/commands/crear_usuarios_profesionales.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from preoperacion.models import ProfesionalesSeguimiento
from django.db import transaction

class Command(BaseCommand):
    help = 'Crea usuarios Django para profesionales de seguimiento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--actualizar',
            action='store_true',
            help='Actualizar usuarios existentes también',
        )

    def handle(self, *args, **options):
        # Crear grupo si no existe
        grupo_profesionales, created = Group.objects.get_or_create(
            name='Profesionales_Seguimiento'
        )
        
        if created:
            self.stdout.write('✅ Grupo "Profesionales_Seguimiento" creado')
        
        # Crear usuarios para cada profesional
        creados = 0
        actualizados = 0
        existentes = 0
        errores = 0
        
        for profesional in ProfesionalesSeguimiento.objects.all():
            username = profesional.cod_profesional
            
            # GENERAR EMAIL ÚNICO USANDO EL USERNAME
            email = f"{username}@sistema.igac.gov.co"  # Siempre único
            
            try:
                with transaction.atomic():
                    # Verificar si ya existe el usuario
                    if User.objects.filter(username=username).exists():
                        existentes += 1
                        # Asegurar relación y grupo
                        user = User.objects.get(username=username)
                        if not profesional.usuario_django:
                            profesional.usuario_django = user
                            profesional.save()
                        user.groups.add(grupo_profesionales)
                        continue
                    
                    # Crear nuevo usuario
                    user = User.objects.create_user(
                        username=username,
                        password=username,  # Password = cod_profesional
                        email=email,  # Email único basado en username
                        first_name=profesional.nombre_profesional.split()[0] if profesional.nombre_profesional else '',
                        last_name=' '.join(profesional.nombre_profesional.split()[1:]) if len(profesional.nombre_profesional.split()) > 1 else '',
                        is_active=True,
                        is_staff=False,
                        is_superuser=False
                    )
                    
                    # Agregar al grupo
                    user.groups.add(grupo_profesionales)
                    
                    # Establecer relación
                    profesional.usuario_django = user
                    profesional.save()
                    
                    creados += 1
                    self.stdout.write(f'✅ Usuario creado: {username} ({profesional.nombre_profesional})')
                    
            except Exception as e:
                errores += 1
                self.stdout.write(
                    self.style.ERROR(f'❌ Error creando {username}: {str(e)}')
                )
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado: {creados} creados, {existentes} ya existían, {errores} errores'
            )
        )