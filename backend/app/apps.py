from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

class DirectoriosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'directorios'
    verbose_name = 'Gestión de Directorios y Archivos'
    
    def ready(self):
        """Configuración cuando la app está lista"""
        # Aquí puedes importar signals si los necesitas
        # import directorios.signals
        pass