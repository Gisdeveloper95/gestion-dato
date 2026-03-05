from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Crear grupos
        admin_group, created = Group.objects.get_or_create(name='Administradores')
        profesional_group, created = Group.objects.get_or_create(name='Profesionales_Seguimiento')
        
        self.stdout.write('Grupos creados exitosamente')