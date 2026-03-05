from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import json

# Importar función de permisos de preoperacion
try:
    from preoperacion.models import ProfesionalesSeguimiento, ProfesionalMunicipio
except ImportError:
    ProfesionalesSeguimiento = None
    ProfesionalMunicipio = None


class DirectorioMunicipioPermissionMiddleware(MiddlewareMixin):
    """
    Middleware que agrega información de municipios permitidos a todas las requests
    de la app de directorios, para optimizar las consultas de permisos.
    """
    
    def process_request(self, request):
        # Solo aplicar a la app de directorios
        if not request.path.startswith('/directorios/'):
            return None
        
        if request.user.is_authenticated:
            # Cachear los municipios permitidos en la request
            request.directorios_municipios_permitidos = self._get_municipios_permitidos(request.user)
        else:
            request.directorios_municipios_permitidos = []
        
        return None
    
    def _get_municipios_permitidos(self, user):
        """
        Función copiada de preoperacion para obtener municipios permitidos
        """
        if not user.is_authenticated:
            return []
        
        # Super administradores y administradores pueden ver todo
        if user.is_superuser or user.is_staff:
            return 'todos'
        
        # Verificar si es profesional de seguimiento
        if user.groups.filter(name='Profesionales_Seguimiento').exists():
            try:
                if ProfesionalesSeguimiento and ProfesionalMunicipio:
                    profesional = ProfesionalesSeguimiento.objects.get(
                        cod_profesional=user.username
                    )
                    municipios_ids = ProfesionalMunicipio.objects.filter(
                        cod_profesional=profesional
                    ).values_list('cod_municipio', flat=True)
                    return list(municipios_ids)
            except ProfesionalesSeguimiento.DoesNotExist:
                return []
        
        return []


class DirectorioAPIErrorMiddleware(MiddlewareMixin):
    """
    Middleware para manejar errores específicos de la API de directorios
    y devolver respuestas JSON consistentes.
    """
    
    def process_exception(self, request, exception):
        # Solo aplicar a la app de directorios y requests de API
        if not request.path.startswith('/directorios/api/'):
            return None
        
        # Manejar errores de permisos específicos
        if isinstance(exception, PermissionError):
            return JsonResponse({
                'error': 'No tiene permisos para acceder a este recurso',
                'codigo': 'PERMISSION_DENIED',
                'detalle': str(exception)
            }, status=403)
        
        # Manejar errores de municipio no encontrado
        if 'municipio' in str(exception).lower() and 'not found' in str(exception).lower():
            return JsonResponse({
                'error': 'Municipio no encontrado o sin acceso',
                'codigo': 'MUNICIPIO_NOT_FOUND',
                'detalle': str(exception)
            }, status=404)
        
        return None


class DirectorioRequestLogMiddleware(MiddlewareMixin):
    """
    Middleware opcional para logging de requests a la API de directorios
    """
    
    def process_request(self, request):
        if not request.path.startswith('/directorios/api/'):
            return None
        
        # Log de requests importantes (opcional, para debugging)
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            import logging
            logger = logging.getLogger('directorios')
            logger.info(f"API Request: {request.method} {request.path} - Usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'}")
        
        return None


class DirectorioCORSMiddleware(MiddlewareMixin):
    """
    Middleware para manejar CORS específico para la API de directorios
    """
    
    def process_response(self, request, response):
        if not request.path.startswith('/directorios/api/'):
            return response
        
        # Agregar headers CORS para la API de directorios
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response['Access-Control-Expose-Headers'] = 'X-Total-Count, X-Page-Count'
        
        return response
    
    def process_request(self, request):
        if request.method == 'OPTIONS' and request.path.startswith('/directorios/api/'):
            # Manejar preflight requests
            from django.http import HttpResponse
            response = HttpResponse()
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            return response
        return None