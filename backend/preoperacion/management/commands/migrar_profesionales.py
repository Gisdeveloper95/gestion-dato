from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from preoperacion.models import ProfesionalesSeguimiento

class Command(BaseCommand):
    def handle(self, *args, **options):
        grupo_profesionales = Group.objects.get(name='Profesionales_Seguimiento')
        
        for profesional in ProfesionalesSeguimiento.objects.all():
            if not profesional.usuario_django:
                # Crear usuario Django
                username = profesional.cod_profesional
                email = profesional.correo_profesional or f"{username}@sistema.com"
                
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': profesional.nombre_profesional.split()[0],
                        'last_name': ' '.join(profesional.nombre_profesional.split()[1:]),
                        'is_active': True
                    }
                )
                
                if created:
                    user.set_password('temporal123')  # Contraseña temporal
                    user.save()
                    user.groups.add(grupo_profesionales)
                
                # Asociar con profesional
                profesional.usuario_django = user
                profesional.save()
                
                self.stdout.write(f'Usuario creado para: {profesional.nombre_profesional}')